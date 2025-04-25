"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: EKETA (CERTH) - Ι.ΜΕΤ. (HIT)
 * Contributor: Georgios Karanasios R&D Software Engineer (DOTSOFT)
 */
"""

import logging
from math import sqrt, ceil
from typing import Dict

from scipy.optimize import minimize
from scipy.stats import norm

from .inventory_service_interface import InventoryServiceInterface

logger = logging.getLogger(__name__)


class InventoryService(InventoryServiceInterface):

    def optimize_inventory(self, params: Dict) -> Dict:
        """
        Runs an inventory optimization routine based on various cost parameters
        and demand distributions. Returns JSON-friendly output.

        :param params: Dict: A dictionary containing the cost & demand parameters
        :return: Dict: Optimized order quantity (Q) and reorder point (R),
                  cost breakdown, total cost, and input parameters.
        """
        # 1) Extract variables from params
        lambda_ = params.get('lambda')  # Demand rate (units/time period)
        sigma = params.get('sigma')  # Std deviation of demand (units/time period)
        T = params.get('T')  # Time period
        K = params.get('K')  # Fixed order cost (€/order)
        p = params.get('p')  # Penalty cost per stockout unit (€/stockout)
        i = params.get('i')  # Holding cost rate (€/€/time period)
        c = params.get('c')  # Cost per unit (€/unit)
        FTL = params.get('FTL')  # Truckload capacity (units)
        TR = params.get('TR')  # Transportation cost (€/truckload)

        def total_cost(x):
            Q, R = x
            epsilon = 1e-5
            Q = max(Q, epsilon)  # Prevent divide-by-zero

            # 2) Number of orders
            num_orders = lambda_ / Q

            # 3) Calculate costs
            demand_std = sigma * sqrt(T)
            z = (R - lambda_ * T) / demand_std
            holding_cost = i * c * ((Q / 2) + demand_std * z)
            setup_cost_transport_cost = num_orders * (K + TR * ceil(Q / FTL))
            pdf_z = norm.pdf(z)
            cdf_z = norm.cdf(z)
            stockouts_per_cycle = demand_std * (pdf_z - z * (1 - cdf_z))
            stockout_cost = p * num_orders * stockouts_per_cycle

            total_costs = holding_cost + setup_cost_transport_cost + stockout_cost
            return total_costs, holding_cost, setup_cost_transport_cost, stockout_cost

        # 4) Minimization
        initial_guess = [500, 1000]
        bounds = [(1e-5, None), (0, None)]
        result = minimize(lambda x: total_cost(x)[0], initial_guess, method='SLSQP', bounds=bounds)

        final_costs, holding_cost, transport_setup, stockout_cost = total_cost(result.x)

        # 5) Prepare result
        output = {
            'optimized_values': {
                'Q': result.x[0],
                'R': result.x[1]
            },
            'cost_details': {
                'holding_cost': holding_cost,
                'setup_cost_and_transportation_cost': transport_setup,
                'stockout_cost': stockout_cost
            },
            'total_cost': final_costs,
            'parameters_used': params
        }

        logger.info(f"Inventory optimization result: {output}")
        return output
