"""
Pydantic schemas for Evaluation-related API operations.

This module defines the serialization schemas for the Evaluation domain,
including request/response schemas for the evaluation lifecycle.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class EvaluationRequest(BaseModel):
    """
    Request schema for creating a new Evaluation.

    Attributes:
        repo_url: URL of the GitHub repository to evaluate
        rubric_id: ID of the rubric to use for evaluation
        briefing_path: Path to the briefing PDF file
    """

    repo_url: str
    rubric_id: int
    briefing_path: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "repo_url": "https://github.com/student/backend-project",
                    "rubric_id": 1,
                    "briefing_path": "/data/briefings/project-briefing.pdf",
                }
            ]
        }
    }


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class EvaluationResponse(BaseModel):
    """
    Response schema for Evaluation data.

    Represents the basic evaluation information returned after creation
    or when listing evaluations.

    Attributes:
        id: Unique identifier for the evaluation
        rubric_id: ID of the rubric used for evaluation
        repo_url: URL of the evaluated repository
        status: Current status - 'pending', 'processing', 'completed', 'failed'
        total_score: Aggregated score (null until completed)
        ai_summary: AI-generated summary (null until completed)
        created_at: Timestamp of evaluation creation
    """

    id: int
    rubric_id: int
    repo_url: str
    status: str
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponseWithFindings(BaseModel):
    """
    Response schema for detailed Evaluation data with nested findings.

    Used when full evaluation details are needed, including all
    individual criterion findings.

    Attributes:
        id: Unique identifier for the evaluation
        rubric_id: ID of the rubric used for evaluation
        repo_url: URL of the evaluated repository
        status: Current status - 'pending', 'processing', 'completed', 'failed'
        total_score: Aggregated score (null until completed)
        ai_summary: AI-generated summary (null until completed)
        created_at: Timestamp of evaluation creation
        findings: List of individual criterion findings (empty until completed)
    """

    id: int
    rubric_id: int
    repo_url: str
    status: str
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    findings: List["FindingResponse"] = []

    class Config:
        from_attributes = True


class FindingResponse(BaseModel):
    """
    Response schema for Finding data.

    Represents a single criterion evaluation result (WHIS finding).

    Attributes:
        id: Unique identifier for the finding
        criterion_id: ID of the criterion being evaluated
        selected_level_id: ID of the selected scoring level
        file_path: Location in repository where evidence was found
        evidence_snippet: Code excerpt demonstrating the finding
        improvement_suggestion: Recommended action for improvement
    """

    id: int
    criterion_id: int
    selected_level_id: Optional[int] = None
    file_path: Optional[str] = None
    evidence_snippet: Optional[str] = None
    improvement_suggestion: Optional[str] = None

    class Config:
        from_attributes = True


# Update forward references
EvaluationResponseWithFindings.model_rebuild()