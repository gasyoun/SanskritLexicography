#!/usr/bin/env python3
"""H4884 adjudicator: one verdict row per never-seen (4,112) and dropped (27)
class of the mw72_baseline_sup7.py 2x2 (mw72_baseline_sup7.tsv).

never-seen = absent from MW72 AND MW99 (the kAritra class proper) - gets the
same corroboration / stem / fold-twin logic as mw_pwk_nachtraege_adjudicate.py
(H4878/H4883), reused not rebuilt: 36-dict corroboration, MW99 stemkey groups,
case-fold twin check, MAHAVY citation from the pw.txt sup_7 body. pwkvn.txt and
bhs.txt are added as extra corpus-check corroboration (handoff scope) on top of
the 36-dict set (bhs is already inside the 36; pwkvn is not).

dropped = MW72 had it, MW99 lost it (27 rows) - each gets a fixed
deleted-between-editions editorial note, plus the same corroboration/citation
columns for evidence.

Verdict semantics (never-seen rows only; dropped rows are always
dropped-between-editions):
  confirmed-missing            no exact/stem/fold hit in MW99 - the omission
                                stands; corr_n>=2 -> Tier A candidate.
  covered-by-MW-stem-form      MW99 carries the same stemkey headword.
  covered-by-fold-twin-flagged MW99 carries a case/vowel-length twin (the
                                Akalita/akalita trap) - needs eyes.
Named false-positive classes (flagged in review_note, verdict unchanged):
  denominal -aya verb stems (MW handles under the root/verb apparatus, not as
  a separate headword) and len(hw)<3 short forms - both named in
  MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md §5/§9.4.

Canary: kAritra (never-seen) -> confirmed-missing, pointers pw L620963 (the
physical line of its <L> tag in pw.txt) / pwkvn L53131 / bhs L4759 (the <L>
tag value in bhs.txt) / MAHAVY 245/844.

Stdlib only. Usage: python -u mw72_classes_adjudicate.py [csl-orig-v02]
"""
import os
import re
import sys
import time
import random
from pathlib import Path

t0 = time.time()
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
DATE = "15-09-2026"

V02 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    os.environ.get("CSL_ORIG_V02", r"C:/Users/user/Documents/GitHub/csl-orig/v02"))
if not V02.exists():
    sys.exit("ERROR: pass csl-orig v02 dir as argv[1] or set CSL_ORIG_V02")

BASELINE = HERE / "mw72_baseline_sup7.tsv"


def clean(hw):
    return "".join(c for c in hw if c.isalpha())


STEM_SUFFIXES = ("aH", "aM", "as", "am", "an", "at", "eH", "oH",
                 "A", "a", "I", "i", "U", "u", "F", "f", "o", "e")


def stemkey(hw):
    for suf in STEM_SUFFIXES:
        if hw.endswith(suf) and len(hw) > len(suf):
            return hw[: -len(suf)]
    return hw


HW_LINE = re.compile(r"^<L>([^<]+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)")
# pw.txt cites MAHAVY two ways in the same body: an inline "MAHAVY. 245" AND a
# second sense via <ls n="MAHAVY.">844</ls> with no inline text - both must be
# collected (kAritra's canonical citation is 245/844, only the first form was
# caught until this was noticed against the kAritra canary during H4884).
MAHVY_INLINE = re.compile(r"MAH[AĀ]VY\.?\s*([0-9]+)")
MAHVY_ATTR = re.compile(r'<ls\s+n="MAH[AĀ]VY\.?">\s*([0-9]+)')
AYA_DENOMINAL = re.compile(r"ay$")


def mahavy_refs(body):
    refs = []
    for rx in (MAHVY_INLINE, MAHVY_ATTR):
        for m in rx.finditer(body):
            if m.group(1) not in refs:
                refs.append(m.group(1))
    return refs


def dict_set(path):
    ks = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                for k in (clean(m.group(3)), clean(m.group(4))):
                    if k:
                        ks.add(k)
    return ks


