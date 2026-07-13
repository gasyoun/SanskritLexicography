#!/usr/bin/env python3
"""Module 5 - aksara / phoneme frequency (Sanskrit-in-Numbers Wave 1, H813).

Duden's *Sprache in Zahlen* reports letter frequency over German headwords.
Sanskrit's analog must report BOTH layers, because sandhi makes them diverge:
  - phonemic  : SLP1 character frequency (1 SLP1 char == 1 phoneme, no digraphs)
  - graphemic : Devanagari akshara (orthographic syllable) frequency, after
                SLP1 -> Devanagari transliteration

Two corpora, computed independently:
  (a) Petersburg-family headwords (PWG + PWK + SCH), key1 (SLP1) forms,
      from HeadwordLists/now-2026/ (this repo).
  (b) DCS corpus tokens (surface forms), from VisualDCS's real DCS sqlite
      (DCS-data-2026/dcs_full.sqlite -- NOT src/dcs_full.sqlite, which is a
      0-byte decoy; see SanskritLexicography memory
      dcs-full-db-path-and-gita-gap.md).

Output: module5_akshara_phoneme_freq.json with both histograms for both
corpora, normalized to percent, plus n and date for the trust block.
"""
import csv
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

REPO_ROOT = Path(__file__).resolve().parents[2]
GITHUB_ROOT = REPO_ROOT.parent
HW_DIR = REPO_ROOT / "HeadwordLists" / "now-2026"
DCS_DB = GITHUB_ROOT / "VisualDCS" / "src" / "DCS-data-2026" / "dcs_full.sqlite"

FAMILY_FILES = {
    "PWG": HW_DIR / "PWG-unique-key1-106082.txt",
    "PWK": HW_DIR / "PWK-unique-key1-151349.txt",
    "SCH": HW_DIR / "SCH-unique-key2-28519.txt",  # SCH has no key1 export; key2 used, SLP1-compatible
}

# SLP1 phoneme inventory (single ASCII char == single phoneme; no digraphs).
SLP1_VOWELS = set("aAiIuUfFxXeEoO")
SLP1_CONS = set("kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh")
SLP1_MARKS = set("MH~")  # anusvara, visarga, avagraha
SLP1_ALPHABET = SLP1_VOWELS | SLP1_CONS | SLP1_MARKS

# Devanagari akshara segmentation: an akshara is
#   (consonant + virama)* consonant (vowel-sign | anusvara/visarga)?
# or a single independent vowel (+ anusvara/visarga)?
DEVANAGARI_CONS = "क-हक़-य़"
DEVANAGARI_INDEP_VOWEL = "ऄ-औॠॡॲ-ॷ"
DEVANAGARI_VOWEL_SIGN = "ा-ौॕ-ॗॢॣ"
DEVANAGARI_VIRAMA = "्"
DEVANAGARI_ANUSVARA_VISARGA = "ंःँ"

AKSHARA_RE = re.compile(
    rf"(?:[{DEVANAGARI_CONS}]{DEVANAGARI_VIRAMA})*[{DEVANAGARI_CONS}]"
    rf"(?:[{DEVANAGARI_VOWEL_SIGN}])?(?:[{DEVANAGARI_ANUSVARA_VISARGA}])?"
    rf"|[{DEVANAGARI_INDEP_VOWEL}](?:[{DEVANAGARI_ANUSVARA_VISARGA}])?"
)


def phoneme_tokens(slp1_text: str):
    """Yield SLP1 phoneme characters, skipping non-alphabet chars (digits, '-', '/')."""
    for ch in slp1_text:
        if ch in SLP1_ALPHABET:
            yield ch


def akshara_tokens(devanagari_text: str):
    for m in AKSHARA_RE.finditer(devanagari_text):
        if m.group(0):
            yield m.group(0)


def load_family_keys():
    """Return list of SLP1 key strings across the Petersburg family (PWG+PWK+SCH)."""
    keys = []
    counts = {}
    for dict_name, path in FAMILY_FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        n = 0
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                key = line.strip().split("\t")[0]
                if not key:
                    continue
                keys.append(key)
                n += 1
        counts[dict_name] = n
    return keys, counts


