"""
Centralized API response messages.

This module provides a resource-based structure for all API response messages,
making it easy to maintain consistency and support internationalization in the future.

Usage:
    from core.messages import Messages
    
    message=Messages.Rubric.LIST_RETRIEVED
    message=Messages.Generic.NOT_FOUND.format(resource="Rubric")
"""


class Messages:
    """Centralized API response messages organized by resource."""

    class Rubric:
        """Rubric-related messages."""

        LIST_RETRIEVED = "Rubrics retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve rubrics"
        RETRIEVED = "Rubric retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve rubric"
        NOT_FOUND = "Rubric not found"
        NOT_FOUND_DETAIL = "Rubric with id {id} not found"

        # Future: POST/PUT/DELETE messages
        CREATED = "Rubric created successfully"
        CREATE_FAILED = "Failed to create rubric"
        UPDATED = "Rubric updated successfully"
        UPDATE_FAILED = "Failed to update rubric"
        DELETED = "Rubric deleted successfully"
        DELETE_FAILED = "Failed to delete rubric"

    class Evaluation:
        """Evaluation-related messages (for future use)."""

        LIST_RETRIEVED = "Evaluations retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve evaluations"
        RETRIEVED = "Evaluation retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve evaluation"
        NOT_FOUND = "Evaluation not found"
        NOT_FOUND_DETAIL = "Evaluation with id {id} not found"

        CREATED = "Evaluation created successfully"
        CREATE_FAILED = "Failed to create evaluation"

    class Finding:
        """Finding-related messages (for future use)."""

        LIST_RETRIEVED = "Findings retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve findings"
        RETRIEVED = "Finding retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve finding"
        NOT_FOUND = "Finding not found"
        NOT_FOUND_DETAIL = "Finding with id {id} not found"

    class Criterion:
        """Criterion-related messages (for future use)."""

        LIST_RETRIEVED = "Criteria retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve criteria"
        RETRIEVED = "Criterion retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve criterion"
        NOT_FOUND = "Criterion not found"
        NOT_FOUND_DETAIL = "Criterion with id {id} not found"

    class Level:
        """Level-related messages (for future use)."""

        LIST_RETRIEVED = "Levels retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve levels"
        RETRIEVED = "Level retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve level"
        NOT_FOUND = "Level not found"
        NOT_FOUND_DETAIL = "Level with id {id} not found"

    class Generic:
        """Generic reusable messages with placeholders."""

        NOT_FOUND = "{resource} not found"
        RETRIEVED = "{resource} retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve {resource}"
        CREATED = "{resource} created successfully"
        CREATE_FAILED = "Failed to create {resource}"
        UPDATED = "{resource} updated successfully"
        UPDATE_FAILED = "Failed to update {resource}"
        DELETED = "{resource} deleted successfully"
        DELETE_FAILED = "Failed to delete {resource}"
        INVALID_ID = "Invalid {resource} id: {id}"

        # Validation errors
        VALIDATION_ERROR = "Validation error"
        INVALID_PATH_PARAMETER = "Invalid path parameter"
        INVALID_QUERY_PARAMETER = "Invalid query parameter"
        INVALID_REQUEST_BODY = "Invalid request body"

    class Error:
        """HTTP error messages."""

        BAD_REQUEST = "Bad request"
        UNAUTHORIZED = "Unauthorized"
        FORBIDDEN = "Forbidden"
        NOT_FOUND = "Resource not found"
        METHOD_NOT_ALLOWED = "Method not allowed"
        INTERNAL_SERVER_ERROR = "Internal server error"
