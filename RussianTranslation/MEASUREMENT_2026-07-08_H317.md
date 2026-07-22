# H317 — pwg-ru medium50 pipeline test window (2026-07-08)

_Created: 08-07-2026 · Last updated: 08-07-2026_

Measurement for [H317](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H317-Sonnet_RussianTranslation_pwg-ru-medium50-test_07.07.26.md):
a controlled 50-headword test of the PWG→RU pipeline on **medium** words (DCS
frequency band 4, nominal, 3–30 citations per entry — see
[`src/pilot/select_medium50.py`](src/pilot/select_medium50.py) for the exact
selection rule and why "senses" is operationalized as citation count for
nominal entries). Worklist frozen at
[`src/pilot/H317_medium50_worklist.08.07.26.json`](src/pilot/H317_medium50_worklist.08.07.26.json).
Model: Sonnet 5 (`claude-sonnet-5`), isolated worktree `SanskritLexicography-h317`
(branch `h317-pwg-ru-medium50-test`).

## Result: 0/50 promoted — the pipeline did not clear this window this session

This is the finding, filed per the handoff's own instruction ("if the clean
rate is materially below the verb-lane baseline, file the finding — don't
silently absorb it"). Two launch attempts were made; both failed to produce a
usable clean-card rate, for two distinct but overlapping reasons documented in
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) (`H317_MEDIUM50_3WIDE_KILL_CASCADE_2026-07-08`).

### Attempt 1 — 3 windows launched concurrently (≤3-wide, per `RUN_FREQ_MAX.md`)

| window | cards | expected agents | actual agents | ok | null |
|---|---:|---:|---:|---:|---:|
| h317_w1a | 13 | 19 | 67 | 0 | 13 |
| h317_w1b | 12 | 17 | 61 | 0 | 12 |
| h317_w2a | 13 | 13 | 49 | 0 | 13 |
| **subtotal** | **38** | **49** | **177** | **0** | **38** |

Every batch and every self-heal bisection group hit the kill-timeout ceiling
(45–180s) and cascaded through the binary-split heal lanes until each window's
own `MAX_AGENTS` budget-kill-switch tripped. 1,550,959 subagent tokens spent,
zero cards translated. h317_w2b was never launched (paused after this result).

### Attempt 2 — solo (1-wide) retries of h317_w1a and h317_w1b

| window | cards | agents | ok | null | agent-errors ("Connection closed mid-response") |
|---|---:|---:|---:|---:|---:|
| h317_w1a (retry) | 13 | 67 | 1 raw / **0 net clean** (flagged `missing_senses`) | 12 | 8 |
| h317_w1b (retry) | 12 | 61 | 3 raw / **0 net clean** (1 high-confidence defect `d_ikz_a`, 2 more flagged in review queue) | 9 | 0 |
| **subtotal** | **25** | **128** | **0 net clean** | **21 null + 4 raw-but-defective** | 8 |

Retrying solo (removing concurrency entirely) still surfaced widespread
`Connection closed mid-response` agent errors on the first retry (h317_w1a),
though none on the second (h317_w1b) — consistent with a session-wide
transient API instability that was easing but had not fully cleared, layered
on top of (not instead of) the kill-gate's known sensitivity to no-fallback
nominal singleton cards (see the `DAH_TAIL_2026-07-06` / kill-gate-calibration
entry in `LAUNCH_FUCKUPS.md` for the precedent of the same class of card
behaving differently from dense verb batches).

### Totals across both attempts

- **50 cards planned, 63 card-attempts made (38 + 25, some cards attempted twice), 0 promoted.**
- **305 agent() calls, ~6,647,614 subagent tokens spent, 0 clean cards.**
- Every null was classified **transient** by the deterministic gate (0 markup/coverage/NWS
  defects among the nulls); the handful of cards that DID return content were flagged
  by the semantic-risk gate (`missing_senses`, `missing_required_sense_field`,
  `possible_sense_compression`) rather than passing clean — so even where the API call
  itself succeeded, the model's output under time pressure/retry churn was not print-safe.

