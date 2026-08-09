# H963 — single-profile c4 Gate-0 health attempt (fresh dated D-K reading)

_Created: 16-07-2026 · Last updated: 02-08-2026 (**EIGHTH READING: GATE-0 PASS — measured 43 815 ms, the fastest decomposed c4 reading on record, and the canary then passed too, so the gate returned `LIVE_GO`. The 31-07 rate-limit root cause below is HISTORICAL: quota stopped binding when auth was restored on 01-08**)_

**Verdict: `C4 HEALTH NO-GO` · `CANARY NOT LAUNCHED` · `RUNG 3 NOT ENTERED` · `NO PRODUCTION TRANSLATION` · `canonical store unchanged at 11,605`.**

This is a **single-profile c4** measurement. It is **not** a two-profile or four-profile
acceptance, and it earns **no** production readiness. It is one **new dated** health reading —
it does **not** overwrite, replace or reinterpret the historical 15-07-2026 NO-GO, which stands
unchanged.

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`), Claude Code, Ultracode, probing the exact
generation model `claude-sonnet-5`. Run from a clean worktree off `origin/master`
[`9d7d00d0`](https://github.com/gasyoun/SanskritLexicography/commit/9d7d00d0) (`v1.9.19-9`,
i.e. probe tooling ≥ [v1.9.17](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.17)
with the D-P natural schema-carrying prompt). Handoff:
[H963](https://github.com/gasyoun/Uprava/blob/main/handoffs/H963-Opus_SanskritLexicography_pwg-ru-four-profile-live-ladder-acceptance_15.07.26.md).

## Gate 0 — auth (credential-safe, read-only)

| Profile | `CLAUDE_CONFIG_DIR` | `loggedIn` | Tier |
|---|---|---|---|
| **c4** | `D:\ClaudeTools\profiles\claude4\.claude` | ✅ `true` | `max` |

`claude auth status --json` only; **only** the `loggedIn` / `subscriptionType` fields were read.
No credential material was printed, copied, requested or modified. c1 / c5 / c6 were **not**
touched (out of scope for this session). **Auth = PASS.**

## Gate 0 — one fresh dated D-K health attempt (`run_id=h963-c4-single-profile-gate0-2026-07-16`)

Exactly **one** attempt: one warm-up call, then one measured call. **No retry, no re-warm, no
reroll.** Both readings were emitted to append-only telemetry *before* the fail-closed exit, so
this NO-GO leaves the same immutable trace a PASS would.

| Phase | elapsed | classification | output bytes | vs 30 000 ms ceiling |
|---|---|---|---|---|
| warm-up | **53 290 ms** | `success` | 1 488 B | ❌ 1.78× over |
| measured | **104 870 ms** | `success` | 1 487 B | ❌ **3.50× over** |

- **Payload:** `payload_bytes=6491` → **actual prompt 6 828 B** (≥ the 5 000 B repository floor and
  ≥ 5 KiB = 5 120 B). Matches the H909-runbook corrected figure. **Not undersized.**
- **Connection errors: 0.** Both phases classified `success` — a valid Claude CLI result envelope
  carrying the structured schema result `{"ok": true}`. Neither `process` nor `timeout`.
- **Exact model:** `claude-sonnet-5`, `--permission-mode plan` (the same mode the real generation
  path `headless_worker.call` uses).

**This is a pure-latency NO-GO.** It is not authentication, not a connection error, not a
malformed report, not an undersized payload, and not the D-P refusal artifact — the probe
returned clean, well-formed structured output **both** times. c4 is *responsive but far too slow*.

### It is ~2× worse than the 15-07 baseline

| Reading | 15-07-2026 (H994/H963 baseline) | **16-07-2026 (this attempt)** | Change |
|---|---|---|---|
| warm-up | 29 743 ms | **53 290 ms** | ~1.8× slower |
| measured | 52 815 ms | **104 870 ms** | ~2.0× slower |

The fresh reading does not merely reproduce the historical NO-GO — it is substantially **worse**,
on the same tooling, same profile, same exact model and a same-size representative payload.

## Robustness of the verdict

The NO-GO does **not** depend on any contested interpretation:

- The **fastest** reading in this attempt (53 290 ms warm-up) is already **1.78× the ceiling**.
- Under the resume brief's strict rule (**either** reading ≥ 30 000 ms ⇒ NO-GO) — NO-GO on both.
- Under `live_probe`'s own, laxer gate (warm-up excluded; only the measured reading is gated) —
  still NO-GO, at 3.50× the ceiling.
- The independent mechanical gate in
  [`probe_log.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py)
  derived `NO-GO` from the raw numbers on its own (`latency 104870ms > 30000ms`), and
  `probe_log.py gate` now exits **1** (fail-closed), mechanically blocking a launch.

There is no reading of this evidence under which c4 passes a 30 s health ceiling.

## What did NOT happen (explicitly)

