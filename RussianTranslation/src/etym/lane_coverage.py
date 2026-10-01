"""How the two C4 etymology lanes overlap on PWG headwords (H3169).

The ceiling C4 ruling requires the *traditional* lane (Cologne 19th-c.
extractors) and the *modern IE* lane (KEWA, later EWA) to stay separately
labelled and never merge into one undifferentiated `etymology` field.  This
script does not merge them - it reports, per PWG headword, which lanes reach
it, so a reader can see how much of PWG each tradition actually covers and
where they are each other's only witness.

Inputs (read-only):
  * modern IE  - `kewa_pwg_crosswalk.tsv` from [`join_kewa_pwg.py`](join_kewa_pwg.py)
  * traditional - `csl-orig/v02/pwg/pwg_etymology.tsv` (`headword_slp1`)

Usage:
    python lane_coverage.py [--github-root DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = "C:/Users/user/Documents/GitHub"
PWG_ETYM = "csl-orig/v02/pwg/pwg_etymology.tsv"
PWG_KEY1 = "SanskritLexicography/HeadwordLists/now-2026/PWG-unique-key1-106082.txt"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github-root", default=DEFAULT_ROOT)
    ap.add_argument("--indir", default=os.path.join(HERE, "..", "..", "data", "etym"))
    args = ap.parse_args()

    indir = os.path.abspath(args.indir)
    root = args.github_root

    with open(os.path.join(root, PWG_KEY1), encoding="utf-8") as fh:
        pwg = {line.strip() for line in fh if line.strip()}

    traditional: set[str] = set()
    etym_path = os.path.join(root, PWG_ETYM)
    if os.path.exists(etym_path):
        with open(etym_path, encoding="utf-8") as fh:
            head = fh.readline().rstrip("\n").split("\t")
            col = head.index("headword_slp1")
            for line in fh:
                parts = line.rstrip("\n").split("\t")
                if len(parts) > col and parts[col]:
                    traditional.add(parts[col])

    modern: set[str] = set()
    with open(os.path.join(indir, "kewa_pwg_crosswalk.tsv"), encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        ci = head.index("pwg_key1")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > ci and parts[ci]:
                modern.update(p for p in parts[ci].split("|") if p)

    both = modern & traditional
    report = {
        "pwg_key1_headwords": len(pwg),
        "lane_modern_ie_kewa": len(modern),
        "lane_traditional_cologne": len(traditional & pwg),
        "both_lanes": len(both),
        "modern_only": len(modern - traditional),
        "traditional_only": len((traditional & pwg) - modern),
        "pwg_with_no_lane": len(pwg - modern - traditional),
        "note": ("Lanes are reported, never merged - the C4 ruling keeps "
                 "*traditional* (Cologne) and *modern IE* (KEWA/EWA) as "
                 "separately labelled fields."),
        "sources": {"modern_ie": "kewa_pwg_crosswalk.tsv", "traditional": PWG_ETYM},
    }

    dst = os.path.join(indir, "etym_lane_coverage.json")
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
