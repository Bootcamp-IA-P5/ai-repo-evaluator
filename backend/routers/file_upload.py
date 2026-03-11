"""
File Upload Router - API endpoints for file upload operations.

This module defines the FastAPI router for file upload operations,
specifically for uploading briefing PDF files to the backend.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel

from core.settings import settings
from services.file_upload_service import FileUploadService


class UploadResponse(BaseModel):
    """Response model for file upload operations."""
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[list] = None


# Router configuration
router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}{settings.EVALUATIONS_ROUTE_PREFIX}",
    tags=["File Upload"],
)


def get_file_upload_service() -> FileUploadService:
    """
    Dependency injection provider for FileUploadService.

    Returns a new instance of FileUploadService for each request,
    following FastAPI's dependency injection pattern.

    Returns:
        FileUploadService: A new service instance
    """
    return FileUploadService()


# =============================================================================
# FILE UPLOAD ENDPOINTS
# =============================================================================


@router.post(
    settings.BRIEFING_UPLOAD_ENDPOINT,
    response_model=UploadResponse,
    summary="Upload briefing file",
    description="Upload a PDF briefing file to the backend server.",
    responses={
        400: {
            "description": "Bad request - invalid file or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "File validation failed",
                        "errors": ["File size must be less than 5MB"],
                        "data": None
                    }
                }
            },
        },
        413: {
            "description": "File too large",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "File too large",
                        "errors": ["File size must be less than 5MB"],
                        "data": None
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Failed to upload file",
                        "errors": ["Failed to save file to server"],
                        "data": None
                    }
                }
            },
        },
    },
)
async def upload_briefing_file(
    file: UploadFile = File(...),
    file_upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """
    Upload a briefing PDF file to the backend server.
    
    The file is saved to the <FILE_UPLOAD_PATH> directory and the server-side
    path is returned for use in evaluation creation.
    
    Args:
        file: The PDF file to upload
        file_upload_service: File upload service dependency
        
    Returns:
        UploadResponse with success status and file path on success,
        or error information on failure.
    """
    return file_upload_service.upload_briefing_file(file)


