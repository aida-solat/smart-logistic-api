"""Risk-aware Vehicle Routing Problem (phase 4).

Pipeline
--------
1. **Base solution** — solve a deterministic CVRP with OR-Tools using the
   mean travel-time matrix. Returns one route per vehicle plus the mean
   completion time.
2. **Stochastic scoring** — resample travel-times from a user-supplied
   distribution (LogNormal by default), re-evaluate each route's completion
   time, and aggregate an empirical **CVaR_α** of the makespan.
3. **Risk signal** — the endpoint returns both the deterministic plan and
   the empirical risk distribution, so the caller can trade off expected
   duration vs tail risk.

This separation (optimize deterministic + evaluate stochastic) is the
typical two-stage heuristic used when the pure stochastic CVRP-CVaR is
combinatorially too expensive. It gives a clean recipe: *"a method
for producing risk-aware routing decisions by solving a mean-time CVRP and
scoring candidate routes via Monte-Carlo CVaR of travel-time scenarios."*
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VRPRoute:
    vehicle: int
    nodes: list[int]           # sequence of node indices (0 = depot)
    mean_duration: float


@dataclass
class RiskAwareVRPResult:
    routes: list[VRPRoute]
    mean_makespan: float
    makespan_samples: list[float]  # per-scenario makespan (max over vehicles)
    cvar_makespan: float
    var_makespan: float
    alpha: float
    n_scenarios: int

    def to_dict(self) -> dict:
        return {
            "routes": [
                {"vehicle": r.vehicle, "nodes": r.nodes, "mean_duration": r.mean_duration}
                for r in self.routes
            ],
            "mean_makespan": self.mean_makespan,
            "cvar_makespan": self.cvar_makespan,
            "var_makespan": self.var_makespan,
            "alpha": self.alpha,
            "n_scenarios": self.n_scenarios,
            "makespan_samples": self.makespan_samples,
        }


def _solve_cvrp_ortools(
    distance_matrix: np.ndarray,
    demands: np.ndarray,
    vehicle_capacities: list[int],
    depot: int = 0,
    time_limit_s: int = 10,
) -> list[list[int]]:
    """Solve CVRP via OR-Tools, return routes as lists of node indices."""
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2

    n = distance_matrix.shape[0]
    n_vehicles = len(vehicle_capacities)
    mgr = pywrapcp.RoutingIndexManager(n, n_vehicles, depot)
    routing = pywrapcp.RoutingModel(mgr)

    # Scale to ints (OR-Tools wants ints).
    scale = 1000
    dist_int = np.round(distance_matrix * scale).astype(int)

    def dist_cb(from_idx, to_idx):
        f = mgr.IndexToNode(from_idx)
        t = mgr.IndexToNode(to_idx)
        return int(dist_int[f, t])

    transit_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    def demand_cb(from_idx):
        return int(demands[mgr.IndexToNode(from_idx)])

    demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(
        demand_idx, 0, list(vehicle_capacities), True, "Capacity"
    )

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    params.time_limit.seconds = time_limit_s

    solution = routing.SolveWithParameters(params)
    if solution is None:
        raise RuntimeError("OR-Tools CVRP solver found no solution")

    routes: list[list[int]] = []
    for v in range(n_vehicles):
        idx = routing.Start(v)
        route = []
        while not routing.IsEnd(idx):
            route.append(mgr.IndexToNode(idx))
            idx = solution.Value(routing.NextVar(idx))
        route.append(mgr.IndexToNode(idx))  # end = depot
        routes.append(route)
    return routes


def _route_duration(route: list[int], matrix: np.ndarray) -> float:
    total = 0.0
    for a, b in zip(route[:-1], route[1:]):
        total += float(matrix[a, b])
    return total


def _sample_travel_scenarios(
    mean: np.ndarray, cv: float, n_scenarios: int, seed: int
) -> np.ndarray:
    """LogNormal-multiplicative noise on travel times.

    ``cv`` = coefficient of variation (std / mean) applied per edge.
    Returns shape ``(n_scenarios, n, n)``.
    """
    rng = np.random.default_rng(seed)
    sigma = np.sqrt(np.log(1.0 + cv ** 2))
    mu = -0.5 * sigma ** 2  # so E[multiplier] = 1
    n = mean.shape[0]
    mult = rng.lognormal(mean=mu, sigma=sigma, size=(n_scenarios, n, n))
    return mean[None, :, :] * mult


def solve_risk_aware_vrp(
    distance_matrix: np.ndarray,
    demands: np.ndarray,
    vehicle_capacities: list[int],
    travel_cv: float = 0.3,
    n_scenarios: int = 200,
    alpha: float = 0.95,
    depot: int = 0,
    time_limit_s: int = 10,
    seed: int = 0,
) -> RiskAwareVRPResult:
    """Solve CVRP and evaluate makespan tail risk under travel-time noise.

    Parameters
    ----------
    distance_matrix
        Shape ``(n, n)``. Mean travel time (or distance) between each pair.
    demands
        Shape ``(n,)``. Integer demand at each node; depot's demand is 0.
    vehicle_capacities
        List of integer vehicle capacities; one vehicle per element.
    travel_cv
        Coefficient of variation for the per-edge travel-time noise
        (LogNormal, multiplicative). ``0.3`` = 30% CV.
    n_scenarios
        Number of Monte-Carlo scenarios used to compute CVaR of makespan.
    alpha
        CVaR tail level.
    """
    distance_matrix = np.asarray(distance_matrix, dtype=float)
    demands = np.asarray(demands, dtype=int)
    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        raise ValueError("distance_matrix must be square")
    n = distance_matrix.shape[0]
    if demands.shape[0] != n:
        raise ValueError("demands length must match distance_matrix size")

    # 1. Deterministic CVRP.
    raw_routes = _solve_cvrp_ortools(
        distance_matrix, demands, vehicle_capacities, depot=depot,
        time_limit_s=time_limit_s,
    )
    routes = [
        VRPRoute(
            vehicle=v,
            nodes=r,
            mean_duration=_route_duration(r, distance_matrix),
        )
        for v, r in enumerate(raw_routes)
    ]

    # 2. Monte-Carlo scoring: makespan = max across vehicles per scenario.
    scenarios = _sample_travel_scenarios(distance_matrix, travel_cv, n_scenarios, seed)
    makespans = np.empty(n_scenarios, dtype=float)
    for s in range(n_scenarios):
        M = scenarios[s]
        per_vehicle = [_route_duration(r.nodes, M) for r in routes]
        makespans[s] = max(per_vehicle) if per_vehicle else 0.0

    var_alpha = float(np.quantile(makespans, alpha))
    tail = makespans[makespans >= var_alpha]
    cvar_alpha = float(tail.mean()) if tail.size else var_alpha

    return RiskAwareVRPResult(
        routes=routes,
        mean_makespan=float(makespans.mean()),
        makespan_samples=makespans.tolist(),
        cvar_makespan=cvar_alpha,
        var_makespan=var_alpha,
        alpha=alpha,
        n_scenarios=n_scenarios,
    )
