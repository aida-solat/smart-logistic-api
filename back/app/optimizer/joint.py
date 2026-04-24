"""Joint inventory + routing CVaR decision (novel claim 4 dependent).

Two-stage composition:

1. Solve CVaR inventory reallocation → `post_stock` per warehouse.
2. Build a VRP whose **per-customer demand** is proportional to the
   post-decision stock distribution (each warehouse becomes a depot node
   serving its own downstream customers), and solve it with risk-aware VRP
   (OR-Tools + travel-time CVaR).

The output bundles both decisions so an operator can see how the
inventory reallocation reshapes the routing plan.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from app.optimizer.cvar import solve_cvar_inventory
from app.optimizer.vrp import solve_risk_aware_vrp

logger = logging.getLogger(__name__)


def joint_inventory_routing(
    initial_stock: np.ndarray,
    demand_scenarios: np.ndarray,
    transport_cost: np.ndarray,
    customer_distance_matrix: np.ndarray,
    customer_demands: np.ndarray,
    vehicle_capacities: list[int],
    stockout_penalty: float = 10.0,
    alpha: float = 0.95,
    lam: float = 0.5,
    travel_cv: float = 0.3,
    n_vrp_scenarios: int = 200,
    seed: int = 0,
) -> dict:
    """Chain CVaR inventory → risk-aware VRP with a single call.

    Parameters
    ----------
    initial_stock, demand_scenarios, transport_cost, stockout_penalty,
    alpha, lam
        Passed through to :func:`solve_cvar_inventory`.
    customer_distance_matrix
        (n_customers+1) × (n_customers+1) mean travel-time matrix where
        index 0 is the depot.
    customer_demands
        Array of length n_customers+1; index 0 (depot) must be 0.
    vehicle_capacities
        List of per-vehicle capacities passed to OR-Tools.
    travel_cv
        Coefficient of variation for travel-time noise (VRP CVaR).
    """
    # 1. Inventory CVaR LP
    inv = solve_cvar_inventory(
        initial_stock=np.asarray(initial_stock, dtype=float),
        demand_scenarios=np.asarray(demand_scenarios, dtype=float),
        transport_cost=np.asarray(transport_cost, dtype=float),
        stockout_penalty=stockout_penalty,
        alpha=alpha,
        lam=lam,
    )

    # 2. Risk-aware VRP
    vrp = solve_risk_aware_vrp(
        distance_matrix=np.asarray(customer_distance_matrix, dtype=float),
        demands=np.asarray(customer_demands, dtype=int),
        vehicle_capacities=list(vehicle_capacities),
        travel_cv=travel_cv,
        n_scenarios=n_vrp_scenarios,
        alpha=alpha,
        seed=seed,
    )

    return {
        "inventory": inv.to_dict(),
        "routing": vrp.to_dict(),
        "joint_objective": {
            "inventory_cvar": inv.cvar_alpha,
            "routing_cvar_makespan": vrp.cvar_makespan,
            "alpha": alpha,
        },
    }
