# R3434 independent gate verdict — FAIL overall (honest halt, no second repair); the targeted serious-error floor PASSES

_Created: 24-08-2026 · Session: H3434 execution · Seed 3434 (new vs R15's 3299) · n=400 stratified over the regenerated pool_

## Verdict lines (floors unchanged: fidelity ≥98% · equivalence ≥95% · serious ≤1%)

| floor | full n=400 | translated surface only (n=267) |
|---|---|---|
| fidelity ≥ 0.98 | **0.6475** ❌ | **0.9700** ❌ |
| equivalence ≥ 0.95 | **0.6075** ❌ | **0.9101** ❌ |
| serious_error ≤ 0.01 | **0.0075** ✅ | 0.0112 ❌ |

Machine report: [quality_report.json](quality_report.json) (`ok: false`, rubric violations: 0).

Judge identity: 4 shards, `opencode-shard-01…04`, model `x-preview-f-free` — not grok-4.6,
not the drafter; FORBIDDEN list enforced by the apparatus (`independence_errors` clean).

## What the two repairs bought

R15 (seed 3299) convicted **7 serious rows / 400 = 1.75%**; R3434 measures **3/400 = 0.75% ✅**
under the floor. The three R15 root causes are closed at the policy layer:

1. `{%an%}` → «переселяться» — now `unfilled` (denylist + exact-reuse guard).
2. `{%einen%}` → «найти себе» — now `unfilled`; the partial-invention sense row
   (`{%einen%} … {%werth%}`) is also unfilled.
3. `<ab>v. a.</ab>` → `<ab>т. е.</ab>` — now `<ab>особенно</ab>` (502 promoted rows
   corrected; zero «т. е.» renders remain).

Denominator disclosure (same convention as R15): 133/400 sampled rows are empty-target
`unfilled` cells — intentional absence of translation (denylisted slots and senses left for
a future draft wave), labelled fail/fail/none per the recorded convention. On the
translated surface only (n=267) serious is 3/267 = 1.12%; fidelity/equivalence remain
below their floors there too.

## The 3 remaining serious rows — all root cause family (c), out of scope per H3434

1. `{%ein <ab>best.</ab> Opfer%}` → «совершать» (definition_gloss, wave-1-carried fill)
2. sense udBid: same `{%ein best. Opfer%}` → «совершать» inside the sense line
3. sense dvika: `{%habend%}` → «от» (+ German residue)

These are residual model-drafted sense/gloss fills promoted into the publication TM in
wave 1 and carried by `sense_merge` from tracked canonical rows — not re-ingested noise.
H3434 names this class out of scope unless the gate still fails on it; it does, so per the
halt contract: **report, do not improvise a second repair.**

## Ruling per the H2684 halt contract

The regenerated payloads stay local and regenerable ($0, `drafted=0`), nothing is promoted
to any release surface. The named follow-up is an adjudication/curation path over the
wave-1-carried sense fills inside the tracked publication TM (the ~residual class above),
plus the standing question of whether intentional unfills should keep counting against the
fidelity/equivalence floors on the full-n denominator.

## Provenance

- Repairs merged via worktree PR (branch `h3434-pwgtm-wave3-denylist-formula`).
- Gates at PR time: policy+generate selftests green; pytest 140 passed
  (test_nws_ls_markup/test_rv_spine skipped: pre-existing `csl_pyutil` env gap, fails
  identically on pristine master); window_selftest **213/213** after lang_parity re-stamp
  (`pwg_tm_grok46_wave1_generate_h2684` INTENTIONAL-DIVERGENCE verdict re-verified, holds).
- Regeneration: `$0`, ledger calls=0, prompt_sha256 55ae9562… unchanged;
  [reconciliation_delta_vs_h3299.md](reconciliation_delta_vs_h3299.md).
