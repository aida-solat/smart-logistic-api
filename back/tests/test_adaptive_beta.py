"""Tests for adaptive β calibration."""
from __future__ import annotations

import numpy as np
import pytest

from app.causal.adaptive_beta import (
    BetaFit,
    calibrate_from_log,
    fit_beta,
    record_observation,
)


def test_fit_beta_recovers_known_slope():
    rng = np.random.default_rng(0)
    delay_shifts = rng.uniform(-3, 3, size=200)
    true_beta = 0.35
    ratios = 1.0 + true_beta * delay_shifts + rng.normal(0, 0.05, size=200)
    fit = fit_beta(delay_shifts, ratios)
    assert abs(fit.beta - true_beta) < 0.02
    assert fit.n_observations == 200
    assert fit.r_squared > 0.95


def test_fit_beta_requires_variation():
    with pytest.raises(ValueError):
        fit_beta(np.zeros(5), np.ones(5))


def test_record_and_calibrate_roundtrip(tmp_path):
    log = tmp_path / "beta.jsonl"
    true_beta = 0.4
    rng = np.random.default_rng(1)
    for d in rng.uniform(-2, 2, size=50):
        ratio = 1.0 + true_beta * d + rng.normal(0, 0.02)
        record_observation(
            delay_shift=float(d),
            baseline_cost=1000.0,
            decision_cost=1000.0 * ratio,
            path=log,
        )
    fit = calibrate_from_log(log)
    assert isinstance(fit, BetaFit)
    assert abs(fit.beta - true_beta) < 0.05
    assert fit.n_observations == 50
