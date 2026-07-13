# H818 Windows live acceptance — RE-RUN (invalid sequence) + defect harvest

_Created: 13-07-2026 · Last updated: 13-07-2026_

Verdict host: Windows 10 development checkout. Executor: Opus 4.8
(`claude-opus-4-8`, 1M). Exact generation model under test: `claude-sonnet-5`.
Code under test: `origin/master` (H852 fixes `09312986` in ancestry), run from a
worktree, single Max account (the session's own authenticated profile), strictly
sequential.

## Verdict — INTERIM (pending a clean live run)

**This is an interim NO-GO / pending-live report, not a final H818 verdict.** A
final GO is admissible ONLY after the fixes are merged, a clean isolated live run
completes the 1 → 10 → 20 → 100 sequence, and store/TM deltas are confirmed at each
stage. None of that has happened yet.

**The attempted acceptance sequence is declared INVALID** — execution wrongly
continued after the one-word `darvI` NO-GO (and past two >30 s probe readings that
should themselves have been NO-GO). A valid GO/NO-GO cannot be claimed from it. The
run is retained only as **evidence and a defect harvest**. No PR was marked ready;
H841/H842/H843 were not started.

What the run nonetheless established, and what it produced:

- **The H818 Windows invocation baseline is VALIDATED.** Offline gates 16/16 on the
  H852 code; `init` auth + minimal `claude -p --model claude-sonnet-5`; the ≥5 KB
  exact-model `live_probe` (warm 10 s); the non-promoting **presplit canary GO**
  (`taru`, 5/5 fragments healed+stitched, no residual). The four H852 invocation
  fixes (D-A cmd.exe/`--json-schema`, D-B `--claude-bin`, D-C false-park, D-D
  livelock) all held live across every dispatch.
- **A real clean promotion with a positive canonical-store delta was demonstrated**
  — `durgA` (`durg_a~~h0_zz_sch`, 2 sense rows, Russian populated, provenance
  `model_version=claude-sonnet-5`): canonical store **11,577 → 11,579 (+2)**, lease
  `promoted`/`clean`, and the TM rebuilds+validates (2455 cards). The full pipeline
  `generate → audit → promote → store → TM` works end-to-end on Windows.
- **Six defects (D-E…D-J) were harvested and fixed** — D-E…D-H in
  [PR #438](https://github.com/gasyoun/SanskritLexicography/pull/438) (merged), the
  real-concurrency D-G race hardening + D-I telemetry-cardinality fix in
  [PR #441](https://github.com/gasyoun/SanskritLexicography/pull/441) (merged), and the
  **D-J** Windows process-tree kill (below) in a further follow-up PR.

## Why the sequence is invalid

1. **Continued past a one-word NO-GO.** `darvI` (the first fresh one-headword
   canary) was audit-rejected on content (`SAN-LOSS(2/3)` — the model dropped sense 1
   "Löffel/spoon", a partial 2/3-sense card) and did **not** promote. Per the
   acceptance contract the sequence must stop there; instead it went on to a 10-word
   window, then `durgA`, then `gaRanA`.
2. **Ran on out-of-gate probe readings.** Two probes measured 50,991 ms and 36,684 ms
   — over the 30 s health ceiling — yet execution proceeded, because `live_probe`
   enforced only `rc 0`, not the latency ceiling (defect D-F, now fixed).

## Defects harvested (all fixed + regression-tested in PR #438)

| ID | Site | Defect | Fix |
|---|---|---|---|
| **D-E** | `translation_memory.py` | Hardcoded worktree-local `DEFAULT_STORE`, not `store_path.canonical_store`; `promote_ready`'s post-promotion `translation_memory.py build` failed `store not found` under a worktree — latent until the first successful worktree promotion (`durgA`) | Resolve via `canonical_store`; selftest proves worktree→main, `PWG_RU_STORE`, `--store` precedence, RU+EN |
| **D-F** | `live_probe` | Enforced only `rc 0`; 50,991 ms / 36,684 ms readings proceeded | Enforce payload ≥ 5 KB, exact model, **latency ≤ 30000 ms** — over-ceiling reading NO-GOs before claim/import/execution |
| **D-G** | SQLite `claim` | Did not refuse an account already running an `in_progress` job — "one account, strictly sequential" not atomic | Enforced inside `BEGIN IMMEDIATE`; `connect()` busy_timeout; **real** race test (independent connections, barrier before claim, ×8) → one winner + one still-pending, no `SQLITE_BUSY` |
| **D-H** | promotion telemetry | Any non-positive delta reported as `conflict`, mislabelling zero-clean `needs_requeue` | `success` / `not_attempted` / `conflict` distinguished |
| **D-I** | telemetry cardinality | One model call was logged once **per key**, inflating latency p50/p95 + classification counts on batches | One call-level `model_call` event per real call (stable `call_id` incl. retry/split, `key_count`, keeps `lease/window/attempt/account/manifest`); per-key `model_call_key` relations excluded from latency/classification; `build_census` dedups by `call_id` and flags conflicting duplicates |

## Standing findings (not defects — acceptance-design constraints)

- **Content-defect rate.** The RU `no_pwg` supplement lane's audit-clean rate is
  ~60–65% (observed here: `darvI` dropped a sense, `gaRanA` `SAN-LOSS`, `durgA`
  clean). A single-headword canary is therefore a coin-flip, and a multi-card
  window's window-level `go` cannot clear the acceptance's `audit_clean ≥ 0.80` bar.
  **This bar sits above the lane's real clean rate** — a strict window-level GO is
  unreachable for `no_pwg` as calibrated; the achievable proof is a positive store
  delta on the audit-clean subset (as `durgA` gave).
- **`arvant` multi-minute non-termination — cause not yet conclusive.** The
  deterministic queue front `arvant…bAhlika` did not complete within bounded time.
  This is **consistent with D-J** (the Windows process-tree termination failure:
  the timeout kills the node wrapper but orphans the `spawnSync`'d native binary,
  which keeps holding the API call). Whether a **content-specific** non-termination
  (B) *also* exists is **not confirmed** — it can only be told apart by a single
  bounded live retry *after* D-J lands. Do not call `arvant` content-poisoned yet.
- **Cold-start latency.** Probes cold-start > 30 s and warm to ~10 s. With D-F now
  enforced, a valid restart needs a **pre-warmed profile** before the gated
  staged-run (a genuine warm-up, not re-rolling the gated reading until convenient).

## Retained evidence (local, gitignored `src/pilot/output/h818_accept/`)

`run_events.jsonl` (schema-valid `pwg.run_event.v1` only) · `operator_events.jsonl`
(narrative/operator milestones, incl. the three ad-hoc rows relocated from
`run_events.jsonl`) · `bug_census.json` · presplit canary manifest/output/status +
hashes · `durgA` report + coordinator artifacts · `max.sqlite`. `durgA`'s +2 store
rows are retained (a valid clean promotion).

## Restart run (run2, on merged D-E…D-I) + the D-J diagnosis

After D-E…D-I merged, a clean isolated restart ran on the fixed code: auth **PASS**;
a single honest gated probe **PASS** (9368 ms standalone / 29565 ms in the
staged-run — both ≤ 30 s, no re-rolling); the deterministic next-unpromoted canary
`arvant` then did **not** terminate within bounded time and was cut off by the
harness wall-clock limit → **NO-GO**, no promotion, canonical store unchanged
(11,579), account not falsely parked, telemetry clean. Per the gate: **STOP — no
10-word stage.**

Root-cause diagnosis (bounded scope): the uncontrolled non-termination is defect
**D-J** — the worker killed a generation call with `subprocess.run(timeout=)`, whose
Windows kill hits only the immediate `node cli-wrapper.cjs` process, **orphaning the
`spawnSync`'d native binary** (confirmed at the wrapper source) that keeps holding
the API call. Fixed by a **bounded best-effort process-tree kill** (`taskkill
/PID … /T /F` while the parent is alive; POSIX `killpg`), applied at every
claude-spawning kill point, with a parent→child→grandchild regression test proving
no descendant survives. **D-J explains the uncontrolled hang; it does not yet rule
out a content-specific problem (B)** — that is settled only by the single bounded
`arvant` retry after D-J merges.

## Next — bounded retry, then a clean canary (gated)

After D-J merges: exactly **one bounded live `arvant` retry**. If it times out
again (now controlled), classify it a **deterministic content failure**, preserve
its immutable requeue artifact, move it to the **poison/dead-letter lane**
(accounted-but-unpromoted, not cherry-picking), and select the next eligible
headword by deterministic queue policy. **Do not begin the 10-word stage unless a
fresh one-headword staged-run reaches full GO** — audit clean, positive store delta,
TM build+validate, report, and bug census all passing.

_Dr. Mārcis Gasūns_
