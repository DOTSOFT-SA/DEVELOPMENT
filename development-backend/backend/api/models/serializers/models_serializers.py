from rest_framework import serializers

from ..inventory_optimization import InventoryOptimization
from ...models.distribution_optimization import DistributionOptimization
from ...models.sku_order_quantity_prediction import SkuOrderQuantityPrediction


class SkuOrderQuantityPredictionSerializer(serializers.ModelSerializer):
    """
    Serializer for SKU Order Quantity Predictions.
    Used for both input validation (POST) and structured output (GET).
    """

    class Meta:
        model = SkuOrderQuantityPrediction
        fields = '__all__'  # Includes all model fields


class InventoryOptimizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Inventory Optimization model.
    """

    class Meta:
        model = InventoryOptimization
        fields = "__all__"  # Includes all model fields


class DistributionOptimizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Distribution Optimization model.
    Handles serialization and deserialization of distribution optimization records.
    """

    class Meta:
        model = DistributionOptimization
        fields = "__all__"  # Includes all model fields


class SkuInputSerializer(serializers.Serializer):
    """
    Serializer for the input data needed to retrieve merged SKU metric info.
    """
    sku_number = serializers.IntegerField()
    user_id = serializers.IntegerField()
