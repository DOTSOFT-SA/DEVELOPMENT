"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from rest_framework import serializers


class PageParams(serializers.Serializer):
    """
    Basic pagination parameters using DRF fields.
    """
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, required=False, allow_null=True)


class SkuOrderQuantityPredictionCriteria(serializers.Serializer):
    """
    Filtering fields for SkuOrderQuantityPrediction.
    """
    model_name = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.IntegerField(required=True)
    sku_number = serializers.IntegerField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)


class InventoryOptimizationCriteria(serializers.Serializer):
    """
    Filtering criteria for Inventory Optimization records.
    """
    inventory_record_id = serializers.IntegerField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    user_id = serializers.IntegerField(required=True)


class DistributionOptimizationCriteria(serializers.Serializer):
    """
    Filtering criteria for Distribution Optimization records.
    """
    vehicle_id = serializers.IntegerField(required=False)
    start_location_name = serializers.CharField(required=False)
    destination_location_name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    user_id = serializers.IntegerField(required=True)
