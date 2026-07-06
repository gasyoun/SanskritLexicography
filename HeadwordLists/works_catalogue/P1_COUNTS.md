# ACC x NCC P1 -- crosswalk candidate counts

_Created: 06-07-2026 · Last updated: 06-07-2026_

Produced by [`build_works_crosswalk.py`](build_works_crosswalk.py) against the current `acc.jsonl` / `ncc.jsonl` (P0 outputs, read-only inputs here).

| Tier | Candidate rows | Distinct ACC keys | Distinct NCC keys |
|---|---:|---:|---:|
| A | 107,815 | 8,397 | 8,397 |
| B | 12,426 | 2,041 | 2,047 |
| C | 5,353 | 1,254 | 2,904 |
| D | 43,666 | 7,552 | 7,745 |

**Total candidate rows:** 169,260. **Distinct ACC keys covered (any tier):** 19,244 of 32,287. **Distinct NCC keys covered (any tier):** 21,093 of 124,801.

## Tier A cross-check against P0

P0_COUNTS.md measured 8,397 shared exact keys. This run measures **8,397** shared exact keys re-derived directly from the current acc.jsonl/ncc.jsonl. Matches P0 exactly.

## Tier B rule

Nasal fold (`m`/`n` treated as one symbol -- anusvara vs. place-assimilated-nasal is a transliteration-convention choice, not a distinct lexical form) + geminate fold (collapse repeated letters -- single vs. doubled consonant at a compound boundary). Adds **12,426** candidate rows beyond Tier A's 107,815.

## Tier C rule

Proper PREFIX containment (not general substring) between remaining distinct keys, minimum key length 5 chars to avoid short-key explosion; checked via sorted-array + bisect in both directions. **Flagged for adjudication, not auto-merged.** 5,353 candidate rows.

## Tier D rule

Edit distance (rapidfuzz `Levenshtein.distance`) <= `max(1, len(key)//7)`, computed only within (first-letter, length//4-bucket) blocks for tractability against the full 32k x 125k cross-product. **Flagged for adjudication, not auto-merged.** Every row carries a 0-1 `score` (`1 - dist/max_len`) for the adjudication sheet to rank by. 43,666 candidate rows.

No tier's output was capped for size -- all measured counts above are the actual, uncapped totals.
