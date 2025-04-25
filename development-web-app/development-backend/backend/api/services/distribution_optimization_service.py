"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

import inject

from .distribution_optimization_service_interface import DistributionOptimizationServiceInterface
from ..models.distribution_optimization import DistributionOptimization
from ..models.serializers.page_criteria_serializers import PageParams, DistributionOptimizationCriteria
from ..repositories.distribution_optimization_repository_interface import DistributionOptimizationRepositoryInterface


class DistributionOptimizationService(DistributionOptimizationServiceInterface):

    @inject.autoparams()
    def __init__(self, distribution_optimization_repository: DistributionOptimizationRepositoryInterface):
        self.distribution_optimization_repository = distribution_optimization_repository

    def get_all_distribution_optimizations(self, page_params: PageParams,
                                           criteria: DistributionOptimizationCriteria) -> List[
        DistributionOptimization]:
        """
        Retrieves all Distribution Optimization records matching the specified criteria.

        :param page_params: PageParams(page, page_size): Pagination parameters.
        :param criteria: DistributionOptimizationCriteria: Filtering criteria including user_id, vehicle_id, date range etc.
        :return: List[DistributionOptimization]: A list of matching DistributionOptimization objects.
        """
        return self.distribution_optimization_repository.find_all_distribution_optimizations(page_params, criteria)

    def create_distribution_optimization(self,
                                         distribution_optimization: DistributionOptimization) -> DistributionOptimization:
        """
        Saves a single DistributionOptimization record in the database.

        :param distribution_optimization: DistributionOptimization: The record to be stored.
        :return: DistributionOptimization: The stored record.
        """
        return self.distribution_optimization_repository.store_distribution_optimization(distribution_optimization)