## What this measures (and does not measure)

This test window **does not indicate a regression in translation quality** on
medium-band nominal headwords — no card that returned content was cleanly
promotable, but none was rejected for a genuine markup/coverage defect either;
the sample is too thin (4 raw returns out of 25 attempts) to judge quality at
all. What it **does** measure:

1. **≤3-wide concurrent Workflow launches are not a safe floor.** This session's
   exactly-3-wide launch produced a 100% kill-timeout cascade — worse than the
   previously-documented 18-wide Slice-D blowout in relative terms (that run at
   least got partial results before the 429 storm).
2. **A session-wide transient API instability (`Connection closed mid-response`)
   was present during this window**, independent of concurrency, and was still
   partially present on the first solo retry.
3. **The self-heal/binary-split kill cascade is expensive when it doesn't
   resolve**: 305 agent calls for 0 net clean cards is a total-loss cost profile,
   not a graceful degradation — each hard-failure group's bisection attempts
   still count against the same window's `MAX_AGENTS` budget, so a run already
   struggling with latency spends its entire budget retrying instead of failing
   fast to a clean transient-requeue state.

## Recommended next action

Do not keep burning agent budget against a session showing these symptoms.
Resume the H317 window (h317_w1a residual 12, h317_w1b residual 9, h317_w2a
all 13, h317_w2b not yet attempted — see
`src/pilot/output/requeue.h317_w1a.keys.txt` (local-only, gitignored),
`requeue.h317_w1b.keys.txt`,
`requeue.h317_w2a.keys.txt`) in a
fresh session once a solo diagnostic launch comes back mostly/fully clean,
confirming the transient instability has passed. If a clean-environment solo
retry *still* shows this failure pattern, escalate as a genuine kill-gate
miscalibration for nominal medium-band cards (parallel to the `DAH_TAIL`
no-fallback-singleton finding) rather than assuming transient infra again.

## Update — 09-07-2026 diagnostic (H389): the real blocker is the agent() schema classifier, not transient infra

[H389](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H389-Sonnet_RussianTranslation_pwg-ru-medium50-resume_08.07.26.md)
launched the single solo diagnostic window this measurement recommended
(`h317_w1a`, 13 keys, no concurrency), on 09-07-2026, Opus 4.8
(`claude-opus-4-8`) driving the Workflow tool; generation model unchanged
(Sonnet 5, hardcoded in the harness).

**Result: 0/13, 0 subagent tokens, 83 ms.** All 67 `agent()` calls — every
batch (b0–b9), every binary-split heal group, every retry — errored identically:

> `blocked by safety classifier: output schema too large to classify safely`

The budget kill-switch (`MAX_AGENTS=67`) tripped because every errored call
counts against the window budget. No model was ever invoked (0 tokens).

### This supersedes the "transient API instability" reading above

