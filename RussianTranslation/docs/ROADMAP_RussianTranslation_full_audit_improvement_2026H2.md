# ROADMAP — RussianTranslation full-audit improvement programme (2026 H2)

_Created: 23-07-2026 · Last updated: 23-07-2026_

Parent index: [PLAN_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md).

## Wave 1 — offline factory + umbrella (must, ≥8 h portfolio)

Unblocks safe, measured operation and a single navigation hub. **No paid gen, no store write.**

| Track | Deliverable | Unblocks | Effort |
|---|---|---|---|
| **A+F** | H1403 A2+A3 residues: auto wall-clock + stage_boundary; promote refuse defect keys without `--force`; `ready_partial` clean-subset promote helper; LANG_PARITY update if SHARED | Closed-loop economy; removes promote-then-revert footgun | ~3–4 h |
| **B** | Attempt/result/run binding + promotion receipt + reconcile pure functions + fixture selftests (no multi-profile live) | H1437 Phase-0 prerequisites; crash-safe promote accounting | ~2–3 h |
| **C** | This five-layer plan + metadoc + ROADMAP_INDEX + README pointer + stale-audit map | Cold-start; one handoff per later programme | ~1–2 h (authoring session) |

**Must-complete success:** each of A, B, C has a merged PR (or C lands with the plan PR) and green tests per [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_full_audit_improvement.md).

### Wave 1 best-effort

| Track | Deliverable | If incomplete |
|---|---|---|
| **D** | `apply_style_abbrev_decisions.py` (name flexible) dry-run CLI over H1303/H1306 `decisions.json` → delta report; never writes store | Handoff remains queued; zero partial store risk |
| **E** | Thin handoff bodies whose starter lines point at pubgrade TM + Sa→Ru gloss PLANs | Pointer-only is complete |

## Wave 2 — live drain (after wave-1 + fresh health GO)

| Step | Deliverable | Gate |
|---|---|---|
| 2.0 | Fresh c4 (or chosen profile) health PASS via `/pwg-live-gate` Step 1 | Stale GO (incl. H1447's) never authorizes spend |
| 2.1 | Resume H1447 medium50 plan (regenerate claims if worktree state gone) | `--stop-before-promote` |
| 2.2 | `/pwg-window-close` path for clean windows; requeue defect/transient | Track A refuse-defect on any accidental promote |
| 2.3 | Serial frequency / nominal drain per [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) | ≤3-wide global; single promoter |

**Non-goals for wave-2:** multi-profile live (that's H1437 after scaffold); monster kAla-class without explicit human budget.

## Wave 3 — research + editorial (parallel after or alongside late wave-2)

| Programme | Source of truth | Notes |
|---|---|---|
| Pubgrade TM + oral | [PLAN_…_pubgrade_tm_oral…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md) | Tracks A/B/C as already ruled; nothing auto-publishes |
| Sa→Ru gloss W3–W4 | [PLAN_…_saru-gloss…](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md) | No published-data rewrite without human GO |
| Editorial apply | Track D machinery + MG votes on H1303/H1306/h178/Renou/H180 | Apply only after `decisions.json` present |
| Cohort multi-profile | [H1437](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1437-Fable_RussianTranslation_bounded-wave-barrier-promotion-ledger_21.07.26.md) | **Phase 0 GREEN offline** via H1618 (`cohort_engine.py` 7/7 pins + admitted-fleet parked guard). Live CLI width>1 still H1437 Phases 2–3 |

## Stale-audit map (cold-start filter)

Treat as **history / evidence**, not live queue:

| Doc | Role today |
|---|---|
| [STRATEGY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/STRATEGY.md) | Historical strategy; concurrency numbers pre-headless |
| [REVIEW_AND_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md) | Jun 2026 corpus-first narrative; frequency pivot still valid |
| [ARCHITECTURE_AUDIT_2026-07-02.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ARCHITECTURE_AUDIT_2026-07-02.md) | S10 failure modes — mostly closed |
| [SCALE_READINESS_CENSUS_2026-07-12.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/SCALE_READINESS_CENSUS_2026-07-12.md) | Point-in-time; API state changes daily |
| [PWG_RU_SPEED_…_2026-07-20.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md) | Action map still load-bearing for Track A |
| [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md) | H335; government etc. largely landed |

**Live truth order:** [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md) → this PLAN → `src/pilot/RUN_FREQ_MAX.md` → `window_status.json` / coordinator state.

## Explicit non-goals (whole programme unless a later interview re-opens)

- Rebuilding Max-Workflow as the production route
- Greenfield orchestration daemon
- Anthropic Message Batches integration in wave-1 (probe is wave-2+ research, optional)
- mw_ru re-translation
- EN bulk scale-up (LANG_PARITY mechanical only)
- Agent-cast votes on review sheets
- csl-orig corrections
- Auto-publish of TM / store text

## Human `@DO` (not agent wave-1)

- Vote H1303 abbrev sheet, H1306 style sheet, h178 residual, Renou v2, H180×3
- Fresh health only when intending wave-2 spend
- Optional: authenticate c5/c6 (not required for serial-c4)

_Dr. Mārcis Gasūns_
