"""Tests for the operator feedback / override loop (phase 9)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.feedback.schemas import OverrideRecord
from app.feedback.storage import append_override, read_overrides


@pytest.fixture()
def tmp_feedback_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log = tmp_path / "overrides.jsonl"
    monkeypatch.setenv("FEEDBACK_LOG_PATH", str(log))
    return log


def _mk_record(dt: str = "cvar_inventory") -> OverrideRecord:
    return OverrideRecord(
        decision_id="dec-1",
        decision_type=dt,
        state={"stock": [10, 5]},
        ai_recommendation={"move": 3},
        human_decision={"move": 1},
        reason="looked risky",
    )


def test_append_and_read_roundtrip(tmp_feedback_log: Path) -> None:
    append_override(_mk_record())
    append_override(_mk_record("vrp_routing"))
    records = read_overrides()
    assert len(records) == 2
    # newest first
    assert records[0].decision_type == "vrp_routing"


def test_router_post_and_summary(tmp_feedback_log: Path) -> None:
    from app.main import app

    client = TestClient(app)

    payload = _mk_record().model_dump(mode="json")
    r = client.post("/feedback/override", json=payload)
    assert r.status_code == 200
    assert r.json()["decision_id"] == "dec-1"

    r = client.get("/feedback/overrides?limit=10")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get("/feedback/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["by_type"]["cvar_inventory"] == 1
    assert body["with_outcome"] == 0
    assert body["latest"] is not None


def test_filter_by_decision_type(tmp_feedback_log: Path) -> None:
    from app.main import app

    client = TestClient(app)
    client.post("/feedback/override", json=_mk_record("cvar_inventory").model_dump(mode="json"))
    client.post("/feedback/override", json=_mk_record("vrp_routing").model_dump(mode="json"))

    r = client.get("/feedback/overrides?decision_type=vrp_routing")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["decision_type"] == "vrp_routing"
