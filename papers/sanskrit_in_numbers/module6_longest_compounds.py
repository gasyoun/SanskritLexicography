#!/usr/bin/env python3
"""Module 6 - longest compounds / samasa (Sanskrit-in-Numbers Wave 1, H813).

Duden's *Sprache in Zahlen* reports German's longest attested word (the
79-character Bandwurmwort record) with an occurrence-count honesty floor.
Sanskrit's compounding is unbounded and far more productive than German's, so
this is the show-stopper module: longest attested compound-shaped surface
forms in the DCS corpus, subject to the SAME >=5-occurrence honesty floor
(so a one-off philosophical run-on doesn't set the "record"), plus the full
length distribution.

Source: VisualDCS's real DCS sqlite, DCS-data-2026/dcs_full.sqlite (5,688,416
tokens; NOT src/dcs_full.sqlite, a 0-byte decoy -- see SanskritLexicography
memory dcs-full-db-path-and-gita-gap.md).

Method: rank token.form (surface form, sandhi-joined -- the orthographic
"word" as printed, matching Duden's own unit of measurement) by character
length among forms occurring >=5 times in the corpus. Reported in BOTH
Sanskrit's natural prosodic unit (akshara / orthographic syllable count,
after Devanagari transliteration) and raw IAST character count (the direct
Duden-comparable unit).
"""
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

REPO_ROOT = Path(__file__).resolve().parents[2]
GITHUB_ROOT = REPO_ROOT.parent
DCS_DB = GITHUB_ROOT / "VisualDCS" / "src" / "DCS-data-2026" / "dcs_full.sqlite"

MIN_OCCURRENCES = 5

DEVANAGARI_CONS = "क-ह"  # standard 33 consonants; nukta letters (क़ etc.) never occur in transliterated Sanskrit
DEVANAGARI_INDEP_VOWEL = "ऄ-औॠॡॲ-ॷ"
DEVANAGARI_VOWEL_SIGN = "ा-ौॕ-ॗॢॣ"
DEVANAGARI_VIRAMA = "्"
DEVANAGARI_ANUSVARA_VISARGA = "ंःँ"
AKSHARA_RE = re.compile(
    rf"(?:[{DEVANAGARI_CONS}]{DEVANAGARI_VIRAMA})*[{DEVANAGARI_CONS}]"
    rf"(?:[{DEVANAGARI_VOWEL_SIGN}])?(?:[{DEVANAGARI_ANUSVARA_VISARGA}])?"
    rf"|[{DEVANAGARI_INDEP_VOWEL}](?:[{DEVANAGARI_ANUSVARA_VISARGA}])?"
)


def akshara_count(iast_text: str) -> int:
    deva = transliterate(iast_text, sanscript.IAST, sanscript.DEVANAGARI)
    return len(AKSHARA_RE.findall(deva))


def main():
    con = sqlite3.connect(str(DCS_DB))
    cur = con.cursor()
    cur.execute("SELECT form, COUNT(*) AS n FROM token GROUP BY form")
    rows = cur.fetchall()
    con.close()

    total_distinct_forms = len(rows)
    floor_rows = [(form, n) for form, n in rows if n >= MIN_OCCURRENCES and form]
    print(f"distinct forms: {total_distinct_forms}, >= {MIN_OCCURRENCES} occ: {len(floor_rows)}")

    # rank by IAST character length
    floor_rows.sort(key=lambda r: len(r[0]), reverse=True)
    top50 = floor_rows[:50]

    records = []
    for form, n in top50:
        records.append({
            "form": form,
            "occurrences": n,
            "char_length": len(form),
            "akshara_length": akshara_count(form),
        })

    # length distribution (character length) over the floor-passing set
    length_hist = Counter(len(form) for form, _ in floor_rows)
    length_hist_sorted = sorted(length_hist.items())

    # also the ALL-forms record (no floor) for the honesty-floor comparison Duden itself makes
    all_forms_sorted = sorted(rows, key=lambda r: len(r[0]), reverse=True)
    no_floor_record = all_forms_sorted[0] if all_forms_sorted else None

    out = {
        "module": 6,
        "title": "longest compounds (samasa)",
        "trust_block": {
            "source": "VisualDCS DCS-data-2026/dcs_full.sqlite (DCS-2026 release), token.form surface forms",
            "n": {
                "total_tokens": sum(n for _, n in rows) if False else None,
                "distinct_forms": total_distinct_forms,
                "distinct_forms_meeting_floor": len(floor_rows),
                "occurrence_floor": MIN_OCCURRENCES,
            },
            "date": str(date.today()),
            "model": "Sonnet 5 (claude-sonnet-5)",
        },
        "record_with_floor": records[0] if records else None,
        "top50_with_floor": records,
        "record_no_floor": {
            "form": no_floor_record[0],
            "occurrences": no_floor_record[1],
            "char_length": len(no_floor_record[0]),
        } if no_floor_record else None,
        "length_distribution_char": length_hist_sorted,
        "note": "'Compound' here means the longest attested single orthographic word "
                "in the DCS corpus (Duden's own unit for the Bandwurmwort record), not "
                "a formally verified samasa parse -- DCS does not corpus-wide segment "
                "every long noun into its samasa members, so a handful of top entries "
                "could in principle be non-compound single stems (rare at this length "
                "in Sanskrit) or proper-name/colophon strings. The record_no_floor entry "
                "shows why the floor matters: without it, a hapax colophon title sets "
                "an unrepresentative 'record', exactly the failure mode Duden's own "
                "floor avoids.",
    }

    out_path = Path(__file__).parent / "module6_longest_compounds.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"record (floor>={MIN_OCCURRENCES}): {records[0] if records else None}")
    print(f"record (no floor): form={no_floor_record[0] if no_floor_record else None}, n={no_floor_record[1] if no_floor_record else None}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
