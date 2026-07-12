#!/usr/bin/env python3
"""renou_stage_redundancy_check.py — H692: are the pipeline-stage files redundant?

Two series of large local-only, gitignored, single-copy JSONL artifacts in
``RussianTranslation/src/`` repeat a progressive-enrichment pattern, and the
data-layer census flagged ~1.4 GB as possibly dead. This tool PROVES or REFUTES
content-level redundancy — it never deletes, moves or rewrites anything.

Series A — ``assembled_cards`` chain (full streaming verification, every row):
    assembled_cards.jsonl -> .renou -> .renou.bhs -> .renou.bhs.wl
  For each adjacent pair, every record is checked: same ``key1`` sequence, and
  every field of the earlier stage must be present with a deeply-equal value in
  the later stage (containment). Any modification, not just addition, is
  counted and exemplified (keys only — no data rows are emitted).

Series B — per-dict old stepwise chain vs the canonical pipeline artifact:
    {code}_renou.jsonl [-> {code}_renou.bhs.jsonl -> {code}_renou.bhs.wl.jsonl]
    vs {code}.renou.jsonl        (built by renou_pipeline.py, all four signals)
  Checks: row counts, adjacent containment inside the old chain (full check),
  then old-final vs canonical: key1 coverage both ways plus agreement of the
  shared Renou signal fields on a deterministic 1-in-25 sample of common keys.

Output: aggregates-only Markdown report (--out). Exit code 0 always (report
tool, not a gate).

Usage:
    python renou_stage_redundancy_check.py [--src DIR] [--out REPORT.md]

H692 (Lane B, Fable sprint). Run 11/12-07-2026 by Fable 5 (claude-fable-5).
"""

import argparse
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ASSEMBLED = [
    "assembled_cards.jsonl",
    "assembled_cards.renou.jsonl",
    "assembled_cards.renou.bhs.jsonl",
    "assembled_cards.renou.bhs.wl.jsonl",
]
DICTS = ["ap", "ap90", "ben", "bhs", "mw", "pw", "sch", "pwg"]


def jl(path):
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def check_chain(paths):
    """Full containment check along a chain of JSONL files (same row order).

    Returns dict with rows per file, added-fields per step, and per-step
    violation stats: {step: {"key_mismatch": n, "modified": Counter(field),
    "examples": [(key, field)]}}.
    """
    gens = [jl(p) for p in paths]
    rows = 0
    added = [None] * (len(paths) - 1)
    viol = [
        {"key_mismatch": 0, "modified": Counter(), "examples": []}
        for _ in range(len(paths) - 1)
    ]
    short = None
    while True:
        recs = []
        for g in gens:
            recs.append(next(g, None))
        if all(r is None for r in recs):
            break
        if any(r is None for r in recs):
            short = rows  # length mismatch — record and stop the zip
            break
        rows += 1
        for i in range(len(recs) - 1):
            a, b = recs[i], recs[i + 1]
            if a.get("key1") != b.get("key1"):
                viol[i]["key_mismatch"] += 1
                continue
            if added[i] is None:
                added[i] = sorted(set(b) - set(a))
            for f, v in a.items():
                if f not in b or b[f] != v:
                    viol[i]["modified"][f] += 1
                    if len(viol[i]["examples"]) < 3:
                        viol[i]["examples"].append((a.get("key1"), f))
        if rows % 20000 == 0:
            print(f"  …{rows} rows", file=sys.stderr)
    return {"rows": rows, "added": added, "viol": viol, "short": short}


