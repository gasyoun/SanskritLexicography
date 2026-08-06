#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for H2241/H2268 progress_kitchen_slice field mapping.

Sonnet override PR #1112 shipped kitchen_slice() inline in
build_progress_data.py with no committed pin. This selftest is the Grok
dual-run residual's regression pin for the pure mapping (field selection,
GO/NO-GO encoding, current-idle conversion, review-approved non-duplication).

Run from repo root:
  python progress_dashboard/kitchen_progress_slice_selftest.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kitchen_slices as ks  # noqa: E402


def test_none_not_measured():
    out = ks.progress_kitchen_slice(None)
    assert out["measured"] is False
    assert "yield_clean_pct" not in out
    print("PASS: test_none_not_measured")


def test_empty_payload_measured_nulls():
    """File present but sections missing → measured, fields None (not crash)."""
    out = ks.progress_kitchen_slice({})
    assert out["measured"] is True
    assert out["yield_clean_pct"] is None
    assert out["health_last_verdict"] is None
    assert out["health_last_go"] is None
    assert out["idle_hours"] is None
    assert out["current_idle_hours"] is None
    print("PASS: test_empty_payload_measured_nulls")


def test_full_kitchen_payload_matches_h2241_sample():
    """Values mirror the H2241 verify row (yield 0.63, NO-GO, idle 430.54)."""
    kd = {
        "yield_quality": {"clean_window_pct": 0.63, "clean_windows": 3},
        "health": {"last_verdict": "NO-GO"},
        "idle": {
            "total_idle_hours": 430.54,
            "current_idle_seconds": 328080,
        },
    }
    out = ks.progress_kitchen_slice(kd)
    assert out["measured"] is True
    assert out["yield_clean_pct"] == 0.63
    assert out["health_last_verdict"] == "NO-GO"
    assert out["health_last_go"] == 0
    assert out["idle_hours"] == 430.54
    assert out["current_idle_hours"] == 91.13  # 328080 / 3600
    print("PASS: test_full_kitchen_payload_matches_h2241_sample")


def test_go_verdict_encodes_one():
    out = ks.progress_kitchen_slice(
        {
            "health": {"last_verdict": "GO"},
            "yield_quality": {},
            "idle": {},
        }
    )
    assert out["health_last_go"] == 1
    assert out["health_last_verdict"] == "GO"
    print("PASS: test_go_verdict_encodes_one")


def test_unknown_verdict_is_none_not_zero():
    """Non-GO/NO-GO must not silently map to 0 (that would fake NO-GO)."""
    out = ks.progress_kitchen_slice({"health": {"last_verdict": "DEGRADED"}})
    assert out["health_last_go"] is None
    print("PASS: test_unknown_verdict_is_none_not_zero")


def test_no_kitchen_review_approved_field():
    """H2241 'review approved' is store `approved`, not a kitchen_* invent."""
    out = ks.progress_kitchen_slice(
        {
            "yield_quality": {"clean_window_pct": 1.0},
            "store": {"review": {"approved": 99}},  # must not be projected
            "review": {"approved": 99},
        }
    )
    assert "review_approved" not in out
    assert "approved" not in out
    assert out["yield_clean_pct"] == 1.0
    print("PASS: test_no_kitchen_review_approved_field")


def test_malformed_section_types():
    """Non-dict sections treated as empty (no TypeError)."""
    out = ks.progress_kitchen_slice(
        {
            "yield_quality": "broken",
            "health": ["GO"],
            "idle": 12,
        }
    )
    assert out["measured"] is True
    assert out["yield_clean_pct"] is None
    assert out["health_last_go"] is None
    assert out["current_idle_hours"] is None
    print("PASS: test_malformed_section_types")


def main() -> int:
    test_none_not_measured()
    test_empty_payload_measured_nulls()
    test_full_kitchen_payload_matches_h2241_sample()
    test_go_verdict_encodes_one()
    test_unknown_verdict_is_none_not_zero()
    test_no_kitchen_review_approved_field()
    test_malformed_section_types()
    print("All kitchen_progress_slice_selftest cases passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
