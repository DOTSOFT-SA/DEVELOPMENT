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

from ..models.dtos.inventory_service_dto import InventoryOptimizationRequest
from ..models.serializers.models_serializers import SkuInputSerializer
from ..models.serializers.predictions_serializers import (
    ModelInferenceInputSerializer,
    ModelInferenceDemandPredictionResultSerializer, InventoryOptimizationResultSerializer,
    InventoryOptimizationInputSerializer, DistributionOptimizationInputSerializer
)
from ..services.facades.distribution_optimization_routing_facade_interface import \
    DistributionOptimizationRoutingFacadeInterface
from ..services.facades.inventory_service_facade_interface import InventoryServiceFacadeInterface
from ..services.facades.model_inference_service_facade_interface import ModelInferenceServiceFacadeInterface
from ..utils.constant_messages import SKU_ORDER_QUANTITY_PREDICTION_FETCH_FAILED_EN, SKU_ORDER_QUANTITY_FETCH_FAILED_GR, \
    INVENTORY_OPTIMIZATION_FETCH_FAILED_EN, INVENTORY_OPTIMIZATION_FETCH_FAILED_GR, \
    DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_EN, DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR, \
    INVENTORY_PARAMS_FETCH_FAILED_EN, INVENTORY_PARAMS_FETCH_FAILED_GR
from ..utils.custom_exceptions import CustomLoggerException
from ..utils.decorators import create_role_privilege_permission
from ..utils.enums import Role, UserPrivileges

logger = logging.getLogger(__name__)


