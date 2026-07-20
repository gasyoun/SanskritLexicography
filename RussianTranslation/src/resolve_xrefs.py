#!/usr/bin/env python
"""H1350 W1.7 -- resolve PWG's <ab>s.</ab> ("siehe"/"see") cross-reference redirects.

csl-atlas's scripts/lexico/m3_xrefs.py already extracts PWG's "Vgl." redirects
(kind="vgl", 22,987 rows, gated on the `<div n="v">...<ab>Vgl.</ab>` context) --
reused as-is, not rebuilt. It does NOT extract PWG's OTHER redirect marker,
`<ab>s.</ab>` ("siehe unten"/plain "s." -- 8,128 raw occurrences), because that
marker is genuinely mixed-target: most instances point at a grammar-rule
citation ("s. P. 6,2,2"), not a Sanskrit lemma. This script applies the SAME
lemma-likeness discipline m3_xrefs.py already uses for Apte's ambiguous
`cf. {#...#}` (a single SLP1 token, no space/period, <=24 chars) so only the
genuinely lemma-pointing subset becomes an edge; the rest is left alone
(never guessed -- D8's "no synthesised sources" spirit applied to xrefs).

Emits a NEW kind="s" row set, appended to csl-atlas's xref_edges.csv (extend,
not rebuild -- the existing "vgl"/"cf" rows for pwg and every other dict are
untouched).

    python resolve_xrefs.py --report
    python resolve_xrefs.py --write <path-to-csl-atlas-worktree>/data/lexico/xref_edges.csv
"""
import argparse
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))

HEADER_RE = re.compile(r'^<L>([\d.]+)<pc>(.*?)<k1>(.*?)<k2>(.*?)(?:<h>(\d+))?\s*$')
S_TARGET_RE = re.compile(r'<ab>s\.</ab>\s*(?:also\s+|and\s+|or\s+)?(?:√\s*)?\{#([^#}]*)#\}')
_BRACE_SPLIT = re.compile(r'/|,')
_LEMMA_TOK = re.compile(r"^[A-Za-z][A-Za-z'~]*$")
_LEMMA_MAX = 24


def is_lemma_like(target):
    parts = _BRACE_SPLIT.split(target.strip())
    return bool(parts) and all(_LEMMA_TOK.match(p) and len(p) <= _LEMMA_MAX for p in parts if p)


def extract():
    edges = []
    unresolved = 0
    buf = []
    key1 = None
    with open(PWG, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                buf = [line]
                m = HEADER_RE.match(line)
                key1 = m.group(3) if m else None
            elif line.startswith('<LEND>'):
                buf = []
                key1 = None
            elif buf:
                buf.append(line)
                for tm in S_TARGET_RE.finditer(line):
                    target = tm.group(1)
                    if key1 and is_lemma_like(target):
                        for t in _BRACE_SPLIT.split(target.strip()):
                            if t:
                                edges.append({'dict': 'pwg', 'L': (HEADER_RE.match(buf[0]).group(1) if buf else ''),
                                              'k1': key1, 'kind': 's', 'target': t})
                    else:
                        unresolved += 1
    return edges, unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--write', help='path to an xref_edges.csv to APPEND the new kind="s" rows to')
    args = ap.parse_args()

    edges, unresolved = extract()
    print(f'<ab>s.</ab> lemma-like edges resolved: {len(edges)}')
    print(f'<ab>s.</ab> occurrences NOT lemma-like (citation/rule pointers, left unresolved): {unresolved}')
    print(f'resolved fraction: {len(edges)/(len(edges)+unresolved)*100:.1f}%' if (edges or unresolved) else 'n/a')

    if args.write:
        exists = os.path.exists(args.write)
        with open(args.write, 'a', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['dict', 'L', 'k1', 'kind', 'target'])
            if not exists:
                w.writeheader()
            for e in edges:
                w.writerow(e)
        print(f'appended {len(edges)} rows to {args.write}')


if __name__ == '__main__':
    main()
