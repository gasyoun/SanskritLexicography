#!/usr/bin/env python
"""Validate canonical pwg_ru lexicographic portraits.

This is a lightweight standard-library gate for the v1 portrait contract in
schemas/pwg_ru_lexicographic_portrait.schema.json. It validates live
microstructure.portrait() output for representative PWG records.

  python validate_portrait_schema.py [N]
  python validate_portrait_schema.py --limit N
"""
import argparse
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import microstructure as ms
import pwg_mask

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
SCHEMA = os.path.join(ROOT, 'schemas', 'pwg_ru_lexicographic_portrait.schema.json')

EXPECTED_VERSION = 'pwg_ru.lexicographic_portrait.v1'
CARD_REQUIRED = {
    'schema_version', 'key1', 'key2', 'h', 'iast',
    'pos', 'diasystem', 'labels', 'senses',
}
SENSE_REQUIRED = {
    'n', 'sub', 'equivalents_de', 'gloss_de', 'equivalence_type',
    'grammar', 'ab_labels', 'diasystem', 'citations', 'citations_resolved',
    'strata', 'examples_sa',
}
EQ_TYPES = {'equivalent', 'explanatory', 'none'}


def fail(msg):
    raise ValueError(msg)


def need_keys(obj, keys, where):
    miss = sorted(k for k in keys if k not in obj)
    if miss:
        fail('%s missing keys: %s' % (where, ', '.join(miss)))


def need_list(obj, key, where):
    if not isinstance(obj.get(key), list):
        fail('%s.%s must be a list' % (where, key))


def validate_portrait(p):
    need_keys(p, CARD_REQUIRED, 'portrait')
    if p['schema_version'] != EXPECTED_VERSION:
        fail('bad schema_version: %r' % p['schema_version'])
    if not p.get('key1'):
        fail('key1 is empty')
    for key in ('pos', 'diasystem', 'labels', 'senses'):
        need_list(p, key, 'portrait')
    if not p['senses']:
        fail('%s has no senses' % p['key1'])
    if p.get('corpus_synonyms') is not None:
        cs = p['corpus_synonyms']
        need_keys(cs, {'n', 'by_stratum', 'candidates'}, 'corpus_synonyms')
        if not isinstance(cs['n'], int) or cs['n'] < 0:
            fail('corpus_synonyms.n must be a non-negative integer')
        if not isinstance(cs['by_stratum'], dict):
            fail('corpus_synonyms.by_stratum must be an object')
        need_list(cs, 'candidates', 'corpus_synonyms')
    for i, s in enumerate(p['senses']):
        where = 'sense[%d]' % i
        need_keys(s, SENSE_REQUIRED, where)
        if s['equivalence_type'] not in EQ_TYPES:
            fail('%s bad equivalence_type: %r' % (where, s['equivalence_type']))
        for key in ('equivalents_de', 'grammar', 'ab_labels', 'diasystem',
                    'citations', 'examples_sa'):
            need_list(s, key, where)
        if not isinstance(s['citations_resolved'], dict):
            fail('%s.citations_resolved must be an object' % where)
        if not isinstance(s['strata'], dict):
            fail('%s.strata must be an object' % where)


def parse_args():
    ap = argparse.ArgumentParser(
        description='Validate live PWG lexicographic portrait schema output.')
    ap.add_argument('n', nargs='?', type=int,
                    help='number of live PWG portraits to validate')
    ap.add_argument('--limit', type=int,
                    help='number of live PWG portraits to validate')
    args = ap.parse_args()
    if args.n is not None and args.limit is not None:
        ap.error('use either positional N or --limit, not both')
    n = args.limit if args.limit is not None else (args.n if args.n is not None else 25)
    if n < 1:
        ap.error('limit must be a positive integer')
    return n


def main():
    n = parse_args()
    schema = json.load(open(SCHEMA, encoding='utf-8'))
    if schema.get('$id') != 'pwg_ru.lexicographic_portrait.schema.v1':
        fail('unexpected schema id')
    checked = 0
    for buf in pwg_mask.records():
        p = ms.portrait(buf)
        validate_portrait(p)
        checked += 1
        if checked >= n:
            break
    print('portrait schema validation OK: %d portrait(s)' % checked)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('PORTRAIT SCHEMA CHECK FAILED: %s' % e, file=sys.stderr)
        raise SystemExit(1)
