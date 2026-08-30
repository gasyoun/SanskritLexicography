# VERIFICATION — PWG translation control-plane strangler

_Created: 30-08-2026 · Last updated: 30-08-2026_

Parent: [PLAN — PWG translation control-plane strangler](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md).

## Acceptance matrix

| ID | Criterion | Proof |
|---|---|---|
| V1 | One provider request creates exactly one reserved and finalized `Call` row | Unit tests covering success, empty result, malformed result, timeout, and exception. |
| V2 | Cost/call ceilings refuse before provider I/O | Fake adapter call counter remains zero. |
| V3 | Route, requested model, served model, and usage are sealed and distinguish xAI, DeepSeek, Claude shadow, deterministic reuse, and imported drafts | Contract tests plus receipt snapshot. |
| V4 | Database transitions are transactional and restartable | Kill/reopen tests at every transition. |
| V5 | Audit functions make no filesystem changes | Before/after tree digest equality around every audit test. |
| V6 | Refill/migration cannot lose a row across interruption | Fault tests around prepare, first store commit, second store commit, receipt, and restart. |
| V7 | Recursive validator scans every row and every nested payload | A middle-row `{Tn}` fixture fails; absence of `jsonschema` fails closed when schema validation is required. |
| V8 | Existing 79 placeholder-bearing rows (609 occurrences) are reported/fenced without mutation | Read-only report count and hashes; canonical file digest unchanged. |
| V9 | Four legacy/new replays have zero unexplained contract mismatches | Checked comparison reports for clean, partial, failure, and interrupted-promotion campaigns. |
| V10 | Claude behavior is unchanged | Existing window, headless, coordinator, promotion, and language-parity suites stay green. |
| V11 | Direct legacy writers route through the facade or refuse | CLI compatibility tests and call-site search. |
| V12 | Independent review approves money/store paths | Review receipt names commit, reviewer, findings, and disposition. |
| V13 | Live canaries obey the fence | At most one xAI plus one DeepSeek call, `max_calls=2`, USD 4 total, no retries, non-promotable artifacts, store digest unchanged. |

## Four frozen replay campaigns

1. **Clean success:** one card/fragment set with complete result and evaluable usage.
2. **Partial/requeue:** mixed clean, transient, and defect outcomes with explicit child jobs.
3. **Provider failure:** timeout and malformed/empty response; billed usage, when present, remains
   attributable and the call finalizes once.
4. **Interrupted promotion:** inject interruption after each journal phase and prove startup
   reconciliation produces the same final hashes exactly once.

Each replay compares selected jobs, transitions, attempts, calls, route/model bindings, artifact
hashes, verdicts, requeue decisions, promotion delta, and final store/TM projection.

## Fault-injection matrix

| Boundary | Required result |
|---|---|
| Before provider request | Reservation can be released/closed without a call; zero spend recorded. |
| After paid response, before parse | Raw response and usage survive; restart never replays automatically. |
| After parse, before seal | Attempt is incomplete and recoverable from raw response. |
| After artifact seal, before verdict | Restart audits the same hash without a provider call. |
| After verdict, before apply | No canonical mutation. |
| After source/quarantine prepare | Neither side changes until journal commit. |
| After store commit | Journal recovery rebuilds/validates derived TM exactly once. |
| After derived validation | Coordinator commit resumes without rewriting store/TM. |
| After coordinator commit | Finalization is idempotent. |

## Planned proof commands

```powershell
python -m unittest discover -s RussianTranslation/tests -p "test_pwg_pipeline_*.py"
python RussianTranslation/src/pilot/window_selftest.py
python RussianTranslation/src/pilot/headless_worker_selftest.py
python RussianTranslation/src/pilot/bounded_staged_run_selftest.py
python RussianTranslation/src/pilot/max_account_orchestrator_selftest.py
python RussianTranslation/src/promote_final_cards_selftest.py
python RussianTranslation/src/pilot/promotion_journal_selftest.py
python RussianTranslation/src/pilot/lang_parity_check.py
python -m pwg_pipeline replay --matrix RussianTranslation/tests/fixtures/pwg_pipeline/replay_matrix.json
python -m pwg_pipeline validate --canonical RussianTranslation/release/pwg_tm_canonical/canonical.v1.jsonl --recursive --read-only
```

The canary command is run only after all offline commands and independent review pass:

```powershell
python -m pwg_pipeline canary --providers xai,deepseek --max-calls 2 --cost-ceiling-usd 4 --no-retry --non-promotable
```

## Canary GO/NO-GO

**GO** requires both provider calls, if attempted, to have exact route/model binding, evaluable
provider usage, sealed raw and parsed artifacts, zero retries, total cost at or below USD 4, and
no canonical file digest change. An unavailable provider may stop its adapter track, but the other
provider must not consume the unused call as a retry.

**NO-GO** is any missing/derived-only usage, route mismatch, substituted model, timeout without
terminal accounting, unexpected extra call, attempted promotion, canonical digest change, or
unexplained shadow mismatch.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| New database becomes a sixth state authority | Redesign worsens the problem | Import/shadow/cut over one stage; old writer disabled as new stage becomes authoritative. |
| Adapter abstraction hides provider differences | Incorrect accounting or retry behavior | Small protocol; provider-specific usage/result fixtures; no kernel-owned semantic retry. |
| Pure-audit extraction changes verdicts | Requeue/promotion drift | Frozen replay comparison before any caller cutover. |
| Existing placeholder rows tempt an in-scope repair | Canonical mutation | Report and fence only; route repair separately. |
| Compatibility shims become permanent | Two operator surfaces persist | Deprecation telemetry and explicit removal criterion. |
| Canary spends without useful evidence | Money lost | Offline gate, independent review, two-call/USD4 ceiling, no retry. |
| SQLite contention on Windows | Stalls or partial state | WAL, busy timeout, explicit short transactions, crash tests. |

## Cutover verdict format

The Wave-1 close report must state `GO`, `NO-GO`, or `PARTIAL`. `GO` requires V1–V13. `PARTIAL`
may preserve landed offline infrastructure but authorizes no legacy-writer shutdown. `NO-GO`
preserves all evidence and leaves the existing production route authoritative.

_Dr. Mārcis Gasūns_
