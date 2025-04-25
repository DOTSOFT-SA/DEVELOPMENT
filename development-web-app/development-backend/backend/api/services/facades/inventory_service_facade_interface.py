"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod

from ...models.dtos.inventory_service_dto import InventoryServiceResponse, InventoryOptimizationRequest


class InventoryServiceFacadeInterface(ABC):

    @abstractmethod
    def get_most_recent_sku_inventory_params(self, sku_number: int, user_id: int) -> dict:
        pass

    @abstractmethod
    def run_inventory_optimization(self,
                                   inventory_optimization_dto: InventoryOptimizationRequest) -> InventoryServiceResponse:
        pass
