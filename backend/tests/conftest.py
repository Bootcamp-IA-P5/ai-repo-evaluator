"""
Pytest fixtures for AI Repository Evaluator tests.

This module provides shared fixtures for database setup, sessions,
and test data generation for use across all test modules.
"""

import sys
import os
from datetime import datetime

# Set environment variables needed by pydantic Settings before any app modules are imported.
# This ensures Settings can be instantiated safely during module import/collection.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key")
os.environ.setdefault("OPENAI_MODEL", "gpt-4")
os.environ.setdefault("GEMINI_API_KEY", "fake-gemini-key")
os.environ.setdefault("GEMINI_MODEL", "gemini-pro")
os.environ.setdefault("GROQ_API_KEY", "fake-groq-key")
os.environ.setdefault("GROQ_MODEL", "groq-1")
os.environ.setdefault("EMBEDDING_API_KEY", "fake-embedding-key")
os.environ.setdefault("EMBEDDING_MODEL", "text-embedding-3-small")

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Rubric, Criterion, Level


# =============================================================================
# ENVIRONMENT FIXTURES
# =============================================================================
# Environment variables are now set at import time above, before any app modules
# (such as core.settings) are imported. No additional fixture-based setup is needed.

# =============================================================================
# DATABASE FIXTURES
# =============================================================================


@pytest.fixture
def test_engine():
    """
    Create an in-memory SQLite database engine for testing.

    This fixture creates a fresh database schema for each test,
    ensuring complete isolation between tests.

    Yields:
        Engine: SQLAlchemy engine connected to in-memory SQLite
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """
    Create a database session for each test.

    This fixture provides a clean session that is automatically
    closed after each test, ensuring proper cleanup.

    Args:
        test_engine: The test database engine fixture

    Yields:
        Session: SQLAlchemy session for database operations
    """
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.close()


# =============================================================================
# RUBRIC FIXTURES
# =============================================================================


@pytest.fixture
def sample_rubric(db_session: Session):
    """
    Create a single sample rubric for testing.

    Args:
        db_session: The database session fixture

    Returns:
        Rubric: A sample rubric instance
    """
    rubric = Rubric(
        title="Sample Rubric",
        description="A sample rubric for testing",
    )
    db_session.add(rubric)
    db_session.commit()
    db_session.refresh(rubric)
    return rubric


@pytest.fixture
def sample_rubrics(db_session: Session):
    """
    Create multiple sample rubrics for testing list operations.

    Args:
        db_session: The database session fixture

    Returns:
        list[Rubric]: A list of sample rubric instances
    """
    rubrics = [
        Rubric(title="Rubric 1", description="First rubric"),
        Rubric(title="Rubric 2", description="Second rubric"),
        Rubric(title="Rubric 3", description="Third rubric"),
    ]
    db_session.add_all(rubrics)
    db_session.commit()
    for rubric in rubrics:
        db_session.refresh(rubric)
    return rubrics


@pytest.fixture
def rubric_with_criteria(db_session: Session):
    """
    Create a rubric with nested criteria and levels for testing.

    This fixture creates a complete rubric structure including:
    - 1 Rubric
    - 2 Criteria
    - 3 Levels per criterion

    Args:
        db_session: The database session fixture

    Returns:
        Rubric: A rubric instance with nested criteria and levels
    """
    rubric = Rubric(
        title="Complete Rubric",
        description="A rubric with criteria and levels",
    )
    db_session.add(rubric)
    db_session.commit()
    db_session.refresh(rubric)

    # Create criteria
    criterion1 = Criterion(
        rubric_id=rubric.id,
        title="Code Quality",
        description="Evaluates code quality",
        weight=1.0,
    )
    criterion2 = Criterion(
        rubric_id=rubric.id,
        title="Documentation",
        description="Evaluates documentation",
        weight=0.5,
    )
    db_session.add_all([criterion1, criterion2])
    db_session.commit()
    db_session.refresh(criterion1)
    db_session.refresh(criterion2)

    # Create levels for criterion1
    levels_c1 = [
        Level(
            criterion_id=criterion1.id,
            level_title="Excellent",
            level_description="Code is well-structured and clean",
            score_points=4.0,
        ),
        Level(
            criterion_id=criterion1.id,
            level_title="Good",
            level_description="Code is readable with minor issues",
            score_points=3.0,
        ),
        Level(
            criterion_id=criterion1.id,
            level_title="Needs Improvement",
            level_description="Code has quality issues",
            score_points=2.0,
        ),
    ]

    # Create levels for criterion2
    levels_c2 = [
        Level(
            criterion_id=criterion2.id,
            level_title="Excellent",
            level_description="Comprehensive documentation",
            score_points=4.0,
        ),
        Level(
            criterion_id=criterion2.id,
            level_title="Good",
            level_description="Adequate documentation",
            score_points=3.0,
        ),
        Level(
            criterion_id=criterion2.id,
            level_title="Needs Improvement",
            level_description="Missing documentation",
            score_points=2.0,
        ),
    ]

    db_session.add_all(levels_c1 + levels_c2)
    db_session.commit()

    # Refresh to load relationships
    db_session.refresh(rubric)
    return rubric


# =============================================================================
# SERVICE FIXTURES
# =============================================================================


@pytest.fixture
def rubric_service():
    """
    Create a RubricServiceAPI instance for testing.

    Returns:
        RubricServiceAPI: A service instance
    """
    from services.rubric_service_api import RubricServiceAPI

    return RubricServiceAPI()