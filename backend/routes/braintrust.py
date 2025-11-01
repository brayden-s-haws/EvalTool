"""Braintrust integration API endpoints."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import requests
import os
from models import Trace, TraceStep

router = APIRouter()


class BraintrustImportRequest(BaseModel):
    """Request model for importing traces from Braintrust."""

    api_key: Optional[str] = None
    project_id: str
    experiment_id: str
    filters: Dict[str, Any] = {}


class BraintrustExportRequest(BaseModel):
    """Request model for exporting annotations to Braintrust."""

    api_key: Optional[str] = None
    project_id: str
    experiment_id: str
    trace_ids: List[str]


@router.post("/import")
async def import_from_braintrust(request: BraintrustImportRequest):
    """
    Import traces from Braintrust.

    Request Body:
    - api_key: Braintrust API key (optional, uses env var if not provided)
    - project_id: Braintrust project ID
    - experiment_id: Braintrust experiment ID
    - filters: Optional filters (start_date, end_date, limit)
    """
    api_key = request.api_key or os.getenv("BRAINTRUST_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Braintrust API key not provided and BRAINTRUST_API_KEY not set"
        )

    try:
        # Build Braintrust API URL
        url = f"https://api.braintrust.dev/v1/experiment/{request.experiment_id}/fetch"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Build query parameters
        params = {
            "limit": request.filters.get("limit", 100)
        }

        if "cursor" in request.filters:
            params["cursor"] = request.filters["cursor"]

        # Make API request
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Convert Braintrust traces to our Trace format
        traces = []
        for bt_trace in data.get("objects", []):
            trace = Trace(
                id=bt_trace.get("id", f"bt_{len(traces)}"),
                user_input=str(bt_trace.get("input", "")),
                agent_output=str(bt_trace.get("output", "")),
                system_prompt=bt_trace.get("metadata", {}).get("system_prompt"),
                intermediate_steps=[],
                metadata={
                    "braintrust_trace_id": bt_trace.get("id"),
                    "timestamp": bt_trace.get("created"),
                    "scores": bt_trace.get("scores", {}),
                    **bt_trace.get("metadata", {})
                }
            )
            traces.append(trace)

        # Store traces in traces_db
        from routes.traces import traces_db
        for trace in traces:
            traces_db[trace.id] = trace

        return {
            "success": True,
            "imported_count": len(traces),
            "traces": traces,
            "cursor": data.get("cursor")
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch from Braintrust API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import traces: {str(e)}"
        )


@router.post("/export")
async def export_to_braintrust(request: BraintrustExportRequest):
    """
    Export annotations to Braintrust.

    Request Body:
    - api_key: Braintrust API key (optional, uses env var if not provided)
    - project_id: Braintrust project ID
    - experiment_id: Braintrust experiment ID
    - trace_ids: List of trace IDs to export
    """
    api_key = request.api_key or os.getenv("BRAINTRUST_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Braintrust API key not provided and BRAINTRUST_API_KEY not set"
        )

    try:
        from routes.traces import traces_db
        from routes.tags import tags_db

        # Build feedback payload
        feedback_items = []
        failures = []

        for trace_id in request.trace_ids:
            if trace_id not in traces_db:
                failures.append({
                    "trace_id": trace_id,
                    "error": "Trace not found"
                })
                continue

            trace = traces_db[trace_id]

            if not trace.reviewed:
                failures.append({
                    "trace_id": trace_id,
                    "error": "Trace not reviewed"
                })
                continue

            # Convert pass/fail to score
            score = None
            if trace.pass_fail == "pass":
                score = 1.0
            elif trace.pass_fail == "fail":
                score = 0.0

            # Get tag names from IDs
            tag_names = [
                tags_db[tag_id].name
                for tag_id in trace.axial_tags
                if tag_id in tags_db
            ]

            feedback_item = {
                "id": trace.metadata.get("braintrust_trace_id", trace.id),
                "scores": {
                    "pass_fail": score
                } if score is not None else {},
                "comment": trace.open_code or "",
                "metadata": {
                    "axial_tags": tag_names,
                    "reviewer": trace.reviewer_id,
                    "reviewed_at": trace.reviewed_at.isoformat() if trace.reviewed_at else None
                }
            }

            feedback_items.append(feedback_item)

        if not feedback_items:
            return {
                "success": False,
                "exported_count": 0,
                "failures": failures,
                "message": "No traces to export"
            }

        # Send to Braintrust
        url = f"https://api.braintrust.dev/v1/experiment/{request.experiment_id}/feedback"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "feedback": feedback_items
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        return {
            "success": True,
            "exported_count": len(feedback_items),
            "failures": failures
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to Braintrust API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export annotations: {str(e)}"
        )
