"""Q&A over a specific decision payload."""
from __future__ import annotations

import json
from typing import Any

from app.llm.client import LLMResponse, chat

_SYSTEM = (
    "You answer operator questions about a specific logistics decision. "
    "Ground every claim in the provided JSON payload. If the answer cannot "
    "be inferred from the payload, say so explicitly. Keep answers under "
    "150 words."
)


def ask(question: str, payload: dict[str, Any]) -> LLMResponse:
    user = (
        "Decision payload:\n"
        + json.dumps(payload, default=str, indent=2)
        + f"\n\nOperator question: {question}"
    )
    return chat(_SYSTEM, user, temperature=0.1, max_tokens=300)
