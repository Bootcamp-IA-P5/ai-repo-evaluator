"""
Unit tests for EvaluationServiceAPI.

This module contains comprehensive tests for the EvaluationServiceAPI class,
covering all CRUD operations and error handling scenarios.
"""
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from services.evaluation_service_api import EvaluationServiceAPI
from schemas.response import APIResponse
from schemas.evaluation import EvaluationResponse, EvaluationResponseWithFindings
from core.messages import Messages


class TestEvaluationServiceAPIGetAll:
    """Tests for EvaluationServiceAPI.get_all() method."""

    def test_get_all_success_empty(self, db_session: Session, evaluation_service: EvaluationServiceAPI):
        """Test get_all returns empty list when no evaluations exist."""
        response = evaluation_service.get_all(db_session)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert response.data == []
        assert response.errors is None
        assert response.message == Messages.Evaluation.LIST_RETRIEVED

    def test_get_all_success_with_data(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_all returns list of evaluations when data exists."""
        response = evaluation_service.get_all(db_session)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert len(response.data) == 3
        assert response.errors is None
        assert response.message == Messages.Evaluation.LIST_RETRIEVED

        # Verify data structure
        for item in response.data:
            assert isinstance(item, EvaluationResponse)
            assert hasattr(item, "id")
            assert hasattr(item, "repo_url")
            assert hasattr(item, "status")

    def test_get_all_returns_correct_repo_urls(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_all returns evaluations with correct repo URLs."""
        response = evaluation_service.get_all(db_session)

        repo_urls = [e.repo_url for e in response.data]
        assert "https://github.com/test/repo1" in repo_urls
        assert "https://github.com/test/repo2" in repo_urls
        assert "https://github.com/test/repo3" in repo_urls

    def test_get_all_database_error(self, evaluation_service: EvaluationServiceAPI):
        """Test get_all handles database errors gracefully."""
        # Create a mock session that raises an exception
        mock_session = MagicMock(spec=Session)
        mock_session.query.side_effect = Exception("Database connection error")

        response = evaluation_service.get_all(mock_session)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert "Database connection error" in response.errors[0]
        assert response.message == Messages.Evaluation.LIST_RETRIEVE_FAILED


class TestEvaluationServiceAPIGetById:
    """Tests for EvaluationServiceAPI.get_by_id() method."""

    def test_get_by_id_success(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_by_id returns evaluation when found."""
        evaluation = sample_evaluations[0]
        response = evaluation_service.get_by_id(db_session, evaluation.id)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, EvaluationResponseWithFindings)
        assert response.data.id == evaluation.id
        assert response.data.repo_url == evaluation.repo_url
        assert response.errors is None
        assert response.message == Messages.Evaluation.RETRIEVED

    def test_get_by_id_not_found(self, db_session: Session, evaluation_service: EvaluationServiceAPI):
        """Test get_by_id returns error when evaluation not found."""
        non_existent_id = 99999
        response = evaluation_service.get_by_id(db_session, non_existent_id)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert str(non_existent_id) in response.errors[0]
        assert response.message == Messages.Evaluation.NOT_FOUND

    def test_get_by_id_with_findings(
        self, db_session: Session, evaluation_with_findings, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_by_id returns evaluation with nested findings."""
        response = evaluation_service.get_by_id(db_session, evaluation_with_findings.id)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, EvaluationResponseWithFindings)
        assert response.data.id == evaluation_with_findings.id

        # Verify nested findings
        assert len(response.data.findings) == 2
        finding_titles = [f.file_path for f in response.data.findings]
        assert "/src/code_quality.py" in finding_titles
        assert "/src/documentation.py" in finding_titles

    def test_get_by_id_includes_score_and_summary(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_by_id includes evaluation score and summary."""
        evaluation = sample_evaluations[1]  # This one has score and summary
        response = evaluation_service.get_by_id(db_session, evaluation.id)

        assert response.success is True
        assert response.data.total_score == evaluation.total_score
        assert response.data.ai_summary == evaluation.ai_summary

    def test_get_by_id_database_error(self, evaluation_service: EvaluationServiceAPI):
        """Test get_by_id handles database errors gracefully."""
        # Create a mock session that raises an exception
        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        response = evaluation_service.get_by_id(mock_session, 1)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert "Database error" in response.errors[0]
        assert response.message == Messages.Evaluation.RETRIEVE_FAILED


class TestEvaluationServiceAPICreate:
    """Tests for EvaluationServiceAPI.create() method."""

    def test_create_rubric_not_found(self, db_session: Session, evaluation_service: EvaluationServiceAPI):
        """Test create returns error when rubric not found."""
        from schemas.evaluation import EvaluationRequest

        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=99999,
            briefing_path="/path/to/briefing.pdf",
        )

        response = evaluation_service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Rubric.NOT_FOUND

    @patch("services.evaluation_service_api.BriefingProcessor")
    def test_create_briefing_file_not_found(
        self, mock_processor, db_session: Session, sample_rubric, evaluation_service: EvaluationServiceAPI
    ):
        """Test create returns error when briefing file not found."""
        from schemas.evaluation import EvaluationRequest

        mock_processor.side_effect = FileNotFoundError("File not found")

        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=sample_rubric.id,
            briefing_path="/nonexistent/briefing.pdf",
        )

        response = evaluation_service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is False
        assert "not found" in response.errors[0].lower()
        assert response.message == "Failed to process briefing"

    @patch("services.evaluation_service_api.BriefingProcessor")
    def test_create_success(
        self, mock_processor_class, db_session: Session, sample_rubric, evaluation_service: EvaluationServiceAPI
    ):
        """Test create returns created evaluation with pending status."""
        from schemas.evaluation import EvaluationRequest

        # Mock the BriefingProcessor
        mock_processor = MagicMock()
        # Return a list with a mock Document-like object that has page_content
        mock_doc = MagicMock()
        mock_doc.page_content = "test chunk content"
        mock_doc.metadata = {"source": "test.pdf"}
        mock_processor.process.return_value = [mock_doc]
        mock_processor_class.return_value = mock_processor

        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=sample_rubric.id,
            briefing_path="/path/to/briefing.pdf",
        )

        response = evaluation_service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

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
    def test_create_with_ai_provider(
        self, mock_processor_class, db_session: Session, sample_rubric, evaluation_service: EvaluationServiceAPI
    ):
        """Test create with AI provider parameters."""
        from schemas.evaluation import EvaluationRequest

        # Mock the BriefingProcessor
        mock_processor = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "test chunk content"
        mock_doc.metadata = {"source": "test.pdf"}
        mock_processor.process.return_value = [mock_doc]
        mock_processor_class.return_value = mock_processor

        mock_background_tasks = MagicMock(spec=BackgroundTasks)

        eval_request = EvaluationRequest(
            repo_url="https://github.com/test/repo",
            rubric_id=sample_rubric.id,
            briefing_path="/path/to/briefing.pdf",
            ai_provider="openai",
            ai_model="gpt-4",
            ai_api_key="test-key",
        )

        response = evaluation_service.create(db_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is True
        assert response.data.repo_url == "https://github.com/test/repo"
        assert response.message == Messages.Evaluation.CREATED

    @patch("services.evaluation_service_api.BriefingProcessor")
    def test_create_database_error(
        self, mock_processor_class, evaluation_service: EvaluationServiceAPI
    ):
        """Test create handles database errors gracefully."""
        from schemas.evaluation import EvaluationRequest

        # Mock the BriefingProcessor to return proper Document-like objects
        mock_processor = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "test chunk content"
        mock_doc.metadata = {"source": "test.pdf"}
        mock_processor.process.return_value = [mock_doc]
        mock_processor_class.return_value = mock_processor

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

        response = evaluation_service.create(mock_session, eval_request, mock_background_tasks, "sqlite:///:memory:")

        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert response.message == Messages.Evaluation.CREATE_FAILED


class TestEvaluationServiceAPIUpdate:
    """Tests for EvaluationServiceAPI.update() method."""

    def test_update_status_success(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test update modifies evaluation status."""
        from schemas.evaluation import EvaluationUpdateRequest

        evaluation = sample_evaluations[0]
        update_request = EvaluationUpdateRequest(status="completed")

        response = evaluation_service.update(db_session, evaluation.id, update_request)

        assert response.success is True
        assert response.data.status == "completed"
        assert response.data.repo_url == evaluation.repo_url
        assert response.message == Messages.Evaluation.UPDATED

    def test_update_score_and_summary_success(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test update modifies evaluation score and summary."""
        from schemas.evaluation import EvaluationUpdateRequest

        evaluation = sample_evaluations[0]
        update_request = EvaluationUpdateRequest(
            total_score=4.5,
            ai_summary="Updated summary"
        )

        response = evaluation_service.update(db_session, evaluation.id, update_request)

        assert response.success is True
        assert response.data.total_score == 4.5
        assert response.data.ai_summary == "Updated summary"

    def test_update_not_found(self, db_session: Session, evaluation_service: EvaluationServiceAPI):
        """Test update returns error when evaluation not found."""
        from schemas.evaluation import EvaluationUpdateRequest

        update_request = EvaluationUpdateRequest(status="completed")

        response = evaluation_service.update(db_session, 99999, update_request)

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Evaluation.NOT_FOUND

    def test_update_database_error(self, evaluation_service: EvaluationServiceAPI):
        """Test update handles database errors gracefully."""
        from schemas.evaluation import EvaluationUpdateRequest

        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        update_request = EvaluationUpdateRequest(status="completed")

        response = evaluation_service.update(mock_session, 1, update_request)

        assert response.success is False
        assert response.message == Messages.Evaluation.UPDATE_FAILED


class TestEvaluationServiceAPIDelete:
    """Tests for EvaluationServiceAPI.delete() method."""

    def test_delete_success(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test delete removes evaluation from database."""
        evaluation = sample_evaluations[0]
        evaluation_id = evaluation.id

        response = evaluation_service.delete(db_session, evaluation_id)

        assert response.success is True
        assert response.data is None
        assert response.message == Messages.Evaluation.DELETED

        # Verify evaluation is deleted
        from models import Evaluation
        deleted_evaluation = db_session.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        assert deleted_evaluation is None

    def test_delete_not_found(self, db_session: Session, evaluation_service: EvaluationServiceAPI):
        """Test delete returns error when evaluation not found."""
        response = evaluation_service.delete(db_session, 99999)

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Evaluation.NOT_FOUND

    def test_delete_cascades_to_findings(
        self, db_session: Session, evaluation_with_findings, evaluation_service: EvaluationServiceAPI
    ):
        """Test delete cascades to associated findings."""
        from models import Finding

        evaluation_id = evaluation_with_findings.id
        finding_ids = [f.id for f in evaluation_with_findings.findings]

        response = evaluation_service.delete(db_session, evaluation_id)

        assert response.success is True

        # Verify findings are deleted
        remaining_findings = db_session.query(Finding).filter(
            Finding.evaluation_id == evaluation_id
        ).all()
        assert len(remaining_findings) == 0

    def test_delete_database_error(self, evaluation_service: EvaluationServiceAPI):
        """Test delete handles database errors gracefully."""
        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        response = evaluation_service.delete(mock_session, 1)

        assert response.success is False
        assert response.message == Messages.Evaluation.DELETE_FAILED


class TestEvaluationServiceAPIResponseFormat:
    """Tests for APIResponse format consistency."""

    def test_response_format_on_success(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test that successful response follows APIResponse format."""
        evaluation = sample_evaluations[0]
        response = evaluation_service.get_by_id(db_session, evaluation.id)

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

    def test_response_format_on_error(self, db_session: Session, evaluation_service: EvaluationServiceAPI):
        """Test that error response follows APIResponse format."""
        response = evaluation_service.get_by_id(db_session, 99999)

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

    def test_get_all_response_data_is_list(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test that get_all returns data as a list."""
        response = evaluation_service.get_all(db_session)

        assert response.success is True
        assert isinstance(response.data, list)
        assert len(response.data) > 0


class TestFindingServiceAPI:
    """Tests for finding CRUD operations."""

    def test_get_finding_by_id_success(
        self, db_session: Session, evaluation_with_findings, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_finding_by_id returns finding data."""
        finding = evaluation_with_findings.findings[0]

        response = evaluation_service.get_finding_by_id(
            db_session, evaluation_with_findings.id, finding.id
        )

        assert response.success is True
        assert response.data.id == finding.id
        assert response.data.file_path == finding.file_path
        assert response.data.evidence_snippet == finding.evidence_snippet
        assert response.data.improvement_suggestion == finding.improvement_suggestion
        assert response.message == Messages.Finding.RETRIEVED

    def test_get_finding_by_id_not_found(
        self, db_session: Session, evaluation_with_findings, evaluation_service: EvaluationServiceAPI
    ):
        """Test get_finding_by_id returns error when not found."""
        response = evaluation_service.get_finding_by_id(
            db_session, evaluation_with_findings.id, 99999
        )

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Finding.NOT_FOUND

    def test_create_finding_success(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test create_finding adds finding to evaluation."""
        from schemas.evaluation import FindingRequest

        evaluation = sample_evaluations[0]
        finding_request = FindingRequest(
            criterion_id=1,
            selected_level_id=1,
            file_path="/src/test.py",
            evidence_snippet="def test_function(): pass",
            improvement_suggestion="Add more tests",
        )

        response = evaluation_service.create_finding(
            db_session, evaluation.id, finding_request
        )

        assert response.success is True
        assert response.data.file_path == "/src/test.py"
        assert response.data.evidence_snippet == "def test_function(): pass"
        assert response.data.improvement_suggestion == "Add more tests"
        assert response.message == Messages.Finding.CREATED

    def test_create_finding_evaluation_not_found(
        self, db_session: Session, evaluation_service: EvaluationServiceAPI
    ):
        """Test create_finding returns error when evaluation not found."""
        from schemas.evaluation import FindingRequest

        finding_request = FindingRequest(
            criterion_id=1,
            selected_level_id=1,
            file_path="/src/test.py",
            evidence_snippet="def test_function(): pass",
            improvement_suggestion="Add more tests",
        )

        response = evaluation_service.create_finding(db_session, 99999, finding_request)

        assert response.success is False
        assert response.message == Messages.Evaluation.NOT_FOUND

    def test_update_finding_success(
        self, db_session: Session, evaluation_with_findings, evaluation_service: EvaluationServiceAPI
    ):
        """Test update_finding modifies finding."""
        from schemas.evaluation import FindingUpdateRequest

        finding = evaluation_with_findings.findings[0]
        update_request = FindingUpdateRequest(
            file_path="/src/updated.py",
            improvement_suggestion="Updated suggestion",
        )

        response = evaluation_service.update_finding(
            db_session, evaluation_with_findings.id, finding.id, update_request
        )

        assert response.success is True
        assert response.data.file_path == "/src/updated.py"
        assert response.data.improvement_suggestion == "Updated suggestion"
        assert response.message == Messages.Finding.UPDATED

    def test_update_finding_not_found(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test update_finding returns error when not found."""
        from schemas.evaluation import FindingUpdateRequest

        evaluation = sample_evaluations[0]
        update_request = FindingUpdateRequest(
            file_path="/src/updated.py",
        )

        response = evaluation_service.update_finding(
            db_session, evaluation.id, 99999, update_request
        )

        assert response.success is False
        assert response.message == Messages.Finding.NOT_FOUND

    def test_delete_finding_success(
        self, db_session: Session, evaluation_with_findings, evaluation_service: EvaluationServiceAPI
    ):
        """Test delete_finding removes finding."""
        finding = evaluation_with_findings.findings[0]
        finding_id = finding.id

        response = evaluation_service.delete_finding(
            db_session, evaluation_with_findings.id, finding_id
        )

        assert response.success is True
        assert response.data is None
        assert response.message == Messages.Finding.DELETED

    def test_delete_finding_not_found(
        self, db_session: Session, sample_evaluations, evaluation_service: EvaluationServiceAPI
    ):
        """Test delete_finding returns error when not found."""
        evaluation = sample_evaluations[0]

        response = evaluation_service.delete_finding(
            db_session, evaluation.id, 99999
        )

        assert response.success is False
        assert response.message == Messages.Finding.NOT_FOUND