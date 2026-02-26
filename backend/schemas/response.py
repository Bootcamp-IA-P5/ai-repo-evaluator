"""
Generic API Response wrapper for consistent API responses across all endpoints.

This module provides a standardized response format that all API endpoints
should use to ensure consistency in the API's output structure.

Response Format:
    {
        "success": bool,
        "data": Optional[T],
        "errors": Optional[List[str]],
        "message": str
    }
"""

from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Generic wrapper for all API responses.

    Provides a consistent structure for API responses, making it easy
    for clients to handle both success and error cases uniformly.

    Attributes:
        success: Indicates whether the operation was successful
        data: The response payload (null if success is False)
        errors: List of error messages (null if success is True)
        message: Human-readable message describing the result

    Example (Success):
        APIResponse(
            success=True,
            data=[{"id": 1, "title": "Rubric 1"}],
            errors=None,
            message="Rubrics retrieved successfully"
        )

    Example (Error):
        APIResponse(
            success=False,
            data=None,
            errors=["Rubric with id 999 not found"],
            message="Failed to retrieve rubric"
        )
    """

    success: bool
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    message: str