#!/usr/bin/env python
r"""Backfill store ``form_labels`` + ``form_notes`` from DE (H1624 form-layer).

Sibling of annotate_government.py. Streams the translated store and stamps:

  * ``form_labels`` — number / gender / case_form / voice multi-axis list
  * ``form_notes``  — dedicated nom/voc form-note field only

New promotions already stamp both in promote_final_cards; this script is the
retrofit for older rows.

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

from form_labels import extract_form_labels, extract_form_notes
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
    notes = extract_form_notes(de)
    assert notes and notes[0]['case'] == 'voc', notes
    assert extract_form_labels('') == [] and extract_form_notes('') == []
    print('annotate_form_labels selftest: OK')


def run(store, dry_run, no_backup):
    rows = load_rows(store)
    populated = n_notes = 0
    for r in rows:
        de = r.get('de')
        fl = extract_form_labels(de)
        fn = extract_form_notes(de)
        r['form_labels'] = fl
        r['form_notes'] = fn
        if fl:
            populated += 1
        if fn:
            n_notes += 1
    print('=== FORM LABELS + FORM NOTES ANNOTATION ===')
    print('store rows              : %d' % len(rows))
    print('rows with form_labels   : %d (%.1f%%)' % (
        populated, 100 * populated / max(1, len(rows))))
    print('rows with form_notes    : %d (%.1f%%)  # nom/voc only' % (
        n_notes, 100 * n_notes / max(1, len(rows))))
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
