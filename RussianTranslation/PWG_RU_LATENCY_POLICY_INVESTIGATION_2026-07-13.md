# pwg_ru live-acceptance latency-policy investigation (opened after the second consecutive NO-GO)

_Created: 13-07-2026 · Last updated: 13-07-2026_

Opened per the H818 acceptance STOP-branch directive and handoff
[H895](https://github.com/gasyoun/Uprava/blob/main/handoffs/H895-Opus_SanskritLexicography_h818-acceptance-DE-DK-latency-blocked_13.07.26.md):
_"If it remains > 30 s, stop again and open a separate evidence-based latency-policy
investigation — do NOT weaken the 30 s threshold."_ Executor of the triggering run:
Opus 4.8 (`claude-opus-4-8[1m]`) driving `max_account_orchestrator staged-run`.
Generation model under test: `claude-sonnet-5`. Single Max account `max1`
(`D:\ClaudeTools\profiles\claude1\.claude`).

## Trigger — H895 run1: second consecutive measured-probe NO-GO

The integrated warm-up+measured two-phase probe (D-K) was run **exactly once**, with no
manual preliminary probes, from a clean `origin/master` worktree
(`SanskritLexicography-h895`, HEAD `529baf89`). The measured reading again exceeded the
30 000 ms health ceiling, so the run STOPped at the probe **before any job was imported or
claimed** — `arvant` never ran, the canonical store is unchanged at **11,579** rows, the
jobs table is empty.

| Field | Value |
|---|---|
| run_id | `h895-run1-arvant` |
| warm-up probe | **41 159 ms**, `success`, `claude-sonnet-5`, output 1 478 B |
| measured probe (gated) | **40 339 ms**, `success`, `claude-sonnet-5`, output 1 502 B |
| ceiling | 30 000 ms → **honest NO-GO** (no retry, no re-warm) |
| job claimed | none (probe gated before import) |
| canonical store | 11,579 (unchanged) |
| A-vs-B (`arvant` D-J vs content-specific) | still **UNRESOLVED** — `arvant` never generated |
| events | `src/pilot/output/h895_accept/run_events.jsonl` (gitignored, local) |

## Evidence across runs — the ceiling breach is stable, not transient warm-up flap

| Run | when (UTC) | warm-up ms | measured ms (gated) | verdict |
|---|---|---|---|---|
| run5 (H818 rerun) | ~2026-07-13 22:5x (prior session) | 24 773 | **40 925** | NO-GO |
| run1 (H895, this session) | 2026-07-13 21:31–21:32 | **41 159** | **40 339** | NO-GO |

Two independent measured readings ~40 s apart on the same profile, both classified
`success` (auth, exact model, and result-envelope all valid) — this is a **pure latency**
condition, not an auth / quota-park / content / invocation failure. All seven D-E…D-K
invocation and telemetry defects remain fixed; nothing in the pipeline regressed.

## Two observations that sharpen the cause

1. **Warm-up did not help — the ~40 s is steady-state, not cold-start.** In run1 the
   warm-up (41 159 ms) and the measured call (40 339 ms) are within ~2 % of each other.
   The D-K warm-up exists precisely to absorb cold-connection cost; here it absorbed
   nothing. A cold-start explanation is therefore **not supported** for run1 — the
   degraded latency is sustained across back-to-back calls.
2. **Latency appears to scale with payload/generation size (hypothesis, not isolated).**
   The `init` account-validation step in the same session — whose live call is a tiny
   `-p 'Return exactly OK.'` on the exact model — completed inside `init`'s ~7 s total
   wall (including the local `auth status` check), whereas every ≥5 KB-payload probe
   takes ~40 s. This is **consistent with** latency scaling with input/output size rather
   than a flat per-request penalty, but it was **not measured under controlled conditions**
   (different prompts, different output caps). It is a lead for the method below, not a
   conclusion.

"Transient throttling" and "degraded Russia→Anthropic generation path" (the H818
load-bearing hypothesis, see [H818](https://github.com/gasyoun/Uprava/blob/main/handoffs/H818-Codex_RussianTranslation_pwg-ru-full-pipeline-audit-4account-max-orchestration_12.07.26.md))
remain **inferences consistent with the observations, not proven causes**.

## Method — how to settle it (next live session, when quota is healthy enough to probe)

Do these as an explicit diagnostic pass (this is now sanctioned — the acceptance gate has
already honestly NO-GO'd; further probing is investigation, not gate re-rolling):

1. **Payload-size sweep.** Time exact-model calls at a controlled ladder of input sizes
   (~90 B minimal → ~1 KB → ~2.5 KB → ~5 KB → ~6.5 KB) with a fixed small output cap,
   ≥3 samples each, one after another. Plot latency vs input bytes. A linear/​superlinear
   climb confirms size-dependence; a flat ~40 s floor points at a per-request network/route
   penalty instead.
2. **Route comparison.** Repeat the 6.5 KB probe from a non-Russia egress (VPN or the
   foreign server the H818 4-account orchestration provisions). If the foreign route lands
   ≤ 30 s on the same payload, the degraded-path hypothesis is confirmed and the policy
   answer is the H818 foreign-server orchestration, not a threshold change.
3. **Time-of-day / recovery curve.** Re-probe at intervals to see whether the ceiling
   breach is diurnal (throttling window) or persistent.

## Policy (standing, do NOT weaken)

- **The 30 000 ms ceiling stays.** It gates *usable* generation performance for a
  batch-scale translation run; a ~40 s/call floor makes any real drain economically and
  operationally unviable, and lowering the bar to force a GO would ship a pipeline that
  cannot actually translate at scale. This is exactly the outcome H818 was opened to fix.
- **The fix is the route, not the threshold** — the H818 4-account foreign-server Max
  orchestration (`CLAUDE_CONFIG_DIR` per account, queue, rate-limit parking) is the
  designed remedy for a degraded home-egress generation path. It has a **human
  prerequisite** (foreign server + account logins; the agent never performs `/login`).
- **`arvant` A-vs-B stays open** until a measured ≤ 30 s reading lets the single bounded
  `arvant` retry actually run — D-J (Windows process-tree kill) is fixed, but whether a
  content-specific non-termination also exists is untestable while the probe gates first.

## Reproduce this run

```
# clean worktree off origin/master, then, from RussianTranslation/:
python src/pilot/no_pwg_scale_plan.py --window-size 1 --headwords 1 --headless \
  --dry-run --limit-windows 1 --prefix h895_run1_w --start-index 1 \
  --coordinator-dir src/pilot/output/h895_accept/coordinator_dry \
  --manifest src/pilot/output/h895_accept/plan_dry.json
python src/pilot/max_account_orchestrator.py --db src/pilot/output/h895_accept/max.sqlite \
  init --account "max1=D:/ClaudeTools/profiles/claude1/.claude" \
  --claude-bin "C:/Users/user/AppData/Roaming/npm/claude"
python src/pilot/max_account_orchestrator.py --db src/pilot/output/h895_accept/max.sqlite \
  staged-run --coord-dir src/pilot/output/h895_accept/coordinator_dry \
  --cwd <worktree>/RussianTranslation --coordinator src/pilot/coordinator.py \
  --plan src/pilot/output/h895_accept/plan_dry.json --stop-after 1 --timeout 480 \
  --report src/pilot/output/h895_accept/readiness.json \
  --events src/pilot/output/h895_accept/run_events.jsonl \
  --census src/pilot/output/h895_accept/bug_census.json \
  --claude-bin "C:/Users/user/AppData/Roaming/npm/claude" --run-id h895-run1-arvant
```

Gotcha worth keeping: `--claude-bin` **must** be the full path to the npm `claude` shim
(`C:/Users/user/AppData/Roaming/npm/claude`), not the bare name — `claude_argv_prefix`
resolves the `node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs` entry relative to the
shim's own directory, so a bare `claude` abspath's to the CWD and dies with `[WinError 2]`
before the D-A rewrite can help.

_Dr. Mārcis Gasūns_
