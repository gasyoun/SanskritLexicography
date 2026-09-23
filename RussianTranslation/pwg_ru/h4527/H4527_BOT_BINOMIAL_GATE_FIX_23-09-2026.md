# H4527, 23-09-2026: the `<bot>` binomial gate false positive is fixed (gate and masker), 0 paid calls

_Created: 23-09-2026 · Last updated: 23-09-2026_

Executor: Opus 5.5 (`claude-opus-5-5`), interactive `/go` on the Mac. Follows
[H4527_REPAIR_RUN_DARVI_REMADE_KASTURI_GATE_FALSE_POSITIVE_23-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_REPAIR_RUN_DARVI_REMADE_KASTURI_GATE_FALSE_POSITIVE_23-09-2026.md),
which named the defect: `kast_ur_i~~h0_zz_pw` was requeued for
`untranslated_braced_german_gloss` on `{%<bot>Hibiscus abelmoschus</bot>%}` and
`{%<bot>Amaryllis zeylanica</bot>%}`, Latin species names the Russian correctly keeps verbatim.

## What changed

1. [`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)
   `looks_foreign_literal` strips markup tags (content kept) with a new `MARKUP_TAG`
   before any classifier runs. The anchored `LATIN_BINOMIAL` no longer fails on a leading tag.
2. [`pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)
   `looks_botany_binomial` strips tags the same way. This was the independent critic's
   should-fix. Before it, the masker sent `{%{T1}Hibiscus abelmoschus{T2}%}` to the model
   inline as German to translate, while the gate expected it verbatim. Now the whole span
   is masked as one placeholder and `restore()` brings it back byte for byte.
3. [`bounded_staged_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py)
   refuses a `--cwd` that is not an existing directory (argparse exit 2) on the dry run and
   on `--execute`. On 23-09 the dry run passed, and the paid run then crashed with
   `NotADirectoryError` after preflight.

## Checks

| Check | Result |
|---|---|
| `window_selftest.py` | 229/229 (new pins in `test_braced_gloss_audit`: two `<bot>` binomials not flagged; bare `{%Moschus%}` and `{%<bot>Moschus</bot>%}` echoes still flagged) |
| `pwg_mask.py --selftest` | 20 checks OK (tagged binomial → `la`; three German-with-`<bot>` shapes stay `de`; mask/restore byte-exact) |
| `bounded_staged_run_selftest.py` | PASS, new pin `test_x_missing_cwd_refused_before_run_h4527` |
| `cohort_engine_selftest.py` · `coordinator_hardening_selftest.py` | PASS (12 pins) · PASS |
| `tests/run_offline_suite.py` | 201 passed |
| Mutation tests | Each fix reverted in turn: the matching pin fails every time. An over-broad mutant ("any tag means foreign") fails the German-direction pin |
| `lang_parity_check.py` | clean, 50 entries re-stamped (receipt `src/pilot/h4527_bot_parity_restamp.py`), no verdict moved |

## Census (blast radius), 0 calls

[`h4527_bot_binomial_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4527_bot_binomial_census.py)
classifies every markup-bearing `{%...%}` span in PW and PWG twice: with both fixes and
with the pre-fix functions patched back in. Receipt:
[`h4527_bot_binomial_census_23-09-2026.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/h4527_bot_binomial_census_23-09-2026.json).

| Source | Braced spans | With markup | Gate moves | Masker moves |
|---|---|---|---|---|
| PW (`pw.txt`, csl-orig `e994234`) | 212 558 | 19 232 | 5 705 German → foreign (5 420 `<bot>`, 285 `<zoo>`); 1 foreign → German | 5 705 `de` → `la` |
| PWG (`pwg.txt`) | 192 763 | 7 850 | 0 | 0 |

- All 5 705 moved spans (649 unique) are strict `Genus species[ epithet]` shapes after
  stripping. None has an umlaut or a `GERMAN_GLOSS_WORDS` hit. This is the relaxation's
  whole reach, and it contains no German.
- The one foreign → German move is `{%agreable |<sic/>, pleasing%}`. It was "foreign"
  before only because the tag NAME `sic` matched `LATIN_WORDS`. It now fails closed: a
  verbatim echo would be requeued, not published.
- Every no-PWG `~~h0_zz_pw` card with a PW botanical or zoological name was
  structurally unable to pass this gate before the fix.

## Independent critic

A read-only Explore agent (Fable 5.1, `claude-fable-5-1`) reviewed the diff before
the PR. Verdict: **PASS-WITH-NOTES**, no blocker.

- Should-fixes, all applied:
  - the masker disagreement (item 2 above);
  - the parity re-stamp;
  - the census scanning PW, not only PWG.
- Theoretical note, not in either corpus: `Zimmt <ab>u.s.w.</ab>` strips to a
  binomial-shaped string. The bare form `Zimmt u.s.w.` had the same weakness before.
  The census shows 0 `<ab>` moves.
- `--cwd` refusal is safe. The only programmatic caller (`nonstop_scheduler.py`)
  passes an existing directory.

## `kast_ur_i`: not promoted in this pass

- The coordinator records output only for a lease in state `running`
  (`coordinator.py` `record_output`, P11/H1420). `h4527vol14` is `needs_requeue`.
- There is no gated path that re-audits a stored output for a lease in that state.
  "Re-audit for 0 paid calls, then promote" would need a new state transition in
  money-path code, a change of its own.
- The cheapest path that uses only existing gates is one retry through
  `--repair-lease` (1 card call + probe legs). It runs after this fix is merged and pulled
  on MSI.
- MSI was offline on the tailnet for this whole session (last seen ~13:30Z). So the
  pull, the standalone read-only audit and the retry all wait for the box.

_Гасунс_
