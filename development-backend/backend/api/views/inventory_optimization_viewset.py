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

from .shared import force_user_id_as_criteria
from ..models.serializers.models_serializers import InventoryOptimizationSerializer
from ..models.serializers.page_criteria_serializers import PageParams, InventoryOptimizationCriteria
from ..services.inventory_optimization_service_interface import InventoryOptimizationServiceInterface
from ..utils.constant_messages import INVENTORY_OPTIMIZATION_FETCH_FAILED_EN, INVENTORY_OPTIMIZATION_FETCH_FAILED_GR
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission
from ..utils.enums import Role, UserPrivileges

logging.basicConfig()
logger = logging.getLogger(__name__)


class InventoryOptimizationViewSet(viewsets.ViewSet):
    # Define permission requirement
    optimization_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[UserPrivileges.RECOMMENDED_STOCK_QUANTITY.value]
    )

    @inject.autoparams()
    def __init__(self, inventory_optimization_service: InventoryOptimizationServiceInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inventory_optimization_service = inventory_optimization_service

    @action(detail=False, methods=['get'], permission_classes=[optimization_permissions])
    def get_all_inventory_optimizations(self, request) -> Response:
        """
        Handles a GET request to retrieve all inventory optimization records with pagination and filtering.
        Enforces 'user_id' as a mandatory criterion to restrict retrieval of data belonging to all users.

        :param request: Request: The HTTP request object containing query parameters for filtering and pagination.
        :return: Response: The HTTP response containing a paginated list of inventory optimization records.
        :raises ValidationError: If the query parameters fail validation.
        :raises CustomLoggerException: If a domain-specific exception occurs.
        :raises Exception: If an unexpected error occurs.
        """
        try:
            query_params = force_user_id_as_criteria(request)
            page_serializer = PageParams(data=query_params)
            criteria_serializer = InventoryOptimizationCriteria(data=query_params)
            page_serializer.is_valid(raise_exception=True)
            criteria_serializer.is_valid(raise_exception=True)
            optimizations = self.inventory_optimization_service.get_all_optimizations(
                page_params=page_serializer, criteria=criteria_serializer
            )
            serialized_optimizations = InventoryOptimizationSerializer(optimizations, many=True)
            return Response(serialized_optimizations.data, status=status.HTTP_200_OK)
        except (CustomLoggerException, ValidationError) as e:
            logger.error(INVENTORY_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": INVENTORY_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": INVENTORY_OPTIMIZATION_FETCH_FAILED_GR},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
