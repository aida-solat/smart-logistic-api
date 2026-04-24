"""Adaptive β calibration — learn the penalty-sensitivity from history.

The novel claim treats β as a user knob that maps a causal delay-shift
to a CVaR penalty adjustment. In practice we don't want the operator to
pick β by hand forever. This module learns β from a log of past runs in
which the realized stockout cost is observed after deployment.

Minimal model
-------------
We store rows of the form::

    (delay_shift, base_penalty, realized_stockout_cost, decision_cost)

and fit β via one-dimensional OLS on the linear model

    realized_cost / baseline_cost  ≈  1 + β · delay_shift

Both inputs and outputs are scalars so a trivial closed-form solution
suffices — no external solver needed. We expose the learner as a pure
function for tests and an MLflow-logged wrapper for production.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_LOG = Path(__file__).resolve().parents[2] / "data" / "beta_calibration.jsonl"


@dataclass
class BetaFit:
    beta: float
    n_observations: int
    r_squared: float
    residual_std: float


def fit_beta(
    delay_shifts: np.ndarray,
    cost_ratios: np.ndarray,
) -> BetaFit:
    """Closed-form OLS of ``cost_ratio - 1 = β · delay_shift``.

    We force the intercept to 1 (the identity transform under zero delay
    shift), which matches the penalty rule.
    """
    x = np.asarray(delay_shifts, dtype=float)
    y = np.asarray(cost_ratios, dtype=float) - 1.0
    n = len(x)
    if n < 2:
        raise ValueError("Need at least 2 observations to fit β.")
    denom = float((x * x).sum())
    if denom < 1e-12:
        raise ValueError("All delay_shifts are ~0; β is unidentified.")
    beta = float((x * y).sum() / denom)
    y_pred = beta * x
    ss_res = float(((y - y_pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return BetaFit(
        beta=beta, n_observations=n, r_squared=r2, residual_std=float(np.sqrt(ss_res / n))
    )


def record_observation(
    delay_shift: float,
    baseline_cost: float,
    decision_cost: float,
    meta: Optional[dict] = None,
    path: Optional[Path] = None,
) -> None:
    """Append one post-deployment observation to the calibration log."""
    p = Path(path) if path else DEFAULT_LOG
    p.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "delay_shift": float(delay_shift),
        "baseline_cost": float(baseline_cost),
        "decision_cost": float(decision_cost),
        "cost_ratio": float(decision_cost) / max(1e-9, float(baseline_cost)),
        "meta": meta or {},
    }
    with p.open("a") as f:
        f.write(json.dumps(row) + "\n")


def load_observations(path: Optional[Path] = None) -> List[dict]:
    """Return all recorded observations, or [] if the log does not exist."""
    p = Path(path) if path else DEFAULT_LOG
    if not p.exists():
        return []
    rows: List[dict] = []
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def calibrate_from_log(path: Optional[Path] = None) -> BetaFit:
    """Load the calibration log and fit β."""
    p = Path(path) if path else DEFAULT_LOG
    if not p.exists():
        raise FileNotFoundError(f"No calibration log at {p}.")
    rows: List[dict] = []
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    shifts = np.array([r["delay_shift"] for r in rows])
    ratios = np.array([r["cost_ratio"] for r in rows])
    return fit_beta(shifts, ratios)
