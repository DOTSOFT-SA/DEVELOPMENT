"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from utils.settings import settings

Base = declarative_base()


class LoginUserORM(Base):
    __tablename__ = "login_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    last_login = Column(TIMESTAMP, nullable=True)

    user_erp_api = relationship("UserErpApiORM", back_populates="user", uselist=False, cascade="all, delete-orphan")


class SkuMetricORM(Base):
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
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    sku_order_record_id = Column(Integer, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('login_user.id'), nullable=False)


class UserErpApiORM(Base):
    __tablename__ = 'user_erp_api'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String, nullable=False, unique=True)
    login_token_url = Column(String(512), nullable=False)
    sku_order_url = Column(String(512), nullable=False)
    inventory_params_url = Column(String(512), nullable=False)
    distribution_routing_url = Column(String(512), nullable=False)
    sku_order_latest_url = Column(String(512), nullable=False)
    inventory_params_latest_url = Column(String(512), nullable=False)
    token_username = Column(String, nullable=False)
    token_password = Column(
        EncryptedType(String, settings.secret_key, AesEngine, 'pkcs5'),
        nullable=False
    )
    user_id = Column(Integer, ForeignKey('login_user.id', ondelete="CASCADE"), nullable=False, unique=True)

    user = relationship("LoginUserORM", back_populates="user_erp_api")
