"""
Unit tests for EvaluationServiceAPI.

This module contains comprehensive tests for the EvaluationServiceAPI class,
covering all CRUD operations and error handling scenarios.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from services.evaluation_service_api import EvaluationServiceAPI
from schemas.response import APIResponse
from schemas.evaluation import EvaluationResponse, EvaluationResponseWithFindings
from core.messages import Messages


class TestEvaluationServiceAPIGetAll:
    """Tests for EvaluationServiceAPI.get_all() method."""

    def test_get_all_success_empty(self, db_session: Session):
        """Test get_all returns empty list when no evaluations exist."""
        from services.evaluation_service_api import EvaluationServiceAPI

        service = EvaluationServiceAPI()
        response = service.get_all(db_session)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert response.data == []
        assert response.errors is None
        assert response.message == Messages.Evaluation.LIST_RETRIEVED

    def test_get_all_success_with_data(
        self, db_session: Session, sample_rubric
    ):
        """Test get_all returns list of evaluations when data exists."""
        from models import Evaluation
        from services.evaluation_service_api import EvaluationServiceAPI

        # Create sample evaluations
        eval1 = Evaluation(
            rubric_id=sample_rubric.id,
            repo_url="https://github.com/test/repo1",
            briefing_snapshot='[{"test": "data"}]',
            status="pending",
        )
        eval2 = Evaluation(
            rubric_id=sample_rubric.id,
            repo_url="https://github.com/test/repo2",
            briefing_snapshot='[{"test": "data"}]',
            status="completed",
        )
        db_session.add_all([eval1, eval2])
        db_session.commit()

        service = EvaluationServiceAPI()
        response = service.get_all(db_session)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert len(response.data) == 2
        assert response.errors is None
        assert response.message == Messages.Evaluation.LIST_RETRIEVED

        # Verify data structure
        for item in response.data:
            assert isinstance(item, EvaluationResponse)
            assert hasattr(item, "id")
            assert hasattr(item, "repo_url")
            assert hasattr(item, "status")

    def test_get_all_database_error(self):
        """Test get_all handles database errors gracefully."""
        from services.evaluation_service_api import EvaluationServiceAPI

        service = EvaluationServiceAPI()
        mock_session = MagicMock(spec=Session)
        mock_session.query.side_effect = Exception("Database connection error")

        response = service.get_all(mock_session)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert "Database connection error" in response.errors[0]
        assert response.message == Messages.Evaluation.LIST_RETRIEVE_FAILED


class TestEvaluationServiceAPIGetById:
    """Tests for EvaluationServiceAPI.get_by_id() method."""

    def test_get_by_id_success(self, db_session: Session, sample_rubric):
        """Test get_by_id returns evaluation when found."""
        from models import Evaluation
        from services.evaluation_service_api import EvaluationServiceAPI

        evaluation = Evaluation(
            rubric_id=sample_rubric.id,
            repo_url="https://github.com/test/repo",
            briefing_snapshot='[{"test": "data"}]',
            status="pending",
        )
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)

        service = EvaluationServiceAPI()
        response = service.get_by_id(db_session, evaluation.id)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, EvaluationResponseWithFindings)
        assert response.data.id == evaluation.id
        assert response.data.repo_url == evaluation.repo_url
        assert response.errors is None
        assert response.message == Messages.Evaluation.RETRIEVED

    def test_get_by_id_not_found(self, db_session: Session):
        """Test get_by_id returns error when evaluation not found."""
        from services.evaluation_service_api import EvaluationServiceAPI

        service = EvaluationServiceAPI()
        non_existent_id = 99999
        response = service.get_by_id(db_session, non_existent_id)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert str(non_existent_id) in response.errors[0]
        assert response.message == Messages.Evaluation.NOT_FOUND

    def test_get_by_id_includes_findings(self, db_session: Session, rubric_with_criteria):
        """Test get_by_id returns evaluation with nested findings."""
        from models import Evaluation, Finding
        from services.evaluation_service_api import EvaluationServiceAPI

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

        # Create a finding
        criterion = rubric_with_criteria.criteria[0]
        finding = Finding(
            evaluation_id=evaluation.id,
            criterion_id=criterion.id,
            file_path="/src/main.py",
            evidence_snippet="def example(): pass",
            improvement_suggestion="Add docstring",
        )
        db_session.add(finding)
        db_session.commit()

        service = EvaluationServiceAPI()
        response = service.get_by_id(db_session, evaluation.id)

        assert response.success is True
        assert len(response.data.findings) == 1
        assert response.data.findings[0].file_path == "/src/main.py"

    def test_get_by_id_database_error(self):
        """Test get_by_id handles database errors gracefully."""
        from services.evaluation_service_api import EvaluationServiceAPI

        service = EvaluationServiceAPI()
        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        response = service.get_by_id(mock_session, 1)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert "Database error" in response.errors[0]
        assert response.message == Messages.Evaluation.RETRIEVE_FAILED


class TestEvaluationServiceAPICreate:
    """Tests for EvaluationServiceAPI.create() method."""

    def test_create_rubric_not_found(self, db_session: Session):
        """Test create returns error when rubric not found."""
        from schemas.evaluation import EvaluationRequest
        from services.evaluation_service_api import EvaluationServiceAPI

        service = EvaluationServiceAPI()
        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=99999,
            briefing_path="/path/to/briefing.pdf",
        )

        response = service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Rubric.NOT_FOUND

    @patch("services.evaluation_service_api.BriefingProcessor")
    def test_create_briefing_file_not_found(
        self, mock_processor, db_session: Session, sample_rubric
    ):
        """Test create returns error when briefing file not found."""
        from schemas.evaluation import EvaluationRequest
        from services.evaluation_service_api import EvaluationServiceAPI

        mock_processor.side_effect = FileNotFoundError("File not found")

        service = EvaluationServiceAPI()
        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=sample_rubric.id,
            briefing_path="/nonexistent/briefing.pdf",
        )

        response = service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is False
        assert "not found" in response.errors[0].lower()
        assert response.message == "Failed to process briefing"

    @patch("services.evaluation_service_api.BriefingProcessor")
    def test_create_success(
        self, mock_processor_class, db_session: Session, sample_rubric
    ):
        """Test create returns created evaluation with pending status."""
        from schemas.evaluation import EvaluationRequest
        from services.evaluation_service_api import EvaluationServiceAPI

        # Mock the BriefingProcessor
        mock_processor = MagicMock()
        mock_processor.process.return_value = [{"content": "test chunk"}]
        mock_processor_class.return_value = mock_processor

        service = EvaluationServiceAPI()
        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=sample_rubric.id,
            briefing_path="/path/to/briefing.pdf",
        )

        response = service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, EvaluationResponse)
        assert response.data.repo_url == "https://github.com/test/repo"
        assert response.data.rubric_id == sample_rubric.id
        assert response.data.status == "pending"
        assert response.errors is None
        assert response.message == Messages.Evaluation.CREATED

        # Verify background task was queued
        mock_background_tasks.add_task.assert_called_once()

    @patch("services.evaluation_service_api.BriefingProcessor")
    def test_create_database_error(
        self, mock_processor_class, rubric_service
    ):
        """Test create handles database errors gracefully."""
        from schemas.evaluation import EvaluationRequest
        from services.evaluation_service_api import EvaluationServiceAPI

        mock_processor = MagicMock()
        mock_processor.process.return_value = [{"content": "test"}]
        mock_processor_class.return_value = mock_processor

        service = EvaluationServiceAPI()
        mock_session = MagicMock(spec=Session)
        mock_session.add.side_effect = Exception("Database error")

        # Add rubric query mock
        from models import Rubric
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = Rubric(id=1, title="Test")
        mock_session.query.return_value = mock_query

        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=1,
            briefing_path="/path/to/briefing.pdf",
        )

        response = service.create(mock_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert response.message == Messages.Evaluation.CREATE_FAILED


class TestEvaluationServiceAPIResponseFormat:
    """Tests for APIResponse format consistency."""

    def test_response_format_on_success(self, db_session: Session, sample_rubric):
        """Test that successful response follows APIResponse format."""
        from models import Evaluation
        from services.evaluation_service_api import EvaluationServiceAPI

        evaluation = Evaluation(
            rubric_id=sample_rubric.id,
            repo_url="https://github.com/test/repo",
            briefing_snapshot='[{"test": "data"}]',
            status="pending",
        )
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)

        service = EvaluationServiceAPI()
        response = service.get_by_id(db_session, evaluation.id)

        # Check all required fields exist
        assert hasattr(response, "success")
        assert hasattr(response, "data")
        assert hasattr(response, "errors")
        assert hasattr(response, "message")

        # Check types
        assert isinstance(response.success, bool)
        assert response.success is True
        assert response.errors is None
        assert isinstance(response.message, str)

    def test_response_format_on_error(self, db_session: Session):
        """Test that error response follows APIResponse format."""
        from services.evaluation_service_api import EvaluationServiceAPI

        service = EvaluationServiceAPI()
        response = service.get_by_id(db_session, 99999)

        # Check all required fields exist
        assert hasattr(response, "success")
        assert hasattr(response, "data")
        assert hasattr(response, "errors")
        assert hasattr(response, "message")

        # Check types
        assert isinstance(response.success, bool)
        assert response.success is False
        assert response.data is None
        assert isinstance(response.errors, list)
        assert isinstance(response.message, str)