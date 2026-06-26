---
paper_id: A42
title: "A Word-Aligned Sanskrit→Russian Corpus Lexicon: a 1.09-Million-Pair Open Alignment Resource"
status: draft (skeleton, 2/5) — scaffolded 2026-06-26
readiness: 2/5
venue: "Письменные памятники Востока / Вопросы языкознания (ВЯ) / CLARIN-LRE"
author: "M. Gasūns (sole) — ORCID to confirm"
data_source: "RussianTranslation/src/corpus_lexicon.jsonl (built & verified; 1,091,528 alignments) — figures recomputed 2026-06-26 from the JSONL and from RussianTranslation/gold/precision_report.md"
---

# A Word-Aligned Sanskrit→Russian Corpus Lexicon: a 1.09-Million-Pair Open Alignment Resource

> **Draft status (2026-06-26).** Manuscript skeleton built directly on the verified
> data asset
> [`RussianTranslation/src/corpus_lexicon.jsonl`](../RussianTranslation/src/corpus_lexicon.jsonl)
> and the precision scaffold
> [`RussianTranslation/gold/precision_report.md`](../RussianTranslation/gold/precision_report.md).
> Every numeric claim below was recomputed from the JSONL on this date (rows,
> works, distinct keys, kind split, date span, period/genre tallies) or transcribed
> from the precision report. **Open before submission:** (1) write §2 Related work
> (currently a stub); (2) state recall as a measured gap — no recall figure exists
> yet, do not invent one; (3) downgrade the precision number to "LLM-judged
> estimate" wording until the human gold pass lands; (4) **[@DO]** document the IP /
> redistribution rights of the underlying modern Russian translations before any
> public deposit; (5) **[@DO]** mint a Zenodo DOI; (6) **[@DO]** confirm ORCID and
> lock the venue. The alignment is **LLM-induced, not deterministic** — the resource
> is described by artifact and method, never headlined by a model name.

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
normaliser then provides a deterministic join key into the dictionary side. On a
stratified random sample of 320 alignments judged against their source verses,
estimated precision is **84.4%** (95% CI 80.0–87.9), rising to 90.0% on Vedic and
Epic strata; this is an LLM-judged estimate pending a human gold pass. The
contribution is not a new alignment algorithm — induced bitext alignment is a mature
method — but the construction, stratification, evaluation, and open documentation of
a **diachronically labelled Sanskrit→Russian lexical-alignment resource** that did
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

The alignment is **LLM-induced**: per-pair, JSON-constrained, and guarded against
fabrication, rather than produced by a deterministic statistical aligner. We describe
it by its artifact and method and treat the particular model as a build detail
recorded in the changelog, not as the contribution.

## 2. Related work  *(TODO — to be written)*

Position against three axes. (a) **Parallel-corpus and word-alignment resources** for
Sanskrit and for low/medium-resource pairs: the DCS corpus and lemma data, the
verse-aligned `samskrtam.ru` Sanskrit↔Russian corpus this work is induced from, and
statistical/neural aligners (IBM models, `fast_align`, `awesome-align`) versus
LLM-prompted alignment. (b) **The Sanskrit→Russian lexicographic tradition** —
Kochergina 1987, Kossowich 1854, Knauer 1908, Smirnov, Frisch — none of which is a
corpus-attested token-alignment resource; this resource is complementary, not a
replacement. (c) **LLM-induced word alignment and bitext mining as method**, and the
evaluation practice (gold sets, precision/recall, adversarial verification) that a
resource paper is held to. Land the novelty claim precisely: the contribution is the
*first large, openly-documented, period/genre/date-stratified Sanskrit→Russian
alignment lexicon*, induced and corpus-gated — not a new alignment algorithm.

## 3. Data and method

### 3.1 Source: a verse-aligned parallel corpus
The Russian evidence is not generated: it comes from existing, published Russian
translations held verse-aligned against the Sanskrit in the SamudraManthanam corpus
(`samskrtam.ru`), accessed read-only. A "group" is one aligned passage; within it the
Sanskrit segment (`sa`), the running translation (`ru`), and any commentary notes
(`comm1`, `comm2`, …) are distinct segments. We align the translation (tagged
`kind = translation`) and the commentary notes (`kind = commentary`) separately and
never confuse one for the other.

### 3.2 Inducing the word alignment
For each aligned pair, a large language model is prompted to map every Sanskrit
*content* word (noun, verb, adjective; particles skipped) to the Russian word or
phrase that renders it *in that translation only*, in the word's dictionary/citation
form, emitting strict JSON and omitting any Sanskrit word with no genuine Russian
counterpart. Calls are batched (~8 verse-units each), run concurrently, and the build
is append-only and group-resumable. Each surviving alignment is written as
`{group, work, passage, slp1, sa, ru, kind, genre, period, date}`. Implementation:
[`RussianTranslation/src/build_corpus_lexicon.py`](../RussianTranslation/src/build_corpus_lexicon.py).

### 3.3 The fabrication guard (an integrity control, not cosmetics)
Early builds fed *untranslated* placeholder verses (a bare `…` or `—` where the corpus
had no Russian yet) to the model, which then hallucinated fluent alignments against a
translation that did not exist — **166k of 204k rows (≈81%) were fabricated** before
the guard was added. The shipped resource refuses to align, or to write, any Russian
segment carrying no Cyrillic letter (`has_cyr`), drops rows where the Russian equals
the Sanskrit or is a known refusal string (`REJECT_RU`), strips dhātu `√` notation
from keys, and de-duplicates repeated commentary units. The 1.09M shipped rows are all
post-guard.

