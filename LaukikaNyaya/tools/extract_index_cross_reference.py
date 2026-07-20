# -*- coding: utf-8 -*-
"""
H803 follow-up (19-07-2026, continuation of the phrase-tier-recall-audit
follow-up): the clean-scan source (handfulofpopular03jacoiala) turns out to
HAVE a back-matter index after all -- README.md's "No back-matter index in
this source (unlike the 300-record lane)" claim only checked the literal
last ~6 pages; vol03 leaves 167-176 (9 pages before the true end at 186,
so genuinely missed by that check) carry an "ALPHABETICAL LIST OF NYAYAS
EXPLAINED IN PARTS I, II & III" -- a canonical cross-reference index
covering nyayas from ALL THREE volumes, not just vol03's own.

This script extracts that index, normalizes every Devanagari headword-like
token in it, and diffs against the currently-committed data/laukika_nyaya.jsonl
headwords to find genuinely explained nyayas the extraction pipeline missed.
Read-only / diagnostic.

Run:
    cd LaukikaNyaya/tools
    python extract_index_cross_reference.py
"""
import re
import sys
import json
import difflib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE.parent / "raw"
DATA_PATH = HERE.parent / "data" / "laukika_nyaya.jsonl"

DEVA_CHAR = re.compile(r'[ऀ-ॿ]')
PAGE_MARK = re.compile(r'^=== PAGE (\d+)(?: MISSING.*)?\s*===\s*$')
INDEX_START_LEAF = 169  # "LIST OF NYAYAS." title page
INDEX_END_LEAF = 176    # last leaf before "ERRATA." at leaf 177


def load_lines_with_leaf(path):
    lines, page_of = [], []
    cur = 0
    with open(path, encoding='utf-8') as f:
        for raw in f:
            s = raw.rstrip('\n')
            m = PAGE_MARK.match(s.strip())
            if m:
                cur = int(m.group(1))
                continue
            lines.append(s)
            page_of.append(cur)
    return lines, page_of


def skeleton(s):
    """Normalize a Devanagari headword-ish string for fuzzy comparison:
    keep only Devanagari letters (drop vowel signs/matras/anusvara/visarga
    to absorb common OCR consonant/vowel-sign confusion), collapse."""
    devanagari_only = ''.join(DEVA_CHAR.findall(s))
    # Strip common inflectional/OCR-noisy tail (न्यायः/न्याय/न्यायेन etc.)
    stripped = re.sub(r'न्याय[a-zऀ-ॿ]*$', '', devanagari_only)
    return stripped if len(stripped) >= 4 else devanagari_only


def extract_index_tokens():
    lines, page_of = load_lines_with_leaf(RAW_DIR / "handfulofpopular03jacoiala_ocr_san_eng.txt")
    tokens = []
    for i, line in enumerate(lines):
        leaf = page_of[i]
        if leaf < INDEX_START_LEAF or leaf > INDEX_END_LEAF:
            continue
        # Split into runs of Devanagari (a token = maximal run of Devanagari
        # letters + internal spaces immediately followed by non-Devanagari
        # marker text -- approximate by matching Devanagari-run then
        # capturing up to the next Devanagari-run start).
        for m in re.finditer(r'[ऀ-ॿ][ऀ-ॿ\s]{2,60}', line):
            tok = m.group(0).strip()
            tok = re.sub(r'\s+', ' ', tok)
            if len(DEVA_CHAR.findall(tok)) >= 5:
                tokens.append((leaf, tok))
    return tokens


def load_dataset_headwords():
    heads = []
    with open(DATA_PATH, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            heads.append(r.get('nyaya_deva', '') or '')
    return heads


def main():
    tokens = extract_index_tokens()
    print(f"Index tokens extracted (leaves {INDEX_START_LEAF}-{INDEX_END_LEAF}): {len(tokens)}")

    dataset_heads = load_dataset_headwords()
    dataset_skel = [skeleton(h) for h in dataset_heads]

    unmatched = []
    for leaf, tok in tokens:
        sk = skeleton(tok)
        if len(sk) < 4:
            continue
        best = max((difflib.SequenceMatcher(None, sk, ds).ratio() for ds in dataset_skel), default=0.0)
        if best < 0.72:
            unmatched.append((leaf, tok, best))

    print(f"Index tokens with no close match (ratio<0.72) in current {len(dataset_heads)}-record dataset: {len(unmatched)}")
    print()
    for leaf, tok, best in unmatched:
        print(f"leaf{leaf} best={best:.2f}  {tok!r}")


if __name__ == '__main__':
    main()
