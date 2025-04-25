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
from rest_framework.response import Response

from ..models.serializers.user_serializer import UserErpApiSerializer
from ..models.user_erp_api import UserErpApi
from ..services.facades.user_privilege_service_facade_interface import UserPrivilegeServiceFacadeInterface
from ..services.user_erp_api_service_interface import UserErpApiServiceInterface
from ..utils.constant_messages import (
    USER_ERP_API_RETRIEVE_FAILED_EN, USER_ERP_API_RETRIEVE_FAILED_GR,
    USER_ERP_API_UPDATE_FAILED_EN, USER_ERP_API_UPDATE_FAILED_GR,
    USER_ERP_API_UPDATE_SUCCESS_GR
)
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission
from ..utils.enums import Role, UserPrivileges

logger = logging.getLogger(__name__)


class UserErpApiViewSet(viewsets.ViewSet):
    """
    ViewSet to manage ERP API configurations for users.
    """

    # Admin-only permission
    admin_permissions = create_role_privilege_permission(
        required_role=Role.ADMIN.value,
        required_privileges=[UserPrivileges.ADMIN_PRIVILEGE.value]
    )

    @inject.autoparams()
    def __init__(self, user_erp_api_service: UserErpApiServiceInterface,
                 user_service_facade: UserPrivilegeServiceFacadeInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_erp_api_service = user_erp_api_service
        self.user_service_facade = user_service_facade

    @action(detail=False, methods=['get'], permission_classes=[admin_permissions])
    def get_user_erp_api(self, request) -> Response:
        """
        Handle GET request to retrieve a user's ERP API configuration.

        :param request: Request: The HTTP request containing the user ID as a query parameter.
        :return: Response: JSON response containing the user's ERP API configuration.
        """
        try:
            user_id = request.query_params.get("user_id")
            if not user_id:
                raise ValidationError("Parameter 'user_id' is required.")
            user_erp_api = self.user_erp_api_service.get_user_erp_api(int(user_id))
            serializer = UserErpApiSerializer(user_erp_api)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            logger.error(USER_ERP_API_RETRIEVE_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_ERP_API_RETRIEVE_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(USER_ERP_API_RETRIEVE_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": USER_ERP_API_RETRIEVE_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_ERP_API_RETRIEVE_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[admin_permissions])
    def create_or_update_user_erp_api(self, request) -> Response:
        """
        Handle POST request to create or update a user's ERP API configuration.

        :param request: Request: The HTTP request containing the ERP API details in the request body.
        :return: Response: Success or failure message.
        """
        serializer = UserErpApiSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_erp_api_record = UserErpApi(**serializer.validated_data)
            updated_record = self.user_service_facade.create_or_update_user_erp_api(user_erp_api_record)
            return Response({
                "message": USER_ERP_API_UPDATE_SUCCESS_GR,
                # "updated_record": UserErpApiSerializer(updated_record).data
            }, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            logger.error(USER_ERP_API_UPDATE_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": USER_ERP_API_UPDATE_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(USER_ERP_API_UPDATE_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": USER_ERP_API_UPDATE_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": USER_ERP_API_UPDATE_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
