"""ACC (Aufrecht's Catalogus Catalogorum) parser -- P0 canonical extraction.

Per ROADMAP_ACC_NCC.md P0: parses csl-orig's acc.txt (Cologne <L>...<LEND>
records, SLP1 k1/k2 headwords) into acc.jsonl, one row per work entry, with a
sanskrit-util slp1_simplify match_key for the P1 fuzzy crosswalk to join
against NCC.

Record shape (acc.txt, see csl-orig v02/acc/acc-meta2.txt):
    <L>N<pc>PAGE-REF<k1>SLP1HEADWORD<k2>ORIGSPELLING
    body line(s) -- {#slp1#} inline devanagari refs, {%..%} italics,
    {@..@} bold, {??} unreadable, {{Lbody=N}} "see entry N" cross-ref,
    <HI1>/<P> line-break markers, [Page...] scan breaks
    <LEND>

Sigla extraction is a best-effort citation-shape heuristic (capitalized
abbreviation/name token(s) + a page/volume number), NOT an abbreviation-
resolved list -- no canonical ACC sigla table exists in the repo (checked
acc-meta2.txt), so resolving abbreviations to full collection names is out
of scope for P0 and would be fabricating precision we don't have.

Usage:
    python HeadwordLists/works_catalogue/parse_acc.py
    ACC_TXT=<path> python HeadwordLists/works_catalogue/parse_acc.py
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

ACC_TXT = os.environ.get(
    "ACC_TXT", r"C:/Users/user/Documents/GitHub/csl-orig/v02/acc/acc.txt")
OUT_PATH = os.path.join(HERE, "acc.jsonl")

HEADER_RE = re.compile(
    r'^<L>(?P<L>[\d.]+)<pc>(?P<pc>[^<]+)<k1>(?P<k1>[^<]+)<k2>(?P<k2>.*)$')
DEVA_SLP1_RE = re.compile(r'\{#(.*?)#\}')
ITALIC_RE = re.compile(r'\{%(.*?)%\}')
UNREADABLE_RE = re.compile(r'\{\?\?\}')
BOLD_RE = re.compile(r'\{@(.*?)@\}')
LBODY_RE = re.compile(r'\{\{Lbody=(\d+(?:\.\d+)?)\}\}')
PAGEBREAK_RE = re.compile(r'\[Page[^\]]*\]')
TAG_RE = re.compile(r'<[^>]+>')

# Citation-shape heuristic: Capitalized-token(s) + page/volume number(s),
# optionally with a scan column (^a/^b), a lowercase page-marker particle
# (p./pp./vol./no.), or comma-separated locants.
SIGLUM_RE = re.compile(
    r"([A-ZĀĪŪŚṢṬḌṆ][\w.'’-]*(?:\.\s+[A-ZĀĪŪŚṢṬḌṆ][\w.'’-]*)*)\s+"
    r"(?:(?:p{1,2}|vol|no)\.\s*)?"
    r"(\d+(?:\^[ab]\d*)?(?:,\s*\d+(?:\^[ab]\d*)?)*)"
)
PARENTHETICAL_RE = re.compile(r'\([^)]*\)')


def normalize_headword_for_matching(text):
    """Per ROADMAP_ACC_NCC.md P0: strip parentheticals + underscores before
    the match key (k1 is currently always a plain compound in acc.txt, but
    this mirrors parse_ncc.py's normalization so a future k1 with either
    doesn't silently produce a wrong key)."""
    text = PARENTHETICAL_RE.sub('', text)
    text = text.replace('_', '')
    return text


def clean_body(raw_text):
    """Render body markup to plain readable text (SLP1 inline refs -> IAST)."""
    text = LBODY_RE.sub('', raw_text)
    text = DEVA_SLP1_RE.sub(lambda m: su.from_slp1(m.group(1)), text)
    text = ITALIC_RE.sub(lambda m: m.group(1), text)
    text = BOLD_RE.sub(lambda m: m.group(1), text)
    text = UNREADABLE_RE.sub('[?]', text)
    text = PAGEBREAK_RE.sub('', text)
    text = TAG_RE.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.lstrip('¦').strip()  # leading BROKEN BAR separator
    return text


def extract_sigla(body_text):
    return [f"{m.group(1)} {m.group(2)}" for m in SIGLUM_RE.finditer(body_text)]


def parse_records(path):
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()

    records = []
    cur_header = None
    cur_body_lines = []
    warnings = 0

    for line in lines:
        if line.startswith('<L>'):
            cur_header = line
            cur_body_lines = []
        elif line.startswith('<LEND>'):
            if cur_header is None:
                continue
            m = HEADER_RE.match(cur_header)
            if not m:
                print(f"WARN: unparsed header: {cur_header!r}", file=sys.stderr)
                warnings += 1
                cur_header = None
                cur_body_lines = []
                continue
            raw_body = '\n'.join(cur_body_lines)
            lbody_m = LBODY_RE.search(raw_body)
            body = clean_body(raw_body)
            k1 = m.group('k1')
            records.append({
                'acc_L': m.group('L'),
                'pc_scan': m.group('pc'),
                'k1_slp1': k1,
                'k2': m.group('k2'),
                'body': body,
                'sigla': extract_sigla(body),
                'lbody_ref': lbody_m.group(1) if lbody_m else None,
                'match_key': su.slp1_simplify(normalize_headword_for_matching(k1)),
            })
            cur_header = None
            cur_body_lines = []
        else:
            if cur_header is not None:
                cur_body_lines.append(line)

    if warnings:
        print(f"ACC: {warnings} unparsed header line(s), see stderr", file=sys.stderr)
    return records


def main():
    records = parse_records(ACC_TXT)
    with open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    distinct_keys = len({r['match_key'] for r in records})
    print(f"ACC: {len(records)} records ({distinct_keys} distinct match-keys) -> {OUT_PATH}")


if __name__ == '__main__':
    main()
