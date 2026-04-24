"""Scenario generators for the CVaR stochastic optimizer.

Two generators are provided:

* :func:`parametric_demand` — i.i.d. lognormal / normal draws from supplied
  per-warehouse mean/std (fast, for what-if analysis).
* :func:`bootstrap_from_history` — nonparametric bootstrap from a historical
  demand panel (preserves empirical cross-warehouse correlations).

Both return an ``(S, N)`` numpy array consumable by
:func:`app.optimizer.cvar.solve_cvar_inventory`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def parametric_demand(
    mean: np.ndarray,
    std: np.ndarray,
    n_scenarios: int = 500,
    distribution: str = "lognormal",
    seed: int = 0,
) -> np.ndarray:
    """Generate i.i.d. demand scenarios with the requested distribution.

    Parameters
    ----------
    mean, std
        Shape ``(N,)`` marginal mean / std-dev per warehouse.
    n_scenarios
        Number of scenarios ``S`` to draw.
    distribution
        ``"lognormal"`` (default, non-negative, heavy right tail) or
        ``"normal"`` (clipped at 0).
    """
    mean = np.asarray(mean, dtype=float).ravel()
    std = np.asarray(std, dtype=float).ravel()
    if mean.shape != std.shape:
        raise ValueError("mean and std must have the same shape")

    rng = np.random.default_rng(seed)
    N = mean.shape[0]

    if distribution == "normal":
        D = rng.normal(loc=mean, scale=std, size=(n_scenarios, N))
        return np.clip(D, 0.0, None)

    if distribution == "lognormal":
        # Match target mean/std via lognormal moment matching.
        variance = np.clip(std ** 2, 1e-12, None)
        mu = np.log(np.clip(mean, 1e-12, None) ** 2 / np.sqrt(variance + mean ** 2))
        sigma = np.sqrt(np.log(1.0 + variance / np.clip(mean, 1e-12, None) ** 2))
        D = rng.lognormal(mean=mu, sigma=sigma, size=(n_scenarios, N))
        return D

    raise ValueError(f"Unknown distribution: {distribution}")


def bootstrap_from_history(
    history: pd.DataFrame,
    n_scenarios: int = 500,
    seed: int = 0,
) -> np.ndarray:
    """Nonparametric bootstrap of demand vectors from a historical panel.

    Parameters
    ----------
    history
        DataFrame with one row per historical period and one column per
        warehouse. Column order defines the warehouse order in the output.
    n_scenarios
        Number of bootstrap draws.
    """
    X = history.to_numpy(dtype=float)
    if X.ndim != 2:
        raise ValueError("history must be 2D (periods x warehouses)")
    rng = np.random.default_rng(seed)
    idx = rng.integers(low=0, high=X.shape[0], size=n_scenarios)
    return X[idx]
