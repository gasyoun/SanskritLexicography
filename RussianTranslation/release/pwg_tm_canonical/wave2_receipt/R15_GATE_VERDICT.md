# R15 independent gate verdict — FAIL (honest halt, no second repair)

_Created: 24-08-2026 · Session: H3299 execution · Seed 3299 · n=400 stratified over the regenerated pool_

## Verdict lines (floors unchanged: fidelity ≥98% · equivalence ≥95% · serious ≤1%)

| floor | measured | verdict |
|---|---|---|
| fidelity ≥ 0.98 | **0.6675** | ❌ FAIL |
| equivalence ≥ 0.95 | **0.6200** | ❌ FAIL |
| serious_error ≤ 0.01 | **0.0175** | ❌ FAIL |

Machine report: [quality_report.json](quality_report.json) (`ok: false`, rubric violations: 0). Judge identity: 4 shards, `opencode-shard-01…04`, model `x-preview-f-free` — not grok-4.6, not the drafter; FORBIDDEN list enforced by the apparatus.

## Denominator disclosure (why fidelity/equivalence look so low)

The regenerated pool's quarantine is dominated by **intentional unfills** (35 533 unfilled rows: denylisted slot/function words and senses left for a future draft wave). 131 of 400 sampled rows are empty-target `unfilled` cells; they are labelled `fail/fail/none` per the recorded convention but are absence of translation, not bad translation. On the **translated surface only** (n=269): fidelity **0.9926** ✅ · equivalence **0.9219** ❌ · serious **0.0260** ❌. The serious-error failure therefore stands on either denominator.

## The 7 serious errors — personally re-adjudicated, 0 overcalls, root-caused

1. `{%an%}` → `{%переселяться%}` (definition_gloss) — function-word span filled from wave-1-carried publication lexicon; `an` is not in `SHORT_GLOSS_DENYLIST`.
2. `{%einen%}` → `{%найти себе%}` — same class as (1).
3. `<ab>v. a.</ab>` → `<ab>т. е.</ab>` — **tracked-code defect**: `FORMULA_RU['v. a.'] = 'т. е.'` in `src/pwg_tm_generate.py`; German *v. a.* = *vor allem* («особенно»), not «то есть».
4. sense `{%einen%} … {%werth%}` partially translated, «найти себе» invented + German residue.
5. sense `{%ein best. Opfer%}` → «совершать» — noun gloss destroyed into a verb.
6. sense `{%alt%}` → «возраста» (+ `{%üppig%}` left German) — wrong meaning.
7. sense `{%habend%}` → «от» — relation inverted.

Root-cause families: (a) `SHORT_GLOSS_DENYLIST` does not cover the full harvested function-word inventory (`an`, `einen`, …), so wave-1 model noise survives inside the tracked publication TM and re-enters deterministically via exact source reuse; (b) one wrong pinned entry in `FORMULA_RU`; (c) residual model-drafted sense fills promoted in wave 1 that still sit in the publication surface.

## Ruling per the H2684 halt contract

One repair was permitted before the independent gate (the Jmd/Etwas placeholder fix — landed, pinned, and proven by 12 enumerated deterministic fills). After an independent-gate FAIL, **no second repair runs in this round**: the regenerated payloads stay local and regenerable ($0, `drafted=0`), nothing is promoted to any release surface, and the follow-up is named, not improvised:

1. Extend `SHORT_GLOSS_DENYLIST` to the corpus-harvested function-word inventory (kills re-ingest of (1)/(2) at the policy layer).
2. Correct `FORMULA_RU['v. a.']` → «особенно» + selftest pin.
3. Re-drain ($0) and run a fresh seeded independent gate; expect the serious class to collapse to the residual wave-1 sense fills, which need their own adjudication path.
