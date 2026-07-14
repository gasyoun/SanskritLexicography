# Launch-telemetry ledger audit — code vs docs (H462, July 2026)

_Created: 10-07-2026 · Last updated: 10-07-2026_

Audit of the four pwg_ru launch ledgers against the code that (supposedly) produces their
numbers, executed per
[H462](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md)
by Fable 5 (`claude-fable-5`). Files audited:
[`LAUNCH_FUCKUPS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
(13 entries),
[`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md),
[`src/pilot/RUN_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md),
[`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md),
against
[`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py),
[`src/pilot/check_launch_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/check_launch_ledger.py),
[`src/pilot/harvest_launch_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/harvest_launch_stats.py),
[`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py).

**Headline.** The ledgers' *evidence* is broadly faithful, but its two decisive numbers
(kill-timeout count, connection-error count) were never returned by the code — they were
hand-counted from `console.log` transcript lines, and the checker only validated *shape*,
never *classification*. Re-deriving all 13 classifications from their own recorded evidence
overturns 2 of 13. Both overturned entries date from the last 24 hours of H442 work, i.e.
exactly the period when hand-transcribed telemetry was being used to adjudicate a
code-vs-infra question. One denominator-provenance defect was found in `LAUNCH_STATS.md`
that is worse than the bias the handoff suspected.

## Q1 — do the recorded classifications match the recorded evidence?

Method: for each entry, re-derive the class from the entry's own `symptoms` / `actual` /
`root_cause` fields against the typology definitions at the top of `LAUNCH_FUCKUPS.md`,
ignoring the recorded `classification`. Verdicts:

| # | Entry | Recorded class | Re-derived | Verdict |
|---|---|---|---|---|
| 1 | `SLICE_D_2026-06-30` | `concurrency/api` | 80+ server 429s at 18-wide = provider throttling | ✅ confirmed |
| 2 | `PRIL10_W1_2026-07-05` | `complexity-estimate-drift` | preflight missed per-fragment fan-out (174 est → 230 agents, $80) | ✅ confirmed |
| 3 | `NOMINAL_W1_100SMALL_2026-07-06` | `concurrency/api` | same transport error across ALL batches = transient infra | ✅ confirmed |
| 4 | `DAH_TAIL_2026-07-06` | `structured-output-limit` | one fragment exceeded the schema-emission envelope after bounded retries | ✅ confirmed |
| 5 | `NO_PWG_W1_FIRST_RUN_2026-07-06` | `kill-gate-calibration` | multi-cause (kill budget + key echo + audit assumptions); kill gate is the primary per H220's follow-up fix | ✅ confirmed (multi-type, primary correct) |
| 6 | `NO_PWG_DIAG_2026-07-06` | `kill-gate-calibration` | 6/6 nulls were kill-timeouts from a dense-batch profile applied to no-fallback singles; fixed by the CEIL budget | ✅ confirmed |
| 7 | `ARMB_SYNTH_FANOUT_2026-07-06` | `operator/process` | unsafe liveness signals, shared paths, bare fan-out — process, not platform | ✅ confirmed |
| 8 | `H317_MEDIUM50_3WIDE_KILL_CASCADE_2026-07-08` | `concurrency/api` | 3-wide saturation + session-wide transport instability; the later supersession (schema classifier) is properly recorded in `residual_risk`, and the 08-07 symptoms themselves were transport-class | ✅ confirmed |
| 9 | `H389_MEDIUM50_SCHEMA_CLASSIFIER_BLOCK_2026-07-09` | `structured-output-limit` | deterministic pre-generation refusal by the Workflow `agent()` safety classifier. Note: this is a *platform admission gate*, not the model failing to emit the schema — the class is kept because the fix (schema size) and the H428 pair entry share it, but the typology definition reads narrower than this use | ✅ confirmed, with note |
| 10 | `H428_OPT2_SCHEMA_SLIM_FIX_2026-07-09` | `structured-output-limit` | fix-confirmation twin of #9 | ✅ confirmed |
| 11 | `H437_MEDIUM50_KILLGATE_CASCADE_2026-07-09` | `kill-gate-calibration` | clean env (0 conn-errors, 1 kill-timeout across 162 agents), budget exhausted purely through heal-bisection fan-out on dense cards — genuinely the gate's design | ✅ confirmed |
| 12 | `H442_MEDIUM50_KILLTIMEOUT_BISECTION_WASTE_2026-07-10` | `kill-gate-calibration` | **infra-dominated by its own evidence**: 3 × `Connection closed` + 58/76 kill-timeouts per run, incl. an 11-byte fragment killed at the 45 s floor (latency independent of payload) — the same signature entry 13 classes as infra. The kill-timeout × bisection *design flaw* it documents is real and env-independent, but it is not what nulled the cards: run 2 had the no-bisect guard active and still went 0/12 under 76 kill-timeouts | ❌ **overturned → `concurrency/api`** |
| 13 | `H442_MEDIUM50_LAUNCH3_INFRA_CONFOUNDED_2026-07-10` | `external-api` | diagnosis (infra, not code) is right; the *bucket* violates the ledger's own typology — `external-api` is defined as **non-Workflow** service quirks (JSON mode, DeepSeek), while "connection loss, mid-stream stalls, provider throttling" is the `concurrency/api` definition verbatim; siblings #3 and #8 with the same symptom class use `concurrency/api` | ❌ **overturned (bucket only) → `concurrency/api`** |

