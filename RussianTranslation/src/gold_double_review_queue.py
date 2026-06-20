#!/usr/bin/env python
"""Create a deterministic stratified queue for second human review."""
import argparse
import collections
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_OUT = os.path.join(ROOT, 'gold', '_double_review_queue.csv')


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def stratified(rows, sample_size):
    groups = collections.defaultdict(list)
    for row in rows:
        groups[(row.get('period') or '', row.get('kind') or '')].append(row)
    for group_rows in groups.values():
        group_rows.sort(key=lambda r: (int(r.get('id') or 0), r.get('slp1') or ''))
    selected = []
    keys = sorted(groups)
    while len(selected) < sample_size and keys:
        next_keys = []
        for key in keys:
            if groups[key] and len(selected) < sample_size:
                selected.append(groups[key].pop(0))
            if groups[key]:
                next_keys.append(key)
        keys = next_keys
    return selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    ap.add_argument('--sample-size', type=int, default=80)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()
    fields, rows = read_rows(args.csv_path)
    if args.sample_size < 1:
        raise SystemExit('--sample-size must be positive')
    selected = stratified(rows, min(args.sample_size, len(rows)))
    extra = ['second_reviewer_id', 'second_human_label', 'second_confidence',
             'second_needs_adjudication', 'second_human_note']
    out_fields = fields + [f for f in extra if f not in fields]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=out_fields, extrasaction='ignore')
        w.writeheader()
        for row in selected:
            row = dict(row)
            for field in extra:
                row.setdefault(field, '')
            w.writerow(row)
    counts = collections.Counter((r.get('period') or '', r.get('kind') or '') for r in selected)
    print('double-review queue: %d row(s) -> %s' % (len(selected), args.out))
    print('strata:', dict(sorted(('%s/%s' % k, v) for k, v in counts.items())))


if __name__ == '__main__':
    main()
