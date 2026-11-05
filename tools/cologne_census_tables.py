#!/usr/bin/env python3
"""Derive every report table from the census gz (H7228 report re-quote helper).

Reads reports/cologne_entry_census.tsv.gz and prints, as TSV blocks ready for
markdown: per-year, core-dict matrix, dictionary breadth (top 10), issue
attribution (top 8), record churn, and dataset fingerprints. Pure read; no
clone needed.

    python tools/cologne_census_tables.py [--in reports/cologne_entry_census.tsv.gz]
"""
import argparse
import collections
import gzip
import hashlib
from pathlib import Path

CORE_DICTS = ("mw", "mw72", "ap90", "pw", "pwg", "bhs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=Path,
                    default=Path(__file__).resolve().parents[1] / "reports" / "cologne_entry_census.tsv.gz")
    args = ap.parse_args()
    raw = args.inp.read_bytes()
    text = gzip.decompress(raw).decode("utf-8")

    per_year = collections.defaultdict(lambda: collections.Counter())
    yc = collections.defaultdict(set)
    yd = collections.defaultdict(set)
    breadth = collections.defaultdict(lambda: collections.Counter())
    issue = collections.Counter()
    churn = collections.Counter()
    per_dict_distinct = collections.defaultdict(set)
    core = collections.defaultdict(int)
    n = 0
    distinct = 0
    seen = set()
    for i, line in enumerate(text.splitlines()):
        if i == 0:
            continue
        y, d, l, hw, kind, iss, sha, date = line.split("\t")
        n += 1
        per_year[y]["e"] += 1
        per_year[y][kind] += 1
        yc[y].add(sha)
        yd[y].add(d)
        breadth[d]["e"] += 1
        breadth[d][kind] += 1
        issue[iss or "(none)"] += 1
        key = (d, l)
        churn[key] += 1
        if key not in seen:
            seen.add(key)
            distinct += 1
            per_dict_distinct[d].add(l)
        if d in CORE_DICTS:
            core[(y, d)] += 1

    print("== per-year: year commits dicts entries add mod add_share ==")
    for y in sorted(per_year):
        c = per_year[y]
        tot = c["e"]
        print(f"{y}\t{len(yc[y])}\t{len(yd[y])}\t{tot}\t{c['add']}\t{c['mod']}\t{100.0*c['add']/max(tot,1):.1f}%")

    print("== core matrix: year mw mw72 ap90 pw pwg bhs ==")
    print("year\t" + "\t".join(CORE_DICTS))
    for y in sorted(per_year):
        print(y + "\t" + "\t".join(str(core[(y, d)]) for d in CORE_DICTS))

    print("== breadth top10: dict entries add mod distinct_L ==")
    for d, c in sorted(breadth.items(), key=lambda kv: -kv[1]["e"])[:10]:
        print(f"{d}\t{c['e']}\t{c['add']}\t{c['mod']}\t{len(per_dict_distinct[d])}")

    print("== issue top8: issue entries ==")
    for iss, cnt in issue.most_common(8):
        print(f"{iss}\t{cnt}")

    print("== churn ==")
    once = sum(1 for v in churn.values() if v == 1)
    five = sum(1 for v in churn.values() if v == 5)
    tenp = sum(1 for v in churn.values() if v >= 10)
    top = sorted(churn.items(), key=lambda kv: -kv[1])[:3]
    print(f"rows={n} distinct={distinct} events_per_record={n/max(distinct,1):.2f} "
          f"once={once} five={five} ten_plus={tenp}")
    for (d, l), v in top:
        print(f"top\t{d}\t{l}\t{v}")

    print("== fingerprints ==")
    print(f"plain_sha256\t{hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    print(f"gz_sha256\t{hashlib.sha256(raw).hexdigest()}")
    print(f"plain_bytes\t{len(text.encode('utf-8'))}")
    print(f"gz_bytes\t{len(raw)}")


if __name__ == "__main__":
    main()