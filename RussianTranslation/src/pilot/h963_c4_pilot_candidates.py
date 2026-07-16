#!/usr/bin/env python3
"""H963 c4 owner-override pilot — READ-ONLY candidate scan over the nominal-core worklist.

Makes NO model calls and writes nothing outside this worktree's attempt dir. Scans the
282 runnable nominal-core lemmas (already store-deduped by nominals_worklist.py against
the SNAPSHOTTED store) and reports, in priority order, which have prebuilt runtime inputs
available to copy, with their sizes -- the input to the per-key preflight gate.

no_pwg / H255 is frozen per the owner-override brief: this scans the NOMINAL-CORE
worklist only, never the no_pwg window queue.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

WT = r"C:\Users\user\Documents\GitHub\SanskritLexicography-h963-c4-live\RussianTranslation"
SHARED_INP = r"C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot\input"

sys.path.insert(0, os.path.join(WT, "src"))
from safe_filename import safe_name  # noqa: E402

worklist = json.load(open(os.path.join(WT, "src", "pilot", "output",
                                       "nominal_batch_worklist.json"), encoding="utf-8"))
detail = worklist["runnable_detail"]

# blocked residuals (registry) — nominal-core keys are flat, but check anyway
blocked = set()
rp = os.path.join(WT, "src", "pilot", "no_pwg_residuals.jsonl")
if os.path.exists(rp):
    for line in open(rp, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r.get("status") == "blocked":
                blocked.add(r["key"])
                blocked.add(r["key"].split("~~")[0])

print("runnable nominal-core lemmas: %d (priority order)" % len(detail))
print("blocked residual stems: %d" % len(blocked))
print()

rows = []
for d in detail:
    fk = d["form_key"]
    stem = safe_name(fk)
    raw = os.path.join(SHARED_INP, stem + ".raw.txt")
    por = os.path.join(SHARED_INP, stem + ".portrait.json")
    if not (os.path.exists(raw) and os.path.exists(por)):
        continue
    size = os.path.getsize(raw)
    text = open(raw, encoding="utf-8", errors="replace").read()
    # senses: top-level numbered senses in the PWG raw
    senses = len(re.findall(r"—\s*\d+〉", text)) or len(re.findall(r"^\s*\d+\)", text, re.M))
    cites = text.count("<ls")
    curly = len(re.findall(r"\{#[^}]*#\}", text))
    rows.append({
        "form_key": fk, "stem": stem, "score": d["score"], "band": d["band"],
        "raw_bytes": size, "senses": senses, "cites": cites, "sanskrit_spans": curly,
        "blocked": fk in blocked or stem in blocked,
    })

print("candidates WITH prebuilt inputs: %d / %d" % (len(rows), len(detail)))
print()
print("%-14s %-6s %5s %9s %7s %7s %7s" % ("form_key", "score", "band", "raw_B", "senses", "<ls>", "{#..#}"))
print("-" * 66)
for r in rows[:40]:
    flag = "  BLOCKED" if r["blocked"] else ""
    print("%-14s %-6.1f %5d %9d %7d %7d %7d%s"
          % (r["form_key"], r["score"], r["band"], r["raw_bytes"], r["senses"],
             r["cites"], r["sanskrit_spans"], flag))

print()
print("=== size distribution of candidates with inputs ===")
sizes = sorted(r["raw_bytes"] for r in rows)
if sizes:
    import statistics
    print("n=%d  min=%d  p25=%d  median=%d  p75=%d  max=%d"
          % (len(sizes), sizes[0], sizes[len(sizes) // 4], statistics.median(sizes),
             sizes[3 * len(sizes) // 4], sizes[-1]))

# smallest, still-priority-ordered view: the one-batch / 2-agent ceiling favours small cards
small = [r for r in rows if not r["blocked"] and r["raw_bytes"] <= 6000]
print()
print("=== SMALL candidates (raw <= 6000 B), priority order — the one-batch lane ===")
for r in small[:20]:
    print("%-14s score=%-6.1f band=%d raw=%6d B senses=%2d <ls>=%3d {#..#}=%2d"
          % (r["form_key"], r["score"], r["band"], r["raw_bytes"], r["senses"],
             r["cites"], r["sanskrit_spans"]))
print("\nsmall candidate count: %d" % len(small))

out = os.path.join(WT, "src", "pilot", "output", "h963_c4_pilot", "candidate_scan.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump({"schema": "pwg.h963_c4_pilot_candidates.v1",
               "source_worklist": "nominal_batch_worklist.json (pril10 Tier-2 LEADS)",
               "runnable_total": len(detail), "with_inputs": len(rows),
               "candidates": rows}, f, ensure_ascii=False, indent=1)
print("\nwrote %s" % out)
