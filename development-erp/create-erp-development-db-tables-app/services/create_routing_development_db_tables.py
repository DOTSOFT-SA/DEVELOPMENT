"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import os

import numpy as np
import pandas as pd
from sqlalchemy import inspect

from utils.database_connection import engine
from utils.database_helper_methods import is_table_empty_or_missing, assign_table_primary_key, assign_unique_key, \
    assign_foreign_key, convert_type_text_to_varchar


# ========================================================
# Synthetic Data Creation (with basic logic)
# ========================================================
def create_vehicle_data() -> pd.DataFrame:
    """
    Generates synthetic data for the 'vehicle_development' table.
    Returns a pandas DataFrame with synthetic data for 'vehicle_development':
      - vehicle_id:      Unique ID for each vehicle
      - capacity:        Random capacity
      - cost_per_trip:   Cost for using this vehicle in one trip, correlated with capacity
      - created_at:      Timestamp

    :return: A pandas DataFrame containing synthetic data for 5 vehicles.
    """
    np.random.seed(42)
    # Let's create 5 vehicles
    np.random.seed(42)
    vehicle_rows = []
    # Let's create 5 vehicles
    for idx in range(5):
        vehicle_id = 100 + idx
        # Capacity from 80..120 (so no single vehicle can cover very large demands alone)
        capacity = np.random.randint(80, 121)
        # Cost is a base random + small fraction of capacity
        base_cost = np.random.uniform(10, 20)
        cost_per_trip = round(base_cost + capacity * 0.01, 2)
        vehicle_rows.append({
            'vehicle_id': vehicle_id,
            'capacity': capacity,
            'cost_per_trip': cost_per_trip,
            'created_at': pd.Timestamp.utcnow()
        })
    return pd.DataFrame(vehicle_rows)


def create_location_data() -> pd.DataFrame:
    """
    Generates synthetic data for the 'location_development' table.
    Returns a pandas DataFrame with synthetic data for 'location_development':
      - location_id:  Unique ID for each location
      - location_name:  Name of the warehouse
      - demand:       Basic demand, 0 if depot
      - is_depot:     Boolean indicating if this location is a depot
      - created_at:   Timestamp

    :return: A pandas DataFrame containing synthetic data for 6 locations.
    """
    np.random.seed(43)
    # Create 6 locations, ID from 0..5, where location 0 is the depot (demand=0).
    # Warehouse locations in Thessaloniki, Greece
    warehouse_areas = [
        "ΚΕΝΤΡΙΚΗ ΑΠΟΘΗΚΗ",  # location 0
        "ΑΠΟΘΗΚΗ ΚΑΤΑΣΤΗΜΑΤΟΣ ΚΑΛΟΧΩΡΙΟΥ",
        "ΑΠΟΘΗΚΗ ΚΑΤΑΣΤΗΜΑΤΟΣ ΣΙΝΔΟΥ",
        "ΑΠΟΘΗΚΗ ΚΑΤΑΣΤΗΜΑΤΟΣ ΔΙΑΒΑΤΩΝ",
        "ΑΠΟΘΗΚΗ ΚΑΤΑΣΤΗΜΑΤΟΣ ΚΑΛΑΜΑΡΙΑΣ",
        "ΑΠΟΘΗΚΗ ΚΑΤΑΣΤΗΜΑΤΟΣ ΕΥΚΑΡΠΙΑΣ"
    ]
    num_locations = len(warehouse_areas)  # 6 locations

    location_rows = []
    for loc_id in range(num_locations):
        is_depot = (loc_id == 0)  # Assume first location is the depot
        # Increase demands to force multiple vehicle usage
        demand = 0 if is_depot else np.random.randint(30, 71)  # e.g. 30..70 units
        location_rows.append({
            'location_id': loc_id,
            'location_name': warehouse_areas[loc_id],  # Assign Greek warehouse names
            'demand': demand,
            'is_depot': is_depot,
            'created_at': pd.Timestamp.utcnow()
        })
    return pd.DataFrame(location_rows)


def create_route_data() -> pd.DataFrame:
    """
    Generates synthetic data for the 'route_development' table.
    Returns a pandas DataFrame with synthetic data for 'route_development':
      - route_id:              Unique ID for each route
      - distance:              Distance for traveling between locations
      - traffic_factor:        Factor to scale distance or cost, correlated with distance
      - source_location_id:    The origin location
      - destination_location_id: The target location
      - created_at:            Timestamp

    :return: A pandas DataFrame containing synthetic route data.
    """
    np.random.seed(44)
    route_rows = []
    route_id_counter = 200
    location_ids = list(range(6))  # 0..5
    # Iterate each (source) location
    for src in location_ids:
        for dst in location_ids:
            if src != dst:
                if src == 0 or dst == 0:
                    # Depot <-> location distances are bigger: discourage returning
                    distance = np.random.randint(30, 51)  # 30..50
                    traffic_factor = round(np.random.uniform(1.1, 1.4), 2)
                else:
                    # Inter-location distances are smaller: encourage traveling among locations
                    distance = np.random.randint(5, 16)   # 5..15
                    traffic_factor = round(np.random.uniform(1.0, 1.2), 2)
                route_rows.append({
                    'route_id': route_id_counter,
                    'distance': float(distance),
                    'traffic_factor': traffic_factor,
                    'source_location_id': src,
                    'destination_location_id': dst,
                    'created_at': pd.Timestamp.utcnow()
                })
                route_id_counter += 1
    return pd.DataFrame(route_rows)


