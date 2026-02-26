"""
Rubric Router - API endpoints for Rubric operations.

This module defines the FastAPI router for rubric-related endpoints,
using dependency injection for both database sessions and service instances.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.settings import settings
from schemas.response import APIResponse
from schemas.rubric import RubricResponse, RubricResponseWithCriteria
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