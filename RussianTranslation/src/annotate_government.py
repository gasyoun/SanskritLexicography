#!/usr/bin/env python
r"""Backfill the translated store's ``government`` field (H335 W3(b) / H338).

Streams src/pwg_ru_translated.jsonl and, for each row, deterministically
extracts case-government (Rektion) markers from the row's **German** text
(``de`` — never ``ru``: only 375/510 rows preserve markers in the Russian,
H335 measured) via ``government_census.extract_government()``, writing the
result to the row's ``government`` field (a list of structured hit dicts,
possibly empty — see schemas/pwg_ru_final_card.schema.json).

Idempotent and in-place (writes a .bak unless --no-backup). Re-runnable.

  python src/annotate_government.py                 # annotate the store in place
  python src/annotate_government.py --dry-run        # coverage report only
  python src/annotate_government.py --check           # flag stored vs re-extracted drift, no write
  python src/annotate_government.py --selftest
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

from government_census import extract_government

STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')


def load_rows(store):
    return [json.loads(l) for l in open(store, encoding='utf-8') if l.strip()]


def write_rows(store, rows, no_backup):
    if not no_backup:
        os.replace(store, store + '.pregov.bak')
    with open(store, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def selftest():
    row = {'de': '{%sich heften auf%} (<ab>loc.</ab>): {#y#} <ls>KATHĀS. 11,11</ls>.'}
    hits = extract_government(row['de'])
    assert hits == [{'cases': ['loc'], 'variation': False, 'connector': '',
                      'kind': 'paren-single', 'span': '(<ab>loc.</ab>)'}], hits
    assert extract_government('') == []
    assert extract_government(None) == []
    print('annotate_government selftest: OK')


def run(store, dry_run, no_backup, check):
    rows = load_rows(store)
    n = len(rows)
    populated = 0
    mismatches = []
    for r in rows:
        gov = extract_government(r.get('de'))
        if check:
            stored = r.get('government')
            if stored is None:
                stored = []
            if stored != gov:
                mismatches.append({'key1': r.get('key1'), 'subcard': r.get('subcard'),
                                    'sense_tag': r.get('sense_tag'),
                                    'stored': stored, 'extracted': gov})
            continue
        r['government'] = gov
        if gov:
            populated += 1

    print('=== GOVERNMENT ANNOTATION ===')
    print('store rows            : %d' % n)
    if check:
        print('mismatches (stored vs extracted): %d' % len(mismatches))
        for m in mismatches[:25]:
            print('  %-20s subcard=%-20s sense=%-6s stored=%s extracted=%s' % (
                m['key1'], m['subcard'], m['sense_tag'], m['stored'], m['extracted']))
        if len(mismatches) > 25:
            print('  ... %d more' % (len(mismatches) - 25))
        return mismatches
    print('rows with >=1 government marker: %d (%.1f%%)' % (populated, 100 * populated / max(1, n)))
    if dry_run:
        print('\n(dry run — store not written)')
        return rows
    write_rows(store, rows, no_backup)
    print('\nwrote annotated store -> %s' % store)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--check', action='store_true',
                     help='report stored-vs-extracted mismatches; never writes')
    ap.add_argument('--fail-on-mismatch', action='store_true',
                     help='with --check, exit non-zero if any mismatch is found')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    mismatches = run(args.store, args.dry_run, args.no_backup, args.check)
    if args.check and args.fail_on_mismatch and mismatches:
        sys.exit(1)


if __name__ == '__main__':
    main()
