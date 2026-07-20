# -*- coding: utf-8 -*-
"""
H803 follow-up #2 (21-07-2026, Sonnet 5 `claude-sonnet-5`, picked up via
`/next-task`): applies the `prev_is_prose()` pipeline-wide fix that
README.md "Follow-up" #2 flagged but explicitly deferred ("a general fix
risks silently reshaping body-text boundaries of already-reconciled
377-set records this session cannot fully re-verify in one pass").

Root cause (unchanged from the 20-07-2026 diagnosis): prev_is_prose()
rejected ANY index-crossref candidate whose nearest preceding non-empty
line was heavy Devanagari, conflating "sits mid-verse-citation" with
"immediately follows a DIFFERENT entry's own closing verse" -- an
ordinary, common pattern in this text. The fix (see build_laukika_nyaya.py)
now only rejects when that preceding line does NOT itself close with a
verse-final danda/double-danda (।/॥, trailing OCR noise tolerated).

Re-running the fixed `build_laukika_nyaya.py` alone recovers 27 more
headword-boundary candidates (302 -> 329 in the base djvu lane). Of the
original 12 hand-verified H803-followup-1 records
(tools/append_h803_followup_records.py), 9 are now recovered automatically
(their own preceding line DOES close with a clean danda); 3 are not (their
preceding line's danda is itself obscured by OCR noise) and still need
manual inclusion here.

Because Sanskrit verse padas commonly end in a danda even mid-citation,
the relaxed heuristic also surfaces false positives. Every one of the 18
brand-new candidates (beyond the known-12) was independently verified by
a 2-stage adversarial review (1 initial classifier + 2 independent
skeptic/refuters per GENUINE call, `wf_98474080-6ab`, 50 agent calls
total, Sonnet 5 `claude-sonnet-5`) against: (a) the raw OCR context before
and after the line, (b) the book's own back-matter alphabetical index
(the project's established corroboration method), and (c) the committed
dataset (duplicate check). Verdicts:

  - 15 confirmed GENUINE new headwords -- previously silently swallowed,
    verbatim, into the tail of the PRECEDING entry's `explanation` field
    (the exact failure mode this fix targets). The fixed pipeline's own
    good_idx-based boundary computation now correctly splits them out;
    no manual intervention needed beyond letting index_crossref_pass()
    recover them.
  - 3 rejected as duplicates of content ALREADY present in the dataset
    under a different OCR lane/spelling (not fresh discoveries):
      * OCR line 2134 (नौरापराधान्साण्डव्यनियहन्यायः, garbled for
        चोरापराधान्माण्डव्यनिग्रहन्यायः) -- already record's own content
        via the clean-scan lane (nyaya_deva
        "चोरापराधान्माण्डव्यनिग्रहन्यायः", `_match_method`
        "clean-scan-lane-new", scan leaf 45).
      * OCR line 5844 (दामव्यालकटन्यायः) -- confirmed via adversarial
        refute to already exist verbatim, merged into TWO existing
        records' overrun explanation fields (base-lane दाण्डन्यायः and a
        clean-scan-lane record), not a fresh entry.
      * OCR line 9963 (हृदयवचसामहूदयसुत्तरम्, garbled for
        अहृदयवचसामहृदयमुत्तरम्) -- already present via the clean-scan
        lane under the ungarbled spelling (`_scan_leaf` 33).
    These 3 indices are still real TEXT boundaries (they correctly stop
    their preceding neighbour's runaway explanation) so they remain in
    the boundary-computation set -- they are simply never emitted as
    their own record, exactly mirroring the established
    BOUNDARY_ONLY_IDXS convention from append_h803_followup_records.py.

Combined with the 3 residual known-good H803-followup-1 records the fix
still can't auto-recover, this produces a corrected 329-record base djvu
lane (302 + 12 known-good + 15 newly-confirmed = 329), which then feeds
`reconcile_clean_scan_lane.py` fresh (see README.md "Reproduce" for the
step order) to reach the final 404-record `data/laukika_nyaya.jsonl` --
crossing the ≥400 Definition-of-Done target for the first time.

Run (from a clean base-lane state, i.e. right after
`python build_laukika_nyaya.py`):
    cd LaukikaNyaya/tools
    python build_laukika_nyaya.py
    python apply_h803_followup2_prevprose_fix.py
    python reconcile_clean_scan_lane.py
"""
import re
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import build_laukika_nyaya as M

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "data" / "laukika_nyaya.jsonl"

