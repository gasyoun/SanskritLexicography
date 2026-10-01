#!/usr/bin/env python
r"""H3751 census -- is a store row's printed locus its OWN homograph's? (issue #1801)

`~~h<N>_` in a pwg_ru sub-card key is an `enumerate` index over the PWG source records of
a headword, not a homonym number (see `pwg_homonym.py`). `pwg_page_index.annotate_cards`
compared it against the source's printed `<h>`, which starts at 1, so `card_h='0'` never
matched, selection fell back to "every record sharing this key1", and `column`/`volume`/
`page` were taken from the LOWEST `(vol, col)` across all homographs -- another word's
printed column, shipped into the DE edition graph.

This census reconciles every store row against the source **positionally** -- the only
evidence-decidable reading of an enumerate index -- and reports how many rows carry a
locus that is not their own record's:

    python src/h3751_homonym_census.py [--store PATH] [--src pwg.txt]
                                       [--json OUT] [--report OUT.md]

Read-only; exit 0 always (a census never gates). Ruling 14 of the wave plan: if the
measured population diverges >=2x from issue #1801's claimed 24.5 % of mappable pwg-layer
rows, the rewrite half HALTS and this census is the whole delivery -- `verdict.halt_rewrite`
in the JSON carries that decision mechanically.
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import corpus_gate as cg                                            # noqa: E402
from pwg_homonym import (                                           # noqa: E402
    AMBIGUOUS, index_by_form_key, resolve_locus, split_subcard,
)
from pwg_page_index import DEFAULT_SRC, parse_source, pc_str        # noqa: E402
from store_path import canonical_store                              # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))

# issue #1801's claimed population, measured by H2889 at af58b3b01836e7:
ISSUE_CLAIM_WRONG = 1278
ISSUE_CLAIM_MAPPABLE = 5211
ISSUE_CLAIM_SHARE = ISSUE_CLAIM_WRONG / ISSUE_CLAIM_MAPPABLE
HALT_FACTOR = 2.0


def load_rows(path):
    with io.open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def census(rows, by_fk):
    """Classify every row: does its stored scalar locus match its own source record?"""
    classes = collections.Counter()
    wrong = []
    hom_map = collections.defaultdict(collections.Counter)
    wrong_keys = collections.Counter()
    for i, r in enumerate(rows):
        stem, enum_idx = split_subcard(r.get('subcard') or '')
        recs = by_fk.get(cg.form_key(stem)) if stem else None
        stored = r.get('column')
        if not recs:
            classes['no_source_record' + ('' if stored else '_unannotated')] += 1
            continue
        locus = resolve_locus(recs, enum_idx)
        if locus is AMBIGUOUS:
            classes['unresolvable_index'] += 1
            if stored:
                wrong_keys[r.get('key1')] += 1
                wrong.append({'line': i + 1, 'key1': r.get('key1'),
                              'subcard': r.get('subcard'), 'enum_index': enum_idx,
                              'n_source_records': len(recs), 'stored_column': stored,
                              'true_column': None, 'rule': 'omit-ambiguous'})
            continue
        hom_map['none' if enum_idx is None else enum_idx][locus.h or 'none'] += 1
        true_col = pc_str(locus.vol, locus.col)
        if stored is None:
            classes['unannotated_but_mappable'] += 1
        elif stored == true_col:
            classes['locus_correct'] += 1
        else:
            classes['locus_wrong'] += 1
            wrong_keys[r.get('key1')] += 1
            wrong.append({'line': i + 1, 'key1': r.get('key1'), 'subcard': r.get('subcard'),
                          'enum_index': enum_idx, 'n_source_records': len(recs),
                          'stored_column': stored, 'true_column': true_col,
                          'printed_homonym': locus.h, 'rule': 'positional'})
    ordered = sorted(hom_map.items(), key=lambda kv: (kv[0] == 'none', kv[0]))
    return {'classes': dict(classes), 'wrong': wrong,
            'wrong_headwords': len(wrong_keys),
            'wrong_by_key': wrong_keys.most_common(),
            'enum_to_printed_homonym': {str(k): dict(v) for k, v in ordered}}


def verdict(layer):
    """Ruling 14: a >=2x divergence from the issue's claim halts the rewrite half."""
    mappable, wrong = layer['mappable'], layer['wrong']
    share = (wrong / mappable) if mappable else 0.0
    ratio = share / ISSUE_CLAIM_SHARE
    halt = bool(ratio >= HALT_FACTOR or ratio <= 1.0 / HALT_FACTOR)
    return {'pwg_layer_mappable_rows': mappable, 'pwg_layer_wrong_rows': wrong,
            'measured_share': share, 'issue_claimed_share': ISSUE_CLAIM_SHARE,
            'ratio_measured_over_claimed': ratio, 'halt_factor': HALT_FACTOR,
            'halt_rewrite': halt}


def pwg_layer_slice(rows, by_fk):
    """The issue's own denominator: pwg-layer rows that map to a source record."""
    res = census([r for r in rows if r.get('layer') == 'pwg'], by_fk)
    c = res['classes']
    return {'mappable': c.get('locus_correct', 0) + c.get('locus_wrong', 0),
            'wrong': c.get('locus_wrong', 0), 'classes': c,
            'headwords': res['wrong_headwords']}


