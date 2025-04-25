"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models

from .login_user import LoginUser


class DistributionOptimization(models.Model):
    id = models.AutoField(primary_key=True)
    total_cost = models.FloatField()
    vehicle_id = models.IntegerField()
    start_location_name = models.CharField()
    destination_location_name = models.CharField()
    units = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    # Foreign Key
    user = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id'
    )

    class Meta:
        db_table = 'distribution_optimization'

    def __str__(self):
        return f"DistributionOptimization(id={self.id}, total_cost={self.total_cost})"
