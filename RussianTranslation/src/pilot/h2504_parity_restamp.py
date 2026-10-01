#!/usr/bin/env python
"""Re-stamp parity entries after the H2504 router hardening CI repair.

This driver is retained as review evidence because the ledger hash update is only valid
after its existing verdicts have been re-derived.  The drift has four independent causes:

* ``window_selftest.py`` now compares the language-neutral process timeout with the shared
  600000 ms execution-contract constant.  It reads no target field and changes no RU/EN
  branch, so every existing verdict tracking that common test module still stands.
* ``max_account_orchestrator_selftest.py`` only makes the depth-three process-tree fixture
  reliable on cold machines.  Account process termination is shared by every language.
* H2439 retargeted the already parameterized DeepSeek comparison arm to a new default model
  and prices.  The generator remains selected before, and independently of, target language.
* H2410 adds Sanskrit synonym and English sense evidence to the RU corpus card.  The existing
  ``corpus_gate_evidence_markers_fl7_h321`` INTENTIONAL-DIVERGENCE verdict therefore still
  holds: this remains RU editorial evidence and does not claim an EN twin.

The new Griffith alignment auditor is not re-stamped here.  LANG_PARITY classifies it as a
read-only diagnostic exemption: it reads Sanskrit and English witnesses and prints a report,
but cannot translate, mutate a card/store, or produce a promotion verdict.

H4408: mechanics moved to parity_restamp.py (drift census + in-process N-id hash refresh).
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parity_restamp as pr  # noqa: E402


def main():
    ids = pr.drifted_ids()
    print('re-stamping %d re-derived parity entries' % len(ids))
    pr.update_hashes(ids)
    return 0


if __name__ == '__main__':
    sys.exit(main())
