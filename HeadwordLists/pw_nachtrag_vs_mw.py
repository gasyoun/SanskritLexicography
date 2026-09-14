#!/usr/bin/env python3
"""H4837 builder: PW/PWK Nachtraege starred headwords missing from MW (csl-corrections#119).

Frozen convention (reproduces the handoff's derived stat exactly: 273 MAHAYV citers):

1. Parse pw.txt + pwkvn.txt headers with the loose regex (catches fractional <L>
   inserted sub-entries): ^<L>([^<]+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)
2. Keep entries whose <k2> starts with '*' (Cologne marker for digitizer-inserted
   Nachtraege headwords). clean(k1) == clean(k2[1:]) holds for all such entries.
3. Dedupe by cleaned SLP1 headword; keep the richest body (tie: lexicographically
   smallest (src, L)). clean() = isalpha-only (strips * / digits / marks).
4. Candidate = headword absent from MW99's cleaned k1|k2 set.
5. Cross-dict corroboration over all 36 other v02 dictionaries (cleaned k1|k2).
6. Corpus check against DCS-conllu lemma + form sets (IAST), if the corpus is present.

Stdlib only. Env: CSL_ORIG_V02 (csl-orig v02 dir), DCS_CONLLU (DCS-conllu dir, optional).

Usage: python -u pw_nachtrag_vs_mw.py [csl-orig-v02-dir]
Outputs (beside this script):
  MW-missing-PW-Nachtrag-candidates-14-09-2026.tsv   frozen candidate list
  MW-missing-PW-Nachtrag-candidates-14-09-2026.md    method + counts companion
"""
import os
import re
import sys
import time
from collections import OrderedDict
from difflib import SequenceMatcher
from pathlib import Path

t0 = time.time()
OUT = Path(__file__).parent
DATE = "14-09-2026"

V02 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ.get("CSL_ORIG_V02", ""))
if not V02 or not V02.exists():
    sys.exit("ERROR: pass csl-orig v02 dir as argv[1] or set CSL_ORIG_V02")

DCS = Path(os.environ.get("DCS_CONLLU", "")) if os.environ.get("DCS_CONLLU") else None

HW_LINE = re.compile(r"^<L>([^<]+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)")

SLP1_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "E": "ai", "O": "au", "M": "ṃ", "H": "ḥ", "N": "ṅ", "Y": "ñ", "w": "ṭ",
    "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ", "T": "th", "D": "dh", "L": "ḻ",
    "S": "ś", "z": "ṣ", "K": "kh", "G": "gh", "C": "ch", "J": "jh", "P": "ph", "B": "bh",
}


def clean(hw):
    """Keep SLP1 letters only (strip * / accents-marks / digits)."""
    return "".join(c for c in hw if c.isalpha())


def iast(s):
    return "".join(SLP1_IAST.get(c, c) for c in s)


STEM_SUFFIXES = ("aH", "aM", "as", "am", "an", "at", "eH", "oH",
                 "A", "a", "I", "i", "U", "u", "F", "f", "o", "e")


def stemkey(hw):
    c = hw
    for suf in STEM_SUFFIXES:
        if c.endswith(suf) and len(c) > len(suf):
            return c[: -len(suf)]
    return c


def fold(s):
    return s.lower()


def iter_entries(path):
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                if cur is not None:
                    yield cur
                cur = {"L": m.group(1), "pc": m.group(2), "k1": m.group(3),
                       "k2": m.group(4), "body": []}
            elif cur is not None:
                cur["body"].append(line)
    if cur is not None:
        yield cur


def dict_set(path):
    ks = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HW_LINE.match(line)
            if m:
                c1 = clean(m.group(3))
                c2 = clean(m.group(4))
                if c1:
                    ks.add(c1)
                if c2:
                    ks.add(c2)
    return ks


