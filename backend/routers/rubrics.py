"""
Rubric Router - API endpoints for Rubric operations.

This module defines the FastAPI router for rubric-related endpoints,
using dependency injection for both database sessions and service instances.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.settings import settings
from schemas.response import APIResponse
from schemas.rubric import (
    RubricResponse,
    RubricResponseWithCriteria,
    RubricRequest,
    RubricUpdateRequest,
    CriterionResponseWithLevels,
    CriterionRequest,
    CriterionUpdateRequest,
    LevelResponse,
    LevelRequest,
    LevelUpdateRequest,
)
from services.rubric_service_api import RubricServiceAPI


# Router configuration
router = APIRouter(
    prefix=settings.RUBRICS_ROUTE_PREFIX,
    tags=[settings.RUBRICS_TAG],
)

# Common response schemas for OpenAPI documentation
RESPONSE_404 = {
    "description": "Resource not found",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "data": None,
                "errors": ["Rubric not found"],
                "message": "Rubric not found",
            }
        }
    },
}

RESPONSE_422 = {
    "description": "Validation error",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "data": None,
                "errors": ["rubric_id: Must be a valid integer"],
                "message": "Validation error",
            }
        }
    },
}


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================


def get_rubric_service_api() -> RubricServiceAPI:
    """
    Dependency injection provider for RubricServiceAPI.

    Returns a new instance of RubricServiceAPI for each request,
    following FastAPI's dependency injection pattern.

    Returns:
        RubricServiceAPI: A new service instance
    """
    return RubricServiceAPI()


# =============================================================================
# GET ENDPOINTS
# =============================================================================


@router.get(
    "/",
    response_model=APIResponse[List[RubricResponse]],
    summary="List all rubrics",
    description="Retrieve a list of all rubrics without their nested criteria.",
    responses={
        422: RESPONSE_422,
    },
)
def list_rubrics(
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Retrieve all rubrics from the database.

    Returns a list of rubrics with basic information (id, title, description, created_at).
    Does not include nested criteria - use GET /rubrics/{id} for full details.
    """
    return rubric_service_api.get_all(db)


