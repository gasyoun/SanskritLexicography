# H4527 work item 2 — the Codex reviewer's verdict is FAIL

_Created: 21-09-2026 · Last updated: 21-09-2026_

**Reviewer:** Codex `gpt-5.6-sol`, reasoning effort high, `codex exec --sandbox read-only`, session `01a0c4ac-fbca-7103-a164-7ca779101aa0`, run on the Windows box (MSI). The Mac's Codex account was still over its usage limit at 15:52Z, but MSI's own login had quota. The review ran on a clean detached worktree at `origin/master` `28beaa4ac`, and the prompt was section 3 of [H4527_WORK_ITEM_2_CODEX_REVIEWER_BRIEF_21-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_WORK_ITEM_2_CODEX_REVIEWER_BRIEF_21-09-2026.md). It used about 132.6k tokens. It made no paid PWG calls, used no probe ration and wrote nothing.

**Launched by:** Opus 5 (`claude-opus-5`), interactive `/go` on the Mac.

## What follows from the FAIL

1. `COHORT_LIVE_ACCEPTANCE.json` stays **unwritten**, as the brief's FAIL branch requires. The admission gate for widths above 1 therefore stays closed. Nothing practical is lost today, because the `c1`-only fleet can't run width 2 anyway (MG ruling 11-09).
2. **The run itself passed review.** Checks A, B, C, E and F hold: identity, the live cohort route, the 1 == 1 accounting, one promote plus one TM, no bypassed gate, and the width-1 record envelope on `["c1"]`.
3. **Check D failed, and it is a contract defect, not a run defect.** `cohort_live_admission.validate_record` *requires* `byte_identical_to_serial: true`. No live evidence can make that field literally true, because a sub-card is promoted once and a same-card A/B is impossible. The honest claim is "offline byte identity across simulated widths plus live structural compatibility". Clearing this needs a human ruling on the contract. It cannot be fixed with a better packet.
4. **Two retention gaps, both fixable, neither fixed here.** First, the compare script's raw inputs (`src/pilot/output/coordinator/artifacts/h4527sen08` and the serial lease) exist only on MSI and are gitignored. They are card data in a public repo, so committing them is a data-fence question. Second, the canary receipt (`h4527-canary-200920`) and the exact executed argv were never retained as review artifacts.

## The verdict, verbatim

Paths are made relative to the repo root; nothing else is edited.

```
VERDICT: FAIL
REASONS:
- The run identity is consistent: `h4527-acc-200920`, window `h4527sen08`, and profile `c1` appear in the report and event stream; `completed_utc` matches the promotion timestamp in both report and checkpoint. [Report](RussianTranslation/pwg_ru/h4527/acceptance.sen.report.json:3) · [events](RussianTranslation/pwg_ru/h4527/acceptance.sen.events.jsonl:3) · [checkpoint](RussianTranslation/pwg_ru/h4527/acceptance.sen.checkpoint.json:34)
- The live cohort route and accounting are proven: `summary.cohort.path` is `live`; accepted order is non-empty; calls spent/reserved are 1/1; requeue is empty; promotion and TM completion are true; `stop_reason` is null. [Report](RussianTranslation/pwg_ru/h4527/acceptance.sen.report.json:63) · [cohort branch](RussianTranslation/src/pilot/bounded_staged_run.py:1161)
- The former exit-code 1 did not invalidate the completed wave: it was a route-scoring defect after the successful summary had been produced, and the current implementation now evaluates cohort terminal facts separately. [Exit contract](RussianTranslation/src/pilot/bounded_staged_run.py:963)
- Section 1’s envelope correction is right: the validator accepts `max_admitted_width: 1` with `admitted_profiles: ["c1"]`, while the fleet guard necessarily refuses width 2 with only one profile. [Validator](RussianTranslation/src/pilot/cohort_live_admission.py:117) · [fleet guard](RussianTranslation/src/pilot/cohort_live_dispatch.py:68)
- The required `byte_identical_to_serial: true` assertion is not established. The live receipt compares file sets, schemas, and JSON field sets—not file or store bytes—and explicitly records `same_outcome: false`; the byte-level proof is an offline fake-worker width-1/2/3 simulation. [Comparison criteria](RussianTranslation/src/pilot/h4527_acceptance_compare.py:140) · [receipt](RussianTranslation/pwg_ru/h4527/acceptance.sen.serial_compare.json:6) · [offline proof](RussianTranslation/pwg_ru/h1437/H1437_PHASE4_CLOSEOUT_2026-08-29.md:41)
- The raw coordinator artifact directories consumed by the comparison script are absent from this checkout, so its committed result cannot be independently recomputed; the script correctly fails when either lease directory is missing. [Comparison inputs and failure rule](RussianTranslation/src/pilot/h4527_acceptance_compare.py:42)
CAVEATS:
- `byte_identical_to_serial` overclaims. The defensible statement is “offline byte identity across simulated widths plus live structural compatibility”; that is materially weaker than live byte identity with the serial-supervisor route.
- No affirmative evidence of `--skip-canary-gate` or `ALLOW_*` use was found. However, the retained packet supplies only a prose assertion of CANARY GO; neither the canary receipt nor the exact executed argv is among the review artifacts. [Packet](RussianTranslation/pwg_ru/h4527/H4527_LIVE_COHORT_ACCEPTANCE_FIRST_CLEAN_20-09-2026.md:86) · [mechanical canary gate](RussianTranslation/src/pilot/bounded_staged_run.py:1368)
- This FAIL concerns the truthfulness and reproducibility of the sign-off field, not the integrity of the observed width-1 run or the corrected width-1 record envelope.
```

_Гасунс_
