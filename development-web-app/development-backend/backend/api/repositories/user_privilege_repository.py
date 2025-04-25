"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from django.db import transaction
from django.utils import timezone

from .user_privilege_repository_interface import UserPrivilegeRepositoryInterface
from ..models.login_user import LoginUser
from ..models.privilege import Privilege
from ..models.user_privilege import UserPrivilege
from ..utils.constant_messages import PRIVILEGE_NOT_EXIST_DB
from ..utils.custom_exceptions import CustomLoggerException


class UserPrivilegeRepository(UserPrivilegeRepositoryInterface):
    """
    Concrete implementation of UserPrivilegeRepositoryInterface.
    """

    @staticmethod
    def assign_user_privileges(login_user: LoginUser, privilege_names: List[str]) -> None:
        """
        Assign privileges to a user by creating UserPrivilege records.
        This method ensures that each provided privilege exists in the database
        and then associating it with the user. If any privilege does not exist,
        a CustomLoggerException is raised.

        :param login_user: LoginUser: The user to whom the privileges will be assigned.
        :param privilege_names: List[str]: A list of privilege names to be assigned.
        :raises CustomLoggerException: If any of the provided privilege names do not exist in the database.
        """
        for priv_name in privilege_names:
            # Find privilege in the DB
            privilege = Privilege.objects.filter(name=priv_name).first()
            if not privilege:
                raise CustomLoggerException(PRIVILEGE_NOT_EXIST_DB.format(privilege_name=priv_name))
            # Add privileges to the many-to-many table
            UserPrivilege.objects.create(
                user=login_user,
                privilege=privilege,
                is_enabled=True
            )

    @staticmethod
    def find_user_privileges_by_user_id(login_user_id: int) -> List[str]:
        """
        Retrieve the privilege names assigned to a specific user.
        Queries the database for all enabled privileges associated with the given user ID.

        :param login_user_id: int: The ID of the user.
        :return: List[str]: A list of privilege names assigned to the user.
        """
        return list(UserPrivilege.objects.filter(user_id=login_user_id, is_enabled=True)
                    .values_list('privilege__name', flat=True))

    @staticmethod
    @transaction.atomic
    def update_user_privileges(login_user: LoginUser, new_privilege_names: List[str]) -> List[str]:
        """
        Updates a user's privileges according to the following rules:
          1) If a privilege in 'new_privilege_names' already exists and is enabled, keep it.
          2) If a privilege in 'new_privilege_names' already exists but is disabled, enable it.
          3) If a privilege in 'new_privilege_names' does not exist, create it (enabled).
          4) If a privilege exists in DB but not in 'new_privilege_names', disable it (set is_enabled=False).

        :param login_user: LoginUser: The user whose privileges are being updated.
        :param new_privilege_names: List[str]: The list of privilege names that should remain enabled.
        :return: List[str]: The final list of enabled privilege names for the user.
        :raises CustomLoggerException: If any of the provided privilege names do not exist in the database.
        """
        # 1. Fetch all existing UserPrivilege records for this user
        existing_records = UserPrivilege.objects.filter(user=login_user).select_related('privilege')
        # Create a dictionary for quick lookups: { privilege_name: UserPrivilege obj }
        existing_map = {rec.privilege.name: rec for rec in existing_records}
        # 2. Process each new privilege in 'new_privilege_names'
        for priv_name in new_privilege_names:
            # Ensure the privilege exists in the DB
            privilege_obj = Privilege.objects.filter(name=priv_name).first()
            if not privilege_obj:
                raise CustomLoggerException(PRIVILEGE_NOT_EXIST_DB.format(privilege_name=priv_name))
            if priv_name in existing_map:
                # If privilege record already exists
                user_priv = existing_map[priv_name]
                if not user_priv.is_enabled:
                    # Re-enable it if currently disabled
                    user_priv.is_enabled = True
                    user_priv.updated_at = timezone.now()  # Update timestamp
                    user_priv.save(update_fields=['is_enabled', 'updated_at'])
                # Remove from the map to mark it processed
                del existing_map[priv_name]
            else:
                # Create a new record if it doesn't exist
                UserPrivilege.objects.create(
                    user=login_user,
                    privilege=privilege_obj,
                    is_enabled=True
                )
        # 3. For any leftover privileges in 'existing_map' that weren't in the new list, disable them
        for leftover_priv_name, user_priv in existing_map.items():
            if user_priv.is_enabled:
                user_priv.is_enabled = False
                user_priv.updated_at = timezone.now()  # Update timestamp
                user_priv.save(update_fields=['is_enabled', 'updated_at'])
        # 4. Return the final list of enabled privileges for this user
        final_enabled_privileges = list(
            UserPrivilege.objects.filter(
                user=login_user, is_enabled=True
            ).values_list('privilege__name', flat=True)
        )
        return final_enabled_privileges
