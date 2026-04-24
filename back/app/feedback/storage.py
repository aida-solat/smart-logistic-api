"""Append-only JSONL storage for operator overrides.

Path is configurable via `FEEDBACK_LOG_PATH`. Defaults to
`back/data/overrides.jsonl` which is gitignored.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from threading import Lock
from typing import Iterable, Iterator

from app.feedback.schemas import OverrideRecord

_LOCK = Lock()


def _log_path() -> Path:
    p = Path(os.getenv("FEEDBACK_LOG_PATH", "data/overrides.jsonl"))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def append_override(record: OverrideRecord) -> None:
    """Append one record to the JSONL log (thread-safe)."""
    line = record.model_dump_json()
    with _LOCK:
        with _log_path().open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def read_overrides(limit: int | None = None) -> list[OverrideRecord]:
    """Return recent overrides, newest first."""
    path = _log_path()
    if not path.exists():
        return []
    records: list[OverrideRecord] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(OverrideRecord.model_validate_json(line))
            except Exception:
                # Skip malformed lines; do not crash the endpoint.
                continue
    records.reverse()
    if limit is not None:
        records = records[:limit]
    return records


def iter_overrides() -> Iterator[OverrideRecord]:
    """Stream records oldest-first. Useful for retraining jobs."""
    path = _log_path()
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield OverrideRecord.model_validate_json(line)
            except Exception:
                continue
