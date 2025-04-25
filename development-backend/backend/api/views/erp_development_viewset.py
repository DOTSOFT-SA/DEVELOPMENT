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

from ..models.serializers.models_serializers import SkuInputSerializer
from ..models.serializers.predictions_serializers import MergedSkuMetricSerializer
from ..services.facades.erp_development_service_facade import ErpDevelopmentServiceFacade
from ..utils.constant_messages import MERGED_ERP_SKU_METRIC_FETCH_FAILED_EN, GENERAL_FETCH_FAILED_GR
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission
from ..utils.enums import Role, UserPrivileges

logging.basicConfig()
logger = logging.getLogger(__name__)


class ErpDevelopmentViewSet(viewsets.ViewSet):
    """
    ViewSet to retrieve merged SKU metric data from local SkuMetric records
    combined with the latest ERP record, using a POST request with JSON body.
    """

    # Define permission requirement
    sku_metric_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[UserPrivileges.DEMAND_FORECASTING.value]
    )

    @inject.autoparams()
    def __init__(self, erp_development_service: ErpDevelopmentServiceFacade, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.erp_development_service = erp_development_service

    @action(detail=False, methods=['post'], permission_classes=[sku_metric_permissions])
    def get_merged_sku_metric_info(self, request) -> Response:
        """
        Handles a POST request to retrieve merged SKU metric data.
          1. Validates the request payload to ensure SKU number and user ID are provided.
          2. Calls the `erp_development_service` to retrieve the merged SKU metric data.
          3. If data retrieval is successful, serializes the DTO and returns a JSON response.
          4. If data retrieval fails, an appropriate error response is returned.
    
        :param request: The HTTP request containing SKU number and user ID.
        :return: Response: A JSON response containing the merged SKU metric data or an error message.
        :raises ValidationError: If the request payload is invalid.
        :raises CustomLoggerException: If a domain-specific issue occurs during data retrieval.
        :raises Exception: For unexpected failures during execution.
        """
        try:
            # Validate request data
            serializer = SkuInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            sku_number = serializer.validated_data['sku_number']
            user_id = serializer.validated_data['user_id']
            # Fetch merged SKU metric data
            merged_dto = self.erp_development_service.get_merged_sku_metric_info(sku_number, user_id)
            if not merged_dto:
                raise
            # Serialize response
            serialized_merged_dto = MergedSkuMetricSerializer(merged_dto).data
            # Serialize response
            return Response(serialized_merged_dto, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            logger.error(MERGED_ERP_SKU_METRIC_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": GENERAL_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(MERGED_ERP_SKU_METRIC_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": GENERAL_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": GENERAL_FETCH_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