def index_corpus(path, use_tag_as_L=False):
    """headword -> (L_citation, pc, body) for the FIRST entry per headword.
    L_citation is the physical line number by default (matches the pw/pwkvn
    canary quote); use_tag_as_L=True cites the <L> tag value instead (matches
    the bhs canary quote)."""
    idx = {}
    with open(path, encoding="utf-8") as f:
        cur = None
        for lineno, line in enumerate(f, start=1):
            m = HW_LINE.match(line)
            if m:
                tag, pc, k1, k2 = m.group(1), m.group(2), clean(m.group(3)), clean(m.group(4))
                Lcite = tag if use_tag_as_L else str(lineno)
                cur = [Lcite, pc, [line]]
                for k in (k1, k2):
                    if k and k not in idx:
                        idx[k] = cur
            elif cur is not None:
                cur[2].append(line)
    return {k: (v[0], v[1], "".join(v[2])) for k, v in idx.items()}


print("indexing corpora...", flush=True)

# ---- MW99 (mw.txt): headword set + stemkey groups + case-fold set ----
mw_stems, mw_hw_all = {}, set()
with open(V02 / "mw" / "mw.txt", encoding="utf-8") as f:
    for line in f:
        m = HW_LINE.match(line)
        if m:
            for k in (clean(m.group(3)), clean(m.group(4))):
                if k:
                    mw_stems.setdefault(stemkey(k), set()).add(k)
                    mw_hw_all.add(k)
mw_fold = {x.lower() for x in mw_hw_all}
print(f"MW99: {len(mw_hw_all)} headwords, {len(mw_stems)} stemkey groups", flush=True)

# ---- 36-dict corroboration (identical list to mw_pwk_nachtraege_adjudicate.py) ----
DICTS = ["mw72", "pwg", "ap90", "bhs", "cae", "mci", "vei", "yat", "sch", "ap",
         "skd", "lan", "md", "pe", "pui", "wil", "bor", "bop", "ben", "gra",
         "gst", "ieg", "inm", "krm", "lrv", "nybj", "shs", "snp", "stc", "vcp",
         "armh", "acc", "ae", "bur", "ccs", "fri"]
sets = {n: dict_set(V02 / n / f"{n}.txt") for n in DICTS
        if (V02 / n / f"{n}.txt").exists()}
print(f"corroboration dictionaries: {len(sets)}", flush=True)

# ---- pw.txt (sup_7 source; MAHAVY + citation) ----
pw_idx = index_corpus(V02 / "pw" / "pw.txt", use_tag_as_L=False)
print(f"pw.txt headwords indexed: {len(pw_idx)}", flush=True)

# ---- extra corpus checks named in the handoff: pwkvn.txt, bhs.txt ----
pwkvn_idx = index_corpus(V02 / "pwkvn" / "pwkvn.txt", use_tag_as_L=False) \
    if (V02 / "pwkvn" / "pwkvn.txt").exists() else {}
bhs_idx = index_corpus(V02 / "bhs" / "bhs.txt", use_tag_as_L=True) \
    if (V02 / "bhs" / "bhs.txt").exists() else {}
print(f"pwkvn.txt headwords: {len(pwkvn_idx)}; bhs.txt headwords: {len(bhs_idx)}", flush=True)

# ---- baseline rows ----
with open(BASELINE, encoding="utf-8") as f:
    lines = f.read().strip("\n").split("\n")
header = lines[0].split("\t")
base_rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
never_rows = [r for r in base_rows if r["class"] == "never-seen"]
dropped_rows = [r for r in base_rows if r["class"] == "dropped"]
print(f"baseline: never-seen={len(never_rows)} dropped={len(dropped_rows)}", flush=True)

DROP_NOTE = ("deleted-between-editions class: present in MW72 (1872), absent "
             "from MW99 (1899) - MW dropped an entry it once had; not a "
             "PWK-omission candidate, a separate correction class "
             "(see MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md §3)")

