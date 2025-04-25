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


class DistributionOptimizationWithTrafficServiceInterface(ABC):

    @abstractmethod
    def get_distribution_optimizations(self, user_id: int, data: dict) -> List[DistributionOptimization]:
        pass
