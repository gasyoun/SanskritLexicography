# ACL Anthology / NLP-for-DH Monitor

_Created: 04-07-2026 · Last updated: 04-07-2026_

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

_Dr. Mārcis Gasūns_
