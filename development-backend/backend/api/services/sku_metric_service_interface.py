"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.sku_metric import SkuMetric


class SkuMetricServiceInterface(ABC):
    """
    Interface defining the contract for SkuMetricService.
    """

    @abstractmethod
    def get_all_sku_order_record_ids_by_sku_number(self, sku_number: int) -> List[int]:
        pass

    @abstractmethod
    def get_by_sku_order_record_id(self, sku_order_record_id: int) -> Optional[SkuMetric]:
        pass
