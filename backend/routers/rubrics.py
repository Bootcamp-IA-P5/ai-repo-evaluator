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
from schemas.rubric import RubricResponse, RubricResponseWithCriteria, RubricRequest
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
    description="Update an existing rubric with its criteria and scoring levels. Performs a full replacement of criteria and levels.",
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
def update_rubric(
    rubric_id: int,
    rubric_request: RubricRequest,
    db: Session = Depends(get_db),
    rubric_service_api: RubricServiceAPI = Depends(get_rubric_service_api),
):
    """
    Update an existing rubric.

    Performs a full replacement of criteria and levels (PUT semantics).
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
