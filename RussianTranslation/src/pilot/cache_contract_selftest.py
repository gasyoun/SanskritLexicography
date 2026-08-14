#!/usr/bin/env python
"""Stable offline entry point for the H2702 cache-economy contract.

    python src/pilot/cache_contract_selftest.py

Zero paid/provider calls. Runs identity, compiler, migration, ledger,
reuse, scheduler, and the golden-byte / refusal fixtures.
"""
from __future__ import annotations

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import cache_event_ledger  # noqa: E402
import cache_identity  # noqa: E402
import cache_migrate  # noqa: E402
import cache_reuse  # noqa: E402
import cache_scheduler  # noqa: E402
import prompt_compiler  # noqa: E402


def main():
    cache_identity.selftest()
    prompt_compiler.selftest()
    cache_migrate.selftest()
    cache_event_ledger.selftest()
    cache_reuse.selftest()
    cache_scheduler.selftest()
    print('cache_contract_selftest: PASS (6 modules)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
