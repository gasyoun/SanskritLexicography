"""NCC (New Catalogus Catalogorum) parser -- P0 canonical extraction.

Per ROADMAP_ACC_NCC.md P0: parses VisualDCS's
SktNewCatalogus_Catalogorum_combined.txt (5-column TSV: devanagari, IAST,
structured ID `vol_page_col_seq`, numeric ID, HTML `<p>` body) into
ncc.jsonl, one row per work entry, with a sanskrit-util slp1_simplify
match_key (via IAST -> to_slp1) for the P1 fuzzy crosswalk against ACC.

Body text embeds line breaks as a literal two-character `\\n` sequence
(verified: every physical line in the source has exactly 4 tab separators,
so no record spans more than one physical line) -- kept as-is in the raw
`body_html` field, only unescaped for the sigla/mss-witness extraction pass.

`sigla` / `mss_witnesses` are both citation-shape heuristics over the body
text (same "Capitalized-abbrev(s) + number" shape as parse_acc.py), NOT
resolved against Skt_ncc_abbr.txt -- that table maps abbreviation -> full
term (e.g. "jy." -> "Jyotisa"), a different axis from the manuscript/library
sigla found here (e.g. "MD. 4397", "Rice 28"), so this P0 pass keeps them
as raw citation strings rather than fabricating a resolved-abbreviation
mapping the table doesn't actually provide for library sigla.

Usage:
    python HeadwordLists/works_catalogue/parse_ncc.py
    NCC_TXT=<path> python HeadwordLists/works_catalogue/parse_ncc.py
"""
import sys
import os
import re
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY", r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su  # noqa: E402

NCC_TXT = os.environ.get(
    "NCC_TXT",
    r"C:/Users/user/Documents/GitHub/VisualDCS/non-derived/NCC/files/src/SktNewCatalogus_Catalogorum_combined.txt")
OUT_PATH = os.path.join(HERE, "ncc.jsonl")

TAG_RE = re.compile(r'<[^>]+>')
LITERAL_NEWLINE_RE = re.compile(r'\\n')

# Same citation-shape heuristic as parse_acc.py: Capitalized-token(s) +
# optional lowercase page-marker particle + number(s).
SIGLUM_RE = re.compile(
    r"([A-ZĀĪŪŚṢṬḌṆ][\w.'’-]*(?:\.\s+[A-ZĀĪŪŚṢṬḌṆ][\w.'’-]*)*)\s+"
    r"(?:(?:p{1,2}|vol|no)\.\s*)?"
    r"(\d+(?:\^[ab]\d*)?(?:,\s*\d+(?:\^[ab]\d*)?)*)"
)
# Manuscript-witness shape: abbreviation immediately followed by an
# accession-style number (no intervening prose word) -- a subset of the
# broader `sigla` matches, e.g. "MD. 4397", "TCD. 627", "IO. 3183".
MSS_WITNESS_RE = re.compile(
    r"([A-ZĀĪŪŚṢṬḌṆ][A-Za-zĀĪŪŚṢṬḌṆāīū]*\.)\s+(\d+[A-Za-z]?)"
)


def clean_body(raw_html):
    text = LITERAL_NEWLINE_RE.sub(' ', raw_html)
    text = TAG_RE.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


PARENTHETICAL_RE = re.compile(r'\([^)]*\)')


def normalize_headword_for_matching(text):
    """Per ROADMAP_ACC_NCC.md P0: strip parentheticals + underscores before
    transliteration (NCC headwords carry variant-spelling parentheticals like
    "Aṃśanāḍīphala(keralīya)" and underscore-joined multi-word titles like
    "Aṃśādīni_Induphalāni" that ACC's single-compound-word k1 never has)."""
    text = PARENTHETICAL_RE.sub('', text)
    text = text.replace('_', '')
    return text


def match_key_for(iast):
    slp1 = su.to_slp1(normalize_headword_for_matching(iast))
    return su.slp1_simplify(slp1)


def parse_records(path):
    records = []
    bad_lines = 0
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, start=1):
            line = line.rstrip('\n')
            if not line:
                continue
            cols = line.split('\t')
            if len(cols) != 5:
                print(f"WARN: line {lineno} has {len(cols)} columns, expected 5", file=sys.stderr)
                bad_lines += 1
                continue
            deva, iast, structured_id, numeric_id, body_html = cols
            clean = clean_body(body_html)
            records.append({
                'ncc_id': structured_id,
                'ncc_numid': numeric_id,
                'deva': deva,
                'iast': iast,
                'body_html': body_html,
                'sigla': extract_sigla(clean),
                'mss_witnesses': extract_mss_witnesses(clean),
                'match_key': match_key_for(iast),
            })
    if bad_lines:
        print(f"NCC: {bad_lines} malformed line(s), see stderr", file=sys.stderr)
    return records


def extract_sigla(clean_text):
    return [f"{m.group(1)} {m.group(2)}" for m in SIGLUM_RE.finditer(clean_text)]


def extract_mss_witnesses(clean_text):
    return [f"{m.group(1)} {m.group(2)}" for m in MSS_WITNESS_RE.finditer(clean_text)]


def main():
    records = parse_records(NCC_TXT)
    with open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    distinct_keys = len({r['match_key'] for r in records})
    print(f"NCC: {len(records)} records ({distinct_keys} distinct match-keys) -> {OUT_PATH}")


if __name__ == '__main__':
    main()
