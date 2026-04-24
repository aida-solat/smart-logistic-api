"""FastAPI router for CVaR stochastic optimization (phase 2)."""
from __future__ import annotations

from typing import List, Optional

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.optimizer.cvar import solve_cvar_inventory
from app.optimizer.joint import joint_inventory_routing
from app.optimizer.scenarios import bootstrap_from_history, parametric_demand
from app.optimizer.vrp import solve_risk_aware_vrp

router = APIRouter(prefix="/optimize", tags=["optimize"])


class CVaRInventoryRequest(BaseModel):
    initial_stock: List[float] = Field(..., description="Current stock at each warehouse.")
    transport_cost: List[List[float]] = Field(
        ...,
        description="N×N per-unit transport cost matrix (diagonal ignored).",
    )
    # One of the following two must be provided:
    demand_scenarios: Optional[List[List[float]]] = Field(
        None,
        description="Explicit S×N demand scenarios. Overrides parametric fields.",
    )
    demand_mean: Optional[List[float]] = Field(
        None, description="Per-warehouse demand mean (used if scenarios omitted)."
    )
    demand_std: Optional[List[float]] = Field(
        None, description="Per-warehouse demand std-dev (used if scenarios omitted)."
    )
    n_scenarios: int = Field(500, gt=0, le=20000)
    distribution: str = Field("lognormal", pattern="^(lognormal|normal)$")

    stockout_penalty: float = Field(10.0, gt=0)
    alpha: float = Field(0.95, gt=0, lt=1)
    lam: float = Field(0.5, ge=0, le=1)
    seed: int = Field(0)
    solver: Optional[str] = Field(
        None, description="CVXPY solver name (ECOS, SCS, CLARABEL)."
    )


