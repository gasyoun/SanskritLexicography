# H963 — offline PWG→RU launch-readiness report (runtime report)

_Created: 16-07-2026 · Last updated: 17-07-2026_

**Status: TRACKED runtime report.** The H963 offline-continuation brief said "Keep runtime
reports uncommitted unless repository policy explicitly tracks them"; repository policy does
track them — the six sibling `H963_C4_*.md` reports in this same directory are committed on
`master` and nothing here is gitignored — so the brief's own exception applies and this
report is committed rather than left to die in a worktree. It is a read-only snapshot for
launch planning — it makes **no** generation call, promotes nothing, and writes to no store.
Model: Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode. Recovered and committed 17-07-2026
(Opus 4.8 `claude-opus-4-8`) during a worktree sweep.

## What this is / is not

A read-only pass over the on-disk stores, TM data, the residual registry, the frozen
generation-API probe log, `LAUNCH_STATS.md`, and one saved preflight — assembled to answer
"once generation health is GO, what is the cheapest safe first tranche, and what does the
full drain cost in **calls and agents**?" It does **not** run the ladder (that is owner-gated
— see [H963](https://github.com/gasyoun/Uprava/blob/main/handoffs/H963-Opus_SanskritLexicography_pwg-ru-four-profile-live-ladder-acceptance_15.07.26.md)),
and it does **not** fabricate dollar precision the current rate table cannot support.

## Health gate (unchanged — this report does NOT lift it)

The live ladder is **NO-GO** on two independent rungs, both owner-gated:

- **Auth:** `c1`/`c4` logged-in Max, **`c5`/`c6` logged out** → four-profile = **NO-GO**.
- **Latency:** `c4` measured **~30–53 s** under a load-representative payload vs the **≤ 30 s**
  ceiling → latency **NO-GO** (H818/H895/H909 foreign-route territory). `c1` rate-limited/parked.

No tranche below is launchable until a human logs in `c5`/`c6` **and** resolves the latency
rung. This report is the *plan* for that moment, not a GO.

## Data provenance (what was on disk in this isolated worktree)

| Source | State | What it yields |
|---|---|---|
| [`src/pilot/generation_api_probe_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/generation_api_probe_log.jsonl) | PRESENT (30 rows: 12 launch, 8 warmup, 1 abort, 9 outcome) | economy ledger: agents-per-clean + cost band |
| [`src/pilot/no_pwg_residuals.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residuals.jsonl) | PRESENT (7 `blocked`) | the blocked-residual denylist |
| [`src/pilot/lexical_cores/pwg_miss_backfill_queue.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lexical_cores/pwg_miss_backfill_queue.md) | PRESENT (232 lemmas) | the headword universe |
| [`src/pilot/NOMINAL_W1_100SMALL.preflight.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/NOMINAL_W1_100SMALL.preflight.json) | PRESENT | a concrete 100-key window's TM/cost shape |
| [`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md) | PRESENT (458 windows / 62 roots) | hard-fail %, requeue stats, coverage gaps |
| `src/pwg_ru_translated.jsonl` (canonical store, ~11,605 rows) | **ABSENT** (gitignored) | dedup denominator — documented count only |
| `src/pilot/translation_memory.*.{json,jsonl}` (TM sidecars) | **ABSENT** (derived from store) | TM-reuse credit |
| `src/pilot/output/` (plan JSON, coordinator `state.json`, window ledger) | **ABSENT** | live plan/lease state |

> **Honesty caveat (load-bearing).** The store and TM sidecars are gitignored and **absent**
> in this worktree. Every "after TM reuse" figure below is therefore an **UPPER BOUND**: a live
> run with the real card- and fragment-TM would credit *more* reuse (fewer agents/calls), not
> fewer. Do not read these as observed floors.

## 1. Blocked residuals — 7 keys, do NOT launch

The residual denylist (`no_pwg_residuals.jsonl`) holds **7 `blocked` sub-cards**, filtered out
of every window by `no_pwg_scale_plan.filter_residual_subcards` unless `--include-residuals`.
These are prior *deterministic* failures — relaunching reproduces the failure and burns calls:

| key | failure class |
|---|---|
| `arvant~~h0_zz_pw` | second consecutive kill-timeout |
| `apr_apta~~h0_zz_pw` · `as_a_dya~~h0_zz_pw` · `asa_mskfta~~h0_zz_pw` · `avy_ahata~~h0_zz_pw` · `avyagra~~h0_zz_pw` · `b_ahlika~~h0_zz_pw` | second consecutive self-heal-nothing-resolved on presplit cards |

These do **not** enter any tranche until root-caused (H818/H858/H920 span-drop + self-heal
classes). Treat as blocked, never as "cheap remaining work."

## 2. Economy ledger — observed agents-per-clean and the cost band

Reduced from the 9 outcome rows of the frozen probe log (read-only,
`economy_ledger.py`; missing accounting is reported honestly, never as zero):

| metric | value | basis |
|---|---|---|
| agents-per-clean (incl. requeues) | **2.837** | 139 agents / 49 clean over 5 rows w/ structured `agents_used` & clean>0 |
| first-pass agents-per-clean | **3.519** | 95 agents / 27 clean (fresh, non-requeue) |
| cost per clean (band) | **$0.070 .. $0.699** | floor = cache-read rate, ceil = fresh-input rate; **excludes** the output premium |
| cost per clean (true upper) | **$3.493** | every token at the output rate (honest worst case) |
| wasted | **58 agents / 1,798,042 tokens** | on the 1 `clean=0` run |

Coverage: only **5/9** outcome rows carry structured `agents_used` (1 wasted, 3 nulled-into-note).
The `agents_per_clean ≈ 2.84` is the number to plan the **agent** budget against — it is *not*
the `run_summary.calls` model-call counter.

## 3. Per-window shape — the cheap-normal lane (saved preflight)

`NOMINAL_W1_100SMALL.preflight.json` (a 100-key nominal window) is the canonical **cheap**
lane and the shape a first tranche should resemble:

| field | value | meaning |
|---|---|---|
| `selected_keys` | 100 | keys in the window |
| `degenerate_passthrough_keys` | **5** | **zero-agent / TM-only-style** passthrough (no model call) |
| `tm_cards` / `frag_tm_cards` | 0 / 0 | **no TM credited here** (TM sidecar absent/empty at capture) — a live run would reduce agents further |
| `cards_to_translate` | 95 | 100 − 5 degenerate |
| `batch_count` | 3 | dispatch batches |
| **`agent_expected_after_tm`** | **3** | the **TM-reduced agent/call FLOOR** for the whole 100-key window |
| `presplit_keys` | 0 | no monster presplits |
| `recommended_action` | **run-now-low** | the planner's own "cheap, launch it" verdict |
| `cost_gate.verdict` | **ok** | within the $2/card · $25/window gate |

So a healthy ~100-key nominal window is a **3-agent / 3-batch** job (before the ~1.35 realism
overrun → ~4 agents observed). That is the *cheap normal work* profile.

## 4. Zero-agent / TM-only eligible work

Two mechanisms produce work that needs **zero model calls**:

- **Degenerate passthrough** — `degenerate_passthrough_keys` (5/100 in the sample) copy through
  with no agent.
- **Whole-card TM hits** — when `agent_expected_after_tm == 0` the planner recommends
  **`skip-cached`** (`perf_preflight.py`), i.e. the window is fully served from TM with zero agents.

Because the store/TM are **absent here**, the *count* of currently TM-satisfiable keys is not
computable offline in this worktree — it must be read from a live `perf_preflight.py` pass once
the store is mounted. Structurally, this is the first bucket to drain (free), and the bounded
runner's clean-target drain handles it without spending any call budget.

## 5. Expensive monster heads / windows

`perf_preflight.cost_partition` peels **per-card monsters** out of an otherwise-cheap window
into a `defer_monster` lane (agents>0 **and** per-card $ > `--cost-ceiling-per-card`, default $2):

- Cheap batched card ≈ **$0.07/card**; a `kAla`-class monster head ≈ **$10–27/card**; the worst
  observed, `pril10_w1`, was **$79.83 over 3 cards**.
- `window_size` caps *headwords* (default 20, hard cap 30) but **one head** can expand into many
  large sub-cards — "monster" is a per-**card** property, not per-window.

For the `no_pwg` backfill queue specifically, monsters are the exception, not the rule; the
cost gate (`$2/card · $25/window`) plus `enforce_cost_gate` park a monster window rather than
launch it. **A first tranche must exclude any `defer_monster` key.**

## 6. Full-drain population and rates (LAUNCH_STATS, 458 windows / 62 roots)

| metric | value |
|---|---|
| windows launched (historical) | 458 (62 distinct roots) |
| hard-fail windows (stale-refused + crashed) | **113 = 24.67%** |
| windows that requeued ≥ once | 342 (mean **12.07** requeues when they did) |
| fully `clean` outcome | **3** windows |

> `needs_requeue` is the *normal* iterative state, not a failure — the honest hard-fail rate
> (24.67%) counts only stale-refused + crashed.

**Instrumentation gap (drives the cost fail-closed policy):** wall-clock is recorded on **12/458**
windows, output-tokens on **1/458**, `gen_model` on **0/458**. Per-window observed cost is
therefore *usually unavailable* — exactly why the bounded runner must **fail closed** (not zero)
when a cost ceiling is set and a window carries no trustworthy cost. This matches H911's
"observed economy INCONCLUSIVE (tokens `not_recoverable`)."

## 7. Expected agent count / expected calls after TM reuse

- **Per ~100-key window:** `agent_expected_after_tm = 3` (planner floor) → ~**4 agents observed**
  at the 1.35 realism factor. `projected_calls` in a plan window == `agent_expected_after_tm`.
- **Documented H818 dry-run shape** (100 headwords): **120 subcards / 117 projected calls / 0
  presplits / 5 cost gates OK** — the canonical "one staged run" magnitude.
- **Remaining universe:** 232 backfill lemmas − 7 blocked residuals = **225 candidate lemmas**,
  minus whatever is already promoted into the (absent here) ~11,605-row store. The *net*
  remaining is only computable against the live store; treat 225 as the pre-dedup ceiling.
- **Agent budget rule of thumb:** at agents-per-clean ≈ **2.84** (§2), draining *N* clean cards
  costs ≈ **2.84 N agents** including requeues — the number to size a quota against, **not**
  a per-window call count.

All "after TM reuse" numbers are **upper bounds** (store/TM absent — §Provenance caveat).

## 8. Cheapest safe first tranche (once health is GO)

When a human has logged in `c5`/`c6` and the latency rung passes, the cheapest measured-not-scaled
first tranche is **one small nominal window**, run through the new bounded staged-run in a
tightly-bounded, cost-fail-closed, dry-run-first way:

1. **Dry-run the plan first** (zero calls) to print the exact scope, ceilings, account
   allocation, checkpoint path and stop policy — verify the window carries no `defer_monster`
   key and no blocked residual, and that `cost_basis.evaluable` is true.
2. **Then execute one window**, single profile, with hard ceilings:
   - `--max-windows 1` (one window/call batch), `--max-clean ≤ window size`,
     `--max-calls ≈ 5` (≈ the ~4-agent floor + a margin), `--empty-streak 1`,
     `--max-accounts 1`, and a `--cost-ceiling` only if trustworthy cost data exists
     (else omit it — a set-but-unpriceable ceiling **fails closed** by design).
3. **Measure, do not scale.** A clean result feeds rung 5 (10 → 20); a NO-GO stops at the first
   hard rung with immutable evidence, no reroll (the H911 discipline).

The exact command is in the H963 footer ("the single exact command the owner should run").
Never widen ceilings or add profiles until a 10- then 20-window rung is green.

---

_Auto-derived read-only from on-disk stores/ledgers; no generation, promotion, or store write._
_Dr. Mārcis Gasūns_
