"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import logging
from typing import List

from .distribution_optimization_repository_interface import DistributionOptimizationRepositoryInterface
from ..models.distribution_optimization import DistributionOptimization
from ..models.serializers.page_criteria_serializers import PageParams, DistributionOptimizationCriteria

logger = logging.getLogger(__name__)


class DistributionOptimizationRepository(DistributionOptimizationRepositoryInterface):

    @staticmethod
    def find_all_distribution_optimizations(page_params: PageParams,
                                            criteria: DistributionOptimizationCriteria) -> List[
        DistributionOptimization]:
        """
        Retrieves all distribution optimization records from the database based on the provided criteria
        and paginates the results.

        :param page_params: PageParams(page, page_size): Pagination parameters containing
                                                         the current page number and optional page size.
        :param criteria: DistributionOptimizationCriteria: Filtering criteria including user_id, vehicle_id,
                              start_location_name, destination_location_name, date range etc.
        :return: List[DistributionOptimization]: A list of DistributionOptimization objects matching the criteria.
        """
        queryset = DistributionOptimization.objects.all()
        # Filtering
        if criteria.validated_data.get('user_id'):
            queryset = queryset.filter(user_id=criteria.validated_data['user_id'])
        if criteria.validated_data.get('vehicle_id'):
            queryset = queryset.filter(vehicle_id=criteria.validated_data['vehicle_id'])
        if criteria.validated_data.get('start_location_name'):
            queryset = queryset.filter(vehicle_id=criteria.validated_data['start_location_name'])
        if criteria.validated_data.get('destination_location_name'):
            queryset = queryset.filter(vehicle_id=criteria.validated_data['destination_location_name'])
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
        # Returns a list of matching DistributionOptimization records
        return list(queryset)

    @staticmethod
    def store_distribution_optimization(
            distribution_optimization_record: DistributionOptimization) -> DistributionOptimization:
        """
        Inserts or updates a distribution optimization record in the database.

        :param distribution_optimization_record: DistributionOptimization:
        The distribution optimization record containing
                              user_id, vehicle_id, start_location_name, and destination_location_name.
        :return: DistributionOptimization: The stored or updated DistributionOptimization object.
        """
        # Convert the model instance into a dictionary except the internal '_state' parameter
        fields = {
            key: value
            for key, value in vars(distribution_optimization_record).items()
            if key != "_state" and value is not None
        }
        # Unique constraints
        user_id = distribution_optimization_record.user_id
        vehicle = distribution_optimization_record.vehicle_id
        start_loc = distribution_optimization_record.start_location_name
        dest_loc = distribution_optimization_record.destination_location_name

        obj, created = DistributionOptimization.objects.update_or_create(
            user_id=user_id,
            vehicle_id=vehicle,
            start_location_name=start_loc,
            destination_location_name=dest_loc,
            defaults=fields
        )
        return obj
