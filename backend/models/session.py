"""Session model for review sessions."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .trace import Trace
from .tag import AxialTag


class Session(BaseModel):
    """Represents a review session."""

    id: str = Field(..., description="Unique identifier for the session")
    name: Optional[str] = Field(
        default=None,
        description="Optional session name (auto-generated if not provided)"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the session was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
    traces: List[Trace] = Field(
        default_factory=list,
        description="All traces in this session"
    )
    axial_tags: List[AxialTag] = Field(
        default_factory=list,
        description="All axial tags defined in this session"
    )

    # Session metadata
    mode: str = Field(
        default="combined",
        description="Review mode: 'open_coding', 'axial_coding', or 'combined'"
    )
    current_trace_index: int = Field(
        default=0,
        ge=0,
        description="Index of the current trace being reviewed"
    )
    total_traces: int = Field(
        default=0,
        ge=0,
        description="Total number of traces in the session"
    )
    reviewed_count: int = Field(
        default=0,
        ge=0,
        description="Number of traces that have been reviewed"
    )
    passed_count: int = Field(
        default=0,
        ge=0,
        description="Number of traces marked as pass"
    )
    failed_count: int = Field(
        default=0,
        ge=0,
        description="Number of traces marked as fail"
    )
    deferred_count: int = Field(
        default=0,
        ge=0,
        description="Number of traces deferred for later"
    )

    # Configuration
    randomize_order: bool = Field(
        default=False,
        description="Whether to randomize trace order"
    )
    source: str = Field(
        default="upload",
        description="Source of traces: 'upload', 'braintrust', 'demo'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "session_abc123",
                "name": "Snack Recommendations Q4 2024",
                "mode": "combined",
                "total_traces": 50,
                "reviewed_count": 25,
                "passed_count": 15,
                "failed_count": 8,
                "deferred_count": 2,
                "source": "demo"
            }
        }
