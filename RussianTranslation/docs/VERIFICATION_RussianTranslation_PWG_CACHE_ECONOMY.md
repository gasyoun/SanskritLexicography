# Verification — PWG prompt-cache economy

_Created: 13-08-2026 · Last updated: 13-08-2026_

Plan index: [PWG cache economy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md).

## Acceptance matrix

| Deliverable | Acceptance criterion | Proof |
|---|---|---|
| Compiler | Legacy fixtures reconstruct byte-for-byte; changed identity input changes request ID. | Golden-byte and mutation tests. |
| Migration | Legacy→v1 conversion deterministic, sealed, reversible; ambiguity fails closed. | Converter round-trip and refusal fixtures. |
| TM hierarchy | Whole-card and fragment hits still make zero calls; experimental namespace cannot resolve to canonical paths. | Existing TM tests plus namespace escape tests. |
| DeepSeek transport | ≥95% of bounded-cohort requests reach a parseable terminal response; zero unclassified failures. | Frozen Q3 telemetry and event-ledger report. |
| Billing integrity | Every call has evaluable usage/cost or explicit unevaluable stop; no missing value becomes zero. | Ledger schema checks and reconciliation. |
| Cache evidence | Exact-prefix cold/warm pairs show hit/miss, input/output, latency, accepted yield, retry amplification, and TTL/schedule context. | Derived cohort report. |
| Economy | ≥20% lower cost per mechanically clean card with an interval. | Predeclared baseline/new-route comparison. |
| Quality | Existing deterministic gates do not regress; blinded semantic review shows no meaningful increase in major errors. | Canonical audit plus blinded sheet/score. |
| Dependent lane | PREP/TM retrieval or corpus alignment emits the same economic schema and passes its acceptance gate. | Second-lane report. |
| Safety | No canonical TM/store write, default-model flip, peak dispatch, or promotion-fence change. | Path/hash assertions and git diff audit. |

## Experiment ladder

1. Credential-free tests and manifest sealing.
2. One DeepSeek Pro streaming capability canary.
3. Frozen 22-card Q3 rematch under the existing verdict rule.
4. Exact-prefix cold/warm cache A/B only if step 3 reaches ≥95% parseable terminal responses and quality gates pass.
5. Larger bounded cohort only if steps 3–4 pass and the declared remaining N/cost fits before the cutoff.
6. After 16-08-2026 16:00 UTC, off-peak only under the same sealed rules.

Do not reuse the failed `urllib` arm. Do not change the Q3 denominator or acceptance floor after observing results.

## Statistical and semantic bar

- Report arithmetic means, medians, totals, and a bootstrap confidence interval for cost per mechanically clean card. The ≥20% threshold applies to the point estimate; the interval must be shown rather than hidden.
- Stratify by cold/warm ordinal, retry variant, size/polysemy class, and output termination.
- Deterministic gates run on 100% of returned cards.
- Blind semantic review to route/cache state. Compare major-error incidence; adoption fails on a meaningful increase even if deterministic yield improves.
- A cache hit is an explanatory variable, not an accepted artifact. Failed, truncated, controller-pending, and null outputs stay in the economic denominator according to the predeclared rule.

## Commands

Exact filenames may be introduced by implementation, but verification must expose stable entry points equivalent to:

```powershell
python -m py_compile <changed-python-files>
python src/pilot/cache_contract_selftest.py
python src/pilot/deepseek_stream_selftest.py
python src/pilot/translation_memory.py selftest
python src/pilot/window_selftest.py
python src/pilot/lang_parity_check.py
python src/pilot/cache_experiment.py check --manifest <sealed-manifest>
python src/pilot/cache_report.py build --manifest <sealed-manifest> --events <events.jsonl>
python src/pilot/h1209/canonical_audit.py <slice-result> <manifest> --out <audit.json>
git diff --check
```

## Stop-gate tests

Tests must demonstrate refusal for: cost/call ceiling exhaustion; peak schedule after cutoff; served-model mismatch; request/prefix hash mismatch; missing or malformed usage; below-95% reliability; deterministic regression; experimental namespace escape; attempted canonical store/TM write; undeclared repair variant; and repeated systemic failure.

## Risks and spikes

| Risk | Treatment |
|---|---|
| Provider cache telemetry semantics change by model/version. | Preserve raw fields, version mappings, and refuse unknown pricing/usage semantics. |
| H1210 Flash cache hits do not imply Pro behavior. | Measure Pro cold/warm pairs; make no inherited claim. |
| Streaming fixes transport but Pro remains too slow or verbose. | Overall deadline plus deterministic compact/increase/partition ladder. |
| Prefix grouping changes worklist order and cohort mix. | Predeclare groups and compare within exact prefix/strata. |
| Retrieved TM/evidence stales identity. | Hash every relevant asset; invalidate on change. |
| Converter silently loses legacy meaning. | Non-representable fields are a hard refusal, not a warning. |
| Experimental TM contaminates canonical state. | Separate root, namespace marker, path assertions, no promoter integration. |
| Concurrent PWG work alters builders during the experiment. | Isolated worktree; seal source commit and prompt bytes; rebase only before sealing. |
| Deadline pressure encourages post-hoc widening. | N, ceilings, ladder, and verdict rule sealed before token 1. |

## Autonomy-readiness checklist

- [x] Every wave-1 deliverable has an architecture contract.
- [x] Ordered implementation steps are specified in the implementation layer.
- [x] Every deliverable has an acceptance criterion and proof command/flow.
- [x] Risks and spikes are identified.
- [x] No blocking decision remains; ambiguity defaults are explicit.
- [x] Existing TM, prompt builders, cost tools, and audit gates are reused.
- [x] Canonical promotion and sibling propagation are outside the fence.

_Dr. Mārcis Gasūns_
