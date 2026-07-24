---
paper_id: A42
title: "A Word-Aligned Sanskrit→Russian Corpus Lexicon: a 1.09-Million-Pair Open Alignment Resource"
status: draft (skeleton, 3/5) — scaffolded 2026-06-26, advanced 2026-07-08 (H353)
readiness: 3/5
venue: "Письменные памятники Востока / Вопросы языкознания (ВЯ) / CLARIN-LRE / ComputEL / LoResMT (added 04-07-2026, ACL Anthology scan — both live, on-topic for low-resource classical-language alignment)"
author: "Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru — venue + byline to confirm (a human decides)"
data_source: "RussianTranslation/src/corpus_lexicon.jsonl (built & verified; 1,091,528 alignments at the 2026-06-26 recompute; 1,093,391 after the H309 targeted re-harvest of 08-07-2026) — evaluation figures from RussianTranslation/gold/PR_MEMO_A42.md (P 84.4% / R 95.4% / coverage 98.9%, LLM-estimated, human packets pending)"
---

# A Word-Aligned Sanskrit→Russian Corpus Lexicon: a 1.09-Million-Pair Open Alignment Resource

_Created: 26-06-2026 · Last updated: 08-07-2026_

> **Draft status (2026-07-08, H353; scaffolded 2026-06-26).** Manuscript skeleton built
> directly on the verified data asset
> [`RussianTranslation/src/corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)
> (the JSONL itself is gitignored; link is to its committed builder) and the evaluation
> memo [PR_MEMO_A42.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/PR_MEMO_A42.md) —
> the single citation point for every evaluation number in this paper. Scale/shape
> figures were recomputed from the JSONL on 2026-06-26; evaluation figures follow the
> memo as of 08-07-2026 (post-[H309](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H309-Sonnet_RussianTranslation_corpus-lexicon-reharvest-gaps_07.07.26.md)).
> **§2 Related work written 04-07-2026**
> ([PR #145](https://github.com/gasyoun/SanskritLexicography/pull/145), ACL Anthology
> scan; citations verified).
> **Advanced 08-07-2026 (readiness 2/5 → 3/5, H353, Fable 5 `claude-fable-5`):** the
> measured recall figures (H136 measurement + H309 targeted fix) folded in as the
> headline evaluation with the "LLM-estimated, human packets pending" caveat
> first-class (§4.4–§4.6); reproducibility limits of an LLM-induced, non-deterministic
> resource stated explicitly, in contrast with A41's deterministic extraction (§3.6);
> claim→artifact inventory (§9) and companion-paper scope block (§10) added;
> References (§11); all links upgraded to full blob URLs.
> **Open before submission:** (1) **[@DO]** document the IP / redistribution rights of
> the underlying modern Russian translations before any public deposit (what the 1.09M
> pairs derive from and what ships openly — §6, §8); (2) **[@DO]** mint a Zenodo DOI
> once the rights scope is fixed; (3) venue + byline/ORCID (a human decides); (4) both
> precision and recall are **LLM-judged estimates until the human gold packets land**
> (annotator recruit is a standing @DO) — the frozen scaffolds are committed and
> re-checkable, but no number below may be cited as print-grade before that pass.

## Abstract

We present a word-aligned Sanskrit→Russian lexicon of **1,091,528 token-pair
alignments** drawn from **116 works** spanning roughly **−1125 to 1374 CE**, the
first large, openly-documented Sanskrit-to-Russian alignment resource. Each
alignment records a Sanskrit content word (in SLP1 and IAST surface form) and the
Russian word or phrase that renders it *in a specific translated passage*, stamped
with the work's period, genre, and median date, and tagged by whether the Russian
evidence is a running **translation** (990,499 rows, 90.7%) or a **commentary** note
(101,029 rows, 9.3%). The resource is *induced*, not hand-aligned: for each
verse-aligned Sanskrit↔Russian pair in an existing parallel corpus, a large language
model is prompted, under a strict JSON contract and a Cyrillic-presence guard, to
emit the per-word renderings attested in that translation; a length-preserving SLP1
normaliser then provides a deterministic join key into the dictionary side. On frozen
stratified samples, estimated **precision is 84.4%** (95% CI 80.0–87.9, n=320
alignments) and estimated **word-level recall is 95.4%** (95% CI 92.2–97.3, n=280
translated content lemmata) within processed groups, with deterministic **group-level coverage
of 98.9%** (58,897 eligible groups); precision and recall are LLM-judged estimates
pending a human gold pass over the committed scaffolds. The contribution is not a new
alignment algorithm — induced bitext alignment is a mature method — but the
construction, stratification, evaluation, and open documentation of a
**diachronically labelled Sanskrit→Russian lexical-alignment resource** that did
not previously exist, together with the empirical per-headword distribution of
attested Russian renderings it makes computable.

## 1. Introduction

Bilingual lexicography between Sanskrit and Russian has a respectable printed
tradition — Kossowich (1854), Knauer (1908), Smirnov, Frisch, and above all
Kochergina (1987) — but it has no *corpus-attested* layer: no resource records, for a
given Sanskrit word, *which Russian renderings actually occur in translated text, in
which works, of which period.* Sanskrit-side parallel data is comparatively rich (the
DCS corpus; the verse-aligned Sanskrit↔Russian corpus behind `samskrtam.ru`), but the
alignment between the two languages has lived implicitly inside translations rather
than as a queryable lexical object.

This paper documents a resource that makes that alignment explicit at the word level.
Starting from a verse-aligned Sanskrit↔Russian parallel corpus, we induce, per
aligned pair, a mapping from each Sanskrit content word to its Russian rendering in
that translation, and accumulate the result into a single SLP1-keyed lexicon. The
output is a 1.09-million-row table in which a query for a headword returns its
empirical distribution of attested Russian equivalents across the corpus — for
example `agni` renders as the proper name *Агни* 1,111 times and as the common noun
*огонь* ('fire', plus its inflected forms) several hundred more.

Our claims:

1. **A first large, open Sa→Ru alignment resource.** 1,091,528 word-pair
   alignments over 116 works, openly documented and reproducible from committed code.
2. **Diachronically and generically stratified.** Every row carries period, genre,
   and median-date stamps and a translation-vs-commentary tag, so the resource
   supports diachronic and register-aware queries, not just a flat gloss list.
3. **A consumable join, not a black box.** A length-preserving SLP1 key
   (`form_key()`) joins the lexicon deterministically to dictionary headwords; the
   resource already feeds an independent dictionary-verification gate.
4. **An evaluated draft layer, honestly labelled.** Precision, recall, and coverage
   are measured on frozen, committed, re-checkable stratified scaffolds — and
   explicitly flagged as LLM-judged estimates until a human pass confirms them.

The alignment is **LLM-induced**: per-pair, JSON-constrained, and guarded against
fabrication, rather than produced by a deterministic statistical aligner. We describe
it by its artifact and method and treat the particular model as a build detail
recorded in the changelog, not as the contribution.

## 2. Related work

Position against three axes. (a) **Parallel-corpus and word-alignment resources** for
Sanskrit and for low/medium-resource pairs: the DCS corpus and lemma data, the
verse-aligned `samskrtam.ru` Sanskrit↔Russian corpus this work is induced from, and
statistical/neural aligners (IBM models, `fast_align`, `awesome-align`) versus
LLM-prompted alignment. The closest published analogue is Nehrdich's **SansTib**, a
Sanskrit–Tibetan parallel corpus of 317,289 automatically sentence-aligned pairs with
a bilingual sentence-embedding model (LREC 2022,
[2022.lrec-1.724](https://aclanthology.org/2022.lrec-1.724/)) — a large classical-
Sanskrit-paired alignment resource for a different target language, built by
embedding-based sentence alignment rather than LLM-prompted word alignment; the two
resources differ in granularity (sentence vs. word) and method but share the goal of
turning an implicit bitext into a queryable alignment asset. Punia et al.'s
Sanskrit–English NMT work (ICON 2020,
[2020.icon-main.30](https://aclanthology.org/2020.icon-main.30/)) similarly releases
a parallel/aligned Sanskrit corpus alongside its translation model and is a useful
prior-resource comparison point on the English side, as is **Itihasa**, the
93,000-pair Sanskrit–English śloka parallel corpus (WAT 2021,
[2021.wat-1.22](https://aclanthology.org/2021.wat-1.22/)) that functions as the
field's standard MT-benchmarking scale reference — worth citing alongside our own
1.09M-alignment figure to situate the resource's scale. Sentence/word-alignment work
for Sanskrit does exist in the Anthology, but as corpus-construction papers built on
automatic/embedding alignment, not LLM-prompted alignment framed as the method
itself; the closest methodological analogue for that framing is Mao & Yu's LLM
fine-tuning with statistical-alignment-derived contrastive signal for unseen
low-resource MT (LoResMT 2024,
[2024.loresmt-1.1](https://aclanthology.org/2024.loresmt-1.1/)). No ACL Anthology
paper targets Sanskrit→Russian specifically or frames LLM-induced (vs.
statistical/embedding) word alignment as the explicit contribution for a classical
Indic language — this genuine gap, not a search miss, is what this paper's novelty
claim rests on (rule-based Sanskrit→Hindi MT and generic English–Hindi
word-alignment work were checked and found too off-topic to cite as direct
comparators). A distinct but sibling precedent is Patel & Kulkarni's **Word Sense
Alignment of Sanskrit Lexica** (ISCLS 2024,
[2024.iscls-1.1](https://aclanthology.org/2024.iscls-1.1/)), which aligns
*dictionary senses* between Wilson and Yates rather than *corpus token
occurrences* — the closer Sanskrit-specific precedent for [[A09]] and [[A35]]'s
dictionary-crosswalk problem, not this paper's, and cross-referenced here only to
keep the two alignment objects (lexicon sense vs. corpus token) distinct.
**ComputEL** (Computational Methods for the Study of Endangered
Languages, live, 9th edition 2026, [venues/computel](https://aclanthology.org/venues/computel/))
and **LoResMT** (live, 9th edition 2026, [venues/loresmt](https://aclanthology.org/venues/loresmt/))
are both active low-resource-focused workshops and are added below as submission-venue
candidates alongside the existing Russian-orientalist target journals, given a
classical-language, LLM-induced alignment resource is squarely in scope for either.
(b) **The Sanskrit→Russian lexicographic tradition** — Kochergina 1987, Kossowich
1854, Knauer 1908, Smirnov, Frisch — none of which is a corpus-attested
token-alignment resource; this resource is complementary, not a replacement.
(c) **LLM-induced word alignment and bitext mining as method**, and the evaluation
practice (gold sets, precision/recall, adversarial verification) that a resource
paper is held to. Land the novelty claim precisely: the contribution is the *first
large, openly-documented, period/genre/date-stratified Sanskrit→Russian alignment
lexicon*, induced and corpus-gated — not a new alignment algorithm.

## 3. Data and method

### 3.1 Source: a verse-aligned parallel corpus
The Russian evidence is not generated: it comes from existing, published Russian
translations held verse-aligned against the Sanskrit in the SamudraManthanam corpus
(`samskrtam.ru`), accessed read-only. A "group" is one aligned passage; within it the
Sanskrit segment (`sa`), the running translation (`ru`), and any commentary notes
(`comm1`, `comm2`, …) are distinct segments. We align the translation (tagged
`kind = translation`) and the commentary notes (`kind = commentary`) separately and
never confuse one for the other. The corpus itself — its sources and their
deterministic markup-aligned extraction — is documented by the companion paper A41
([SamudraManthanam papers/A41_parallel_corpus_descriptor.md](https://github.com/gasyoun/SamudraManthanam/blob/main/papers/A41_parallel_corpus_descriptor.md));
this paper consumes it and never re-describes it (§10).

### 3.2 Inducing the word alignment
For each aligned pair, a large language model is prompted to map every Sanskrit
*content* word (noun, verb, adjective, adverb; particles skipped) to the Russian word
or phrase that renders it *in that translation only*, in the word's
dictionary/citation form, emitting strict JSON and omitting any Sanskrit word with no
genuine Russian counterpart. Calls are batched and run
concurrently (~8 align-units per call — one align-unit per target segment, so a
group with both a translation and a commentary note counts twice; a group is never
split across batches), and the build is append-only and group-resumable. Each surviving
alignment is written as
`{group, work, passage, slp1, sa, ru, kind, genre, period, date}`. Implementation:
[`RussianTranslation/src/build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py).
(The adverb category and an explicit exhaustiveness instruction were added to the
harvest prompt on 08-07-2026 after the recall measurement exposed their absence —
§4.5; the prompt lineage is part of the method's audit trail, not hidden.)

### 3.3 The fabrication guard (an integrity control, not cosmetics)
Early builds fed *untranslated* placeholder verses (a bare `…` or `—` where the corpus
had no Russian yet) to the model, which then hallucinated fluent alignments against a
translation that did not exist — **166k of 204k rows (≈81%) were fabricated** before
the guard was added. The shipped resource refuses to align, or to write, any Russian
segment carrying no Cyrillic letter (`has_cyr`), drops rows where the Russian equals
the Sanskrit or is a known refusal string (`REJECT_RU`), strips dhātu `√` notation
from keys, and de-duplicates repeated commentary units. The shipped rows are all
post-guard.

### 3.4 The join key
Each Sanskrit token is normalised to an SLP1 key by `form_key()` — a
length-preserving normalisation that keeps case and vowel length, drops accents,
slashes, and hyphen bounds, and is explicitly *not* a naive NFD-strip-combining-marks
(which would destroy vowel length and the retroflex dots). This key joins the lexicon
to dictionary headwords; it is the same key the consuming verification gate
([`RussianTranslation/src/corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py))
uses.

### 3.5 Stratification
Every row inherits its work's `genre`, `period`, and median `date` from a curated
strata table, so the lexicon is queryable by epoch and register, not only by headword.

### 3.6 Reproducibility limits: an LLM-induced resource, honestly stated
The alignment layer is **non-deterministic**: re-running the committed builder against
the same corpus will not reproduce the shipped JSONL byte-for-byte, because the
inducing step is an LLM call, not a deterministic algorithm. This is a structural
property of the method, not an accident, and we state its consequences plainly rather
than blur them. What *is* deterministic and re-checkable: (i) the join key
(`form_key()`) and the consuming gate; (ii) the group-level coverage scan (§4.6),
recomputable by anyone from the shipped rows; (iii) the frozen evaluation scaffolds —
[gold_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl)
and [recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl) —
which pin the exact samples and per-item labels so the estimates can be re-adjudicated
by a human without re-sampling; and (iv) the fabrication-guard and de-duplication
rules, which are ordinary code. The honest reproducibility claim is therefore:
*the artifact is versioned and its evaluation is replicable; the artifact's generation
is not bit-replicable.* This contrasts with the companion corpus paper A41, whose
verse-aligned corpus is produced by **deterministic markup extraction** and is fully
re-derivable from its sources — the two resources sit at different points on the
reproducibility spectrum and are cited accordingly, never conflated (§10).

## 4. Results

All scale/shape figures below (§4.1–§4.3) were recomputed on 2026-06-26 directly from
`corpus_lexicon.jsonl` (290 MB; gitignored, regenerated by
[`build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)).
Evaluation figures (§4.4–§4.6) are transcribed from the consolidated memo
[gold/PR_MEMO_A42.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/PR_MEMO_A42.md)
as of 08-07-2026. A targeted re-harvest of two commentary works on 08-07-2026 (H309;
§4.5) brought the shipped build to **1,093,391 rows** (+1,863 net, all within a
780-group population); the §4.1–§4.3 breakdowns were **not** recomputed after it and
describe the 2026-06-26 build — the delta is confined to the Medieval commentary
stratum and does not materially move any figure below.

### 4.1 Scale and shape

| quantity | value |
|---|--:|
| token-pair alignments (rows) | **1,091,528** |
| distinct works | **116** |
| distinct SLP1 keys (Sanskrit side) | **190,838** |
| distinct Russian renderings | **253,275** |
| `kind = translation` | **990,499** (90.7%) |
| `kind = commentary` | **101,029** (9.3%) |
| date span (per-row `date`, CE) | **−1125 … 1374** |

### 4.2 Diachronic and generic distribution
By period: Epic / early-Classical **769,971** · Ṛgvedic **156,748** · Vedic
(Brāhmaṇa–Upaniṣad) **80,815** · Classical **62,194** · Medieval **21,800**. By genre
(top five): Mahābhārata **452,024** · Veda-Saṃhitā **217,491** · Rāmāyaṇa **124,593** ·
Bhagavad-Gītā **89,517** · Manu-smṛti **39,361**, with a long tail across kāvya
(Kālidāsa, Buddhist mahākāvya, śataka, Jayadeva), śāstra (Dharma, Nyāya, Yoga, Sāṃkhya),
and Āgama/Tantra. The corpus is Epic-heavy, as the source translations are.

### 4.3 Per-headword rendering distributions
Because many headwords recur across works and translators, the resource yields an
*empirical distribution of attested renderings* per Sanskrit word: **65,089** of the
190,838 distinct SLP1 keys have ≥2 distinct Russian renderings, and the most polysemous
single key carries **458** distinct renderings. The `agni` entry illustrates the
proper-name/common-noun split a flat dictionary cannot show: *Агни* ×1111, *огонь*
('fire') ×408, plus its inflected genitive/locative/plural/dative forms.

### 4.4 Precision (LLM-judged estimate; human pass pending)
On a stratified random sample of **320** alignments (seed 42, balanced across
period × kind), each judged against its source verse with adversarial verification of
every flagged error, estimated **precision (good renderings) is 84.4%** (95% CI
80.0–87.9), partial 8.8%, errors 6.9% (good + partial 93.1%). By period: Vedic 90.0%,
Epic / early-Classical 90.0%, Classical 78.8%, Medieval 78.8%. By kind: translation
**86.9%** vs commentary **81.9%** — commentary is noisier, as expected from sparser,
note-form evidence. Label counts: correct 200 · lemma-variant 46 · proper-name 24 ·
partial 28 · wrong-sense 13 · hallucinated 9. Source:
[gold/precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md)
(measured 2026-06-16; not affected by the H309 recall-side re-harvest).

> This is an **LLM-judged** estimate (per the report's own note and
> [`HUMAN_GOLD_PROTOCOL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md)). The
> frozen 320-row sample is the scaffold for a human spot-check that will confirm or
> adjust these numbers; until then it must not be cited as print-grade precision.

### 4.5 Recall (LLM-adjudicated estimate; human spot-check pending)
Recall — the share of Sanskrit content words *rendered in the published Russian* that
received an aligned row — was measured on 07-07-2026 over a stratified sample of
**32 processed groups** (8 per period stratum, seed 42), yielding **287 unique content
lemmata** after excluding particles, pronouns, copulas, and tokenization junk; every
sampled token was read against its source verse and published translation, and the
per-group labels are frozen in
[recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl).
Estimated **word-level recall is 95.4%** (Wilson 95% CI 92.2–97.3, n=280), counting a
lemma as covered when the lexicon has a pair for it in that group and as a recall loss
only when the published Russian renders it and the lexicon lacks it; the 7 sampled
lemmata with no distinct Russian counterpart in their translation are reported
separately and excluded from the denominator (280 = 267 covered + 13 missed). By stratum:
Vedic 97.3%, Epic / early-Classical 91.3%, Classical 96.3%, Medieval 95.1%. Source:
[gold/recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md).

The measurement did its diagnostic job: the initial figure was **92.1%** (CI
88.4–94.7), with the Medieval stratum at 84.0%, and the failure classes it
exposed were root-caused and the largest fixed the next day (H309, 08-07-2026).
(1) *Commentary-tail dilution:* on dense groups whose `sa` blob fuses verse and prose
commentary, the single-pass aligner silently dropped content words — fixed by an
explicit exhaustiveness instruction plus a **targeted REPLACE re-harvest** of the two
genre-tagged commentary works (780 groups; 12,841 → 14,704 rows), re-measured against
the *same* eight frozen Medieval groups (apples-to-apples): Medieval recall
**84.0% → 95.1%**, 9 of 13 misses resolved, 4 residual misses documented individually.
(2) *Adverb skip:* adverbs were simply absent from the prompt's content-word category
list — fixed for all future harvests; the sampled instances live outside the
re-harvested population and remain documented residuals in the shipped build (the
re-harvest was deliberately targeted, not a full rebuild).
(3) *Scattered single misses:* a small heterogeneous remainder (e.g. `sarva`, `eka`,
`arh`) with no single mechanism; the two of these that fell inside the re-harvested
population were resolved by it, the rest are unchanged and documented. Like precision, this is an
LLM-adjudicated estimate (single frontier-model reading pass) awaiting a human
spot-check over the frozen scaffold.

### 4.6 Group-level coverage (deterministic)
Of the **58,897** verse groups eligible for harvesting (a Sanskrit segment and a
Cyrillic-bearing Russian segment, work present in the strata table), **98.9%** have at
least one lexicon row (Vedic 99.9%, Epic / early-Classical 99.3%, Classical 90.2%,
Medieval 99.6%) — a full-corpus deterministic scan, not a sample. Combining the
axes, end-to-end coverage of translated content words is roughly
**recall × group coverage ≈ 94.3%** — a derived characterisation, not an
independently measured figure. The resource is best described as
**high-precision, high-recall within processed groups, with a measured and
documented residual**, replacing the earlier "high-precision, partial-recall,
recall unmeasured" characterisation that stood before 07-07-2026.

## 5. Discussion

A token-aligned, date-stamped Sanskrit→Russian lexicon turns translations from prose
to be read into evidence to be queried. Three uses follow directly. (1) **Empirical
lexicography:** per-headword rendering distributions (§4.3) expose sense splits and
translator preferences a single gloss list hides. (2) **Diachronic / register study:**
the period and genre stamps let one ask how a word's Russian rendering shifts from
Vedic to Classical, or between epic narration and śāstric commentary. (3) **Dictionary
verification:** the resource already feeds the `pwg_ru` corpus gate
([`corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py))
as corpus evidence for
whether a proposed Russian gloss is attested in translated context. The induced-then-
gated design is what makes a million-row resource tractable to build while keeping a
deterministic, auditable join.

### 5.1 Technique-adoption assessment: Mao & Yu's contrastive signal (§2)

**Yes, concretely actionable — a prompt-construction change, not citation-only.**
Mao & Yu's LoResMT 2024 method feeds a statistical aligner's output into the LLM as a
contrastive signal during fine-tuning. This pipeline does not fine-tune, but the
equivalent prompt-time move is available cheaply: before calling `align_batch()`
([`build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)),
look up the Sanskrit surface form's `form_key()` in
the already-accumulated `corpus_lexicon.jsonl` and, if prior renderings exist for that
key, inject them into the prompt as "previously observed rendering(s) for this word:
…confirm, refine, or override if this context differs." This is a stronger prior than
Mao & Yu's statistical aligner, since it comes from the same LLM's own accumulated,
Cyrillic-guarded output rather than an independent word-alignment model — but the
structural idea (give the model a contrastive anchor instead of aligning cold every
time) is exactly theirs. Scope: one new lookup function plus a prompt-template edit;
no new dependency, no schema change to `corpus_lexicon.jsonl`. Not yet implemented —
flagged here as a scoped follow-up, not done in this pass.

## 6. Limitations

- **Induced, not gold.** Alignments are LLM-emitted, not hand-verified; the resource
  is a high-precision draft layer, not a manually curated gold alignment.
- **Non-deterministic generation.** Re-running the builder will not reproduce the
  shipped rows byte-for-byte (§3.6); the versioned artifact plus frozen evaluation
  scaffolds, not bit-replication, are the reproducibility contract.
- **Both evaluation axes are LLM-estimated.** Precision 84.4% (§4.4) and recall 95.4%
  (§4.5) are LLM-judged/adjudicated estimates over frozen, committed samples pending
  the human gold pass defined in
  [HUMAN_GOLD_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md)
  (reviewer-packet generation is specified in
  [gold/REVIEWER_HANDOFF.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/REVIEWER_HANDOFF.md);
  the packets themselves are generated on demand, not committed; annotator
  recruitment is an open action).
- **Recall residual is bounded and documented, not zero.** A small adverb-class miss
  set and a scattered heterogeneous remainder persist outside the 780-group population
  re-harvested on 08-07-2026, and 4 residual commentary-class misses persist within it
  (§4.5) — each documented individually in the recall report.
- **Commentary is noisier than translation** (81.9% vs 86.9% precision); the
  commentary stratum should be consumed with that in mind.
- **Corpus composition is skewed Epic** (MBh + Rām + Gītā dominate), so per-headword
  distributions over-weight epic register.
- **Fabrication risk is controlled, not absent.** The Cyrillic guard (§3.3) removed
  the 81% placeholder-hallucination failure, but residual wrong-sense (13) and
  hallucinated (9) labels remain in the gold sample.
- **Third-party translation rights.** The Russian renderings derive from modern
  published translations (Elizarenkova, the academic Mahābhārata, Russian Gītās)
  whose redistribution is governed by their source-corpus permissions, *not* by this
  project's own licence — see §8 and the open IP gate. Which slice of the 1.09M pairs
  can ship openly (full pairs vs. alignment-only vs. aggregate frequencies) is
  undetermined until that documentation pass completes.

## 7. Conclusion

We document the first large, openly-described Sanskrit→Russian word-alignment lexicon:
1.09 million alignments over 116 works, −1125 to 1374 CE, in SLP1 + IAST + Cyrillic,
stamped by period, genre, and date and tagged translation-vs-commentary, induced from
a verse-aligned parallel corpus, fabrication-guarded, and joined deterministically by
a length-preserving SLP1 key. Its evaluation is unusually complete for an induced
resource of this size — precision 84.4%, word-level recall 95.4%, group coverage
98.9%, all on frozen committed scaffolds — and unusually honest about its status:
both sampled estimates are LLM-judged pending a human pass, and the recall
measurement's own failure classes were root-caused, one fixed by a targeted
re-harvest, and the residual documented item-by-item. The resource makes the Russian
rendering of a Sanskrit word a computable, diachronically situated distribution
rather than a single printed gloss, and is already consumed as evidence by an
independent dictionary-verification pipeline. The remaining work is the
human-confirmed evaluation pass and a rights-cleared, DOI-minted public deposit.

## 8. Data and reproducibility

The data asset is
`RussianTranslation/src/corpus_lexicon.jsonl`
(JSON-lines; one alignment per line; `{group, work, passage, slp1, sa, ru, kind,
genre, period, date}`). It is gitignored for size and for the third-party rights below
and is regenerated by the committed builder
[`build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py):

```sh
python build_corpus_lexicon.py build <textfile> [N]   # needs an API key in src/.env
python build_corpus_lexicon.py status                 # rows · distinct SLP1 keys · works
```

The deterministic join contract and the consuming gate are in
[`corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py);
the consolidated evaluation memo is
[`gold/PR_MEMO_A42.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/PR_MEMO_A42.md);
the precision scaffold and human protocol are in
[`gold/precision_report.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md) and
[`gold/HUMAN_GOLD_PROTOCOL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md);
the recall scaffold and sampler are in
[`gold/recall_report.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md),
[`gold/recall_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl), and
[`src/gold_recall_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_recall_sample.py);
the build history and the placeholder-fabrication fix are in
[`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md).

**Licence.** The project's own contributions are released **CC BY-SA 4.0** — see
[`DATA_LICENSE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DATA_LICENSE.md);
its enumerated scope currently names the pwg_ru edition, stratification, and
documentation, and extending its wording to name the alignment lexicon explicitly is
part of the open rights pass. **Third-party rights
(blocking for public release):** the Russian side derives from modern published
translations whose redistribution is governed by their source-corpus permissions, not
by this licence; the public deposit scope (full pairs vs. alignment-only vs. aggregate
frequencies) must be settled per source before release. **DOI:** *TODO — Zenodo DOI to
mint once the rights scope is fixed (author action).*

**Rights-partitioned release bundles (H1458, 22-07-2026, Sonnet 5 `claude-sonnet-5`).**
The "settled per source" step above is now mechanized, not just stated: the sibling
Publication-Grade Sa→Ru TM span
([H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md)/[H1458](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1458-Sonnet_RussianTranslation_pubgrade-tm-track-c-release-prep_22.07.26.md))
built
[`RussianTranslation/src/build_release_bundles.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_release_bundles.py),
which reads this exact alignment lexicon and, per-work, consults the canonical
[SamudraManthanam rights ledger](https://github.com/gasyoun/SamudraManthanam/blob/main/nkrya-parallel/export/RIGHTS_TABLE.md)
(H821) fail-closed (absent-from-ledger = grey, never assumed clear). Result as of
22-07-2026: **all 131 source works are still `needs_review`** (that ledger's own
finding stands: 4 of 131 have a documented translator, 0 of 131 are cleared) — so the
tool emits an `alignment-only` bundle
([`RussianTranslation/release/corpus_tm/derived_only.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/corpus_tm/derived_only.sample.jsonl),
1,093,391 rows with the `ru` field stripped, sample committed) with **zero** Russian
surface text, mechanically asserted by `build_release_bundles.py --audit-rights`. This
does not resolve the per-translator clearance this section still calls a blocker — it
proves the *mechanical* side (no accidental leak of copyrighted text) is now airtight,
so the remaining gap is purely the human per-source clearance pass, not tooling.

## 9. Claim → artifact inventory

Every headline claim, its figure, and the artifact it traces to (per the
`/paper-scaffold` discipline — a claim without a committed artifact is a gap,
flagged as such):

| # | Claim | Figure(s) | Artifact | Status |
|--:|---|---|---|---|
| 1 | Scale and shape (rows, works, keys, kind split, date span) | 1,091,528 rows · 116 works · 190,838 keys · 90.7%/9.3% · −1125…1374 | `corpus_lexicon.jsonl` (gitignored) via [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py) `status` | ⚠️ regenerable, not committed (size + rights); recomputed 2026-06-26 |
| 2 | Post-H309 build size | 1,093,391 rows (+1,863 in the 780-group re-harvest population) | [PR_MEMO_A42.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/PR_MEMO_A42.md) + [recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md) affected-group census | ✅ committed |
| 3 | Precision 84.4% (CI 80.0–87.9), n=320, stratified period×kind, seed 42 | §4.4 | [precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md) + frozen [gold_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl) | ✅ committed; ⬜ LLM-judged, human packets pending |
| 4 | Word-level recall 95.4% (CI 92.2–97.3), n=280 translated lemmata (287 sampled) / 32 groups, seed 42 | §4.5 | [recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md) + frozen [recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl) | ✅ committed; ⬜ LLM-adjudicated, human spot-check pending |
| 5 | Medieval recall 84.0% → 95.1% after the targeted H309 re-harvest (same 8 frozen groups) | §4.5 | [recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md) re-measurement table | ✅ committed |
| 6 | Group-level coverage 98.9% (58,897 eligible groups) | §4.6 | [recall_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_report.md) coverage table, deterministic scan via [gold_recall_sample.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_recall_sample.py) `coverage` | ✅ committed |
| 7 | Pre-guard fabrication: 166k of 204k rows (≈81%) | §3.3 | [RussianTranslation/CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md) build history | ✅ committed |
| 8 | Per-headword distributions (65,089 keys ≥2 renderings; max 458; `agni` ×1111/×408) | §4.3 | recomputed 2026-06-26 from the JSONL | ⚠️ regenerable, not committed |
| 9 | Source corpus: verse-aligned Sa↔Ru parallel corpus, deterministic extraction | §3.1 | companion paper [A41](https://github.com/gasyoun/SamudraManthanam/blob/main/papers/A41_parallel_corpus_descriptor.md) + [SamudraManthanam](https://github.com/gasyoun/SamudraManthanam) | ✅ committed (cited, owned by A41) |

## 10. Scope versus companion papers (anti-salami)

- **A41 (SamudraManthanam parallel-corpus descriptor)** owns the verse-aligned
  Sa↔Ru corpus itself: its sources, the markup-aligned **deterministic**
  extraction, and the corpus-level statistics. A42 consumes that corpus read-only and
  cites it; it never re-describes the corpus, and it never blurs the method line —
  A41's extraction is deterministic and re-derivable, A42's alignment layer is
  LLM-induced and is evaluated precisely because it is not (§3.6).
- **A43 (the Russian Sanskrit lexicographic family)** owns the digitized printed
  tradition — Kochergina, Kossowich, Knauer and their comparability as a dictionary
  family. A42 references that tradition only as background (§1, §2b) and contributes
  the corpus-attested layer none of those dictionaries has; the dictionaries
  themselves are A43's object.
- **A40 (CDSL headword census) and A38 (the DCS-2026 corpus release)** own the
  dictionary-inventory and Sanskrit-corpus sides respectively; A42 overlaps neither —
  its denominator is a Sa↔Ru parallel corpus, not the DCS, and its output is an
  alignment lexicon, not a headword census.
- A42 leads with exactly what nothing else owns: the **word-level, LLM-induced,
  diachronically stratified Sanskrit→Russian alignment lexicon** and its
  precision/recall/coverage evaluation on frozen scaffolds.

## 11. References

- Aralikatte, R., M. de Lhoneux, A. Kunchukuttan & A. Søgaard. 2021.
  [Itihāsa: A large-scale corpus for Sanskrit to English translation](https://aclanthology.org/2021.wat-1.22/).
  *Proceedings of the 8th Workshop on Asian Translation (WAT 2021)*.
- Dou, Z.-Y. & G. Neubig. 2021.
  [Word alignment by fine-tuning embeddings on parallel corpora](https://aclanthology.org/2021.eacl-main.181/).
  *Proceedings of EACL 2021*. (awesome-align.)
- Dyer, C., V. Chahuneau & N. A. Smith. 2013.
  [A simple, fast, and effective reparameterization of IBM Model 2](https://aclanthology.org/N13-1073/).
  *Proceedings of NAACL-HLT 2013*. (fast_align.)
- Hellwig, O. *Digital Corpus of Sanskrit (DCS)* —
  [github.com/OliverHellwig/sanskrit](https://github.com/OliverHellwig/sanskrit).
- Knauer, F. (Кнауэр, Ф. И.). 1908. *Учебник санскритскаго языка.* Leipzig.
- Kochergina, V. A. (Кочергина, В. А.). 1987. *Санскритско-русский словарь.* Moscow:
  Русский язык.
- Kossowich, K. A. (Коссович, К. А.). 1854. *Санскрито-русскій словарь.*
  St. Petersburg.
- Mao, Z. & C. Yu. 2024.
  [Tuning LLMs with contrastive alignment instructions for machine translation in unseen, low-resource languages](https://aclanthology.org/2024.loresmt-1.1/).
  *Proceedings of LoResMT 2024*.
- Nehrdich, S. 2022.
  [SansTib: A Sanskrit–Tibetan parallel corpus and bilingual sentence embedding model](https://aclanthology.org/2022.lrec-1.724/).
  *Proceedings of LREC 2022*.
- Patel, D. & M. Kulkarni. 2024.
  [Word sense alignment of Sanskrit lexica](https://aclanthology.org/2024.iscls-1.1/).
  *Proceedings of ISCLS 2024*.
- Punia, R. et al. 2020.
  [Improving neural machine translation for Sanskrit–English](https://aclanthology.org/2020.icon-main.30/).
  *Proceedings of ICON 2020*.
- SamudraManthanam — the verse-aligned Sanskrit↔Russian parallel corpus behind
  `samskrtam.ru`: [github.com/gasyoun/SamudraManthanam](https://github.com/gasyoun/SamudraManthanam);
  descriptor paper A41 (in preparation,
  [papers/A41_parallel_corpus_descriptor.md](https://github.com/gasyoun/SamudraManthanam/blob/main/papers/A41_parallel_corpus_descriptor.md)).
- ⬜ A41 / A43 self-citations to be finalized once their venues/DOIs freeze.

_Dr. Mārcis Gasūns_
