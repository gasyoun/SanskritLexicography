# PUBLICATION_PIPELINE_DEEP_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 20-07-2026_

Companion record for [docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PUBLICATION_PIPELINE_DEEP_MANUAL.md) (subsystem deep manual, H608).

## Purpose & audience

`papers/` + the M01 book build + `docs_site/` in depth: paper lifecycle and skills, chapter conversion, rights, site build/deploy state. Audience: a session doing paper/book/site work.

## Provenance

Authored 11-07-2026 (H608), touched 14-07 and 18-07 (H740 verdict). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md): 11 findings fixed — the docs-site CI job is real (H733), A30/A31 full drafts merged, chapters 12/14, CITATION.cff exists here and in kosha, the corpus-methods `@DECIDE` closed as ch02 §6, A40 4/5, the papers census + A58 row, H607 shipped, the Zenodo-DOI cross-document conflict flagged (→ [CONTRADICTIONS.md §6](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)), the wiki-drift example marked historical.

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 1
```

Executed 18-07-2026: `pytest docs_site/test_docs_site.py -q` — 4 passed in 3.7 s (with the pinned `zettelkastenwiki` installed).

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | ~~Resolve CONTRADICTIONS §6 (the `10.5281/zenodo.15834721` mint status) with one online Zenodo check, then fix whichever doc is wrong~~ | ✅ done (H1364, 20-07-2026) — BOOK_PLAN was right, false DOI; FAIR_RELEASE_1 + csl-observatory CITATION.cff corrected |
| 2 | Once Ch. 3 / Ch. 11 are written, the §4 tables need the terminal update | open |

## Known limitations

- Paper readiness numbers mirror [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) as of 18-07-2026.

## Intended use / known misuse

**For:** paper/book/site work with the real current state. **Misuse:** scaffolding a paper the registry already carries as drafted (check ARTICLES first — the A30/A31 near-miss this refresh caught).

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes; H1246 consumes the Verification block.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Subject manual authored (H608); H740 verdict spliced 18-07-2026 | Fable 5 (`claude-fable-5`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); 11 findings fixed incl. the DOI-conflict flag | Fable 5 (`claude-fable-5`) |
| 20-07-2026 | DOI conflict ruled false-DOI via live Zenodo check; backlog item 1 closed | Sonnet 5 (`claude-sonnet-5`) |

_Dr. Mārcis Gasūns_