class PredictionsViewSet(viewsets.ViewSet):
    """
    ViewSet to handle SKU order quantity prediction inference.
    """

    forecasting_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[UserPrivileges.DEMAND_FORECASTING.value]
    )

    forecasting_and_inventory_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[
            # UserPrivileges.DEMAND_FORECASTING.value,
            UserPrivileges.RECOMMENDED_STOCK_QUANTITY.value
        ]
    )

    routing_permissions = create_role_privilege_permission(
        required_role=Role.USER.value,
        required_privileges=[UserPrivileges.ROUTING.value]
    )

    @inject.autoparams()
    def __init__(self,
                 model_inference_service_facade: ModelInferenceServiceFacadeInterface,
                 inventory_service_facade: InventoryServiceFacadeInterface,
                 distribution_optimization_routing_facade: DistributionOptimizationRoutingFacadeInterface,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_inference_service = model_inference_service_facade
        self.inventory_service_facade = inventory_service_facade
        self.distribution_routing_facade = distribution_optimization_routing_facade

    @action(detail=False, methods=['post'], permission_classes=[forecasting_permissions])
    def run_inference(self, request) -> Response:
        """
        POST endpoint to run SKU order quantity inference.

        Returns 200 with merged_sku_metric & sku_order_quantity_prediction fields if successful,
        or 400/404/500 depending on errors.

        :param request: Request: The HTTP request object containing SKU inference input.
        :return: Response: The HTTP response containing inference results.
        :raises ValidationError: If the input data validation fails.
        :raises CustomLoggerException: If a domain-specific exception occurs.
        :raises Exception: If an unexpected error occurs.
        """
        model_inference_input_serializer = ModelInferenceInputSerializer(data=request.data)
        try:
            # 1. Validate the input
            model_inference_input_serializer.is_valid(raise_exception=True)
            sku_number = model_inference_input_serializer.validated_data['sku_number']
            user_id = model_inference_input_serializer.validated_data['user_id']
            # 2. The facade now returns ModelInferenceDto, not a tuple
            model_inference_dto = self.model_inference_service.run_sku_order_quantity_inference(sku_number, user_id)
            # 3. Build combined output for serialization
            output_data = {
                "merged_sku_metric": model_inference_dto.merged_sku_metric_dto.__dict__,
                "sku_order_quantity_prediction": model_inference_dto.sku_order_quantity_prediction.__dict__
            }
            # 4. Serialize final response
            result_serializer = ModelInferenceDemandPredictionResultSerializer(data=output_data)
            result_serializer.is_valid(raise_exception=True)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.error(SKU_ORDER_QUANTITY_PREDICTION_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": SKU_ORDER_QUANTITY_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except CustomLoggerException as e:
            logger.error(SKU_ORDER_QUANTITY_PREDICTION_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": SKU_ORDER_QUANTITY_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": SKU_ORDER_QUANTITY_FETCH_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[forecasting_and_inventory_permissions])
    def get_sku_inventory_params(self, request) -> Response:
        """
        Handles a POST request to retrieve the most recent inventory parameters record.
          1. Validates the request payload to ensure that a SKU number and user ID are provided.
          2. Calls the ERP service facade's `get_most_recent_inventory_params_record` method.
          3. Returns the inventory parameters data if successful.
          4. Returns an appropriate error response if data retrieval fails.

        :param request: The HTTP request containing the SKU number and user ID.
        :return: Response: A JSON response containing the inventory parameters data or an error message.
        :raises ValidationError: If the request payload is invalid.
        :raises CustomLoggerException: If a domain-specific issue occurs during data retrieval.
        :raises Exception: For any unexpected failures during execution.
        """
        try:
            # Validate request data using the same serializer as for merged sku metrics;
            # this expects both 'sku_number' and 'user_id'.
            serializer = SkuInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            sku_number = serializer.validated_data['sku_number']
            user_id = serializer.validated_data['user_id']
            # Fetch the most recent inventory parameters record from the ERP system.
            inventory_data = self.inventory_service_facade.get_most_recent_sku_inventory_params(sku_number, user_id)
            if not inventory_data:
                raise Exception("No inventory parameters data returned from ERP API.")
            # Return the raw inventory data.
            return Response(inventory_data, status=status.HTTP_200_OK)
        except CustomLoggerException as e:
            logger.error(INVENTORY_PARAMS_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": INVENTORY_PARAMS_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(INVENTORY_PARAMS_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": INVENTORY_PARAMS_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": INVENTORY_PARAMS_FETCH_FAILED_GR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[forecasting_and_inventory_permissions])
    def run_inventory_optimization(self, request) -> Response:
        """
        POST endpoint to run inventory optimization.

        Requires both DEMAND_FORECASTING and RECOMMENDED_STOCK_QUANTITY privileges.
        Returns final optimization info with a 200 if successful,
        or 400/404/500 depending on errors.

        :param request: Request: The HTTP request object containing inventory optimization input.
        :return: Response: The HTTP response containing optimization results.
        :raises ValidationError: If the input data validation fails.
        :raises CustomLoggerException: If a domain-specific exception occurs.
        :raises Exception: If an unexpected error occurs.
        """
        input_serializer = InventoryOptimizationInputSerializer(data=request.data)
        try:
            input_serializer.is_valid(raise_exception=True)
            # Extract validated data
            sku_number = input_serializer.validated_data['sku_number']
            user_id = input_serializer.validated_data['user_id']
            inventory_params = input_serializer.validated_data.get('inventory_params')
            # Create DTO
            dto = InventoryOptimizationRequest(sku_number=sku_number, user_id=user_id,
                                               inventory_params=inventory_params)
            # Call the facade
            inventory_dto = self.inventory_service_facade.run_inventory_optimization(dto)
            # Serialize output
            output_serializer = InventoryOptimizationResultSerializer(inventory_dto)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.error(INVENTORY_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": INVENTORY_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except CustomLoggerException as e:
            logger.error(INVENTORY_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": INVENTORY_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": INVENTORY_OPTIMIZATION_FETCH_FAILED_GR},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[routing_permissions])
    def run_distribution_optimization(self, request) -> Response:
        """
        POST endpoint to run distribution optimization with traffic factors.

        Requires the 'ROUTING' privilege.
        Returns distribution optimization records on success, or 400/500 on errors.

        :param request: Request: The HTTP request object containing distribution optimization input.
        :return: Response: The HTTP response containing optimization results.
        :raises ValidationError: If the input data validation fails.
        :raises CustomLoggerException: If a domain-specific exception occurs.
        :raises Exception: If an unexpected error occurs.
        """
        input_serializer = DistributionOptimizationInputSerializer(data=request.data)
        try:
            input_serializer.is_valid(raise_exception=True)
            user_id = input_serializer.validated_data['user_id']
            # 1) facade returns a DistributionRoutingDto
            distribution_dto = self.distribution_routing_facade.run_distribution_routing_optimization(user_id)
            # 2) Convert the DTO into a JSON-friendly structure
            output = {
                "total_cost": distribution_dto.total_cost,
                "routes": [
                    {
                        "vehicle_id": route.vehicle_id,
                        "start_location_name": route.start_location_name,
                        "destination_location_name": route.destination_location_name,
                        "units": route.units
                    }
                    for route in distribution_dto.routes
                ]
            }
            return Response(output, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.error(DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.detail, exc_info=True)
            return Response({"error": DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except CustomLoggerException as e:
            logger.error(DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_EN)
            logger.error(e.message, exc_info=True)
            return Response({"error": DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": DISTRIBUTION_OPTIMIZATION_FETCH_FAILED_GR},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
