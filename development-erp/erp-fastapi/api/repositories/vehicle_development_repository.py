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

from ..models.models import VehicleDevelopment
from ..models.page_criteria_models import PageParams, VehicleDevelopmentCriteria
from ..models.schema import VehicleDevelopmentORM


class VehicleDevelopmentRepository:
    """
    Repository that handles CRUD operations for the 'vehicle_development' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_all_vehicles(
            self,
            page_params: PageParams,
            criteria: VehicleDevelopmentCriteria
    ) -> List[VehicleDevelopment]:
        """
        Retrieves vehicle records from the database with optional pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (vehicle_id).
        @return: A list of vehicle records as Pydantic models.
        """
        query = select(VehicleDevelopmentORM)

        # Apply filters
        if criteria.vehicle_id is not None:
            query = query.where(VehicleDevelopmentORM.vehicle_id == criteria.vehicle_id)

        # Apply pagination
        if page_params.page_size is not None:
            offset = (page_params.page - 1) * page_params.page_size
            query = query.offset(offset).limit(page_params.page_size)

        # Execute query
        result = await self.session.execute(query)
        rows = result.scalars().all()

        # Convert ORM instances to Pydantic models
        return [VehicleDevelopment.from_orm(row) for row in rows]
