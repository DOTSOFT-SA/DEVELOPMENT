"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..models.login_user import LoginUser


class UserServiceInterface(ABC):
    """
    Interface for the LoginUser Service
    """

    @abstractmethod
    def get_all_users(self) -> List[LoginUser]:
        pass

    @abstractmethod
    def create_user(self, user: LoginUser) -> LoginUser:
        pass

    @abstractmethod
    def authenticate_user(self, login_user: LoginUser) -> Dict:
        pass

    @abstractmethod
    def change_password(self, user_with_old_password: LoginUser, new_password: str) -> None:
        pass

    @abstractmethod
    def reset_password(self, user_email: str, new_password: str) -> None:
        pass

    @abstractmethod
    def update_user(self, user: LoginUser) -> LoginUser:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[LoginUser]:
        pass
