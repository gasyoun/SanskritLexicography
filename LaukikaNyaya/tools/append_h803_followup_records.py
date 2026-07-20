# -*- coding: utf-8 -*-
"""
H803 follow-up (19/20-07-2026, this session): appends 12 genuinely new,
manually-verified records to the committed data/laukika_nyaya.jsonl.

Provenance: the clean-scan source (handfulofpopular03jacoiala) turns out
to carry its own "ALPHABETICAL LIST OF NYAYAS EXPLAINED IN PARTS I, II &
III" back-matter index at leaves 169-176 -- README.md's prior "No
back-matter index in this source" claim only checked the literal last ~6
pages and missed it (see README.md follow-up write-up for the full
account). Cross-referencing this index (which turns out to duplicate the
SAME index already used by build_laukika_nyaya.py's own index-crossref
pass, at YKTn-djvu lines ~16495-17207) against the 377 committed headwords
surfaced 12 named-tier nyayas the pipeline still had not recovered --
each one independently confirmed:
  (a) absent from the 377-set via the project's OWN rigorous skeleton+
      gloss-corroboration matcher (reconcile_clean_scan_lane.py's
      best_match()), not just a blunt substring/ratio check (which
      produced false "gaps" for entries already present under OCR
      spelling drift -- see the audit tool docstrings for that dead end),
  (b) a genuine standalone headword line followed by real English
      explanatory prose (manually read in full context, not just the
      headword line in isolation), and
  (c) correctly bounded against every OTHER new-or-existing headword in
      its vicinity (several were found only because extracting one
      revealed a second, previously-unnoticed headword embedded inside
      its own tail -- e.g. उपजीव्यविरोधस्यायुक्तत्वस्‌ inside
      उत्खातदंष्ट्रोरगन्यायः's naive body, झङ्गग्राहिकान्यायः inside
      शुकनलिकान्यायः's).

Root cause of why the existing pipeline missed these: build_laukika_nyaya.py's
own index_crossref_pass correctly LOCATES several of them (they score
>=0.9 against the book's own index) but then rejects them via
prev_is_prose() -- a heuristic meant to reject a headword-shaped line that
sits mid-explanation-verse-quotation, which also incorrectly fires
whenever a genuine NEW headword happens to follow immediately after a
DIFFERENT entry's own explanation ending in a Devanagari verse (a common,
ordinary pattern in this text, not a citation). This is a real, scoped
gap in that heuristic, not fixed here (a general fix risks touching the
already-reconciled 377-set in ways this session cannot fully re-verify in
one pass) -- flagged in README.md "Follow-up" for a future session that
wants to fix it pipeline-wide rather than case-by-case.

Two apparent further "gaps" this same process surfaced (सकृद्गतिन्यायः,
सूत्रबद्धशकुनिन्यायः) turned out to be FALSE gaps -- already present in
the 377-set under OCR spelling drift, confirmed via best_match() before
being excluded from this batch (not a silent drop -- see the console
output this script's development run produced).

Run:
    cd LaukikaNyaya/tools
    python append_h803_followup_records.py
"""
import re
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import build_laukika_nyaya as M

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "data" / "laukika_nyaya.jsonl"

NEW_IDXS = [912, 1410, 2230, 2248, 3275, 3297, 4497, 4506, 4885, 8421, 12818, 16214]
BOUNDARY_ONLY_IDXS = [15758, 16260]  # confirmed already-present duplicates,
# kept ONLY to give their true new-entry neighbours (सूक्तवाकन्यायः) the
# correct body-stop boundary; never emitted as records themselves.

TIER_OVERRIDE = {4506: 'phrase'}  # उपजीव्यविरोधस्यायुक्तत्वस्‌ -- headword
# line itself carries no "न्याय" substring (a phrase-tier maxim, headed by
# its own quoted clause, same convention as the rest of the dataset).


def main():
    lines = M.load_lines(M.RAW_PATH)
    v1_tagged = M.find_headword_indices_v1(lines, M.FRONT_MATTER_END, M.INDEX_START)
    good_idx = []
    for idx, tier in v1_tagged:
        raw = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        if raw in M.TITLE_FALSE_POSITIVES or 'न्यायाञ्जलि' in raw:
            continue
        if M.is_true_headword_v1(lines, idx):
            good_idx.append(idx)
    recovered = M.index_crossref_pass(lines, good_idx)
    good_idx = sorted((set(good_idx) | set(recovered.keys())) - M.EXCLUDED_LINES)
    assert len(good_idx) == 302, f"baseline drifted: {len(good_idx)} (expected 302 -- re-verify before appending)"

    combined = sorted(set(good_idx) | set(NEW_IDXS) | set(BOUNDARY_ONLY_IDXS))

    existing = []
    with open(DATA_PATH, encoding='utf-8') as f:
        for l in f:
            existing.append(json.loads(l))
    assert len(existing) == 377, f"existing dataset drifted: {len(existing)} (expected 377 -- re-verify before appending)"
    max_num = max(r['num'] for r in existing)

    new_records = []
    for ni in NEW_IDXS:
        pos = combined.index(ni)
        nxt = combined[pos + 1] if pos + 1 < len(combined) else min(ni + 400, len(lines))
        headword = M.format_headword(lines[ni])
        body = M.clean_body(lines[ni + 1:nxt])
        gloss_match = re.match(r'^([A-Z"\'“‘`\[(][^.]*\.)', body)
        gloss = gloss_match.group(1).strip() if gloss_match else None
        part = 1 if ni < M.PART2_START_LINE else (2 if ni < M.PART3_START_LINE else 3)
        tier = TIER_OVERRIDE.get(ni, 'named' if M.NYAYA_WORD.search(lines[ni]) else 'phrase')
        deva = headword
        try:
            iast = M.deva_to_iast(deva)
        except Exception:
            iast = None
        try:
            slp1 = M.deva_to_slp1(deva)
        except Exception:
            slp1 = None
        max_num += 1
        new_records.append({
            'num': max_num,
            'nyaya_deva': deva,
            'nyaya_iast': iast,
            'nyaya_slp1': slp1,
            'gloss_en': gloss,
            'explanation': body[:4000],
            'source': M.PART_SOURCE[part],
            '_ocr_line': ni,
            '_headword_tier': tier,
            '_match_method': 'H803-followup-index-crossref-manual-20.07.26',
        })

    print(f"New records to append: {len(new_records)}")
    for r in new_records:
        print(f"  #{r['num']} {r['nyaya_deva']} ({r['_headword_tier']}, line {r['_ocr_line']})")

    all_records = existing + new_records
    with open(DATA_PATH, 'w', encoding='utf-8') as out:
        for r in all_records:
            out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"TOTAL: {len(all_records)} -> wrote {DATA_PATH}")


if __name__ == '__main__':
    main()
