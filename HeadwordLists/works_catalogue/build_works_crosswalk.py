"""ACC x NCC P1 -- full-fuzzy matching engine.

Per ROADMAP_ACC_NCC.md P1: reads acc.jsonl + ncc.jsonl (P0 outputs, read-only)
and emits crosswalk_candidates.jsonl.gz, one row per candidate ACC<->NCC work
link, tiered A-D per the roadmap's table. P2 (human adjudication of Tier C/D
via /review-sheet) is out of scope here -- this script only scores candidates.

Output is gzip-compressed (~14 MB vs. ~119 MB uncompressed) because the
uncompressed JSONL exceeds GitHub's 100 MB single-file limit -- unlike
acc.jsonl/ncc.jsonl, this file duplicates each side's full body text once per
candidate pair, so the raw size crosses that limit even though the row count
is comparable. Read with `gzip.open(path, 'rt', encoding='utf-8')`.

Tier definitions (see docstrings on each tier's builder function below for the
full rationale):

    A  exact match_key equality (P0's own 8,397 -- re-derived here, not hardcoded)
    B  match_key equality after an additional nasal-fold + doubled-letter fold
       normalization, that A's plain match_key equality does not catch
    C  prefix containment: one side's match_key is a proper prefix of the
       other's (`amsatrayivicara` vs `amsatrayivicaraxyz`)
    D  edit-distance <= a length-scaled threshold on match_key, via rapidfuzz
       (already installed in this environment; no new edit-distance library
       hand-rolled)

Tiers are checked in order A -> B -> C -> D and a pair is assigned to the
FIRST tier it qualifies for (a pair already counted in A is never re-counted
in B/C/D, etc.) -- this keeps the per-tier counts partitioned and additive.

Usage:
    python HeadwordLists/works_catalogue/build_works_crosswalk.py
"""
import sys
import os
import json
import bisect
import gzip
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from rapidfuzz.distance import Levenshtein  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ACC_JSONL = os.path.join(HERE, "acc.jsonl")
NCC_JSONL = os.path.join(HERE, "ncc.jsonl")
OUT_PATH = os.path.join(HERE, "crosswalk_candidates.jsonl.gz")
COUNTS_PATH = os.path.join(HERE, "P1_COUNTS.md")

# Tier C: shortest key allowed to participate in a prefix-containment match.
# Below this length a "prefix" is nearly meaningless (e.g. a 3-char key is a
# prefix of thousands of unrelated longer keys) -- this is a precision floor,
# not a recall cap: every match at/above this length is still emitted, none
# silently dropped.
TIER_C_MIN_KEY_LEN = 5


def load_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def nasal_and_geminate_fold(key):
    """Tier B normalization, applied ON TOP OF slp1_simplify's match_key.

    Rationale: slp1_simplify already folds the SLP1 anusvara glyph (M) to
    plain 'm', and folds the three place-nasals ṅ/ñ/ṇ (N/Y/R) to 'n' -- but
    it leaves 'm' and 'n' as two DIFFERENT letters. In practice, whether a
    catalogue scribe wrote a nasal before a following consonant as an
    anusvara (ṃ) or as the phonetically-assimilated place nasal (ṅ/ñ/ṇ/n) is
    a transliteration-convention choice, not a distinct lexical form -- e.g.
    ACC's k1 and NCC's iast disagree on this exact point for some titles.
    Tier B folds m and n into one symbol so such pairs land here instead of
    staying unmatched.

    Second fold: collapse any run of the same letter to a single instance
    (geminate vs. single-consonant spelling at a compound boundary, e.g.
    "-tva" vs "-ttva" renderings of the same title) -- a compound-boundary
    variant the roadmap's Tier B row names explicitly.
    """
    folded = key.replace('n', 'm')
    out = []
    prev = None
    for ch in folded:
        if ch != prev:
            out.append(ch)
        prev = ch
    return ''.join(out)


