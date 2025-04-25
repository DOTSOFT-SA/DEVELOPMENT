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
from ..models.serializers.models_serializers import SkuOrderQuantityPredictionSerializer
from ..models.serializers.page_criteria_serializers import PageParams, SkuOrderQuantityPredictionCriteria
from ..services.sku_order_quantity_prediction_service_interface import SkuOrderQuantityPredictionServiceInterface
from ..utils.constant_messages import SKU_ORDER_QUANTITY_PREDICTION_FETCH_FAILED_EN, SKU_ORDER_QUANTITY_FETCH_FAILED_GR
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission
from ..utils.enums import Role, UserPrivileges

logging.basicConfig()
logger = logging.getLogger(__name__)


class SkuOrderQuantityPredictionViewSet(viewsets.ViewSet):
    # Define permission requirement
    forecasting_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[UserPrivileges.DEMAND_FORECASTING.value]
    )

    @inject.autoparams()
    def __init__(self, sku_order_quantity_prediction_service: SkuOrderQuantityPredictionServiceInterface, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.sku_order_quantity_prediction_service = sku_order_quantity_prediction_service

    @action(detail=False, methods=['get'], permission_classes=[forecasting_permissions])
    def get_all_sku_order_quantity_predictions(self, request) -> Response:
        """
        Retrieves a paginated list of SKU order quantity predictions.

        Steps:
          1) Ensures 'user_id' is enforced in query parameters to prevent unauthorized data access.
          2) Applies pagination and filtering using `PageParams` and `SkuOrderQuantityPredictionCriteria`.
          3) Fetches the filtered records via `get_all_predictions(...)`.
          4) Serializes the retrieved records into `SkuOrderQuantityPredictionSerializer`.
          5) Returns the serialized data in the response.

        :param request: The HTTP request containing optional query parameters for filtering and pagination.
        :return: Response: A paginated list of SKU order quantity predictions.
        """
        try:
            # Force 'user_id' to be int criteria (avoid see data of all users at once)
            query_params = force_user_id_as_criteria(request)
            # Consider Pagination and Filtering
            page_serializer = PageParams(data=query_params)
            criteria_serializer = SkuOrderQuantityPredictionCriteria(data=query_params)
            page_serializer.is_valid(raise_exception=True)
            criteria_serializer.is_valid(raise_exception=True)
            # Fetch filtered & paginated predictions
            sku_order_quantity_predictions = self.sku_order_quantity_prediction_service.get_all_predictions(
                page_params=page_serializer, criteria=criteria_serializer)
            # Serialize predictions into JSON
            serialized_predictions = SkuOrderQuantityPredictionSerializer(sku_order_quantity_predictions, many=True)
            # Return records
            return Response(serialized_predictions.data, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            logger.error(SKU_ORDER_QUANTITY_PREDICTION_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": SKU_ORDER_QUANTITY_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(SKU_ORDER_QUANTITY_PREDICTION_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": SKU_ORDER_QUANTITY_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in list_predictions: {str(e)}", exc_info=True)
            return Response({"error": SKU_ORDER_QUANTITY_FETCH_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
