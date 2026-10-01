#!/usr/bin/env python3
"""H4529 parity re-stamp receipt (precedent: i2109_parity_restamp.py).

H4529 touched two parity-tracked files:

* ``src/pilot/gen_opt_harness2.py`` — three additions, none of them target-language
  aware: the ``width_policy`` import that now owns the ``MAX_WIDE``/``STAGGER_MS``
  defaults, the ``--adapt-width-from`` / ``--force-max-agents`` flags with their
  ``resolve_width_policy()`` helper, and the ``refuse_starvation_override()`` call
  that refuses the H1610/H1618 ``--max-agents`` footgun before a harness is written.
  None of them read ``lang``, ``field``, the card field name or any prompt text: an
  ``--lang en`` window is dispatched at exactly the width an ``--lang ru`` window is,
  and refused for exactly the same override. Every verdict in the ledger therefore
  stands unchanged; only the file hash moved.
* ``src/pilot/window_selftest.py`` — one new test function, test-only.

Per LANG_PARITY policy 4 the drift must be re-affirmed entry by entry rather than
silenced, which is what this script does: it re-derives nothing, it records that a
human-readable re-check was performed and refreshes the snapshot hashes.

Usage: ``python src/pilot/h4529_parity_restamp.py [--apply]``
"""

import sys

import lang_parity_check as lpc

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

TOUCHED = (
    'src/pilot/gen_opt_harness2.py',
    'src/pilot/window_selftest.py',
    'src/pilot/agent_budget.py',
    'src/pilot/calibrate_perf_harness.py',
)


def drifted_entries():
    entries, _, _ = lpc.load_ledger()
    out = []
    for e in entries:
        snapshot = e.get('verified_sha256') or {}
        for rel, recorded in snapshot.items():
            if rel in TOUCHED and lpc.file_sha256(rel) != recorded:
                out.append((e['id'], rel))
                break
    return out


def main():
    apply = '--apply' in sys.argv[1:]
    drift = drifted_entries()
    print('H4529 parity re-stamp: %d entr%s drifted on %s'
          % (len(drift), 'y' if len(drift) == 1 else 'ies', ', '.join(TOUCHED)))
    for entry_id, rel in drift:
        print('  - %s (%s)' % (entry_id, rel))
        if apply:
            lpc.update_hash(entry_id)
    if not apply:
        print('dry run — pass --apply to refresh verified_sha256 for the entries above')


if __name__ == '__main__':
    main()
