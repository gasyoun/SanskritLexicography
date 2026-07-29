#!/usr/bin/env python
r"""H1846 — the A/B under BOTH defensible definitions of "clean", per length quartile.

The H1210 report scored each arm by the canonical audit alone, because H1209 v1 had proved
the rig's own `would_promote` can lie. True — but the audit scores `cards_out`, which holds
the last SUCCESSFUL attempt's card even when the card ENDED as `worker-null-death` or
`escalate-review-sheet`. So "audit-clean" silently includes cards the pipeline itself
refused to ship, and the two arms do not refuse at the same rate (arm A 21 such cards, arm B
8). With one metric that difference is invisible; with both it is the finding.

  audit-clean   = canonical_audit promote_dry (what the H1210 report published)
  shippable     = promote_dry AND the rig ended the card in a clean status
                  (clean-no-review | clean-controller-approved) — i.e. what the pipeline
                  would actually have written to the store, unattended

Neither is "the" right metric: audit-clean measures the TEXT, shippable measures the
PIPELINE. Reporting only the one that flatters a conclusion is the failure mode this script
exists to prevent.

Usage:
  python src/pilot/h1210/dual_metric_breakdown.py \
      --arm-a-result F [F ...] --arm-a-audit F \
      --arm-b-result F [F ...] --arm-b-audit F \
      --worklist F [--out F]
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from ab_report import CLEAN_STATUSES, audit_index, card_id, load, merge_results  # noqa: E402


def arm(results, audit_path, worklist):
    rows = {r['key1']: r for r in merge_results(results)['results']}
    reports = audit_index(load(audit_path), worklist)
    out = {}
    for k, r in rows.items():
        clean = bool(reports.get(k, {}).get('promote_dry'))
        out[k] = (clean, clean and r['final_status'] in CLEAN_STATUSES)
    return out


def bands(worklist):
    byts = {card_id(r): r['bytes'] for r in worklist['detail']}
    sized = sorted((k for k in byts if byts[k] is not None), key=lambda k: byts[k])
    n = len(sized)
    out = []
    for i in range(4):
        grp = sized[i * n // 4:(i + 1) * n // 4]
        out.append(('Q%d (%d-%d B)' % (i + 1, byts[grp[0]], byts[grp[-1]]), grp))
    nb = [k for k in byts if byts[k] is None]
    if nb:
        out.append(('no_pwg', nb))
    return out


def cell(vals, idx):
    seen = [v for v in vals if v is not None]
    ok = sum(1 for v in seen if v[idx])
    return '%d/%d (%.0f%%)' % (ok, len(seen), 100.0 * ok / len(seen)) if seen else '—'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm-a-result', nargs='+', required=True)
    ap.add_argument('--arm-a-audit', required=True)
    ap.add_argument('--arm-b-result', nargs='+', required=True)
    ap.add_argument('--arm-b-audit', required=True)
    ap.add_argument('--worklist', required=True)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    wl = load(a.worklist)
    A = arm(a.arm_a_result, a.arm_a_audit, wl)
    B = arm(a.arm_b_result, a.arm_b_audit, wl)

    rows, out_rows = [], []
    for label, grp in bands(wl):
        av, bv = [A.get(k) for k in grp], [B.get(k) for k in grp]
        rows.append((label, cell(av, 0), cell(bv, 0), cell(av, 1), cell(bv, 1)))
        out_rows.append({
            'stratum': label, 'n': len(grp),
            'arm_a_audit_clean': sum(1 for v in av if v and v[0]),
            'arm_b_audit_clean': sum(1 for v in bv if v and v[0]),
            'arm_a_shippable': sum(1 for v in av if v and v[1]),
            'arm_b_shippable': sum(1 for v in bv if v and v[1]),
        })

    tot = ('**TOTAL**', cell(list(A.values()), 0), cell(list(B.values()), 0),
           cell(list(A.values()), 1), cell(list(B.values()), 1))
    md = ['| entry-length quartile | A audit-clean | B audit-clean | A shippable | B shippable |',
          '|---|---:|---:|---:|---:|']
    md += ['| %s | %s | %s | %s | %s |' % r for r in rows + [tot]]
    print('\n'.join(md))

    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'schema': 'pwg.h1210_dual_metric.v1',
                       'definitions': {
                           'audit_clean': 'canonical_audit promote_dry',
                           'shippable': 'promote_dry AND rig final_status in %s'
                                        % sorted(CLEAN_STATUSES)},
                       'rows': out_rows,
                       'total': {'arm_a_audit_clean': sum(1 for v in A.values() if v[0]),
                                 'arm_b_audit_clean': sum(1 for v in B.values() if v[0]),
                                 'arm_a_shippable': sum(1 for v in A.values() if v[1]),
                                 'arm_b_shippable': sum(1 for v in B.values() if v[1])}},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('\nwrote %s' % a.out)


if __name__ == '__main__':
    main()
