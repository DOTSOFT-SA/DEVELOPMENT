"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import Optional

import requests

from .erp_development_repository_interface import ErpDevelopmentRepositoryInterface
from .user_erp_api_repository import UserErpApiRepository

logger = logging.getLogger(__name__)


class ErpDevelopmentRepository(ErpDevelopmentRepositoryInterface):
    """
    Repository responsible for fetching data from the external ERP system.
    """

    @staticmethod
    def fetch_erp_api_token(user_id: int) -> Optional[str]:
        """
        Fetch an access token from the ERP API's 'login_token_url' for the specified user.
        If any error occurs, return None (no logging or raising here).

        :param user_id: The ID of the user whose token we want to retrieve.
        :return: The token string if successful, or None otherwise.
        """
        user_erp_api = UserErpApiRepository.find_user_erp_api_by_user_id(user_id)
        if not user_erp_api:
            return None  # No record in DB
        # Build the auth request using the stored credentials
        auth_url = user_erp_api.login_token_url
        payload = {
            "username": user_erp_api.token_username,
            "password": user_erp_api.token_password
        }
        try:
            resp = requests.post(auth_url, data=payload, timeout=10)
            resp.raise_for_status()
            token = resp.json().get("access_token")
            return token
        except requests.RequestException as e:
            logger.error(str(e))
            return None

    @staticmethod
    def fetch_data_from_erp(url: str, token: str, method: str = "GET", payload=None) -> Optional[dict]:
        """
        Generic helper to call an ERP endpoint with a Bearer token.
        Return JSON data or None on error.

        :param url: The full ERP API endpoint URL.
        :param token: The Bearer token to authenticate.
        :param method: "GET" or "POST".
        :param payload: JSON payload for POST requests.
        :return: The parsed JSON data dict.
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            if method == "POST":
                resp = requests.post(url, headers=headers, json=payload, timeout=10)
            else:
                resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json() or {}
        except requests.RequestException as e:
            logger.error(str(e))
            return None
