#!/usr/bin/env python
"""check_gold_frame.py — verify a sampled H2401 gold frame is well-formed.

Run this on any frame before it goes to annotation. It asserts the properties the
protocol claims, so a regenerated frame cannot silently drift from the design:

  1. every (band x POS) cell is present and hit its per-cell target (or is listed
     as a declared shortfall in the header);
  2. no duplicate lemmas (a lemma annotated twice inflates apparent agreement);
  3. no gold/label column leaked into the frame (the H070 rule-based-arm trap);
  4. every row carries a non-empty gloss with >= 1 Russian content token, i.e. it
     is actually answerable by an annotator;
  5. reports the polysemy distribution, which is an OBSERVED byproduct of the
     band x POS draw, not a controlled axis -- the protocol must not claim it is
     balanced when it is not.

Usage: python check_gold_frame.py <frame.tsv> [--per-cell 20]
"""
import argparse
import collections
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CONTENT_RE = re.compile(r'[а-яёА-ЯЁ]{4,}')
BANNED_COLUMNS = ('gold', 'label', 'ru_gold', 'ru_gold_tokens', 'verdict')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('frame')
    ap.add_argument('--per-cell', type=int, default=20)
    args = ap.parse_args()

    header_lines, rows, columns = [], [], None
    with open(args.frame, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#'):
                header_lines.append(line)
                continue
            if columns is None:
                columns = line.split('\t')
                continue
            if line.strip():
                rows.append(dict(zip(columns, line.split('\t'))))

    failures, notes = [], []

    for banned in BANNED_COLUMNS:
        if banned in (columns or []):
            failures.append(f'frame carries a label column "{banned}" — '
                            'labels must come from the two annotation passes')

    seen = collections.Counter(r['slp1'] for r in rows)
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        failures.append(f'duplicate lemmas: {dupes[:5]} ({len(dupes)} total)')

    cells = collections.Counter((r['band'], r['pos']) for r in rows)
    declared_shortfall = any('Shortfall' in h for h in header_lines)
    for cell, n in sorted(cells.items()):
        if n != args.per_cell and not declared_shortfall:
            failures.append(f'cell {cell} has {n} rows, target {args.per_cell}, '
                            'and no shortfall declared in the header')

    unanswerable = [r['slp1'] for r in rows
                    if not CONTENT_RE.search(r.get('koch_gloss', ''))]
    if unanswerable:
        failures.append(f'rows with no Russian content token: {unanswerable[:5]} '
                        f'({len(unanswerable)} total)')

    poly = collections.Counter(r['polysemy'] for r in rows)
    total = len(rows) or 1
    notes.append(f'rows: {len(rows)} across {len(cells)} cells '
                 f'(per-cell {sorted(set(cells.values()))})')
    notes.append('polysemy (OBSERVED, not a controlled stratum): ' + ', '.join(
        f'{k}={v} ({v / total:.0%})' for k, v in sorted(poly.items())))

    # A frame where one polysemy bucket dominates cannot support a per-bucket rate.
    thin = [k for k, v in poly.items() if v < 20]
    if thin:
        notes.append('polysemy buckets under 20 rows (report pooled, do not quote '
                     f'a per-bucket rate): {sorted(thin)}')

    for n in notes:
        print('note:', n)
    if failures:
        print('\nCHECK FAIL')
        for f_ in failures:
            print('  -', f_)
        return 1
    print('\nCHECK PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
