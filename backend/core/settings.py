"""
Application settings using Pydantic Settings.

This module provides centralized configuration management with:
- Type-safe settings with IDE autocomplete
- Automatic loading from .env file
- Sensible defaults for all values
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from enum import Enum


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    GROK = "grok"


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

    # RAG / Vector Store Configuration. To be obtained from environment
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = ""
    GROK_API_KEY: str = ""
    GROK_MODEL: str = ""
    EMBEDDING_MODEL: str = "models/text-embedding-001"
    FAISS_STORAGE_PATH: str = "/app/storage/faiss"

    # GitLoader Configuration
    CODE_SUFFIXES: list = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".rb", ".go", ".php", ".mjs"]
    TEXT_SUFFIXES: list = [".md", ".txt", ".rst", ".html", ".css", ".sh", ".bat", ".ps1"]
    CONFIG_SUFFIXES: list = [".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".env.example", ".sql"]
    SPECIAL_FILES: set = {"Dockerfile", "Makefile", "Procfile", "Gemfile", ".gitignore", ".dockerignore"}
    IGNORE_DIRS: set = {".git", "node_modules", "__pycache__", ".venv", "venv",
                        ".tox", ".mypy_cache", ".pytest_cache", "dist", "build"}
    IGNORE_FILES: set = {"package-lock.json", "yarn.lock", "poetry.lock", 
                         "Pipfile.lock", "composer.lock", "pnpm-lock.yaml", ".DS_Store"}
    MAX_FILE_SIZE: int = 50_000  # ~50KB

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra environment variables
    )

    @field_validator('OPENAI_API_KEY', 'GEMINI_API_KEY', 'GROK_API_KEY', mode='before')
    @classmethod
    def validate_api_keys(cls, v: str, info) -> str:
        """Validate that API keys are provided."""
        if not v:
            raise ValueError(f"{info.field_name} must be provided in .env file")
        return v
    
    @field_validator('OPENAI_MODEL', 'GEMINI_MODEL', 'GROK_MODEL', mode='before')
    @classmethod
    def validate_models(cls, v: str, info) -> str:
        """Validate that models are provided."""
        if not v:
            raise ValueError(f"{info.field_name} must be provided in .env file")
        return v
    

# Global settings instance
settings = Settings()


def get_api_key(provider: AIProvider) -> str:
    """Get API key for the specified provider."""
    if provider == AIProvider.OPENAI:
        return settings.OPENAI_API_KEY
    elif provider == AIProvider.GEMINI:
        return settings.GEMINI_API_KEY
    elif provider == AIProvider.GROK:
        return settings.GROK_API_KEY
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
    
def get_model(provider: AIProvider) -> str:
    """Get model for the specified provider."""
    if provider == AIProvider.OPENAI:
        return settings.OPENAI_MODEL
    elif provider == AIProvider.GEMINI:
        return settings.GEMINI_MODEL
    elif provider == AIProvider.GROK:
        return settings.GROK_MODEL
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
