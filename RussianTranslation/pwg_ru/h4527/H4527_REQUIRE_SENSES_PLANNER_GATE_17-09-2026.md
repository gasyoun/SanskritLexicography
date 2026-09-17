_Created: 17-09-2026 · Last updated: 17-09-2026_

# H4527 — `--require-senses`: the planner gate that keeps a paid acceptance window off a card with no repair lane

**Pass:** 17-09-2026, Opus 5 (`claude-opus-5`), unattended worker on the Mac · **0 paid calls** · ~45 min.
**Scope:** the 17-09 census's own recommended step 1, landed offline. Nothing live was attempted this pass and no ration attempt was spent.

## What this closes

The [16-09 live window](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_LIVE_COHORT_WINDOW_FIRST_RUN_16-09-2026.md) ran the cohort path end to end and came back with a **null card**. The [offline diagnosis](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_NULL_CARD_OFFLINE_DIAGNOSIS_16-09-2026.md) found the window had `max_heal_agents: 0` — `agent_budget` derives the self-heal pool from a card's **sense groups**, and the acceptance subject `asa_mskfta~~h0_zz_nws00` declares none. The [census](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_SENSE_ELIGIBILITY_CENSUS_17-09-2026.md) then showed the zero is structural for the whole `~~h0_zz_nws00` class (0 of 10 declare a sense), and that no existing planner flag can steer a window onto a sense-bearing card: `--start-index` only labels, `--headwords` truncates from the front, `--include-residuals` unblocks every residual at once.

So the planner could not prepare the acceptance window the handoff asks for. It can now.

## The contract

`python src/pilot/no_pwg_scale_plan.py … --require-senses N`

1. **Default 0 = off.** The historical planning path is unchanged, and a caller that does not pass the flag never reaches the gate (`prepare_window` reads it through `getattr`, so an older `args` object is still valid).
2. **Sub-card level, not head level.** Only sub-cards proving `N`+ top-level source senses are prepared; a head whose eligible sub-cards are all sense-poor is **omitted** exactly as a fully-blocked head is, and the omission does **not** consume the `--limit-windows` quota — the planner walks on to the next head.
3. **Two readings of the count, in census order.** The portrait sidecar's stamped `source_senses` first; failing that, a deterministic recount of the raw sidecar through `sense_count.count_source_senses` (line-opening top-level ordinals only). The census cross-checked both over all 34 portraits on disk and they agree everywhere a portrait exists.
4. **Unprovable is never zero, and never admitted.** `subcard_source_senses` returns `None` when neither sidecar is on disk; the gate skips such a key. The flag's only job is to *prove* a repair lane before a call is paid for, so an unproven card fails closed.
5. **No registry write, no backlog semantics.** A sense-skipped key gets **no** `pwg.no_pwg_residual.v1` row — it is not blocked, merely not chosen now, and the next planning run sees it unchanged.
6. **The manifest records the gate.** `require_senses` and a flat `sense_skipped` list (key, measured count, reason) land in the plan payload, and each window carries its own `sense_skipped`, so a prepared window's size is auditable after the fact.
7. **Timing is deliberate.** The gate runs **after** `_pilot_gen_merged.py`, because only the sidecars generation writes say how many senses a sub-card declares. Generation is local and unpaid; the call that would follow is not.
8. `--require-senses -1` is refused by name; `--plan-only` prepares nothing, so the flag is inert there.

## Checks (actual output, this box, Python 3.9.6)

| Check | Result |
|---|---|
| `python src/pilot/window_selftest.py` | 226 defined, 160 passed — **failure set byte-identical to pristine `origin/master`** on the same box (66 pre-existing, environment-bound: this Mac has no Node harness and Python 3.9). New pin `test_no_pwg_require_senses_gate` **PASS**. |
| `python src/pilot/windows100_selftest.py` | PASS |
| `python src/pilot/cohort_engine_selftest.py` | PASS (10 pins) |
| `python src/pilot/cohort_live_admission_selftest.py` | 6 pins PASS |
| `python src/pilot/cohort_live_dispatch_selftest.py` | 6 pins PASS |
| `python src/pilot/bounded_staged_run_selftest.py` | PASS |
| `python src/pilot/lang_parity_check.py` | 117 entries, all verdicts complete, **no drift**; 38 language-aware files tracked or exempt |
| `python src/pilot/h809_selftest.py` | fails identically on pristine `master` — `int \| None` under Python 3.9 on this box, pre-existing, not this pass |

Baseline discipline: the `window_selftest` failure sets were captured on this branch and on the pristine main checkout and diffed — identical.

## LANG_PARITY

42 entries drifted on the two touched files and were re-derived through `src/pilot/h4527c_parity_restamp.py` (same class as the `h4527_`/`h4527b_` receipts, mechanics in `parity_restamp.restamp_receipt`). Every verdict stands: both readings of the sense count describe the **German source entry**, before any target field exists, and the new path has no `lang` parameter and no RU/EN branch — a Russian and an English drain admit the identical sub-cards. New entry `no_pwg_sense_gate_h4527`, verdict **SHARED**.

## What this does NOT do

- It does **not** run a live window, buy a canary, or spend a probe attempt. Work item 1's acceptance window stays unrun.
- It does **not** unpark lease `h4527acc05`, touch `no_pwg_residuals.jsonl`, or change what the lane considers blocked.
- It does **not** make `darvI` a one-call window by itself — it makes one *possible*: with `--require-senses 1` the planner admits `darv_i~~h0_zz_pw` (3 senses) and skips its zero-sense `nws00` sibling, so the prepared window is one sub-card and one paid call.
- It does **not** touch work item 3 (width 2), which stays parked on the one-lane condition of the 11-09 MG ruling.

## Ordered next step

1. `python src/pilot/max_account_orchestrator.py --db src/pilot/max_orchestrator.sqlite probe-ration --account c1` — exit 0 means the UTC-day ration is open (the 16-09 refusal named `next_legal_utc 2026-09-17T00:00:00Z`, so it should be).
2. Prepare the acceptance lease with the new gate, on MSI, from `RussianTranslation`:
   `python src/pilot/no_pwg_scale_plan.py --window-size 1 --limit-windows 1 --require-senses 1 --headless --profile-slot c1 --config-dir <c1 config dir> --prefix h4527acc` — verify the prepared window is **one** sub-card before going further, and keep `h4527acc05` parked.
3. Buy a fresh `dq_canary_puregloss` GO receipt (one paid call, no probe attempt), then run the corrected `--execute --cohort-path --cohort-width 1` command of the [16-09 (2) packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_LIVE_COHORT_WINDOW_FIRST_RUN_16-09-2026.md) — it carries `--coordinator`, `--cwd` as a bare scratch dir and `--events` — pointed at the new lease.
4. If a card **with** senses also returns `missing-or-mismatched-key`, the class is harness-wide: retention (logging the raw `cards[]` on the null path) comes before any further paid call.
5. Work item 2 (Codex sign-off) and the money-class `## Verifier` PASS each still need a different session.

_Гасунс_
