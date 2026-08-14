# PWG prompt-cache economy — execution plan

_Created: 13-08-2026 · Last updated: 14-08-2026_

## Execution status

The plan and CI fix merged in [PR #1685](https://github.com/gasyoun/SanskritLexicography/pull/1685). The transport canary, frozen Pro rematch, and Flash PREP first-200 baseline then shipped in [PR #1686](https://github.com/gasyoun/SanskritLexicography/pull/1686), [PR #1690](https://github.com/gasyoun/SanskritLexicography/pull/1690), and [PR #1693](https://github.com/gasyoun/SanskritLexicography/pull/1693). The old monolithic Codex execution brief is superseded; remaining work is deliberately serial:

1. [H2702 (Grok 4.6) — PWG cache economy residual A: provider-neutral contracts, identity, migration, and ledger](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2702-Grok_SanskritLexicography_pwg-cache-economy-contract-foundation_14.08.26.md)
2. [H2703 (Grok 4.6) — PWG cache economy residual B: exact-request generation cold/warm proof](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2703-Grok_SanskritLexicography_pwg-cache-economy-generation-cold-warm_14.08.26.md), blocked until H2702 merges
3. [H2704 (Grok 4.6) — PWG cache economy residual C: PREP/TM proof, bounded L3, and adoption verdict](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2704-Grok_SanskritLexicography_pwg-cache-economy-prep-tm-adoption-verdict_14.08.26.md), blocked until H2703 merges

## Goal

Reduce total cost per useful PWG artifact, starting with PWG→Russian generation and its complete dependency closure: whole-card and fragment translation memory, corpus/TMX inputs, PREP/context construction, DeepSeek generation, retries, controllers, and judges. Wave 1 exploits the remaining pre-price-change DeepSeek window, then continues only in authorized off-peak windows. It proves the design locally before proposing organization-wide reuse.

## Plan layers

- [Roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md)
- [Architecture](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_PWG_CACHE_ECONOMY.md)
- [Implementation](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_PWG_CACHE_ECONOMY.md)
- [Verification](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_PWG_CACHE_ECONOMY.md)
- [Metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.meta.md)

## Evidence and prior-art verdict

Verdict: **PARTIAL — reuse the existing machinery and build only the missing common contract and instrumentation.**

- Provider caching already works strongly in the H1210 DeepSeek lane: the 40-card Flash run recorded 512,640 cache-hit versus 78,622 cache-miss input tokens, but cost per clean card remained poor because 85% of cards died on output truncation.
- Whole-card TM and fragment TM already eliminate calls on content-addressed hits. They remain the first two short-circuits; this plan does not rebuild them.
- Claude CLI v2.1.223 reused a cold prefix across six later calls in the H2250 sequence; five created zero new cache tokens. The older “never reused” statement in `RussianTranslation/AGENTS.md` is stale and must be synchronized.
- Bare cwd, safe mode, stable-left prompt order, TTL-aware pricing, and offline-ready Claude Message Batches already exist. Wave 1 consumes them rather than re-implementing them.
- DeepSeek V4 Pro's 13-08 `urllib` rematch failed in transport, but the replacement streaming client subsequently passed its 3/3 canary and the frozen 22-card rematch reached 21/22 deterministic-clean. Those gates are complete and must not be rerun by the residual handoffs.
- No existing component supplies one provider-neutral prompt identity, retry-lineage ledger, prefix-group scheduler, or accepted-yield economics across generation and dependent lanes. That is the named gap.

Sources of record: [prompt-caching playbook](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md), [operator runbook](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md), [H2652 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/H2652_v4pro_rematch/REPORT.md), [E1 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/E1_FLASH_0731_VS_C4_REPORT_13-08-2026.md), and [Message Batches contract](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/BATCH_PROCESSING_PWG_RU.md).

## Decisions taken — 29 rulings

| # | Ruling | Rationale / effect |
|---:|---|---|
| 1 | Optimize total useful-output cost. | Tokens are inputs; accepted artifacts are the outcome. |
| 2 | Audit the full PWG dependency closure. | Local optimization must not move spend into TM, PREP, retries, or judging. |
| 3 | Prioritize paid experiments before the DeepSeek price change. | Use the already-authorized PWG allowance while the flat card remains. |
| 4 | Success is lower cost per accepted artifact with no quality regression and fewer repeated calls. | Cache ratio alone cannot win. |
| 5 | Prove on PWG, then extract an organization-wide standard. | Avoid premature shared infrastructure. |
| 6 | Use layered content addressing. | Identity binds provider/model, prompt/schema, prefix, volatile input, and relevant data/TM hashes. |
| 7 | Build one provider-neutral prompt compiler. | It emits stable prefix, volatile tail, hashes, estimates, and provider envelope. |
| 8 | Use hierarchical short-circuiting. | Whole-card TM → fragment TM → retrieved evidence → provider cache → generation. |
| 9 | Retry exact sealed requests unless a declared repair variant is required. | Every variant gets a new identity and lineage edge. |
| 10 | Replace DeepSeek transport with a streaming compatible client and persistent connections. | The current blocker is transport, not measured translation quality. |
| 11 | Implement PWG-local interfaces with a provider-neutral schema. | Extract only after measured success. |
| 12 | Run the DeepSeek V4 Pro transport requalification first. | It unblocks all later Pro evidence. |
| 13 | Use a gated experiment ladder. | Canary → frozen Q3 → cache A/B → larger bounded cohort only on GO. |
| 14 | Schedule exact prefix-hash/model groups contiguously. | Maximize warm reuse while preserving cold/warm attribution. |
| 15 | Store evidence in append-only JSONL plus sealed manifests. | Summaries are derived, not mutable truth. |
| 16 | Repair output overruns via a deterministic escalation ladder. | Compact response → bounded ceiling increase → partition card/fragment. |
| 17 | Permit a manifest/schema migration with a converter. | Side-by-side migration is explicit and reversible. |
| 18 | Require at least 20% lower cost per mechanically clean card. | Adoption needs a material saving with an interval, not noise. |
| 19 | Block on deterministic regression or meaningful blinded major-error increase. | Economy never weakens publication quality. |
| 20 | Require at least 95% parseable terminal responses. | Transport must be dependable enough for scale. |
| 21 | Prove caching with exact-prefix cold/warm pairs and accepted-yield economics. | Provider hit ratio alone is insufficient. |
| 22 | Prove generation plus one dependent lane before extraction. | Shared design needs two production-shaped consumers. |
| 23 | After the cutoff, stop peak execution and continue off-peak only. | This is the standing human price ruling. |
| 24 | On ambiguity, use the marked default and log it; park irreversible or quality-affecting cases. | Keeps unattended execution moving safely. |
| 25 | Stop on any named spend, identity, reliability, quality, mutation, or systemic-failure gate. | See the autonomy contract below. |
| 26 | Work in isolation, milestone-commit, push, PR, and merge only after all gates pass. | Concurrent PWG work exists; delivery remains evidence-gated. |
| 27 | Code/tests/manifests/ledgers/docs/migration may change; an experimental TM namespace may be written. | Canonical TM/store remain fenced. |
| 28 | Do not promote canonical data, flip models, run monster/Q4 unattended, spend at peak, touch unrelated repos, or weaken gates. | Hard fence. |
| 29 | Author the provider-neutral contract and extraction plan only; do not port siblings in wave 1. | Propagation follows proof. |

## Autonomy contract — verbatim operational form

### On ambiguity

Apply the plan's marked default, record the decision and evidence in the append-only ledger, and continue. Park only an irreversible or quality-affecting ambiguity. Never silently change a predeclared experiment, identity, denominator, or acceptance rule.

### Immediate stop conditions

Stop paid execution when any of these occurs:

- call or cost ceiling reached;
- any DeepSeek peak window after 16-08-2026 16:00 UTC;
- served-model mismatch;
- unsealed or identity-mismatched request;
- unevaluable billing or a missing-usage value represented as zero;
- parseable terminal response rate below 95% on the bounded cohort;
- deterministic or semantic quality regression;
- unexpected canonical TM/store write;
- repeated systemic failure under the predeclared retry ladder.

### Commit and delivery authority

Use an isolated worktree and `codex/` branch. Make milestone commits, push, open a PR, and merge only when every acceptance gate passes and no human-review gate remains. A failed or incomplete experiment may still deliver code and evidence by PR, but must not claim route adoption.

### Mutation authority

Allowed: PWG-local code, tests, versioned schemas, converters, manifests, append-only experiment ledgers, derived reports, documentation, and a separate experimental TM namespace. Forbidden: canonical PWG store or TM promotion.

### Do-not-touch fence

No canonical PWG store/TM promotion; no default-model flip; no unattended Q4 or monster-head run; no peak DeepSeek spend; no unrelated repository changes; no weakening cost, quality, audit, or promotion gates. Wave 1 authors the provider-neutral contract and extraction plan but modifies no sibling repository.

## Definition of done

Wave 1 is done only when the architecture, implementation, verification, and risk coverage in the four linked documents all pass the autonomy-readiness gate; the streaming transport reaches the declared reliability bar; generation and one dependent lane emit comparable accepted-yield economics; and the route either earns the ≥20% adoption verdict or is rejected with durable evidence. Canonical promotion is not part of done.

_Dr. Mārcis Gasūns_
