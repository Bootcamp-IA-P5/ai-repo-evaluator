"""
Unit tests for RubricServiceAPI.

This module contains comprehensive tests for the RubricServiceAPI class,
covering all GET operations and error handling scenarios.
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from services.rubric_service_api import RubricServiceAPI
from schemas.response import APIResponse
from schemas.rubric import RubricResponse, RubricResponseWithCriteria
from core.messages import Messages


class TestRubricServiceAPIGetAll:
    """Tests for RubricServiceAPI.get_all() method."""

    def test_get_all_success_empty(self, db_session: Session, rubric_service: RubricServiceAPI):
        """Test get_all returns empty list when no rubrics exist."""
        response = rubric_service.get_all(db_session)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert response.data == []
        assert response.errors is None
        assert response.message == Messages.Rubric.LIST_RETRIEVED

    def test_get_all_success_with_data(
        self, db_session: Session, sample_rubrics: list, rubric_service: RubricServiceAPI
    ):
        """Test get_all returns list of rubrics when data exists."""
        response = rubric_service.get_all(db_session)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert len(response.data) == 3
        assert response.errors is None
        assert response.message == Messages.Rubric.LIST_RETRIEVED

        # Verify data structure
        for item in response.data:
            assert isinstance(item, RubricResponse)
            assert hasattr(item, "id")
            assert hasattr(item, "title")
            assert hasattr(item, "description")

    def test_get_all_returns_correct_titles(
        self, db_session: Session, sample_rubrics: list, rubric_service: RubricServiceAPI
    ):
        """Test get_all returns rubrics with correct titles."""
        response = rubric_service.get_all(db_session)

        titles = [r.title for r in response.data]
        assert "Rubric 1" in titles
        assert "Rubric 2" in titles
        assert "Rubric 3" in titles

    def test_get_all_database_error(self, rubric_service: RubricServiceAPI):
        """Test get_all handles database errors gracefully."""
        # Create a mock session that raises an exception
        mock_session = MagicMock(spec=Session)
        mock_session.query.side_effect = Exception("Database connection error")

        response = rubric_service.get_all(mock_session)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert "Database connection error" in response.errors[0]
        assert response.message == Messages.Rubric.LIST_RETRIEVE_FAILED


class TestRubricServiceAPIGetById:
    """Tests for RubricServiceAPI.get_by_id() method."""

    def test_get_by_id_success(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test get_by_id returns rubric when found."""
        response = rubric_service.get_by_id(db_session, sample_rubric.id)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, RubricResponseWithCriteria)
        assert response.data.id == sample_rubric.id
        assert response.data.title == sample_rubric.title
        assert response.errors is None
        assert response.message == Messages.Rubric.RETRIEVED

    def test_get_by_id_not_found(self, db_session: Session, rubric_service: RubricServiceAPI):
        """Test get_by_id returns error when rubric not found."""
        non_existent_id = 99999
        response = rubric_service.get_by_id(db_session, non_existent_id)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert str(non_existent_id) in response.errors[0]
        assert response.message == Messages.Rubric.NOT_FOUND

    def test_get_by_id_with_criteria(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test get_by_id returns rubric with nested criteria and levels."""
        response = rubric_service.get_by_id(db_session, rubric_with_criteria.id)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, RubricResponseWithCriteria)
        assert response.data.id == rubric_with_criteria.id

        # Verify nested criteria
        assert len(response.data.criteria) == 2
        criterion_titles = [c.title for c in response.data.criteria]
        assert "Code Quality" in criterion_titles
        assert "Documentation" in criterion_titles

        # Verify nested levels within criteria
        for criterion in response.data.criteria:
            assert len(criterion.levels) == 3
            level_titles = [l.level_title for l in criterion.levels]
            assert "Excellent" in level_titles
            assert "Good" in level_titles
            assert "Needs Improvement" in level_titles

    def test_get_by_id_includes_description(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test get_by_id includes rubric description."""
        response = rubric_service.get_by_id(db_session, sample_rubric.id)

        assert response.success is True
        assert response.data.description == sample_rubric.description

    def test_get_by_id_database_error(self, rubric_service: RubricServiceAPI):
        """Test get_by_id handles database errors gracefully."""
        # Create a mock session that raises an exception
        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        response = rubric_service.get_by_id(mock_session, 1)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert "Database error" in response.errors[0]
        assert response.message == Messages.Rubric.RETRIEVE_FAILED


class TestRubricServiceAPIResponseFormat:
    """Tests for APIResponse format consistency."""

    def test_response_format_on_success(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test that successful response follows APIResponse format."""
        response = rubric_service.get_by_id(db_session, sample_rubric.id)

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

    def test_response_format_on_error(self, db_session: Session, rubric_service: RubricServiceAPI):
        """Test that error response follows APIResponse format."""
        response = rubric_service.get_by_id(db_session, 99999)

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
        self, db_session: Session, sample_rubrics, rubric_service: RubricServiceAPI
    ):
        """Test that get_all returns data as a list."""
        response = rubric_service.get_all(db_session)

        assert response.success is True
        assert isinstance(response.data, list)
        assert len(response.data) > 0