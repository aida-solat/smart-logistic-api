"""Pydantic schemas for operator feedback / override records."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class OverrideRecord(BaseModel):
    """A single human override of an AI recommendation.

    The tuple (state, ai_recommendation, human_decision, observed_outcome)
    is the counterfactual training signal used by the active-learning loop
    to refine downstream causal estimators.
    """

    decision_id: str = Field(..., description="ID of the decision being overridden.")
    decision_type: str = Field(
        ..., description="One of: cvar_inventory, vrp_routing, informed_cvar, joint."
    )
    state: dict[str, Any] = Field(
        ...,
        description="Environment snapshot at the time of the decision "
        "(stock levels, demand scenarios, etc.).",
    )
    ai_recommendation: dict[str, Any] = Field(
        ..., description="What the optimizer proposed."
    )
    human_decision: dict[str, Any] = Field(
        ..., description="What the operator did instead."
    )
    observed_outcome: Optional[dict[str, Any]] = Field(
        None,
        description="Realised KPIs once the decision played out "
        "(may be filled in a later call).",
    )
    operator_id: Optional[str] = Field(None)
    reason: Optional[str] = Field(
        None, description="Free-text rationale from the operator."
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OverrideSummary(BaseModel):
    total: int
    by_type: dict[str, int]
    with_outcome: int
    latest: Optional[datetime]
