"""Trace data model for LLM interactions."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    """Represents a single step in a trace (e.g., tool call, LLM response)."""

    step_type: str = Field(
        ...,
        description="Type of step: 'llm_call', 'tool_call', 'retrieval', 'output'"
    )
    content: str = Field(..., description="Content of the step")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the step"
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description="When this step occurred"
    )


class Trace(BaseModel):
    """Complete trace of an LLM interaction."""

    id: str = Field(..., description="Unique identifier for the trace")
    user_input: str = Field(..., description="User's input/prompt")
    agent_output: str = Field(..., description="Agent's final response")
    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt used for this interaction"
    )
    intermediate_steps: List[TraceStep] = Field(
        default_factory=list,
        description="List of intermediate steps (tool calls, reasoning, etc.)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "model_version": None,
            "latency_ms": None,
            "token_count": None,
            "timestamp": None,
            "braintrust_trace_id": None
        },
        description="Metadata about the trace"
    )

    # Review fields (populated during evaluation)
    reviewed: bool = Field(
        default=False,
        description="Whether this trace has been reviewed"
    )
    pass_fail: Optional[str] = Field(
        default=None,
        description="Judgment: 'pass', 'fail', or 'defer'"
    )
    open_code: Optional[str] = Field(
        default=None,
        description="Freeform observation about failures"
    )
    axial_tags: List[str] = Field(
        default_factory=list,
        description="List of axial tag IDs applied to this trace"
    )
    reviewer_id: Optional[str] = Field(
        default=None,
        description="ID of the person who reviewed this trace"
    )
    reviewed_at: Optional[datetime] = Field(
        default=None,
        description="When the trace was reviewed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "trace_001",
                "user_input": "I love spicy kettle chips with a crunchy texture. What else would I like?",
                "agent_output": "Based on your love for spicy kettle chips, here are some recommendations:\n\n1. Takis Fuego - These rolled corn tortilla chips pack serious heat with lime and chili pepper seasoning\n2. Spicy Sweet Chili Doritos - Combines sweet and spicy flavors with that classic Doritos crunch\n3. Paqui Haunted Ghost Pepper Chips - For extreme heat lovers, these kettle-cooked chips deliver intense spiciness",
                "system_prompt": "You are a helpful snack recommendation assistant.",
                "reviewed": True,
                "pass_fail": "pass"
            }
        }
