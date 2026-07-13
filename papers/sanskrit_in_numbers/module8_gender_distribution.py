#!/usr/bin/env python3
"""Module 8 - gender distribution (Sanskrit-in-Numbers Wave 1, H813).

Duden's *Sprache in Zahlen* reports German gender shares (fem 46 / masc 34 /
neut 20) plus multi-gender headwords (der/die/das Joghurt). Sanskrit's analog:
m./f./n. shares over the Petersburg family, plus the multi-gender headword set
(m.n., m.f.n., m.f., f.n. -- words attested with more than one grammatical
gender across dictionary entries).

Source: the already-public zaliznyak-grammar-index dataset (A56, kosha
release data-v0.1.0) -- a per-headword classification of all 98,639 PWG
headwords into a lexical-category token (`lex` column), built for the
Zaliznyak-style paradigm-token retrofit. This module reuses that `lex` column
directly (per org convention: reuse a committed derived asset rather than
re-deriving gender from raw PWG markup from scratch). Anti-salami note: A56
itself is Module 7's owner (POS distribution) and is cited, not re-derived,
there -- Module 8 is a NEW module that draws on the SAME already-released
column for a different cut (gender, not POS), which is legitimate reuse, not
duplication of A56's own novelty (paradigm-token inventory).

This script downloads the release TSV on first run (cached locally,
gitignored) and computes the gender-share table.
"""
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
TSV_PATH = CACHE_DIR / "zaliznyak_grammar_index.tsv"
RELEASE_URL = "https://github.com/gasyoun/kosha/releases/tag/data-v0.1.0"

GENDER_MAP = {
    "m.": ("masculine", 1),
    "f.": ("feminine", 1),
    "n.": ("neuter", 1),
    "fem.": ("feminine", 1),  # spelling variant, folded
    "neutr.": ("neuter", 1),  # spelling variant, folded
    "m.n.": ("multi: m./n.", 2),
    "m.f.": ("multi: m./f.", 2),
    "f.n.": ("multi: f./n.", 2),
    "m.f.n.": ("multi: m./f./n. (tri-gender)", 3),
    "mm.": ("masculine", 1),  # "always-plural masculine" notation (index_token still m·N), folded to m.
    "ff.": ("feminine", 1),  # "always-plural feminine" notation (index_token still f·N; verified against source rows), folded to f.
}
NON_GENDERED = {"adj.", "adv.", "indecl.", "ind.", "interj."}


def ensure_tsv():
    if TSV_PATH.exists() and TSV_PATH.stat().st_size > 0:
        return
    subprocess.run(
        [
            "gh", "release", "download", "data-v0.1.0",
            "--repo", "gasyoun/kosha",
            "--dir", str(CACHE_DIR),
            "--pattern", "*.tsv",
            "--clobber",
        ],
        check=True,
    )


def main():
    ensure_tsv()

    lex_counts = Counter()
    with open(TSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)
    for row in rows:
        lex_counts[row["lex"]] += 1

    n_total = len(rows)
    gendered = Counter()
    multi_gender_rows = []
    non_gendered_n = 0
    unmapped = Counter()

    for row in rows:
        lex = row["lex"]
        if lex in GENDER_MAP:
            label, arity = GENDER_MAP[lex]
            gendered[label] += 1
            if arity > 1:
                multi_gender_rows.append(
                    {"k1": row["k1"], "hom": row["hom"], "lex": lex}
                )
        elif lex in NON_GENDERED:
            non_gendered_n += 1
        else:
            unmapped[lex] += 1

    n_gendered_simple = sum(
        v for k, v in gendered.items() if not k.startswith("multi")
    )
    n_multi = sum(v for k, v in gendered.items() if k.startswith("multi"))
    n_gendered_total = n_gendered_simple + n_multi

    simple_shares = {
        k: {"n": v, "pct": round(100 * v / n_gendered_simple, 2)}
        for k, v in gendered.items()
        if not k.startswith("multi")
    }

    out = {
        "module": 8,
        "title": "gender distribution",
        "trust_block": {
            "source": f"zaliznyak-grammar-index (A56, kosha release {RELEASE_URL}), "
                      "`lex` column over all PWG headwords",
            "n": n_total,
            "date": str(date.today()),
            "model": "Sonnet 5 (claude-sonnet-5)",
        },
        "gender_shares_simple_pct": simple_shares,
        "n_gendered_simple": n_gendered_simple,
        "n_multi_gender": n_multi,
        "multi_gender_breakdown": {
            k: v for k, v in gendered.items() if k.startswith("multi")
        },
        "n_non_gendered_categories": non_gendered_n,
        "n_unmapped_lex_values": dict(unmapped),
        "multi_gender_sample": multi_gender_rows[:30],
        "note": "Shares computed over gendered NOUN headwords only (m./f./n. and "
                "their multi-gender combinations); adj./adv./indecl./interj. are "
                "excluded from the percentage base since Sanskrit adjectives take "
                "the gender of the noun they modify rather than carrying a fixed "
                "dictionary gender -- the direct structural reason Sanskrit's "
                "'multi-gender' set is a distinct, much smaller class from German's "
                "(where any noun can in principle be multi-gender, e.g. der/die/das "
                "Joghurt): in Sanskrit the tri-gender class is dominated by adjectives "
                "used substantively, not ordinary nouns.",
    }

    out_path = Path(__file__).parent / "module8_gender_distribution.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"n_total rows: {n_total}")
    print(f"lex counts: {lex_counts.most_common(20)}")
    # lgtm[py/clear-text-logging-sensitive-data] -- false positive: "gender" here is
    # grammatical gender (PWG dictionary m./f./n. classification), not personal data.
    print(f"n_gendered_simple: {n_gendered_simple}, shares: {simple_shares}")  # lgtm[py/clear-text-logging-sensitive-data]
    print(f"n_multi_gender: {n_multi}, breakdown: {dict(gendered)}")  # lgtm[py/clear-text-logging-sensitive-data]
    print(f"unmapped: {dict(unmapped)}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
