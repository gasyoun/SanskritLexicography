#!/usr/bin/env python
r"""H3751 -- ledgered rewrite of the pwg_ru store's printed-locus fields (issue #1801).

Re-derives `column`/`volume`/`page`/`pc_all`/`page_all` for every store row through the
FIXED `pwg_page_index.compute_annotations` (positional homograph resolution, see
`pwg_homonym.py`) and writes the store back under the H2146 lock -- with a JSONL ledger
row for every field that moved, committed in the same PR as the rewrite (the H3591
store-mutation pattern).

    python src/h3751_apply_homonym_locus.py                       # dry run, writes nothing
    python src/h3751_apply_homonym_locus.py --apply --ledger reports/H3751_locus_ledger.jsonl

Guards, any of which stops the write:

  G1 census premise -- `h3751_homonym_census.py`'s ruling-14 verdict must be "do not halt".
     A census that no longer reproduces issue #1801's population voids the authorization to
     rewrite, so this refuses rather than proceeding on a broken premise.
  G2 field fence    -- no field outside `pwg_page_index.PC_FIELDS` may differ before/after.
     Anything else means the recomputation touched translation content; that is never this
     tool's business.
  G3 delta==ledger  -- after the write the store is re-read from disk and diffed against the
     fsynced backup; the set of changed (row, field) pairs must equal the ledger exactly.
     A mismatch is reported and the backup path printed for a one-command restore.

The `pwg-ru-data/tm/` mirror is deliberately NOT touched here: the mirror refresh is the
LAST step of the unit (`refresh_tm_mirror.py --handoff H3751 --apply`), never the first, so
the mirror stays one commit behind as the rollback of record until the rewrite is proven.
"""
import argparse
import collections
import io
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import h3751_homonym_census as census_mod                             # noqa: E402
from pwg_homonym import split_subcard                                 # noqa: E402
from pwg_page_index import (                                          # noqa: E402
    DEFAULT_SRC, PC_FIELDS, compute_annotations, parse_source,
)
from store_path import canonical_store                                # noqa: E402
from store_write import locked_store_rewrite                          # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
DEFAULT_LEDGER = os.path.normpath(os.path.join(HERE, '..', 'reports',
                                               'H3751_locus_ledger.jsonl'))
SCHEMA = 'pwg_ru.h3751_locus_rewrite.v1'


def load_rows(path):
    with io.open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def row_key(row):
    """Positional identity is enough here: the rewrite never adds, drops or reorders rows."""
    return (row.get('key1') or '', row.get('subcard') or '', row.get('sense_tag') or '')


def field_delta(before, after):
    """`{field: (old, new)}` for every field that differs between two row dicts."""
    delta = {}
    for field in set(before) | set(after):
        old, new = before.get(field, KeyError), after.get(field, KeyError)
        if old != new:
            delta[field] = (None if old is KeyError else old,
                            None if new is KeyError else new)
    return delta


def classify(delta, before, after):
    """A short, countable name for what happened to this row's locus."""
    if 'column' in delta:
        if delta['column'][0] is None:
            return 'scalar_added'
        if delta['column'][1] is None:
            return 'scalar_omitted_ambiguous'
        return 'scalar_repointed'
    if delta:
        return 'headword_fields_only'
    return 'unchanged'


def build_ledger(before_rows, after_rows, entries_count, src):
    ledger, classes, off_fence = [], collections.Counter(), []
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    for i, (b, a) in enumerate(zip(before_rows, after_rows)):
        delta = field_delta(b, a)
        if not delta:
            classes['unchanged'] += 1
            continue
        stray = sorted(set(delta) - set(PC_FIELDS))
        if stray:
            off_fence.append({'line': i + 1, 'row': row_key(b), 'fields': stray})
            continue
        cls = classify(delta, b, a)
        classes[cls] += 1
        stem, enum_idx = split_subcard(a.get('subcard') or '')
        ledger.append({
            'schema': SCHEMA, 'handoff': 'H3751', 'issue': 1801, 'ts': ts,
            'line': i + 1, 'key1': a.get('key1'), 'subcard': a.get('subcard'),
            'sense_tag': a.get('sense_tag'), 'generation_key': stem,
            'enum_index': enum_idx, 'class': cls,
            'rule': 'positional homograph resolution (pwg_homonym.resolve_locus)',
            'src': os.path.basename(src), 'src_records': entries_count,
            'changed': {f: {'old': o, 'new': n} for f, (o, n) in sorted(delta.items())},
        })
    return ledger, classes, off_fence