def fuzzy_best(target, mw_list):
    """Deterministic near-form best match (same rule as the landed trial fix):
    highest case-folded ratio, then highest case-sensitive ratio, then
    lexicographically smallest candidate."""
    best = None
    best_key = None
    tc = fold(target)
    for cand in mw_list:
        r1 = SequenceMatcher(None, tc, fold(cand)).ratio()
        r2 = SequenceMatcher(None, target, cand).ratio()
        key = (round(r1, 6), round(r2, 6), tuple(-ord(ch) for ch in cand))
        if best_key is None or key > best_key:
            best_key = key
            best = (cand, r1)
    return best  # (form, folded_ratio)


def main():
    # ---- sources: starred-k2 entries of pw + pwkvn ----
    cands = OrderedDict()
    stats = {}
    for name, rel in (("pw", "pw/pw.txt"), ("pwkvn", "pwkvn/pwkvn.txt")):
        n_entries = n_star = 0
        for e in iter_entries(V02 / rel):
            n_entries += 1
            if not e["k2"].startswith("*"):
                continue
            n_star += 1
            hw = clean(e["k1"]) or clean(e["k2"])
            if not hw:
                continue
            body = "".join(e["body"])
            cur = cands.get(hw)
            if cur is None or len(body) > cur["blen"] or (
                    len(body) == cur["blen"] and (name, e["L"]) < (cur["src"], cur["L"])):
                cands[hw] = {"hw": hw, "src": name, "L": e["L"], "pc": e["pc"],
                             "body": body, "blen": len(body)}
        stats[name] = (n_entries, n_star)
        print(f"{rel}: {n_entries} entries, {n_star} starred-k2", flush=True)

    # ---- MW presence ----
    mw_set = dict_set(V02 / "mw" / "mw.txt")
    mw_stems = {stemkey(k) for k in mw_set}
    # near-form index: first-char bucket over MW headwords
    mw_buckets = {}
    for k in mw_set:
        mw_buckets.setdefault(k[0].lower(), []).append(k)
    print(f"MW cleaned k1|k2 set: {len(mw_set)}", flush=True)

    # ---- cross-dict corroboration ----
    DICTS = ["mw72", "pwg", "ap90", "bhs", "cae", "mci", "vei", "yat", "sch", "ap",
             "skd", "lan", "md", "pe", "pui", "wil", "bor", "bop", "ben", "gra",
             "gst", "ieg", "inm", "krm", "lrv", "nybj", "shs", "snp", "stc", "vcp",
             "armh", "acc", "ae", "bur", "ccs", "fri"]
    sets = {}
    for name in DICTS:
        p = V02 / name / f"{name}.txt"
        if p.exists():
            sets[name] = dict_set(p)
    print(f"corroboration dictionaries available: {len(sets)}", flush=True)

    # ---- DCS corpus sets ----
    dcs_lemmas = dcs_forms = None
    if DCS and DCS.exists():
        dcs_lemmas = set()
        dcs_forms = set()
        n_files = 0
        for conllu in sorted(DCS.glob("files/*/*.conllu")):
            n_files += 1
            with open(conllu, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#") or "\t" not in line:
                        continue
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 4 or "-" in parts[0]:
                        continue
                    if parts[1] != "_":
                        dcs_forms.add(parts[1])
                    if parts[2] != "_":
                        dcs_lemmas.add(parts[2])
        print(f"DCS-conllu: {n_files} files, {len(dcs_lemmas)} lemmas, {len(dcs_forms)} forms", flush=True)
    else:
        print("DCS-conllu: not provided (set DCS_CONLLU) - corpus columns empty", flush=True)

    MAHVY = re.compile(r"MAHĀVY\.?\s*((?:[0-9]+(?:\s*[.,]\s*)?)+)")

    rows = []
    for hw in sorted(cands):
        c = cands[hw]
        if hw in mw_set:
            continue  # candidate definition: absent from MW99
        corr = [d for d in sorted(sets) if hw in sets[d]]
        corr_ex72 = [d for d in corr if d != "mw72"]
        stem = stemkey(hw) in mw_stems
        bucket = mw_buckets.get(hw[0].lower(), [])
        near = fuzzy_best(hw, bucket) if bucket else None
        near_s = f"{near[0]}:{near[1]:.3f}" if near and near[1] >= 0.92 else ""
        mahv = MAHVY.search(c["body"])
        row = {
            "hw_slp1": hw,
            "iast": iast(hw),
            "src": c["src"],
            "pwk_L": c["L"],
            "pwk_pc": c["pc"],
            "also_pwkvn": 0,
            "body_chars": c["blen"],
            "mahavy": 1 if mahv else 0,
            "mahavy_refs": mahv.group(1).strip() if mahv else "",
            "mw_stem_variant": 1 if stem else 0,
            "mw_near": near_s,
            "corr_n": len(corr),
            "corr_n_ex_mw72": len(corr_ex72),
            "corr_dicts": ";".join(corr),
            "dcs_lemma": 0,
            "dcs_form": 0,
        }
        if dcs_lemmas is not None:
            row["dcs_lemma"] = 1 if iast(hw) in dcs_lemmas else 0
            row["dcs_form"] = 1 if iast(hw) in dcs_forms else 0
        rows.append(row)

    # also_pwkvn second pass (pw-starred headwords that pwkvn also digitizes)
    pwkvn_hws = set()
    for e in iter_entries(V02 / "pwkvn" / "pwkvn.txt"):
        if e["k2"].startswith("*"):
            c1 = clean(e["k1"])
            if c1:
                pwkvn_hws.add(c1)
    for r in rows:
        r["also_pwkvn"] = 1 if r["hw_slp1"] in pwkvn_hws else 0

    # ---- counts ----
    n = len(rows)
    tA = sum(1 for r in rows if r["corr_n"] >= 2)
    tB = sum(1 for r in rows if r["corr_n"] == 1)
    tC = sum(1 for r in rows if r["corr_n"] == 0)
    tA72 = sum(1 for r in rows if r["corr_n_ex_mw72"] >= 2)
    tB72 = sum(1 for r in rows if r["corr_n_ex_mw72"] == 1)
    tC72 = sum(1 for r in rows if r["corr_n_ex_mw72"] == 1)
    tC72 = sum(1 for r in rows if r["corr_n_ex_mw72"] == 0)
    mah = sum(1 for r in rows if r["mahavy"])
    stem_n = sum(1 for r in rows if r["mw_stem_variant"])
    near_n = sum(1 for r in rows if r["mw_near"])
    dcs_l = sum(1 for r in rows if r["dcs_lemma"])
    dcs_f = sum(1 for r in rows if r["dcs_form"])

    cols = list(rows[0].keys())
    out_tsv = OUT / f"MW-missing-PW-Nachtrag-candidates-{DATE}.tsv"
    with open(out_tsv, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[k]) for k in cols) + "\n")

    print(f"""
== frozen candidate list ==
unique starred Nachtraege headwords: {len(cands)}
missing from MW99: {n}
tiers (corr_n over {len(sets)} dicts, incl mw72+pwg): A(>=2)={tA} B(=1)={tB} C(=0)={tC}
tiers excl mw72: A={tA72} B={tB72} C={tC72}
cite MAHAYV: {mah}
mw stem-variant present: {stem_n}
mw near-form (>=0.92): {near_n}
DCS lemma attested: {dcs_l}; form attested: {dcs_f}
canary kAritra: {['MISSING-OK' for r in rows if r['hw_slp1']=='kAritra'] or 'FAIL'}
wrote {out_tsv.name} ({n} rows) in {time.time()-t0:.0f}s""", flush=True)

    # canary detail
    for r in rows:
        if r["hw_slp1"] == "kAritra":
            print(f"canary row: corr={r['corr_dicts'] or '-'} mahavy={r['mahavy']}"
                  f" refs={r['mahavy_refs']!r} near={r['mw_near']!r} dcs_lemma={r['dcs_lemma']}", flush=True)


if __name__ == "__main__":
    main()
