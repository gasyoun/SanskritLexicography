# Speed-audit residues A2/A6 — offline verification (no new design)

_Created: 01-08-2026 · Last updated: 01-08-2026_

**Model:** Grok 4.5 (`grok-4.5`) · offline Sonnet-tier batch  
**Source audit:** [PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md)

## Verdict

| Item | Status on `origin/master` (d759c0b8 + this branch) | Action this pass |
|---|---|---|
| **A2** wall-clock auto-derive + `wall_clock_source` | **SHIPPED** — `window_reports.derive_wall_clock_minutes` / `build_production_metrics`; `audit_window` + `audit_window_en` call it; `dashboard_events.emit_stage_boundary` present | Verify only |
| **A3** promote refuse-defect-keys | **SHIPPED** — `promote_final_cards.refuse_defect_keys` + `discover_defect_keys_path` | Verify only |
| **A6** residual ledger append from defect requeue | **SHIPPED** — `requeue_from_audit` → `no_pwg_residual_ledger.append_from_audit_report` (opt-out `--no-residual`); O(n²) append fixed H1811 | Verify only |
| **A6** C-49 backfill tool | **SHIPPED** — `no_pwg_residual_ledger backfill` | Operator may still run against live ledger when needed |
| Fragment-TM harvest at promote | Already on promotion path (H1339 / journal) | No code this pass |

## Evidence (file pointers)

- [`src/pilot/window_reports.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_reports.py) — `derive_wall_clock_minutes`, `build_production_metrics`
- [`src/pilot/dashboard_events.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/dashboard_events.py) — `emit_stage_boundary`
- [`src/promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) — `refuse_defect_keys`
- [`src/pilot/requeue_from_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) — residual append on `--defect`
- [`src/pilot/no_pwg_residual_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residual_ledger.py) — `append_from_audit_report`, `backfill_documented`

## Residual (not code)

- Live ledger rows still depend on operators running defect requeue (not audit alone) — by design after H1618.
- Width recalibration (ledger #4) still needs **healthy** transport + explicit experiment — blocked until c4 GO.

_Dr. Mārcis Gasūns_
