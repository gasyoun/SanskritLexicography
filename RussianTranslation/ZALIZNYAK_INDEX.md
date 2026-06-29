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

Zaliszniak's a–f encode accent *mobility* across the whole paradigm. Sanskrit's full mobility
(Whitney's hysterodynamic shifts, §317 etc.) needs the per-case Vedic paradigm, which our data
does not carry per word. So we emit a **coarse, honest** accent on the *citation form* only,
read from the udātta mark (`/` after the accented vowel in the accented key, e.g. `a/MSa` = áṃśa,
`agni/` = agní):

- `a` = **barytone** — udātta not on the final stem vowel (accent stays on the stem). E.g. áṃśa.
- `b` = **oxytone** — udātta on the final stem vowel (accent tends to move to endings in the
  weak cases). E.g. agní, senā́, devá.
- `—` = accent unrecorded (Classical headword, no Vedic accent). The common case.

This is **not yet** Zaliznyak's full a–f mobility — it is a citation-accent flag (where the
accent sits on the lemma), not how it moves across cases.

### Vedic accent mobility (a–f) — the data IS in Whitney; this is an extraction task, not a missing source

Correcting an earlier overstatement: it is **not** that "Whitney might supply it but our data
can't." Both halves of the data already exist here:

1. **The mobility RULES — in Whitney, already ingested** (`whitney_sections.json`, declension
   ch. IV–V). The accent-in-declension rules are concrete and per-(stem-class, accent-position):
   - **§§315–317** — change of accent affects monosyllables and final-accented stems; *"the
     accent falls upon the ending in all the weak cases"* (`nāvā́, vācí, vākṣú`). The mobile scheme.
   - **§318** — polysyllabic consonant stems shift only in the *weakest* cases; present participles
     in -ánt: `tudatā́` but `tudátsu`.
   - **§319** — polysyllabic stems in an accented short vowel *retain* the accent: `agnínā, agnáye`
     (agní stays — a *fixed*, not mobile, scheme).
   - Per-class accent paragraphs: **§350** (ī/ū monosyllables), **§372** (ṛ-stems), **§390**
     (consonant monosyllables), **§423** (an-stems lose suffix á → tone to ending), **§446**
     (final-accented in-stems shift in the weakest cases), **§314** (vocative → first syllable).
2. **The per-word accent POSITION — in PWG, already in hand.** The udātta `/` in `key2`
   (`agni/` = agní, `se/nA` = sénā) gives each lemma's lexical accent. Whitney's rules are
   *conditioned* on exactly this (oxytone stems shift; barytone/retaining stems do not), so the
   two compose.

**So the gap is encoding, not sourcing.** Build steps for the full a–f axis:
- Hand-encode the ~10 Whitney accent rules above into a table keyed by (stem-class,
  accent-position) → per-case accent pattern (strong / middle / weakest), i.e. the Zaliznyak
  a–f scheme. This is the accent analog of the existing stem-class→§ concordance.
- Join each word's accent position (`key2` `/`) with its stem-class rule → assign `a`–`f`.
- Validate the generated accent paradigm against accented Vedic text. **Validation set PROBED +
  CONFIRMED (2026-06-29): VedaWeb 2.0** — API live at `vedaweb.uni-koeln.de/api` (FastAPI, OpenAPI
  at `/api/openapi.json`). `POST /api/search {"type":"quick","q":"<lemma>"}` returns hits with
  per-resource highlights; the **accented word-split** comes from the Casaretto et al. (2025)
  annotation resource `66695e4a14f6d337f7788740` (e.g. searching `agni` → RV 6.59.3 highlight
  `… índrā; nú; agnī́; ávasā; ihá; vajríṇā; vayám; devā́` — udātta-marked, position-aligned).
  Companion layers at the same locations: lemmatization `679b7da2d5b833a67f64b3f7`, Scarlata–Widmer
  accented text `66695c4b14f6d337f778873f`, Lubotsky padapatha `668ba4460b5942c9849a8684`. Bulk:
  `GET /api/resources/{id}/export`. So per lemma, collect all attested inflected+accented forms,
  bucket by the Casaretto morphology (case/number), and compare to the generated paradigm — turnkey.
  (Build note: the older legacy `/rigveda/api/search` is superseded by this 2.0 platform.)
- _(superseded validation note retained for context): VedaWeb_ ([vedaweb.uni-koeln.de](https://vedaweb.uni-koeln.de), GitHub
  [VedaWebProject/vedaweb](https://github.com/VedaWebProject/vedaweb)) — the accented Rigveda with
  per-word UZH morphology (lemma/case/number/gender) and accent-sensitive search
  (`rigveda/api/search`, `accents` param; ~10,522 stanzas), **CC BY 4.0**, and already linked to
  CDSL via the **C-SALT APIs** (same integration as the org's Salt/Kosh work). It gives, per
  attested RV word-form, the real case/number **and accent**, with a lemma to join back to PWG —
  so a generated accent paradigm (e.g. predicted ins.sg `agnínā`) can be checked against the
  attested form. This is in-ecosystem and redistributable; it removes the last blocker named above.

**Honest limits** (why it is staged, not blocked): (a) the axis is **Vedic-only** — Classical
headwords carry no recorded accent (`key2` has no `/`), so `—` stays the common value; (b) it is
genuine philological encoding work (~10 rules + exception §§ like §350/§423), not a parse; (c) it
needs the accented-RV validation set to trust the output. The current `a`/`b`/`—` citation flag
is the honest interim; full a–f is the next concrete axis, with the source already on disk.

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