@router.post("/cvar-inventory")
def post_cvar_inventory(req: CVaRInventoryRequest):
    """Risk-aware inventory reallocation under uncertain demand."""
    initial_stock = np.asarray(req.initial_stock, dtype=float)
    N = initial_stock.shape[0]

    transport_cost = np.asarray(req.transport_cost, dtype=float)
    if transport_cost.shape != (N, N):
        raise HTTPException(
            status_code=422,
            detail=f"transport_cost must be {N}x{N}; got {transport_cost.shape}",
        )

    if req.demand_scenarios is not None:
        demand = np.asarray(req.demand_scenarios, dtype=float)
        if demand.ndim != 2 or demand.shape[1] != N:
            raise HTTPException(
                status_code=422,
                detail=f"demand_scenarios must be S×{N}; got {demand.shape}",
            )
    else:
        if req.demand_mean is None or req.demand_std is None:
            raise HTTPException(
                status_code=422,
                detail="Provide either demand_scenarios OR both demand_mean and demand_std.",
            )
        mean = np.asarray(req.demand_mean, dtype=float)
        std = np.asarray(req.demand_std, dtype=float)
        if mean.shape != (N,) or std.shape != (N,):
            raise HTTPException(
                status_code=422,
                detail=f"demand_mean/std must have length {N}.",
            )
        demand = parametric_demand(
            mean=mean,
            std=std,
            n_scenarios=req.n_scenarios,
            distribution=req.distribution,
            seed=req.seed,
        )

    try:
        result = solve_cvar_inventory(
            initial_stock=initial_stock,
            demand_scenarios=demand,
            transport_cost=transport_cost,
            stockout_penalty=req.stockout_penalty,
            alpha=req.alpha,
            lam=req.lam,
            solver=req.solver,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return result.to_dict()


class CVaROlistRequest(BaseModel):
    """CVaR inventory using Olist historical demand as scenarios.

    Warehouses are the top-``k`` destination states in the Olist dataset.
    """
    freq: str = Field("W", description="Panel frequency: W, D, MS, …")
    top_k: int = Field(5, gt=1, le=15)
    stock_multiplier: float = Field(
        1.2, gt=0,
        description="Initial stock per warehouse = multiplier × panel mean demand.",
    )
    transport_cost_uniform: float = Field(1.0, gt=0)
    stockout_penalty: float = Field(10.0, gt=0)
    alpha: float = Field(0.95, gt=0, lt=1)
    lam: float = Field(0.5, ge=0, le=1)
    n_scenarios: int = Field(500, gt=0, le=20000)
    seed: int = 0


@router.post("/cvar-inventory-olist")
def post_cvar_olist(req: CVaROlistRequest):
    """CVaR reallocation using *bootstrapped* Olist demand scenarios.

    This is the causal-informed variant: the scenarios come from the actual
    historical distribution of per-state weekly demand, preserving the
    empirical cross-state correlation structure instead of an i.i.d.
    parametric assumption. MLflow logs every run.
    """
    try:
        from app.causal.dataset import build_demand_panel

        panel = build_demand_panel(freq=req.freq, top_k=req.top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    N = panel.shape[1]
    means = panel.mean(axis=0).to_numpy()
    initial_stock = means * req.stock_multiplier
    transport = np.full((N, N), req.transport_cost_uniform)
    np.fill_diagonal(transport, 0.0)

    scenarios = bootstrap_from_history(panel, n_scenarios=req.n_scenarios, seed=req.seed)

    try:
        result = solve_cvar_inventory(
            initial_stock=initial_stock,
            demand_scenarios=scenarios,
            transport_cost=transport,
            stockout_penalty=req.stockout_penalty,
            alpha=req.alpha,
            lam=req.lam,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    out = result.to_dict()
    out["warehouses"] = panel.columns.tolist()
    out["historical_mean_demand"] = means.tolist()
    out["panel_shape"] = list(panel.shape)
    return out


class RiskVRPRequest(BaseModel):
    distance_matrix: List[List[float]] = Field(..., description="n×n mean travel time/distance.")
    demands: List[int] = Field(..., description="Demand per node (depot = 0).")
    vehicle_capacities: List[int] = Field(..., min_length=1)
    depot: int = Field(0, ge=0)
    travel_cv: float = Field(0.3, gt=0, le=2.0, description="CV of per-edge travel-time noise.")
    n_scenarios: int = Field(200, gt=0, le=5000)
    alpha: float = Field(0.95, gt=0, lt=1)
    time_limit_s: int = Field(10, gt=0, le=120)
    seed: int = 0


@router.post("/risk-vrp")
def post_risk_vrp(req: RiskVRPRequest):
    """Solve CVRP deterministically, then score makespan CVaR under travel-time noise."""
    D = np.asarray(req.distance_matrix, dtype=float)
    if D.ndim != 2 or D.shape[0] != D.shape[1]:
        raise HTTPException(status_code=422, detail="distance_matrix must be square.")
    if len(req.demands) != D.shape[0]:
        raise HTTPException(status_code=422, detail="demands length must match matrix.")

    try:
        result = solve_risk_aware_vrp(
            distance_matrix=D,
            demands=np.asarray(req.demands, dtype=int),
            vehicle_capacities=list(req.vehicle_capacities),
            travel_cv=req.travel_cv,
            n_scenarios=req.n_scenarios,
            alpha=req.alpha,
            depot=req.depot,
            time_limit_s=req.time_limit_s,
            seed=req.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return result.to_dict()


class JointRequest(BaseModel):
    initial_stock: List[float]
    transport_cost: List[List[float]]
    demand_scenarios: List[List[float]]
    stockout_penalty: float = 10.0
    alpha: float = 0.95
    lam: float = 0.5
    customer_distance_matrix: List[List[float]]
    customer_demands: List[int]
    vehicle_capacities: List[int] = Field(..., min_length=1)
    travel_cv: float = 0.3
    n_vrp_scenarios: int = 200
    seed: int = 0


@router.post("/joint")
def post_joint(req: JointRequest):
    """Joint CVaR inventory + risk-aware VRP (dependent novel claim)."""
    try:
        return joint_inventory_routing(
            initial_stock=np.asarray(req.initial_stock, dtype=float),
            demand_scenarios=np.asarray(req.demand_scenarios, dtype=float),
            transport_cost=np.asarray(req.transport_cost, dtype=float),
            customer_distance_matrix=np.asarray(req.customer_distance_matrix, dtype=float),
            customer_demands=np.asarray(req.customer_demands, dtype=int),
            vehicle_capacities=list(req.vehicle_capacities),
            stockout_penalty=req.stockout_penalty,
            alpha=req.alpha,
            lam=req.lam,
            travel_cv=req.travel_cv,
            n_vrp_scenarios=req.n_vrp_scenarios,
            seed=req.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
