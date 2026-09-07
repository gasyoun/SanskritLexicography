# GLOSS WRAPPERS worked example is language-keyed — the EN lane no longer reads a Russian example for its own English output (#2109)

_Created: 07-09-2026 · Last updated: 07-09-2026_

_Date: 07-09-2026 · Executor: Opus 5 (`claude-opus-5`), interactive · **0 paid calls** (offline)_

- **The gap.** The H4270 `=== GLOSS WRAPPERS {%…%} ===` block reached both lanes — `MASK_PREAMBLE`
  is parameterized at its two call sites by `.replace('`russian`', '`%s`' % field)` — but that
  swaps the target-field NAME only. The worked example inside the block stayed RU-illustrated, so
  an `--lang en` window was shown «becomes RU `а) {%некий%} …`» as the model for the English it was
  about to produce. Surfaced while re-deriving the LANG_PARITY ledger for H4326.
- **Fix.** `MASK_PREAMBLE_TEMPLATE` now carries a `{{GLOSS_WRAPPER_EXAMPLE}}` slot filled from
  `GLOSS_WRAPPER_EXAMPLE[field]` by a new `mask_preamble(field)` helper, which both call sites (v2
  execution manifest + generated JS harness) use in place of the raw `.replace()`. EN gets the same
  DE source sense demonstrated as `a) {%a certain%} <is>Arhant</is> <ls>H. 25</ls>.`, with the same
  `{Tn}`-verbatim tightening clause.
- **RU is byte-identical.** `MASK_PREAMBLE` is now `mask_preamble('russian')` and renders exactly
  the pre-fix text — verified against `origin/master` — so the language-neutral readiness probe
  (`max_account_orchestrator._probe_prompt`, which prepends the constant) and every RU manifest are
  untouched.
- **Pinned.** `test_gloss_wrapper_prompt_preservation_h4270` grew an EN-lane section: the EN
  rendering must carry the English example and the shared rule clauses, must not carry «некий», and
  the RU rendering must not pick up the English example. Window selftest 223/223.
- **Ledger.** `gloss_wrapper_worked_example_localisation` flipped **GAP → SHARED** in
  [`RussianTranslation/LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md);
  59 entries hashing `src/pilot/gen_opt_harness2.py` / `src/pilot/window_selftest.py` re-stamped by
  [`src/pilot/i2109_parity_restamp.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/i2109_parity_restamp.py)
  (kept as the receipt, exempted in the coverage map like its three predecessors). Gate: 109
  entries, no drift, 32 language-aware files all tracked or exempt.

_Dr. Mārcis Gasūns_
