# PWG->RU research-grade capability roadmap: 30 additive layers

_Created: 09-07-2026_

This roadmap turns the four H335 capability questions into a wider, ranked
research programme for `pwg_ru`. It is additive: the baseline remains the
existing pipeline audit (`PIPELINE_CAPABILITY_AUDIT_2026-07-08.md`), the ACL/TM
crosswalk (`ACL_TM_CROSSWALK_MEMO.md`), and the current evidence/government/genre
decisions (`DECISIONS_PIPELINE_CAPABILITY_H335.md`). The ordering below favors
publishable, measurable claims over feature breadth.

Each card has the same contract:

- **Claim**: a falsifiable sentence.
- **Data**: local feed or external acquisition need.
- **Metric**: the measurement that makes the claim reviewable.
- **Acceptance**: the minimum useful pass/fail threshold.
- **Dependency flag**: `local-only`, `needs gold sample`, `needs external text`,
  `rights-gated`, or `cross-repo`.

## ACL method spine

| Method family | Anchor | Local use |
|---|---|---|
| Word alignment | [awesome-align](https://aclanthology.org/2021.eacl-main.181/), [SimAlign](https://aclanthology.org/2020.findings-emnlp.147/) | Calibrate word-pair confidence instead of relying on a flat threshold. |
| MT/QE | [COMET](https://aclanthology.org/2020.emnlp-main.213/) | Validate or replace `tm_grade.py` proxy QE against human grades. |
| Prose bitext mining | [LaBSE](https://aclanthology.org/2022.acl-long.62/), [margin mining](https://aclanthology.org/P19-1309/), [Vecalign](https://aclanthology.org/D19-1136/) | Recover aligned Sa/Ru prose where verse anchors are absent. |
| Sanskrit preprocessing | [Hellwig & Nehrdich 2018](https://aclanthology.org/D18-1295/) | Add segmentation/compound handling before alignment and WSD. |
| WSD | [Raganato et al. 2017](https://aclanthology.org/E17-1010/) | Evaluate token-in-context PWG sense prediction with MFS baselines. |
| BLI | [Glavas et al. 2019](https://aclanthology.org/P19-1070/) | Evaluate `corpus_lexicon` intrinsically via P@1/MRR. |
| Annotation reliability | [Artstein & Poesio 2008](https://aclanthology.org/J08-4004/) | Require kappa/alpha on human gold slices and taxonomy crosswalks. |
| Semantic change | [SemEval 2020 Task 1](https://aclanthology.org/2020.semeval-1.1/) | Reframe PWG sense strata as diachronic lexical-semantic evidence. |
| Release documentation | [Data Statements](https://aclanthology.org/Q18-1041/) | Make every release artifact carry a reproducible data statement. |

## Ranked capability cards

### 1. COMET-QE calibration for A/B/C translation grades

- **Claim**: Reference-free QE scores correlate with human A/B/C grades strongly
  enough to replace or reweight the hand proxy in `tm_grade.py`.
- **Data**: `build_l0.py` output, current `tm_grade.py` grades, a frozen human
  A/B/C gold slice.
- **Metric**: Spearman rho and macro-F1 after thresholding into A/B/C.
- **Acceptance**: rho >= 0.50 against the adjudicated sample, or a documented
  negative result showing Sanskrit->Russian QE transfer fails.
- **Dependency flag**: `needs gold sample`.

### 2. Awesome-align/SimAlign agreement as a word-alignment confidence gate

- **Claim**: Word pairs where an independent aligner agrees with the DeepSeek
  alignment have higher precision than disagreements.
- **Data**: `corpus_lexicon.jsonl`, `tm_align.py` output, committed precision
  samples under `pwg_ru/`.
- **Metric**: precision by agreement bucket, with confidence intervals.
- **Acceptance**: the agreement-positive bucket beats the no-agreement bucket by
  >= 10 precision points, or the flat gate remains justified.
- **Dependency flag**: `local-only`.

### 3. BLI evaluation of `corpus_lexicon` with P@1/MRR

- **Claim**: The 1.09M-row Sa->Ru alignment lexicon performs above a
  most-frequent-translation baseline on bilingual lexicon induction.
- **Data**: `corpus_lexicon.jsonl`, a 300-item Sa->Ru gold set drawn from
  dictionary-backed entries.
- **Metric**: P@1, P@5, MRR, and baseline delta.
- **Acceptance**: P@1 beats the most-frequent baseline and error classes are
  reported by POS/genre/polysemy band.
- **Dependency flag**: `needs gold sample`.

### 4. Token-in-context PWG sense disambiguation for DCS passages

- **Claim**: A DCS token's PWG sense is predictable from local context above a
  most-frequent-sense baseline.
- **Data**: DCS token contexts from VisualDCS, translated PWG sense inventory,
  gold sense labels for high-frequency polysemous lemmas.
- **Metric**: accuracy, macro-F1, and delta over MFS.
- **Acceptance**: >= 10 point absolute accuracy gain over MFS on the frozen set,
  or a published failure analysis of the confusable senses.
- **Dependency flag**: `cross-repo`, `needs gold sample`.

### 5. Most-frequent-sense baseline per lemma

- **Claim**: A simple MFS baseline is necessary to keep WSD and learner-ranking
  claims honest.
- **Data**: store rows grouped by `key1`, DCS frequency dimensions, existing
  per-sense genre/stratum signals.
- **Metric**: coverage of lemmas with a computed MFS and baseline accuracy on
  any available sense-labeled sample.
- **Acceptance**: every lemma with >= 2 senses and DCS frequency evidence gets a
  deterministic MFS candidate plus an `unknown` outcome when evidence is absent.
- **Dependency flag**: `local-only`.

### 6. Multi-translator consensus score for grade-A TM candidates

- **Claim**: Cross-translator agreement predicts safer grade-A TM rows.
- **Data**: multi-reference verse groups from `corpus_lexicon.jsonl` and L0
  segment outputs.
- **Metric**: agreement rate by key/segment and precision against adjudicated
  rows.
- **Acceptance**: consensus-positive rows show higher human grade distribution
  than singleton rows, or consensus is kept as a provenance note only.
- **Dependency flag**: `local-only`, `rights-gated` for release.

### 7. Variant-reading extractor from systematic translator divergence

- **Claim**: Repeated disagreement among reputable translators identifies
  genuine sense variation rather than mere noise.
- **Data**: multi-reference corpus groups, translator/source metadata, PWG sense
  inventory.
- **Metric**: cluster purity on a reviewed sample and count of reusable variant
  readings.
- **Acceptance**: at least 50 reviewed divergence clusters are classified with
  kappa >= 0.60 and mapped to PWG senses or "translation style" buckets.
- **Dependency flag**: `needs gold sample`, `rights-gated`.

### 8. Per-sense confidence score

- **Claim**: A composite confidence score over evidence, genre, government, and
  TM agreement predicts review priority better than any single signal.
- **Data**: in-store `evidence[]`, `government`, `genre`, TM grades, audit
  verdicts.
- **Metric**: AUC for predicting human or audit failures.
- **Acceptance**: composite AUC beats the best single feature by >= 0.05 on a
  frozen validation slice.
- **Dependency flag**: `local-only`, `needs gold sample` for final calibration.

### 9. Contradiction lane for sources that actively disagree

- **Claim**: Distinguishing contradiction from silence improves evidence
  readability and catches risky senses.
- **Data**: `corpus_gate.build_card` lanes, `annotate_evidence.py` output,
  source gloss tokens.
- **Metric**: precision of `contradicts` on a spot-check sample.
- **Acceptance**: >= 90% precision on a 50-item reviewed sample; otherwise keep
  contradictions as `needs_review`.
- **Dependency flag**: `local-only`, `needs gold sample`.

### 10. Per-sense diachronic first/last attestation band

- **Claim**: PWG senses can be dated more informatively as first/last citation
  bands, not only as coarse Renou states.
- **Data**: per-sense `<ls>` citations, `ls_source_map.json`, `sense_stratum.py`
  output.
- **Metric**: coverage and distribution of dated senses.
- **Acceptance**: every sense with a mapped citation gets `date_min/date_max`
  and unmapped citations are counted separately.
- **Dependency flag**: `local-only`.

### 11. Lexical semantic-change detector over period/genre strata

- **Claim**: Sense distribution across periods reveals measurable semantic
  change or register narrowing.
- **Data**: per-sense date bands, DCS frequency/genre dimensions, PWG sense
  counts.
- **Metric**: Jensen-Shannon divergence or comparable period-distribution shift
  score, with reviewed top cases.
- **Acceptance**: top 100 shifted lemmas produce >= 70% substantively meaningful
  candidates on review.
- **Dependency flag**: `cross-repo`, `needs gold sample`.

### 12. "Still alive" score for senses found in live/corpus usage

- **Claim**: DCS and other corpus evidence can rank PWG senses by likely
  current or corpus-attested usefulness.
- **Data**: DCS attestation, per-sense evidence, corpus examples, genre fallback.
- **Metric**: coverage and reviewer agreement that high-score senses are more
  useful for readers.
- **Acceptance**: score computed for all senses with evidence; unknown remains
  explicit for senses with no corpus route.
- **Dependency flag**: `local-only`, `cross-repo`.

### 13. Dual-model mined-pair acceptance score

- **Claim**: Two independent model judgments reduce mined-pair false positives
  at an acceptable recall cost.
- **Data**: 10,132 mined pairs, existing precision samples, second-model verdicts.
- **Metric**: precision/recall by acceptance policy.
- **Acceptance**: dual-agreement policy reaches the target precision for
  publication-grade promotion, or fallback to human adjudication is documented.
- **Dependency flag**: `local-only`, `needs gold sample`.

### 14. Bicleaner-style bitext filter for mined Sa/Ru pairs

- **Claim**: A learned or feature-based bitext filter generalizes better than
  hard-coded thresholds for mined pairs.
- **Data**: mined pair features, accepted/rejected examples, source metadata.
- **Metric**: ROC-AUC and precision@k.
- **Acceptance**: filter improves precision@k over the current threshold gate
  without hiding known proper-name/list-scope failures.
- **Dependency flag**: `needs gold sample`.

### 15. Segment-level provenance for every TMX row

- **Claim**: Every exported TMX row can explain its source, method, grade,
  rights state, and model involvement.
- **Data**: `build_tmx.py`, `tm_grade.py`, source weights, rights metadata.
- **Metric**: provenance-field coverage and schema validation.
- **Acceptance**: 100% of exportable rows validate; rights-gated rows are
  excluded or marked non-public.
- **Dependency flag**: `local-only`, `rights-gated`.

### 16. Independent bilingual-lexicon drift detector

- **Claim**: A model-independent bilingual lexicon can flag alignment drift and
  hallucinated Sa->Ru pairs.
- **Data**: corpus frequencies, embeddings or external BLI tooling, sampled
  alignment rows.
- **Metric**: disagreement precision on reviewed flags.
- **Acceptance**: flagged disagreements have >= 50% actionable value; otherwise
  the detector is deferred as too noisy.
- **Dependency flag**: `needs external text/tooling`, `needs gold sample`.

### 17. Bad-reuse detector for stale/rejected fragment TM reuse

- **Claim**: Fragment TM reuse can be audited for stale, rejected, or
  superseded content before it reaches new cards.
- **Data**: fragment TM sidecars, denylist, `window_selftest.py` fixtures,
  audit/requeue logs.
- **Metric**: number of unsafe reuse candidates caught and false-positive rate.
- **Acceptance**: detector catches all seeded stale/rejected fixtures and emits
  zero false positives on known-good sidecars.
- **Dependency flag**: `local-only`.

### 18. LaBSE margin-mining path for unanchored prose

- **Claim**: Embedding margin mining recovers useful Sa/Ru pairs from prose
  texts where verse anchors are unavailable.
- **Data**: rights-clear Sanskrit/Russian prose pairs; Leitan-style clean pilots
  where available.
- **Metric**: precision@k on mined segment pairs.
- **Acceptance**: precision@100 is high enough to justify a larger Track-A
  prose ingestion run; otherwise keep prose blocked on manual anchoring.
- **Dependency flag**: `needs external text`, `rights-gated`.

### 19. Vecalign-style long-document prose alignment

- **Claim**: Long-document alignment improves continuity and recall over
  independent segment mining for prose translations.
- **Data**: same prose candidates as card 18, plus paragraph boundaries.
- **Metric**: alignment precision/recall on hand-checked contiguous passages.
- **Acceptance**: Vecalign or equivalent beats plain nearest-neighbor mining on
  a pilot text.
- **Dependency flag**: `needs external text`, `rights-gated`.

### 20. Rights-aware ingestion queue for candidate source texts

- **Claim**: Source acquisition can be managed as a structured queue so research
  candidates do not silently become publishable data.
- **Data**: candidate works, source URL, rights status, owner, intended use,
  blocker notes.
- **Metric**: queue completeness and number of candidates with resolved status.
- **Acceptance**: every external-data capability points to an item with a rights
  state: `public-domain`, `permissioned`, `private-use`, `blocked`, or `unknown`.
- **Dependency flag**: `rights-gated`.

### 21. Parallel-passage finder by PWG lemma

- **Claim**: For a queried PWG lemma, the system can surface aligned Sa/Ru
  passages that instantiate the sense evidence.
- **Data**: `corpus_lexicon.jsonl`, SamudraManthanam `corpus.db`, PWG store.
- **Metric**: retrieval precision@k and passage coverage by lemma.
- **Acceptance**: top-5 passages for common lemmas are useful in >= 80% of a
  reviewed sample.
- **Dependency flag**: `local-only`, `cross-repo`.

### 22. Sanskrit compound segmentation lane before alignment/mining

- **Claim**: Sanskrit segmentation before alignment improves recall for compounds
  and derived forms.
- **Data**: Sanskrit text, `sanskrit-util` normalization, optional validation via
  Samsaadhanii/Heritage outputs.
- **Metric**: recall gain on compounds and false-segmentation rate.
- **Acceptance**: compound recall improves without exceeding an agreed false
  segmentation ceiling on a reviewed sample.
- **Dependency flag**: `cross-repo`, `needs gold sample`.

### 23. Morphosyntactic compatibility check

- **Claim**: Sanskrit case/government evidence can catch incompatible Russian
  renderings or missing government notes.
- **Data**: structured `government`, source German `de`, Sanskrit morphology
  where available, Russian output fields.
- **Metric**: precision of mismatch flags.
- **Acceptance**: >= 85% of high-severity mismatch flags are real review issues.
- **Dependency flag**: `local-only`, `cross-repo`.

### 24. Proper-name/transliteration classifier

- **Claim**: A classifier separating names/transliterations from lexical
  translations reduces false mined-pair promotions.
- **Data**: specialist name glossaries, mined-pair failures, source metadata.
- **Metric**: F1 on name/transliteration vs lexical classes.
- **Acceptance**: classifier catches the known proper-name failure class with
  >= 90% recall on a labelled sample.
- **Dependency flag**: `needs gold sample`.

### 25. Inter-annotator agreement dashboard for gold slices

- **Claim**: Every human-labelled evaluation slice should report agreement before
  it is used as ground truth.
- **Data**: review-sheet decisions, gold JSONL/CSV files, adjudication records.
- **Metric**: Cohen's kappa, Krippendorff's alpha where applicable, label
  distribution.
- **Acceptance**: dashboard renders agreement for all active gold slices and
  blocks "gold" status when agreement/adjudication is missing.
- **Dependency flag**: `local-only`, `needs gold sample`.

### 26. Data Statement / Datasheet generator for releases

- **Claim**: Release artifacts can emit a consistent data statement from their
  manifests and provenance fields.
- **Data**: release manifests, `DATASHEET.ru.md`, source metadata, rights state.
- **Metric**: required-section coverage and manual correction count.
- **Acceptance**: generated draft covers all Bender/Friedman-style fields that
  are knowable from repo metadata, with explicit `unknown` for the rest.
- **Dependency flag**: `local-only`, `rights-gated`.

### 27. OntoLex/PROV-O upgrade for sense/evidence provenance

- **Claim**: PWG->RU sense, evidence, genre, government, and provenance fields
  can be exported as a queryable LOD graph without losing store information.
- **Data**: existing `export_lod.py` / `release/ontolex.ttl` direction, store
  rows, H350/csl-standards boundary.
- **Metric**: round-trip field coverage and SHACL validation.
- **Acceptance**: all core card fields are either mapped losslessly or listed as
  intentionally unmapped; graph passes the csl-standards profile.
- **Dependency flag**: `cross-repo`.

### 28. SPARQL-style query layer over senses, genre, evidence, and government

- **Claim**: Research questions such as "all kavya senses supported by Kossovich
  with locative government" can be answered over the exported graph or a local
  query facade.
- **Data**: LOD graph or store-derived query index, `annotation_report.py`,
  genre/evidence/government fields.
- **Metric**: query coverage and manually verified result precision.
- **Acceptance**: at least 10 named research queries return reproducible results
  with documented unknown/missing-data semantics.
- **Dependency flag**: `local-only`, `cross-repo`.

### 29. Capability observatory

- **Claim**: A single observatory can show which research layers exist, their
  coverage, confidence, blockers, and owner boundaries.
- **Data**: this roadmap, H335 audit, local scripts, release manifests,
  cross-repo hub pointers.
- **Metric**: coverage of roadmap cards with status and last verification date.
- **Acceptance**: all 30 cards display status (`not-started`, `prototype`,
  `validated`, `blocked`, `shipped`) and a dependency flag.
- **Dependency flag**: `local-only`.

### 30. Research-paper matrix

- **Claim**: The roadmap can be turned into a paper agenda where every
  experiment has a claim, ACL precedent, dataset, metric, and expected figure.
- **Data**: this roadmap, `ACL_TM_CROSSWALK_MEMO.md`,
  `EPISTEMIC_REACH_MEMO.md`, article tracker.
- **Metric**: number of complete experiment rows and readiness score per paper
  candidate.
- **Acceptance**: at least three coherent paper packages emerge: one TM/QE
  paper, one sense/genre/WSD paper, and one LOD/provenance data paper.
- **Dependency flag**: `local-only`, `cross-repo`.

## Work packages

| Package | Cards | First artifact | Why first |
|---|---:|---|---|
| Evaluation spine | 1, 2, 3, 5, 25 | gold-sample manifest + metrics stubs | Turns existing claims into publishable measurements. |
| Sense intelligence | 4, 8, 9, 10, 11, 12, 23 | per-sense feature table | Builds directly on H335 evidence/government/genre. |
| TM safety and release | 6, 7, 13, 14, 15, 16, 17, 24, 26 | TM provenance/quality dashboard | Reduces false promotion and makes release claims auditable. |
| External acquisition | 18, 19, 20, 21, 22 | rights-aware source queue | Keeps high-upside prose mining honest. |
| Graph and publication layer | 27, 28, 29, 30 | capability observatory | Makes the research programme visible and queryable. |

## Defaults for implementers

- Reuse `sanskrit-util` for normalization/transliteration; do not add another
  SLP1 helper.
- Consume VisualDCS outputs for DCS frequency/morphology; do not re-parse CoNLL-U.
- Keep OntoLex/SPARQL modelling aligned with the `csl-standards` ownership
  boundary; local RussianTranslation code may emit the graph inputs/generator.
- Treat rights as a first-class field. Any external text without clearance can
  support private evaluation only, not public release.
- Use explicit `unknown`/`unmapped` outcomes. Do not collapse absent evidence
  into negative evidence.