The recommended-next-action test ("resume once a solo diagnostic comes back
mostly clean, else escalate as a kill-gate miscalibration") returned a **third,
decisive** answer neither branch anticipated: a **deterministic, pre-generation
platform block**. It is not concurrency (the run was 1-wide), not transient
latency (`Connection closed mid-response` did not appear — the agents never ran),
and not the nominal kill-gate (the kill-gate never engaged; the classifier
refused the schema first).

Root cause = the same one measured for the H388 SkillOpt B-arm the same day:
the opt2 `CARDS_SCHEMA` handed to every `agent({schema})` call is **too large
for the Workflow-tool safety classifier** (~8,202 chars: nested `$defs` for
card/record/sense carrying `government`/`evidence`/`evidence_summary` objects,
many enums, long descriptions). [Uprava/FINDINGS.md §30](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
🔴 first recorded this class; its orphan-`$def` prune fix (`_ref_names` /
`_reachable_defs`, landed 03-07, H130) is **necessary but no longer sufficient**
— H335 (government) and H405 (evidence/stage-2) grew the *reachable* schema past
the classifier threshold after that fix landed.

### Consequence — the whole opt2 path is blocked, not just this window

Every pwg_ru opt2 window uses `gen_opt_harness2.py` and hits the identical block:
the H317/H389 medium50 windows, the H388 B-arm live gate, and the H151 verb-root
drain. The block wastes **0 tokens per attempt but yields 0 progress**, so
retrying is pointless.

**Decision: STOP the H317/H389 window resume.** Do not launch `h317_w1b`,
`h317_w2a`, or `h317_w2b` — they would each hit the same deterministic refusal.
Escalated to
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md):
slim the *generation* schema to reachable-AND-model-generated fields only (drop
the post-generation-added `government`/`evidence`/`evidence_summary`/`labels`/
`renou*`, trim descriptions, flatten `$defs`), pinned by a `window_selftest.py`
test so a future field addition cannot silently re-cross the threshold. Once
H428 lands, H389's medium50 windows become launchable again.

Classified in [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) as
`H389_MEDIUM50_SCHEMA_CLASSIFIER_BLOCK_2026-07-09` (and the prior
`H317_MEDIUM50_3WIDE_KILL_CASCADE_2026-07-08` entry marked `superseded`).

## Update — 09-07-2026 relaunch (H437): classifier IS unblocked, but the kill-gate cascade is now the isolated blocker

[H437](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H437-Sonnet_RussianTranslation_pwg-ru-medium50-resume-post-h428_09.07.26.md)
relaunched the three windows H389 could not (`h317_w1b`, `h317_w2a`,
`h317_w2b`) now that
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md)
slimmed the opt2 generation schema (10,940 → 1,698 chars; `--dump-schema`
re-confirmed 1,698 at the start of this session). Opus 4.8 (`claude-opus-4-8`)
drove the Workflow tool; generation model unchanged (Sonnet 5, hardcoded in the
harness). Each window launched **solo (1-wide)**, sequentially, per
`RUN_FREQ_MAX.md`. Fresh worktree `SanskritLexicography-h437` (branch
`h437-pwg-ru-medium50-resume`).

### Per-window result — every window tripped its own budget-kill-switch

| window | cards | agents (spent/max) | raw returns | **net clean (promoted)** | defect | transient-null | subagent tokens | wall-clock |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| h317_w1b | 12 | 61/61 | 3 | **1** (`yuvan`) | 2 (`dīkṣā`, `rātra`) | 9 | 2,898,353 | 7.96 min |
| h317_w2a | 13 | 49/49 | 3 | **1** (`ṛtvij`) | 2 (`bhakṣa`, `vināśa`) | 10 | 1,628,556 | 6.28 min |
| h317_w2b | 12 | 52/52 | 2 | **0** | 2 (`bhrū`, `prada`) | 10 | 2,153,758 | 6.82 min |
| **total** | **37** | **162** | **8** | **2** | **6** | **29** | **6,680,667** | **21.06 min** |

`budget_kill_switch_tripped = true` on all three. Two clean cards promoted to
`pwg_ru_translated.jsonl` (`yuvan` 11 sense-rows, `ṛtvij` 3 sense-rows) via
`promote_final_cards.py --merge` on the audit-clean subset only (defects and
kill-switched nulls held back).

### The three-way branch H317 posed is now decided — it is (3), the kill-gate

H317's measurement named three candidate blockers and could not choose between
them; each successive session eliminated one:

1. **Concurrency** — refuted by H317 attempt 2 (solo 1-wide still failed) and
   again here (all three solo launches failed identically).
2. **Transient API instability** (`Connection closed mid-response`) — refuted
   here: **zero** connection errors across 162 agent calls / 6.68 M tokens. The
   agents ran to completion; they were not dropped.
