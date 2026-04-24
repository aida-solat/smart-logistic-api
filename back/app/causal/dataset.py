"""Olist dataset loader + feature engineering for causal analysis.

Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
Expected layout under ``back/data/raw/olist/``::

    olist_orders_dataset.csv
    olist_order_items_dataset.csv
    olist_customers_dataset.csv
    olist_sellers_dataset.csv
    olist_geolocation_dataset.csv
    olist_products_dataset.csv

The loader builds a single per-order dataframe with the columns needed for
the causal analysis in :mod:`app.causal.effects`:

    - processing_time_days   (treatment candidate)
    - shipping_distance_km   (confounder)
    - product_weight_kg      (confounder)
    - seller_state, customer_state  (confounders)
    - order_month            (seasonality confounder)
    - delay_days             (outcome: actual_delivery - estimated_delivery)
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DATA_ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "olist"


def _read(name: str) -> pd.DataFrame:
    path = DATA_ROOT / name
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Download Olist dataset and extract to {DATA_ROOT}."
        )
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_order_features() -> pd.DataFrame:
    """Return one-row-per-order dataframe with features + outcome."""
    orders = _read("olist_orders_dataset.csv")
    items = _read("olist_order_items_dataset.csv")
    customers = _read("olist_customers_dataset.csv")
    sellers = _read("olist_sellers_dataset.csv")
    products = _read("olist_products_dataset.csv")

    # Keep only delivered orders with all timestamps present.
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for c in date_cols:
        orders[c] = pd.to_datetime(orders[c], errors="coerce")

    orders = orders[orders["order_status"] == "delivered"].dropna(subset=date_cols)

    # Outcome: positive = late, negative = early
    orders["delay_days"] = (
        orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400.0

    # Treatment candidate: processing_time = approval -> carrier handoff
    orders["processing_time_days"] = (
        orders["order_delivered_carrier_date"] - orders["order_approved_at"]
    ).dt.total_seconds() / 86400.0
    orders = orders[orders["processing_time_days"] >= 0]

    orders["order_month"] = orders["order_purchase_timestamp"].dt.month

    # Merge product & seller info (first item per order for simplicity)
    first_items = items.sort_values("order_item_id").drop_duplicates("order_id")
    df = orders.merge(first_items, on="order_id", how="left")
    df = df.merge(
        products[["product_id", "product_weight_g"]], on="product_id", how="left"
    )
    df = df.merge(
        sellers[["seller_id", "seller_state"]], on="seller_id", how="left"
    )
    df = df.merge(
        customers[["customer_id", "customer_state"]], on="customer_id", how="left"
    )

    df["product_weight_kg"] = df["product_weight_g"].fillna(
        df["product_weight_g"].median()
    ) / 1000.0

    # Shipping distance: simple state-pair indicator (phase 1 stub).
    # Real geodesic distance via geolocation dataset is a phase-1.5 task.
    df["same_state"] = (df["seller_state"] == df["customer_state"]).astype(int)
    df["shipping_distance_km"] = np.where(df["same_state"] == 1, 50.0, 800.0)

    keep = [
        "order_id",
        "processing_time_days",
        "shipping_distance_km",
        "product_weight_kg",
        "seller_state",
        "customer_state",
        "order_month",
        "same_state",
        "delay_days",
    ]
    df = df[keep].dropna()
    logger.info("Loaded Olist features: %d orders", len(df))
    return df


@lru_cache(maxsize=4)
def build_demand_panel(
    freq: str = "W",
    top_k: int = 5,
    state_col: str = "customer_state",
) -> pd.DataFrame:
    """Aggregate Olist orders into a period × warehouse demand panel.

    We treat the top-``k`` destination states as "warehouses" and count orders
    per ``freq`` (e.g. weekly). The resulting panel is the ground-truth
    historical distribution used by the bootstrap scenario generator in
    :func:`app.optimizer.scenarios.bootstrap_from_history`.

    Parameters
    ----------
    freq
        Pandas offset alias for the aggregation bucket (``"W"`` weekly,
        ``"D"`` daily, ``"MS"`` month-start).
    top_k
        Number of top destination states to keep as warehouses.
    state_col
        Either ``"customer_state"`` (demand origin, default) or ``"seller_state"``.

    Returns
    -------
    pandas.DataFrame
        Shape ``(n_periods, top_k)`` with one column per state. Integer counts.
    """
    orders = _read("olist_orders_dataset.csv")
    customers = _read("olist_customers_dataset.csv")
    sellers = _read("olist_sellers_dataset.csv")
    items = _read("olist_order_items_dataset.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders = orders.dropna(subset=["order_purchase_timestamp"])

    if state_col == "customer_state":
        merged = orders.merge(
            customers[["customer_id", "customer_state"]], on="customer_id", how="left"
        )
    else:
        first_items = items.sort_values("order_item_id").drop_duplicates("order_id")
        merged = orders.merge(
            first_items[["order_id", "seller_id"]], on="order_id", how="left"
        ).merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")

    merged = merged.dropna(subset=[state_col])
    top_states = (
        merged[state_col].value_counts().head(top_k).index.tolist()
    )
    merged = merged[merged[state_col].isin(top_states)]

    panel = (
        merged.groupby(
            [pd.Grouper(key="order_purchase_timestamp", freq=freq), state_col]
        )
        .size()
        .unstack(fill_value=0)
        .reindex(columns=top_states, fill_value=0)
        .astype(float)
        .sort_index()
    )
    panel.index.name = "period"
    logger.info("Built demand panel: %d periods × %d states", *panel.shape)
    return panel
