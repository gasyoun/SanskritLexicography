#!/usr/bin/env python
r"""H1210 — audit-clean rate by ENTRY-LENGTH quartile, per arm.

The headline "audit-clean %" hides the finding that actually decides the A/B: the two arms
are near-indistinguishable on short entries and diverge sharply on long ones. A single
percentage over a length-STRATIFIED sample is a weighted average whose weights are an
artifact of the selection rule, so it must not be read as "arm B is N points worse" — this
script is the breakdown that makes the interaction visible.

Quartiles are cut on the worklist's `bytes` (raw PWG entry size). The 10 `no_pwg` cards
carry no `bytes` (they are supplement sub-cards, not PWG entries) and are reported as their
own row rather than silently dropped or bucketed at zero.

Usage:
  python src/pilot/h1210/length_breakdown.py \
      --arm-a-audit src/pilot/h1210/arm_a.canonical_audit.json \
      --arm-b-audit src/pilot/h1210/arm_b.canonical_audit.json \
      --worklist src/pilot/h1210/H1210_ab100_worklist.28.07.26.json
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from safe_filename import safe_name                          # noqa: E402


def card_id(row):
    return row['sub_key'] if row.get('layer') == 'no_pwg' and row.get('sub_key') \
        else safe_name(row['key1'])


def load(p):
    return json.load(open(p, encoding='utf-8'))


def index(audit, alias):
    """Same resolver contract as ab_report.audit_index — see its docstring for why."""
    out = {}
    for r in audit['reports']:
        cid = alias.get(r['key1']) or alias.get(safe_name(r['key1']))
        if not cid:
            sys.exit('FAIL: audit row %r not resolvable to a worklist card id' % r['key1'])
        out[cid] = r
    return out


def rate(ids, rep):
    seen = [k for k in ids if k in rep]
    ok = sum(1 for k in seen if rep[k].get('promote_dry'))
    return ok, len(seen)


def cell(ok, n):
    return '—' if not n else '%d/%d (%.0f%%)' % (ok, n, 100.0 * ok / n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm-a-audit', required=True)
    ap.add_argument('--arm-b-audit', required=True)
    ap.add_argument('--worklist', required=True)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    wl = load(a.worklist)
    alias, byts = {}, {}
    for r in wl['detail']:
        cid = card_id(r)
        alias[cid] = cid
        alias[r['key1']] = cid
        alias[safe_name(r['key1'])] = cid
        byts[cid] = r['bytes']

    A = index(load(a.arm_a_audit), alias)
    B = index(load(a.arm_b_audit), alias)

    sized = sorted((k for k in byts if byts[k] is not None), key=lambda k: byts[k])
    n = len(sized)
    rows, out_rows = [], []
    for i in range(4):
        grp = sized[i * n // 4:(i + 1) * n // 4]
        ao, an = rate(grp, A)
        bo, bn = rate(grp, B)
        label = 'Q%d (%d–%d B)' % (i + 1, byts[grp[0]], byts[grp[-1]])
        rows.append((label, cell(ao, an), cell(bo, bn)))
        out_rows.append({'stratum': label, 'lo': byts[grp[0]], 'hi': byts[grp[-1]],
                         'arm_a_clean': ao, 'arm_a_n': an,
                         'arm_b_clean': bo, 'arm_b_n': bn})

    nb = [k for k in byts if byts[k] is None]
    if nb:
        ao, an = rate(nb, A)
        bo, bn = rate(nb, B)
        rows.append(('no_pwg (no byte size)', cell(ao, an), cell(bo, bn)))
        out_rows.append({'stratum': 'no_pwg', 'lo': None, 'hi': None,
                         'arm_a_clean': ao, 'arm_a_n': an,
                         'arm_b_clean': bo, 'arm_b_n': bn})

    md = ['| entry-length quartile | arm A clean | arm B clean |', '|---|---:|---:|']
    md += ['| %s | %s | %s |' % r for r in rows]
    print('\n'.join(md))

    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'schema': 'pwg.h1210_length_breakdown.v1', 'rows': out_rows},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('\nwrote %s' % a.out)


if __name__ == '__main__':
    main()
