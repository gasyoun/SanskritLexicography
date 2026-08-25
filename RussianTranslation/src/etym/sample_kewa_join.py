"""Draw the class-weighted adjudication sample from the KEWA-PWG crosswalk.

The acceptance bar for H3169 is at least 50 hand-adjudicated rows, weighted
toward `finite-form->root` and `ambiguous-multi` - the two classes where a
wrong join fabricates an etymology.  Seeded, so the sample is reproducible.

Usage:
    python sample_kewa_join.py [--n-per-class ...] [--seed 3169]
"""
from __future__ import annotations

import argparse
import collections
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
QUOTA = {
    "finite-form->root": 20,
    "ambiguous-multi": 20,
    "routes-disagree": 12,
    "inflected-form->stem": 6,
    "sandhi/diacritic-normalized": 6,
    "unmatched": 6,
    "exact": 2,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default=os.path.join(HERE, "..", "..", "data", "etym"))
    ap.add_argument("--seed", type=int, default=3169)
    args = ap.parse_args()

    indir = os.path.abspath(args.indir)
    src = os.path.join(indir, "kewa_pwg_crosswalk.tsv")
    idx = os.path.join(indir, "kewa_index_normalized.tsv")

    with open(idx, encoding="utf-8") as fh:
        ih = fh.readline().rstrip("\n").split("\t")
        by_seq = {}
        for line in fh:
            row = dict(zip(ih, line.rstrip("\n").split("\t")))
            by_seq[(row["kewa_seq"], row["heading_idx"])] = row

    with open(src, encoding="utf-8") as fh:
        h = fh.readline().rstrip("\n").split("\t")
        rows = [dict(zip(h, line.rstrip("\n").split("\t"))) for line in fh]

    # `routes-disagree` is a stratum in its own right: those are the rows where
    # the rule rung and the witness rung point at different PWG headwords, i.e.
    # exactly where a wrong join would invent an etymology.
    buckets = collections.defaultdict(list)
    for r in rows:
        if "routes-disagree" in r["flags"]:
            buckets["routes-disagree"].append(r)
        else:
            buckets[r["match_basis"]].append(r)

    rng = random.Random(args.seed)
    out = []
    for basis, n in QUOTA.items():
        pool = buckets.get(basis, [])
        take = pool if len(pool) <= n else rng.sample(pool, n)
        out.extend(sorted(take, key=lambda r: int(r["kewa_seq"])))

    cols = ["match_basis", "kewa_seq", "vol", "page", "deva", "iast_printed",
            "kewa_slp1", "pwg_key1", "witness", "lemma_route", "flags"]
    dst = os.path.join(indir, "kewa_join_adjudication_sample.tsv")
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in out:
            src_row = by_seq.get((r["kewa_seq"], r["heading_idx"]), {})
            merged = {**r, "deva": src_row.get("deva", ""),
                      "iast_printed": src_row.get("iast_printed", "")}
            fh.write("\t".join(str(merged.get(c, "")) for c in cols) + "\n")

    print(f"sampled {len(out)} rows (seed {args.seed}) -> {dst}")
    for basis, n in QUOTA.items():
        print(f"  {basis}: requested {n}, pool {len(buckets.get(basis, []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
