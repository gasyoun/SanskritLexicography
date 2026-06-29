# Grammar layer — the 3rd axis (Whitney) for pwg_ru

pwg_ru already carries two evidence axes per headword: **lexicon** (corpus_lexicon Sa→Ru
candidates) and **corpus** (parallel verse + Renou register). This adds the **grammar** axis,
reusing the existing [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) crosswalk
(Grammar × Corpus × MW/Apte, 24k FAIR triples) — **not** a fresh Whitney/Wiki scrape.

## What it is

- [`src/whitney_grammar.py`](src/whitney_grammar.py) consumes WhitneyRoots'
  `crosswalk/roots.csv` and materializes a slim SLP1-keyed lookup
  [`src/whitney_grammar.json`](src/whitney_grammar.json) (855 roots / 930 records), so the
  pipeline has no run-time dependency on the sibling repo. `--build` re-materializes it.
- `grammar_for(slp1[, homonym])` → the grammar block: `class`, `class_uncertain`, `ppp`,
  `period_tags`, `dcs_freq`, corpus-attested `attested_forms`, `section_refs` (Whitney §§
  per form-category — the "why this form?" links), `mw_id`/`apte_id`, and a derived
  **`irregularities`** exception list.
- [`src/pilot/enrich_portrait_grammar.py`](src/pilot/enrich_portrait_grammar.py) attaches
  the root grammar block to a root's portraits (sibling of `corpus_synonyms`):
  `python src/pilot/enrich_portrait_grammar.py <root> [--apply]` (dry-run shows a sample).

## The `irregularities` (your "expulsions") exception level

Derived flags surface the grammar exceptions worth annotating:

| flag | meaning | examples |
|---|---|---|
| `multi_class:…` | root conjugates in >1 gaṇa | gam `I|II`, han `I|II|VIII`, yuj `II|VII` |
| `class_uncertain` | Whitney's "ROMAN ?" (uncertain gaṇa) | han, yuj |
| `class_unrecorded` | defective `—` OR a capture gap (verify) | — |
| `root_final_nasal_loss(…)` | root-final m/n dropped in the PPP — the "expelled" nasal | gam→gatá, han→hatá, man→matá |

## Status & scope

- **Built + prototyped on `gam`** — the enriched portrait carries all three layers
  (`corpus_synonyms` + `grammar`); `gam` whitney_no 170, class `I|II`, ppp `gatá`,
  irregularities `multi_class`, `root_final_nasal_loss(gam→gatá)`.
- **Verb-root keyed** — lands cleanly on the dhātu frequency queue (gam, yuj, vid, han,
  sthā, bhū, as, i…), which *are* Whitney roots. Noun/compound headwords need nominal
  morphology (a separate source) and are out of scope.
- **Homonym alignment** — single-record roots (gam, yuj, han) join directly; multi-record
  roots (as, i, vid carry 2 Whitney homonyms) need PWG-homonym↔Whitney-homonym alignment
  first (the same hand-curated step the crosswalk solved for MW/Apte). Flagged, not guessed.

## Non-root headwords — the nominal grammar layer (built 2026-06-29)

**BUILT 2026-06-29.** Modules shipped:

