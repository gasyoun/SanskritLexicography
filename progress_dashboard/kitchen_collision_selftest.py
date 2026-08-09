#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for OPT-8 / H2229 kitchen lease-collision banner (observability only).

Run from repo root:
  python progress_dashboard/kitchen_collision_selftest.py

Pins:
  - collision_guard blocks on fixture events
  - banner + operator one-liner present
  - empty events → blocked=false
  - emit_collision writes a kitchen-readable type
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "RussianTranslation" / "src" / "pilot"))

import kitchen_slices as ks  # noqa: E402
from dashboard_events import (  # noqa: E402
    OPERATOR_ONE_LINER_COLLISION,
    emit_collision,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


def test_fixture_blocks_banner():
    fixture = HERE / "examples" / "collision_events.example.jsonl"
    assert fixture.exists(), "example fixture missing: %s" % fixture
    out = ks.collision_guard(fixture)
    assert out["measured"] is True
    assert out["blocked"] is True
    assert out["banner"] == "DO NOT START A SECOND PAID WINDOW"
    assert out["collision_count"] >= 2
    assert out["operator_one_liner"]
    assert "DO NOT start a second paid window" in out["operator_one_liner"]
    assert out["last"] is not None
    assert out["recent"]
    kinds = out.get("kind_counts") or {}
    assert kinds, "expected kind_counts from fixture"
    print("PASS: test_fixture_blocks_banner")


def test_empty_not_blocked():
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td) / "empty.jsonl"
        empty.write_text("", encoding="utf-8")
        out = ks.collision_guard(empty)
        assert out["blocked"] is False
        assert out["banner"] is None
        assert out["collision_count"] == 0
        assert out["operator_one_liner"]
    print("PASS: test_empty_not_blocked")


def test_missing_events_degrades():
    missing = Path("/nonexistent/dashboard_events_h2229.jsonl")
    out = ks.collision_guard(missing)
    assert out["blocked"] is False
    assert out["collision_count"] == 0
    # measured may be false when nothing exists
    print("PASS: test_missing_events_degrades")


def test_emit_collision_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "events.jsonl"
        rec = emit_collision(
            "occupied_keys_overlap",
            root="lease-selftest",
            summary="selftest overlap agni~~h0",
            source="kitchen_collision_selftest",
            data={"overlap_count": 1, "overlap_sample": ["agni~~h0"]},
            log_path=str(log),
        )
        assert rec["type"] == "lease_collision"
        assert rec["state"] == "blocked_second_window"
        assert "DO NOT START A SECOND PAID WINDOW" in rec["summary"]
        out = ks.collision_guard(log)
        assert out["blocked"] is True
        assert out["last"]["root"] == "lease-selftest"
        assert out["last"]["kind"] == "occupied_keys_overlap"
    print("PASS: test_emit_collision_roundtrip")


def test_summary_regex_legacy():
    """Legacy stderr-style summaries still surface without a typed event."""
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "legacy.jsonl"
        _write_jsonl(
            log,
            [
                {
                    "ts": "2026-08-02T00:00:00Z",
                    "source": "operator",
                    "type": "note",
                    "level": "error",
                    "root": "legacy-root",
                    "summary": "occupied-keys guard: SECOND paid window refused",
                    "data": {},
                }
            ],
        )
        out = ks.collision_guard(log)
        assert out["blocked"] is True
        assert out["last"]["root"] == "legacy-root"
    print("PASS: test_summary_regex_legacy")


def test_one_liner_constant_aligned():
    assert "DO NOT start a second paid window" in OPERATOR_ONE_LINER_COLLISION
    assert "DO NOT start a second paid window" in ks.OPERATOR_ONE_LINER_COLLISION
    print("PASS: test_one_liner_constant_aligned")


def main():
    test_fixture_blocks_banner()
    test_empty_not_blocked()
    test_missing_events_degrades()
    test_emit_collision_roundtrip()
    test_summary_regex_legacy()
    test_one_liner_constant_aligned()
    print("ALL PASS: kitchen_collision_selftest (H2229 OPT-8)")


if __name__ == "__main__":
    main()
