"""
Pydantic schemas for Rubric-related API operations.

This module defines the serialization schemas for the Rubric domain,
including nested relationships with Criterion and Level entities.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# =============================================================================
# LEVEL SCHEMAS
# =============================================================================


class LevelResponse(BaseModel):
    """
    Response schema for Level data.

    Represents a scoring level within a criterion (e.g., 'Excellent', 'Satisfactory').
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    criterion_id: int
    level_title: str
    level_description: Optional[str] = None
    score_points: float


# =============================================================================
# CRITERION SCHEMAS
# =============================================================================


class CriterionResponse(BaseModel):
    """
    Response schema for Criterion data without nested levels.

    Represents a single evaluation dimension within a rubric.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    rubric_id: int
    title: str
    description: Optional[str] = None
    weight: float = 1.0


class CriterionResponseWithLevels(BaseModel):
    """
    Response schema for Criterion data with nested scoring levels.

    Used when detailed criterion information is needed, including
    all available scoring options.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    rubric_id: int
    title: str
    description: Optional[str] = None
    weight: float = 1.0
    levels: List[LevelResponse] = []


# =============================================================================
# RUBRIC SCHEMAS
# =============================================================================


class RubricResponse(BaseModel):
    """
    Response schema for basic Rubric data in list responses.

    Contains the core rubric fields without nested relationships,
    suitable for list views and summaries.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime


class RubricResponseWithCriteria(BaseModel):
    """
    Response schema for detailed Rubric data with nested criteria and levels.

    Used when full rubric details are needed, including all evaluation
    criteria and their scoring levels.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    criteria: List[CriterionResponseWithLevels] = []


# =============================================================================
# REQUEST SCHEMAS (For POST/PUT operations)
# =============================================================================


class LevelRequest(BaseModel):
    """Request schema for creating a new Level."""

    level_title: str
    level_description: Optional[str] = None
    score_points: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "level_title": "Excellent",
                    "level_description": "Comprehensive error handling with logging and custom exceptions",
                    "score_points": 4.0,
                }
            ]
        }
    }


class CriterionRequest(BaseModel):
    """Request schema for creating a new Criterion."""

    title: str
    description: Optional[str] = None
    weight: float = 1.0
    levels: List[LevelRequest] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Error Handling",
                    "description": "Evaluates the completeness and quality of error handling",
                    "weight": 1.0,
                    "levels": [
                        {
                            "level_title": "Excellent",
                            "level_description": "Comprehensive error handling with logging",
                            "score_points": 4.0,
                        },
                        {
                            "level_title": "Satisfactory",
                            "level_description": "Basic error handling present",
                            "score_points": 3.0,
                        },
                        {
                            "level_title": "Insufficient",
                            "level_description": "Minimal or no error handling",
                            "score_points": 1.0,
                        },
                    ],
                }
            ]
        }
    }


class CriterionUpdateRequest(BaseModel):
    """Request schema for updating an existing Criterion."""

    title: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    levels: Optional[List[LevelRequest]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated Error Handling",
                    "description": "Updated description",
                    "weight": 1.5,
                }
            ]
        }
    }


class LevelUpdateRequest(BaseModel):
    """Request schema for updating an existing Level."""

    level_title: Optional[str] = None
    level_description: Optional[str] = None
    score_points: Optional[float] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "level_title": "Excellent (Updated)",
                    "level_description": "Updated description",
                    "score_points": 5.0,
                }
            ]
        }
    }


class RubricRequest(BaseModel):
    """Request schema for creating a new Rubric with nested criteria and levels."""

    title: str
    description: Optional[str] = None
    criteria: List[CriterionRequest] = []


class RubricUpdateRequest(BaseModel):
    """Request schema for updating rubric metadata only (title and description)."""

    title: Optional[str] = None
    description: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Python Backend Project (Updated)",
                    "description": "Updated evaluation criteria for backend projects",
                }
            ]
        }
    }
