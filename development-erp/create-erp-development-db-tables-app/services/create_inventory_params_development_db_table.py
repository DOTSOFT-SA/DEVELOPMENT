"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import numpy as np
import pandas as pd
from sqlalchemy import inspect

from services import merge_csv_sku
from utils.database_connection import engine
from utils.database_helper_methods import is_table_empty_or_missing, assign_table_primary_key
from utils.sql_constant_queries import SELECT_SKU_NUMBER_QUERY


# ========================================================
# Data Processing Functions
# ========================================================
def get_sku_order_data(table_name='sku_order_development') -> pd.DataFrame:
    """
    Reads the 'sku_number' data from the specified table.

    This function connects to the database and reads the data from the specified table.
    If the table is missing or empty, it raises an Exception.

    :param table_name: The name of the table to fetch the data from (default is 'sku_order_development').
    :return: A DataFrame containing the 'sku_number' data from the table.
    :raises Exception: If there's an error reading from the table or if the table is empty.
    """
    try:
        select_query = SELECT_SKU_NUMBER_QUERY.format(table_name=table_name)
        df = pd.read_sql(select_query, engine)
        if df.empty:
            raise ValueError(f"The table '{table_name}' is empty.")
        return df
    except Exception as e:
        raise Exception(f"Failed to read data from table '{table_name}': {e}")


def generate_synthetic_inventory_params(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates synthetic inventory parameters for each 'sku_number' row in a DataFrame.

    This method adds synthetic columns like fixed order cost, unit cost, penalty cost, etc.,
    to simulate inventory parameters for each SKU number in the given DataFrame.

    :param df: A DataFrame containing 'sku_number' rows to generate synthetic inventory parameters for.
    :return: A DataFrame with the synthetic inventory parameters added.
    """
    n = len(df)
    np.random.seed(42)  # For reproducibility
    # Stock level
    df['stock_level'] = np.random.randint(100, 800, size=n)  # e.g., between 100 and 800
    # Time period T: Assume it's constant for simplicity
    df['time_period_t'] = 1.0  # Example: 1 week or 1 time unit
    # Fixed Order Cost (K): Randomly generated between 20 and 200 euros
    df['fixed_order_cost_k'] = (np.random.randint(20, 200, size=n).astype(float)).round(2)
    # Unit Cost (c): Randomly generated between 10 and 100 euros per unit
    df['unit_cost_c'] = (np.random.randint(10, 100, size=n).astype(float)).round(2)
    # Penalty Cost (p): Correlated with unit cost (20%–80% of unit cost)
    df['penalty_cost_p'] = (df['unit_cost_c'] * np.random.uniform(0.2, 0.8, size=n)).round(2)
    # Holding Cost Rate (i): Random between 1% and 5% per time period
    df['holding_cost_rate_i'] = (np.random.uniform(0.01, 0.05, size=n)).round(2)
    # Truckload Capacity (FTL): Randomly generated between 30 and 100 units
    df['truckload_capacity_ftl'] = (np.random.randint(30, 100, size=n).astype(float)).round(2)
    # Transportation Cost (TR): Base cost (100–300 euros) + scaling factor
    base_transport = np.random.randint(100, 300, size=n).astype(float)
    df['transportation_cost_tr'] = (base_transport + (0.1 * df['unit_cost_c'])).round(2)
    # Add a created_at timestamp
    df['created_at'] = pd.Timestamp.utcnow()
    # Return DataFrame with added synthetic inventory parameters
    return df


def process_and_merge_data() -> pd.DataFrame:
    """
    Orchestrates the process of fetching SKU data and generating synthetic inventory parameters,
    for each row, and returns the final merged DataFrame.

    :return: A DataFrame containing the merged SKU data with added synthetic inventory parameters.
    """
    base_df = get_sku_order_data()  # get a df with column 'sku_number' only
    # Generate synthetic data columns for each row (extend the df)
    final_df = generate_synthetic_inventory_params(base_df)
    # Return final DataFrame
    return final_df


def create_db_table_with_index_label(df, table_name, pk_column):
    """
    Creates a table in the database from the provided DataFrame and assigns a primary key.

    This function inserts the DataFrame into the specified table, ensuring that an index is
    created as the primary key column. If the insertion fails, the data is saved to a CSV file.

    :param df: The DataFrame to insert into the table.
    :param table_name: The name of the table to create in the database.
    :param pk_column: The name of the primary key column to assign to the table.
    :raises Exception: If there is an error during the table creation or data insertion.
    """
    try:
        df.index = df.index + 1  # Set ID column starting from 1
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',  # appends if table exists, or creates if not
            index=True,  # to have an index column
            index_label=pk_column  # rename index to 'id'
        )
        # Assign PK
        assign_table_primary_key(table_name, pk_column)
    except Exception as e:
        # Instead, save the merged DataFrame to CSV file
        print("\n" + "Error: " + str(e))
        print("\n" + f"Failed to write '{table_name}' data into the database, stored to local .CSV file instead.")
        merge_csv_sku.save_table_to_csv(table_name)


# ========================================================
# Main Entry Point
# ========================================================
def main():
    """
    Main entry point of the script that orchestrates the creation of the 'inventory_params_development' table.

    This function checks if the source table exists and contains data, processes and merges data,
    and finally creates a new table with synthetic inventory parameters in the database.
    """
    print("\n" + "---- create_inventory_params_development_db_table.py ----")
    try:
        source_table_name = 'sku_order_development'  # We are checking this table, reading from it
        new_table_name = 'inventory_params_development'  # Target table
        inspector = inspect(engine)  # Inspect the database
        # Check if source table is empty or missing
        if is_table_empty_or_missing(inspector, source_table_name):
            print(f"Table '{source_table_name}' does not exist or is empty. Stopping process.")
            return
        # Check: we do not want to modify the table if already used (prevent mistake)
        if is_table_empty_or_missing(inspector, new_table_name):
            # Process and merge data
            final_merged_df = process_and_merge_data()
            print("\nWriting data to the database table:", new_table_name)
            create_db_table_with_index_label(final_merged_df, new_table_name, 'id')
            print(f"Data successfully inserted into the table: '{new_table_name}'")
        else:
            print("Table '{}' already exists and contains data, no further action needed!".format(new_table_name))
    except Exception as e:
        print("\n" + "Error:", str(e))
