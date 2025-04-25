"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List, Optional

from ..models.models import SkuOrderDevelopment
from ..models.page_criteria_models import PageParams, SkuOrderDevelopmentCriteria
from ..repositories.sku_order_development_repository import SkuOrderDevelopmentRepository


class SkuOrderDevelopmentService:
    """
    Service responsible for business logic related to 'sku_order_development'.
    """

    def __init__(self, repository: SkuOrderDevelopmentRepository):
        self.repository = repository

    async def get_all_skus(
            self,
            page_params: PageParams,
            criteria: SkuOrderDevelopmentCriteria
    ) -> List[SkuOrderDevelopment]:
        """
        Retrieves a list of SKUs with pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (sku_number, sku_name, etc.).
        @return: A list of SKU records as Pydantic models.
        """
        return await self.repository.fetch_all_skus(page_params, criteria)

    async def get_latest_sku_order_by_ids(
            self,
            ids: List[int]
    ) -> Optional[SkuOrderDevelopment]:
        """
        Retrieves the SkuOrderDevelopment record with the latest order_date
        among the specified IDs.

        @param ids: The list of IDs to filter by.
        @return: The record with the max order_date, or None if not found.
        """
        return await self.repository.fetch_latest_sku_order_by_ids(ids)
