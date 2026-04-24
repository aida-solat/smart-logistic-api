"""Tests for the CVaR inventory optimizer (phase 2)."""
from __future__ import annotations

import numpy as np
import pytest

from app.optimizer.cvar import solve_cvar_inventory
from app.optimizer.scenarios import parametric_demand


def _toy_problem(seed: int = 0):
    """Two warehouses, skewed demand: #0 has excess, #1 has shortfall risk."""
    initial_stock = np.array([100.0, 20.0])
    # Deterministic-ish demand: site 0 low, site 1 high with variance
    mean = np.array([30.0, 60.0])
    std = np.array([5.0, 15.0])
    D = parametric_demand(mean, std, n_scenarios=200, seed=seed)
    # Transport cost: symmetric, nonzero off-diagonal
    C = np.array([[0.0, 1.0], [1.0, 0.0]])
    return initial_stock, D, C


def test_parametric_demand_shape_and_nonneg():
    mean = np.array([10.0, 20.0, 5.0])
    std = np.array([1.0, 2.0, 0.5])
    D = parametric_demand(mean, std, n_scenarios=100, seed=1)
    assert D.shape == (100, 3)
    assert (D >= 0).all()


def test_cvar_reallocates_stock_toward_risky_warehouse():
    initial_stock, D, C = _toy_problem()
    res = solve_cvar_inventory(
        initial_stock=initial_stock,
        demand_scenarios=D,
        transport_cost=C,
        stockout_penalty=20.0,
        alpha=0.95,
        lam=0.5,
    )
    assert res.solver_status in ("optimal", "optimal_inaccurate")
    # Reallocation should move stock from #0 (excess) to #1 (risky).
    moved_0_to_1 = res.allocation[0, 1]
    moved_1_to_0 = res.allocation[1, 0]
    assert moved_0_to_1 > moved_1_to_0 + 1e-3
    # Post-stock at the risky site should exceed initial.
    assert res.post_stock[1] > initial_stock[1]
    # Flow conservation: sum of stock preserved.
    assert abs(res.post_stock.sum() - initial_stock.sum()) < 1e-6


def test_cvar_heavier_risk_aversion_increases_cvar_term_weight():
    """Higher alpha (more conservative tail) should not reduce post-stock at
    the risky warehouse compared to a risk-neutral solution."""
    initial_stock, D, C = _toy_problem()

    neutral = solve_cvar_inventory(
        initial_stock=initial_stock,
        demand_scenarios=D,
        transport_cost=C,
        stockout_penalty=20.0,
        alpha=0.95,
        lam=0.0,  # pure expected-cost
    )
    averse = solve_cvar_inventory(
        initial_stock=initial_stock,
        demand_scenarios=D,
        transport_cost=C,
        stockout_penalty=20.0,
        alpha=0.99,
        lam=1.0,  # pure CVaR
    )
    # Risk-averse decision reallocates at least as much to the risky site.
    assert averse.post_stock[1] >= neutral.post_stock[1] - 1e-6


def test_cvar_shape_validation():
    with pytest.raises(ValueError):
        solve_cvar_inventory(
            initial_stock=np.array([10.0, 20.0]),
            demand_scenarios=np.zeros((5, 3)),  # wrong width
            transport_cost=np.zeros((2, 2)),
        )


def test_cvar_inventory_endpoint(client):
    body = {
        "initial_stock": [100.0, 20.0],
        "transport_cost": [[0.0, 1.0], [1.0, 0.0]],
        "demand_mean": [30.0, 60.0],
        "demand_std": [5.0, 15.0],
        "n_scenarios": 100,
        "alpha": 0.95,
        "lam": 0.5,
        "stockout_penalty": 20.0,
    }
    r = client.post("/optimize/cvar-inventory", json=body)
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["solver_status"] in ("optimal", "optimal_inaccurate")
    assert len(out["allocation"]) == 2
    assert len(out["post_stock"]) == 2
    assert out["n_scenarios"] == 100
