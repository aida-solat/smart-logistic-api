"""Causal → Optimizer integration (novel claim).

Combines the causal ATE estimate with the CVaR inventory optimizer:

1. Estimate the causal ATE of ``processing_time_days`` on ``delay_days``
   from the Olist panel.
2. Compute the expected delay shift produced by an intervention Δ (days) on
   processing time: ``Δ · ATE``.
3. Convert the delay shift into an **effective stockout penalty adjustment**
   used by the CVaR optimizer. The intuition: shorter expected delay → lower
   downstream penalty per stockout unit (customers wait less, SLA risk drops).

The concrete adjustment rule used here is a simple, auditable linear form:

    effective_penalty = base_penalty · (1 + β · expected_delay_shift)

where ``β`` is a user-supplied sensitivity (₁/day). This keeps the result
interpretable — the novel claim is the *pipeline*, not the specific
functional form, which can be swapped for any monotone mapping.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from app.causal.dataset import build_demand_panel, load_order_features
from app.causal.effects import estimate_counterfactual
from app.optimizer.cvar import solve_cvar_inventory
from app.optimizer.scenarios import bootstrap_from_history

logger = logging.getLogger(__name__)


def causal_informed_cvar(
    intervention_delta: float,
    base_stockout_penalty: float = 10.0,
    beta: float = 0.5,
    freq: str = "W",
    top_k: int = 5,
    stock_multiplier: float = 1.2,
    transport_cost_uniform: float = 1.0,
    alpha: float = 0.95,
    lam: float = 0.5,
    n_scenarios: int = 500,
    causal_sample_size: int = 5000,
    seed: int = 0,
) -> dict:
    """End-to-end causal-informed CVaR reallocation.

    Parameters
    ----------
    intervention_delta
        Proposed change to ``processing_time_days`` (days, negative = faster).
    base_stockout_penalty
        Baseline per-unit stockout penalty.
    beta
        Sensitivity of the stockout penalty to the causal delay shift
        (per day of delay change). ``0.5`` means a 1-day reduction in
        expected delay lowers the penalty by 50% of baseline (linearly).

    Returns
    -------
    dict
        A combined payload containing:
          * the causal estimate (ATE, CI, expected shift, narrative)
          * the optimizer solution (allocation, CVaR, objective)
          * the derived effective penalty
          * MLflow-logged provenance
    """
    # 1. Causal step
    features = load_order_features()
    if causal_sample_size and causal_sample_size < len(features):
        features = features.sample(n=causal_sample_size, random_state=seed)
    causal = estimate_counterfactual(
        features, intervention_delta=intervention_delta
    )
    delay_shift = causal["expected_outcome_shift"]  # typically negative if Δ<0

    # 2. Penalty adjustment (clipped to be positive)
    effective_penalty = max(
        0.01, base_stockout_penalty * (1.0 + beta * delay_shift)
    )

    # 3. Historical demand panel → bootstrap scenarios
    panel = build_demand_panel(freq=freq, top_k=top_k)
    means = panel.mean(axis=0).to_numpy()
    initial_stock = means * stock_multiplier
    N = panel.shape[1]
    transport = np.full((N, N), transport_cost_uniform)
    np.fill_diagonal(transport, 0.0)
    scenarios = bootstrap_from_history(panel, n_scenarios=n_scenarios, seed=seed)

    # 4. CVaR optimize with effective penalty
    cvar_res = solve_cvar_inventory(
        initial_stock=initial_stock,
        demand_scenarios=scenarios,
        transport_cost=transport,
        stockout_penalty=effective_penalty,
        alpha=alpha,
        lam=lam,
    )

    return {
        "causal": causal,
        "penalty_adjustment": {
            "base_stockout_penalty": base_stockout_penalty,
            "beta": beta,
            "expected_delay_shift": delay_shift,
            "effective_penalty": effective_penalty,
            "rule": "p_eff = p_base · (1 + β · Δ·ATE)",
        },
        "optimizer": cvar_res.to_dict(),
        "warehouses": panel.columns.tolist(),
        "historical_mean_demand": means.tolist(),
        "panel_shape": list(panel.shape),
    }
