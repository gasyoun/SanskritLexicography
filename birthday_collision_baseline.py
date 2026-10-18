#!/usr/bin/env python3
"""Birthday-paradox collision baseline for Cologne batches (MW Herfindahl).

Answers: when a correction batch of k headwords shows N "collisions" on a
phonetic field (same first letter, same final, ...), is that a signal or the
background noise the birthday paradox predicts?

Method (memory note 2026-09-26, MG rulings 26-09-2026):
  1. Herfindahl index H = sum p_i^2 of the ACTUAL MW headword distribution per
     field (Sanskrit is heavily skewed — uniform 1/n would lie).
  2. Expected colliding pairs among k cases: lambda = C(k,2) * H.
  3. Observed-vs-expected with a Poisson p-value P(X >= observed).
  4. Ruling P < 5% = signal, otherwise noise. For k=10 that means a field needs
     m_eff = 1/H >~ 900 to ever reach signal (first-3-letters-or-longer in MW).

Usage:
  python birthday_collision_baseline.py --mw <path/to/mw.txt> --batch <batch_dir>
  python birthday_collision_baseline.py --mw mw.txt --k1-file cases.txt

_created: 26-09-2026 · oxalpha (GLM) per MG grill rulings · Гасунс_
"""
import argparse
import collections
import glob
import math
import os
import re
import sys

VOWELS = set("aAiIuUfFxXeEoO")  # SLP1


def onset_cluster(k):
    """Initial run: leading vowels + first consonant cluster (up to next vowel)."""
    i = 0
    while i < len(k) and k[i] in VOWELS:
        i += 1
    j = i
    while j < len(k) and k[j] not in VOWELS:
        j += 1
    return k[:j + 1] if j < len(k) else k[i:]


FIELDS = [
    ("first letter", lambda k: k[0]),
    ("first 2 letters", lambda k: k[:2]),
    ("first 3 letters", lambda k: k[:3]),
    ("final letter", lambda k: k[-1]),
    ("final 2 letters", lambda k: k[-2:]),
    ("onset cluster", onset_cluster),
]

K1_RE = re.compile(r"<k1>([^<]+)")


def mw_herfindahl(mw_path):
    keys = set()
    with open(mw_path, encoding="utf-8") as f:
        for line in f:
            m = K1_RE.search(line)
            if m:
                keys.add(m.group(1))
    keys = sorted(keys)
    out = {}
    for name, fn in FIELDS:
        c = collections.Counter(fn(k) for k in keys)
        n = len(keys)
        h = sum((v / n) ** 2 for v in c.values())
        out[name] = (h, len(c))
    return len(keys), out


def load_batch_cases(path):
    cases = []
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, "**", "change_*.txt"), recursive=True))
    else:
        files = [path]
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            for line in f:
                if " ins " not in line:
                    continue
                m = K1_RE.search(line)
                if m and m.group(1) not in cases:
                    cases.append(m.group(1))
    return cases, files


def poisson_sf(obs, lam):
    """P(X >= obs) for X ~ Poisson(lam)."""
    cdf = 0.0
    for i in range(obs):
        cdf += math.exp(-lam) * lam ** i / math.factorial(i)
    return max(0.0, 1.0 - min(1.0, cdf))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mw", required=True, help="path to csl-orig v02/mw/mw.txt")
    ap.add_argument("--batch", help="batch dir (recursive change_*.txt) or single change file")
    ap.add_argument("--k1-file", help="plain file, one k1 headword per line (overrides --batch)")
    args = ap.parse_args()

    n_mw, her = mw_herfindahl(args.mw)
    print(f"MW unique headwords: {n_mw}")
    if args.k1_file:
        cases = [ln.strip() for ln in open(args.k1_file, encoding="utf-8") if ln.strip()]
        files = [args.k1_file]
    else:
        cases, files = load_batch_cases(args.batch)
    k = len(cases)
    pairs = k * (k - 1) // 2
    print(f"Batch cases: {k} ({pairs} pairs) from {len(files)} change file(s)")
    print()

    header = f"{'field':<18}{'cats':>7}{'m_eff':>9}{'lambda':>9}{'observed':>10}{'p-value':>10}  verdict"
    print(header)
    print("-" * len(header))
    signal_found = False
    for name, fn in FIELDS:
        h, cats = her[name]
        lam = pairs * h
        groups = collections.defaultdict(list)
        for c in cases:
            groups[fn(c)].append(c)
        obs = sum(len(g) * (len(g) - 1) // 2 for g in groups.values())
        p = poisson_sf(obs, lam) if obs else 1.0
        verdict = "SIGNAL" if p < 0.05 else "noise"
        if p < 0.05:
            signal_found = True
        print(f"{name:<18}{cats:>7}{1 / h:>9.1f}{lam:>9.1f}{obs:>10}{p:>10.3f}  {verdict}")
        if obs and verdict == "noise" and name in ("onset cluster", "first 2 letters", "final 2 letters"):
            detail = "; ".join(f"{v!r}: {','.join(g)}" for v, g in sorted(groups.items()) if len(g) > 1)
            if detail:
                print(f"    colliders: {detail}")
    print()
    print("Ruling MG 26-09-2026: P < 5% = signal, otherwise birthday-paradox noise.")
    if not signal_found:
        print("Result: every observed collision is background noise — no systematic defect implied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