# ========================================================
# Main Entry Point
# ========================================================
def create_table(table_name, create_data_function, inspector, engine):
    """
    Checks if a table exists and is populated. If not, creates the table and populates it with synthetic data.
    This method uses the specified data creation function to generate data and insert it into the table.
    If the table is missing or empty, it will be created and populated with synthetic data.

    :param table_name: The name of the table to check and populate.
    :param create_data_function: The function used to generate synthetic data for the table.
    :param inspector: SQLAlchemy inspector object used to inspect the database.
    :param engine: SQLAlchemy engine object to interact with the database.
    """
    try:
        if is_table_empty_or_missing(inspector, table_name):
            print(f"Creating or populating table '{table_name}' with synthetic data...")
            df_data = create_data_function()
            df_data.index = df_data.index + 1  # Start 'id' from 1
            df_data.to_sql(
                name=table_name,
                con=engine,
                if_exists='append',
                index=True,
                index_label='id'
            )
            assign_table_primary_key(table_name, 'id')
            # Enforce UNIQUE constraints
            if table_name == "location_development":
                convert_type_text_to_varchar(table_name, 'location_name')  # TEXT cannot be unique due no-length
                assign_unique_key(table_name, 'location_name')
            print(f"Table '{table_name}' populated successfully.\n")
        else:
            print(f"Table '{table_name}' already exists and contains data, no further action needed!")
    except Exception as e:
        print(f"Error processing table '{table_name}':", str(e))


def add_constraints(inspector):
    """
    Adds unique constraints and foreign keys to specific tables in the database.
    This function ensures that necessary constraints (unique keys and foreign keys) are added to the tables,
    particularly for the 'vehicle_development', 'location_development', and 'route_development' tables.

    :param inspector: SQLAlchemy inspector object used to inspect the database.
    """
    unique_constraints = [
        ('vehicle_development', 'vehicle_id'),
        ('location_development', 'location_id'),
        ('route_development', 'route_id')
    ]
    # Apply unique constraints using a loop
    for table_name, column_name in unique_constraints:
        if is_table_empty_or_missing(inspector, table_name):
            assign_unique_key(table_name, column_name)
    # Apply FKs for the table 'route_development'
    if is_table_empty_or_missing(inspector, 'route_development'):
        # Add foreign keys for route_development
        assign_foreign_key('route_development', 'source_location_id', 'location_development', 'location_id')
        assign_foreign_key('route_development', 'destination_location_id', 'location_development', 'location_id')


def save_tables_to_csv(tables_to_store):
    """
    This method generates synthetic data for each table and saves it as a CSV file in the specified output directory.

    :param tables_to_store: A list of tuples where each tuple contains the table name and its data generation function.
    """
    try:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for table_name, create_data_function in tables_to_store:
            csv_file = os.path.join(output_dir, f"{table_name}.csv")
            create_data_function().to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to: {csv_file}")
    except Exception as e:
        print("Error while saving to .CSV:", str(e))


def main():
    """
    Main entry point of the script to create and populate routing-related development tables in the database.

    This function checks if necessary tables exist and contain data. If not, it creates and populates the tables
    ('vehicle_development', 'location_development', 'route_development') with synthetic data and applies constraints.
    """
    print("\n" + "---- create_routing_development_db_tables.py ----")
    try:
        inspector = inspect(engine)
        # List of tables with corresponding data creation functions
        tables_to_create = [
            ('vehicle_development', create_vehicle_data),
            ('location_development', create_location_data),
            ('route_development', create_route_data)
        ]
        # Create/Populate each table using the reusable method
        for table_name, create_data_function in tables_to_create:
            create_table(table_name, create_data_function, inspector, engine)
        # Add unique & FK keys
        add_constraints(inspector)
    except Exception as e:
        print("\n" + "Error:", str(e))
        print("\n" + "Failed to write data to the database, stored to local .CSV file instead.")
        tables_to_store = [
            ('vehicle_development', create_vehicle_data),
            ('location_development', create_location_data),
            ('route_development', create_route_data)
        ]
        save_tables_to_csv(tables_to_store)
