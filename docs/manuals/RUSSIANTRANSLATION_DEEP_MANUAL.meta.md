# RUSSIANTRANSLATION_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 20-08-2026_

Companion record for [docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) (subsystem deep manual, H606).

## Purpose & audience

The mw_ru post-mortem + pwg_ru production operation in depth: lanes, gates, kill mechanics, promotion, parity, script census. Audience: the operator running/auditing/promoting a translation window.

## Provenance

Authored 11-07-2026 (H606). Refreshed 18-07-2026 under H1245. Headless-first rewrite 24-07-2026 (Grok 4.5, H1622). **UX pack same day (Grok 4.5):** §0 cold start; §5.0 skill-primary path; §11 symptom cookbook; §10 generated script census via `script_census.py` + committed `SCRIPT_CENSUS.md`; LAUNCH_STATS re-harvest (473 windows); RUN_FREQ_MAX headless worked example A (H1447) primary, `vid` demoted to historical B.

## Verification

```
LAST_VERIFIED: 20-08-2026
VERIFIED_BY: Grok 4.6 (grok-4.6), H3059
COMMANDS_SPOT_RUN: 6
```

H3059 (20-08-2026): `probe_log.py --help`, `preflight_remaining_gates.py --help`, `nominal_grammar.py --help`, `reverse_index.py --help`, plus the four review selftests used by the sibling review manual. Store file absent in this worktree (gitignored) — 11,603 remains the 24-07-2026 dated figure. Headless/manifest-v2 §0 still matches RUN_FREQ_MAX.

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Steps 4–7 still narrate Workflow as primary | **done** H1622; **re-verified closed** H2071 (01-08-2026) |
| 2 | §10 script census generated | **done** 24-07 (script_census.py + SCRIPT_CENSUS.md) |
| 3 | Re-harvest LAUNCH_STATS | **done** 24-07 (473 rows; still mostly Workflow-era date span — re-harvest after headless windows fill ledger) |
| 4 | Cold start + skill-primary + symptom cookbook | **done** 24-07 |
| 5 | Headless worked example in RUN_FREQ_MAX | **done** 24-07 (H1447) |
| 6 | Split mw_ru post-mortem to separate file | open |
| 7 | Bare-clone offline vs store-required matrix | open |
| 8 | EN operator checklist subsection | open |
| 9 | pwg_ru.md sibling metadoc | open |
| 10 | Capability Q/N matrix (layers → questions) | **done** 25-07 — pwg_ru.md §8 + deep manual §2b |
| 11 | Link DE editorial principles datasheet (H1634) | **done** 25-07 — §2c + cold-start table → EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md |
| 12 | Document web kitchen 60 s vs local ops 5 s + interlink both UIs | **done** 31-07 — §2d + progress_dashboard dual banner + local dashboard dual banner |

## Known limitations

- The store and TM are gitignored; nothing there is verifiable from a bare clone beyond script source.
- LAUNCH_STATS date span still ends 2026-07-15 — headless production windows may not yet dominate the local ledger.

## Intended use / known misuse

**For:** operating pwg_ru without rediscovering fixed bugs. **Misuse:** Workflow generation for NEW attempts; canary `--max-agents 1` on multi-key windows; medium50 without fresh live-gate GO.

## Maintenance & sunset plan

Re-run `script_census.py` and `harvest_launch_stats.py` when the pipeline tree or launch population moves; bump §0 counts from command output.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 20-08-2026 | H3059 manual_staleness fact-check refresh (LAST_VERIFIED bump + real command/count probes) | Grok 4.6 (grok-4.6) |
| 01-08-2026 | H2078 manual_staleness refresh (LAST_VERIFIED bump + spot probes; COMMANDS_SPOT_RUN integer) | Grok 4.5 (grok-4.5) |
| 31-07-2026 | §2d: autostart residual + human `@DO` for logged-off stored credentials; links windows/README inventory | Grok 4.5 (grok-4.5) |
| 31-07-2026 | §2d dual dashboards (local 5 s · web 60 s) + doc map row; interlinked with progress_dashboard + dashboard_server UIs (H2032 follow-up) | Grok 4.5 (grok-4.5) |
| 25-07-2026 | H1623 freshness re-verify (LAST_VERIFIED bump + spot probes) | Grok 4.5 (grok-4.5) |
| 11-07-2026 | Subject manual authored (H606) | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245) | Fable 5 (`claude-fable-5`) |
| 24-07-2026 | Headless-first rewrite (H1622) | Grok 4.5 |
| 24-07-2026 | UX pack: cold start, skills, cookbook, census generator, H1447 example | Grok 4.5 |

_Dr. Mārcis Gasūns_
