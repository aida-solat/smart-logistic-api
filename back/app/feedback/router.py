"""FastAPI router for the feedback / override loop (phase 9)."""
from __future__ import annotations

from collections import Counter
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.feedback.schemas import OverrideRecord, OverrideSummary
from app.feedback.storage import append_override, iter_overrides, read_overrides

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/override", response_model=OverrideRecord)
def post_override(record: OverrideRecord) -> OverrideRecord:
    """Log an operator override of an AI recommendation.

    These tuples form the counterfactual training set consumed by the
    active-learning retraining job.
    """
    try:
        append_override(record)
    except Exception as exc:  # pragma: no cover - IO failure edge case
        raise HTTPException(500, f"Failed to persist override: {exc}") from exc
    return record


@router.get("/overrides", response_model=list[OverrideRecord])
def list_overrides(
    limit: int = Query(50, gt=0, le=1000),
    decision_type: Optional[str] = None,
) -> list[OverrideRecord]:
    """Return recent overrides (newest first)."""
    records = read_overrides(limit=None)
    if decision_type:
        records = [r for r in records if r.decision_type == decision_type]
    return records[:limit]


@router.get("/summary", response_model=OverrideSummary)
def summary() -> OverrideSummary:
    """Roll-up statistics across every logged override."""
    total = 0
    by_type: Counter[str] = Counter()
    with_outcome = 0
    latest = None
    for rec in iter_overrides():
        total += 1
        by_type[rec.decision_type] += 1
        if rec.observed_outcome is not None:
            with_outcome += 1
        if latest is None or rec.created_at > latest:
            latest = rec.created_at
    return OverrideSummary(
        total=total,
        by_type=dict(by_type),
        with_outcome=with_outcome,
        latest=latest,
    )
