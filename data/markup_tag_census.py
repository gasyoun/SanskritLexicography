#!/usr/bin/env python3
"""Markup-tag frequency census across the local csl-orig/v02 dictionaries.

For every dictionary directory ``<code>/`` under csl-orig/v02 that carries a
main text file ``<code>.txt``, counts:

  * every opening angle-bracket tag ``<tag ...>`` (closing ``</tag>`` forms are
    deliberately not counted — one logical use of a tag counts once);
  * the Cologne brace markers ``{#...#}`` (SLP1 Sanskrit), ``{%...%}``
    (italics), ``{@...@}`` (bold), ``{~...~}``, ``{!...!}``, ``{|...|}``
    as pseudo-tags.

Entry counts come from the ``<L>`` record markers (one per entry in the v02
format). Rates are normalized per 1,000 entries.

Output: ``markup_tag_census.tsv`` (long format:
``dict  entries  tag  count  per_1000_entries``), sorted by dict then count
descending.

Usage:
    python markup_tag_census.py [--csl-orig PATH] [--out PATH]

H683 (Lane B, Fable sprint). Run 11-07-2026 by Fable 5 (claude-fable-5).
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ANGLE_TAG = re.compile(r"<([A-Za-z][A-Za-z0-9_.]*)")
BRACE_MARK = re.compile(r"\{([#%@~!|])")
BRACE_LABEL = {
    "#": "{#...#}",
    "%": "{%...%}",
    "@": "{@...@}",
    "~": "{~...~}",
    "!": "{!...!}",
    "|": "{|...|}",
}


def census_file(path: Path):
    """Return (entry_count, Counter of tag -> occurrences) for one dict file."""
    tags = Counter()
    entries = 0
    # utf-8-sig transparently strips a BOM if present, and is a no-op if not.
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            if line.startswith("<L>"):
                entries += 1
            for m in ANGLE_TAG.finditer(line):
                tags[f"<{m.group(1)}>"] += 1
            for m in BRACE_MARK.finditer(line):
                tags[BRACE_LABEL[m.group(1)]] += 1
    return entries, tags


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--csl-orig",
        default=str(Path(__file__).resolve().parents[2] / "csl-orig" / "v02"),
        help="path to the local csl-orig/v02 directory",
    )
    ap.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent / "markup_tag_census.tsv"),
        help="output TSV path",
    )
    args = ap.parse_args()

    root = Path(args.csl_orig)
    if not root.is_dir():
        sys.exit(f"csl-orig/v02 not found at {root}")

    rows = []
    skipped = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        main_txt = d / f"{d.name}.txt"
        if not main_txt.is_file():
            skipped.append(d.name)
            continue
        entries, tags = census_file(main_txt)
        for tag, count in tags.most_common():
            rate = round(count * 1000.0 / entries, 2) if entries else ""
            rows.append((d.name, entries, tag, count, rate))
        print(
            f"{d.name}: {entries} entries, {sum(tags.values())} tag hits, "
            f"{len(tags)} distinct tags"
        )

    out = Path(args.out)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("dict\tentries\ttag\tcount\tper_1000_entries\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    dicts = sorted({r[0] for r in rows})
    print(f"\n{len(dicts)} dictionaries censused -> {out}")
    if skipped:
        print(f"skipped (no <code>.txt): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
