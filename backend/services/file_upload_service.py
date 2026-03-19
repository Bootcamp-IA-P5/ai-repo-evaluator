"""
File Upload Service - Business logic for file upload operations.

This module provides the service layer for file upload operations,
specifically for uploading briefing PDF files to the backend.
"""

from typing import Optional
from fastapi import UploadFile, HTTPException, status
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import re
import os

from core.settings import settings
from core.logging_config import logger
from core.messages import Messages


class UploadResponse(BaseModel):
    """Response model for file upload operations."""
    success: bool
    message: str
    data: Optional[dict] = None
    errors: Optional[list] = None


class FileUploadService:
    """
    Service class for file upload operations.

    This class encapsulates all business logic related to file uploads,
    providing a clean interface for uploading briefing PDF files.
    """

    def upload_briefing_file(self, file: UploadFile) -> UploadResponse:
        """
        Upload a briefing PDF file to the backend server.
        
        The file is saved to the <FILE_UPLOAD_PATH> directory and the server-side
        path is returned for use in evaluation creation.
        
        Args:
            file: The PDF file to upload
            
        Returns:
            UploadResponse with success status and file path on success,
            or error information on failure.
        """
        # Constants
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
        ALLOWED_TYPES = {'.pdf'}
        UPLOAD_DIR = Path(settings.FILE_UPLOAD_PATH)
        
        try:
            # 1. Validate file type
            if not self._validate_file_type(file, ALLOWED_TYPES):
                logger.warning(f"Invalid file type uploaded: {file.filename}")
                return UploadResponse(
                    success=False,
                    message="File validation failed",
                    errors=[f"Please upload a PDF file"],
                    data=None
                )
            
            # 2. Validate file size
            # Read file content to check size
            file_content = file.file.read()
            if not self._validate_file_size(file_content, MAX_FILE_SIZE):
                logger.warning(f"File too large: {file.filename} ({len(file_content)} bytes)")
                return UploadResponse(
                    success=False,
                    message="File too large",
                    errors=[f"File size must be less than 5MB"],
                    data=None
                )
            
            # 3. Ensure upload directory exists
            upload_dir = self._ensure_upload_directory(UPLOAD_DIR)
            
            # 4. Generate safe filename
            safe_filename = self._sanitize_filename(file.filename)
            file_path = upload_dir / safe_filename
            
            # 5. Save file to server
            try:
                server_path = self._save_file_to_server(file_content, file_path)
                
                logger.debug(f"Successfully uploaded briefing file: {file.filename} -> {server_path}")
                
                return UploadResponse(
                    success=True,
                    message="File uploaded successfully",
                    data={
                        "file_path": server_path,
                        "file_name": safe_filename,
                        "file_size": len(file_content)
                    },
                    errors=None
                )
                
            except Exception as e:
                logger.error(f"Failed to save file {file.filename}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save file to server"
                )
                
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )

    def _validate_file_type(self, file: UploadFile, allowed_types: set) -> bool:
        """
        Validate file type is in allowed types.
        
        Args:
            file: The uploaded file
            allowed_types: Set of allowed file extensions
            
        Returns:
            True if file type is valid, False otherwise
        """
        file_extension = Path(file.filename).suffix.lower()
        return file_extension in allowed_types

    def _validate_file_size(self, file_content: bytes, max_size: int) -> bool:
        """
        Validate file size is within limits.
        
        Args:
            file_content: The file content as bytes
            max_size: Maximum allowed file size in bytes
            
        Returns:
            True if file size is valid, False otherwise
        """
        return len(file_content) <= max_size

    def _ensure_upload_directory(self, upload_dir: Path) -> Path:
        """
        Ensure upload directory exists.
        
        Args:
            upload_dir: Path to the upload directory
            
        Returns:
            The upload directory path
        """
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename and add timestamp to ensure uniqueness.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename with timestamp suffix safe for server storage
        """
        # Remove path separators and other dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?* ]', '_', filename)

        # Extract name and extension
        name, ext = os.path.splitext(sanitized)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create unique name with timestamp
        unique_name = f"{name}_{timestamp}{ext}"

        # Handle length limits - ensure total length doesn't exceed filesystem limits
        if len(unique_name) > 255:
            # Calculate maximum allowed name length
            # 255 - timestamp length (15) - extension length - 1 (underscore)
            max_name_length = 255 - len(timestamp) - len(ext) - 1
            if max_name_length > 0:
                name = name[:max_name_length]
                unique_name = f"{name}_{timestamp}{ext}"
            else:
                # Fallback if extension is too long
                unique_name = f"uploaded_file_{timestamp}.pdf"

        # Ensure it's not empty or dangerous
        if not unique_name or unique_name == '.' or unique_name == '..':
            unique_name = f"uploaded_file_{timestamp}.pdf"

        return unique_name

    def _save_file_to_server(self, file_content: bytes, file_path: Path) -> str:
        """
        Save file to server and return server path.
        
        Args:
            file_content: The file content as bytes
            file_path: Path where the file should be saved
            
        Returns:
            Server path to the saved file
        """
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Return the server path
        server_path = f"{settings.FILE_UPLOAD_PATH}/{file_path.name}"
        return server_path