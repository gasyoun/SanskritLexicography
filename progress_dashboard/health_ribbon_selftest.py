#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for B3 residual (H2240): canonical `health_probe_log.jsonl` writer/reader.

Run from repo root:
  python progress_dashboard/health_ribbon_selftest.py

Pins:
  - health_ribbon prefers `health_probe_log.jsonl` exclusively when present
  - a sibling per-account glob file present alongside it is ignored (no double count)
  - falls back to the old per-account glob scrape when the canonical file is absent
  - degrades quietly (measured=False) when neither is present
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


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


def _row(ts, elapsed_ms, account="c4"):
    return {
        "ts": ts,
        "event": "probe_call",
        "purpose": "measured",
        "elapsed_ms": elapsed_ms,
        "account": account,
        "model": "claude-sonnet-5",
    }


def test_canonical_preferred_exclusively():
    with tempfile.TemporaryDirectory() as td:
        pilot_out = Path(td)
        _write_jsonl(pilot_out / "health_probe_log.jsonl", [
            _row("2026-08-03T10:00:00Z", 40_000),
            _row("2026-08-03T11:00:00Z", 70_000),
        ])
        # A stale/legacy per-account file sits alongside it — must NOT be double-counted.
        _write_jsonl(pilot_out / "h963_c4_gate0_probe_events.jsonl", [
            _row("2026-08-01T09:00:00Z", 20_000),
        ])
        out = ks.health_ribbon(pilot_out)
        assert out["measured"] is True
        assert out["probes"] == 2, out
        assert out["last_verdict"] == "NO-GO", out
    print("PASS: test_canonical_preferred_exclusively")


def test_fallback_glob_when_canonical_absent():
    with tempfile.TemporaryDirectory() as td:
        pilot_out = Path(td)
        _write_jsonl(pilot_out / "h963_c4_gate0_probe_events.jsonl", [
            _row("2026-08-01T09:00:00Z", 20_000),
        ])
        out = ks.health_ribbon(pilot_out)
        assert out["measured"] is True
        assert out["probes"] == 1, out
        assert out["last_verdict"] == "GO", out
    print("PASS: test_fallback_glob_when_canonical_absent")


def test_missing_degrades_quietly():
    with tempfile.TemporaryDirectory() as td:
        out = ks.health_ribbon(Path(td))
        assert out["measured"] is False
    print("PASS: test_missing_degrades_quietly")


def main():
    test_canonical_preferred_exclusively()
    test_fallback_glob_when_canonical_absent()
    test_missing_degrades_quietly()
    print("ALL PASS: health_ribbon_selftest (H2240 B3 residual)")


if __name__ == "__main__":
    main()
