"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import asyncio

import requests
from sqlalchemy import text

from app.utils.database_connection import AsyncSessionLocal, Base
from app.utils.settings import settings, api_clients_configs, api_users_erp_api_configs


def login_admin():
    """
    Logs in as an admin user and retrieves an access token.

    :return: Access token string.
    """
    api_url = f"{settings.api_host}{settings.api_port}{settings.api_login_admin_url}"

    admin_credentials = {
        "email": settings.admin_email,
        "password": settings.admin_password,
    }

    try:
        response = requests.post(api_url, json=admin_credentials, timeout=10)
        response.raise_for_status()  # Raise error if the request fails
        data = response.json()

        if "access" in data:
            # print("✅ Admin login successful!")
            return data["access"]
        else:
            raise Exception("❌ Failed to retrieve access token from admin login.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Admin login request failed: {str(e)}")


def register_admin(admin_data):
    """
    Registers an admin user.

    :param admin_data: Dictionary containing admin details.
    :return: API response JSON or None if failed.
    """
    api_url = f"{settings.api_host}{settings.api_port}{settings.api_register_admin_url}"
    try:
        response = requests.post(api_url, json=admin_data, timeout=10)
        response.raise_for_status()
        print(f"✅ Admin '{admin_data['email']}' registered successfully!")
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Failed to register admin '{admin_data['email']}': {str(e)}")


def register_user(user_data):
    """
    Registers a normal user after logging in as an admin to get a valid access token.

    :param user_data: Dictionary containing user details.
    :return: API response JSON or None if failed.
    """
    api_url = f"{settings.api_host}{settings.api_port}{settings.api_register_user_url}"
    # Get the admin access token
    token = login_admin()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(api_url, json=user_data, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ User '{user_data['email']}' registered successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Failed to register user '{user_data['email']}': {str(e)}")


def register_user_erp_api(erp_api_data):
    """
    Registers ERP API credentials for a user via the ERP API endpoint.

    :param erp_api_data: Dictionary containing ERP API configuration details.
    :return: API response JSON or None if failed.
    """
    api_url = f"{settings.api_host}{settings.api_port}{settings.api_register_erp_api_url}"
    # Get the admin access token
    token = login_admin()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(api_url, json=erp_api_data, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ ERP API credentials for user_id {erp_api_data.get('user_id')} registered successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Failed to register ERP API credentials for user_id {erp_api_data.get('user_id')}: {str(e)}")


def register():
    """
    1. Loads users from settings and registers them via API calls.
    2. Calls register_admin() if role is 'ΔΙΑΧΕΙΡΙΣΤΗΣ', else calls register_user().
    3. Registers ERP API info of each user.
    """
    users = api_clients_configs  # Loaded from users.json
    for user in users:
        if user["role"] == "ΔΙΑΧΕΙΡΙΣΤΗΣ":
            if "code" not in user:
                raise Exception(f"❌ Error with admin registration '{user['email']}' - missing activation code.")
            register_admin(user)
        else:
            register_user(user)
    erp_apis = api_users_erp_api_configs
    for erp_api in erp_apis:
        register_user_erp_api(erp_api)


async def check_login_user_table_if_empty(conn):
    """
    Checks if the `login_user` has at least one record.

    :param conn: SQLAlchemy database connection.
    :return: True if the table has data, False otherwise.
    """
    result = await conn.execute(text("SELECT EXISTS(SELECT 1 FROM login_user)"))
    return result.scalar()


async def main():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                conn = await session.connection()
                # Check if `login_user` table exists and is not empty
                login_user_exists_and_not_empty = await check_login_user_table_if_empty(conn)
                if login_user_exists_and_not_empty:
                    print("⚠️ Skipping user registration because `login_user` table is NOT empty.")
                    return  # Exit without registering users
                # Proceed with user registration only if the table exists and has data
                register()
            except Exception as e:
                error_message = str(e).lower()
                # Check if the error is a connection issue by inspecting the error message
                # TODO: a temporary workaround, there are might be better solutions
                if "connection" in error_message or "unauthorized" in error_message:
                    print(f"❌ Connection issue detected, tables were NOT deleted.")
                    raise e
                else:
                    await conn.run_sync(Base.metadata.drop_all)
                    await session.commit()
                    print("❌ An error occurred, the tables were deleted!")
                    raise e


# if __name__ == '__main__':
#     asyncio.run(main())
