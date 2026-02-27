"""
Application settings using Pydantic Settings.

This module provides centralized configuration management with:
- Type-safe settings with IDE autocomplete
- Automatic loading from .env file
- Sensible defaults for all values
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have sensible defaults but can be overridden
    via environment variables or .env file.
    """

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    APP_TITLE: str = "Evaluador RAG API"
    APP_DESCRIPTION: str = "Automated GitHub Repository Grading with RAG"
    APP_VERSION: str = "1.0.0"

    # Route Configuration - Rubrics
    RUBRICS_ROUTE_PREFIX: str = "/rubrics"
    RUBRICS_TAG: str = "Rubrics"

    # Route Configuration - Evaluations
    EVALUATIONS_ROUTE_PREFIX: str = "/evaluations"
    EVALUATIONS_TAG: str = "Evaluations"

    # Route Configuration - System
    HEALTH_CHECK_PATH: str = "/health"
    ROOT_PATH: str = "/"

    # Evaluation Status Constants
    EVALUATION_STATUS_PENDING: str = "pending"
    EVALUATION_STATUS_PROCESSING: str = "processing"
    EVALUATION_STATUS_COMPLETED: str = "completed"
    EVALUATION_STATUS_FAILED: str = "failed"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()