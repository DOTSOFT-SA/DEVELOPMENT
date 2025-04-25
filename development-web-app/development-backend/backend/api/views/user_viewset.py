"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging

import inject
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models.dtos.user_dto import RegisterUserDto, UserDto
from ..models.login_user import LoginUser
from ..models.serializers.user_serializer import RegisterSerializer, LoginSerializer, AfterLoginSerializer, \
    ChangePasswordSerializer, RegisterAdminSerializer, UserSerializer, ChangePasswordByAdminSerializer
from ..services.facades.user_privilege_service_facade_interface import UserPrivilegeServiceFacadeInterface
from ..services.user_service_interface import UserServiceInterface
from ..utils.constant_messages import USER_CREATED_SUCCESSFULLY_GR, USER_CREATED_SUCCESSFULLY_EN, \
    USER_CREATED_FAILED_GR, \
    USER_CREATED_FAILED_EN, USER_LOGIN_FAILED_EN, USER_LOGIN_FAILED_GR, USER_CHANGE_PASSWORD_SUCCESS_EN, \
    USER_CHANGE_PASSWORD_SUCCESS_GR, USER_CHANGE_PASSWORD_FAILED_EN, USER_CHANGE_PASSWORD_FAILED_GR, \
    USER_UPDATED_FAILED_EN, USER_UPDATED_SUCCESSFULLY_EN, USER_UPDATED_FAILED_GR, USER_UPDATED_SUCCESSFULLY_GR
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission, AllowAnyIsActiveUser
from ..utils.enums import Role, UserPrivileges

