# H4527 work item 2 — Codex reviewer brief and a correction to the record shape

_Created: 21-09-2026 · Last updated: 21-09-2026_

**Status (updated 21-09-2026, 16:30Z):** the review **ran and returned FAIL**. Codex `gpt-5.6-sol` on MSI, session `01a0c4ac-fbca-7103-a164-7ca779101aa0`; verdict and consequences in [H4527_WORK_ITEM_2_CODEX_VERDICT_FAIL_21-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_WORK_ITEM_2_CODEX_VERDICT_FAIL_21-09-2026.md). The run checked out, but `byte_identical_to_serial: true` overclaims, so no record is written.

**Earlier status:** the review has **not** happened yet. On 21-09-2026 at 14:09Z, Opus 5 (`claude-opus-5`, interactive `/go`) launched it as `codex exec --sandbox read-only` (`gpt-6-astra`, reasoning effort high). The launch died before the first tool call with `You've hit your usage limit ... try again at 10:02 PM` (Mac local time). Codex thread: `01a0c44c-ab21-7de0-8f6e-424a61e7616b`. There were zero paid PWG calls and zero probe attempts, and nothing was written.

## 1. The packet's paste-ready record does not validate — use this shape instead

The `serial_acceptance` object in [H4527_LIVE_COHORT_ACCEPTANCE_FIRST_CLEAN_20-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_LIVE_COHORT_ACCEPTANCE_FIRST_CLEAN_20-09-2026.md) is correct. The **envelope** around it is not. I checked it against `cohort_live_admission.validate_record` on `origin/master` `2b5b4427`, with a placeholder PASS block standing in for the review:

| Record shape | `validate_record` verdict |
|---|---|
| Packet object as written (`max_admitted_width: 2`, no `admitted_profiles`) | **False** — `admitted_profiles must be a non-empty list of profile names` |
| Plus `admitted_profiles: ["c1"]`, width still 2 | **False** — `admitted_profiles lists 1 profile(s) but max_admitted_width is 2` |
| `admitted_profiles: ["c1"]`, `max_admitted_width: 1` | **True** — `acceptance record valid` |

The fleet is `c1` alone. That was MG's 11-09 ruling (`c2`'s token expired 24-07, and `claude4`–`claude6` stay unfunded), so **the only honest record today admits width 1 on `["c1"]`**. Width 2 then needs two things: a second profile with money, and a deliberate edit of this record that adds that profile together with its own admission evidence. `fleet_guard` refuses width 2 for the same reason in the meantime. The record's value is that the acceptance and sign-off halves are finished, so the width-2 rung is later a one-field change.

## 2. The reviewer run (paste on the Mac after 22:02 local time on 21-09, or any later day)

```bash
cd ~/Documents/GitHub/SanskritLexicography && git fetch origin && git worktree add ../SanskritLexicography-h4527-review origin/master
```

```bash
cd ~/Documents/GitHub/SanskritLexicography-h4527-review && codex exec --sandbox read-only -c model_reasoning_effort=high - < RussianTranslation/pwg_ru/h4527/H4527_WORK_ITEM_2_CODEX_REVIEWER_BRIEF_21-09-2026.md
```

Codex reads this whole file as its prompt. Section 3 is addressed to it.

**If the verdict is PASS:** a session that is not the Codex session writes `RussianTranslation/pwg_ru/h4527/COHORT_LIVE_ACCEPTANCE.json` in the section 1 shape. It fills `reviewer_sign_off` with `reviewer: "Codex <exact model id>"`, `session: "<codex thread id>"`, `dated`, `verdict: "PASS"`, and `evidence` pointing at the committed verdict text. Then `python RussianTranslation/src/pilot/cohort_live_admission.py --width 1` must print admitted, and `--width 2` must still refuse.
**If the verdict is FAIL:** no record gets written. The reasons are recorded here and in the H4527 handoff, and width 2 stays refused.

## 3. Brief — addressed to the Codex reviewer

You are an **independent reviewer** for work item 2 of handoff H4527, and you did not run the window under review. Work read-only: do not edit, commit, spawn paid calls, or run anything that talks to a model API. Re-derive every claim from the primary artifacts. The packet's own claims are what you are testing.

**What is being signed off:** whether one live width-1 window, run through the cohort path (`bounded_staged_run.py --execute --cohort-path --cohort-width 1`) on profile `c1`, is valid acceptance evidence for `RussianTranslation/pwg_ru/h4527/COHORT_LIVE_ACCEPTANCE.json` (schema `pwg.cohort_live_acceptance.v1`, validator `RussianTranslation/src/pilot/cohort_live_admission.py`). The claimed `serial_acceptance` half is: run_id `h4527-acc-200920`, window_id `h4527sen08`, profile `c1`, completed_utc `2026-09-20T18:02:59Z`, `via_cohort_path: true`, `byte_identical_to_serial: true`.

**Primary evidence:**

1. `RussianTranslation/pwg_ru/h4527/H4527_LIVE_COHORT_ACCEPTANCE_FIRST_CLEAN_20-09-2026.md` — the packet under test
2. `RussianTranslation/pwg_ru/h4527/acceptance.sen.report.json`, `acceptance.sen.events.jsonl`, `acceptance.sen.checkpoint.json`
3. `RussianTranslation/pwg_ru/h4527/acceptance.sen.serial_compare.json` and `RussianTranslation/src/pilot/h4527_acceptance_compare.py`. You may run the compare script if reading it first confirms it is read-only and spawns nothing.
4. `RussianTranslation/src/pilot/cohort_live_admission.py`, `cohort_live_dispatch.py`, `cohort_engine.py`, and the cohort-path branch of `bounded_staged_run.py`
5. `RussianTranslation/pwg_ru/h1437/H1437_PHASE4_CLOSEOUT_2026-08-29.md` — the offline proof that widths 1, 2 and 3 are byte-identical

**Checks — cite a file:line or JSON key for each:**

- **A.** The claimed run_id, window_id, profile and completed_utc match the report, events and checkpoint exactly.
- **B.** The window went through the cohort path (`summary.cohort.path == "live"`, cohort dispatch visible in events), not through the serial supervisor.
- **C.** The accounting holds. `calls_spent == calls_reserved`. The wave has exactly one promote-ready, one batch_promote and one TM callback. `accepted_order` is not empty, there is no requeue, and no failure `stop_reason` appears. A `null` stop_reason with exit code 1 is the known FINDINGS §642 reporting defect, fixed by H5209. Judge whether it matters here.
- **D.** State what `byte_identical_to_serial: true` actually rests on. The packet admits `same_outcome: false` and says no same-card A/B is possible. Judge whether live structural identity (19 shared sealed artifacts, identical window_status and ledger key sets) plus H1437 Phase 4's offline byte identity is **sufficient** for a width-1 acceptance record. Say plainly if the field name overclaims.
- **E.** Report anything that makes admitting the record unsafe: missing evidence files, numbers that disagree, a bypassed gate, or any use of `--skip-canary-gate` or `ALLOW_*`.
- **F.** Confirm or refute section 1: with the fleet at `c1` alone, is `max_admitted_width: 1`, `admitted_profiles: ["c1"]` the right record shape?

Print exactly this block as the last thing you output:

```
VERDICT: PASS | FAIL
REASONS: <3-8 bullets, each with a citation>
CAVEATS: <bullets; include your view on the byte_identical_to_serial wording>
```

_Гасунс_
