#!/usr/bin/env python
r"""Backfill store ``edition_rel`` from layer + DE typology rules (H1624 G4).

Uses the same classifier as promote (`edition_rel.classify_edition_rel`) and,
when scanning the full store, builds a PWG gender index so PW gender corrections
become ``pw_correct`` (matching build_relationships.py / relationships_rollup).

Does not rewrite ``de`` and does not delete other fields.

  python src/annotate_edition_rel.py              # annotate store in place
  python src/annotate_edition_rel.py --dry-run
  python src/annotate_edition_rel.py --selftest
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from edition_rel import (
    edition_rel_for_row, build_pwg_gender_index, classify_edition_rel,
)
from store_path import canonical_store
from store_write import locked_store_rewrite

STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))


def load_rows(store):
    return [json.loads(l) for l in open(store, encoding='utf-8') if l.strip()]


def write_rows(store, rows, no_backup):
    # H2146: locked (PromoteClaim) + unique fsynced backup + atomic replace — the old
    # in-place rewrite was unlocked and left a truncated store on crash (FINDINGS §513).
    locked_store_rewrite(store, rows, tag='preedition', no_backup=no_backup)


def selftest():
    rows = [
        {'key1': 'x', 'subcard': 'x~~h0_00_pwg00', 'layer': 'pwg',
         'sense_tag': '1', 'de': '<lex>m.</lex> {%x%}'},
        {'key1': 'x', 'subcard': 'x~~h0_zz_pw01', 'layer': 'pw',
         'sense_tag': '1', 'de': '<lex>f.</lex> {%x%}'},
        {'key1': 'a', 'subcard': 'a~~h0_zz_sch', 'layer': 'sch',
         'sense_tag': 'anu_desid', 'de': '{%einstimmen%}'},
    ]
    idx = build_pwg_gender_index(rows)
    assert edition_rel_for_row(rows[0], idx)['subtype'] == 'base'
    assert edition_rel_for_row(rows[1], idx)['subtype'] == 'pw_correct'
    assert edition_rel_for_row(rows[2], idx)['subtype'] == 'derived_sense'
    # DE unchanged
    assert rows[1]['de'] == '<lex>f.</lex> {%x%}'
    print('annotate_edition_rel selftest: OK')


def run(store, dry_run, no_backup):
    rows = load_rows(store)
    idx = build_pwg_gender_index(rows)
    counts = Counter()
    for r in rows:
        rel = edition_rel_for_row(r, idx)
        r['edition_rel'] = rel
        counts[rel['subtype']] += 1
    print('=== EDITION_REL ANNOTATION ===')
    print('store rows : %d' % len(rows))
    for subtype, n in counts.most_common():
        print('  %-18s %d' % (subtype, n))
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
