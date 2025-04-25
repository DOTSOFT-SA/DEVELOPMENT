"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import inspect

from services import merge_csv_sku
from utils.database_connection import engine
from utils.database_helper_methods import is_table_empty_or_missing, assign_table_primary_key


def create_db_table(df, table_name, pk_column):
    """
    This function writes the DataFrame data into the database table. If the table does not exist, it is created.
    After the data insertion, the primary key constraint is assigned to the specified column.

    :param df: The DataFrame containing the data to be inserted into the table.
    :param table_name: The name of the target database table where the data should be inserted.
    :param pk_column: The column name to assign as the primary key in the database table.
    """
    print("\n" + "Writing data to the database...")
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',  # Re-creates the table with the data
        index=True
    )
    # Call the method to alter the table
    assign_table_primary_key(table_name, pk_column)


def main():
    """
    Main entry point of the script that checks if the 'sku_order_development' table exists and is populated.
    If the table is empty or missing, it populates the table with data and assigns a primary key.

    This function first checks if the specified table exists and contains data. If not, the second function
    fetches the data from the CSV file and writes it to the database, then assigns the primary key to
    the specified column.
    """
    print("\n" + "---- create_sku_order_development_db_table.py ----")

    table_name = 'sku_order_development'  # Define target table name
    try:
        inspector = inspect(engine)  # Lets you inspect the database
        if is_table_empty_or_missing(inspector, table_name):
            sku_order_development_df = merge_csv_sku.get_sku_order_development_df()
            create_db_table(sku_order_development_df, table_name, 'id')
            print(f"Data successfully inserted into the table: '{table_name}'")
        else:
            print(f"Table '{table_name}' already exists and contains data, no further action needed!")
    except Exception as e:
        # Instead, save the merged DataFrame to CSV file
        print("\n" + "Error: " + str(e))
        print("\n" + f"Failed to write '{table_name}' data into the database, stored to local .CSV file instead.")
        merge_csv_sku.save_table_to_csv(table_name)
