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


class SkuMetricRepositoryInterface(ABC):

    @abstractmethod
    def find_all_sku_order_record_ids_by_sku_number(self) -> List[int]:
        pass

    @abstractmethod
    def find_by_sku_order_record_id(self, record_id: int) -> Optional[SkuMetric]:
        pass
