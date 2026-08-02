# Doc-vs-code drift audit — the daily "what's actually true today" routine

_Created: 02-08-2026 · Last updated: 02-08-2026_

The spec for a scheduled agent that files **at most one** GitHub issue per day recording a
place where this repo's **documentation asserts something the code does not do**.

Commissioned by MG on 02-08-2026 after [H2160](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2160-Opus_RussianTranslation_whole-card-b0-hang-and-medium50-completion_02.08.26.md)
found one such drift by accident and it turned out to have decided a real spend decision.
This file is the durable copy: the routine's prompt is a transcription of the sections below,
so **edit here first**, then update the routine.

## The seed case — the bar, stated as an example

The `/pwg-live-gate` skill instructed operators to *"Gate on `duration_api_ms`"*.

The code never did. [`probe_log.verdict_for()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py)
takes a **generic** `latency_ms`, and its only caller —
[`h963_c4_gate0_probe.derive_fails`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py) —
supplies `elapsed_ms`, the wall clock. **No code had ever gated on `duration_api_ms`.**

What makes it a finding rather than a nitpick: on 02-08-2026 the two numbers **disagreed on a
real verdict** — wall 75 586 ms (NO-GO) against `duration_api_ms` 29 069 ms (comfortable PASS) —
and that verdict decided whether a paid window ran. Ruled by MG the same day: the gate is wall,
the prose was wrong, and the drift had been live long enough to be quoted back as policy.

Two structural lessons the routine exists to exploit:

- **The recommendation-becomes-policy path.** The `duration_api_ms` idea entered as a *proposal*
  ([H963:488](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md),
  restated at [H2152 §212](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md)),
  was copied into a skill as an *instruction*, and no one implemented it. Look for that shape.
- **The repo often already knows.** [H2056](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md)
  had already written *"That recommendation is documentation only — no code implements it."*
  A finding the memos already record is **not** a new finding.

## The bar — all four, or it is not a finding

1. **A specific documented claim**, quoted with `file:line`. Prose lives in `*.md` across
   `RussianTranslation/**` (especially `pwg_ru/**`,
   [`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md),
   `AGENTS.md`, `PIPELINE_HISTORY.md`, `REPRODUCIBILITY.md`, `LANG_PARITY.md`) **and** in the long
   explanatory comments and docstrings inside `src/pilot/*.py`, which carry as much load-bearing
   prose as the docs do.
2. **The code contradicting it**, quoted with `file:line`. Follow the real call path; never infer
   behaviour from a function name. The seed case is exactly a function whose name
   (`verdict_for(latency_ms, …)`) says nothing about which latency arrives.
3. **A consequence** — the concrete wrong action a reader takes because of the drift: spend money,
   weaken a guard, mis-read a gate, trust a stale number, skip a real check. **No consequence
   means trivia; discard it.**
4. **Not already known.** Search open **and** closed issues, then grep `RESULTS_LOG.md`,
   `PIPELINE_HISTORY.md`, `FINDINGS.md` and `pwg_ru/h*/`.

## Hard rules

- **At most ONE issue per run.** Highest-consequence finding only; runners-up get a single line
  inside that same issue, never their own.
- **If nothing clears the bar, file NOTHING.** An empty day is a correct and expected outcome, and
  is strongly preferred to a weak issue. A daily quota is precisely the pressure that manufactures
  findings — this rule is what keeps the routine from degrading into noise, and it is the rule
  most likely to be quietly eroded. If you would not bet the finding survives a skeptical
  reviewer, drop it.
- **Read-only on the repo.** No edits, no PRs, no pushes. The only write is the issue.
- **Verify before filing.** Open the files; confirm both quotes are real and current at `master`.
  A fabricated or stale `file:line` is worse than filing nothing.
- **Never spend money.** No `claude -p`, no probes, no `headless_worker.py`, no bounded runs.
  Static audit only — the routine reads code, it does not exercise the paid lane.

## Issue format

Title: `[drift] <short claim> — docs say X, code does Y`

Body: the documented claim (quote + link) · what the code actually does (quote + link) ·
consequence · suggested resolution (usually *correct the prose* or *implement the claim* — say
which and why, but do **not** do it) · confidence, with what would refute it. Footer:
`Filed by the daily doc-vs-code drift audit (scheduled routine). Model: <exact model id>. Seed case: H2160.`

Full `https://github.com/gasyoun/SanskritLexicography/blob/master/<path>#L<n>` URLs — relative
links do not render in issue bodies.

## Schedule

`0 17 * * *` UTC = **20:00 Europe/Moscow**, daily. Cloud routine (isolated sandbox, own checkout),
model Sonnet 5 (`claude-sonnet-5`), repo `gasyoun/SanskritLexicography`, tools Bash / Read / Write /
Edit / Glob / Grep.

⚠️ Creating the routine requires a **connected GitHub account** on claude.ai — the create call
returns `HTTP 401 "Connect your GitHub account before saving a routine that uses a GitHub
repository"` otherwise. That was the open blocker when this file was written.

## Known limitations

- **Sonnet-tier judgment on a judgment task.** The bar's fourth clause (is this already known?) and
  the consequence test both need real reading. Escalate the model if empty days and weak issues
  both become common — those are the two failure directions.
- **Scope is `RussianTranslation/`**, not the whole repo or the org. The same drift class certainly
  exists in sibling repos; widening scope is a deliberate future change, not an oversight.
- **It finds drift, not correctness.** A doc and its code agreeing while both are wrong is
  invisible to this routine.

_Dr. Mārcis Gasūns_
