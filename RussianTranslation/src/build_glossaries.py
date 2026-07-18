#!/usr/bin/env python
"""Build pwg_ru corpus-gate SPECIALIST sources from SamudraManthanam's raw
name-glossary .txt files (Data/*.txt — NOT the corpus_builder/jsonl pipeline
that build_src.py reads; these never went through that extraction).

Each source is a printed dictionary's "index of names" appendix: Cyrillic
headword, TAB, then either "(IAST) — gloss" or a bare Russian gloss with no
IAST at all. Only sources with a parenthetical IAST form immediately after the
tab give a deterministic, ambiguity-free SLP1 join key (reusing build_src's
iast_to_slp1) — so only those are wired here. See README.md "SPECIALIST
sources" section for why the other four candidate glossaries (Бада Кадамбари,
Потапова, Эрман-Темкин: Cyrillic-only, no IAST -> transliteration would be
ambiguous, esp. dental/retroflex collapse -- risks silently wrong join keys in
what is a correctness-authority signal; Топоров: a page-number index, not a
gloss at all) are intentionally NOT wired.

Output: gitignored, like build_src.py's. Schema: {"source","slp1","iast","gloss"}.

Usage:  python build_glossaries.py [path-to-SamudraManthanam]
Output: grin12.jsonl grin3.jsonl
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from build_src import iast_to_slp1, bad_initial

DEFAULT_SM = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'SamudraManthanam'))
SM = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SM
DATA = os.path.join(SM, "Index", "lib", "x86_64-win64", "Data")
OUT = os.path.dirname(os.path.abspath(__file__))

# filename in SamudraManthanam/Data -> our gate code
SOURCES = [
    ("Словарь Гринцера из Рамаяны 1-2.txt", "grin12"),  # Гринцер, Рамаяна I-II (2006)
    ("Рамаяна 3. Словарь.txt",              "grin3"),   # Гринцер, Рамаяна III (2006)
]

_ENTRY = re.compile(r'^(\S.*?)[\t ]\(([^)]+)\)\s*(?:—|-)?\s*(.*)$')

def extract(fname, code):
    path = os.path.join(DATA, fname)
    out_path = os.path.join(OUT, code + ".jsonl")
    n_in = n_out = n_noiast = n_badkey = 0
    with open(path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8", newline="") as o:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if i == 0 or not line.strip():
                continue  # header comment line
            n_in += 1
            m = _ENTRY.match(line)
            if not m:
                n_noiast += 1
                continue
            _headword_ru, iast_paren, gloss = m.groups()
            # the parenthetical sometimes carries a literal gloss too, e.g.
            # "(Agnivarṇa — "[имеющий] цвет огня")" -- keep only the leading
            # IAST token for the key, fold any trailing text into the gloss.
            iast = iast_paren.split('—')[0].split('-')[0].strip()
            extra = iast_paren[len(iast):].lstrip('—- ').strip()
            if extra:
                gloss = (extra + ' ' + gloss).strip()
            # PWG's SLP1 keys are never proper-noun-capitalized (case there
            # encodes vowel length/retroflex only, e.g. 'A'=ā) -- lowercase
            # the IAST first so capitalized names (Śiva, Ūrmilā) convert.
            slp1 = iast_to_slp1(iast.lower())
            if not slp1 or bad_initial(slp1):
                n_badkey += 1
                continue
            o.write(json.dumps({"source": code, "slp1": slp1, "iast": iast,
                                "gloss": gloss}, ensure_ascii=False) + "\n")
            n_out += 1
    print(f"{code:8s} <- {fname:42s} in={n_in:4d} out={n_out:4d} "
          f"no-iast-paren={n_noiast} bad-key={n_badkey}")
    return n_out

if __name__ == "__main__":
    if not os.path.isdir(DATA):
        sys.exit(f"SamudraManthanam Data dir not found: {DATA}")
    total = sum(extract(fname, code) for fname, code in SOURCES)
    print(f"TOTAL keyed entries: {total}")
