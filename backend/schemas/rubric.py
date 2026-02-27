"""
Pydantic schemas for Rubric-related API operations.

This module defines the serialization schemas for the Rubric domain,
including nested relationships with Criterion and Level entities.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# =============================================================================
# LEVEL SCHEMAS
# =============================================================================


class LevelResponse(BaseModel):
    """
    Response schema for Level data.

    Represents a scoring level within a criterion (e.g., 'Excellent', 'Satisfactory').
    """

    id: int
    criterion_id: int
    level_title: str
    level_description: Optional[str] = None
    score_points: float

    class Config:
        from_attributes = True


# =============================================================================
# CRITERION SCHEMAS
# =============================================================================


class CriterionResponse(BaseModel):
    """
    Response schema for Criterion data without nested levels.

    Represents a single evaluation dimension within a rubric.
    """

    id: int
    rubric_id: int
    title: str
    description: Optional[str] = None
    weight: float = 1.0

    class Config:
        from_attributes = True


class CriterionResponseWithLevels(BaseModel):
    """
    Response schema for Criterion data with nested scoring levels.

    Used when detailed criterion information is needed, including
    all available scoring options.
    """

    id: int
    rubric_id: int
    title: str
    description: Optional[str] = None
    weight: float = 1.0
    levels: List[LevelResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# RUBRIC SCHEMAS
# =============================================================================


class RubricResponse(BaseModel):
    """
    Response schema for basic Rubric data in list responses.

    Contains the core rubric fields without nested relationships,
    suitable for list views and summaries.
    """

    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RubricResponseWithCriteria(BaseModel):
    """
    Response schema for detailed Rubric data with nested criteria and levels.

    Used when full rubric details are needed, including all evaluation
    criteria and their scoring levels.
    """

    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    criteria: List[CriterionResponseWithLevels] = []

    class Config:
        from_attributes = True


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


class RubricRequest(BaseModel):
    """Request schema for creating a new Rubric with nested criteria and levels."""

    title: str
    description: Optional[str] = None
    criteria: List[CriterionRequest] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Python Backend Project",
                    "description": "Evaluates backend architecture, code quality, and best practices",
                    "criteria": [
                        {
                            "title": "Error Handling",
                            "description": "Evaluates the completeness of error handling",
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
                        },
                        {
                            "title": "Code Quality",
                            "description": "Evaluates code organization and readability",
                            "weight": 1.5,
                            "levels": [
                                {
                                    "level_title": "Excellent",
                                    "level_description": "Clean, well-documented code following PEP 8",
                                    "score_points": 4.0,
                                },
                                {
                                    "level_title": "Satisfactory",
                                    "level_description": "Readable code with minor style issues",
                                    "score_points": 3.0,
                                },
                                {
                                    "level_title": "Insufficient",
                                    "level_description": "Poorly organized or undocumented code",
                                    "score_points": 1.0,
                                },
                            ],
                        },
                    ],
                }
            ]
        }
    }
