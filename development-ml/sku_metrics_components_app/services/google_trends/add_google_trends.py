"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

import pandas as pd
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import SkuMetric
from repositories.sku_metric_repository import SkuMetricRepository
from services.google_trends.shared import load_search_terms_from_file, fetch_trends, map_trend_values_by_date
from utils.database_connection import AsyncSessionLocal
from utils.settings import settings


def parse_date_range_cross_year(date_range_str: str) -> Tuple[datetime, datetime]:
    """
    Parse a date range string formatted as 'Dec 31, 2023 – Jan 6, 2024'
    and return the start and end datetime objects.

    @params date_range_str: str The date range string to parse, spanning two different years.
    @return: Tuple[datetime, datetime] A tuple containing the start and end datetime objects for the range.
    """
    # Split the input string
    parts = date_range_str.split('–')
    start_str = parts[0].strip()
    end_str = parts[1].strip()
    # Parse the start date (e.g., 'Dec 31, 2023')
    start_date = datetime.strptime(start_str, "%b %d, %Y")
    # Parse the end date (e.g., 'Jan 6, 2024')
    end_date = datetime.strptime(end_str, "%b %d, %Y")
    # Return tuple dates
    return start_date, end_date


def parse_date_range(date_range_str: str) -> Tuple[datetime, datetime]:
    """
    Parse a date range string and return the start and end datetime objects.

    @params date_range_str: str The date range string, e.g., 'Jul 23 – 29, 2023' or 'May 26 – Jun 1, 2024'.
    @return: Tuple[datetime, datetime] A tuple containing the start and end datetime objects for the range.
    """

    # Split the input string into start and end parts based on the separator '–'
    # Example: 'Jul 23 – 29, 2023' becomes ['Jul 23 ', ' 29, 2023']
    parts = date_range_str.split('–')
    start_str = parts[0].strip()  # Extract and trim the start date string
    end_str = parts[1].strip()  # Extract and trim the end date string

    # Extract and parse the year from the end date string
    # Example: '29, 2023' becomes year = 2023
    year = int(end_str.split(',')[1].strip())

    # Parse the start date
    if len(start_str.split()) == 2:  # If the start date string contains only month and day
        # Example: 'Jul 23' + ' 2023' -> 'Jul 23 2023'
        start_date = datetime.strptime(f"{start_str} {year}", "%b %d %Y")
    else:  # If the start date string contains full details including the year
        # Example: 'May 26, 2024' (already complete)
        start_date = datetime.strptime(start_str + f" {year}", "%b %d %Y")

    # Parse the end date
    if len(end_str.split()) == 2:  # If the end date string contains only day and year
        # Use the month from the start date for the end date
        # Example: '29, 2023' -> 'Jul 29, 2023'
        end_month = start_date.strftime("%b")
        end_date = datetime.strptime(f"{end_month} {end_str}", "%b %d, %Y")
    else:  # If the end date string contains full details including the month, day, and year
        # Example: 'Jun 1, 2024' (already complete)
        end_date = datetime.strptime(end_str, "%b %d, %Y")

    return start_date, end_date


def generate_timestamps(date_range: str) -> List[datetime]:
    """
    Generate a list of timestamps for each day in the provided date range.

    @params date_range: str The date range string, e.g., '2023-01-01 2025-01-01'.
    @return: List[datetime] A list of datetime objects representing each day in the range.
    """
    if len(date_range) < 23:  # bigger text = cross_year date
        start_date, end_date = parse_date_range(date_range)  # Parse the date range
    else:
        start_date, end_date = parse_date_range_cross_year(date_range)
    timestamps = []
    current_date = start_date
    while current_date <= end_date:  # Generate timestamps from start to end date
        timestamps.append(current_date)
        current_date += timedelta(days=1)  # Increment the current date by one day
    return timestamps  # Return the list of timestamps


