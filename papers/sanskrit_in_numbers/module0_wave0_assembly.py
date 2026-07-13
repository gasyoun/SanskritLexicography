#!/usr/bin/env python3
"""Wave 0 assembly (Sanskrit-in-Numbers, H813): pull the already-OWNED modules
(2, 7, 1, partial 3/4) into one data table, and build the Zipf coverage curve
that Module 3/4 lacked ("100 words ~ 1/2 of text", Duden's own framing).

Anti-salami: modules 2 and 7 are CITED here, never recomputed -- this script
only filters the already-published union_headwords.tsv down to the
Petersburg-family subset (a read, not a re-derivation) and reads off already-
published totals from A40/A55/A56/VisualDCS. The Zipf coverage curve IS new
computation (module 3/4 was flagged "partial" in the roadmap, not owned), but
uses only the ALREADY-committed VisualDCS DCS-2026 corpus (real lemma
frequencies from token.lemma_id joins, not the coarse frequency BANDS in
dcs_lemma_summary.json, which are too coarse for a coverage curve).
"""
import csv
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
GITHUB_ROOT = REPO_ROOT.parent
UNION_TSV = REPO_ROOT / "HeadwordLists" / "union" / "union_headwords.tsv"
DCS_DB = GITHUB_ROOT / "VisualDCS" / "src" / "DCS-data-2026" / "dcs_full.sqlite"

FAMILY = {"PWG", "PWK", "SCH"}


