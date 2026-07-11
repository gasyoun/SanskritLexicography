#!/usr/bin/env python3
"""Pairwise headword-overlap matrix over the cross-dict UNION index.

Consumes ``HeadwordLists/union/union_headwords.tsv`` (15 dictionaries,
323,425 rows — never rebuilt here, per the reuse rule). The union key is the
bare SLP1 lemma from each dict's csl-orig ``<k1>`` with homograph numbering
collapsed and 237 gender-confirmed ``-inI`` feminines folded (see
``HeadwordLists/union/UNION.md``) — so overlap below is exact SLP1 string
equality on that key; no additional normalization is applied or needed.

Outputs (beside this script):
  * ``headword_overlap_matrix.tsv`` — long format, one row per unordered dict
    pair: ``dict_a  dict_b  shared  union  jaccard`` (a < b alphabetically).
  * ``headword_unique_counts.tsv`` — per dict: ``dict  headwords
    unique_to_dict  unique_share``.

Also prints a square shared-count matrix and top/bottom pairs for the report.

Usage:
    python headword_overlap_matrix.py [--union PATH]

H684 (Lane B, Fable sprint). Run 11-07-2026 by Fable 5 (claude-fable-5).
"""

import argparse
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--union",
        default=str(
            Path(__file__).resolve().parents[1]
            / "HeadwordLists"
            / "union"
            / "union_headwords.tsv"
        ),
    )
    args = ap.parse_args()

    totals = Counter()  # dict -> headwords containing it
    uniques = Counter()  # dict -> headwords only it attests
    pair_shared = Counter()  # (a, b) sorted -> shared headwords
    rows = 0
    with open(args.union, encoding="utf-8-sig") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        i_dicts = header.index("dicts")
        for line in fh:
            rows += 1
            dicts = line.rstrip("\n").split("\t")[i_dicts].split()
            for d in dicts:
                totals[d] += 1
            if len(dicts) == 1:
                uniques[dicts[0]] += 1
            else:
                for a, b in combinations(sorted(dicts), 2):
                    pair_shared[(a, b)] += 1

    codes = sorted(totals)
    here = Path(__file__).resolve().parent

    with open(here / "headword_overlap_matrix.tsv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dict_a\tdict_b\tshared\tunion\tjaccard\n")
        for a, b in combinations(codes, 2):
            shared = pair_shared[(a, b)]
            uni = totals[a] + totals[b] - shared
            fh.write(f"{a}\t{b}\t{shared}\t{uni}\t{shared / uni:.4f}\n")

    with open(here / "headword_unique_counts.tsv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dict\theadwords\tunique_to_dict\tunique_share\n")
        for d in codes:
            fh.write(f"{d}\t{totals[d]}\t{uniques[d]}\t{uniques[d] / totals[d]:.4f}\n")

    print(f"union rows: {rows}; dicts: {len(codes)}; pairs: {len(list(combinations(codes, 2)))}")
    print("\nPer-dict totals / uniques:")
    for d in codes:
        print(f"  {d}: {totals[d]} headwords, {uniques[d]} unique ({uniques[d]/totals[d]:.1%})")

    print("\nSquare shared-count matrix:")
    print("\t" + "\t".join(codes))
    for a in codes:
        cells = []
        for b in codes:
            if a == b:
                cells.append(str(totals[a]))
            else:
                cells.append(str(pair_shared[tuple(sorted((a, b)))]))
        print(a + "\t" + "\t".join(cells))

    ranked = sorted(
        ((pair_shared[p] / (totals[p[0]] + totals[p[1]] - pair_shared[p]), p) for p in pair_shared),
        reverse=True,
    )
    print("\nTop-10 pairs by Jaccard:")
    for j, (a, b) in ranked[:10]:
        print(f"  {a}-{b}: J={j:.3f}, shared={pair_shared[(a,b)]}")
    print("\nBottom-5 pairs by Jaccard:")
    for j, (a, b) in ranked[-5:]:
        print(f"  {a}-{b}: J={j:.3f}, shared={pair_shared[(a,b)]}")


if __name__ == "__main__":
    main()
