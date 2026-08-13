#!/usr/bin/env python3
"""Re-grade a sealed run under the corrected GO basis, without touching the original.

The first receipt of the H2612 run was graded by the rule as it stood: arm TOTALS. That
rule fired GO on a +10.21 % wall margin which decomposition immediately withdrew — remove
arm A's one refusal and the same margin inverts to -8.85 %, while the paired figure over
the units both arms produced is +4.25 %. The rule now keys off the paired margin.

The original receipt stays exactly as sealed — it is the record of what the old rule said,
and overwriting it would erase the evidence for changing the rule. This writes the re-grade
beside it as `comparison_receipt.regraded.json`.

Read-only with respect to the run: no call, no reservation, no envelope is touched.

    python regrade_receipt.py [--run-dir run3]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
for path in (os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE)),
             os.path.dirname(os.path.dirname(os.path.dirname(HERE)))):
    if path not in sys.path:
        sys.path.insert(0, path)

import prep_context_compare as pcc                            # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', default=os.path.join(HERE, 'run3'))
    parser.add_argument('--plan-file', default=os.path.join(HERE, 'plan.json'))
    args = parser.parse_args()

    with open(args.plan_file, encoding='utf-8') as handle:
        plan = json.load(handle)
    plan['__plan_file__'] = os.path.abspath(args.plan_file)
    pcc.verify_plan_hash(plan)

    with open(os.path.join(args.run_dir, 'check.json'), encoding='utf-8') as handle:
        check_report = json.load(handle)

    envelopes = []
    for path in sorted(glob.glob(os.path.join(args.run_dir, 'envelopes', '*.json'))):
        with open(path, encoding='utf-8') as handle:
            envelopes.append(json.load(handle))
    envelopes.sort(key=lambda e: e['ordinal'])

    run = {'envelopes': envelopes, 'stopped': None,
           'calls_spent': len(envelopes), 'ledger_usage': None}
    receipt = pcc.build_receipt(plan, run, check_report=check_report)

    original_path = os.path.join(args.run_dir, 'comparison_receipt.json')
    original = None
    if os.path.exists(original_path):
        with open(original_path, encoding='utf-8') as handle:
            original = json.load(handle)

    out = os.path.join(args.run_dir, 'comparison_receipt.regraded.json')
    pcc.atomic_json(out, dict(receipt, regrade={
        'reason': 'GO basis moved from arm totals to the paired margin over units both arms '
                  'returned schema for',
        'original_receipt_sha256': (original or {}).get('receipt_sha256'),
        'original_verdict': (original or {}).get('verdict'),
    }))

    print('original verdict : %s (%s)' % ((original or {}).get('verdict'),
                                          (original or {}).get('receipt_sha256', '')[:16]))
    print('regraded verdict : %s (%s)' % (receipt['verdict'],
                                          receipt['receipt_sha256'][:16]))
    paired = receipt['paired_deltas']
    print('arm-total wall gain %+.2f %%  ->  paired wall gain %+.2f %% over %d unit(s), '
          'PREP faster on %d'
          % (100 * (receipt['deltas']['wall_ms_relative_gain'] or 0),
             100 * (paired['wall_ms_relative_gain'] or 0),
             paired['unit_count'], paired['prep_faster_units']))
    print('paired token gain %+.2f %% (negative = PREP costs more)'
          % (100 * (paired['non_cache_token_relative_gain'] or 0)))
    print('wrote %s' % out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
