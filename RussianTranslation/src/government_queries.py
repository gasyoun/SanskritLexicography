#!/usr/bin/env python
r"""Standalone case-government queries over the annotated store (H335 W3(b) / H338).

Fallback reader: H337's shared ``annotation_report.py`` query CLI had not landed at
build time, so these three queries are implemented standalone here instead of being
folded into it (per H338 step 4's explicit fallback clause). If/when
``annotation_report.py`` lands, these functions are pure and importable — fold them in
there and keep this file as a thin CLI, or retire it.

Reads ``government`` fields written by ``annotate_government.py`` (a list of structured
hit dicts per row: ``{cases, variation, connector, kind, span}``).

Queries:
  (a) --loc-required   senses requiring loc. only (cases == ['loc'], no variation)
  (b) --variation      senses with case variation (>1 case in one marker)
  (c) --never-gen      per-root (key1, layer=='pwg') aggregation: roots that carry
                       >=1 government marker but NEVER govern gen. "No marker at all"
                       is kept separate as unknown — never counted as "never governs".

  python src/government_queries.py                 # all three, summary counts
  python src/government_queries.py --loc-required --limit 20
  python src/government_queries.py --never-gen --limit 20
  python src/government_queries.py --selftest
"""
import argparse
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')


def load_store(path=STORE):
    return [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]


def loc_required(rows):
    """(a) senses requiring loc. only — a single-case marker whose case is loc."""
    out = []
    for r in rows:
        for hit in r.get('government') or []:
            if not hit['variation'] and hit['cases'] == ['loc']:
                out.append(r)
                break
    return out


def case_variation(rows):
    """(b) senses whose government carries a variation marker (>1 case)."""
    return [r for r in rows
            if any(hit['variation'] for hit in (r.get('government') or []))]


def root_case_summary(pwg_rows):
    """Per-root (key1) aggregation: has_marker + union of all cases governed."""
    summary = defaultdict(lambda: {'has_marker': False, 'cases': set()})
    for r in pwg_rows:
        d = summary[r.get('key1')]
        hits = r.get('government') or []
        if hits:
            d['has_marker'] = True
        for hit in hits:
            d['cases'].update(hit['cases'])
    return summary


def never_governs_gen(rows):
    """(c) roots (layer=='pwg') that carry >=1 marker but never 'gen'. Returns
    (never_list, unknown_list) — unknown = no marker at all, kept separate."""
    pwg_rows = [r for r in rows if r.get('layer') == 'pwg']
    summary = root_case_summary(pwg_rows)
    never = sorted(k for k, d in summary.items() if d['has_marker'] and 'gen' not in d['cases'])
    unknown = sorted(k for k, d in summary.items() if not d['has_marker'])
    return never, unknown


def selftest():
    rows = [
        {'key1': 'snih', 'layer': 'pwg', 'government': [
            {'cases': ['loc'], 'variation': False, 'connector': '', 'kind': 'paren-single', 'span': ''},
        ]},
        {'key1': 'snih', 'layer': 'pwg', 'government': [
            {'cases': ['loc', 'gen'], 'variation': True, 'connector': 'und', 'kind': 'paren-variation', 'span': ''},
        ]},
        {'key1': 'sTA', 'layer': 'pwg', 'government': [
            {'cases': ['loc'], 'variation': False, 'connector': '', 'kind': 'paren-single', 'span': ''},
        ]},
        {'key1': 'gam', 'layer': 'pwg', 'government': []},
        {'key1': 'gam', 'layer': 'pw', 'government': [
            {'cases': ['acc'], 'variation': False, 'connector': '', 'kind': 'paren-single', 'span': ''},
        ]},
    ]
    loc_hits = loc_required(rows)
    assert len(loc_hits) == 2, loc_hits  # snih[0] (bare loc), sTA (bare loc)
    var_hits = case_variation(rows)
    assert len(var_hits) == 1 and var_hits[0]['key1'] == 'snih', var_hits
    never, unknown = never_governs_gen(rows)
    # sTA: only loc ever -> never-gen. snih: has a gen (via variation) -> excluded.
    # gam: only a 'pw'-layer row has a marker; its lone 'pwg' row is markerless -> unknown.
    assert never == ['sTA'], never
    assert unknown == ['gam'], unknown
    print('government_queries selftest: OK')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--loc-required', action='store_true')
    ap.add_argument('--variation', action='store_true')
    ap.add_argument('--never-gen', action='store_true')
    ap.add_argument('--limit', type=int, default=15)
    ap.add_argument('--summary', action='store_true',
                    help='corpus-level marker totals from the frozen census sidecar '
                         '(H778) — no store reload, no pwg.txt re-scan')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    if args.summary:
        # The corpus-level "how many such markers in PWG" answer is a settled count —
        # read it from the committed census_stats.json rather than re-scanning (H778).
        import government_census as gc
        census, origin = gc.census_or_load()
        gov_total = sum(n for k, n in census['kinds'].items() if k != 'paren-nongov')
        print('census source: %s' % origin)
        print('government markers (total)       : %d' % gov_total)
        print('  paren-single / variation / mit : %d / %d / %d' % (
            census['kinds'].get('paren-single', 0),
            census['kinds'].get('paren-variation', 0),
            census['kinds'].get('mit-phrase', 0)))
        print('entries with >=1 marker          : %d' % census['entries_with'])
        print('sense units with >=1 marker      : %d' % census['units_with'])
        print('(per-row listing queries still stream the store — the rows are not frozen)')
        return

    rows = load_store(args.store)
    run_all = not (args.loc_required or args.variation or args.never_gen)

    if run_all or args.loc_required:
        hits = loc_required(rows)
        print('(a) senses requiring loc. only: %d' % len(hits))
        for r in hits[:args.limit]:
            print('  %-12s %-20s sense=%s' % (r.get('key1'), r.get('iast') or r.get('h'), r.get('sense_tag')))

    if run_all or args.variation:
        hits = case_variation(rows)
        print('(b) senses with case variation: %d' % len(hits))
        for r in hits[:args.limit]:
            cases = [h['cases'] for h in r.get('government') or [] if h['variation']]
            print('  %-12s %-20s sense=%s cases=%s' % (
                r.get('key1'), r.get('iast') or r.get('h'), r.get('sense_tag'), cases))

    if run_all or args.never_gen:
        never, unknown = never_governs_gen(rows)
        print('(c) roots (layer=pwg) that carry a marker but never gen.: %d (unknown/no-marker: %d)' % (
            len(never), len(unknown)))
        for k in never[:args.limit]:
            print('  %s' % k)


if __name__ == '__main__':
    main()
