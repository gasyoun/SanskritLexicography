# DharmaMitra AI-MT failure taxonomy — form vs. published, mapped onto pwg_ru

_Created: 02-07-2026 · Last updated: 02-07-2026_

**Purpose:** MG decided (02-07-2026) to adopt DharmaMitra's failure vocabulary as shared terminology
for the PWG→RU/EN judging rubric. This memo separates the **form** (not citable — an intake
questionnaire) from DharmaMitra's **published** work (citable), and maps both onto our own 7-class
rubric used in [`FU1_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md)
and the [`FABLE_JUDGE_S7_2026-07-02.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FABLE_JUDGE_S7_2026-07-02.md)
gold-sample judgment.

## 1. The two DharmaMitra sources are not the same taxonomy

| Source | Status | What it contains |
|---|---|---|
| Pre-Workshop Google Form ([saved copy](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/Pre-Workshop_Questionnaire.md), [analysis](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/Pre-Workshop_Questionnaire_ANALYSIS.md)) | **Not citable** — an unpublished intake questionnaire, not a peer-reviewed instrument | 8 informal failure classes + a breakdown-level scale (word/term → sentence → paragraph/passage → whole-document) + a post-editing-burden scale |
| Nehrdich & Keutzer, **"MITRA: A Large-Scale Parallel Corpus and Multilingual Pretrained Language Model for Machine Translation and Semantic Retrieval for Pāli, Sanskrit, Buddhist Chinese, and Tibetan"**, arXiv:2601.06400 ([abs](https://arxiv.org/abs/2601.06400), [PDF](https://arxiv.org/pdf/2601.06400)) | **Citable** | Evaluates with **GEMBA-MQM** (Kocmi & Federmann's GPT-based MQM error-span detector, [arXiv:2310.13988](https://arxiv.org/pdf/2310.13988)), scored via Gemini 2.0 Flash. MQM error categories used: **accuracy** {addition, mistranslation, omission, untranslated text}, **fluency** {character encoding, grammar, inconsistency, punctuation, register, spelling}, **style** {awkward}, **terminology** {inappropriate for context, inconsistent use}, plus non-translation / other / no-error. |
| Nehrdich & Keutzer (same team), **"From Outliers to Errors: Auditing Pali-to-English LLM Translations with Multi-Reference Adjudication"**, arXiv:2606.01136 ([abs](https://arxiv.org/abs/2606.01136), [PDF](https://arxiv.org/pdf/2606.01136)) | **Citable** | A closer methodological analog to our own pipeline: multi-reference embedding-drift triage + blinded LLM judge-panel adjudication (calibrated against an author-adjudicated validation set), reporting **major-error rate** by drift band. Dominant major-error categories named: **omission/truncation**, **doctrinal term errors**. |

**Conclusion:** the form's 8-class list is DharmaMitra's *internal, informal* framing for a workshop
audience; their **published** evaluation instrument is standard **MQM** (via GEMBA-MQM), not the
form's categories. Cite MQM/GEMBA-MQM (arXiv:2601.06400, arXiv:2606.01136; underlying method
Freitag et al. MQM, Kocmi & Federmann GEMBA-MQM arXiv:2310.13988) in any A-paper. **Never cite the
Google Form** — it has no DOI, no peer review, and was an unpublished draft MG saw as a workshop
invitee.

## 2. Three-way crosswalk: our rubric ⇄ form category ⇄ published (MQM) category

Our 7 classes come from the [FU1 gold-sample judgment](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FABLE_JUDGE_S7_2026-07-02.md#failure-classes-all-severities).

| our class | form category (not citable) | published MQM category (citable) | breakdown level (form scale) |
|---|---|---|---|
| `addition` | hallucinated or invented content | accuracy: **addition** | word/term → sentence |
| `mw-tm-contamination` | hallucinated or invented content | accuracy: **addition** (cross-source leak is our own refinement — no MQM sub-tag distinguishes provenance) | word/term |
| `term-mistranslation` | vocabulary/terminology handling; handling of ambiguous or polysemous terms | terminology: inappropriate for context; accuracy: **mistranslation** | word/term |
| `grammar` | grammar and syntax errors | fluency: **grammar** | sentence |
| `omission` | *(no form category — the form has no explicit omission item)* | accuracy: **omission** | sentence → paragraph |
| `register-drift` | register/tone | fluency: **register** | sentence → passage |
| `markup-loss` | *(no form or MQM counterpart — an artifact of our `{%..%}`/XML markup, not a general MT failure mode)* | *(none)* | word/term |

Form categories with **no counterpart in our rubric or in MQM**: *lack of context awareness across
sentences* and *lack of consistency/coherence across a passage*. These describe document-level
failures our per-sense/per-card judging does not currently score (FU1 judges at sense-row/card
granularity, not passage-level); they are candidates for a future document-level judge pass, not a
rename of an existing class.

## 3. What this changes (and doesn't)

- **Documentation-only.** The crosswalk in [`FU1_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md)
  is vocabulary alignment for methods sections, not a rubric change. No gate semantics changed, no
  judging re-run.
- **Citable framing going forward:** when an A-paper's methods section describes the pwg_ru/PWG→EN
  failure taxonomy, cite MQM/GEMBA-MQM and the two Nehrdich & Keutzer papers above as the field's
  comparable published instrument — not the DharmaMitra form.
- **The form stays useful internally** (it is what motivated this crosswalk and named the two
  document-level gaps in §2), but per [Uprava FINDINGS §14](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  and the [six-takeaway analysis](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/Pre-Workshop_Questionnaire_ANALYSIS.md),
  it is not a publication-grade source.

## 4. Feeds

- **Methods vocabulary** — [`FU1_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md)
  §"Failure taxonomy — DharmaMitra crosswalk", and any future A-paper drawing on the pwg_ru/PWG→EN
  translation work (currently scoped as **A42**/**A43** in [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) —
  no dedicated pwg_ru translation-methods paper exists yet; this memo is the citation-ready source
  for whichever paper first describes the judging pipeline in print).
- **[`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) reusable framing block** —
  the "updatable verified dictionary" paragraph already points here for citation-grade taxonomy use;
  this memo is that pointer's target.

_Dr. Mārcis Gasūns_
