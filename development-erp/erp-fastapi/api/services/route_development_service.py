"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from ..models.models import RouteDevelopment
from ..models.page_criteria_models import PageParams, RouteDevelopmentCriteria
from ..repositories.route_development_repository import RouteDevelopmentRepository


class RouteDevelopmentService:
    """
    Service responsible for business logic related to 'route_development'.
    """

    def __init__(self, repository: RouteDevelopmentRepository):
        self.repository = repository

    async def get_all_routes(
            self,
            page_params: PageParams,
            criteria: RouteDevelopmentCriteria
    ) -> List[RouteDevelopment]:
        """
        Retrieves a list of routes with pagination and filtering.

        @param page_params: The pagination parameters (page, page_size).
        @param criteria: The filtering criteria (route_id).
        @return: A list of route records as Pydantic models.
        """
        return await self.repository.fetch_all_routes(page_params, criteria)
