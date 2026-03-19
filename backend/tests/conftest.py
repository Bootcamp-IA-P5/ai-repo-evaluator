"""
Pytest fixtures for AI Repository Evaluator tests.

This module provides shared fixtures for database setup, sessions,
and test data generation for use across all test modules.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Rubric, Criterion, Level


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


@pytest.fixture
def evaluation_service():
    """
    Create an EvaluationServiceAPI instance for testing.

    Returns:
        EvaluationServiceAPI: A service instance
    """
    from services.evaluation_service_api import EvaluationServiceAPI

    return EvaluationServiceAPI()


@pytest.fixture
def sample_evaluations(db_session: Session, sample_rubrics: list):
    """
    Create multiple sample evaluations for testing list operations.

    Args:
        db_session: The database session fixture
        sample_rubrics: List of sample rubrics to associate with evaluations

    Returns:
        list[Evaluation]: A list of sample evaluation instances
    """
    from models import Evaluation

    evaluations = [
        Evaluation(
            rubric_id=sample_rubrics[0].id,
            repo_url="https://github.com/test/repo1",
            briefing_snapshot='[{"test": "data"}]',
            status="pending",
        ),
        Evaluation(
            rubric_id=sample_rubrics[1].id,
            repo_url="https://github.com/test/repo2",
            briefing_snapshot='[{"test": "data"}]',
            status="completed",
            total_score=3.5,
            ai_summary="Test summary for repo2",
        ),
        Evaluation(
            rubric_id=sample_rubrics[2].id,
            repo_url="https://github.com/test/repo3",
            briefing_snapshot='[{"test": "data"}]',
            status="failed",
        ),
    ]
    db_session.add_all(evaluations)
    db_session.commit()
    for evaluation in evaluations:
        db_session.refresh(evaluation)
    return evaluations


@pytest.fixture
def evaluation_with_findings(db_session: Session, rubric_with_criteria):
    """
    Create an evaluation with nested findings for testing.

    This fixture creates a complete evaluation structure including:
    - 1 Evaluation
    - 2 Findings (one for each criterion)
    - Associated with rubric criteria

    Args:
        db_session: The database session fixture
        rubric_with_criteria: A rubric with nested criteria

    Returns:
        Evaluation: An evaluation instance with nested findings
    """
    from models import Evaluation, Finding

    evaluation = Evaluation(
        rubric_id=rubric_with_criteria.id,
        repo_url="https://github.com/test/repo",
        briefing_snapshot='[{"test": "data"}]',
        status="completed",
        total_score=3.5,
        ai_summary="Test summary",
    )
    db_session.add(evaluation)
    db_session.commit()
    db_session.refresh(evaluation)

    # Create findings for each criterion
    for criterion in rubric_with_criteria.criteria:
        # Get the first level for this criterion
        level = criterion.levels[0]
        
        finding = Finding(
            evaluation_id=evaluation.id,
            criterion_id=criterion.id,
            selected_level_id=level.id,
            file_path=f"/src/{criterion.title.lower().replace(' ', '_')}.py",
            evidence_snippet=f"def {criterion.title.lower().replace(' ', '_')}_function(): pass",
            improvement_suggestion=f"Add more comprehensive {criterion.title.lower()}",
        )
        db_session.add(finding)

    db_session.commit()
    db_session.refresh(evaluation)
    return evaluation
