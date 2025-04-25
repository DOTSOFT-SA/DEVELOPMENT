"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.serializers.page_criteria_serializers import PageParams, SkuOrderQuantityPredictionCriteria
from ..models.sku_order_quantity_prediction import SkuOrderQuantityPrediction


class SkuOrderQuantityPredictionRepositoryInterface(ABC):

    @abstractmethod
    def find_all_sku_order_quantity_predictions(
            page_params: PageParams,
            criteria: SkuOrderQuantityPredictionCriteria) -> List[SkuOrderQuantityPrediction]:
        pass

    @abstractmethod
    def store_sku_order_quantity_prediction(self,
                                            sku_order_quantity_prediction: SkuOrderQuantityPrediction) -> SkuOrderQuantityPrediction:
        pass

    @abstractmethod
    def find_sku_order_quantity_prediction_by_record_id(self, record_id: int) -> Optional[SkuOrderQuantityPrediction]:
        pass

    @abstractmethod
    def find_sku_order_quantity_prediction_by_sku_number(self, sku_number: int) -> List[SkuOrderQuantityPrediction]:
        pass
