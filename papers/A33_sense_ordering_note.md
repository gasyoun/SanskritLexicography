# Genetic, not historical: how the 19th-century European Sanskrit dictionaries order senses — and how Apte and Kochergina differ

**A33 · research note / short communication · draft 2026-06-24 · target: Lexikos / IJL / eLex**

> **Status:** full first draft (3/5). Evidence assembled and reproducible; needs prose
> tightening, a related-work paragraph, and a venue decision before submission.

## Abstract

It is widely assumed that the great 19th-century European dictionaries of Sanskrit — the
St Petersburg dictionaries of Böhtlingk & Roth (PWG, PW), Monier-Williams (MW), and
Grassmann's Rig-Veda dictionary (GRA) — arrange the senses *within* an entry in
**historical** order, oldest attested meaning first. Using the Cologne Digital Sanskrit
Lexicon's machine-readable editions and a citation-dating map that assigns every
literary-source siglum a date and a Renou language-state (I–V), we test this at corpus
scale. The assumption is **half right**. These dictionaries are better described as
**etymological-genetic**: the lead sense is the reconstructed root meaning
(*Grundbedeutung*), and chronology governs a *tendency* in citation order rather than a
strict sort. Across 13,900 multi-sense PWG entries, the printed first sense is the
oldest-attested sense **73.5 %** of the time, and the overall sense order correlates with
attestation date only **moderately** (Kendall τ = 0.375). Monier-Williams behaves almost
identically (69.4 %; τ = 0.367). By contrast, Apte's student dictionary (AP90) and
Kochergina's modern Russian learner's dictionary order senses by **pedagogical salience**:
their Vedic-citation density is **2.3 %** and **0 %** respectively, against **23–25 %** for
PWG and MW. The finding has a direct consequence for digital re-editions: re-sorting senses
by attestation date — now trivially possible — would silently overwrite the editors'
genetic judgement for roughly one entry in four, and should be offered as an optional view,
not imposed.

## 1. The question

Macrostructure (the order of headwords) is alphabetical in all of these dictionaries and is
not at issue. The question is **microstructure**: given a polysemous word, in what order are
its senses printed? Four principles are conceivable — *historical* (oldest attestation
first), *logical-semantic* (commonest or most pedagogically useful first, grouped by
affinity), *etymological* (root meaning first, then derived), and *frequency* (no printed
frequency dictionary of Sanskrit exists). The received view, repeated in handbooks, is that
the comparative-philology generation ordered senses historically. We test it.

## 2. Method

We use the CDSL editions (`csl-orig`) and an existing citation-dating resource built for the
`pwg_ru` translation project: a map from each `<ls>` literary-source siglum to a numeric
date and a Renou state (I Vedic · II Pāṇinian · III Epic · IV Classical · V Buddhist/Jaina).
The map covers **72.4 %** of PWG's 772,567 source citations; the unrecognised tail is
dominated by catalogues and secondary literature (Aufrecht's Oxford catalogue, *Indische
Studien*, *Indische Sprüche*), not primary datable texts, so the sample is the most-cited
primary corpus and is if anything conservative about the oldest layer.

For each entry we segment the printed senses (PWG/PW: `<div>`-numbered senses; MW:
consecutive `<L>` records sharing the headword; AP90: `{@N@}` markers), extract the dated
citations in each sense, and compute (1) whether the first printed sense is the
oldest-attested, and the Kendall τ between printed order and date order; (3) whether the
citations *inside* a sense run oldest→newest. As a single cross-dictionary discriminator we
compute **Vedic-citation density**: the fraction of cited senses that reach at least one
Renou-I (Vedic) source. Apte has no citation map, so its density is measured by matching
Apte's own Vedic sigla (Ṛv., Av., the Brāhmaṇas and Upaniṣads, Nirukta), deliberately
excluding *Ms.* = Manusmṛti, which is classical. The analysis scripts and raw metrics are
released with this note.

## 3. Results

### 3.1 PWG and MW: genetic, not a date-sort

| Metric | PWG | MW |
|---|---|---|
| Multi-sense entries with ≥2 dated senses | 13,900 | 13,825 |
| Printed sense 1 = oldest-attested sense | **73.5 %** | **69.4 %** |
| Kendall τ (printed order vs date order) | **0.375** | **0.367** |
| Citations within a sense strictly oldest→newest | 26.2 % | 55.0 % |
| Adjacent citation pairs non-decreasing in date | 76.3 % | 67.6 % |

