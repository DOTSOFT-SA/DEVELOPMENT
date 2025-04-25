"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import List

from api.repositories.user_privilege_repository import UserPrivilegeRepository
from api.repositories.user_repository import UserRepository
from api.utils.constant_messages import USER_EMAIL_NOT_FOUND
from api.utils.constant_messages import USER_INACTIVE
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


def create_role_privilege_permission(required_role: str = None, required_privileges: List[str] = None):
    """
    Creates a dynamic permission class for role and privilege-based access control.
    This function generates a custom permission class that validates whether a user has a specified role and/or
    a set of privileges. The generated class can be used as a permission decorator in 'views' folder.

    :param required_role: str (Optional): The role that the user must have to gain access.
                          If not specified, only privilege checks are performed.
    :param required_privileges: List[str] (Optional): A list of privilege names that the user must possess.
                              If not specified, only role checks are performed.
    :return: BasePermission: A subclass of `BasePermission` that implements the specified role and privilege checks.
    """
    required_privileges = required_privileges or []

    class DynamicRolePrivilegePermission(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            if not user or not user.is_authenticated:
                return False
            # Check the required role if specified
            if required_role and user.role != required_role:
                return False
            # Check the required privileges if specified
            user_privileges = UserPrivilegeRepository.find_user_privileges_by_user_id(user.id)
            if required_privileges:
                # Ensure the user has all the required privileges
                if not all(p in user_privileges for p in required_privileges):
                    return False

            return True

    return DynamicRolePrivilegePermission


class AllowAnyIsActiveUser(BasePermission):
    """
    Permission class to allow access only to active users.
    Applied globally in backend.settings.py.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user has permission to access the requested resource.
        Allows authenticated active users or users attempting to log in if they are active.

        :param request: Request: The HTTP request object.
        :param view: View: The view being accessed.
        :return: bool: True if the user has permission, otherwise False.
        """

        # Handle the case where the user is authenticated (AllowAny)
        if request.user and request.user.is_authenticated:
            return UserRepository().is_user_active(request.user.email)
        # Handle the case for unauthenticated requests (e.g., login)
        if request.method == "POST" and view.action == "login":
            email = request.data.get("email")  # Extract email from the login request payload
            if email and UserRepository.is_user_active(email) is True:
                return True
            elif email and UserRepository.is_user_active(email) is False:
                logger.error(USER_INACTIVE.format(email=email))
                return False
            else:
                logger.error(USER_EMAIL_NOT_FOUND.format(email=email))
                return False

        # Deny access for any other cases
        return False
