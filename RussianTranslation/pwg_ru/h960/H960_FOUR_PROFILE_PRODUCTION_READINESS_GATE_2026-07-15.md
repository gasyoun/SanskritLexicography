# H960 — PWG→Russian four-profile production-readiness gate (offline)

_Created: 15-07-2026 · Last updated: 15-07-2026_

**Verdict: `OFFLINE-READINESS = EARNED` · `FOUR-PROFILE NONSTOP SCALE = NO-GO (owner-gated live ladder is the only residue)`.**

H960 had two charges: **verify H920**, and **earn four-profile nonstop PWG-RU scale**. The first is
complete — every offline gate reproduces green. The second is earned *as far as offline work can take
it*: the six load-bearing gaps the [H911 LOCAL-READINESS gate](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md)
(FAIL) and the post-H920 Codex audit surfaced are closed at the offline/deterministic layer, each pinned
by a selftest. The residual NO-GO is **exactly** the owner-gated live ladder
(auth → latency → targeted canary → 10 → 20 → multi-profile), which needs real Max logins (c5/c6 were
logged out on 15-07) and live generation — categorically out of scope for an offline session.

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode. Offline code/analysis only — **no** live
translation generation, Claude Workflow/API call, account login, network probe, promotion, store/TM
mutation, or orchestrator run against real accounts. Delivered from a worktree off `origin/master`.

## A. H920 verified — the offline codebase is green

Reproduced from the current tree (`RussianTranslation/`), independent of the Codex audit that recorded
the gate:

| Offline gate | Result |
|---|---|
| `window_selftest.py` (incl. all 4 `test_h920_*` sense-count guard tests) | **OK** |
| `lang_parity_check.py` | **49 entries, all verdicts complete, no drift** |
| `h809_selftest.py` | **OK** |
| `headless_worker_selftest.py` | **PASS** |
| `max_account_orchestrator_selftest.py` (D-G one-active-job, D-G REAL race ×8, D-I exactly-once) | **PASS** |
| `run_observability_selftest.py` | **PASS** |
| `economy_ledger_selftest.py` (new) · `bounded_supervisor_selftest.py` (new) | **PASS** |

H920's merged deliverable (the deterministic SAN-LOSS sense-count guard, PR #467) is intact and its
guard fires on the darvI 2/3 shape while skipping null/pre-stamp cards.

## B. The six load-bearing gaps — closed offline

Each was audited against the real code and its proposed fix adversarially verified for
offline-testability before implementation. Every new guard is **SOFT / report-only by default**
(telemetry, no reject/requeue) — arming any hard reject is a deliberate owner-gated step, because
turning a silent pass into a reject changes throughput and must be measured on live traffic first.

| # | Gap (H911 lineage) | Offline fix landed | Selftest | Live residue (owner-gated) |
|---|---|---|---|---|
| 1 | **`accept()` sense-count** — H920's explicitly-deferred deepest fix (SAN-LOSS backlog #1) | `gen_opt_harness2.py` stamps the hardened `source_senses`; `accept()` records a `SANLOSS_SHORTFALLS` shortfall (emitted<expected, exp>0) — **soft**, `SANLOSS_HARD_REJECT` owner-gated. Counter hardened to skip cross-reference ordinals (~4.78% FP class) | `test_h960_accept_sanloss_soft_gate` (node, extracts the real `accept()`); 3 cross-ref fixtures in `sense_count._selftest` | measure the live shortfall/false-flag rate, then arm the reject+requeue |
| 2 | **Grammar `{Tn}` multiset** — dropped `<lex>` grammar span passes the `<ls>/{#` count | `accept()` compares the emitted `{Tn}` multiset to the source skeleton's (the heal path's existing check, brought to the main path) — `TNMASK_MISMATCHES`, **soft**, `TNMASK_HARD_REJECT` owner-gated | same node selftest (drop → soft telemetry while `<ls>/{#` passes; reorder-ok; armed → reject) | measure incidence (incl. self-expansion), then arm |
| 3 | **German `{#..#}` span drop** — H911 backlog #3 (`untranslated_braced_german_gloss` family) | `prompt_rule_audit.dropped_sanskrit_span` — content-multiset diff of source-vs-target `{#..#}`, **LOW / report-only** (never in `HIGH_CONFIDENCE_RISKS`), excluding structural head-label spans (the measured 95%-FP class) | `test_h960_dropped_sanskrit_span` (mid-drop fires; head/root/retained silent; LOW) | measure the live false-flag rate, then consider arming a requeue |
| 4 | **Economy telemetry** — H911 backlog #4; two INCONCLUSIVE economy gates unmeasurable | `economy_ledger.py` reduces the frozen `generation_api_probe_log.jsonl` to `agents_per_clean` + a bounded `$/clean` band, imports `parse_workflow_cost.PRICE`, `gate()` on aggregate breach | `economy_ledger_selftest.py` (8 tests, real-log integration) | exact `$/clean` needs the live per-agent cache-split transcript; blessing the ceilings is a human call |
| 5 | **`staged-run` four-profile** — hard-capped to one account | `max_account_orchestrator.py`: guard relaxed to ≥1; `probe_fleet()` probes each account, STOP-on-any-NO-GO (`--drop-unhealthy` opt-in), `probe_latency_ms` rewired to a per-account map | `max_account_orchestrator_selftest.py` (+N=4 fan-out, one-active, recover exactly-once, probe_fleet unit, N=1 regression) | the real 4-account login + live staged-run loop |
| 6 | **Bounded supervisor** — no nonstop drain loop | `bounded_supervisor.py` — injectable `run_window` seam; bounds on window-count / budget / clean-target / consecutive-empty; requeues partials; atomic checkpoint + crash resume | `bounded_supervisor_selftest.py` (8 cases incl. crash-resume, satisfied-not-failed) | wire `cmd_staged_run` to delegate with the live `run_window` |

