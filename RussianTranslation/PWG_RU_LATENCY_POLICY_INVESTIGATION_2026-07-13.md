# pwg_ru live-acceptance latency-policy investigation (opened after the second consecutive NO-GO)

_Created: 13-07-2026 · Last updated: 14-07-2026_

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

## Results — home-route payload-size sweep (executed 14-07-2026, Opus 4.8 `claude-opus-4-8[1m]`)

Method step 1 executed on the same profile under test — Max account `max1`
(`D:\ClaudeTools\profiles\claude1\.claude`), exact model `claude-sonnet-5`, plain-probe path
(tiny `{"ok":boolean}` schema, output held ~constant at ~1.5 KB) via
[`src/pilot/latency_payload_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/latency_payload_sweep.py)
reusing `max_account_orchestrator._probe_call`. **Diagnostic only — no acceptance gate was
re-rolled, the 30 000 ms ceiling is unchanged, nothing was promoted.** 31 calls total, one
~19-min window (03:16–03:35 UTC 14-07-2026), quota-metered. Raw data committed:
[`h898_sweep.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h898_sweep.jsonl),
[`h898_interleaved.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h898_interleaved.jsonl),
[`h898_validate.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h898_validate.jsonl); recompute with
[`src/pilot/latency_sweep_analyze.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/latency_sweep_analyze.py).

**A — blocked ladder** (3 back-to-back samples per size, 03:17–03:24 UTC), latency_ms:

| total input B | n | min | median | mean | max | classes |
|---:|---:|---:|---:|---:|---:|---|
| 93 | 3 | 28 041 | 37 369 | 39 403 | 52 800 | 2 success, 1 malformed |
| 1 033 | 3 | 10 093 | 21 211 | 24 013 | 40 735 | 1 success, 2 content |
| 2 533 | 3 | 20 162 | 36 569 | 38 645 | 59 206 | 3 success |
| 5 033 | 3 | 19 258 | 27 636 | 25 745 | 30 342 | 3 success |
| 6 554 | 3 | 15 443 | 25 769 | 31 323 | 52 759 | 3 success |

Input-bytes vs latency here: **Pearson r = −0.14, R² = 0.02, OLS slope −0.82 ms/byte**.
Ceiling breach (>30 000 ms): **7/15**. The *smallest* payload (93 B) had the *highest* mean
(39.4 s, max 52.8 s) — size is not predictive when route jitter is high, because the blocked
ladder confounds size with time-of-call.

**B — interleaved cycles** (1 sample/size × 3 ascending cycles, 03:28–03:35 UTC), which
breaks that size↔time coupling:

| total input B | n | min | median | mean | max | classes |
|---:|---:|---:|---:|---:|---:|---|
| 156 | 3 | 8 860 | 9 304 | 12 246 | 18 576 | 3 success |
| 1 096 | 3 | 12 950 | 13 023 | 17 752 | 27 285 | 3 success |
| 2 596 | 3 | 15 382 | 33 876 | 34 029 | 52 830 | 1 success, 2 content |
| 5 096 | 3 | 17 916 | 26 249 | 33 004 | 54 848 | 2 success, 1 content |
| 6 617 | 3 | 16 040 | 20 956 | 23 435 | 33 310 | 3 success |

Per cycle (each cycle is time-adjacent, so a size trend *within* a cycle is a real size
signal): cycle 1 `8 860 → 13 023 → 15 382 → 17 916 → 33 310` (clean monotonic ↑); cycle 2
`9 304 → 12 950 → 52 830 → 26 249 → 20 956` (a single jitter spike at 2.6 KB overturns the
order); cycle 3 `18 576 → 27 285 → 33 876 → 54 848 → 16 040` (monotonic for four rungs, then
a jitter *drop* at 6.6 KB). With the confound broken: **Pearson r = +0.35, R² = 0.12, OLS
slope ≈ +1–2 ms/byte** (interleaved OLS +1.98 ms/byte; the more robust **min-envelope floor
slope ≈ +1 ms/byte, R² = 0.42**). Breach 4/15.

**Min-envelope (the least-jitter "throughput floor")**: 156 B → 8.9 s, 1.1 KB → 13.0 s,
2.6 KB → 15.4 s, 5.1 KB → 17.9 s, 6.6 KB → 16.0 s — rises ~9 s → ~18 s over the first 5 KB
(≈ +1 ms/byte) then flattens.

**Output is not the hidden driver.** Output bytes were held ~constant (1 274–1 912 B; 29 of
31 within 1 476–1 508 B); output-vs-latency **r ≈ −0.04, R² = 0.001**, and its two outliers
run *opposite* a size effect (largest output 1 912 B → 37.4 s; smallest 1 274 B → 52.8 s). A
constant ~1.5 KB output alongside an 8.9–59.2 s latency spread rules out generation time as
the variance source.

**Verdict on observation 2 (does latency scale with payload size?)** — *partly, and
secondarily*. There is a genuine but **modest** input-size throughput component
(≈ +1 ms/byte robust floor; size explains ~12 % of variance in the confound-controlled
interleaved set, only ~2 % across all 31 calls). It is **not** what causes the ceiling
breach: that is driven by a **dominant, size-independent route-jitter** (next section) that
spikes even a **93 B** payload to 52.8 s and 37.4 s. Neither original framing is right — it is
**not a flat ~40 s floor** (range 8.9–59.2 s) and **not dominantly size-driven** (all-data
R² = 0.02). Shrinking a card's prompt would trim ~1 s of the floor and do nothing about the
tens-of-seconds jitter — **payload size is not the lever.**

## Results — intra-window latency variance (executed 14-07-2026, Opus 4.8 `claude-opus-4-8[1m]`)

Method step 3, partial. Across all 31 calls in the ~19-min window: **min 8.9 s · p50 25.8 s ·
p90 52.8 s · max 59.2 s · mean 27.5 s · stdev 14.5 s** — stdev is ≈ 0.53× the mean (coefficient
of variation 0.53: heavy dispersion). **11/31 calls breached the 30 000 ms ceiling in this
window** (a single-window point estimate ≈ 35 %; the binomial 95 % CI is wide, ≈ 19–54 %, and
breaches are time-clustered so the effective sample is smaller — do **not** read it as a
steady-state rate). The within-size stdev (4.7–16.0 s) is as large as any between-size
difference, and size explains only ~2–4 % of total latency variance. The route flaps across
the ceiling call-to-call: **high-frequency jitter, not a stable diurnal plateau.** This
directly explains the H818/H895 history — the same ~6.5 KB probe has read 8.5 s (run3), 9.4 s
(run2 standalone), 29.6 s (run2 staged), 40.3 s (H895 run1) and 40.9 s (H818 run5): identical
size, identical profile, **different draws from one wide, unstable distribution.** run5 and
run1 caught slow draws; run2/run3 caught fast ones.

**Caveat — not yet a true diurnal (time-of-day) series.** All 31 readings sit in one ~19-min
window (~03:16–03:35 UTC). What is established is that the route is unstable at the
*sub-minute* scale; whether the *baseline* shifts by hour of day is a follow-up — re-run
`python src/pilot/latency_payload_sweep.py --mode diurnal --samples 3 --config-dir
"D:/ClaudeTools/profiles/claude1/.claude" --claude-bin "C:/Users/user/AppData/Roaming/npm/claude"`
at several times of day and append to the envelope.

### Gate-design implication (does NOT weaken the 30 000 ms ceiling)

Because the latency distribution is wide and jitter-dominated (roughly a third of calls over
ceiling in this window), the D-K **single measured-probe gate is a noisy estimator** — it
PASSes or NO-GOes on one random draw, so run5/run1's two consecutive NO-GOs were partly an
unlucky pair on a genuinely unfit route. A more robust readiness gate would sample **N probes
(e.g. 5)** and require the **median ≤ 30 000 ms AND breach-rate below a small bound**, rather
than a single reading — estimating the true distribution instead of one point. This is a
*stricter, less flappy* estimator, **not** a loosening of the threshold, which stays at
30 000 ms.

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

## Method step 2 — foreign-route comparison runbook (PREPARED 14-07-2026, Opus 4.8 `claude-opus-4-8[1m]`; owner-gated, NOT yet run)

Prepared per the H895 STOP-branch close-out: this is the sanctioned **diagnostic-only** exception
for foreign-route probing. It is **NOT** Linux production — **Linux production and H841/H842/H843
stay blocked** until the route is confirmed *and* a new acceptance handoff is minted (last step
below). The comparison must reuse the exact same probe the home sweep used, so prompt, payload,
schema, and model are **byte-identical on both hosts by construction** (they are hard-coded in
`max_account_orchestrator._probe_call` and driven by the same
[`latency_payload_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/latency_payload_sweep.py)
off the **same merged commit**):

