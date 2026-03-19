"""
Rubric Service API - Business logic for Rubric operations.

This module provides the service layer for Rubric CRUD operations,
following the API service pattern for consistency across the codebase.
"""

from typing import List
from sqlalchemy.orm import Session

from models import Rubric, Criterion, Level
from schemas.response import APIResponse
from schemas.rubric import (
    RubricResponse,
    RubricResponseWithCriteria,
    RubricRequest,
    RubricUpdateRequest,
    CriterionResponseWithLevels,
    CriterionRequest,
    CriterionUpdateRequest,
    LevelResponse,
    LevelRequest,
    LevelUpdateRequest,
)
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
            # Check for existing rubric with the same title (case-insensitive)
            existing_rubric = db.query(Rubric).filter(
                Rubric.title.ilike(rubric_request.title)
            ).first()
            
            if existing_rubric:
                logger.warning(f"Rubric with title '{rubric_request.title}' already exists")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Rubric.DUPLICATE_TITLE],
                    message=Messages.Rubric.DUPLICATE_TITLE,
                )

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
        self, db: Session, rubric_id: int, rubric_request: RubricUpdateRequest
    ) -> APIResponse[RubricResponseWithCriteria]:
        """
        Update rubric metadata only (title and description).

        Criteria and levels are managed through dedicated endpoints:
        - PUT /rubrics/{rubric_id}/criteria/{criterion_id}
        - PUT /rubrics/criteria/{criterion_id}/levels/{level_id}

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the rubric to update
            rubric_request: The updated rubric metadata

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

            # Update only provided rubric metadata fields
            if rubric_request.title is not None:
                rubric.title = rubric_request.title
            if rubric_request.description is not None:
                rubric.description = rubric_request.description

            db.commit()
            db.refresh(rubric)

            rubric_response = RubricResponseWithCriteria.model_validate(rubric)

            logger.debug(f"Updated rubric {rubric_id} metadata")

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

    # =========================================================================
    # CRITERION CRUD OPERATIONS
    # =========================================================================

    def get_criterion_by_id(
        self, db: Session, rubric_id: int, criterion_id: int
    ) -> APIResponse[CriterionResponseWithLevels]:
        """
        Retrieve a single criterion by ID with its levels.

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the parent rubric
            criterion_id: The ID of the criterion to retrieve

        Returns:
            APIResponse containing the criterion with nested levels,
            or error information if not found.
        """
        try:
            criterion = (
                db.query(Criterion)
                .filter(Criterion.id == criterion_id, Criterion.rubric_id == rubric_id)
                .first()
            )

            if criterion is None:
                logger.warning(f"Criterion {criterion_id} not found in rubric {rubric_id}")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Criterion.NOT_FOUND_DETAIL.format(id=criterion_id)],
                    message=Messages.Criterion.NOT_FOUND,
                )

            criterion_response = CriterionResponseWithLevels.model_validate(criterion)

            logger.debug(f"Retrieved criterion {criterion_id} with {len(criterion.levels)} levels")

            return APIResponse(
                success=True,
                data=criterion_response,
                errors=None,
                message=Messages.Criterion.RETRIEVED,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve criterion {criterion_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Criterion.RETRIEVE_FAILED,
            )

    def create_criterion(
        self, db: Session, rubric_id: int, criterion_request: CriterionRequest
    ) -> APIResponse[CriterionResponseWithLevels]:
        """
        Create a new criterion within a rubric.

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the parent rubric
            criterion_request: The criterion data to create

        Returns:
            APIResponse containing the created criterion with nested levels,
            or error information on failure.
        """
        try:
            # Verify rubric exists
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
            if rubric is None:
                logger.warning(Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id))
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Rubric.NOT_FOUND_DETAIL.format(id=rubric_id)],
                    message=Messages.Rubric.NOT_FOUND,
                )

            # Create criterion
            criterion = Criterion(
                rubric_id=rubric_id,
                title=criterion_request.title,
                description=criterion_request.description,
                weight=criterion_request.weight,
            )

            # Create nested levels
            for level_data in criterion_request.levels:
                level = Level(
                    level_title=level_data.level_title,
                    level_description=level_data.level_description,
                    score_points=level_data.score_points,
                )
                criterion.levels.append(level)

            db.add(criterion)
            db.commit()
            db.refresh(criterion)

            criterion_response = CriterionResponseWithLevels.model_validate(criterion)

            logger.debug(f"Created criterion {criterion.id} in rubric {rubric_id}")

            return APIResponse(
                success=True,
                data=criterion_response,
                errors=None,
                message=Messages.Criterion.CREATED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create criterion: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Criterion.CREATE_FAILED,
            )

    def update_criterion(
        self, db: Session, rubric_id: int, criterion_id: int, criterion_request: CriterionUpdateRequest
    ) -> APIResponse[CriterionResponseWithLevels]:
        """
        Update an existing criterion (partial update).

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the parent rubric
            criterion_id: The ID of the criterion to update
            criterion_request: The updated criterion data

        Returns:
            APIResponse containing the updated criterion with nested levels,
            or error information if not found or on failure.
        """
        try:
            criterion = (
                db.query(Criterion)
                .filter(Criterion.id == criterion_id, Criterion.rubric_id == rubric_id)
                .first()
            )

            if criterion is None:
                logger.warning(f"Criterion {criterion_id} not found in rubric {rubric_id}")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Criterion.NOT_FOUND_DETAIL.format(id=criterion_id)],
                    message=Messages.Criterion.NOT_FOUND,
                )

            # Update only provided fields
            if criterion_request.title is not None:
                criterion.title = criterion_request.title
            if criterion_request.description is not None:
                criterion.description = criterion_request.description
            if criterion_request.weight is not None:
                criterion.weight = criterion_request.weight

            # Update levels if provided
            if criterion_request.levels is not None:
                criterion.levels.clear()
                for level_data in criterion_request.levels:
                    level = Level(
                        level_title=level_data.level_title,
                        level_description=level_data.level_description,
                        score_points=level_data.score_points,
                    )
                    criterion.levels.append(level)

            db.commit()
            db.refresh(criterion)

            criterion_response = CriterionResponseWithLevels.model_validate(criterion)

            logger.debug(f"Updated criterion {criterion_id}")

            return APIResponse(
                success=True,
                data=criterion_response,
                errors=None,
                message=Messages.Criterion.UPDATED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update criterion {criterion_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Criterion.UPDATE_FAILED,
            )

    def delete_criterion(
        self, db: Session, rubric_id: int, criterion_id: int
    ) -> APIResponse[None]:
        """
        Delete a criterion by ID.

        Cascade deletes all associated levels.

        Args:
            db: SQLAlchemy database session
            rubric_id: The ID of the parent rubric
            criterion_id: The ID of the criterion to delete

        Returns:
            APIResponse with success status and message,
            or error information if not found or on failure.
        """
        try:
            criterion = (
                db.query(Criterion)
                .filter(Criterion.id == criterion_id, Criterion.rubric_id == rubric_id)
                .first()
            )

            if criterion is None:
                logger.warning(f"Criterion {criterion_id} not found in rubric {rubric_id}")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Criterion.NOT_FOUND_DETAIL.format(id=criterion_id)],
                    message=Messages.Criterion.NOT_FOUND,
                )

            db.delete(criterion)
            db.commit()

            logger.debug(f"Deleted criterion {criterion_id}")

            return APIResponse(
                success=True,
                data=None,
                errors=None,
                message=Messages.Criterion.DELETED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete criterion {criterion_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Criterion.DELETE_FAILED,
            )

    # =========================================================================
    # LEVEL CRUD OPERATIONS
    # =========================================================================

    def get_level_by_id(
        self, db: Session, criterion_id: int, level_id: int
    ) -> APIResponse[LevelResponse]:
        """
        Retrieve a single level by ID.

        Args:
            db: SQLAlchemy database session
            criterion_id: The ID of the parent criterion
            level_id: The ID of the level to retrieve

        Returns:
            APIResponse containing the level,
            or error information if not found.
        """
        try:
            level = (
                db.query(Level)
                .filter(Level.id == level_id, Level.criterion_id == criterion_id)
                .first()
            )

            if level is None:
                logger.warning(f"Level {level_id} not found in criterion {criterion_id}")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Level.NOT_FOUND_DETAIL.format(id=level_id)],
                    message=Messages.Level.NOT_FOUND,
                )

            level_response = LevelResponse.model_validate(level)

            logger.debug(f"Retrieved level {level_id}")

            return APIResponse(
                success=True,
                data=level_response,
                errors=None,
                message=Messages.Level.RETRIEVED,
            )
        except Exception as e:
            logger.error(f"Failed to retrieve level {level_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Level.RETRIEVE_FAILED,
            )

    def create_level(
        self, db: Session, criterion_id: int, level_request: LevelRequest
    ) -> APIResponse[LevelResponse]:
        """
        Create a new level within a criterion.

        Args:
            db: SQLAlchemy database session
            criterion_id: The ID of the parent criterion
            level_request: The level data to create

        Returns:
            APIResponse containing the created level,
            or error information on failure.
        """
        try:
            # Verify criterion exists
            criterion = db.query(Criterion).filter(Criterion.id == criterion_id).first()
            if criterion is None:
                logger.warning(Messages.Criterion.NOT_FOUND_DETAIL.format(id=criterion_id))
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Criterion.NOT_FOUND_DETAIL.format(id=criterion_id)],
                    message=Messages.Criterion.NOT_FOUND,
                )

            # Create level
            level = Level(
                criterion_id=criterion_id,
                level_title=level_request.level_title,
                level_description=level_request.level_description,
                score_points=level_request.score_points,
            )

            db.add(level)
            db.commit()
            db.refresh(level)

            level_response = LevelResponse.model_validate(level)

            logger.debug(f"Created level {level.id} in criterion {criterion_id}")

            return APIResponse(
                success=True,
                data=level_response,
                errors=None,
                message=Messages.Level.CREATED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create level: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Level.CREATE_FAILED,
            )

    def update_level(
        self, db: Session, criterion_id: int, level_id: int, level_request: LevelUpdateRequest
    ) -> APIResponse[LevelResponse]:
        """
        Update an existing level (partial update).

        Args:
            db: SQLAlchemy database session
            criterion_id: The ID of the parent criterion
            level_id: The ID of the level to update
            level_request: The updated level data

        Returns:
            APIResponse containing the updated level,
            or error information if not found or on failure.
        """
        try:
            level = (
                db.query(Level)
                .filter(Level.id == level_id, Level.criterion_id == criterion_id)
                .first()
            )

            if level is None:
                logger.warning(f"Level {level_id} not found in criterion {criterion_id}")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Level.NOT_FOUND_DETAIL.format(id=level_id)],
                    message=Messages.Level.NOT_FOUND,
                )

            # Update only provided fields
            if level_request.level_title is not None:
                level.level_title = level_request.level_title
            if level_request.level_description is not None:
                level.level_description = level_request.level_description
            if level_request.score_points is not None:
                level.score_points = level_request.score_points

            db.commit()
            db.refresh(level)

            level_response = LevelResponse.model_validate(level)

            logger.debug(f"Updated level {level_id}")

            return APIResponse(
                success=True,
                data=level_response,
                errors=None,
                message=Messages.Level.UPDATED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update level {level_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Level.UPDATE_FAILED,
            )

    def delete_level(
        self, db: Session, criterion_id: int, level_id: int
    ) -> APIResponse[None]:
        """
        Delete a level by ID.

        Args:
            db: SQLAlchemy database session
            criterion_id: The ID of the parent criterion
            level_id: The ID of the level to delete

        Returns:
            APIResponse with success status and message,
            or error information if not found or on failure.
        """
        try:
            level = (
                db.query(Level)
                .filter(Level.id == level_id, Level.criterion_id == criterion_id)
                .first()
            )

            if level is None:
                logger.warning(f"Level {level_id} not found in criterion {criterion_id}")
                return APIResponse(
                    success=False,
                    data=None,
                    errors=[Messages.Level.NOT_FOUND_DETAIL.format(id=level_id)],
                    message=Messages.Level.NOT_FOUND,
                )

            db.delete(level)
            db.commit()

            logger.debug(f"Deleted level {level_id}")

            return APIResponse(
                success=True,
                data=None,
                errors=None,
                message=Messages.Level.DELETED,
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete level {level_id}: {e}")
            return APIResponse(
                success=False,
                data=None,
                errors=[str(e)],
                message=Messages.Level.DELETE_FAILED,
            )
