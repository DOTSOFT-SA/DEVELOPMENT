"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import List

from ..models.inventory_optimization import InventoryOptimization
from ..models.serializers.page_criteria_serializers import PageParams, InventoryOptimizationCriteria


class InventoryOptimizationServiceInterface(ABC):
    """
    Interface for the Inventory Optimization service.
    """

    @abstractmethod
    def get_all_optimizations(
            self, page_params: PageParams, criteria: InventoryOptimizationCriteria
    ) -> List[InventoryOptimization]:
        pass

    @abstractmethod
    def create_inventory_optimization(
            self, inventory_optimization: InventoryOptimization
    ) -> InventoryOptimization:
        pass