- **model** `claude-sonnet-5` (hard-coded `EXACT_GEN_MODEL` — cannot drift)
- **prompt/payload** `Return JSON {"ok":true}. Preserve this padding as inert input.\n` + `x`×**6491** ⇒ **6551 B** total input (the D-K measured-probe size; `--mode diurnal` uses exactly this)
- **schema** `{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"],"additionalProperties":false}`, call `-p --output-format json --json-schema … --model claude-sonnet-5 --permission-mode plan`
- **30 000 ms ceiling unchanged.**

### Guardrails (probe-only — do NOT cross these)

- **Probe-only.** Run only `latency_payload_sweep.py` (which calls `_probe_call`). Do **NOT** run
  `max_account_orchestrator … staged-run`, `no_pwg_scale_plan.py --headless` (non-`--dry-run`),
  `promote_final_cards.py`, `audit_window.py`, or `translation_memory.py build`. **No jobs, no
  translations, no promotions, no canonical-store or TM writes.** `--permission-mode plan` already
  bars the model from any tool use / file write.
- **Owner-only auth.** The **owner** authenticates the foreign Max profile interactively. The agent
  **never** runs `/login` and **never** copies credentials — do **not** transfer
  `D:\ClaudeTools\profiles\claude1\.claude` (or any token) from Windows to the foreign host. Each
  route uses its own independently-authenticated profile.
