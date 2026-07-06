# ACL Anthology / NLP-for-DH Monitor

_Created: 04-07-2026 · Last updated: 06-07-2026_

Monthly monitor home for ACL Anthology and adjacent NLP-for-Digital-Humanities
work relevant to the Sanskrit repos.

Each dated section should append new, deduplicated items with:

- citation and URL;
- two- or three-sentence summary;
- `Actionable for us?` verdict;
- concrete follow-up repo/tool when actionable.

Primary topics: translation memory, retrieval-augmented translation, lexically
constrained MT, terminology curation, low-resource lexicons, corpus alignment,
data statements / dataset cards, OCR, normalization, and cultural-heritage NLP.

## 04-07-2026 Setup

- Codex automation `monthly-acl-anthology-sanskrit-nlp-monitor` is active.
- First run should append the first annotated bibliography below this section.

## 04-07-2026 — First annotated bibliography (manual seed run)

Mapped against the **pwg_ru** pipeline's actual subsystems. Each entry ends with
an `Actionable for us?` verdict and the concrete file/decision it touches.

### A. LLM-as-judge / MT evaluation (touches the Fable/Opus judge gate)

1. **Kocmi & Federmann, "GEMBA-MQM: Detecting Translation Quality Error Spans
   with GPT-4", WMT 2023** — [aclanthology.org/2023.wmt-1.64](https://aclanthology.org/2023.wmt-1.64/).
   Reference-free MT quality estimation via a fixed **three-shot** prompt that
   makes the model mark MQM **error spans with severity**, then scores by a
   weighted error count; language-agnostic prompt, SOTA system-ranking, but the
   authors warn against black-box-model dependence in scholarly use.
   `Actionable for us? YES.` Our judge layer ([`FIDELITY_JUDGE_2026-06-30.md`](../FIDELITY_JUDGE_2026-06-30.md),
   [`FABLE_JUDGE_S7_2026-07-02.md`](../FABLE_JUDGE_S7_2026-07-02.md),
   [`fable_s7_verdicts_2026-07-02.json`](../fable_s7_verdicts_2026-07-02.json))
   emits pass/flag verdicts; adopting **error-span + severity** output (not just a
   verdict) gives per-sense localization for the review queue and a reproducible
   fixed-shot prompt. The paper's own caveat = the argument for keeping a
   **human-adjudicated gold** behind the judge (we already do via `/gold-adjudicate`).

