# H1386 prepare-stage batching — A/B bench evidence (closes the H1339 25% speed target)

_Created: 22-07-2026 · Last updated: 22-07-2026_

Executor: Fable 5 (`claude-fable-5`), [H1386](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1386-Fable_RussianTranslation_pwg-ru-post-h1339-resume-fixes-prepare-speed_20.07.26.md).
Method: [`src/pilot/h1339_offline_bench.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_offline_bench.py)
(H1339's committed hermetic bench, now fully sandboxed per H1386 P3f — `PWG_INPUT_DIR` +
`PWG_EVENTS_PATH` overrides, `finally:` teardown), 2 warmups + **10 measured runs per
mode**, offline, zero model calls, on the H1386 worktree at `4a3efa99` + the H1386 fixes.

## What changed

`coordinator prepare-batch` (H1386 OPT) prepares N claimed leases in **one** coordinator
process and runs the two per-lease prepare children (`perf_preflight` cost gate +
`gen_opt_harness2` harness/manifest generation) **in-process** via
`audit_window.run_py_inproc` — the H1339 runpy-gates pattern applied to the prepare
stage, which H1339's own closeout named as the remaining dominant per-lease
interpreter-spawn cost. 3 interpreter spawns per lease become 0 marginal spawns per
lease. Per-lease semantics are identical (same operation tokens, same cost gate, same
artifacts, same state transitions).

## A/B result (5-lease fixture, medians over 10 runs)

| Stage | per-lease (pre-H1386) | prepare-batch (H1386) | Δ median |
|---|---|---|---|
| **prepare** | median 11.669 s · p95 15.546 s | median 3.263 s · p95 5.426 s | **−72.0%** |
| total | median 27.892 s · p95 37.070 s | median 21.763 s · p95 28.639 s | **−22.0%** |

- **Semantic store equality: PROVEN.** Both modes produce the identical deterministic
  output signature `da1341e6ac11…` on every one of the 10+10 runs (`deterministic: true`,
  one signature per mode, signatures equal across modes) — same store rows, same TM, same
  per-lease final states (fx1 promoted 3 clean · fx2 promoted_partial 1 clean +
  transient/defect backlog · fx3 promoted 2 · fx4 promoted 1 · fx5 promoted 3).
- **Stage gate:** the H1339 constraint was "ship only stages that clear the 25% stage
  gate; never weaken a guard to manufacture the last points." Prepare clears at −72.0%
  with zero guard changes (the cost gate, operation tokens and manifests are the same
  code, run in-process). Combined with H1339's measured −23.0% pipeline win, the
  offline-path total is now well past the original ≥25% target.
- Machine-readable reports: [`h1386_bench_perlease.json`](h1386_bench_perlease.json) ·
  [`h1386_bench_batch.json`](h1386_bench_batch.json) (committed beside this memo;
  generated under gitignored `src/pilot/output/` and copied here as evidence).

## Caveats

- The bench's `total` includes stages H1339 already optimized; the −22.0% total here is
  measured against the *per-lease-prepare* shape on the same H1386 code, not against the
  pre-H1339 baseline (that comparison was H1339's own PARTIAL −23.0%).
- `--prepare-mode per-lease` is kept in the bench for future A/B evidence; production
  callers opt into `prepare-batch` explicitly — `coordinator prepare` is byte-identical
  in behavior and stays the default single-lease form.
- In-process children accept the `timeout=` parameter for signature parity but cannot
  enforce it per child; the prepare stage's own operation deadline
  (`PREPARE_TIMEOUT_SECONDS`, checked between children) still applies.

_Dr. Mārcis Gasūns_
