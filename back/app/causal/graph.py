"""Causal graph definition for the logistics decision problem.

Domain knowledge encoded as a DAG. DoWhy uses this graph to derive a valid
adjustment set (backdoor / frontdoor) for unbiased effect estimation.

Nodes (for the Olist-based phase 1 analysis):

    processing_time_days   — treatment (decision variable)
    shipping_distance_km   — confounder (affects both processing and delay)
    product_weight_kg      — confounder
    seller_state           — confounder (capacity, proximity)
    customer_state         — confounder
    order_month            — confounder (seasonality / holidays)
    delay_days             — outcome

Edges (cause -> effect):
    shipping_distance_km  -> processing_time_days, delay_days
    product_weight_kg     -> processing_time_days, delay_days
    seller_state          -> processing_time_days, delay_days, shipping_distance_km
    customer_state        -> shipping_distance_km, delay_days
    order_month           -> processing_time_days, delay_days
    processing_time_days  -> delay_days          (the effect we estimate)
"""
from __future__ import annotations


# GML format consumed by DoWhy's ``CausalModel``.
_DAG_GML = """graph [
  directed 1
  node [id 0 label "processing_time_days"]
  node [id 1 label "shipping_distance_km"]
  node [id 2 label "product_weight_kg"]
  node [id 3 label "seller_state"]
  node [id 4 label "customer_state"]
  node [id 5 label "order_month"]
  node [id 6 label "delay_days"]
  edge [source 0 target 6]
  edge [source 1 target 0]
  edge [source 1 target 6]
  edge [source 2 target 0]
  edge [source 2 target 6]
  edge [source 3 target 0]
  edge [source 3 target 1]
  edge [source 3 target 6]
  edge [source 4 target 1]
  edge [source 4 target 6]
  edge [source 5 target 0]
  edge [source 5 target 6]
]"""


def get_graph() -> str:
    """Return the causal DAG as a GML string."""
    return _DAG_GML


TREATMENT = "processing_time_days"
OUTCOME = "delay_days"
CONFOUNDERS = [
    "shipping_distance_km",
    "product_weight_kg",
    "seller_state",
    "customer_state",
    "order_month",
]
