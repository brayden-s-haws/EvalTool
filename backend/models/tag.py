"""Axial tag model for structured failure categories."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AxialTag(BaseModel):
    """Represents a structured failure category."""

    id: str = Field(..., description="Unique identifier for the tag")
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Short, descriptive tag name"
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=200,
        description="Explanation of what failures belong in this category"
    )
    color: str = Field(
        default="#808080",
        description="Hex color code for visual distinction"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When this tag was created"
    )
    usage_count: int = Field(
        default=0,
        ge=0,
        description="Number of traces with this tag"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Sample open codes assigned this tag"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "tag_001",
                "name": "Hallucinated Metadata",
                "description": "Agent invented facts or attributes not present in source data",
                "color": "#EF4444",
                "usage_count": 12,
                "examples": [
                    "Claimed solar panels when listing has none",
                    "Stated product is sugar-free when it contains sugar"
                ]
            }
        }
