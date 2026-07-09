# H317 — pwg-ru medium50 pipeline test window (2026-07-08)

_Created: 08-07-2026 · Last updated: 08-07-2026_

Measurement for [H317](https://github.com/gasyoun/Uprava/blob/main/handoffs/H317-Sonnet_RussianTranslation_pwg-ru-medium50-test_07.07.26.md):
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
[`src/pilot/output/requeue.h317_w1a.keys.txt`](src/pilot/output/requeue.h317_w1a.keys.txt),
[`requeue.h317_w1b.keys.txt`](src/pilot/output/requeue.h317_w1b.keys.txt),
[`requeue.h317_w2a.keys.txt`](src/pilot/output/requeue.h317_w2a.keys.txt)) in a
fresh session once a solo diagnostic launch comes back mostly/fully clean,
confirming the transient instability has passed. If a clean-environment solo
retry *still* shows this failure pattern, escalate as a genuine kill-gate
miscalibration for nominal medium-band cards (parallel to the `DAH_TAIL`
no-fallback-singleton finding) rather than assuming transient infra again.

## Update — 09-07-2026 diagnostic (H389): the real blocker is the agent() schema classifier, not transient infra

[H389](https://github.com/gasyoun/Uprava/blob/main/handoffs/H389-Sonnet_RussianTranslation_pwg-ru-medium50-resume_08.07.26.md)
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
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md):
slim the *generation* schema to reachable-AND-model-generated fields only (drop
the post-generation-added `government`/`evidence`/`evidence_summary`/`labels`/
`renou*`, trim descriptions, flatten `$defs`), pinned by a `window_selftest.py`
test so a future field addition cannot silently re-cross the threshold. Once
H428 lands, H389's medium50 windows become launchable again.

Classified in [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) as
`H389_MEDIUM50_SCHEMA_CLASSIFIER_BLOCK_2026-07-09` (and the prior
`H317_MEDIUM50_3WIDE_KILL_CASCADE_2026-07-08` entry marked `superseded`).

_Dr. Mārcis Gasūns_
