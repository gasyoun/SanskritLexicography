#!/usr/bin/env python
"""Ingest filled double-review queue CSV into long-form gold-label JSONL.

The queue CSV is wide (`second_*` columns). This bridge emits normal reviewer
rows compatible with gold_agreement.py.
"""
import argparse
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
BASE_LABELS = os.path.join(ROOT, 'gold', 'human_gold_labels.jsonl')
REQUIRED_SECOND = (
    'second_reviewer_id',
    'second_human_label',
    'second_confidence',
    'second_needs_adjudication',
)
REQUIRED_FIRST = ('reviewer_id', 'human_label', 'confidence', 'needs_adjudication')
LABELS = {'correct', 'lemma-variant', 'proper-name', 'partial',
          'wrong-sense', 'hallucinated'}
CONFIDENCE = {'low', 'medium', 'high'}
BOOLS = {'true', 'false', 'yes', 'no', '0', '1'}


def norm_bool(v):
    return str(v).strip().lower() in {'true', 'yes', '1'}


def read_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def second_row(row, line_no):
    errors = []
    for field in REQUIRED_SECOND:
        if not (row.get(field) or '').strip():
            errors.append('line %d id=%s: %s required' % (line_no, row.get('id') or '', field))
    reviewer = (row.get('second_reviewer_id') or '').strip()
    first_reviewer = (row.get('reviewer_id') or '').strip()
    label = (row.get('second_human_label') or '').strip()
    conf = (row.get('second_confidence') or '').strip().lower()
    adj = (row.get('second_needs_adjudication') or '').strip().lower()
    if first_reviewer and reviewer and reviewer == first_reviewer:
        errors.append('line %d id=%s: second reviewer must differ from first reviewer' %
                      (line_no, row.get('id') or ''))
    if label and label not in LABELS:
        errors.append('line %d id=%s: bad second_human_label %r' %
                      (line_no, row.get('id') or '', label))
    if conf and conf not in CONFIDENCE:
        errors.append('line %d id=%s: bad second_confidence %r' %
                      (line_no, row.get('id') or '', conf))
    if adj and adj not in BOOLS:
        errors.append('line %d id=%s: bad second_needs_adjudication %r' %
                      (line_no, row.get('id') or '', adj))
    if errors:
        return None, errors
    return {
        'id': row.get('id'), 'slp1': row.get('slp1'), 'sa': row.get('sa'),
        'ru': row.get('ru'), 'kind': row.get('kind'), 'period': row.get('period'),
        'work': row.get('work'), 'llm_label': row.get('llm_label'),
        'human_label': label, 'reviewer_id': reviewer,
        'confidence': conf,
        'needs_adjudication': norm_bool(adj),
        'human_note': row.get('second_human_note') or '',
    }, []


def first_row(row, line_no):
    if not all((row.get(field) or '').strip() for field in REQUIRED_FIRST):
        return None, []
    return {
        'id': row.get('id'), 'slp1': row.get('slp1'), 'sa': row.get('sa'),
        'ru': row.get('ru'), 'kind': row.get('kind'), 'period': row.get('period'),
        'work': row.get('work'), 'llm_label': row.get('llm_label'),
        'human_label': (row.get('human_label') or '').strip(),
        'reviewer_id': (row.get('reviewer_id') or '').strip(),
        'confidence': (row.get('confidence') or '').strip().lower(),
        'needs_adjudication': norm_bool(row.get('needs_adjudication')),
        'human_note': row.get('human_note') or '',
    }, []


def dedupe(rows):
    out = []
    seen = set()
    for row in rows:
        key = (str(row.get('id')), row.get('reviewer_id'))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_path')
    ap.add_argument('out_jsonl', nargs='?', default=None)
    args = ap.parse_args()
    if args.out_jsonl is None and not os.path.exists(BASE_LABELS):
        raise SystemExit('base %s missing; pass explicit out_jsonl for validation/testing' % BASE_LABELS)
    out = args.out_jsonl or BASE_LABELS
    rows = read_csv(args.csv_path)
    converted, errors = [], []
    for line_no, row in enumerate(rows, 2):
        rec, row_errors = first_row(row, line_no)
        errors.extend(row_errors)
        if rec:
            converted.append(rec)
        rec, row_errors = second_row(row, line_no)
        errors.extend(row_errors)
        if rec:
            converted.append(rec)
    if errors:
        for e in errors[:50]:
            print('  ERROR:', e)
        raise SystemExit('double-review ingest failed: %d error(s)' % len(errors))
    base = read_jsonl(BASE_LABELS) if args.out_jsonl is None else []
    merged = dedupe(base + converted)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='') as f:
        for row in merged:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('double-review labels: %d converted row(s), %d total -> %s' %
          (len(converted), len(merged), out))


if __name__ == '__main__':
    main()
