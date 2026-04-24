"""FastAPI router for the digital twin (phase 3)."""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.simulator.twin import WarehouseConfig, monte_carlo, run_simulation
from app.simulator.validate import validate_decision

router = APIRouter(prefix="/simulate", tags=["simulate"])


class WarehouseIn(BaseModel):
    name: str
    initial_stock: float = Field(..., ge=0)
    arrival_rate: float = Field(..., gt=0, description="Orders per time unit.")
    units_per_order_mean: float = Field(..., gt=0)
    units_per_order_std: float = Field(0.0, ge=0)
    service_time_mean: float = Field(..., gt=0)
    shipping_mu: float = 1.0
    shipping_sigma: float = 0.5
    transport_cost_per_unit: float = 1.0
    stockout_penalty_per_unit: float = 10.0


class SimulateRequest(BaseModel):
    warehouses: List[WarehouseIn] = Field(..., min_length=1)
    horizon: float = Field(168.0, gt=0, description="Simulated time (hours).")
    n_replications: int = Field(30, gt=0, le=500)
    seed: int = 0
    initial_stock_override: Optional[Dict[str, float]] = Field(
        None,
        description="Optional stock override per warehouse name (use the output of /optimize/cvar-inventory).",
    )


def _to_cfg(w: WarehouseIn) -> WarehouseConfig:
    return WarehouseConfig(**w.model_dump())


@router.post("/network")
def post_simulate_network(req: SimulateRequest):
    """Monte-Carlo simulate the fulfillment network and return KPI distributions."""
    cfgs = [_to_cfg(w) for w in req.warehouses]
    try:
        return monte_carlo(
            warehouses=cfgs,
            horizon=req.horizon,
            n_replications=req.n_replications,
            seed=req.seed,
            initial_stock_override=req.initial_stock_override,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {exc}")

class ValidateRequest(BaseModel):
    warehouses: List[WarehouseIn] = Field(..., min_length=1)
    allocation: Optional[List[List[float]]] = Field(
        None, description="N×N reallocation matrix (allocation[i][j] = units moved i→j)."
    )
    stock_override: Optional[Dict[str, float]] = Field(
        None, description="Direct per-warehouse post-decision stock (alternative to allocation)."
    )
    horizon: float = Field(168.0, gt=0)
    n_replications: int = Field(30, gt=0, le=500)
    seed: int = 0


@router.post("/validate")
def post_validate(req: ValidateRequest):
    """A/B offline backtest: simulate baseline vs decision stock, return uplift."""
    cfgs = [_to_cfg(w) for w in req.warehouses]
    try:
        return validate_decision(
            warehouses=cfgs,
            allocation=req.allocation,
            stock_override=req.stock_override,
            horizon=req.horizon,
            n_replications=req.n_replications,
            seed=req.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Validation failed: {exc}")



@router.post("/single-run")
def post_single_run(req: SimulateRequest):
    """Run a single replication (fast, useful for UI preview)."""
    cfgs = [_to_cfg(w) for w in req.warehouses]
    return run_simulation(
        warehouses=cfgs,
        horizon=req.horizon,
        seed=req.seed,
        initial_stock_override=req.initial_stock_override,
    )
