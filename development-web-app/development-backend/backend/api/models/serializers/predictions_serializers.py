"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from ..dtos.inventory_service_dto import InventoryOptimizationDto


class SkuOrderQuantityPredictionDTOSerializer(serializers.Serializer):
    """
    Serializer for SkuOrderQuantityPrediction fields.
    """
    sku_number = serializers.IntegerField()
    week_number = serializers.IntegerField()
    year_of_the_week = serializers.IntegerField()
    predicted_value = serializers.FloatField()
    mape = serializers.FloatField()


class InventoryOptimizationDtoSerializer(DataclassSerializer):
    """
    Serializer for the Inventory Optimization model.
    """

    class Meta:
        dataclass = InventoryOptimizationDto


class InventoryParamsSerializer(serializers.Serializer):
    """
    Serializer for inventory optimization parameters.
    Ensures that required parameters are provided together and follow logical constraints.
    """
    id = serializers.IntegerField(required=False, allow_null=True)  # Optional, if the users knows it
    lambda_ = serializers.FloatField(required=True, min_value=0.0001)  # Demand rate must be > 0
    sigma = serializers.FloatField(required=True, min_value=0.0001)  # Standard deviation must be > 0
    stock_level = serializers.IntegerField(required=False, min_value=0.0)  # Stock level can be 0
    time_period_t = serializers.FloatField(required=True, min_value=0.0001)  # Time period must be > 0
    fixed_order_cost_k = serializers.FloatField(required=True, min_value=0.0)  # Fixed order cost can be 0
    penalty_cost_p = serializers.FloatField(required=True, min_value=0.0)  # Penalty cost can be 0
    holding_cost_rate_i = serializers.FloatField(required=True, min_value=0.0)  # Holding cost rate can be 0
    unit_cost_c = serializers.FloatField(required=True, min_value=0.0001)  # Unit cost must be > 0
    truckload_capacity_ftl = serializers.FloatField(required=True, min_value=0.0001)  # Truckload capacity must be > 0
    transportation_cost_tr = serializers.FloatField(required=True, min_value=0.0)  # Transportation cost can be 0


class InventoryOptimizationInputSerializer(serializers.Serializer):
    """
    Serializer for inventory optimization input parameters.
    Ensures that either all inventory parameters are provided or ERP defaults are used.
    """
    user_id = serializers.IntegerField(required=True)
    sku_number = serializers.IntegerField(required=True)
    inventory_params = InventoryParamsSerializer(required=False, allow_null=True)

    def validate(self, data):
        """
        Validates that either all parameters are provided or none at all.
        """
        inventory_params = data.get("inventory_params")

        # If inventory_params is provided, ensure all fields exist
        if inventory_params is not None:
            if not isinstance(inventory_params, dict):
                raise serializers.ValidationError("inventory_params must be a valid dictionary of parameters.")
            missing_fields = [
                field for field in InventoryParamsSerializer().fields.keys() if field not in inventory_params
            ]
            if missing_fields:
                raise serializers.ValidationError(f"Missing required fields in inventory_params: {missing_fields}")

        return data


class InventoryOptimizationResultSerializer(serializers.Serializer):
    """
    Combines both 'inventory_params' (raw ERP response) and
    the newly computed 'InventoryOptimization' record in one response.
    """
    inventory_params = serializers.DictField()
    inventory_optimization_dto = InventoryOptimizationDtoSerializer()


class DistributionOptimizationInputSerializer(serializers.Serializer):
    """
    Serializer for the input data required to run a distribution routing optimization.
    Typically, includes just the user_id, or could contain other fields if needed.
    """
    user_id = serializers.IntegerField(required=True)


class MergedSkuMetricSerializer(serializers.Serializer):
    """
    Serializer for MergedSkuMetricDto, combining both external ERP data
    and local SkuMetric fields.
    """
    order_date = serializers.DateTimeField(required=False, allow_null=True)
    sku_number = serializers.IntegerField(required=False, allow_null=True)
    sku_name = serializers.CharField(required=False, allow_null=True)
    class_display_name = serializers.CharField(required=False, allow_null=True)
    order_item_price_in_main_currency = serializers.FloatField(required=False, allow_null=True)
    order_item_unit_count = serializers.IntegerField(required=False, allow_null=True)
    cl_price = serializers.FloatField(required=False, allow_null=True)
    is_weekend = serializers.BooleanField(required=False, allow_null=True)
    is_holiday = serializers.BooleanField(required=False, allow_null=True)
    mean_temperature = serializers.FloatField(required=False, allow_null=True)
    rain = serializers.BooleanField(required=False, allow_null=True)
    average_competition_price_external = serializers.FloatField(required=False, allow_null=True)
    review_sentiment_score = serializers.FloatField(required=False, allow_null=True)
    review_sentiment_timestamp = serializers.DateTimeField(required=False, allow_null=True)
    trend_value = serializers.IntegerField(required=False, allow_null=True)


class ModelInferenceInputSerializer(serializers.Serializer):
    sku_number = serializers.IntegerField()
    user_id = serializers.IntegerField()


class ModelInferenceDemandPredictionResultSerializer(serializers.Serializer):
    """
    Combines both MergedSkuMetricDto and SkuOrderQuantityPredictionDTO in one response.
    """
    merged_sku_metric = MergedSkuMetricSerializer()
    sku_order_quantity_prediction = SkuOrderQuantityPredictionDTOSerializer()
