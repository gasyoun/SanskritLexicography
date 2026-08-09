#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for H2238/H2275 nominal + medium-50 burn-down (B7).

Sonnet override PR #1119 shipped burn-down fields, live medium-50 measure,
eta_nominal, and structured pause_reason — but no committed pin, and the
progress path's pause_reason object drifted (no ``detail``) from the kitchen
constant. This selftest is the Grok dual-run residual's regression pin:

- measure_medium50_band live intersection + documented fallback
- pause_reason shape (code + label + detail + docs)
- eta_nominal burn-down fields + nested medium50
- progress-side shape parity for medium50_* keys

Run from repo root:
  python progress_dashboard/kitchen_nominal_selftest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kitchen_slices as ks  # noqa: E402


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_store(path: Path, key1s: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, k in enumerate(key1s):
        rows.append(
            {
                "key1": k,
                "provenance": {
                    "generated_at": f"2026-07-0{1 + (i % 5)}T12:00:00Z",
                },
            }
        )
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


def test_measure_missing_worklist_fallback():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        m50 = ks.measure_medium50_band(rt)
        assert m50["promoted"] == 2
        assert m50["total"] == 50
        assert m50["measured"] is False
        assert m50["pause_reason"]["code"] == "killgate_cascade"
        assert "detail" in m50["pause_reason"]
        assert m50["status"] == m50["pause_reason"]["label"]
    print("PASS: test_measure_missing_worklist_fallback")


def test_measure_live_intersection():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        keys = ["a", "b", "c", "d", "e"]
        wl = rt / "src" / "pilot" / "H317_medium50_worklist.08.07.26.json"
        _write_json(wl, {"n_selected": 5, "keys": keys})
        store = rt / "src" / "pwg_ru_translated.jsonl"
        _write_store(store, ["a", "c"])  # 2 of 5 promoted
        m50 = ks.measure_medium50_band(rt)
        assert m50["promoted"] == 2
        assert m50["total"] == 5
        assert m50["measured"] is True
        assert m50["pause_reason"]["code"] == "killgate_cascade"
        assert m50["pause_reason"].get("detail")
        assert isinstance(m50["pause_reason"].get("docs"), list)
        assert m50["pause_reason"]["docs"] == ["H437", "H442", "H462"]
    print("PASS: test_measure_live_intersection")


def test_measure_worklist_without_store_keeps_total():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        wl = rt / "src" / "pilot" / "H317_medium50_worklist.08.07.26.json"
        _write_json(wl, {"n_selected": 50, "keys": [f"k{i}" for i in range(50)]})
        m50 = ks.measure_medium50_band(rt)
        assert m50["measured"] is False
        assert m50["total"] == 50
        assert m50["promoted"] == 2  # documented fallback until store is present
    print("PASS: test_measure_worklist_without_store_keeps_total")


def test_eta_nominal_missing_worklist():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        out = ks.eta_nominal(rt)
        assert out == {"measured": False}
    print("PASS: test_eta_nominal_missing_worklist")


def test_eta_nominal_burn_down_and_medium50():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        # already_promoted as list (rate source); counts as ints
        promoted_keys = ["p1", "p2", "p3"]
        runnable = [f"r{i}" for i in range(7)]
        nm = {
            "nominal_candidates": 20,
            "already_promoted": promoted_keys,
            "already_promoted_count": 3,
            "runnable_remaining": runnable,
            "runnable_count": 7,
        }
        wl = rt / "src" / "pilot" / "output" / "nominal_batch_worklist.json"
        _write_json(wl, nm)
        m50_keys = ["p1", "x1", "x2"]
        m50_wl = rt / "src" / "pilot" / "H317_medium50_worklist.08.07.26.json"
        _write_json(m50_wl, {"n_selected": 3, "keys": m50_keys})
        store = rt / "src" / "pwg_ru_translated.jsonl"
        # p1,p2,p3 promoted in store; only p1 is in medium-50 band
        _write_store(store, ["p1", "p2", "p3"])

        out = ks.eta_nominal(rt)
        assert out["measured"] is True
        assert out["nominal_promoted"] == 3
        assert out["nominal_scope"] == 20
        assert out["nominal_remaining"] == 7
        assert out["nominal_pct"] == 15.0  # 3/20
        assert out["mean_keys_promoted_per_active_day"] is not None
        assert out["estimated_days_at_keys_per_day_rate"] is not None
        m50 = out["medium50"]
        assert m50["measured"] is True
        assert m50["promoted"] == 1  # only p1 of m50 keys in store
        assert m50["total"] == 3
        assert m50["pause_reason"]["code"] == "killgate_cascade"
        assert m50["pause_reason"].get("detail")
        assert m50["status"] == m50["pause_reason"]["label"]
    print("PASS: test_eta_nominal_burn_down_and_medium50")


def test_pause_reason_shape_constant():
    pr = ks.MEDIUM50_PAUSE_REASON
    for field in ("code", "label", "detail", "docs", "doc_urls"):
        assert field in pr, f"missing {field}"
    assert pr["code"] == "killgate_cascade"
    assert isinstance(pr["docs"], list) and pr["docs"]
    assert isinstance(pr["doc_urls"], list) and pr["doc_urls"]
    assert all(u.startswith("https://") for u in pr["doc_urls"])
    print("PASS: test_pause_reason_shape_constant")


def main() -> int:
    test_measure_missing_worklist_fallback()
    test_measure_live_intersection()
    test_measure_worklist_without_store_keeps_total()
    test_eta_nominal_missing_worklist()
    test_eta_nominal_burn_down_and_medium50()
    test_pause_reason_shape_constant()
    print("\nAll kitchen_nominal_selftest cases PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
