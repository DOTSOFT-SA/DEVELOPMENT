"""
/*
 * Copyright 2024 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import json
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
import serpapi


def load_search_terms_from_file(file_path: str) -> Dict[str, str]:
    """
    Load search terms from a specific JSON file.

    @params file_path: str Path to the `google_trends_categories.json` file.
    @return: dict A dictionary where `class_display_name_uk` is the key and `search_term` is the value.
    """
    search_terms = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            # Load JSON content
            data = json.load(json_file)
            # Extract `class_display_name_uk` and `search_term`
            for key, value in data.items():
                search_terms[value['class_display_name_el']] = value['search_term']
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
    return search_terms


def add_sku_numbers(group: pd.DataFrame, extracted_data: List[Dict[str, Any]]) -> None:
    """
    Add `sku_number` from the category group to the extracted data.

    @params group: pd.DataFrame The DataFrame group for the current category.
    @params extracted_data: List[Dict[str, Any]] The list of dictionaries containing extracted Google Trends data.
    @return: None
    """
    for idx, row in group.iterrows():  # Iterate through each row in the current category group
        for data in extracted_data:
            data['sku_number'] = row['sku_number']  # Add the SKUNumber from the current row to the extracted data


def serpapi_google_trends_data(account_api_key: str, q_parameters: str, date_range: str = "today 12-m") -> Dict[
    str, Any]:
    """
    Fetch data from the Google Trends API with specific query parameters.

    @params account_api_key: str The API key for authentication with SerpAPI.
    @params q_parameters: str The search term for Google Trends.
    @params date_range: str The date range for fetching trends data, e.g., "2023-01-01 2025-01-01".
    @return: Dict[str, Any] The JSON response from the Google Trends API.
    """
    client = serpapi.Client(api_key=account_api_key)
    params = {  # Define the call parameters
        "engine": "google_trends",  # Specify the engine as Google Trends
        "q": q_parameters,  # Set the query parameters
        "data_type": "TIMESERIES",  # Request timeseries data
        "date": date_range,  # Data for the given date_range
        "geo": "GR"  # Region: Greece
    }
    return client.search(params)  # Fetch the data from the API


def extract_required_data(json_data: dict, category_label: str) -> List[Dict[str, Any]]:
    """
    Extract required fields like `date`, `query`, and `value` from the JSON response.

    @params json_data: dict The JSON response from the Google Trends API.
    @params category_label: str The label of the category being processed.
    @return: List[Dict[str, Any]] A list of dictionaries containing extracted data for `date`, `query`, and `value`.
    """
    timeline_data = json_data.get("interest_over_time", {}).get("timeline_data", [])  # Get the timeline data
    extracted_data = []  # List to store the desired fields: "date", "query", and "value"
    # Iterate through each time period
    for time_period in timeline_data:
        extracted_date = time_period.get("date", "N/A")  # Extract the date
        values = time_period.get("values", [])  # Extract the values
        # Loop through each query-value pair
        for value_data in values:
            extracted_query = value_data.get("query", "N/A")  # Extract the query
            extracted_value = value_data.get("value", "N/A")  # Extract the value
            # Append the extracted data to the list
            extracted_data.append({
                "class_display_name": category_label,
                "query": extracted_query,
                "date": extracted_date,
                "value": extracted_value
            })
    return extracted_data


def map_trend_values_by_date(
        original_df: pd.DataFrame, trend_data: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Map trend values to the original DataFrame by date.
    @params original_df: pd.DataFrame The original DataFrame containing ERP SKU order development data.
    @params trend_data: List[Dict[str, Any]] The expanded trend data with individual timestamps.
    @return: pd.DataFrame The updated DataFrame with trend values mapped by date.
    """
    # Convert the trend data into a DataFrame
    trend_df = pd.DataFrame(trend_data)
    # Convert the 'timestamp' column to datetime and extract the date part
    trend_df['timestamp'] = pd.to_datetime(trend_df['timestamp']).dt.date
    # Rename columns to match the original DataFrame's structure
    trend_df.rename(columns={"value": "trend_value"}, inplace=True)
    # Convert the 'order_date' column in the original DataFrame to datetime
    original_df["order_date"] = pd.to_datetime(original_df["order_date"])
    # Create a copy of the relevant columns from the original DataFrame
    copy_original_df = original_df[['id', 'sku_number', 'sku_name', 'class_display_name', 'order_date']].copy()
    # Initialize the 'trend_value' column with None
    copy_original_df["trend_value"] = None
    # Iterate row by row to find the matching trend value
    for index, row in copy_original_df.iterrows():
        category = row["class_display_name"]  # Get the category for the current row
        date_val = row["order_date"].date()  # Get the date for the current row
        # Find the trend value corresponding to the current category and date
        trend_value = trend_df[
            (trend_df["class_display_name"] == category) &
            (trend_df["timestamp"] == date_val)
            ]["trend_value"]
        # If a matching trend value is found, assign it to the 'trend_value' column of the result DataFrame
        if not trend_value.empty:
            copy_original_df.at[index, "trend_value"] = trend_value.values[0]
    # Return the result df
    return copy_original_df


def fetch_trends(
        df: pd.DataFrame, serp_api_key: str, search_terms: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Fetch Google Trends data for each category in the DataFrame.

    @params df: pd.DataFrame The DataFrame containing ERP SKU order development data grouped by `class_display_name`.
    @params serp_api_key: str The API key for authentication with SerpAPI.
    @params search_terms: Dict[str, str] A dictionary mapping `class_display_name` to search terms.
    @return: List[Dict[str, Any]] A list of dictionaries containing extracted trend data for all categories.
    """
    all_extracted_data = []
    # Iterate through each category group
    for category, group_df in df.groupby("class_display_name"):
        # Check if the category exists in search_terms
        if category in search_terms:
            # Extract the search_term from the dictionary for the current category
            search_term = search_terms[category]
            # Ensure search_term is not None
            if search_term:
                # Define date range
                start_date = group_df["order_date"].min().strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')  # today's date
                date_range = f"{start_date} {end_date}"
                # Fetch data from SerpAPI using the search_term and date_range
                json_data = serpapi_google_trends_data(serp_api_key, search_term, date_range)
                if json_data and "interest_over_time" in json_data:
                    # Extract the required data (e.g., 'query', 'date', and 'value')
                    extracted_data = extract_required_data(json_data, category)
                    add_sku_numbers(group_df, extracted_data)  # Add sku_number to each extracted data entry
                    all_extracted_data.extend(extracted_data)
            else:
                print(f"No search_term found for category: {category}")
        else:
            print(f"Category '{category}' not found in search_terms.")
    return all_extracted_data
