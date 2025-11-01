"""Session management API endpoints."""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import Session, Trace
from routes.traces import traces_db
from routes.tags import tags_db
import uuid

router = APIRouter()

# In-memory storage for sessions
sessions_db: dict[str, Session] = {}


class SessionCreateRequest(BaseModel):
    """Request model for creating a session."""

    name: Optional[str] = None
    traces: List[Trace] = []
    config: dict = {}


@router.get("/")
async def get_sessions():
    """List all saved sessions."""
    return {
        "sessions": [
            {
                "id": session.id,
                "name": session.name,
                "created_at": session.created_at,
                "total_traces": session.total_traces,
                "reviewed_count": session.reviewed_count,
                "source": session.source
            }
            for session in sessions_db.values()
        ]
    }


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Load specific session."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return sessions_db[session_id]


@router.post("/")
async def create_session(request: SessionCreateRequest):
    """
    Create new session.

    Request Body:
    - name: Optional session name
    - traces: List of traces
    - config: Session configuration
    """
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    # Generate name if not provided
    session_name = request.name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Calculate initial counts
    total_traces = len(request.traces)
    reviewed_count = sum(1 for t in request.traces if t.reviewed)
    passed_count = sum(1 for t in request.traces if t.pass_fail == "pass")
    failed_count = sum(1 for t in request.traces if t.pass_fail == "fail")
    deferred_count = sum(1 for t in request.traces if t.pass_fail == "defer")

    session = Session(
        id=session_id,
        name=session_name,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        traces=request.traces,
        axial_tags=list(tags_db.values()),
        mode=request.config.get("mode", "combined"),
        total_traces=total_traces,
        reviewed_count=reviewed_count,
        passed_count=passed_count,
        failed_count=failed_count,
        deferred_count=deferred_count,
        randomize_order=request.config.get("randomize_order", False),
        source=request.config.get("source", "upload")
    )

    sessions_db[session_id] = session

    # Add traces to traces_db
    for trace in request.traces:
        traces_db[trace.id] = trace

    return {
        "success": True,
        "session": session
    }


@router.put("/{session_id}")
async def update_session(session_id: str, session: Session):
    """Update session (auto-save)."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session.updated_at = datetime.now()

    # Recalculate counts
    session.reviewed_count = sum(1 for t in session.traces if t.reviewed)
    session.passed_count = sum(1 for t in session.traces if t.pass_fail == "pass")
    session.failed_count = sum(1 for t in session.traces if t.pass_fail == "fail")
    session.deferred_count = sum(1 for t in session.traces if t.pass_fail == "defer")

    sessions_db[session_id] = session

    # Update traces in traces_db
    for trace in session.traces:
        traces_db[trace.id] = trace

    return {
        "success": True
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete session."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    del sessions_db[session_id]

    return {
        "success": True
    }
