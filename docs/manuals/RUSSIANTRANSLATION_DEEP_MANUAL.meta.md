# RUSSIANTRANSLATION_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 24-07-2026_

Companion record for [docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) (subsystem deep manual, H606).

## Purpose & audience

The mw_ru post-mortem + pwg_ru production operation in depth: lanes, gates, kill mechanics, promotion, parity, script census. Audience: the operator running/auditing/promoting a translation window.

## Provenance

Authored 11-07-2026 (H606). Refreshed 18-07-2026 under H1245. Headless-first rewrite 24-07-2026 (Grok 4.5, H1622). **UX pack same day (Grok 4.5):** §0 cold start; §5.0 skill-primary path; §11 symptom cookbook; §10 generated script census via `script_census.py` + committed `SCRIPT_CENSUS.md`; LAUNCH_STATS re-harvest (473 windows); RUN_FREQ_MAX headless worked example A (H1447) primary, `vid` demoted to historical B.

## Verification

```
LAST_VERIFIED: 24-07-2026
VERIFIED_BY: Grok 4.5
COMMANDS_SPOT_RUN: script_census.py (306 files); harvest_launch_stats.py (473 ledger rows); H1447 packet for worked example numbers
```

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Steps 4–7 still narrate Workflow as primary | **done** H1622 |
| 2 | §10 script census generated | **done** 24-07 (script_census.py + SCRIPT_CENSUS.md) |
| 3 | Re-harvest LAUNCH_STATS | **done** 24-07 (473 rows; still mostly Workflow-era date span — re-harvest after headless windows fill ledger) |
| 4 | Cold start + skill-primary + symptom cookbook | **done** 24-07 |
| 5 | Headless worked example in RUN_FREQ_MAX | **done** 24-07 (H1447) |
| 6 | Split mw_ru post-mortem to separate file | open |
| 7 | Bare-clone offline vs store-required matrix | open |
| 8 | EN operator checklist subsection | open |
| 9 | pwg_ru.md sibling metadoc | open |

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
| 11-07-2026 | Subject manual authored (H606) | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245) | Fable 5 (`claude-fable-5`) |
| 24-07-2026 | Headless-first rewrite (H1622) | Grok 4.5 |
| 24-07-2026 | UX pack: cold start, skills, cookbook, census generator, H1447 example | Grok 4.5 |

_Dr. Mārcis Gasūns_
