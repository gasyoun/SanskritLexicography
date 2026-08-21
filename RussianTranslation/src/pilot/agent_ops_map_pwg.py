#!/usr/bin/env python
r"""Vendored copy of Uprava/tools/agent_ops/map_pwg.py (canon).

PWG worker must not import Uprava at runtime (different repo, Windows path).
Keep this table in comment-sync with:

  https://github.com/gasyoun/Uprava/blob/main/tools/agent_ops/map_pwg.py
  https://github.com/gasyoun/Uprava/blob/main/docs/ARCHITECTURE_UPRAVA_AGENT_OPS.md

Do not retune HARD_TIMEOUT_MS or $2 here. Additive ``agent_ops_code`` only.
"""
from __future__ import annotations

# Existing bounded_supervisor.STOP_* values — do not rename them.
PWG_STOP_TO_CODE = {
    "budget": "A4",
    "call_count": "A1",
    "consecutive_empty": "A2",
    "cost_unevaluable": "A6",
    "window_count": "A5",
    "clean_target": None,
    "clean_quota": None,
}

_TIMEOUT_MARKERS = ("timeout", "kill", "kill_ceil", "hard_timeout")


def map_pwg_stop(stop_reason, usage=None):
    """Return A1–A6 or None. Missing stop_reason → None, never 0."""
    if stop_reason in PWG_STOP_TO_CODE:
        return PWG_STOP_TO_CODE[stop_reason]
    usage = usage if isinstance(usage, dict) else {}
    classification = str(usage.get("classification") or usage.get("kill_class") or "").lower()
    if any(m in classification for m in _TIMEOUT_MARKERS):
        return "A3"
    if stop_reason and str(stop_reason).lower() in _TIMEOUT_MARKERS:
        return "A3"
    return None
