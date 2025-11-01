"""Trace management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from models import Trace

router = APIRouter()

# In-memory storage for demo (replace with database in production)
traces_db: dict[str, Trace] = {}


@router.get("/", response_model=dict)
async def get_traces(
    reviewed: Optional[bool] = Query(None, description="Filter by review status"),
    pass_fail: Optional[str] = Query(None, description="Filter by judgment (pass/fail/defer)")
):
    """
    Retrieve all traces in current session.

    Query Parameters:
    - reviewed: Filter by review status (true/false)
    - pass_fail: Filter by judgment (pass/fail/defer)
    """
    filtered_traces = list(traces_db.values())

    if reviewed is not None:
        filtered_traces = [t for t in filtered_traces if t.reviewed == reviewed]

    if pass_fail:
        filtered_traces = [t for t in filtered_traces if t.pass_fail == pass_fail]

    return {
        "traces": filtered_traces,
        "count": len(filtered_traces)
    }


@router.get("/{trace_id}", response_model=Trace)
async def get_trace(trace_id: str):
    """Retrieve single trace by ID."""
    if trace_id not in traces_db:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    return traces_db[trace_id]


@router.post("/import")
async def import_traces(data: dict):
    """
    Import traces from JSON file.

    Request Body:
    - traces: List of Trace objects
    - session_config: Optional session configuration
    """
    try:
        imported_traces = [Trace(**trace_data) for trace_data in data.get("traces", [])]

        for trace in imported_traces:
            traces_db[trace.id] = trace

        return {
            "success": True,
            "imported_count": len(imported_traces),
            "session_id": data.get("session_config", {}).get("session_id", "default")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import traces: {str(e)}")


@router.delete("/{trace_id}")
async def delete_trace(trace_id: str):
    """Delete a trace."""
    if trace_id not in traces_db:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    del traces_db[trace_id]
    return {"success": True, "message": f"Trace {trace_id} deleted"}