def count_rows(path):
    n = 0
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def series_b(src, code, out):
    old = [f"{code}_renou.jsonl", f"{code}_renou.bhs.jsonl", f"{code}_renou.bhs.wl.jsonl"]
    old = [f for f in old if os.path.exists(os.path.join(src, f))]
    canon = f"{code}.renou.jsonl"
    has_canon = os.path.exists(os.path.join(src, canon))
    out.append(f"### {code.upper()}")
    if not old:
        out.append(f"- old underscore chain: **absent** (canonical `{canon}` only — already clean)\n")
        return
    paths = [os.path.join(src, f) for f in old]
    if len(old) > 1:
        r = check_chain(paths)
        out.append(f"- old chain `{' -> '.join(old)}`: {r['rows']} rows zipped"
                   + (f", LENGTH MISMATCH at {r['short']}" if r["short"] is not None else ""))
        for i, v in enumerate(r["viol"]):
            mods = sum(v["modified"].values())
            out.append(
                f"  - step {old[i]} ⊂ {old[i+1]}: adds {r['added'][i]}; key mismatches {v['key_mismatch']}; "
                f"modified-field violations {mods}"
                + (f" (fields: {dict(v['modified'])}; e.g. {v['examples']})" if mods else "")
            )
    else:
        out.append(f"- old chain: only `{old[0]}` ({count_rows(paths[0])} rows)")
    if not has_canon:
        out.append(f"- canonical `{canon}`: **ABSENT** — old chain is the only artifact, keep\n")
        return
    # old-final vs canonical: key coverage + sampled signal agreement
    old_final = paths[-1]
    keys_old = Counter()
    sample_old = {}
    for i, rec in enumerate(jl(old_final)):
        k = rec.get("key1")
        keys_old[k] += 1
        if i % 25 == 0:
            sample_old[k] = rec
    keys_can = Counter()
    agree = disagree = 0
    dis_fields = Counter()
    sig_fields = ["renou_enriched", "renou_ls", "renou_dcs", "renou_bhs", "renou_wl"]
    for rec in jl(os.path.join(src, canon)):
        k = rec.get("key1")
        keys_can[k] += 1
        s = sample_old.get(k)
        if s is not None:
            if all(s.get(f) == rec.get(f) for f in sig_fields if f in s):
                agree += 1
            else:
                disagree += 1
                for f in sig_fields:
                    if f in s and s.get(f) != rec.get(f):
                        dis_fields[f] += 1
            sample_old.pop(k, None)  # count each sampled key once
    only_old = sum(c for k, c in keys_old.items() if k not in keys_can)
    only_can = sum(c for k, c in keys_can.items() if k not in keys_old)
    out.append(
        f"- old-final `{old[-1]}` ({sum(keys_old.values())} rows, {len(keys_old)} distinct key1) vs canonical "
        f"`{canon}` ({sum(keys_can.values())} rows, {len(keys_can)} distinct key1): "
        f"key1 only-in-old {only_old} rows / only-in-canonical {only_can} rows"
    )
    tot = agree + disagree
    out.append(
        f"- sampled signal agreement on common key1 (1-in-25, n={tot}): "
        f"{agree} agree / {disagree} disagree"
        + (f" (fields: {dict(dis_fields)})" if disagree else "")
        + "\n"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    src = args.src

    out = []
    out.append("## Series A — assembled_cards chain (full check, every row)\n")
    paths = [os.path.join(src, f) for f in ASSEMBLED]
    print("Series A: zipping 4 assembled_cards stages …", file=sys.stderr)
    r = check_chain(paths)
    out.append(f"- rows (all four stages zipped in lockstep): **{r['rows']}**"
               + (f" — LENGTH MISMATCH at row {r['short']}" if r["short"] is not None else " — equal lengths"))
    for i, v in enumerate(r["viol"]):
        mods = sum(v["modified"].values())
        out.append(
            f"- {ASSEMBLED[i]} ⊂ {ASSEMBLED[i+1]}: adds {r['added'][i]}; "
            f"key1 sequence mismatches **{v['key_mismatch']}**; modified-field violations **{mods}**"
            + (f" (fields: {dict(v['modified'])}; examples {v['examples']})" if mods else "")
        )
    out.append("")

    out.append("## Series B — per-dict old underscore chain vs canonical `{code}.renou.jsonl`\n")
    for code in DICTS:
        print(f"Series B: {code} …", file=sys.stderr)
        series_b(src, code, out)

    text = "\n".join(out) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"written -> {args.out}", file=sys.stderr)
    print(text)


if __name__ == "__main__":
    main()
