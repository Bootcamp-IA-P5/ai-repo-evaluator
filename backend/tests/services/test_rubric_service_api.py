"""
Unit tests for RubricServiceAPI.

This module contains comprehensive tests for the RubricServiceAPI class,
covering all CRUD operations and error handling scenarios.
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


class TestRubricServiceAPICreate:
    """Tests for RubricServiceAPI.create() method."""

    def test_create_success(self, db_session: Session, rubric_service: RubricServiceAPI):
        """Test create returns created rubric with correct data."""
        from schemas.rubric import RubricRequest

        rubric_request = RubricRequest(
            title="New Rubric",
            description="A new rubric for testing",
        )

        response = rubric_service.create(db_session, rubric_request)

        assert isinstance(response, APIResponse)
        assert response.success is True
        assert isinstance(response.data, RubricResponseWithCriteria)
        assert response.data.title == "New Rubric"
        assert response.data.description == "A new rubric for testing"

    def test_create_duplicate_title_fails(
        self, db_session: Session, sample_rubrics: list, rubric_service: RubricServiceAPI
    ):
        """Test that creating a rubric with a duplicate title fails."""
        from schemas.rubric import RubricRequest
        
        # Try to create a rubric with the same title as an existing one
        rubric_request = RubricRequest(
            title="Rubric 1",  # This title already exists in sample_rubrics
            description="Duplicate rubric",
        )
        
        response = rubric_service.create(db_session, rubric_request)
        
        assert response.success is False
        assert response.data is None
        assert Messages.Rubric.DUPLICATE_TITLE in response.errors
        assert response.message == Messages.Rubric.DUPLICATE_TITLE

    def test_create_duplicate_title_case_insensitive_fails(
        self, db_session: Session, sample_rubrics: list, rubric_service: RubricServiceAPI
    ):
        """Test that creating a rubric with a duplicate title (different case) fails."""
        from schemas.rubric import RubricRequest
        
        # Try to create a rubric with the same title but different case
        rubric_request = RubricRequest(
            title="RUBRIC 1",  # This should match "Rubric 1" case-insensitively
            description="Duplicate rubric with different case",
        )
        
        response = rubric_service.create(db_session, rubric_request)
        
        assert response.success is False
        assert response.data is None
        assert Messages.Rubric.DUPLICATE_TITLE in response.errors
        assert response.message == Messages.Rubric.DUPLICATE_TITLE

    def test_create_rubric_with_whitespace_in_title(
        self, db_session: Session, rubric_service: RubricServiceAPI
    ):
        """Test that rubrics with whitespace in titles are handled correctly."""
        from schemas.rubric import RubricRequest
        
        # Create a rubric with whitespace in the title
        rubric_request = RubricRequest(
            title="  Test Rubric  ",  # Title with leading/trailing whitespace
            description="Rubric with whitespace",
        )
        
        response = rubric_service.create(db_session, rubric_request)
        
        assert response.success is True
        assert response.data.title == "  Test Rubric  "  # Whitespace preserved
        
        # Try to create another rubric with the same title (including whitespace)
        rubric_request2 = RubricRequest(
            title="  Test Rubric  ",
            description="Another rubric with same title",
        )
        
        response2 = rubric_service.create(db_session, rubric_request2)
        
        assert response2.success is False
        assert Messages.Rubric.DUPLICATE_TITLE in response2.errors
        assert response.data.id is not None
        assert response.errors is None
        assert response.message == Messages.Rubric.CREATED

    def test_create_with_criteria_and_levels(
        self, db_session: Session, rubric_service: RubricServiceAPI
    ):
        """Test create with nested criteria and levels."""
        from schemas.rubric import RubricRequest, CriterionRequest, LevelRequest

        rubric_request = RubricRequest(
            title="Complete Rubric",
            description="Rubric with criteria",
            criteria=[
                CriterionRequest(
                    title="Code Quality",
                    description="Evaluates code",
                    weight=1.0,
                    levels=[
                        LevelRequest(
                            level_title="Excellent",
                            level_description="Great code",
                            score_points=4.0,
                        ),
                        LevelRequest(
                            level_title="Good",
                            level_description="Decent code",
                            score_points=3.0,
                        ),
                    ],
                ),
            ],
        )

        response = rubric_service.create(db_session, rubric_request)

        assert response.success is True
        assert len(response.data.criteria) == 1
        assert response.data.criteria[0].title == "Code Quality"
        assert len(response.data.criteria[0].levels) == 2

    def test_create_database_error(self, rubric_service: RubricServiceAPI):
        """Test create handles database errors gracefully."""
        from schemas.rubric import RubricRequest

        mock_session = MagicMock(spec=Session)
        # Mock the query to return None (no existing rubric) but add to fail
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        mock_session.add.side_effect = Exception("Database error")

        rubric_request = RubricRequest(title="Test")

        response = rubric_service.create(mock_session, rubric_request)

        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 1
        assert response.message == Messages.Rubric.CREATE_FAILED


class TestRubricServiceAPIUpdate:
    """Tests for RubricServiceAPI.update() method."""

    def test_update_title_success(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test update modifies rubric title."""
        from schemas.rubric import RubricUpdateRequest

        update_request = RubricUpdateRequest(title="Updated Title")

        response = rubric_service.update(db_session, sample_rubric.id, update_request)

        assert response.success is True
        assert response.data.title == "Updated Title"
        assert response.data.description == sample_rubric.description
        assert response.message == Messages.Rubric.UPDATED

    def test_update_description_success(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test update modifies rubric description."""
        from schemas.rubric import RubricUpdateRequest

        update_request = RubricUpdateRequest(description="Updated description")

        response = rubric_service.update(db_session, sample_rubric.id, update_request)

        assert response.success is True
        assert response.data.description == "Updated description"

    def test_update_not_found(self, db_session: Session, rubric_service: RubricServiceAPI):
        """Test update returns error when rubric not found."""
        from schemas.rubric import RubricUpdateRequest

        update_request = RubricUpdateRequest(title="Updated")

        response = rubric_service.update(db_session, 99999, update_request)

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Rubric.NOT_FOUND

    def test_update_database_error(self, rubric_service: RubricServiceAPI):
        """Test update handles database errors gracefully."""
        from schemas.rubric import RubricUpdateRequest

        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        update_request = RubricUpdateRequest(title="Updated")

        response = rubric_service.update(mock_session, 1, update_request)

        assert response.success is False
        assert response.message == Messages.Rubric.UPDATE_FAILED


class TestRubricServiceAPIDelete:
    """Tests for RubricServiceAPI.delete() method."""

    def test_delete_success(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test delete removes rubric from database."""
        rubric_id = sample_rubric.id

        response = rubric_service.delete(db_session, rubric_id)

        assert response.success is True
        assert response.data is None
        assert response.message == Messages.Rubric.DELETED

        # Verify rubric is deleted
        from models import Rubric
        deleted_rubric = db_session.query(Rubric).filter(Rubric.id == rubric_id).first()
        assert deleted_rubric is None

    def test_delete_not_found(self, db_session: Session, rubric_service: RubricServiceAPI):
        """Test delete returns error when rubric not found."""
        response = rubric_service.delete(db_session, 99999)

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Rubric.NOT_FOUND

    def test_delete_cascades_to_criteria(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test delete cascades to associated criteria and levels."""
        from models import Criterion, Level

        rubric_id = rubric_with_criteria.id
        criterion_ids = [c.id for c in rubric_with_criteria.criteria]

        response = rubric_service.delete(db_session, rubric_id)

        assert response.success is True

        # Verify criteria are deleted
        remaining_criteria = db_session.query(Criterion).filter(
            Criterion.rubric_id == rubric_id
        ).all()
        assert len(remaining_criteria) == 0

    def test_delete_database_error(self, rubric_service: RubricServiceAPI):
        """Test delete handles database errors gracefully."""
        mock_session = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = Exception("Database error")
        mock_session.query.return_value = mock_query

        response = rubric_service.delete(mock_session, 1)

        assert response.success is False
        assert response.message == Messages.Rubric.DELETE_FAILED


class TestCriterionServiceAPI:
    """Tests for criterion CRUD operations."""

    def test_get_criterion_by_id_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test get_criterion_by_id returns criterion with levels."""
        criterion = rubric_with_criteria.criteria[0]

        response = rubric_service.get_criterion_by_id(
            db_session, rubric_with_criteria.id, criterion.id
        )

        assert response.success is True
        assert response.data.id == criterion.id
        assert response.data.title == criterion.title
        assert len(response.data.levels) == 3
        assert response.message == Messages.Criterion.RETRIEVED

    def test_get_criterion_by_id_not_found(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test get_criterion_by_id returns error when not found."""
        response = rubric_service.get_criterion_by_id(
            db_session, rubric_with_criteria.id, 99999
        )

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Criterion.NOT_FOUND

    def test_create_criterion_success(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test create_criterion adds criterion to rubric."""
        from schemas.rubric import CriterionRequest, LevelRequest

        criterion_request = CriterionRequest(
            title="New Criterion",
            description="A new criterion",
            weight=1.5,
            levels=[
                LevelRequest(level_title="High", score_points=3.0),
                LevelRequest(level_title="Low", score_points=1.0),
            ],
        )

        response = rubric_service.create_criterion(
            db_session, sample_rubric.id, criterion_request
        )

        assert response.success is True
        assert response.data.title == "New Criterion"
        assert response.data.weight == 1.5
        assert len(response.data.levels) == 2
        assert response.message == Messages.Criterion.CREATED

    def test_create_criterion_rubric_not_found(
        self, db_session: Session, rubric_service: RubricServiceAPI
    ):
        """Test create_criterion returns error when rubric not found."""
        from schemas.rubric import CriterionRequest

        criterion_request = CriterionRequest(title="Test")

        response = rubric_service.create_criterion(db_session, 99999, criterion_request)

        assert response.success is False
        assert response.message == Messages.Rubric.NOT_FOUND

    def test_update_criterion_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test update_criterion modifies criterion."""
        from schemas.rubric import CriterionUpdateRequest

        criterion = rubric_with_criteria.criteria[0]
        update_request = CriterionUpdateRequest(
            title="Updated Criterion",
            weight=2.0,
        )

        response = rubric_service.update_criterion(
            db_session, rubric_with_criteria.id, criterion.id, update_request
        )

        assert response.success is True
        assert response.data.title == "Updated Criterion"
        assert response.data.weight == 2.0
        assert response.message == Messages.Criterion.UPDATED

    def test_update_criterion_with_levels(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test update_criterion replaces levels."""
        from schemas.rubric import CriterionUpdateRequest, LevelRequest

        criterion = rubric_with_criteria.criteria[0]
        update_request = CriterionUpdateRequest(
            levels=[
                LevelRequest(level_title="New Level", score_points=5.0),
            ]
        )

        response = rubric_service.update_criterion(
            db_session, rubric_with_criteria.id, criterion.id, update_request
        )

        assert response.success is True
        assert len(response.data.levels) == 1
        assert response.data.levels[0].level_title == "New Level"

    def test_update_criterion_not_found(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test update_criterion returns error when not found."""
        from schemas.rubric import CriterionUpdateRequest

        update_request = CriterionUpdateRequest(title="Updated")

        response = rubric_service.update_criterion(
            db_session, sample_rubric.id, 99999, update_request
        )

        assert response.success is False
        assert response.message == Messages.Criterion.NOT_FOUND

    def test_delete_criterion_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test delete_criterion removes criterion."""
        criterion = rubric_with_criteria.criteria[0]
        criterion_id = criterion.id

        response = rubric_service.delete_criterion(
            db_session, rubric_with_criteria.id, criterion_id
        )

        assert response.success is True
        assert response.data is None
        assert response.message == Messages.Criterion.DELETED

    def test_delete_criterion_not_found(
        self, db_session: Session, sample_rubric, rubric_service: RubricServiceAPI
    ):
        """Test delete_criterion returns error when not found."""
        response = rubric_service.delete_criterion(
            db_session, sample_rubric.id, 99999
        )

        assert response.success is False
        assert response.message == Messages.Criterion.NOT_FOUND


class TestLevelServiceAPI:
    """Tests for level CRUD operations."""

    def test_get_level_by_id_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test get_level_by_id returns level data."""
        criterion = rubric_with_criteria.criteria[0]
        level = criterion.levels[0]

        response = rubric_service.get_level_by_id(
            db_session, criterion.id, level.id
        )

        assert response.success is True
        assert response.data.id == level.id
        assert response.data.level_title == level.level_title
        assert response.data.score_points == level.score_points
        assert response.message == Messages.Level.RETRIEVED

    def test_get_level_by_id_not_found(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test get_level_by_id returns error when not found."""
        criterion = rubric_with_criteria.criteria[0]

        response = rubric_service.get_level_by_id(
            db_session, criterion.id, 99999
        )

        assert response.success is False
        assert response.data is None
        assert response.message == Messages.Level.NOT_FOUND

    def test_create_level_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test create_level adds level to criterion."""
        from schemas.rubric import LevelRequest

        criterion = rubric_with_criteria.criteria[0]
        level_request = LevelRequest(
            level_title="New Level",
            level_description="A new scoring level",
            score_points=5.0,
        )

        response = rubric_service.create_level(
            db_session, criterion.id, level_request
        )

        assert response.success is True
        assert response.data.level_title == "New Level"
        assert response.data.score_points == 5.0
        assert response.message == Messages.Level.CREATED

    def test_create_level_criterion_not_found(
        self, db_session: Session, rubric_service: RubricServiceAPI
    ):
        """Test create_level returns error when criterion not found."""
        from schemas.rubric import LevelRequest

        level_request = LevelRequest(level_title="Test", score_points=1.0)

        response = rubric_service.create_level(db_session, 99999, level_request)

        assert response.success is False
        assert response.message == Messages.Criterion.NOT_FOUND

    def test_update_level_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test update_level modifies level."""
        from schemas.rubric import LevelUpdateRequest

        criterion = rubric_with_criteria.criteria[0]
        level = criterion.levels[0]
        update_request = LevelUpdateRequest(
            level_title="Updated Level",
            score_points=10.0,
        )

        response = rubric_service.update_level(
            db_session, criterion.id, level.id, update_request
        )

        assert response.success is True
        assert response.data.level_title == "Updated Level"
        assert response.data.score_points == 10.0
        assert response.message == Messages.Level.UPDATED

    def test_update_level_not_found(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test update_level returns error when not found."""
        from schemas.rubric import LevelUpdateRequest

        criterion = rubric_with_criteria.criteria[0]
        update_request = LevelUpdateRequest(level_title="Updated")

        response = rubric_service.update_level(
            db_session, criterion.id, 99999, update_request
        )

        assert response.success is False
        assert response.message == Messages.Level.NOT_FOUND

    def test_delete_level_success(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test delete_level removes level."""
        criterion = rubric_with_criteria.criteria[0]
        level = criterion.levels[0]
        level_id = level.id

        response = rubric_service.delete_level(
            db_session, criterion.id, level_id
        )

        assert response.success is True
        assert response.data is None
        assert response.message == Messages.Level.DELETED

    def test_delete_level_not_found(
        self, db_session: Session, rubric_with_criteria, rubric_service: RubricServiceAPI
    ):
        """Test delete_level returns error when not found."""
        criterion = rubric_with_criteria.criteria[0]

        response = rubric_service.delete_level(
            db_session, criterion.id, 99999
        )

        assert response.success is False
        assert response.message == Messages.Level.NOT_FOUND
