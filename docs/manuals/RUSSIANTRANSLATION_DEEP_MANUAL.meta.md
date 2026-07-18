# RUSSIANTRANSLATION_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 18-07-2026_

Companion record for [docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) (subsystem deep manual, H606).

## Purpose & audience

The mw_ru post-mortem + pwg_ru production operation in depth: lanes, gates, kill mechanics, promotion, parity, script census. Audience: the operator running/auditing/promoting a translation window.

## Provenance

Authored 11-07-2026 (H606). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 11 findings fixed — the manifest-v2 promotion refusal (H1080 Stage 3, PR #511) now documented at step 8, the H255 footguns marked mechanically guarded, the H818 model-pin closure (SHARED), the split heal pools shipped on master (PR #311), the 53-entry parity census, 142 selftests, 458/62 launch denominators, store 11,603 post-repair, the 252-script census, ~106/244 doc census, and the environment-gated lane status (H1110 NO-GO / H1209 GO). Also gained §13 (multi-account protocol, folded from the root AGENTS sheet) and §14 (session-vs-workflow limits, folded from HUMAN_RU §8).

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 0
```

No pipeline command was executed this pass — every lane is either environment-gated or store-touching (fenced out of a docs-only run). All command shapes, flags, and counts were verified read-only against the scripts' argparse, [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md), [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md), and the subsystem [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md).

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Steps 4–7 still narrate the historical Workflow lane; once a manifest-v2 CLI run has actually landed, rewrite them around `coordinator.py prepare` as primary | open |
| 2 | §10's script census is the fastest-rotting section — consider generating it | open |

## Known limitations

- The store and TM are gitignored; nothing there is verifiable from a bare clone beyond script source.

## Intended use / known misuse

**For:** operating pwg_ru without rediscovering fixed bugs. **Misuse:** running step-4-style Workflow generation for a NEW attempt (the manifest-v2 CLI path is mandatory now), or relaunching medium50 blind (§6 preconditions).

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes; the fastest-decaying numbers carry as-of stamps. H1246 consumes the Verification block.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Subject manual authored (H606) | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); 11 findings fixed; §13/§14 folded in from the root sheets | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
