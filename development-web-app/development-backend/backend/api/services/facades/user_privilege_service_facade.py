"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import Dict, List

from django.db import transaction

from .user_privilege_service_facade_interface import UserPrivilegeServiceFacadeInterface
from ..user_erp_api_service_interface import UserErpApiServiceInterface
from ..user_privilege_service_interface import UserPrivilegeServiceInterface
from ..user_service_interface import UserServiceInterface
from ...models.dtos.user_dto import RegisterUserDto, UserDto
from ...models.login_user import LoginUser
from ...models.user_erp_api import UserErpApi
from ...utils.dto_converters import (
    register_user_dto_to_login_user,
    login_user_to_user_dto,
    user_dto_to_login_user
)


class UserPrivilegeServiceFacade(UserPrivilegeServiceFacadeInterface):

    def __init__(self,
                 user_service: UserServiceInterface,
                 user_privilege_service: UserPrivilegeServiceInterface,
                 user_erp_api_service: UserErpApiServiceInterface):
        self.user_service = user_service
        self.user_privilege_service = user_privilege_service
        self.user_erp_api_service = user_erp_api_service

    def register_user(self, user_dto: RegisterUserDto) -> None:
        """
        Register a new user and assign privileges in a single transaction.
        This method ensures that a user is created first, and then privileges are assigned.
        If privilege assignment fails, the entire transaction is rolled back.

        :param user_dto: RegisterUserDto: The Data Transfer Object containing user details (e.g., email, password, role)
                         and privileges.
        """
        with transaction.atomic():  # prevent e.g., user creation if assigning privileges fails
            stored_user = self._store_user(user_dto)
            self.user_privilege_service.assign_privileges_to_user(stored_user, user_dto.privilege_names)

    def user_authentication(self, login_user: LoginUser) -> Dict:
        """
        Authenticate a user and retrieve their privileges.
        Calls the user service to authenticate the user, then fetches the user's assigned privileges.

        :param login_user: LoginUser: The user instance containing email and password.
        :return: Dict: A dictionary containing authenticated user data with privileges and JWT tokens.
        """
        result = self.user_service.authenticate_user(login_user)
        privilege_names = self.user_privilege_service.get_privileges_for_user(result['user'])
        result['user'].privilege_names = privilege_names  # Inject privileges
        return result

    def get_all_users_with_privileges(self) -> List[UserDto]:
        """
        Retrieve all users along with their assigned privileges.
        Fetches all users with the role 'USER' and enriches their data with their respective privileges.

        :return: List[UserDto]: A list of UserDto instances with populated privilege names.
        """
        users = self.user_service.get_all_users()  # Retrieve all users with the role 'USER'
        user_dtos = []
        for user in users:
            privilege_names = self.user_privilege_service.get_privileges_for_user(user)
            user_dto = login_user_to_user_dto(user)
            user_dto.privilege_names = privilege_names  # Attach privilege names
            user_dtos.append(user_dto)
        return user_dtos

    @transaction.atomic
    def update_user_and_privileges(self, user_dto: UserDto) -> UserDto:
        """
        Update user details and assigned privileges in a single transaction.
        First updates user details, then modifies assigned privileges, ensuring
        a consistent state across both operations.

        :param user_dto: UserDto: The DTO containing updated user information (email, role, etc.).
        :return: UserDto: The updated UserDto instance with the final list of privileges.
        """
        # 1) Convert from DTO and Update user fields
        user = user_dto_to_login_user(user_dto)
        updated_user = self.user_service.update_user(user)
        # 2) Update user privileges
        final_user_privileges_names = self.user_privilege_service.update_privileges_for_user(updated_user,
                                                                                             user_dto.privilege_names)
        # 3) Create DTO for return
        final_user_dto = login_user_to_user_dto(updated_user)
        final_user_dto.privilege_names = final_user_privileges_names

        return final_user_dto

    @transaction.atomic
    def create_or_update_user_erp_api(self, user_erp_api_record: UserErpApi) -> UserErpApi:
        """
        Create or update an ERP API record associated with a user.

        This method ensures that a user exists before assigning or updating their ERP API
        records. If the user does not exist, an exception will be raised. Otherwise, the
        method proceeds to create or update the user's ERP API information.

        :param user_erp_api_record: UserErpApi: Contains the user's unique id and their associated ERP API details.
        :return: UserErpApi: The newly created or updated ERP API record.
        :raises DoesNotExist: If the user referenced does not exist.
        """
        # Validate that the user exists before proceeding
        self.user_service.get_user_by_id(user_erp_api_record.user_id)
        # Return the created or updated ERP API record for the user
        return self.user_erp_api_service.create_or_update_user_erp_api(user_erp_api_record)

    def _store_user(self, user_dto: RegisterUserDto) -> LoginUser:
        """
        Convert user data from RegisterUserDto into a LoginUser instance and persist it.

        :param user_dto: RegisterUserDto: The data transfer object containing user details (email, password, role).
        :return: LoginUser: The newly created and persisted LoginUser instance.
        """
        login_user = register_user_dto_to_login_user(user_dto)
        return self.user_service.create_user(login_user)
