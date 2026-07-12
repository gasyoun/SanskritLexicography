#!/usr/bin/env python
"""Build a scan-verification anchor sheet for the DERIVED PWG page numbers.

pwg_page_index.py derives a physical page from a column via
    page = (column + 1) // 2   (2 columns per leaf, column 1 on page 1)
That derivation is NOT stored in the source and can be off by a constant
per-volume front-matter offset (or, worse, the (2k-1, 2k) pairing could be
shifted). PWG is cited by COLUMN (Spalte) and the scans print column numbers,
so a scan verifies the PAIRING/OFFSET, not a page label.

This tool emits anchor rows a human takes to the scan. For each anchor
(physical page P in volume V) it names the two columns the formula assigns to
that leaf -- left = 2P-1, right = 2P -- and, for each, the first headword that
STARTS in that column (the landmark to locate on the scan), in SLP1 / IAST /
Devanagari. The verifier fills:

    scan_leaf        page/leaf label actually printed on the scan (blank if the
                     book labels only columns -- then just confirm the pairing)
    cols_on_leaf     the two column numbers actually printed together on that leaf
    offset           scan_leaf - derived_page  (should be constant within a volume)
    paired_ok        Y if the two columns above == (2P-1, 2P), else N

If offset is constant per volume and paired_ok is all Y, the derivation holds
(shifted by that offset). Any drift is a real defect to chase.

Anchors per volume: first leaf, last leaf, and evenly spaced interior leaves
(--per, default 10). Deterministic; no Date.now / randomness.
"""
import argparse
import collections
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from indic_transliteration import sanscript
    def iast(x): return sanscript.transliterate(x, sanscript.SLP1, sanscript.IAST)
    def deva(x): return sanscript.transliterate(x, sanscript.SLP1, sanscript.DEVANAGARI)
except Exception:  # pragma: no cover - lib optional
    def iast(x): return ''
    def deva(x): return ''

DEFAULT_COLS = 'pwg_columns.tsv'


def load_columns(path):
    """(vol, col) -> first headword (SLP1) that starts in that column."""
    first = {}
    per_vol = collections.defaultdict(list)
    with io.open(path, encoding='utf-8') as f:
        next(f)
        for line in f:
            p = line.rstrip('\n').split('\t')
            pc, vol = p[0], int(p[1])
            col = int(pc.split('-')[1])
            heads = p[5].split(', ') if len(p) > 5 else []
            if (vol, col) not in first:
                first[(vol, col)] = heads[0] if heads else ''
                per_vol[vol].append(col)
    for v in per_vol:
        per_vol[v].sort()
    return first, per_vol


def anchor_pages(cols_present, per):
    """Choose ~`per` physical-page anchors spread across a volume's columns."""
    if not cols_present:
        return []
    pages = sorted({(c + 1) // 2 for c in cols_present})
    if len(pages) <= per:
        return pages
    step = (len(pages) - 1) / (per - 1)
    idx = sorted({round(i * step) for i in range(per)})
    return [pages[i] for i in idx]


def landmark(first, vol, col):
    hw = first.get((vol, col))
    if not hw:
        return '(continuation / no new entry)', '', ''
    return hw, iast(hw), deva(hw)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cols', default=DEFAULT_COLS, help='pwg_columns.tsv path')
    ap.add_argument('--per', type=int, default=10, help='anchor leaves per volume')
    ap.add_argument('--out', default='pwg_page_verification.tsv',
                    help='fillable anchor sheet (TSV)')
    args = ap.parse_args()

    first, per_vol = load_columns(args.cols)

    rows = []
    for vol in sorted(per_vol):
        for pg in anchor_pages(per_vol[vol], args.per):
            lcol, rcol = 2 * pg - 1, 2 * pg
            l_slp, l_iast, l_deva = landmark(first, vol, lcol)
            r_slp, r_iast, r_deva = landmark(first, vol, rcol)
            rows.append([
                vol, pg,
                f'{vol}-{lcol:04d}', l_slp, l_iast, l_deva,
                f'{vol}-{rcol:04d}', r_slp, r_iast, r_deva,
                '', '', '', '',  # scan_leaf, cols_on_leaf, offset, paired_ok
            ])

    header = ['volume', 'derived_page',
              'left_pc', 'left_hw_slp1', 'left_hw_iast', 'left_hw_deva',
              'right_pc', 'right_hw_slp1', 'right_hw_iast', 'right_hw_deva',
              'scan_leaf', 'cols_on_leaf', 'offset', 'paired_ok']
    with io.open(args.out, 'w', encoding='utf-8') as f:
        f.write('\t'.join(header) + '\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print(f'wrote {len(rows)} anchor rows across {len(per_vol)} volumes -> {args.out}')


if __name__ == '__main__':
    main()
