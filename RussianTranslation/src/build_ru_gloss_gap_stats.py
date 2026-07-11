#!/usr/bin/env python
r"""H685 — corpus_lexicon RU-gloss statistics: per-dict coverage, hapax rate, gap-list.

Reads the live aligned corpus (src/corpus_lexicon.jsonl) plus the three glossary
layers (surface = derived here from the live corpus; lemma + root = the committed
rollups in the sibling gasyoun/SanskritRussian repo) and answers the
DATA_LAYERS_CENSUS.md §3 questions for this asset:

  1. per-dict coverage % — which Cologne dictionary headwords (HeadwordLists/
     now-2026 key1 lists, SLP1) have >=1 corpus-attested RU gloss in any layer;
  2. hapax rate — surface keys attested exactly once in the corpus;
  3. the "keys with no RU gloss" gap-list — dictionary headwords with no RU gloss
     in any layer, ranked by DCS corpus frequency (src/dcs_freq.json, IAST ->
     SLP1), so the top of the list = highest-value targets for the next
     translation window.

It also re-runs the resolution-tier token-coverage measurement (DCS -> +Vidyut ->
+marker) against the LIVE corpus so the glossary README's 79.1 / 86.6 / 87.1 %
figures can be reconciled with the current row count.

Outputs (paths relative to RussianTranslation/):
  glossary/ru_gloss_gaps.tsv        the full gap-list (gitignored via glossary/*.tsv)
  glossary/ru_gloss_gap_stats.json  small committed stats snapshot (tables source)

Only key1 dictionaries are joined (key1 = the normalized computational key; key2
keeps print accents/marks that never match SLP1 joins). Key2-only dictionaries
(BHS, BUR, CAE, CCS, INM, MD, SCH) are out of scope here.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent          # RussianTranslation/src
RT_DIR = SRC_DIR.parent                            # RussianTranslation
GITHUB_DIR = RT_DIR.parent.parent                  # GitHub/

MARKER_SPLIT = re.compile(r"[+-]")


def norm_key(k: str) -> str:
    """Join-key normalization used across the glossary pipeline."""
    return k.lstrip("'’")


def load_tsv_col(path: Path, col: int = 0, skip_header: bool = True) -> set:
    out = set()
    with path.open(encoding="utf-8") as fh:
        if skip_header:
            next(fh, None)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > col and parts[col]:
                out.add(norm_key(parts[col]))
    return out


def load_tsv_pairs(path: Path, kcol: int = 0, vcol: int = 1) -> dict:
    out = {}
    with path.open(encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > max(kcol, vcol):
                out.setdefault(norm_key(parts[kcol]), parts[vcol])
    return out


def load_jsonl_keys(path: Path, field: str) -> set:
    out = set()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.add(norm_key(json.loads(line)[field]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", type=Path, default=SRC_DIR / "corpus_lexicon.jsonl")
    ap.add_argument("--sanskrit-russian", type=Path,
                    default=GITHUB_DIR / "SanskritRussian")
    ap.add_argument("--headword-dir", type=Path,
                    default=GITHUB_DIR / "SanskritLexicography" / "HeadwordLists" / "now-2026")
    ap.add_argument("--dcs-freq", type=Path, default=SRC_DIR / "dcs_freq.json")
    ap.add_argument("--out-dir", type=Path, default=RT_DIR / "glossary")
    args = ap.parse_args()

    sr = args.sanskrit_russian

    # --- resolution maps (for the README token-coverage reconciliation) -------
    dcs_form2lemma = load_tsv_pairs(sr / "dcs_form2lemma.tsv")
    vidyut_form2lemma = load_tsv_pairs(sr / "vidyut_form2lemma.tsv")
    known_lemmas = set(dcs_form2lemma.values()) | set(vidyut_form2lemma.values())
    known_lemmas |= load_tsv_col(sr / "dcs_lemma2root.tsv", col=1)

    # --- glossary layers with RU glosses --------------------------------------
    lemma_keys = load_jsonl_keys(sr / "lemma_glossary.jsonl", "lemma_slp1")
    root_keys = load_jsonl_keys(sr / "root_glossary.jsonl", "root_slp1")

    # --- stream the live corpus ------------------------------------------------
    key_count = Counter()          # per normalized surface key: total rows
    key_ru_count = Counter()       # per key: rows with a nonempty RU gloss
    kinds = Counter()
    rows = rows_empty_ru = 0
    tok_dcs = tok_vidyut = tok_marker = 0
    with args.corpus.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            rows += 1
            key = norm_key(rec["slp1"])
            key_count[key] += 1
            kinds[rec.get("kind", "?")] += 1
            if rec.get("ru", "").strip():
                key_ru_count[key] += 1
            else:
                rows_empty_ru += 1
            # resolution tiers, mirroring build_rollup_glossaries.py
            if key in dcs_form2lemma:
                tok_dcs += 1
            elif key in vidyut_form2lemma:
                tok_vidyut += 1
            elif "+" in key or "-" in key:
                joined = key.replace("+", "").replace("-", "")
                tail = MARKER_SPLIT.split(key)[-1]
                if (joined in dcs_form2lemma or joined in vidyut_form2lemma
                        or tail in known_lemmas):
                    tok_marker += 1

    surface_ru_keys = {k for k, n in key_ru_count.items() if n > 0}
    glossed_any = surface_ru_keys | lemma_keys | root_keys
    hapax = sum(1 for n in key_count.values() if n == 1)
    distinct = len(key_count)

    # --- DCS frequency, transcoded IAST -> SLP1 -------------------------------
    from indic_transliteration import sanscript
    dcs_freq_slp1 = {}
    dcs_meta = {}
    if args.dcs_freq.exists():
        freq = json.loads(args.dcs_freq.read_text(encoding="utf-8"))
        dcs_meta = freq.get("meta", {})
        for lemma_iast, rec in freq.get("by_lemma", {}).items():
            slp1 = sanscript.transliterate(lemma_iast, sanscript.IAST, sanscript.SLP1)
            prev = dcs_freq_slp1.get(slp1)
            if prev is None or rec["count"] > prev["count"]:
                dcs_freq_slp1[slp1] = rec

    # --- per-dict coverage ------------------------------------------------------
    dict_files = sorted(args.headword_dir.glob("*-unique-key1-*.txt"))
    per_dict = {}
    gap_membership = {}            # gap key -> [dict codes]
    for path in dict_files:
        code = path.name.split("-")[0]
        raw = path.read_text(encoding="utf-8-sig").splitlines()
        heads = {norm_key(h.strip()) for h in raw if h.strip()}
        m_surface = len(heads & surface_ru_keys)
        m_lemma = len(heads & lemma_keys)
        m_root = len(heads & root_keys)
        matched_any = heads & glossed_any
        for h in heads - glossed_any:
            gap_membership.setdefault(h, []).append(code)
        per_dict[code] = {
            "headwords": len(heads),
            "surface": m_surface,
            "lemma": m_lemma,
            "root": m_root,
            "any": len(matched_any),
            "any_pct": round(100.0 * len(matched_any) / len(heads), 2),
        }

    # --- gap-list ranked by DCS frequency --------------------------------------
    def rank(item):
        rec = dcs_freq_slp1.get(item[0])
        return (-(rec["count"] if rec else 0), item[0])

    gaps = sorted(gap_membership.items(), key=rank)
    gaps_in_dcs = sum(1 for k, _ in gaps if k in dcs_freq_slp1)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    gap_path = args.out_dir / "ru_gloss_gaps.tsv"
    with gap_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("key_slp1\tdicts\tdcs_count\tdcs_band\n")
        for key, codes in gaps:
            rec = dcs_freq_slp1.get(key)
            fh.write(f"{key}\t{','.join(codes)}\t"
                     f"{rec['count'] if rec else 0}\t{rec['band'] if rec else 0}\n")

    stats = {
        "corpus_rows": rows,
        "corpus_distinct_keys": distinct,
        "rows_empty_ru": rows_empty_ru,
        "kinds": dict(kinds),
        "hapax_keys": hapax,
        "hapax_rate_pct": round(100.0 * hapax / distinct, 2),
        "surface_keys_with_ru": len(surface_ru_keys),
        "lemma_layer_keys": len(lemma_keys),
        "root_layer_keys": len(root_keys),
        "token_coverage_pct": {
            "dcs_only": round(100.0 * tok_dcs / rows, 2),
            "plus_vidyut": round(100.0 * (tok_dcs + tok_vidyut) / rows, 2),
            "plus_marker": round(100.0 * (tok_dcs + tok_vidyut + tok_marker) / rows, 2),
        },
        "dcs_freq_lemmas_slp1": len(dcs_freq_slp1),
        "dcs_freq_meta": {k: dcs_meta.get(k) for k in ("source", "total_tokens", "distinct_lemmas")},
        "per_dict_coverage": per_dict,
        "gap_keys_total": len(gaps),
        "gap_keys_in_dcs": gaps_in_dcs,
        "gap_list_file": str(gap_path.relative_to(RT_DIR)).replace("\\", "/"),
        "gap_head_top20": [
            {"key": k, "dicts": c, "dcs_count": dcs_freq_slp1[k]["count"]}
            for k, c in gaps[:20] if k in dcs_freq_slp1
        ],
    }
    stats_path = args.out_dir / "ru_gloss_gap_stats.json"
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
