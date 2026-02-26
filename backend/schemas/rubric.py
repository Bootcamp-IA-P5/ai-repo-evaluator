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
# REQUEST SCHEMAS (For future POST/PUT operations)
# =============================================================================


class LevelRequest(BaseModel):
    """Request schema for creating a new Level."""

    level_title: str
    level_description: Optional[str] = None
    score_points: float


class CriterionRequest(BaseModel):
    """Request schema for creating a new Criterion."""

    title: str
    description: Optional[str] = None
    weight: float = 1.0
    levels: List[LevelRequest] = []


class RubricRequest(BaseModel):
    """Request schema for creating a new Rubric with nested criteria and levels."""

    title: str
    description: Optional[str] = None
    criteria: List[CriterionRequest] = []