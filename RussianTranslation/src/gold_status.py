#!/usr/bin/env python
"""Report completeness of the human gold-review CSV without filling labels."""
import collections
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REQUIRED_HUMAN = ('human_label', 'reviewer_id', 'confidence', 'needs_adjudication')


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join('gold', '_human_gold_review.csv')
    rows = read_rows(path)
    missing = collections.Counter()
    by_reviewer = collections.Counter()
    incomplete = []
    for i, row in enumerate(rows, 2):
        reviewer = (row.get('reviewer_id') or '').strip() or '<blank>'
        by_reviewer[reviewer] += 1
        row_missing = [field for field in REQUIRED_HUMAN if not (row.get(field) or '').strip()]
        for field in row_missing:
            missing[field] += 1
        if row_missing:
            incomplete.append((i, row.get('id') or '', row.get('slp1') or '', ','.join(row_missing)))

    print('gold rows: %d' % len(rows))
    print('complete rows: %d' % (len(rows) - len(incomplete)))
    print('incomplete rows: %d' % len(incomplete))
    print('missing fields:', dict(sorted(missing.items())))
    print('rows by reviewer:', dict(sorted(by_reviewer.items())))
    if incomplete:
        print('first incomplete rows:')
        for line_no, rid, slp1, fields in incomplete[:25]:
            print('  line %d id=%s slp1=%s missing=%s' % (line_no, rid, slp1, fields))


if __name__ == '__main__':
    main()
