"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models

from .login_user import LoginUser


class SkuMetric(models.Model):
    id = models.AutoField(primary_key=True)
    sku_number = models.IntegerField(null=True, blank=True)
    is_weekend = models.BooleanField(null=True, blank=True)
    is_holiday = models.BooleanField(null=True, blank=True)
    mean_temperature = models.FloatField(null=True, blank=True)
    rain = models.BooleanField(null=True, blank=True)
    average_competition_price_external = models.FloatField(null=True, blank=True)
    review_sentiment_score = models.FloatField(null=True, blank=True)
    review_sentiment_timestamp = models.DateTimeField(null=True, blank=True)
    trend_value = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Unique, non-null integer to map SkuOrder record from ERP
    sku_order_record_id = models.IntegerField(unique=True)
    # ForeignKey to user model (login_user table)
    user = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'sku_metric'

    def __str__(self):
        """
        String representation of this SKU metric object.
        """
        return f"SkuMetric(id={self.id}, sku_order_record_id={self.sku_order_record_id})"
