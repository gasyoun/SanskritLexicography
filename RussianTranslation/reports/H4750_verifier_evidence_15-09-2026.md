# H4750 — verifier evidence appendix (executor-executed live recount)

_Created: 15-09-2026 · Requested by the paired-family verifier (DeepSeek), whose harness
is read-only and could not execute code or reach `csl-orig`/`SamudraManthanam`. This file
records the executor's fresh, independent re-derivation of exactly the checks the
verifier marked PARTIAL — fresh snippet, no import of `h4750_cyr_slp1_backfill.py` — so
the verifier can adjudicate on the combined record. Verifier verdict lives in the
handoff close record; this file is the evidence, not the verdict._

_Method: raw `git show origin/master:...` diff; `<k1>` sets re-extracted from
`/Users/mac/Documents/GitHub/csl-orig/v02/{inm/inm.txt,pui/pui.txt,mw/mw.txt}` with a
fresh regex; tier recount recomputed per-row; attestation re-derived via
`h3985_cyr_slp1_table.index_headwords` over `seeds_pure_cyrillic` (the ONE sanctioned
headword extractor, used read-only)._

## Measured results (2026-09-15, worktree h4750-drain @ 504ced93)

| Check | Result |
|---|---|
| rows | **622** |
| distinct slp1 | **620** |
| diff vs origin/master (cyrillic,slp1 pairs) | **added 88, removed 0** |
| added keys NOT in inm/pui k1 | **[] (empty — 0 of 88)** |
| added spellings NOT attested in the pure-Cyrillic indices | **[] (empty — 0 of 88)** |
| live tier recount | **onomasticon 534 / lexicon 50 / iast-witness-only 38** |

Raw JSON from the evidence run:

```json
{
 "rows": 622,
 "distinct_slp1": 620,
 "added": 88,
 "removed": 0,
 "added_keys_not_in_inm_pui": [],
 "added_spellings_unattested_in_indices": [],
 "tier_recount_live": {"onomasticon": 534, "lexicon": 50, "iast-witness-only": 38}
}
```

Correspondence with [H4750_cyr_slp1_backfill.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4750_cyr_slp1_backfill.json):
`table_rows_before/after` 534/622 ✓ · `new_rows_shipped` 88 ✓ · `recount_before` 446/50/38 ✓ ·
`recount_after` 534/50/38 ✓ · `rule_derived_keys` 0 ✓ (all 88 keys are literal `<k1>` strings).

## Pre-existing defects flagged by the verifier (NOT introduced by H4750, out of scope here)

- line 609: `Палов` row carries a mismatched cyrillic/slp1/iast triple (iast-witness-only tier)
- line 320: key `kRzRa` renders `Kṇṣṇa` (should be `kfzRa`/Kṛṣṇa) — pre-existing H3985-row typo

Both are ticketed as a GTD residual; the backfill batch touches neither row.

_Гасунс_
