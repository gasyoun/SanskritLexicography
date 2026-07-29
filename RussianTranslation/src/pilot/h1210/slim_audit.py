#!/usr/bin/env python
r"""H1210 — strip a canonical-audit report down to its COMMITTABLE verdict rows.

`h1209/canonical_audit.py` embeds the whole `restored_card` in every report row, which is
what makes the report the authoritative artifact — and also what makes it unpublishable:
those cards are unpublished RU/DE store-grade text, the same class the review-sheet HTML is
gitignored for. So the fat report stays local and this writes the slim twin that IS
committed: every gate verdict, every defect class, every count — no card text.

Kept per row: key1, wf self-report, promote_dry, hard_fail, soft_flags, tnmask/fidelity/
sanloss/schema counters, notes-parked token IDs (ids only, never the payload preview).

Usage:
  python src/pilot/h1210/slim_audit.py <audit.json> <out_slim.json> [--arm NAME]
"""
import argparse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def slim_row(r):
    np = r.get('notes_parked') or {}
    return {
        'key1': r['key1'],
        'promote_dry': r.get('promote_dry'),
        'null_card': r.get('null_card', False),
        'wf_would_promote': r.get('wf_would_promote'),
        'wf_coverage': r.get('wf_coverage'),
        'hard_fail': r.get('hard_fail') or [],
        'soft_flags': r.get('soft_flags') or [],
        'tnmask': r.get('tnmask') and {k: v for k, v in r['tnmask'].items()
                                       if k in ('match', 'n_skeleton', 'n_output')},
        'fidelity_german': r.get('fidelity_german'),
        'fidelity_translation': r.get('fidelity_translation'),
        'sanloss': r.get('sanloss'),
        'schema_ok': (r.get('schema') or {}).get('ok'),
        # token IDs only — the `lost_payload_preview` carries source text, so it is dropped.
        'notes_parked_tokens': np.get('tokens') or [],
        'notes_lost_content': np.get('lost_content') or [],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audit')
    ap.add_argument('out')
    ap.add_argument('--arm', default=None)
    a = ap.parse_args()
    d = json.load(open(a.audit, encoding='utf-8'))
    rows = [slim_row(r) for r in d['reports']]
    out = {'schema': 'pwg.h1210_canonical_audit_slim.v1', 'arm': a.arm,
           'source': 'h1209/canonical_audit.py (restored_card stripped — unpublished text)',
           'n_cards': len(rows),
           'n_promote_dry': sum(1 for r in rows if r['promote_dry']),
           'reports': rows}
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote %s: %d rows, %d promote-DRY PASS' % (a.out, len(rows), out['n_promote_dry']))


if __name__ == '__main__':
    main()
