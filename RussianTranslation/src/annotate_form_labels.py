#!/usr/bin/env python
r"""Backfill store ``form_labels`` from DE (H1624 form-layer).

Sibling of annotate_government.py. Streams the translated store and stamps
``form_labels = extract_form_labels(de)`` on every row (number / gender /
nom|voc / voice). New promotions already stamp this in promote_final_cards;
this script is the retrofit for older rows.

  python src/annotate_form_labels.py              # annotate store in place
  python src/annotate_form_labels.py --dry-run
  python src/annotate_form_labels.py --selftest
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

from form_labels import extract_form_labels
from store_path import canonical_store

STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))


def load_rows(store):
    return [json.loads(l) for l in open(store, encoding='utf-8') if l.strip()]


def write_rows(store, rows, no_backup):
    if not no_backup:
        os.replace(store, store + '.preform.bak')
    with open(store, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def selftest():
    de = '<lex>m.</lex> {%Gott%} (<ab>pl.</ab>). (<ab>voc.</ab>)'
    hits = extract_form_labels(de)
    axes = {(h['axis'], h['value']) for h in hits}
    assert ('gender', 'm') in axes and ('number', 'pl') in axes and ('case_form', 'voc') in axes, hits
    assert extract_form_labels('') == []
    print('annotate_form_labels selftest: OK')


def run(store, dry_run, no_backup):
    rows = load_rows(store)
    populated = 0
    for r in rows:
        fl = extract_form_labels(r.get('de'))
        r['form_labels'] = fl
        if fl:
            populated += 1
    print('=== FORM LABELS ANNOTATION ===')
    print('store rows            : %d' % len(rows))
    print('rows with >=1 label   : %d (%.1f%%)' % (
        populated, 100 * populated / max(1, len(rows))))
    if dry_run:
        print('(dry run — store not written)')
        return rows
    write_rows(store, rows, no_backup)
    print('wrote annotated store -> %s' % store)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    run(args.store, args.dry_run, args.no_backup)


if __name__ == '__main__':
    main()
