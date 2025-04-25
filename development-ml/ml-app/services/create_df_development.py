"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import Optional

import pandas as pd

from repositories.ml_repositories import SkuMetricRepository
from services.fetch_erp_development_service import fetch_erp_development_data
from utils.database_connection import AsyncSessionLocal


async def create_df_development(full_url: str, auth_url: str, user_id: int) -> pd.DataFrame:
    """
    1. Fetch all SkuMetric records for the given user_id.
    2. Fetch ERP development data using the provided URLs.
    3. Filter ERP data to keep only entries with 'id' matching SkuMetric.sku_order_record_id.
    4. Merge matching data into a single dictionary.
    5. Return a DataFrame with the specified columns in the desired order.

    @param full_url: The URL to fetch ERP data.
    @param auth_url: The URL to fetch the ERP API auth token.
    @param user_id: The user ID to filter SkuMetric records.

    @return: A pandas DataFrame with columns
    """

    # 1. Query SkuMetric records by user_id
    async with AsyncSessionLocal() as session:
        sku_metric_repo = SkuMetricRepository(session)
        sku_metrics = await sku_metric_repo.get_all_sku_metrics_by_user_id(user_id)
    # 2. Fetch ERP data
    data_records = await fetch_erp_development_data(full_url, auth_url, user_id)
    # 3. Build a dict of {sku_order_record_id: SkuMetric} for faster access
    sku_metric_dict = {
        metric.sku_order_record_id: metric for metric in sku_metrics if metric.sku_order_record_id is not None
    }
    # 4. Filter and merge
    rows = []
    for record in data_records:
        record_id: Optional[int] = record.get("id")
        # Check if the ERP record ID exists in the SKU metric dictionary
        if record_id in sku_metric_dict:
            sku_metric = sku_metric_dict[record_id]  # Retrieve the corresponding SKU metric object from dict
            # Merge data from ERP + SkuMetric
            merged_data = {
                "id": record_id,
                "order_date": record.get("order_date"),
                "sku_number": record.get("sku_number"),
                "sku_name": record.get("sku_name"),
                "class_display_name": record.get("class_display_name"),
                "order_item_price_in_main_currency": record.get("order_item_price_in_main_currency"),
                "order_item_unit_count": record.get("order_item_unit_count"),
                "cl_price": record.get("cl_price"),
                "is_weekend": sku_metric.is_weekend,
                "is_holiday": sku_metric.is_holiday,
                "mean_temperature": sku_metric.mean_temperature,
                "rain": sku_metric.rain,
                "average_competition_price_external": sku_metric.average_competition_price_external,
                "review_sentiment_score": sku_metric.review_sentiment_score,
                "review_sentiment_timestamp": sku_metric.review_sentiment_timestamp,
                "trend_value": sku_metric.trend_value,
            }
            # Append the merged record as (future) rows for the Dataframe
            rows.append(merged_data)

    # 5. Construct the DataFrame in the specified column order
    df = pd.DataFrame(rows, columns=[
        "id",
        "order_date",
        "sku_number",
        "sku_name",
        "class_display_name",
        "order_item_price_in_main_currency",
        "order_item_unit_count",
        "cl_price",
        "is_weekend",
        "is_holiday",
        "mean_temperature",
        "rain",
        "average_competition_price_external",
        "review_sentiment_score",
        "review_sentiment_timestamp",
        "trend_value",
    ])

    return df
