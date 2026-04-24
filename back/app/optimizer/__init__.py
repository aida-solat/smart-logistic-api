"""Risk-aware stochastic optimizer (phase 2 — live).

Public API:
    - :func:`app.optimizer.cvar.solve_cvar_inventory`
    - :func:`app.optimizer.scenarios.parametric_demand`
    - :func:`app.optimizer.scenarios.bootstrap_from_history`
    - :data:`app.optimizer.router.router` — FastAPI router mounted under /optimize
"""
from app.optimizer.router import router  # noqa: F401

