"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from dataclasses import dataclass
from typing import List


@dataclass
class RouteDto:
    """
    Represents a single route leg in the optimization solution
    (omitting total_cost, which is stored once at the top-level).
    """
    vehicle_id: int
    start_location_name: str
    destination_location_name: str
    units: float


@dataclass
class DistributionRoutingDto:
    """
    Collects the top-level total_cost plus a list of route segments.
    """
    total_cost: float
    routes: List[RouteDto]