3. **Kill-gate / self-heal-budget miscalibration for nominal medium-band
   singleton cards** — **confirmed.** With the classifier unblocked and the
   network healthy, every window still cascaded through the self-heal
   binary-split heal lanes (`heal-group-hard-failure gN`) until it exhausted its
   own `MAX_AGENTS` budget. The cost profile is near-total-loss by design: ~2 M
   tokens per window buys ~1 clean card, because each hard-failure group's
   bisection attempts count against the same budget, so a window that hits dense
   `<ls>`/sense presplit fragments spends its whole budget healing instead of
   failing fast to a clean transient-requeue.

This is the escalation H389's recommended-next-action foresaw ("If a
clean-environment solo retry *still* shows this failure pattern, escalate as a
genuine kill-gate miscalibration for nominal medium-band cards"). The
clean-environment retry happened; the pattern held; it is escalated.

### n=50 medium50 — final tally

| window | keys | status | net clean |
|---|---:|---|---:|
| h317_w1a | 13 | H389 diagnostic classifier-blocked (0 tokens) pre-H428; **not relaunched under H437** (out of scope; cascade now reproduced on the other 3, so relaunching without the kill-gate fix would burn ~2 M tokens for ~1 card) | 0 |
| h317_w1b | 12 | launched, kill-switch tripped | 1 |
| h317_w2a | 13 | launched, kill-switch tripped | 1 |
| h317_w2b | 12 | launched (first-ever), kill-switch tripped | 0 |
| **medium50** | **50** | **2 promoted; kill-gate is the blocker** | **2** |

Net across the whole H317→H389→H437 arc: **50 keys planned, 2 promoted (4%)**;
the pipeline is now proven to *run* on this card class (H428 unblocked
generation) but the kill-gate/self-heal budget converts that into ~1 clean card
per 12–13 dense band-4 nominal singletons.

Classified in [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) as
`H437_MEDIUM50_KILLGATE_CASCADE_2026-07-09` (`kill-gate-calibration`, routed to a
bug-hunt handoff for the recalibration). Compact rollup row in
[`RESULTS_LOG.md`](RESULTS_LOG.md).

## Update — 10-07-2026 (H442): per-card heal budget landed; w1b re-measure CONFOUNDED by transient slowness

