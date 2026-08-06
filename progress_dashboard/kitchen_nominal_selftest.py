#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for H2238/H2275 B7 nominal + medium-50 burn-down.

Sonnet override PR #1119 shipped the burn-down fields + UI. This selftest is
the Grok dual-run residual's regression pin: medium-50 live measure (H317 keys
∩ store key1), structured pause_reason (code + detail + docs), and eta_nominal
burn-down shape.

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


def _write_store(path: Path, key1s: list[str]) -> None:
    rows = []
    for k in key1s:
        rows.append(
            json.dumps(
                {
                    "key1": k,
                    "ru": "t",
                    "provenance": {"generated_at": "2026-07-09T12:00:00Z"},
                },
                ensure_ascii=False,
            )
        )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _write_m50(path: Path, keys: list[str]) -> None:
    path.write_text(
        json.dumps({"n_selected": len(keys), "keys": keys}, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_nominal_wl(path: Path, promoted: list[str], scope: int, remaining: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "already_promoted": promoted,
                "already_promoted_count": len(promoted),
                "nominal_candidates": scope,
                "runnable_remaining": remaining,
                "runnable_count": len(remaining),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_measure_missing_worklist_falls_back():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        (rt / "src" / "pilot").mkdir(parents=True)
        out = ks.measure_medium50_band(rt)
        assert out["measured"] is False
        assert out["promoted"] == ks.MEDIUM50_FALLBACK_PROMOTED
        assert out["total"] == ks.MEDIUM50_FALLBACK_TOTAL
        assert out["pause_reason"]["code"] == "killgate_cascade"
        assert "detail" in out["pause_reason"]
        assert out["status"] == out["pause_reason"]["label"]
    print("PASS: test_measure_missing_worklist_falls_back")


def test_measure_live_intersection():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        pilot = rt / "src" / "pilot"
        pilot.mkdir(parents=True)
        store = rt / "src" / "pwg_ru_translated.jsonl"
        m50 = pilot / "H317_medium50_worklist.08.07.26.json"
        _write_m50(m50, ["a", "b", "c", "d"])
        _write_store(store, ["a", "c", "z"])  # 2 of 4 in band
        out = ks.measure_medium50_band(rt)
        assert out["measured"] is True
        assert out["promoted"] == 2
        assert out["total"] == 4
        assert out["pause_reason"]["code"] == "killgate_cascade"
        assert out["pause_reason"]["docs"] == ["H437", "H442", "H462"]
    print("PASS: test_measure_live_intersection")


def test_measure_explicit_path():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        (rt / "src").mkdir(parents=True)
        store = rt / "src" / "pwg_ru_translated.jsonl"
        m50 = Path(td) / "custom_m50.json"
        _write_m50(m50, ["x", "y"])
        _write_store(store, ["x"])
        out = ks.measure_medium50_band(rt, medium50_wl_path=m50)
        assert out["measured"] is True
        assert out["promoted"] == 1
        assert out["total"] == 2
    print("PASS: test_measure_explicit_path")


def test_pause_reason_not_prose_only():
    pr = ks.MEDIUM50_PAUSE_REASON
    assert isinstance(pr, dict)
    assert pr.get("code")
    assert pr.get("label")
    assert pr.get("detail")
    assert pr.get("docs")
    assert pr.get("doc_urls")
    # must not be a bare string masquerading as structure
    assert not isinstance(pr, str)
    print("PASS: test_pause_reason_not_prose_only")


def test_eta_nominal_burn_down_shape():
    with tempfile.TemporaryDirectory() as td:
        rt = Path(td)
        wl = rt / "src" / "pilot" / "output" / "nominal_batch_worklist.json"
        store = rt / "src" / "pwg_ru_translated.jsonl"
        m50 = rt / "src" / "pilot" / "H317_medium50_worklist.08.07.26.json"
        promoted = ["k1", "k2"]
        remaining = ["r1", "r2", "r3"]
        _write_nominal_wl(wl, promoted=promoted, scope=100, remaining=remaining)
        _write_store(store, ["k1", "k2", "m50a"])
        _write_m50(m50, ["m50a", "m50b"])
        out = ks.eta_nominal(rt)
        assert out["measured"] is True
        assert out["nominal_promoted"] == 2
        assert out["nominal_scope"] == 100
        assert out["nominal_remaining"] == 3
        assert out["nominal_pct"] == 2.0
        assert "remaining" not in out  # kitchen uses nominal_* prefix
        m = out["medium50"]
        assert m["measured"] is True
        assert m["promoted"] == 1
        assert m["total"] == 2
        assert m["pause_reason"]["code"] == "killgate_cascade"
        assert m["status"] == m["pause_reason"]["label"]
    print("PASS: test_eta_nominal_burn_down_shape")


def test_eta_nominal_missing_worklist():
    with tempfile.TemporaryDirectory() as td:
        out = ks.eta_nominal(Path(td))
        assert out == {"measured": False}
    print("PASS: test_eta_nominal_missing_worklist")


def main() -> int:
    test_measure_missing_worklist_falls_back()
    test_measure_live_intersection()
    test_measure_explicit_path()
    test_pause_reason_not_prose_only()
    test_eta_nominal_burn_down_shape()
    test_eta_nominal_missing_worklist()
    print("ALL PASS kitchen_nominal_selftest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
