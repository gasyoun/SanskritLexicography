# IMPLEMENTATION — RussianTranslation full-audit improvement (wave-1)

_Created: 23-07-2026 · Last updated: 23-07-2026_

Parent: [PLAN_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md).

Execute **one track handoff at a time** (or parallel handoffs in separate worktrees).
Order for a single agent doing the must set: **C (if docs not already on master) → A → B → D → E**.

Working directory for all steps:
`C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation`
(via worktree checkout of the monorepo root).

---

## Track C — umbrella docs (often already landed by the `/ask` authoring session)

1. Confirm these files exist under `RussianTranslation/docs/`:
   - `PLAN_RussianTranslation_full_audit_improvement_2026H2.md` (+ `.meta.md`)
   - `ROADMAP_…`, `ARCHITECTURE_…`, `IMPLEMENTATION_…`, `VERIFICATION_…`
2. Add a row to [Uprava/ROADMAP_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/ROADMAP_INDEX.md) Tier-1 RussianTranslation table pointing at the ROADMAP.
3. Add a short “Improvement programme” pointer near the top of
   [RussianTranslation/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md)
   Operating / Milestones section → full blob URL to the PLAN.
4. Append `[Unreleased]` CHANGELOG bullet for the plan set.
5. Point `.ai_state.md` Next Steps at the PLAN + track handoffs.

**Files:** docs/* listed · README.md · CHANGELOG.md · `.ai_state.md` · Uprava ROADMAP_INDEX.md

---

## Track A+F — H1403 A2+A3 (must)

### A2 — instrumentation

1. Read `src/pilot/audit_window.py` CLI block (~429+) and `window_reports.py` ledger writer.
2. Implement `derive_wall_clock_minutes(wf_path, meta, cli_value) -> (minutes|None, source)` in
   `window_reports.py` (or a tiny helper in the same module — no new package).
3. When `args.wall_clock_minutes` is None, call derive; stamp `performance_metrics` /
   ledger fields with `wall_clock_source`.
4. Emit one `stage_boundary` dashboard event at audit start and audit end if
   `dashboard_events.py` already has an emit API; if not, add a minimal
   `emit_stage_boundary(stage, window_tag, ts)` append-only JSONL under
   `src/pilot/output/` (gitignored path) — do not invent a server.
5. Pin tests in `window_selftest.py`:
   - explicit CLI wins over derive
   - derive from fixture mtimes
   - unavailable → null + source tag (no crash)

### A3 — promote defect refusal

1. Read `src/promote_final_cards.py` argparse (`--force` ~970) and merge path.
2. Add discovery of defect keys: optional `--defect-keys PATH`; else if
   `src/pilot/output/requeue.keys.defect` or sibling `.defect` exists for the
   invoked context, load it.
3. Before merge, intersect incoming keys with defect set; if any overlap and not
   `--force`, exit non-zero with a clear list (no store write).
4. Selftest: temp store + temp defect list → refuse; with `--force` → allow
   (still use temp store only).

### A3 — ready_partial helper

1. Add `promote_ready_partial_clean(lease_or_report, *, dry_run=True)` either as
   a function in `promote_final_cards.py` or `coordinator.py` **called only from
   CLI with default dry_run=True**.
2. Behavior: given an audit report JSON marking clean vs pending keys, promote
   **only** clean keys into a **fixture store** in tests; production CLI requires
   explicit `--apply` (still fenced in wave-1 handoff: document but tests use temp).
3. Default for wave-1 agent: implement + test; do not run `--apply` on live store.

### LANG_PARITY

1. If SHARED with EN (`promote_en` path or shared report fields), update
   `LANG_PARITY.md` and re-hash via `lang_parity_check.py`.

### Verify A

```powershell
python -m py_compile src\pilot\audit_window.py src\pilot\window_reports.py src\promote_final_cards.py
python src\pilot\window_selftest.py
python src\pilot\lang_parity_check.py
```

---

## Track B — cohort / promotion ledger scaffold (must)

**Do not implement the multi-profile scheduler.** Align names with H1437 if that
branch already landed symbols on master.

1. Add `src/pilot/promotion_receipt.py` (or H1437's chosen path if present):
   - dataclasses / TypedDict for binding + receipt
   - `write_receipt(path, receipt)`, `load_receipts(dir)`
   - `reconcile_startup(receipts, store_keys) -> ReconcilePlan`
2. Fixtures under `src/pilot/fixtures/cohort_scaffold/`:
   - serial accept
   - crash after receipt before store (promote_missing)
   - double receipt same keys (skip_already_present)
   - inconsistent row counts (error)
3. `promotion_receipt_selftest.py` or block inside `window_selftest.py`.
4. Optional: document field list in ARCHITECTURE (already) — no coordinator wiring
   required for wave-1 complete.

### Verify B

```powershell
python src\pilot\promotion_receipt_selftest.py
# or the window_selftest block name documented in the PR
python src\pilot\window_selftest.py
```

**If H1437 worktree conflicts:** stop Track B code; leave a Dev Note; do not
overwrite H1437 in-flight files (autonomy stop condition c).

---

## Track D — quality apply dry-run (best-effort)

1. New `src/pilot/apply_editorial_decisions.py` (name OK to adjust):
   - `--abbrev-decisions pwg_ru/eval/h1303_abbrev.decisions.json`
   - `--style-decisions pwg_ru/eval/h1306_style.decisions.json`
   - `--store` default to canonical store path helper **read-only**
   - `--dry-run` default True; **refuse** if dry-run false unless env
     `PWG_RU_ALLOW_EDITORIAL_APPLY=1` (wave-1 never sets this)
2. Output: JSON + markdown delta counts (tokens that would change, sample keys).
3. If decisions files missing: exit 0 with `status: pending_votes` (not a failure).
4. Selftest with synthetic decisions + 2–3 fixture store rows in temp dir.

---

## Track E — thin pointers (best-effort, complete when handoff body is filled)

Handoff body contains only:

```
Read <PLAN_pubgrade_tm> and execute its wave-1 track A offline scope.
Read <PLAN_saru_gloss> and execute remaining waves per that plan's autonomy contract.
```

No new code required for E to be “done”.

---

## PR / git sequence (each track)

1. `git fetch origin`
2. `git worktree add … -b h<id>-<slug> origin/master`
3. Implement + tests
4. Commit (complete sentences)
5. Push + `gh pr create` + enable auto-merge if green
6. Remove worktree after merge

Never commit in the shared `SanskritLexicography` main checkout.

_Dr. Mārcis Gasūns_
