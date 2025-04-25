"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from datetime import timedelta
from typing import List

from django.utils import timezone

from .inventory_optimization_repository_interface import InventoryOptimizationRepositoryInterface
from ..models.inventory_optimization import InventoryOptimization
from ..models.serializers.page_criteria_serializers import PageParams, InventoryOptimizationCriteria

logger = logging.getLogger(__name__)


class InventoryOptimizationRepository(InventoryOptimizationRepositoryInterface):

    @staticmethod
    def find_all_inventory_optimizations(
            page_params: PageParams, criteria: InventoryOptimizationCriteria
    ) -> List[InventoryOptimization]:
        """
        Retrieves all inventory optimization records from the database based on the provided criteria
        and paginates the results.

        :param page_params: PageParams(page, page_size): Pagination parameters containing the current page number and optional page size.
        :param criteria: InventoryOptimizationCriteria: Filtering criteria including inventory_record_id and date range.
        :return: List[InventoryOptimization]: A list of InventoryOptimization objects matching the criteria.
        """
        queryset = InventoryOptimization.objects.all()

        # Filtering
        if criteria.validated_data.get('user_id'):
            queryset = queryset.filter(user_id=criteria.validated_data['user_id'])
        if criteria.validated_data.get("inventory_record_id"):
            queryset = queryset.filter(inventory_record_id=criteria.validated_data["inventory_record_id"])
        if criteria.validated_data.get("start_date"):
            queryset = queryset.filter(created_at__gte=criteria.validated_data["start_date"])
        if criteria.validated_data.get("end_date"):
            queryset = queryset.filter(created_at__lte=criteria.validated_data["end_date"])

        # Pagination
        page = page_params.validated_data["page"]
        page_size = page_params.validated_data.get("page_size", None)
        if page_size:
            offset = (page - 1) * page_size
            queryset = queryset[offset: offset + page_size]

        return list(queryset)

    @staticmethod
    def store_inventory_optimization(inventory_optimization: InventoryOptimization) -> InventoryOptimization:
        """
        Stores or updates the given InventoryOptimization record in the database.
        If a record with the same inventory_record_id, user, and sku_number exists
        and its updated_at is within the last day, it is updated.
        Otherwise, a new record is created.

        :param inventory_optimization: InventoryOptimization: The InventoryOptimization instance to be stored.
        :return: InventoryOptimization: The stored or updated InventoryOptimization object.
        """
        # Convert the model instance to a dictionary, filtering out None values and Django internals.
        inventory_optimization_fields = {
            key: value
            for key, value in vars(inventory_optimization).items()
            if value is not None and key != "_state"
        }
        # Extract the key fields used to identify the record.
        inventory_record_id = inventory_optimization.inventory_record_id
        user_id = inventory_optimization.user.id
        sku_number = inventory_optimization.sku_number
        # Ensure these keys are part of the fields.
        inventory_optimization_fields["inventory_record_id"] = inventory_record_id
        inventory_optimization_fields["user_id"] = user_id
        # Determine the threshold for a "fresh" record (i.e. updated within the last 10 hours).
        update_threshold = timezone.now() - timedelta(hours=10)
        # Look for an existing record with these keys and a recent updated_at.
        qs = InventoryOptimization.objects.filter(
            inventory_record_id=inventory_record_id,
            user_id=user_id,
            sku_number=sku_number,
            updated_at__gte=update_threshold
        ).order_by('-updated_at')  # update the latest one if there are same rows
        if qs.exists():
            # If a fresh record exists, update it.
            obj = qs.first()
            for field, value in inventory_optimization_fields.items():
                setattr(obj, field, value)
            obj.save()
        else:
            # Otherwise, create a new record.
            obj = InventoryOptimization.objects.create(**inventory_optimization_fields)

        return obj
