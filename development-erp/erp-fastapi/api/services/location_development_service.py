"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from ..models.models import LocationDevelopment
from ..models.page_criteria_models import PageParams, LocationDevelopmentCriteria
from ..repositories.location_development_repository import LocationDevelopmentRepository


class LocationDevelopmentService:
    """
    Service responsible for business logic related to 'location_development'.
    """

    def __init__(self, repository: LocationDevelopmentRepository):
        self.repository = repository

    async def get_all_locations(
            self,
            page_params: PageParams,
            criteria: LocationDevelopmentCriteria
    ) -> List[LocationDevelopment]:
        """
        Retrieves a list of locations with pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (location_id).
        @return: A list of location records as Pydantic models.
        """
        return await self.repository.fetch_all_locations(page_params, criteria)
