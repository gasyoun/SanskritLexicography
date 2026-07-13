# H818 Windows live acceptance — GO/NO-GO report

_Created: 13-07-2026 · Last updated: 13-07-2026_

Verdict host: Windows 10 development checkout. Executor model: Opus 4.8
(`claude-opus-4-8`, 1M). Exact generation model under test: `claude-sonnet-5`.
Code under test: PR [#416](https://github.com/gasyoun/SanskritLexicography/pull/416)
(`codex/h818-windows100-readiness`), **already merged** to `master` at
[`30fdeef9`](https://github.com/gasyoun/SanskritLexicography/commit/30fdeef9); run
from a worktree off `origin/master` whose H818 pilot code is byte-identical to the
#416 tip (empty diff). Single Max account, strictly sequential.

## Verdict

**NO-GO.** The mandatory non-promoting presplit canary (acceptance step 3) FAILED,
and the promoting path (step 4) FAILED before any generation, on **four distinct
Windows / robustness defects** in the H818 headless dispatch code. No window was
promoted; the canonical store is **unchanged at 11,562 rows**; no data was lost.
Per the acceptance contract, the run stopped at the first failed criterion — the
PR is **not** marked ready and the downstream production handoffs (H841/H842/H843)
are **not** started.

This is a strictly deeper result than the prior audit
([`PIPELINE_AUDIT_2026-07_H818.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_AUDIT_2026-07_H818.md)),
which was blocked at `401` authentication and never exercised generation. Here
authentication and the exact-model probe **passed**, so the run reached the
headless generation layer and surfaced the real Windows portability defects.

## Resolution — H852 (13-07-2026): all four defects fixed + verified

The four defects below were fixed in
[H852](https://github.com/gasyoun/Uprava/blob/main/handoffs/H852-Opus_SanskritLexicography_h818-windows-headless-invocation-fix_13.07.26.md)
and re-verified on this Windows host: **presplit canary GO** (classification
`success`, was `process`); the 1-headword `staged-run` job returned `done`/`success`
(worker generated via node-direct, was `[WinError 2]`); the account was **not
falsely parked** (`quota_incidents=0`); `staged-run` finished in 562 s (was a 6-min
busy-loop). Offline D-A/D-C unit tests were added. The Windows headless **invocation**
baseline is now functional; the one residual non-GO in the re-run was `arvant`
audit-rejected on **content** (the H255/H834 content-hard class), not invocation.

## What passed (gates cleared before the failure)

| Gate | Result | Evidence |
|---|---|---|
| Step 1 — all offline gates | PASS | `py_compile` OK; selftests PASS: `store_path`, `run_observability`, `max_account_orchestrator` (recover/timeout/retry/crash-after-output/rate-park/import), `headless_worker` (incl. presplit heal/stitch), `windows100`, `window`, `h809`, `agent_budget`; `lang_parity` (47, no drift); `launch_ledger` (15); `roadmap_check`; final-card schema; `run_pilot_wf.js` |
| Step 2 — auth status | PASS | `claude auth status --json` → `loggedIn=true`; `init` validated account `max1` |
| Step 2 — minimal exact-model call | PASS | `init` ran `claude -p 'Return exactly OK.' --model claude-sonnet-5` → rc 0 |
| Step 2 — ≥5 KB exact-model probe | PASS | `live_probe` (6.5 KB, `--json-schema --model claude-sonnet-5`) rc 0; latencies 31951 → 23585 → 9583 ms (cold-start decay; warm 9.6 s < 30 s health ceiling) |
| Preconditions | PASS | canonical store present (11,562 rows); **149** unpromoted queue headwords (of 232), **all absent from store → net-additive → positive deltas**; fresh isolated worktree coordinator dir |

## What failed — four defects (deterministically classified)

### D-A · presplit canary (step 3): cmd.exe corrupts the `--json-schema` argv via the `.cmd` shim
`headless_worker.call()` invokes `[claude, '-p', …, '--json-schema', <output_schema>, …]`.
On Windows the only available `claude` launcher is the npm **batch shim
`claude.cmd`**, so Python routes the call through `cmd.exe`, which re-parses the
command line. The card `output_schema` (1,573 chars) contains `<`×4 and `>`×4 —
**cmd.exe redirection metacharacters** — plus 214 quotes; cmd.exe mangles the arg
and emits *"The system cannot find the file specified."* (locale-encoded).
- Reproduced both with and without `env=`; the tiny `{"ok":boolean}` probe schema
  (~90 chars, no metachars) survives, the real card schema does not.
- **Verified fix direction:** `node ".../@anthropic-ai/claude-code/cli-wrapper.cjs"
  -p … --json-schema <real schema> …` (bypassing cmd.exe) → **rc 0, valid result**
  in 36 s. Larger schemas would additionally hit the cmd.exe ~8191-char ceiling.
- Classification: `process` (worker) — Windows CLI-shim invocation defect.
- Evidence: `presplit_canary_status.json` (`classification: process`, error
  "cannot find the file specified"), `run_events.jsonl` (5 `process` `model_call`
  rows for `taru_f0..f4`, elapsed ~20 ms each).

### D-B · promoting path (step 4): `run_claimed` never forwards `--claude-bin`
`max_account_orchestrator.run_claimed` builds the `headless_worker` argv **without
`--claude-bin`**, so the worker falls back to its default bare `claude`, which is
not invokable via Python `subprocess` on Windows → **`[WinError 2]`**. The probe
and presplit-canary paths only work because they pass `--claude-bin` explicitly;
the actual window runner does not, so no production window can generate on Windows
even before D-A applies.
- Classification: `configuration` (worker), exit 2.
- Evidence: `…/h818_c1_w01/…attempt1.status.json` (`classification: configuration`,
  `[WinError 2]`), `…attempt1.runner.json` (returncode 2).

### D-C · false rate-limit park: `RATE_LIMIT` regex matches the `manifest_sha256` hash
`run_claimed` classifies rate-limits by `RATE_LIMIT = re.compile(r"rate.?limit|usage
limit|too many requests|429")` searched over `combined` (worker stdout+stderr) — which
**includes the printed `manifest_sha256`**. The step-4 hash
`…80179`**`429`**`d4f8…` contained the substring `429`, so a **configuration error
(D-B) was misclassified as a rate-limit** and the account was parked 5 h (default,
no machine-readable reset). The real Max account was **never** rate-limited by the
API — the park exists only in the test SQLite. In production this would spuriously
park a healthy account on ~1-in-many runs (any sha256 containing `429`).
- Evidence: job `h818_c1_w01` → `state=pending, failure_class=rate_limit,
  parked_until=1783936323` (13-07-2026 12:52, exactly run-time + 5 h) while the
  worker status said `configuration`.

### D-D · `staged-run` livelocks when all accounts are parked
With the account parked (D-C) and a job pending, `cmd_staged_run`'s `while True`
loop has no sleep and no all-parked deadlock exit: `run_once` finds no runnable
job, `record_done`/`promote-ready` no-op, and it **spins indefinitely** (observed:
6+ min of CPU + repeated `promote-ready` subprocess spawns until killed).
- Classification: robustness/liveness defect.

## GO criteria — none reached

The runbook GO (per `cmd_staged_run.go`) requires: windows==expected,
headwords==expected, no duplicate/unaccounted keys, cards==selected_keys, no hard
failures, **every window a positive canonical-store delta**, audit_clean/cards ≥
0.80, fidelity/cards < 0.05, and (mandatory pre-GO) a passing non-promoting
presplit canary. The presplit canary failed (D-A) and no window generated (D-B),
so **no GO criterion was evaluated on real output**. Result: **NO-GO**.

## Store & account safety (no harm done)

- Canonical store `RussianTranslation/src/pwg_ru_translated.jsonl`: **11,562 rows
  before and after** — zero promotions, zero mutations, zero lost/duplicate keys.
- c1 lease `h818_c1_w01`: `state=prepared`, `store_delta=None` — never recorded,
  audited, or promoted (no requeue artifact exists because it never reached audit).
- Real Max account: healthy; the only "rate-limit" was the D-C false positive in
  the disposable test DB. No A/B experiments were run; no Linux was provisioned;
  credentials were never inspected, printed, copied, or modified (auth checked only
  via `claude auth status` / the orchestrator's own `init`).

## Recommended fixes (for the follow-up handoff — NOT applied here)

1. **Windows-safe CLI invocation** (fixes D-A): resolve a `.cmd`/`.ps1`/
   extensionless `claude` launcher to `[node, <cli-wrapper.cjs>]` and invoke that
   directly (bypasses cmd.exe; verified working), or accept a multi-token launcher.
   Apply in `headless_worker`, `live_probe`, `profile_status`.
2. **Forward `--claude-bin` through dispatch** (fixes D-B): thread `claude_bin`
   from `staged-run` → `cmd_run_once` → `run_claimed` → the `headless_worker` argv.
3. **Tighten rate-limit detection** (fixes D-C): classify rate-limits from the
   worker's `classification`/API error payload, not a regex over `combined` that
   includes the `manifest_sha256`; at minimum exclude the hash from the search text.
4. **Parked-account guard in `staged-run`** (fixes D-D): when jobs are pending and
   all accounts are parked, sleep to the earliest `parked_until` or exit with a
   clear "all accounts parked until <t>" message.

After these land in a separate PR, re-run this Windows acceptance from step 2.

## Retained artifacts (local, gitignored `src/pilot/output/h818_accept/`)

`run_events.jsonl` (12 events: probes + canary + c1) · `bug_census.json`
(`process:5, rate_limit:1, success:5`; p95 41.3 s; quota_incidents:1) ·
`presplit_canary_manifest.json` (heavy `taru` fixture, `presplit_keys=['taru']`) ·
`presplit_canary_status.json` · `presplit_canary_harness.js` · `plan_c1.json`
(headword `arvant`) · `…/coordinator/artifacts/h818_c1_w01/…attempt1.{runner,status}.json`
· `max.sqlite` · `c1.sqlite` (holds the D-C false park). No PR review flag flipped;
H841/H842/H843 not started.

_Dr. Mārcis Gasūns_
