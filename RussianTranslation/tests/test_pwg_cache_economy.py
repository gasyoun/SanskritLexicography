"""Focused cache-economy contract tests (H2702). Zero paid calls."""
import os
import sys

PILOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'pilot'))
sys.path.insert(0, PILOT)

import cache_baseline_freeze  # noqa: E402
import cache_event_ledger  # noqa: E402
import cache_identity  # noqa: E402
import cache_migrate  # noqa: E402
import cache_reuse  # noqa: E402
import cache_scheduler  # noqa: E402
import prompt_compiler  # noqa: E402


def test_identity():
    assert cache_identity.selftest() == 0


def test_compiler_golden_bytes():
    assert prompt_compiler.selftest() == 0


def test_migrate_round_trip_and_refusal():
    assert cache_migrate.selftest() == 0


def test_ledger_crash_resume_and_torn():
    assert cache_event_ledger.selftest() == 0


def test_reuse_namespace_fence():
    assert cache_reuse.selftest() == 0


def test_scheduler_order():
    assert cache_scheduler.selftest() == 0


def test_baseline_manifest():
    assert cache_baseline_freeze.selftest() == 0
