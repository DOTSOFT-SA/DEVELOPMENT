"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from .database_connection import engine, engine_super
from .sql_constant_queries import PRIMARY_KEY_QUERY, TABLE_COUNT_QUERY, UNIQUE_KEY_QUERY, FOREIGN_KEY_QUERY, \
    CREATE_USER_QUERY, CHECK_USER_EXISTS_QUERY, GRANT_PRIVILEGES_QUERY, FLUSH_PRIVILEGES_QUERY, \
    MODIFY_TEXT_TO_VARCHAR_QUERY


def is_table_empty_or_missing(inspector, table_name):
    """
    Checks if a database table is empty or missing.

    @param inspector: An SQLAlchemy Inspector object used to check the table's existence.
    @param table_name: The name of the table to check.
    @return:
        - True: If the table exists but is empty, or if the table does not exist.
        - False: If the table exists and contains data.
    """
    with engine.connect() as connection:
        if inspector.has_table(table_name):
            query = text(TABLE_COUNT_QUERY.format(table_name=table_name))
            query_result_flag = connection.execute(query).scalar()  # Check if table is empty
            return query_result_flag == 0  # True if table exists but is empty
        else:
            return True  # True if the table does not exist


def assign_table_primary_key(table_name: str, column_name: str):
    """
    Alters a table to set a specified column as the PRIMARY KEY with AUTO_INCREMENT.

    @param table_name: The name of the table to be altered.
    @param column_name: The name of the column to be set as the PRIMARY KEY.
    @raises Exception: If the operation fails, an exception is raised with an error message.
    """
    try:
        with engine.connect() as connection:
            # Check if the given columns is already a PK
            inspector = inspect(engine)
            pk_columns = inspector.get_pk_constraint(table_name).get('constrained_columns', [])
            if column_name in pk_columns:
                return  # It's already a primary key
            # If not, make it a primary key
            alter_table_query = text(PRIMARY_KEY_QUERY.format(
                table_name=table_name,
                column_name=column_name
            ))
            connection.execute(alter_table_query)
            print(
                f"Table '{table_name}' successfully altered: '{column_name}' is now a PRIMARY KEY with AUTO_INCREMENT."
            )
    except Exception as e:
        print(f"Failed to alter the table '{table_name}': {e}")


def assign_unique_key(table_name: str, column_name: str):
    """
    Adds a unique constraint to a specified column in a table.

    @param table_name: The name of the table to be altered.
    @param column_name: The name of the column to be made unique.
    """
    try:
        with engine.connect() as connection:
            unique_query = text(UNIQUE_KEY_QUERY.format(
                table_name=table_name,
                column_name=column_name
            ))
            connection.execute(unique_query)
            print(f"Unique constraint added: {table_name}.{column_name}")
    except Exception as e:
        print(f"Failed to add unique constraint to '{table_name}.{column_name}': {e}")


def assign_foreign_key(table_name: str, column_name: str, reference_table: str, reference_column: str):
    """
    Adds a foreign key constraint to a specified column in a table.

    @param table_name: The name of the table to be altered.
    @param column_name: The name of the column to add the foreign key constraint.
    @param reference_table: The table being referenced.
    @param reference_column: The column being referenced in the reference table.
    """
    try:
        with engine.connect() as connection:
            # SQL query to add a foreign key constraint
            fk_query = FOREIGN_KEY_QUERY.format(
                table_name=table_name,
                column_name=column_name,
                reference_table=reference_table,
                reference_column=reference_column
            )
            connection.execute(text(fk_query))
            print(f"Foreign key constraint added: {table_name}.{column_name} -> {reference_table}.{reference_column}")
    except Exception as e:
        print(f"Failed to add foreign key constraint to '{table_name}.{column_name}': {e}")


def create_db_user(username, host, password, privileges):
    """
    Ensures a MySQL user exists. If not, creates the user and grants privileges.

    @param username: The MySQL username to check/create.
    @param host: The host for the MySQL user.
    @param password: The password for the MySQL user.
    @param privileges: The privileges to grant to the user.
    """
    try:
        with engine_super.connect() as connection:
            # Check if the user exists
            check_query = CHECK_USER_EXISTS_QUERY.format(username=username, host=host)
            user_exists = connection.execute(text(check_query)).scalar()
            if user_exists:
                print(f"User '{username}'@'{host}' already exists.")
            else:
                print(f"Creating user '{username}'@'{host}'...")
                # Create the user
                create_query = CREATE_USER_QUERY.format(username=username, host=host, password=password)
                connection.execute(text(create_query))
                # Grant privileges
                grant_query = GRANT_PRIVILEGES_QUERY.format(
                    username=username, host=host, privileges=privileges
                )
                connection.execute(text(grant_query))
                # Flush privileges
                connection.execute(text(FLUSH_PRIVILEGES_QUERY))
                print(f"User '{username}'@'{host}' created and privileges granted successfully.")

    except SQLAlchemyError as e:
        print(f"Error ensuring user exists: {e}")


def convert_type_text_to_varchar(table_name: str, column_name: str):
    """
    Converts a TEXT column to VARCHAR(255) in a given table.

    @param table_name: The name of the table to modify.
    @param column_name: The column that should be converted to VARCHAR(255).
    """
    try:
        with engine.connect() as connection:
            alter_query = text(MODIFY_TEXT_TO_VARCHAR_QUERY.format(
                table_name=table_name,
                column_name=column_name
            ))
            connection.execute(alter_query)
            print(f"Converted '{column_name}' to VARCHAR(255) in '{table_name}'.")
    except Exception as e:
        print(f"Failed to convert '{column_name}' to VARCHAR(255) in '{table_name}': {e}")
