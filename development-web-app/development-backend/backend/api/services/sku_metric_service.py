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

from .sku_metric_service_interface import SkuMetricServiceInterface
from ..models.sku_metric import SkuMetric
from ..repositories.sku_metric_repository_interface import SkuMetricRepositoryInterface

logger = logging.getLogger(__name__)


class SkuMetricService(SkuMetricServiceInterface):
    """
    Service layer for handling operations related to SKU metrics.
    """

    @inject.autoparams()
    def __init__(self, sku_metric_repository: SkuMetricRepositoryInterface):
        """
        Constructor injection of the SkuMetricRepository.
        """
        self.sku_metric_repository = sku_metric_repository

    def get_all_sku_order_record_ids_by_sku_number(self, sku_number: int) -> List[int]:
        """
        Retrieves a list of all 'sku_order_record_id' values from SkuMetric for a given SKU number.

        :param sku_number: int: The SKU number to filter by.
        :return: List[int]: A list of unique sku_order_record_id integers matching the given sku_number,
                            or an empty list if no records are found.
        """
        record_ids = self.sku_metric_repository.find_all_sku_order_record_ids_by_sku_number(sku_number)
        if not record_ids:
            logger.warning(f"No sku_order_record_ids found for sku_number={sku_number}.")
        return record_ids

    def get_by_sku_order_record_id(self, sku_order_record_id: int) -> Optional[SkuMetric]:
        """
        Retrieves a single SkuMetric object by sku_order_record_id.

        :param sku_order_record_id: int: The sku_order_record_id to filter by.
        :return: Optional[SkuMetric]: The SkuMetric instance if found, otherwise None.
        """
        sku_metric = self.sku_metric_repository.find_by_sku_order_record_id(sku_order_record_id)
        if not sku_metric:
            logger.warning(f"SkuMetric with record_id={sku_order_record_id} not found.")
        return sku_metric
