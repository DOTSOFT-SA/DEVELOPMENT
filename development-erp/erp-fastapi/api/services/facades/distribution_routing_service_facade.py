"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

from typing import Dict

from ..location_development_service import LocationDevelopmentService
from ..route_development_service import RouteDevelopmentService
from ..vehicle_development_service import VehicleDevelopmentService
from ...models.page_criteria_models import PageParams, LocationDevelopmentCriteria, RouteDevelopmentCriteria, \
    VehicleDevelopmentCriteria


class DistributionRoutingServiceFacade:
    """
    Facade that collects data from location, route, and vehicle services
    to build a JSON model similar to create_data_model().
    """

    def __init__(
            self,
            location_service: LocationDevelopmentService,
            route_service: RouteDevelopmentService,
            vehicle_service: VehicleDevelopmentService
    ):
        self.location_service = location_service
        self.route_service = route_service
        self.vehicle_service = vehicle_service

    async def build_data_model(self) -> Dict:
        """
        Builds a data model that includes distance_matrix, traffic_factors, demands,
        vehicle_capacities, cost_per_trip_per_vehicle, num_vehicles, location_id/name and depot index.

        @return: A dictionary with the following keys:
                 - distance_matrix (List[List[float]])
                 - traffic_factors (List[List[float]])
                 - demands (List[int])
                 - vehicle_capacities (List[int])
                 - cost_per_trip_per_vehicle (List[float])
                 - num_vehicles (int)
                 - depot (int) -> index in the location array representing the depot
                 - location_data (List[Dict[str, Any]]): Metadata for each location, including:
                    - location_id (Optional[int]): Unique identifier of the location.
                    - location_name (Optional[str]): Name of the location.
        """

        # 1. Fetch all locations (with demands, is_depot, etc.)
        all_locations = await self.location_service.get_all_locations(
            page_params=PageParams(page=1, page_size=9999),
            criteria=LocationDevelopmentCriteria()
        )
        # Separate depot(s) from non-depots
        depot_locs = [loc for loc in all_locations if loc.is_depot]
        non_depot_locs = [loc for loc in all_locations if not loc.is_depot]
        if not depot_locs:
            raise ValueError("No depot found.")
        # Assume exactly one depot
        depot = depot_locs[0]
        # Sort the non-depots by location_id (optional)
        non_depot_locs = sorted(non_depot_locs, key=lambda loc: loc.location_id or float('inf'))
        # Final location list: depot is index=0, then others
        final_locations = [depot] + non_depot_locs
        # Now final_locations[0] is definitely the depot, so demands[0] = 0
        demands = [loc.demand if loc.demand else 0 for loc in final_locations]
        # Build a location_index_map based on final_locations
        location_index_map = {}
        for idx, loc in enumerate(final_locations):
            # Must have a location_id to map
            if loc.location_id is not None:
                location_index_map[loc.location_id] = idx
        # 2. Initialize distance_matrix and traffic_factors with 0's
        size = len(final_locations)
        distance_matrix = [[0.0] * size for _ in range(size)]
        traffic_factors = [[1.0] * size for _ in range(size)]
        # 3. Fetch all routes (with distance, traffic_factor, source/destination IDs)
        all_routes = await self.route_service.get_all_routes(
            page_params=PageParams(page=1, page_size=9999),
            criteria=RouteDevelopmentCriteria()
        )
        # Fill distance_matrix / traffic_factors
        for route in all_routes:
            src_id = route.source_location_id
            dst_id = route.destination_location_id
            if src_id in location_index_map and dst_id in location_index_map:
                i = location_index_map[src_id]
                j = location_index_map[dst_id]
                distance_matrix[i][j] = route.distance or 0.0
                traffic_factors[i][j] = route.traffic_factor or 1.0
        # 4. Fetch all vehicles
        all_vehicles = await self.vehicle_service.get_all_vehicles(
            page_params=PageParams(page=1, page_size=9999),
            criteria=VehicleDevelopmentCriteria()
        )
        # Extract capacities and cost_per_trip
        vehicle_capacities = [v.capacity if v.capacity else 0 for v in all_vehicles]
        cost_per_trip_per_vehicle = [v.cost_per_trip if v.cost_per_trip else 0 for v in all_vehicles]
        num_vehicles = len(all_vehicles)
        # 5. Build the final dictionary
        data = {
            "distance_matrix": distance_matrix,
            "traffic_factors": traffic_factors,
            "demands": demands,
            "vehicle_capacities": vehicle_capacities,
            "cost_per_trip_per_vehicle": cost_per_trip_per_vehicle,
            "num_vehicles": num_vehicles,
            "depot": 0  # Depot is explicitly set to index 0
        }
        # 6. Build location_data as a list of dictionaries with location_id and location_name
        location_data = [
            {"location_id": loc.location_id, "location_name": loc.location_name}
            for loc in final_locations
        ]
        data["location_data"] = location_data  # Add the new key to the data dictionary
        # Return the JSON input for the ML Algorithm
        return data
