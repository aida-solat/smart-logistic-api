"""Unified LLM client with graceful offline fallback.

If ``OPENAI_API_KEY`` is set, we route requests to OpenAI's chat-completions
API. Otherwise, we return a deterministic template-based response so the
endpoint never hard-fails in dev / CI.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    model: str
    offline: bool


def _offline_fallback(system: str, user: str) -> LLMResponse:
    """Template-based narrative when no LLM backend is configured."""
    snippet = user[:400].replace("\n", " ")
    text = (
        "[offline narrator] "
        f"{system.split('.')[0]}. "
        f"Observation: {snippet}"
    )
    return LLMResponse(text=text, model="offline-template", offline=True)


def chat(
    system: str,
    user: str,
    *,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 400,
) -> LLMResponse:
    """Run a single chat turn. Falls back to a template if no API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.info("LLM: no OPENAI_API_KEY — using offline template.")
        return _offline_fallback(system, user)

    try:
        from openai import OpenAI  # lazy import
    except ImportError:
        logger.warning("LLM: openai package not installed — offline fallback.")
        return _offline_fallback(system, user)

    client = OpenAI(api_key=api_key)
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = (resp.choices[0].message.content or "").strip()
        return LLMResponse(text=text, model=model, offline=False)
    except Exception as exc:  # pragma: no cover — network/billing edge cases
        logger.warning("LLM call failed (%s) — falling back.", exc)
        return _offline_fallback(system, user)
