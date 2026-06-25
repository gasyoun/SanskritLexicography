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
MD = os.path.join(os.path.dirname(HERE), "REVIEW_QUEUE_TRIAGE.md")

# Phrases where the judge says German was NOT left untranslated. Stripped before
# we test the positive "left untranslated" marker, else they false-positive.
# The regex covers "no German <anything> (left|remains) untranslated", plus the
# explicit "all ... translated" affirmations.
NEG_UNTRANS = re.compile(
    r"no german[\w ,'-]{0,40}?(?:left |remains? )?untranslated|"
    r"no german[\w ,'-]{0,30}?(?:left|residue)|"
    r"(?:none|nothing)[\w ,'-]{0,20}?left untranslated|"
    r"no untranslated german|no german untranslated|"
    r"all (?:german |german prose |prose |connectives? )?translated",
    re.IGNORECASE,
)

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

# A defect "clause" is the operative sentence(s) where the judge states what is
# wrong. The pass-narration ("connective 'im' correctly rendered") is NOT a
# clause, so classifying on clauses avoids the substring false-positives that
# plague whole-reason keyword matching.
_CLAUSE_MARKERS = re.compile(
    r"(FAIL\b[^.]*\.|DEFECT[^.]*\.|\bdefect\b[^.]*\.|BUT\b[^.]*\.|"
    r"However[^.]*\.|[Mm]inor[^.]*\.|One (?:defect|minor|slip)[^.]*\.|"
    r"[Oo]nly (?:nit|blemish|issue|blemish)[^.]*\.|[Bb]lemish[^.]*\.|"
    r"\bnit:[^.]*\.|awkward[^.]*\.|inverted[^.]*\.|"
    r"[^.]*\bleft untranslated[^.]*\.|[^.]*\buntranslated\b[^.]*\.|"
    r"[^.]*\bshould be[^.]*\.|[^.]*\bslip\b[^.]*\.)",
)

# clauses that explicitly disavow a defect -> fold back into FAST
NONDEF = re.compile(r"non-defect|non-issue|not a defect|\bharmless\b|"
                    r"minor non|no defect", re.IGNORECASE)

# mechanical: a German leftover, or anchor/structure damage. Tested on clauses.
MECH_RE = re.compile(
    r"left untranslated|\buntranslated\b|untranslated_gloss|check \(c\)|"
    r"\bleftover\b|residue|retains? (?:the )?german|"
    r"german[^.]{0,40}(?:left|not rendered|not translated)|"
    r"anchors?[^.]{0,30}(?:lost|broken|dropped|duplicat)|"
    r"placeholder[^.]{0,20}(?:lost|dropped|missing)|"
    r"structure[^.]{0,20}(?:lost|merged|collapsed)|clusters merged|"
    r"semicolons?[^.]{0,20}(?:lost|dropped|not preserved)",
    re.IGNORECASE,
)
# quality: German WAS translated but rendering doubted.
QUAL_RE = re.compile(
    r"semantic|terminolog|anglicism|calque|hallucinat|truncat|leans|loose|"
    r"softening|nuance|should be|\bslip\b|drops?\b|\badded\b|looser|stronger|"
    r"expansion|mis-render|case agreement|agreement|grammar|\bwrong\b|"
    r"incorrect|clash|too literal|over-literal|mistransl",
    re.IGNORECASE,
)


def strip_neg(text):
    return NEG_UNTRANS.sub(" ", text.lower())


def defect_clauses(reason):
    """Return the list of operative defect sentences (negation stripped)."""
    low = strip_neg(" ".join(reason.split()))
    return [m.group(0).strip() for m in _CLAUSE_MARKERS.finditer(low)]


def defect_clause(reason):
    """One-line summary: a window from the start of the most informative defect
    clause. Uses a char window (not a period boundary) so 19th-c. abbreviation
    dots ("lat.", "т.") inside the sentence don't truncate the summary."""
    low = strip_neg(" ".join(reason.split()))
    cs = defect_clauses(reason)
    if cs:
        # prefer a hard-fail clause over a 'Minor' aside if both exist
        hard = [c for c in cs if re.match(r"fail|defect|but|however", c, re.I)]
        anchor = (hard[0] if hard else cs[0])[:25]
        i = low.find(anchor.lower())
        window = low[i:i + 240] if i >= 0 else (hard[0] if hard else cs[0])
        return window.strip()
    return " ".join(reason.split())[:180]


def classify(sev, reason):
    """Return (bucket, fast_pass, subtype, defect_clause)."""
    clauses = defect_clauses(reason)
    ctext = " ".join(clauses)

    # --- source-data defect (highest routing priority, escalates out) ---
    src_hit = bool(SOURCE_HARD.search(reason))
    quirk = "quirk" in reason.lower()
    quirk_mirrored = quirk and any(m in reason.lower() for m in MIRRORED)
    if src_hit and not quirk_mirrored:
        return "C_source", False, "source-data defect", defect_clause(reason)

    # --- no real defect clause, or only an explicit non-defect aside ---
    real = [c for c in clauses if not NONDEF.search(c)]
    if not real:
        if sev <= 1:
            return "FAST_pass", True, "likely-clean", defect_clause(reason)
        # sev>=2 with no extractable clause: park for a human look
        return "B_quality", False, "unclassified (sev>=2)", defect_clause(reason)

    rtext = " ".join(real)
    # mechanical takes precedence: it is the concrete, low-judgement fix
    if MECH_RE.search(rtext):
        return "A_mechanical", False, "untranslated/format", defect_clause(reason)
    if QUAL_RE.search(rtext):
        return "B_quality", False, "rendering doubt", defect_clause(reason)
    return "B_quality", False, "other doubt", defect_clause(reason)


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

    write_md(rows)
    print("wrote guide -> %s" % MD)


