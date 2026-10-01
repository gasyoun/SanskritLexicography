"""Reproduce the (lost) csl-corrections#119 pilot: PW sup_7 Nachträge headwords vs MW.

The 20:13 pilot run of 14-09-2026 (worktree GRA-h4799-mwpwk-missing, swept before
commit) established the method and numbers; this builder re-derives them
deterministically from csl-orig/v02 so the candidate list survives.

Method (re-derived from the data, verified against the pilot's report):
  * pw.txt marks entries from the «Nachträge und Verbesserungen» sections with
    `<info n="sup_N"/>` (N=1..7); sup_7 = the letzte Nachträge (final supplement).
    Supplement headwords also carry a `*` in <k2> (`<k1>kAritra<k2>*kAritra`).
  * A sup_7 headword is compared to MW's key set (k1 ∪ k2, verbatim):
      exact  — present verbatim,
      stem   — present after stem/variant normalization (final vowel, visarga,
               * ˚ ~ markers),
      near   — difflib ratio >= 0.92 against an alphabetical-bucket neighbour
               (a REVIEW FLAG, never a match: kAritra~kAritA is the named false
               friend — causative participle vs abstract 'activity'),
      absent — none of the above = candidate entry MW skipped.
  * absent candidates get a rank from their alphabetical MW neighbours:
      A = neighbour is an MW annexure entry (<info n="sup"/>), i.e. MW inserted
          supplement entries around the candidate but skipped it (the kārāpaka
          pattern of csl-corrections#119),
      B = neighbour is MW main,
      C = no neighbour evidence.
  * reverse direction: share of MW annexure headwords present in sup_7 — the
    quantitative form of Andhrabharati's "MW(99) annexure draws on the letzte
    Nachträge" postulate.

Read-only over csl-orig; deterministic; no normalization beyond the stated tiers.
"""
import sys, os, io, re, difflib, bisect
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02")
OUT_TSV = os.path.join(HERE, "mw_pw_sup7_missing_entries.tsv")
OUT_REV = os.path.join(HERE, "mw_pw_sup7_reverse_overlap.tsv")

K1_RE = re.compile(r"<k1>([^<]+)")
K2_RE = re.compile(r"<k2>([^<]+)")
PC_RE = re.compile(r"<pc>([^<]+)")
L_RE = re.compile(r"^<L>(\d+)")
SUP_RE = re.compile(r'<info n="sup_(\d)"/>')
MWSUP = '<info n="sup"/>'

def entries(path):
    """Yield (Lnum, k1, k2, pc, body) per <L>-anchored entry."""
    Lnum = k1 = k2 = pc = None; body = []
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            m = L_RE.match(line)
            if m:
                if Lnum is not None:
                    yield Lnum, k1, k2, pc, "".join(body)
                Lnum = m.group(1)
                g = K1_RE.search(line); k1 = g.group(1).strip() if g else ""
                g = K2_RE.search(line); k2 = g.group(1).strip() if g else ""
                g = PC_RE.search(line); pc = g.group(1).strip() if g else ""
                body = [line]
            elif Lnum is not None:
                body.append(line)
                if line.startswith("<LEND>"):
                    yield Lnum, k1, k2, pc, "".join(body); Lnum = None; body = []
    if Lnum is not None:
        yield Lnum, k1, k2, pc, "".join(body)

def norm(key):
    """Stem/variant tier: drop * ˚ ~ markers and a final vowel / visarga / anusvara."""
    k = key.strip().strip("*˚~").strip()
    return re.sub(r"[aAiIuUfFxXeEoOHM]$", "", k)

# --- MW ------------------------------------------------------------------
mw_k1, mw_k2, mw_sup_k1 = set(), set(), set()
for Lnum, k1, k2, pc, body in entries(os.path.join(ORIG, "mw", "mw.txt")):
    if not k1: continue
    mw_k1.add(k1)
    if k2: mw_k2.add(k2)
    if MWSUP in body: mw_sup_k1.add(k1)
