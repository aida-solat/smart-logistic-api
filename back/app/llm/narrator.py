"""Translate optimizer / causal output into a short natural-language brief."""
from __future__ import annotations

import json
from typing import Any

from app.llm.client import LLMResponse, chat

_SYSTEM = (
    "You are a concise logistics operations analyst. "
    "Given a JSON decision payload from a causal / risk-aware optimizer, "
    "produce a 4-6 sentence executive brief. Highlight: (1) the recommended "
    "action, (2) the tail-risk (CVaR) trade-off, (3) at most two caveats. "
    "Do not invent numbers; only reference fields present in the payload."
)


def narrate(payload: dict[str, Any], context: str | None = None) -> LLMResponse:
    user = "Decision payload:\n" + json.dumps(payload, default=str, indent=2)
    if context:
        user += f"\n\nAdditional context:\n{context}"
    return chat(_SYSTEM, user, temperature=0.2, max_tokens=350)
