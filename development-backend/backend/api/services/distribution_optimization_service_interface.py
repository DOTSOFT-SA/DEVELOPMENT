"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import List

from ..models.distribution_optimization import DistributionOptimization
from ..models.serializers.page_criteria_serializers import PageParams, DistributionOptimizationCriteria


class DistributionOptimizationServiceInterface(ABC):

    @abstractmethod
    def get_all_distribution_optimizations(self, page_params: PageParams,
                                           criteria: DistributionOptimizationCriteria) -> List[
        DistributionOptimization]:
        pass

    @abstractmethod
    def create_distribution_optimization(self,
                                         distribution_optimization: DistributionOptimization) -> DistributionOptimization:
        pass
