"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: Optional[int] = Field(1, ge=1)  # greater than (ge 1)
    page_size: Optional[int] = Field(default=None, ge=1)  # no limit on the default page size


class SkuOrderDevelopmentCriteria(BaseModel):
    """
    Define the filter criteria for SkuOrderDevelopment.
    Any field left as None means 'no filtering on that field'.
    """
    sku_number: Optional[int] = None
    sku_name: Optional[str] = None
    class_display_name: Optional[str] = None
    order_date: Optional[datetime] = None
    start_order_date: Optional[datetime] = None
    end_order_date: Optional[datetime] = None


class InventoryParamsCriteria(BaseModel):
    sku_number: Optional[int] = None


class VehicleDevelopmentCriteria(BaseModel):
    vehicle_id: Optional[int] = None


class LocationDevelopmentCriteria(BaseModel):
    location_id: Optional[int] = None
    location_name: Optional[str] = None


class RouteDevelopmentCriteria(BaseModel):
    route_id: Optional[int] = None
