# -*- coding: utf-8 -*-
"""
Build data/laukika_nyaya.jsonl v3 -- combines BOTH independent H803
follow-up techniques that were developed concurrently and merged/rebased
separately (PR #577 and PR #576), and supersedes a subsequent manual
reconciliation (PR #587, "dual-run-salvage") that turned out to have real
defects -- see "19-07-2026 dedup + false-positive correction" in README.md
for the full account. This script is the single, deterministic source of
truth: `python build_laukika_nyaya.py` reproduces `data/laukika_nyaya.jsonl`
exactly, with no manual/hand-merge step.

  1. Broadened phrase-tier gloss-opener gate (ex-PR #577): the strict
     literal "The maxim of" gate found only 4/199 non-nyaya candidates.
     looks_like_gloss_sentence() generalizes it to any real English topic
     sentence, raising phrase-tier recall to 93 (151->240 total).
  2. Index-cross-referenced recovery pass (ex-PR #576): the OCR text's own
     back-matter "ALPHABETICAL LIST OF NYAYAS EXPLAINED IN EACH PART"
     (~458 entries) is used as an authoritative cross-check to recover
     headword occurrences the regex pass still misses because of stray
     OCR noise around an otherwise-legible line. The index only decides
     WHERE to look -- every recovered record's headword/explanation text
     is still taken verbatim from the same raw OCR body as everything
     else; nothing is synthesized. Run AFTER the broadened regex pass and
     told which lines it already used, so it only ever recovers genuinely
     new lines (this is what PR #587's manual union got wrong -- see
     README "correction" section: PR #576's own index-crossref pass only
     knew about ITS OWN pre-#577 v1-narrow used-set, not the later
     broadened-phrase-tier lines, so it re-discovered some of #577's own
     +89 phrase-tier entries under different whitespace formatting,
     producing same-`_ocr_line` duplicate pairs once both lanes were
     unioned).
  3. Prefix-match candidate-length cap (H803 combine-pass QA finding): an
     initial unbounded port of #576's 8-codepoint-prefix strategy
     recovers many candidates, but a length-vs-recovery-method audit
     (`_match_method` exists specifically to make this auditable) shows
     the vast majority of long ones (>25 codepoints) are false positives
     -- mid-explanation citation fragments, multi-nyaya list-summary
     lines, or verse quotations sharing an 8-char Devanagari prefix with
     an unrelated index entry, not fresh headwords (a genuine headword is
     short by construction, matching the regex tier's own 9-55 char
     range). Capped at 30 codepoints rather than shipping the long
     false positives.

Also carries forward a genuine bug fix found during the #576 pass (H803
resume): the original BOILERPLATE regex's trailing `.*` is unanchored, so
applied to the whole joined explanation string it doesn't remove just one
digitization-credit line -- it greedily eats everything from the first
match to the end of the string, silently truncating any explanation whose
OCR window happens to contain a mid-body credit stamp (common -- the
digitizer stamped credit lines every page or two). Filtering boilerplate
PER LINE before joining is bounded by construction and fixes this for
every entry, old and newly recovered alike.

Source: ../raw/jacob_1907-1911_archiveorg_djvu.txt -- the plain-text OCR
derivative of archive.org identifier
YKTn_a-handful-of-popular-maxims-vol-1-collected-by-colonel-g-a-jacob-1907-tukaram-javaji-bombay
("A Handful Of Popular Maxims Vol 1 ... 1907 - Tukaram Javaji Bombay",
digitized by Siddhanta eGangotri Gyaan Kosha, CC-0). Despite the "Vol 1"
label, this single scan binds ALL THREE of Jacob's "handfuls" (1907/1909/
1911) back to back under one consistent, comparatively good-quality
Devanagari+English OCR pass -- see the section-boundary constants below.

Genuine, non-fabricated extraction: every field is derived mechanically
from this actual downloaded OCR text. OCR noise is expected and is NOT
silently "corrected" into invented content -- only light, mechanical
cleanup (de-hyphenation, stripping repeated digitization-credit
boilerplate lines, whitespace collapse) is applied. See README.md
"Known limitations / OCR fidelity" for the residual error rate found by
manual spot-check.

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
# Bounded, per-line boilerplate test (bug fix carried from the #576 pass --
# see module docstring). Matches a line CONTAINING boilerplate anywhere, so
# the whole (short) credit line is dropped rather than truncating the body.
BOILER_LINE = re.compile(
    r'Digitized|Gyaan Kosha|CC-0|Prof\.? Satya Vrat|eGangotri', re.I
)
# A line is a boilerplate-ONLY line (used by the headword-candidate scan to
# skip a credit line without counting it as "checked", not to truncate body
# text).
BOILERPLATE_LINE = re.compile(
    r'^\s*(Digitized [Bb]y .*(eGangotri|Gyaan Kosha|Arya Samaj).*'
    r'|;?\s*CC-0\.?\s*Prof\.?\s*Satya Vrat Shastri Collection\.?)\s*$',
    re.I,
)
# Broader phrase-tier gloss-opener test (ex-PR #577, H803 follow-up #3): the
# strict literal "The maxim of" gate found only 4/199 non-nyaya candidates.
# Manual read of all 113 candidates that survive is_true_headword_v1() (see
# H803 handoff + README "Known limitations" for the audit) showed the true
# positives are ordinary English topic sentences of many shapes ("Like a
# decoration...", "A young fawn cannot...", "If Mithila should be...") while
# the false positives (Sanskrit couplet restatements, OCR-garbled fragments,
# boilerplate) either have NO English sentence following at all, or fail one
# of these three cheap checks.
NON_GLOSS_OPEN = re.compile(
    r'^(See |Cf\.|Professor .*(rendering|translat)|Prof\. )', re.I,
)
TITLE_FALSE_POSITIVES = {
    'लोकिकन्यायाञ्जलिः', 'लौकिकन्यायाञ्जलिः', 'ठोकिकन्यायाञ्ञलिः',
}
# Citation-introducing phrases (ex-PR #576): mark a headword-shaped
# Devanagari fragment as QUOTED INSIDE a different entry's explanation,
# not a fresh heading of its own -- used only by the index-crossref pass,
# which (unlike the regex pass) has no "next line is English gloss" signal
# to lean on.
CITATION_MARKERS = re.compile(
    r'as follows\s*[:—-]|namely|same class as|same purport|'
    r'it appears as|the following passage',
    re.I,
)
CURLY_OPEN_QUOTE = re.compile(r'^[“‘]')
# A verse-final danda/double-danda (।/॥) as the LAST substantive content on
# a line -- only trailing OCR noise (quotes, digits, a parenthetical page
# ref, whitespace; no further Devanagari) may follow it. Used by
# prev_is_prose() (H803 follow-up fix) to tell "this heavy-Devanagari
# previous line is a DIFFERENT entry's own verse closing cleanly" (not
# mid-citation) apart from "still inside an ongoing quotation" (no danda,
# or one followed by more Devanagari prose).
VERSE_CLOSE_TAIL = re.compile(r'[।॥][^ऀ-ॿ]*$')

# Real section boundaries, found by grepping this OCR text for the
# Devanagari part-ordinal + English "N HANDFUL" title lines (`grep -n
# "तृतीयो\|THIRD HANDFUL\|हितीयो\|SECOND HANDFUL"`):
#   First Handful  (2nd ed., 1907): OCR lines   807 - 3548
#   Second Handful (1909):          OCR lines  3549 - 8664
#   Third Handful (1911):           OCR lines  8665 - end
# The separately-uploaded standalone "Second Handful" archive.org item
# (qqlv_..., digitized by Arya Samaj Foundation Chennai) has UNUSABLE
# Devanagari OCR (0 recoverable headwords when run through this same
# pipeline); the standalone "Third Handful" item (ukZa_...) has badly
# garbled English OCR alongside partially-legible headwords. This bound-in
# combined copy is therefore the ONLY usable source for all three parts.
FRONT_MATTER_END = 750
PART2_START_LINE = 3549
PART3_START_LINE = 8665
# The back-matter "ALPHABETICAL LIST OF NYAYAS" index + errata + publisher's
# ad pages start here (ex-PR #576) -- must be excluded from body extraction
# (these are index/errata/ad lines, not fresh headword+explanation pairs).
INDEX_START = 16495
INDEX_END = 17207
# Confirmed by direct visual spot-check against the archive.org page scan
# (leaf 300, printed page ~183, ex-PR #576): OCR line 14614 IS a genuine
# headword, but its explanation paragraph's own OCR came out as near-total
# noise for ~20 lines, AND the following entry's own heading line OCR'd with
# its first word replaced by Latin noise, so no clean boundary could be
# found either side -- the resulting window mixes garbage with a chunk of
# the NEXT entry's unrelated content. Excluded rather than shipped with
# misattributed content; see README "Known limitations".
EXCLUDED_LINES = {14614}

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
    coined compounds; collapsing them into one run-on token would lose real
    information even though every character is still genuine OCR text.
    Applied uniformly to EVERY entry (not just index-crossref recoveries) so
    the two lanes can never again diverge on whitespace and produce a
    same-`_ocr_line` duplicate pair under different formatting (H803
    dedup-correction finding)."""
    s = re.sub(r'[^ऀ-ॿ\s]', '', raw_line.strip())
    s = s.replace('।', ' ').replace('॥', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def looks_like_gloss_sentence(s):
    """A candidate 'first English line after a phrase-tier headword' must:
    look like real running English prose, not a citation/fragment/boilerplate.
    """
    if not s or BOILERPLATE_LINE.match(s) or NON_GLOSS_OPEN.match(s):
        return False
    if deva_ratio(s) > 0.15:
        return False  # still mostly Devanagari -- a couplet, not a gloss
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", s)
    if len(words) < 4:
        return False  # e.g. "Who git", "T. Lon" -- OCR fragments
    return bool(re.match(r"^[\"'“‘`\[(]*[A-Z]", s))


def clean_body(raw_lines):
    # Bug fix (found during the #576 pass, H803 resume): the original
    # BOILERPLATE regex's trailing `.*` is unanchored, so when applied to
    # the whole JOINED explanation string it doesn't just remove one
    # digitization-credit line -- it greedily eats EVERYTHING from the
    # first "Digitized By ... eGangotri/Gyaan Kosha/Arya Samaj" match to the
    # end of the string, silently truncating (sometimes to nothing) any
    # explanation whose OCR window happens to contain one of these lines
    # mid-body (common -- the digitizer stamped credit lines every page or
    # two throughout the source). Stripping boilerplate PER LINE, before
    # joining, is bounded by construction and fixes this for every entry.
    kept = [l.strip() for l in raw_lines if l.strip() and not BOILER_LINE.search(l)]
    text = ' '.join(kept)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # de-hyphenate line-wraps
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# --------------------------------------------------------- v1 regex pass --

def find_headword_indices_v1(lines, skip_before, stop_at):
    """Two tiers of candidate headword line, scanned only across the body
    (before the back-matter index -- stop_at excludes it):
    - 'named': pure-Devanagari line containing the word न्याय (the common
      "X-nyaya" coined-compound headword style).
    - 'phrase': pure-Devanagari line WITHOUT न्याय, accepted only if the
      first non-blank, non-boilerplate line after it (looked at within 4
      lines) passes looks_like_gloss_sentence() -- broadened phrase-tier
      gate, see its docstring.
    """
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
            while j < len(lines) and checked < 4:
                t = lines[j].strip()
                if not t:
                    j += 1
                    continue
                if BOILERPLATE_LINE.match(t):
                    j += 1
                    continue  # skip digitization credit, don't count it
                checked += 1
                if looks_like_gloss_sentence(t):
                    hit = True
                break
            if hit:
                idxs.append((i, 'phrase'))
    return idxs


def is_true_headword_v1(lines, idx):
    """Reject false positives: (a) previous non-empty line is itself
    substantial Devanagari prose (inside a quoted passage); (b) next
    non-empty line is ITSELF a headword-pattern line (a quoted shloka
    couplet citing the nyaya, not a fresh heading). Require the gloss
    sentence to appear (English letters) within a handful of lines."""
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


# ---------------------------------------------------- v2 index-crossref --

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
    Devanagari prose AND does not itself close with a verse-final
    danda/double-danda (।/॥) -- candidate likely sits mid-verse-quotation,
    not at a fresh heading. A heavy-Devanagari previous line that DOES
    close with a danda (trailing OCR noise -- quotes, digits, a
    parenthetical page ref -- tolerated after it) marks a DIFFERENT
    entry's own explanation ending cleanly; the candidate right after it
    is an ordinary fresh heading, not a continuation, and must not be
    rejected (H803 follow-up fix, root-caused 20-07-2026 -- see README.md
    "Follow-up" #2: this heuristic previously conflated 'sits mid-citation'
    with 'immediately follows a different entry's own closing verse',
    losing genuine headwords like कारणगुणप्रक्रमन्यायः at OCR line 4885)."""
    j, seen = idx - 1, 0
    while j >= 0 and seen < 2:
        s = lines[j].strip()
        if s:
            seen += 1
            if not (deva_ratio(s) > 0.5 and len(s) > 15):
                return False
            return not VERSE_CLOSE_TAIL.search(s)
        j -= 1
    return False


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
    index, not already present in already_used_lines (the current, already
    broadened, v1-pass result -- so this only ever recovers entries the
    regex pass, even with the phrase-tier broadening, still cannot match).
    Passing the CURRENT (already-broadened) good_idx, not an old/narrow
    snapshot of it, is what prevents the same-`_ocr_line` duplicate class
    found in the PR #587 manual union (see module docstring)."""
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
    # max_len=30 (H803 combine-pass QA, not in the original #576 draft):
    # an initial max_len=90 pass recovered 48 candidates, but a length-vs-
    # method audit + manual spot-check showed the 40/48 over 25 codepoints
    # were false positives -- mid-explanation citation lines, multi-nyaya
    # list summaries, or verse quotations that happen to share an 8-char
    # Devanagari prefix with an unrelated index entry, not fresh headwords
    # (a genuine coined-compound or phrase-opener headword is short by
    # construction, matching the regex-tier's own 9-55 char range). Only
    # the <=25-char candidates read as real on inspection, so the cap is
    # tightened to 30 (small margin over the observed genuine max) rather
    # than shipping the long false positives.
    prefix_candidates = build_body_candidates(lines, min_ratio=0.5, max_len=30)
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
            continue  # running book/section title re-appearing at a part break
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
        gloss_match = re.match(r'^([A-Z"\'“‘`\[(][^.]*\.)', body)
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