The two dictionaries are statistically almost the same animal. The lead sense is the oldest
about 70–74 % of the time — high, but far from the ~100 % a true historical sort would give;
and the overall τ ≈ 0.37 shows only a moderate correlation with date. Inside a sense,
citations *lean* old-to-new (76 % of adjacent pairs in PWG) but are strictly sorted in only
a quarter of cases, because the editors also group citations by sub-sense and grammatical
construction. (MW's higher strict-chronology figure is a granularity artefact: an MW "sense"
is a single short record with few citations, so monotonicity is easier to attain.)

This matches what the prefaces actually say. PWG's preface never states a sense-ordering
rule; it states a *method of meaning-recovery* anchored in the Veda ("reach back into the
treasure of the Veda… to recover the original value"). Grassmann's is the only preface to
state the rule explicitly, and it is etymological-genetic, not historical: "the basic
concept is *das Erstrebte*… **therefore** 1) goal; 2) work…". Monier-Williams describes only
the etymological *macrostructure* (root-nesting) and a punctuation convention for grouping
adjacent senses by affinity. The numbers and the prefaces agree: **genetic lead sense,
chronological tendency.**

### 3.2 The śāstra pocket

PWG itself mixes axes for one class of vocabulary. For grammar and philosophy technical
terms — *prakṛti, vṛtti, nyāya, karaṇa, mātrā* — the first printed sense is the
**Classical/Pāṇinian technical sense**, not the oldest. Here the dictionary follows
logical-semantic salience, exactly as a śāstra reader needs. Sense ordering is therefore not
a single global policy even within one dictionary.

### 3.3 Apte and Kochergina: salience, no historical layer

The discriminator that separates the two traditions cleanly is Vedic-citation density:

| Dictionary | Vedic-citation density | basis |
|---|---|---|
| PWG (Böhtlingk–Roth) | **23.4 %** | 118,528 cited senses |
| MW (Monier-Williams) | **24.8 %** | 99,726 cited senses |
| AP90 (Apte, 1890) | **2.3 %** | 19,163 cited senses |
| Koch (Kochergina, 1978/87) | **0.0 %** | 29,177 records (5 dated cites total) |

Apte and Kochergina drop by an order of magnitude or to zero. Their first sense is the one a
student needs first: Apte's *dharma* opens with "Religion", relegating the etymological core
"that which is established, ordinance" to sense 2 and the philosophical "essential property"
to sense 8; PWG and MW open *dharma* with the root meaning "that which is held fast, statute"
and MW even flags the older Vedic stem *dharman*. Their sense order is **logical-semantic /
pedagogical**, by editorial choice (Apte) or by being a citation-free learner's dictionary
(Kochergina).

## 4. Consequence for digital re-editions

Because every sense can now be auto-dated, it is tempting to "improve" a historical
dictionary by re-sorting its senses oldest-first. Our measurement shows the cost: such a
re-sort would **change the lead sense for ~26.5 %** of PWG's multi-sense entries and impose a
stricter chronology than Böhtlingk and Roth used, discarding their genetic judgement — and it
would actively mis-serve the śāstra vocabulary of §3.2. The right move for a digital edition
or translation (here, the `pwg_ru` Russian Petersburg dictionary) is to **preserve the
source order** and attach the attestation period as **per-sense display metadata** (a
Vedic / Brāhmaṇa / epic / classical badge), with an optional, explicitly-labelled
"sort by oldest attestation" and a future "sort by corpus frequency" view. Editorial order is
an authorial stance; chronology and frequency are lenses laid over it, not replacements for
it.

## 5. Reproducibility

Scripts and metrics: [`research/analyze_sense_order.py`](../RussianTranslation/research/analyze_sense_order.py),
[`research/analyze_cross_dict.py`](../RussianTranslation/research/analyze_cross_dict.py),
[`research/sense_order_metrics.md`](../RussianTranslation/research/sense_order_metrics.md),
[`research/cross_dict_metrics.md`](../RussianTranslation/research/cross_dict_metrics.md). Full
preface evidence and probe-word reads:
[`research/HANDOFF_sense_ordering.md`](../RussianTranslation/research/HANDOFF_sense_ordering.md).
Source editions: Cologne Digital Sanskrit Lexicon (`csl-orig`). Citation-dating map:
`ls_source_map.json` / `ls_source_map_mw.json`.

## To do before submission

- Related work: position against Stamm/Hausmann lexicographic-microstructure theory and the
  Sanskrit-lexicography literature (Wezler, Vogel's *Indian Lexicography*).
- Add GRA and PW to the quantitative tables (GRA is single-corpus, so chronology is moot — a
  useful control); confirm the AP90 Vedic-siglum recall against a hand-checked sample.
- Decide venue (Lexikos vs IJL vs eLex) and trim to that length.
