# IMPLEMENTATION — RussianTranslation ask-batch residual

_Created: 02-08-2026 · Last updated: 02-08-2026_

Worktree: `git -C SanskritLexicography worktree add -b <branch> ../SanskritLexicography-h###-<pid> origin/master`.

## W1-RV (Opus)

1. `git fetch`; open sibling RV PLAN + ROADMAP; check H1843/H1844 status on origin (registry + merged PRs).
2. If 1a/1b incomplete: finish the first red residual per sibling IMPLEMENTATION.
3. If 1a/1b ✅: take the first open wave-2 item in sibling ROADMAP that is still machine-doable without new human votes.
4. Commit + PR; update `RussianTranslation/.ai_state.md` one checkbox.

## W1-TM (Fable)

1. Open sibling pubgrade TM PLAN; inventory open wave items vs committed tree.
2. Execute **one** unfinished deliverable with acceptance in sibling VERIFICATION (prefer smallest closed loop).
3. Commit + PR; note LANG_PARITY if SHARED surfaces change.

## W1-GL (Fable)

1. Open sibling Sa→Ru gloss PLAN; same residual pick discipline as TM.
2. Execute one unfinished unit (indexed gloss — never full rewrite).
3. Commit + PR.

## W1-GATE (Sonnet)

1. Read `/pwg-live-gate` skill; confirm credentials path without printing secrets.
2. Run **exactly five** paired measurements: each probe records wall-clock and `duration_api_ms` (or equivalent API duration field present in telemetry).
3. Write committed table under e.g. `RussianTranslation/pwg_ru/reports/C4_CEILING_REMEASURE_2026-08.md` (create if needed) with n=5, both metrics, date, model tier+version.
4. Lock **one** fail metric in that file (and append FINDINGS one-liner if ceiling floor changes).
5. If measured floor supports raising/relaxing ceiling constants, surgical config edit only — **never** promote, **never** write store, always leave `--stop-before-promote` as the operator default.
6. Do **not** start medium50/bulk drain (wave-2).

_Dr. Mārcis Gasūns_
