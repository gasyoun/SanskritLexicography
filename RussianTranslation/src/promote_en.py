#!/usr/bin/env python
r"""promote_en.py — attach EN translations onto the RU store, making it tri-lingual (de+ru+en).

The RU bridge (promote_final_cards.py) writes one store row per sense from the RU wf_output
files: each row carries `de` (German source) + `ru` (Russian) + provenance. The EN track lives
separately in per-root wf_output.en.<root>.json (per-sense `english`). This script JOINS them:
for every store row it finds the matching EN sense and attaches an `en` field, leaving the row
otherwise untouched. The result is a single store carrying de + ru + en per sense.

Join key — why not (subkey, sense_tag) or position:
  RU and EN are INDEPENDENT generation runs over the same masked PWG skeleton, so they do NOT
  agree on sense tags ('1-sub-einen Damm durchbrechen' vs '1-dam') NOR on sense segmentation
  (one run may split a sense the other merged). The one stable anchor is the German source text
  each sense carries verbatim. So the join is, within a sub-card:
    1. exact match on the normalized German (whitespace/punctuation-insensitive), else
    2. a difflib fuzzy match above --threshold (default 0.92), unambiguous by a margin, else
    3. leave `en` ABSENT — never fabricate a translation onto a row we could not match.

review_status is NOT changed (stays 'ai_translated' — the G5 gate). Run annotate_dcs_freq.py
AFTER this (it is language-agnostic and idempotent) to (re)attach the dcs_freq block.

  python src/promote_en.py                      # attach EN -> src/pwg_ru_translated.jsonl
  python src/promote_en.py --dry-run            # report coverage, write nothing
  python src/promote_en.py --glob 'wf_output.en.pat.json'   # a subset
  python src/promote_en.py --selftest
"""
import argparse
import difflib
import glob
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_GLOB = 'wf_output.en.*.json'
_KEEP = re.compile(r'[^0-9A-Za-z{}#%]')


def norm_de(g):
    """Whitespace/punctuation-insensitive key for the German source skeleton. Keeps alnum and
    the span markers ({}, #, %) so two senses differing only by a stray comma / newline / tag
    spacing between the two runs collapse to the same key, but distinct glosses stay distinct."""
    if not g:
        return ''
    return _KEEP.sub('', re.sub(r'\s+', ' ', g))


