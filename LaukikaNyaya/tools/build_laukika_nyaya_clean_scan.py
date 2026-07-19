# -*- coding: utf-8 -*-
"""
Extracts entries from the clean-scan raw OCR text (fetch_clean_scan_ocr.py's
output: raw/handfulofpopular01/02/03jacoiala_ocr_san_eng.txt) with REAL
per-entry printed-page citations, as an alternative/supplement to
build_laukika_nyaya.py (which mines the garbled-Devanagari bound-combined
YKTn_... scan and can only cite at edition/part level).

Writes data/laukika_nyaya_clean_scan.jsonl -- a separate file, NOT
data/laukika_nyaya.jsonl. The committed data/laukika_nyaya.jsonl is a
manual reconciliation of THREE independent extraction lanes (see
README.md "Three-lane reconciliation, 19-07-2026"), not directly
reproducible by any single script invocation -- same caveat as the
existing lane-1/lane-2 union already carried.

Requires the sibling sanskrit-lexicon/sanskrit-util repo next to this one
(GitHub/sanskrit-util/py).

Run:
    cd LaukikaNyaya/tools
    python build_laukika_nyaya_clean_scan.py
"""
import re
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
RAW_DIR = HERE.parent / "raw"
OUT_PATH = HERE.parent / "data" / "laukika_nyaya_clean_scan.jsonl"
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
# ‌/‍ (ZWNJ/ZWJ, U+200C/U+200D) are legitimate Devanagari-adjacent control
# chars Tesseract emits around conjuncts -- outside the ऀ-ॿ block but not
# "impurity"; excluding them from the headword-line pattern silently drops
# real entries (found by spot-check: 'अकाले कृतमकृतं स्यात्‌ ॥' at
# vol03 p13 was invisible-broken until this was added).
HEADWORD_LINE = re.compile(r'^[ऀ-ॿ‌‍\s]{5,60}$')
NYAYA_WORD = re.compile(r'न्याय')
NON_GLOSS_OPEN = re.compile(r'^(See |Cf\.|Professor .*(rendering|translat)|Prof\. )', re.I)
PAGE_MARK = re.compile(r'^=== PAGE (\d+)(?: MISSING.*)?\s*===\s*$')
TITLE_FALSE_POSITIVE_SUBSTRINGS = ('न्यायाञ्जलि', 'न्यायाज्ज', 'न्यायाञ्ज')

# Printed-page = scan-leaf-index - offset, calibrated by reading the
# printed page number off spot-checked page images (each volume's own
# front matter -- title page, preface, errata -- pushes the offset up by a
# fixed amount; not verified page-by-page, so treat as accurate to within
# +/-1 near part boundaries / inserted errata leaves).
VOL_META = {
    '01': {'offset': 18, 'part_name': 'First Handful',
           'cite': "Jacob, A Handful of Popular Maxims, Bombay (Tukaram Javaji), "
                   "1907 (First Handful), UC Libraries scan, p. {p}"},
    '02': {'offset': 12, 'part_name': 'Second Handful',
           'cite': "Jacob, A Second Handful of Popular Maxims, Bombay "
                   "(Nirnaya-Sagara Press), 1909 (Second Handful), UC Libraries scan, p. {p}"},
    '03': {'offset': 12, 'part_name': 'Third Handful',
           'cite': "Jacob, A Third Handful of Popular Maxims (Laukikanyayanjali), "
                   "Bombay (Nirnaya-Sagara Press), 1911 (Third Handful), UC Libraries scan, p. {p}"},
}
VOL_IDS = {'01': 'handfulofpopular01jacoiala', '02': 'handfulofpopular02jacoiala',
           '03': 'handfulofpopular03jacoiala'}


def deva_ratio(s):
    if not s:
        return 0.0
    return len(DEVA_CHAR.findall(s)) / len(s)


def looks_like_gloss_sentence(s):
    if not s or NON_GLOSS_OPEN.match(s):
        return False
    if deva_ratio(s) > 0.15:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", s)
    if len(words) < 4:
        return False
    return bool(re.match(r"^[\"'\[(]*[A-Z]", s))


def is_title_false_positive(headword):
    return any(t in headword for t in TITLE_FALSE_POSITIVE_SUBSTRINGS)


def load_volume(vol):
    """Return (lines, page_of_line) honoring === PAGE N === markers."""
    path = RAW_DIR / f"{VOL_IDS[vol]}_ocr_san_eng.txt"
    lines, page_of_line = [], []
    cur_page = 0
    with open(path, encoding='utf-8') as f:
        for raw in f:
            s = raw.rstrip('\n')
            m = PAGE_MARK.match(s.strip())
            if m:
                cur_page = int(m.group(1))
                continue
            lines.append(s)
            page_of_line.append(cur_page)
    return lines, page_of_line


def find_headword_indices(lines):
    idxs = []
    for i, line in enumerate(lines):
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
                checked += 1
                if looks_like_gloss_sentence(t):
                    hit = True
                break
            if hit:
                idxs.append((i, 'phrase'))
    return idxs


def is_true_headword(lines, idx):
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


def clean_body(raw_lines):
    text = ' '.join(l.strip() for l in raw_lines if l.strip())
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_entries(lines, page_of_line):
    all_tagged = find_headword_indices(lines)
    tier_of = dict(all_tagged)
    all_idx = [i for i, _ in all_tagged]
    good_idx = []
    for idx in all_idx:
        hw = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        if is_title_false_positive(hw):
            continue
        if is_true_headword(lines, idx):
            good_idx.append(idx)

    entries = []
    for pos, idx in enumerate(good_idx):
        nxt = good_idx[pos + 1] if pos + 1 < len(good_idx) else min(idx + 200, len(lines))
        headword = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        body = clean_body(lines[idx + 1:nxt])
        gloss_match = re.match(r'^([A-Z"\'\[(][^.]*\.)', body)
        entries.append({
            'nyaya_deva': headword,
            'gloss_en': gloss_match.group(1).strip() if gloss_match else None,
            'explanation': body[:4000],
            'tier': tier_of.get(idx, 'named'),
            '_leaf': page_of_line[idx],
        })
    return entries


def to_record(e, num, vol):
    meta = VOL_META[vol]
    deva = e['nyaya_deva']
    try:
        iast = deva_to_iast(deva)
    except Exception:
        iast = None
    try:
        slp1 = deva_to_slp1(deva)
    except Exception:
        slp1 = None
    printed_page = e['_leaf'] - meta['offset']
    page_str = printed_page if printed_page > 0 else 'front matter'
    return {
        'num': num,
        'nyaya_deva': deva,
        'nyaya_iast': iast,
        'nyaya_slp1': slp1,
        'gloss_en': e['gloss_en'],
        'explanation': e['explanation'],
        'source': meta['cite'].format(p=page_str),
        '_scan_leaf': e['_leaf'],
        '_headword_tier': e['tier'],
    }


def main():
    all_records, n = [], 1
    for vol in ('01', '02', '03'):
        lines, page_of_line = load_volume(vol)
        entries = extract_entries(lines, page_of_line)
        named = sum(1 for e in entries if e['tier'] == 'named')
        phrase = sum(1 for e in entries if e['tier'] == 'phrase')
        print(f"vol{vol} ({VOL_META[vol]['part_name']}): {len(entries)} entries "
              f"(named={named}, phrase={phrase})")
        for e in entries:
            all_records.append(to_record(e, n, vol))
            n += 1

    print(f"TOTAL: {len(all_records)}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as out:
        for r in all_records:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"Wrote {OUT_PATH}")


if __name__ == '__main__':
    main()
