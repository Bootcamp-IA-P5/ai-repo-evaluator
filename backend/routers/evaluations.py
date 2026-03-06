"""
Evaluation Router - API endpoints for Evaluation operations.

This module defines the FastAPI router for evaluation-related endpoints,
using dependency injection for both database sessions and service instances.
"""

from typing import List
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from core.database import get_db, SQLALCHEMY_DATABASE_URL
from core.settings import settings
from schemas.response import APIResponse
from schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    EvaluationResponseWithFindings,
)
from services.evaluation_service_api import EvaluationServiceAPI


# Router configuration
router = APIRouter(
    prefix=settings.EVALUATIONS_ROUTE_PREFIX,
    tags=[settings.EVALUATIONS_TAG],
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


def get_evaluation_service_api() -> EvaluationServiceAPI:
    """
    Dependency injection provider for EvaluationServiceAPI.

    Returns a new instance of EvaluationServiceAPI for each request,
    following FastAPI's dependency injection pattern.

    Returns:
        EvaluationServiceAPI: A new service instance
    """
    return EvaluationServiceAPI()


# =============================================================================
# GET ENDPOINTS
# =============================================================================


@router.get(
    "/",
    response_model=APIResponse[List[EvaluationResponse]],
    summary="List all evaluations",
    description="Retrieve a list of all evaluations without their nested findings.",
    responses={
        422: RESPONSE_422,
    },
)
def list_evaluations(
    db: Session = Depends(get_db),
    evaluation_service: EvaluationServiceAPI = Depends(get_evaluation_service_api),
):
    """
    Retrieve all evaluations from the database.

    Returns a list of evaluations with basic information
    (id, rubric_id, repo_url, status, total_score, ai_summary, created_at).
    Does not include nested findings - use GET /evaluations/{id} for full details.
    """
    return evaluation_service.get_all(db)


@router.get(
    "/{evaluation_id}",
    response_model=APIResponse[EvaluationResponseWithFindings],
    summary="Get evaluation by ID",
    description="Retrieve a single evaluation with all its findings.",
    responses={
        404: RESPONSE_404,
        422: RESPONSE_422,
    },
)
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    evaluation_service: EvaluationServiceAPI = Depends(get_evaluation_service_api),
):
    """
    Retrieve a specific evaluation by ID with full details.

    Returns the evaluation including all nested findings (WHIS data points).
    Returns an error if the evaluation is not found.
    """
    return evaluation_service.get_by_id(db, evaluation_id)


# =============================================================================
# POST ENDPOINTS
# =============================================================================


@router.post(
    "/",
    response_model=APIResponse[EvaluationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new evaluation",
    description=(
        "Create a new evaluation for a GitHub repository. "
        "The evaluation is processed in the background - returns immediately with status 'pending'."
    ),
    responses={
        404: {
            "description": "Rubric not found",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "errors": ["Rubric with id 999 not found"],
                        "message": "Rubric not found",
                    }
                }
            },
        },
        422: RESPONSE_422,
    },
)
def create_evaluation(
    evaluation_request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    evaluation_service: EvaluationServiceAPI = Depends(get_evaluation_service_api),
):
    """
    Create a new evaluation.

    Validates that the rubric exists, processes the briefing PDF for RAG context,
    creates an evaluation record with status 'pending', and queues a background
    task for AI processing.

    The endpoint returns immediately with HTTP 201 and the pending evaluation.
    The actual AI evaluation happens asynchronously in the background.

    Status lifecycle:
    - 'pending': Evaluation created, waiting to be processed
    - 'processing': AI evaluation in progress
    - 'completed': Evaluation finished successfully
    - 'failed': Evaluation encountered an error
    """
    return evaluation_service.create(
        db=db,
        evaluation_request=evaluation_request,
        background_tasks=background_tasks,
        db_url=SQLALCHEMY_DATABASE_URL,
    )