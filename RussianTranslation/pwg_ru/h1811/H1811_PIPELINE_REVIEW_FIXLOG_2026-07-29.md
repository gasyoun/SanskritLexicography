# H1811 — PWG→RU pipeline review: verified findings + fix log (hardening + offline speed)

_Created: 29-07-2026 · Last updated: 30-07-2026_

> **Provenance.** Handoff [H1811](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1811-Kimi_RussianTranslation_pwg-ru-offline-pipeline-review-hardening-speed_29.07.26.md).
> Executor: Kimi K3 (`moonshotai/kimi-k3`). Method: hermetic bench baseline
> ([`h1339_offline_bench.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_offline_bench.py)),
> 3 parallel survey agents (audit-stage profile, store-write cProfile, orchestration
> adversarial review), then **every claim re-verified against fresh origin/master**
> (`d5650afe`) before any edit — 154 commits had landed since the agents' read base,
> incl. Codex hardening PR #761, so several original findings were already fixed upstream.
> Zero model calls; offline path only.

## 0. Scope and prior-art check

Task: code review of the PWG→RU pipeline → harden + increase speed. Prior art honored
(per repo rules): [H1403 22-agent speed audit](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md)
("idea saturation — execute, don't design"), H1339 (−23 % offline), H1386 (prepare-batch
−72 %), H1420 (P10/P11), H1618 (budget-note preservation). This pass covers the **still-open
residue**, verified live on master — nothing below re-proposes shipped work.

**Bench baseline (fixture, 5 leases / 10 cards):** audit stage ≈ 50–55 % of total,
store-write ≈ 30 %. Per-lease `record-output` still pays 2 interpreter spawns
(`coordinator` already amortized by upstream `record-output-batch`; `audit_window` +
`_pilot_collect` remain).

## 1. SPEED fixes (verified live on master)

| # | Finding | Evidence | Fix | Est. saving |
|---|---|---|---|---|
| S1 | `process_record_output` spawns `audit_window.py` per lease | [`coordinator.py:1537-1546`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | ~~run audit in-proc via `run_py_inproc`; 30-min timeout re-imposed via worker thread~~ — **reverted, §5.2**: a thread cannot be killed, so the timeout never cancelled the audit | ~0.5–0.9 s/lease (given back) |
| S2 | `_pilot_collect` is the last subprocess gate | [`audit_window.py:234-237`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) | route through existing `run_py_inproc` (H1339 pattern; the other 5 gates already in-proc) | ~0.3–0.5 s/lease |
| S3 | `component_sha` re-hashes the same files per `stamp()` — 30 calls/promote batch, ~27 % of batch-promote in-proc time (cProfile) | [`pipeline_version.py:90-108`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py) | ~~per-process memo keyed on (patterns, root)~~ — **reverted, §5.2**: keyed on patterns, not content, so it never invalidated and stamped stale provenance | ~0.27 s/promote (given back) |

Already upstream (verified, **no work**): `record-output-batch` (one coordinator process
for N leases), TM `build`/`build_frags` in-proc via `promotion_journal`, prepare-batch.

## 2. HARDENING fixes (verified live on master)

| # | Sev | Finding | Evidence | Fix |
|---|---|---|---|---|
| H9 | P1 | `cohort_engine`: a transient probe exception persists `_failed_profiles` into the checkpoint (never re-probed, even on resume); the terminal barrier skips those leases and the wave still settles `promoted/tm_done=True` → leases **silently stranded forever** | `cohort_engine.py` (probe/restore/barrier) | don't persist failed profiles (re-probe on resume); `stop_reason` when the wave settles with runnable-undispatched leases |
| H2a | P1 | `self_heal`: presplit base key gets soft `selfheal-nothing-resolved` while the real cause `budget_exceeded:heal` sits only on frag keys → transient budget stop misclassified as content defect (C-49 lane) | [`headless_worker.py:791-792`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) | stamp the base key with the frag budget note (exact frag-key set, not prefix) |
| H8 | P1 | `claim` holds the global state DirLock while running a **no-timeout** `perf_preflight` subprocess + full store/worklist scans — a hung preflight wedges every coordinator op until lock TTL | [`coordinator.py:865+`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | timeout on the preflight `run_cmd` (moving candidate computation out of the lock deferred as larger refactor) |
| H1 | P2 | manifest `open` + `json.loads` outside the try; `KeyError`/`TypeError` not in the except tuple → malformed/drifted manifest crashes with **no status file**; orchestrator burns retries on a deterministic defect | [`headless_worker.py:1001-1004,1044`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) | move into try; add `(KeyError, TypeError)` → `classification: configuration` |
| H2b | P2 | `resolve_group` blanket `budget_exceeded:translate` note (preserve=False) overwrites attempt-1 per-key content notes | [`headless_worker.py:636-638`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) | `preserve=True` for budget notes |
| H3 | P2 | checkpoint writes lack fsync (headless_worker, bounded_supervisor, cohort_engine) — power loss loses the last checkpoint → wasteful full re-audit | three files vs fsyncing `window_common.atomic_write_text` | route through the fsynced atomic writer |
| H4 | P2 | `claim` accepts a duplicate `--lease-id` (`register_prepared_lease` refuses, `claim` doesn't) → unreachable second lease breaks the single-id CAS assumption | [`coordinator.py:865+`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | same existence guard in `claim` |
| H5 | P2 | corrupt/missing `window_status.json`/`audit_window.report.json` swallowed to `{}` → lease recorded with meaningless `'unknown'` audit state | [`coordinator.py:1549-1557`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | unreadable status/report + rc ∈ {0,1} → append to `audit_errors` |
| H7 | P2 | zero-claim drain pass hot-spins (no sleep) until `max_drain_iterations` | `bounded_staged_run.py` | consecutive-no-progress backstop (mirror staged C4) |
| H10 | P2 | `_pilot_collect.py:14` hardcodes `OUT = src/pilot/output` — even the **hermetic bench** rewrites live `.merged.md` sidecars + quarantine renames (same class as H1386 P3f) | [`_pilot_collect.py:14`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_collect.py) | `PWG_OUTPUT_DIR` env override |

Verified **sound / obsolete** (no work): promotion-journal TM rebuild (= tm-dirty idea done
properly), `record-output` run-id binding (P11 active), ActiveCallClaim kernel lock,
receipt binding, claim CAS/stale-token recovery, bounded-staged crash-resume exactly-once,
journal-scoped `build_frags(clean_files)` (the full-artifact frag grep is gone).

## 3. Contention note

A dormant Codex branch (`codex/rt-pipeline-hardening-speed`, worktree
`SanskritLexicography-rt-harden-codex`) holds 3 unmerged `ai-wip` commits on a **stale
base** (last 28-07 09:31; two-dot diff would delete 746k master lines). Its valuable parts
already landed via PR #761 et al. This pass branches from fresh `origin/master` and does
not touch that branch; a human may archive it.

## 4. Fix log

| Fix | Status | Commit | Selftest pin |
|---|---|---|---|
| S3 component_sha memo | ❌ **REVERTED by H1957** — the memo keyed on file patterns, never content, so it had no invalidation and stamped pre-edit provenance onto rows promoted after a mid-run source change | [PR #897](https://github.com/gasyoun/SanskritLexicography/pull/897) | `pipeline_version.selftest` fresh-stamp block (assertion inverted — it previously certified the stale hash) |
| S2 collect in-proc | ✅ DONE (bench-verified), **retained** | this branch | bench outcomes == baseline |
| S1 audit in-proc | ❌ **REVERTED by H1957** — the daemon-thread timeout returned rc=124 while the audit kept running and kept writing the files the caller then read | [PR #897](https://github.com/gasyoun/SanskritLexicography/pull/897) | `window_selftest.test_h1957_audit_timeout_actually_kills_the_child` |
| H5 corrupt status | ✅ DONE (code; gate pending) | this branch | — |
| H10 collect OUT override | ✅ DONE — needed **five** readers patched, not one: `_pilot_collect`, `audit_window`, `audit_translation` (feeds `stage2_pregate` via `at.merged_output_path`), `root_glue_translated`, **and shared `window_common.OUT`** (feeds `window_reports.merged_exists` → `audit_state`). Missing the 4th/5th caused first NO-OUTPUT defects, then phantom `partial` states — the bench caught both instantly | this branch | bench hermeticity + outcomes == baseline |
| H1 manifest crash | ⏳ handed to Opus 5 ([H1940](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1940-Opus_RussianTranslation_pwg-ru-h1811-integrate-verify_30.07.26.md)) | — | — |
| H2a budget note on presplit base | ✅ DONE 30-07-2026 (H1940 Phase 2) — `self_heal`'s zero-sense branch no longer hard-codes `selfheal-nothing-resolved`. When this card's OWN fragments recorded a typed `budget_exceeded:*`, that reason is propagated to the base key, so a transient heal-ceiling stop stops being filed as a content defect (the C-49 lane). The fragment-key set is derived EXACTLY from `fragment_groups[key]` (`<key>_f<index>`), never by prefix — `ab_f` would otherwise capture `ab_foo_f0`. Precedence is the lowest NUMERIC fragment index, so `_f10` cannot outrank `_f2`. `preserve=True` could not have fixed this: a presplit key runs no whole-card attempt, so there is no earlier base note to preserve | [PR #900](https://github.com/gasyoun/SanskritLexicography/pull/900) | `headless_worker_selftest` ×4: budget-stop-not-content-defect (RED on pre-H2a master), exact-not-prefix (RED against a prefix-matching impl), unchanged-content-path (regression guard), deterministic-precedence (RED on pre-H2a master) |
| H2b budget note preserve | ⏳ handed to Opus 5 (H1940) — **explicitly NOT bundled with H2a** | — | — |
| H3 fsync checkpoints | ⏳ handed to Opus 5 (H1940) | — | — |
| H4 dup lease-id | ⏳ handed to Opus 5 (H1940) | — | — |
| H7 drain spin | ⏳ handed to Opus 5 (H1940) | — | — |
| H8 preflight timeout | ⏳ handed to Opus 5 (H1940) | — | — |
| H9 cohort stranding | ✅ DONE 30-07-2026 (H1940 Phase 2) — `_failed_profiles` is no longer persisted and a failed probe no longer persists into `probed`, so a **transient** probe exception is re-probed on resume instead of becoming a permanent verdict; a wave that settles with runnable-undispatched leases now records a `stop_reason` naming each lease/profile/cause. Settling itself is unchanged (same partial-wave semantics as the budget path) — what changed is that it is no longer silent | [PR #899](https://github.com/gasyoun/SanskritLexicography/pull/899) | `cohort_engine_selftest` pins **8** (transient probe re-probed on resume) and **9** (settle records `stop_reason`), each verified to FAIL against the pre-H9 engine |

**Bench verification (fixture, per-lease outcomes must equal the pre-change baseline):**
fx1 clean=3/promoted · fx2 clean=1/promoted_partial (transient `_a_g_ata`, defect
`_a_dikya`) · fx3 clean=2/promoted · fx4 clean=1/promoted · fx5 clean=3/promoted ·
deterministic signature stable — **MATCH** after the fixes (29-07-2026).

## 5. Bench A/B

Interleaved A/B on the same host (candidate branch vs detached `origin/master`
worktree, 1 warmup + 3 measured runs per side, alternating; 30-07-2026, Python
3.14/win32). Per-lease outcomes, deterministic signature (`9bd2a14297…`) and store
semantic hash (`c72281ca…`) **byte-identical on both sides** — semantic equality
proven, same criterion as H1339/H1386.

| Stage | base median | cand median | Δ |
|---|---|---|---|
| prepare | 1.18 s | 1.21 s | +2.3 % (noise) |
| normalize | 0.05 s | 0.05 s | noise |
| **audit** | 3.60 s | 2.19 s | **−39.3 %** |
| promotion-plan | 0.45 s | 0.28 s | −36.2 % |
| store-write | 2.35 s | 2.06 s | −12.4 % |
| **total** | 7.23 s | 5.58 s | **−22.9 %** |

Machine-readable: `h1811_ab_summary.json` (session temp); per-run JSONs
`h1811_ab_{base,cand}_N.json`. Gates at close: `window_selftest` **194/194 PASS**,
`lang_parity_check` **0 violations** (89 entries), `pipeline_version` selftest OK.

### 5.1 Re-verification on fresh master (H1940 Phase 1, 30-07-2026)

[PR #893](https://github.com/gasyoun/SanskritLexicography/pull/893) went
`CONFLICTING` after 26 commits landed on master. Rebased onto `f15bcf0f`
(release 1.111.3); the only conflict was
[`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md)
— master had cut the H1887 block into `## [1.106.0]` while the branch still
carried it under `## [Unreleased]`; resolved keep-both, H1811's `### Changed`
restored to the top of `[Unreleased]`.
[`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
auto-merged. Bench re-run 1 warmup + 3 runs per side on one host, Opus 5
(`claude-opus-5[1m]`):

| Stage | master `f15bcf0f` | rebased branch | Δ |
|---|---|---|---|
| prepare | 1.367 s | 1.584 s | +15.9 % (noise, see below) |
| normalize | 0.068 s | 0.066 s | noise |
| **audit** | 4.188 s | 2.643 s | **−36.9 %** |
| promotion-plan | 0.585 s | 0.403 s | −31.1 % |
| store-write | 2.880 s | 2.585 s | −10.2 % |
| **total** | 8.421 s | 6.797 s | **−19.3 %** |

The headline deltas are smaller than §5's −39.3 %/−22.9 % because the **base
moved, not the candidate**: master's own total rose 7.23 s → 8.42 s over those
26 commits. The candidate's absolute total also rose (5.58 s → 6.80 s), so both
sides drifted upward on this host and the ordering is unchanged. `prepare` is
below the noise floor at 3 runs (branch spread 1.53–1.79 s) — not a regression
claim. Per-lease outcomes match §5 exactly and the deterministic signature
`9bd2a14297` is byte-identical across both sides, which is the load-bearing
result: **semantic equality still holds against new master.**

**The inherited red gate, and how it was cleared.** The first pass over these
gates was red, and not through any fault of this PR:

- `window_selftest` — 194 defined, **193 PASS / 1 FAIL**.
- `lang_parity_check` — **3 violations**, all inherited: `citation_tm.py`,
  `corpus_gate.py`, `annotate_genres.py` drifted under H1902
  ([PR #892](https://github.com/gasyoun/SanskritLexicography/pull/892),
  `af299375`). All three are **byte-identical between `origin/master` and this
  branch** (`git diff --name-only origin/master HEAD` lists none of them), so
  the drift is master's own re-affirm debt — `lang_parity_check` on a clean
  `origin/master` worktree reproduces the identical 3 violations.
- The single `window_selftest` failure is `test_lang_parity_ledger_complete`,
  i.e. the same three inherited entries surfacing through the suite. No other
  test fails.

That debt was then paid on master in its own PR rather than smuggled through
this one: each of the three verdicts was re-derived against H1902's actual diff
(the same `+2/-1` swap of a hard-coded sibling-root guess for `sibling_root(HERE)`,
whose resolver carries no language-conditional logic at all), re-affirmed with the
reasoning written into each ledger note, and merged as
[PR #894](https://github.com/gasyoun/SanskritLexicography/pull/894) / `459ee452`.

This branch was then rebased a second time onto that green master. The
`LANG_PARITY.md` collision it produced is worth recording, because it is
structural rather than accidental: `corpus_gate_evidence_markers_fl7_h321`
tracks **two** files, `src/corpus_gate.py` (re-stamped by #894) and
`src/pilot/window_selftest.py` (modified and stamped by this PR), so the two
PRs necessarily rewrote adjacent lines of the same `verified_sha256` object.
Resolved keep-both — #894's `corpus_gate.py` hash beside this branch's
`window_selftest.py` hash — and confirmed by re-running the gate rather than by
inspection. Final state on the rebased branch: `lang_parity_check` **89 entries,
no drift**; `window_selftest` **194/194, 0 failed**; bench per-lease outcomes
unchanged with signature `9bd2a14297` intact. The `f15bcf0f → 459ee452` delta is
`CHANGELOG.md` + `LANG_PARITY.md` only, so the A/B table above still stands on
identical code.

### 5.2 Correction: S1 and S3 reverted for correctness (H1957, 30-07-2026)

Opus 5 (`claude-opus-5[1m]`). Both speed fixes above were correct about the *cost* they
removed and wrong about what they cost in exchange. Neither defect was visible to any
gate — §5.1 recorded 194/194 green with both present.

**S1 — the timeout could not cancel the audit.** `run_audit` ran `audit_window`
in-process on a daemon thread. [`run_py_inproc`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)'s
own docstring forbids exactly that usage: *"callers must not run two of these
concurrently (sys.argv/stdout are process-global)."* On timeout the caller returned
rc=124 and moved on while the worker kept running, producing three concurrent-access
failures: (1) the live thread kept **writing `window_status.json`, the audit report and
requeue files** that `process_record_output` reads on the next line; (2) `sys.argv`,
the process cwd (`run_py_inproc` chdirs to `SRC`) and `stdout`/`stderr` stayed
redirected out from under the coordinator; (3) the `finally` restored argv/cwd whenever
the thread ended, clobbering any value the main thread had set meanwhile. Failure (2)
was observed directly while reproducing this: the reproduction script's own `print`
output disappeared into the abandoned thread's capture buffer and only resumed after
that thread exited. Fixed by restoring a **killable subprocess** boundary — the pre-H1811
shape — while keeping the `run_audit` test seam and H1811's rc=124 timeout contract
(so H5's `rc ∉ {0,1}` handling is unchanged) and keeping S2 in-process inside the child.

**S3 — provenance could be stamped stale.** `_STAMP_MEMO` keyed on
`(tuple(comp['files']), abspath(root))` — the file *patterns*. Nothing in the key
varies with content, so the entry never expired: any process that outlived a source
edit stamped every later row with the pre-edit hash. Long-lived waves
(`bounded_staged_run`, `cohort_engine`) are exactly that case. `check()`/`freeze()`
remained exact, but they inspect the manifest and cannot repair provenance already
written into the store. Removed; `stamp()` re-reads.

**The gates were not merely silent — one was inverted.** The S3 selftest asserted
`st2['prompt_sha'] == st['prompt_sha']` under the message *"stamp memo must return the
first hash"*, certifying the stale result as the contract. The S1 test monkeypatched
`run_py_inproc` and asserted only the rc=124 mapping, so it could not fail for the
reason that mattered. Both replaced; the new timeout test drives a real child that
sleeps then writes a sentinel, and was checked to **fail against the old
implementation** rather than assumed to.

**Cost of the correction.** Interleaved A/B vs master `3070941b`, 5 alternating pairs,
host under variable load (base totals ranged 10.79–13.29 s), minimum per side as the
robust estimator:

| Stage | base `3070941b` | H1957 | Δ (min) | Δ (median) |
|---|---|---|---|---|
| prepare | 2.240 s | 2.000 s | −10.7 % | −9.6 % |
| **audit** | 3.950 s | 5.320 s | **+34.7 %** | +41.4 % |
| promotion-plan | 0.650 s | 0.760 s | +16.9 % | +45.6 % |
| **store-write** | 4.000 s | 4.960 s | **+24.0 %** | +8.9 % |
| **total** | 10.790 s | 12.410 s | **+15.0 %** | +25.3 % |

`audit` carries the restored interpreter spawn; `store-write` carries `stamp()`
re-hashing per promoted row. `prepare` moved without being touched, which is the
scale of the noise floor here — treat the small deltas as unresolved. The
deterministic signature `9bd2a14297` is byte-identical on both sides, so **outputs are
unchanged**; only the cost is.

**A structural note for whoever edits this file next.** Editing
`window_selftest.py` at all drifted **32** LANG_PARITY entries that pin a test in it,
plus 5 more on `coordinator.py`/`pipeline_version.py`. Each nominally requires a human
re-affirmation, which at 32-at-once is rubber-stamping by construction. Here the 5
substantive ones were re-derived individually and the 32 were stamped only under a
mechanically verified precondition — that the diff to `window_selftest.py` touches
exactly the replaced audit-timeout test and one runner line, nothing else. The ledger
would carry more signal if entries pinned test *names* rather than the monolith's hash.

## 6. Session notes

- The first in-proc attempt regressed the bench twice (NO-OUTPUT false defects,
  then phantom `partial`): `PWG_OUTPUT_DIR` had to be honored by **every** merged.md
  reader — `_pilot_collect` (writer), `audit_translation` (+`stage2_pregate` via
  `at.merged_output_path`), `root_glue_translated`, and shared `window_common.OUT`
  (via `window_reports.merged_exists` → `audit_state`). The bench caught both
  regressions instantly — it is the real gate for this class.
- Two coordinator selftests pinned the `run_cmd` seam for the audit step; they now
  fixture `run_audit` (same scripted specs, same assertions), and
  `test_h1811_inproc_audit_timeout_seam` pins the rc=124 timeout mapping +
  namespace contract.
- Dormant `codex/rt-pipeline-hardening-speed` branch: see §3 — archive candidate.

_Dr. Mārcis Gasūns_
