"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class SkuOrderDevelopment(BaseModel):
    id: int
    sku_number: Optional[int]
    sku_name: Optional[str]
    review_count: Optional[float]
    review_score: Optional[float]
    class_display_name: Optional[str]
    sku_short_description: Optional[str]
    order_item_price_in_main_currency: Optional[float]
    order_item_unit_count: Optional[int]
    order_date: Optional[datetime]
    product_cost: Optional[float]
    cl_price: Optional[float]
    price_date: Optional[date]

    class Config:
        from_attributes = True


class InventoryParamsDevelopment(BaseModel):
    id: int
    sku_number: Optional[int]
    stock_level: Optional[int]
    time_period_t: Optional[float]
    fixed_order_cost_k: Optional[float]
    unit_cost_c: Optional[float]
    penalty_cost_p: Optional[float]
    holding_cost_rate_i: Optional[float]
    truckload_capacity_ftl: Optional[float]
    transportation_cost_tr: Optional[float]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class VehicleDevelopment(BaseModel):
    id: int
    vehicle_id: Optional[int]
    capacity: Optional[int]
    cost_per_trip: Optional[float]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class LocationDevelopment(BaseModel):
    id: int
    location_id: Optional[int]
    location_name: str
    demand: Optional[int]
    is_depot: Optional[bool]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class RouteDevelopment(BaseModel):
    id: int
    route_id: Optional[int]
    distance: Optional[float]
    traffic_factor: Optional[float]
    source_location_id: Optional[int]
    destination_location_id: Optional[int]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
