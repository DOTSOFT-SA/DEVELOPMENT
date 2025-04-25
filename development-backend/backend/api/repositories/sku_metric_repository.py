"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist

from .sku_metric_repository_interface import SkuMetricRepositoryInterface
from ..models.sku_metric import SkuMetric

logger = logging.getLogger(__name__)


class SkuMetricRepository(SkuMetricRepositoryInterface):

    @staticmethod
    def find_all_sku_order_record_ids_by_sku_number(sku_number: int) -> List[int]:
        """
        Retrieve a list of all 'sku_order_record_id' values from the SkuMetric table
        for a given sku_number.

        :param sku_number: int: The SKU number to filter by.
        :return: List[int]: A list of unique sku_order_record_id integers matching the given sku_number,
                            or an empty list if no records are found.
        """
        return list(
            SkuMetric.objects.filter(sku_number=sku_number)
            .values_list('sku_order_record_id', flat=True)
        )

    @staticmethod
    def find_by_sku_order_record_id(record_id: int) -> Optional[SkuMetric]:
        """
        Retrieve a single SkuMetric object based on the given sku_order_record_id.

        :param record_id: int: The sku_order_record_id to filter by.
        :return: Optional[SkuMetric]: The SkuMetric instance if found, otherwise None.
        """
        try:
            return SkuMetric.objects.get(sku_order_record_id=record_id)
        except ObjectDoesNotExist:
            return None