# Verified duplicates of already-existing dataset content (see docstring
# above for the specific existing record each duplicates) -- real
# boundary points, never emitted as their own record.
EXCLUDE_FROM_EMIT = {2134, 5844, 9963}

# The 3 of the original H803-followup-1 known-good 12
# (tools/append_h803_followup_records.py's NEW_IDXS) that the relaxed
# prev_is_prose() still does NOT auto-recover, because their own
# preceding line's verse-final danda is itself obscured by OCR noise
# (912/1410/2230/2248/3275/4506/4885/8421/12818 -- the other 9 -- ARE
# now auto-recovered and need no manual handling here).
RESIDUAL_MANUAL_IDXS = [3297, 4497, 16214]
# Carried forward from append_h803_followup_records.py: confirmed
# already-present duplicates, kept ONLY to give सूक्तवाकन्यायः (16214) the
# correct body-stop boundary; never emitted as records themselves.
BOUNDARY_ONLY_IDXS = [15758, 16260]


def main():
    lines = M.load_lines(M.RAW_PATH)

    v1_tagged = M.find_headword_indices_v1(lines, M.FRONT_MATTER_END, M.INDEX_START)
    tier_of, method_of, good_idx = {}, {}, []
    for idx, tier in v1_tagged:
        raw = re.sub(r'[^ऀ-ॿ]', '', lines[idx].strip()).replace('।', '').replace('॥', '').strip()
        if raw in M.TITLE_FALSE_POSITIVES or 'न्यायाञ्जलि' in raw:
            continue
        if M.is_true_headword_v1(lines, idx):
            good_idx.append(idx)
            tier_of[idx] = tier
            method_of[idx] = 'headword-regex'

    recovered = M.index_crossref_pass(lines, good_idx)
    for idx, method in recovered.items():
        good_idx.append(idx)
        method_of[idx] = method
        tier_of[idx] = 'named' if M.NYAYA_WORD.search(lines[idx]) else 'phrase'

    good_idx = sorted(set(good_idx) - M.EXCLUDED_LINES)
    assert len(good_idx) == 329, (
        f"fixed-pipeline baseline drifted: {len(good_idx)} (expected 329 -- "
        f"re-verify the candidate classification before re-running)"
    )

    for ni in RESIDUAL_MANUAL_IDXS:
        tier_of[ni] = 'named' if M.NYAYA_WORD.search(lines[ni]) else 'phrase'
        method_of[ni] = 'H803-followup2-index-crossref-manual-21.07.26'

    combined = sorted(set(good_idx) | set(RESIDUAL_MANUAL_IDXS) | set(BOUNDARY_ONLY_IDXS))

    entries = []
    for pos, idx in enumerate(combined):
        if idx in BOUNDARY_ONLY_IDXS or idx in EXCLUDE_FROM_EMIT:
            continue
        nxt = combined[pos + 1] if pos + 1 < len(combined) else min(idx + 400, len(lines))
        headword = M.format_headword(lines[idx])
        body = M.clean_body(lines[idx + 1:nxt])
        gloss_match = re.match(r'^([A-Z"\'“‘`\[(][^.]*\.)', body)
        entries.append({
            'nyaya_deva': headword,
            'gloss_en': gloss_match.group(1).strip() if gloss_match else None,
            'explanation': body[:4000],
            'tier': tier_of.get(idx, 'named'),
            '_method': method_of.get(idx, 'headword-regex'),
            '_line': idx,
        })

    part1 = [e for e in entries if e['_line'] < M.PART2_START_LINE]
    part2 = [e for e in entries if M.PART2_START_LINE <= e['_line'] < M.PART3_START_LINE]
    part3 = [e for e in entries if e['_line'] >= M.PART3_START_LINE]
    print(f"Corrected base lane: Part 1: {len(part1)}  Part 2: {len(part2)}  Part 3: {len(part3)}")

    records, n = [], 1
    with open(DATA_PATH, 'w', encoding='utf-8') as out:
        for part_num, part_entries in ((1, part1), (2, part2), (3, part3)):
            for e in part_entries:
                r = M.to_record(e, n, M.PART_SOURCE[part_num])
                records.append(r)
                n += 1
                out.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"TOTAL: {len(records)} -> wrote {DATA_PATH}")
    print("Next: python reconcile_clean_scan_lane.py")


if __name__ == '__main__':
    main()
