# H963 — single-profile c4 Gate-0 health attempt (fresh dated D-K reading)

_Created: 16-07-2026 · Last updated: 16-07-2026_

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
