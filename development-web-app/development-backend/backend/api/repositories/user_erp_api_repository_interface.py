"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.user_erp_api import UserErpApi


class UserErpApiRepositoryInterface(ABC):

    @abstractmethod
    def find_user_erp_api_by_user_id(self, user_id: int) -> Optional[UserErpApi]:
        pass

    @abstractmethod
    def store_or_update_user_erp_api_record(self, user_erp_api_record: UserErpApi) -> Optional[UserErpApi]:
        pass
