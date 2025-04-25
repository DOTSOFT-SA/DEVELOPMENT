"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoginUser(BaseModel):
    id: int
    email: str
    password: str
    role: str
    is_active: bool
    updated_at: datetime
    create_at: Optional[datetime]
    last_login: Optional[datetime]


class SkuMetric(BaseModel):
    id: Optional[int] = None
    sku_number: Optional[int] = None
    is_weekend: Optional[bool] = None
    is_holiday: Optional[bool] = None
    mean_temperature: Optional[float] = None
    rain: Optional[bool] = None
    average_competition_price_external: Optional[float] = None
    review_sentiment_score: Optional[float] = None
    review_sentiment_timestamp: Optional[datetime] = None
    trend_value: Optional[int] = None
    updated_at: Optional[datetime] = None
    sku_order_record_id: Optional[int] = None  # Required in DB (unique + not null)
    user_id: Optional[int] = None  # Required in DB (foreign key to login_user.id)

    model_config = {"from_attributes": True}


class MlModel(BaseModel):
    """
    Stores an ML model file (.sav) in the DB for a given user_id.
    """
    id: Optional[int] = None
    model_type: str  # e.g., 'sku_quantity_prediction_ml_model'
    model_name: Optional[str] = None  # e.g., 'DecisionTreeRegressor'
    model_file: Optional[bytes] = None
    mape: Optional[float] = None
    mae: Optional[float] = None
    model_features: Optional[str] = None
    updated_at: Optional[datetime] = None
    user_id: int

    model_config = {"from_attributes": True}


class UserErpApi(BaseModel):
    """
    Represents the ERP API configuration for a given user.
    """
    id: Optional[int] = None
    client_name: str
    login_token_url: str
    sku_order_url: str
    inventory_params_url: str
    distribution_routing_url: str
    sku_order_latest_url: str
    inventory_params_latest_url: str
    token_username: str
    token_password: str
    user_id: int

    model_config = {"from_attributes": True}
