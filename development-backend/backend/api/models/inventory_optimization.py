"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models

from .login_user import LoginUser


class InventoryOptimization(models.Model):
    """
    Represents an inventory optimization record storing computed values for order quantity,
    reorder points, and various cost factors.
    """

    id = models.AutoField(primary_key=True)
    sku_number = models.IntegerField()
    order_quantity_q = models.FloatField()
    reorder_point_r = models.FloatField()
    holding_cost = models.FloatField()
    setup_transportation_cost = models.FloatField()
    stockout_cost = models.FloatField()
    total_cost = models.FloatField()
    order_frequency = models.FloatField()
    cycle_time = models.FloatField()
    is_custom = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    inventory_record_id = models.IntegerField(null=True)

    # Foreign Key Reference to User
    user = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id'
    )

    class Meta:
        db_table = 'inventory_optimization'

    def __str__(self):
        return (
            f"InventoryOptimization(id={self.id}, "
            f"inventory_record_id={self.inventory_record_id}, "
            f"total_cost={self.total_cost})"
        )
