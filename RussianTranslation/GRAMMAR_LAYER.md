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

## Open: wiring into the harness (for `yuj`, before it is translated)

Two ways to make the translator *use* the grammar during the DE→RU pass (so the data is
enriched once, not redone later):
1. **Portrait block** (this prototype) — `--apply` to the root's portraits; the harness
   inlines portraits, so the model sees it. Cost: the block repeats per sub-card.
2. **Root-level harness injection** (token-smart) — inject the single root grammar block
   once into the `gen_opt_harness2.py` preamble (the grammar is identical across a root's
   sub-cards), plus one prompt line directing its use. Avoids per-card duplication.

Recommended: (2) for production efficiency. Either way, add a prompt line: "Grammar
(Whitney) — the root's class/PPP/§§ and irregularities; use to inform grammatical notes
and flag irregular/defective forms; never override a corpus- or German-attested sense."