def expand_trend_data(trend_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Expand trend data to include individual timestamps for each day in the date range.

    @params trend_data: List[Dict[str, Any]] The original trend data with date ranges.
    @return: List[Dict[str, Any]] The expanded trend data with individual timestamps for each day.
    """
    expanded_data = []
    for row in trend_data:
        timestamps = generate_timestamps(row['date'])  # Generate timestamps based on the date range
        for timestamp in timestamps:  # Create the rows for each timestamp
            expanded_data.append({
                'sku_number': row['sku_number'],
                'class_display_name': row['class_display_name'],
                'query': row['query'],
                'timestamp': timestamp,
                'value': row['value']
            })
    return expanded_data


async def process_google_trends(
        session: AsyncSession, erp_sku_order_development_data: List[Dict[str, Any]]
) -> None:
    """
    Process Google Trends data and update the database with trend values.
    1) Filter DB for records with trend_value IS NULL.
    2) Convert those records to a df.
    3) For each category, fetch SerpAPI data and map 'trend_value' by date.
    4) Update the DB with the newly found 'trend_value'.
    5) Retry the process once if an HTTP error or unexpected error occurs.

    @params session: AsyncSession
        The active asynchronous database session used to query and update the database.
    @params erp_sku_order_development_data: List[Dict[str, Any]]
        A list of dictionaries representing SKU order data retrieved from the ERP.
    @return: None
        Updates the database with fetched Google Trends data for records with NULL 'trend_value'.
        Logs progress and results for debugging and monitoring purposes.
    """

    max_retries = 2  # Total attempts will be 2 (1 retry)

    for attempt in range(1, max_retries + 1):
        try:
            # Keep DB records that do not have 'trend_value'
            sku_metric_repo = SkuMetricRepository(session)
            filtered_erp_sku_order_development_data = await sku_metric_repo.filter_in_db_with_null_columns(
                erp_sku_order_development_data,
                ["trend_value"],
                "sku_order_record_id"
            )
            if not filtered_erp_sku_order_development_data:
                print("No rows found with NULL 'trend_value'.")
                return

            # Define search terms
            root_path = os.getcwd()
            google_trends_json_file_path = os.path.join(root_path, "configs", "google_trends_categories.json")
            search_terms = load_search_terms_from_file(google_trends_json_file_path)

            # Convert these to a DataFrame
            df = pd.DataFrame(filtered_erp_sku_order_development_data)
            # Convert the 'order_date' column to datetime format, coercing errors
            df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')

            # 1. For each 'class_display_name', fetch from SerpAPI
            all_trend_data = fetch_trends(df, settings.serp_api_key, search_terms)
            if not all_trend_data:
                print("No trend data fetched. Nothing to update.")
                return

            # 2. Expand the extracted trend data to include individual timestamps
            expanded_trend_data = expand_trend_data(all_trend_data)
            # 3. Map the fetched trend values back to df by date
            mapped_df = map_trend_values_by_date(df,
                                                 expanded_trend_data)  # it has a "trend_value" column set for each row

            # 4. Update the DB for each row that got a new Trend Value
            for _, row in mapped_df.iterrows():
                if row.get("trend_value") is not None:
                    # Create SkuMetric object with the updated trend_value
                    sku_metric = SkuMetric(
                        sku_order_record_id=row["id"],
                        trend_value=row["trend_value"]
                    )
                    await sku_metric_repo.update_sku_metric_trend_value(sku_metric)

            print("Google Trends values successfully updated in the DB.")
            break  # If processing is successful, exit the retry loop

        except requests.HTTPError as http_err:
            print(f"Attempt {attempt} of {max_retries} failed due to HTTPError: {http_err}")
            if attempt == max_retries:
                raise requests.HTTPError(
                    f"process_google_trends(): HTTP error occurred after {attempt} attempts: {http_err}")
            # Wait before retrying
            await asyncio.sleep(2)
        except Exception as exc:
            print(f"Attempt {attempt} of {max_retries} failed due to an unexpected error: {exc}")
            if attempt == max_retries:
                raise Exception(f"process_google_trends(): Unexpected error after {attempt} attempts: {exc}")
            # Wait before retrying
            await asyncio.sleep(2)


async def main(erp_sku_order_development_data: list):
    try:
        async with AsyncSessionLocal() as session:
            await process_google_trends(session, erp_sku_order_development_data)
    except Exception as e:
        await session.rollback()
        raise e
