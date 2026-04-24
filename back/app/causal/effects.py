"""Causal effect estimators (DoWhy-based).

Estimates the Average Treatment Effect (ATE) of a decision variable on a
logistics KPI using the DAG defined in :mod:`app.causal.graph`.

All runs are logged to MLflow (if reachable) as an immutable audit trail.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import numpy as np
import pandas as pd

from app.causal.graph import CONFOUNDERS, OUTCOME, TREATMENT, get_graph

logger = logging.getLogger(__name__)


def _log_to_mlflow(params: dict, metrics: dict, experiment: str = "causal") -> None:
    """Best-effort MLflow logging. Silently skips if server unreachable."""
    try:
        import mlflow

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment)
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics({k: float(v) for k, v in metrics.items() if v is not None})
    except Exception as exc:  # pragma: no cover - best effort
        logger.warning("MLflow logging skipped: %s", exc)


def estimate_ate(
    data: pd.DataFrame,
    treatment: str = TREATMENT,
    outcome: str = OUTCOME,
    confounders: Optional[list[str]] = None,
    method: str = "backdoor.linear_regression",
    refute: bool = True,
) -> dict:
    """Estimate the ATE of ``treatment`` on ``outcome`` via DoWhy.

    Parameters
    ----------
    data
        Tidy dataframe with treatment, outcome, and confounder columns.
    treatment, outcome
        Column names. Default to the phase-1 decision problem.
    confounders
        Override the default confounder list from ``graph.CONFOUNDERS``.
    method
        DoWhy estimation method identifier.
    refute
        If True, run a placebo-treatment refuter for robustness.

    Returns
    -------
    dict with keys: ``ate``, ``ate_ci_lower``, ``ate_ci_upper``,
    ``refutation_p_value``, ``n_samples``, ``method``, ``treatment``, ``outcome``.
    """
    from dowhy import CausalModel

    confounders = confounders or list(CONFOUNDERS)

    df = data.copy()
    # Encode categorical confounders to integers (DoWhy + sklearn friendly).
    for col in confounders:
        if df[col].dtype == object:
            df[col] = df[col].astype("category").cat.codes

    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        graph=get_graph(),
    )
    identified = model.identify_effect(proceed_when_unidentifiable=True)
    estimate = model.estimate_effect(identified, method_name=method)

    ate = float(estimate.value)
    ci_lower = ci_upper = None
    if hasattr(estimate, "get_confidence_intervals"):
        try:
            ci = estimate.get_confidence_intervals()
            ci_lower, ci_upper = float(ci[0][0]), float(ci[0][1])
        except Exception:
            pass

    refutation_p = None
    if refute:
        try:
            ref = model.refute_estimate(
                identified,
                estimate,
                method_name="placebo_treatment_refuter",
                placebo_type="permute",
            )
            refutation_p = float(getattr(ref, "refutation_result", {}).get("p_value", np.nan))
        except Exception as exc:
            logger.warning("Refutation failed: %s", exc)

    result = {
        "ate": ate,
        "ate_ci_lower": ci_lower,
        "ate_ci_upper": ci_upper,
        "refutation_p_value": refutation_p,
        "n_samples": int(len(df)),
        "method": method,
        "treatment": treatment,
        "outcome": outcome,
        "confounders": confounders,
    }

    _log_to_mlflow(
        params={
            "treatment": treatment,
            "outcome": outcome,
            "method": method,
            "n_samples": len(df),
            "confounders": ",".join(confounders),
        },
        metrics={
            "ate": ate,
            "ate_ci_lower": ci_lower,
            "ate_ci_upper": ci_upper,
            "refutation_p_value": refutation_p,
        },
    )
    return result


def estimate_counterfactual(
    data: pd.DataFrame,
    intervention_delta: float,
    treatment: str = TREATMENT,
    outcome: str = OUTCOME,
) -> dict:
    """Translate an ATE into a human-friendly counterfactual.

    Answers: *"If I shift `treatment` by `intervention_delta` units for every
    order, what is the expected shift in `outcome`?"*
    """
    est = estimate_ate(data, treatment=treatment, outcome=outcome, refute=False)
    ate = est["ate"]
    expected_shift = ate * intervention_delta
    return {
        **est,
        "intervention_delta": intervention_delta,
        "expected_outcome_shift": expected_shift,
        "narrative": (
            f"Shifting {treatment} by {intervention_delta:+.2f} units is estimated "
            f"to change {outcome} by {expected_shift:+.3f} units on average "
            f"(ATE={ate:+.4f} per unit, n={est['n_samples']})."
        ),
    }
