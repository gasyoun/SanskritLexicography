# PWG card anatomy — index + measured crosswalk

_Created: 20-07-2026 · Last updated: 20-07-2026_

Part of the [PWG data-layers wave](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md)
(H1350, step W1.1). Three independent descriptions of a PWG record's anatomy
already exist in this repo — this doc does not replace any of them, it
crosswalks them:

- **Pedagogical** — [`EntryAnatomy/pwg-entry-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/pwg-entry-anatomy.html)
  ([PDF](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/pwg-entry-anatomy.pdf)),
  24 labelled callouts on a real re-typeset entry, aimed at a human reader
  meeting PWG's conventions for the first time.
- **Machine-measured** — [`csl-atlas/data/parse-rules/pwg.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/parse-rules/pwg.json),
  every markup tag in `v02/pwg/pwg.txt` with an occurrence count and a
  measured parse-adequacy rating (`clean` / `partial` / `lossy` / unmapped).
- **Working parser** — [`RussianTranslation/src/microstructure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py),
  which turns a flat record into an Apresjan-style lexicographic portrait
  (homonym card → grammar/diasystem → numbered sense tree), validated by
  [`schemas/pwg_ru_lexicographic_portrait.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json).

The crosswalk below is generated, not hand-maintained — regenerate with
[`RussianTranslation/src/build_anatomy_crosswalk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_anatomy_crosswalk.py)
(`--check` asserts every census tag is accounted for; it exits non-zero
otherwise). It reads the existing measured census — it does **not** re-parse
`pwg.txt`.

## How to read the table

- **Tag / Count / Adequacy** — straight from the machine census.
- **Pedagogical element(s)** — which of the 24 callouts on the specimen page
  point at this tag (a tag can anchor several callouts; a callout can have no
  dedicated tag — see the prose list below the table).
- **Portrait field** — where this tag's content resurfaces in
  `microstructure.py`'s output, if it does.
- **Divergence note** — why a cell is thin: lossy/partial parse, or content
  present in the source but not yet surfaced by the portrait stage.

## Coverage matrix

```
python RussianTranslation/src/build_anatomy_crosswalk.py
```

| Tag | Count | Adequacy | Pedagogical element(s) | Portrait field | Divergence note |
|---|---|---|---|---|---|
| `<ls>` | 772,567 | lossy | Citation with exact locus, Run-on citations, Dhatupatha reference | `senses[].citations` / `citations_resolved` / `strata` | lossy parse (literary source / L. hedge) — see W1.6 citation-coverage extension |
| `<ab>` | 185,563 | partial | Usage restriction, N. pr. (nomen proprium), Voice and derived-stem labels, so v. a. (extended-meaning marker), v. l. (varia lectio) | `senses[].ab_labels` / `diasystem` | partial parse (abbreviation, q.v. → cross-ref) |
| `<lex>` | 131,189 | clean | Grammatical gender | `senses[].grammar` / `pos` | — |
| `<k1>` | 123,366 | clean | Headword in Devanāgarī, Compounds follow as separate entries, Root marker (verbal root entries), Prefixed verbs nest inside the root article | `key1` | — |
| `<k2>` | 123,366 | partial | — (not in the 24-element spread) | `key2` | partial parse (segmented/sort key) |
| `<pc>` | 123,366 | n/a | — (not in the 24-element spread) | not surfaced — archival locus, used only by `pwg_page_index.py` | — |
| `<div>` | 113,613 | clean | Sense numbering | `senses[].n` / `senses[].sub` (sense-tree node) | — |
| `<is>` | 53,947 | unmapped | Indian grammatical apparatus | not surfaced as a named field — retained inline in `gloss_de`/`examples_sa` text | present in source, no parse-rules mapping yet |
| `<h>` | 6,499 | clean | Homograph numbers, Accent distinguishes homographs | `h` | — |
| `<info>` | 628 | n/a | — (not in the 24-element spread) | not surfaced — machine/infrastructure annotation, stripped before parse | — |
| `<lang>` | 550 | partial | — (not in the 24-element spread) | `senses[].diasystem` (source-language label) | partial parse (source language) |
| `<span>` | 88 | unmapped | — (not in the 24-element spread) | not surfaced by `microstructure.py` | present in source, no parse-rules mapping yet |
| `<hom>` | 82 | clean | — (not in the 24-element spread) | `labels` (via `<ab>`-style diasystem folding) | — |
| `<H>` | 76 | unmapped | — (not in the 24-element spread) | not surfaced by `microstructure.py` | present in source, no parse-rules mapping yet |
| `<F>` | 38 | unmapped | — (not in the 24-element spread) | not surfaced by `microstructure.py` | present in source, no parse-rules mapping yet |
| `<VN>` | 3 | unmapped | — (not in the 24-element spread) | not surfaced by `microstructure.py` | present in source, no parse-rules mapping yet |
| `<fr>` | 1 | unmapped | — (not in the 24-element spread) | not surfaced by `microstructure.py` | present in source, no parse-rules mapping yet |

**Every one of the 17 tags in the census appears above** (`--check` passes).
12 of the 24 pedagogical elements map onto a specific tag (several onto the
same tag — e.g. `<k1>` anchors 4 distinct callouts); the remaining 12 are
typographic/prose conventions realised inline, not as their own element.

### Inline (non-tag) markers

Not XML elements, so absent from the tag census, but load-bearing for both
the pedagogical page and the portrait parser:

| Marker | Role |
|---|---|
| `{#…#}` | SLP1 → IAST Sanskrit (accented forms, quoted examples) |
| `{%…%}` | German-vs-Latin gloss switch |
| `〉` (U+3009) | PWG's own sense-closing glyph — 87,680 occurrences; folded into the sense-number stream by the `MARK` regex in `microstructure.py` (`[)〉]`), see [W1.4](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md#step-4--w14--full-measure--quarantine-store-untouched) |

### Pedagogical elements with no dedicated markup tag

These 12 of the 24 callouts are how a human reader recognises PWG structure
without corresponding to a distinct XML tag — realised as prose conventions
next to a tagged span, or via the inline markers above:

- Etymology in parentheses — prose inside the gloss, following the headword
- German gloss in italics — carried by the `{%…%}` inline marker, not a tag
- Vedic saṃhitā quotation with tonal accents — carried by the `{#…#}` inline marker (accent characters are part of the SLP1 payload)
- Commentators' dissent recorded — prose convention inside a citation's surrounding text
- Variant reading — prose convention, typically inside or beside a `<ls>` citation
- Present stem with accent — carried by the `{#…#}` inline marker
- Poetic examples quoted in full — carried by the `{#…#}` inline marker (`examples_sa` in the portrait)

## Divergences worth flagging for Wave 2

- **`<is>` (53,947 occurrences) has no dedicated portrait field.** It is
  measured by the census and shown pedagogically ("Indian grammatical
  apparatus" — gaṇa/Dhātupāṭha membership), but `microstructure.py` retains it
  only inline inside `gloss_de`/`examples_sa` rather than as a structured
  field. A future wave could promote it to its own portrait field.
- **Five tags (`<span>`, `<H>`, `<F>`, `<VN>`, `<fr>`) are unmapped** in the
  parse-rules census itself (present in the source, no `mdf`/adequacy rating
  assigned) — combined 206 occurrences, negligible relative to the 123,366
  records, but genuinely undocumented rather than merely low-frequency.
- **`<ls>` is the one high-volume lossy tag** (772,567 occurrences, 72.4%
  recognised) — the citation-coverage extension (W1.6) targets exactly this
  gap.

_Dr. Mārcis Gasūns_
