# Roadmap B — what ACL Anthology / comparable projects teach: BLI evaluation, sense benchmark, Lexical Linked Data

_Created: 08-07-2026 · Last updated: 08-07-2026_

Three ACL-adjacent literatures map directly onto layers this repo already has. This roadmap folds the ground-truth corrections verified 08-07-2026 (what exists vs what the naive reading assumed) and MG's same-day rulings (decision log at the bottom). Companion: [ROADMAP_CEILING_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) (the "what we can't answer" side) and the standing [ACL_ANTHOLOGY_MONITOR.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ACL_ANTHOLOGY_MONITOR.md) (complement, don't duplicate). Sequencing: **H335 audit → quick wins in parallel with translation → benchmark/graph phases after ~50% coverage.**

## Ground truth (verified 08-07-2026 — build on this, don't re-derive)

- **OntoLex already exists as a flat one-way export**: `release/ontolex.ttl` (32 MB, populated) + `tei_lex0.xml` via [src/export_interop.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py). The gap is a real LOD graph: placeholder `example.org` IRIs, no `vartrans` sense-links, no PROV-O, no LiLa link, no SPARQL. **Upgrade, not stand-up.**
- **Per-sense dating exists as a Renou proxy**: `src/pwg_sense_stratum.jsonl` (23,461 senses, stratum + date span). Chronology claims soften to "Renou-state proxy", not "cannot answer".
- **DCS genre is per-lemma** (`dcs_freq_dims.json`) — confirming H335 W4's per-sense gap.
- **[ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json) already carries per-work `genre`/`period`/`date`/`renou`** (45 works) — the traditional lane of sense-genre is largely derivable today.
- **BLI evaluation and WSD are genuinely absent** — B1 and the ceiling roadmap's C1 are net-new.

## B1 — BLI-style evaluation of the alignment lexicon

`corpus_lexicon.jsonl` (1.09 M Sa↔Ru pairs, SLP1) *is* bilingual lexicon induction from parallel text — but it has coverage numbers, not a BLI evaluation. ACL's 25-year literature (IBM/fast_align → embedding BLI) gives the standard: **P@1 and MRR against a gold set**. Cheap, publishable upgrade.

- **Gold set** (~500 lemma→RU pairs, stratified by frequency band): MG annotates pass 1; a frozen, documented model (Fable 5, fixed prompt + version) annotates pass 2 independently; `/gold-adjudicate` computes κ and MG adjudicates disagreements. Honest label: *human–model agreement* (human recruiting parked for 2026 — do not resurface).
- **Harness**: deterministic scorer (P@1, P@5, MRR) over `corpus_lexicon` ranked candidates; the same harness later scores any embedding-BLI or DharmaMitra candidate system (shared with ceiling-roadmap C1's design).
- **Paper slot**: this is an obvious `Axx` (BLI for a morphologically rich low-resource pair with a 19th-c. dictionary as silver standard) — route through `/paper-scaffold` when the numbers exist.

## B2 — sense inventory + sense-attestation benchmark (WordNet/SemCor lineage)

H335 W4's "which sense in kāvya" is a **sense-attestation task**; ACL's lesson is to publish it as a benchmark with agreement stats. Three rulings wire the inventory side:

- **IndoWordNet synset crosswalk** (`/crosswalk-build` PWG-senses × Sanskrit WordNet synsets, per Kulkarni GWC-2010): gives each PWG sense a synset ID, unlocking WordNet-lineage sense-frequency methods. **Rights first**: IndoWordNet's license is restrictive — check via the Samsaadhanii/Kulkarni contact (org memory: call/cross-validate, don't clone GPL); the crosswalk *mapping* (our sense-ID → synset-ID pairs) is ours to publish even where their glosses aren't.
- **Leonchenko Sinonimy as a W2 evidence lane**: `VisualDCS/derived-data/Sinonimy` (xlsx: Глагольные синонимы, Значения, S_P_D_F, Works-Share-Syn) → digitize to jsonl → another per-sense evidence source alongside grin12/grin3 ("which senses does Leonchenko's synonymy support"). Local data, no rights blocker.
- **Sinonimy as its own published crosswalk**: additionally align Leonchenko's synonym *groups* to PWG senses as a standalone asset — kosha manifest row + PROJECT_INTERLINKS registration on release.
- **Benchmark packaging**: once W4's per-sense genre attribution + the synset crosswalk exist, publish sense-attestation gold (sense × genre × attested?) with κ, via `/data-release` (FAIR, DOI).

## B3 — Lexical Linked Data: upgrade the flat export to a real LLOD node

The single biggest architectural lesson: each sense a `LexicalSense`, each citation a `Reference`, and every question in the capability roadmaps becomes one SPARQL query instead of a bespoke script. Reframed as **upgrade** of `export_interop.py`:

1. **Real IRIs** — `w3id.org` community redirect (MG ruling): register a `w3id.org/…` namespace (one PR to [w3id.org](https://github.com/perma-id/w3id.org)), pointing at GitHub Pages now, re-pointable forever. Replace every `example.org` IRI.
2. **`vartrans` sense-links** — RU/EN translation relations between senses (the data already exists in the store; the export just doesn't emit it).
3. **PROV-O provenance** — model + pipeline version per sense (the store's `provenance` block, incl. the H321-era `evidence_status` markers, maps directly).
4. **LiLa linking** — link lemmas to the LiLa/citation-corpus ecosystem where IDs exist; the Whitney-root crosswalk (FAIR 24k triples, already released) is the template.
5. **SPARQL endpoint** — static-first (a triple store dump + a hosted-query option like qlever/Fuseki on demand); publishing gate: `/publish-safety-check` before any endpoint goes live.

Milestones 1–3 are deterministic edits to one exporter + its selftest; 4–5 are the research-facing tail.

## Phasing

- **Wave 0 (now):** H335 audit (W2/W4 specs are B2's substrate).
- **Wave 1 (parallel with translation):** B3 milestones 1–3 (exporter upgrade — quick win), Sinonimy xlsx→jsonl digitization, IndoWordNet rights check (`@DECIDE` on composition after the license quote).
- **Wave 2 (after ~50% coverage):** B1 gold set + scoring, B2 synset crosswalk + benchmark packaging, B3 milestones 4–5.
- Wave-1 handoffs are minted after H335 lands; each will carry its own starter line in the registry.

## Decision log (MG rulings, 08-07-2026)

| Fork | Ruling |
|---|---|
| LOD IRI namespace | w3id.org community redirect |
| Gold/κ under no-second-annotator | Model as annotator 2 (frozen, documented), `/gold-adjudicate` |
| WordNet + Sinonimy entry | ALL THREE: IndoWordNet synset crosswalk + Sinonimy as W2 evidence lane + Sinonimy as standalone crosswalk |
| Sequencing | Audit → quick wins → rest |

_Dr. Mārcis Gasūns_