def family_union():
    """Filter the already-published 15-dict union down to the Petersburg
    family (PWG+PWK+SCH), reading dict-membership per headword. This is a
    read/filter of already-published data (A40/A55), not a re-derivation."""
    n_family_union = 0
    n_all_three = 0
    n_pwg = n_pwk = n_sch = 0
    with open(UNION_TSV, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            dicts = set(row["dicts"].split())
            fam_dicts = dicts & FAMILY
            if fam_dicts:
                n_family_union += 1
                if fam_dicts == FAMILY:
                    n_all_three += 1
                if "PWG" in fam_dicts:
                    n_pwg += 1
                if "PWK" in fam_dicts:
                    n_pwk += 1
                if "SCH" in fam_dicts:
                    n_sch += 1
    return {
        "family_union_dedup": n_family_union,
        "in_all_three": n_all_three,
        "pwg_rows": n_pwg,
        "pwk_rows": n_pwk,
        "sch_rows": n_sch,
        "naive_sum": n_pwg + n_pwk + n_sch,
    }


def zipf_coverage_curve():
    """Real lemma-frequency Zipf coverage curve from DCS-2026: what % of all
    tokens do the top-N lemmas cover. Uses exact counts from token.lemma_id,
    not dcs_lemma_summary.json's coarse freqBand (1..5), which cannot support
    a precise coverage curve."""
    con = sqlite3.connect(str(DCS_DB))
    cur = con.cursor()
    cur.execute(
        "SELECT lemma, COUNT(*) AS n FROM token WHERE lemma IS NOT NULL "
        "AND lemma != '' GROUP BY lemma ORDER BY n DESC"
    )
    rows = cur.fetchall()
    con.close()

    total_tokens = sum(n for _, n in rows)
    n_distinct_lemmas = len(rows)

    checkpoints = [1, 10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    curve = []
    running = 0
    idx = 0
    for cp in checkpoints:
        while idx < cp and idx < len(rows):
            running += rows[idx][1]
            idx += 1
        curve.append({
            "top_n": cp,
            "cumulative_tokens": running,
            "pct_of_corpus": round(100 * running / total_tokens, 2),
        })

    top20 = [{"lemma": l, "n": n, "pct": round(100 * n / total_tokens, 3)} for l, n in rows[:20]]

    return {
        "total_tokens": total_tokens,
        "n_distinct_lemmas": n_distinct_lemmas,
        "coverage_curve": curve,
        "top20_lemmas": top20,
    }


def main():
    fam = family_union()
    zipf = zipf_coverage_curve()

    out = {
        "wave": 0,
        "generated": str(date.today()),
        "model": "Sonnet 5 (claude-sonnet-5)",
        "modules_owned": {
            "module_2_vocabulary_size": {
                "owner": "A40 (headword census) + A55 (union index, kosha)",
                "source": [
                    "papers/A40_headword_inventory_note.md",
                    "https://github.com/gasyoun/kosha/blob/main/papers/A55_UNION_HEADWORDS_DATA_PAPER_JOHD.md",
                    "data/HEADWORD_OVERLAP_UNION15_2026.md",
                ],
                "headline_n": {
                    "full_15_dict_union": 323425,
                    "petersburg_family_union_dedup": fam["family_union_dedup"],
                    "petersburg_family_naive_sum": fam["naive_sum"],
                    "petersburg_family_double_count_inflation_pct": round(
                        100 * (fam["naive_sum"] - fam["family_union_dedup"]) / fam["family_union_dedup"], 1
                    ),
                    "in_all_three_pwg_pwk_sch": fam["in_all_three"],
                    "pwg_headwords": fam["pwg_rows"],
                    "pwk_headwords": fam["pwk_rows"],
                    "sch_headwords": fam["sch_rows"],
                },
                "caveat": "PWK abridges PWG, PW abridges further, SCH is addenda -- naive "
                          "summing double-counts massively (D2/D6 caveat, roadmap SS2). "
                          "The honest 'vocabulary size' number is the de-duplicated union, "
                          "computed here by filtering the already-published 15-dict union "
                          "(union_headwords.tsv) to the family, NOT recomputed from scratch.",
            },
            "module_7_pos_distribution": {
                "owner": "A56 (Zaliznyak grammar-token index, kosha)",
                "source": "https://github.com/gasyoun/kosha/blob/main/papers/A56_ZALIZNYAK_GRAMMAR_INDEX_DATA_PAPER_JOHD.md",
                "headline_n": {"headwords_classified": 98639, "paradigm_tokens": 335},
                "caveat": "Cited, not recomputed here.",
            },
            "module_1_lemma_vs_token": {
                "owner": "VisualDCS (DCS-2026 release)",
                "source": "https://github.com/gasyoun/VisualDCS",
                "headline_n": {
                    "texts": 270,
                    "tokens": zipf["total_tokens"],
                    "sentences": 754726,
                    "distinct_lemmas_attested": zipf["n_distinct_lemmas"],
                },
            },
            "module_3_4_frequency_and_zipf": {
                "owner": "VisualDCS (DCS-2026 release); coverage curve NEW this wave",
                "source": "VisualDCS/src/DCS-data-2026/dcs_full.sqlite (real per-token lemma "
                          "counts, not the coarse freqBand in dcs_lemma_summary.json)",
                "coverage_curve": zipf["coverage_curve"],
                "top20_lemmas": zipf["top20_lemmas"],
                "caveat": "Duden's own headline stat is '100 words cover ~half the text'; "
                          "DCS's top-100 lemmas cover "
                          f"{next(c['pct_of_corpus'] for c in zipf['coverage_curve'] if c['top_n']==100)}% "
                          "of tokens -- see the curve for the full comparison. Scale caveat: "
                          "DCS (5.7M tokens) is ~1000x smaller than the Dudenkorpus (5.2B); "
                          "corpus-unattested does not mean non-existent (A40 caveat).",
            },
        },
        "anti_salami_note": "This file CITES modules 2 and 7 (A40/A55/A56 own their novelty); "
                             "it does not re-derive their headline results. The family-union "
                             "figure above is a FILTER of already-published per-headword "
                             "dict-membership data, not a new census. The Zipf coverage curve "
                             "is genuinely new (module 3/4 was 'partial' in the roadmap), "
                             "computed once here from the already-committed DCS-2026 corpus.",
    }

    out_path = Path(__file__).parent / "module0_wave0_owned_modules.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"family union dedup: {fam}")
    print(f"zipf total_tokens: {zipf['total_tokens']}, distinct lemmas: {zipf['n_distinct_lemmas']}")
    print(f"coverage curve: {zipf['coverage_curve']}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