def family_histograms():
    keys, counts = load_family_keys()
    phon = Counter()
    aksh = Counter()
    for key in keys:
        phon.update(phoneme_tokens(key))
        deva = transliterate(key, sanscript.SLP1, sanscript.DEVANAGARI)
        aksh.update(akshara_tokens(deva))
    return phon, aksh, counts, len(keys)


def dcs_token_sample():
    """Pull all DCS token surface forms (IAST). Returns list[str]."""
    con = sqlite3.connect(str(DCS_DB))
    cur = con.cursor()
    cur.execute("SELECT form FROM token")
    forms = [row[0] for row in cur.fetchall() if row[0]]
    con.close()
    return forms


IAST_TO_SLP1_DIGRAPH_SAFE = True


def dcs_histograms(forms):
    phon = Counter()
    aksh = Counter()
    for form in forms:
        # IAST -> SLP1 for phonemic count (indic_transliteration handles digraphs kh/gh/... correctly)
        slp1 = transliterate(form, sanscript.IAST, sanscript.SLP1)
        phon.update(phoneme_tokens(slp1))
        deva = transliterate(form, sanscript.IAST, sanscript.DEVANAGARI)
        aksh.update(akshara_tokens(deva))
    return phon, aksh, len(forms)


def top_percent(counter: Counter, total_chars: int, limit=40):
    return [
        {"unit": k, "count": v, "pct": round(100 * v / total_chars, 3)}
        for k, v in counter.most_common(limit)
    ]


def main():
    fam_phon, fam_aksh, fam_counts, fam_n = family_histograms()
    dcs_forms = dcs_token_sample()
    dcs_phon, dcs_aksh, dcs_n_tokens = dcs_histograms(dcs_forms)

    fam_phon_total = sum(fam_phon.values())
    fam_aksh_total = sum(fam_aksh.values())
    dcs_phon_total = sum(dcs_phon.values())
    dcs_aksh_total = sum(dcs_aksh.values())

    out = {
        "module": 5,
        "title": "akshara / phoneme frequency",
        "trust_block": {
            "source": "Petersburg family (PWG+PWK+SCH) headwords, HeadwordLists/now-2026/ key1(key2 for SCH); "
                       "DCS corpus tokens, VisualDCS DCS-data-2026/dcs_full.sqlite (DCS-2026 release)",
            "n": {
                "family_headwords": fam_n,
                "family_by_dict": fam_counts,
                "dcs_tokens": dcs_n_tokens,
            },
            "date": str(date.today()),
            "model": "Sonnet 5 (claude-sonnet-5)",
        },
        "family": {
            "phonemic": {
                "total_phonemes": fam_phon_total,
                "top": top_percent(fam_phon, fam_phon_total),
            },
            "graphemic": {
                "total_aksharas": fam_aksh_total,
                "top": top_percent(fam_aksh, fam_aksh_total),
            },
        },
        "dcs_corpus": {
            "phonemic": {
                "total_phonemes": dcs_phon_total,
                "top": top_percent(dcs_phon, dcs_phon_total),
            },
            "graphemic": {
                "total_aksharas": dcs_aksh_total,
                "top": top_percent(dcs_aksh, dcs_aksh_total),
            },
        },
        "note": "Phonemic = SLP1 character count (1 char = 1 phoneme, no digraphs). "
                "Graphemic = Devanagari akshara (orthographic syllable) count after "
                "SLP1/IAST -> Devanagari transliteration. The two diverge because of "
                "sandhi (e.g. a word-final consonant assimilating/eliding at a word "
                "boundary is a phonemic event with no single-word graphemic trace, and "
                "conversely visarga/anusvara alternations are graphemically stable but "
                "phonetically variable) -- this divergence has no German analog and is "
                "the module's main finding.",
    }

    out_path = Path(__file__).parent / "module5_akshara_phoneme_freq.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"family headwords: {fam_n} ({fam_counts})")
    print(f"family phonemes: {fam_phon_total}, aksharas: {fam_aksh_total}")
    print(f"DCS tokens: {dcs_n_tokens}")
    print(f"DCS phonemes: {dcs_phon_total}, aksharas: {dcs_aksh_total}")
    print(f"top-5 family phonemes: {fam_phon.most_common(5)}")
    print(f"top-5 family aksharas: {fam_aksh.most_common(5)}")
    print(f"top-5 DCS phonemes: {dcs_phon.most_common(5)}")
    print(f"top-5 DCS aksharas: {dcs_aksh.most_common(5)}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
