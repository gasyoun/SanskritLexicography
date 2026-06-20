#!/usr/bin/env python
"""Ingest validated human gold-review CSV to JSONL.

  python gold_ingest.py <human_gold_review.csv> [out.jsonl]
"""
import csv, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import gold_validate

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, 'gold', 'human_gold_labels.jsonl')


def norm_bool(v):
    return str(v).strip().lower() in {'true', 'yes', '1'}


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit('usage: python gold_ingest.py <human_gold_review.csv> [out.jsonl]')
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) == 3 else OUT
    rows = gold_validate.read_rows(inp)
    errors, unique_ids = gold_validate.validate_rows(rows)
    if len(unique_ids) != 320 and out == OUT:
        errors.append('expected 320 unique gold item(s), found %d' % len(unique_ids))
    if errors:
        for e in errors[:50]:
            print('  ERROR:', e)
        sys.exit('human gold validation failed: %d error(s)' % len(errors))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='') as f:
        for r in rows:
            f.write(json.dumps({
                'id': r.get('id'), 'slp1': r.get('slp1'), 'sa': r.get('sa'),
                'ru': r.get('ru'), 'kind': r.get('kind'), 'period': r.get('period'),
                'work': r.get('work'), 'llm_label': r.get('llm_label'),
                'human_label': r.get('human_label'), 'reviewer_id': r.get('reviewer_id'),
                'confidence': r.get('confidence'),
                'needs_adjudication': norm_bool(r.get('needs_adjudication')),
                'human_note': r.get('human_note') or '',
            }, ensure_ascii=False) + '\n')
    print('human gold labels: %d row(s) → %s' % (len(rows), out))


if __name__ == '__main__':
    main()
