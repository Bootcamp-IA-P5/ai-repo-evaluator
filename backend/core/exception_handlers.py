"""
Custom exception handlers for standardized API responses.

This module provides exception handlers that convert FastAPI's default
error responses into our standardized APIResponse format.

Usage:
    from fastapi import FastAPI
    from core.exception_handlers import register_exception_handlers
    
    app = FastAPI()
    register_exception_handlers(app)
"""

from typing import List
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas.response import APIResponse
from core.messages import Messages
from core.logging_config import logger


def _format_validation_errors(errors: List[dict]) -> List[str]:
    """
    Format validation errors into readable strings.

    Args:
        errors: List of error dictionaries from RequestValidationError

    Returns:
        List of formatted error messages
    """
    formatted_errors = []
    for error in errors:
        # Get the location (path, query, body, etc.)
        loc = error.get("loc", [])
        loc_str = ".".join(str(item) for item in loc if item != "body")

        # Get the error message
        msg = error.get("msg", "Invalid value")

        # Get the error type
        error_type = error.get("type", "")

        # Format based on error type
        if "int_parsing" in error_type:
            formatted_errors.append(f"{loc_str}: Must be a valid integer")
        elif "float_parsing" in error_type:
            formatted_errors.append(f"{loc_str}: Must be a valid number")
        elif "missing" in error_type:
            formatted_errors.append(f"{loc_str}: This field is required")
        else:
            formatted_errors.append(f"{loc_str}: {msg}")

    return formatted_errors


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle RequestValidationError (422) with standardized APIResponse format.

    Args:
        request: The FastAPI request object
        exc: The RequestValidationError exception

    Returns:
        JSONResponse with APIResponse format
    """
    errors = _format_validation_errors(exc.errors())

    logger.warning(f"Validation error on {request.method} {request.url.path}: {errors}")

    response = APIResponse(
        success=False,
        data=None,
        errors=errors,
        message=Messages.Generic.VALIDATION_ERROR,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTPException with standardized APIResponse format.

    Args:
        request: The FastAPI request object
        exc: The HTTPException exception

    Returns:
        JSONResponse with APIResponse format
    """
    # Map status codes to messages
    message_map = {
        status.HTTP_400_BAD_REQUEST: Messages.Error.BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED: Messages.Error.UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: Messages.Error.FORBIDDEN,
        status.HTTP_404_NOT_FOUND: Messages.Error.NOT_FOUND,
        status.HTTP_405_METHOD_NOT_ALLOWED: Messages.Error.METHOD_NOT_ALLOWED,
        status.HTTP_500_INTERNAL_SERVER_ERROR: Messages.Error.INTERNAL_SERVER_ERROR,
    }

    message = message_map.get(exc.status_code, exc.detail or "An error occurred")

    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {message}")

    response = APIResponse(
        success=False,
        data=None,
        errors=[exc.detail] if exc.detail else None,
        message=message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all custom exception handlers on the FastAPI app.

    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    logger.debug("Custom exception handlers registered")