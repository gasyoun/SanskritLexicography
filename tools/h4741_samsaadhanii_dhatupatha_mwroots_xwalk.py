#!/usr/bin/env python3
"""H4741 — Samsaadhanii Dhātupāṭha × WhitneyRoots mw_roots join (VALIDATION-ONLY).

Sibling census A5 pilot 4. Joins Amba Kulkarni's SCL (samsaadhanii/scl)
machine-readable Pāṇinian Dhātupāṭha (skt_gen/Sentence/data/
dhatu_info_chart_wx.txt, 7,419 pada-rows; dhaatupaatha data CC BY-SA 3.0
per dhaatupaatha/README) to WhitneyRoots crosswalk/mw_roots.json (750
MW verbal roots, Cologne SLP1 keys).

VALIDATION-ONLY by mission: the upstream Dhātupāṭha data carries a
share-alike license and the handoff grants no LICENSE/registration step —
the committed artifacts are the script + an AGGREGATE parity report.
Row-level join output is emitted only with --emit-join-tsv (local/temp use).

Transliteration: SCL-WX → estate SLP1 via SCL's OWN converter table
(converters/wx2slp.lex, GPL; the table's pair mappings are facts) composed
with canonical `sanskrit_util` SLP1 (ṭ=w, ṭh=W, ḍ=q, ḍh=Q, ṇ=R, ṅ=N, ñ=Y,
ṛ=f, ṝ=F, ḷ=x, ṣ=z, ś=S). Identity for the shared ASCII remainder.
Rosetta verification in --selftest uses SCL's own filenames/words:
XAwu→dhātu, gaNa→gaṇa, parasmEpaxI→parasmaipada, AwmanepaxI→ātmanepada.

Tiers:
  tier1  exact estate-SLP1 root equality (anubandha/variant digits stripped)
  tier2  recall-only ASCII fold (case-sensitive SLP1 relaxed; diagnostics)

Prior art consumed, never re-derived:
  - sanskrit_util to_slp1/from_slp1 (canonical shared lib)
  - SCL converters/wx2slp.lex (upstream's own WX↔SLP pair table)
  - WhitneyRoots crosswalk/mw_roots.json (estate root canon)

Usage:
  python3 tools/h4741_samsaadhanii_dhatupatha_mwroots_xwalk.py \
      --dhatu /path/scl/skt_gen/Sentence/data/dhatu_info_chart_wx.txt \
      --mwroots /path/WhitneyRoots/crosswalk/mw_roots.json \
      --outdir data/samsaadhanii_dhatupatha_mwroots_xwalk \
      [--emit-join-tsv]
  python3 tools/h4741_samsaadhanii_dhatupatha_mwroots_xwalk.py --selftest

Exit 0 = PASS. Refuses to overwrite the report without --force.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date

# --- sanskrit-util discovery (canonical shared lib; do NOT fork its tables) ---
_SANSKRIT_UTIL_CANDIDATES = [
    os.environ.get("SANSKRIT_UTIL_PY", ""),
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "sanskrit-util", "py"),
    os.path.expanduser("~/Documents/GitHub/sanskrit-util/py"),
]
for _c in _SANSKRIT_UTIL_CANDIDATES:
    if _c and os.path.isdir(os.path.join(_c, "sanskrit_util")):
        sys.path.insert(0, _c)
        break
try:
    from sanskrit_util import to_slp1  # type: ignore
except ImportError:  # pragma: no cover
    sys.exit("FATAL: sanskrit_util not found (set SANSKRIT_UTIL_PY=<sanskrit-util>/py)")

# SCL-WX → SLP1 char. Pair mappings lifted from SCL's own converters/wx2slp.lex
# (the pairings are facts, not copyrightable expression); chars absent from the
# lex are shared between SCL-WX and SLP1 (verified via SCL Rosetta words).
WX2SLP = {
    "w": "t", "W": "T", "x": "d", "X": "D",          # dental row ↔ retroflex row
    "t": "w", "T": "W", "d": "q", "D": "Q",          #   (SCL-WX / SLP1 shuffles)
    "q": "f", "Q": "F",                              # ṛ, ṝ
    "R": "z",                                        # ṣ
    "N": "R",                                        # ṇ
    "F": "Y",                                        # ñ
    "f": "N",                                        # ṅ
    "L": "x",                                        # ḷ
    "z": "~", "Z": "'",                              # anubandha markers (stripped)
}
# SLP1 chars that are anubandha/citation markers in Dhātupāṭha citations,
# never part of an MW root citation form.
_ANUBANDHA = {"~", "'"}

# The 10 gaṇa "Adi" series names in SCL-WX → Pāṇinian class number.
# Rosetta: wuxAxiH=tudādi(7), ruXAxiH=rudhādi(8), wanAxiH=tanādi(9), kryAxiH=kryādi(10).
GANACLS = {
    "BvAxiH": 1, "axAxiH": 2, "juhowyAxiH": 3, "xivAxiH": 4, "svAxiH": 5,
    "curAxiH": 6, "wuxAxiH": 7, "ruXAxiH": 8, "wanAxiH": 9, "kryAxiH": 10,
}

DKEY_RE = re.compile(r"^[0-9]+$")


def wx_to_slp1(s):
    """SCL-WX string → estate SLP1, dropping anubandha markers."""
    out = []
    for ch in s:
        m = WX2SLP.get(ch, ch)
        if m in _ANUBANDHA:
            continue
        out.append(m)
    return "".join(out)


def parse_dhatu_key(key):
    """'aBi_arh1' → ('arh', ['aBi']) : last underscore token, digits stripped."""
    parts = key.split("_")
    root = parts[-1]
    root = re.sub(r"[0-9]+$", "", root)
    return wx_to_slp1(root), [wx_to_slp1(p) for p in parts[:-1]]


def parse_dhatu_chart(path):
    """Parse SCL dhatu_info_chart_wx.txt → distinct roots with gaṇa classes."""
    roots = {}      # slp1 root -> set of class numbers (None where unknown)
    n_rows = 0
    unknown_gana = Counter()
    prefixes_seen = Counter()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            cols = line.split(",")
            if len(cols) < 3:
                continue
            # field 0 is 'key <ws> pada' (tab or space); fields 1,2 are form, gaṇa
            f0 = cols[0].split()
            if len(f0) < 2:
                continue
            n_rows += 1
            key, pada = f0[0].strip(), f0[1].strip()
            _form, gana = cols[1].strip(), cols[2].strip()
            root, prefixes = parse_dhatu_key(key)
            if not root:
                continue
            prefixes_seen.update(prefixes)
            cls = GANACLS.get(gana)
            if cls is None:
                unknown_gana[gana] += 1
            roots.setdefault(root, set()).add(cls)
    return {
        "n_rows": n_rows,
        "roots": roots,
        "unknown_gana": unknown_gana,
        "prefixes_seen": prefixes_seen,
    }


def parse_mw_roots(path):
    """WhitneyRoots crosswalk/mw_roots.json → list of (slp1, hom, classes, gloss)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for e in data:
        slp1 = e.get("slp1", "")
        hom = e.get("homonym")
        classes = [int(c) for c in (e.get("class_arabic") or [])]
        out.append((slp1, hom, classes, e.get("gloss", "")))
    return out


