"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MergedSkuMetricDto:
    """
    A merged DTO combining both external ERP data (e.g., order_date, sku_name, etc.)
    and local SkuMetric fields (e.g., is_weekend, mean_temperature, etc.).
    """
    sku_order_record_id: int
    order_date: Optional[datetime] = None
    sku_number: Optional[int] = None
    sku_name: Optional[str] = None
    class_display_name: Optional[str] = None
    order_item_price_in_main_currency: Optional[float] = None
    order_item_unit_count: Optional[int] = None
    cl_price: Optional[float] = None
    is_weekend: Optional[bool] = None
    is_holiday: Optional[bool] = None
    mean_temperature: Optional[float] = None
    rain: Optional[bool] = None
    average_competition_price_external: Optional[float] = None
    review_sentiment_score: Optional[float] = None
    review_sentiment_timestamp: Optional[datetime] = None
    trend_value: Optional[int] = None
