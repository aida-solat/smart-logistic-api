"""Tests for the causal inference layer (phase 1)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.causal.graph import CONFOUNDERS, OUTCOME, TREATMENT, get_graph


def _synthetic_data(n: int = 2000, true_ate: float = 0.5, seed: int = 0) -> pd.DataFrame:
    """Generate synthetic data where the true ATE is known."""
    rng = np.random.default_rng(seed)
    shipping = rng.normal(500, 200, n).clip(10, 2000)
    weight = rng.gamma(2.0, 1.0, n)
    seller_state = rng.integers(0, 10, n)
    customer_state = rng.integers(0, 10, n)
    month = rng.integers(1, 13, n)

    # Treatment depends on confounders (makes it confounded).
    processing = (
        0.002 * shipping
        + 0.3 * weight
        + 0.05 * seller_state
        + 0.02 * month
        + rng.normal(0, 1, n)
    )
    # Outcome has both a direct causal effect from treatment AND confounders.
    delay = (
        true_ate * processing
        + 0.003 * shipping
        + 0.2 * weight
        + 0.04 * customer_state
        + 0.03 * month
        + rng.normal(0, 1, n)
    )

    return pd.DataFrame(
        {
            TREATMENT: processing,
            "shipping_distance_km": shipping,
            "product_weight_kg": weight,
            "seller_state": seller_state,
            "customer_state": customer_state,
            "order_month": month,
            OUTCOME: delay,
        }
    )


def test_graph_is_valid_gml():
    g = get_graph()
    assert g.strip().startswith("graph [")
    assert "directed 1" in g
    for node in [TREATMENT, OUTCOME, *CONFOUNDERS]:
        assert node in g


@pytest.mark.slow
def test_estimate_ate_recovers_synthetic_effect():
    from app.causal.effects import estimate_ate

    df = _synthetic_data(n=2000, true_ate=0.5)
    result = estimate_ate(df, refute=False)

    assert result["n_samples"] == 2000
    # Linear regression backdoor should recover the true ATE within tolerance.
    assert abs(result["ate"] - 0.5) < 0.1, f"Recovered ATE={result['ate']}"


@pytest.mark.slow
def test_counterfactual_narrative():
    from app.causal.effects import estimate_counterfactual

    df = _synthetic_data(n=1000, true_ate=0.5)
    result = estimate_counterfactual(df, intervention_delta=-2.0)
    assert "intervention_delta" in result
    assert result["intervention_delta"] == -2.0
    # Negative delta * positive ATE should yield negative expected shift.
    assert result["expected_outcome_shift"] < 0
    assert "narrative" in result and "ATE=" in result["narrative"]


def test_causal_graph_endpoint(client):
    r = client.get("/causal/graph")
    assert r.status_code == 200
    body = r.json()
    assert body["treatment"] == TREATMENT
    assert body["outcome"] == OUTCOME
    assert body["confounders"] == CONFOUNDERS


def test_estimate_endpoint_without_data(client):
    """Without the Olist dataset present, the endpoint must return 503, not 500."""
    from app.causal import dataset

    dataset.load_order_features.cache_clear()
    r = client.post("/causal/estimate-effect", json={})
    # Either 503 (no data) or 200 (user downloaded it) — both are acceptable.
    assert r.status_code in (200, 503)