Both corrections are applied in `LAUNCH_FUCKUPS.md` as appended `correction` fields (old
class + reason + date preserved — no silent history rewrite, per the ledger's closeout rule),
and `LAUNCH_STATS.md` is re-harvested. Corrected orchestration distribution:
`concurrency/api` 5 · `structured-output-limit` 3 · `kill-gate-calibration` 3 ·
`complexity-estimate-drift` 1 · `operator/process` 1 · `external-api` 0.

**Consequence of #12 (the handoff's suspicion, confirmed):** the corrective action taken
from the wrong class — keep tuning the heal budget — was aimed at the wrong target for one
more launch. The correct action (pause the lane on infra) was only taken after launch 3
burned a further ~1.8 M tokens. The two PR
[#301](https://github.com/gasyoun/SanskritLexicography/pull/301) guardrails remain sound and
field-untested, exactly as entry 13 records.

## Q2 — is `LAUNCH_STATS.md`'s denominator honest?

Two defects, one worse than the handoff suspected:

1. **Survivorship bias (suspected — confirmed).** The population counts only windows that
   launched. Probe-refused launches (abort / NO-GO rows in
   [`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md))
   are structurally invisible, so every rate is conditioned on "we chose to launch".
   **Fixed:** `harvest_launch_stats.py` now writes a standing bias note into the generated
   file, quoting the live refused-launch counts from the probe log as a **separate**
   denominator. **Ruling on the handoff's open question 1: abort rows do NOT feed the
   population.** Mixing refused launches into launched-window rates would silently change
   the meaning of every existing rate; the two denominators stay side by side.
2. **Denominator provenance (not suspected — found).** The committed 09-07-2026 edition
   reported "Windows launched: **3**" — harvested from an H437 *worktree* whose local
   `output/window_ledger.jsonl` held only that worktree's 3 launches, while the main
   checkout's ledger held **450 windows / 55 roots** (the population
   `LAUNCH_FUCKUPS.md`'s own methodology section cites). The auto-generated file carried
   no trace of which ledger produced it, so a 450-window population silently became a
   3-window one on master. **Fixed:** the harvester now stamps data-root, ledger path and
   row count into the generated file; regenerated from the main checkout (450 rows).
3. **Corollary (recorded, not fixable retroactively):** the 08–10.07 medium50 launches
   (H317 ×4, H389 ×1, H437 ×3, H442 ×3) were run from worktrees whose gitignored
   `output/` died with the worktree — none of them exists in the surviving 450-row window
   ledger. The durable record of those launches is `LAUNCH_FUCKUPS.md` + the probe log
   only. Going forward the probe log's `launch`/`outcome` rows (committed JSONL) close
   this hole.

## Q3 — is `agent_expected_after_tm` comparable across runs?

No, and it is now stated where the comparisons live. `MAX_AGENTS` derives from
`agent_expected_after_tm` ([`gen_opt_harness2.py:1159-1162`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)),
which shrinks as the fragment-TM sidecar grows — `h317_w1b` was 17 expected / `MAX_AGENTS=61`
under H437 and 16 expected / `MAX_AGENTS=58` on 10-07 purely because the sidecar had grown to
217 cached fragments. Non-comparable cross-run comparisons found (all same-window,
different-TM):

- `LAUNCH_FUCKUPS.md` entries 12/13: "vs H437's 1 promoted", "61/61 … 58/58" — the H437
  baseline ran with a smaller TM; agent counts and clean-rates are not the same experiment.
  The appended `correction` fields now carry this audit's pointer.
- [`RussianTranslation/.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
  H442 queue row and
  [`MEASUREMENT_2026-07-08_H317.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/MEASUREMENT_2026-07-08_H317.md)
  launch sections: the run-to-run token and agent comparisons (2.90 M → 2.22 M → 1.80 M
  tokens for "the same" w1b) span three different TM states.
- `LAUNCH_STATS.md` and `RUN_LOG.md`: no offending cross-run comparison found —
  `LAUNCH_STATS.md` aggregates without comparing windows across time, and `RUN_LOG.md`'s
  detailed blocks predate the medium50 lane.

**Normalization is not possible retroactively** (the TM state at H437 time was not
recorded); the affected comparisons are hereby marked non-comparable rather than
re-derived. Going forward the stamp exists twice: the harness summary already returns
`frag_tm_fragments`, and the probe log's `harness.frag_tm_cached` field records it per
launch — any future cross-run comparison must hold both equal or say why not.

## Q4 — does the code's budget logic match what the ledgers say?

**Confirmed against the code — a design fact, not a tuning parameter.**
`MAX_AGENTS = ceil(agent_expected × 3.0) + 10`
([`gen_opt_harness2.py:1162`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py));
every heal call goes through `agentKill`, which spends the same `AGENTS_SPENT` counter as
the translate lane — the heal pool and the translate pool are one counter. The per-card
heal ceiling is `ceil(nGroups × 1.5) + 3` *per card*; for a window where **every** card
routes to heal, the sum of per-card ceilings exceeds the shared window pool by
construction (h317_w1b: 12 cards' ceilings sum to ≫ 58), so the window budget always binds
first and the per-card cap is unreachable — exactly what three consecutive runs measured
(`0 per-card fires, partial_keys=[]` each time). H442's conclusion is code-accurate; the
per-card cap only ever binds on a *sparse*-heal window (one pathological card among
healthy ones), which is the H437 shape it was designed for. The lever that would make it
bind on all-heal windows — uncoupling the heal pool from the translate pool — is real,
behavioural, and therefore **out of H462's counters-only scope**; it stays recorded in
entry 13's `residual_risk` as the next structural move.

> **Follow-up implemented offline 10-07-2026 (Codex/GPT-5):** the current refactor removes
> that shared-counter design. `agent_budget.py` derives independent translate and heal
> ceilings; `agentKill` charges by lane; the heal ceiling is the sum of per-card caps; and
> summary/meta return both pools' spend and trip state. A generated-JS Node test with two
> all-heal, always-null cards reaches both per-card caps without tripping the window heal
> pool. The historical finding above remains the correct reading of H437/H442 artifacts;
> the new behavior is not production-validated until a healthy `h317_w1b` canary runs.

**Ruling on the handoff's open question 2 (per-card vs per-window `heal_calls`):**
per-window. The summary's new `heal_calls` counts heal-lane `agent()` calls window-wide
(labels `heal:*`); the per-card view already exists inside the run as `cardBudget.spent`
and per-card failure strings, and surfacing 12 more per-card counters in the summary would
duplicate what `failures` + `partial_keys` already localize. Given Q4 (one shared pool),
the window-level number is the one every adjudication actually uses.

## What landed (telemetry patch, counters only)

- [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py):
  summary now returns `kill_timeouts`, `conn_errors`, `heal_calls`,
  `kill_bisect_blocked` — counted centrally in `agentKill`'s catch (re-throws; zero
  control-flow change). Caveat by design: `conn_errors` counts *thrown* transport errors;
  an `agent()` that returns `null` on a terminal API error stays visible in
  `summary.failures` as `agent-returned-null`.
- [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py):
  `test_run_telemetry_counters_returned` pins the counters into the summary and pins that
  counting stays out of control flow; `test_classify_run_verdicts` pins the classifier.
- [`classify_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/classify_run.py)
  (new): `clean` / `code-failure` / `infra-confounded` from the payload alone —
  infra-confounded on ≥1 conn-error or kill-timeouts ≥ max(3, 25% of agents); honest
  `unclassifiable` on pre-H462 payloads. Exit codes 0/1/2/3 for scripting.
- [`probe_log.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py):
  warm-up gate now requires a load-representative payload (≥ 5 KB, `--payload-bytes`,
  `prompt` subcommand emits one) — a 3.3 s trivial GO probe demonstrably failed to predict
  a degraded window on 10-07-2026.
- [`harvest_launch_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/harvest_launch_stats.py):
  provenance stamp + standing bias note + probe-refusal side-denominator (Q2).
- `LANG_PARITY.md`: counters classified **SHARED** (language-agnostic harness JS).

_Dr. Mārcis Gasūns_