def _md_table(rows):
    out = ["| sev | headword (key2) | attested? | defect (judge's words) |",
           "|----:|-----------------|:---------:|------------------------|"]
    for r in rows:
        att = "yes" if r["attested"] else "—"
        clause = r["defect_clause"].replace("|", "\\|")
        if len(clause) > 150:
            clause = clause[:147] + "…"
        out.append("| %d | `%s` | %s | %s |" %
                    (r["severity"], r["key2"], att, clause))
    return "\n".join(out)


def write_md(rows):
    from collections import Counter
    n = len(rows)
    by = Counter(r["bucket"] for r in rows)
    A = [r for r in rows if r["bucket"] == "A_mechanical"]
    B2 = [r for r in rows if r["bucket"] == "B_quality" and r["severity"] >= 2]
    B1 = [r for r in rows if r["bucket"] == "B_quality" and r["severity"] < 2]
    C = [r for r in rows if r["bucket"] == "C_source"]
    att = sum(1 for r in rows if r["attested"])
    doc = f"""# Review-queue triage — pwg_ru legacy `needs_review`

**Auto-generated — do not hand-edit.** Regenerate with
[`src/triage_review_queue.py`](src/triage_review_queue.py).
Ranked worklist (one row per card, all columns): `src/_review_queue.triage.csv`
(gitignored — it is your personal worklist, derived from the gitignored
`src/_review_queue.jsonl`).

This is **pre-processing, not adjudication.** Every row was already scored by the
Opus QA judge (rubric: [`pwg_ru_prompts/2_qa_sudya_opus.txt`](pwg_ru_prompts/2_qa_sudya_opus.txt));
this tool only *buckets* those existing verdicts by defect type and orders them
by the judge's own severity. **You** make the final call on every card — nothing
here was auto-edited, and no correction was applied to any source.

## At a glance — {n} cards

| bucket | what it is | count | how to work it |
|--------|-----------|------:|----------------|
| **C — source-data defect** | the 19th-c. German source itself is broken (OCR/garble/typo) so a clean RU is impossible | **{by['C_source']}** | escalate to Cologne; do **not** "fix" in Russian |
| **A — mechanical / format** | German connective/preposition left untranslated, or anchors/structure damaged | **{by['A_mechanical']}** | fast, low-judgement edits; the judge names the exact word |
| **B — translation-quality** | German *was* translated but the rendering is doubted (semantic / terminology / nuance) | **{by['B_quality']}** | needs scholarly judgement; weigh against the attested gloss |
| **FAST — likely clean** | sev ≤ 1, no actionable defect ("Publishable" / minor non-issue) | **{by['FAST_pass']}** | bulk rubber-stamp / spot-check |

Severity is the judge's own 0–5 confidence (rubric: 1–2 = keep, 3 = arguable,
4–5 = must redo). **{sum(1 for r in rows if r['severity'] >= 2)} cards score sev ≥ 2** — those are the real work; the other
{by['FAST_pass'] + sum(1 for r in rows if r['bucket']=='B_quality' and r['severity']<2)} are minor.
**{att}/{n}** cards carry an independent attested-dictionary corroboration
(Kochergina / KOW / Knauer …) in the `attested` column — lean on it in bucket B.

## Suggested order of work

1. **C (source defects) — {by['C_source']}.** None survived triage: every "source
   quirk" the judge noted was *faithfully mirrored* in the RU, so there is
   nothing to escalate. If you spot a genuine source defect while reviewing,
   route it to csl-orig / Cologne — never silently "correct" it in the RU.
2. **A (mechanical) — {by['A_mechanical']}.** Quickest wins. Each is one or two
   untranslated German function-words (`und`→и, `oder`→или, `im`→в, `von`→от)
   sitting in an otherwise-fine card. Confirm the judge's call and patch.
3. **B (quality) sev ≥ 2 — {len(B2)}.** The cards that need you. Semantic choice,
   terminology calque, gender/agreement slips, awkward word order. Decide
   against the attested gloss where present.
4. **B (quality) sev 1 — {len(B1)}** and **FAST — {by['FAST_pass']}.** Minor nuances
   and clean cards. Skim / spot-check; bulk-approve.

## A — mechanical / format ({len(A)})

{_md_table(A)}

## B — translation-quality, sev ≥ 2 ({len(B2)})

{_md_table(B2)}
"""
    if C:
        doc += "\n## C — source-data defect (confirm before escalating)\n\n"
        doc += _md_table(C) + "\n"
    doc += ("\n---\n*Buckets are heuristic groupings of the judge's prose, meant "
            "to order your pass — not a substitute for reading the card. The full "
            "`reason` text for every row is in `src/_review_queue.triage.csv`.*\n")
    with open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)


if __name__ == "__main__":
    main()