@router.get(
    "/{rubric_id}",
    response_model=APIResponse[RubricResponseWithCriteria],
    summary="Get rubric by ID",
    description="Retrieve a single rubric with all its criteria and scoring levels.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def get_rubric(
    rubric_id: int,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Retrieve a specific rubric by ID with full details.

    Returns the rubric including all nested criteria and their scoring levels.
    Returns an error if the rubric is not found.
    """
    return rubric_service_api.get_by_id(db, rubric_id)


# =============================================================================
# POST ENDPOINTS
# =============================================================================


@router.post(
    "/",
    response_model=APIResponse[RubricResponseWithCriteria],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new rubric",
    description="Create a new rubric with optional nested criteria and scoring levels.",
    responses={
        422: RESPONSE_422,
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Python Backend Project",
                        "description": "Evaluation criteria for Python backend projects",
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
                }
            }
        }
    },
)
def create_rubric(
    rubric_request: RubricRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Create a new rubric.

    Accepts a rubric with optional nested criteria and scoring levels.
    Returns the created rubric with all nested relationships.
    """
    return rubric_service_api.create(db, rubric_request)


# =============================================================================
# PUT ENDPOINTS
# =============================================================================


@router.put(
    "/{rubric_id}",
    response_model=APIResponse[RubricResponseWithCriteria],
    summary="Update a rubric",
    description="Update rubric metadata (title and description). Criteria and levels are managed through dedicated endpoints.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Python Backend Project (Updated)",
                        "description": "Updated evaluation criteria for backend projects",
                    }
                }
            }
        }
    },
)
def update_rubric(
    rubric_id: int,
    rubric_request: RubricUpdateRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Update rubric metadata only.

    Only updates title and description. Criteria and levels must be managed
    through their dedicated endpoints:
    - PUT /rubrics/{rubric_id}/criteria/{criterion_id}
    - PUT /rubrics/criteria/{criterion_id}/levels/{level_id}

    Returns the updated rubric with all nested relationships.
    """
    return rubric_service_api.update(db, rubric_id, rubric_request)


# =============================================================================
# DELETE ENDPOINTS
# =============================================================================


@router.delete(
    "/{rubric_id}",
    response_model=APIResponse[None],
    summary="Delete a rubric",
    description="Delete a rubric and all its associated criteria and scoring levels.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def delete_rubric(
    rubric_id: int,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Delete a rubric by ID.

    Cascade deletes all associated criteria and scoring levels.
    Returns a success message on completion.
    """
    return rubric_service_api.delete(db, rubric_id)


# =============================================================================
# CRITERION ENDPOINTS
# =============================================================================


@router.get(
    "/{rubric_id}/criteria/{criterion_id}",
    response_model=APIResponse[CriterionResponseWithLevels],
    summary="Get a specific criterion",
    description="Retrieve a single criterion with all its scoring levels from a rubric.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def get_criterion(
    rubric_id: int,
    criterion_id: int,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Retrieve a specific criterion by ID from a rubric.

    Returns the criterion including all its scoring levels.
    Returns an error if either the rubric or criterion is not found.
    """
    return rubric_service_api.get_criterion_by_id(db, rubric_id, criterion_id)


@router.post(
    "/{rubric_id}/criteria",
    response_model=APIResponse[CriterionResponseWithLevels],
    status_code=status.HTTP_201_CREATED,
    summary="Add a criterion to a rubric",
    description="Create a new criterion within an existing rubric with optional scoring levels.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Documentation",
                        "description": "Evaluates the quality and completeness of documentation",
                        "weight": 1.0,
                        "levels": [
                            {
                                "level_title": "Excellent",
                                "level_description": "Comprehensive README, API docs, and inline comments",
                                "score_points": 4.0,
                            },
                            {
                                "level_title": "Satisfactory",
                                "level_description": "Basic README with setup instructions",
                                "score_points": 3.0,
                            },
                            {
                                "level_title": "Insufficient",
                                "level_description": "Missing or outdated documentation",
                                "score_points": 1.0,
                            },
                        ],
                    }
                }
            }
        }
    },
)
def create_criterion(
    rubric_id: int,
    criterion_request: CriterionRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Add a new criterion to an existing rubric.

    Accepts a criterion with optional nested scoring levels.
    Returns the created criterion with all nested relationships.
    """
    return rubric_service_api.create_criterion(db, rubric_id, criterion_request)


@router.put(
    "/{rubric_id}/criteria/{criterion_id}",
    response_model=APIResponse[CriterionResponseWithLevels],
    summary="Update a criterion",
    description="Update a criterion. Only provided fields will be updated.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Documentation (Updated)",
                        "description": "Updated description for documentation criterion",
                        "weight": 1.5,
                        "levels": [
                            {
                                "level_title": "Excellent",
                                "level_description": "Comprehensive documentation with examples",
                                "score_points": 5.0,
                            },
                            {
                                "level_title": "Good",
                                "level_description": "Clear documentation covering main features",
                                "score_points": 4.0,
                            },
                            {
                                "level_title": "Satisfactory",
                                "level_description": "Basic README with setup instructions",
                                "score_points": 3.0,
                            },
                            {
                                "level_title": "Insufficient",
                                "level_description": "Missing or outdated documentation",
                                "score_points": 1.0,
                            },
                        ],
                    }
                }
            }
        }
    },
)
def update_criterion(
    rubric_id: int,
    criterion_id: int,
    criterion_request: CriterionUpdateRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Update an existing criterion (partial update).

    Only updates the fields that are provided in the request.
    If levels are provided, they replace all existing levels.
    Returns the updated criterion with all nested relationships.
    """
    return rubric_service_api.update_criterion(db, rubric_id, criterion_id, criterion_request)


@router.delete(
    "/{rubric_id}/criteria/{criterion_id}",
    response_model=APIResponse[None],
    summary="Delete a criterion",
    description="Delete a criterion and all its associated scoring levels from a rubric.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def delete_criterion(
    rubric_id: int,
    criterion_id: int,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Delete a criterion by ID from a rubric.

    Cascade deletes all associated scoring levels.
    Returns a success message on completion.
    """
    return rubric_service_api.delete_criterion(db, rubric_id, criterion_id)


# =============================================================================
# LEVEL ENDPOINTS
# =============================================================================


@router.get(
    "/criteria/{criterion_id}/levels/{level_id}",
    response_model=APIResponse[LevelResponse],
    summary="Get a specific level",
    description="Retrieve a single scoring level from a criterion.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def get_level(
    criterion_id: int,
    level_id: int,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Retrieve a specific level by ID from a criterion.

    Returns the level details.
    Returns an error if either the criterion or level is not found.
    """
    return rubric_service_api.get_level_by_id(db, criterion_id, level_id)


@router.post(
    "/criteria/{criterion_id}/levels",
    response_model=APIResponse[LevelResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a level to a criterion",
    description="Create a new scoring level within an existing criterion.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "level_title": "Excellent",
                        "level_description": "Exceeds expectations with exceptional quality",
                        "score_points": 5.0,
                    }
                }
            }
        }
    },
)
def create_level(
    criterion_id: int,
    level_request: LevelRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Add a new scoring level to an existing criterion.

    Accepts a level with title, description, and score points.
    Returns the created level.
    """
    return rubric_service_api.create_level(db, criterion_id, level_request)


@router.put(
    "/criteria/{criterion_id}/levels/{level_id}",
    response_model=APIResponse[LevelResponse],
    summary="Update a level",
    description="Update a scoring level. Only provided fields will be updated.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "level_title": "Excellent (Updated)",
                        "level_description": "Exceeds all expectations with outstanding quality",
                        "score_points": 6.0,
                    }
                }
            }
        }
    },
)
def update_level(
    criterion_id: int,
    level_id: int,
    level_request: LevelUpdateRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Update an existing scoring level (partial update).

    Only updates the fields that are provided in the request.
    Returns the updated level.
    """
    return rubric_service_api.update_level(db, criterion_id, level_id, level_request)


@router.delete(
    "/criteria/{criterion_id}/levels/{level_id}",
    response_model=APIResponse[None],
    summary="Delete a level",
    description="Delete a scoring level from a criterion.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def delete_level(
    criterion_id: int,
    level_id: int,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Delete a scoring level by ID from a criterion.

    Returns a success message on completion.
    """
    return rubric_service_api.delete_level(db, criterion_id, level_id)
