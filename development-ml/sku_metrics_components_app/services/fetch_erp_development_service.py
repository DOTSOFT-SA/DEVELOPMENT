"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""
import requests

from repositories.user_erp_api_repository import UserErpApiRepository
from repositories.user_repository import UserRepository
from utils.database_connection import AsyncSessionLocal
from utils.django_decryption import decrypt_django_user_password


async def fetch_erp_development_data(full_url: str, auth_url: str, user_id: int) -> dict:
    """
    Fetches and validates ERP data for a specific client.

    Steps:
    1. Use the provided URLs to fetch ERP data from the API.
    2. Extract the user ID and data records from the response.
    3. Validate that the user exists in the database.

    @param full_url: str - The full endpoint URL to fetch ERP data.
    @param auth_url: str - The authentication URL for the ERP API.
    @param user_id: The ID of the user associated with the 'development' data.

    @return: dict - data_records
    """

    # Fetch data from ERP API
    data_records = await _fetch_erp_development_data(full_url, auth_url, user_id)
    # Extract 'user_id' and 'sku_order_data' from erp_data
    if not user_id or not data_records:
        raise ValueError("No (all) data returned from ERP API.")
    # Check if the user exists in the database
    if not await _is_user_exists_and_active(user_id):
        raise Exception(f"User with ID {user_id} does not exist (or inactive) in the database.")
    return data_records


async def _fetch_erp_development_data(full_url: str, auth_url: str, user_id: int) -> dict:
    """
    Fetch data from the ERP API using the access token.

    @param full_url: The client's ERP API URL for getting the data
    @param auth_url: The client's API URL for getting the auth token
    @param user_id: The ID of the user associated with the 'development' data.
    @return: A dictionary containing user_id and data records.
    @raises Exception: If the request fails or the response is empty.
    """
    try:
        # Await the asynchronous token retrieval
        token = await _get_erp_api_token(auth_url, user_id)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        erp_data = response.json()
        # Extract data from json
        data_records = erp_data.get("data", [])
        # Check if the response is empty
        if not user_id or not data_records:
            return {}
        # Return data records
        return data_records
    except requests.HTTPError as http_err:
        raise Exception(f"fetch_erp_development_data(): {http_err}")
    except Exception as exc:
        raise Exception(f"fetch_erp_development_data(): {exc}")


async def _get_erp_api_token(auth_url: str, erp_user_id: int) -> str:
    """
    Fetch an access token from the ERP API authentication endpoint.
    If a 401 Unauthorized error occurs, attempt to decrypt the password and retry.

    @param auth_url: The client's API URL for getting the auth token.
    @param erp_user_id: The ID of the user associated with the ERP API configuration.
    @return: A string representing the Bearer token.
    @raises Exception: If the authentication request fails.
    """

    # Open an async session to fetch the ERP API configuration for the given ERP user
    async with AsyncSessionLocal() as session:
        repo = UserErpApiRepository(session)
        erp_user_api = await repo.find_user_erp_api_by_user_id(erp_user_id)

    if not erp_user_api:
        raise Exception("ERP API configuration not found for the provided ERP user ID.")

    payload = {
        "username": erp_user_api.token_username,
        "password": erp_user_api.token_password
    }

    try:
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()  # raise if response status is not 200
    except requests.HTTPError as http_err:
        # Check if the error is 401 Unauthorized
        if http_err.response.status_code == 401:
            # Attempt to decrypt the password considering as a Django account
            decrypted_password = decrypt_django_user_password()
            if decrypted_password:
                payload["password"] = decrypted_password
                response = requests.post(auth_url, data=payload)
                response.raise_for_status()
            else:
                raise Exception("Failed to decrypt ERP API password to recover from 401 error.")
        else:
            raise http_err

    token = response.json().get("access_token")
    if not token:
        raise Exception("get_erp_api_token(): Failed to retrieve access token from ERP API.")
    return token


async def _is_user_exists_and_active(user_id) -> bool:
    """
    Check if a user exists in the DOTSOFT database.
    This function connects to the database using an asynchronous session and queries the
    UserRepository to verify if a user with the given ID exists.

    @param user_id: The unique identifier of the user to be checked.
    @return: True if the user exists in the database, False otherwise.
    """
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        return await user_repo.is_user_exist_and_active_by_id(user_id)
