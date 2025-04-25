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


class UserPrivilegeServiceInterface(ABC):
    @abstractmethod
    def assign_privileges_to_user(self, login_user: LoginUser, privilege_names: List[str]) -> None:
        pass

    @abstractmethod
    def get_privileges_for_user(self, login_user: LoginUser) -> List[str]:
        pass

    @abstractmethod
    def update_privileges_for_user(self, login_user: LoginUser, new_privilege_names: List[str]) -> List[str]:
        pass
