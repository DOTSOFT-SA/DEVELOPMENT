"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from dataclasses import dataclass

from ...models.dtos.merged_sku_metric_dto import MergedSkuMetricDto
from ...models.sku_order_quantity_prediction import SkuOrderQuantityPrediction


@dataclass
class ModelInferenceDto:
    """
    Holds both the merged_sku_metric_dto (local + ERP data)
    and the resulting sku_order_quantity_prediction from the inference.
    """
    merged_sku_metric_dto: MergedSkuMetricDto
    sku_order_quantity_prediction: SkuOrderQuantityPrediction
