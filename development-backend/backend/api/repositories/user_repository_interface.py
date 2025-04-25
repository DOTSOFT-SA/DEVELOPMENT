"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import List

from ..models.login_user import LoginUser


class UserRepositoryInterface(ABC):
    @abstractmethod
    def find_all_users(self) -> List[LoginUser]:
        pass

    @abstractmethod
    def find_user_by_id(self, user_id: int) -> LoginUser | None:
        pass

    @abstractmethod
    def add_user(self, login_user: LoginUser) -> LoginUser:
        pass

    @abstractmethod
    def change_user_password_by_email(self, user_email: str, new_password: str) -> LoginUser | None:
        pass

    @abstractmethod
    def is_user_active(self, user_email: str) -> bool | None:
        pass

    @abstractmethod
    def modify_user(self, login_user: LoginUser) -> LoginUser | None:
        pass

    @abstractmethod
    def update_login_timestamp_by_email(self, user_email: str) -> LoginUser | None:
        pass
