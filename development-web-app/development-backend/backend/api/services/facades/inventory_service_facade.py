"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import Dict

import inject

from .inventory_service_facade_interface import InventoryServiceFacadeInterface
from .model_inference_service_facade_interface import ModelInferenceServiceFacadeInterface
from ..inventory_optimization_service_interface import InventoryOptimizationServiceInterface
from ..inventory_service_interface import InventoryServiceInterface
from ..sku_metric_service_interface import SkuMetricServiceInterface
from ..sku_order_quantity_prediction_service_interface import SkuOrderQuantityPredictionServiceInterface
from ...models.dtos.inventory_service_dto import InventoryServiceResponse, InventoryOptimizationRequest
from ...models.inventory_optimization import InventoryOptimization
from ...services.facades.erp_development_service_facade_interface import ErpDevelopmentServiceFacadeInterface
from ...utils.dto_converters import inventory_optimization_to_dto

logger = logging.getLogger(__name__)


class InventoryServiceFacade(InventoryServiceFacadeInterface):
    @inject.autoparams()
    def __init__(
            self,
            erp_development_service: ErpDevelopmentServiceFacadeInterface,
            sku_order_quantity_prediction_service: SkuOrderQuantityPredictionServiceInterface,
            sku_metric_service: SkuMetricServiceInterface,
            inventory_service: InventoryServiceInterface,
            inventory_optimization_service: InventoryOptimizationServiceInterface,
            model_inference_service: ModelInferenceServiceFacadeInterface
    ):
        self.erp_development_service = erp_development_service
        self.sku_order_quantity_prediction_service = sku_order_quantity_prediction_service
        self.sku_metric_service = sku_metric_service
        self.inventory_service = inventory_service
        self.inventory_optimization_service = inventory_optimization_service
        self.model_inference_service = model_inference_service

    def get_most_recent_sku_inventory_params(self, sku_number: int, user_id: int) -> dict:
        """
        Retrieves the most recent inventory parameters record from the ERP system and augments
        it with demand forecast parameters (`lambda_` and `sigma`).

        Steps:
        1. Calls `erp_development_service.get_most_recent_inventory_params_record` with the provided
           sku_number and user_id.
        2. If inventory parameters are not found, raises a ValueError.
        3. Calls `_get_lambda_and_sigma` to get the demand forecast parameters.
        4. Adds `lambda_` and `sigma` to the ERP inventory parameters dictionary.

        :param sku_number: int: The SKU number for which to fetch inventory parameters.
        :param user_id: int: The user ID requesting the inventory parameters.
        :return: Dict: A dictionary containing the inventory parameters along with demand forecast parameters.
        :raises ValueError: If no inventory parameters are found for the specified SKU and user.
        """
        # Fetch ERP inventory parameters.
        inventory_params = self.erp_development_service.get_most_recent_inventory_params_record(sku_number, user_id)
        if not inventory_params:
            raise ValueError(f"No inventory parameters found for SKU {sku_number} and user {user_id}")
        # Fetch demand forecast parameters.
        lambda_, sigma = self._get_lambda_and_sigma(sku_number, user_id)
        # Include lambda_ and sigma in the returned dictionary.
        inventory_params["lambda_"] = lambda_
        inventory_params["sigma"] = sigma
        # Return the final inventory parameters
        return inventory_params

    def run_inventory_optimization(
            self, inventory_optimization_request: InventoryOptimizationRequest
    ) -> InventoryServiceResponse:
        """
        Executes inventory optimization, either by:
        - Fetching ERP inventory parameters if none are provided.
        - Using user-provided parameters from the frontend.

        Steps:
        1) Fetch inventory parameters (from ERP or frontend input).
        2) Fetch or infer demand forecast (`lambda_`, `sigma`).
        3) Build the input dictionary for `optimize_inventory`.
        4) Call the optimization service.
        5) Create an `InventoryOptimization` record.
        6) Store and return the optimization response.

        :param inventory_optimization_request: InventoryOptimizationRequest: DTO containing `sku_number`, `user_id`,
                                           optional `inventory_params`.
        :return: InventoryServiceResponse: The response containing inventory data and optimization results.
        """

        # Define the inventory params
        if inventory_optimization_request.inventory_params is None:
            # Get the most recent inventory params from ERP
            inventory_params = self._fetch_erp_inventory_params(inventory_optimization_request.sku_number,
                                                                inventory_optimization_request.user_id)
            lambda_, sigma = self._get_lambda_and_sigma(inventory_optimization_request.sku_number,
                                                        inventory_optimization_request.user_id)
            # Add lambda_ and sigma to inventory_params
            inventory_params["lambda_"] = lambda_
            inventory_params["sigma"] = sigma
            is_custom = False
        else:
            # Use user-provided parameters
            inventory_params = inventory_optimization_request.inventory_params
            is_custom = True
        # Build the input params for optimize_inventory
        params = {
            "lambda": inventory_params.get("lambda_"),
            "sigma": inventory_params.get("sigma"),
            "stock_level": inventory_params.get("stock_level"),
            "T": inventory_params.get("time_period_t"),
            "K": inventory_params.get("fixed_order_cost_k"),
            "p": inventory_params.get("penalty_cost_p"),
            "i": inventory_params.get("holding_cost_rate_i"),
            "c": inventory_params.get("unit_cost_c"),
            "FTL": inventory_params.get("truckload_capacity_ftl"),
            "TR": inventory_params.get("transportation_cost_tr"),
        }
        # Call inventory_service.optimize_inventory
        optimization_result = self.inventory_service.optimize_inventory(params)
        # Build an InventoryOptimization object
        inventory_optimization_record = self._build_inventory_optimization(
            inventory_optimization_dto=inventory_optimization_request,
            optimization_result=optimization_result,
            inventory_params=inventory_params,
            is_custom=is_custom
        )
        # Store the optimization
        inventory_opt = self.inventory_optimization_service.create_inventory_optimization(inventory_optimization_record)
        # Return both (inventory_params/input, inventory_optimization/output) in a DTO
        return InventoryServiceResponse(
            inventory_params=inventory_params,
            inventory_optimization_dto=inventory_optimization_to_dto(inventory_opt,
                                                                     inventory_optimization_request.user_id)
        )

    def _fetch_erp_inventory_params(self, sku_number: int, user_id: int) -> Dict:
        """
        Fetches inventory parameters from the ERP system.

        Steps:
        1) Calls `get_most_recent_inventory_params_record()` from `erp_development_service`.
        2) If no parameters exist, raises a ValueError.

        :param sku_number: int: The SKU number for which inventory parameters are needed.
        :param user_id: int: The ID of the user requesting inventory optimization.
        :return: Dict: A dictionary containing ERP-fetched inventory parameters.
        :raises ValueError: If no inventory parameters are found.
        """
        inventory_params = self.erp_development_service.get_most_recent_inventory_params_record(sku_number, user_id)
        if not inventory_params:
            raise ValueError(f"No inventory parameters found for SKU {sku_number} and user {user_id}")
        return inventory_params

    def _get_lambda_and_sigma(self, sku_number: int, user_id: int) -> tuple[float, float]:
        """
        Fetches or generates demand forecast parameters (`lambda_` and `sigma`) for inventory optimization.

        Steps:
        1) Fetch `lambda_` (expected demand per period) and `sigma` (standard deviation of demand).
        2) If missing, run model inference and retrieve them again.

        :param sku_number: int: The SKU number for which demand parameters are needed.
        :param user_id: int: The ID of the user requesting inventory optimization.
        :return: tuple[float, float]: A tuple(lambda_, sigma) where `lambda_` (expected demand) and `sigma` (demand standard deviation).
        """
        # predicted_value => lambda, mae => sigma
        lambda_, sigma = self.sku_order_quantity_prediction_service.calculate_demand_parameters(sku_number)
        # If there are no demand forecasts, we need to generate them.
        if lambda_ is None or sigma is None:
            logger.info("Run model inference..")
            self.model_inference_service.run_sku_order_quantity_inference(sku_number, user_id)
            lambda_, sigma = self.sku_order_quantity_prediction_service.calculate_demand_parameters(sku_number)

        return lambda_, sigma

    @staticmethod
    def _build_inventory_optimization(
            inventory_optimization_dto: InventoryOptimizationRequest,
            optimization_result: Dict,
            inventory_params: Dict,
            is_custom: bool
    ) -> InventoryOptimization:
        """
        Constructs an `InventoryOptimization` model from the optimization result dictionary.

        :param inventory_optimization_dto: InventoryOptimizationRequest: DTO containing `sku_number`, `user_id`,
                                           optional `inventory_params`.
        :param optimization_result: Dict: A dictionary containing computed inventory optimization results.
        :param inventory_params: Dict: A dictionary containing the original inventory parameters.
        :param is_custom: bool: Indicates whether parameters were user-provided (True) or ERP-fetched (False).
        :return: InventoryOptimization: The constructed `InventoryOptimization` model object.
        """

        opt_values = optimization_result["optimized_values"]
        cost_details = optimization_result["cost_details"]

        inventory_opt = InventoryOptimization(
            sku_number=inventory_optimization_dto.sku_number,
            order_quantity_q=opt_values["Q"],
            reorder_point_r=opt_values["R"],
            holding_cost=cost_details["holding_cost"],
            setup_transportation_cost=cost_details["setup_cost_and_transportation_cost"],
            stockout_cost=cost_details["stockout_cost"],
            total_cost=optimization_result["total_cost"],
            order_frequency=inventory_params.get("lambda_") / opt_values["Q"],
            cycle_time=opt_values["Q"] / inventory_params.get("lambda_"),
            is_custom=is_custom,
            inventory_record_id=(
                    inventory_params.get("id")
                    or (inventory_optimization_dto.inventory_params.get("id")
                        if inventory_optimization_dto.inventory_params else None)
            ),
            user_id=inventory_optimization_dto.user_id
        )
        return inventory_opt
