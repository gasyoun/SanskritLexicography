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
| S1 | `process_record_output` spawns `audit_window.py` per lease | [`coordinator.py:1537-1546`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) | run audit in-proc via the proven `run_py_inproc` pattern (already used by prepare-batch, `coordinator.py:1069`); 30-min audit timeout re-imposed via worker thread | ~0.5–0.9 s/lease |
| S2 | `_pilot_collect` is the last subprocess gate | [`audit_window.py:234-237`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) | route through existing `run_py_inproc` (H1339 pattern; the other 5 gates already in-proc) | ~0.3–0.5 s/lease |
| S3 | `component_sha` re-hashes the same files per `stamp()` — 30 calls/promote batch, ~27 % of batch-promote in-proc time (cProfile) | [`pipeline_version.py:90-108`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py) | per-process memo keyed on (patterns, root) | ~0.27 s/promote |

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
| S3 component_sha memo | ✅ DONE (pipeline_version selftest OK) | this branch | `pipeline_version.selftest` stamp-memo block |
| S2 collect in-proc | ✅ DONE (bench-verified) | this branch | bench outcomes == baseline |
| S1 audit in-proc | ✅ DONE (bench-verified) | this branch | bench outcomes == baseline |
| H5 corrupt status | ✅ DONE (code; gate pending) | this branch | — |
| H10 collect OUT override | ✅ DONE — needed **five** readers patched, not one: `_pilot_collect`, `audit_window`, `audit_translation` (feeds `stage2_pregate` via `at.merged_output_path`), `root_glue_translated`, **and shared `window_common.OUT`** (feeds `window_reports.merged_exists` → `audit_state`). Missing the 4th/5th caused first NO-OUTPUT defects, then phantom `partial` states — the bench caught both instantly | this branch | bench hermeticity + outcomes == baseline |
| H1 manifest crash | ⏳ handed to Opus 5 ([H1940](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1940-Opus_RussianTranslation_pwg-ru-h1811-integrate-verify_30.07.26.md)) | — | — |
| H2a/H2b budget notes | ⏳ handed to Opus 5 (H1940) | — | — |
| H3 fsync checkpoints | ⏳ handed to Opus 5 (H1940) | — | — |
| H4 dup lease-id | ⏳ handed to Opus 5 (H1940) | — | — |
| H7 drain spin | ⏳ handed to Opus 5 (H1940) | — | — |
| H8 preflight timeout | ⏳ handed to Opus 5 (H1940) | — | — |
| H9 cohort stranding | ⏳ handed to Opus 5 (H1940) | — | — |

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

Gate status on the rebased branch, and the one red:

- `window_selftest` — 194 defined, **193 PASS / 1 FAIL**.
- `lang_parity_check` — **3 violations**, all inherited: `citation_tm.py`,
  `corpus_gate.py`, `annotate_genres.py` drifted under H1902
  ([PR #892](https://github.com/gasyoun/SanskritLexicography/pull/892),
  `af299375`). All three are **byte-identical between `origin/master` and this
  branch** (`git diff --name-only origin/master HEAD` lists none of them), so
  the drift is master's own re-affirm debt. Not stamped here — per H1940, a
  human re-affirms the verdicts on files this PR did not touch.
- The single `window_selftest` failure is `test_lang_parity_ledger_complete`,
  i.e. the same three inherited entries surfacing through the suite. No other
  test fails.

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
