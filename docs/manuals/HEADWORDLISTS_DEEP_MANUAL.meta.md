# HEADWORDLISTS_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 20-08-2026_

Companion record for [docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/HEADWORDLISTS_DEEP_MANUAL.md) (subsystem deep manual, H607).

## Purpose & audience

Cross-dictionary headword analytics in depth: the then-2014/now-2026 eras, key1/key2, the union, print-readiness, per-file traps. Audience: the analyst or agent working inside `HeadwordLists/`.

## Provenance

Authored 11-07-2026 (H607). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 4 findings fixed (MW 2014 key2 = 575 homonym-index digits, not legacy transliteration; the `corpus_gate.py` pin fixed same-day by H733/PR #357; the FEATURES_INDEX range excludes C15/C17; the second root binary named).

## Verification

```
LAST_VERIFIED: 20-08-2026
VERIFIED_BY: Grok 4.6 (grok-4.6), H3059
COMMANDS_SPOT_RUN: 9
```

H3059 (20-08-2026): now-2026 file count 25 (was 23; PD key1+key2 present); BOM still exactly 6 files; union_headwords.tsv 323,425 data rows; AP-unique-key1-88867.txt line count = 88,867; sanhw1.xlsx 41,221,158 B; heritage gzip 538,102 B; script census 16+5+9=30; `headword_diff.py --help` and `build_union.py --help` exit 0. Earlier 18-07-2026 era `wc -l` / BOM method still holds.

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
| 20-08-2026 | H3059 manual_staleness fact-check refresh (LAST_VERIFIED bump + real command/count probes) | Grok 4.6 (grok-4.6) |
| 01-08-2026 | H2078 manual_staleness refresh (LAST_VERIFIED bump + spot probes; COMMANDS_SPOT_RUN integer) | Grok 4.5 (grok-4.5) |
| 25-07-2026 | H1623 freshness re-verify (LAST_VERIFIED bump + spot probes) | Grok 4.5 (grok-4.5) |
| 11-07-2026 | Subject manual authored (H607) | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); subject manual fact-checked, 4 findings fixed | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
