# H579 — the `h317_w1b` probe inputs were destroyed, and what rebuilding them changed

_Created: 18-08-2026 · Last updated: 18-08-2026_

Recorded by Opus 5 (`claude-opus-5`) while executing
[H579](https://github.com/gasyoun/Uprava/blob/main/handoffs/H579-Opus_RussianTranslation_h317-w1b-recovery-reprobe_11.07.26.md)
— `h317_w1b` recovery re-probe after generation-env recovery + guarded 12-key retry.

## What was lost

H579 assumes a live worktree at `SanskritLexicography-h317-split-canary`. That
worktree no longer exists. Two of its inputs lived **only** inside it:

| Input | Status | Why it died |
|---|---|---|
| `src/pilot/input/*.raw.txt` + `*.portrait.json` | gone | gitignored, [`.gitignore`](https://github.com/gasyoun/SanskritLexicography/blob/codex/h317-w1b-split-canary/RussianTranslation/.gitignore) line 63 `RussianTranslation/src/pilot/input/` |
| `src/pilot/output/requeue.keys.txt` (the 12-key queue) | gone | untracked local state under the same worktree |
| `src/pilot/run_pilot_wf.h317_w1b.split.js` | gone | generated harness, ignored by `run_pilot_wf.*.js` |

Neither `input/` nor the launchers were ever tracked on any ref
(`git rev-list --all --objects` finds nothing under `pilot/input`), so there is
no commit to restore them from.

## What rebuilding recovered — and what it did not

The 12 keys survive because H579's own body lists them verbatim; the cards were
regenerated with
[`src/_pilot_gen_merged.py`](https://github.com/gasyoun/SanskritLexicography/blob/codex/h317-w1b-split-canary/RussianTranslation/src/_pilot_gen_merged.py)
after decoding the safe-names to real keys via `decode_safe_name`
(`spf_s` → `spfS`, `_ac_arya` → `AcArya`, …). The harness regenerates cleanly:
12 cards, 7 batches, `agent_expected_after_tm=17`.

**The regenerated window is not the July window.** The probe payload moved:

| Reading | Largest card | Skeleton | Payload |
|---|---|---|---:|
| H532 10-07-2026 | `spf_s` | 8,909 chars | 27,462 B |
| H566 11-07-2026 | `spf_s` | 8,909 chars | 27,462 B |
| **H579 18-08-2026** | **`vfzwi`** | **2,752 chars** | **22,006 B** |

`spfS` now merges as `PWG rec=1 senses=1 | PW=1 SCH=0 PWKVN=0` and its skeleton
is 2,226 B. So any latency this session measures is **not** byte-comparable to
the 284,838 ms / 682,753 ms readings in
[`generation_api_probe_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/codex/h317-w1b-split-canary/RussianTranslation/src/pilot/generation_api_probe_log.jsonl).
It does still gate correctly in the absolute sense the handoff defines
(< 90,000 ms, 0 connection errors), and it gates the *right* harness, because
the recovery launcher is built from these same regenerated cards.

`probe_schema.py emit` also warns that the launcher's `GRAMMARS` are non-empty
and their contribution to `cardBlock()` is omitted from the probe — the probe
under-represents the real per-card load by that much.

## The reusable lesson

A handoff whose execution depends on gitignored, worktree-local state is only as
durable as the worktree. `/worktree-gc` sees a clean tree and removes it; the
handoff then reads as `@WAITING` on an external service when it is really
blocked on vanished inputs. Either the state is regenerable from a tracked
command recorded in the handoff, or it must be archived before gc.

_Dr. Mārcis Gasūns_
