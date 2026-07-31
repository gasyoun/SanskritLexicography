# PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md — metadoc

_Created: 31-07-2026 · Last updated: 31-07-2026_

## Purpose

The consolidated Russian style guide of record for the pwg_ru lane: every ratified style
rule in one document, each rule citing the handoff / MG vote / merged PR that ruled it.
Deliverable of [H1859](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1859-Fable_SanskritLexicography_pwg-ru-russian-style-guide-of-record_29.07.26.md).

## Audience

Future translation/repair sessions (agents) needing the operative rule set without
re-deriving it from ~10 scattered reports; MG when voting the pending ratification sheets.

## Provenance

Authored 31-07-2026 by Fable 5 (`claude-fable-5`) under H1859. Consolidation only — no
new rules invented; every rule carries a source link. Key sources:
[RU_STYLE_MECHANICAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md),
[ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md),
[STYLE_RESEARCH_DOUBLETS_VL_COMP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md),
[H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md),
the H1302/H1651/H1682/H1702 reports, H858,
[DECISIONS_PWG_RU_QUALITY_BAR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md).

## Design decisions

- **Three-status honesty (✅/🔶/🕓):** the mint assumed the H1303/H1306 votes had landed;
  in fact neither `h1303_abbrev.decisions.json` nor `h1306_style.decisions.json` exists
  (checked 31-07-2026), so per-token abbreviations and the A1/B1/C1 recommendations are
  recorded as 🕓 proposals, NOT silently promoted to rules.
- **Conflicts surfaced, not harmonised:** the 10-07 vs 19-07 abbreviation contradiction
  ([CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) §4)
  and the dead `v. l.` prompt line are recorded with their designated resolution paths.
- **Spine, not a fork:** detail stays in the owning docs; the guide absorbs only what had
  no doc home (the H1651/H1702 `{%…%}` conventions, previously report/code-only).
- **Append-only rule ledger** adopted from DECISIONS_PWG_RU_QUALITY_BAR.md governance.

## Improvement backlog (ranked)

1. After the `h1303_abbrev` v2 vote lands: append the ratified per-token outcome rows
   (§3.5 → ✅), graduate CONTRADICTIONS §4 to a `D##`.
2. After the `h1306_style` vote lands: flip §4/§5.2/§6 to their voted variants.
3. Mint the in-`ls` siglum RU-display handoff promised in RU_STYLE_MECHANICAL.md and
   record its outcome in §8.1.
4. EN-side parity measurement (doublets) per LANG_PARITY once the EN store is accessible.

## Limitations

- Statuses reflect disk/registry state as of 31-07-2026; the vote exports are local-only
  gitignored files, so a landed vote is NOT visible from git history alone.
- H1351/H1437 were checked and contain no style rulings (infra only) — deliberately absent.

## Revision history

| Date | Change | Model |
|---|---|---|
| 31-07-2026 | Created under H1859 | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
