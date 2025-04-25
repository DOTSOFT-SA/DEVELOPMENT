"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils import timezone

from .user_repository_interface import UserRepositoryInterface
from ..models.login_user import LoginUser
from ..utils.enums import Role


class UserRepository(UserRepositoryInterface):
    """
    Concrete implementation of UserRepositoryInterface.
    """

    @staticmethod
    def find_all_users() -> List[LoginUser]:
        """
        Retrieve all users with the role 'USER' from the database.

        :return: List[LoginUser]: A list of LoginUser instances with the role 'USER'.
        """
        return LoginUser.objects.filter(role=Role.USER.value)

    def find_user_by_id(user_id: int) -> LoginUser | None:
        """
        Retrieve a user from the database by their id.
        If no user is found, it returns None.

        :param user_id: int: The id of the user to be retrieved.
        :return: LoginUser | None: The LoginUser instance if found, otherwise None.
        """
        try:
            return LoginUser.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None

    def add_user(login_user: LoginUser) -> LoginUser:
        """
        Create and save a new user record in the database.
        This method takes a LoginUser instance containing user details (email, password, and role)
        and creates a corresponding record in the database using Django's custom user manager (see login_user.py).

        :param login_user: LoginUser: The user instance containing email, password, and role details.
        :return: LoginUser: The newly created LoginUser instance with a database-generated ID.
        :raises ValueError: If an integrity error occurs (e.g., duplicate email).
        """
        try:
            return LoginUser.objects.create_user(
                email=login_user.email,
                password=login_user.password,
                role=login_user.role
            )
        except IntegrityError as e:
            raise ValueError(str(e))

    def change_user_password_by_email(user_email: str, new_password: str) -> LoginUser | None:
        """
        Update a user's password by email.
        Fetches the user associated with the given email, changes his password using Django's built-in
        password hashing, and saves the changes.

        :param user_email: str: The email of the user whose password will be updated.
        :param new_password: str: The new password to be set.
        :return: LoginUser | None: The updated LoginUser instance if the user exists, otherwise None.
        """
        try:
            user = LoginUser.objects.get(email=user_email)
            user.set_password(new_password)  # Use Django's set_password to hash the password
            user.updated_at = timezone.now()  # update since the user's info have changed
            user.save()
            return user
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def is_user_active(user_email: str) -> bool | None:
        """
        It was set as a '@staticmethod' due to its usage within the 'decorators.py' file.
        Check if a user is active based on the 'is_active' field.

        :param user_email: str: The email of the user.
        :return: bool | None: True if the user is active, False if inactive, or None if the user does not exist.
        """
        try:
            user = LoginUser.objects.get(email=user_email)
            return user.is_active
        except ObjectDoesNotExist:
            return None

    def modify_user(login_user: LoginUser) -> LoginUser | None:
        """
        Update an existing user's details.
        Fetches the user by ID and updates all provided fields except what is in the 'excluded_fields' list.
        Iterates through the provided LoginUser instance's attributes, and updates the corresponding fields
        in the database. Only non-None attributes are modified.

        :param login_user: LoginUser: The user instance containing the ID and fields to update.
        :return: LoginUser | None: The updated LoginUser instance if found, otherwise None.
        :raises ObjectDoesNotExist: If no user with the provided ID exists.
        """
        try:
            excluded_fields = ['password', 'created_at', 'updated_at', 'login_at']
            user = LoginUser.objects.get(id=login_user.id)
            for key, value in login_user.__dict__.items():
                if key in excluded_fields or value is None:
                    continue
                setattr(user, key, value)
            user.updated_at = timezone.now()  # update since the user's info have changed
            user.save()
            return user
        except ObjectDoesNotExist:
            return None

    def update_login_timestamp_by_email(user_email: str) -> LoginUser | None:
        """
        Update the login timestamp of the user.
        Sets the 'login_at' field to the current time when a user logs in.

        :param user_email: str: The email of the user whose login timestamp will be updated.
        :return: LoginUser | None: The updated LoginUser instance if found, otherwise None.
        """
        try:
            user = LoginUser.objects.get(email=user_email)
            user.login_at = timezone.now()
            user.save(update_fields=['login_at'])  # Update only 'login_at' column
            return user
        except ObjectDoesNotExist:
            return None
