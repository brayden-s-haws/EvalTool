"""Annotation management API endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import Trace
from routes.traces import traces_db

router = APIRouter()


class AnnotationRequest(BaseModel):
    """Request model for creating/updating annotations."""

    trace_id: str
    pass_fail: str  # "pass", "fail", or "defer"
    open_code: Optional[str] = None
    axial_tags: List[str] = []
    reviewer_id: Optional[str] = None


@router.post("/")
async def create_annotation(annotation: AnnotationRequest):
    """
    Create or update annotation for a trace.

    Request Body:
    - trace_id: ID of the trace to annotate
    - pass_fail: Judgment (pass/fail/defer)
    - open_code: Freeform observation text
    - axial_tags: List of tag IDs
    - reviewer_id: ID of the reviewer
    """
    if annotation.trace_id not in traces_db:
        raise HTTPException(
            status_code=404,
            detail=f"Trace {annotation.trace_id} not found"
        )

    trace = traces_db[annotation.trace_id]

    # Update trace with annotation
    trace.reviewed = True
    trace.pass_fail = annotation.pass_fail
    trace.open_code = annotation.open_code
    trace.axial_tags = annotation.axial_tags
    trace.reviewer_id = annotation.reviewer_id
    trace.reviewed_at = datetime.now()

    return {
        "success": True,
        "trace": trace
    }


@router.put("/{trace_id}")
async def update_annotation(trace_id: str, annotation: AnnotationRequest):
    """
    Update existing annotation.

    Same request body as POST /annotations
    """
    if trace_id not in traces_db:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    if annotation.trace_id != trace_id:
        raise HTTPException(
            status_code=400,
            detail="Trace ID in path must match trace_id in request body"
        )

    trace = traces_db[trace_id]

    # Update trace with new annotation
    trace.reviewed = True
    trace.pass_fail = annotation.pass_fail
    trace.open_code = annotation.open_code
    trace.axial_tags = annotation.axial_tags
    trace.reviewer_id = annotation.reviewer_id
    trace.reviewed_at = datetime.now()

    return {
        "success": True,
        "trace": trace
    }


@router.delete("/{trace_id}")
async def delete_annotation(trace_id: str):
    """Remove annotation from trace."""
    if trace_id not in traces_db:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    trace = traces_db[trace_id]

    # Clear annotation fields
    trace.reviewed = False
    trace.pass_fail = None
    trace.open_code = None
    trace.axial_tags = []
    trace.reviewer_id = None
    trace.reviewed_at = None

    return {
        "success": True,
        "message": f"Annotation removed from trace {trace_id}"
    }
