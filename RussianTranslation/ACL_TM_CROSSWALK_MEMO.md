# Publication-Grade Sa→Ru TM — ACL-Anthology method crosswalk + research agenda

_Created: 08-07-2026 · Last updated: 08-07-2026_

Repo-anchored `/dh-memo` for [`SanskritLexicography/RussianTranslation`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation), scoped to the **Publication-Grade Sanskrit→Russian Translation Memory** ([H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md)) and its multi-source ingestion: the 1.09M verse-aligned [`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py), the 10,132-pair running-text `mined` tier ([H186/H224](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py)), and the oral corpus ([H174](https://github.com/gasyoun/Uprava/blob/main/handoffs/H174-Opus_spoken-sanskrit-corpus_spoken_sanskrit_corpus_scaffold_04.07.26.md)).

**Primary deliverable:** an evidence-grade **ACL-Anthology crosswalk** (§4) — 22 methods, every anthology ID live-verified against [aclanthology.org](https://aclanthology.org), mapped to the concrete component each one upgrades. This deepens the inline method map already sketched in H215 into a citable table a methods section can lean on. Memo-only: no pipeline runs, no data mutation; every item ends in a spec + a future starter line.

---

## 1. Executive summary

Five highest-leverage moves, one line each:

1. **[P0] Adopt `awesome-align` ([#2](https://aclanthology.org/2021.eacl-main.181/)) as a calibrated confidence gate, not just a cross-check** — [`tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) already runs it; turn its DeepSeek-agreement rate into the per-pair signal that replaces the flat 97% threshold (TM-H1).
2. **[P0] Validate/replace the proxy-QE in [`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py) with real COMET-QE ([#7](https://aclanthology.org/2020.emnlp-main.213/))** — the A/B/C "publication-grade" stamp currently rests on a hand-weighted proxy; COMET-QE is the reference-free, ACL-standard grader (TM-H2).
3. **[P1] Route the H308-"blocked" prose parallel texts through LaBSE margin mining ([#4](https://aclanthology.org/2022.acl-long.62/)/[#5](https://aclanthology.org/P19-1309/))** — Kādambarī/Panchatantra have no verse numbers to anchor on; embedding-margin mining recovers pairs anchoring cannot (TM-H6).
4. **[P1] Surface the one committed, unsurfaced diachronic layer — [`corpus_strata.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_strata.json)** (121 works, 24 genres, −1125→+1374 CE) — no viz exists over it today; it is the axis for gloss-density-over-time (TM-H4, Viz-1).
5. **[P2] Operationalize multi-translator consensus (MBR-style, [#20](https://aclanthology.org/2020.coling-main.398/))** — agreement → grade A; systematic divergence localizes genuine polysemy and publishes as *variant readings*, not errors (TM-H5).

Everything below is Claim → Evidence → committed-Source; unverifiable reuse assets are flagged, not asserted.

## 2. New testable hypotheses

Proposed IDs `TM-H1..7`. Nearest existing hypotheses: the Renou cluster `H1–H7` in [`RENOU_HYPOTHESES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_HYPOTHESES.md) (register-scoped, not TM-scoped) and the scattered pipeline IDs `H151/H186/H215/H290`; there is **no** central TM hypothesis registry, so each below cites its nearest neighbour + delta.

**TM-H1 — Independent-aligner agreement predicts DeepSeek L1 precision.**
Word-pairs where `awesome-align` ([#2](https://aclanthology.org/2021.eacl-main.181/)) or SimAlign ([#1](https://aclanthology.org/2020.findings-emnlp.147/)) agrees with the DeepSeek alignment are measurably higher-precision than disagreements; agreement rate is a usable per-pair confidence replacing the flat gate.
· **Data:** L1 pairs (corpus_lexicon.jsonl, gitignored bulk) + [`tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py) output; gold = the two **committed** precision samples ([`running_text_mining_precision_sample.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample.jsonl), [`_scale.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample_scale.jsonl)), frozen + Cohen's κ on a re-adjudication.
· **Method:** agreement-bucket → adjudicated P/R/F1.
· **Research read:** alignment-ensemble QE for LLM-produced word alignments (WSC/ACL-publishable). **Learner read:** "which glosses to trust."
· **Nearest:** `tm_align.py` exists as a *cross-check* only (H215 Slice 3) — **delta:** turn it into a calibrated gate. · Readiness: **high** (both inputs exist).

**TM-H2 — COMET-QE segment scores correlate with human A/B/C grades.**
Reference-free COMET-QE ([#7](https://aclanthology.org/2020.emnlp-main.213/)) / TransQuest ([#8](https://aclanthology.org/2020.coling-main.445/)) on L0 segment pairs predicts the composite grade well enough to replace the hand-weighted proxy.
· **Data:** L0 pairs from [`build_l0.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_l0.py) + a `/gold-adjudicate` grade sample (reuse H136 gold).
· **Method:** COMET-QE vs κ-adjudicated grade, Spearman ρ; report calibration.
· **Research read:** does a Latin/none-Sanskrit-trained QE model transfer to Sa→Ru? (a genuine low-resource-QE result). **Learner read:** a trustworthiness bar per sense card.
· **Nearest:** [`tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py) uses a **proxy** QE (H215 Slice 2) — **delta:** validate/replace with real COMET-QE. · Readiness: **medium** (needs a gold grade sample frozen).

**TM-H3 — Dual-model adjudication beats single-model at fixed recall on the mined tier.**
The 07-07-2026 MG ruling (a second model confirms each mined pair) drops the two known noise modes (proper-name transliteration, list-scoping) measurably vs the single-model 97%/80% baseline.
· **Data:** the 10,132 `mined` pairs (gitignored) + the two committed precision samples as the labeled validation set.
· **Method:** dual-model agree-gate; precision/recall vs the H224 single-model baseline table in [`RUNNING_TEXT_MINING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RUNNING_TEXT_MINING.md).
· **Research read:** LLM-as-judge inter-model agreement as a bitext filter (cf. Bicleaner [#11](https://aclanthology.org/2020.eamt-1.31/)). **Learner read:** the promotion gate that makes the tier citable.
· **Nearest:** H186/H224 single-model gate — **delta:** the promotion mechanism itself. · Readiness: **high**.

**TM-H4 — Gloss density varies by genre/period, not randomly (diachronic).**
Mined term-glosses per 1k tokens is higher in medieval term-encyclopedias than in Vedic saṃhitā — lexical *explicitness* is register-conditioned.
· **Data:** `mined` per-source counts × the **committed** [`corpus_strata.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_strata.json) (`genre_code`, `period`, `date_median`).
· **Method:** gloss-density regression on `genre_code`/`period`; report with 95% CIs already in the strata file.
· **Research read:** diachronic lexical-explicitness in commentary vs primary text (DH-publishable). **Learner read:** "where explained terms live."
· **Nearest:** none — genuinely new. · Readiness: **high** (strata committed; needs mined counts).

**TM-H5 — Multi-translator consensus marks grade-A senses; divergence localizes polysemy.**
For verses with ≥2 Russian translators (the Gītā has ~14 in the corpus), cross-translator agreement on an SLP1 key → grade A; *systematic* divergence flags genuinely polysemous keys to publish as variant readings, not errors.
· **Data:** corpus_lexicon.jsonl restricted to multi-reference `group`s.
· **Method:** per-key cross-translator agreement (MBR/consensus framing, [#20](https://aclanthology.org/2020.coling-main.398/)); output a polysemy census.
· **Research read:** consensus-as-confidence + a variant-reading dataset (scholarly value). **Learner read:** "this word has several accepted senses."
· **Nearest:** H215 mentions consensus/MBR conceptually — **delta:** operationalize + emit the census. · Readiness: **medium**.

**TM-H6 — LaBSE margin mining recovers pairs from the H308-"blocked" prose texts.**
Kādambarī/Panchatantra/Hitopadeśa prose (no verse numbers) yields ≥ a useful precision@k of parallel segments via LaBSE ([#4](https://aclanthology.org/2022.acl-long.62/)) + margin criterion ([#5](https://aclanthology.org/P19-1309/)) / Vecalign ([#3](https://aclanthology.org/D19-1136/)), unblocking Track A without manual verse anchoring.
· **Data:** GRETIL TEI Sanskrit + a rights-clear RU edition (to acquire — see H308); pilot on Leitan Sundarakāṇḍa (rights-clean).
· **Method:** LaBSE embed → margin mining → precision@k on a hand-checked sample.
· **Research read:** embedding bitext mining for a low-resource classical language (WSC-publishable). **Learner read:** unlocks more parallel reading material.
· **Nearest:** [H308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H308-Sonnet_SamudraManthanam_gretil-tei-ingestion-scoping_07.07.26.md) declares prose "blocked on verse anchor" — **delta:** the embedding path around the block. · Readiness: **low** (needs RU sources; boundary = SamudraManthanam corpus_builder owns ingestion).

**TM-H7 — An unsupervised VecMap lexicon is a DeepSeek-independent drift detector.**
A VecMap ([#17](https://aclanthology.org/P18-1073/)) Sa↔Ru lexicon over the corpus agrees with corpus_lexicon on high-frequency keys; disagreements flag either DeepSeek hallucination (the 166k-invention failure class) or genuine rare senses worth review.
· **Data:** corpus_lexicon.jsonl frequencies + embeddings.
· **Method:** VecMap induction; agreement@freq-band vs corpus_lexicon; route disagreements.
· **Research read:** a second, model-independent audit channel. **Learner read:** none primary → **secondary/deferred** (audit-only; kept but flagged). · Readiness: **medium**.

## 3. Visualisation proposals

Repo stack today: standalone **HTML** (dashboards + research explorers — e.g. [`src/pilot/dashboard/index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/dashboard/index.html), [`research/affix_explorer.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/affix_explorer.html)); **no** Observable/Docusaurus, **no** committed `figures/` dir. All proposals below are HTML/JS in that idiom; chart styling per the `dataviz` skill.

**Viz-1 — Diachronic gloss-density heatmap** _(new; over the orphaned `corpus_strata.json`; diachronic)_. `genre_code` (rows) × `period` (cols), cell = mined glosses per 1k tokens. Loader: `corpus_strata.json` + mined counts. **Effort S.**
```
            Ṛgvedic  Vedic  Epic/eClass  Classical  Medieval
Veda          ░░       ▒▒        ·           ·          ·
Epic           ·        ·        ▓▓          ▒▒         ·
Kāvya          ·        ·         ·          ▓▓         ▓▓
Śāstra(comm)   ·        ·         ·          ▓▓         ██   ← densest
```
· Research read: register-conditioned explicitness (TM-H4). · Learner read: "where explained terms cluster."

**Viz-2 — Aligner-agreement precision curve** _(new)_. X = awesome-align∩DeepSeek agreement bucket, Y = adjudicated precision; overlay the 97% flat line the curve should beat. Loader: `tm_align.py` output + precision samples. **Effort S.** (TM-H1) · Research: alignment-ensemble QE. · Learner: the trust dial.

**Viz-3 — A/B/C grade distribution by source × modality** _(upgrade [`src/pilot/dashboard/index.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/dashboard/index.html))_. Stacked bars, one per source, split written/oral, A/B/C colour. Loader: graded TMX + [`tm_source_weights.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_source_weights.json) (committed). **Effort M.** · Research: provenance-trust transparency. · Learner: which sources are gold.

**Viz-4 — Translator-consensus polysemy explorer** _(new; interactive, in the `affix_explorer.html` idiom)_. Enter an SLP1 key → show its N Russian renderings across translators, agreement highlighted, divergences flagged as variant readings. **Effort M.** (TM-H5) · Research: variant-reading dataset UI. · Learner: "one word, several accepted senses."

**Viz-5 — Multi-source TM provenance flow (Sankey)** _(new; pedagogical)_. corpus / mined / suggestion feeds → G1 guards → G2 dual-model → G3 rights → G4 grade → TMX. Loader: static counts from the pipeline. **Effort S.** · Research: a one-glance data-statement figure. · Learner: how the TM is actually built.

**Viz-6 — COMET-QE vs human-grade calibration scatter** _(new)_. Each point = one adjudicated segment; X = COMET-QE, Y = human grade; report ρ + a threshold band. **Effort M.** (TM-H2) · Research: QE-transfer calibration plot. · Learner: none primary → paired with Viz-3 for the learner read.

## 4. ACL-Anthology method crosswalk (the deliverable)

Every ID below was **live-verified against aclanthology.org** (Explore agent, 08-07-2026 — page fetched, ID/title/authors/venue confirmed). Grouped by method family. "Applies to" distinguishes **committed-now** data from **needs-derivation**. Nearest-repo-thing gives the gap delta.

### 4a. Word alignment (the L1 layer)
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **SimAlign** — Jalili Sabet, Dufter, Yvon, Schütze | [`2020.findings-emnlp.147`](https://aclanthology.org/2020.findings-emnlp.147/) · Findings-EMNLP 2020 | L1 pairs (corpus_lexicon, needs-derivation for scoring) | TM-H1, Viz-2 | `tm_align.py` names it as cross-check — no precision calibration yet |
| **awesome-align** — Dou & Neubig | [`2021.eacl-main.181`](https://aclanthology.org/2021.eacl-main.181/) · EACL 2021 | same | TM-H1 (primary), the P0 gate | same — **delta: make it the gate** |
| **VecMap** (unsup. bilingual lexicon) — Artetxe, Labaka, Agirre | [`P18-1073`](https://aclanthology.org/P18-1073/) · ACL 2018 | corpus_lexicon frequencies | TM-H7 drift audit | none — new audit channel |
| **eflomal** (MCMC alignment) — Östling & Tiedemann | NOT-IN-ACL · PBML 106, 2016 · [pdf](https://ufal.mff.cuni.cz/pbml/106/art-ostling-tiedemann.pdf) | same | cheap statistical baseline for TM-H1 | none |

### 4b. Sentence/bitext mining (unblocks Track A prose)
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **LaBSE** — Feng, Yang, Cer, Arivazhagan, Wang | [`2022.acl-long.62`](https://aclanthology.org/2022.acl-long.62/) · ACL 2022 | GRETIL TEI + RU editions (needs-acquisition) | TM-H6, P1 | none — H308 anchors on verse numbers only |
| **Margin-based mining** — Artetxe & Schwenk | [`P19-1309`](https://aclanthology.org/P19-1309/) · ACL 2019 | same | TM-H6 scoring criterion | none |
| **LASER / massively-multilingual embeddings** — Artetxe & Schwenk | [`Q19-1038`](https://aclanthology.org/Q19-1038/) · TACL 2019 | same | TM-H6 backbone option | none |
| **Vecalign** (linear-time sent. align) — Thompson & Koehn | [`D19-1136`](https://aclanthology.org/D19-1136/) · EMNLP-IJCNLP 2019 | same | TM-H6 alignment step | none |
| **WikiMatrix** — Schwenk, Chaudhary, Sun … | [`2021.eacl-main.115`](https://aclanthology.org/2021.eacl-main.115/) · EACL 2021 | method precedent | mining-recipe reference | n/a |
| **CCMatrix** — Schwenk, Wenzek, Edunov … | [`2021.acl-long.507`](https://aclanthology.org/2021.acl-long.507/) · ACL-IJCNLP 2021 | method precedent | scale precedent | n/a |

### 4c. Parallel-corpus filtering (the mined-tier gate)
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **Bicleaner** — Ramírez-Sánchez, Zaragoza-Bernabeu, Bañón, Ortiz Rojas | [`2020.eamt-1.31`](https://aclanthology.org/2020.eamt-1.31/) · EAMT 2020 | mined tier (10,132) | TM-H3 principled per-pair scoring | H224 flat 97% threshold — **delta: learned score** |
| **Bicleaner AI** — Zaragoza-Bernabeu, Ramírez-Sánchez, Bañón, Ortiz Rojas | [`2022.lrec-1.87`](https://aclanthology.org/2022.lrec-1.87/) · LREC 2022 | same | TM-H3 neural variant | same |
| **WMT18 Parallel Corpus Filtering** — Koehn, Khayrallah, Heafield, Forcada | [`W18-6453`](https://aclanthology.org/W18-6453/) · WMT 2018 | same | evaluation protocol for the gate | none |

### 4d. Reference-free Quality Estimation (the A/B/C grade)
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **COMET** — Rei, Stewart, Farinha, Lavie | [`2020.emnlp-main.213`](https://aclanthology.org/2020.emnlp-main.213/) · EMNLP 2020 | L0 segments (build_l0) | TM-H2, Viz-6, P0 | `tm_grade.py` proxy-QE — **delta: real QE** |
| **TransQuest** — Ranasinghe, Orasan, Mitkov | [`2020.coling-main.445`](https://aclanthology.org/2020.coling-main.445/) · COLING 2020 | same | TM-H2 alternative QE | same |

### 4e. Retrieval-TM / consensus / decoding
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **Neural Fuzzy Repair** — Bulté & Tezcan | [`P19-1175`](https://aclanthology.org/P19-1175/) · ACL 2019 | graded TMX as retrieval input | the "TM feeds the engine" claim in H215 | H215 states it; not yet measured |
| **MBR / "Is MAP Decoding All You Need?"** — Eikema & Aziz | [`2020.coling-main.398`](https://aclanthology.org/2020.coling-main.398/) · COLING 2020 | multi-reference `group`s | TM-H5 consensus framing, Viz-4 | H215 mentions consensus — delta: operationalize |
| **kNN-MT** — Khandelwal, Fan, Jurafsky, Zettlemoyer, Lewis | NOT-IN-ACL · ICLR 2021 · [openreview](https://openreview.net/forum?id=7wCBOfJ8hJM) | future engine retrieval | retrieval-augmentation roadmap | deferred (§7) |

### 4f. Provenance / data statements (the publication wrapper)
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **Data Statements** — Bender & Friedman | [`Q18-1041`](https://aclanthology.org/Q18-1041/) · TACL 2018 | the release (H215 Slice 5) | the dataset descriptor | [`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md) exists — align to the Bender/Friedman schema |
| **Datasheets for Datasets** — Gebru et al. | NOT-IN-ACL · CACM 2021 · [doi](https://cacm.acm.org/research/datasheets-for-datasets/) | same | complementary schema | same |

### 4g. Low-resource + Sanskrit NLP (domain grounding)
| Method → ACL paper | Anthology ID · venue/yr | Applies to | Enables | Nearest repo thing (delta) |
|---|---|---|---|---|
| **Sanskrit Word Segmentation (char-RNN/CNN)** — Hellwig & Nehrdich | [`D18-1295`](https://aclanthology.org/D18-1295/) · EMNLP 2018 | Sanskrit-side tokenization | better L1 keys for prose (TM-H6) | SLP1 `form_key` normalization — delta: real segmentation for compounds |
| **"Free as in Free Word Order" (EBM)** — Krishna, Santra, Bandaru … Goyal | [`D18-1276`](https://aclanthology.org/D18-1276/) · EMNLP 2018 | Sanskrit morphosyntax | segmentation/parse precedent | none |
| **Digital Corpus of Sanskrit (DCS)** — Hellwig | NOT-IN-ACL · online resource · [dcs](http://www.sanskrit-linguistics.org/dcs/) | frequency/lemma layer | **boundary → VisualDCS** (§7) | consumed via kosha, not re-derived |

### What to adopt first, and why
**COMET-QE (#7) and awesome-align (#2), in that order** — both are P0 because they retrofit *existing* components with ACL-standard rigor at low cost: `tm_grade.py`'s grade and `tm_align.py`'s cross-check already exist and already have the plumbing; swapping a proxy for COMET-QE and promoting the aligner to a calibrated gate turns two hand-rolled heuristics into defensible, publishable measurements without new data acquisition. **LaBSE margin mining (#4/#5) is the highest-*upside* but P1**, because it depends on acquiring rights-clear RU editions (H308 boundary). Bicleaner (#11) is the natural third — it generalizes the dual-model gate (TM-H3) into a learned filter. The provenance pair (#14, Datasheets) is the release-day wrapper, aligned to the already-present [`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md).

## 5. New sections mining additional layers

**§A — Diachronic stratum surface** (the orphan-data section). Surfaces `corpus_strata.json`, committed but un-visualized. Claim ("gloss explicitness rises in commentary/medieval strata") → Evidence (gloss-density × genre_code/period) → Source (`corpus_strata.json` + mined counts). ETL: a small aggregator; **owned here**. Research + learner reads = TM-H4/Viz-1.

**§B — Alignment-confidence layer.** Surfaces `tm_align.py` agreement as a first-class per-pair field. Claim ("agreement predicts precision") → Evidence (agreement-bucket P/R) → Source (tm_align output + precision samples). ETL: extend `tm_align.py` to persist a confidence column; **owned here**. Reads = TM-H1/Viz-2.

**§C — Variant-readings / polysemy layer.** Surfaces multi-translator divergence as scholarly output. Claim ("divergence = polysemy, not error") → Evidence (per-key cross-translator agreement) → Source (corpus_lexicon multi-ref groups). ETL: a consensus aggregator; **owned here**. Reads = TM-H5/Viz-4. **Boundary:** the Sanskrit lemma/frequency backbone (DCS) is **VisualDCS's**, consumed via the kosha manifest, never re-derived here.

## 6. Prioritised build backlog

Build handoffs are **not** minted this session (memo-only). Big items already own handoffs — cite them; small new items get placeholder starter lines.

| Rank | Item | Leverage | Effort | Deps | Owner repo | Tier | Starter line |
|---|---|---|---|---|---|---|---|
| 1 | COMET-QE into `tm_grade.py` (P0, TM-H2, Viz-6) | High | M | gold grade sample | RussianTranslation | Sonnet 5 (`claude-sonnet-5`) build; Opus judge | folds into [H215 Slice 2](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md) |
| 2 | awesome-align calibrated gate (P0, TM-H1, Viz-2) | High | M | tm_align output | RussianTranslation | Sonnet 5 (`claude-sonnet-5`) | folds into [H215 Slice 3](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md) |
| 3 | Dual-model mined-tier gate (TM-H3) | High | M | mined tier | RussianTranslation | Opus 4.8 (`claude-opus-4-8`) | the retired-into-H215 07-07 ruling; runs under H215 |
| 4 | Diachronic gloss-density section+viz (TM-H4, Viz-1) | Med | S | mined counts | RussianTranslation | Sonnet 5 (`claude-sonnet-5`) | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Sonnet_RussianTranslation_diachronic-gloss-density_DD.MM.YY.md and execute it.` |
| 5 | LaBSE margin mining for prose Track A (TM-H6) | High-upside | L | RU editions (H308) | SamudraManthanam + RussianTranslation | Opus 4.8 (`claude-opus-4-8`) | runs under [H308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H308-Sonnet_SamudraManthanam_gretil-tei-ingestion-scoping_07.07.26.md) |
| 6 | Consensus/polysemy layer+explorer (TM-H5, Viz-4) | Med | M | multi-ref groups | RussianTranslation | Sonnet 5 (`claude-sonnet-5`) | `Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-Sonnet_RussianTranslation_translator-consensus-polysemy_DD.MM.YY.md and execute it.` |
| 7 | Provenance flow Sankey (Viz-5) | Low | S | pipeline counts | RussianTranslation | Sonnet 5 (`claude-sonnet-5`) | bundle with rank 4 |

## 7. Deferred / out-of-scope

- **kNN-MT (#10)** — ICLR, not ACL; retrieval-augmented *decoding* is an engine-side roadmap item, not a TM-build task. Park.
- **VecMap drift audit (TM-H7)** — audit-only, no learner read; keep as a secondary channel, low priority.
- **DCS integration (#21)** — **boundary → VisualDCS**; consume the lemma/frequency layer via the [kosha manifest](https://github.com/sanskrit-lexicon/kosha/blob/main/data/manifest/datasets.json), never re-derive here.
- **TEI/OntoLex export of the TMX** — **boundary → csl-standards**; the TMX 1.4b export ([`build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py)) stays here, but any OntoLex-Lemon modelling routes to csl-standards.
- **Corpus_builder prose ingestion** — **boundary → SamudraManthanam** (owns `web/corpus_builder/`, per H308).
- **Unverified reuse assets:** none asserted above without a fetched confirmation; `corpus_lexicon.mined.jsonl` is **absent on disk** (only the declared output path) and gitignored — treated as needs-generation, never as a surfaceable layer.

---

## @DECIDE / @DO surfaced (mirror to GTD)
- **@DO** — freeze a `/gold-adjudicate` grade sample so TM-H2 (COMET-QE calibration) has ground truth (human-gated).
- **@DECIDE** — per-translator rights clearance (Гринцер/Сыркин/Потапова) gates whether any graded TMX from mined literary sources can be released (H215 Slice 5; already an active outreach workstream per the 07-07-2026 ruling).

_Provenance: analysis + authoring by Opus 4.8 (`claude-opus-4-8`), 08-07-2026. All 22 ACL IDs live-verified against [aclanthology.org](https://aclanthology.org) by an Explore agent (08-07-2026, pages fetched). Repo data ground-truth by an Explore recon pass (08-07-2026). Corpus alignment model = DeepSeek `deepseek-chat`; pipeline translate/judge = Claude Sonnet 5 (`claude-sonnet-5`) + Opus 4.8 (`claude-opus-4-8`); strata dating = Dharmamitra + Renou genre tags._

_Dr. Mārcis Gasūns_
