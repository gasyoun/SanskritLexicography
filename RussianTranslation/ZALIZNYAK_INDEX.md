_Created: 01-08-2026 · Last updated: 05-09-2026_

# A Sanskrit inflection-index code — the Zaliznyak scheme for the nominal layer

Zaliznyak's *Грамматический словарь* links each word to its full paradigm with a single
compact code (e.g. `ж 3*a` = fem · declension-type 3 · stem-reduction `*` · stress scheme `a`).
The code is the join key between lexicon and grammar; the paradigm itself lives once in a shared
template table. This is the design the nominal A/B endorsed building toward — **structured
grammatical data**, not a translation aid (see [`NOMINAL_GRAMMAR_AB.md`](NOMINAL_GRAMMAR_AB.md)).

Source note: the live Russian sources (ru.wikipedia, sysblok, Wiktionary appendix) and the
original 2010 preface (image-only at prlib.ru) were network-unreachable from here; the operative
taxonomy below is reconstructed from the English summaries + the gramdict/zalizniak-2010 README
([[reference_zaliznyak_gramdict]]). Verify the exact разряд list against the original before any
publication claim.

## Zaliznyak's three-part code → Sanskrit analog

| Zaliznyak slot | Russian | Sanskrit nominal analog |
|---|---|---|
| **помета** (gender/POS) | м / ж / с / мо | `m` `f` `n` `mfn`(adj) `ind`(indecl) |
| **type number** (stem-final class, 1–8, 0) | hard/soft/velar/hushing/ц/vowel/и/3rd | `1`–`8` by Whitney stem class (below), `0` indeclinable |
| **stress scheme** (a–f) | accent across sg/pl | `a` barytone · `b` oxytone · `—` unknown (Vedic-only axis) |
| **flags** (`*` `°` ①) | stem reduction / deviation / irregular forms | `*` strong/weak gradation · `°` deviation · `+N` N-member compound |

## Type numbers (T) — Whitney stem class as a Zaliznyak-style number

| T | stem class | example | Whitney §§ |
|---:|---|---|---|
| 1 | a-stem | deva | §§326–334 |
| 2 | ā-stem | senā | §§362–368 |
| 3 | i-stem | agni | §§335–345 |
| 4 | ī-stem | nadī | §§350–362 |
| 5 | u-stem | śatru | §§335–345 |
| 6 | ū-stem | vadhū | §§350–362 |
| 7 | ṛ-stem | pitṛ | §§369–376 |
| 8 | consonant-stem | (subtypes below) | §§377–474 |
| 0 | indeclinable | ca, aciram | §§1096–1135 |

Consonant subtypes (letter after `8`, by SLP1 final cluster):

| code | final | example | note |
|---|---|---|---|
| `8n` | -an/-man/-van | rājan | nasal stems, strong/weak |
| `8i` | -in | balin | possessive -in |
| `8s` | -as/-is/-us | manas | sibilant stems |
| `8t` | -at/-ant/-mant/-vant | bhagavant | participles, possessives |
| `8c` | -añc | prāñc | directional, strong/weak |
| `8√` | other consonant / root-stem | vāc | radical |

## Stress scheme (S) — the Vedic accent axis

