# pwg_ru cards → MDF/LIFT — mapping design and exporter (H727)

_Created: 11-07-2026 · Last updated: 11-07-2026_

Design note for [`src/pilot/export_mdf_pwg_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/export_mdf_pwg_ru.py),
the read-only exporter that turns already-promoted pwg_ru translation cards
([`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md),
local-only store, 11,383 sense rows / 2,350 cards as of 11-07-2026) into
SIL MDF standard-format records (Toolbox/FLEx lineage). Built for
[H727](https://github.com/gasyoun/Uprava/blob/main/handoffs/H727-Fable_SanskritLexicography_pwg-kosha-mdf-integration_11.07.26.md)
per the MG ruling of 11-07-2026 in the
[SIL MDF ecosystem correlation map](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md) §4–5.
Written by Fable 5 (`claude-fable-5`).

## Why

Coward & Grimes 2000 §4 of the correlation map: pwg_ru cards are already
isomorphic to bilingual MDF records. Making the isomorphism explicit gives the
RU translation an exchange format consumable by the language-documentation
toolchain (Lexique Pro, Webonary, Dictionary App Builder) with none of our own
tooling required on the consumer side. Distribution runs through the
[kosha data-hub manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json).

## Record grain

One MDF record per **card** = one `(key1, subcard)` group of store rows; each
store row is one sense. Rows keep store (promotion) order inside a card; cards
sort by IAST headword. 11,383 rows → 2,350 records on the current store.

## Field mapping

Profile alignment: the exporter's marker subset and field order are checked by
`--selftest` against the csl-standards
[`mdf-export-profile.json`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/data/schema/mdf-export-profile.json)
schema when the sibling clone is present (marker inventory ⊇ ours; field order
must match verbatim), so the two exporters cannot drift silently.

| Card element | MDF | Notes |
|---|---|---|
| `iast` headword | `\lx` | IAST display form (consumers are human-facing tools); SLP1 `key1` preserved in the meta note. The csl-standards MW profile uses SLP1 — an intentional divergence, documented here. |
| homonym index (`~~hN_` in `subcard`, N>0) | `\hm` | `h0` = not a homonym, suppressed. |
| first `<lex>` in the card (RU, then DE field) | `\ps` | Gender/POS folded in, PWG-style (`m.`, `adj.`, …). Absent for most verb roots — expected, not missing data. |
| `sense_tag` | `\sn` | **PWG prints real sense numbers** (unlike MW's prose-inferred senses): when every row has a distinct numeric `sense_tag`, the printed numbering is kept as observed. Otherwise numbering is inferred 1..n and flagged with the same `\nt sense-numbering: inferred` convention csl-standards uses. Monosemous cards omit `\sn` per MDF convention. |
| `en` (when present) | `\ge` | The secondary **English gloss lane**. Emitted only when [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py) has attached an `en` field — never fabricated. The current store carries none yet (EN promotion pending), so current exports are `\de`-only; the lane is wired and tested. |
| `ru` | `\de` | The primary **national/target-language definition** — exactly the book's §2.3 national-vs-English contrast, and the same ruling csl-standards H721 gives Sanskrit-Sanskrit koshas (SKD/VCP): the analysis language of the dictionary goes to `\de`, English to `\ge`. |
| inline `<ls>` citations | `\bb` | Distinct citations per card, in order; `<ls n="M.">8,64.</ls>` continuation form expanded to a self-contained `M. 8,64.`. Also kept inline in `\de` prose (the citation is part of the printed definition). MDF has no evidence-class field — same `partial` adequacy call as the csl-standards mapping. |
| store provenance | `\nt meta:` | profile version, national language, SLP1 key, subcard, PWG column/page pointer, `review_status`, generating model version. |

**Not exported:** the German `de` field (PWG's own text — this dataset is the
*translation*, recoverable via the meta pointer, not a PWG re-edition), the
`evidence`/`evidence_summary` blocks and `differentia` (pipeline QA apparatus,
not lexicography), `dcs_freq` (a kosha dataset in its own right).

### `\ge`/`\de` in one sense block — bilingual deviation

The csl-standards MW profile treats `\ge` and `\de` as alternates that never
co-occur (English is MW's national language, so `\ge` alone is used). A
bilingual RU+EN card legitimately carries both per sense (`\sn → \ge → \de`,
in App. B relative order), and multi-sense cards repeat `\de` — which the
MW-profile validator's order check would flag. The exporter's own structural
validation therefore treats `\sn`/`\ge`/`\de` as one repeating sense block;
everything else follows the shared App. B order table verbatim.

## Markup resolution inside `\de` (one line per field, MDF is line-oriented)

* `{%…%}` translation gloss — unwrapped.
* `{#…#}` SLP1 Sanskrit — transliterated to IAST via the shared
  `build_article_site.slp1_iast` (no transcoder #63).
* `<ab>` abbreviations — the
  [ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
  tooltip policy applied as render-time text: Bucket A editorial tokens →
  Russian via [`pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py)
  (`vgl.` → `ср.`), Bucket B grammatical categories stay international Latin.
  MDF has no tooltip channel, so the visible-text half of the policy is all
  that applies.
* `<is>` proper names — kept IAST. The site Cyrillicizes these, but
  [`iast_to_cyrillic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py)
  is documented as not yet corpus-validated (ABBREVIATIONS_RU.md open item);
  an exchange format should not bake in an unvalidated transliteration.
* `[Page…]` print markers and the `¦` headword/body separator — stripped
  (layout, not prose).

## RANGE-SET gate (book §9.7) — closed vocabularies as a selftest

Two field families are checked against **closed vocabularies**, the book's
RANGE-SET discipline:

1. **`<ab>` tokens** must resolve in PWG's own 791-entry `pwgab` table
   ([`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py);
   lowercase-keyed, so sentence-initial capitals are folded first).
2. **`\ps` values** must be in the exporter's `PS_RANGE` (the store's observed
   `<lex>` inventory + standard PWG gender/POS values).

Violations are counted and reported on every run; `--strict` makes them fatal;
`--selftest` proves the gate trips on poisoned fixtures. Current full-store
residue: **4 distinct out-of-range `<ab>` tokens** (`3.`, `Präs.`,
`adv. Comp.`, `s. u. d.`) — the census's known "not in pwgab" tail (OCR noise /
non-standard local abbreviations), left visible rather than silently passed.

## LIFT

The LIFT (XML) fourth serialization landed in csl-standards via H721
([PR #107](https://github.com/sanskrit-lexicon/csl-standards/pull/107):
[`export-lift.mjs`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/scripts/export-lift.mjs),
[`LIFT_EXPORT_MAPPING.md`](https://github.com/sanskrit-lexicon/csl-standards/blob/main/docs/LIFT_EXPORT_MAPPING.md)).
The pwg_ru→LIFT mapping is the same table as above with the standard MDF↔LIFT
correspondences (`\lx` → `lexical-unit`, `\ps` → `grammatical-info`, `\de` →
`definition` with `lang="ru"`, `\ge` → `gloss` with `lang="en"`, `\bb` →
`note type="source"`); a dedicated pwg_ru LIFT serializer is deferred until a
consumer needs LIFT specifically (Lexique Pro, the first target consumer,
reads MDF natively — see H722).

## Running

```
python src/pilot/export_mdf_pwg_ru.py --selftest
python src/pilot/export_mdf_pwg_ru.py --keys dah,gam --limit 30 --out docs/samples/pwg_ru_sample.mdf
python src/pilot/export_mdf_pwg_ru.py --out src/pilot/output/pwg_ru_full.mdf
```

The committed 30-card sample lives at
[`docs/samples/pwg_ru_sample.mdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/samples/pwg_ru_sample.mdf);
the full export stays gitignored (`src/pilot/output/`) like the store it is
derived from, and is distributed through the kosha manifest instead.

_Dr. Mārcis Gasūns_
