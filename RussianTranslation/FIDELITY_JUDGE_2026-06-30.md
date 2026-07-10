# PWG→Russian fidelity — first measured number (Opus judge, interim)

**Date:** 2026-06-30 · **Decision context:** all ~1,989 bulk cards carry `judge=null`; the
0/320 human gold (G6) is the only path to a *human* fidelity number, but MG chose an **Opus
LLM-judge interim** to get a first measurement now.

## Headline

| metric | value |
|---|---|
| cards judged | **100** (stratified, seed 42) |
| **precision** | **98.0 %** (98 good / 2 bad) |
| **95 % CI (Wilson)** | **[93.0 %, 99.4 %]** |
| severity 0 / 1 / 2 / 3 | 39 / 58 / 1 / 2 |
| bad-issue classes | anchors ×1, grammar/anglicism ×1 |

A card is **BAD** when `ok=false` or `severity ≥ 3` (the `judge_ab_score` convention). Both
BADs are **markup/grammar, not mistranslation** — the in-sample *semantic* faithfulness is
effectively 100 %.

### The two defects (full)

- `n_i~~h0_57_vipari` (sev 3, *anchors*): the `{%..%}` gloss markers around the Russian
  definition were dropped — a markup-fidelity loss, the meaning is correct. (F-class markup
  residual, not a translation error.)
- `m_a~~h0_zz_pw00` (sev 3, *grammar/anglicism*): gender disagreement *"Примечателен
  употребление"* → should be *"Примечательно употребление"*. A genuine but trivial Russian
  agreement slip; the gloss meaning is faithful.

One borderline sev-2: `muc~~h0_zz_pw00` renders a single German *aufgelöst* as a duplicated
*"расслабленный, расслабленный"* (likely a typo dup) — anchors intact.

### By stratum

| stratum | n | precision | 95 % CI |
|---|---:|---:|---|
| Vedic | 20 | 100 % | [84 %, 100 %] |
| Epic | 10 | 100 % | [72 %, 100 %] |
| Classical | 6 | 100 % | [61 %, 100 %] |
| Medieval | 2 | 100 % | [34 %, 100 %] |
| Buddhist | 1 | 100 % | [21 %, 100 %] |
| unspecified | 61 | 97 % | [89 %, 99 %] |

(Both BADs fall in `unspecified`. The stratum skew — 61 % unspecified — reflects that the
`stratum` field is empty on most senses, not a sampling defect; see caveats.)

## Method

1. [`fidelity_sample.py`](src/fidelity_sample.py) — deterministic stratified draw of 100 cards
   (seed 42) from the 1,431 non-null cards (same non-null/dedup as the bridge), stratified by
   each card's modal sense `stratum`.
2. [`gen_fidelity_judge.py`](src/pilot/gen_fidelity_judge.py) — emits a self-contained judge
   workflow (17 batches of 6), rubric **adapted from [`mw_ru_prompts/qa_judge_v4.md`](mw_ru_prompts/qa_judge_v4.md)**
   to PWG DE→RU (semantic / anchors / hallucination / truncation / grammar; with the PWG
   carve-outs: retained German abbreviations, Latin euphemisms, `{%German%}` echoes are NOT
   defects). Verdict schema = `judge_ab_score`'s `{key, ok, severity, issues, note}`.
3. **Opus** judged every card (one agent per batch). 710 k subagent tokens, ~75 s wall-clock.
4. [`fidelity_aggregate.py`](src/pilot/fidelity_aggregate.py) — precision + 95 % Wilson CI,
   overall and per stratum; severity + bad-issue histograms.

## Caveats (this is an *interim*, not the human gold)

- **Single judge.** No second judge / Cohen κ. JUDGE_POLICY's A/B found Opus≈Sonnet (κ=1.0)
  on the mechanical core, so a single Opus pass is a defensible interim, but it is not the
  G6 human gold (0/320) that a publishable fidelity claim needs.
- **Stratum skew.** 61 % `unspecified` because the per-sense `stratum` field is usually empty
  (a *coverage* gap in the structured layer, not the translation). Deterministic backfill of
  `stratum` from the citation (PROCESS_AUDIT rec 9) would let a future run stratify properly.
- **Senses capped at 600 chars** for judging (gloss meaning is up front; citations are markup);
  the rubric tells the judge not to penalize end-of-gloss cutoff.
- **Self-selection:** judged the *non-null* cards (the translations that exist); says nothing
  about the Slice-C cards lost to the requeue-overwrite gap.

## Takeaway

In a 100-card stratified sample, the harness DE→RU output is **98 % clean (CI 93–99 %)**, and
**the only two defects are a dropped markup marker and a gender typo — zero semantic
mistranslations**. This corroborates the design assumption that the bulk quality is high and
that the remaining residual is markup/grammar (already handled by the deterministic gates +
the `fix_german_connectives` pass), not meaning. The human G6 gold remains the gate for a
*publishable* number.

Evidence: [`fidelity_verdicts_2026-06-30.json`](fidelity_verdicts_2026-06-30.json) (raw 100
verdicts), `src/pilot/output/fidelity_aggregate.json` (regenerable).
