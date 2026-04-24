"""Active-learning feedback loop from human overrides (Phase 9).

When an operator overrides an AI recommendation, we capture:
    (state, ai_recommendation, human_decision, observed_outcome)
These tuples become counterfactual training examples that refine the causal
effect estimators. This is one of the core novel mechanisms.
"""
from app.feedback.router import router  # noqa: F401
from app.feedback.schemas import OverrideRecord, OverrideSummary  # noqa: F401
