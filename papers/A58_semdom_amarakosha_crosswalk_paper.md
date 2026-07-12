# A58 — First crosswalk of SIL's semantic domains to a classical thesaurus: semdom ↔ Amarakosha varga structure

_Created: 12-07-2026 · Last updated: 12-07-2026_

Paper skeleton for **A58** in the
[Uprava ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)
pipeline, scaffolded over the tables committed by
[H742](https://github.com/gasyoun/Uprava/blob/main/handoffs/H742-Fable_SanskritLexicography_semdom-kosha-crosswalk-build_11.07.26.md)
([PR #364](https://github.com/gasyoun/SanskritLexicography/pull/364)). The
scoping memo with the GO verdict, verified prior-art sweep and licence route is
[SEMDOM_KOSHA_CROSSWALK_SCOPING.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md)
(H725); the results-of-record document is
[data/SEMDOM_AK_CROSSWALK_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md).

## Claim

SIL's 1,792 field-lexicography semantic domains
([semdom.org](https://semdom.org)) have never been mapped to any classical or
historical thesaurus; crosswalking them to the Amarakosha's varga structure
(24 vargas, 5,590 synsets, ~6th c. CE) shows that (i) a 1,500-year-old native
semantic organization and a modern elicitation taxonomy agree on **67.0%** of
synset placements at the section level, (ii) SIL's domain inventory has **no
coverage hole** for the sampled classical material (0 NONE votes in a
200-synset dual-annotated gold, exact κ 0.677 / level-2 κ 0.806), and (iii)
the automatic MW-gloss → WordNet → GWC-2023 bridge is a usable **candidate
generator but not a classifier** (top-1 17.5% exact vs 58.5% gold-in-top-6 at
level-2) — an honest negative that transfers to any classical-thesaurus
mapping attempt (Roget, Buck, Chinese leishu).

## Data inventory

Every intended result and the committed artifact that backs it. All headline
numbers are recomputable from the committed tables via
[semdom_ak_metrics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_metrics.py).

| Intended result | Committed artifact | Status |
|---|---|---|
| Level A structural map: 20 thematic vargas → semdom level-2/3 domains, 108 ID pairs, per-row evidence | [semdom_varga_crosswalk.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_varga_crosswalk.csv) + validator [semdom_varga_crosswalk.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_varga_crosswalk.py) | exists |
| Level B candidates: all 5,590 synsets × top-6 machine candidate domains | [semdom_ak_candidates.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_candidates.tsv) | exists |
| 200-synset stratified gold (leaf-domain label per `eid`, provenance column) | [semdom_ak_gold.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_gold.tsv) | exists |
| Inter-annotator agreement (exact κ 0.677 / level-2 κ 0.806) | [semdom_ak_annotator_A.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annotator_A.tsv) · [semdom_ak_annotator_B.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annotator_B.tsv) · κ via [semdom_ak_metrics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_metrics.py) `kappa` | exists |
| Adjudication audit trail (64 A≠B items, 60→A / 4→B, adjudicator-bias caveat) | [semdom_ak_disagreements.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_disagreements.tsv) | exists |
| Bridge quality vs gold (top-1 17.5% / top-6 45.0% exact; 27.5% / 58.5% level-2) | [semdom_ak_bridge.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_bridge.py) + [semdom_ak_metrics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_metrics.py) `metrics` | exists |
| Structure agreement (134/200 = 67.0% inside the varga's Level A subtree) | [semdom_ak_metrics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_metrics.py) `metrics` over gold + Level A CSV | exists |
| Coverage (5,391/5,590 = 96.4% synsets with ≥1 candidate; 1,196/1,792 = 66.7% domains reached) | [semdom_ak_candidates.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_candidates.tsv) via [semdom_ak_bridge.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_bridge.py) | exists |
| Grammatical-annex parallel (AK kāṇḍa 3 ≈ semdom top-level 9 "Grammar"): 2,592/5,590 synsets (46.4%) vs 168/1,792 domains (9.4%); form-class annex proper (minus nānārtha's 1,995-synset polysemy register) 597 synsets = 10.7% ≈ semdom's 9.4% | counted table in [data/SEMDOM_AK_CROSSWALK_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md), derived live by [semdom_ak_annex_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py) (H774) | exists |
| Dataset citation of record (Zenodo DOI over the ID-pair tables) | kosha manifest row `semdom-amarakosha-crosswalk` in [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) exists; DOI mint = `/data-release` | needs a `/data-release` |
| CDSL consumption demo (`\sd` field in MDF/LIFT exports, H721) | shipped as [csl-standards PR #110](https://github.com/sanskrit-lexicon/csl-standards/pull/110) — cite as deployment evidence in §6 | exists |
| Human validation of model-authored gold (MG spot-check via `/review-sheet`) | not started — the paper can ship with the model-annotator limitation stated, but a ~50-row human spot-check materially strengthens §7 | needs deriving |

## Outline

1. **Introduction** — two semantic taxonomies built 1,500 years apart for the
   same job (organizing a lexicon by meaning); why no classical thesaurus has
   ever been mapped to semdom; what CDSL gains (`\sd` layer, semantic browse
   axis over MW/PWG via their AK citations).
2. **Related work** — GWC-2023 semdom↔WordNet mapping (our bridge, not our
   competitor); UoHyd Amarakosha knowledge structure (Nair & Kulkarni); Sanskrit
   WordNet lineage (Bharati, Kulkarni & Nair; CFILT); SIL's own in-schema
   crosswalk hooks (OcmCodes, LouwNidaCodes) as the methodological precedent —
   a varga code is a third such hook.
3. **Data** — semdom 1,792 domains (CC BY-SA 4.0); AMAR 24 vargas / 5,590 `eid`
   synsets; the ID-pair-only licence route (no AK/UoHyd prose redistributed).
4. **Method** — Level A hand-authored structural map with per-row evidence, 4
   grammatical vargas excluded by design; Level B machine candidates
   (MW gloss → WordNet → GWC bridge) + 200-synset stratified gold,
   dual-blind model annotation (Fable 5 `claude-fable-5` × Opus 4.8
   `claude-opus-4-8`), adjudication protocol incl. the recorded
   adjudicator-shares-a-model-with-A bias.
5. **Results** — coverage; κ table; structure agreement 67.0%; bridge quality
   (the honest negative: candidate generator, not classifier; failure modes —
   incidental gloss words, botanical Latin, polysemous English glosses).
6. **Discussion** — the residual third of structure disagreement (AK's
   associative chaining vs SIL's artifact/activity splits); the
   grammatical-annex parallel (kāṇḍa 3 ≈ semdom top-level 9 — both taxonomies
   needed a formal bucket the semantic scheme could not absorb; counted:
   46.4% of AK synsets vs 9.4% of semdom domains, converging to 10.7% vs 9.4%
   once nānārtha's polysemy register is set aside — semdom absorbs homonymy
   by multiple listing, the one annex bucket AK needed and SIL did not); the
   action-subtree asymmetry (one domain from top-level 7 vs 22 from top-level
   4); deployment: the `\sd` field in CDSL's MDF/LIFT exports.
7. **Limitations** — model annotators only (no human gold yet); English-only
   pivot through MW glosses and semdom's canonical English; single kosha
   (extension path: [sanskrit-kosha/kosha](https://github.com/sanskrit-kosha/kosha)
   corpus); adjudication bias documented in §4.
8. **Conclusion + data availability** — ID-pair tables CC BY-SA 4.0, DOI, kosha
   manifest row, reproduction commands.

## Comparanda / literature

The 2–3 analogs a referee would name — verified in the scoping memo's prior-art
sweep (11-07-2026), not deferred to review time:

- da Costa, Kratochvíl, Saad, Bond et al.,
  [Linking SIL Semantic Domains to Wordnet (GWC 2023)](https://aclanthology.org/2023.gwc-1.38/)
  — the nearest neighbor on the semdom side and our bridge input; A58's delta
  is the classical-thesaurus target + the structure-agreement question.
- Nair & Kulkarni,
  [The Knowledge Structure in Amarakośa (2010)](https://sanskrit.uohyd.ac.in/scl/amarakosha/amarakosha_knowledge_structure.pdf)
  — the nearest neighbor on the kosha side (WordNet-style relations, not a
  field-lexicography taxonomy).
- The earlier [GWC 2014 semdom linking paper](https://aclanthology.org/W14-0106.pdf)
  — establishes the "link semdom to an external resource" genre.

## Venue candidates

GWC / LT4HALA / eLex (per the ARTICLES row); serious shortlist = `/venue-scout`
at readiness 3+.

## Provenance

Scaffolded 12-07-2026 by Fable 5 (`claude-fable-5`) under
[H767](https://github.com/gasyoun/Uprava/blob/main/handoffs/H767-Fable_SanskritLexicography_a58-semdom-ak-paper-scaffold_12.07.26.md)
(`/paper-scaffold A58`). Data built 11-07-2026 by Fable 5 (`claude-fable-5`)
under H742; gold annotators Fable 5 (`claude-fable-5`) and Opus 4.8
(`claude-opus-4-8`).

_Dr. Mārcis Gasūns_
