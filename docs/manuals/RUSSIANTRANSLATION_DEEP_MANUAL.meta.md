# RUSSIANTRANSLATION_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 24-07-2026_

Companion record for [docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) (subsystem deep manual, H606).

## Purpose & audience

The mw_ru post-mortem + pwg_ru production operation in depth: lanes, gates, kill mechanics, promotion, parity, script census. Audience: the operator running/auditing/promoting a translation window.

## Provenance

Authored 11-07-2026 (H606). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md). **Headless-first rewrite 24-07-2026 (Grok 4.5):** production loop §5 rewritten around `/pwg-live-gate` → coordinator prepare → headless execute → audit → requeue → promote; §1 status table, §6 lanes, §7/§8 selftest+parity counts, §9 store stamp, §10 script map, §14 session limits; companion editor doc [pwg_ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) flipped from pre-run plan to live production; RUN_FREQ_MAX / AGENTS / README / USE_CASES / PIPELINE_HISTORY / parent CLAUDE.md aligned.

## Verification

```
LAST_VERIFIED: 24-07-2026
VERIFIED_BY: Grok 4.5
COMMANDS_SPOT_RUN: store row count (11,603); lang_parity_check (74 entries no drift); verb_worklist (48 promoted / 701 remaining); window_selftest test_* census (182 defs)
```

Docs-only pass — no paid generation, no store promotion. Counts taken from local gitignored store + script output on this checkout.

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Steps 4–7 still narrate the historical Workflow lane; once a manifest-v2 CLI run has actually landed, rewrite them around `coordinator.py prepare` as primary | **done 24-07-2026** (headless-first §5) |
| 2 | §10's script census is the fastest-rotting section — consider generating it | open |
| 3 | Re-harvest LAUNCH_STATS denominators after headless windows accumulate | open |

## Known limitations

- The store and TM are gitignored; nothing there is verifiable from a bare clone beyond script source.
- Launch ledger / LAUNCH_STATS still reflect the Workflow-era population (458 windows as of last harvest 12-07-2026).

## Intended use / known misuse

**For:** operating pwg_ru without rediscovering fixed bugs. **Misuse:** running Workflow generation for a NEW attempt (the manifest-v2 CLI path is mandatory now), copying canary `--max-agents 1` onto multi-key windows, or relaunching medium50 without a fresh live-gate GO.

## Maintenance & sunset plan

Refreshed by docs truth-passes when the execution route or store denominators move; the fastest-decaying numbers carry as-of stamps.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Subject manual authored (H606) | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); 11 findings fixed; §13/§14 folded in from the root sheets | Fable 5 (`claude-fable-5`) |
| 24-07-2026 | Headless-first rewrite of §5 + live counts; backlog item 1 closed | Grok 4.5 |

_Dr. Mārcis Gasūns_
