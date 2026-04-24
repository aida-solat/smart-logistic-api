"""FastAPI router for the causal decision endpoints (phase 1)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.causal.dataset import load_order_features
from app.causal.effects import estimate_ate, estimate_counterfactual
from app.causal.integration import causal_informed_cvar
from app.causal.adaptive_beta import (
    calibrate_from_log,
    load_observations,
    record_observation,
)
from app.causal.graph import CONFOUNDERS, OUTCOME, TREATMENT

router = APIRouter(prefix="/causal", tags=["causal"])


class EstimateRequest(BaseModel):
    treatment: str = Field(TREATMENT, description="Decision variable column name.")
    outcome: str = Field(OUTCOME, description="KPI column name.")
    method: str = Field(
        "backdoor.linear_regression",
        description="DoWhy estimation method (e.g. backdoor.linear_regression).",
    )
    refute: bool = Field(True, description="Run placebo-treatment refuter for robustness.")
    sample_size: Optional[int] = Field(
        None,
        description="Optional: use a random subsample for faster iteration.",
        gt=0,
    )


class CounterfactualRequest(EstimateRequest):
    intervention_delta: float = Field(
        ...,
        description=(
            "How much to shift the treatment (positive or negative). "
            "Units match the treatment column."
        ),
    )


@router.get("/graph")
def get_causal_graph():
    """Return the DAG (GML) plus the declared treatment / outcome / confounders."""
    from app.causal.graph import get_graph

    return {
        "treatment": TREATMENT,
        "outcome": OUTCOME,
        "confounders": CONFOUNDERS,
        "graph_gml": get_graph(),
    }


@router.post("/estimate-effect")
def post_estimate_effect(req: EstimateRequest):
    """Estimate the causal effect (ATE) of a decision on a KPI."""
    try:
        df = load_order_features()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Olist dataset not found. {exc}. "
                "See back/data/raw/olist/README.md for download instructions."
            ),
        )

    if req.sample_size and req.sample_size < len(df):
        df = df.sample(n=req.sample_size, random_state=42)

    try:
        return estimate_ate(
            df,
            treatment=req.treatment,
            outcome=req.outcome,
            method=req.method,
            refute=req.refute,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Causal estimation failed: {exc}")


@router.post("/counterfactual")
def post_counterfactual(req: CounterfactualRequest):
    """Estimate the expected outcome shift under a hypothetical intervention."""
    try:
        df = load_order_features()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    if req.sample_size and req.sample_size < len(df):
        df = df.sample(n=req.sample_size, random_state=42)

    try:
        return estimate_counterfactual(
            df,
            intervention_delta=req.intervention_delta,
            treatment=req.treatment,
            outcome=req.outcome,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Counterfactual failed: {exc}")


class CausalInformedCVaRRequest(BaseModel):
    intervention_delta: float = Field(
        ..., description="Change in processing_time_days to simulate (negative = faster)."
    )
    base_stockout_penalty: float = Field(10.0, gt=0)
    beta: float = Field(
        0.5, description="Sensitivity of penalty to the causal delay shift (per day)."
    )
    freq: str = Field("W")
    top_k: int = Field(5, gt=1, le=15)
    stock_multiplier: float = Field(1.2, gt=0)
    transport_cost_uniform: float = Field(1.0, gt=0)
    alpha: float = Field(0.95, gt=0, lt=1)
    lam: float = Field(0.5, ge=0, le=1)
    n_scenarios: int = Field(500, gt=0, le=20000)
    causal_sample_size: int = Field(5000, gt=0)
    seed: int = 0


@router.post("/informed-cvar")
def post_informed_cvar(req: CausalInformedCVaRRequest):
    """End-to-end causal-informed CVaR reallocation (novel pipeline).

    Pipeline:
    1. Estimate causal ATE of processing_time → delay from Olist.
    2. Convert intervention Δ to expected delay shift (Δ · ATE).
    3. Map delay shift to an **effective stockout penalty**.
    4. Bootstrap demand scenarios from the Olist historical panel.
    5. Solve the Rockafellar-Uryasev CVaR LP with the adjusted penalty.

    Every step is logged to MLflow for audit.
    """
    try:
        return causal_informed_cvar(
            intervention_delta=req.intervention_delta,
            base_stockout_penalty=req.base_stockout_penalty,
            beta=req.beta,
            freq=req.freq,
            top_k=req.top_k,
            stock_multiplier=req.stock_multiplier,
            transport_cost_uniform=req.transport_cost_uniform,
            alpha=req.alpha,
            lam=req.lam,
            n_scenarios=req.n_scenarios,
            causal_sample_size=req.causal_sample_size,
            seed=req.seed,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Informed CVaR failed: {exc}")


class CalibrationObservation(BaseModel):
    delay_shift: float
    baseline_cost: float
    decision_cost: float
    meta: Optional[dict] = None


@router.post("/calibration/record")
def post_record_observation(obs: CalibrationObservation):
    """Append a post-deployment observation to the β calibration log."""
    record_observation(
        delay_shift=obs.delay_shift,
        baseline_cost=obs.baseline_cost,
        decision_cost=obs.decision_cost,
        meta=obs.meta,
    )
    return {"status": "recorded"}


@router.get("/calibration/observations")
def get_calibration_observations():
    """Return the raw calibration log (for UI plotting)."""
    rows = load_observations()
    return {"n": len(rows), "observations": rows}


@router.get("/calibration/beta")
def get_calibrated_beta():
    """Fit β from the calibration log and return the estimate."""
    try:
        fit = calibrate_from_log()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {
        "beta": fit.beta,
        "n_observations": fit.n_observations,
        "r_squared": fit.r_squared,
        "residual_std": fit.residual_std,
    }
