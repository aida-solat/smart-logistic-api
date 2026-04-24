"""Tests for the LLM narrator + Q&A endpoints (phase 8).

These tests use the offline template fallback (no API key), so they run
deterministically in CI with no network access.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _no_openai_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_narrate_returns_offline_brief() -> None:
    from app.main import app

    client = TestClient(app)
    payload = {
        "mean_cost": 123.4,
        "cvar_95": 210.7,
        "decision": {"move_from_A_to_B": 50},
    }
    r = client.post("/llm/narrate", json={"payload": payload})
    assert r.status_code == 200
    body = r.json()
    assert body["offline"] is True
    assert body["model"] == "offline-template"
    assert "cvar_95" in body["text"] or "mean_cost" in body["text"]


def test_ask_returns_offline_answer() -> None:
    from app.main import app

    client = TestClient(app)
    r = client.post(
        "/llm/ask",
        json={
            "question": "Why is CVaR so high?",
            "payload": {"cvar_95": 210.7, "alpha": 0.95},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["offline"] is True
    assert len(body["text"]) > 0


def test_ask_rejects_empty_question() -> None:
    from app.main import app

    client = TestClient(app)
    r = client.post("/llm/ask", json={"question": "hi", "payload": {}})
    assert r.status_code == 422  # min_length=3
