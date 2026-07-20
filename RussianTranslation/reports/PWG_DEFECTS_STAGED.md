# PWG defects staged for csl-corrections (H1350 W1.9)

_Created: 20-07-2026 · Last updated: 20-07-2026_

## Manifest

**0 change files staged this pass.**

## Why zero, not a skip

Per the fence (D4: csl-corrections change files only, no csl-orig PR, no
maintainer-repo merge) this step stages VERIFIED defects as change files. Two
intended sources, both honestly empty or out of safe scope this pass:

1. **This wave's own byproduct buckets (W1.2 RNG + W1.3 portrait schema).**
   [`pwg_markup_validation.json`](pwg_markup_validation.json) found **zero**
   real defects — 122,730 pass + 636 `unexpected-but-attested` (Cologne
   float-id supplement records, an attested, expected pattern per
   `pwg_mask.py`'s own comment, not a markup defect). `pwg_portrait_validation.json`
   found **zero** failures of any kind (123,366/123,366 pass). Neither bucket
   has anything to stage.
2. **"The 12 PWG SanskritSpellCheck typos" named in the plan
   ([PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md)
   Sec.3 D9) could not be located as a specific curated list.** The actual
   [`SanskritSpellCheck/Allvs_2026/PWG/`](https://github.com/gasyoun/SanskritSpellCheck/tree/master/Allvs_2026/PWG)
   suspect pool has 256 raw -> 107 signal (99 priority + 8 gemination), none
   individually re-verified against the printed scans in this pass. Staging
   any of them as a csl-corrections change file without that verification
   would violate the org correction-workflow's core discipline
   ([csl-corrections/docs/correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md)) —
   a correction must be checked against the printed source before it becomes
   a change file, not batch-guessed from a faultfinder suspect list.

## Open question for W1.10

**`@DECIDE`** — either point this pass (or a Wave-2 follow-up) at the
specific 12-item list the plan intended, or authorize a dedicated
`/cologne-correction-queue` pass over the 99 priority-tier
[`AllvsPWG-priority.txt`](https://github.com/gasyoun/SanskritSpellCheck/blob/master/Allvs_2026/PWG/AllvsPWG-priority.txt)
suspects (verify each against the Cologne PWG scans, then stage only the
confirmed ones). A human should decide which.

## Verification (V9)

- N change files in `batch_pending/` (0) == N manifest rows (0). ✅
- `git -C csl-orig status` — untouched throughout this wave (read-only, `git log`/`git show` only). ✅
- No PR opened to csl-orig or csl-corrections this pass. ✅

_Dr. Mārcis Gasūns_