- ❌ No canary — `dq_canary_puregloss` was **not** run. Rung 3 was **not** entered.
- ❌ **No production translation of any kind. Production translation has not started.**
- ❌ No 10- or 20-headword window; no promotion; no canonical-store write; no TM rebuild.
- ❌ No reroll after the failed gate; no second probe.
- ❌ No c1 / c5 / c6 use. No four-profile (or two-profile) readiness claim.
- ❌ No use of the unmerged [PR #495](https://github.com/gasyoun/SanskritLexicography/pull/495)
  bounded-staged-run implementation.
- ❌ No language-parity hash update.
- ✅ **Canonical store `RussianTranslation/src/pwg_ru_translated.jsonl` verified unchanged:
  11,605 rows, mtime 2026-07-14 07:22:24** — byte-identical to the state H994 recorded. The probe
  performs no store write by construction; `PWG_RU_STORE` was additionally pinned to a scratch
  path, and that scratch file was never created.

## Defect surfaced — D-R · `claude_argv_prefix` is defeated by its own default

The first invocation died with `FileNotFoundError [WinError 2]` **before any probe call was made**
(zero events emitted — no attempt consumed, so correcting it was not a reroll).

**Root cause.**
[`claude_argv_prefix`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
resolves the npm shim via `shim_dir = os.path.dirname(os.path.abspath(claude_bin))`. For the
repository default — the **bare name** `'claude'` (`live_probe(..., claude='claude')`,
`probe_fleet(..., claude='claude')`, and every `--claude-bin` default: `init`, `run-once`,
`staged-run`) — `os.path.abspath('claude')` yields `<CWD>/claude`, so `shim_dir` becomes the
**current working directory**. The `node_modules/@anthropic-ai/claude-code/cli*.cjs` lookup
therefore searches the CWD, never the npm shim directory, always misses, and falls back to the
bare `[claude_bin]`.

**Two consequences — the second is environment-independent and the more serious:**

1. On this environment the fallback `['claude']` cannot be launched by Windows `CreateProcess`
   (the real file is a `.cmd` shim) → the probe cannot run at all.
2. **The H818 D-A protection is silently inactive whenever the bare default is used.** That
   function exists specifically to bypass `cmd.exe` so a `--json-schema` argument's `<` / `>`
   characters are not reinterpreted as redirection and the ~8191-char command-line cap does not
   truncate a real card schema. A bare default can never reach its `[node, cli*.cjs]` form, so any
   caller relying on the default silently loses that protection.

The documented commands in
[`ORCHESTRATION_4ACCOUNT_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ORCHESTRATION_4ACCOUNT_MAX.md)
pass no `--claude-bin`, so they take this default.

**Workaround used here (scoped to this probe script only — the orchestrator was NOT modified):**
resolve the real `.cmd` shim path, which lets the prefix reach its intended form
`['C:\Program Files\nodejs\node.EXE', '…\@anthropic-ai\claude-code\cli-wrapper.cjs']`. A
**pre-flight assertion** now aborts *without making a call* if the prefix does not resolve to
`[node, cli*.cjs]`, so a mis-resolved binary can never consume the one no-reroll attempt.

Fixing the orchestrator default is deliberately **not** done in this NO-GO reporting pass — it
touches the live generation path and belongs to its own handoff with its own selftest.

## Limitations (stated, not resolved)

- **Single measurement, by design.** The brief forbids repeating the probe after a failed gate, so
  no variance estimate is available from this pass. The historical record already describes c4's
  home route as high-variance (~30–53 s).
- **Self-profile contention is a confound I cannot exclude.** This orchestrating session itself runs
  on the c4 profile, and the probe spawns `claude -p` subprocesses against those same credentials,
  so the readings may include contention from the parent session. **The 15-07 baseline shares this
  exact confound** (that session was also c4-hosted), so the ~2× degradation is a like-for-like
  comparison — but neither pass isolates it. Disambiguating would need a probe from a
  non-c4-hosted session, which is out of scope here and must not be done by re-rolling this gate.
  **The verdict does not rest on this**: even the fastest reading is 1.78× the ceiling.
- **Anomaly: the second call was SLOWER than the first, with no rest between them.** The measured call
  began ~2 ms after the warm-up returned (derived from the raw event timestamps: warm-up completed
  07:55:58.121Z, measured completed 07:57:42.993Z minus its own 104 870 ms) — yet took ~2× as long
  (104 870 ms vs 53 290 ms). This is the **opposite** of the cold-start pattern the warm-up exists to
  absorb (`live_probe`'s warm-up is documented as stabilizing the cold connection). Output size does
  **not** explain it: 1 487 B vs 1 488 B, i.e. both calls returned the same tiny `{"ok": true}` envelope.
  This shape is *consistent with* contention accumulating across the ~2.5-minute window on the shared c4
  profile, but that link is **not asserted here** — only the anomaly is recorded, and it remains
  unexplained. It does not change the verdict (the faster reading is still 1.78× the ceiling).
- **Machine load and network conditions were not instrumented** and cannot be reconstructed from the
  captured telemetry; they remain residual unquantified confounds.
- **This says nothing about c1/c5/c6, nor about quality.** Responsiveness is a precondition for, not
  evidence of, clean card generation. No SAN-LOSS / TNMASK / `dropped_sanskrit_span` false-flag rate
  was measured — rung 3 remains the open measurement.
- **A rung-3 blocker beyond latency persists** (recorded by H994, re-confirmed here): `src/pilot/input/`
  is gitignored and absent in a fresh worktree, so the canary portrait must be rebuilt before
  `dq_canary_puregloss` can run even once the latency rung passes.

## Immutable evidence

| Artifact | SHA-256 |
|---|---|
| `src/pilot/output/h963_c4_gate0_probe_events.jsonl` (raw readings) | `c2a930d532090848d549c709b64f8111dd9b9b9c0c4026e613a7f8c83723d006` |
| `src/pilot/h963_c4_gate0_probe.py` (the attempt) | `100f58235aa3f5a6e0c06b1dc83c8fa39707eac1f6faac07fc89e1b41d3b3a5c` |
| `src/pilot/generation_api_probe_log.jsonl` (after append) | `03f5184727d36ce5947fdbac53b4228248819428a66904a50b59249c056f9eb3` |

Rendered reading table:
[`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md)
(22 readings / 9 outcomes).

## What this moves

| Gate | Before | After this attempt |
|---|---|---|
| c4 auth | c4 Max (15-07) | **re-confirmed PASS** — `loggedIn: true`, `max` |
| c4 home-route latency | ~30–53 s NO-GO (15-07) | **NO-GO re-confirmed and WORSE** — 53 290 / 104 870 ms, both `success` |
| probe reliability | D-P fixed (v1.9.17) | **new defect D-R** — `claude_argv_prefix` defeated by its own bare default |
| rung 3 canary | prepared, not run | **still not run** (latency gate not passed) |
| canonical store | 11,605 | **11,605 (verified untouched)** |
| four-profile readiness | NO-GO (c5/c6 out) | **NO-GO, unchanged** — not addressed here |

## Recommended next step (a human decides)

The blocker is **latency, not authentication** — logging in c5/c6 would **not** unblock this gate.
Two consecutive dated measurements now put c4's home route decisively over the 30 s ceiling, the
second ~2× worse than the first, which is consistent with the H818/H895 ~40 s NO-GOs.

The open path remains the **foreign-route latency investigation**, currently
🟠 archived-deferred as
[H909](https://github.com/gasyoun/Uprava/blob/main/handoffs/H909-Opus_SanskritLexicography_h818-foreign-route-paired-probe-analysis_14.07.26.md)
(prep + runbook ready at
[v1.9.19](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.9.19); the analysis never
ran). This reading is fresh evidence for re-opening it. Whether to re-open H909, and whether the
home route is simply not viable for this workload, is a decision for a human — it is not
self-resolved here, and no threshold was silently chosen or hard-reject armed.

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`), Claude Code, Ultracode, executing the H963
Gate-0 single-profile c4 health attempt: one fresh dated D-K reading, no canary, no promotion, no
store/TM mutation, no reroll._

_Dr. Mārcis Gasūns_

---

## Fourth reading, 31-07-2026 13:07Z — the same day, one hour later, 52 % worse

Taken immediately after MG's ruling raised the ceiling to 33 000 ms and made the warm-up
advisory, to re-gate under the new policy.
`run_id …/2026-07-31T13:07:42Z-pid32320` · wall 100.3 s.

| Phase | elapsed | gated? | vs 33 000 ms ceiling |
|---|---|---|---|
| warm-up | 52 268 ms | **no — advisory** | (not a fail; ruling working as intended) |
| measured | **47 953 ms** | yes | ❌ 1.45× over |

**Verdict NO-GO**, on the measured reading alone — the fail list is now one entry, not two, so
the policy change did exactly what it was meant to.

### What this reading actually settles

The two 31-07 measured readings, **~1 hour apart on the same profile and route**:

| 31-07 12:05Z | 31-07 13:07Z | spread |
|---|---|---|
| 31 623 ms | **47 953 ms** | **+52 %** |

So the 31 623 ms figure was **not a new stable regime** — it was the low end of a wide
distribution. That retires the reading of the earlier entry above ("the best c4 has ever
recorded", "cold-start cost the measured call no longer pays"): with n=2 an hour apart, the
honest description is **high variance**, not improvement. The single-reading caveat written
into that entry is the one that held up; the optimistic interpretation is not.

**Consequence for the ceiling question:** a +10 % raise (30 000 → 33 000) does not unblock this
route, and no small raise would — the observed measured band today is ~32–48 s. Clearing it
reliably needs roughly **55–60 s (+85–100 %)**, which is a materially different policy question
from the one that was asked, and is not self-resolved here.

**Second ceiling, found while applying the ruling:** raising the gate alone would not have
started translation anyway. Production dispatch gates on
`max_account_orchestrator.PROBE_LATENCY_CEILING_MS = 30 000` (mirrored at
`coordinator.py:56`), which `probe_fleet` applies when the bounded run parks an account. It is
**deliberately left at 30 000** — changing the number that decides whether real windows spend
money is not the same decision as changing the number that decides whether a probe reports GO,
and it was not the one ruled on.

_Auto-generated by Opus 5 (`claude-opus-5[1m]`), Claude Code, re-gating c4 under the raised
ceiling on operator authorisation: one fresh dated reading, no canary, no promotion, no store/TM
mutation, no reroll._

_Dr. Mārcis Gasūns_

---

## Re-reading 31-07-2026 — NO-GO, but the closest c4 has ever come to GO

`run_id h963-c4-single-profile-gate0-2026-07-16/2026-07-31T12:05:01Z-pid5492` · wall 163.5 s ·
model `claude-sonnet-5` · prompt 6 828 B (floor 5 000 B) · one attempt, no reroll.

| Phase | elapsed | classification | output bytes | vs 30 000 ms ceiling |
|---|---|---|---|---|
| warm-up | **131 737 ms** | `success` | 1 362 B | ❌ 4.39× over |
| measured | **31 623 ms** | `success` | 1 396 B | ❌ 1.05× over |

**`gate_reason = HEALTH_NOGO` → verdict NO-GO.** Stopped there: no canary, no bounded window,
nothing further billed.

### Why this reading matters more than the two before it

| Reading | 15-07-2026 | 16-07-2026 | **31-07-2026** | 31-07 vs 16-07 |
|---|---|---|---|---|
| warm-up | 29 743 ms | 53 290 ms | **131 737 ms** | ~2.5× **slower** |
| measured | 52 815 ms | 104 870 ms | **31 623 ms** | **~3.3× faster** |
| measured vs ceiling | 1.76× over | 3.50× over | **1.05× over** | near-miss |

The two axes have moved in **opposite** directions, and the summary "third NO-GO in a row" hides
that. The **measured** reading — the one the policy gates on — is the **best c4 has ever
recorded**, 3.3× better than 16-07 and better even than the 15-07 baseline, missing the ceiling
by **1 623 ms (5.4 %)**. The warm-up, meanwhile, is the worst on record. A warm-up that is 4.2×
the measured reading is not the "home route is uniformly slow" picture the earlier entries
describe; it looks like a cold-start/first-call cost that the measured call no longer pays.

**This does not license a GO,** and none is asserted: the policy reads the measured value against
a fixed ceiling, and 31 623 ≥ 30 000. A hand-asserted GO over a measured `HEALTH_NOGO` is a hard
error under this gate, not an override — that rule was exercised today, since the operator's
standing expectation was that c4 was healthy.

### What a human may want to decide

- **Is the 30 000 ms ceiling still the right number**, or was it set against the 15-07/16-07
  regime? A 5.4 % miss is inside the noise band of a single unrepeated reading. Re-deriving the
  ceiling is a human's call and must not be done by a session that wants a GO — that is exactly
  the "never weaken a guard to pass a gate" case.
- **Is the warm-up worth excluding from the policy?** It is currently a hard NO-GO input in its
  own right. If it is genuinely cold-start cost, it is measuring the *first* call rather than the
  workload.
- The foreign-route investigation ([H909](https://github.com/gasyoun/Uprava/blob/main/handoffs/H909-Opus_SanskritLexicography_h818-foreign-route-paired-probe-analysis_14.07.26.md),
  🟠 archived-deferred) gains a **second** piece of fresh evidence, and a more interesting one:
  the home route may already be viable for the measured call.

Raw telemetry appended to `src/pilot/output/h963_c4_gate0_probe_events.jsonl` (gitignored, per-run
series) under the `run_id` above.

_Auto-generated by Opus 5 (`claude-opus-5[1m]`), Claude Code, executing `/pwg-live-gate` Step 1 on
operator spend authorisation: one fresh dated D-K reading, no canary, no promotion, no store/TM
mutation, no reroll._

_Dr. Mārcis Gasūns_

---

## Fifth reading, 31-07-2026 15:03Z — NO-GO, and the first one that is NOT a c4 latency signal

`run_id h963-c4-single-profile-gate0-2026-07-16/2026-07-31T15:03:25Z-pid35360` · wall 300.8 s ·
model `claude-sonnet-5` · prompt 6 828 B (floor 5 000 B) · ceiling 65 000 ms · one attempt, no
reroll. Run under [H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md)
from a clean worktree off `origin/master` [`b514f233`](https://github.com/gasyoun/SanskritLexicography/commit/b514f233).

| Phase | elapsed | classification | output bytes | verdict input |
|---|---|---|---|---|
| warm-up | **300 544 ms** | `timeout` | **0 B** | errors still fail the gate — advisory applies to *latency* only |
| measured | — | — | — | never ran (`live_probe` fail-closed on the warm-up) |

**`gate_reason = HEALTH_NOGO` → verdict NO-GO.** Stopped there: no canary, no bounded window,
nothing beyond the single warm-up reservation. The call ledger finalised that reservation as
`cost_evaluable: false` with 0 input/output/cache tokens — the `UNEVALUABLE` state, not a zero.

### Why this NO-GO must not be filed next to the four before it

The previous four readings are all **c4 route latency**. This one is not, and the gate log cannot
tell them apart on its own: a machine-wide stall and a slow home route both surface here as
`timeout` / over-ceiling. Classifying it took a diagnostic ladder of tiny non-representative
calls — deliberately **far below** the 5 000 B floor, so no row below is or can be read as a
health reading:

| # | invocation | config dir | prompt | result |
|---|---|---|---|---|
| 1 | gate probe (`node cli-wrapper.cjs`) | c4 | 6 828 B | **TIMEOUT 300 544 ms**, 0 B |
| 2 | tiny ping, same argv shape | c4 | ~46 B | TIMEOUT 90 433 ms |
| 3 | tiny ping, same argv shape | `C:\Users\user\.claude` (control) | ~46 B | TIMEOUT 90 458 ms |
| 4 | tiny ping, **native `bin/claude.exe`** (no Node wrapper) | c4 | ~46 B | TIMEOUT 90 710 ms |
| 5 | `--version` (no API call) | c4 | — | rc 0, `2.1.220 (Claude Code)`, **11 314 ms** |
| 6 | bare `-p`, no other flags | c4 | ~44 B | TIMEOUT 60 328 ms |
| 7 | `-p --output-format json` | c4 | ~44 B | TIMEOUT 60 709 ms |
| 8 | + `--model claude-sonnet-5` | c4 | ~44 B | TIMEOUT 60 705 ms |
| 9 | + `--json-schema` | c4 | ~44 B | TIMEOUT 61 676 ms |
| 10 | full probe argv (+ `--permission-mode plan`) | c4 | ~44 B | TIMEOUT 63 321 ms |
| 11 | recovery ping, native exe, 120 s ceiling | c4 | ~46 B | TIMEOUT 120 211 ms |
| 12 | recovery ping, native exe, 150 s ceiling (+40 min) | c4 | ~46 B | TIMEOUT 150 444 ms |
| 13 | `--debug -p`, cwd `C:\Users\user` | c4 | ~8 B | started, printed the untrusted-workspace warning, then **silent for 75 s** |
| 14 | tiny ping, cwd = the **long-trusted** main tree `SanskritLexicography\RussianTranslation` | c4 | ~8 B | TIMEOUT 90 s (rc 124) |
| 15 | outbound TLS reachability, same host, same minute | — | — | `api.anthropic.com` **OK, TLS 748 ms** (TLSv1.3, 160.79.104.10); `api.github.com` OK 936 ms; `github.com`, `registry.npmjs.org`, `www.google.com` all OK |

Rows 6–10 rule out every flag the probe adds, including `--json-schema` (the historical H818
Windows suspect). Row 4 rules out the Node shim resolution in `headless_worker.claude_argv_prefix`
— the D-R defect the `/pwg-live-gate` skill warns about — because the native binary hangs
identically. Row 3 rules out anything c4-specific: a **different config directory hangs the same
way**. Row 5 proves the binary itself runs and the machine is not wedged, though 11.3 s for a
version string that makes no API call is itself a load signal. Rows 11–12, at +25 and +40 minutes,
show the condition persisting rather than blipping.

Rows 13–15 close off three tempting wrong answers. Row 14 rules out the **fresh-worktree trust
state**: a gate run's cwd is a directory created minutes earlier and never trusted, and row 13
shows the CLI does emit an untrusted-workspace warning — but the same call hangs identically from
a main tree trusted for months, so the trust dialog is not what blocks. Row 15 rules out **raw
network reachability**: `api.anthropic.com` completed a TLS 1.3 handshake in 748 ms from this host
in the same minute a `-p` call was hanging. Row 13 also locates the stall: the process *starts*,
reaches its own warning path, and only then goes silent — it is not failing to launch.

**Conclusion: the headless `claude -p` route was unresponsive on this host for the whole window,
and the fault is neither c4-specific, nor flag-specific, nor the Windows shim, nor cwd/trust, nor
raw connectivity. Nothing here measures c4's route health, and nothing here revises the 31-07
12:05Z / 13:33Z readings.**

### The most probable cause — self-contention, and it is a campaign-level constraint

A process census taken during the stall found **21 live `claude` processes** on this machine, the
oldest started **25-07-2026 14:27** (six days earlier) and several having accumulated 4 000–6 850
CPU-seconds:

| started | count | note |
|---|---|---|
| 25-07-2026 | 7 | oldest cohort; two at 2 329 s and 4 320 s CPU |
| 26-07-2026 | 3 | |
| 28-07 → 30-07 | 8 | six at 3 900–6 900 s CPU |
| 31-07-2026 | 3 | includes this session |

That is the ordinary reading of a headless call that never returns a byte while `--version` still
works and the API host is reachable: new `-p` invocations get no slot. Row 15 makes it the
**leading** hypothesis rather than one of two, since it removes "the network is down" from the
table — the CLI starts, warns, and then waits, with a healthy TLS path to `api.anthropic.com`
available to it.

It is still **not proven**. What this evidence establishes is *host/account-fleet-wide, not
c4-specific*; what it cannot separate is an account concurrency/quota wall from a CLI-internal
stall. Proving it needs one ping taken after the abandoned sessions are gone — a human's call,
since killing another session's process is destructive and outside this run.

One loose thread, recorded because it is cheap to re-check and easy to over-read: **`statsig.anthropic.com`
fails DNS resolution from this host** (`getaddrinfo` failure, 11 544 ms on the cold lookup, then
negative-cached), while `statsig.com`, `featureassets.org`, `console.anthropic.com`, `claude.ai`
and both Sentry hosts all resolve normally. The 11.5 s cold-miss is suspiciously close to the
11 314 ms that a no-API-call `--version` took. That may be nothing — a hostname that simply does
not exist would also fail — and **no causal claim is made here**; it is noted so the next session
does not spend the same twenty minutes rediscovering it.

The campaign-level point stands either way: **the gate does not measure c4 in isolation — it
measures c4 under whatever else this machine is running.** A bounded paid window would face the
same contention, so window scheduling and process hygiene are a throughput variable, not
housekeeping.

### What the next session should do first (60 s, not 300 s)

Before spending the 300-second representative call, fire **one tiny ping** at the native binary
(rows 4/11 above). If it times out, the route is down and the gate reading is guaranteed to be a
`timeout` NO-GO carrying no information about c4 — stop, and do not burn the reservation.

Backlog item for the probe itself, **not** implemented here on purpose: a cheap liveness
pre-flight inside `h963_c4_gate0_probe.py` would save that 300 s, but a *billed* pre-flight would
absorb the cold start and silently change what "warm-up" measures, breaking comparability with the
four historical readings. Any such change must keep the two-phase protocol's semantics intact —
e.g. classify post-hoc (`timeout` + 0 output bytes ⇒ report a `route_unresponsive` sub-reason)
rather than insert a call. It can only ever add a NO-GO path, never a GO one.

### Raw event row (preserved here because `src/pilot/output/` is gitignored)

```json
{"schema":"pwg.run_event.v1","ts":"2026-07-31T15:08:26.682Z","run_id":"h963-c4-single-profile-gate0-2026-07-16/2026-07-31T15:03:25Z-pid35360","account":"c4","stage":"probe","event":"probe_call","purpose":"warmup","elapsed_ms":300544,"model":"claude-sonnet-5","output_bytes":0,"classification":"timeout","policy":"production_v1","executor_lane":"claude-cli-headless/readiness-schema","schema_valid":false}
```

Each gate run writes its events log inside its own worktree, and that path is gitignored — so the
per-run series is **destroyed with the worktree** unless the row is copied into this document. The
31-07 12:05Z, 13:33Z and 15:03Z readings were each taken in a different worktree, which is why no
single events file holds them.

_Auto-generated by Opus 5 (`claude-opus-5[1m]`), Claude Code, executing `/pwg-live-gate` Step 1
under H2011 on standing operator spend authorisation: one fresh dated D-K reading plus
non-representative tooling diagnostics; no canary, no window, no promotion, no store/TM mutation,
no reroll of the gate call._

_Dr. Mārcis Gasūns_

---

## Sixth reading, 31-07-2026 18:58Z — the route came back, and c4 still fails. Here is where the time actually goes

The stall above cleared at ~18:56Z: a tiny native-binary ping returned `rc 0`. Under the resume
protocol that is the trigger to take a **fresh** representative reading, so one was taken
immediately — this time from the **main tree**, deliberately, so the row joins the eleven-row
historical series instead of dying in a worktree.

`run_id h963-c4-single-profile-gate0-2026-07-16/2026-07-31T18:58:24Z-pid32116` · wall 173.1 s ·
model `claude-sonnet-5` · prompt 6 828 B · ceiling 65 000 ms · one attempt, no reroll.

| Phase | elapsed | classification | output bytes | vs 65 000 ms ceiling |
|---|---|---|---|---|
| warm-up | **94 606 ms** | `success` | 1 380 B | advisory (latency only) |
| measured | **78 415 ms** | `success` | 1 400 B | ❌ **1.21× over** |

**`gate_reason = HEALTH_NOGO` → verdict NO-GO.** Both calls returned clean, well-formed
structured output, so unlike the 15:03Z reading this one **is** a real c4 latency measurement —
the second consecutive NO-GO of the session, which is H2011's stop condition. No canary, no
window.

### The decomposition that matters more than the verdict

The recovery ping taken ~2 minutes earlier returned a full CLI result envelope, and its own
numbers split the wall clock in a way the gate never reports:

| quantity | value | source |
|---|---|---|
| total wall clock, process spawn → exit | **70 987 ms** | the probe's own `time.monotonic()` |
| `duration_ms` (CLI-reported end-to-end) | 6 199 ms | result envelope |
| `duration_api_ms` (model time) | **4 028 ms** | result envelope |
| ⇒ startup/teardown outside the API call | **≈ 65 s** | difference |

So on this host, right now, **roughly 65 seconds of a headless call is local CLI startup, not the
route.** The 65 000 ms ceiling is therefore being spent almost entirely before a token moves. Two
consequences follow, and neither is about c4:

1. **Under this load, c4 cannot pass the gate no matter how healthy the route is.** The startup
   component alone is at the ceiling. A reading of 78 415 ms with a 4-second API call is not a
   slow model — it is a slow process launch measured by a gate that cannot see the difference.
2. **That upgrades the abandoned-process cleanup from housekeeping to the actual blocker.** The
   21-process census in the previous section stops being a hypothesis about "why the route hung"
   and becomes the leading explanation for why the *latency* readings are what they are.

**This is not a licence to raise the ceiling again.** The correct fix is to make the measurement
mean something — either reduce the startup cost, or gate on `duration_api_ms` (which the envelope
already carries) with the startup cost tracked as its own separate budget. Raising a ceiling to
clear an overhead the ceiling was never meant to measure is the exact "weaken a guard to pass a
gate" move this document has refused four times. Recording the decomposition is the honest step;
the policy choice is a human's.

### Economics captured (H2011's "instrument everything" mandate)

Two paid calls, both cost-evaluable — no `UNEVALUABLE` this time:

| field | value |
|---|---|
| calls | 2 (warm-up + measured), 0 unevaluable |
| `input_tokens` | 4 |
| `output_tokens` | 1 507 |
| `cache_read_tokens` | 64 237 |
| `cache_creation_tokens` | **90 485** |
| `observed_cost_usd` | **$0.5848** (≈ $0.29 per call) |

The striking row is `cache_creation_tokens`: a 6 828 B prompt drags **~90 k tokens** of CLI
scaffolding into cache creation per run. That is a fixed per-call overhead the per-card economics
must budget for, and it argues directly against the one-card-per-call lane H2011 mandates for the
first window — not against measuring per-card, but the ~$0.29 floor and ~65 s startup are paid
**per call**, so a one-card-per-call window pays them once per card. Worth pricing before the
window opens rather than discovering it in the invoice.

### Raw event rows

```json
{"ts":"2026-07-31T18:59:59.255Z","purpose":"warmup","elapsed_ms":94606,"classification":"success","output_bytes":1380,"model":"claude-sonnet-5","run_id":"h963-c4-single-profile-gate0-2026-07-16/2026-07-31T18:58:24Z-pid32116"}
{"ts":"2026-07-31T19:01:17.695Z","purpose":"measured","elapsed_ms":78415,"classification":"success","output_bytes":1400,"model":"claude-sonnet-5","run_id":"h963-c4-single-profile-gate0-2026-07-16/2026-07-31T18:58:24Z-pid32116"}
```

Taken in the main tree, so these two rows are appended to the **surviving** 11-row series in
`src/pilot/output/h963_c4_gate0_probe_events.jsonl` (13 rows) rather than to a disposable
worktree copy.

### The c4 series so far

| date | warm-up | measured | verdict |
|---|---|---|---|
| 15-07-2026 | 29 743 ms | 52 815 ms | NO-GO (ceiling 30 000) |
| 16-07-2026 | 53 290 ms | 104 870 ms | NO-GO |
| 31-07 12:05Z | 131 737 ms | 31 623 ms | NO-GO (5.4 % miss) |
| 31-07 13:33Z | 49 456 ms | 37 501 ms | **PASS** (ceiling raised to 65 000) |
| 31-07 15:03Z | timeout, 0 B | — | NO-GO — host stall, not a c4 reading |
| **31-07 18:58Z** | **94 606 ms** | **78 415 ms** | **NO-GO**, 1.21× over |

_Auto-generated by Opus 5 (`claude-opus-5[1m]`), Claude Code, executing `/pwg-live-gate` Step 1
under H2011: second consecutive NO-GO, which is the handoff's stop condition. No canary, no
window, no promotion, no store/TM mutation, no reroll._

_Dr. Mārcis Gasūns_

---

## ROOT CAUSE, 31-07-2026 ~20:45Z — c4 is RATE-LIMITED, not slow. The latency series is contaminated

An authenticated request issued **outside the CLI**, using the profile's own OAuth token, ends
the investigation in two calls:

| probe | result |
|---|---|
| authenticated, deliberately invalid body | **HTTP 400 in 892 ms** — `messages: Field required` |
| authenticated, real 1-token completion | **HTTP 429 in 1 103 ms** — `rate_limit_error` |
| repeat, capturing headers | **HTTP 429 in 754 ms**; tier `default_claude_max_20x` |

The 400 proves the token, the scopes, the tunnel and the authenticated path are all healthy. The
429 is the whole answer: **the API rejects the account's inference immediately, in under a
second.** The CLI evidently retries with backoff instead of surfacing that, so `claude -p`
*appears* to hang for 120–300 s while the underlying condition is an instant refusal. No
rate-limit reset headers are exposed on this 429 (only `request-id`), so the reopening time
cannot be read off the response.

### What this retracts

**The "≈65 s of a headless call is CLI startup" conclusion in the sixth reading is WRONG, and it
is withdrawn here.** It was inferred from one envelope (70 987 ms wall vs `duration_api_ms`
4 028 ms) on the assumption that the gap was process launch. It was not: `--version` returns in
**1 071 ms**, `auth status` in **1 106 ms**, and an authenticated API call in **under 1.1 s**.
There is no 65 seconds of startup on this host. **The gap is the CLI silently retrying
rate-limited attempts until one gets through.**

Everything else follows, and the corrections are worth more than the original readings:

- **The 78 415 ms "measured latency" of the sixth reading is mostly backoff, not model time.** It
  is not a measurement of c4's route.
- **The whole latency series may be contaminated.** Any reading taken while the account was
  rate-limited measured retry delay, not route health — which puts the 15-07 (52 815 ms), 16-07
  (104 870 ms) and 31-07 (78 415 ms) figures in doubt as *route* evidence, and means the ceiling
  policy has been calibrated partly against backoff.
- **The intermittency is explained.** 18:56Z succeeded and 15:03Z / 19:45Z did not, because
  whether the retry loop lands in a window with capacity is a matter of timing, not of the host.
- **Three earlier hypotheses are formally dead:** host self-contention (already refuted by the
  kill test), the VPN path (Amnezia carries a 512 KB POST in 383 ms), and CLI startup cost.
- The historical `rate_limit` rows in the events log (24-07, 25-07) show the probe *can* classify
  this correctly — so the failure mode is specifically the CLI **hanging** on 429 rather than
  returning it.

### What this means for the campaign

**c4's gate cannot be read as a health signal while the account is rate-limited, and the fix is
scheduling, not engineering.** Concretely, for whoever resumes:

1. **Probe with the authenticated one-liner first** (400/429 in ~1 s) instead of the 300 s
   representative call. A 429 means stop; there is nothing to measure.
2. **Do not raise the ceiling** — it was already raised 30 000 → 65 000 on 31-07 partly against
   what is now known to be backoff time. Re-deriving it needs readings taken when the account is
   demonstrably *not* rate-limited.
3. **The one-card-per-call lane H2011 mandates is the worst possible shape under a rate limit** —
   it maximises call count for a fixed body of work. That trade was made for per-card
   attribution and should be re-examined against the quota now that the quota is the binding
   constraint.
4. Consider whether the campaign should run on a profile whose quota is not shared with
   interactive sessions on the same box.

_Auto-generated by Opus 5 (`claude-opus-5[1m]`), Claude Code, under H2011. Credential discipline:
the OAuth token was read from the profile store and used as a request header only — never
printed, logged or written. Only key names, lengths and expiry were reported. Two authenticated
calls were made; one billed a 4-token completion attempt that the API refused._

_Dr. Mārcis Gasūns_

---

## Eighth reading, 02-08-2026 05:46Z — **PASS**, and the canary passed too: the gate is `LIVE_GO`

The first reading in this whole series that clears both halves of the gate. Taken under
[H2011](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2011-Opus_RussianTranslation_c4-gate-ceiling-decision-and-live-optimisation_31.07.26.md)
from a clean worktree off `origin/master`
[`64a4fa62`](https://github.com/gasyoun/SanskritLexicography/commit/64a4fa62), run id
`h963-c4-single-profile-gate0-2026-07-16/2026-08-02T05:46:22Z-pid25748`.

| purpose | wall `elapsed_ms` | `duration_api_ms` | `api_gap_ms` | ceiling | class | schema |
|---|---|---|---|---|---|---|
| warm-up | 55 390 | 37 690 | 17 700 | 65 000 | success | valid |
| **measured** | **43 815** | **26 386** | **17 429** | 65 000 | success | valid |

**GATE-0 VERDICT: PASS** — the measured reading is 1.48× under the ceiling. Wall clock for the
whole two-call probe: 99.3 s. Payload 6 828 B (floor 5 000 B), model `claude-sonnet-5`, profile
`c4`, argv resolved to `[node.exe, cli-wrapper.cjs]` (no bare-`claude` D-R fallback).

### What the three decomposed readings now show together

| date | warm-up wall | measured wall | measured `api_ms` | measured `api_gap_ms` | verdict |
|---|---|---|---|---|---|
| 01-08 20:20Z | 39 437 | 50 336 | 27 557 | 22 779 | PASS |
| **02-08 05:46Z** | **55 390** | **43 815** | **26 386** | **17 429** | **PASS** |

Two things follow, and neither was readable before the H2095 instrumentation:

1. **The route is steady.** `duration_api_ms` on the measured call moved 27 557 → 26 386 ms
   (−4 %) across ~9 hours. The wall-clock swing (50 336 → 43 815) is almost entirely the gap.
2. **The gap is a fixed tax, not noise.** 22 779 → 17 429 ms, and the warm-up's gap is 17 700 ms
   in the same run — i.e. the non-API overhead is ~17–23 s whether the call is first or second.
   That is the same quantity [PR #994](https://github.com/gasyoun/SanskritLexicography/pull/994)
   isolated as an unstable cache prefix being re-written per invocation, seen here from the
   latency side rather than the token side.

**What this does NOT settle:** the ceiling itself. 65 000 ms was calibrated partly against
backoff ([FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)) and
[issue #946](https://github.com/gasyoun/SanskritLexicography/issues/946) still wants ≥5 paired
readings before re-deriving it. This reading is the second uncontaminated point, not a
re-derivation, and no constant was moved.

### Step 2 — the canary, and why this is the first true `LIVE_GO`

One separate paid call on `dq_canary_puregloss~~h0_zz_pw` through the headless CLI on
manifest v2: **121 693 ms, `success`, 3/3 senses, 0 null**, and
[`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)
returned 1/1 clean with the SAN-LOSS sense-count guard, the sense-dupe gate, `ru_style` and
coverage all PASS. Cost `$0.8660853`, `cost_evaluable: true`. Full economics, the exact cost
decomposition and the soft `markup_wrapper_dropped` advisory are in
[`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

`gate_reason = LIVE_GO`, `verdict = GO`, derived from the two measured results by the named
policy — never asserted.

### Raw event rows (preserved here because `src/pilot/output/` is gitignored)

```json
{"ts":"2026-08-02T05:47:17.844Z","purpose":"warmup","elapsed_ms":55390,"classification":"success","output_bytes":1382,"duration_api_ms":37690,"api_gap_ms":17700,"latency_ceiling_ms":65000,"schema_valid":true,"policy":"production_v2","run_id":"h963-c4-single-profile-gate0-2026-07-16/2026-08-02T05:46:22Z-pid25748"}
{"ts":"2026-08-02T05:48:01.692Z","purpose":"measured","elapsed_ms":43815,"classification":"success","output_bytes":1382,"duration_api_ms":26386,"api_gap_ms":17429,"latency_ceiling_ms":65000,"schema_valid":true,"policy":"production_v2","run_id":"h963-c4-single-profile-gate0-2026-07-16/2026-08-02T05:46:22Z-pid25748"}
```

### The c4 series, updated

| date | warm-up | measured | verdict |
|---|---|---|---|
| 15-07-2026 | 29 743 ms | 52 815 ms | NO-GO (ceiling 30 000) |
| 16-07-2026 | 53 290 ms | 104 870 ms | NO-GO |
| 31-07 12:05Z | 131 737 ms | 31 623 ms | NO-GO (5.4 % miss) |
| 31-07 13:33Z | 49 456 ms | 37 501 ms | PASS (ceiling raised to 65 000) |
| 31-07 15:03Z | timeout, 0 B | — | NO-GO — host stall, not a c4 reading |
| 31-07 18:58Z | 94 606 ms | 78 415 ms | NO-GO, 1.21× over |
| 01-08 20:20Z | 39 437 ms | 50 336 ms | PASS (first decomposed) |
| **02-08 05:46Z** | **55 390 ms** | **43 815 ms** | **PASS + canary PASS ⇒ `LIVE_GO`** |

_Auto-generated by Opus 5 1M (`claude-opus-5[1m]`), Claude Code, executing `/pwg-live-gate`
Steps 1–3 under H2011. Three paid calls (2 gate + 1 canary). No production window, no promotion —
the canary is `synthetic_control` and must never reach the store — no store or TM mutation, no
constant moved, no reroll._

_Dr. Mārcis Gasūns_
