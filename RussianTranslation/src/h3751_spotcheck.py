#!/usr/bin/env python
r"""H3751 own-data spot check -- show the primary sources behind a sample of the rewrite.

For a handful of affected rows this prints the row's sub-card key, the PWG source records
its enumerate index ranges over (with their printed `<h>` and `<pc>` straight from
csl-orig), the locus the store held, and the locus the fix assigns -- so the repair can be
read against the printed page rather than trusted.

    python src/h3751_spotcheck.py [--key1 Ap] [--limit 6]
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

import corpus_gate as cg                                              # noqa: E402
from pwg_homonym import index_by_form_key, split_subcard              # noqa: E402
from pwg_page_index import (                                          # noqa: E402
    DEFAULT_SRC, compute_annotations, page_of, parse_source, pc_str,
)
from store_path import canonical_store                                # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--key1', action='append', default=None,
                    help='restrict to these key1 values (repeatable)')
    ap.add_argument('--limit', type=int, default=6, help='sub-cards to show')
    args = ap.parse_args()

    entries = parse_source(args.src)
    by_fk = index_by_form_key(entries)
    with io.open(args.store, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]

    after = [dict(r) for r in rows]
    compute_annotations(entries, after)

    seen = collections.OrderedDict()
    for b, a in zip(rows, after):
        if b.get('column') == a.get('column'):
            continue
        if args.key1 and b.get('key1') not in args.key1:
            continue
        seen.setdefault(b.get('subcard'), (b, a))
        if len(seen) >= args.limit:
            break

    for subcard, (b, a) in seen.items():
        stem, idx = split_subcard(subcard or '')
        recs = by_fk.get(cg.form_key(stem)) or []
        print('=' * 78)
        print('sub-card %s   key1=%s   enumerate index=%s of %d source records'
              % (subcard, b.get('key1'), idx, len(recs)))
        for pos, e in enumerate(recs):
            mark = '  <== this record' if pos == (0 if idx is None else idx) else ''
            print('  [%2d] L%-10s <pc>%s  <h>%-4s k1=%s%s'
                  % (pos, e.L, pc_str(e.vol, e.col), e.h or '-', e.k1, mark))
        print('  stored : column=%s volume=%s page=%s'
              % (b.get('column'), b.get('volume'), b.get('page')))
        print('  fixed  : column=%s volume=%s page=%s (page = (col+1)//2 = %s)'
              % (a.get('column'), a.get('volume'), a.get('page'),
                 page_of(recs[0 if idx is None else idx].col) if recs else '-'))
    print('=' * 78)
    print('%d sub-card(s) shown' % len(seen))
    return 0


if __name__ == '__main__':
    sys.exit(main())
