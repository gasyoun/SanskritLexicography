#!/usr/bin/env python
r"""extract_lexical_cores.py — VisualDCS Leonchenko lexical-core .xls/.xlsx -> SLP1 wordlists.

The nominal translation queue (handoff H179) is ordered by lexical priority, not
dictionary letter order. Its tiers come from V.V. Leonchenko's corpus lexical-core
appendices, which live in the sibling VisualDCS repo as legacy Excel files with the
lemmas written in **IAST** (kṛ, bhū, mahat, rājan), NOT SLP1 as the folder README
once claimed. This script converts each core to a plain SLP1 wordlist (the shape
`nominals_worklist.py` consumes) plus a provenance TSV (slp1, iast, pos), deduping
lemmas across the multi-column period sheets.

Sources (in queue-tier order):
  Приложение 10  «стабильная ядерная лексика за всю историю»   440  -> pril10  (tier 2, LEADS)
  Приложение 5   «Лексические ядра ... периодов»              3493  -> pril5   (tier 3)
  Сборное ядро   Consolidated Core                            7532  -> sbornoe (tier 4)

  python src/pilot/extract_lexical_cores.py            # write all three cores
  python src/pilot/extract_lexical_cores.py --core pril5

Writes (tracked, under src/pilot/lexical_cores/):
  <core>.slp1.txt   one SLP1 lemma per line, deduped, source order preserved
  <core>.tsv        slp1<TAB>iast<TAB>pos  (full provenance, incl. POS for verb routing)
"""
import argparse
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))                    # RussianTranslation/
SRC = os.path.join(RT, 'src')
GITHUB = os.path.normpath(os.path.join(RT, '..', '..'))
CORES_DIR = os.path.join(GITHUB, 'VisualDCS', 'derived-data', 'Lexical-Cores')
OUT_DIR = os.path.join(HERE, 'lexical_cores')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

import build_src                                               # noqa: E402  canonical IAST->SLP1

# core -> (filename, kind, lemma columns [0-based], pos column | None)
# Приложение 5 is 7 periods x 2 cols (lemma, POS); lemmas sit in the even columns.
CORES = {
    'pril10': ('Приложение 10. «Список стабильной ядерной лексики за всю историю '
               'санскритской литературы, отраженную в корпусе».xls',
               'xls', [0], 1),
    'pril5':  ('Приложение 5. «Лексические ядра санскритской литературы различных '
               'исторических периодов».xls',
               'xls', [0, 2, 4, 6, 8, 10, 12], None),          # POS is the odd col beside each
    'sbornoe': ('Сборное ядро.xlsx', 'xlsx', [0], 1),
}


def _iter_xls_rows(path):
    import xlrd
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    for r in range(sh.nrows):
        yield [sh.cell_value(r, c) for c in range(sh.ncols)]


def _iter_xlsx_rows(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    for row in ws.iter_rows(values_only=True):
        yield list(row)


def read_core(core):
    """-> list of (slp1, iast, pos, spread), deduped by SLP1, first-seen order.

    Skips the header row and blank/padding cells (the period sheet is blank-padded
    to the longest column). POS for Приложение 5 is the odd column immediately to the
    right of each lemma column. `spread` = the number of distinct lemma columns the
    lemma appears in (1 for single-column cores; 1..7 for Приложение 5's periods) —
    a Leonchenko-period-spread stability signal used as an ordering tiebreak.
    """
    fname, kind, lemma_cols, pos_col = CORES[core]
    path = os.path.join(CORES_DIR, fname)
    if not os.path.exists(path):
        sys.exit('missing source xls: %s' % path)
    rows = list(_iter_xls_rows(path) if kind == 'xls' else _iter_xlsx_rows(path))
    order, meta, spread = [], {}, {}
    for i, row in enumerate(rows):
        if i == 0:
            continue                                           # header
        for lc in lemma_cols:
            if lc >= len(row):
                continue
            iast = str(row[lc]).strip() if row[lc] is not None else ''
            if not iast:
                continue
            pc = pos_col if pos_col is not None else lc + 1
            pos = (str(row[pc]).strip() if pc < len(row) and row[pc] is not None else '')
            slp1 = build_src.iast_to_slp1(iast)
            if not slp1:
                continue
            if slp1 not in meta:
                meta[slp1] = (iast, pos)
                order.append(slp1)
                spread[slp1] = set()
            spread[slp1].add(lc)
    return [(k, meta[k][0], meta[k][1], len(spread[k])) for k in order]


def write_core(core, entries):
    os.makedirs(OUT_DIR, exist_ok=True)
    slp1_path = os.path.join(OUT_DIR, core + '.slp1.txt')
    tsv_path = os.path.join(OUT_DIR, core + '.tsv')
    with open(slp1_path, 'w', encoding='utf-8') as f:
        for slp1, _iast, _pos, _spread in entries:
            f.write(slp1 + '\n')
    with open(tsv_path, 'w', encoding='utf-8') as f:
        f.write('slp1\tiast\tpos\tperiod_spread\n')
        for slp1, iast, pos, spread in entries:
            f.write('%s\t%s\t%s\t%d\n' % (slp1, iast, pos, spread))
    n_verb = sum(1 for _, _, p, _ in entries if p == 'v')
    print('%-8s %5d lemmas (%d verbs) -> %s'
          % (core, len(entries), n_verb, os.path.relpath(slp1_path, RT)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--core', choices=sorted(CORES), help='extract only this core (default: all)')
    args = ap.parse_args()
    cores = [args.core] if args.core else ['pril10', 'pril5', 'sbornoe']
    for core in cores:
        write_core(core, read_core(core))


if __name__ == '__main__':
    main()
