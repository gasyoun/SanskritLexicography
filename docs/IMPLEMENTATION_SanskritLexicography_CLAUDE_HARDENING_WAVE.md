# Implementation — Claude Code hardening wave (pwg_ru pipeline)

_Created: 30-08-2026 · Last updated: 30-08-2026_

File-level build sequence per wave unit. Every unit: fresh session-unique worktree off `origin/master`, own branch, own PR, merge on green (handoff-scoped autonomy). Index: [PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md).

## W0 — #1864 epistemic gate green (Sonnet 5, 🟡2) — FIRST, alone

1. Reproduce: run the epistemic integrity gate exactly as CI does on master tip; capture the RED output verbatim (do NOT read the verdict through a pipe — [FINDINGS §-pipeline-exit-code trap](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
2. Classify the failure: registry drift vs genuine content defect. Fix the underlying rows/crosslinks, never the gate's sensitivity, unless the gate itself is provably wrong (then fix gate + add a RED-pin).
3. PR with the gate's own green run in the body; merge.

## W1 — gate-evidence contract (Opus 5, 🔴3) — after W0

1. New `RussianTranslation/src/pilot/gate_evidence.py`: `GateEvidence` dataclass, `emit()` JSON sidecar, `assert_nonvacuous()`. Selftest: a zero-input PASS must FAIL (pin RED against a stub gate without the contract).
2. Enumerate the nine gates from [#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803); retrofit one gate per commit, predicate logic untouched, each commit adding that gate's vacuous-PASS RED-pin to [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) or the gate's own selftest.
3. [#1800](https://github.com/gasyoun/SanskritLexicography/issues/1800): move the promote claim to wrap the full read-modify-write span in the promote path; RED-pin replays the `--ready-partial-report` silent-apply scenario from H2889.
4. [#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798): G9 duplicate-id predicate; RED-pin on a fixture carrying a known duplicated id.
5. Wire sidecar presence into the CI RussianTranslation-gates job. One PR (or two if the promote fix merits isolation); update the three sync-rule docs only if `--max-agents` semantics are touched (they should not be).

## W2 — mechanical batch (Sonnet 5, 🔴3)

Order inside the unit (each item = one commit + RED-verified pin, per the [H1811 fixlog](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1811/H1811_PIPELINE_REVIEW_FIXLOG_2026-07-29.md) recorded fix shapes):

1. H3 fsync: route checkpoint writes in `headless_worker.py`, `bounded_staged_run.py` (bounded_supervisor), `cohort_engine.py` through `window_common.atomic_write_text`.
2. H4: `coordinator.py` `claim` refuses a duplicate `--lease-id` (mirror `register_prepared_lease`).
3. H5: corrupt/missing `window_status.json` / `audit_window.report.json` become a typed configuration verdict, not `{}`→`'unknown'`.
4. H7: `bounded_staged_run.py` zero-claim drain gets the consecutive-no-progress backstop.
5. H10: `_pilot_collect.py` `OUT` parameterized; hermetic bench writes only under its own tmp root; pin asserts no live sidecar mtime changes.
6. sibling_root sweep: `grep` the sibling-path guess pattern, migrate all 41 modules to `sibling_root.py`, one mechanical commit; full gate battery green proves no path regressed.

## W3 — provenance census + backfill design (Opus 5, 🟡2)

1. Read-only classifier over the store + promotion/campaign ledgers → per-row provenance class (measured / asserted / absent), per-era counts.
2. Dated report `RussianTranslation/reports/PWG_RU_PROVENANCE_CENSUS_<date>.md` + FINDINGS row + GAPS row for whatever is honestly unrecoverable.
3. Backfill SPEC (not execution): field semantics, evidence source per era, ledger format. Execution is out of scope.

## W4 — homonym `h<N>` remap (Opus 5, 🔴3) — after W1

1. Census script: for every mappable store row, derive the true printed homograph column (source-side homograph block reconciliation) vs the stored enumerate index; report confirms/updates the 24.5% figure. **≥2× off → halt rewrite, deliver census (ruling 14).**
2. Fix the assignment at source (fragmentize/assembly path) so new rows carry the true homonym number; RED-pin on a multi-homograph fixture (`vasa`-class).
3. Ledgered store rewrite of affected rows (H3591 pattern) + `pwg-ru-data/tm/` mirror refresh; `audit_store_gates.py` before/after proves delta == ledger, hard flags unchanged.
4. Fold [#1767](https://github.com/gasyoun/SanskritLexicography/issues/1767): census the 161 degraded `key1` rows in the same pass; repair only what is evidence-decidable, ledgered; the rest lands in the report.

## W5 — relation-label revision (Opus 5, 🔴3) — after W1

1. Re-derivation: relation label computed from actual sense attachment, not layer identity; census the 4,132 «пересказ PWG» rows against re-derived truth ([#1736](https://github.com/gasyoun/SanskritLexicography/issues/1736)).
2. Fix the labeling code; RED-pin: a re-glued row whose layer says paraphrase but whose attachment target is absent must not get the paraphrase label.
3. Ledgered rewrite + mirror refresh + gate proof, as W4 step 3.

## W6 — fragmentizer rejoin (Sonnet 5, 🟡2)

1. Census grep over PWG source: gloss pairs separated only by an `<is>`…`</is>` run; count → FINDINGS row (graduates [GAPS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)).
2. `pwg_tm_fragmentize.py`: rejoin such spans into one fragment pre-emission; RED-pin on the `viSveSa` 2 case ({%die%} must not emit standalone).
3. Existing rows untouched; note in the PR how many future fragments the fix affects.

## W7 — perf top-10 (Opus 5, 🟡2) — LAST among parallel units

1. Characterization test for `coordinator.py` claim/audit paths (it is untested at 1.0/10 health) BEFORE any edit.
2. Profile real hot paths (claim, audit, residual ledger, TM ops) on a realistic fixture; rank measured cost.
3. Fix top ~10 confirmed hotspots; each commit carries before/after timing (bytes/4 discipline not needed — wall-clock per operation is enough); behavior-equality proven by the characterization test + gate battery.

## Cross-cutting

- Windows encoding rules (`sys.stdout.reconfigure(encoding='utf-8')`, no BOM, no inline multi-step `python -c`): new scripts follow the org [CLAUDE.md § Windows / encoding](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md).
- Every unit ends: CHANGELOG `[Unreleased]` bullet (dual-changelog namespace rule — use [`Uprava/tools/cut_release.py`](https://github.com/gasyoun/Uprava/blob/main/tools/cut_release.py) only via its union gate), FINDINGS append for reusable gotchas, issue closed with the PR link, `/handoff-close` for its H###.

_Dr. Mārcis Gasūns_