**Status (H2103, 01-08-2026):** full Whitney **a–f mobility** is emitted on every accented
PWG headword. Implementation:
[`RussianTranslation/src/nominal_grammar.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nominal_grammar.py)
(`_accent_scheme` + `_MATRIX_SCHEME` + `_LEXICAL_SCHEME`). Source matrix:
[WhitneyRoots `crosswalk/accent_rules.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
(19 cells). Validation (VedaWeb 2.0): **17/19 GO, 0 NO-GO**
([WhitneyRoots PR #24](https://github.com/gasyoun/WhitneyRoots/pull/24) / H063;
T8c polish [PR #29](https://github.com/gasyoun/WhitneyRoots/pull/29) / H115). Regenerated FAIR
tables: `headword_index.tsv` · `reverse_paradigm_index.json` · `paradigm_stats.tsv`
(98,639 indexed headwords; scheme counts on 01-08-2026 rebuild: `—` 80,014 · `a` 9,885 ·
`b` 8,346 · `d` 349 · `c` 43 · `f` 2).

Letters keep Zaliznyak's spirit but follow Whitney's strong/middle/weakest mobility (not
Russian sg/pl number mobility — see `schemes` in `accent_rules.json`):

- `a` = **fixed non-final** — accent stays on the lexically accented (non-final) stem syllable
  through the paradigm (§315). Barytones of every stem class; root-ā monosyllables; ī/ū
  root-compounds (-dhī́, -bhū́). E.g. áṃśa → `m·1a`.
- `b` = **columnar-final** — accent stays on the stem-final syllable in its grades; shifts only
  under fusion / semivowelization / ṛ→r / Vedic G.pl -nā́m (§§316–320, §372). Oxytone vowel
  stems and non-syncopating oxytone consonant stems. E.g. agní → `m·3b`, devá → `m·1b`.
- `c` = **fully mobile (hysterodynamic)** — strong on stem, all weak on ending (§317, §350,
  §390). Monosyllabic ī/ū and radical consonant stems. E.g. bhū́ → `f·6c`, vā́c → `f·8√c`.
- `d` = **weakest-mobile** — strong + middle on stem-final; only weakest cases shift (§318,
  §423, §446). Oxytone -ant participles, oxytone an-stems, añc-stems. E.g. adánt → `m·8td*`,
  ātmán → `m·8nd*`.
- `f` = **lexically irregular** — lemma property, not class (gó §361c, nṛ́ §372, śván/yúvan
  §427, …). See `lexical_exceptions` in `accent_rules.json`. E.g. gó → `m·8√f`.
- `—` = accent unrecorded (Classical headword, no `/` in key2). Omitted from the compact
  token. Still the common case (~81% of indexed headwords).

Join key: `(T-code, accent_position)` where `accent_position` is recomputed from key2 `/`
(barytone / oxytone / monosyllable), not read from the old citation-only a/b letter.

**Advisory only** — VedaWeb-derived / rule-predicted accent is never written into reviewed
spine or app data (I/VI accent-collapse lesson). The index is a structured-grammar FAIR
asset; translation portraits stay grammar-OFF per `NOMINAL_GRAMMAR_AB.md`.

### Provenance of the axis (rules + validation already shipped before emission)

1. **Rules** — Whitney §§315–320 / 350 / 372 / 390 / 423 / 446 / 314 encoded as the 18-rule
   / 19-cell matrix in WhitneyRoots `accent_rules.json` (Fable 5, H018 / session S8).
2. **Per-word accent position** — PWG `key2` udātta `/` (`agni/` = agní, `a/MSa` = áṃśa).
3. **Validation** — VedaWeb 2.0 Casaretto accented word-split
   (`66695e4a14f6d337f7788740`) + lemmatization layer; bulk feed under
   [VisualDCS/non-derived/vedaweb/](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb).
   Roadmap closeout:
   [ROADMAP_VEDAWEB_REUSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_VEDAWEB_REUSE.md)
   (Phases 0–4 COMPLETE).

Residual (not this emission): D3 ī/ū G.pl thin-n wider VedaWeb pull in WhitneyRoots
`DECISIONS_NEEDED` / accent_validation `d3_genitive_plural_split` — measurement polish,
does not block a–f letters on the GO cells.

## Flags (F)

- `*` — **strong/weak stem gradation** (the Sanskrit analog of Zaliszniak's stem-reduction `*`):
  consonant stems whose stem alternates across cases (rājan/rājñ-, prāñc/prāc-). Set for 8n/8t/8c.
- `°` — **deviation / irregular**: any non-empty `irregularities` from the grammar block
  (class_unrecorded, monosyllabic_long_vowel, whitney_exception, …).
- `+N` — **N-member compound** (from the MW `<k2>` segmentation).

## Token format

`G·T S F` rendered compact, e.g.:

| headword | lex | index | reading |
|---|---|---|---|
| deva | m. | `m·1b` | masc a-stem, oxytone (devá) |
| áṃśa | m. | `m·1a` | masc a-stem, barytone |
| agni | m. | `m·3b` | masc i-stem, oxytone (agní) |
| senā | f. | `f·2b` | fem ā-stem, oxytone (senā́) |
| rājan | m. | `m·8n*` | masc an-stem, strong/weak gradation |
| manas | n. | `n·8s` | neut as-stem |
| abaddhamukha | adj. | `mfn·1+2` | tri-gender a-stem, 2-member compound |
| aciram | adv. | `ind·0` | indeclinable |

The token is sortable, diff-able, and a stable join key — exactly Zaliznyak's purpose. It is a
**structured-data field** on the grammar block, not injected into translation (the A/B rejected
that). Consumers: declension display, a reverse "index → all headwords of this paradigm" view,
and FAIR export.

## Reverse index (the Zaliznyak reverse-dictionary, over all of PWG)

[`src/reverse_index.py`](src/reverse_index.py) applies the index to the whole dictionary:
streams `csl-orig/v02/pwg/pwg.txt` (read-only), computes the token per headword (`<k1>` +
first `<lex>` + `<k2>` accent), and inverts it.

  python src/reverse_index.py --build               materialize the index + stats
  python src/reverse_index.py --query "m·8n*"        list every headword in that paradigm
  python src/reverse_index.py --stats 30             paradigm distribution

**Coverage (2026-06-29 build):** 123,366 PWG entries → **98,639 indexed** (have a `<lex>`
gender/POS; 24,727 cross-refs/bare forms skipped) → **335 distinct paradigm tokens**. Flag
sanity: `+N` compound 47.3% (≈ MW's 44.5% compound rate), `*` gradation 3.6%, `°` genuine
deviation 0.04% (monosyllabic long-vowel stems — the only nominal anomaly currently detected).
Top paradigms: `m·1+2` 12,681 · `m·1` 11,496 · `mfn·1` 8,346 · `n·1+2` 6,116 · `f·2+2` 3,811.

**FAIR outputs** (committed, materialized — rebuild with `--build`):
- `src/headword_index.tsv` — **the per-word structured-grammar dataset** (5.8 MB, 98,639 rows):
  `k1 · hom · lex · accented · index_token · stem_class · compound_members · irregularities`.
  The declension §§ / paradigm § are omitted (fully derivable from `stem_class` via
  `nominal_grammar._STEM_SECTIONS`) to keep it compact.
- `src/reverse_paradigm_index.json` — `{token: [headword#hom, …]}` (1.1 MB)
- `src/paradigm_stats.tsv` — `index_token · count`, descending (335 rows)
- `src/datapackage.json` — **Frictionless Data Package** descriptor (field schemas, CC-BY-SA-4.0,
  sources PWG/MW/Whitney/WhitneyRoots/vidyut, provenance) over the five grammar resources above
  (incl. `mw_compounds.json`, `whitney_grammar.json`). Makes the layer a citable, archivable dataset.

**This grammar data is recorded per word as a standalone asset and is DELIBERATELY kept out of
translation.** The nominal-grammar A/B ([`NOMINAL_GRAMMAR_AB.md`](NOMINAL_GRAMMAR_AB.md)) showed
grammar-ON does not improve DE→RU and sometimes mildly hurts it, so the portraits (which the
harness inlines) are left untouched and nominal windows run grammar OFF. The data lives here, in
the structured-grammar layer, for declension display / FAIR export — not in the translator's prompt.

This is the foundation for declension display ("show the paradigm of every `m·8n*` noun") and a
grammatical FAIR export — the Scope B/C deliverable the nominal A/B pointed to.

## Declension display (the «Грамматические сведения» template)

The index → paradigm payoff is wired via vidyut:

  python src/reverse_index.py --show "m·8n*"     # paradigm template + member count + examples
  python src/nominal_grammar.py --table agni m.  # one headword's full declension table

`--show <token>` picks a representative member and renders the **shared** declension template
(every headword in that token declines alike — Zaliznyak's principle). `render_paradigm()` in
`nominal_grammar.py` formats any `paradigm_for()` result as an aligned 8-case × 3-number table.
The an-stem template (`m·8n*`, repr. atidhanvan) visibly shows the strong/weak gradation the `*`
flag encodes: `atidhanvā` (nom sg) → `atidhanvānam` (strong) → `atidhanvanā` (weak).

_Dr. Mārcis Gasūns_
