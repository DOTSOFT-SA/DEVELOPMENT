"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod

from ...models.dtos.distribution_routing_dto import DistributionRoutingDto


class DistributionOptimizationRoutingFacadeInterface(ABC):

    @abstractmethod
    def run_distribution_routing_optimization(self, user_id: int) -> DistributionRoutingDto:
        pass
