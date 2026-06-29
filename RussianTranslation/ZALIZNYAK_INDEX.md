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

This is **not** Zaliszniak's full a–f mobility — it is a citation-accent flag. Extending to true
mobility (the `c`/`f` mobile schemes) requires a Vedic paradigm source (Whitney §§ per case),
a future axis.

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
