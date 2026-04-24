"""A/B validation loop: simulate baseline vs optimizer decision.

Given a CVaR reallocation (or any stock override), this module runs the
SimPy digital twin twice — once with the baseline stock, once with the
optimizer-modified stock — and reports the empirical uplift on every KPI.

This closes the causal → optimize → simulate → audit loop: no decision
leaves the system without an offline backtest.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from app.simulator.twin import WarehouseConfig, monte_carlo

logger = logging.getLogger(__name__)


def _apply_allocation(
    warehouses: list[WarehouseConfig], allocation: list[list[float]]
) -> dict:
    """Apply an N×N reallocation matrix to the initial stock and return overrides.

    Convention: ``allocation[i][j]`` is the quantity moved from warehouse ``i``
    to warehouse ``j``. Diagonal entries stay put.
    """
    N = len(warehouses)
    A = np.asarray(allocation, dtype=float)
    if A.shape != (N, N):
        raise ValueError(
            f"allocation must be {N}×{N}, got {A.shape}."
        )
    # Net: out-flow = row sum, in-flow = col sum (excluding diagonal).
    off = A.copy()
    np.fill_diagonal(off, 0.0)
    outflow = off.sum(axis=1)
    inflow = off.sum(axis=0)
    new_stock = {
        w.name: float(max(0.0, w.initial_stock - outflow[i] + inflow[i]))
        for i, w in enumerate(warehouses)
    }
    return new_stock


def validate_decision(
    warehouses: list[WarehouseConfig],
    allocation: Optional[list[list[float]]] = None,
    stock_override: Optional[dict] = None,
    horizon: float = 168.0,
    n_replications: int = 30,
    seed: int = 0,
) -> dict:
    """Run baseline + decision simulations and return the uplift.

    Exactly one of ``allocation`` or ``stock_override`` must be provided.
    """
    if (allocation is None) == (stock_override is None):
        raise ValueError("Provide exactly one of 'allocation' or 'stock_override'.")

    if allocation is not None:
        stock_override = _apply_allocation(warehouses, allocation)

    baseline = monte_carlo(
        warehouses, horizon=horizon, n_replications=n_replications, seed=seed
    )
    decision = monte_carlo(
        warehouses,
        horizon=horizon,
        n_replications=n_replications,
        seed=seed,
        initial_stock_override=stock_override,
    )

    def delta(key: str) -> dict:
        b = baseline["aggregated"][key]["mean"]
        d = decision["aggregated"][key]["mean"]
        rel = (d - b) / b if abs(b) > 1e-9 else float("nan")
        return {"baseline": b, "decision": d, "absolute": d - b, "relative": rel}

    keys = [
        "service_level", "mean_lead_time", "p95_lead_time", "p99_lead_time",
        "transport_cost", "stockout_cost", "total_cost",
        "n_stockouts", "total_units_shorted",
    ]
    uplift = {k: delta(k) for k in keys}

    # Signal: is the decision an improvement overall?
    improves = (
        uplift["service_level"]["decision"] >= uplift["service_level"]["baseline"]
        and uplift["total_cost"]["decision"] <= uplift["total_cost"]["baseline"]
    )

    return {
        "stock_override": stock_override,
        "baseline_aggregated": baseline["aggregated"],
        "decision_aggregated": decision["aggregated"],
        "uplift": uplift,
        "pareto_improvement": improves,
        "horizon": horizon,
        "n_replications": n_replications,
    }
