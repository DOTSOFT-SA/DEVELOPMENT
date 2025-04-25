"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import List

import inject

from .distribution_optimization_routing_facade_interface import DistributionOptimizationRoutingFacadeInterface
from ..distribution_optimization_service_interface import DistributionOptimizationServiceInterface
from ..distribution_optimization_with_traffic_service_interface import \
    DistributionOptimizationWithTrafficServiceInterface
from ...services.facades.erp_development_service_facade_interface import ErpDevelopmentServiceFacadeInterface
from ...models.distribution_optimization import DistributionOptimization
from ...models.dtos.distribution_routing_dto import RouteDto, DistributionRoutingDto

logger = logging.getLogger(__name__)


class DistributionOptimizationRoutingFacade(DistributionOptimizationRoutingFacadeInterface):
    """
    Concrete facade implementing the distribution routing optimization steps:
      1) Retrieve routing data from ERP.
      2) Run distribution optimization with traffic service.
      3) Store results in DB.
    """

    @inject.autoparams()
    def __init__(
            self,
            erp_development_service: ErpDevelopmentServiceFacadeInterface,
            distribution_optimization_with_traffic_service: DistributionOptimizationWithTrafficServiceInterface,
            distribution_optimization_service: DistributionOptimizationServiceInterface
    ):
        """
        Constructor injection of the necessary services.
        """
        self.erp_development_service = erp_development_service
        self.distribution_traffic_service = distribution_optimization_with_traffic_service
        self.distribution_optimization_service = distribution_optimization_service

    def run_distribution_routing_optimization(self, user_id: int) -> DistributionRoutingDto:
        """
        Runs distribution routing optimization and returns a DistributionRoutingDto.

        Steps:
          1) Retrieve routing data from ERP.
          2) Run distribution optimization with traffic adjustments.
          3) Store results in the database.
          4) Construct and return a DistributionRoutingDto.

        :param user_id: int: The ID of the user requesting the optimization.
        :return: DistributionRoutingDto: Contains total cost and optimized routes (array).
        """
        optimization_records = self._process_distribution_routing_optimization(user_id)
        if not optimization_records:
            raise ValueError("No distribution optimization records were produced.")

        # All records share the same cost -> extract from first item
        total_cost = optimization_records[0].total_cost

        # Build RouteDto for each record
        route_dtos = []
        for record in optimization_records:
            route_dtos.append(RouteDto(
                vehicle_id=record.vehicle_id,
                start_location_name=record.start_location_name,
                destination_location_name=record.destination_location_name,
                units=record.units
            ))

        # Return a single top-level DTO
        return DistributionRoutingDto(total_cost=total_cost, routes=route_dtos)

    def _process_distribution_routing_optimization(self, user_id: int) -> List[DistributionOptimization]:
        """
        Processes distribution routing optimization by retrieving ERP data,
        running traffic-based optimization, and storing the results.

        Steps:
          1) Fetch routing data from ERP via `get_distribution_routing_data(user_id)`.
          2) Compute optimized routes using `get_distribution_optimizations(user_id, routing_data)`.
          3) Store each route in DB using `create_distribution_optimization(distribution_record)`.
          4) Return the final list of stored records.

        :param user_id: int: The ID of the user requesting the optimization.
        :return: List[DistributionOptimization]: A list of distribution optimization records.
        """
        # Step 1: retrieve routing data
        routing_data = self.erp_development_service.get_distribution_routing_data(user_id)
        if not routing_data:
            raise ValueError(f"No routing data returned for user_id={user_id}.")
        # Step 2: build distribution optimization records
        distribution_records = self.distribution_traffic_service.get_distribution_optimizations(
            user_id, routing_data
        )
        if not distribution_records:
            raise ValueError(f"No distribution records created for user_id={user_id}.")
        # Step 3: store each record in DB
        saved_records = []
        for record in distribution_records:
            saved = self.distribution_optimization_service.create_distribution_optimization(record)
            saved_records.append(saved)
        # Return saved records
        return saved_records
