#!/usr/bin/env python
r"""H1846 — cross-tab each card's RIG verdict against the CANONICAL AUDIT verdict.

Why this exists. In `wf_template_ab.js`'s per-card loop, `rec.card` holds the last
SUCCESSFUL attempt's output, while `rec.final_status` reflects how the card ENDED. Those
can disagree: a card whose attempt 1 was rejected by the controller and whose attempt 2 died
on an API error ends as `worker-null-death`, yet still carries attempt 1's card in
`cards_out` — and `canonical_audit.py`, which scores `cards_out`, may pass it.

That is not necessarily wrong (the audit is the documented authority, the rig's
`would_promote` is a self-report), but it means an arm's audit-clean rate can include cards
its own pipeline refused to ship. A report that quotes the rate without this cross-tab is
hiding which population it is really describing — so the cross-tab is printed, per arm, and
the cards where the two disagree are named.

Usage:
  python src/pilot/h1210/status_vs_audit.py --result F [F ...] --audit F --label ARM
      [--subset key1,key1,...]
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from ab_report import audit_index, load, merge_results       # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--result', nargs='+', required=True)
    ap.add_argument('--audit', required=True)
    ap.add_argument('--worklist', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--subset', default=None, help='comma-separated card ids to isolate')
    a = ap.parse_args()

    worklist = load(a.worklist)
    rows = {r['key1']: r for r in merge_results(a.result)['results']}
    reports = audit_index(load(a.audit), worklist)
    subset = set(x.strip() for x in a.subset.split(',')) if a.subset else None

    tab = collections.Counter()
    disagree = []
    for k, r in sorted(rows.items()):
        if subset is not None and k not in subset:
            continue
        clean = bool(reports.get(k, {}).get('promote_dry'))
        st = r['final_status']
        tab[(st, clean)] += 1
        rig_ok = bool(r.get('would_promote'))
        if rig_ok != clean:
            disagree.append((k, st, 'audit CLEAN' if clean else 'audit REJECT',
                             r.get('attempts'), r.get('controller_calls')))

    print('\n== %s ==%s' % (a.label, ' (subset of %d)' % len(subset) if subset else ''))
    print('| rig final_status | audit clean | audit not clean |')
    print('|---|---:|---:|')
    for st in sorted({s for s, _ in tab}):
        print('| %s | %d | %d |' % (st, tab[(st, True)], tab[(st, False)]))
    n = sum(tab.values())
    ok = sum(v for (_, c), v in tab.items() if c)
    print('| **total** | **%d** | **%d** |' % (ok, n - ok))

    shipped_by_rig = sum(v for (s, c), v in tab.items()
                         if c and s in ('clean-no-review', 'clean-controller-approved'))
    print('\naudit-clean cards the rig ITSELF would ship: %d of %d (%.1f%%)'
          % (shipped_by_rig, n, 100.0 * shipped_by_rig / n) if n else 'no cards')
    print('audit-clean cards the rig REFUSED (null-death / escalated): %d' % (ok - shipped_by_rig))
    if disagree:
        print('\ncards where rig and audit disagree:')
        for row in disagree:
            print('  %-12s rig=%-26s %-13s attempts=%s controller_calls=%s' % row)


if __name__ == '__main__':
    main()
