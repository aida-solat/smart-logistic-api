"""FastAPI router for the LLM narrator + Q&A endpoints (phase 8)."""
from __future__ import annotations

from fastapi import APIRouter

from app.llm.narrator import narrate
from app.llm.qa import ask
from app.llm.schemas import AskRequest, LLMAnswer, NarrateRequest

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/narrate", response_model=LLMAnswer)
def post_narrate(req: NarrateRequest) -> LLMAnswer:
    """Turn a decision payload into a short executive brief."""
    resp = narrate(req.payload, context=req.context)
    return LLMAnswer(text=resp.text, model=resp.model, offline=resp.offline)


@router.post("/ask", response_model=LLMAnswer)
def post_ask(req: AskRequest) -> LLMAnswer:
    """Answer an operator question about a specific decision payload."""
    resp = ask(req.question, req.payload)
    return LLMAnswer(text=resp.text, model=resp.model, offline=resp.offline)
