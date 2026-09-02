_Created: 02-09-2026 · Last updated: 02-09-2026_

# PWG→RU translation process — improvement audit, 02-09-2026

Handoff: [H3864](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3864-Fable_SanskritLexicography_pwg-translation-process-improvement-audit_02.09.26.md).

**Ask:** «Improve PWG translation process in any possible way.» **Executor:** Fable 5.1 (`claude-fable-5-1`), interactive, Medium effort. **Scope:** the PWG→RU pipeline in [RussianTranslation/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) orchestrated by the seven `pwg-*` skills in [gasyoun/claude-config `commands/`](https://github.com/gasyoun/claude-config/tree/main/commands). **Fences held:** zero provider calls, USD 0.00, no store row touched, no promotion, `csl-orig/v02/pwg/pwg.txt` untouched.

## 1. What actually shipped this pass

1. **The German-apparatus gate is now enforced.** [`store_flags.row_metalanguage_ok`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_flags.py) was exported on 16-08-2026 (H2876, PR #1754) and had **no consumer** for 17 days — the 22-08 [FULL_DH_STANDARDS_AUDIT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FULL_DH_STANDARDS_AUDIT_PWG_RU_22-08-2026.md) row R5 recorded that and nobody wired it. `machine_ok` (the machine half of the G5 print-ready predicate) now applies it, so both consumers — [`release_readiness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/release_readiness.py) and [`preflight_remaining_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/preflight_remaining_gates.py) — refuse a row whose DE source is pure apparatus (`eines`, `im Comp. vorangehend`) rendered as an RU gloss. One new test in [`tests/test_store_flags.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_store_flags.py); the mixed-prose case (`Name eines Baumes`) stays print-ready, as the H2876 fence requires. Both consumers are read-only reports, so the change cannot lose data; it can only make the readiness count honest.
2. **Two state docs stopped lying.** [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md) (root) queued the hardening wave H3747–H3754 as «nothing started» and H3714 as «planned, not executed»; [`RussianTranslation/.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) carried the same H3714 line while its own WIP section already recorded Wave 1 as landed. All eight hardening handoffs merged 31-08-2026 (PRs #1997–#2012, releases 1.144.132–1.144.134); H3714 Wave 1 landed via PR #1992 (squash `681c06a4`), verdict PARTIAL. A fresh executor reading the queue would have re-run shipped work.

## 2. Candidates that were already shipped — do not re-propose

Every one of these was on my scouting list; each was verified against code before this doc was written.

| Candidate | Where it already lives | Shipped by |
|---|---|---|
| Live-gate Step 2b paste missing `CLAUDE_CONFIG_DIR` / hard-coded `--timeout` | [`pwg-live-gate.md`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) lines 75–91 set the env var and take `--timeout` only from 2a's printed command | claude-config |
| `v. a.` (vor allem) translated as «действительный залог» | [`pwg_tm_generate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_generate.py) FORMULA_RU `'v. a.': 'особенно'` + assert | H3434, `7df0ee4f`, 24-08-2026 |
| Wave-3 short-gloss denylist extension | [`pwg_tm_wave2_policy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_wave2_policy.py) `SHORT_GLOSS_DENYLIST` (31 census-evidenced tokens) | H3434, PR #1874 |
| Spot-check Sanskrit-loss scan using a literal grep | [`spot_check_daily.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/spot_check_daily.py) `store_san_loss_scan` now calls `markup_fidelity_gates.markup_span_flags` | FINDINGS §589, PR #1902 |
| Nominals worklist singleton output collides between sessions | [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py) `--out` flag + docstring warning | shipped |
| Cost parser rate table stale | [`parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py) carries Sonnet 5 list rates and TTL-priced cache writes | shipped |
| «CI only lints, never runs tests» | [`ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml) runs `pytest tests -q`, `window_selftest.py`, `lang_parity_check.py`, docs_site tests | shipped |
| Headless worker silently ignores a missing config dir | [`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) raises `ValueError('CLAUDE_CONFIG_DIR is required …')` | shipped |

**Lesson:** the PWG estate moves faster than any scouting memory. A proposal without a `file:line` read this session is a re-proposal until proven otherwise.

## 3. The Ultracode attempt — honest record

The first pass ran under Ultracode as a 28-agent workflow (`wf_3aede81c-98c`: understand → design → implement → review). Every agent died on the account session limit («resets 2am Europe/Moscow»); ~654k subagent tokens were spent and **zero files** were written. The script survives at the session's `workflows/scripts/` path and is resumable, but the user moved to Medium, so it was not relaunched. Everything in this doc was produced directly in one interactive pass.

## 4. What remains — ranked by what it unblocks

1. **Human review throughput is the bottleneck, not compute.** The store holds ~11 615 `ai_translated` rows against 3 `approved`. Sheets built and never voted: G6 320-card gold (H2769), 40-card A/B (H2787), 46 reglue cards (H2879–H2881), [h3473 wave-4 sense-fill](https://gasyoun.github.io/vote/sheets/h3473_wave4_sensefill_sheet.html) (the only one confirmed still on the hub), H3658. Every gate downstream — promotion, print-readiness, the H3628 human gate — waits on these. No agent can move this.
2. **H3628's four owed decisions** (RU editorial pass over five authored targets before any promotion; then the three that follow) — [PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md). Projected n=400 clears all three floors; nothing promoted.
3. **Store lineage reconcile before any promote.** Windows live store 11 519+ rows vs Mac mirror 11 462. Until the two are reconciled with a digest, `promote_final_cards.py` must not run on either box. Offline, agent-doable, medium.
4. **H3714 PARTIAL → COMPLETE** needs two human acts: a reviewer other than the implementing agent signs [`docs/evidence/H3714_review_packet.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/evidence/H3714_review_packet.json) (V12), and the two-call canary runs on a box where `XAI_API_KEY`/`DEEPSEEK_API_KEY` are set (V13, ~USD 0.01). Until then no legacy writer may be disabled.
5. **The 23-key rerun and the 38 monsters (~USD 409)** — H3627 made windows resumable; the prepared inputs sit under `src/pilot/output/h3627win/`. This is a spend decision, needs a fresh `/pwg-live-gate` GO receipt, never a hand-asserted one.
6. **DeepSeek key rotation** — the key in `src/.env` has been on disk since before H3714; rotate, never read or echo.

## 5. Human decisions owed (plain sentences)

1. Vote the h3473 sheet on the hub, then say in chat which of the four other built sheets should be republished (they are not on the hub today), so promotion has a signal to act on.
2. Read the five H3628 authored targets for register and reply «принято» or name the ones to redo.
3. Say whether the 38-monster spend (~USD 409) is approved for the next live window, or whether the 23-key rerun alone should go first.

_Dr. Mārcis Gasūns_
