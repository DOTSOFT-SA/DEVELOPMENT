"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List, Optional

from ..models.models import InventoryParamsDevelopment
from ..models.page_criteria_models import PageParams, InventoryParamsCriteria
from ..repositories.inventory_params_development_repository import InventoryParamsDevelopmentRepository


class InventoryParamsDevelopmentService:
    """
    Service responsible for business logic related to 'inventory_params_development'.
    """

    def __init__(self, repository: InventoryParamsDevelopmentRepository):
        self.repository = repository

    async def get_all_inventory_params(
            self,
            page_params: PageParams,
            criteria: InventoryParamsCriteria
    ) -> List[InventoryParamsDevelopment]:
        """
        Retrieves a list of inventory parameters with pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (sku_number, week_number).
        @return: A list of inventory parameter records as Pydantic models.
        """
        return await self.repository.fetch_all_inventory_params(page_params, criteria)

    async def get_latest_by_sku_number(
            self, sku_number: int
    ) -> Optional[InventoryParamsDevelopment]:
        """
        Retrieves the latest inventory parameter record for a given SKU number
        based on the 'created_at' field.

        @param sku_number: The SKU number to filter records.
        @return: The latest InventoryParamsDevelopment record as a Pydantic model.
        """
        return await self.repository.fetch_latest_by_sku_number(sku_number)
