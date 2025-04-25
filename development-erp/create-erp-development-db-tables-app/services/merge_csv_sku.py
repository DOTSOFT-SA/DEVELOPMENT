"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import os

import pandas as pd


def process_and_merge_data() -> pd.DataFrame:
    """
    Processes and merges data from multiple CSV files into a single DataFrame.
    This function loads the product SKU, order item, and competition CSV files, processes the data
    (e.g., renaming columns, converting date formats), filters rows based on certain criteria,
    and merges them into a single DataFrame.

    :return: A merged pandas DataFrame containing the combined data from the product SKU, order item, and competition files.
    """
    file_list = ['product_sku.csv', 'order_item.csv', 'competition.csv']
    data_frames = []
    # Load the .CSV files into a list of DataFrames
    for file_name in file_list:
        file_path = os.path.join('data', file_name)
        # Load data from the CSV
        df = pd.read_csv(file_path)
        print(f"File '{file_name}' loaded successfully.")
        # Remove 'id' columns if they exist
        df = df.loc[:, ~df.columns.str.lower().str.contains('^id$')]
        # In competition.csv, rename 'sku' to 'sku_number'
        if (file_name == 'competition.csv') and ('sku' in df.columns):
            df.rename(columns={'sku': 'sku_number'}, inplace=True)
        # Add the new DataFrame to the list
        data_frames.append(df)
    print("All .CSV files converted to DataFrames and each added to the list.")
    # Extract individual DataFrames
    product_sku_df = data_frames[0]  # product_sku.csv
    order_item_df = data_frames[1]  # order_item.csv
    competition_df = data_frames[2]  # competition.csv
    print("\n" + "All DataFrames extracted successfully.")
    # Convert date columns to datetime
    competition_df['price_date'] = pd.to_datetime(competition_df['price_date'], errors='coerce')
    order_item_df['order_date'] = pd.to_datetime(order_item_df['order_date'], errors='coerce')
    print("Date columns converted successfully.")
    # Drop rows with NaT in date columns
    competition_df.dropna(subset=['price_date'], inplace=True)
    order_item_df.dropna(subset=['order_date'], inplace=True)
    print("Rows with invalid dates dropped.")
    # For 'competition_df', keep only rows where 'price_date'
    # is closest to the 'order_date' and not later than 'order_date'
    print("\n" + "Filtering 'competition_df' for closest 'price_date' to 'order_date' (may take a while)...")
    closest_rows = []
    for _, order_row in order_item_df.iterrows():
        sku_number = order_row['sku_number']
        order_date = order_row['order_date']
        # Filter competition rows with 'price_date <= order_date'
        comp_rows = competition_df[
            (competition_df['sku_number'] == sku_number) &
            (competition_df['price_date'] <= order_date)
            ]
        if not comp_rows.empty:
            # Reset index to avoid KeyError
            comp_rows = comp_rows.reset_index(drop=True)
            # Pick row with 'price_date' closest to order_date
            closest_row = comp_rows.loc[
                (comp_rows['price_date'] - order_date).abs().argsort()[:1]
            ].copy()
            # Add 'order_date' to match columns during merge
            closest_row.loc[:, 'order_date'] = order_date
            closest_rows.append(closest_row)
        else:
            # If nothing before or on 'order_date', pick next-later date
            comp_rows_later = competition_df[
                (competition_df['sku_number'] == sku_number) &
                (competition_df['price_date'] > order_date)
                ]
            if not comp_rows_later.empty:
                comp_rows_later = comp_rows_later.reset_index(drop=True)
                closest_row = comp_rows_later.loc[
                    (comp_rows_later['price_date'] - order_date).abs().argsort()[:1]
                ].copy()
                closest_row.loc[:, 'order_date'] = order_date
                closest_rows.append(closest_row)

    # Combine all the closest (in terms of date) rows into a single DataFrame, resetting the index
    competition_df_filtered = pd.concat(closest_rows, ignore_index=True)
    print("Filtered 'competition_df' created.")
    # Merge 'competition_df_filtered' with 'order_item_df' on ['sku_number','order_date']
    print("\n" + "Merging 'competition_df_filtered' with 'order_item_df'...")
    merged_df = pd.merge(
        order_item_df,
        competition_df_filtered,
        on=['sku_number', 'order_date'],
        how='left',
        suffixes=('', '_comp')
    )
    print("First merge completed.")
    # Finally, merge (the above merged DataFrame) with 'product_sku_df' on 'sku_number' column
    print("Merging now with product_sku_df...")
    final_merged_df = pd.merge(
        merged_df,
        product_sku_df,
        on='sku_number',
        how='left'
    )
    print("Second merge completed.")
    # Re-order columns to put 'product_sku_df' columns first
    product_sku_columns = product_sku_df.columns.tolist()
    remaining_columns = [col for col in final_merged_df.columns if col not in product_sku_columns]
    final_merged_df = final_merged_df[product_sku_columns + remaining_columns]
    print("\n" + "Column re-ordering completed.")
    # Return final DataFrame
    return final_merged_df


def apply_post_processing(df) -> pd.DataFrame:
    """
    Applies post-processing steps to the merged DataFrame.
    This function performs several edits on the DataFrame, such as:
    - Removing dots in the 'sku_short_description' column (if it exists)
    - Setting the 'id' column to start from 1
    - Converting 'order_date' to datetime format
    - Converting 'price_date' to a date format (YYYY-MM-DD)

    :param df: The DataFrame to apply post-processing on.
    :return: The DataFrame after applying post-processing changes.
    """
    # Edit 1: Remove dots in 'sku_short_description'
    if 'sku_short_description' in df.columns:
        df['sku_short_description'] = df['sku_short_description'].str.replace('.', '', regex=False)
    # Edit 2: Set ID column starting from 1
    df.index = df.index + 1
    df.index.name = 'id'
    # Edit 3: Change 'order_date' is in datetime format
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    # Edit 4: 'price_date' format to 'DATE' (YYYY-MM-DD)
    if 'price_date' in df.columns:
        df['price_date'] = pd.to_datetime(df['price_date']).dt.date
    # Return DataFrame
    print("Post-processing completed.")
    return df


def save_table_to_csv(table_name):
    """
    Saves the merged and post-processed DataFrame to a CSV file.
    This function processes and merges data from various sources, applies post-processing,
    and saves the resulting DataFrame to a CSV file.

    :param table_name: The name of the table to save as a CSV file.
    """
    try:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        output_file_csv = os.path.join(output_dir, f"{table_name}.csv")
        # Process and merge data
        final_merged_df = process_and_merge_data()
        # Apply post-processing changes
        final_merged_df = apply_post_processing(final_merged_df)
        # Store into .CSV
        final_merged_df.to_csv(output_file_csv, index=True, encoding='utf-8-sig')
        print(f"Data successfully saved to: {output_file_csv}")
    except Exception as e:
        print(f"Failed to save the DataFrame '{table_name}' to CSV: {e}")


def get_sku_order_development_df() -> pd.DataFrame:
    """
    Returns the merged and post-processed SKU order development DataFrame.
    This function processes and merges the relevant data, applies post-processing,
    and returns the final SKU order development DataFrame.

    :return: The final SKU order development DataFrame.
    """
    try:
        # Process and merge data
        final_merged_df = process_and_merge_data()
        # Apply post-processing changes
        sku_order_development_df = apply_post_processing(final_merged_df)
        print("CSV data successfully merged into the DataFrame: 'sku_order_development_df'")
        return sku_order_development_df
    except Exception as e:
        # Instead, save the merged DataFrame to CSV file
        print("Error - CSV data failed to merged into the DataFrame ")
        print(str(e))
