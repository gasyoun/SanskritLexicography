# VERIFICATION — RussianTranslation full-audit improvement

_Created: 23-07-2026 · Last updated: 23-07-2026_

Parent: [PLAN_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md).

## Track acceptance criteria

### Track A+F (must)

| # | Criterion | Proof command / artifact |
|---|---|---|
| A1 | Wall-clock auto-derive when CLI flag omitted | `window_selftest` case; ledger fixture shows `wall_clock_source` |
| A2 | Explicit `--wall-clock-minutes` still wins | unit assertion |
| A3 | stage_boundary or documented emit path exists | test or grep-stable function + one fixture call |
| A4 | Promote refuses intersection with defect keys without `--force` | promote selftest on temp store |
| A5 | Promote allows same with `--force` | same selftest |
| A6 | ready_partial clean-subset helper tested dry | selftest; no live store |
| A7 | `window_selftest` green; `lang_parity_check` no unexpected drift | full run |
| A8 | PR merged | GitHub PR URL in handoff close note |

### Track B (must)

| # | Criterion | Proof |
|---|---|---|
| B1 | Receipt schema v1 load/save round-trip | selftest |
| B2 | reconcile: missing / present / inconsistent cases | three fixtures |
| B3 | No multi-profile live code required | PR diff review — no default route change |
| B4 | `window_selftest` or dedicated selftest green | CI |
| B5 | PR merged | URL |

### Track C (must)

| # | Criterion | Proof |
|---|---|---|
| C1 | Five layer docs + PLAN.meta.md present | paths under `docs/` |
| C2 | ROADMAP_INDEX Tier-1 row | Uprava file |
| C3 | README pointer to PLAN | link resolves |
| C4 | CHANGELOG `[Unreleased]` bullet | file |
| C5 | Full blob URLs, dated header, byline | md hygiene |

### Track D (best-effort)

| # | Criterion | Proof |
|---|---|---|
| D1 | Dry-run default; missing votes → pending status exit 0 | CLI |
| D2 | Synthetic decisions → non-empty delta report | selftest |
| D3 | Cannot write store without explicit env gate | selftest attempting write fails |

### Track E (best-effort)

| # | Criterion | Proof |
|---|---|---|
| E1 | Handoff starter lines point at existing PLANs | handoff file |

## Portfolio done (wave-1)

- [ ] A1–A8
- [ ] B1–B5
- [ ] C1–C5
- [ ] D optional
- [ ] E optional
- [ ] Live store row count unchanged by agent actions (spot-check mtime/size before/after)
- [ ] Zero paid generation in session logs

## Risks & spikes

| Risk | Impact | Mitigation |
|---|---|---|
| H1437 concurrent edit of same files | Track B conflict | Stop condition c; prefer H1437 symbols; park B |
| derived wall-clock overstates gen time | Bad economy metrics | `wall_clock_source` tag; stage_boundary later |
| Defect list path wrong → silent skip | Footgun remains | Log `defect_guard: skipped_no_list`; test discoverable paths |
| ready_partial helper mis-wired to live promote | Store risk | Default dry_run; wave-1 fence; temp-only tests |
| LANG_PARITY dirty CI | Red PR | Update hashes same PR |
| Agent treats H1447 resume as wave-1 | Paid spend | Explicit fence; handoff scope = offline only |

## Non-goals verification (must stay false)

- [ ] No new commits that invoke `headless_worker` production translate
- [ ] No decrease in `pwg_ru_translated.jsonl` size from agent promote
- [ ] No Pages/DOI actions

## Suggested smoke after all must tracks merge

```powershell
cd RussianTranslation
python src\pilot\window_selftest.py
python src\pilot\lang_parity_check.py
python -m py_compile src\promote_final_cards.py src\pilot\window_reports.py
# optional if B landed:
python src\pilot\promotion_receipt_selftest.py
```

_Dr. Mārcis Gasūns_
