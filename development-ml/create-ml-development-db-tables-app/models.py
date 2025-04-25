"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Float, ForeignKey, TIMESTAMP, func, LargeBinary, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from utils.database_connection import Base
from utils.settings import settings


# Tables required for FK (create as well if not exists)
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

    sku_metrics = relationship("SkuMetric", back_populates="user", cascade="all, delete-orphan")
    ml_models = relationship("MLModel", back_populates="user", cascade="all, delete-orphan")
    user_erp_api = relationship("UserErpApi", back_populates="user", cascade="all, delete-orphan", uselist=False)


# Tables to create
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
    sku_order_url = Column(String(512), nullable=False)
    inventory_params_url = Column(String(512), nullable=False)
    distribution_routing_url = Column(String(512), nullable=False)
    sku_order_latest_url = Column(String(512), nullable=False)
    inventory_params_latest_url = Column(String(512),
                                         nullable=False)
    token_username = Column(String, nullable=False)

    # This field is automatically encrypted at write time and decrypted at read time.
    token_password = Column(
        EncryptedType(String, settings.secret_key, AesEngine, 'pkcs5'),
        nullable=False
    )

    # 1-to-1 relationship
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False, unique=True)

    user = relationship("LoginUser", back_populates="user_erp_api")