[H442](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H442-Opus_RussianTranslation_pwg-ru-killgate-recalibration-nominal-medium_09.07.26.md)
(Opus 4.8 `claude-opus-4-8` drove the Workflow; generation Sonnet 5, hardcoded) added a
**per-card heal-call ceiling** (direction #1 of the handoff — fail fast, not
heal-to-exhaustion): `selfHeal` derives one shared `{spent,max}` per card sized
`ceil(nGroups * PER_CARD_HEAL_FACTOR) + PER_CARD_HEAL_HEADROOM` and threads it through
`healGroup` + its bisection recursion, so a card that crosses its ceiling returns a
**partial** instead of draining the shared window `MAX_AGENTS` pool
([SanskritLexicography PR #301](https://github.com/gasyoun/SanskritLexicography/pull/301)).
Tuned to `factor 1.5 / headroom 3` after the w1b caps at `3.0/4` summed to ~198 >> the
61-agent window budget. Fresh worktree `SanskritLexicography-h442` (branch `h442-killgate`).

### Per-window result — h317_w1b re-run (one launch)

| run | cards | agents | raw ok | **audit-clean** | tripped | conn-errors | kill-timeouts | per-card fires | kill-bisect blocks | tokens | wall |
|---|---:|---:|---:|---:|:--:|---:|---:|---:|---:|---:|---:|
| H437 w1b (clean env) | 12 | 61/61 | 3 | **1** (`yuvan`) | yes | 0 | 1 | n/a | n/a | 2.90M | 7.96 min |
| H442 w1b run-1 (per-card cap) | 12 | 61/61 | 3 | **0** | yes | 3 | 58 | 0 | n/a | 2.22M | 9.27 min |
| H442 w1b run-2 (+ kill-no-bisect, depth-1 precursor) | 12 | 61/61 | 3 | **0** | yes | 3 | 76 | 0 | **19** | 2.17M | 10.49 min |

Both H442 runs returned 3 raw cards, all `requeue_defect` → **audit-clean 0/12** (vs H437's 1
promoted). Neither met the stop condition (≥6/12 clean AND no trip), and **both were confounded
by a persistently degraded generation environment** — not the heal lane:

1. **The per-card cap never bound.** `partial_keys` empty, **0** `per-card-heal-budget`
   failures. With all 12 cards routing to the heal lane in one shared `parallel()` pool
   against one `AGENTS_SPENT` counter, the **window budget (61) is hit first** — no single
   card reaches its own 6–14 cap. Direction #1 alone cannot stop this window: the binding
   constraint is the *shared* window budget when *every* card heals, not one card's monopoly.
2. **Transient API degradation returned.** 3 × `Connection closed mid-response` (H437 had
   **zero**), and **58 of 61 agent calls were kill-timeouts** — including fragments of
   **11–135 bytes killed at the 45 s floor** (`heal:vicitra#g1/A/B: kill-timeout 45s @
   skelBytes=11`). An 11-byte fragment cannot legitimately need 45 s; the calls themselves
   were hanging. So this window's budget was consumed by *killed* calls, not by healthy
   heal work — a different (infra) failure than H437's clean-env cascade.
3. **The kill-timeout × bisection waste was fixed, and the fix demonstrably fired.** `healGroup`
   bisected a kill-timeout the same as a malformed response, but bisection only helps a too-**big**
   group; under slow calls each split just spawns smaller fragments that hit the **same 45 s
   floor** (run-1: `heal:vicitra#g1/A/B: kill-timeout 45s @ skelBytes=11`, an 11-byte fragment
   killed at 45 s). Run-2's harness was generated with a depth-capped precursor
   (`KILL_BISECT_MAX_DEPTH=1` — split a killed group once, then requeue), which **fired 19 times**
   (19 second-level kill-timeouts routed to requeue instead of re-split), confirming the mechanism
   works. **The version that shipped to `master` is the stricter, simpler `KILL_TIMEOUT_NO_BISECT`
   (default on): the *first* kill-timeout on a heal group routes its fragments straight to the
   transient requeue — no kill-triggered bisection at all** (soft/malformed bisection stays
   uncapped). It was reconciled to that form during the PR #301 merge (see "reconciliation" note
   below); the depth-1 precursor and the shipped no-bisect reach the same conclusion here because
   the confound is *slow calls*, which neither can make fast: run-2 had **76 kill-timeouts** (up
   from 58) and the **same 3 connection errors**, so the window still tripped and 0 cards cleared
   audit.

**Both runs were in a degraded generation environment** (3 `Connection closed` errors each;
58 then 76 kill-timeouts, many on trivially small fragments). H437's clean env (0 connection
errors, 1 kill-timeout) is **not currently reproducible**, so the H442 stop condition
(≥6/12 clean, no trip) **cannot be measured right now** — the confound is infrastructure, not
the code. This is exactly the "each blind re-run is ~2 M tokens for ~1 card" waste the H437
guardrail warned against, so the 3rd allowed launch is **deliberately NOT fired** into the same
degradation.

