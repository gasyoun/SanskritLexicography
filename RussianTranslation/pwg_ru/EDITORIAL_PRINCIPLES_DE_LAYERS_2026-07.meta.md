# EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md — metadoc

_Created: 25-07-2026 · Last updated: 25-07-2026_

Companion record for
[EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md).

## Purpose & audience

Authority-class datasheet for **German-side** pwg_ru fields after H1624:
derived vs voted vs undecided, with confidence and blockers (G5/G7). Audience:
editors, agents, and DH reviewers who must not invent style policy or rewrite DE.

## Provenance

| Field | Value |
|---|---|
| Handoff | [H1634](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1634-Sonnet_SanskritLexicography_pwg-de-editorial-principles-doc_25.07.26.md) |
| Parent | [H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md) |
| Model | Dual-run: Claude Code PR #737 (G1–G6 core) + Grok 4.5 (`grok-4.5`) PR #738 gap-fill |
| Date | 25-07-2026 |

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Cross-link from pwg_ru.md §8.0 + deep manual §2c | **done** H1634 |
| 2 | form_labels / form_notes rows (H1634 Do list) | **done** dual-run salvage PR #738 |
| 3 | Design fence + G7 blocked table | **done** PR #738 |
| 4 | Fill G5 rows after h1306_style.decisions.json | open (blocked on vote / H1627) |
| 5 | Fill G7 rows after Palsule XLS + H1333 | open |
| 6 | Optional: per-field population % from live store (local-only) | open |
| 7 | Optional: Russian short abstract for editor manual | open |

## Known limitations

- Does not re-measure store population (gitignored store); confidence is
  extractor-class, not live coverage %.
- H180 typology *display names* remain optional; machine subtypes are authoritative
  for `edition_rel` until a vote renames them.
- Conflict rate for G6 is a snapshot from PR #722 era — re-run
  `enrich_portrait_derivation --conflict-rate` before citing as current.

## Related documents

- [pwg_ru.md §8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md)
- [RUSSIANTRANSLATION_DEEP_MANUAL.md §2b–§2c](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
- [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
- [DATA_STATEMENT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/DATA_STATEMENT.md)

## Revision history

| Date | Change |
|---|---|
| 25-07-2026 | Initial H1634 inventory of G1–G6 + form_notes + G5/G7 blockers |

_Dr. Mārcis Gasūns_
