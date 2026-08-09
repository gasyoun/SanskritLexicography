# DOC_VS_CODE_DRIFT_AUDIT_DAILY_ROUTINE.meta.md

_Created: 02-08-2026 · Last updated: 02-08-2026_

Companion record for [`DOC_VS_CODE_DRIFT_AUDIT_DAILY_ROUTINE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/DOC_VS_CODE_DRIFT_AUDIT_DAILY_ROUTINE.md).

## Purpose

Durable home for the spec of a scheduled cloud agent that files at most one GitHub issue per day
recording a place where this repo's documentation asserts something the code does not do. The
routine's own prompt is a transcription of the subject file, so the subject is the source of
truth: **edit the doc first, then update the routine**, or they drift — which would be a
particularly embarrassing failure for this doc in particular.

## Audience

Whoever maintains or re-tunes the routine, and any session that inherits a `[drift]`-labelled
issue and wants to know what bar it was filed against.

## Provenance

- Commissioned by MG, 02-08-2026, in the session that executed
  [H2160](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2160-Opus_RussianTranslation_whole-card-b0-hang-and-medium50-completion_02.08.26.md).
- Written by **Opus 5 1M** (`claude-opus-5[1m]`).
- The seed case is H2160's own incidental finding: `/pwg-live-gate` instructed "Gate on
  `duration_api_ms`" while no code had ever gated on it, and on 02-08 the two numbers disagreed
  on a real spend verdict (wall 75 586 ms NO-GO vs api 29 069 ms PASS). MG ruled the same day
  that the gate is wall (option A); the prose was corrected on both skill hosts.

## Ranked improvement backlog

1. **Wire the routine.** Blocked when written: creating it returns `HTTP 401` until a GitHub
   account is connected on claude.ai. Until then this file is a spec with nothing executing it.
2. **Measure the empty-day rate after ~2 weeks.** The two failure directions are opposite and both
   diagnostic: mostly-empty days mean the scope or the model tier is too narrow; a weak issue
   every single day means the "file nothing" rule is being eroded by the quota. Either one is a
   reason to re-tune, and neither is visible without counting.
3. **Consider widening scope beyond `RussianTranslation/`.** The drift class is not repo-specific;
   `csl-atlas`, `kosha` and `Systema-Sanscriticum` are the obvious next targets. Deliberately
   deferred — prove the signal on one repo first.
4. **Feed confirmed findings back into `/findings-append`.** A recurring drift *shape* (e.g.
   "recommendation in a memo copied into a skill as an instruction") belongs in FINDINGS as a
   class, not only as N individual issues.
5. **Escalate the model tier** if clause 4 of the bar (is this already known?) proves to be where
   the routine fails — that clause needs the most reading.

## Limitations

- **Finds drift, not correctness.** A doc and its code agreeing while both are wrong is invisible.
- **Scope is one subtree** of one repo.
- **Cloud sandbox, so no paid lane** — by design; it can read the gate code but never exercise it.
- The routine is **read-only on the repo**: it files an issue and never fixes anything, so a
  confirmed drift still needs a human or a follow-up session to close.

## Revision history

| Date | Change | Model |
|---|---|---|
| 02-08-2026 | Created alongside the subject doc; routine not yet created (GitHub-connection 401). | Opus 5 1M (`claude-opus-5[1m]`) |

_Dr. Mārcis Gasūns_
