"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from .user_privilege_service_interface import UserPrivilegeServiceInterface
from ..models.login_user import LoginUser
from ..repositories.user_privilege_repository import UserPrivilegeRepositoryInterface
from ..utils.constant_messages import (
    PRIVILEGE_NOT_EXIST_ENUM,
    INVALID_PRIVILEGE_ADMIN_ASSIGNMENT
)
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.enums import UserPrivileges, Role


class UserPrivilegeService(UserPrivilegeServiceInterface):

    def __init__(self, user_privilege_repository: UserPrivilegeRepositoryInterface):
        self.user_privilege_repository = user_privilege_repository

    def assign_privileges_to_user(self, login_user: LoginUser, privilege_names: List[str]) -> None:
        """
        Validate and assign privileges to a user.
        After validation, the creation of UserPrivilege entries is delegated to the repository.

        :param login_user: LoginUser: The user instance to which the privileges will be assigned.
        :param privilege_names: List[str]: A list of privilege names to be validated and assigned.
        :raises CustomLoggerException: If a privilege does not exist in the UserPrivileges enum.
                                       If an 'admin-privilege' is assigned to a non-admin user.
        """
        validated_privileges = self._validate_privileges(login_user, privilege_names)
        self.user_privilege_repository.assign_user_privileges(login_user, validated_privileges)

    def get_privileges_for_user(self, login_user: LoginUser) -> List[str]:
        """
        Retrieve a list of privilege names assigned to the user.

        :param login_user: LoginUser: The user instance from which we want to retrieve the privileges.
        :return: List[str]: List of privilege names currently enabled for this user.
        """
        return self.user_privilege_repository.find_user_privileges_by_user_id(login_user.id)

    def update_privileges_for_user(self, login_user: LoginUser, new_privilege_names: List[str]) -> List[str]:
        """
        Updates a user's privileges based on a new list of privilege names.
        Before calling the repository method, we validate first.

        :param login_user: LoginUser: The user instance whose privileges will be updated.
        :param new_privilege_names: List[str]: The new list of privileges that should be enabled after this update.
        :return: List[str]: The final list of enabled privileges for this user after the update.
        :raises CustomLoggerException: If a privilege does not exist in the UserPrivileges enum.
                                       If 'admin-privilege' is assigned to a non-admin user.
        """
        validated_privileges = self._validate_privileges(login_user, new_privilege_names)
        final_privileges = self.user_privilege_repository.update_user_privileges(login_user, validated_privileges)
        return final_privileges

    @staticmethod
    def _validate_privileges(login_user: LoginUser, privilege_names: List[str]) -> List[str]:
        """
        Internal helper that ensures that:
          1) Each privilege name exists in the UserPrivileges enum.
          2) The 'admin-privilege' is assigned only to users with the 'ADMIN' role.
        If validation fails, a CustomLoggerException is raised.

        :param login_user: LoginUser: The user instance for privilege checks.
        :param privilege_names: List[str]: The list of privilege names to validate.
        :return: List[str]: A list of validated privilege names.
        :raises CustomLoggerException: If any privilege does not exist in the UserPrivileges enum.
                                       If 'admin-privilege' is assigned to a non-admin user.
        """
        validated = []
        for p_name in privilege_names:
            # Validate existence in the UserPrivilege enum
            if p_name not in UserPrivileges.list_privileges():
                raise CustomLoggerException(
                    "user_privilege_service: " +
                    PRIVILEGE_NOT_EXIST_ENUM.format(privilege_name=p_name)
                )
            # Prevent assigning an 'admin-privilege' to a non-admin user
            if (p_name == UserPrivileges.ADMIN_PRIVILEGE.value
                    and login_user.role != Role.ADMIN.value):
                raise CustomLoggerException(INVALID_PRIVILEGE_ADMIN_ASSIGNMENT)

            validated.append(p_name)
        return validated
