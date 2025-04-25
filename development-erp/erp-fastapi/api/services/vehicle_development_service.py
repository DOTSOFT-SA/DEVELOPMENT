"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from ..models.models import VehicleDevelopment
from ..models.page_criteria_models import PageParams, VehicleDevelopmentCriteria
from ..repositories.vehicle_development_repository import VehicleDevelopmentRepository


class VehicleDevelopmentService:
    """
    Service responsible for business logic related to 'vehicle_development'.
    """

    def __init__(self, repository: VehicleDevelopmentRepository):
        self.repository = repository

    async def get_all_vehicles(
            self,
            page_params: PageParams,
            criteria: VehicleDevelopmentCriteria
    ) -> List[VehicleDevelopment]:
        """
        Retrieves a list of vehicles with pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (vehicle_id).
        @return: A list of vehicle records as Pydantic models.
        """
        return await self.repository.fetch_all_vehicles(page_params, criteria)
