"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class InventoryOptimizationDto:
    id: int
    sku_number: int
    sku_name: str  # extra field
    order_quantity_q: float
    reorder_point_r: float
    holding_cost: float
    setup_transportation_cost: float
    stockout_cost: float
    total_cost: float
    order_frequency: float
    cycle_time: float
    is_custom: bool
    updated_at: datetime
    inventory_record_id: Optional[int]
    user_id: int


@dataclass
class InventoryOptimizationRequest:
    """
    DTO for passing inventory optimization inputs.
    Can either include inventory parameters (provided by user) or fetch them from ERP.
    """
    sku_number: int
    user_id: int
    inventory_params: Optional[Dict[str, Any]] = None  # Can be None if using ERP values


@dataclass
class InventoryServiceResponse:
    """
    Holds the output from running the inventory optimization,
    including both the computed optimization_result
    and the inventory_params fetched from ERP.
    """
    inventory_params: Dict[str, Any]
    inventory_optimization_dto: InventoryOptimizationDto