mw_all = mw_k1 | mw_k2
mw_all_norm = {norm(x) for x in mw_all if x}
mw_sorted = sorted(mw_all)

# --- pw sup_7 slice ------------------------------------------------------
sup_by_layer = {}
rows = []
mw_annex_in_sup7 = 0
for Lnum, k1, k2, pc, body in entries(os.path.join(ORIG, "pw", "pw.txt")):
    m = SUP_RE.search(body)
    if not m: continue
    layer = int(m.group(1))
    sup_by_layer[layer] = sup_by_layer.get(layer, 0) + 1
    if layer != 7 or not k1: continue
    hw = k2.lstrip("*") if k2.startswith("*") else k1
    if hw in mw_all: verdict = "exact"
    elif norm(hw) in mw_all_norm: verdict = "stem"
    else:
        i = bisect.bisect_left(mw_sorted, hw)
        lo, hi = max(0, i - 200), min(len(mw_sorted), i + 200)
        best, ratio = "", 0.0
        for cand in mw_sorted[lo:hi]:
            r = difflib.SequenceMatcher(None, hw, cand).ratio()
            if r > ratio: best, ratio = cand, r
        verdict = "near" if ratio >= 0.92 else "absent"
        near_best, near_ratio = best, ratio
    if verdict == "absent":
        i = bisect.bisect_left(mw_sorted, hw)
        nb = [mw_sorted[j] for j in (i - 1, i) if 0 <= j < len(mw_sorted)]
        if any(n in mw_sup_k1 for n in nb): rank = "A"
        elif nb: rank = "B"
        else: rank = "C"
    else:
        rank = ""
    rows.append((hw, Lnum, pc, verdict, rank,
                 near_best if verdict == "near" else "", f"{near_ratio:.2f}" if verdict == "near" else "",
                 re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", body)).strip()[:120]))

# reverse direction
sup7_hw = {r[0] for r in rows}
mw_annex_in_sup7 = sum(1 for k in mw_sup_k1 if k in sup7_hw)

from collections import Counter
c = Counter(r[3] for r in rows)
rc = Counter(r[4] for r in rows if r[3] == "absent")
print(f"pw sup layers: " + ", ".join(f"sup_{k}={v}" for k, v in sorted(sup_by_layer.items())))
print(f"sup_7 entries: {sum(sup_by_layer.get(7,0) for _ in [0])}; unique headwords: {len(sup7_hw)}")
print(f"verdicts: exact={c['exact']}, stem={c['stem']}, near={c['near']}, absent={c['absent']}")
print(f"absent ranks: A={rc['A']}, B={rc['B']}, C={rc['C']}")
print(f"reverse: MW annexure headwords={len(mw_sup_k1)}, of which in sup_7={mw_annex_in_sup7} "
      f"({100.0*mw_annex_in_sup7/len(mw_sup_k1):.0f}%)")
gate = any(r[0] == "kAritra" and r[3] in ("near", "absent") for r in rows)
print(f"GATE kAritra surfaced: {gate}")
if not gate:
    sys.exit("GATE FAIL: kAritra must surface in sup_7 (near or absent) — refusing to write artifacts.")

with io.open(OUT_TSV, "w", encoding='utf-8', newline='') as f:
    f.write("headword_slp1\tpw_L\tpc\tverdict\trank\tnear_mw\tnear_ratio\tentry_text\n")
    for r in sorted(rows):
        f.write("\t".join(str(x) for x in r) + "\n")
with io.open(OUT_REV, "w", encoding='utf-8', newline='') as f:
    f.write("mw_annexure_headword\tin_sup7\n")
    for k in sorted(mw_sup_k1):
        f.write(f"{k}\t{'Y' if k in sup7_hw else 'N'}\n")
print(f"WROTE {OUT_TSV}\nWROTE {OUT_REV}")