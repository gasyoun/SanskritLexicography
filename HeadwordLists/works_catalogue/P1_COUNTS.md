# ACC x NCC P1 -- crosswalk candidate counts

_Created: 06-07-2026 · Last updated: 26-07-2026_

Produced by [`build_works_crosswalk.py`](build_works_crosswalk.py) against the current `acc.jsonl` / `ncc.jsonl` (P0 outputs, read-only inputs here).

| Tier | Candidate rows | Distinct ACC keys | Distinct NCC keys |
|---|---:|---:|---:|
| A | 241,970 | 22,775 | 22,775 |
| B | 7,832 | 1,335 | 1,336 |
| C | 9,039 | 2,717 | 3,729 |
| D | 1,575 | 872 | 972 |

**Total candidate rows:** 260,416. **Distinct ACC keys covered (any tier):** 27,699 of 32,287. **Distinct NCC keys covered (any tier):** 28,812 of 124,523.

## Tier A cross-check against P0

P0_COUNTS.md measured 22,775 shared exact keys. This run measures **22,775** shared exact keys re-derived directly from the current acc.jsonl/ncc.jsonl. Matches P0 exactly.

## Tier B rule

Nasal fold (`m`/`n` treated as one symbol -- anusvara vs. place-assimilated-nasal is a transliteration-convention choice, not a distinct lexical form) + geminate fold (collapse repeated letters -- single vs. doubled consonant at a compound boundary). Adds **7,832** candidate rows beyond Tier A's 241,970.

## Tier C rule

Proper PREFIX containment (not general substring) between remaining distinct keys, minimum key length 5 chars to avoid short-key explosion; checked via sorted-array + bisect in both directions. **Flagged for adjudication, not auto-merged.** 9,039 candidate rows.

## Tier D rule

Edit distance (rapidfuzz `Levenshtein.distance`) <= `max(1, len(key)//7)`, computed only within (first-letter, length//4-bucket) blocks for tractability against the full 32k x 125k cross-product. **Flagged for adjudication, not auto-merged.** Every row carries a 0-1 `score` (`1 - dist/max_len`) for the adjudication sheet to rank by. 1,575 candidate rows.

No tier's output was capped for size -- all measured counts above are the actual, uncapped totals.
