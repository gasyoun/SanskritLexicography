#!/usr/bin/env python
"""H1651 deterministic store repair for D1 (Cyrillic-in-{#...#}) and D3 (gloss-wrapper
drift: DE {%...%} rendered as RU «...»).

D1 -- every {#...#} span containing Cyrillic is rewrapped to {%...%}. Content is
unchanged; only the wrapper delimiter changes (Cyrillic is never valid inside {#...#},
so this has no false-positive mode -- see wrapper_defect_scan.find_d1).

D3 -- for rows where the DE gloss-slot count ({%...%}) exactly matches the RU
guillemet-span count («...»), every «...» in ru is rewrapped to {%...%} (matches the
store's own documented convention -- pwg_ru/DATA_STATEMENT.md section D: "{%...%} --
italicized glosses/emphases from the print"; «...» is not a documented store wrapper).
Rows where the counts do NOT match are left untouched and reported for manual review
-- a count mismatch means at least one guillemet span is not a clean 1:1 gloss-drift
instance (nested quote, stray «...», or a genuine translation-structure difference),
so a positional swap risks corrupting content.

  python src/pilot/fix_wrapper_defects.py --store [--dry-run]
"""
import argparse
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from wrapper_defect_scan import (  # noqa: E402
    SKT_SPAN, GLOSS_SPAN, GUILLEMET_SPAN, find_d1,
)


def fix_d1(ru_text):
    """Rewrap {#...#} spans that contain Cyrillic to {%...%}. Returns (text, n_fixed)."""
    if not ru_text:
        return ru_text, 0
    n = [0]

    def repl(m):
        inner = m.group(1)
        from wrapper_defect_scan import CYR
        if CYR.search(inner):
            n[0] += 1
            return '{%' + inner + '%}'
        return m.group(0)

    fixed = SKT_SPAN.sub(repl, ru_text)
    return fixed, n[0]


def fix_d3(de_text, ru_text):
    """Rewrap ALL «...» in ru to {%...%} iff de-gloss-count == ru-guillemet-count.
    Returns (text, n_fixed, eligible)."""
    if not ru_text or not de_text:
        return ru_text, 0, False
    de_n = len(GLOSS_SPAN.findall(de_text))
    ru_n = len(GUILLEMET_SPAN.findall(ru_text))
    if de_n == 0 or ru_n == 0 or de_n != ru_n:
        return ru_text, 0, False
    fixed, count = GUILLEMET_SPAN.subn(lambda m: '{%' + m.group(1) + '%}', ru_text)
    return fixed, count, True


def run_store(dry=False):
    from store_path import canonical_store
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = canonical_store(default_local)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)

    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line:
                rows.append(json.loads(line))

    d1_touched, d3_touched, d3_skipped_mismatch = [], [], []
    for r in rows:
        ru = r.get('ru') or ''
        de = r.get('de') or ''
        label = '%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag'))

        d1_before = find_d1(ru)
        new_ru, n1 = fix_d1(ru)
        if n1:
            d1_touched.append((label, n1))
            ru = new_ru

        de_n = len(GLOSS_SPAN.findall(de))
        ru_guillemet_n = len(GUILLEMET_SPAN.findall(ru))
        if ru_guillemet_n:
            new_ru2, n3, eligible = fix_d3(de, ru)
            if eligible and n3:
                d3_touched.append((label, n3))
                ru = new_ru2
            elif ru_guillemet_n and de_n != ru_guillemet_n:
                d3_skipped_mismatch.append((label, de_n, ru_guillemet_n))

        if not dry:
            r['ru'] = ru

    print('STORE MODE %s' % ('(DRY RUN)' if dry else ''))
    print('store              : %s' % store)
    print('rows               : %d' % len(rows))
    print('D1 rows fixed      : %d (%d spans)' % (
        len(d1_touched), sum(n for _, n in d1_touched)))
    print('D3 rows fixed      : %d (%d spans)' % (
        len(d3_touched), sum(n for _, n in d3_touched)))
    print('D3 skipped (count mismatch, needs manual review): %d' % len(d3_skipped_mismatch))
    for label, de_n, ru_n in d3_skipped_mismatch:
        print('  %-40s de=%d ru=%d' % (label, de_n, ru_n))

    if not dry and (d1_touched or d3_touched):
        bak = store + '.h1651.bak'
        if not os.path.exists(bak):
            shutil.copyfile(store, bak)
            print('backup             : %s' % bak)
        # H2146: locked (PromoteClaim) + unique per-run backup + atomic replace — the
        # fixed '.tmp' rewrite was unlocked (last-writer-wins, FINDINGS §513); the
        # one-time .h1651.bak above stays as the pre-campaign forensic copy.
        from store_write import locked_store_rewrite
        locked_store_rewrite(store, rows, tag='h1651fix')
        print('wrote              : %s' % store)

    return {
        'd1_rows': len(d1_touched),
        'd1_spans': sum(n for _, n in d1_touched),
        'd3_rows': len(d3_touched),
        'd3_spans': sum(n for _, n in d3_touched),
        'd3_skipped': [
            {'label': label, 'de_n': de_n, 'ru_n': ru_n}
            for label, de_n, ru_n in d3_skipped_mismatch
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', action='store_true', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    run_store(dry=args.dry_run)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
