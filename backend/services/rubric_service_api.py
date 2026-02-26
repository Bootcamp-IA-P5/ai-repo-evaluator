"""
Rubric Service API - Business logic for Rubric operations.

This module provides the service layer for Rubric CRUD operations,
following the API service pattern for consistency across the codebase.
"""

from typing import List
from sqlalchemy.orm import Session

from models import Rubric
from schemas.response import APIResponse
from schemas.rubric import RubricResponse, RubricResponseWithCriteria
from core.logging_config import logger
from core.messages import Messages


class RubricServiceAPI:
    """
    Service class for Rubric API operations.

    This class encapsulates all business logic related to rubric management,
    providing a clean interface for CRUD operations with standardized responses.

    Future operations will include:
        - create(): Create a new rubric
        - update(): Update an existing rubric
        - delete(): Delete a rubric
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

            logger.info(f"Retrieved {len(rubric_responses)} rubrics")

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

            logger.info(f"Retrieved rubric {rubric_id} with {len(rubric.criteria)} criteria")

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
