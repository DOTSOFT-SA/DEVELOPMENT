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

from ..models.models import InventoryParamsDevelopment
from ..models.page_criteria_models import PageParams, InventoryParamsCriteria
from ..models.schema import InventoryParamsDevelopmentORM


class InventoryParamsDevelopmentRepository:
    """
    Repository that handles CRUD operations for the 'inventory_params_development' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_all_inventory_params(
            self,
            page_params: PageParams,
            criteria: InventoryParamsCriteria
    ) -> List[InventoryParamsDevelopment]:
        """
        Retrieves inventory parameters from the database with optional pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (sku_number, week_number).
        @return: A list of inventory parameter records as Pydantic models.
        """
        query = select(InventoryParamsDevelopmentORM)

        # Apply filters
        if criteria.sku_number is not None:
            query = query.where(InventoryParamsDevelopmentORM.sku_number == criteria.sku_number)

        # Apply pagination
        if page_params.page_size is not None:
            offset = (page_params.page - 1) * page_params.page_size
            query = query.offset(offset).limit(page_params.page_size)

        # Execute query
        result = await self.session.execute(query)
        rows = result.scalars().all()

        # Convert ORM instances to Pydantic models
        return [InventoryParamsDevelopment.from_orm(row) for row in rows]

    async def fetch_latest_by_sku_number(
            self, sku_number: int
    ) -> InventoryParamsDevelopment:
        """
        Retrieves the latest inventory parameter record for a given SKU number
        based on the 'created_at' field.

        @param sku_number: The SKU number to filter records.
        @return: The latest InventoryParamsDevelopment record as a Pydantic model.
        """
        query = (
            select(InventoryParamsDevelopmentORM)
            .where(InventoryParamsDevelopmentORM.sku_number == sku_number)
            .order_by(InventoryParamsDevelopmentORM.created_at.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        row = result.scalar_one_or_none()

        return InventoryParamsDevelopment.from_orm(row) if row else None
