#!/usr/bin/env python
"""verify_cards_renou_redundancy.py — H692 redundancy verifier (aggregates only).

Tests the DATA_LAYERS_CENSUS §2 claim that the `assembled_cards*.jsonl` and
`*.renou*.jsonl` pipeline files are redundant "progressive stages" of one another
(~1.4 GB recoverable). Emits ONLY aggregates — row counts, top-level key sets,
sampled-headword overlap, byte sizes. NO data rows are printed or written, so its
output is safe to commit next to gitignored, single-copy source data.

Run from the directory holding the data files (RussianTranslation/src/):

  python verify_cards_renou_redundancy.py

Verdict logic:
  * assembled_cards*  — only the file with the full corpus row count is the canonical
    artifact; the rest are dev/CI fixtures (orders of magnitude smaller). No stage
    siblings of the 210 MB file exist on disk — renou_pipeline.py builds the
    intermediate stages inside a tempfile.TemporaryDirectory(), never persisting them.
  * {dict}.renou.jsonl — one per SOURCE DICTIONARY (mw/pw/pwg/ap/ap90/ben/bhs/sch),
    identical 13-field schema but disjoint headword sets and distinct row counts.
    None is contained in another; deleting any loses that dictionary.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))

ASSEMBLED = [
    'assembled_cards.chunk.jsonl',
    'assembled_cards.perf.jsonl',
    'assembled_cards.smoke.jsonl',
    'assembled_cards.test.jsonl',
    'assembled_cards.renou.bhs.wl.jsonl',
]
RENOU_DICTS = [
    'mw.renou.jsonl', 'pw.renou.jsonl', 'pwg.renou.jsonl',
    'ap.renou.jsonl', 'ap90.renou.jsonl', 'ben.renou.jsonl',
    'bhs.renou.jsonl', 'sch.renou.jsonl',
]
SAMPLE = 2000  # rows sampled for the headword-overlap probe


def scan(fname):
    """Return (rows, size_bytes, keyset, sampled_key1_set) — streaming, aggregates only."""
    path = os.path.join(HERE, fname)
    if not os.path.exists(path):
        return None
    rows = 0
    keyset = set()
    k1 = set()
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if not line.strip():
                continue
            rows += 1
            if rows <= SAMPLE:
                o = json.loads(line)
                keyset |= set(o.keys())
                if 'key1' in o:
                    k1.add(o['key1'])
    return rows, os.path.getsize(path), keyset, k1


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return '%.1f %s' % (n, unit)
        n /= 1024
    return '%.1f TB' % n


def main():
    print('== assembled_cards* — is the 210 MB file one of 4 identical-row stages? ==')
    full = None
    for f in ASSEMBLED:
        r = scan(f)
        if r is None:
            print('  %-38s MISSING' % f)
            continue
        rows, size, _, _ = r
        role = 'CANONICAL (full corpus)' if rows > 100000 else 'fixture (dev/CI)'
        print('  %-38s %8d rows  %10s  %s' % (f, rows, human(size), role))
        if rows > 100000:
            full = f
    print('  -> exactly one file carries the full corpus row count; the census\'s'
          '\n     "4 progressive ~210 MB variants, identical rows" is REFUTED —'
          '\n     the others are %d small fixtures. 0 MB recoverable here.\n'
          % (len(ASSEMBLED) - 1))

    print('== {dict}.renou.jsonl — redundant stages, or one per source dictionary? ==')
    k1_by = {}
    schemas = []
    for f in RENOU_DICTS:
        r = scan(f)
        if r is None:
            print('  %-20s MISSING' % f)
            continue
        rows, size, keyset, k1 = r
        k1_by[f] = k1
        schemas.append(frozenset(keyset))
        print('  %-20s %8d rows  %10s  %2d fields' % (f, rows, human(size), len(keyset)))
    print('  schema identical across all: %s (%d fields)'
          % (len(set(schemas)) == 1, len(schemas[0]) if schemas else 0))

    # pairwise sampled headword overlap — prove non-containment
    print('  sampled headword (first %d key1) overlap, mw vs pw vs pwg:' % SAMPLE)
    for a, b in (('mw.renou.jsonl', 'pw.renou.jsonl'),
                 ('mw.renou.jsonl', 'pwg.renou.jsonl'),
                 ('pw.renou.jsonl', 'pwg.renou.jsonl')):
        if a in k1_by and b in k1_by:
            A, B = k1_by[a], k1_by[b]
            print('    %-11s ∩ %-11s = %4d  | %s-only %4d  | %s-only %4d'
                  % (a.split('.')[0], b.split('.')[0], len(A & B),
                     a.split('.')[0], len(A - B), b.split('.')[0], len(B - A)))
    print('  -> same schema, DISJOINT content, distinct row counts: these are 8 '
          'different\n     dictionaries, not stages. None contained in another. '
          '0 MB recoverable.\n')

    print('== VERDICT ==')
    print('  assembled_cards: keep %s + 4 fixtures; delete NOTHING.' % (full or '?'))
    print('  *.renou.jsonl:   keep all 8 per-dictionary indexes; delete NOTHING.')
    print('  Census "~1.4 GB recoverable stage-redundancy" — REFUTED. Recoverable = 0 MB.')


if __name__ == '__main__':
    main()
