"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from sqlalchemy import Column, Integer, Text, Date, Double, DateTime, Boolean, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SkuOrderDevelopmentORM(Base):
    __tablename__ = "sku_order_development"

    id = Column(Integer, primary_key=True, index=True)
    sku_number = Column(Integer, nullable=True)
    sku_name = Column(Text, nullable=True)
    review_count = Column(Double, nullable=True)
    review_score = Column(Double, nullable=True)
    class_display_name = Column(Text, nullable=True)
    sku_short_description = Column(Text, nullable=True)
    order_item_price_in_main_currency = Column(Double, nullable=True)
    order_item_unit_count = Column(Integer, nullable=True)
    order_date = Column(DateTime, nullable=True)
    product_cost = Column(Double, nullable=True)
    cl_price = Column(Double, nullable=True)
    price_date = Column(Date, nullable=True)


class InventoryParamsDevelopmentORM(Base):
    __tablename__ = "inventory_params_development"

    id = Column(Integer, primary_key=True, index=True)
    stock_level = Column(Integer, nullable=True)
    sku_number = Column(Integer, nullable=True)
    time_period_t = Column(Double, nullable=True)
    fixed_order_cost_k = Column(Double, nullable=True)
    unit_cost_c = Column(Double, nullable=True)
    penalty_cost_p = Column(Double, nullable=True)
    holding_cost_rate_i = Column(Double, nullable=True)
    truckload_capacity_ftl = Column(Double, nullable=True)
    transportation_cost_tr = Column(Double, nullable=True)
    created_at = Column(DateTime, nullable=True)


class VehicleDevelopmentORM(Base):
    __tablename__ = "vehicle_development"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, nullable=True, unique=True)
    capacity = Column(Integer, nullable=True)
    cost_per_trip = Column(Double, nullable=True)
    created_at = Column(DateTime, nullable=True)


class LocationDevelopmentORM(Base):
    __tablename__ = "location_development"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, nullable=True, unique=True)
    location_name = Column(String(255), nullable=True, unique=True)
    demand = Column(Integer, nullable=True)
    is_depot = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True)


class RouteDevelopmentORM(Base):
    __tablename__ = "route_development"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, nullable=True, unique=True)
    distance = Column(Double, nullable=True)
    traffic_factor = Column(Double, nullable=True)
    source_location_id = Column(Integer, ForeignKey("location_development.location_id", ondelete="CASCADE"),
                                nullable=True)
    destination_location_id = Column(Integer, ForeignKey("location_development.location_id", ondelete="CASCADE"),
                                     nullable=True)
    created_at = Column(DateTime, nullable=True)
