"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List, Dict, Optional

import inject
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .user_service_interface import UserServiceInterface
from ..models.login_user import LoginUser
from ..repositories.user_repository_interface import UserRepositoryInterface
from ..utils.constant_messages import INVALID_ROLE, INVALID_CREDENTIALS, USER_EMAIL_NOT_FOUND, USER_ID_NOT_FOUND
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.enums import Role


class UserService(UserServiceInterface):
    """
    Concrete implementation of UserServiceInterface
    """

    @inject.autoparams()
    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Initialize the UserService with a UserRepository instance.

        :param user_repository: Implementation of UserRepositoryInterface.
        """
        self.user_repository = user_repository

    def get_all_users(self) -> List[LoginUser]:
        """
        Retrieve all users with the role 'USER'.

        :return: List[LoginUser]: A list of LoginUser instances with the role 'USER'.
        """
        return self.user_repository.find_all_users()

    def create_user(self, new_user: LoginUser) -> LoginUser:
        """
        Create a new user with the specified details.

        Validates the user's role against the allowed roles defined in the Role enum.
        If the role is invalid, a CustomLoggerException is raised. Once validated,
        the user is added to the database via the repository.

        :param new_user: LoginUser: The user instance containing the details (email, password, role) to be created.
        :return: LoginUser: The newly created user instance.
        :raises CustomLoggerException: If the user's role is not included in the list of valid roles.
        """
        if new_user.role not in Role.list_roles():
            raise CustomLoggerException(INVALID_ROLE.format(role=new_user.role))
        return self.user_repository.add_user(new_user)

    def authenticate_user(self, login_user: LoginUser) -> Dict:
        """
        Authenticate a user with the given email and password.
        Uses Django's authentication system to validate the user's credentials.
        If authentication is successful, updates the user's login timestamp and generates JWT tokens.

        :param login_user: LoginUser: The object containing the user's email and password.
        :return: Dict: A dictionary containing the authenticated user instance and JWT tokens.
        :raises CustomLoggerException: If authentication fails due to invalid credentials.
        :raises ValueError: If the user is not found in the database.
        """
        user = authenticate(email=login_user.email, password=login_user.password)  # From Django auth lib
        if not user or not user.is_active:
            raise CustomLoggerException(INVALID_CREDENTIALS)
        # Update user's login timestamp
        updated_user = self.user_repository.update_login_timestamp_by_email(login_user.email)
        if updated_user is None:
            raise ValueError(USER_EMAIL_NOT_FOUND.format(email=user.email))
        # Generate JWT tokens
        refresh = RefreshToken.for_user(updated_user)
        # Return tokens
        return {
            'user': updated_user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    def change_password(self, user_with_old_password: LoginUser, new_password: str) -> None:
        """
        Change the password for a specific user, verifying the old password first.

        :param user_with_old_password: LoginUser: The user instance containing the email and old password.
        :param new_password: str: The new password to be set.
        :raises ValueError: If the user is not found in the database.
        """
        user_check = authenticate(email=user_with_old_password.email, password=user_with_old_password.password)
        if not user_check:
            raise ValueError("The given username or the old password is incorrect.")
        updated_user = self.user_repository.change_user_password_by_email(user_with_old_password.email,
                                                                          new_password)
        if updated_user is None:
            raise ValueError(USER_EMAIL_NOT_FOUND.format(email=user_with_old_password.email))

    def reset_password(self, user_email: str, new_password: str) -> None:
        """
        Reset the password for a specific user.
        NOTE: It is strongly recommended that this function be protected by a serializer in the ViewSet
        (e.g., ROLE="ΔΙΑΧΕΙΡΙΣΤΗΣ" and ADMIN_REGISTER_CODE required).

        :param user_email: The email of the user whose password needs to be reset.
        :param new_password: str: The new password to be set.
        :raises ValueError: If the user is not found in the database.
        """
        updated_user = self.user_repository.change_user_password_by_email(user_email, new_password)
        if updated_user is None:
            raise ValueError(USER_EMAIL_NOT_FOUND.format(email=user_email))

    def update_user(self, user: LoginUser) -> LoginUser:
        """
        Update an existing user's details.
        If the user is not found, an exception is raised.

        :param user: LoginUser: The user instance containing updated details.
        :return: LoginUser: The updated LoginUser instance.
        :raises ValueError: If the user is not found in the database.
        """
        updated_user = self.user_repository.modify_user(user)
        if updated_user is None:
            raise ValueError(USER_ID_NOT_FOUND.format(id=user.id))
        return updated_user

    def get_user_by_id(self, user_id: int) -> Optional[LoginUser]:
        """
        Retrieves a single user by their id.

        :param user_id: int: The id to filter by.
        :return: Optional[LoginUser]: The LoginUser instance if found.
        :raises ValueError: If the user is not found in the database.
        """
        user = self.user_repository.find_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with id={user_id} not found.")
        return user
