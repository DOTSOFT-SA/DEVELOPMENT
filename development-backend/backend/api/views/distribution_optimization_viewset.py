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
from ..models.serializers.models_serializers import DistributionOptimizationSerializer
from ..models.serializers.page_criteria_serializers import PageParams, DistributionOptimizationCriteria
from ..services.distribution_optimization_service_interface import DistributionOptimizationServiceInterface
from ..utils.constant_messages import DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_EN, \
    DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission
from ..utils.enums import Role, UserPrivileges

logging.basicConfig()
logger = logging.getLogger(__name__)


class DistributionOptimizationViewSet(viewsets.ViewSet):
    """
    ViewSet to handle retrieving and storing Distribution Optimization records.
    """

    # Define permission requirement
    routing_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[UserPrivileges.ROUTING.value]
    )

    @inject.autoparams()
    def __init__(self, distribution_optimization_service: DistributionOptimizationServiceInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distribution_optimization_service = distribution_optimization_service

    @action(detail=False, methods=['get'], permission_classes=[routing_permissions])
    def get_all_distribution_optimizations(self, request) -> Response:
        """
        Retrieves a paginated list of Distribution Optimization records.

        Steps:
          1) Ensures 'user_id' is enforced in query parameters to restrict unauthorized data access.
          2) Applies pagination and filtering using `PageParams` and `DistributionOptimizationCriteria`.
          3) Fetches the filtered records via `get_all_distribution_optimizations(...)`.
          4) Serializes the retrieved records into `DistributionOptimizationSerializer`.
          5) Returns the serialized data in the response.

        :param request: The HTTP request containing optional query parameters for filtering and pagination.
        :return: Response: A paginated list of Distribution Optimization records.
        """
        try:
            # Force 'user_id' to be int criteria (avoid see data of all users at once)
            query_params = force_user_id_as_criteria(request)
            # Apply pagination and filtering
            page_serializer = PageParams(data=query_params)
            criteria_serializer = DistributionOptimizationCriteria(data=query_params)
            page_serializer.is_valid(raise_exception=True)
            criteria_serializer.is_valid(raise_exception=True)
            # Fetch records
            distribution_optimizations = self.distribution_optimization_service.get_all_distribution_optimizations(
                page_params=page_serializer, criteria=criteria_serializer
            )
            # Serialize response
            serialized_data = DistributionOptimizationSerializer(distribution_optimizations, many=True)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            logger.error(DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
