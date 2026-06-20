#!/usr/bin/env python
"""Verify a double-review queue before sending it to second reviewers."""
import argparse
import collections
import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SECOND = ['second_reviewer_id', 'second_human_label', 'second_confidence',
          'second_needs_adjudication', 'second_human_note']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('queue_csv')
    ap.add_argument('--sample-size', type=int, default=80)
    args = ap.parse_args()
    with open(args.queue_csv, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    missing_fields = [f for f in SECOND if f not in fields]
    if missing_fields:
        raise SystemExit('missing second-review columns: %s' % ', '.join(missing_fields))
    if len(rows) != args.sample_size:
        raise SystemExit('expected %d row(s), found %d' % (args.sample_size, len(rows)))
    prefilled = []
    for i, row in enumerate(rows, 2):
        filled = [f for f in SECOND if (row.get(f) or '').strip()]
        if filled:
            prefilled.append('line %d id=%s fields=%s' %
                             (i, row.get('id') or '', ','.join(filled)))
    if prefilled:
        for item in prefilled[:20]:
            print('prefilled:', item)
        raise SystemExit('double-review queue should be blank for second-review fields')
    counts = collections.Counter((r.get('period') or '', r.get('kind') or '') for r in rows)
    if not counts:
        raise SystemExit('double-review queue is empty')
    min_n, max_n = min(counts.values()), max(counts.values())
    if max_n - min_n > 1:
        raise SystemExit('strata are imbalanced: %s' %
                         dict(sorted(('%s/%s' % k, v) for k, v in counts.items())))
    print('double-review queue OK: %d row(s), %d strata, balance %d..%d' %
          (len(rows), len(counts), min_n, max_n))


if __name__ == '__main__':
    main()
