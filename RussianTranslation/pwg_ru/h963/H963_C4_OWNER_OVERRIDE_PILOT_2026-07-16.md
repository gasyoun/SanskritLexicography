# H963 — single-profile c4 owner-override bounded pilot

_Created: 16-07-2026 · Last updated: 16-07-2026_

**Verdict: `C4 PILOT GENERATED — NOT PROMOTED`.**

**Exact failed gate: the real nominal translate agent hit the 180 s kill ceiling
(`kill-timeout 180s @ skelBytes=5606`) → both real cards null → clean rate 0 % against an
80 % floor → no promotion.**

This is a **single-profile c4 owner-override pilot**. It is **not** a health PASS, **not** a
two-profile or four-profile run, and **not** an H963 production-readiness PASS. It was an
explicit owner override of the 30-second latency/throughput launch prohibition, taken
**after** a measured latency NO-GO
([Gate-0 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md),
warm-up 53 290 ms / measured 104 870 ms). It does not change the repository's default health
gate, erase either historical NO-GO, or establish production readiness.

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode, orchestrating generation calls on the
exact model `claude-sonnet-5`. Clean worktree off `origin/master`
[`9d7d00d0`](https://github.com/gasyoun/SanskritLexicography/commit/9d7d00d0).

## ⚠️ PROTOCOL DEVIATION — the two manifests ran CONCURRENTLY, not serially

**Manifest A and Manifest B were launched back-to-back without waiting for A to finish, so the two
calls overlapped on the c4 profile. The owner brief required serial execution.** `max_wide=1` was
honoured *within* each manifest (and is a within-manifest dispatch cap), but it does **not**
serialise two separately-launched manifests — the executor's error, not a tooling failure.

Consequences, stated plainly:

- **These timings are NOT serial c4 throughput or economy evidence** and must not be quoted as such.
- **This pilot cannot justify widening concurrency** in any direction.
- **The real call's 180 s kill-timeout was measured under concurrent load from this pilot's own
  canary call.** How much of the timeout is attributable to that self-contention versus c4's
  baseline latency is **unresolved and unresolvable from this run** — settling it would need a
  serial re-run, which is a prohibited reroll and was not performed.
- This is the **same self-contention confound** flagged in the Gate-0 report, reintroduced at a
  second level (pilot-call vs pilot-call, on top of session-vs-subprocess).

The **NOT PROMOTED** verdict does not depend on this: 0 clean real rows is 0 clean real rows, and
the promotion gate is a clean-rate floor, not a latency measurement.

## Headline result — the latency NO-GO had a production consequence

The Gate-0 NO-GO was not academic. A trivial 6 828 B `{"ok": true}` probe took **104 870 ms** on
c4. A **real** card (masked skeleton 5 606 B) never returned: it was abandoned at the **180 000 ms
kill ceiling**. The health gate anticipated this failure class.

**Narrowed by the deviation above:** the honest claim is that a real card did **not** finish inside
180 s **under concurrent load from a second in-flight call on the same profile**. This run does
**not** establish that a real card cannot finish inside 180 s on a quiet, serially-driven c4 —
that remains untested.

| Run | agents | wall | cards | ok | null | kill-timeouts | conn errors |
|---|---|---|---|---|---|---|---|
| canary (`h963_c4_canary`) | 1 / 1 | ~118 s | 1 | **1** | 0 | 0 | 0 |
| real (`h963_c4_real`) | 1 / 1 | ~206 s | 2 | **0** | **2** | **1** | 0 |

_Wall-clock figures above are **overlapping**, not serial — see the deviation notice._

## Scope actually executed

Per the owner's mid-session correction: **`no_pwg_w08` was rejected and H255/no-PWG stays frozen**
— no real row was taken from that queue. Real candidates came from the **nominal-core worklist**
(`nominals_worklist.py` over the Tier-2 LEADS core
[`pril10.slp1.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lexical_cores/pril10.slp1.txt)),
which already excludes store-promoted lemmas by cumulative dedup (H179).

**Two manifests, not one.** The execution-manifest schema `pwg.headless_execution_manifest.v1`
carries no provenance/synthetic discriminator field — one manifest could only distinguish the
synthetic canary by key-name convention, not by any manifest-level guarantee. So per the owner's
conditional the modes were **not forced together**: two attempt-specific manifests inside one
bounded pilot, each with `max_agents: 1` (**2 agents total**), each with exactly one root, making
provenance unambiguous by construction.

### Selection — rank is scholarly priority, never cost order

Worklist rank was **not** allowed to drive cost. The top-ranked band-5 ultra-core heads were
**rejected**: `kAla` / `brahman` / `arTa` / `manas` / `pada` (no prebuilt input available to copy),
`rasa` (38 693 B / 421 `<ls>`), `yoga` (40 555 B / 469 `<ls>`), `Atman` (21 610 B / 232 `<ls>`) —
monster shapes. The runnable pool (282 lemmas, 114 with prebuilt inputs, raw median 12 556 B) was
searched for the **smallest raw/sense/citation shapes**, and **exact `perf_preflight` decided
eligibility**:

| real keys | `agent_expected_after_tm` | verdict |
|---|---|---|
| `vastra,zaz,upama,tftIya,Asya` (5) | 5 | run-now-low but 5 agents |
| `zaz,upama,tftIya,Asya` (4) | 3 | run-now-low but 3 agents |
| `zaz,upama,Asya` (3) | 2 | run-now-low but 2 agents |
| **`zaz,upama` (2)** | **1** | **run-now-low · cost ok · SELECTED** |

Five eligible heads do not fit a one-agent call at `--output-budget=90` (citation-weighted:
`zaz` 60 + `upama` 26 = 86 ≤ 90 = one batch), so the brief's "if five eligible real heads do not
exist, use fewer" applies. Selected shapes: `zaz` 3 813 B / 3 senses / 60 `<ls>`; `upama`
4 745 B / 3 senses / 26 `<ls>`. Deterministic order, no duplicates, no presplit card, no
`defer_monster`, no blocked residual, not in store.

## Measured — guard false-flag rates (the rung-3 question)

| Metric | canary | real | note |
|---|---|---|---|
| real silent sense drops | **0** | n/a | canary emitted **3/3** source senses |
| SANLOSS false positives | **0** | 0 | `sanloss_shortfalls=0`, `sanloss_detail=[]` |
| TNMASK true/false positives | **0 / 0** | 0 / 0 | `tnmask_mismatches=0` |
| `dropped_sanskrit_span` | **0** | n/a | canary carries no `{#…#}`/`<ls>` by construction |
| clean-card yield | 1/1 (100 %) | **0/2 (0 %)** | floor 80 % |

**What the canary actually establishes — and what it does not.** All three pure-gloss senses
rendered (черепаха / мелкая рыба / водное растение), so the SAN-LOSS soft guard produced **0 false
positives on one complete three-sense output**. That is the entire claim. **Do not call the
detector validated.** Specifically:

- **SAN-LOSS true-positive sensitivity was NOT exercised.** The canary is a *trap*: it only fires
  if the model drops a sense. The model dropped none, so the detector's ability to *catch* a silent
  drop — the thing rung 3 exists to measure — was never tested. A guard that never fired on a card
  where nothing was wrong tells us nothing about whether it fires when something is.
- **n = 1, and possibly unrepresentative.** The model **explicitly recognised the card as a
  synthetic canary** in its `notes` ("Synthetic D-Q silent-SAN-LOSS canary control card (H994), not
  a real PWG headword"). A model that knows it is being tested may behave more conservatively than
  on real production input — this biases representativeness in the direction that *flatters* the
  result.
- **Zero real clean cards.** One clean synthetic card cannot establish a SANLOSS/TNMASK false-flag
  *rate on real output*, which is what rung 4's arming decision requires. The real lane returned no
  cards to measure.

**Rung 3 remains unmeasured.** Nothing here supports arming a hard reject.

## Costs and telemetry

| | canary | real |
|---|---|---|
| calls / agents | 1 / 1 (ceiling 1) | 1 / 1 (ceiling 1) |
| subagent tokens | 59 250 | 0 (killed before return) |
| wall clock | ~118 s | ~206 s |
| prompt bytes (masked skeleton) | — | 5 606 B at kill |
| budget kill switch tripped | false | **true** |
| translate / heal budget tripped | false / false | **true / true** |
| preflight est. cost | $0.47 | $0.47 |

The `max_agents: 1` ceiling was **mechanically honoured** in both runs (`agents_spent=1`). With
`max_heal_agents: 0` (a direct consequence of the one-agent cap), the kill-timeout left no heal
lane, so both cards hard-failed to null rather than being retried — correct fail-closed behaviour
under "no retry/requeue".

## Store safety — verified, not asserted

**The canonical store is byte-for-byte unchanged.**

| | value |
|---|---|
| rows before / after | **11 605 / 11 605** |
| sha256 before (optimistic-concurrency base) | `cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805` |
| sha256 after | `cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805` |
| mtime after | 2026-07-14 07:22:24 (unchanged) |

This mattered more than it looks. `store_path.canonical_store()` resolves a **linked worktree's
store to the MAIN checkout's real store by design** (the H255 `no_pwg_w06` / H805 loss fix) —
verified empirically from this worktree. So an isolated worktree is **not** isolated for the store;
every generation/preflight/audit step here ran with `PWG_RU_STORE` pinned to a scratch copy, and
the scratch copy still hashes to the base (nothing was written to it either).

Nothing was promoted, so **no TM rebuild** was triggered (the brief rebuilds TM only if ≥ 1 real
row promotes).

## Prohibitions — all honoured

No second window · no retry/requeue · no 10→20 ladder continuation · no c1/c5/c6 · no
[PR #495](https://github.com/gasyoun/SanskritLexicography/pull/495) code · no weakening or
rewriting of the 30-second default gate · no four-profile readiness claim · no language-parity hash
update · **no promotion of `dq_canary_puregloss`** (synthetic, never promotable) · H255 and general
scale remain **frozen**.

## Immutable evidence

| Artifact | SHA-256 |
|---|---|
| `manifest.canary.json` | `7fbb7b74ece5e2721b0b91bd9f4570a006610f0fe888ab668f1758e8b0c6314e` |
| `run_pilot_wf.canary.js` | `0d6e6aabeaa60f1e9a558be6968e9508b48aedd46a1b5628b46509cfb883b983` |
| `manifest.real.json` | `5a438e34035e3dc7ddbf8ad9afb02dc1e7ff2e2e90fae4ff04fc5c8199555929` |
| `run_pilot_wf.real.js` | `b088afbd7cd3afb46461a57562d0eaa9e7acee8d9059114c0c15f2c9bbc439e0` |
| `scale_manifest.freq.json` (copied, verified identical) | `37b3a330b6c488050a5c1c035a09b3d5ae30c05822092925c34b736159daec0f` |
| `pril10.slp1.txt` (nominal core) | `00940c3f3c7c8d4fd65eefa1e756c578fa34435344e166847271a14d01ae1abf` |
| `translation_memory.ru.json` (snapshotted TM) | `f2efc0e68d8dbb0e0858203d491a430a80d169ae3a5f2ec3c7c44d32ea0a79ef` |
| `translation_memory.frag.ru.jsonl` | `2d89aab877e49c6855825f3eae8be0cd412527ea8371a1b4791761a008e06a3d` |

Per-key input hashes: `zaz` raw `fe9d3aa0…` / portrait `6a4f4a6b…`; `upama` raw `b1161745…` /
portrait `26618d19…`; canary raw `4713259b…` / portrait `3d08e33e…`. Every run's result was bound
back to its exact manifest (root, selected keys, batches, model, ceilings, presplit, guard-arming
state all verified — see `pilot_measurement.json`, all checks OK).

Both harnesses passed `node --check`; neither was hand-edited after its manifest was written.

## What this moves

| Gate | Before | After this pilot |
|---|---|---|
| c4 home-route latency | NO-GO (53 290 / 104 870 ms) | **NO-GO unchanged** — a real card did not finish inside the 180 s ceiling *under concurrent self-load*; serial behaviour untested (protocol deviation) |
| serial c4 throughput / economy | unmeasured | **still unmeasured** — the two calls overlapped; no serial evidence produced |
| rung-3 guard false-flag rate | unmeasured | **still unmeasured** — 1 clean synthetic card is not a rate; 0 real cards returned |
| SAN-LOSS soft guard | untested live | **0 false positives on 1 complete 3-sense output** — true-positive sensitivity NOT exercised; not validated |
| canonical store | 11,605 | **11,605 (verified unchanged)** |
| four-profile readiness | NO-GO | **NO-GO, unchanged** — not addressed |

## Recommended next step (a human decides)

The blocker is **latency, not authentication, and not the guards**. Logging in c5/c6 would not
change it.

**But this run cannot say how bad the home route is.** Because the two manifests overlapped
(deviation above), the real call's kill-timeout conflates c4's baseline latency with
self-contention from this pilot's own second call. The defensible statement is only: *a real
5 606 B-skeleton card did not complete within 180 s while a second call was in flight on the same
profile.* Whether a **serially-driven** c4 could complete it is **untested** — and testing it means
a fresh, serial, owner-authorised attempt, not a reroll of this one.

The open path remains the **foreign-route latency investigation**, currently 🟠 archived-deferred as
[H909](https://github.com/gasyoun/Uprava/blob/main/handoffs/H909-Opus_SanskritLexicography_h818-foreign-route-paired-probe-analysis_14.07.26.md)
(prep + runbook ready at
[v1.9.19](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.19)). Whether to
re-open it — and whether a home-route pilot should be attempted again at all before the route
question is settled — is a decision for a human. No threshold was silently chosen and no hard
reject was armed: `SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` remained `false` throughout.

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`), Claude Code, Ultracode, executing the H963 c4
owner-override bounded pilot: 2 calls / 2 agents total, no retry, no requeue, no promotion, no
store/TM mutation._

_Dr. Mārcis Gasūns_
