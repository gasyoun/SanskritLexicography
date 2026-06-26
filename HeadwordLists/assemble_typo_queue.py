"""Assemble the PRINT_READINESS item-A typo queue for MW + PWG into one ready-to-file list.

Pulls the body-confirmed FILE-FIRST typos from SanskritSpellCheck
(corrections_draft/<DICT>/<DICT>_file_first_sf.txt, CORRECTIONS format DICT:wrong:right:n),
enriches each with IAST, an error-type label, and the entry-body evidence from the triaged
file, and writes A_TYPO_QUEUE.md. The human verifies each on the scan, flips n→y, and files
via SanskritSpellCheck's chg_nchg_sep.py — this is just the consolidated, readable queue.
"""
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
SSC = os.environ.get("SSC_DIR", os.path.normpath(os.path.join(HERE, "..", "..", "SanskritSpellCheck", "corrections_draft")))
OUT = os.path.join(HERE, "A_TYPO_QUEUE.md")
DICTS = ["MW", "PWG"]

def iast(s):
    try: return su.from_slp1(s)
    except Exception: return s

CLASS = {  # SLP1 confusion -> human label (order-independent)
    frozenset("nR"): "dental→retroflex (n→ṇ)", frozenset("tw"): "dental→retroflex (t→ṭ)",
    frozenset("dq"): "dental→retroflex (d→ḍ)", frozenset("TW"): "aspirate retroflex (th→ṭh)",
    frozenset("DQ"): "aspirate retroflex (dh→ḍh)", frozenset("sS"): "sibilant (s→ś)",
    frozenset("Sz"): "sibilant (ś→ṣ)", frozenset("sz"): "sibilant (s→ṣ)", frozenset("wW"): "aspiration (ṭ→ṭh)",
    frozenset("bv"): "b↔v", frozenset("aA"): "vowel length (a↔ā)", frozenset("iI"): "vowel length (i↔ī)",
    frozenset("uU"): "vowel length (u↔ū)",
}
def err_label(w, r):
    diffs = [(a, b) for a, b in zip(w, r) if a != b]
    if len(w) == len(r) and len(diffs) == 1:
        a, b = diffs[0]
        return CLASS.get(frozenset(a + b) if a != b else frozenset(a), f"{a}→{b}")
    return "spelling"

def evidence(dictcode):
    """wrong-key -> short entry-body evidence from <DICT>_triaged.txt."""
    p = os.path.join(SSC, dictcode, f"{dictcode}_triaged.txt")
    ev = {}
    if not os.path.exists(p): return ev
    lines = open(p, encoding="utf-8").read().splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r'^(\S+)\s+->\s+\S+\s+(\[[^\]]*\])', ln)
        if m:
            body = lines[i + 1].strip() if i + 1 < len(lines) else ""
            ev[m.group(1)] = (m.group(2), body[:160])
    return ev

def main():
    rows = []
    for d in DICTS:
        sf = os.path.join(SSC, d, f"{d}_file_first_sf.txt")
        if not os.path.exists(sf):
            print(f"  missing {sf}"); continue
        ev = evidence(d)
        for ln in open(sf, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if ln.startswith(";") or not ln.strip():
                continue
            parts = ln.split(":")
            if len(parts) != 4:
                continue
            dc, w, r, flag = parts
            tag, body = ev.get(w, ("", ""))
            rows.append((dc, w, iast(w), r, iast(r), err_label(w, r), tag, body))

    L = ["# Item A — MW + PWG typo queue (ready to file)", "",
         f"The **{len(rows)}** body-confirmed FILE-FIRST typos for the print spine "
         "(MW + PWG), consolidated from "
         "[SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) "
         "(`corrections_draft/<DICT>/<DICT>_file_first_sf.txt`). Each was classified TYPO from "
         "the dictionary's **own entry text** and source-confirmed; the consonant-class flags "
         "(retroflex / sibilant / aspirate / b↔v) are the high-precision ones.", "",
         "**To file:** verify each on the scan, then in the SanskritSpellCheck repo flip the "
         "trailing `n`→`y` in the `*_file_first_sf.txt` and run "
         "`python chg_nchg_sep.py <DICT>_file_first_sf.txt chg.txt nchg.txt` → file to "
         "[csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections). "
         "Do **not** bulk-apply — these are individually confirmed.", "",
         "| dict | wrong (SLP1) | wrong (IAST) | → right (SLP1) | right (IAST) | error type | evidence |",
         "|---|---|---|---|---|---|---|"]
    for dc, w, wi, r, ri, lab, tag, body in rows:
        ev = (f"`{tag}` " if tag else "") + (body.replace("|", "\\|") if body else "")
        L.append(f"| {dc} | `{w}` | {wi} | `{r}` | {ri} | {lab} | {ev} |")
    L += ["", f"_MW: {sum(1 for x in rows if x[0]=='MW')} · "
          f"PWG: {sum(1 for x in rows if x[0]=='PWG')} · total {len(rows)}. "
          "Source-of-truth + filing workflow live in SanskritSpellCheck; this is the print-readiness "
          "(item A) consolidated view._"]
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print(f"wrote {OUT}: {len(rows)} typos ({', '.join(d + '=' + str(sum(1 for x in rows if x[0]==d)) for d in DICTS)})")

if __name__ == "__main__":
    main()
