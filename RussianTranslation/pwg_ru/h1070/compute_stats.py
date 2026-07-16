#!/usr/bin/env python
r"""compute_stats.py - recompute the H1070 adjudication tables from en_gold_adjudication.jsonl.

Numbers in H1070_EN_GOLD_ADJUDICATION_2026-07-17.md and the go/no-go memo are produced
by this script (per /gold-adjudicate: committed next to the data, recomputable).
Wilson 95% CI implementation matches fidelity_aggregate.py's convention (z=1.96).
"""
import collections
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, 'en_gold_adjudication.jsonl'), encoding='utf-8') if l.strip()]
    for tranche in ('pilot', 'fu1', 'ALL'):
        sub = rows if tranche == 'ALL' else [r for r in rows if r['tranche'] == tranche]
        n = len(sub)
        c = collections.Counter(r['ruling'] for r in sub)
        ws = c.get('wrong-sense', 0)
        lo, hi = wilson(ws, n)
        clean = c.get('correct', 0) + c.get('acceptable-variant', 0)
        print('%-5s n=%3d  correct=%3d  acceptable-variant=%3d  wrong-sense=%d  register-mismatch=%d'
              % (tranche, n, c.get('correct', 0), c.get('acceptable-variant', 0),
                 ws, c.get('register-mismatch', 0)))
        print('       clean(C+AV)=%.1f%%  wrong-sense=%.2f%% Wilson95 [%.2f%%, %.2f%%]'
              % (100 * clean / n, 100 * ws / n, 100 * lo, 100 * hi))
    print()
    cls = collections.Counter()
    for r in rows:
        for k in r.get('classes', []):
            cls[(r['tranche'], k)] += 1
    print('classes by tranche:')
    for (t, k), v in sorted(cls.items()):
        print('  %-5s %-28s %d' % (t, k, v))
    print()
    mw = collections.Counter(r['mw_scope'].split(':')[0] for r in rows)
    print('MW adversary scope:', dict(mw))
    ws_rows = [r for r in rows if r['ruling'] == 'wrong-sense']
    print('wrong-sense rows:', [(r['uid'], r['key']) for r in ws_rows])


if __name__ == '__main__':
    main()
