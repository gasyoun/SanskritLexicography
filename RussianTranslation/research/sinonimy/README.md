# Sinonimy — digitized Leonchenko synonym evidence lane

_Created: 26-07-2026 · Last updated: 26-07-2026_

`sinonimy.jsonl` digitizes V.V. Leonchenko's synonym-research xlsx workbooks at
[VisualDCS/derived-data/Sinonimy](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Sinonimy/README.md)
into a structured per-sense evidence lane, per
[../ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md)
B2/Wave 1 ("Sinonimy xlsx→jsonl digitization … another per-sense evidence source
alongside grin12/grin3"). Built by
[build_sinonimy.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sinonimy/build_sinonimy.py)
(`python build_sinonimy.py [path-to-VisualDCS]`, defaults to the sibling repo).

**Scope note (H1491):** this step is digitization only — turning Leonchenko's xlsx
into machine-readable jsonl with provenance. It is **not** wired into the pwg_ru
`corpus_gate.py` gate (unlike `grin12`/`grin3` in `../../src/`) and does not yet
align Leonchenko's synonym groups to PWG senses — that is roadmap bullet
"Sinonimy as its own published crosswalk", explicitly scoped out of this handoff.

## Source-file dedup finding

The roadmap bullet named four groups in the source folder (Глагольные синонимы,
Значения, S_P_D_F, Works-Share-Syn). Opening all of them showed these reduce to
**three distinct datasets, not four** — the folder contains duplicate exports:

| Distinct dataset | Canonical file (used) | Confirmed duplicates (skipped) |
|---|---|---|
| Sense inventory + lemma-anchored rings | `Значения.xlsx` | `Works-Share-Syn/data30.xlsx` (identical sheet names/headers) |
| Verb synonym rings (gloss-anchored) | `Глагольные синонимы_,без ограничений (2).xlsx` | `S_P_D_F/Глагольные синонимы.xlsx` (README-confirmed byte-identical shared strings), `Works-Share-Syn/data28.xlsx` (README-confirmed byte-size-identical) |
| Noun/general synonym rings (gloss-anchored) | `Поиск синонимов в Цифровом корпусе Санскрита.xlsx` | `S_P_D_F/Синонимы существительных.xlsx` (verified here: `По дефинициям` 12,601 rows and `Краткая запись` 19,751 rows match exactly, first row identical), `Works-Share-Syn/data29.xlsx` (identical sheet names/headers) |

Also out of scope, not synonym-group/pair data:
- `Подобие по векторам.xlsx` — a different, unvalidated vector-similarity method
  (the source README flags its neighbor lists as *not* obviously semantic
  synonyms). Flagged for a future session if this evidence type is wanted.
- `S_P_D_F/Частотный список существительных и глаголов.xlsx` — corpus frequency
  baseline, not synonym data.
- `S_P_D_F/Синтагматическая таблица DCS.csv/.txt` — raw collocation substrate
  with unresolved legacy-encoding corruption (see source README); not
  digitized here.

Within each canonical file, only the sheet(s) giving clean group/pair shape were
digitized (`Значения` + `Алфавитный порядок` for the sense/ring file; `По
дефинициям` for the two gloss-ring files). Sibling sheets in the same workbooks
(`Синонимы без ограничений`, `Заголовки син.рядов`, `Поиск омонимов`, `Краткая
статистика`, `Синонимы при 50% соответствия`, `По убыванию глубины` — the last a
confirmed same-row-count re-sort of `Алфавитный порядок`) hold the same
underlying data restructured for different lookups (lemma-keyed vs
homonym-search vs stats) and were not separately digitized to avoid redundant
rows; a future session can add them if a specific lookup shape is needed.

## Schema

One JSON object per line, `{"type", "source", ..., "provenance": {"file", "sheet"}}`.
Three row types:

| `type` | From | Fields | Rows |
|---|---|---|---|
| `sense_inventory` | `Значения.xlsx` sheet `Значения` | `lemma`, `n_senses`, `senses[]` (English gloss fragments) | 9,264 |
| `synonym_group_lemma` | `Значения.xlsx` sheet `Алфавитный порядок` | `lemma`, `depth` (ring size), `gloss_anchor`, `members[]` (IAST synonyms) | 13,922 |
| `synonym_group_gloss` | `Глагольные синонимы...xlsx` / `Поиск синонимов...xlsx`, sheet `По дефинициям` | `pos` (`verb` / `noun_or_general`), `gloss` (English anchor), `n_members`, `members[]` (IAST synonyms) | 24,087 (verb) + noun/general |

`clean_lemma()` strips the `|pipe|`/`/slash/` delimiters Leonchenko's export
wraps headwords in; empty cells (`//`, `||`) are dropped from `members[]`.

Total: 47,273 rows, 18 MB.

## Known caveats (inherited from the source)

- Gloss-overlap methodology only — `synonym_group_*` rows reflect shared English
  MW/DCS gloss fragments, not an independently verified semantic-synonym
  judgment; treat as candidate evidence, same posture as `grin12`/`grin3`.
- `Значения.xlsx`'s lemma keys sometimes carry a homonym-disambiguation suffix
  (`aṁśa 2`) rather than a clean IAST form — left as-is (provenance over
  normalization); a consumer should strip/parse this if joining on bare lemma.
- No rights blocker (local research data, per the roadmap ruling) — but also no
  rights *confirmation* was sought here; treat as evidence-only, matching
  `grin12`/`grin3`'s posture, until a rights check happens.

_Dr. Mārcis Gasūns_
