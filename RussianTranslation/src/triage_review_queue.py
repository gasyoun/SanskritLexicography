#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-sort the pwg_ru legacy review queue for the HUMAN reviewer.

This does NOT re-judge. It reuses the existing QA-judge verdicts already in
``_review_queue.jsonl`` (severity + prose ``reason`` written by the Opus QA
judge, rubric in ``pwg_ru_prompts/2_qa_sudya_opus.txt``) and buckets each row by
the *kind* of defect the judge described, then orders by the judge's own
severity (= confidence). Final adjudication stays human; nothing is auto-edited.

Buckets (the three the handoff asked for, plus a FAST-PASS pre-tier):
  C  source-data defect   -> the GERMAN source itself is broken (OCR/garble/
                             typo) in a way that blocks a clean translation.
                             ESCALATE to Cologne; do not "fix" in Russian.
  A  mechanical/format     -> German left untranslated (connective/gloss),
                             or anchors/structure damaged. Fast, low-judgement.
  B  translation-quality   -> German WAS translated but the rendering is doubted
                             (semantic / terminology / anglicism / hallucination
                             / truncation / grammar). Needs scholarly judgement.
  FAST sev<=1, no actionable defect ("Publishable" / negated findings). Bulk
       rubber-stamp.

Run:  python triage_review_queue.py
Reads  _review_queue.jsonl   Writes  _review_queue.triage.csv (gitignored)
"""
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_review_queue.jsonl")
OUT = os.path.join(HERE, "_review_queue.triage.csv")

# Phrases where the judge says German was NOT left untranslated. Stripped before
# we test the positive "left untranslated" marker, else they false-positive.
NEG_UNTRANS = [
    "no german left untranslated",
    "no german words left untranslated",
    "no german prose left untranslated",
    "no german left literally",
    "no german words left",
    "none left untranslated",
    "nothing left untranslated",
    "no untranslated german",
    "no german untranslated",
    "no german connective left",
    "all german translated",
    "all german prose translated",
    "all prose translated",
    "all connectives translated",
]

# Source-data defect: source itself broken AND it is NOT merely a quirk that was
# faithfully mirrored. Conservative on purpose — a human confirms any hit.
# Word-boundary regex so e.g. "incorruptibility" does NOT match "corrupt".
SOURCE_HARD = re.compile(
    r"\b(source defect|source-data defect|source typo|source error|"
    r"garbl\w*|corrupt\w*|illegible|ocr error|scanno|mis-scan|"
    r"broken in the source|source is corrupt|defective source|"
    r"missing in the source)\b",
    re.IGNORECASE,
)
MIRRORED = ["mirror", "preserved", "faithfully", "kept as", "retain"]

MECH = [
    "left untranslated", "untranslated german", "untranslated connective",
    "connective", "untranslated_gloss", "untranslated gloss",
    "gloss left", "fail on check (c)", "check (c)",
]
MECH_ANCHOR = ["anchor", "placeholder lost", "placeholder dropped",
               "{tn} lost", "structure lost", "structure collapsed",
               "clusters merged", "semicolon", "merged"]

QUAL = [
    "semantic", "terminolog", "anglicism", "calque", "hallucinat",
    "truncat", "leans", "loosely", "should be", "mis-render", "slip",
    "grammar", "case agreement", "agreement", "wrong", "incorrect",
    "drops", "added", "clash",
]


def strip_neg(text):
    low = text.lower()
    for p in NEG_UNTRANS:
        low = low.replace(p, " ")
    return low


def classify(sev, reason):
    """Return (bucket, fast_pass, subtype, defect_clause)."""
    low_full = reason.lower()
    low = strip_neg(reason)

    # --- source-data defect (highest routing priority, escalates out) ---
    src_hit = bool(SOURCE_HARD.search(low))
    quirk = "quirk" in low_full
    quirk_mirrored = quirk and any(m in low_full for m in MIRRORED)
    if src_hit and not quirk_mirrored:
        return "C_source", False, "source-data defect", defect_clause(reason)

    mech_hit = any(k in low for k in MECH) or any(k in low for k in MECH_ANCHOR)
    qual_hit = any(k in low for k in QUAL)

    # --- fast-pass: judge says minor/keep and no hard defect remains ---
    publishable = "publishable" in low_full or "no defect" in low_full
    if sev <= 1 and not mech_hit and (publishable or not qual_hit):
        return "A_mechanical" if False else "FAST_pass", True, "likely-clean", defect_clause(reason)

    if mech_hit:
        return "A_mechanical", False, "untranslated/format", defect_clause(reason)
    if qual_hit:
        return "B_quality", False, "rendering doubt", defect_clause(reason)
    # nothing matched but sev>=2 -> needs a human look, park in quality
    return "B_quality", False, "unclassified (sev>=2)", defect_clause(reason)


_CLAUSE_MARKERS = re.compile(
    r"(FAIL[^.]*\.|DEFECT[^.]*\.|BUT [^.]*\.|However[^.]*\.|Minor[^.]*\.|"
    r"[^.]*left untranslated[^.]*\.|[^.]*should be[^.]*\.|[^.]*slip[^.]*\.)",
    re.IGNORECASE,
)


def defect_clause(reason):
    """Pull the single most informative defect sentence for a one-line summary."""
    flat = " ".join(reason.split())
    m = _CLAUSE_MARKERS.search(flat)
    clause = m.group(1).strip() if m else flat
    return clause[:240]


# work order: source first (escalate), then mechanical & quality by severity
# desc, fast-pass last. Lower sort key sorts first.
BUCKET_ORDER = {"C_source": 0, "A_mechanical": 1, "B_quality": 2, "FAST_pass": 3}


def sort_key(row):
    return (BUCKET_ORDER[row["bucket"]], -int(row["severity"]), int(row["ord"]))


def main():
    rows = []
    with open(SRC, encoding="utf-8") as f:
        objs = [json.loads(l) for l in f if l.strip()]
    for o in objs:
        sev = int(o.get("severity") or 0)
        bucket, fast, subtype, clause = classify(sev, o.get("reason", ""))
        rows.append({
            "bucket": bucket,
            "severity": sev,
            "fast_pass": fast,
            "subtype": subtype,
            "ord": o.get("ord"),
            "key1": o.get("key1", ""),
            "key2": o.get("key2", ""),
            "attested": bool(o.get("attested")),
            "defect_clause": clause,
            "reason": o.get("reason", ""),
        })
    rows.sort(key=sort_key)

    fields = ["bucket", "severity", "fast_pass", "subtype", "ord", "key1",
              "key2", "attested", "defect_clause", "reason"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ----- console summary (cross-tab) -----
    from collections import Counter
    by_bucket = Counter(r["bucket"] for r in rows)
    print("triaged %d rows -> %s" % (len(rows), OUT))
    print("\nbucket x severity:")
    sevs = sorted({r["severity"] for r in rows})
    print("  %-14s %s  total" % ("bucket", " ".join("s%d" % s for s in sevs)))
    for b in ["C_source", "A_mechanical", "B_quality", "FAST_pass"]:
        brows = [r for r in rows if r["bucket"] == b]
        cells = Counter(r["severity"] for r in brows)
        line = " ".join("%2d" % cells.get(s, 0) for s in sevs)
        print("  %-14s %s   %3d" % (b, line, len(brows)))
    print("\nactionable (sev>=2): %d" % sum(1 for r in rows if r["severity"] >= 2))
    print("attested-corroborated rows: %d / %d" %
          (sum(1 for r in rows if r["attested"]), len(rows)))


if __name__ == "__main__":
    main()
