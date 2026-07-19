# -*- coding: utf-8 -*-
"""
Build data/laukika_nyaya.jsonl v2 -- adds an INDEX-CROSS-REFERENCED recovery
pass on top of the original v1 (headword-regex-only) extraction.

Same source as v1: ../raw/jacob_1907-1911_archiveorg_djvu.txt (archive.org
item YKTn_..., binds all 3 of Jacob's "handfuls" 1907/1909/1911).

NEW in v2: the OCR text's own back-matter "ALPHABETICAL LIST OF NYAYAS
EXPLAINED IN EACH PART" (~458 entries, OCR lines ~16518-17206) is used as an
authoritative cross-check to recover headword occurrences in the body that
the v1 strict regex missed because of stray OCR noise around an otherwise-
legible headword line (e.g. a misread danda rendered as a stray Latin
letter). This is NOT synthesis: every recovered record's headword and
explanation are still taken VERBATIM from the same committed raw OCR body
text as v1 -- the index is used only to decide WHERE to look, never to
supply content. Two match strategies, both index-gated:
  1. seqmatch  -- difflib.SequenceMatcher ratio >=0.75 between the index
     entry's cleaned Devanagari and a body candidate line's cleaned
     Devanagari (catches "named" nyaya-suffixed headwords with edge noise).
  2. prefix    -- exact 8-codepoint Devanagari-prefix match (catches
     "phrase"-type headwords, which are the maxim's own opening words and
     too long/variable for a whole-line ratio match to work well).
Both strategies additionally require: the candidate is not itself sitting
inside a citation ("as follows:", "namely", "same class as", "same
purport", "it appears as" -- these mark a headword-shaped Devanagari
fragment quoted INSIDE a different entry's explanation, not a fresh
heading), and the immediately preceding non-empty line is not itself heavy
Devanagari prose (which would mean the candidate sits mid-verse-quotation).

Run:
    cd LaukikaNyaya/tools
    python build_laukika_nyaya.py
"""
import re
import sys
import json
import difflib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]  # .../SanskritLexicography
RAW_PATH = HERE.parent / "raw" / "jacob_1907-1911_archiveorg_djvu.txt"
OUT_PATH = HERE.parent / "data" / "laukika_nyaya.jsonl"
SANSKRIT_UTIL_PATH = REPO_ROOT.parent / "sanskrit-util" / "py"

sys.path.insert(0, str(SANSKRIT_UTIL_PATH))
try:
    from sanskrit_util import deva_to_iast, deva_to_slp1  # noqa: E402
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        f"Could not import sanskrit_util from {SANSKRIT_UTIL_PATH} -- "
        f"clone/update the sibling sanskrit-lexicon/sanskrit-util repo "
        f"next to this one. ({exc})"
    )

DEVA_CHAR = re.compile(r'[ऀ-ॿ]')
DEVA_ONLY = re.compile(r'[^ऀ-ॿ]')
HEADWORD_LINE = re.compile(r'^[ऀ-ॿ\s]{5,60}$')
NYAYA_WORD = re.compile(r'न्याय')
MAXIM_OPEN = re.compile(r'^The maxim of')
BOILER_LINE = re.compile(
    r'Digitized|Gyaan Kosha|CC-0|Prof\.? Satya Vrat|eGangotri', re.I
)
TITLE_FALSE_POSITIVES = {
    'लोकिकन्यायाञ्जलिः', 'लौकिकन्यायाञ्जलिः', 'ठोकिकन्यायाञ्ञलिः',
}
CITATION_MARKERS = re.compile(
    r'as follows\s*[:—-]|namely|same class as|same purport|'
    r'it appears as|the following passage',
    re.I,
)

# Real section boundaries (unchanged from v1; see README for how these were
# found -- grep for the Devanagari part-ordinal + English "N HANDFUL" lines):
# Found by DIRECT VISUAL spot-check against the archive.org page scan
# (leaf 300, printed page ~183): OCR line 14614 ("य एव करोति स एव x ॥") IS a
# genuine headword (confirmed on the scan), but the printed page's own OCR
# for its explanation paragraph came out as near-total noise (single stray
# characters) for ~20 lines, AND the following entry's own heading line
# ("यत्करभस्य पृष्ठे...") OCR'd with its first word replaced by Latin noise
# ("Hawa"), so no headword boundary could be found there either -- the
# result is an explanation window that mixes garbage with a chunk of the
# NEXT entry's content (about a camel's back, not this entry's actual
# "reaps what he sows" topic). Excluded rather than shipped with
# misattributed content; see README "Known limitations".
EXCLUDED_LINES = {14614}

