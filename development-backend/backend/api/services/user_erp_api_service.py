"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging

from .user_erp_api_service_interface import UserErpApiServiceInterface
from ..models.user_erp_api import UserErpApi
from ..repositories.user_erp_api_repository_interface import UserErpApiRepositoryInterface
from ..utils.custom_exceptions import CustomLoggerException

logger = logging.getLogger(__name__)


class UserErpApiService(UserErpApiServiceInterface):

    def __init__(self, user_erp_api_repository: UserErpApiRepositoryInterface):
        self.user_erp_api_repository = user_erp_api_repository

    def get_user_erp_api(self, user_id: int) -> UserErpApi:
        """
        Retrieve the ERP API record for a specific user by user_id.

        :param user_id: int: The ID of the user whose ERP API record we want.
        :return: UserErpApi: The ERP API configuration record for this user.
        :raises CustomLoggerException: If no record is found.
        """
        record = self.user_erp_api_repository.find_user_erp_api_by_user_id(user_id)
        if record is None:
            raise CustomLoggerException(f"No ERP API record found for user_id={user_id}")
        return record

    def create_or_update_user_erp_api(self, user_erp_api_record: UserErpApi) -> UserErpApi:
        """
        Create a new or update an ERP API record for the user.

        :param user_erp_api_record: UserErpApi: The record containing the user's ERP API links.
        :return: UserErpApi: The newly created or updated record.
        """
        record = self.user_erp_api_repository.store_or_update_user_erp_api_record(user_erp_api_record)
        return record
