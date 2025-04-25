"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Nikos Pavlidis Innovation Engineer
 */
"""

from datetime import datetime
from typing import List

import holidays
import pandas as pd
import requests

from models.models import SkuMetric
from repositories.sku_metric_repository import SkuMetricRepository
from utils.database_connection import AsyncSessionLocal


def get_public_holidays(year: int) -> List[datetime]:
    """
    Fetch public holidays for Greece for a given year.

    @param year: The year for which public holidays need to be fetched.
    @return: A list of datetime objects representing public holidays in Greece for the given year.
    """
    gr_holidays = holidays.Greece(years=year)
    return list(gr_holidays.keys())


def add_weekend_holiday_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'is_weekend' and 'is_holiday' columns to a DataFrame based on the 'order_date' column.

    @param df: A pandas DataFrame containing an 'order_date' column.
    @return: The modified DataFrame with two additional columns:
             - 'is_weekend': A boolean column indicating whether the order_date is a weekend.
             - 'is_holiday': A boolean column indicating whether the order_date is a public holiday.
    """
    public_holidays = []
    df['order_date'] = pd.to_datetime(df['order_date'])
    years = df['order_date'].dt.year.unique()  # Extract the years from the 'order_date' column
    for year in years:  # Iterate over each year
        public_holidays.extend(get_public_holidays(year))  # Add holidays of each year (add list elements at once)
    public_holidays = set(public_holidays)  # Convert the list to a set to remove any duplicate holidays
    df['is_weekend'] = df['order_date'].dt.dayofweek >= 5  # if the day of the week is Saturday (5) or Sunday (6)
    df['is_holiday'] = df['order_date'].dt.date.isin(public_holidays)  # if the date is in the public holidays set
    return df


def get_historical_weather_open_meteo(date: datetime.date) -> tuple[float | None, bool]:
    """
    Fetch historical weather data (temperature and precipitation/rain) for a given date using the Open-Meteo API.

    @param date: A datetime.date object representing the date for which weather data is requested.
    @return: A tuple containing:
             - avg_temp (float or None): The average temperature (in Celsius) for the given date, or None if data is unavailable.
             - rain (bool): True if there was any precipitation (rain) on the given date, False otherwise.
    """
    # Base API URL for Open-Meteo historical weather data
    url = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        'latitude': 37.9838,  # Athens latitude
        'longitude': 23.7275,  # Athens longitude
        'start_date': date.strftime('%Y-%m-%d'),  # Format start date as YYYY-MM-DD
        'end_date': date.strftime('%Y-%m-%d'),  # Format end date as YYYY-MM-DD (same as start_date for one day)
        'hourly': 'temperature_2m,precipitation'  # Request hourly temperature and precipitation data
    }
    response = requests.get(url, params=params)
    data = response.json()
    # Check if hourly data is present in the response
    if 'hourly' in data:
        temperatures = data['hourly'].get('temperature_2m', [])  # Get hourly temperature data
        precipitation = data['hourly'].get('precipitation', [])  # Get hourly precipitation data
        # Calculate the average temperature if temperature data is available
        if temperatures:
            avg_temp = sum(temperatures) / len(temperatures)
        else:
            avg_temp = None
        # Determine if there was any precipitation
        rain = any(p > 0 for p in precipitation)
        # Return the average temperature and rain status
        return avg_temp, rain
    else:
        return None, None  # Return None values if no data is available


def add_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add weather-related columns to a DataFrame based on historical weather data.

    This function adds two new columns:
    - 'mean_temperature': The average temperature (in Celsius) for the order date.
    - 'rain': A boolean column indicating if there was precipitation (rain) on the order date.

    @param df: A pandas DataFrame containing an 'order_date' column with datetime or date values.
    @return: The modified DataFrame with the two above additional columns:
    """
    # Convert the 'order_date' column to datetime and extract only the date part
    df['date'] = pd.to_datetime(df['order_date']).dt.date
    # Fetch historical weather data (avg temperature and rain status) for each date from meteo
    weather_data = df['date'].apply(get_historical_weather_open_meteo)
    df['mean_temperature'] = weather_data.apply(lambda x: x[0])  # average temperature = first element of the tuple
    df['rain'] = weather_data.apply(lambda x: x[1])  # rain status = second element of the tuple
    # Return the DataFrame with the new columns added
    return df


async def process_sku_orders(session: AsyncSessionLocal(), erp_sku_order_development_data: list) -> None:
    """
    Main function to process SKU orders:
      1. Process the SKU data to enrich it with weekend/holiday and weather information.
      2. Store the processed records in the 'sku_metric' table using SkuMetricRepository.
    @param session: An active AsyncSession instance for performing database operations
    @param erp_sku_order_development_data: A list containing the user's SKU order data retrieved from the ERP
    @return: None
    """
    try:
        # Initialize the repositories for SKU metrics
        sku_metric_repo = SkuMetricRepository(session)
        # We do not want to work with DB records that already have populated these columns
        filtered_erp_sku_order_development_data = await sku_metric_repo.filter_in_db_with_null_columns(
            erp_sku_order_development_data,
            ["is_weekend", "is_holiday", "mean_temperature", "rain"],
            "sku_order_record_id")
        if not filtered_erp_sku_order_development_data:
            print("No rows found with NULL 'is_weekend, is_holiday, mean_temperature, rain'")
            return
        # Process the data in a DataFrame
        df = pd.DataFrame(filtered_erp_sku_order_development_data)
        # Add weekend and holiday columns to the DataFrame
        df = add_weekend_holiday_columns(df)
        print("add_weekend_holiday_columns: success")
        # Add weather-related columns to the DataFrame
        df = add_weather_columns(df)
        print("add_weather_columns: success")
        # Store each processed record in the 'sku_metric' df
        for _, row in df.iterrows():
            # Build the Pydantic SkuMetric model with the processed data
            sku_metric = SkuMetric(
                is_weekend=row.get("is_weekend"),
                is_holiday=row.get("is_holiday"),
                mean_temperature=row.get("mean_temperature"),
                rain=row.get("rain"),
                sku_order_record_id=row.get("id")
            )
            # Save or update the record in the database
            await sku_metric_repo.update_sku_metric_holidays_weekends_weather(sku_metric)
        print("Data of 'holidays, weekends, weather' added successfully in sku_metric.")
    except requests.HTTPError as http_err:
        raise requests.HTTPError(f"process_sku_orders(): HTTP error occurred when calling ERP API: {http_err}")
    except Exception as exc:
        raise Exception(f"process_sku_orders(): An unexpected error occurred: {exc}")


async def main(erp_sku_order_development_data: list):
    try:
        async with AsyncSessionLocal() as session:
            await process_sku_orders(session, erp_sku_order_development_data)
    except Exception as e:
        await session.rollback()
        raise e