FRONT_MATTER_END = 750
PART2_START_LINE = 3549
PART3_START_LINE = 8665
# NEW in v2: the back-matter "ALPHABETICAL LIST OF NYAYAS" index + errata +
# publisher's ad pages start here -- must be excluded from body extraction
# (these are index/errata/ad lines, not fresh headword+explanation pairs).
INDEX_START = 16495
INDEX_END = 17207

PART_SOURCE = {
    1: "Jacob, A Handful of Popular Maxims, 2nd ed., Bombay (Tukaram Javaji / "
       "Nirnaya-Sagara Press), 1907 (First Handful)",
    2: "Jacob, A Second Handful of Popular Maxims, Bombay (Nirnaya-Sagara "
       "Press), 1909 (Second Handful)",
    3: "Jacob, A Third Handful of Popular Maxims (Laukika-nyayanjali), Bombay "
       "(Nirnaya-Sagara Press), 1911 (Third Handful)",
}


def deva_ratio(s):
    if not s:
        return 0.0
    return len(DEVA_CHAR.findall(s)) / len(s)


def clean_deva(s):
    """Devanagari LETTERS only -- strips danda, ZWNJ, digits, Latin, spaces.
    Used purely for fuzzy matching, never for the shipped headword text."""
    return DEVA_ONLY.sub('', s).replace('‌', '').replace('।', '').replace('॥', '')


