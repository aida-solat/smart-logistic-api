"""Tests for the SimPy digital twin (phase 3)."""
from __future__ import annotations

import pytest

from app.simulator.twin import WarehouseConfig, monte_carlo, run_simulation


def _cfgs():
    return [
        WarehouseConfig(
            name="A", initial_stock=500, arrival_rate=2.0,
            units_per_order_mean=1.5, units_per_order_std=0.3,
            service_time_mean=0.5, shipping_mu=1.0, shipping_sigma=0.4,
        ),
        WarehouseConfig(
            name="B", initial_stock=50, arrival_rate=3.0,
            units_per_order_mean=1.5, units_per_order_std=0.3,
            service_time_mean=0.5, shipping_mu=1.2, shipping_sigma=0.6,
        ),
    ]


def test_single_run_produces_kpis():
    out = run_simulation(_cfgs(), horizon=48.0, seed=1)
    assert out["n_orders"] > 0
    assert 0.0 <= out["service_level"] <= 1.0
    assert out["total_cost"] >= 0
    assert "final_stock" in out


def test_understocked_warehouse_has_stockouts():
    out = run_simulation(_cfgs(), horizon=48.0, seed=1)
    # Warehouse B is tiny relative to its arrival rate -> expect stockouts.
    assert out["n_stockouts"] > 0
    assert out["total_units_shorted"] > 0


def test_monte_carlo_aggregates_tails():
    mc = monte_carlo(_cfgs(), horizon=48.0, n_replications=10, seed=2)
    agg = mc["aggregated"]
    assert "service_level" in agg
    assert agg["service_level"]["p5"] <= agg["service_level"]["p95"]
    assert mc["n_replications"] == 10


def test_stock_override_improves_service_level():
    """Reallocating stock toward the risky warehouse should raise service level."""
    base = monte_carlo(_cfgs(), horizon=48.0, n_replications=15, seed=3)
    improved = monte_carlo(
        _cfgs(),
        horizon=48.0,
        n_replications=15,
        seed=3,
        initial_stock_override={"A": 300, "B": 250},  # move 200 from A to B
    )
    base_sl = base["aggregated"]["service_level"]["mean"]
    improved_sl = improved["aggregated"]["service_level"]["mean"]
    assert improved_sl >= base_sl - 1e-6


def test_validate_decision_detects_improvement():
    """Moving stock from over- to under-stocked warehouse must improve service level."""
    from app.simulator.validate import validate_decision

    out = validate_decision(
        _cfgs(),
        allocation=[[0.0, 200.0], [0.0, 0.0]],  # move 200 A -> B
        horizon=48.0,
        n_replications=10,
        seed=7,
    )
    assert out["pareto_improvement"] is True
    assert out["stock_override"] == {"A": 300.0, "B": 250.0}
    sl = out["uplift"]["service_level"]
    assert sl["decision"] >= sl["baseline"]


def test_validate_endpoint_requires_one_of_allocation_or_override(client):
    body = {
        "warehouses": [
            {
                "name": "A", "initial_stock": 500, "arrival_rate": 2.0,
                "units_per_order_mean": 1.5, "units_per_order_std": 0.3,
                "service_time_mean": 0.5, "shipping_mu": 1.0, "shipping_sigma": 0.4,
            },
        ],
        "horizon": 12.0, "n_replications": 3,
    }  # neither allocation nor stock_override → 422
    r = client.post("/simulate/validate", json=body)
    assert r.status_code == 422, r.text


def test_simulate_endpoint(client):
    body = {
        "warehouses": [
            {
                "name": "A", "initial_stock": 500, "arrival_rate": 2.0,
                "units_per_order_mean": 1.5, "units_per_order_std": 0.3,
                "service_time_mean": 0.5, "shipping_mu": 1.0, "shipping_sigma": 0.4,
            },
            {
                "name": "B", "initial_stock": 50, "arrival_rate": 3.0,
                "units_per_order_mean": 1.5, "units_per_order_std": 0.3,
                "service_time_mean": 0.5, "shipping_mu": 1.2, "shipping_sigma": 0.6,
            },
        ],
        "horizon": 24.0,
        "n_replications": 5,
    }
    r = client.post("/simulate/network", json=body)
    assert r.status_code == 200, r.text
    out = r.json()
    assert "aggregated" in out
    assert out["n_replications"] == 5
