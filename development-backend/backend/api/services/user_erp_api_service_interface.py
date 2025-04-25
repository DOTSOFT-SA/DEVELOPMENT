"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod

from ..models.user_erp_api import UserErpApi


class UserErpApiServiceInterface(ABC):

    @abstractmethod
    def get_user_erp_api(self, user_id: int) -> UserErpApi:
        pass

    @abstractmethod
    def create_or_update_user_erp_api(self, user_erp_api_record: UserErpApi) -> UserErpApi:
        pass
