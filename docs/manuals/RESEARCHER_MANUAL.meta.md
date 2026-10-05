# RESEARCHER_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 04-10-2026_

Companion record for [docs/manuals/RESEARCHER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md).

## Purpose & audience

The intellectual programme for an external lexicographer / DH researcher / historian of dictionaries: the evidence-graded thesis, the P1–P6 + M01 publication pipeline, citable research objects, the epistemic registries as method. Audience: someone citing or building on the work, not operating it.

## Provenance

Authored 10-07-2026 (H479/H535), consolidated H604. Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 5 fact-check findings fixed (book title/venue/chapter state vs BOOK_PLAN, eight-not-nine registries, §N-citation caveat, ReverseDictionary local-only + rights caveat, grammar-in-prompt attribution).

## Verification

```
LAST_VERIFIED: 04-10-2026
VERIFIED_BY: GLM 5.3 Flash (zai-start-plan/GLM-5.3-Flash), H5991
COMMANDS_SPOT_RUN: 5
```

H5991 (04-10-2026): 8 cited paths exist; §N census re-run (300 unique, max §646 — drift fixed from 231/§577); PWG-layer claims re-checked against [PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) (PW-only 24.0%, no-PWG ~36.8% — both hold); article-comparison + Syntax-Lectures alive; union 323,422 and Sprüche 7,537 re-confirmed in the DATA_REUSE/HEADWORDLISTS passes of the same handoff. Drift fixed: §3 papers pointer rewritten for the same-day sweep (#2385 — manuscripts now private-repo-only, canary left).

H3059 (20-08-2026): read-only count/citation verification pass (union / PWG-layer / particle / literature figures reproduced).

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Add [FEATURES_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) Section VI (Q1–Q30 methods inventory, landed 17-07-2026) as a citable research-object row | open |
| 2 | After the FINDINGS §80/§86/§87 renumber repair, simplify the §5 citation caveat | ✅ done H3059 (20-08-2026) — duplicates gone; caveat kept for §92 downstream-ref risk |

## Known limitations

- Paper readiness scores drift weekly; [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) is canonical.

## Intended use / known misuse

**For:** understanding and citing the programme. **Misuse:** using the P1–P6 table as a live status board (ARTICLES.md is), or citing the reverse-dictionary dataset as fetchable (it is local-only, rights-gated).

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes; venue/scale claims re-checked against BOOK_PLAN + ARTICLES on each pass. H1246 consumes the Verification block.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 04-10-2026 | H5991 manual_staleness refresh (LAST_VERIFIED bump + 5 spot probes; §N census 300/§646; papers pointer rewritten for the #2385 sweep) | GLM 5.3 Flash (zai-start-plan/GLM-5.3-Flash) |
| 20-08-2026 | H3059 manual_staleness fact-check refresh (LAST_VERIFIED bump + real command/count probes) | Grok 4.6 (grok-4.6) |
| 01-08-2026 | H2078 manual_staleness refresh (LAST_VERIFIED bump + spot probes; COMMANDS_SPOT_RUN integer) | Grok 4.5 (grok-4.5) |
| 25-07-2026 | H1623 freshness re-verify (LAST_VERIFIED bump + spot probes) | Grok 4.5 (grok-4.5) |
| 10-07-2026 | Subject manual authored (H479/H535); consolidated H604 11-07-2026 | Fable 5 (`claude-fable-5`) / Opus 4.8 (`claude-opus-4-8`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); subject manual fact-checked by a dedicated agent, all 5 findings fixed same pass | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
