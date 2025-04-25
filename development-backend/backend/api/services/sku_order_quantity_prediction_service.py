"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import List, Optional

import inject
import numpy as np
from django.core.exceptions import ObjectDoesNotExist

from .sku_order_quantity_prediction_service_interface import SkuOrderQuantityPredictionServiceInterface
from ..models.serializers.page_criteria_serializers import PageParams, SkuOrderQuantityPredictionCriteria
from ..models.sku_order_quantity_prediction import SkuOrderQuantityPrediction
from ..repositories.sku_order_quantity_prediction_repository_interface import \
    SkuOrderQuantityPredictionRepositoryInterface

logger = logging.getLogger(__name__)


class SkuOrderQuantityPredictionService(SkuOrderQuantityPredictionServiceInterface):

    @inject.autoparams()
    def __init__(self, sku_order_quantity_prediction_repository: SkuOrderQuantityPredictionRepositoryInterface):
        self.sku_order_quantity_prediction_repository = sku_order_quantity_prediction_repository

    def get_all_predictions(self, page_params: PageParams, criteria: SkuOrderQuantityPredictionCriteria) -> List[
        SkuOrderQuantityPrediction]:
        """
        Retrieves all SKU order quantity predictions that match the specified criteria.

        :param page_params: PageParams: Pagination parameters containing the current page number and optional page size.
        :param criteria: SkuOrderQuantityPredictionCriteria: Filtering criteria for retrieving SKU order quantity
                          predictions, including model name, user ID, SKU number, start date, end date etc.
        :return: List[SkuOrderQuantityPrediction]: A list of SkuOrderQuantityPrediction instances that match
                 the specified criteria.
        """
        return self.sku_order_quantity_prediction_repository.find_all_sku_order_quantity_predictions(page_params,
                                                                                                     criteria)

    def create_sku_order_quantity_prediction(self, sku_order_quantity_prediction: SkuOrderQuantityPrediction) -> None:
        """
        Saves a single SkuOrderQuantityPrediction record in the database.

        :param sku_order_quantity_prediction: SkuOrderQuantityPrediction: The sku_order_quantity_prediction instance
                                              containing the forecast data to be stored.
        :return: None
        """
        self.sku_order_quantity_prediction_repository.store_sku_order_quantity_prediction(sku_order_quantity_prediction)

    def get_sku_order_quantity_prediction_by_record_id(self, record_id: int) -> Optional[SkuOrderQuantityPrediction]:
        """
        Retrieves a single SkuOrderQuantityPrediction by its sku_order_record_id.
        Returns None if not found.

        :param record_id: int: The sku_order_record_id to search for.
        :return: Optional[SkuOrderQuantityPrediction]: The matching SkuOrderQuantityPrediction instance, or None if not found.
        :raises ObjectDoesNotExist: If no matching record is found.
        """
        try:
            return self.sku_order_quantity_prediction_repository.find_sku_order_quantity_prediction_by_record_id(
                record_id)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"No SkuOrderQuantityPrediction found for sku_order_record_id={record_id}.")

    def calculate_demand_parameters(self, sku_number: int) -> tuple[None, None] | tuple[float, float]:
        """
        Calculate demand parameters (lambda and sigma) based on the predicted order quantities
        for the given sku_number.

        :param sku_number: int: The SKU number to calculate parameters for.
        :return: tuple[None, None] | tuple[float, float]: A tuple containing 'lambda' (mean demand) and 'sigma'
                 (standard deviation). If no predictions exist, returns (None, None).
        """
        predictions: List[SkuOrderQuantityPrediction] = \
            self.sku_order_quantity_prediction_repository.find_sku_order_quantity_prediction_by_sku_number(sku_number)
        if not predictions:
            logger.info(f"No predictions found for SKU number {sku_number}.")
            return None, None
        # Extract the predicted order quantities
        predicted_values = [pred.predicted_value for pred in predictions]
        # Calculate lambda (mean demand) and sigma (standard deviation)
        # TODO: Investigate the following approach
        lambda_ = float(np.mean(predicted_values)) if float(np.mean(predicted_values)) != 0 else 1.0
        sigma = float(np.std(predicted_values)) if float(np.std(predicted_values)) != 0 else 1.0
        return lambda_, sigma
