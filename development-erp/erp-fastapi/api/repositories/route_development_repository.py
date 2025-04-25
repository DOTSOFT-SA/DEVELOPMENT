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

from ..models.models import RouteDevelopment
from ..models.page_criteria_models import PageParams, RouteDevelopmentCriteria
from ..models.schema import RouteDevelopmentORM


class RouteDevelopmentRepository:
    """
    Repository that handles CRUD operations for the 'route_development' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_all_routes(
            self,
            page_params: PageParams,
            criteria: RouteDevelopmentCriteria
    ) -> List[RouteDevelopment]:
        """
        Retrieves route records from the database with optional pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (route_id).
        @return: A list of route records as Pydantic models.
        """
        query = select(RouteDevelopmentORM)

        # Apply filters
        if criteria.route_id is not None:
            query = query.where(RouteDevelopmentORM.route_id == criteria.route_id)

        # Apply pagination
        if page_params.page_size is not None:
            offset = (page_params.page - 1) * page_params.page_size
            query = query.offset(offset).limit(page_params.page_size)

        # Execute query
        result = await self.session.execute(query)
        rows = result.scalars().all()

        # Convert ORM instances to Pydantic models
        return [RouteDevelopment.from_orm(row) for row in rows]
