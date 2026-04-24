"""CVaR-optimal inventory reallocation (Rockafellar-Uryasev 2000).

Problem
-------
N warehouses with current stocks ``s_i`` and uncertain demand ``D_i(ω)`` over
a scenario set ``Ω`` (|Ω|=S). We decide a non-negative reallocation matrix
``x_ij`` (units moved from i to j, i≠j) with per-unit transport cost ``c_ij``.
Post-reallocation stock is

    y_i = s_i - Σ_j x_ij + Σ_j x_ji     (must be ≥ 0)

For each scenario ``s`` the loss is transport + stockout:

    L_s(x, y) = Σ_ij c_ij x_ij + p · Σ_i max(D_i^s - y_i, 0)

We minimize a convex combination of expected loss and α-CVaR of loss:

    minimize   (1 - λ) · E[L] + λ · CVaR_α(L)

The CVaR term uses the Rockafellar-Uryasev linear reformulation with
auxiliary variables ``t`` (VaR) and ``u_s ≥ 0`` (excess above VaR):

    CVaR_α(L) = min_t  t + (1 / ((1-α) · S)) · Σ_s u_s
    subject to u_s ≥ L_s - t,   u_s ≥ 0

The whole program is an LP (with a continuous-relaxed positive-part via an
auxiliary variable for the stockout), solved by CVXPY (default ECOS / SCS).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import cvxpy as cp
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CVaRResult:
    allocation: np.ndarray  # (N, N) reallocation matrix x_ij
    post_stock: np.ndarray  # (N,) stock after reallocation y_i
    expected_loss: float
    cvar_alpha: float
    var_alpha: float        # the t* (value-at-risk)
    objective: float
    alpha: float
    lam: float
    n_scenarios: int
    solver_status: str

    def to_dict(self) -> dict:
        return {
            "allocation": self.allocation.tolist(),
            "post_stock": self.post_stock.tolist(),
            "expected_loss": float(self.expected_loss),
            "cvar_alpha": float(self.cvar_alpha),
            "var_alpha": float(self.var_alpha),
            "objective": float(self.objective),
            "alpha": self.alpha,
            "lambda": self.lam,
            "n_scenarios": self.n_scenarios,
            "solver_status": self.solver_status,
        }


def solve_cvar_inventory(
    initial_stock: np.ndarray,
    demand_scenarios: np.ndarray,
    transport_cost: np.ndarray,
    stockout_penalty: float = 10.0,
    alpha: float = 0.95,
    lam: float = 0.5,
    solver: Optional[str] = None,
) -> CVaRResult:
    """Solve the CVaR inventory reallocation LP.

    Parameters
    ----------
    initial_stock
        Shape ``(N,)``. Current non-negative stock at each warehouse.
    demand_scenarios
        Shape ``(S, N)``. Each row is one realization of demand over the
        warehouses. Sampled from history or a parametric model.
    transport_cost
        Shape ``(N, N)``. Per-unit cost ``c_ij`` to move stock from i to j.
        Diagonal is ignored (no self-transport).
    stockout_penalty
        Scalar ``p``. Cost per unit of unmet demand.
    alpha
        CVaR tail level, typically 0.90–0.99. Higher = more risk-averse.
    lam
        Weight on the CVaR term (0 = risk-neutral expected cost,
        1 = pure CVaR minimization).
    solver
        Optional CVXPY solver name (e.g. ``"ECOS"``, ``"SCS"``, ``"CLARABEL"``).

    Returns
    -------
    :class:`CVaRResult`
    """
    s = np.asarray(initial_stock, dtype=float).ravel()
    D = np.asarray(demand_scenarios, dtype=float)
    C = np.asarray(transport_cost, dtype=float)

    N = s.shape[0]
    if D.ndim != 2 or D.shape[1] != N:
        raise ValueError(f"demand_scenarios must be (S, {N}); got {D.shape}")
    if C.shape != (N, N):
        raise ValueError(f"transport_cost must be ({N}, {N}); got {C.shape}")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1)")
    if not (0.0 <= lam <= 1.0):
        raise ValueError("lam must be in [0, 1]")

    S = D.shape[0]
    np.fill_diagonal(C, 0.0)

    # Decision variables
    x = cp.Variable((N, N), nonneg=True)         # reallocation flows
    y = cp.Variable(N, nonneg=True)              # post-reallocation stock
    shortage = cp.Variable((S, N), nonneg=True)  # = max(D_s - y, 0)
    t = cp.Variable()                            # VaR_α
    u = cp.Variable(S, nonneg=True)              # excess above VaR per scenario

    # Flow conservation: y_i = s_i - outflow_i + inflow_i, y_i >= 0 (nonneg above)
    outflow = cp.sum(x, axis=1)
    inflow = cp.sum(x, axis=0)
    constraints = [
        y == s - outflow + inflow,
        # Shortage >= D_s - y (elementwise), shortage >= 0 (nonneg)
        shortage >= D - cp.reshape(y, (1, N), order="C"),
    ]

    # Per-scenario loss
    transport_total = cp.sum(cp.multiply(C, x))
    scenario_loss = transport_total + stockout_penalty * cp.sum(shortage, axis=1)

    # CVaR linearization: u_s >= L_s - t
    constraints.append(u >= scenario_loss - t)

    expected_loss = cp.sum(scenario_loss) / S
    cvar_term = t + cp.sum(u) / ((1.0 - alpha) * S)

    objective = cp.Minimize((1.0 - lam) * expected_loss + lam * cvar_term)
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=solver)

    if prob.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"CVaR LP did not solve to optimality: {prob.status}")

    x_val = np.asarray(x.value)
    np.fill_diagonal(x_val, 0.0)  # numerical zero
    x_val = np.clip(x_val, 0.0, None)

    result = CVaRResult(
        allocation=x_val,
        post_stock=np.asarray(y.value).ravel(),
        expected_loss=float(expected_loss.value),
        cvar_alpha=float(cvar_term.value),
        var_alpha=float(t.value),
        objective=float(prob.value),
        alpha=alpha,
        lam=lam,
        n_scenarios=S,
        solver_status=prob.status,
    )

    _log_to_mlflow(result)
    return result


def _log_to_mlflow(result: CVaRResult, experiment: str = "cvar-optim") -> None:
    """Best-effort MLflow logging — audit trail."""
    try:
        import mlflow

        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
        mlflow.set_experiment(experiment)
        with mlflow.start_run():
            mlflow.log_params(
                {
                    "alpha": result.alpha,
                    "lambda": result.lam,
                    "n_scenarios": result.n_scenarios,
                    "solver_status": result.solver_status,
                }
            )
            mlflow.log_metrics(
                {
                    "expected_loss": result.expected_loss,
                    "cvar_alpha": result.cvar_alpha,
                    "var_alpha": result.var_alpha,
                    "objective": result.objective,
                }
            )
    except Exception as exc:  # pragma: no cover
        logger.warning("MLflow logging skipped: %s", exc)


# Backwards-compatible stub signature used by phase-0 code paths.
def solve_cvar(scenarios, constraints, alpha: float = 0.95, lambda_: float = 0.5):
    raise NotImplementedError(
        "Deprecated phase-0 stub; use solve_cvar_inventory with explicit arrays."
    )
