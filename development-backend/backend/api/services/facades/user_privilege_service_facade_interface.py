"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from ...models import LoginUser
from ...models.dtos.user_dto import RegisterUserDto, UserDto
from ...models.user_erp_api import UserErpApi


class UserPrivilegeServiceFacadeInterface(ABC):
    @abstractmethod
    def register_user(self, user_dto: RegisterUserDto) -> None:
        pass

    @abstractmethod
    def user_authentication(self, login_user: LoginUser) -> Dict:
        pass

    @abstractmethod
    def get_all_users_with_privileges(self) -> List[UserDto]:
        pass

    @abstractmethod
    def update_user_and_privileges(self, user_dto: UserDto) -> UserDto:
        pass

    @abstractmethod
    def create_or_update_user_erp_api(self, user_erp_api_record: UserErpApi) -> UserErpApi:
        pass