out_rows = []
skipped = []
for r in never_rows + dropped_rows:
    hw = clean(r["sup7_headword"])
    is_dropped = r["class"] == "dropped"
    attempts, pw_hit = 0, None
    while attempts < 3:
        attempts += 1
        try:
            pw_hit = pw_idx.get(hw)
            break
        except Exception:
            continue
    if pw_hit is None and attempts >= 3:
        skipped.append(hw)
    pw_L, pw_pc, pw_body = pw_hit if pw_hit else ("", "", "")
    pwkvn_hit = pwkvn_idx.get(hw)
    pwkvn_L, pwkvn_pc = (pwkvn_hit[0], pwkvn_hit[1]) if pwkvn_hit else ("", "")
    bhs_hit = bhs_idx.get(hw)
    bhs_L, bhs_pc = (bhs_hit[0], bhs_hit[1]) if bhs_hit else ("", "")

    refs = mahavy_refs(pw_body) if pw_body else []
    corr = [d for d in sorted(sets) if hw in sets[d]]
    corr_n = len(corr)

    notes = []
    if is_dropped:
        verdict = "dropped-between-editions"
        notes.append(DROP_NOTE)
    else:
        if hw in mw_hw_all:
            verdict = "anomaly-exact-hit-in-mw99"
            notes.append("baseline marked never-seen but hw is exact-present in "
                          "MW99 mw.txt - re-check baseline extraction")
        elif stemkey(hw) in mw_stems:
            verdict = "covered-by-MW-stem-form"
            forms = sorted(mw_stems.get(stemkey(hw), []))[:3]
            notes.append(f"MW99 stem-family forms: {';'.join(forms)}")
        elif hw.lower() in mw_fold:
            verdict = "covered-by-fold-twin-flagged"
            notes.append("case/vowel-length twin of an MW99 form (Akalita/"
                          "akalita trap) - same lexeme or distinct word, needs eyes")
        else:
            verdict = "confirmed-missing"
            if refs:
                notes.append(f"MAHAVY {'. '.join(refs)}")
        if AYA_DENOMINAL.search(hw) and hw.endswith("ay"):
            notes.append("named false-positive class: denominal -aya verb stem "
                          "(MW handles under root/verb apparatus, not as a "
                          "separate headword)")
        if len(hw) < 3:
            notes.append("named false-positive class: short-form (len<3)")

    out_rows.append({
        "sup7_headword": hw, "class": r["class"], "verdict": verdict,
        "pw_L": pw_L, "pw_pc": pw_pc,
        "pwkvn_L": pwkvn_L, "pwkvn_pc": pwkvn_pc,
        "bhs_L": bhs_L, "bhs_pc": bhs_pc,
        "mahavy": 1 if refs else 0,
        "mahavy_refs": ". ".join(refs),
        "corr_n": corr_n, "corr_dicts": ";".join(corr),
        "review_note": "; ".join(notes),
    })

cols = ["sup7_headword", "class", "verdict", "pw_L", "pw_pc",
        "pwkvn_L", "pwkvn_pc", "bhs_L", "bhs_pc",
        "mahavy", "mahavy_refs", "corr_n", "corr_dicts", "review_note"]
