"""A43 — Russian Sanskrit dictionary family: union / overlap statistics.

Recomputes every numeric figure cited in papers/A43_ru_dict_family.md from the
five digitized dictionary JSONLs (koch, kow, kna, smirnov, fri), which live
locally in this directory (schema: {source, slp1, iast, gloss}, one entry per
line). The JSONLs are not committed (size + per-source rights); this script is
the committed, deterministic recompute path.

Usage:  python a43_family_stats.py
"""
import json
import sys
import itertools
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SRC = Path(__file__).resolve().parent
DICTS = ["koch", "kow", "kna", "smirnov", "fri"]
RU4 = ["koch", "kow", "kna", "smirnov"]  # the frame of the pre-existing "~41k / 222" claim


def norm(slp1: str) -> str:
    # Length-preserving headword key: strip whitespace and edge hyphens only
    # (compound-member and prefix entries like "-akza", "a-"); never touch
    # case or vowel length (SLP1 is case-significant — no NFD/strip tricks).
    return slp1.strip().strip("-").strip()


def has_cyrillic(s: str) -> bool:
    return any("Ѐ" <= c <= "ӿ" for c in s)


def load(name: str):
    keys, n, cyr = set(), 0, 0
    with open(SRC / f"{name}.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n += 1
            row = json.loads(line)
            if has_cyrillic(row["gloss"]):
                cyr += 1
            k = norm(row["slp1"])
            if k:
                keys.add(k)
    return keys, n, cyr


def report(sets, combo, label):
    union = set().union(*(sets[d] for d in combo))
    shared = set.intersection(*(sets[d] for d in combo))
    print(f"{label}: union={len(union):,} shared_by_all={len(shared):,}")
    return union, shared


def main():
    sets, rows = {}, {}
    for d in DICTS:
        sets[d], rows[d], cyr = load(d)
        print(
            f"{d}: rows={rows[d]:,} distinct_headword_keys={len(sets[d]):,} "
            f"cyrillic_glosses={cyr:,} ({100 * cyr / rows[d]:.1f}%)"
        )

    print()
    report(sets, DICTS, "5-dict family (koch/kow/kna/smirnov/fri)")
    report(sets, RU4, "4-dict frame (koch/kow/kna/smirnov)")

    print("\npairwise overlaps (distinct normalized keys):")
    for a, b in itertools.combinations(DICTS, 2):
        print(f"  {a} ∩ {b} = {len(sets[a] & sets[b]):,}")

    print("\nunique-to-one-dictionary (within the 5-dict family):")
    total_unique = 0
    for d in DICTS:
        others = set().union(*(sets[x] for x in DICTS if x != d))
        only = len(sets[d] - others)
        total_unique += only
        print(f"  {d} only: {only:,}")
    union5 = set().union(*(sets[d] for d in DICTS))
    print(
        f"  total in exactly one source: {total_unique:,} "
        f"({100 * total_unique / len(union5):.1f}% of the union)"
    )


if __name__ == "__main__":
    main()
