"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from datetime import timedelta
from typing import List, Optional

from django.utils import timezone

from .sku_order_quantity_prediction_repository_interface import SkuOrderQuantityPredictionRepositoryInterface
from ..models.serializers.page_criteria_serializers import PageParams, SkuOrderQuantityPredictionCriteria
from ..models.sku_order_quantity_prediction import SkuOrderQuantityPrediction

logger = logging.getLogger(__name__)


class SkuOrderQuantityPredictionRepository(SkuOrderQuantityPredictionRepositoryInterface):

    @staticmethod
    def find_all_sku_order_quantity_predictions(
            page_params: PageParams,
            criteria: SkuOrderQuantityPredictionCriteria
    ) -> List[SkuOrderQuantityPrediction]:
        """
        Retrieves all matching SKU order quantity predictions from the database based on the provided criteria
        and paginates the results.

        :param page_params: PageParams: Pagination parameters containing the current page number and optional page size.
        :param criteria: SkuOrderQuantityPredictionCriteria: Filtering criteria for retrieving SKU order quantity
                          predictions, including model name, user ID, SKU number, start date, end date etc.
        :return: List[SkuOrderQuantityPrediction]: A list of SkuOrderQuantityPrediction objects that match the given
                 criteria, with pagination applied if specified.
        """
        queryset = SkuOrderQuantityPrediction.objects.all()
        # Filtering
        if criteria.validated_data.get('user_id'):
            queryset = queryset.filter(user_id=criteria.validated_data['user_id'])
        if criteria.validated_data.get('model_type'):
            queryset = queryset.filter(model_name__icontains=criteria.validated_data['model_type'])
        if criteria.validated_data.get('sku_number'):
            queryset = queryset.filter(sku_number=criteria.validated_data['sku_number'])
        if criteria.validated_data.get('start_date'):
            queryset = queryset.filter(created_at__gte=criteria.validated_data['start_date'])
        if criteria.validated_data.get('end_date'):
            queryset = queryset.filter(created_at__lte=criteria.validated_data['end_date'])
        # Pagination
        page = page_params.validated_data['page']
        page_size = page_params.validated_data.get('page_size', None)
        if page_size:
            offset = (page - 1) * page_size
            queryset = queryset[offset: offset + page_size]
        # Return with Pagination/Filtering or not
        return list(queryset)

    @staticmethod
    def store_sku_order_quantity_prediction(
            sku_order_quantity_prediction: SkuOrderQuantityPrediction) -> SkuOrderQuantityPrediction:
        """
        Stores the given SkuOrderQuantityPrediction in the database.
        If a record with the same sku_order_record_id and user_id exists and was updated
        within the last day, it is updated. Otherwise, a new record is created.

        :param sku_order_quantity_prediction: SkuOrderQuantityPrediction: The SkuOrderQuantityPrediction instance
                                              containing the data.
        :return: SkuOrderQuantityPrediction: The stored SkuOrderQuantityPrediction object after saving it to the database.
        """
        # Convert the model instance into a dictionary and filter out None values.
        sku_order_quantity_prediction_fields = {
            key: value
            for key, value in vars(sku_order_quantity_prediction).items()
            if value is not None and key != "_state"
        }
        # Extract the key identifiers.
        sku_order_record_id = sku_order_quantity_prediction.sku_order_record.sku_order_record_id
        user_id = sku_order_quantity_prediction.user.id
        # Ensure these keys are included in the fields dictionary.
        sku_order_quantity_prediction_fields['sku_order_record_id'] = sku_order_record_id
        sku_order_quantity_prediction_fields['user_id'] = user_id
        # Determine the threshold for a "fresh" record (i.e., updated within the last 10 hours).
        update_threshold = timezone.now() - timedelta(hours=10)
        # Look for an existing record that matches and was updated in the last day.
        qs = SkuOrderQuantityPrediction.objects.filter(
            sku_order_record_id=sku_order_record_id,
            user_id=user_id,
            updated_at__gte=update_threshold
        ).order_by('-updated_at')  # update the latest one if there are same rows
        if qs.exists():
            # If a fresh record exists, update it.
            obj = qs.first()
            for field, value in sku_order_quantity_prediction_fields.items():
                setattr(obj, field, value)
            obj.save()
        else:
            # Otherwise, create a new record.
            obj = SkuOrderQuantityPrediction.objects.create(**sku_order_quantity_prediction_fields)
        return obj

    @staticmethod
    def find_sku_order_quantity_prediction_by_record_id(record_id: int) -> Optional[SkuOrderQuantityPrediction]:
        """
        Retrieves a single SkuOrderQuantityPrediction by sku_order_record_id.

        :param record_id: int: The sku_order_record_id to filter by.
        :return: Optional[SkuOrderQuantityPrediction]: The SkuOrderQuantityPrediction instance if found, otherwise None.
        """
        return SkuOrderQuantityPrediction.objects.get(sku_order_record_id=record_id)

    @staticmethod
    def find_sku_order_quantity_prediction_by_sku_number(sku_number: int) -> List[SkuOrderQuantityPrediction]:
        """
        Retrieve all SkuOrderQuantityPrediction records for the given sku_number.

        :param sku_number: int: The sku_number to filter by.
        :return: List[SkuOrderQuantityPrediction]: A list of SkuOrderQuantityPrediction objects matching the sku_number,
                 or an empty list if no matches are found.
        """
        return list(SkuOrderQuantityPrediction.objects.filter(sku_number=sku_number))
