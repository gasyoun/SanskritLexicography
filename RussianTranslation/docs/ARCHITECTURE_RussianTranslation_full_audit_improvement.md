# ARCHITECTURE — RussianTranslation full-audit improvement (wave-1)

_Created: 23-07-2026 · Last updated: 23-07-2026_

Parent: [PLAN_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md).

## Component map (wave-1 touch surface only)

```
wf_output / execution artifacts
        │
        ▼
audit_window.py  ──► window_reports.py ──► window_ledger.jsonl
   │ auto wall-clock (A2)                    stage_boundary events (A2)
   │ performance_metrics fields
   ▼
requeue keys / judge_sample / status
        │
        ▼
promote_final_cards.py
   │ refuse defect keys without --force (A3)
   │ ready_partial clean-subset helper (A3)
   │ ── dry-run / fixtures only in wave-1 ──
   ▼
[fenced] pwg_ru_translated.jsonl

NEW (Track B, pure + tests):
  promotion_receipt.py (or under pilot/)
    · AttemptRunBinding
    · PromotionReceipt
    · reconcile_startup(receipts, store_snapshot) → actions
  fixtures under src/pilot/fixtures/cohort_scaffold/
```

## Build-vs-reuse (prior-art)

| Piece | Verdict | Evidence |
|---|---|---|
| Wall-clock on ledger | **Extend** `audit_window.py` / `window_reports.py` | Flags already exist (`--wall-clock-minutes`); H1403/H390: only 12/458 rows filled — auto-derive missing |
| stage_boundary | **Extend** `dashboard_events.py` if present; else minimal emit in audit path | H1403 A2; avoid new event bus |
| Promote defect refuse | **Extend** `promote_final_cards.py` | Footgun H255_NO_PWG_W02 in LAUNCH_FUCKUPS; `--force` already exists for store-shrink |
| ready_partial promote | **Extend** coordinator / promote path helpers already aware of `ready_partial` | `coordinator.py` states; automate clean-subset path mandated by runbook |
| Cohort binding/receipt | **New thin module + tests**; do **not** implement H1437 scheduler | H1437 claimed for multi-profile; Track B = P0 data shapes only |
| Quality apply | **New small CLI** reusing sheet `decisions.json` schema from csl-pyutil / review sheets | No store write |
| Umbrella docs | **New** under `docs/`; link existing PLANs | R2.5 |
| TM/gloss | **Reuse** existing PLAN docs only | R3.5 |

## Data contracts

### A2 — performance_metrics (ledger row)

When CLI omits economy flags, derive:

| Field | Derivation (default) |
|---|---|
| `wall_clock_minutes` | Prefer explicit flag; else `mtime(wf_output) - parse(meta.generated_at)` if both exist; else `null` + `wall_clock_source: "unavailable"` |
| `wall_clock_source` | `"cli"` \| `"derived_mtime"` \| `"unavailable"` |
| `gen_model` | Already from `workflow_meta.gen_model` if stamped |

**Default on ambiguity:** never invent tokens; null + source tag beats a wrong number (H1403 caveat: generated_at→mtime conflates operator idle — document in status note; stage_boundary later separates).

### A3 — promote defect refusal

| Input | Behavior |
|---|---|
| Keys present in current `requeue.keys.txt` / `.defect` for the same root/window (or explicit `--defect-keys` file) | **Refuse** promote of those keys unless `--force` |
| Clean keys only | Promote as today |
| No defect list available | Proceed (default); log `defect_guard: skipped_no_list` |

**Default:** fail closed only when a defect list is discoverable for the window being promoted.

### B — PromotionReceipt (minimal schema)

```json
{
  "schema": "pwg_ru.promotion_receipt.v1",
  "run_id": "string",
  "attempt_id": "string",
  "lease_id": "string",
  "keys_accepted": ["..."],
  "keys_rejected": ["..."],
  "store_path": "relative-or-fixture",
  "row_count_before": 0,
  "row_count_after": 0,
  "tm_rebuild": false,
  "created_at": "ISO-8601"
}
```

`reconcile_startup(receipts, observed_store_keys) → {promote_missing, skip_already_present, error_inconsistent}` pure function; fixture-tested.

## Interfaces with H1437

- Track B **must not** change default live routing or multi-profile admission.
- If H1437 worktree already added the same module names, **adapt to H1437's names** (default: prefer existing H1437 symbols) rather than dual systems.
- Track B PR may land before H1437 finishes; H1437 rebases and consumes.

## LANG_PARITY

Any SHARED edit to promote/audit surfaces used by EN: update
[LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
entry + `verified_sha256` via the repo's existing check script.

## Out of architecture (wave-1)

Multi-profile barrier scheduler, Message Batches API, COMET-QE, live drain, review-sheet HTML regeneration.

_Dr. Mārcis Gasūns_
