"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import asyncio

import bcrypt
from sqlalchemy import select

from models import LoginUser, UserErpApi
from utils.database_connection import engine, Base, AsyncSessionLocal
from utils.settings import settings


def hash_password(password) -> str:
    """
    Hashes a password using bcrypt.
    This function takes a plain-text password, generates a salt using bcrypt,
    hashes the password with the salt, and returns the hashed password as a string.

    :param password: The plain-text password to be hashed.
    :return: The hashed password as a string.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


async def create_user_erp_api() -> None:
    """
    Inserts a record into the user_erp_api table for user_id=2 if it does not exist.
    Uses bcrypt hashing for token_password (one-way).
    """
    # The ERP API details you want to insert:
    data = {
        "user_id": 2,
        "client_name": "e-commerce",
        "login_token_url": "http://localhost:7000/auth/login-token",
        "sku_order_url": "http://localhost:7000/api/sku_order_development",
        "inventory_params_url": "http://localhost:7000/api/inventory_params_development",
        "distribution_routing_url": "http://localhost:7000/api/distribution_routing_data",
        "sku_order_latest_url": "http://localhost:7000/api/sku_order_latest",
        "inventory_params_latest_url": "http://localhost:7000/api/get_inventory_params_development_latest",
        "token_username": settings.user_token_username,
        "token_password": settings.user_token_password
    }

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if a user_erp_api record already exists for user_id=2
            result = await session.execute(
                select(UserErpApi).where(UserErpApi.user_id == data["user_id"])
            )
            existing_record = result.scalars().first()
            if existing_record:
                print(f"user_erp_api for user_id={data['user_id']} already exists. Skipping insertion.")
                return

            new_erp_api = UserErpApi(
                user_id=data["user_id"],
                client_name=data["client_name"],
                login_token_url=data["login_token_url"],
                sku_order_url=data["sku_order_url"],
                inventory_params_url=data["inventory_params_url"],
                distribution_routing_url=data["distribution_routing_url"],
                sku_order_latest_url=data["sku_order_latest_url"],
                inventory_params_latest_url=data["inventory_params_latest_url"],
                token_username=data["token_username"],
                token_password=data["token_password"]
            )
            session.add(new_erp_api)
            print(f"ERP API details for {data['client_name']} inserted successfully!")


async def create_user() -> None:
    """
    Inserts the user with e.g., ID=2 if it does not already exist in the database.
    This function checks if the user with the specified ID exists in the database.
    If the user does not exist, it creates a new user with e.g. ID=2, sets the user's email, password,
    role, and active status, and then commits the changes to the database.

    :return: None
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if user already exists
            result = await session.execute(select(LoginUser).where(LoginUser.id == settings.user_id))
            existing_user = result.scalars().first()
            if existing_user:
                print("User already exists. Skipping insertion.")
                return
            # Hash password using Django-compatible hasher
            hashed_password = hash_password(settings.user_password)
            # Insert user
            new_user = LoginUser(
                id=2,  # Force ID to 2
                email=settings.user_email,
                password=hashed_password,
                role="ΧΡΗΣΤΗΣ",
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            print(f"User {settings.user_email} added successfully!")


async def create_tables() -> None:
    """
    Creates all tables defined in the metadata.
    This function attempts to create all tables defined in the application's metadata.
    It ensures that tables are only created if they do not already exist in the database
    (checkfirst=True). If an error occurs during table creation, it logs the error.

    :return: None
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            print("The tables creation attempt was successfully completed!")
    except Exception as e:
        print("Error: " + str(e))


async def main() -> None:
    """
    Main entry point for the script.
    This function orchestrates the creation of tables and the admin user by calling
    the `create_tables` and `create_admin_user` functions.

    :return: None
    """
    await create_tables()
    await create_user()
    await create_user_erp_api()


if __name__ == '__main__':
    asyncio.run(main())
