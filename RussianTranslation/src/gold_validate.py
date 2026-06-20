#!/usr/bin/env python
"""Validate human gold-review CSV labels.

  python gold_validate.py gold/_human_gold_review.csv
  python gold_validate.py src/fixtures/human_gold_review.fixture.csv --expect 3
"""
import argparse
import csv, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

LABELS = {'correct', 'lemma-variant', 'proper-name', 'partial',
          'wrong-sense', 'hallucinated'}
CONFIDENCE = {'low', 'medium', 'high'}
BOOLS = {'true', 'false', 'yes', 'no', '0', '1'}
REQUIRED = {'id', 'slp1', 'sa', 'ru', 'kind', 'period', 'work',
            'human_label', 'reviewer_id', 'confidence', 'needs_adjudication'}


def fail(msg):
    raise ValueError(msg)


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    missing = REQUIRED - set(rows[0].keys() if rows else [])
    if missing:
        fail('missing CSV columns: %s' % ', '.join(sorted(missing)))
    return rows


def validate_rows(rows):
    errors = []
    seen = set()
    unique_ids = set()
    for i, r in enumerate(rows, 2):
        rid = (r.get('id') or '').strip()
        reviewer = (r.get('reviewer_id') or '').strip()
        label = (r.get('human_label') or '').strip()
        conf = (r.get('confidence') or '').strip().lower()
        adj = (r.get('needs_adjudication') or '').strip().lower()
        if not rid:
            errors.append('line %d: id required' % i)
        else:
            unique_ids.add(rid)
        if not reviewer:
            errors.append('line %d id=%s: reviewer_id required' % (i, rid))
        if label not in LABELS:
            errors.append('line %d id=%s: bad human_label %r' % (i, rid, label))
        if conf not in CONFIDENCE:
            errors.append('line %d id=%s: bad confidence %r' % (i, rid, conf))
        if adj not in BOOLS:
            errors.append('line %d id=%s: bad needs_adjudication %r' % (i, rid, adj))
        key = (rid, reviewer)
        if key in seen:
            errors.append('line %d id=%s: duplicate reviewer %s' % (i, rid, reviewer))
        seen.add(key)
    return errors, unique_ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    ap.add_argument('--expect', type=int, default=320,
                    help='expected unique gold item count; default closes G6 at 320')
    args = ap.parse_args()
    rows = read_rows(args.csv_path)
    errors, unique_ids = validate_rows(rows)
    if args.expect and len(unique_ids) != args.expect:
        errors.append('expected %d unique gold item(s), found %d' % (args.expect, len(unique_ids)))
    print('human gold rows: %d | unique items: %d' % (len(rows), len(unique_ids)))
    if errors:
        for e in errors[:50]:
            print('  ERROR:', e)
        sys.exit('human gold validation failed: %d error(s)' % len(errors))
    print('human gold validation OK: %d row(s)' % len(rows))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('HUMAN GOLD CHECK FAILED: %s' % e, file=sys.stderr)
        raise SystemExit(1)