## C. Readiness gates — what H960 moves

The [H911 gate table](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md) is the reference. H960 **hardens the instrumentation** behind
those gates; it does not, and cannot offline, flip the measured quality FAIL to a PASS.

| Gate | H911 | After H960 (offline) |
|---|---|---|
| audit-clean subcards ≥ 80% | FAIL (~62%) | **still measured on live traffic** — the SAN-LOSS/`{Tn}`/`{#..#}` guards now make the loss *visible* (were silent passes); the clean-rate GO is a live-run measurement |
| fidelity rejects < 5% | FAIL (SAN-LOSS 15–25%) | detection hardened + cross-ref FP removed; arming the rejects is owner-gated |
| economy observed calls/clean ≤ 1.75 | INCONCLUSIVE (`not_recoverable`) | **now measurable**: `economy_ledger` derives `agents_per_clean` from the frozen log (a metric H911 called unrecoverable actually sits in the probe log) |
| economy observed $/clean ≤ $0.75 | INCONCLUSIVE | **bounded band now derivable** offline; exact point value stays live-gated |
| four-account scale | blocked | scheduler is N-account-capable + proven offline (fair-claim / one-active / exactly-once / recovery); real login+run is the residue |

**Honest framing:** hardening a guard converts a *silent* SAN-LOSS pass into a *visible* requeue. That
raises fidelity but does not by itself lift the clean-rate FAIL — the model must actually stop dropping
senses, which is a live quality measurement. So H960 earns the **production-readiness scaffolding** and
leaves one gate: the live ladder.

## D. The owner-gated live ladder (the only residual NO-GO)

H255 stays frozen until this passes, in order, each stage gating the next:

1. **auth** — owner logs in the Max profiles (`claude /login` per `CLAUDE_CONFIG_DIR`); c5/c6 were logged out on 15-07.
2. **latency** — `probe_fleet` per account within the 30 s ceiling (independent of H909's home-route latency, still WAITING ON OWNER).
3. **targeted canary** — the darvI/gaRanA SAN-LOSS canaries, now with the accept() shortfall telemetry live, to measure the true drop rate and the guard's false-flag rate.
4. **arm the hard rejects** — once the false-flag rate is acceptably low, flip `SANLOSS_HARD_REJECT` / `TNMASK_HARD_REJECT` and promote `dropped_sanskrit_span` to a requeue trigger.
5. **10 → 20** — bounded-supervisor drains, `economy_ledger` measuring real `agents_per_clean` / `$/clean` against the ceilings.
6. **multi-profile** — the four-profile staged-run loop across c1/c4/c5/c6.

None of stages 1–6 is offline-earnable; all are delivered *ready* by H960.

## Limitations

- Every guard is soft/report-only; **no** live quality-rate improvement is claimed — only that the loss
  is now instrumented. The clean-rate ≥80% GO is a live measurement H960 does not manufacture.
- `economy_ledger`'s `$/clean` is a **bounded band** (blunt `subagent_tokens` totalTokens, cache-split
  not recoverable offline; the in-band ceiling excludes the output-token premium — a true worst-case
  `true_upper_output_rate` is exposed separately).
- `bounded_supervisor` is a **parallel** module with an injectable seam; the live `cmd_staged_run` loop
  is not yet delegated to it (deliberate — that wiring needs a live account).
- The counter hardening is a strict FP reduction validated on the cited promoted-store shapes; a source
  whose only sense markers are non-line-opening under-counts to 0 (skipped, never a false shortfall).

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`) as the H960 executor, Ultracode; offline code/analysis, no live generation or store mutation._

_Dr. Mārcis Gasūns_
