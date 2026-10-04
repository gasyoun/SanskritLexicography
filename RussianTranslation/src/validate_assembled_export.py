#!/usr/bin/env python
"""Validate the deterministic assembled-card export.

This gate checks the local output of:

  python assemble.py build

It deliberately uses only the standard library. The export itself is gitignored,
but the validator is committed so G4 can be reproduced before a print cut.

  python validate_assembled_export.py [--expected-cards N | --min-cards N] [--cards PATH] [--quarantine PATH]
"""
import argparse
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import assemble

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assembled_cards.jsonl')
QUARANTINE = os.path.join(HERE, 'assembled_cards.quarantine.jsonl')

CARD_REQUIRED = {
    'key1', 'key2', 'iast', 'records', 'quarantined_records',
    'attested_senses', 'rights', 'reuse',
}
ATTESTED_REQUIRED = {'dict', 'kow_reference', 'corpus', 'corpus_lexicon'}
RIGHTS_REQUIRED = {
    'publishable_dict_senses', 'restricted_dict_senses',
    'corpus_rights', 'note',
}
REUSE_REQUIRED = {'n_dict', 'n_kow', 'n_corpus', 'n_corpus_lex', 'covered'}
RECORD_REQUIRED = {'de_skeleton', 'placeholders', 'lossless'}
QUARANTINE_REQUIRED = {
    'key1', 'key2', 'record_no', 'reason',
    'body_excerpt', 'placeholder_count',
}


def fail(msg):
    raise ValueError(msg)


def need_keys(obj, keys, where):
    miss = sorted(k for k in keys if k not in obj)
    if miss:
        fail('{} missing keys: {}'.format(where, ', '.join(miss)))


def need_list(obj, key, where):
    if not isinstance(obj.get(key), list):
        fail('{}.{} must be a list'.format(where, key))


def expected_card_count():
    return sum(1 for _ in assemble.grouped_records())


def validate_card(card, line_no):
    where = 'assembled card line %d' % line_no
    if not isinstance(card, dict):
        fail('{} must be an object'.format(where))
    need_keys(card, CARD_REQUIRED, where)
    if '_quarantine' in card:
        fail('{} leaked private _quarantine payload into export'.format(where))
    if not card.get('key1'):
        fail('{} key1 is empty'.format(where))
    need_list(card, 'records', where)
    if not isinstance(card.get('quarantined_records'), int) or card['quarantined_records'] < 0:
        fail('{}.quarantined_records must be a non-negative integer'.format(where))

    att = card['attested_senses']
    if not isinstance(att, dict):
        fail('{}.attested_senses must be an object'.format(where))
    need_keys(att, ATTESTED_REQUIRED, where + '.attested_senses')
    for key in ('dict', 'kow_reference', 'corpus'):
        if not isinstance(att.get(key), list):
            fail('{}.attested_senses.{} must be a list'.format(where, key))

    rights = card['rights']
    if not isinstance(rights, dict):
        fail('{}.rights must be an object'.format(where))
    need_keys(rights, RIGHTS_REQUIRED, where + '.rights')
    if rights.get('corpus_rights') != 'approved-for-project-use':
        fail('{}.rights.corpus_rights is not approved-for-project-use'.format(where))

    reuse = card['reuse']
    if not isinstance(reuse, dict):
        fail('{}.reuse must be an object'.format(where))
    need_keys(reuse, REUSE_REQUIRED, where + '.reuse')
    if not isinstance(reuse.get('covered'), bool):
        fail('{}.reuse.covered must be a boolean'.format(where))
    for key in ('n_dict', 'n_kow', 'n_corpus', 'n_corpus_lex'):
        if not isinstance(reuse.get(key), int) or reuse[key] < 0:
            fail('{}.reuse.{} must be a non-negative integer'.format(where, key))

    for i, rec in enumerate(card['records']):
        rwhere = '%s.records[%d]' % (where, i)
        if not isinstance(rec, dict):
            fail('{} must be an object'.format(rwhere))
        need_keys(rec, RECORD_REQUIRED, rwhere)
        if not isinstance(rec.get('de_skeleton'), str):
            fail('{}.de_skeleton must be a string'.format(rwhere))
        if not isinstance(rec.get('placeholders'), list):
            fail('{}.placeholders must be a list'.format(rwhere))
        if rec.get('lossless') is not True:
            fail('{}.lossless must be true in the normal export stream'.format(rwhere))