adj_path = HERE / f"MW72-CLASSES-ADJUDICATION-{DATE}.tsv"
with open(adj_path, "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for rec in out_rows:
        f.write("\t".join(str(rec.get(c, "")) for c in cols) + "\n")

# ---- Tier-A stubs: confirmed-missing (never-seen) with corr_n>=2 ----
tier_a = [r for r in out_rows
          if r["verdict"] == "confirmed-missing" and r["corr_n"] >= 2]
tier_a.sort(key=lambda r: (-(2 * r["corr_n"] + 2 * r["mahavy"]), r["sup7_headword"]))
stubs_path = HERE / f"MW72-CLASSES-TIERA-STUBS-{DATE}.md"
with open(stubs_path, "w", encoding="utf-8") as f:
    f.write(f"""# MW-entry stubs -- H4884 MW72-classes adjudicator (never-seen, corroborated >=2 dictionaries)

_Created: {DATE} · Last updated: {DATE}_

H4884 product over the never-seen (4,112) and dropped (27) classes of
[`mw72_baseline_sup7.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw72_baseline_sup7.tsv),
adjudicated in full in
[`MW72-CLASSES-ADJUDICATION-{DATE}.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW72-CLASSES-ADJUDICATION-{DATE}.tsv).
Stubs = never-seen rows with verdict `confirmed-missing` and corroboration
>= 2 of 36 Cologne dictionaries. Posting anything = MG ruling.

""")
    for r in tier_a:
        mah = f" · MAHĀVY {r['mahavy_refs']}" if r["mahavy"] else ""
        note = f" · ⚠ {r['review_note']}" if r["review_note"] else ""
        f.write(f"### {r['sup7_headword']}\n"
                f"- corr_n {r['corr_n']}: {r['corr_dicts']}{mah}{note}\n"
                f"- Source: pw.txt L{r['pw_L']} ({r['pw_pc']})\n"
                f"- Proposed MW headword: `{r['sup7_headword']}`\n")

n_conf = sum(1 for r in out_rows if r["verdict"] == "confirmed-missing")
n_stem = sum(1 for r in out_rows if r["verdict"] == "covered-by-MW-stem-form")
n_fold = sum(1 for r in out_rows if r["verdict"] == "covered-by-fold-twin-flagged")
n_drop = sum(1 for r in out_rows if r["verdict"] == "dropped-between-editions")
n_anom = sum(1 for r in out_rows if r["verdict"] == "anomaly-exact-hit-in-mw99")

canary = next((r for r in out_rows if r["sup7_headword"] == "kAritra"), None)
if canary is None:
    canary_line = "canary kAritra: NOT FOUND - FAIL"
else:
    ok = (canary["verdict"] == "confirmed-missing" and canary["pw_L"] == "620963"
          and canary["pwkvn_L"] == "53131" and canary["bhs_L"] == "4759"
          and canary["mahavy_refs"] == "245. 844")
    canary_line = (f"canary kAritra: verdict={canary['verdict']} pw_L={canary['pw_L']} "
                    f"pwkvn_L={canary['pwkvn_L']} bhs_L={canary['bhs_L']} "
                    f"mahavy={canary['mahavy_refs']} -> {'PASS' if ok else 'FAIL'}")

print(f"""
== H4884 MW72-classes adjudication ==
rows: {len(out_rows)} (never-seen {len(never_rows)} + dropped {len(dropped_rows)})
confirmed-missing: {n_conf}   covered-by-MW-stem-form: {n_stem}
covered-by-fold-twin-flagged: {n_fold}   dropped-between-editions: {n_drop}
anomalies: {n_anom}   skipped(3x-probe-fail): {len(skipped)}
Tier-A stubs: {len(tier_a)} -> {stubs_path.name}
{canary_line}
wrote {adj_path.name} in {time.time()-t0:.0f}s""", flush=True)

# ---- 30-sample spot-check (deterministic seed, confirmed-missing pool) ----
random.seed(4884)
conf = [r for r in out_rows if r["verdict"] == "confirmed-missing"]
sample = random.sample(conf, min(30, len(conf)))
sp_path = HERE / f"MW72-CLASSES-SPOTCHECK-30-{DATE}.tsv"
with open(sp_path, "w", encoding="utf-8") as f:
    f.write("sup7_headword\tverdict\tpw_L\tpw_pc\tcorr_n\tcorr_dicts\tmahavy_refs\t"
            "mw_exact_hit\tmw_fold_hit\tmw_stem_hit\n")
    for r in sample:
        hw = r["sup7_headword"]
        f.write("\t".join([
            hw, r["verdict"], r["pw_L"], r["pw_pc"], str(r["corr_n"]), r["corr_dicts"],
            r["mahavy_refs"],
            "1" if hw in mw_hw_all else "0",
            "1" if hw.lower() in mw_fold else "0",
            "1" if stemkey(hw) in mw_stems else "0"]) + "\n")
print(f"spot-check sample -> {sp_path.name}", flush=True)
