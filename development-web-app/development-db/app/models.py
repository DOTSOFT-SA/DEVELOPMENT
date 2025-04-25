"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, func, UniqueConstraint, LargeBinary, \
    Float
from sqlalchemy.orm import relationship

from app.utils.database_connection import Base


class LoginUser(Base):
    __tablename__ = 'login_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    login_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user_privileges = relationship("UserPrivilege", back_populates="user", cascade="all, delete-orphan")
    user_erp_api = relationship("UserErpApi", back_populates="user", cascade="all, delete-orphan", uselist=False)


class Privilege(Base):
    __tablename__ = 'privilege'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

    user_privileges = relationship("UserPrivilege", back_populates="privilege", cascade="all, delete-orphan")


class UserPrivilege(Base):
    __tablename__ = 'user_privilege'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False)
    privilege_id = Column(Integer, ForeignKey('privilege.id', ondelete="CASCADE"), nullable=False)

    user = relationship("LoginUser", back_populates="user_privileges")
    privilege = relationship("Privilege", back_populates="user_privileges")

    # The table cannot have two or more records with the same 'user_id' and 'privilege_id'
    __table_args__ = (UniqueConstraint('user_id', 'privilege_id', name='uq_user_privilege'),)


class SkuMetric(Base):
    __tablename__ = 'sku_metric'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_number = Column(Integer, nullable=True)
    is_weekend = Column(Boolean, nullable=True)
    is_holiday = Column(Boolean, nullable=True)
    mean_temperature = Column(Float, nullable=True)
    rain = Column(Boolean, nullable=True)
    average_competition_price_external = Column(Float, nullable=True)
    review_sentiment_score = Column(Float, nullable=True)
    review_sentiment_timestamp = Column(TIMESTAMP, nullable=True)
    trend_value = Column(Integer, nullable=True)
    # Update by default when the record is updated
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    sku_order_record_id = Column(Integer, unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("LoginUser", back_populates="sku_metrics")


class SkuOrderQuantityPrediction(Base):
    __tablename__ = 'sku_order_quantity_prediction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)
    sku_number = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    year_of_the_week = Column(Integer, nullable=False)
    predicted_value = Column(Float, nullable=False)
    mae = Column(Float, nullable=False)
    mape = Column(Float, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    sku_order_record_id = Column(Integer, ForeignKey('sku_metric.sku_order_record_id', ondelete="CASCADE"),
                                 nullable=False)
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False)

    sku_metric = relationship("SkuMetric", back_populates="sku_predictions")
    user = relationship("LoginUser", back_populates="sku_predictions")


class InventoryOptimization(Base):
    __tablename__ = 'inventory_optimization'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_number = Column(Integer, nullable=False)
    order_quantity_q = Column(Float, nullable=False)
    reorder_point_r = Column(Float, nullable=False)
    holding_cost = Column(Float, nullable=False)
    setup_transportation_cost = Column(Float, nullable=False)
    stockout_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    order_frequency = Column(Float, nullable=False)  # λ / Q
    cycle_time = Column(Float, nullable=False)  # Q / λ
    # is_custom = inventory parameters were provided by a frontend user (True) or sourced from the ERP database (False)
    is_custom = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    inventory_record_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False)

    user = relationship("LoginUser", back_populates="inventory_optimizations")


class DistributionOptimization(Base):
    __tablename__ = 'distribution_optimization'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_cost = Column(Float, nullable=False)
    vehicle_id = Column(Integer, nullable=False)
    start_location_name = Column(String, nullable=False)
    destination_location_name = Column(String, nullable=False)
    units = Column(Integer, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False)

    user = relationship("LoginUser", back_populates="distribution_optimizations")


class MLModel(Base):
    __tablename__ = 'ml_model'

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type = Column(String, nullable=False)  # e.g., 'sku_quantity_prediction_ml_model'
    model_name = Column(String, nullable=False)  # e.g., 'DecisionTreeRegressor'
    model_file = Column(LargeBinary, nullable=False)  # store .sav file as binary
    mape = Column(Float, nullable=False)  # Mean Absolute Percentage Error
    mae = Column(Float, nullable=False)  # Mean Absolute Error
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False)
    model_features = Column(String, nullable=False)  # features used for training

    user = relationship("LoginUser", back_populates="ml_models")

    # A user cannot have the same model_type twice. But different users can have the same model_type.
    __table_args__ = (UniqueConstraint('model_type', 'user_id', name='uq_model_name_user'),)


class UserErpApi(Base):
    __tablename__ = 'user_erp_api'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String, nullable=False, unique=True)
    login_token_url = Column(String(512), nullable=False)
    sku_order_url = Column(String(512), nullable=True)
    inventory_params_url = Column(String(512), nullable=True)
    distribution_routing_url = Column(String(512), nullable=True)
    sku_order_latest_url = Column(String(512), nullable=True)
    inventory_params_latest_url = Column(String(512),
                                         nullable=True)
    token_username = Column(String, nullable=False)
    token_password = Column(String, nullable=False)

    # 1-to-1 relationship
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False, unique=True)

    user = relationship("LoginUser", back_populates="user_erp_api")
