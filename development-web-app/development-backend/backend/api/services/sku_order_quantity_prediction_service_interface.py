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


class SkuOrderQuantityPredictionServiceInterface(ABC):

    @abstractmethod
    def get_all_predictions(self, page_params: PageParams, criteria: SkuOrderQuantityPredictionCriteria) -> List[
        SkuOrderQuantityPrediction]:
        pass

    @abstractmethod
    def create_sku_order_quantity_prediction(self, sku_order_quantity_prediction: SkuOrderQuantityPrediction) -> None:
        pass

    @abstractmethod
    def get_sku_order_quantity_prediction_by_record_id(self, record_id: int) -> Optional[SkuOrderQuantityPrediction]:
        pass

    @abstractmethod
    def calculate_demand_parameters(self, sku_number: int) -> tuple[None, None] | tuple[float, float]:
        pass