def tier_d_threshold(key_len):
    """Length-scaled edit-distance threshold for Tier D.

    A flat threshold is wrong at both ends: distance<=2 on a 6-char key
    allows a third of the string to differ (too loose), while distance<=2 on
    a 30-char key barely tolerates one real variant spelling (too strict).
    Scaling roughly 1 edit per 7 characters, floored at 1, keeps the
    tolerance proportional to how much string there is to differ over.
    """
    return max(1, key_len // 7)


def build_tier_a(acc_by_key, ncc_by_key):
    """Tier A: exact match_key equality, re-derived from the JSONL (not
    hardcoded to P0's measured 8,397, since acc.jsonl/ncc.jsonl may have
    shifted slightly since P0_COUNTS.md was written -- see its own
    snapshot-drift note)."""
    shared = set(acc_by_key) & set(ncc_by_key)
    return shared


def build_tier_b(acc_by_key, ncc_by_key, tier_a_keys):
    """Tier B: nasal/geminate-folded key equality, excluding any pair whose
    RAW match_key was already equal (those are Tier A)."""
    acc_folded = defaultdict(set)
    for k in acc_by_key:
        if k in tier_a_keys:
            continue
        acc_folded[nasal_and_geminate_fold(k)].add(k)
    ncc_folded = defaultdict(set)
    for k in ncc_by_key:
        if k in tier_a_keys:
            continue
        ncc_folded[nasal_and_geminate_fold(k)].add(k)

    pairs = []  # (acc_key, ncc_key)
    for folded_key, acc_keys in acc_folded.items():
        ncc_keys = ncc_folded.get(folded_key)
        if not ncc_keys:
            continue
        for ak in acc_keys:
            for nk in ncc_keys:
                if ak == nk:
                    continue  # would already be Tier A; folding is a no-op here
                pairs.append((ak, nk))
    return pairs


def build_tier_c(acc_keys_remaining, ncc_keys_remaining):
    """Tier C: prefix containment between the two DISTINCT-key sets left
    after A+B are removed. Implemented as PREFIX containment specifically
    (X is a proper prefix of Y), not general mid-string substring
    containment -- the roadmap's own example (Abhayapradana c Abhayapradanasara)
    is a prefix case, and prefix containment is checkable in O((n+m) log(n+m))
    via sorted-array + bisect, whereas general substring containment across
    32k x 125k keys would need a suffix-automaton to stay tractable. Both
    directions are checked (ACC key prefix of NCC key, and vice versa).
    """
    sorted_acc = sorted(k for k in acc_keys_remaining if len(k) >= TIER_C_MIN_KEY_LEN)
    sorted_ncc = sorted(k for k in ncc_keys_remaining if len(k) >= TIER_C_MIN_KEY_LEN)

    pairs = []

    def prefix_hits(needle, haystack_sorted):
        lo = bisect.bisect_left(haystack_sorted, needle)
        hi = bisect.bisect_left(haystack_sorted, needle + '￿')
        return haystack_sorted[lo:hi]

    for ak in sorted_acc:
        for nk in prefix_hits(ak, sorted_ncc):
            if nk != ak:
                pairs.append((ak, nk))
    for nk in sorted_ncc:
        for ak in prefix_hits(nk, sorted_acc):
            if ak != nk:
                pairs.append((ak, nk))

    return sorted(set(pairs))


def build_tier_d(acc_keys_remaining, ncc_keys_remaining):
    """Tier D: length-scaled edit-distance on the remaining (post A/B/C)
    distinct keys. Full n x m comparison is infeasible (32k x 125k = ~4B
    pairs), so keys are BLOCKED by (first letter, length bucket) before
    running rapidfuzz's Levenshtein distance -- edit distance <= threshold
    implies the length difference is also <= threshold, and a genuine typo/
    variant overwhelmingly preserves the first letter (a real cross-catalogue
    match starting with a different letter would be an extremely aggressive
    edit at position 0, well past any threshold this tier uses). This is a
    performance blocking heuristic, not a precision filter -- it trades a
    vanishingly small recall loss (first-letter-differing near-matches) for
    making Tier D computable at all.
    """
    by_bucket = defaultdict(lambda: ([], []))  # bucket -> (acc_keys, ncc_keys)
    for k in acc_keys_remaining:
        by_bucket[(k[0] if k else '', len(k) // 4)][0].append(k)
    for k in ncc_keys_remaining:
        by_bucket[(k[0] if k else '', len(k) // 4)][1].append(k)

    pairs = []
    for (_, _), (acc_list, ncc_list) in by_bucket.items():
        if not acc_list or not ncc_list:
            continue
        for ak in acc_list:
            thresh = tier_d_threshold(len(ak))
            for nk in ncc_list:
                if ak == nk:
                    continue
                if abs(len(ak) - len(nk)) > thresh:
                    continue
                dist = Levenshtein.distance(ak, nk, score_cutoff=thresh)
                if dist <= thresh:
                    pairs.append((ak, nk, dist, thresh))
    return pairs


def emit_row(acc_row, ncc_row, tier, score):
    return {
        'acc_L': acc_row['acc_L'],
        'ncc_id': ncc_row['ncc_id'],
        'tier': tier,
        'score': score,
        'acc_match_key': acc_row['match_key'],
        'ncc_match_key': ncc_row['match_key'],
        'acc_k1_slp1': acc_row['k1_slp1'],
        'acc_body': acc_row['body'],
        'ncc_iast': ncc_row['iast'],
        'ncc_deva': ncc_row['deva'],
        'ncc_body_html': ncc_row['body_html'],
    }


def main():
    acc_records = load_jsonl(ACC_JSONL)
    ncc_records = load_jsonl(NCC_JSONL)

    acc_by_key = defaultdict(list)
    for r in acc_records:
        acc_by_key[r['match_key']].append(r)
    ncc_by_key = defaultdict(list)
    for r in ncc_records:
        ncc_by_key[r['match_key']].append(r)

    acc_keys = set(acc_by_key)
    ncc_keys = set(ncc_by_key)

    rows = []
    tier_counts = {}
    tier_acc_covered = {}
    tier_ncc_covered = {}

    def log_tier(tier, key_pairs_with_scores):
        # key_pairs_with_scores: list of (acc_key, ncc_key, score)
        acc_seen, ncc_seen = set(), set()
        n = 0
        for ak, nk, score in key_pairs_with_scores:
            for a_rec in acc_by_key[ak]:
                for n_rec in ncc_by_key[nk]:
                    rows.append(emit_row(a_rec, n_rec, tier, score))
                    n += 1
            acc_seen.add(ak)
            ncc_seen.add(nk)
        tier_counts[tier] = n
        tier_acc_covered[tier] = len(acc_seen)
        tier_ncc_covered[tier] = len(ncc_seen)

    # Tier A
    tier_a_keys = build_tier_a(acc_by_key, ncc_by_key)
    log_tier('A', [(k, k, 1.0) for k in tier_a_keys])

    # Tier B
    tier_b_pairs = build_tier_b(acc_by_key, ncc_by_key, tier_a_keys)
    log_tier('B', [(ak, nk, 0.9) for ak, nk in tier_b_pairs])

    # Remaining distinct keys for C/D: exclude any key already placed in A or B
    b_acc_keys = {ak for ak, _ in tier_b_pairs}
    b_ncc_keys = {nk for _, nk in tier_b_pairs}
    acc_remaining = acc_keys - tier_a_keys - b_acc_keys
    ncc_remaining = ncc_keys - tier_a_keys - b_ncc_keys

    # Tier C
    tier_c_pairs = build_tier_c(acc_remaining, ncc_remaining)
    log_tier('C', [(ak, nk, 0.6) for ak, nk in tier_c_pairs])

    c_acc_keys = {ak for ak, _ in tier_c_pairs}
    c_ncc_keys = {nk for _, nk in tier_c_pairs}
    acc_remaining_d = acc_remaining - c_acc_keys
    ncc_remaining_d = ncc_remaining - c_ncc_keys

    # Tier D
    tier_d_pairs = build_tier_d(acc_remaining_d, ncc_remaining_d)
    # score: 1 - dist/max(len) so a closer match scores higher, in (0, 1)
    tier_d_scored = []
    for ak, nk, dist, thresh in tier_d_pairs:
        maxlen = max(len(ak), len(nk), 1)
        score = round(1.0 - dist / maxlen, 3)
        tier_d_scored.append((ak, nk, score))
    log_tier('D', tier_d_scored)

    with gzip.open(OUT_PATH, 'wt', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    total_acc_covered = len(tier_a_keys | b_acc_keys | c_acc_keys |
                             {ak for ak, _, _ in tier_d_scored})
    total_ncc_covered = len(tier_a_keys | b_ncc_keys | c_ncc_keys |
                             {nk for _, nk, _ in tier_d_scored})

    with open(COUNTS_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write("# ACC x NCC P1 -- crosswalk candidate counts\n\n")
        f.write("_Created: 06-07-2026 · Last updated: 06-07-2026_\n\n")
        f.write("Produced by [`build_works_crosswalk.py`](build_works_crosswalk.py) against "
                "the current `acc.jsonl` / `ncc.jsonl` (P0 outputs, read-only inputs here).\n\n")
        f.write("| Tier | Candidate rows | Distinct ACC keys | Distinct NCC keys |\n")
        f.write("|---|---:|---:|---:|\n")
        for tier in ['A', 'B', 'C', 'D']:
            f.write(f"| {tier} | {tier_counts[tier]:,} | {tier_acc_covered[tier]:,} "
                     f"| {tier_ncc_covered[tier]:,} |\n")
        f.write(f"\n**Total candidate rows:** {len(rows):,}. "
                f"**Distinct ACC keys covered (any tier):** {total_acc_covered:,} of "
                f"{len(acc_keys):,}. **Distinct NCC keys covered (any tier):** "
                f"{total_ncc_covered:,} of {len(ncc_keys):,}.\n\n")
        f.write("## Tier A cross-check against P0\n\n")
        f.write(f"P0_COUNTS.md measured 8,397 shared exact keys. This run measures "
                f"**{len(tier_a_keys):,}** shared exact keys re-derived directly from "
                f"the current acc.jsonl/ncc.jsonl. "
                + ("Matches P0 exactly.\n\n" if len(tier_a_keys) == 8397 else
                   "Differs from P0's 8,397 -- see acc.jsonl/ncc.jsonl for any "
                   "re-parse since P0, this script does not silently reconcile "
                   "the discrepancy.\n\n"))
        f.write("## Tier B rule\n\n")
        f.write("Nasal fold (`m`/`n` treated as one symbol -- anusvara vs. "
                "place-assimilated-nasal is a transliteration-convention choice, "
                "not a distinct lexical form) + geminate fold (collapse repeated "
                "letters -- single vs. doubled consonant at a compound boundary). "
                f"Adds **{tier_counts['B']:,}** candidate rows beyond Tier A's "
                f"{tier_counts['A']:,}.\n\n")
        f.write("## Tier C rule\n\n")
        f.write(f"Proper PREFIX containment (not general substring) between remaining "
                f"distinct keys, minimum key length {TIER_C_MIN_KEY_LEN} chars to avoid "
                f"short-key explosion; checked via sorted-array + bisect in both "
                f"directions. **Flagged for adjudication, not auto-merged.** "
                f"{tier_counts['C']:,} candidate rows.\n\n")
        f.write("## Tier D rule\n\n")
        f.write("Edit distance (rapidfuzz `Levenshtein.distance`) <= `max(1, len(key)//7)`, "
                "computed only within (first-letter, length//4-bucket) blocks for "
                "tractability against the full 32k x 125k cross-product. "
                "**Flagged for adjudication, not auto-merged.** Every row carries a "
                "0-1 `score` (`1 - dist/max_len`) for the adjudication sheet to rank by. "
                f"{tier_counts['D']:,} candidate rows.\n\n")
        f.write("No tier's output was capped for size -- all measured counts above are "
                "the actual, uncapped totals.\n")

    print(f"P1: {len(rows)} candidate rows -> {OUT_PATH}")
    print(f"Tier counts: {tier_counts}")
    print(f"P1 counts written -> {COUNTS_PATH}")


if __name__ == '__main__':
    main()
