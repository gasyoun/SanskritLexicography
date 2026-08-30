# Verification — Claude Code hardening wave (pwg_ru pipeline)

_Created: 30-08-2026 · Last updated: 30-08-2026_

Acceptance criteria and the exact proof per wave unit, plus the risks & spikes register. Index: [PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md).

## The wave-wide bar (ruling 10)

Every behavioral fix ships a selftest pin **verified RED against pre-fix master** (the run output pasted or linked in the PR body), green after. Store rewrites additionally prove themselves via [`audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_store_gates.py) before/after: changed-row count exactly equals the ledger's row count, hard flags unchanged. A green-only test does not count — that is the [#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803) disease this wave exists to cure.

## Per-unit acceptance

| Unit | Done means | Proof command / flow |
|---|---|---|
| W0 | Epistemic integrity gate green on master tip; no sensitivity loosening | The gate's own run, captured directly (never through a pipe — `$?` after `gate | tail` is tail's exit) |
| W1 | Nine gates emit `GateEvidence` sidecars; a zero-work PASS FAILS; promote claim wraps the whole read-modify-write; G9 RED on the 12,374-duplicate fixture | Per-gate vacuous-PASS RED-pins; H2889 `--ready-partial-report` replay pin; full `window_selftest.py` battery green |
| W2 | H3/H4/H5/H7/H10 each fixed with its pin; 41 modules import `sibling_root.py`, zero sibling-path guesses left | Five RED-verified pins; `grep` count of the guess pattern == 0; full gate battery green |
| W3 | Provenance census report committed; FINDINGS + GAPS rows; backfill spec (no execution) | Census script re-runs reproducibly on master tip; report numbers match |
| W4 | New rows carry true homonym numbers; affected old rows rewritten with ledger; mirror refreshed | Multi-homograph fixture RED-pin; `audit_store_gates.py` delta == ledger; census report; halt-on-≥2× honored |
| W5 | Relation labels derived from attachment; 4,132-row class repaired with ledger | RED-pin (absent-sense target must not label «пересказ»); same store proof as W4 |
| W6 | Census count in FINDINGS (GAPS §18 graduates); fragmentizer rejoins `<is>`-interrupted glosses | `viSveSa`-case RED-pin; census grep reproducible; existing rows byte-identical |
| W7 | Top ~10 measured hotspots fixed; no behavior change | Characterization test green before+after; per-fix before/after wall-clock timings in the PR |

Wave-complete: all eight PRs merged green, all named issues closed with PR links, every H### closed via `/handoff-close`, and one release cut per the dual-changelog union rule.

## Risks & spikes register

1. **#1801 population risk** — the 24.5% figure comes from H2889's mappable-rows sample; the full census may diverge. Mitigated by ruling 14 (≥2× → census-only delivery). No spike needed; the census IS the spike.
2. **Gate retrofit false-RED risk** — an evidence-carrying gate may FAIL on a legitimately-empty input class (e.g. a window with zero requeues). Spike inside W1 step 1: enumerate legitimate-zero cases per gate before flipping `assert_nonvacuous` on; represent them as an explicit `expected_empty` declaration, never silence.
3. **W2/W7 collision** — both touch `coordinator.py`/`bounded_staged_run.py`. Mitigated by ordering (W7 LAST) and one-worktree-per-unit.
4. **Store rewrite irreversibility** — mitigated by the ledger + the `pwg-ru-data` mirror being one commit behind until refresh; the mirror refresh is the last step of W4/W5, never the first.
5. **Untested coordinator** — any W7 edit before its characterization test is a defect; the test is step 1, not an afterthought.
6. **LANG_PARITY silent-revert (3rd-recurrence class, [#1101](https://github.com/gasyoun/SanskritLexicography/issues/1101))** — stale-branch merges can revert verdicts invisibly. Every unit rebases on master tip immediately before merge and re-runs `lang_parity_check`.
7. **Fixture drift** — the H2684 n=400 frozen sample and the h1339 bench signature ([#1184](https://github.com/gasyoun/SanskritLexicography/issues/1184) is open on exactly this) may disagree with CI. Units that hit a pre-existing pinned-signature mismatch report it and proceed on the local proof; they do not "fix" the pin to green.

_Dr. Mārcis Gasūns_
