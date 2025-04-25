"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: EKETA (CERTH) - Ι.ΜΕΤ. (HIT)
 * Contributor: Georgios Karanasios R&D Software Engineer (DOTSOFT)
 */
"""

import logging
from typing import List

from ortools.linear_solver import pywraplp

from .distribution_optimization_with_traffic_service_interface import \
    DistributionOptimizationWithTrafficServiceInterface
from ..models.distribution_optimization import DistributionOptimization

logger = logging.getLogger(__name__)


class DistributionOptimizationWithTrafficService(DistributionOptimizationWithTrafficServiceInterface):
    """
    Concrete service applying an OR-Tools solver to find minimal-cost
    routing solutions considering traffic factors.
    """

    def get_distribution_optimizations(self, user_id: int, data: dict) -> List[DistributionOptimization]:
        """
        Performs distribution optimization with traffic adjustments.

        :param user_id: int: The ID of the user requesting the optimization.
        :param data: dict: Input data including distance matrix, demands, and vehicle capacities.
        :return: List[DistributionOptimization]: A list of DistributionOptimization objects
                 corresponding to each route in the solution.
                 If the solver returns no feasible solution, an empty list is returned.
        """
        solution = self._get_distribution_optimization_with_traffic(data)
        if not solution:
            return []
        # Extract total_cost, route details
        total_cost = solution['total_cost']
        route_list = solution['results']
        location_data = data.get('location_data', [])  # array of {location_id, location_name}
        # Convert route_list into distribution_optimization records
        distribution_records = self._convert_to_distribution_optimizations(
            user_id, total_cost, route_list, location_data
        )
        # Return records
        return distribution_records

    @staticmethod
    def _get_distribution_optimization_with_traffic(data: dict) -> dict:
        """
        Runs an OR-Tools integer linear program for multi-vehicle routing with traffic factors.

        :param data: dict: Input data containing distance matrix, vehicle capacities, and traffic factors.
        :return: dict: A dictionary with 'total_cost' (float) and 'results' (list of routes) or an empty dict if infeasible.
        """
        num_nodes = len(data['distance_matrix'])
        num_vehicles = data['num_vehicles']
        depot = data['depot']
        # Create the solver.
        solver = pywraplp.Solver.CreateSolver('SCIP')
        # Variables for flows from depot to nodes and between nodes
        x = {}
        for k in range(num_vehicles):
            for i in range(num_nodes):
                for j in range(num_nodes):
                    if i != j:
                        x[(i, j, k)] = solver.IntVar(0, data['vehicle_capacities'][k], f'x[{i},{j},{k}]')
        # Objective: Minimize the total cost of transportation, adjusted for traffic
        solver.Minimize(solver.Sum(
            data['cost_per_trip_per_vehicle'][k] * x[(i, j, k)] * data['distance_matrix'][i][j] *
            data['traffic_factors'][i][j]
            for i in range(num_nodes) for j in range(num_nodes) for k in range(num_vehicles) if i != j))
        # Capacity constraints for each vehicle
        for k in range(num_vehicles):
            solver.Add(solver.Sum(x[(i, j, k)] for i in range(num_nodes) for j in range(num_nodes) if i != j)
                       <= data['vehicle_capacities'][k])
        # Demand fulfillment for each node
        for j in range(1, num_nodes):
            solver.Add(solver.Sum(x[(i, j, k)] for i in range(num_nodes) for k in range(num_vehicles) if i != j)
                       == data['demands'][j])
        # Routing constraint: all loaded trips must start from the depot
        for k in range(num_vehicles):
            for j in range(1, num_nodes):
                solver.Add(solver.Sum(x[(j, i, k)] for i in range(num_nodes) if i != j)
                           <= x[(depot, j, k)])
        # Solve the problem
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            # print(f'Total cost = {solver.Objective().Value()}')
            results = []
            for k in range(num_vehicles):
                for i in range(num_nodes):
                    for j in range(num_nodes):
                        if i != j and x[(i, j, k)].solution_value() > 0:
                            # print(f'Vehicle {k} transports {x[(i, j, k)].solution_value()} units from {i} to {j}')
                            results.append({
                                'vehicle': k,
                                'from': i,
                                'to': j,
                                'units': x[(i, j, k)].solution_value()
                            })
            return {
                'total_cost': solver.Objective().Value(),
                'results': results
            }
        else:
            return {}

    @staticmethod
    def _convert_to_distribution_optimizations(
            user_id: int, total_cost: float, route_list: list, location_data: list
    ) -> List[DistributionOptimization]:
        """
        Takes a list of route dicts (vehicle, from, to, units)
        plus the final total_cost, converts them into
        DistributionOptimization model objects.

        :param user_id: int: The ID of the user requesting the optimization.
        :param total_cost: float: The computed total cost from the solver.
        :param route_list: list: The optimized routes as dictionaries.
        :param location_data: list: Includes locations ids and names
        :return: List[DistributionOptimization]: A list of DistributionOptimization objects.
        """
        # Build a quick lookup: {location_id: location_name}
        location_map = {
            loc["location_id"]: loc["location_name"]
            for loc in location_data
        }

        distribution_models = []
        for route in route_list:
            start_id = route['from']
            dest_id = route['to']

            dist_opt = DistributionOptimization(
                total_cost=total_cost,
                vehicle_id=route['vehicle'],
                start_location_name=location_map[start_id],
                destination_location_name=location_map[dest_id],
                units=route['units'],
                user_id=user_id  # set the user foreign key by ID
            )
            distribution_models.append(dist_opt)

        return distribution_models
