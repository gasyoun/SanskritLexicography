#!/usr/bin/env python
r"""Backfill store ``citation_edges`` from DE (H1624 G3).

Streams the translated store and stamps
``citation_edges = extract_citation_edges(de)`` on every row. New promotions
already stamp this in promote_final_cards; this is the retrofit path.

Does not modify the ``de`` string (raw ``<ls>`` stays).

  python src/annotate_citation_edges.py              # annotate store in place
  python src/annotate_citation_edges.py --dry-run
  python src/annotate_citation_edges.py --selftest
  python src/annotate_citation_edges.py --report     # coverage only (no write)
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

from citation_edges import extract_citation_edges, coverage_stats, report_store
from store_path import canonical_store
from store_write import locked_store_rewrite

STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))


def load_rows(store):
    return [json.loads(l) for l in open(store, encoding='utf-8') if l.strip()]


def write_rows(store, rows, no_backup):
    # H2146: locked (PromoteClaim) + unique fsynced backup + atomic replace — the old
    # in-place rewrite was unlocked and left a truncated store on crash (FINDINGS §513).
    locked_store_rewrite(store, rows, tag='precite', no_backup=no_backup)


def selftest():
    de = '{%Feuer%} <ls>ṚV. 1,1,1</ls>; <ls n="MBH.">3,50</ls>.'
    edges = extract_citation_edges(de)
    assert len(edges) == 2, edges
    assert edges[0]['siglum'] == 'ṚV' and edges[0]['resolver_status'] == 'map', edges
    assert edges[0]['page'] == '1,1,1', edges
    assert edges[1]['n_attr'] == 'MBH.', edges
    # DE not rewritten
    assert '<ls>ṚV. 1,1,1</ls>' in de
    assert extract_citation_edges('') == []
    print('annotate_citation_edges selftest: OK')


def run(store, dry_run, no_backup, report_only):
    if report_only:
        if not os.path.exists(store):
            print('store missing: %s' % store, file=sys.stderr)
            sys.exit(2)
        stats = report_store(store)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return stats
    rows = load_rows(store)
    all_edges = []
    populated = 0
    for r in rows:
        edges = extract_citation_edges(r.get('de'))
        r['citation_edges'] = edges
        all_edges.extend(edges)
        if edges:
            populated += 1
    stats = coverage_stats(all_edges)
    print('=== CITATION EDGES ANNOTATION ===')
    print('store rows              : %d' % len(rows))
    print('rows with >=1 edge      : %d (%.1f%%)' % (
        populated, 100 * populated / max(1, len(rows))))
    print('edges total             : %d' % stats['total'])
    print('  map (ls_source_map)   : %d (%.1f%%)' % (stats['map'], stats['map_pct']))
    print('  bib (pwgbib only)     : %d' % stats['bib'])
    print('  orphan                : %d (%.1f%%)' % (stats['orphan'], stats['orphan_pct']))
    print('  resolvable (map+bib)  : %d (%.1f%%)' % (
        stats['resolvable'], stats['resolvable_pct']))
    if dry_run or report_only:
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
    ap.add_argument('--report', action='store_true',
                    help='coverage report only (no write)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    run(args.store, args.dry_run, args.no_backup, args.report)


if __name__ == '__main__':
    main()