**Disposition (documented decision, per the H442 goal's alternative outcome):**
- **Landed + kept** ([PR #301](https://github.com/gasyoun/SanskritLexicography/pull/301)): the
  per-card heal budget (`PER_CARD_HEAL_BUDGET`) and the kill-timeout no-bisect guard
  (`KILL_TIMEOUT_NO_BISECT`) are both sound guardrails — the per-card cap is a no-op when it
  doesn't bind (no regression) and *will* bound a single-pathological-card window; the no-bisect
  guard eliminates the re-split waste entirely (the depth-1 precursor's 19 fires demonstrated the
  mechanism; the shipped form is stricter — no kill-triggered bisection at all). Neither harms a
  healthy run.
- **Reconciliation note (concurrent-session merge):** a Codex/GPT-5 session worked H442 in the
  same worktree in parallel and reconciled the two kill-timeout variants *before* the PR #301
  auto-merge fired — keeping this session's `PER_CARD_HEAL_BUDGET` and replacing its depth-1
  `KILL_BISECT_MAX_DEPTH` with the simpler boolean `KILL_TIMEOUT_NO_BISECT` (== `depth 0`). Both
  LANG_PARITY entries (`per_card_heal_budget_h442`, `heal_kill_timeout_no_bisect_h442`) landed
  SHARED; `window_selftest.py` asserts the no-bisect form and bans the depth-cap constant, and
  CI's "RussianTranslation gates" is green. Master is internally consistent; nothing was lost.
- **Paused, not failed:** the medium50 lane's ≥6/no-trip validation is **blocked on a healthy
  generation environment**, not on more code. Re-measure w1b once when the API is clean (0
  connection errors on a warm-up call) before spending the 3rd launch.
- **Correction to H437's conclusion:** H437 refuted "transient API instability" for *its*
  session; these two runs show it is **environment-specific and recurs** — the medium50 lane is
  acutely sensitive to it because every card routes to the heal lane where each call is on the
  critical path. Logged to [`../../Uprava/SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md).

Classified in [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) as
`H442_MEDIUM50_KILLTIMEOUT_BISECTION_WASTE_2026-07-10`.


## Update — 10-07-2026 (H442 launch 3 of 3): env re-probed GREEN, run still 0/12 — INFRA-CONFOUNDED

The third and final allowed H442 launch. Fired only after the
[`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md)
warm-up gate returned **GO** (one Sonnet 5 `agent()` call, 3.3 s, 0 connection errors).
Orchestrator Opus 4.8 (`claude-opus-4-8`); generation Sonnet 5 (`claude-sonnet-5`, harness-pinned).
Harness **regenerated from the post-[PR #301](https://github.com/gasyoun/SanskritLexicography/pull/301)
generator** (verified to carry `KILL_TIMEOUT_NO_BISECT` + `PER_CARD_HEAL_FACTOR` and *not* the
depth-1 `KILL_BISECT_MAX_DEPTH` precursor); no old `run_pilot_wf.h317_w1b.js` was reused.

| run | cards | agents | audit-clean | tripped | conn-err | kill-timeouts | per-card fires | tokens | wall |
|---|---:|---:|---:|:--:|---:|---:|---:|---:|---:|
| H437 w1b (clean env) | 12 | 61/61 | **1** (`yuvan`) | yes | 0 | 1 | n/a | 2.90M | 7.96 min |
| H442 run-1 | 12 | 61/61 | **0** | yes | 3 | 58 | 0 | 2.22M | 9.27 min |
| H442 run-2 | 12 | 61/61 | **0** | yes | 3 | 76 | 0 | 2.17M | 10.49 min |
| **H442 run-3 (this)** | 12 | **58/58** | **0** | yes | **2** | **7** | **0** | **1.80M** | **11.90 min** |

**Verdict: INFRA-CONFOUNDED, not a code failure** (per the H442 goal's rule: *if connection errors
recur, abort the interpretation*). Evidence, in order of force:

1. **`audit_window.py` classified all 12 requeues `transient`, 0 `defect`.** Not one content
   failure. The window produced no bad Russian; it produced no Russian at all.
2. **The kill-timeouts moved to the CEILING.** Runs 1–2 hung 11–135-byte fragments at the 45 s
   `KILL_FLOOR`. This run hung whole 1.2–8.0 KB skeletons at the 180 s `KILL_CEIL`
   (`_ac_arya` @ 7,977 B, `d_ikz_a` @ 7,607 B, `yuvan` @ 5,276 B). Larger payloads, same hang —
   the calls are not slow *because* they are small or *because* they are big. They are slow.
3. **2 × `Connection closed mid-response`** (`b4[2]`, `heal:r_azwra#g2[8]`).
4. **The per-card heal cap still never bound** — `partial_keys` empty, `healed=0`, 0 per-card
   fires — for the third consecutive run. This re-confirms H442 finding #1 *as a structural fact*,
   not a tuning miss: `MAX_AGENTS` is derived from batch count and is the **same counter** the heal
   lane spends, so when every card heals the window budget always binds first. The per-card ceiling
   is unreachable by construction for this window shape.

### The warm-up gate is necessary but NOT sufficient — the finding of this run

A trivial `agent()` probe (a few hundred tokens, 3.3 s) returned **GO**, and the real window still
degraded. A load-representative probe is required: the failures cluster on multi-KB skeletons, and
a one-word prompt exercises none of that path. **Action:** the probe must send a skeleton-sized
payload (≥5 KB) and assert sub-30 s, before it can be trusted to authorize a ~2 M-token launch.
Recorded in the probe log; gate tightening tracked in
[H462](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md).

### Not token-comparable to runs 1–2

This harness generated **8 batches / 16 expected agents** where runs 1–2 were 17 expected / 61
agents, because the fragment-TM sidecar had grown to 217 cached fragments. The window still spent
its **full 58-agent budget** (16 expected → 58 spent) purely on the heal cascade. Any cross-run
token comparison in this table must be read with that in mind; see H462 Q3.

### Disposition

The 3-launch cap set by the H442 goal is now **exhausted**, and no launch produced a measurable
clean-rate: three of three were confounded by the generation environment. Per the goal's
alternative outcome, this is the **documented decision**: the medium50 nominal lane stays
**paused**, and the next move is *not* another tuning pass on the heal budget. It is (a) the
load-representative probe, (b) the returned-telemetry patch so the next run's kill-timeout and
connection-error counts are machine-read rather than hand-counted (H462), and (c) a design change
separating the heal pool from the translate pool — since finding #4 shows the per-card cap cannot
bind while they share one counter.

The FIX_PLAN's audit command is also wrong and was corrected in this pass: it says
`--root nominal_h317_w1b`, but the harness root is `h317_w1b`; the stale-artifact guard correctly
refused the mismatched run.

## Update — 10-07-2026: shared-counter design removed offline; live stop condition still pending

The disposition's structural item (c) is implemented on `codex/pwg-runtime-refactor`:
`agent_budget.py` derives independent translate and heal pools, and the generated runtime
charges whole-card/binary-split calls to `MAX_TRANSLATE_AGENTS` while fragment recovery and
presplit calls use `MAX_HEAL_AGENTS`. The heal ceiling is the sum of the per-card ceilings,
so the window cannot fire before those card caps solely because many cards heal at once.

Offline verification executes generated JavaScript under Node with two sense-dense presplit
cards and a null-returning mock `agent()`: both cards reach their own caps, all keys remain
explicitly requeueable, `heal_agents_spent == max_heal_agents`, and
`heal_budget_tripped=false`. This closes the construction defect, not the production result.
The medium50 lane remains paused until a load-representative probe passes and one healthy
`h317_w1b` canary measures the existing `>=6/12`, no-trip, zero-connection-error stop condition.

## Update — 10-07-2026: split-pool canary launch pack prepared; live probe still external

Fresh worktree `SanskritLexicography-h317-split-canary` on branch
`codex/h317-w1b-split-canary` was created from merged master `e971a69`. All 24 ignored input
files match the old harness metadata; the current TM sidecars were copied and hash-verified.
The stale shared-58 harness was not reused. Regeneration from merged code produced 12 keys /
8 batches / 16 expected calls with independent ceilings of 34 translate + 125 heal (159 total),
413,188 bytes below the Workflow cap. Node syntax, the full window/budget selftests, 41 parity
entries and 13 launch-ledger entries are green.

`probe_log.py prompt` emits a 6,491-byte skeleton-shaped prompt. This Codex environment exposes
no Claude Workflow `agent()` tool, so it cannot measure the required Sonnet-5 latency or connection
errors. No probe row was appended, no GO/NO-GO verdict was invented, and the one-launch canary
allowance remains unused. Continue from `FIX_PLAN_H442_2026-07-10.md` P1 in a Workflow-capable
session; do not run the old main-checkout harness.

_Dr. Mārcis Gasūns_
