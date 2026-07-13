#!/usr/bin/env python3
"""Module 9 - samasa types, best-effort (Sanskrit-in-Numbers Wave 1, H813).

Duden's *Sprache in Zahlen* reports German Fugenzeichen (linking-element)
types in compounds. Sanskrit's structural analog is samasa TYPE (tatpurusa /
bahuvrihi / dvandva / karmadharaya / avyayibhava ...), which the roadmap
flags explicitly as **best-effort** because full compound typing needs
semantic/syntactic segmentation, not markup -- there is no dictionary-markup
shortcut the way there is for gender or verb class.

This module reports what the DCS Universal-Dependencies-style treebank
ALREADY tags reliably, and is explicit about what it cannot distinguish:

  - `compound:coord` (UD "coordinating compound") IS a direct, corpus-native
    tag for dvandva (coordinate) compounds -- reliable, not a heuristic.
  - `compound:name` tags proper-name compounds (a distinct, smaller bucket).
  - plain `compound` covers everything else the treebank marks as an
    internal compound-member relation -- this bucket mixes tatpurusa,
    karmadharaya, AND bahuvrihi, because the UD scheme does not distinguish
    them. This script does NOT attempt to auto-classify that bucket by
    semantic guesswork (that would risk fabricating a typed number); instead
    it draws a small, explicitly-labeled illustrative sample for a human/future
    session to hand-read, and reports the honest undifferentiated count.

Source: VisualDCS DCS-data-2026/dcs_full.sqlite, token.deprel.
"""
import json
import random
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
GITHUB_ROOT = REPO_ROOT.parent
DCS_DB = GITHUB_ROOT / "VisualDCS" / "src" / "DCS-data-2026" / "dcs_full.sqlite"

COMPOUND_DEPRELS = ("compound", "compound:coord", "compound:name")


def main():
    con = sqlite3.connect(str(DCS_DB))
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM token")
    total_tokens = cur.fetchone()[0]

    counts = {}
    samples = {}
    for deprel in COMPOUND_DEPRELS:
        cur.execute("SELECT COUNT(*) FROM token WHERE deprel=?", (deprel,))
        counts[deprel] = cur.fetchone()[0]
        cur.execute(
            "SELECT form, lemma, upos, sentence_id, head FROM token WHERE deprel=?",
            (deprel,),
        )
        rows = cur.fetchall()
        random.seed(42)
        sample = random.sample(rows, min(15, len(rows)))
        samples[deprel] = [
            {"form": r[0], "lemma": r[1], "upos": r[2], "sentence_id": r[3], "head_id": r[4]}
            for r in sample
        ]

    con.close()

    n_total_compound_relations = sum(counts.values())

    out = {
        "module": 9,
        "title": "samasa types (best-effort)",
        "trust_block": {
            "source": "VisualDCS DCS-data-2026/dcs_full.sqlite (DCS-2026 release), "
                       "token.deprel Universal-Dependencies-style compound relations",
            "n": {
                "total_tokens": total_tokens,
                "total_compound_relations": n_total_compound_relations,
                **counts,
            },
            "date": str(date.today()),
            "model": "Sonnet 5 (claude-sonnet-5)",
        },
        "counts": counts,
        "pct_of_compound_relations": {
            k: round(100 * v / n_total_compound_relations, 2) for k, v in counts.items()
        },
        "reliable_typed_bucket": {
            "dvandva (compound:coord)": counts["compound:coord"],
            "proper-name compound (compound:name)": counts["compound:name"],
        },
        "undifferentiated_bucket": {
            "tatpurusa/karmadharaya/bahuvrihi, undifferentiated (compound)": counts["compound"],
        },
        "sample_for_manual_typing": samples,
        "note": "BEST-EFFORT, per roadmap ROADMAP_SANSKRIT_IN_NUMBERS_2026_2027.md Wave 1 "
                "module 9 spec. DCS's own UD-style `deprel` tagging gives a reliable, "
                "corpus-native dvandva count (compound:coord) and a proper-name-compound "
                "count (compound:name) -- these are NOT heuristic. The much larger "
                "remaining question -- tatpurusa vs karmadharaya vs bahuvrihi -- is "
                "NOT auto-classified here: the UD compound relation used by DCS does not "
                "carry that distinction, and guessing it algorithmically without a real "
                "semantic/syntactic samasa parser would risk reporting fabricated "
                "percentages. A random 15-item sample per bucket is included for a human "
                "or a future dedicated-segmentation pass (vidyut cheda + hand adjudication) "
                "to type; that full typing pass is flagged as a follow-up, not delivered "
                "here. Absolute scale caveat: only "
                f"{round(100 * n_total_compound_relations / total_tokens, 3)}% of all "
                "DCS tokens carry an explicit compound-member deprel at all -- most "
                "Sanskrit compounds in this corpus are NOT syntactically decomposed into "
                "member tokens (they remain single orthographic words, see Module 6); "
                "this module's counts describe the tagged MINORITY, not the full "
                "compound population.",
    }

    out_path = Path(__file__).parent / "module9_samasa_types.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"total tokens: {total_tokens}")
    print(f"compound relation counts: {counts}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
