"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from django.db import models

from .login_user import LoginUser


class MLModel(models.Model):
    """
    Stores an ML model file (.sav) in the database for a given user_id.
    """
    id = models.AutoField(primary_key=True)
    model_type = models.CharField(max_length=255)  # e.g., 'sku_quantity_prediction_ml_model'
    model_name = models.CharField(max_length=255)  # e.g., 'DecisionTreeRegressor'
    model_file = models.BinaryField()  # Stores the trained model file as binary data
    mape = models.FloatField()  # Mean Absolute Percentage Error
    mae = models.FloatField()  # Mean Absolute Error
    model_features = models.CharField()
    updated_at = models.DateTimeField(auto_now=True)

    # Foreign key to associate models with users
    user = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        db_column='user_id'
    )

    class Meta:
        db_table = 'ml_model'
        unique_together = ('model_type', 'user')  # Ensure unique models per user

    def __str__(self):
        """
        String representation for debugging/logging.
        """
        return f"MLModel(id={self.id}, model_type={self.model_type}, user_id={self.user.id})"
