"""Prompt improvement API endpoints using Claude."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from anthropic import Anthropic

router = APIRouter()


class PromptImprovementRequest(BaseModel):
    """Request model for prompt improvement suggestions."""

    current_prompt: str
    target_failure_modes: List[str]
    additional_context: Optional[str] = None
    num_suggestions: int = 3


class PromptSuggestion(BaseModel):
    """A single prompt improvement suggestion."""

    version: int
    improved_prompt: str
    changes_made: List[str]
    targeted_failures: List[str]


@router.post("/suggest")
async def generate_suggestions(request: PromptImprovementRequest):
    """
    Generate prompt improvement suggestions using Claude API.

    Request Body:
    - current_prompt: The existing system prompt
    - target_failure_modes: List of failure mode tag IDs to address
    - additional_context: Optional extra guidance
    - num_suggestions: Number of variations to generate (default: 3)
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY not configured"
        )

    try:
        # Import tags and traces to get failure mode details
        from routes.tags import tags_db
        from routes.traces import traces_db

        # Gather failure mode details
        failure_modes_text = []
        for tag_id in request.target_failure_modes:
            if tag_id in tags_db:
                tag = tags_db[tag_id]
                examples = []

                # Find traces with this tag and get their open codes
                for trace in traces_db.values():
                    if tag_id in trace.axial_tags and trace.open_code:
                        examples.append(trace.open_code)

                failure_modes_text.append(
                    f"**{tag.name}**: {tag.description}\n"
                    f"Examples:\n" + "\n".join(f"- {ex}" for ex in examples[:3])
                )

        failure_modes_str = "\n\n".join(failure_modes_text)

        # Build prompt for Claude
        prompt = f"""You are an expert in prompt engineering for LLM systems. I will provide:
1. A current system prompt
2. A list of observed failure modes with specific examples
3. Any additional context about the system

Your task: Generate {request.num_suggestions} improved versions of the system prompt that specifically address the identified failure modes while preserving the original intent and functionality.

For each improved prompt:
- Explain what changes you made and why
- Highlight the specific language or instructions that target each failure mode
- Maintain the overall structure and tone of the original prompt

Current System Prompt:
{request.current_prompt}

Observed Failure Modes and Examples:
{failure_modes_str}

Additional Context:
{request.additional_context or "None provided"}

Please provide {request.num_suggestions} improved prompt variations in JSON format:
{{
  "suggestions": [
    {{
      "version": 1,
      "improved_prompt": "...",
      "changes_made": ["Change 1", "Change 2", ...],
      "targeted_failures": ["Failure Mode 1", "Failure Mode 2", ...]
    }},
    ...
  ]
}}"""

        # Call Claude API
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response
        response_text = response.content[0].text

        # Try to extract JSON from response
        # Look for JSON block between ```json and ``` or just parse the whole thing
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            # Try to find JSON object directly
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]

        result = json.loads(json_str)

        return result

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse Claude response as JSON: {str(e)}\nResponse: {response_text[:500]}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )
