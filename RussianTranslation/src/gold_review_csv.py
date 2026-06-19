#!/usr/bin/env python
"""Export the frozen gold scaffold to a human-review CSV.

The committed gold/gold_set.jsonl contains the current LLM labels. This script
does not alter them; it creates a spreadsheet with blank human-review columns.

  python gold_review_csv.py
"""
import csv, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
GOLD = os.path.join(ROOT, 'gold', 'gold_set.jsonl')
SAMPLE = os.path.join(HERE, 'gold_sample.jsonl')
OUT = os.path.join(ROOT, 'gold', '_human_gold_review.csv')


FIELDS = [
    'id', 'slp1', 'sa', 'ru', 'kind', 'period', 'work', 'llm_label',
    'src_sa', 'src_ru', 'src_comm',
    'human_label', 'reviewer_id', 'confidence', 'needs_adjudication',
    'human_note',
]


def load_context():
    ctx = {}
    if not os.path.exists(SAMPLE):
        return ctx
    with open(SAMPLE, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            ctx[r.get('id')] = r
    return ctx


def main():
    if not os.path.exists(GOLD):
        sys.exit('no %s' % GOLD)
    ctx = load_context()
    rows = []
    with open(GOLD, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            g = json.loads(line)
            c = ctx.get(g.get('id'), {})
            rows.append({
                'id': g.get('id'),
                'slp1': g.get('slp1'),
                'sa': g.get('sa'),
                'ru': g.get('ru'),
                'kind': g.get('kind'),
                'period': g.get('period'),
                'work': g.get('work'),
                'llm_label': g.get('label'),
                'src_sa': c.get('src_sa', ''),
                'src_ru': c.get('src_ru', ''),
                'src_comm': ' | '.join(c.get('src_comm') or []),
                'human_label': '',
                'reviewer_id': '',
                'confidence': '',
                'needs_adjudication': '',
                'human_note': '',
            })
    rows.sort(key=lambda r: (r['period'] or '', r['kind'] or '', int(r['id'])))
    with open(OUT, 'w', encoding='utf-8-sig', newline='') as out:
        w = csv.DictWriter(out, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print('human gold CSV: %d row(s) → %s' % (len(rows), os.path.basename(OUT)))


if __name__ == '__main__':
    main()
