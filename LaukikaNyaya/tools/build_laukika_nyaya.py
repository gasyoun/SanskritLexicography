# -*- coding: utf-8 -*-
"""
Build data/laukika_nyaya.jsonl from the raw archive.org OCR text of
Jacob's "Handful of Popular Maxims" (Laukika-nyaya), mirroring the
IndischeSprueche JSONL pattern.

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
HEADWORD_LINE = re.compile(r'^[ऀ-ॿ\s]{5,60}$')
NYAYA_WORD = re.compile(r'न्याय')
MAXIM_OPEN = re.compile(r'^The maxim of')
BOILERPLATE = re.compile(
    r'(Digitized [Bb]y .*(eGangotri|Gyaan Kosha|Arya Samaj).*'
    r'|CC-0\.?\s*Prof\.?\s*Satya Vrat Shastri Collection\.?)',
    re.I,
)
TITLE_FALSE_POSITIVES = {
    'लोकिकन्यायाञ्जलिः', 'लौकिकन्यायाञ्जलिः', 'ठोकिकन्यायाञ्ञलिः',
}

# Real section boundaries, found by grepping this OCR text for the
# Devanagari part-ordinal + English "N HANDFUL" title lines (`grep -n
# "तृतीयो\|THIRD HANDFUL\|हितीयो\|SECOND HANDFUL"`):
#   First Handful  (2nd ed., 1907): OCR lines   807 - 3548
#   Second Handful (1909):          OCR lines  3549 - 8664
#   Third Handful  (1911):          OCR lines  8665 - end
# The separately-uploaded standalone "Second Handful" archive.org item
# (qqlv_..., digitized by Arya Samaj Foundation Chennai) has UNUSABLE
# Devanagari OCR (0 recoverable headwords when run through this same
# pipeline); the standalone "Third Handful" item (ukZa_...) has badly
# garbled English OCR alongside partially-legible headwords. This bound-in
# combined copy is therefore the ONLY usable source for all three parts.
FRONT_MATTER_END = 750
PART2_START_LINE = 3549
PART3_START_LINE = 8665

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


def load_lines(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.readlines()


def clean_body(raw_lines):
    text = ' '.join(l.strip() for l in raw_lines if l.strip())
    text = BOILERPLATE.sub('', text)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # de-hyphenate line-wraps
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def find_headword_indices(lines, skip_before=0):
    """Two tiers of candidate headword line:
    - 'named': pure-Devanagari line containing the word न्याय (the common
      "X-nyaya" coined-compound headword style).
    - 'phrase': pure-Devanagari line WITHOUT न्याय, accepted only if
      immediately (within 3 lines) followed by the literal English opening
      "The maxim of ..." -- a stricter gate, since without the न्याय anchor
      a short Devanagari line is otherwise indistinguishable from a
      mid-explanation quote fragment.
    """
    idxs = []
    for i, line in enumerate(lines):
        if i < skip_before:
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


def is_true_headword(lines, idx):
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


def extract_entries(lines, start_after_idx=0):
    all_tagged = find_headword_indices(lines, skip_before=start_after_idx)
    tier_of = dict(all_tagged)
    all_idx = [i for i, _ in all_tagged]
    good_idx = []
    for idx in all_idx:
        raw = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        if raw in TITLE_FALSE_POSITIVES or 'न्यायाञ्जलि' in raw:
            continue  # running book/section title re-appearing at a part break
        if is_true_headword(lines, idx):
            good_idx.append(idx)

    entries = []
    for pos, idx in enumerate(good_idx):
        nxt = good_idx[pos + 1] if pos + 1 < len(good_idx) else min(idx + 400, len(lines))
        headword = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        body = clean_body(lines[idx + 1:nxt])
        gloss_match = re.match(r'^(The maxim of[^.]*\.)', body)
        entries.append({
            'nyaya_deva': headword,
            'gloss_en': gloss_match.group(1).strip() if gloss_match else None,
            'explanation': body[:4000],
            'tier': tier_of.get(idx, 'named'),
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
    }


def main():
    lines = load_lines(RAW_PATH)
    entries = extract_entries(lines, start_after_idx=FRONT_MATTER_END)
    part1 = [e for e in entries if e['_line'] < PART2_START_LINE]
    part2 = [e for e in entries if PART2_START_LINE <= e['_line'] < PART3_START_LINE]
    part3 = [e for e in entries if e['_line'] >= PART3_START_LINE]

    named = sum(1 for e in entries if e['tier'] == 'named')
    phrase = sum(1 for e in entries if e['tier'] == 'phrase')
    print(f"Part 1 (First Handful, 1907): {len(part1)} entries")
    print(f"Part 2 (Second Handful, 1909): {len(part2)} entries")
    print(f"Part 3 (Third Handful, 1911): {len(part3)} entries")
    print(f"TOTAL: {len(entries)} (named-tier: {named}, phrase-tier: {phrase})")

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
