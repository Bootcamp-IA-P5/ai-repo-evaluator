"""
Pydantic schemas for Evaluation-related API operations.

This module defines the serialization schemas for the Evaluation domain,
including request/response schemas for the evaluation lifecycle.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator


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
        ai_provider: AI provider to use (openai, gemini, groq) - optional
        ai_model: Specific model for the provider - optional
        ai_api_key: API key for the provider - optional
    """

    repo_url: str
    rubric_id: int
    briefing_path: str
    ai_provider: Optional[str] = Field(None, description="AI provider: openai, gemini, or grok")
    ai_model: Optional[str] = Field(None, description="Specific model for the selected provider")
    ai_api_key: Optional[str] = Field(None, description="API key for the selected provider")
    embedding_provider: Optional[str] = Field(None, description="Embedding provider: gemini or openai")
    embedding_model: Optional[str] = Field(None, description="Embedding model name")

    @field_validator('ai_provider')
    @classmethod
    def validate_ai_provider(cls, v):
        """Validate that ai_provider is one of the supported providers."""
        if v is not None:
            valid_providers = ['openai', 'gemini', 'grok']
            if v not in valid_providers:
                raise ValueError(f"ai_provider must be one of: {', '.join(valid_providers)}")
        return v
        
    @field_validator('embedding_provider')
    @classmethod
    def validate_embedding_provider(cls, v):
        """Validate that embedding_provider is one of the supported providers."""
        if v is not None:
            valid_providers = ['openai', 'gemini']
            if v not in valid_providers:
                raise ValueError(f"embedding_provider must be one of: {', '.join(valid_providers)}")
        return v

    @field_validator('ai_model')
    @classmethod
    def validate_ai_model(cls, v, info):
        """Validate that ai_model is provided when ai_provider is specified."""
        # Get the ai_provider value from the current instance
        ai_provider = info.data.get('ai_provider')
        if ai_provider is not None and v is None:
            raise ValueError("ai_model is required when ai_provider is specified")
        return v

    @field_validator('ai_api_key')
    @classmethod
    def validate_ai_api_key(cls, v, info):
        """Validate that ai_api_key is provided when ai_provider is specified."""
        # Get the ai_provider value from the current instance
        ai_provider = info.data.get('ai_provider')
        if ai_provider is not None and v is None:
            raise ValueError("ai_api_key is required when ai_provider is specified")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "repo_url": "https://github.com/student/backend-project",
                    "rubric_id": 1,
                    "briefing_path": "<FILE_UPLOAD_PATH>/project-briefing.pdf",
                },
                {
                    "repo_url": "https://github.com/student/backend-project",
                    "rubric_id": 1,
                    "briefing_path": "<FILE_UPLOAD_PATH>/project-briefing.pdf",
                    "ai_provider": "openai",
                    "ai_model": "gpt-4",
                    "ai_api_key": "sk-example-api-key"
                },
                {
                    "repo_url": "https://github.com/student/backend-project",
                    "rubric_id": 1,
                    "briefing_path": "<FILE_UPLOAD_PATH>/project-briefing.pdf",
                    "ai_provider": "gemini",
                    "ai_model": "gemini-1.5-pro",
                    "ai_api_key": "AIza-example-api-key"
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

    model_config = ConfigDict(from_attributes=True)

    id: int
    rubric_id: int
    repo_url: str
    status: str
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    created_at: datetime


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

    model_config = ConfigDict(from_attributes=True)

    id: int
    rubric_id: int
    repo_url: str
    status: str
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    findings: List["FindingResponse"] = []


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

    model_config = ConfigDict(from_attributes=True)

    id: int
    criterion_id: int
    selected_level_id: Optional[int] = None
    file_path: Optional[str] = None
    evidence_snippet: Optional[str] = None
    improvement_suggestion: Optional[str] = None


# Update forward references
EvaluationResponseWithFindings.model_rebuild()