def write_report(path, result):
    v = result['verdict']
    full = result['full_store']
    lines = [
        '# H3751 census -- homograph locus vs the stored `~~h<N>` enumerate index (#1801)',
        '',
        '_Created: 31-08-2026 · Last updated: 31-08-2026_',
        '',
        'Generated by [`src/h3751_homonym_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3751_homonym_census.py), '
        'read-only. Store: %d rows. PWG source: %d records.'
        % (result['store_rows'], result['source_records']),
        '',
        '## Verdict (plan ruling 14)',
        '',
        '| Measure | Value |',
        '|---|---|',
        '| pwg-layer mappable rows | %d |' % v['pwg_layer_mappable_rows'],
        "| pwg-layer rows carrying another homograph's column | %d |" % v['pwg_layer_wrong_rows'],
        '| measured share | %.1f %% |' % (100 * v['measured_share']),
        '| issue #1801 claimed share (1,278 / 5,211) | %.1f %% |' % (100 * v['issue_claimed_share']),
        '| ratio measured / claimed | %.2fx |' % v['ratio_measured_over_claimed'],
        '| **halt the rewrite half?** | **%s** |' % ('YES' if v['halt_rewrite'] else 'no'),
        '',
        '## Whole-store classification',
        '',
        '| Class | Rows |',
        '|---|---|',
    ]
    for k, n in sorted(full['classes'].items()):
        lines.append('| `%s` | %d |' % (k, n))
    lines += ['', '## What `~~h<N>` actually maps to', '',
              'Rows grouped by their enumerate index, counted against the **printed** `<h>` '
              'of the source record that index addresses. A true homonym number would be '
              'diagonal. It is not.', '',
              '| enumerate `~~h<N>` | printed `<h>` -> rows |', '|---|---|']
    for k, dist in full['enum_to_printed_homonym'].items():
        pretty = ', '.join('`%s` x%d' % (h, n)
                           for h, n in sorted(dist.items(), key=lambda kv: -kv[1]))
        lines.append('| `%s` | %s |' % (k, pretty))
    lines += ['', '## Most affected headwords', '', '| key1 | wrong rows |', '|---|---|']
    for key, n in full['wrong_by_key'][:25]:
        lines.append('| `%s` | %d |' % (key, n))
    post = result.get('postcheck')
    if post:
        pv, pc = post['verdict'], post['full_store']['classes']
        lines += ['', '## Post-rewrite verification', '',
                  'The same census re-run against `%s` after the ledgered rewrite '
                  '(`src/h3751_apply_homonym_locus.py --apply`).' % post['store'], '',
                  '| Measure | Value |', '|---|---|',
                  '| pwg-layer mappable rows | %d |' % pv['pwg_layer_mappable_rows'],
                  '| pwg-layer rows still carrying a foreign column | %d |'
                  % pv['pwg_layer_wrong_rows'],
                  '| `locus_correct` | %d |' % pc.get('locus_correct', 0),
                  '| `locus_wrong` | %d |' % pc.get('locus_wrong', 0),
                  '| `unresolvable_index` | %d |' % pc.get('unresolvable_index', 0),
                  '| `unannotated_but_mappable` | %d |'
                  % pc.get('unannotated_but_mappable', 0),
                  '',
                  'The ruling-14 verdict above is the **pre-rewrite** measurement, which is '
                  'the one that authorized the rewrite; re-running the verdict on the '
                  'repaired store trivially reads "halt" because the wrong population is '
                  'now zero.']
    lines += ['', '_Dr. Mārcis Gasūns_', '']
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--json', default=None)
    ap.add_argument('--report', default=None)
    ap.add_argument('--postcheck', default=None, metavar='STORE',
                    help='also census this store and append a verification section '
                         '(use --store <pre-rewrite backup> --postcheck <live store>)')
    args = ap.parse_args()

    entries = parse_source(args.src)
    by_fk = index_by_form_key(entries)
    rows = load_rows(args.store)
    print('parsed %d PWG records; loaded %d store rows' % (len(entries), len(rows)))

    full = census(rows, by_fk)
    layer = pwg_layer_slice(rows, by_fk)
    v = verdict(layer)
    result = {'store': args.store, 'src': args.src, 'store_rows': len(rows),
              'source_records': len(entries), 'full_store': full,
              'pwg_layer': layer, 'verdict': v}

    print('--- whole store ---')
    for k, n in sorted(full['classes'].items()):
        print('  %-34s %6d' % (k, n))
    print('--- pwg layer (issue #1801 denominator) ---')
    print('  mappable=%d wrong=%d share=%.3f (issue claimed %.3f, ratio %.2fx)'
          % (layer['mappable'], layer['wrong'], v['measured_share'],
             v['issue_claimed_share'], v['ratio_measured_over_claimed']))
    print('  HALT_REWRITE=%s' % v['halt_rewrite'])

    if args.postcheck:
        post_rows = load_rows(args.postcheck)
        post_full = census(post_rows, by_fk)
        post_layer = pwg_layer_slice(post_rows, by_fk)
        result['postcheck'] = {'store': args.postcheck, 'store_rows': len(post_rows),
                               'full_store': post_full, 'pwg_layer': post_layer,
                               'verdict': verdict(post_layer)}
        print('--- postcheck %s ---' % args.postcheck)
        for k, n in sorted(post_full['classes'].items()):
            print('  %-34s %6d' % (k, n))

    if args.json:
        with io.open(args.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
        print('wrote %s' % args.json)
    if args.report:
        write_report(args.report, result)
        print('wrote %s' % args.report)
    return 0


if __name__ == '__main__':
    sys.exit(main())
