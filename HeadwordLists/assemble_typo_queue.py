"""Assemble the PRINT_READINESS item-A typo queue for ALL dicts into one ready-to-file list.

Pulls every body-confirmed FILE-FIRST typo from SanskritSpellCheck
(corrections_draft/<DICT>/<DICT>_file_first_sf.txt, CORRECTIONS format DICT:wrong:right:n),
enriches each with IAST, an error-type label, and the entry-body evidence from the triaged
file, and writes A_TYPO_QUEUE.md. The human verifies each on the scan, flips n→y, and files
via SanskritSpellCheck's chg_nchg_sep.py — this is just the consolidated, readable queue.
"""
import sys, re, os, glob
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su
SSC = os.environ.get("SSC_DIR", os.path.normpath(os.path.join(HERE, "..", "..", "SanskritSpellCheck", "corrections_draft")))
OUT = os.path.join(HERE, "A_TYPO_QUEUE.md")
SPINE = ("MW", "PWG")   # print spine — list first

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

def read_dict(d):
    sf = os.path.join(SSC, d, f"{d}_file_first_sf.txt")
    if not os.path.exists(sf): return []
    ev = evidence(d); out = []
    for ln in open(sf, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith(";") or not ln.strip(): continue
        parts = ln.split(":")
        if len(parts) != 4: continue
        dc, w, r, flag = parts
        tag, body = ev.get(w, ("", ""))
        out.append((dc, w, iast(w), r, iast(r), err_label(w, r), tag, body))
    return out

def main():
    # discover every dict with a non-empty FILE-FIRST queue; spine first, then by count desc
    found = {}
    for sf in glob.glob(os.path.join(SSC, "*", "*_file_first_sf.txt")):
        d = os.path.basename(os.path.dirname(sf))
        rs = read_dict(d)
        if rs: found[d] = rs
    order = sorted(found, key=lambda d: (d not in SPINE, SPINE.index(d) if d in SPINE else 0, -len(found[d]), d))
    rows = [r for d in order for r in found[d]]
    total = len(rows)
    percent = {d: len(found[d]) for d in order}

    L = ["# Item A — typo queue, all dicts (ready to file)", "",
         f"All **{total}** body-confirmed FILE-FIRST typos across **{len(order)}** dictionaries, "
         "consolidated from [SanskritSpellCheck](https://github.com/gasyoun/SanskritSpellCheck) "
         "(`corrections_draft/<DICT>/<DICT>_file_first_sf.txt`). Each was classified TYPO from "
         "the dictionary's **own entry text** and source-confirmed; the consonant-class flags "
         "(retroflex / sibilant / aspirate / b↔v) are the high-precision ones. The **print "
         "spine (MW, PWG)** is listed first.", "",
         "Per dict: " + " · ".join(f"**{d}** {percent[d]}" for d in order) + ".", "",
         "**To file:** verify each on the scan, then in the SanskritSpellCheck repo flip the "
         "trailing `n`→`y` in that dict's `*_file_first_sf.txt` and run "
         "`python chg_nchg_sep.py <DICT>_file_first_sf.txt chg.txt nchg.txt` → file to "
         "[csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections). "
         "Do **not** bulk-apply — these are individually confirmed.", "",
         "| dict | wrong (SLP1) | wrong (IAST) | → right (SLP1) | right (IAST) | error type | evidence |",
         "|---|---|---|---|---|---|---|"]
    for dc, w, wi, r, ri, lab, tag, body in rows:
        ev = (f"`{tag}` " if tag else "") + (body.replace("|", "\\|") if body else "")
        L.append(f"| {dc} | `{w}` | {wi} | `{r}` | {ri} | {lab} | {ev} |")
    L += ["", f"_Total {total} across {len(order)} dicts. Source-of-truth + filing workflow live in "
          "SanskritSpellCheck; this is the print-readiness (item A) consolidated view. The MW+PWG "
          "spine subset is the minimum to clear before the spine goes to print._"]
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print(f"wrote {OUT}: {total} typos across {len(order)} dicts ("
          + ", ".join(f"{d}={percent[d]}" for d in order) + ")")

if __name__ == "__main__":
    main()