logging.basicConfig()
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet to handle user registration and login.
    """

    # Permission/Authentication classes
    admin_permissions = create_role_privilege_permission(required_role=Role.ADMIN.value,
                                                         required_privileges=[UserPrivileges.ADMIN_PRIVILEGE.value])

    @inject.autoparams()
    def __init__(self, user_service_interface: UserServiceInterface,
                 user_privilege_service_facade_interface: UserPrivilegeServiceFacadeInterface, *args, **kwargs):
        """
        Initialize the UserViewSet with a UserPrivilegeServiceFacade instance.

        @param user_privilege_service_facade: user service instance implementing UserPrivilegeServiceFacadeInterface.
        """
        # super(): Ensures that your class is properly integrated with the 'Django view framework'
        # and any other parent classes it inherits from
        super().__init__(*args, **kwargs)
        self.user_service = user_service_interface
        self.user_privilege_service_facade = user_privilege_service_facade_interface

    @action(detail=False, methods=['get'], permission_classes=[admin_permissions])
    def get_all_users(self, request) -> Response:
        """
        Handle GET request to retrieve all users with the role 'USER'.
        Accessible only to admins.

        :param request: Request: The HTTP request object.
        :return: Response: A JSON response containing the list of users with the role 'USER'.
        """
        try:
            # Call the service layer to retrieve all users with the role 'USER'
            users = self.user_privilege_service_facade.get_all_users_with_privileges()
            # Serialize the data to JSON
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}", exc_info=True)
            return Response({"error": "Failed to retrieve users."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register_admin(self, request) -> Response:
        """
        Handle POST request to register a new admin.
        No permissions required, but you will need the 'ADMIN_REGISTER_CODE'.

        :param request: Request: The HTTP request containing user data.
        :return: Response: The HTTP response with the registration status.
        """
        serializer = RegisterAdminSerializer(data=request.data)
        return self._register(serializer)

    @action(detail=False, methods=['post'], permission_classes=[admin_permissions])
    def register(self, request) -> Response:
        """
        Handle POST request to register a new user.

        :param request: Request: The HTTP request containing user data.
        :return: Response: The HTTP response with the registration status.
        """
        serializer = RegisterSerializer(data=request.data)
        return self._register(serializer)

    @action(detail=False, permission_classes=[AllowAnyIsActiveUser], methods=['post'])
    def login(self, request) -> Response:
        """
        Handle POST request to authenticate a user and generate a token.

        :param request: Request: The HTTP request containing login credentials.
        :return: Response: HTTP response with token if authentication is successful, otherwise an error message.
        :raises CustomLoggerException: If authentication fails due to invalid credentials.
        :raises ValidationError: If validation errors occur.
        :raises Exception: For unexpected errors.
        """
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            login_user = LoginUser(**serializer.validated_data)
            result = self.user_privilege_service_facade.user_authentication(login_user)
            return Response({
                "user": AfterLoginSerializer(result['user']).data,
                "access": result['access'],
                "refresh": result['refresh'],
            }, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            error_message = USER_LOGIN_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_LOGIN_FAILED_GR}, status=status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            error_message = USER_LOGIN_FAILED_EN.format(email=request.data.get('email'))
            error_details = serializer.errors if serializer.errors else {"error": str(e)}
            logger.error(error_message)
            logger.error(error_details, exc_info=True)
            return Response({"error": USER_LOGIN_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = USER_LOGIN_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_LOGIN_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def change_password(self, request) -> Response:
        """
        Handle POST request to change the user's password.

        :param request: Request: The HTTP request containing the user's email and new password.
        :return: Response: HTTP response with a success message if the password is changed successfully.
        :raises CustomLoggerException: If the password change process encounters an issue.
        :raises ValidationError: If validation errors occur.
        :raises Exception: For unexpected errors.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            user = LoginUser(email=email, password=old_password)  # Create a user object with the provided email
            self.user_service.change_password(user, new_password)
            logger.info(USER_CHANGE_PASSWORD_SUCCESS_EN.format(email=user.email))
            return Response({"message": USER_CHANGE_PASSWORD_SUCCESS_GR}, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            error_message = USER_CHANGE_PASSWORD_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_CHANGE_PASSWORD_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:  # Handle serializer-specific errors
            error_message = USER_CHANGE_PASSWORD_FAILED_EN.format(email=request.data.get('email'))
            error_details = serializer.errors if serializer.errors else {"error": str(e)}
            logger.error(error_message)
            logger.error(error_details, exc_info=True)
            return Response({"error": USER_CHANGE_PASSWORD_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = USER_CHANGE_PASSWORD_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_CHANGE_PASSWORD_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def change_password_by_admin(self, request) -> Response:
        """
        Handle POST requests to allow the admin to reset a user's password
        (e.g., when the user has forgotten their password).

        :param request: Request: The HTTP request containing the user's email and new password.
        :return: Response: HTTP response with a success message if the password is changed successfully.
        :raises CustomLoggerException: If the password change process encounters an issue.
        :raises ValidationError: If validation errors occur.
        :raises Exception: For unexpected errors.
        """
        serializer = ChangePasswordByAdminSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            self.user_service.reset_password(user_email, new_password)
            logger.info(USER_CHANGE_PASSWORD_SUCCESS_EN.format(email=user_email))
            return Response({"message": USER_CHANGE_PASSWORD_SUCCESS_GR}, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            error_message = USER_CHANGE_PASSWORD_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_CHANGE_PASSWORD_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:  # Handle serializer-specific errors
            error_message = USER_CHANGE_PASSWORD_FAILED_EN.format(email=request.data.get('email'))
            error_details = serializer.errors if serializer.errors else {"error": str(e)}
            logger.error(error_message)
            logger.error(error_details, exc_info=True)
            return Response({"error": USER_CHANGE_PASSWORD_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = USER_CHANGE_PASSWORD_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_CHANGE_PASSWORD_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[admin_permissions])
    def update_user(self, request) -> Response:
        """
        Handle POST request to update a user account. Only accessible to admins.

        :param request: Request: The HTTP request containing the user details.
        :return: Response: A success message if the account is updated successfully, otherwise an error message.
        :raises CustomLoggerException: If the update process encounters an issue.
        :raises ValidationError: If validation errors occur.
        :raises Exception: For unexpected errors.
        """
        serializer = UserSerializer(data=request.data)
        try:
            # Validate input
            serializer.is_valid(raise_exception=True)
            # Map validated data to a DTO
            user_dto_to_update = UserDto(**serializer.validated_data)
            # Call the service layer to deactivate the user
            updated_user_dto = self.user_privilege_service_facade.update_user_and_privileges(user_dto_to_update)
            logger.info(USER_UPDATED_SUCCESSFULLY_EN.format(email=user_dto_to_update.email))
            return Response(
                {
                    "message": USER_UPDATED_SUCCESSFULLY_GR,
                    "updated_user": updated_user_dto.__dict__
                },
                status=status.HTTP_200_OK
            )
        except CustomLoggerException as e:
            error_message = USER_UPDATED_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_UPDATED_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error_message = USER_UPDATED_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(serializer.errors if serializer.errors else {"error": str(e)}, exc_info=True)
            return Response({"error": USER_UPDATED_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = USER_UPDATED_FAILED_EN.format(email=request.data.get('email'))
            logger.error(error_message)
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_UPDATED_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _register(self, serializer) -> Response:
        """
        Handle user registration by validating input data, creating a user DTO,
        and delegating user creation to the service layer. This method encapsulates the shared registration
        logic for different registration endpoints, ensuring consistency in validation and error handling.

        :param serializer: Serializer: The serializer containing the user data for validation and transformation.
        :return: Response: A Response object with a success message and HTTP 201 status on successful registration,
                 or an error message with the appropriate HTTP status code on failure.
        :raises CustomLoggerException: If the registration process encounters an issue.
        :raises ValidationError: If validation errors occur.
        :raises Exception: For unexpected errors.
        """
        try:
            # Validate input data
            serializer.is_valid(raise_exception=True)
            # Map validated data to a DTO
            registered_user = RegisterUserDto(**serializer.validated_data)
            # Register the user using the facade service
            self.user_privilege_service_facade.register_user(registered_user)
            # Return a success response
            logger.info(USER_CREATED_SUCCESSFULLY_EN.format(email=registered_user.email))
            return Response({"message": USER_CREATED_SUCCESSFULLY_GR}, status=status.HTTP_201_CREATED)
        except CustomLoggerException as e:
            # Handle custom exceptions with specific messages
            error_message = USER_CREATED_FAILED_EN.format(email=self.request.data.get('email'))
            logger.error(error_message)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_CREATED_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error_message = USER_CREATED_FAILED_EN.format(email=self.request.data.get('email'))
            error_details = serializer.errors if serializer.errors else {"error": str(e)}
            logger.error(error_message)
            logger.error(error_details, exc_info=True)
            return Response({"error": USER_CREATED_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = USER_CREATED_FAILED_EN.format(email=self.request.data.get('email'))
            logger.error(error_message)
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_CREATED_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
