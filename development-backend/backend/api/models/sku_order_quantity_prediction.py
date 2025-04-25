"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models

from .login_user import LoginUser
from .sku_metric import SkuMetric


class SkuOrderQuantityPrediction(models.Model):
    id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255)
    sku_number = models.IntegerField()
    week_number = models.IntegerField()
    year_of_the_week = models.IntegerField()
    predicted_value = models.FloatField()
    mae = models.FloatField()
    mape = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
    # Reference to sku_metric
    sku_order_record = models.OneToOneField(
        SkuMetric,
        to_field='sku_order_record_id',  # references the unique 'sku_order_record_id' field in SkuMetric
        db_column='sku_order_record_id',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    # Reference to user
    user = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id'
    )

    class Meta:
        db_table = 'sku_order_quantity_prediction'

    def __str__(self):
        """
        String representation for debugging/logging.
        """
        return f"SkuOrderQuantityPrediction(id={self.id}, model_name={self.model_name}, sku_number={self.sku_number})"
