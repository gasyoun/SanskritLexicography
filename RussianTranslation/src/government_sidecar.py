#!/usr/bin/env python
r"""Case-government sidecar per sense row — roadmap card 23 (sense intelligence).

Card 23's claim: "Sanskrit case/government evidence can catch incompatible Russian
renderings or missing government notes." The deterministic, local-only foundation
of that claim is a per-sense government census extracted from the German source
text — exactly what ``government_census.extract_government`` already computes from
one sense's ``de`` field. This script applies that extractor across the whole
translated store and emits a collision-free SIDECAR keyed by ``subcard``.

WHY A SIDECAR, not an in-place store backfill: ``annotate_government.py`` writes
``r['government']`` in place over all ~11.5k rows. The store is under continuous
concurrent promotion (verb/no-PWG drains rewrite it repeatedly), so an in-place
full rewrite races those sessions. This sidecar reads the store read-only and
writes ``src/pwg_government.jsonl``; downstream cards 8/28 join it on ``subcard``.
When the drain lanes are quiet, ``annotate_government.py`` can fold the same data
into the store field — this sidecar is the safe artifact in the meantime.

WHAT IS AND IS NOT SHIPPED HERE: the deterministic government extraction + census
is complete and measurable. Card 23's full acceptance — ">= 85% of high-severity
RU-rendering mismatch flags are real" — needs a Russian-morphology check plus a
human review sample, and is GOLD-GATED (see GOLD_SLICE_NEEDS_CAPABILITY_ROADMAP.md).
This script deliberately does not emit mismatch flags; it emits the government
evidence those flags will be computed from.

Read-only over the store. Output ``src/pwg_government.jsonl`` is gitignored
(derived from the local-only store). No LLM, no network.

  python src/government_sidecar.py                  # emit sidecar + census
  python src/government_sidecar.py --dry-run         # census only, no write
  python src/government_sidecar.py --selftest
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Single source of truth for what counts as a government marker (H338): reuse the
# census extractor rather than re-defining the regexes here.
from government_census import extract_government, GOV_CASES

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
OUT = os.path.join(HERE, "pwg_government.jsonl")


def government_for_row(row):
    """Return the sidecar record for one store row, or None if it governs no case.

    ``cases_governed`` is the sorted set of core government cases across all hits
    (acc/loc/instr/gen/dat/abl); nom/voc are never government and are already
    excluded by ``extract_government``.
    """
    hits = extract_government(row.get("de"))
    if not hits:
        return None
    cases = sorted({c for h in hits for c in h["cases"] if c in GOV_CASES})
    return {
        "subcard": row.get("subcard"),
        "key1": row.get("key1"),
        "iast": row.get("iast"),
        "sense_tag": row.get("sense_tag"),
        "government": hits,
        "n_government": len(hits),
        "cases_governed": cases,
        "has_variation": any(h["variation"] for h in hits),
    }


def build(rows):
    return [rec for rec in (government_for_row(r) for r in rows) if rec is not None]


def census(rows, records):
    kinds = Counter()
    cases = Counter()
    for rec in records:
        for h in rec["government"]:
            kinds[h["kind"]] += 1
            cases["+".join(h["cases"])] += 1
    return {
        "rows_scanned": len(rows),
        "rows_with_government": len(records),
        "government_markers": sum(r["n_government"] for r in records),
        "entries(key1)_with_government": len({r["key1"] for r in records}),
        "rows_with_variation": sum(1 for r in records if r["has_variation"]),
        "by_kind": dict(kinds),
        "top_case_combos": cases.most_common(8),
    }


def print_report(rows, records):
    c = census(rows, records)
    print("=== GOVERNMENT SIDECAR (card 23) ===")
    print("store rows scanned        : %d" % c["rows_scanned"])
    print("rows with >=1 government  : %d" % c["rows_with_government"])
    print("government markers (total): %d" % c["government_markers"])
    print("distinct key1 with gov    : %d" % c["entries(key1)_with_government"])
    print("rows with case variation  : %d" % c["rows_with_variation"])
    print("by kind                   : " + ", ".join(
        "%s:%d" % (k, v) for k, v in sorted(c["by_kind"].items())))
    print("top case combos           : " + ", ".join(
        "%s(%d)" % (combo, n) for combo, n in c["top_case_combos"]))


def selftest():
    rows = [
        # two government markers on one sense: a paren-single (loc.) + a variation (loc. und gen.)
        {"subcard": "_snih~~h0_02", "key1": "snih", "iast": "snih", "sense_tag": "2",
         "de": "2〉 {%sich heften auf%} (<ab>loc.</ab>): {#y#} <ls>KATHĀS. 11,11</ls>. "
               "{%Zuneigung%} (<ab>loc.</ab> und <ab>gen.</ab>): {#z#} <ls>ŚĀK. 102,6</ls>."},
        # a mit-phrase (instr.)
        {"subcard": "_snih~~h0_p", "key1": "snih", "iast": "snih", "sense_tag": "Praep.",
         "de": "— {#sam#} {%zusammen kommen%} mit dem <ab>instr.</ab>: {#w#} <ls>MBH. 1,1</ls>."},
        # only a non-government (voc.) note -> no record
        {"subcard": "_deva~~h0_01", "key1": "deva", "iast": "deva", "sense_tag": "1",
         "de": "{%Gott%} (<ab>voc.</ab>) auch so. <ls>ṚV. 1,1,1</ls>."},
        # no markers at all -> no record
        {"subcard": "_x~~h0_01", "key1": "x", "iast": "x", "sense_tag": "1",
         "de": "{%plain gloss%} <ls>MBH. 2,2</ls>."},
    ]
    recs = build(rows)
    assert len(recs) == 2, recs                      # snih sense 2 + snih praep; deva/x excluded
    by_sub = {r["subcard"]: r for r in recs}
    s2 = by_sub["_snih~~h0_02"]
    assert s2["n_government"] == 2, s2               # (loc.) + (loc. und gen.)
    assert s2["cases_governed"] == ["gen", "loc"], s2
    assert s2["has_variation"] is True, s2
    praep = by_sub["_snih~~h0_p"]
    assert praep["cases_governed"] == ["instr"], praep
    assert praep["government"][0]["kind"] == "mit-phrase", praep
    c = census(rows, recs)
    assert c["rows_scanned"] == 4 and c["rows_with_government"] == 2, c
    assert c["government_markers"] == 3, c
    assert c["entries(key1)_with_government"] == 1, c   # both records are key1 "snih"
    print("government_sidecar selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    rows = [json.loads(l) for l in open(args.store, encoding="utf-8") if l.strip()]
    records = build(rows)
    print_report(rows, records)
    if args.dry_run:
        print("\n(dry run — sidecar not written)")
        return
    with open(args.out + ".tmp", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(args.out + ".tmp", args.out)
    print("\nwrote government sidecar -> %s (%d rows)" % (args.out, len(records)))


if __name__ == "__main__":
    main()
