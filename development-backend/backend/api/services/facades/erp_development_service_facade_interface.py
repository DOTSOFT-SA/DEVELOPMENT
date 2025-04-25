"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from ...models.dtos.merged_sku_metric_dto import MergedSkuMetricDto


class ErpDevelopmentServiceFacadeInterface(ABC):

    @abstractmethod
    def get_most_recent_sku_order_record(self, sku_order_record_ids: List[int], user_id: int) -> Dict | None:
        pass

    @abstractmethod
    def get_most_recent_inventory_params_record(self, sku_number: int, user_id: int) -> Dict | None:
        pass

    def get_distribution_routing_data(self, user_id: int) -> Dict:
        pass

    @abstractmethod
    def get_merged_sku_metric_info(self, sku_number: int, user_id: int) -> Optional[MergedSkuMetricDto]:
        pass
