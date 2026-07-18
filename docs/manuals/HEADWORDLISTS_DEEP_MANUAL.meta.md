# HEADWORDLISTS_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 18-07-2026_

Companion record for [docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md) (subsystem deep manual, H607).

## Purpose & audience

Cross-dictionary headword analytics in depth: the then-2014/now-2026 eras, key1/key2, the union, print-readiness, per-file traps. Audience: the analyst or agent working inside `HeadwordLists/`.

## Provenance

Authored 11-07-2026 (H607). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 4 findings fixed (MW 2014 key2 = 575 homonym-index digits, not legacy transliteration; the `corpus_gate.py` pin fixed same-day by H733/PR #357; the FEATURES_INDEX range excludes C15/C17; the second root binary named).

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 3
```

Executed 18-07-2026 by the fact-check pass: a 10-file `wc -l` sweep (era invariant confirmed), the 6-file BOM census via `head -c 3 | xxd`, and giant-file `ls -la` size checks. Union / heritage / works-catalogue counts recomputed from the shipped TSVs.

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) table drift (88,869 vs 88,867) + [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md) pre-/post-fold mix — fix at source | open (flagged to GTD, H1245) |
| 2 | The AP +146.6/.7% cross-doc divergence note resolves itself once item 1 lands | open |

## Known limitations

- The manual verifies the SHIPPED files; a `now-2026/` regeneration shifts counts and needs a same-PR manual touch.

## Intended use / known misuse

**For:** correct reuse and auditing of the list files. **Misuse:** citing NOW_VS_THEN's table figures over the shipped files (the manual documents the divergence).

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes; H1246 consumes the Verification block.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Subject manual authored (H607) | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); subject manual fact-checked, 4 findings fixed | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