### 3.4 The join key
Each Sanskrit token is normalised to an SLP1 key by `form_key()` — a
length-preserving normalisation that keeps case and vowel length, drops accents,
slashes, and hyphen bounds, and is explicitly *not* a naive NFD-strip-combining-marks
(which would destroy vowel length and the retroflex dots). This key joins the lexicon
to dictionary headwords; it is the same key the consuming verification gate
([`RussianTranslation/src/corpus_gate.py`](../RussianTranslation/src/corpus_gate.py))
uses.

### 3.5 Stratification
Every row inherits its work's `genre`, `period`, and median `date` from a curated
strata table, so the lexicon is queryable by epoch and register, not only by headword.

## 4. Results

All figures below were recomputed on 2026-06-26 directly from
[`corpus_lexicon.jsonl`](../RussianTranslation/src/corpus_lexicon.jsonl) (290 MB),
except the precision block, transcribed from
[`gold/precision_report.md`](../RussianTranslation/gold/precision_report.md).

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
partial 28 · wrong-sense 13 · hallucinated 9.

> This is an **LLM-judged** estimate (per the report's own note and
> [`HUMAN_GOLD_PROTOCOL.md`](../RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md)). The
> frozen 320-row sample is the scaffold for a human spot-check that will confirm or
> adjust these numbers; until then it must not be cited as print-grade precision.

### 4.5 Recall  *(TODO — measured gap)*
The gold set measures precision of emitted alignments, **not recall** (the share of
Sanskrit content words that received any aligned rendering). No recall figure exists
in the sources; the resource is best characterised as **high-precision, partial-recall**
and the figure left as a TODO rather than invented.

## 5. Discussion

A token-aligned, date-stamped Sanskrit→Russian lexicon turns translations from prose
to be read into evidence to be queried. Three uses follow directly. (1) **Empirical
lexicography:** per-headword rendering distributions (§4.3) expose sense splits and
translator preferences a single gloss list hides. (2) **Diachronic / register study:**
the period and genre stamps let one ask how a word's Russian rendering shifts from
Vedic to Classical, or between epic narration and śāstric commentary. (3) **Dictionary
verification:** the resource already feeds the `pwg_ru` corpus gate
([`corpus_gate.py`](../RussianTranslation/src/corpus_gate.py)) as corpus evidence for
whether a proposed Russian gloss is attested in translated context. The induced-then-
gated design is what makes a million-row resource tractable to build while keeping a
deterministic, auditable join.

## 6. Limitations

- **Induced, not gold.** Alignments are LLM-emitted, not hand-verified; the resource
  is a high-precision draft layer, not a manually curated gold alignment.
- **Precision is LLM-judged.** The 84.4% figure (§4.4) is an estimate pending the
  human gold pass defined in `HUMAN_GOLD_PROTOCOL.md`.
- **Recall is unmeasured** (§4.5) and should be reported before strong coverage
  claims are made.
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
  project's own licence — see §8 and the open IP gate.

## 7. Conclusion

We document the first large, openly-described Sanskrit→Russian word-alignment lexicon:
1,091,528 alignments over 116 works, −1125 to 1374 CE, in SLP1 + IAST + Cyrillic,
stamped by period, genre, and date and tagged translation-vs-commentary, induced from
a verse-aligned parallel corpus, fabrication-guarded, and joined deterministically by
a length-preserving SLP1 key. The resource makes the Russian rendering of a Sanskrit
word a computable, diachronically situated distribution rather than a single printed
gloss, and is already consumed as evidence by an independent dictionary-verification
pipeline. The remaining work is a human-confirmed precision pass, a recall
measurement, and a rights-cleared, DOI-minted public deposit.

## 8. Data and reproducibility

The data asset is
[`RussianTranslation/src/corpus_lexicon.jsonl`](../RussianTranslation/src/corpus_lexicon.jsonl)
(JSON-lines; one alignment per line; `{group, work, passage, slp1, sa, ru, kind,
genre, period, date}`). It is gitignored for size and for the third-party rights below
and is regenerated by the committed builder
[`build_corpus_lexicon.py`](../RussianTranslation/src/build_corpus_lexicon.py):

```sh
python build_corpus_lexicon.py build <textfile> [N]   # needs an API key in src/.env
python build_corpus_lexicon.py status                 # rows · distinct SLP1 keys · works
```

The deterministic join contract and the consuming gate are in
[`corpus_gate.py`](../RussianTranslation/src/corpus_gate.py); the precision scaffold
and human protocol are in
[`gold/precision_report.md`](../RussianTranslation/gold/precision_report.md) and
[`gold/HUMAN_GOLD_PROTOCOL.md`](../RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md);
the build history and the placeholder-fabrication fix are in
[`CHANGELOG.md`](../RussianTranslation/CHANGELOG.md).

**Licence.** The project's own work (alignments produced by this pipeline, the
stratification, the documentation) is **CC BY-SA 4.0** — see
[`DATA_LICENSE.md`](../RussianTranslation/DATA_LICENSE.md). **Third-party rights
(blocking for public release):** the Russian side derives from modern published
translations whose redistribution is governed by their source-corpus permissions, not
by this licence; the public deposit scope (full pairs vs. alignment-only vs. aggregate
frequencies) must be settled per source before release. **DOI:** *TODO — Zenodo DOI to
mint once the rights scope is fixed (author action).*