def load_lines(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return [l.rstrip('\n') for l in f]


def format_headword(raw_line):
    """Shipped-headword text: Devanagari + internal whitespace preserved
    (collapsed to single spaces), danda stripped. Unlike clean_deva() (used
    only for matching), this keeps word boundaries -- important for
    phrase-tier headwords, which are multi-word verse-openings, not single
    coined compounds; collapsing them into one run-on token would lose
    real information even though every character is still genuine OCR
    text."""
    s = re.sub(r'[^ऀ-ॿ\s]', '', raw_line.strip())
    s = s.replace('।', ' ').replace('॥', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def clean_body(raw_lines):
    # Bug fix (found during v2 spot-check, H803 resume): the v1 BOILERPLATE
    # regex's trailing `.*` is unanchored, so when applied to the whole
    # JOINED explanation string it doesn't just remove one digitization-
    # credit line -- it greedily eats EVERYTHING from the first "Digitized
    # By ... eGangotri/Gyaan Kosha/Arya Samaj" match to the end of the
    # string, silently truncating (sometimes to nothing) any explanation
    # whose OCR window happens to contain one of these lines mid-body
    # (common -- the digitizer stamped credit lines every page or two
    # throughout the source). Stripping boilerplate PER LINE, before
    # joining, is bounded by construction and fixes this for both the
    # original headword-regex entries and the new index-crossref ones.
    kept = [l.strip() for l in raw_lines if l.strip() and not BOILER_LINE.search(l)]
    text = ' '.join(kept)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # de-hyphenate line-wraps
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------------------------------------------------------------- v1 pass --

def find_headword_indices_v1(lines, skip_before, stop_at):
    """Original strict-regex pass (unchanged logic from v1)."""
    idxs = []
    for i, line in enumerate(lines):
        if i < skip_before or i >= stop_at:
            continue
        s = line.strip()
        if not s or not HEADWORD_LINE.match(s):
            continue
        if NYAYA_WORD.search(s):
            idxs.append((i, 'named'))
        else:
            j, checked, hit = i + 1, 0, False
            while j < len(lines) and checked < 3:
                t = lines[j].strip()
                if t:
                    checked += 1
                    if MAXIM_OPEN.match(t):
                        hit = True
                    break
                j += 1
            if hit:
                idxs.append((i, 'phrase'))
    return idxs


def is_true_headword_v1(lines, idx):
    j, seen = idx - 1, 0
    while j >= 0 and seen < 2:
        s = lines[j].strip()
        if s:
            seen += 1
            if deva_ratio(s) > 0.5 and len(s) > 15:
                return False
            break
        j -= 1
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j < len(lines):
        nxt_s = lines[j].strip()
        if HEADWORD_LINE.match(nxt_s) and NYAYA_WORD.search(nxt_s):
            return False
    k, checked = idx + 1, 0
    while k < min(len(lines), idx + 8) and checked < 8:
        s = lines[k].strip()
        if s:
            checked += 1
            if len(re.findall(r'[A-Za-z]', s)) >= 8:
                return True
        k += 1
    return False


# ---------------------------------------------------------- v2 index pass --

def parse_index(lines):
    entries = []
    for i in range(INDEX_START + 23, min(INDEX_END, len(lines))):
        # (+23 skips the "ALPHABETICAL LIST ... " heading block down to the
        #  real "LIST OF NYAYAS." + first entries, found by inspection)
        s = lines[i].strip()
        if not s or BOILER_LINE.search(s):
            continue
        if DEVA_CHAR.search(s):
            c = clean_deva(s)
            if len(c) >= 3:
                entries.append((i, s, c))
    return entries


def prev_is_prose(lines, idx):
    """True if the nearest preceding non-empty line is itself heavy
    Devanagari prose (candidate likely sits mid-verse-quotation, not at a
    fresh heading)."""
    j, seen = idx - 1, 0
    while j >= 0 and seen < 2:
        s = lines[j].strip()
        if s:
            seen += 1
            return deva_ratio(s) > 0.5 and len(s) > 15
        j -= 1
    return False


CURLY_OPEN_QUOTE = re.compile(r'^[“‘]')


def sits_inside_citation(lines, idx):
    """True if the candidate's OWN line, or the 1-2 preceding non-empty
    lines, carry an English citation-introducing phrase ('as follows:',
    'namely', ...) -- meaning this Devanagari line is quoted INSIDE
    another entry's explanation, not a fresh heading of its own. Also
    rejects a candidate whose own line opens with a curly quotation mark
    (Jacob's OCR consistently uses a curly open-quote to set off a quoted
    verse citation; a plain straight quote/backtick before an otherwise
    clean headword is common OCR noise, not a real citation marker, and is
    intentionally NOT rejected here)."""
    own = lines[idx].strip()
    if CITATION_MARKERS.search(own) or CURLY_OPEN_QUOTE.match(own):
        return True
    j, seen = idx - 1, 0
    while j >= 0 and seen < 2:
        s = lines[j].strip()
        if s:
            seen += 1
            if CITATION_MARKERS.search(s):
                return True
        j -= 1
    return False


def build_body_candidates(lines, min_ratio, max_len):
    cands = []
    for i in range(FRONT_MATTER_END, INDEX_START):
        raw = lines[i].strip()
        if not raw or len(raw) > max_len:
            continue
        deva_n = len(DEVA_CHAR.findall(raw))
        if deva_n == 0:
            continue
        non_ws = re.sub(r'\s', '', raw)
        if not non_ws:
            continue
        if deva_n / len(non_ws) < min_ratio:
            continue
        c = clean_deva(raw)
        if len(c) < 3:
            continue
        cands.append((i, raw, c))
    return cands


def index_crossref_pass(lines, already_used_lines):
    """Returns a dict {line_idx: method} of NEW body headword occurrences
    recovered via cross-reference against the book's own back-matter
    index, not already present in already_used_lines."""
    index_entries = parse_index(lines)
    used = set(already_used_lines)
    recovered = {}

    # Strategy 1: whole-line fuzzy match (named-type, edge-noise tolerant).
    seq_candidates = build_body_candidates(lines, min_ratio=0.75, max_len=55)
    remaining_index = []
    for idx_i, idx_raw, idx_clean in index_entries:
        best, best_score = None, 0.0
        for cand_i, cand_raw, cand_clean in seq_candidates:
            if cand_i in used:
                continue
            if abs(len(cand_clean) - len(idx_clean)) > max(4, len(idx_clean) * 0.4):
                continue
            s = difflib.SequenceMatcher(None, idx_clean, cand_clean).ratio()
            if s > best_score:
                best_score, best = s, cand_i
        matched_this = False
        if best is not None and best_score >= 0.75:
            if not prev_is_prose(lines, best) and not sits_inside_citation(lines, best):
                used.add(best)
                recovered[best] = 'index-crossref-seqmatch'
                matched_this = True
        if not matched_this:
            remaining_index.append((idx_i, idx_raw, idx_clean))

    # Strategy 2: 8-codepoint Devanagari-prefix match (phrase-type headwords
    # -- the maxim's own opening words, too long/variable for ratio match).
    prefix_candidates = build_body_candidates(lines, min_ratio=0.5, max_len=90)
    PREFIX_LEN = 8
    for idx_i, idx_raw, idx_clean in remaining_index:
        if len(idx_clean) < PREFIX_LEN:
            continue
        prefix = idx_clean[:PREFIX_LEN]
        for cand_i, cand_raw, cand_clean in prefix_candidates:
            if cand_i in used:
                continue
            if cand_clean[:PREFIX_LEN] != prefix:
                continue
            if prev_is_prose(lines, cand_i) or sits_inside_citation(lines, cand_i):
                continue
            used.add(cand_i)
            recovered[cand_i] = 'index-crossref-prefix'
            break

    return recovered


# --------------------------------------------------------------- extract --

def extract_entries(lines):
    v1_tagged = find_headword_indices_v1(lines, FRONT_MATTER_END, INDEX_START)
    tier_of = {}
    method_of = {}
    good_idx = []
    for idx, tier in v1_tagged:
        raw = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        if raw in TITLE_FALSE_POSITIVES or 'न्यायाञ्जलि' in raw:
            continue
        if is_true_headword_v1(lines, idx):
            good_idx.append(idx)
            tier_of[idx] = tier
            method_of[idx] = 'headword-regex'

    recovered = index_crossref_pass(lines, good_idx)
    for idx, method in recovered.items():
        good_idx.append(idx)
        method_of[idx] = method
        tier_of[idx] = 'named' if NYAYA_WORD.search(lines[idx]) else 'phrase'

    good_idx = sorted(set(good_idx) - EXCLUDED_LINES)

    entries = []
    for pos, idx in enumerate(good_idx):
        nxt = good_idx[pos + 1] if pos + 1 < len(good_idx) else min(idx + 400, len(lines))
        headword = format_headword(lines[idx])
        body = clean_body(lines[idx + 1:nxt])
        gloss_match = re.match(r'^(The maxim of[^.]*\.)', body)
        entries.append({
            'nyaya_deva': headword,
            'gloss_en': gloss_match.group(1).strip() if gloss_match else None,
            'explanation': body[:4000],
            'tier': tier_of.get(idx, 'named'),
            '_method': method_of.get(idx, 'headword-regex'),
            '_line': idx,
        })
    return entries


def to_record(e, num, source_full):
    deva = e['nyaya_deva']
    try:
        iast = deva_to_iast(deva)
    except Exception:
        iast = None
    try:
        slp1 = deva_to_slp1(deva)
    except Exception:
        slp1 = None
    return {
        'num': num,
        'nyaya_deva': deva,
        'nyaya_iast': iast,
        'nyaya_slp1': slp1,
        'gloss_en': e['gloss_en'],
        'explanation': e['explanation'],
        'source': source_full,
        '_ocr_line': e['_line'],
        '_headword_tier': e['tier'],
        '_match_method': e['_method'],
    }


def main():
    lines = load_lines(RAW_PATH)
    entries = extract_entries(lines)
    part1 = [e for e in entries if e['_line'] < PART2_START_LINE]
    part2 = [e for e in entries if PART2_START_LINE <= e['_line'] < PART3_START_LINE]
    part3 = [e for e in entries if e['_line'] >= PART3_START_LINE]

    named = sum(1 for e in entries if e['tier'] == 'named')
    phrase = sum(1 for e in entries if e['tier'] == 'phrase')
    by_method = {}
    for e in entries:
        by_method[e['_method']] = by_method.get(e['_method'], 0) + 1
    print(f"Part 1 (First Handful, 1907): {len(part1)} entries")
    print(f"Part 2 (Second Handful, 1909): {len(part2)} entries")
    print(f"Part 3 (Third Handful, 1911): {len(part3)} entries")
    print(f"TOTAL: {len(entries)} (named-tier: {named}, phrase-tier: {phrase})")
    print("By recovery method:", by_method)

    records, n = [], 1
    for part_num, part_entries in ((1, part1), (2, part2), (3, part3)):
        for e in part_entries:
            records.append(to_record(e, n, PART_SOURCE[part_num]))
            n += 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as out:
        for r in records:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"Wrote {len(records)} records -> {OUT_PATH}")


if __name__ == '__main__':
    main()
