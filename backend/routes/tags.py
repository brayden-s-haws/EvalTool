"""Axial tag management API endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from models import AxialTag
from routes.traces import traces_db
import uuid

router = APIRouter()

# In-memory storage for tags
tags_db: dict[str, AxialTag] = {}


class TagCreateRequest(BaseModel):
    """Request model for creating a tag."""

    name: str
    description: str
    color: str = "#808080"


class TagMergeRequest(BaseModel):
    """Request model for merging tags."""

    source_tag_id: str
    target_tag_id: str


@router.get("/")
async def get_tags():
    """Retrieve all axial tags."""
    return {
        "tags": list(tags_db.values())
    }


@router.post("/")
async def create_tag(tag_request: TagCreateRequest):
    """
    Create new axial tag.

    Request Body:
    - name: Tag name (2-30 characters)
    - description: Tag description (20-200 characters)
    - color: Hex color code (optional)
    """
    # Check for duplicate name
    for existing_tag in tags_db.values():
        if existing_tag.name.lower() == tag_request.name.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Tag with name '{tag_request.name}' already exists"
            )

    tag = AxialTag(
        id=f"tag_{uuid.uuid4().hex[:8]}",
        name=tag_request.name,
        description=tag_request.description,
        color=tag_request.color,
        created_at=datetime.now()
    )

    tags_db[tag.id] = tag

    return {
        "success": True,
        "tag": tag
    }


@router.put("/{tag_id}")
async def update_tag(tag_id: str, tag_request: TagCreateRequest):
    """
    Update tag properties.

    Request Body:
    - name: New tag name
    - description: New description
    - color: New color
    """
    if tag_id not in tags_db:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

    tag = tags_db[tag_id]

    # Check for duplicate name (excluding current tag)
    for existing_tag in tags_db.values():
        if (existing_tag.id != tag_id and
            existing_tag.name.lower() == tag_request.name.lower()):
            raise HTTPException(
                status_code=400,
                detail=f"Tag with name '{tag_request.name}' already exists"
            )

    tag.name = tag_request.name
    tag.description = tag_request.description
    tag.color = tag_request.color

    return {
        "success": True,
        "tag": tag
    }


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    untag_traces: bool = Query(True, description="Remove tag from all traces")
):
    """
    Delete tag and optionally untag all traces.

    Query Parameters:
    - untag_traces: Whether to remove tag from all traces (default: true)
    """
    if tag_id not in tags_db:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

    traces_affected = 0

    if untag_traces:
        for trace in traces_db.values():
            if tag_id in trace.axial_tags:
                trace.axial_tags.remove(tag_id)
                traces_affected += 1

    del tags_db[tag_id]

    return {
        "success": True,
        "traces_affected": traces_affected
    }


@router.post("/merge")
async def merge_tags(merge_request: TagMergeRequest):
    """
    Merge two tags into one.

    Request Body:
    - source_tag_id: Tag to merge from (will be deleted)
    - target_tag_id: Tag to merge into (will be kept)
    """
    if merge_request.source_tag_id not in tags_db:
        raise HTTPException(
            status_code=404,
            detail=f"Source tag {merge_request.source_tag_id} not found"
        )

    if merge_request.target_tag_id not in tags_db:
        raise HTTPException(
            status_code=404,
            detail=f"Target tag {merge_request.target_tag_id} not found"
        )

    source_tag = tags_db[merge_request.source_tag_id]
    target_tag = tags_db[merge_request.target_tag_id]

    # Update all traces with source tag to have target tag instead
    traces_affected = 0
    for trace in traces_db.values():
        if merge_request.source_tag_id in trace.axial_tags:
            trace.axial_tags.remove(merge_request.source_tag_id)
            if merge_request.target_tag_id not in trace.axial_tags:
                trace.axial_tags.append(merge_request.target_tag_id)
            traces_affected += 1

    # Update target tag usage count and examples
    target_tag.usage_count += source_tag.usage_count
    target_tag.examples.extend(source_tag.examples)

    # Delete source tag
    del tags_db[merge_request.source_tag_id]

    return {
        "success": True,
        "merged_tag": target_tag,
        "traces_affected": traces_affected
    }