def verify(before_rows, store_path, ledger):
    """G3: the on-disk delta must equal the ledger exactly."""
    after_rows = load_rows(store_path)
    if len(after_rows) != len(before_rows):
        return False, 'row count moved: %d -> %d' % (len(before_rows), len(after_rows))
    on_disk = set()
    for i, (b, a) in enumerate(zip(before_rows, after_rows)):
        for field in field_delta(b, a):
            on_disk.add((i + 1, field))
    claimed = {(row['line'], field) for row in ledger for field in row['changed']}
    if on_disk != claimed:
        extra = sorted(on_disk - claimed)[:8]
        missing = sorted(claimed - on_disk)[:8]
        return False, 'delta != ledger (unledgered %d e.g. %r; ledgered-but-absent %d e.g. %r)' % (
            len(on_disk - claimed), extra, len(claimed - on_disk), missing)
    return True, 'delta == ledger (%d row-field changes over %d rows)' % (
        len(claimed), len({r['line'] for r in ledger}))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--ledger', default=DEFAULT_LEDGER)
    ap.add_argument('--apply', action='store_true', help='actually rewrite the store')
    ap.add_argument('--skip-census-guard', action='store_true',
                    help='G1 escape; only for a fixture store, never the canonical one')
    args = ap.parse_args()

    entries = parse_source(args.src)
    before_rows = load_rows(args.store)
    print('parsed %d PWG records; loaded %d store rows from %s'
          % (len(entries), len(before_rows), args.store))

    # G1 -- the rewrite is authorized by the census reproducing issue #1801's population.
    by_fk = census_mod.index_by_form_key(entries)
    layer = census_mod.pwg_layer_slice(before_rows, by_fk)
    v = census_mod.verdict(layer)
    print('G1 census: pwg-layer mappable=%d wrong=%d share=%.3f ratio=%.2fx halt=%s'
          % (layer['mappable'], layer['wrong'], v['measured_share'],
             v['ratio_measured_over_claimed'], v['halt_rewrite']))
    if v['halt_rewrite'] and not args.skip_census_guard:
        print('G1 REFUSE: ruling 14 -- the census diverges >=%gx from issue #1801; '
              'deliver census-only, do not rewrite.' % census_mod.HALT_FACTOR)
        return 3

    after_rows = [dict(r) for r in before_rows]
    stats = compute_annotations(entries, after_rows)
    ledger, classes, off_fence = build_ledger(before_rows, after_rows, len(entries), args.src)

    print('annotation: matched=%d ambiguous=%d unmatched=%d'
          % (stats['matched'], stats['ambiguous'], stats['unmatched']))
    print('delta by class:')
    for k, n in sorted(classes.items()):
        print('  %-28s %6d' % (k, n))
    print('ledger rows: %d' % len(ledger))

    # G2 -- nothing outside the pc fields may move.
    if off_fence:
        print('G2 REFUSE: %d row(s) differ outside %r, e.g. %r'
              % (len(off_fence), list(PC_FIELDS), off_fence[:5]))
        return 4

    if not args.apply:
        print('DRY RUN -- nothing written. Re-run with --apply --ledger <path>.')
        for row in ledger[:5]:
            print('  sample: %s %s %s' % (row['key1'], row['subcard'],
                                          json.dumps(row['changed'], ensure_ascii=False)[:140]))
        return 0

    if not ledger:
        print('nothing to do: the store already matches the fixed annotation.')
        return 0

    bak = locked_store_rewrite(args.store, after_rows, tag='h3751')
    print('rewrote %s (backup: %s)' % (args.store, bak))

    os.makedirs(os.path.dirname(args.ledger), exist_ok=True)
    with io.open(args.ledger, 'w', encoding='utf-8', newline='\n') as f:
        for row in ledger:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('wrote ledger %s (%d rows)' % (args.ledger, len(ledger)))

    ok, msg = verify(before_rows, args.store, ledger)
    print('G3 %s: %s' % ('PASS' if ok else 'FAIL', msg))
    if not ok:
        print('restore with: copy "%s" "%s"' % (bak, args.store))
        return 5
    return 0


if __name__ == '__main__':
    sys.exit(main())
