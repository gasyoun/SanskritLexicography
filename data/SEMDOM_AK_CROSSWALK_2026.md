# semdom ↔ Amarakosha crosswalk — Level A varga map + Level B synset gold pilot

_Created: 11-07-2026 · Last updated: 12-07-2026_

The first crosswalk between SIL's semantic domains
([semdom.org](https://semdom.org), 1,792 hierarchical domains, data CC BY-SA 4.0)
and a classical thesaurus — the Amarakosha
([sanskrit-lexicon/AMAR amar.txt](https://github.com/sanskrit-lexicon/AMAR/blob/master/amar.txt),
24 vargas, 5,590 `eid` synsets, ~6th c. CE). Built by
[H742](https://github.com/gasyoun/Uprava/blob/main/handoffs/H742-Fable_SanskritLexicography_semdom-kosha-crosswalk-build_11.07.26.md)
per the GO scoping memo
[SEMDOM_KOSHA_CROSSWALK_SCOPING.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SEMDOM_KOSHA_CROSSWALK_SCOPING.md)
(H725). Paper: A58 in the Uprava pipeline. Consumer:
[H721](https://github.com/gasyoun/Uprava/blob/main/handoffs/H721-Sonnet_csl-standards_mdf-spec-refine-lift-export_11.07.26.md)
(`\sd` field of the MDF/LIFT exports).

**Licensing:** all committed tables are **ID pairs only** (semdom codes/GUIDs ↔
varga IDs ↔ AK `eid`s) — no AK/UoHyd prose content — released CC BY-SA 4.0
(share-alike inherited from the semdom side), citing AMAR (GPL v3) as source.

## Files (committed)

| File | What it is |
|---|---|
| [semdom_varga_crosswalk.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_varga_crosswalk.csv) | **Level A**: 20 thematic vargas → semdom level-2/3 domains, many-to-many, hand-authored with per-row evidence; the 4 grammatical vargas (nānārtha, avyaya, liṅgādi, saṁkīrṇa tail) are excluded by design — Amarakosha mixes semantic and grammatical organizing principles, SIL's taxonomy is purely semantic. |
| [semdom_varga_crosswalk.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_varga_crosswalk.py) | Level A validator/emitter (checks codes/GUIDs against `semdom.json`, synset counts against `amar.txt`). |
| [semdom_ak_candidates.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_candidates.tsv) | **Level B**: all 5,590 synsets, top-6 machine candidate domains each (`code:votes`, semicolon-joined). Candidates are HINTS, not labels — see the precision table below. |
| [semdom_ak_gold.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_gold.tsv) | **Gold**: 200-synset stratified sample, adjudicated leaf-domain label per `eid` (`source` = agreed / adjudicated-A / adjudicated-B). |
| [semdom_ak_annotator_A.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annotator_A.tsv), [semdom_ak_annotator_B.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annotator_B.tsv) | The two independent blind annotation passes (code, confidence 1–3, short note). |
| [semdom_ak_disagreements.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_disagreements.tsv) | The 64 A≠B items with both codes + notes — adjudication audit trail. |
| [semdom_ak_bridge.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_bridge.py) | Candidate generator: AK lemmas → MW glosses → WordNet noun synsets → GWC-2023 semdom↔WordNet bridge → ranked codes; also emits the stratified gold packet. |
| [semdom_ak_metrics.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_metrics.py) | Evaluation: Cohen's κ (`kappa` mode), bridge precision / coverage / structure agreement vs gold (`metrics` mode). |
| [semdom_ak_annex_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py) | Grammatical-annex parallel counted (AK kāṇḍa 3 vs semdom top-level 9) — emits the annex table below; reuses the two loaders from `semdom_varga_crosswalk.py`. |

**Inputs NOT committed** (fetch locally to reproduce): `data/semdom.json` from
[sillsdev/LfMerge](https://github.com/sillsdev/LfMerge/blob/master/data/semantic-domains/semdom.json);
`data/wn-links-semdom-words-all.tsv` (10 MB) from
[lmorgadodacosta/sil-semantic-domains-wordnet-mapping](https://github.com/lmorgadodacosta/sil-semantic-domains-wordnet-mapping)
(CC BY-SA 4.0, [GWC 2023 paper](https://aclanthology.org/2023.gwc-1.38/));
`../AMAR/amar.txt`; `../csl-orig/v02/mw/mw.txt`; Princeton WordNet via `nltk`.
`semdom_ak_gold_sample.json` (the annotation packet) is a derived working file
containing MW gloss snippets — regenerate with `semdom_ak_bridge.py`, not released.

## Method (Level B)

Candidates: each synset's SLP1 lemmas looked up in MW (first 3 entries per key);
gloss content words (stop-listed, ≤40 per lemma, ≤12 lemmas) → WordNet noun
synsets (first 3 senses) → GWC-2023 bridge → semdom codes ranked by count of
distinct supporting gloss words, top 6 kept.

Gold: 200 synsets stratified ≥5 per thematic varga (vyomavarga has only 2
synsets total and contributes 2), proportional above the floor, seeded RNG
(42). Dual-annotated by two independent, mutually blind model annotators under
one written protocol — Annotator A: Fable 5 (`claude-fable-5`), Annotator B:
Opus 4.8 (`claude-opus-4-8`) — free to keep a machine candidate, write in any
semdom code, or vote NONE. Disagreements adjudicated by Fable 5
(`claude-fable-5`); adjudication favoured the more specific domain covering the
whole synset and the varga-contextual reading (per protocol), which resolved
60/64 to A and 4/64 to B — the known bias of adjudicator sharing a model with
annotator A is recorded here and in the audit trail.

## Results (11-07-2026, Fable 5 `claude-fable-5`)

### Coverage

| Metric | Value |
|---|---|
| AK synsets with an MW gloss | 5,472 / 5,590 (97.9%) |
| AK synsets with ≥1 candidate domain | 5,391 / 5,590 (96.4%) |
| semdom domains receiving ≥1 AK **candidate** (noisy upper bound) | 1,196 / 1,792 (66.7%) |
| Distinct domains in the 200-synset **gold** | 142 |

### Inter-annotator agreement (n = 200)

| Level | Agreement | Cohen's κ |
|---|---|---|
| Exact leaf code | 68.0% | 0.677 |
| Coarse (level-2 prefix) | 81.5% | 0.806 |

Annotator write-in rates (code outside the machine top-6): A 111/200 (55.5%),
B 84/200 (42.0%). NONE votes: 0 from both — every sampled synset found a
plausible SIL domain, i.e. the 1,792-domain inventory has no coverage hole for
this 6th-century material on the evidence of this sample.

### Bridge quality vs gold (n = 200, no NONEs)

| Metric | Exact | Coarse (level-2) |
|---|---|---|
| Top-1 candidate correct | 17.5% | 27.5% |
| Gold within top-6 candidates | 45.0% | 58.5% |

The MW-gloss → WordNet → GWC-bridge chain is a useful **candidate generator**
(more than half the gold labels sit in the top-6 at level-2) but far from an
auto-classifier — human/model judgment authored the majority of gold labels.
Main failure mode: candidates key on incidental gloss words (mythological
narrative, botanical Latin absent from WordNet, polysemous English glosses)
rather than the synset's concept.

### Structure agreement

134/200 (67.0%) of gold leaf domains fall inside their varga's Level A subtree
set — a 1,500-year-old semantic organization and a modern field-lexicography
taxonomy agree on two-thirds of synset placements at the section level. The
residual third is dominated by (a) AK's associative chaining (e.g. plants
listed inside the human-body chapter as products/measures), and (b) SIL's
artifact/activity splits cutting across AK's substance-first grouping.

### The grammatical vargas and semdom's own Grammar annex

The four excluded kāṇḍa-3 vargas (2,592 synsets, 46% of the kosha — adjectives,
miscellany, homonyms, indeclinables) organize words by form and lexical
relation, not meaning. The sharper version of that finding: **SIL did the same
thing.** Semdom's top-level 9 "Grammar" (9.1 General words … 9.2 Part of
speech) is a non-semantic annex bolted onto a semantic taxonomy for
elicitation completeness — formally parallel to Amarakosha's kāṇḍa 3:
avyayavargaḥ ≈ 9.2.2/9.2.5–9.2.7 (adverbs, conjunctions, particles,
interjections); viśeṣyanighnavargaḥ ≈ 9.1.4/9.2.1 (adjectives). Both
taxonomies, 1,500 years apart, needed a formal bucket the semantic scheme
could not absorb. Counted (12-07-2026, H774, every number derived live by
[semdom_ak_annex_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/data/semdom_ak_annex_table.py)):

| AK grammatical varga | synsets | % of kosha | semdom 9.x counterpart (subtree) | domains | % of semdom |
|---|---|---|---|---|---|
| AK-3.1 viśeṣyanighnavargaḥ | 326 | 5.8% | 9.1.4 General adjectives + 9.2.1 Adjectives | 2 | 0.1% |
| AK-3.2 saṅkīrṇavargaḥ | 168 | 3.0% | — (no counterpart: a miscellany tail, not a category) | 0 | 0% |
| AK-3.3 nānārthavargaḥ | 1,995 | 35.7% | — (no counterpart: semdom handles polysemy by multiple listing, not a bucket) | 0 | 0% |
| AK-3.4 avyayavargaḥ | 103 | 1.8% | 9.2.2 Adverbs + 9.2.5 Conjunctions + 9.2.6 Particles + 9.2.7 Interjections | 8 | 0.4% |
| **kāṇḍa 3 total** | **2,592** | **46.4%** | **semdom top-level 9 (whole annex)** | **168** | **9.4%** |

Two asymmetries in the table are findings, not gaps. Homonymy is the bucket AK
needed and semdom did not: nānārtha alone is 1,995 synsets (35.7% of the
kosha), while semdom absorbs polysemy structurally by listing a word under
several domains. And with that polysemy register set aside, the **form-class
annex proper is almost the same size in both taxonomies**: AK 597/5,590
synsets (10.7%) vs semdom 168/1,792 domains (9.4%) — two semantic schemes,
1,500 years apart, spending the same ~10% of their inventory on the formal
residue their organizing principle could not absorb. These parallels are
documented here and deliberately kept out of the Level A CSV, which stays
purely semantic (top-level 9 therefore takes 0 pairs). A second asymmetry from the Level A
totals: semdom top-level 7 "Physical actions" is touched by exactly one
domain (7.2.4 Travel) — a noun thesaurus has almost no varga-level footprint
in semdom's verb-oriented action subtree, while its social-world coverage
(top-level 4: 22 distinct domains) is the densest of all.

### Gold-sample allocation per varga (200 total)

| Varga | n | Varga | n |
|---|---|---|---|
| AK-1.1 svarga | 10 | AK-2.1 bhūmi | 7 |
| AK-1.2 vyoma | 2 | AK-2.2 pura | 7 |
| AK-1.3 dik | 9 | AK-2.3 śaila | 6 |
| AK-1.4 kāla | 8 | AK-2.4 vanauṣadhi | 18 |
| AK-1.5 dhī | 7 | AK-2.5 siṁhādi | 10 |
| AK-1.6 śabdādi | 8 | AK-2.6 manuṣya | 22 |
| AK-1.7 nāṭya | 10 | AK-2.7 brahma | 12 |
| AK-1.8 pātālabhogi | 6 | AK-2.8 kṣatriya | 17 |
| AK-1.9 naraka | 5 | AK-2.9 vaiśya | 17 |
| AK-1.10 vāri | 10 | AK-2.10 śūdra | 9 |

## Reproduce

```sh
python data/semdom_varga_crosswalk.py          # validate Level A
python data/semdom_ak_bridge.py                # candidates + gold packet
python data/semdom_ak_metrics.py kappa         # A vs B agreement
python data/semdom_ak_metrics.py metrics       # bridge/coverage/structure vs gold
python data/semdom_ak_annex_table.py           # grammatical-annex parallel table
```

_Dr. Mārcis Gasūns_
