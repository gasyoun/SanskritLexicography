# DATA_REUSE_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 18-07-2026_

Companion record for [docs/manuals/DATA_REUSE_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md).

## Purpose & audience

Formats, encodings, traps, and rights for the programmer / data engineer / NLP researcher consuming the committed datasets in scripts.

## Provenance

Authored 10-07-2026 (H479/H535), consolidated H604. Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 5 findings fixed (per-list key2 verdicts, AP 88,867 + recomputed 18-list total, the era-split `wc -l` rule, the RIGHTS_LEDGER lower-bound gate, `helpmorphids.html` un-lumped from the giant-file list).

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 3
```

Executed 18-07-2026 by the fact-check pass: the full era-wide `wc -l` sweep (all 53 list files), `head -c 3 | xxd` BOM checks on the named pairs, and the digit-key measurements behind the key2 verdicts.

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
| 10-07-2026 | Subject manual authored (H479/H535); consolidated H604 11-07-2026 | Fable 5 (`claude-fable-5`) / Opus 4.8 (`claude-opus-4-8`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); subject manual fact-checked by a dedicated agent, all 5 findings fixed same pass | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
