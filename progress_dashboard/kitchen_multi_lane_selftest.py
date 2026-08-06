#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for H2231 B8 multi-lane mix (gen_model / host / profile).

Run from repo root:
  python progress_dashboard/kitchen_multi_lane_selftest.py
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
    out = ks.multi_lane_mix([])
    assert out["measured"] is False
    assert out.get("multi_lane") is False
    print("PASS: test_empty_not_measured")


def test_single_lane_fixture():
    rows = [
        {"gen_model": "claude-sonnet-5", "host": "desk-a", "profile": "c4"},
        {"gen_model": "claude-sonnet-5", "host": "desk-a", "profile": "c4"},
        {"gen_model": None, "host": None, "profile": None},
    ]
    out = ks.multi_lane_mix(rows)
    assert out["measured"] is True
    assert out["windows"] == 3
    assert out["gen_model_present"] == 2
    assert out["host_present"] == 2
    assert out["profile_present"] == 2
    assert out["gen_models"] == {"claude-sonnet-5": 2}
    assert out["hosts"] == {"desk-a": 2}
    assert out["profiles"] == {"c4": 2}
    assert out["multi_lane"] is False
    assert out["distinct_models"] == 1
    print("PASS: test_single_lane_fixture")


def test_multi_lane_fixture():
    rows = [
        {"gen_model": "claude-sonnet-5", "host": "desk-a", "profile": "c4"},
        {"gen_model": "claude-fable-5", "host": "desk-b", "profile": "c2"},
        {"gen_model": "claude-sonnet-5", "host": "desk-a", "profile": "c4"},
    ]
    out = ks.multi_lane_mix(rows)
    assert out["measured"] is True
    assert out["multi_lane"] is True
    assert out["distinct_hosts"] == 2
    assert out["distinct_profiles"] == 2
    assert out["distinct_models"] == 2
    assert out["gen_models"]["claude-sonnet-5"] == 2
    assert out["gen_models"]["claude-fable-5"] == 1
    assert out["hosts"]["desk-a"] == 2
    assert out["profiles"]["c4"] == 2
    print("PASS: test_multi_lane_fixture")


def test_profile_slot_alias():
    rows = [{"profile_slot": "c1", "gen_model": "m", "host": "h"}]
    out = ks.multi_lane_mix(rows)
    assert out["profiles"] == {"c1": 1}
    assert out["profile_present"] == 1
    print("PASS: test_profile_slot_alias")


def main():
    test_empty_not_measured()
    test_single_lane_fixture()
    test_multi_lane_fixture()
    test_profile_slot_alias()
    print("ALL PASS: kitchen_multi_lane_selftest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
