"""
Rubric Service API - Business logic for Rubric operations.

This module provides the service layer for Rubric CRUD operations,
following the API service pattern for consistency across the codebase.
"""

from typing import List
from sqlalchemy.orm import Session

from models import Rubric, Criterion, Level
from schemas.response import APIResponse
from schemas.rubric import RubricResponse, RubricResponseWithCriteria, RubricRequest
from core.logging_config import logger
from core.messages import Messages


class RubricServiceAPI:
    """
    Service class for Rubric API operations.

    This class encapsulates all business logic related to rubric management,
    providing a clean interface for CRUD operations with standardized responses.
    """

    def get_all(self, db: Session) -> APIResponse[List[RubricResponse]]:
        """
        Retrieve all rubrics from the database.

        Args:
            db: SQLAlchemy database session

        Returns:
            APIResponse containing a list of rubrics on success,
            or error information on failure.
        """
        try:
            rubrics = db.query(Rubric).all()

            rubric_responses = [RubricResponse.model_validate(rubric) for rubric in rubrics]

            logger.debug(f"Retrieved {len(rubric_responses)} rubrics")

            return APIResponse(
                success=True,
                data=rubric_responses,
                errors=None,
                message=Messages.Rubric.LIST_RETRIEVED,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve rubrics: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Rubric.LIST_RETRIEVE_FAILED,
            )

    def get_by_id(self, db: Session, rubric_id: int) -> APIResponse[RubricResponseWithCriteria]:
        """
        Retrieve a single rubric by ID with its criteria and levels.

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the rubric to retrieve

        Returns:
            APIResponse containing the rubric with nested criteria and levels,
            or error information if not found.
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

            if rubric is None:
                logger.warning(Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id))
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id)],
                    message=Messages.Rubric.NOT_FOUND,
                )

            rubric_response = RubricResponseWithCriteria.model_validate(rubric)

            logger.debug(f"Retrieved rubric {rubric_id} with {len(rubric.criteria)} criteria")

            return APIResponse(
                success=True,
                data=rubric_response,
                errors=None,
                message=Messages.Rubric.RETRIEVED,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve rubric {rubric_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Rubric.RETRIEVE_FAILED,
            )

    def create(self, db: Session, rubric_request: RubricRequest) -> APIResponse[RubricResponseWithCriteria]:
        """
        Create a new rubric with nested criteria and levels.

        Args:
            db: SQLAlchemy database session
            rubric_request: The rubric data to create

        Returns:
            APIResponse containing the created rubric with nested criteria and levels,
            or error information on failure.
        """
        try:
            # Create the rubric
            rubric = Rubric(
                title=rubric_request.title,
                description=rubric_request.description,
            )

            # Create nested criteria with levels
            for criterion_data in rubric_request.criteria:
                criterion = Criterion(
                    title=criterion_data.title,
                    description=criterion_data.description,
                    weight=criterion_data.weight,
                )

                # Create nested levels for each criterion
                for level_data in criterion_data.levels:
                    level = Level(
                        level_title=level_data.level_title,
                        level_description=level_data.level_description,
                        score_points=level_data.score_points,
                    )
                    criterion.levels.append(level)

                rubric.criteria.append(criterion)

            db.add(rubric)
            db.commit()
            db.refresh(rubric)

            rubric_response = RubricResponseWithCriteria.model_validate(rubric)

            logger.debug(f"Created rubric {rubric.id} with {len(rubric.criteria)} criteria")

            return APIResponse(
                success=True,
                data=rubric_response,
                errors=None,
                message=Messages.Rubric.CREATED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create rubric: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Rubric.CREATE_FAILED,
            )

    def update(
        self, db: Session, rubric_id: int, rubric_request: RubricRequest
    ) -> APIResponse[RubricResponseWithCriteria]:
        """
        Update an existing rubric with nested criteria and levels.

        Performs a full replacement of criteria and levels (PUT semantics).

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the rubric to update
            rubric_request: The updated rubric data

        Returns:
            APIResponse containing the updated rubric with nested criteria and levels,
            or error information if not found or on failure.
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

            if rubric is None:
                logger.warning(Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id))
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id)],
                    message=Messages.Rubric.NOT_FOUND,
                )

            # Update rubric fields
            rubric.title = rubric_request.title
            rubric.description = rubric_request.description

            # Clear existing criteria (cascade will handle levels)
            rubric.criteria.clear()

            # Create new criteria with levels
            for criterion_data in rubric_request.criteria:
                criterion = Criterion(
                    title=criterion_data.title,
                    description=criterion_data.description,
                    weight=criterion_data.weight,
                )

                # Create nested levels for each criterion
                for level_data in criterion_data.levels:
                    level = Level(
                        level_title=level_data.level_title,
                        level_description=level_data.level_description,
                        score_points=level_data.score_points,
                    )
                    criterion.levels.append(level)

                rubric.criteria.append(criterion)

            db.commit()
            db.refresh(rubric)

            rubric_response = RubricResponseWithCriteria.model_validate(rubric)

            logger.debug(f"Updated rubric {rubric_id} with {len(rubric.criteria)} criteria")

            return APIResponse(
                success=True,
                data=rubric_response,
                errors=None,
                message=Messages.Rubric.UPDATED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update rubric {rubric_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Rubric.UPDATE_FAILED,
            )

    def delete(self, db: Session, rubric_id: int) -> APIResponse[None]:
        """
        Delete a rubric by ID.

        Cascade deletes all associated criteria and levels.

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the rubric to delete

        Returns:
            APIResponse with success status and message,
            or error information if not found or on failure.
        """
        try:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

            if rubric is None:
                logger.warning(Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id))
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id)],
                    message=Messages.Rubric.NOT_FOUND,
                )

            db.delete(rubric)
            db.commit()

            logger.debug(f"Deleted rubric {rubric_id}")

            return APIResponse(
                success=True,
                data=None,
                errors=None,
                message=Messages.Rubric.DELETED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete rubric {rubric_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Rubric.DELETE_FAILED,
            )
