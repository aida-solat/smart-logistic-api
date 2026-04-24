"""Tests for the risk-aware VRP (phase 4)."""
from __future__ import annotations

import numpy as np

from app.optimizer.vrp import solve_risk_aware_vrp


def _toy_instance():
    """5 customers + depot, symmetric distance matrix."""
    coords = np.array(
        [[0, 0], [2, 1], [4, 2], [1, 5], [5, 5], [3, 3]], dtype=float
    )
    diff = coords[:, None, :] - coords[None, :, :]
    D = np.linalg.norm(diff, axis=-1)
    demands = np.array([0, 2, 3, 2, 4, 1], dtype=int)  # depot=0
    capacities = [6, 6]  # 2 vehicles
    return D, demands, capacities


def test_risk_vrp_returns_valid_routes():
    D, demands, caps = _toy_instance()
    res = solve_risk_aware_vrp(
        D, demands, caps, travel_cv=0.2, n_scenarios=50, alpha=0.9, seed=0,
    )
    # Every customer visited exactly once across routes; each route starts/ends at depot.
    visited = []
    for r in res.routes:
        assert r.nodes[0] == 0 and r.nodes[-1] == 0
        visited.extend(r.nodes[1:-1])
    assert sorted(visited) == [1, 2, 3, 4, 5]
    # Capacity respected
    for r in res.routes:
        load = sum(demands[n] for n in r.nodes)
        assert load <= caps[r.vehicle]


def test_risk_vrp_cvar_ge_mean_ge_var():
    D, demands, caps = _toy_instance()
    res = solve_risk_aware_vrp(
        D, demands, caps, travel_cv=0.3, n_scenarios=300, alpha=0.9, seed=0,
    )
    # By definition: mean <= VaR_α <= CVaR_α (for α well above 0.5).
    assert res.mean_makespan <= res.var_makespan + 1e-6
    assert res.var_makespan <= res.cvar_makespan + 1e-6


def test_joint_inventory_routing():
    """Joint pipeline returns both inventory and routing decisions."""
    from app.optimizer.joint import joint_inventory_routing

    D, demands, caps = _toy_instance()
    N = 3  # 3 warehouses for inventory step
    rng = np.random.default_rng(0)
    scenarios = rng.normal(loc=[30.0, 60.0, 40.0], scale=[5, 15, 8], size=(200, N))
    transport = np.ones((N, N)) - np.eye(N)

    out = joint_inventory_routing(
        initial_stock=np.array([100.0, 20.0, 60.0]),
        demand_scenarios=scenarios,
        transport_cost=transport,
        customer_distance_matrix=D,
        customer_demands=demands,
        vehicle_capacities=caps,
        stockout_penalty=20.0,
        alpha=0.9,
        n_vrp_scenarios=50,
    )
    assert "inventory" in out and "routing" in out
    assert out["joint_objective"]["alpha"] == 0.9
    assert len(out["routing"]["routes"]) == len(caps)
    assert out["inventory"]["solver_status"] == "optimal"


def test_risk_vrp_endpoint(client):
    D, demands, caps = _toy_instance()
    body = {
        "distance_matrix": D.tolist(),
        "demands": demands.tolist(),
        "vehicle_capacities": caps,
        "travel_cv": 0.2,
        "n_scenarios": 50,
        "alpha": 0.9,
        "time_limit_s": 5,
    }
    r = client.post("/optimize/risk-vrp", json=body)
    assert r.status_code == 200, r.text
    out = r.json()
    assert len(out["routes"]) == 2
    assert out["n_scenarios"] == 50
    assert out["cvar_makespan"] >= out["var_makespan"] - 1e-6
