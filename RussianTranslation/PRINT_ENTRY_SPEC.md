# Printed Bilingual Entry Specification

Date: 2026-06-28

Goal: define the editorial target for a printed Sanskrit-German-Russian PWG
entry before building PDF, LaTeX, HTML, or other renderers. This is a layout
and content contract, not a rendering engine.

## Validated Against Examples

This spec is now checked against real local prototype entries in
[PRINT_ENTRY_EXAMPLES.md](PRINT_ENTRY_EXAMPLES.md): `agni` as a citation-rich
standard headword, `akzara` as a nested homonym/gender/sense case, and `ap` as
a protected/NWS-sensitive homonym split. The examples are layout and QA
evidence only; they are not print-ready publication text until G5/G6/G7/G10
pass.

## Entry Shape

Each printed entry should have this order:

1. **Sanskrit headword**
   - Display `card.key1` / `card.iast`.
   - If present, display homonym marker `record.h`.
   - Keep Sanskrit forms from `{#...#}` visible as Sanskrit/source forms.

2. **Grammar and record header**
   - Display `record.grammar` verbatim where applicable.
   - Do not translate PWG grammar abbreviations such as `m.`, `f.`, `n.`,
     `Pl.`, `Du.`, `adj.`.

3. **Sense block**
   - Preserve PWG printed sense order.
   - For each sense, display:
     - sense tag (`sense.tag`);
     - German PWG source text (`sense.german`);
     - Russian rendering (`sense.russian`);
     - equivalence type (`equivalent` or `explanatory`) when useful for
       editorial QA, not necessarily in main printed text;
     - source type (`attested`, `lexicographic`, `mixed`) as a compact badge or
       apparatus marker;
     - stratum/Renou labels when present.

4. **NWS owner rows**
   - Print each NWS owner row as its own row or indented sub-entry.
   - Preserve the `[NWS: OWNER]` token and owner citation order.
   - Never merge multiple NWS owners into one anonymous sense.

5. **Nachträge and patches**
   - Print addenda/Nachträge as first-class material.
   - Keep patch relation visible: "to sense X add/read/correct...".
   - Never silently fold a patch into the main sense without trace.

6. **Notes and provenance**
   - Print only human-facing notes in the dictionary body.
   - Keep workflow hash, rootmap hash, audit status, and judge status in digital
     edition metadata or apparatus, not as noisy main-entry prose.

## Display Conventions

| source form | print convention |
|---|---|
| `{#...#}` | Sanskrit/source form; keep visible, rendered in the chosen Sanskrit transliteration font. |
| `<ls>...</ls>` | Source citation; print as citation text, with brackets/tags removed by renderer only after validation. |
| `<ab>...</ab>` | PWG abbreviation; print abbreviation verbatim. Expansion may go in abbreviation list, not inline by default. |
| `<is>...</is>` | Italic/source siglum text; keep verbatim and style typographically, never translate as a gloss. |
| `<lex>...</lex>` | Lexical/grammar markup; print content verbatim or as a compact grammar marker. |
| `{%German%}` in German field | German source gloss; Russian field should render its meaning, not necessarily keep braces. |
| `{%Latin/English/binomial%}` | Literal cited foreign gloss; preserve literal form when it appears in Russian field. |
| German abbreviations (`Bed.`, `Schol.`, `s.v.`) | Keep verbatim; define in abbreviation table. |
| Russian gloss | Scholarly Russian; avoid circular Sanskrit-only glosses unless the Sanskrit term is the accepted Russian term. |

## Data Already Present

The current final-card schema already supports the core printed entry:

- `card.key1`
- `card.iast`
- `record.h`
- `record.grammar`
- ordered `record.senses`
- `sense.tag`
- `sense.german`
- `sense.russian`
- `sense.equivalence_type`
- `sense.source_type`
- `sense.stratum`
- `sense.differentia`
- optional `sense.government`
- optional `sense.labels`
- optional Renou fields
- `card.notes`
- `judge` status for digital QA metadata

The portrait schema and rootmap/provenance files provide supporting metadata,
but the printed body should be driven by final-card records after audit and
review.

## Print-Only Decisions Still Needed

These are editorial decisions, not pipeline blockers for continuing translation:

| decision | default recommendation |
|---|---|
| Main entry order | DCS-frequency core tranche for first reviewed slice; full dictionary can later sort by Sanskrit headword. |
| Transliteration | Use the existing IAST/source transliteration consistently; do not mix Devanagari unless a separate design decision is made. |
| Abbreviation expansion | Keep abbreviations in entries; provide a consolidated abbreviation table. |
| Source citations | Keep concise inline citations; reserve long source explanations for front matter or appendix. |
| Audit/provenance markers | Keep in digital apparatus; print only edition-level QA statement unless an entry is exceptional. |
| NWS rows | Print visibly as contributed sub-source rows, not as anonymous merged senses. |
| Nachträge | Mark as addenda/patches, preserving their relation to main senses. |

## Template

```text
HEADWORD [homonym] grammar

1. German PWG sense text with citations.
   RU: Russian rendering.
   [source-type: attested/lexicographic/mixed; stratum/Renou if present]

2. German PWG sense text.
   RU: Russian rendering.

NWS:
   [NWS: OWNER] sub-lemma/tag/gloss -> Russian rendering; owner citation.

Nachträge:
   Add/correct/read under sense N: German source patch -> Russian rendering.

Notes:
   Human-facing note only.
```

## Renderer Requirements

A future renderer must:

- consume only audited/reviewed final-card records for print claims;
- preserve sense order exactly;
- preserve Sanskrit/source/citation tokens until after validation;
- never translate or expand PWG abbreviations silently;
- keep NWS owner rows one-to-one;
- display Nachträge as visible patches;
- fail closed if required fields are missing.

## Non-Goals

- This spec does not generate PDF/LaTeX/HTML.
- This spec does not change schemas or prompts.
- This spec does not make the current dataset print-ready; G5/G6/G7/G10 still
  gate publication.