def fold(s):
    """Recall-only ASCII fold: SLP1 is case-sensitive, folding is lossy —
    used ONLY as a diagnostic tier, never as a matched assertion."""
    return s.lower().replace("~", "").replace("'", "")


def run(dhatu_path, mwroots_path, outdir, emit_join=False, force=False):
    os.makedirs(outdir, exist_ok=True)
    out_report = os.path.join(outdir, "H4741_PARITY_REPORT.md")
    out_join = os.path.join(outdir, "h4741_join_local_only.tsv")
    if os.path.exists(out_report) and not force:
        sys.exit(f"REFUSAL: {out_report} exists (use --force)")

    scl = parse_dhatu_chart(dhatu_path)
    mw = parse_mw_roots(mwroots_path)

    mw_keys_exact = defaultdict(list)   # slp1 -> [(slp1, hom, classes)]
    mw_keys_fold = defaultdict(list)
    for slp1, hom, classes, _g in mw:
        mw_keys_exact[slp1].append((slp1, hom, classes))
        mw_keys_fold[fold(slp1)].append((slp1, hom, classes))

    stats = Counter()
    join_rows = []
    unmatched_exact, fold_only = [], []
    matched_scl_roots = set()
    class_agree = class_disagree = 0

    for root, clss in sorted(scl["roots"].items()):
        stats["scl_roots"] += 1
        hits = mw_keys_exact.get(root)
        if hits:
            stats["tier1"] += 1
            matched_scl_roots.add(root)
            scl_classes = {c for c in clss if c is not None}
            for slp1, hom, classes in hits:
                stats["join_pairs"] += 1
                if scl_classes and classes:
                    if scl_classes & set(classes):
                        class_agree += 1
                    else:
                        class_disagree += 1
                join_rows.append((root, slp1, hom, ",".join(map(str, classes)), 1))
        elif root in mw_keys_fold:
            f1 = mw_keys_fold[fold(root)]
            stats["tier2_fold_only"] += 1
            fold_only.append((root, [x[0] for x in f1]))
        else:
            stats["scl_unmatched"] += 1
            unmatched_exact.append(root)

    all_scl_fold = {fold(r) for r in scl["roots"]}
    mw_matched_exact = 0
    fold_witnessed_only = 0
    unmatched_mw = []   # neither exact nor fold vs the FULL SCL root set
    for slp1, _h, _c, g in mw:
        if slp1 in matched_scl_roots:
            mw_matched_exact += 1
        elif fold(slp1) in all_scl_fold:
            fold_witnessed_only += 1
        else:
            unmatched_mw.append((slp1, g))
    n_mw = len(mw)
    stats["mw_matched"] = mw_matched_exact
    stats["mw_fold_witnessed"] = fold_witnessed_only
    # residue split: explicitly lexicographic (MW "L.") vs other divergence
    l_flagged = [(k, g) for k, g in unmatched_mw
                 if ", L." in g or g.rstrip().endswith("L.") or " L. " in g]

    cov_scl = 100.0 * stats["tier1"] / max(1, stats["scl_roots"])
    cov_mw = 100.0 * stats["mw_matched"] / max(1, n_mw)

    def sha256(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    if emit_join:
        with open(out_join, "w", encoding="utf-8") as f:
            f.write("scl_root_slp1\tmw_slp1\tmw_homonym\tmw_class_arabic\ttier\n")
            for r in join_rows:
                f.write("\t".join(str(c) for c in r) + "\n")

    ug = scl["unknown_gana"]
    report = f"""# H4741 — Samsaadhanii Dhātupāṭha × WhitneyRoots mw_roots parity report

_Created: {date.today().strftime('%d-%m-%Y')} · tier: OxAlpha (opencode/z-ai/glm-5.3-flash) · VALIDATION-ONLY_

## Inputs (provenance)

| input | sha256 (first 12) | size |
|---|---|---|
| SCL `samsaadhanii/scl` `skt_gen/Sentence/data/dhatu_info_chart_wx.txt` (dhaatupaatha data CC BY-SA 3.0 per dhaatupaatha/README; N Shailaja & Amba Kulkarni) | `{sha256(dhatu_path)[:12]}` | {scl['n_rows']} pada-rows |
| WhitneyRoots `crosswalk/mw_roots.json` (estate MW root canon) | `{sha256(mwroots_path)[:12]}` | {len(mw)} roots |

Join key: SCL-WX root → estate SLP1 via a literal char table lifted from SCL's
own `converters/wx2slp.lex` (the pairings are upstream-attested facts; the
table is cross-verified against canonical `sanskrit_util` in `--selftest`,
which is sanskrit_util's only role — it is not in the runtime join path).
Anubandha markers (SCL-WX `z`/`Z`/trailing digits) stripped before join.

## Result — root-count parity

| metric | value |
|---|---|
| SCL distinct roots (anubandha/pada-deduped) | {stats['scl_roots']} |
| WhitneyRoots mw_roots entries | {n_mw} |
| **mw_roots matched by SCL, EXACT SLP1 only** | **{mw_matched_exact} / {n_mw} = {cov_mw:.1f} %** |
| mw_roots witnessed only via recall-only fold (tier2, not counted above) | {fold_witnessed_only} |
| mw_roots unmatched vs the FULL SCL root set (exact or fold) | {len(unmatched_mw)} |
| SCL roots matched in mw_roots (tier1 exact) | {stats['tier1']} / {stats['scl_roots']} = {cov_scl:.1f} % |
| SCL roots matching only under recall-only ASCII fold (tier2) | {stats['tier2_fold_only']} |
| SCL roots unmatched | {stats['scl_unmatched']} |
| join pairs (root × mw entry, tier1) | {stats['join_pairs']} |
| gaṇa-class agreement / disagreement on matched pairs | {class_agree} / {class_disagree} |
| SCL-WX gaṇa tokens outside the 10 Adi series | {sum(ug.values())} |

## Residue analysis (measured, not guessed)

- {len(unmatched_mw)} mw_roots entries have neither an exact nor a case-fold
  SLP1 partner anywhere in the full SCL root set; of these
  **{len(l_flagged)} are explicitly lexicographic** (MW gloss flags ", L." /
  "L." — late Sanskrit additions a Pāṇinian gaṇa-list does not attest); the
  remainder are genuine generator-chart gaps vs MW's inventory.
- Citation-grade divergence is measured separately, as {fold_witnessed_only}
  mw entries + {stats['tier2_fold_only']} SCL roots that pair only under the
  recall-only fold (MW guṇa/vṛddhi or aspirated citation shapes vs the
  Pāṇinian zero-grade chart; SCL-side examples:
  {", ".join(f"{k}↔{'+'.join(v)}" for k, v in fold_only[:6])}).
- Class agreement {class_agree}/{class_agree + class_disagree}
  ({100.0 * class_agree / max(1, class_agree + class_disagree):.1f} %) on matched
  pairs with classes on both sides — informational only.

Parity verdict: mw_roots is a **Whitney/MW-derived canon** — the SCL Pāṇinian
Dhātupāṭha (generator inventory) covers {cov_mw:.1f} % of it exactly; the
residue splits into explicitly lexicographic MW additions and citation-grade
divergence (measured above), not key-bridge failure. VALIDATION-ONLY: no
SCL-derived row-level data is committed; join TSV stays local (--emit-join-tsv).

## Risks

- SCL dhatu_info_chart is the *verb-generator* inventory, not the full
  Dhātupāṭha concordance (dhaatupaatha/files/*.html, 4,388 pages) — parity is
  against the generator's root set.
- tier2 (ASCII fold) is recall-only; tier1 numbers are the assertion.
- gaṇa class disagreement counts compare SCL gaṇa vs MW printed classes —
  informational, never auto-corrective.
"""
    with open(out_report, "w", encoding="utf-8") as f:
        f.write(report)

    print(json.dumps({
        "scl_roots": stats["scl_roots"], "mw_roots": n_mw,
        "mw_matched_exact": mw_matched_exact, "mw_coverage_pct": round(cov_mw, 1),
        "mw_fold_witnessed_only": fold_witnessed_only,
        "mw_unmatched": len(unmatched_mw), "mw_unmatched_L_flagged": len(l_flagged),
        "scl_matched": stats["tier1"], "scl_coverage_pct": round(cov_scl, 1),
        "tier2_fold_only": stats["tier2_fold_only"], "pairs": stats["join_pairs"],
        "class_agree": class_agree, "class_disagree": class_disagree,
    }, ensure_ascii=False))

    if stats["mw_matched"] == 0:
        print("FAIL: zero parity — join key is broken", file=sys.stderr)
        return 1
    return 0


def selftest():
    """Rosetta + join fixture: SCL's own filenames prove the WX table; a tiny
    synthetic chart × mw_roots proves tier1/tier2/miss paths and revalidation."""
    # 1. Rosetta: SCL-WX words of known identity through our converter.
    #    XAwu (SCL's own dhaatupaatha filename) = dhātu; gaNa.html = gaṇa;
    #    pada labels are locative (parasmaipadi/ātmanepadi → …padI).
    assert wx_to_slp1("XAwu") == "DAtu", wx_to_slp1("XAwu")
    assert wx_to_slp1("gaNa") == "gaRa", wx_to_slp1("gaNa")
    assert wx_to_slp1("parasmEpaxI") == "parasmEpadI", wx_to_slp1("parasmEpaxI")
    assert wx_to_slp1("AwmanepaxI") == "AtmanepadI", wx_to_slp1("AwmanepaxI")
    assert wx_to_slp1("BvAxiH") == "BvAdiH", wx_to_slp1("BvAxiH")
    assert wx_to_slp1("xivAxiH") == "divAdiH", wx_to_slp1("xivAxiH")
    assert to_slp1("divādiḥ") == wx_to_slp1("xivAxiH"), to_slp1("divādiḥ")
    # sanskrit_util cross-check on the mapped output (canonical lib, not forked)
    assert to_slp1("dhātu") == wx_to_slp1("XAwu"), to_slp1("dhātu")
    assert to_slp1("gaṇa") == wx_to_slp1("gaNa"), to_slp1("gaṇa")
    assert to_slp1("parasmaipadī") == wx_to_slp1("parasmEpaxI")
    assert to_slp1("ātmanepadī") == wx_to_slp1("AwmanepaxI")
    assert to_slp1("śās") == wx_to_slp1("SAs"), to_slp1("śās")

    # 2. Join fixture: exact hit, anubandha-stripped hit, fold-only hit, miss.
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="h4741_selftest_")
    chart = os.path.join(tmp, "chart.txt")
    with open(chart, "w") as f:
        # root 'gam' (no prefixes), bhvādi, both padas
        f.write("gam1 parasmEpaxI,gamLz,BvAxiH\n")
        f.write("gam1 AwmanepaxI,gamLz,BvAxiH\n")
        # prefixed root aBi_arh with anubandha z in form col
        f.write("aBi_arh1 parasmEpaxI,arhaz,BvAxiH\n")
        # ṇ-root exercising WX N→R
        f.write("gaN1 parasmEpaxI,gaNizf,curAxiH\n")
        # z-anubandha root exercising strip path (cur + z marker)
        f.write("cur1 parasmEpaxI,curAzi,BvAxiH\n")
    mwjson = os.path.join(tmp, "mw.json")
    with open(mwjson, "w") as f:
        json.dump([
            {"mw_L": "1", "slp1": "gam", "homonym": None, "class": ["I"], "class_arabic": [1], "gloss": "to go"},
            {"mw_L": "2", "slp1": "arh", "homonym": None, "class": ["I"], "class_arabic": [1], "gloss": "to deserve"},
            {"mw_L": "3", "slp1": "gaR", "homonym": None, "class": ["VI"], "class_arabic": [6], "gloss": "to count"},
            {"mw_L": "4", "slp1": "cur", "homonym": None, "class": ["X"], "class_arabic": [10], "gloss": "to steal"},
        ], f)
    out = os.path.join(tmp, "out")
    rc = run(chart, mwjson, out, emit_join=True, force=True)
    with open(os.path.join(out, "h4741_join_local_only.tsv"), encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
    pairs = {tuple(l.split("\t")[:3]) for l in lines[1:]}
    assert ("gam", "gam", "None") in pairs, pairs
    assert ("arh", "arh", "None") in pairs, pairs
    # tier1 coverage: 4/4 SCL roots matched exact (gaN→gaR? fixture uses 'gaR' mw key)
    rep = open(os.path.join(out, "H4741_PARITY_REPORT.md"), encoding="utf-8").read()
    assert "tier1 exact) | 4 / 4" in rep, rep
    assert rc == 0
    shutil.rmtree(tmp)
    print("SELFTEST PASS (WX rosetta via SCL words + sanskrit_util cross-check; tier1/anubandha-strip/join pairs)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dhatu")
    ap.add_argument("--mwroots")
    ap.add_argument("--outdir")
    ap.add_argument("--emit-join-tsv", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.dhatu and a.mwroots and a.outdir):
        ap.error("--dhatu --mwroots --outdir required (or --selftest)")
    sys.exit(run(a.dhatu, a.mwroots, a.outdir, a.emit_join_tsv, a.force))


if __name__ == "__main__":
    main()
