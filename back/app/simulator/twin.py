"""Digital twin of a multi-warehouse fulfillment network (SimPy).

Models a simple but realistic logistics process:

* Orders arrive at each warehouse as a Poisson process with a per-warehouse
  rate.
* Each order requires ``units`` units of stock; if available, the warehouse
  picks & ships immediately (service time ~ Exponential); if not, the order
  is logged as a stockout.
* Shipping time to the customer is sampled from a LogNormal with
  warehouse-specific parameters (captures fat-tailed delays).
* KPIs are aggregated: total cost, service level, stockout count, mean &
  tail (p95) lead time.

The simulator is used to evaluate a decision produced by the CVaR optimizer
or the causal engine *before* it is deployed — an A/B offline backtest.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import simpy

logger = logging.getLogger(__name__)


@dataclass
class WarehouseConfig:
    name: str
    initial_stock: float
    arrival_rate: float          # orders per time unit
    units_per_order_mean: float  # mean units demanded per order
    units_per_order_std: float
    service_time_mean: float     # hours to pick & handoff
    shipping_mu: float           # LogNormal mu for shipping time
    shipping_sigma: float        # LogNormal sigma
    transport_cost_per_unit: float = 1.0
    stockout_penalty_per_unit: float = 10.0


@dataclass
class SimMetrics:
    n_orders: int = 0
    n_fulfilled: int = 0
    n_stockouts: int = 0
    total_units_demanded: float = 0.0
    total_units_shorted: float = 0.0
    lead_times: list[float] = field(default_factory=list)
    transport_cost: float = 0.0
    stockout_cost: float = 0.0

    def summary(self) -> dict:
        lead = np.array(self.lead_times) if self.lead_times else np.array([0.0])
        return {
            "n_orders": self.n_orders,
            "n_fulfilled": self.n_fulfilled,
            "n_stockouts": self.n_stockouts,
            "service_level": (
                self.n_fulfilled / self.n_orders if self.n_orders else 1.0
            ),
            "total_units_demanded": self.total_units_demanded,
            "total_units_shorted": self.total_units_shorted,
            "mean_lead_time": float(lead.mean()),
            "p95_lead_time": float(np.percentile(lead, 95)),
            "p99_lead_time": float(np.percentile(lead, 99)),
            "transport_cost": self.transport_cost,
            "stockout_cost": self.stockout_cost,
            "total_cost": self.transport_cost + self.stockout_cost,
        }


def _order_process(env: simpy.Environment, wh: WarehouseConfig,
                   stock: dict, metrics: SimMetrics, rng: np.random.Generator):
    while True:
        # Poisson inter-arrival
        interarrival = rng.exponential(1.0 / max(wh.arrival_rate, 1e-9))
        yield env.timeout(interarrival)

        units = max(1.0, rng.normal(wh.units_per_order_mean, wh.units_per_order_std))
        metrics.n_orders += 1
        metrics.total_units_demanded += units

        available = stock[wh.name]
        if available >= units:
            stock[wh.name] = available - units
            # Service time (pick + ship handoff)
            service = rng.exponential(wh.service_time_mean)
            shipping = rng.lognormal(mean=wh.shipping_mu, sigma=wh.shipping_sigma)
            lead = service + shipping
            metrics.lead_times.append(lead)
            metrics.n_fulfilled += 1
            metrics.transport_cost += units * wh.transport_cost_per_unit
        else:
            short = units - available
            stock[wh.name] = 0.0
            metrics.n_stockouts += 1
            metrics.total_units_shorted += short
            metrics.stockout_cost += short * wh.stockout_penalty_per_unit
            if available > 0:
                # Partially fulfill the part we have
                metrics.lead_times.append(
                    rng.exponential(wh.service_time_mean)
                    + rng.lognormal(wh.shipping_mu, wh.shipping_sigma)
                )


def run_simulation(
    warehouses: list[WarehouseConfig],
    horizon: float = 168.0,     # 1 week in hours
    seed: int = 0,
    initial_stock_override: Optional[dict] = None,
) -> dict:
    """Run one replication of the digital twin.

    Parameters
    ----------
    warehouses
        List of warehouse configs.
    horizon
        Simulated time span (e.g. 168 hours = 1 week).
    seed
        RNG seed (varies across Monte-Carlo replications).
    initial_stock_override
        Optional dict mapping warehouse name -> post-reallocation stock
        (used to evaluate a decision from the CVaR optimizer).
    """
    env = simpy.Environment()
    rng = np.random.default_rng(seed)

    stock = {
        w.name: float(
            initial_stock_override[w.name]
            if initial_stock_override and w.name in initial_stock_override
            else w.initial_stock
        )
        for w in warehouses
    }
    metrics = SimMetrics()

    for wh in warehouses:
        env.process(_order_process(env, wh, stock, metrics, rng))

    env.run(until=horizon)

    out = metrics.summary()
    out["final_stock"] = stock
    out["horizon"] = horizon
    out["seed"] = seed
    return out


def monte_carlo(
    warehouses: list[WarehouseConfig],
    horizon: float = 168.0,
    n_replications: int = 30,
    seed: int = 0,
    initial_stock_override: Optional[dict] = None,
) -> dict:
    """Run ``n_replications`` independent replications and aggregate KPIs.

    Returns mean and p5/p95 across replications — the empirical distribution
    over which CVaR / tail risk of a decision can be measured.
    """
    rng = np.random.default_rng(seed)
    seeds = rng.integers(0, 2**31 - 1, size=n_replications)
    runs = [
        run_simulation(warehouses, horizon=horizon, seed=int(s),
                       initial_stock_override=initial_stock_override)
        for s in seeds
    ]

    def agg(key: str):
        vals = np.array([r[key] for r in runs], dtype=float)
        return {
            "mean": float(vals.mean()),
            "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
            "p5": float(np.percentile(vals, 5)),
            "p50": float(np.percentile(vals, 50)),
            "p95": float(np.percentile(vals, 95)),
        }

    aggregate_keys = [
        "service_level", "mean_lead_time", "p95_lead_time", "p99_lead_time",
        "transport_cost", "stockout_cost", "total_cost",
        "n_stockouts", "total_units_shorted",
    ]
    return {
        "n_replications": n_replications,
        "horizon": horizon,
        "aggregated": {k: agg(k) for k in aggregate_keys},
        "replications": runs,
    }
