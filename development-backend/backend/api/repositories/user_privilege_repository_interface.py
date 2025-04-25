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


class UserPrivilegeRepositoryInterface(ABC):
    @abstractmethod
    def assign_user_privileges(self, login_user: LoginUser, privilege_names: List[str]) -> None:
        pass

    @abstractmethod
    def find_user_privileges_by_user_id(self, login_user_id: int) -> List[str]:
        pass

    @abstractmethod
    def update_user_privileges(self, login_user: LoginUser, new_privilege_names: List[str]) -> List[str]:
        pass
