"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.models import SkuOrderDevelopment
from ..models.page_criteria_models import PageParams, SkuOrderDevelopmentCriteria
from ..models.schema import SkuOrderDevelopmentORM


class SkuOrderDevelopmentRepository:
    """
    Repository that handles CRUD operations for the 'sku_order_development' table.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_all_skus(
            self,
            page_params: PageParams,
            criteria: SkuOrderDevelopmentCriteria
    ) -> List[SkuOrderDevelopment]:
        """
        Retrieves SKU records from the database with optional pagination and filtering.

        @param page_params: An object containing pagination parameters (page, page_size).
        @param criteria: An object containing filtering criteria (sku_number, sku_name, class_display_name, order_date).
        @return: A list of SKU records mapped to Pydantic models.
        """

        query = select(SkuOrderDevelopmentORM)

        # Filtering based on criteria
        if criteria.sku_number is not None:
            query = query.where(SkuOrderDevelopmentORM.sku_number == criteria.sku_number)
        if criteria.sku_name is not None:
            query = query.where(SkuOrderDevelopmentORM.sku_name.ilike(f"%{criteria.sku_name}%"))
        if criteria.class_display_name is not None:
            query = query.where(SkuOrderDevelopmentORM.class_display_name.ilike(f"%{criteria.class_display_name}%"))
        if criteria.order_date is not None:
            query = query.where(SkuOrderDevelopmentORM.order_date == criteria.order_date)
        if criteria.start_order_date is not None:
            query = query.where(SkuOrderDevelopmentORM.order_date >= criteria.start_order_date)
        if criteria.end_order_date is not None:
            query = query.where(SkuOrderDevelopmentORM.order_date <= criteria.end_order_date)

        # Pagination
        if page_params.page_size is not None:
            offset = (page_params.page - 1) * page_params.page_size
            query = query.offset(offset).limit(page_params.page_size)

        result = await self.session.execute(query)
        rows = result.scalars().all()

        # Convert each ORM instance to a Pydantic model
        return [SkuOrderDevelopment.from_orm(row) for row in rows]

    async def fetch_latest_sku_order_by_ids(
            self,
            ids: List[int]
    ) -> Optional[SkuOrderDevelopment]:
        """
        Fetch the SkuOrderDevelopment record with the latest (max) order_date
        among the given list of IDs.

        @param ids: The list of SkuOrderDevelopment IDs to search within.
        @return: A single SkuOrderDevelopment record with the latest order_date,
                 or None if no matching records are found.
        """

        # If no IDs are provided, return None immediately
        if not ids:
            return None
        # Construct a query to fetch the latest record for the given IDs
        query = (
            select(SkuOrderDevelopmentORM)  # Select from the ORM model (db table)
            .where(SkuOrderDevelopmentORM.id.in_(ids))  # Filter to match provided IDs
            .order_by(desc(SkuOrderDevelopmentORM.order_date))  # Order by order_date in descending order (latest first)
            .limit(1)  # Limit the result to the most recent record
        )
        # Execute the query asynchronously
        result = await self.session.execute(query)
        # Retrieve the first result from the query execution
        row = result.scalars().first()
        # If a row is found, convert it to a Pydantic model and return it
        if row:
            return SkuOrderDevelopment.from_orm(row)
        # If no matching row is found, return None
        return None
