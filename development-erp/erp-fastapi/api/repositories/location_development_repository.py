"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.models import LocationDevelopment
from ..models.page_criteria_models import PageParams, LocationDevelopmentCriteria
from ..models.schema import LocationDevelopmentORM


class LocationDevelopmentRepository:
    """
    Repository that handles CRUD operations for the 'location_development' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_all_locations(
            self,
            page_params: PageParams,
            criteria: LocationDevelopmentCriteria
    ) -> List[LocationDevelopment]:
        """
        Retrieves location records from the database with optional pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (location_id).
        @return: A list of location records as Pydantic models.
        """
        query = select(LocationDevelopmentORM)

        # Apply filters
        if criteria.location_id is not None:
            query = query.where(LocationDevelopmentORM.location_id == criteria.location_id)
        if criteria.location_name is not None:
            query = query.where(LocationDevelopmentORM.location_name.ilike(f"%{criteria.location_name}%"))

        # Apply pagination
        if page_params.page_size is not None:
            offset = (page_params.page - 1) * page_params.page_size
            query = query.offset(offset).limit(page_params.page_size)

        # Execute query
        result = await self.session.execute(query)
        rows = result.scalars().all()

        # Convert ORM instances to Pydantic models
        return [LocationDevelopment.from_orm(row) for row in rows]
