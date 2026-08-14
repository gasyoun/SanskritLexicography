# Roadmap — PWG prompt-cache economy, 2026 Q3

_Created: 13-08-2026 · Last updated: 14-08-2026_

Plan index: [PWG cache economy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md).

## Live execution chain

- **Completed:** streaming transport and 3/3 canary ([PR #1686](https://github.com/gasyoun/SanskritLexicography/pull/1686)); frozen Pro Q3 rematch, 21/22 deterministic-clean ([PR #1690](https://github.com/gasyoun/SanskritLexicography/pull/1690)); Flash PREP first-200, 200/200 parseable ([PR #1693](https://github.com/gasyoun/SanskritLexicography/pull/1693)). Do not repeat these paid gates.
- **Next:** [H2702 (Grok 4.6) — PWG cache economy residual A: provider-neutral contracts, identity, migration, and ledger](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2702-Grok_SanskritLexicography_pwg-cache-economy-contract-foundation_14.08.26.md).
- **Then:** [H2703 (Grok 4.6) — PWG cache economy residual B: exact-request generation cold/warm proof](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2703-Grok_SanskritLexicography_pwg-cache-economy-generation-cold-warm_14.08.26.md), after H2702 merges.
- **Finally:** [H2704 (Grok 4.6) — PWG cache economy residual C: PREP/TM proof, bounded L3, and adoption verdict](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2704-Grok_SanskritLexicography_pwg-cache-economy-prep-tm-adoption-verdict_14.08.26.md), after H2703 merges.

## Wave 0 — freeze truth and migration seam

Deliverables:

- reconcile stale cache claims against the H2250 CLI v2.1.223 measurement;
- inventory prompt builders, TM short-circuits, PREP/context, DeepSeek, controller, judge, retry, pricing, and promotion boundaries;
- freeze `pwg.cache_request.v1`, `pwg.cache_event.v1`, and the legacy→v1 converter contract;
- create an experimental TM namespace isolated from canonical TM/store.

Unblocks: transport implementation and comparable telemetry. Acceptance: byte-identical legacy prompt reconstruction on committed fixtures; converter round-trip; zero canonical data writes.

## Wave 1 — exploit the bounded DeepSeek window

Deliverables, in this order:

1. replace the Pro `urllib` path with streaming, persistent transport;
2. run one capability canary;
3. rerun the frozen 22-card Q3 rematch under its predeclared rules;
4. if reliability and quality gates pass, run exact-prefix cold/warm cache pairs;
5. only on GO, run a larger bounded cohort before the cutoff;
6. after 16-08-2026 16:00 UTC, execute only in the standing off-peak windows.

Unblocks: a real cost-per-clean-card verdict for Pro. Acceptance: ≥95% parseable terminal responses, attributable usage/cost, exact served-model evidence, no TM/store promotion.

## Wave 2 — prove the dependent lane

Apply the same compiler, identity, ledger, scheduler, and escalation rules to one dependent production-shaped consumer. Default: PREP/TM retrieval and context construction, because it exercises data hashes and hierarchical short-circuiting without creating another generative publication path. Corpus alignment is the fallback if PREP does not provide enough calls for cold/warm comparison.

Unblocks: shared-contract eligibility. Acceptance: generation and dependent lane both report cold/warm pairs, retry amplification, and cost per accepted artifact under the same schema.

## Wave 3 — adoption verdict and extraction design

- adopt only if cost per mechanically clean card improves by ≥20% with a reported interval and no quality regression;
- otherwise retain the instrumentation and migration seam, reject the route with evidence, and keep the current default;
- author the provider-neutral contract, compatibility matrix, and extraction backlog;
- do not modify sibling repositories in this wave.

## Later waves

- extract a shared package after two PWG lanes prove the contract;
- select a second repository in a separate ruled plan;
- consider Claude Message Batches when incremental API cash or asynchronous throughput beats remaining subscription credit;
- revisit semantic/deduplicated cache retrieval only as an explicit research experiment, never as identity substitution.

## Non-goals

- maximizing cache-hit ratio in isolation;
- rebuilding whole-card or fragment TM;
- multi-card Claude CLI batching merely to share cache;
- trimming translation instructions with known quality loss;
- raising timeouts to hide a hang class;
- canonical TM/store promotion;
- default-model change;
- peak DeepSeek spend after the cutoff;
- unattended Q4 or monster heads;
- sibling-repository ports.

_Dr. Mārcis Gasūns_
