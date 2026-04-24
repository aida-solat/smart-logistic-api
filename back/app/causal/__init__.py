"""Causal inference layer (phase 1 — live).

Public API:
    - :func:`app.causal.effects.estimate_ate`
    - :func:`app.causal.effects.estimate_counterfactual`
    - :func:`app.causal.dataset.load_order_features`
    - :data:`app.causal.router.router` — FastAPI router mounted under /causal
"""
from app.causal.router import router  # noqa: F401

