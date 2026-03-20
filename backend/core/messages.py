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
        DUPLICATE_TITLE = "A rubric with this title already exists"
        UPDATED = "Rubric updated successfully"
        UPDATE_FAILED = "Failed to update rubric"
        DELETED = "Rubric deleted successfully"
        DELETE_FAILED = "Failed to delete rubric"

    class Evaluation:
        """Evaluation-related messages."""

        LIST_RETRIEVED = "Evaluations retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve evaluations"
        RETRIEVED = "Evaluation retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve evaluation"
        NOT_FOUND = "Evaluation not found"
        NOT_FOUND_DETAIL = "Evaluation with id {id} not found"

        CREATED = "Evaluation created successfully"
        CREATE_FAILED = "Failed to create evaluation"
        UPDATED = "Evaluation updated successfully"
        UPDATE_FAILED = "Failed to update evaluation"
        DELETED = "Evaluation deleted successfully"
        DELETE_FAILED = "Failed to delete evaluation"

        # AI Summary Messages
        AI_SUMMARY_PENDING = "Evaluation completed. AI integration pending."
        AI_SUMMARY_FAILED = "Evaluation failed: {error}"

    class Finding:
        """Finding-related messages."""

        LIST_RETRIEVED = "Findings retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve findings"
        RETRIEVED = "Finding retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve finding"
        NOT_FOUND = "Finding not found"
        NOT_FOUND_DETAIL = "Finding with id {id} not found"
        CREATED = "Finding created successfully"
        CREATE_FAILED = "Failed to create finding"
        UPDATED = "Finding updated successfully"
        UPDATE_FAILED = "Failed to update finding"
        DELETED = "Finding deleted successfully"
        DELETE_FAILED = "Failed to delete finding"

    class Criterion:
        """Criterion-related messages."""

        LIST_RETRIEVED = "Criteria retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve criteria"
        RETRIEVED = "Criterion retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve criterion"
        NOT_FOUND = "Criterion not found"
        NOT_FOUND_DETAIL = "Criterion with id {id} not found"
        CREATED = "Criterion created successfully"
        CREATE_FAILED = "Failed to create criterion"
        UPDATED = "Criterion updated successfully"
        UPDATE_FAILED = "Failed to update criterion"
        DELETED = "Criterion deleted successfully"
        DELETE_FAILED = "Failed to delete criterion"

    class Level:
        """Level-related messages."""

        LIST_RETRIEVED = "Levels retrieved successfully"
        LIST_RETRIEVE_FAILED = "Failed to retrieve levels"
        RETRIEVED = "Level retrieved successfully"
        RETRIEVE_FAILED = "Failed to retrieve level"
        NOT_FOUND = "Level not found"
        NOT_FOUND_DETAIL = "Level with id {id} not found"
        CREATED = "Level created successfully"
        CREATE_FAILED = "Failed to create level"
        UPDATED = "Level updated successfully"
        UPDATE_FAILED = "Failed to update level"
        DELETED = "Level deleted successfully"
        DELETE_FAILED = "Failed to delete level"

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

    class AIProvider:
        """AI provider-related error messages."""

        UNSUPPORTED = "Unsupported AI provider: {provider}"
        INITIALIZATION_FAILED = "Failed to initialize {provider} client: {error}"
        API_KEY_MISSING = "API key for {provider} is missing or invalid"
        MODEL_NOT_FOUND = "Model '{model}' not found for provider {provider}"

    class AIRepository:
        """Repository-related error messages."""

        CLONING_FAILED = "Failed to clone repository {repo_url}: {error}"
        PROCESSING_FAILED = "Failed to process repository code: {error}"
        INVALID_URL = "Invalid repository URL: {repo_url}"
        ACCESS_DENIED = "Access denied to repository {repo_url}: {error}"

    class AIRubric:
        """Rubric-related error messages."""

        NOT_FOUND = "Rubric {rubric_id} not found"
        LOADING_FAILED = "Failed to load rubric {rubric_id}: {error}"
        INVALID_STRUCTURE = "Invalid rubric structure for rubric {rubric_id}: {error}"
        NO_CRITERIA = "Rubric {rubric_id} has no criteria defined"

    class AIEvaluation:
        """Evaluation-related error messages."""

        EVALUATION_FAILED = "Evaluation failed: {error}"
        CRITERION_EVALUATION_FAILED = "Failed to evaluate criterion '{criterion_title}': {error}"
        AI_SUMMARY_GENERATION_FAILED = "Failed to generate AI summary: {error}"
        INVALID_FINDING_DATA = "Invalid finding data for criterion {criterion_id}: {error}"
        PARSING_RESPONSE_FAILED = "Failed to parse AI response: {error}"

    class AIRAG:
        """RAG (Retrieval-Augmented Generation) related error messages."""

        CONTEXT_PREPARATION_FAILED = "Failed to prepare RAG context: {error}"
        CHUNKING_FAILED = "Failed to chunk briefing document: {error}"
        SIMILARITY_SEARCH_FAILED = "Failed to find relevant context chunks: {error}"
