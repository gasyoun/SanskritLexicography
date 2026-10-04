# DATA_REUSE_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 04-10-2026_

Companion record for [docs/manuals/DATA_REUSE_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md).

## Purpose & audience

Formats, encodings, traps, and rights for the programmer / data engineer / NLP researcher consuming the committed datasets in scripts.

## Provenance

Authored 10-07-2026 (H479/H535), consolidated H604. Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 5 findings fixed (per-list key2 verdicts, AP 88,867 + recomputed 18-list total, the era-split `wc -l` rule, the RIGHTS_LEDGER lower-bound gate, `helpmorphids.html` un-lumped from the giant-file list).

## Verification

```
LAST_VERIFIED: 04-10-2026
VERIFIED_BY: GLM 5.3 Flash (zai-start-plan/GLM-5.3-Flash), H5991
COMMANDS_SPOT_RUN: 8
```

H5991 (04-10-2026): 22 cited paths exist; era rule re-measured across all 31 then-2014 / 25 now-2026 files (AP 36,030→36,029 = N−1 and 88,867 = N confirm it); CP spine BOM `EF BB BF` + wc-l 61,266 = 61,267−1; headword_index.tsv 98,640 lines − 1 header = 98,639; Sprüche 7,537; mw-apte 202,566 lines; FINDINGS §7/§8/§9/§67 present. Drift fixed: relationships_rollup.tsv is now a **14-row** table summing **6,326** (was 11/6,374); "30 then-2014 files" → 31 (all added 26-06-2026; all no-trailing-newline).

H3059 (20-08-2026): now-2026 25 txt (was 23); BOM still 6; union 323,422 data rows; AP 88,867; headword_index.tsv 98,639 data rows; Indische Sprüche 7,537; relationships_rollup.tsv is an 11-row subtype table summing to 6,374 (not 5,603 per-sense rows).

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md)'s own table carries the 88,869/1,206,384 drift and [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md) mixes pre-/post-fold figures — fix at source, then drop the manual's parentheticals | open (flagged to GTD, H1245) |
| 2 | When the TMX / reverse-dictionary FAIR releases land, rewrite §0 rights framing | open |

## Known limitations

- Counts stamped 18-07-2026; regenerations of `now-2026/` will move them.

## Intended use / known misuse

**For:** writing correct joins/parsers against the committed data on the first try. **Misuse:** redistributing rights-gated material (the RIGHTS_LEDGER lower-bound applies), or trusting filename counts via the wrong-era `wc -l` convention.

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes; H1246 consumes the Verification block.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 04-10-2026 | H5991 manual_staleness refresh (LAST_VERIFIED bump + 8 spot probes; rollup 11→14 rows / 6,374→6,326; then-2014 count 30→31) | GLM 5.3 Flash (zai-start-plan/GLM-5.3-Flash) |
| 20-08-2026 | H3059 manual_staleness fact-check refresh (LAST_VERIFIED bump + real command/count probes) | Grok 4.6 (grok-4.6) |
| 01-08-2026 | H2078 manual_staleness refresh (LAST_VERIFIED bump + spot probes; COMMANDS_SPOT_RUN integer) | Grok 4.5 (grok-4.5) |
| 25-07-2026 | H1623 freshness re-verify (LAST_VERIFIED bump + spot probes) | Grok 4.5 (grok-4.5) |
| 10-07-2026 | Subject manual authored (H479/H535); consolidated H604 11-07-2026 | Fable 5 (`claude-fable-5`) / Opus 4.8 (`claude-opus-4-8`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); subject manual fact-checked by a dedicated agent, all 5 findings fixed same pass | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