def load_wf(path):
    with open(path, encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:
        result = wrapper
    return result


def en_index(paths):
    """sub-card key -> list of (norm_de, english) for every non-empty EN sense, in card order."""
    idx = defaultdict(list)
    for path in paths:
        try:
            res = load_wf(path)
        except (OSError, json.JSONDecodeError) as e:
            print('  skip (unreadable): %s (%s)' % (os.path.basename(path), e))
            continue
        for r in res.get('results') or []:
            sub, card = r.get('key'), r.get('card')
            if not sub or not card:
                continue
            for rec in card.get('records') or []:
                for s in rec.get('senses') or []:
                    e = s.get('english')
                    if e and e.strip():
                        idx[sub].append((norm_de(s.get('german')), e))
    return idx


def match_en(de_key, candidates, threshold):
    """candidates: list of (norm_de, english) for the row's sub-card. Returns (english, how)
    or (None, reason)."""
    if not candidates:
        return None, 'no-en-sense'
    exact = [e for k, e in candidates if k and k == de_key]
    if len(exact) == 1:
        return exact[0], 'exact'
    if len(exact) > 1:
        return exact[0], 'exact-ambiguous'      # identical German repeated; first is as good
    if not de_key:
        return None, 'no-de-key'
    scored = sorted(
        ((difflib.SequenceMatcher(None, de_key, k).ratio(), e) for k, e in candidates if k),
        key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] < threshold:
        return None, 'below-threshold'
    if len(scored) > 1 and (scored[0][0] - scored[1][0]) < 0.02:
        return None, 'fuzzy-ambiguous'
    return scored[0][1], 'fuzzy'


def attach(rows, idx, threshold):
    stats = defaultdict(int)
    for r in rows:
        sub = r.get('subcard')
        r.pop('en', None)                         # idempotent re-run
        if sub not in idx:
            stats['no-en-file'] += 1
            continue
        en, how = match_en(norm_de(r.get('de')), idx[sub], threshold)
        stats[how] += 1
        if en is not None:
            r['en'] = en
            stats['attached'] += 1
    return stats


def selftest():
    rows = [
        {'subcard': 'p_a~~h0', 'sense_tag': '1', 'de': 'trinken', 'ru': 'пить'},
        {'subcard': 'p_a~~h0', 'sense_tag': '2', 'de': '<ab>Caus.</ab>, schützen', 'ru': 'защищать'},
        {'subcard': 'p_a~~h0', 'sense_tag': '3', 'de': 'ganz anderes', 'ru': 'иное'},
        {'subcard': 'zzz~~h9', 'sense_tag': '1', 'de': 'x', 'ru': 'ы'},   # no EN file
    ]
    # EN card: tag differs ('a'), German has a stray comma diff on sense 2 (fuzzy), no sense 3.
    idx = {'p_a~~h0': [
        (norm_de('trinken'), 'to drink'),
        (norm_de('<ab>Caus.</ab> schützen'), 'to protect'),
    ]}
    stats = attach(rows, idx, 0.92)
    assert rows[0].get('en') == 'to drink', 'exact German match'
    assert rows[1].get('en') == 'to protect', 'fuzzy German match across comma diff'
    assert 'en' not in rows[2], 'unmatched sense must be left absent, not fabricated'
    assert 'en' not in rows[3], 'row whose sub-card has no EN file stays EN-absent'
    assert rows[0]['ru'] == 'пить' and rows[0]['de'] == 'trinken', 'ru/de untouched'
    assert stats['attached'] == 2
    print('promote_en selftest OK')


def main():
    if '--selftest' in sys.argv[1:]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', default=DEFAULT_GLOB, help='EN wf_output glob, relative to repo root')
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--threshold', type=float, default=0.92,
                    help='minimum difflib ratio for a fuzzy German match (default 0.92)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    args = ap.parse_args()

    if not os.path.exists(args.store):
        sys.exit('no RU store at %s — run promote_final_cards.py first' % args.store)
    paths = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    if not paths:
        sys.exit('no EN wf_output files matched %s under %s' % (args.glob, ROOT))
    print('store: %s' % os.path.relpath(args.store, ROOT))
    print('ingesting %d EN wf_output file(s)' % len(paths))

    rows = [json.loads(l) for l in open(args.store, encoding='utf-8') if l.strip()]
    idx = en_index(paths)
    en_senses = sum(len(v) for v in idx.values())
    stats = attach(rows, idx, args.threshold)

    eligible = len(rows) - stats['no-en-file']
    print('\n=== EN MERGE COVERAGE ===')
    print('store rows              : %d' % len(rows))
    print('EN sub-cards / senses   : %d / %d' % (len(idx), en_senses))
    print('rows with EN sub-card   : %d' % eligible)
    print('  en attached           : %d (exact %d, exact-ambig %d, fuzzy %d)' % (
        stats['attached'], stats['exact'], stats['exact-ambiguous'], stats['fuzzy']))
    print('  unmatched (left absent): %d (below-threshold %d, fuzzy-ambig %d, no-en-sense %d, no-de-key %d)' % (
        stats['below-threshold'] + stats['fuzzy-ambiguous'] + stats['no-en-sense'] + stats['no-de-key'],
        stats['below-threshold'], stats['fuzzy-ambiguous'], stats['no-en-sense'], stats['no-de-key']))
    print('rows with no EN file yet: %d (roots beyond the EN run — EN absent, expected)' % stats['no-en-file'])

    if args.dry_run:
        print('\n(dry run — store not written)')
        return
    if not args.no_backup:
        bak = args.store + '.preEN.bak'
        with open(bak, 'w', encoding='utf-8') as f, open(args.store, encoding='utf-8') as src:
            f.write(src.read())
        print('\nbacked up store -> %s' % os.path.basename(bak))
    with open(args.store, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('wrote tri-lingual store -> %s (%d rows, %d now carry en)'
          % (os.path.relpath(args.store, ROOT), len(rows), stats['attached']))
    print('NEXT: re-run `python src/annotate_dcs_freq.py` to (re)attach the dcs_freq block.')


if __name__ == '__main__':
    main()
