#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for H2237/H2265 promote_vs_generate (B6).

Sonnet override PR #1107 shipped the kitchen block + UI but no committed pin.
This selftest is the Grok dual-run residual's net-new regression pin:
generation volume vs clean-window outcome, week vs lifetime, and week-scoped
promote-event counts (once promote-typed events exist).

Run from repo root:
  python progress_dashboard/kitchen_promote_selftest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kitchen_slices as ks  # noqa: E402


NOW = datetime(2026, 8, 6, 15, 0, 0, tzinfo=timezone.utc)


def _write_events(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


def test_missing_events_returns_none():
    missing = Path(tempfile.mkdtemp()) / "no_such_events.jsonl"
    assert ks._promote_event_count(missing) is None
    print("PASS: test_missing_events_returns_none")


def test_empty_events_returns_zero():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "events.jsonl"
        p.write_text("", encoding="utf-8")
        assert ks._promote_event_count(p) == 0
    print("PASS: test_empty_events_returns_zero")


def test_promote_match_type_and_summary():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "events.jsonl"
        _write_events(
            p,
            [
                {
                    "ts": "2026-08-01T10:00:00Z",
                    "type": "promote_window",
                    "summary": "ok",
                },
                {
                    "ts": "2026-08-02T10:00:00Z",
                    "type": "audit_end",
                    "summary": "cards promoted to store",
                },
                {
                    "ts": "2026-08-02T11:00:00Z",
                    "type": "audit_end",
                    "summary": "clean close",
                },
            ],
        )
        assert ks._promote_event_count(p) == 2
    print("PASS: test_promote_match_type_and_summary")


def test_promote_week_filter_not_lifetime():
    """Weekly promote_events must not reuse the lifetime total (H2265)."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "events.jsonl"
        _write_events(
            p,
            [
                # older than 7d from NOW
                {
                    "ts": "2026-07-20T10:00:00Z",
                    "type": "promote_window",
                    "summary": "old",
                },
                # inside week
                {
                    "ts": "2026-08-05T10:00:00Z",
                    "type": "promote_window",
                    "summary": "new",
                },
            ],
        )
        since = NOW - timedelta(days=7)
        assert ks._promote_event_count(p) == 2
        assert ks._promote_event_count(p, since=since) == 1
    print("PASS: test_promote_week_filter_not_lifetime")


def test_promote_vs_generate_week_and_lifetime_contrast():
    """Store growth vs clean windows — the B6 acceptance contrast."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "events.jsonl"
        p.write_text("", encoding="utf-8")
        speed = {
            "cards_by_day": {
                "2026-08-05": 100,
                "2026-07-01": 500,
            },
            "total_cards": 600,
        }
        rows = [
            {
                "state": "clean",
                "recorded_at": "2026-08-05T12:00:00Z",
            },
            {
                "state": "failed",
                "recorded_at": "2026-08-04T12:00:00Z",
            },
            {
                "state": "clean",
                "recorded_at": "2026-07-01T12:00:00Z",
            },
            {
                "state": "clean",
                "recorded_at": "2026-06-15T12:00:00Z",
            },
        ]
        out = ks.promote_vs_generate(speed, rows, p, NOW)
        assert out["measured"] is True
        assert out["weekly"]["cards_generated"] == 100
        assert out["weekly"]["clean_windows"] == 1
        assert out["weekly"]["windows_total"] == 2
        assert out["weekly"]["clean_window_pct"] == 50.0
        assert out["weekly"]["promote_events"] == 0
        assert out["lifetime"]["cards_generated"] == 600
        assert out["lifetime"]["clean_windows"] == 3
        assert out["lifetime"]["windows_total"] == 4
        assert out["lifetime"]["clean_window_pct"] == 75.0
        assert out["lifetime"]["promote_events"] == 0
        assert "promoted-outcome proxy" in out["promote_events_source"]
    print("PASS: test_promote_vs_generate_week_and_lifetime_contrast")


def test_empty_not_measured():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "events.jsonl"
        p.write_text("", encoding="utf-8")
        out = ks.promote_vs_generate({}, [], p, NOW)
        assert out["measured"] is False
        assert out["lifetime"]["clean_windows"] == 0
        assert out["lifetime"]["cards_generated"] == 0
    print("PASS: test_empty_not_measured")


def main() -> int:
    test_missing_events_returns_none()
    test_empty_events_returns_zero()
    test_promote_match_type_and_summary()
    test_promote_week_filter_not_lifetime()
    test_promote_vs_generate_week_and_lifetime_contrast()
    test_empty_not_measured()
    print("ALL PASS: kitchen_promote_selftest (H2237/H2265 B6)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
