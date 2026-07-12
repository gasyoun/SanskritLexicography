# PWG→RU scale-readiness census — 2026-07-12

_Created: 12-07-2026 · Last updated: 12-07-2026_

Point-in-time answer to the question **"are the audits finished — ready to scale and
translate nonstop, cheap, quick, does not fall as before?"** Verified against the live
repo (not memory) by an 8-agent read-only workflow (Opus 4.8 `claude-opus-4-8`,
per-lane probes + two adversarial verifiers, ~1.0 M tokens). Fixes are handed off to
Opus in [H809](https://github.com/gasyoun/Uprava/blob/main/handoffs/H809-Opus_RussianTranslation_pwg-ru-scale-unblock-fixes_12.07.26.md).

## Bottom line

**Not ready to translate nonstop — and the dominant blocker is infra, not the pipeline.**
The *code* no longer "falls as before" (the H189/H220/H304 kill-gate + budget-switch +
cap-and-defer fixes hold and were re-verified), but as of 11-07 the **generation API host
is degraded** (schema-carrying probe read 682,753 ms → gate NO-GO), which makes *every*
lane time out regardless of the finished code. One flagship lane is separately blocked,
and the verb backlog cannot run "at scale" for a reason unrelated to the API.

## Per-lane verdict

| Lane | Verdict | State (12-07-2026) |
|---|---|---|
| **Verb-root drain** (H151/H179) | ❌ not "at scale" | Live `verb_worklist.py`: 749 attested · 48 promoted · **701 remaining, only 14 runnable — 687 blocked on missing rootmaps**. The 14 runnable are mostly `defer-calibrate` monsters (`sTA`). H151 is registered 🗄️ legacy. Machinery audited GO (H188) but that GO predates the API degradation and the rootmap gap. |
| **No-PWG supplement chain** (H214/H220/H255) | 🟡 draining, early | ~62 of 232 headwords promoted (~27%); last window 8/13 clean; throttled by recurring 180 s `KILL_CEIL` kill-timeouts (same infra headwind). The only actively-progressing lane. |
| **Dense nominal "medium50"** (H317→H442→H462) | 🔴 blocked | Split-pool fix (#311) landed on master but the live canary was never fired (Codex has no Workflow surface); last real run 0/12 clean. "Do NOT relaunch blind" standing rule still in force. |

## The gating issue: generation-API degradation

[`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md)
+ [`SERVER_OUTAGES.md` row 29](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md):

- 11-07 schema-carrying real-card probe (H566): **682,753 ms → NO-GO**; the 12-key recovery launch was correctly **not fired** (~4.2 M tokens saved).
- Not medium50-specific: cheap single-fragment no-PWG cards hit the 180 s ceiling at a **~57% transient rate** → host-level degradation.
- **Not re-probed on 12-07** (paid windows banned this sprint week). The gate reading stands at NO-GO.
- A blind "nonstop" launch into this state costs **~2.2 M tokens for 0 clean cards** (reproduced 3× on medium50).

## "Cheap" — true for typical heads, not universal

Marginal $ ≈ 0 (generation runs on the Claude **Max** subscription; the binding limit is
the **Max weekly token quota, still unmeasured**). Cheap holds for typical heads and the
verb lane (~$0.07–0.11/card); **kAla-class monster nominal heads are ~$4/card even
post-fix** and are made "cheap" only by *excluding* them via the H189 cost gate + H304
cap-and-defer. Absolute USD ride a **stale Sonnet-4.x rate table**
([`parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py)
+ the `perf_preflight.py` `$0.347/agent` constant) — trust token ratios, not the dollar figures.

## Audits — accurate-with-exceptions

"Audits finished" is essentially **true**. Every named readiness/correctness/architecture
audit is DONE — H188 (GO both paths), H178 Part A, H335, H405 (99.72% clean over 11,261
rows), S10 architecture, audit-churn FL1/2/3/5, the OPUS-tail (FL4/FL8/`ka`) — and three
adversarial re-audits on 09-07 tried to falsify prior fixes and **held**. The one real open
item is **H178 Part B** (human quality-evaluation: 4 review sheets await votes + H274
bake-off compute). No open MG `@DECIDE` gates scaling (the kAla monster-card `@DECIDE` was
closed 07-07 → cap-and-defer).

## "Nonstop" — structurally a throttled, attended drain

There is no API daemon: production runs in-chat through the Max Workflow surface, capped at
**≤3-wide (global, even across accounts** — extra seats buy quota, not concurrency), with
**per-window manual save-verification** required (the H145 `vid` run was silently lost at
exactly that step), the environment reaps long runs, and the 2026-06 autonomous loop was
explicitly **STOPPED**. Recent sessions move tens of rows; the store sits at ~11,383 of a
~140 k-sub-card target (~8–10%).

## What unblocks progress (in order) — handed to Opus in H809

1. **Re-probe the API** — `python src/pilot/probe_log.py gate`. Nothing scales until it returns healthy (<30 s, 0 conn-errors).
2. **If still degraded:** generate the **687 missing verb rootmaps** — the real verb-scale prep, a deterministic ~0-token side-lane that runs while the API is down.
3. **When healthy:** resume the no-PWG drain (per-window probe-gated) and fire the medium50 `h317_w1b` canary to validate the split-pool fix; reconcile the Sonnet-5 rate table.

## Provenance

Method: two read-only Opus 4.8 (`claude-opus-4-8`) workflows — (1) a 6-dimension per-lane
probe + 2 adversarial verifiers (the verb-lane "ready at scale" claim was **REFUTED**; the
medium50 "still blocked" claim **CONFIRMED**); (2) a 4-issue executable fix-spec + a
rootmap-determinism adversarial verify, feeding [H809](https://github.com/gasyoun/Uprava/blob/main/handoffs/H809-Opus_RussianTranslation_pwg-ru-scale-unblock-fixes_12.07.26.md).
Every figure is sourced from live in-repo files
([`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md),
[`RUN_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md),
[`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md),
[`verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py)).

_Dr. Mārcis Gasūns_