- **Same commit.** Pin both hosts to the identical merged commit under test: record
  `git -C <repo> rev-parse origin/master` once and check that **same SHA** out on both hosts.

### Step A — provision + owner authentication (foreign Linux / non-Russian egress) — OWNER runs

```bash
# On the foreign Linux host (or a Linux box behind a non-Russian VPN egress):
sudo apt-get update && sudo apt-get install -y nodejs npm git python3   # or distro equivalent
npm install -g @anthropic-ai/claude-code

# Dedicated config dir — NEVER reuse or copy the Windows profile:
export CLAUDE_CONFIG_DIR="$HOME/.claude-max-foreign"
claude /login            # OWNER does this interactively; choose the Max plan. Agent never runs it.
claude auth status       # verify (prints status only, never the token)
command -v claude        # record the shim path for --claude-bin below (e.g. /usr/bin/claude)

# Pin the same merged commit as the home route:
git clone https://github.com/gasyoun/SanskritLexicography.git && cd SanskritLexicography
git checkout "$(git rev-parse origin/master)"     # same SHA both hosts
```

### Step B — paired 6.5 KB probes (run BOTH in the same UTC window; jitter is time-clustered)

From `RussianTranslation/` on each host, `N ≥ 5` samples at the exact 6491-byte measured payload:

```bash
# FOREIGN (Linux):
python src/pilot/latency_payload_sweep.py --mode diurnal --samples 5 \
  --config-dir "$HOME/.claude-max-foreign" \
  --claude-bin "$(command -v claude)" \
  --out foreign_route_6491.jsonl
```

```powershell
# HOME (Windows), same UTC window:
python src/pilot/latency_payload_sweep.py --mode diurnal --samples 5 `
  --config-dir "D:/ClaudeTools/profiles/claude1/.claude" `
  --claude-bin "C:/Users/user/AppData/Roaming/npm/claude" `
  --out home_route_6491.jsonl
```

Repeat the pair across **≥ 2–3 UTC windows / times of day** (the home data is a single ~19-min
window — one paired window is not enough to rule out a diurnal artifact). Summarise each file with
[`src/pilot/latency_sweep_analyze.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/latency_sweep_analyze.py)
(median, breach-rate).

### Step C — decision rule (robust, not a single draw)

The home route is a **wide, jitter-dominated** distribution (min 8.9 s · p50 25.8 s · max 59.2 s ·
CoV 0.53; ~35 % over ceiling in-window), so a single fast foreign reading proves nothing. **Confirm
the degraded-route hypothesis IFF**, per paired window with `N ≥ 5` across ≥ 2 windows:

- **Foreign:** median measured latency **≤ 30 000 ms AND** breach-rate (fraction > 30 000 ms)
  **below a small bound** (≈ ≤ 10–20 %) — *consistently*, not one lucky draw; **AND**
- **Home (Windows), same windows:** stays high (~40 s tail, p50 ≈ 26 s, ~⅓ breach).

If confirmed, the fix is the H818 foreign-server orchestration, **not** a threshold change (the
30 000 ms ceiling stays). If the foreign route also breaches, the cause is **not** Russia→Anthropic
egress and the investigation reopens (payload lever already ruled out above).

### Step D — ONLY on confirmation (separate step, NOT part of this diagnostic)

Provision **four** Max profiles on the foreign route and **mint a new acceptance handoff** for the
bounded `arvant` retry + the `1 → 10 → 20 → 100` sequence, gated by the **same 30 000 ms ceiling**
(preferably the stricter N-probe median+breach-rate gate from the Gate-design implication above).
Until that confirmation + handoff exist, Linux production and H841/H842/H843 remain **blocked**.

_Dr. Mārcis Gasūns_