| Module | What it does |
|---|---|
| [`src/mw_compounds.py`](src/mw_compounds.py) + [`src/mw_compounds.json`](src/mw_compounds.json) | Streams `csl-orig/v02/mw/mw.txt` (read-only); extracts `<k2>` em-dash compound boundaries → 106,603-entry lookup `{k1_slp1: [member1, member2, …]}`; Vedic accent marks stripped. `compound_for(k1)` → members or `None`. |
| [`src/nominal_grammar.py`](src/nominal_grammar.py) | `nominal_grammar_for(slp1, lex)` → `{stem_class, declension_sections, paradigm_section, compound_members, irregularities, …}`. Stem class from SLP1 final phoneme (the canonical Whitney criterion); Whitney §§ from a static hand-verified concordance built from `whitney_sections.json` ch. IV–V, XVI–XVIII (already fully fetched — all 1316 §§ present). |
| [`src/pilot/enrich_portrait_nominal_grammar.py`](src/pilot/enrich_portrait_nominal_grammar.py) | Portrait-level attachment: adds `nominal_grammar` block to portrait JSONs. Parallel to `enrich_portrait_grammar.py`. |
| `nominal_grammar_text()` in [`src/pilot/gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py) | Harness-level injection function (parallel to `grammar_text()` for roots). Ready for use when nominal translation windows start. |

**Whitney §§ data source** — `whitney_sections.json` already had ALL chapters I–XVIII (no
fetch extension needed). The nominal concordance is baked as a static table into
`nominal_grammar.py` (`_STEM_SECTIONS`), hand-verified against the fetched section texts.

**Compound segmentation** — 106,603 MW k1 entries with em-dash boundaries extracted
(vs. the GRAMMAR_LAYER design estimate of 182k — that figure included `<e>3` sub-entry
lines that share the same k1; only unique k1 is kept per lookup entry). Accent marks
(`/^'`) stripped from member strings. `mw_compounds.json` is committed (3.4 MB); rebuild
with `python src/mw_compounds.py --build` if csl-orig updates.

**Stem-class concordance** (verified, not guessed):

| Stem class | Whitney §§ | Paradigm | Notes |
|---|---|---|---|
| a-stem | §§326–334 | §330 | majority class; m/n |
| ā-stem | §§362–368 | §364 | derivative long-vowel; senā f. model |
| i-stem | §§335–345 | §339 | agni m., gati f., vāri n. |
| ī-stem | §§350–362 | §356 | nadī f. (polysyl.); dhī f. (monosyl. §351) |
| u-stem | §§335–345 | §341 | śatru m., dhenu f., madhu n. |
| ū-stem | §§350–362 | §351 | bhū f. (monosyl.) |
| ṛ-stem | §§369–376 | §373 | agent-nouns in tṛ/tā |
| consonant-stem | §§377–474 | §391 | vāc f., manas n., rājan m. |
| indeclinable | §§1096–1135 | — | adv./particle/indecl. |

Derivation ref `§§1136–1245` and compound ref `§§1246–1316` always appended when applicable.

**vidyut subanta confirmed working** (`vidyut.Pratipadika.basic('deva')` + `Subanta` →
`['devaH']`). Full per-headword paradigm display is deferred — not needed for the core
annotation; add `--paradigm` flag to `nominal_grammar.py` when the nominal window runs.

**A/B test RUN 2026-06-29 → translation injection REJECTED** (full writeup
[`NOMINAL_GRAMMAR_AB.md`](NOMINAL_GRAMMAR_AB.md)). Wired per-card injection into the harness
(`gen_opt_harness2.py --nominal [--no-grammar]`) and ran arm B (grammar ON) vs arm A (OFF) on
8 stratified PWG headwords + blind Opus judge. Result: **A wins 5, ties 2, B wins 1** (grammar
ON does NOT improve DE→RU translation; even `grammar_notes` went 4-1 to A). Why: PWG's German
already carries the grammatical cues, and the one compound's segmentation was already printed in
the source (`abadDa + muKa`), so the MW-join was redundant. Both arms: 0 nulls, 100% markup
fidelity. **Decision: nominal windows run grammar OFF by default.** The layer is NOT retired —
its value is **structured grammatical data** (stem-class index, paradigm, compound segmentation,
exception §§) for the grammatical apparatus / declension display / FAIR export (Scope B/C),
independent of translation. Build that consumer, not a translation injection.

**Exception fold DONE 2026-06-29:** `WhitneyRoots/src/grammar_refs.json` exception §§ are folded
into the ROOT layer (`whitney_grammar.json`, 289 records, joined by whitney_no) — see
`whitney_grammar.py`. (This enriched the root layer, the genuinely useful target; the nominal §§
were always static-concordance, not per-word exceptions.)

**vidyut paradigm display DONE 2026-06-29:** `nominal_grammar.py --paradigm <SLP1> <lex>` emits
the real subanta declension (feminine ā/ī/ū stems use vidyut's `nyap` pratipadika; verified
senā/nadī/agni). `nominal_grammar_for(..., paradigm=True)` attaches it. This is the structured-data
asset the A/B says to build on (not the translation block).

**Zaliznyak-style inflection index DONE 2026-06-29** ([`ZALIZNYAK_INDEX.md`](ZALIZNYAK_INDEX.md)).
`zaliznyak_index(slp1, lex, accented=)` → a compact join token `G·T S F` (gender · declension
type 0–8 · Vedic stress a/b · flags `*°+N`), modelled on Zaliznyak's `ж 3*a`. E.g. agni `m·3b`,
rājan `m·8n*`, manas `n·8s`, abaddhamukha `mfn·1°+2`, aciram `ind·0`. Attached as
`zaliznyak_index` on the grammar block and materialized by the portrait enrich (accent read from
`key2`'s udātta `/`). This is the structured-data join key the A/B endorsed — sortable, citable,
the lexicon↔grammar link as one token. CLI `--index <SLP1> <lex> [accented]`; locked by `--selftest`.
Future axis: true Vedic accent *mobility* (Zaliznyak a–f). The data is NOT missing — Whitney's
per-case accent rules are already ingested (`whitney_sections.json` §§315–319, 350, 372, 390,
423, 446) and the per-word accent position is in PWG `key2`'s udātta `/`; it is an encoding task
(hand-build a stem-class→case-accent table, join, validate vs accented RV). Spec in
[`ZALIZNYAK_INDEX.md`](ZALIZNYAK_INDEX.md) §"Vedic accent mobility".