2. **"RUBRIC-MQM: Span-Level LLM-as-judge in MT for High-End Models", ACL 2025
   Industry** — [aclanthology.org/2025.acl-industry.12](https://aclanthology.org/2025.acl-industry.12/).
   Extends span-level MQM judging to strong models where errors are rare and
   subtle — exactly our regime (Opus/Fable translating, Fable judging).
   `Actionable for us? MONITOR → PILOT.` Worth a side-by-side against our current
   holistic verdict on the existing `judge_ab_battery_*.jsonl` before committing.

### B. Translation memory & retrieval-augmented translation (touches the TM subsystem)

3. **Cai et al., "Neural Machine Translation with Monolingual Translation
   Memory", ACL 2021 (best-paper)** — [aclanthology.org/2021.acl-long.567](https://aclanthology.org/2021.acl-long.567/).
   Learnable cross-lingual retrieval over a **monolingual** target-side memory,
   removing the bilingual-TM requirement and letting memory scale independently
   of parallel data. `Actionable for us? CONCEPTUAL.` Validates our direction
   ([`src/pilot/translation_memory.py`](../src/pilot/translation_memory.py)) but
   ours is exact/fuzzy content-addressed, not learned-retrieval — the lesson is
   that **target-side monolingual Russian** (e.g. Apresjan-style glosses) is a
   legitimate memory even without a Sa→Ru pair.

4. **Bouthors et al., "Retrieving Examples from Memory for Retrieval Augmented
   NMT: A Systematic Comparison", Findings NAACL 2024** — [aclanthology.org/2024.findings-naacl.190](https://aclanthology.org/2024.findings-naacl.190/).
   Systematically compares **how** RA-NMT selects which memory examples to feed —
   the retrieval policy matters as much as the model. `Actionable for us? YES.`
   Directly informs `best_reusable` / fragment selection in
   [`translation_memory.py`](../src/pilot/translation_memory.py) (see review
   finding on trust-ranked selection) — our "pick the highest-trust exact, else
   best fragment" is a retrieval policy that should be **evaluated**, not assumed.

5. **Hoang et al., "Improving Retrieval Augmented NMT by Controlling Source and
   Fuzzy-Match Interactions", Findings EACL 2023** — [aclanthology.org/2023.findings-eacl.22](https://aclanthology.org/2023.findings-eacl.22/).
   Shows uncontrolled fuzzy matches can **hurt**; gains come from gating how much
   the match influences generation. `Actionable for us? YES — corroborates a
   design choice.` It's the external evidence behind our rule that RU raw
   MW-English suggestions are **blocked** and only curated Sa→Ru terminology rows
   enter prompts ([`TRANSLATION_MEMORY_DECISIONS.md`](../TRANSLATION_MEMORY_DECISIONS.md)).

### C. Dictionary / terminology-constrained prompting (touches terminology injection)

6. **Lu et al., "Chain-of-Dictionary Prompting Elicits Translation in LLMs",
   EMNLP 2024** — [aclanthology.org/2024.emnlp-main.55](https://aclanthology.org/2024.emnlp-main.55/).
   Injecting **chained bilingual-dictionary** entries for source words into the
   prompt materially improves LLM translation of low-resource languages.
   `Actionable for us? HIGH.` This is the published form of what we do ad hoc —
   our curated Sanskrit→Russian terminology TM rows are a dictionary chain. The
   lesson: structure terminology injection **per-headword, multi-hop** and measure
   the lift; candidate A/B on the terminology lane already in the harness.

7. **Hasler et al. / Post & Vilar lineage, "NMT Decoding with Terminology
   Constraints", NAACL 2018** — [aclanthology.org/N18-2081](https://aclanthology.org/N18-2081/).
   Hard target-side terminology enforcement via constrained decoding.
   `Actionable for us? REFERENCE.` We can't constrain-decode a hosted model, but
   it frames why our approach is **soft** (prompt-level) constraint — cite when
   documenting why terminology adherence is checked post-hoc in the audit gate,
   not guaranteed at decode.

### D. Structured-output reliability (touches the StructuredOutput stalls + kill gate)

8. **"JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language
   Models", 2025 (preprint, adjacent)** — [arxiv.org/abs/2501.10868](https://arxiv.org/abs/2501.10868).
   Benchmarks constrained-decoding/JSON-Schema frameworks on **schema coverage,
   efficiency, and the quality cost** of forcing structure — the failure mode
   behind our whole-card StructuredOutput stalls. `Actionable for us? YES.`
   Independent evidence for [`FAILURE_MODES_AND_KILL_GATE_2026-07-04.md`](../FAILURE_MODES_AND_KILL_GATE_2026-07-04.md):
   output volume vs schema complexity drives stalls; supports the **sense-presplit
   trigger** and the wall-clock kill gate as the right structural mitigations.

### E. Sanskrit-specific NLP & venue (prior art + the study's home community)

9. **Nehrdich et al., "One Model is All You Need: ByT5-Sanskrit, a Unified Model
   for Sanskrit NLP Tasks", Findings EMNLP 2024** — [aclanthology.org/2024.findings-emnlp.805](https://aclanthology.org/2024.findings-emnlp.805/).
   A single byte-level model for segmentation, lemmatization, morphosyntax, and
   compound/sandhi splitting — the tasks our grammar layer approximates.
   `Actionable for us? EVALUATE (reuse-first).` Before extending
   [`nominal_grammar.py`](../src/nominal_grammar.py) / sandhi handling, benchmark
   ByT5-Sanskrit as an external morphology/segmentation supplier or validation
   oracle — matches the org "don't reinvent" rule; cross-check with the
   vidyut/DCS crosswalk we already wired.

10. **Proceedings of the 7th International Sanskrit Computational Linguistics
    Symposium (ISCLS 2024)** — [aclanthology.org/2024.iscls-1.0](https://aclanthology.org/2024.iscls-1.0/).
    Includes **word-sense alignment of Sanskrit lexica**, digital editions with
    commentaries, and Sanskrit lexicography tooling. `Actionable for us? YES —
    venue + prior art.` This is the natural **publication venue** for the
    pwg_ru / CDSL-article-comparison study, and the word-sense-alignment papers
    are direct prior art for our sense-level TM and the article-comparison track.

### F. Data documentation (touches the TM datasheet / DOI plan)

11. **Bender & Friedman, "Data Statements for NLP", TACL 2018; Gebru et al.,
    "Datasheets for Datasets"** — data-statement / datasheet standard (curation
    rationale, language variety, annotator demographics, uses, risks).
    `Actionable for us? ALREADY ADOPTED — keep aligned.`
    [`TRANSLATION_MEMORY_DATASHEET.md`](../TRANSLATION_MEMORY_DATASHEET.md) and
    [`schemas/translation_memory.schema.json`](../schemas/translation_memory.schema.json)
    follow this; when the TM gets its DOI ([`DOI_PLAN.md`](../DOI_PLAN.md)),
    cite these as the documentation standard the datasheet implements.

### Follow-ups queued from this run

- **[eval]** Prototype GEMBA-MQM-style **error-span + severity** judge output and
  compare to the current holistic verdict on `judge_ab_battery_*.jsonl` (entry 1/2).
- **[reuse]** Benchmark **ByT5-Sanskrit** as an external morphology/sandhi oracle
  before extending the grammar layer (entry 9).
- **[measure]** Treat `best_reusable` fragment selection as a **retrieval policy**
  and evaluate it, per Bouthors et al. (entry 4).
- **[venue]** Log **ISCLS** as target venue for the pwg_ru study in `Uprava/ARTICLES.md`
  (entry 10).

## 06-07-2026 — Publication-grade layered TM: alignment + speech, and the three-gap map

Added when scoping the **Publication-Grade Sa→Ru Translation Memory** (handoff H215):
making the existing `corpus_lexicon`/`corpus_harvest` spine both an engine-retrieval input
AND a citable resource, layered word+segment, ingesting scholarly *and* oral translations,
with a reliability grade per unit. Two subsystems the 04-07 seed run never reached —
**word/sentence alignment** and **speech-translation alignment** — get their own sections
here, plus the summary map of "which of our three gaps each NLP direction closes".

### The three publication-grade gaps → NLP directions (summary map)

| Our gap | NLP direction it maps to | Canonical work |
|---|---|---|
| verse-level signal → **per-word gloss** ("publication-grade", not "somewhere in the verse") | embedding-based **word alignment** (no training) | SimAlign (Jalili Sabet 2020), awesome-align (Dou & Neubig 2021), eflomal — §G |
| "publication-grade" = **reliability of each unit** | reference-free **Quality Estimation** → A/B/C grade | COMET / COMET-QE (Rei 2020), TransQuest — §B/§A judge lineage + §G below |
| many translators of one verse | **multi-reference** + consensus | MBR-decoding, multi-reference eval — §B |
| TM as **retrieval input** to the LLM engine | retrieval-augmented / fuzzy-match NMT | Neural Fuzzy Repair (Bulté & Tezcan 2019), kNN-MT (Khandelwal 2021) — §B entries 3–5 |
| **oral corpus** (not yet formalized) | **speech-translation alignment** | WhisperX, MFA; MuST-C schema — §H |
| citable, provenance-bearing resource | **data statements / datasheets**, TMX/XLIFF interchange | Bender-Friedman 2018, Gebru 2018 — §F |

### G. Word & sentence alignment (touches L1 word-layer + L0 segment-layer of the TM)

12. **Jalili Sabet et al., "SimAlign: High-Quality Word Alignments without Parallel
    Training Data using Static and Contextualized Embeddings", Findings EMNLP 2020** —
    [aclanthology.org/2020.findings-emnlp.147](https://aclanthology.org/2020.findings-emnlp.147/).
    Word alignment straight from multilingual embeddings, **no training** and no bitext —
    competitive with or better than statistical aligners on low-resource pairs.
    `Actionable for us? YES.` A training-free **cross-check on the DeepSeek word-alignment**
    already in `corpus_lexicon.jsonl` (L1) — run it as a second opinion, store an
    `alignment_confidence`, and let disagreement route a unit to review instead of trusting
    one aligner. Exactly the "verse-level → per-word gloss" upgrade in the gap map.

13. **Dou & Neubig, "Word Alignment by Fine-tuning Embeddings on Parallel Corpora",
    EACL 2021 (awesome-align)** — [aclanthology.org/2021.eacl-main.181](https://aclanthology.org/2021.eacl-main.181/).
    Fine-tunes mBERT on available parallel data for higher alignment quality; supersedes
    SimAlign when even a little Sa↔Ru bitext exists. `Actionable for us? EVALUATE.` We
    *have* aligned pairs (the 1.09M lexicon) — awesome-align could be fine-tuned on them as
    the higher-precision L1 aligner, SimAlign as the zero-shot fallback for new texts.

14. **Thompson & Koehn, "Vecalign: Improved Sentence Alignment in Linear Time and Space",
    EMNLP 2019** + **Feng et al., "Language-agnostic BERT Sentence Embedding (LaBSE)",
    ACL 2022** — [aclanthology.org/D19-1136](https://aclanthology.org/D19-1136/) ·
    [aclanthology.org/2022.acl-long.62](https://aclanthology.org/2022.acl-long.62/).
    Embedding-based **sentence alignment** (Vecalign over LaBSE/LASER vectors), linear-time,
    robust to insertions/deletions. `Actionable for us? YES — enables new ingest.` This is
    how a **plain transcript or handout** (no pre-existing verse alignment) becomes L0 TM
    units: LaBSE-embed both sides, Vecalign to pair Sanskrit ↔ Russian segments. The entry
    path for scholar prose and oral-corpus handouts that Samudra's verse alignment can't cover.

### H. Speech-translation alignment (touches the oral Sa→Ru corpus — new subsystem)

15. **Bain et al., "WhisperX: Time-Accurate Speech Transcription of Long-Form Audio",
    Interspeech 2023** — [arxiv.org/abs/2303.00747](https://arxiv.org/abs/2303.00747) ·
    forced alignment via **Montreal Forced Aligner (MFA)**, McAuliffe et al., Interspeech 2017,
    [montreal-forced-aligner.readthedocs.io](https://montreal-forced-aligner.readthedocs.io/).
    Whisper ASR + phoneme-level **forced alignment** gives word-level timestamps on long
    recordings. `Actionable for us? YES — the oral-corpus pipeline.` Lecture/reading audio →
    Whisper (RU) → WhisperX/MFA timestamps → sentence segmentation → LaBSE-align (§G) to the
    read Sanskrit → L0 units with `modality: oral` + time anchors. Formalizes the
    "Устный санскритско-русский корпус"; coordinate with the `spoken-sanskrit-corpus` repo (H174).

16. **Di Gangi et al., "MuST-C: a Multilingual Speech Translation Corpus", NAACL 2019** —
    [aclanthology.org/N19-1202](https://aclanthology.org/N19-1202/).
    The reference **schema** for a speech-translation corpus: aligned (audio segment,
    transcript, translation) triples with speaker/segment metadata. `Actionable for us?
    SCHEMA MODEL.` Adopt its triple layout for the oral corpus so it is a recognizable
    speech-translation dataset at release, not a bespoke format — feeds the FAIR/DOI plan.

_Dr. Mārcis Gasūns_