def validate_quarantine_row(row, line_no):
    where = 'quarantine line %d' % line_no
    if not isinstance(row, dict):
        fail('{} must be an object'.format(where))
    need_keys(row, QUARANTINE_REQUIRED, where)
    if row.get('reason') != 'pwg_mask round-trip failed':
        fail('{} has unexpected reason: {!r}'.format(where, row.get('reason')))
    if not isinstance(row.get('record_no'), int) or row['record_no'] < 1:
        fail('{}.record_no must be a positive integer'.format(where))
    if not isinstance(row.get('placeholder_count'), int) or row['placeholder_count'] < 0:
        fail('{}.placeholder_count must be a non-negative integer'.format(where))


def load_jsonl(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rows.append((line_no, json.loads(line)))
            except json.JSONDecodeError as e:
                fail('%s:%d invalid JSON: %s' % (os.path.basename(path), line_no, e))
    return rows


def parse_args():
    ap = argparse.ArgumentParser(
        description='Validate the deterministic assembled-card export.')
    ap.add_argument('--min-cards', type=int,
                    help='minimum card count for bounded/fixture validation')
    ap.add_argument('--expected-cards', type=int,
                    help='exact card count for bounded/fixture validation')
    ap.add_argument('--cards', default=OUT,
                    help='assembled cards JSONL path')
    ap.add_argument('--quarantine', default=QUARANTINE,
                    help='assembled-card quarantine JSONL path')
    args = ap.parse_args()
    if args.min_cards is not None and args.min_cards < 1:
        ap.error('--min-cards must be a positive integer')
    if args.expected_cards is not None and args.expected_cards < 1:
        ap.error('--expected-cards must be a positive integer')
    if args.min_cards is not None and args.expected_cards is not None:
        ap.error('--min-cards and --expected-cards are mutually exclusive')
    return args


def main():
    args = parse_args()
    min_cards = args.min_cards
    expected_cards = args.expected_cards
    out, quarantine_path = args.cards, args.quarantine
    if not os.path.exists(out):
        fail('missing {}; run python assemble.py build first'.format(os.path.basename(out)))
    if not os.path.exists(quarantine_path):
        fail('missing {}; run python assemble.py build first'.format(os.path.basename(quarantine_path)))

    cards = load_jsonl(out)
    quarantine = load_jsonl(quarantine_path)
    expected = expected_card_count() if min_cards is None and expected_cards is None else expected_cards
    if expected is not None and len(cards) != expected:
        label = 'PWG grouped count' if expected_cards is None else 'expected bounded count'
        fail('assembled card count %d does not match %s %d' %
             (len(cards), label, expected))
    if min_cards is not None and len(cards) < min_cards:
        fail('assembled card count %d is below required minimum %d' %
             (len(cards), min_cards))
    if min_cards is not None:
        print('warning: --min-cards is a floor-only bounded check; use --expected-cards when the fixture count is known',
              file=sys.stderr)

    covered = quarantined_in_cards = 0
    for line_no, card in cards:
        validate_card(card, line_no)
        covered += 1 if card['reuse']['covered'] else 0
        quarantined_in_cards += card['quarantined_records']
    for line_no, row in quarantine:
        validate_quarantine_row(row, line_no)
    if quarantined_in_cards != len(quarantine):
        fail('cards report %d quarantined record(s), but quarantine has %d row(s)' %
             (quarantined_in_cards, len(quarantine)))

    pct = 100.0 * covered / max(len(cards), 1)
    mode = 'full' if min_cards is None and expected_cards is None else 'bounded'
    print('assembled export validation OK (%s): %d cards, %d covered (%.1f%%), %d quarantined record(s)' %
          (mode, len(cards), covered, pct, len(quarantine)))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('ASSEMBLED EXPORT CHECK FAILED: {}'.format(e), file=sys.stderr)
        raise SystemExit(1)
