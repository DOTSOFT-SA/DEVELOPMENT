"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

import inject

from .inventory_optimization_service_interface import InventoryOptimizationServiceInterface
from ..models.inventory_optimization import InventoryOptimization
from ..models.serializers.page_criteria_serializers import PageParams, InventoryOptimizationCriteria
from ..repositories.inventory_optimization_repository_interface import InventoryOptimizationRepositoryInterface


class InventoryOptimizationService(InventoryOptimizationServiceInterface):

    @inject.autoparams()
    def __init__(self, inventory_optimization_repository: InventoryOptimizationRepositoryInterface):
        self.inventory_optimization_repository = inventory_optimization_repository

    def get_all_optimizations(
            self, page_params: PageParams, criteria: InventoryOptimizationCriteria
    ) -> List[InventoryOptimization]:
        """
        Retrieves all inventory optimization records that match the specified criteria.

        :param page_params: PageParams(page, page_size): Pagination parameters containing the current page number and optional page size.
        :param criteria: InventoryOptimizationCriteria: Filtering criteria including inventory_record_id and date range.
        :return: List[InventoryOptimization]: A list of InventoryOptimization instances matching the criteria.
        """
        return self.inventory_optimization_repository.find_all_inventory_optimizations(page_params, criteria)

    def create_inventory_optimization(self, inventory_optimization: InventoryOptimization) -> InventoryOptimization:
        """
        Saves a single InventoryOptimization record in the database.

        :param inventory_optimization: InventoryOptimization: The inventory optimization instance to be stored.
        :return: InventoryOptimization: The stored InventoryOptimization instance.
        """
        return self.inventory_optimization_repository.store_inventory_optimization(inventory_optimization)
