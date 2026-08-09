#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for H2230/H2255 instrumentation_coverage post_cut/historical split.

Sonnet override PR #1080 claimed unit verification against a synthetic fixture
but did not commit a pin. This selftest is the Grok dual-run residual's net-new
regression pin for the honest coverage split.

Run from repo root:
  python progress_dashboard/kitchen_instrumentation_selftest.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kitchen_slices as ks  # noqa: E402


def test_empty_not_measured():
    out = ks.instrumentation_coverage([])
    assert out["measured"] is False
    assert "post_cut" not in out
    print("PASS: test_empty_not_measured")


def test_historical_only_no_source_key():
    """Rows without wall_clock_source are historical — null wall-clock is expected."""
    rows = [
        {"production_metrics": {"wall_clock_minutes": None}, "gen_model": None},
        {"production_metrics": {}, "gen_model": None},
        {"production_metrics": None, "gen_model": None},
    ]
    out = ks.instrumentation_coverage(rows)
    assert out["measured"] is True
    assert out["windows"] == 3
    assert out["wall_clock_present"] == 0
    assert out["wall_clock_coverage_pct"] == 0.0
    assert out["historical"]["windows"] == 3
    assert out["historical"]["wall_clock_present"] == 0
    assert out["post_cut"]["windows"] == 0
    # empty post_cut bucket: pct is None (n=0), not 0.0
    assert out["post_cut"]["wall_clock_coverage_pct"] is None
    print("PASS: test_historical_only_no_source_key")


def test_post_cut_full_wall_clock():
    """post_cut rows with wall_clock_source + minutes > 0 → 100% honest health."""
    rows = [
        {
            "production_metrics": {
                "wall_clock_minutes": 6.1,
                "wall_clock_source": "derived_mtime",
                "max_total_tokens": 12000,
            },
            "gen_model": "claude-sonnet-5",
        },
        {
            "production_metrics": {
                "wall_clock_minutes": 4.0,
                "wall_clock_source": "cli",
            },
            "gen_model": "claude-sonnet-5",
        },
    ]
    out = ks.instrumentation_coverage(rows)
    assert out["post_cut"]["windows"] == 2
    assert out["post_cut"]["wall_clock_present"] == 2
    assert out["post_cut"]["wall_clock_coverage_pct"] == 100.0
    assert out["post_cut"]["token_metrics_present"] == 1
    assert out["post_cut"]["token_coverage_pct"] == 50.0
    assert out["historical"]["windows"] == 0
    assert out["wall_clock_coverage_pct"] == 100.0
    print("PASS: test_post_cut_full_wall_clock")


def test_post_cut_gap_vs_historical_null():
    """Honest split: post_cut null wall-clock is a gap; historical null is not.

    Blended coverage would hide a real post_cut instrumentation failure behind
    a large historical denominator — the Fail= condition H2230 named.
    """
    rows = [
        # historical — pre-instrumentation, legitimately empty
        {"production_metrics": {}},
        {"production_metrics": {"wall_clock_minutes": None}},
        {"production_metrics": None},
        # post_cut — instrumented path, one healthy + one real gap
        {
            "production_metrics": {
                "wall_clock_minutes": 5.0,
                "wall_clock_source": "derived_mtime",
                "max_output_tokens": 8000,
            }
        },
        {
            "production_metrics": {
                "wall_clock_minutes": None,
                "wall_clock_source": "unavailable",
            }
        },
    ]
    out = ks.instrumentation_coverage(rows)
    assert out["windows"] == 5
    # blended: 1/5 = 20% — the dishonest number if used alone
    assert out["wall_clock_present"] == 1
    assert out["wall_clock_coverage_pct"] == 20.0
    # post_cut honest health: 1/2 = 50% (the gap is visible)
    assert out["post_cut"]["windows"] == 2
    assert out["post_cut"]["wall_clock_present"] == 1
    assert out["post_cut"]["wall_clock_coverage_pct"] == 50.0
    assert out["post_cut"]["token_metrics_present"] == 1
    assert out["post_cut"]["token_coverage_pct"] == 50.0
    # historical: 0/3, expected not a gap
    assert out["historical"]["windows"] == 3
    assert out["historical"]["wall_clock_present"] == 0
    assert out["historical"]["wall_clock_coverage_pct"] == 0.0
    assert "wall_clock_source" in (out.get("note") or "")
    print("PASS: test_post_cut_gap_vs_historical_null")


def test_unavailable_source_still_post_cut():
    """wall_clock_source=unavailable (null minutes) is post_cut, not historical."""
    rows = [
        {
            "production_metrics": {
                "wall_clock_minutes": None,
                "wall_clock_source": "unavailable",
            }
        }
    ]
    out = ks.instrumentation_coverage(rows)
    assert out["post_cut"]["windows"] == 1
    assert out["post_cut"]["wall_clock_present"] == 0
    assert out["historical"]["windows"] == 0
    print("PASS: test_unavailable_source_still_post_cut")


def test_zero_minutes_not_present():
    """wall_clock_minutes == 0 does not count as present (same rule as pre-H2230)."""
    rows = [
        {
            "production_metrics": {
                "wall_clock_minutes": 0,
                "wall_clock_source": "cli",
            }
        }
    ]
    out = ks.instrumentation_coverage(rows)
    assert out["post_cut"]["wall_clock_present"] == 0
    assert out["post_cut"]["wall_clock_coverage_pct"] == 0.0
    print("PASS: test_zero_minutes_not_present")


def main():
    test_empty_not_measured()
    test_historical_only_no_source_key()
    test_post_cut_full_wall_clock()
    test_post_cut_gap_vs_historical_null()
    test_unavailable_source_still_post_cut()
    test_zero_minutes_not_present()
    print("ALL PASS: kitchen_instrumentation_selftest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
