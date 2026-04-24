"""Pydantic schemas for the LLM narrator / Q&A endpoints."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class NarrateRequest(BaseModel):
    payload: dict[str, Any] = Field(
        ..., description="Optimizer / causal output to summarise."
    )
    context: Optional[str] = Field(
        None, description="Optional extra domain context (e.g. SLA tier)."
    )


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    payload: dict[str, Any] = Field(
        ..., description="Decision payload the question is about."
    )


class LLMAnswer(BaseModel):
    text: str
    model: str
    offline: bool = Field(
        ..., description="True if the template fallback was used (no API key)."
    )
