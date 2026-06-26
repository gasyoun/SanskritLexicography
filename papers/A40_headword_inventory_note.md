---
paper_id: A40
title: "Twelve Years of Headwords: A Controlled 2014-vs-2026 Census of the Cologne Digital Sanskrit Dictionaries and Their Corpus Grounding"
status: draft (skeleton, 2/5) — scaffolded 2026-06-26
readiness: 2/5
venue: "IJL / eLex"
author: "Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru"
data_source: "HeadwordLists/NOW_VS_THEN.md (census complete; figures regenerate from headword_diff.py against pinned csl-orig) + VisualDCS/dcs_lemma_summary.json (DCS-2021 attested lemmas)"
---

# Twelve Years of Headwords: A Controlled 2014-vs-2026 Census of the Cologne Digital Sanskrit Dictionaries and Their Corpus Grounding

> **Draft status (2026-06-26).** Manuscript skeleton built directly on the completed
> census in [`../HeadwordLists/NOW_VS_THEN.md`](../HeadwordLists/NOW_VS_THEN.md). All
> numerical claims below are transcribed from that synthesis and recompute from the
> frozen [`then-2014/`](../HeadwordLists/then-2014/) snapshots vs the current
> [`now-2026/`](../HeadwordLists/now-2026/) regeneration via
> [`headword_diff.py`](../HeadwordLists/headword_diff.py). **Open before submission:**
> (1) write §2 Related work; (2) pin a single csl-orig commit SHA and reconcile the
> AP 88,869/88,867 live-drift discrepancy; (3) lock ONE DCS denominator (DCS-2021's
> 83,239 attested lemmas) and recompute the per-dictionary attestation table with a
> homograph control, reporting each rate as an upper bound; (4) finalise the byline
> (ORCID) and add the A38 citation once its DOI is minted. The per-dictionary
> DCS-attestation rates in §4.3 are **illustrative upper bounds** (bare-lemma join)
> pending the homograph control.

## Abstract

The Cologne Digital Sanskrit Dictionaries (CDSL) are the de-facto reference corpus of
Sanskrit lexicography, but how their headword inventories actually evolve over time, and
how far those inventories are anchored in attested usage, has not been measured
systematically. We present two complementary measurements on a single, uniformly
marked-up collection. First, a **controlled longitudinal census**: comparing a frozen
2014 headword snapshot against a 2026 re-extraction of the same field, across the ~18
dictionaries whose key format is stable enough to diff honestly, the comparable headword
inventory grows from **1,055,081 to 1,206,384 entries (+14.3%)** — **+171,644 added and
−20,341 removed**. Growth is **additive but strikingly uneven**: Apte's dictionary more
than doubles (**+146.7%**, 36,030 → 88,869 headwords) while the two largest lexica,
Monier-Williams and the Petersburg dictionaries, are essentially frozen (**MW +0.1%, PWG
−0.0%**). The ~20k removals are not noise but an **audit signal** — merges, corrections,
and occasional accidental deletions. Second, a **per-dictionary corpus-grounding rate**:
joining each dictionary's headwords against a single common denominator — the attested
lemmas of the Digital Corpus of Sanskrit — separates **corpus-facing** lexica (Grassmann's
Rig-Veda dictionary, the Vedic Index) from **corpus-detached** ones (the Śabdakalpadruma)
by a factor of roughly five. We argue that a longitudinal, controlled census plus a
common-denominator attestation rate is a more honest portrait of a dictionary collection
than any single headword count, and we release the reproducible diff machinery and the
2014/2026 snapshots as the dataset behind the claims.

## 1. Introduction

A dictionary collection is usually described by a single number: "194,000 headwords",
"36,000 entries". That number is a snapshot of one edition at one moment, and it conflates
two things a lexicographer actually cares about — how the inventory is *changing*, and how
much of it is *grounded in attested language* rather than inherited from earlier lexica or
generated as nonce compounds. The Cologne Digital Sanskrit Dictionaries are an unusually
clean testbed for separating these. The same ~36 dictionaries are marked up in a uniform
XML, each entry carrying a normalised computational key (`<k1>`) and a closer-to-print key
(`<k2>`); and a frozen 2014 export of those keys has been preserved alongside the
continuously-edited live source, giving a genuine twelve-year baseline rather than a
reconstructed one.

We ask two questions:

1. **How has the headword inventory changed, 2014 → 2026, when measured honestly?**
   "Honestly" is the operative word: a naive diff of every committed list against the
   current source reports nonsense for the lists whose 2014 snapshot was in a legacy
   transliteration that has since migrated to SLP1. We isolate the **comparable** lists
   (same key format then and now) from the **format-migrated** ones, and aggregate growth
   only over the former.

2. **How corpus-grounded is each dictionary?** Using one common denominator — the attested
   lemmas of the Digital Corpus of Sanskrit (DCS) — we compute a per-dictionary attestation
   rate, and show that it cleanly separates corpus-facing from corpus-detached lexica.

Our claims:

1. **Growth is additive but uneven.** The inventory grows monotonically in aggregate
   (+14.3%), but the growth is concentrated in a few actively-edited dictionaries (Apte,
   Böhtlingk's shorter recension) while the canonical large lexica are near-frozen.
2. **Removals are an audit channel.** The ~20k headwords present in 2014 and gone in 2026
   are a QA signal — most are corrections and merges, but the list is the right place to
   catch accidental data loss.
3. **A common-denominator attestation rate separates corpus-facing from corpus-detached
   lexica** — a property of the dictionary's purpose, not its size.
4. **A census is a method, not a one-off count.** The diff machinery is committed and
   re-runs against any pinned csl-orig checkout, so the census is reproducible and
   repeatable as the source evolves.

## 2. Related work *(TODO — to be written)*

Position against: CDSL / Cologne project descriptors and the history of the digitisation;
corpus-coverage and lexical-coverage studies for Sanskrit (Gérard Huet's *Sanskrit Heritage*
lexicon, the Catalan headword list — both already cross-tagged against our additions in
[`union/coverage_additions_crosstagged.tsv`](../HeadwordLists/union/coverage_additions_crosstagged.tsv));
the Digital Corpus of Sanskrit and its descriptors (Hellwig; and the companion DCS-2026
release described in A38); and the broader literature on dictionary growth / lexical
inflation and on "ghost words" / unattested headwords in historical lexicography. The
novelty claim is the **controlled longitudinal census** combined with the **per-dictionary
corpus-grounding rate on one common denominator** — not any single count and not a new
corpus.

## 3. Data and method

### 3.1 The two snapshots
Each `*-unique-key{1,2}-N.txt` file in [`then-2014/`](../HeadwordLists/then-2014/) is a frozen
2014 snapshot whose filename count `N` is its line count at extraction (first committed
**2014-10-05**, "Cologne headwords"). The 2026 "now" side is re-extracted from the live
csl-orig source for the same field, written to [`now-2026/`](../HeadwordLists/now-2026/), and
diffed by [`headword_diff.py`](../HeadwordLists/headword_diff.py); full per-list word-level
diffs land under `HeadwordLists/_diff/`. We define **growth** = (now − then) / then and
**overlap** = the share of the *then* keys still present *now*.

> **TODO (pinning).** The 2026 side is extracted from a *live* repository that is edited
> daily, so a census must pin a single csl-orig commit. At scaffolding time csl-orig HEAD was
> `4f342dc4` (2026-06-26). The submission must quote one SHA and re-run against that exact
> checkout. A symptom of the drift is already visible: Apte's live key1 count appears as
> **88,869** in the census table but **88,867** in the prose and the `now-2026/` filename —
> a two-headword edit between two extractions. Reconcile to the pinned value.

### 3.2 key1 vs key2, and the comparability rule
`<k1>` is the normalised computational key (built for matching/dedup; may match no printed
form); `<k2>` is closer to print (retains `-`, `/` accent, parentheses). The decisive
methodological point is that **not every committed list can be honestly diffed.** A list is
**comparable** when its 2014 snapshot and the live 2026 field share a key format, so
`added`/`removed`/`growth` are genuine headword changes. A list is **format-migrated** when
the 2014 `<k2>` snapshot is in the *legacy Cologne numeric transliteration* (e.g. `am2s4a` =
*aṃśa*) while csl-orig is now SLP1: the raw then-vs-now diff is ~100% and is an encoding
artefact, **not** a headword change. We therefore aggregate growth **only over the comparable
lists**, and report the format-migrated lists in a separate panel (their *current* SLP1 form
is perfectly usable; it simply cannot be line-diffed against the numeric 2014 file). Eight
lists are format-migrated: BHS, GRA-k2, MW-k2 (two snapshot variants), SCH, VEI-k2.
[Verified in [`NOW_VS_THEN.md`](../HeadwordLists/NOW_VS_THEN.md).]

### 3.3 The corpus-grounding denominator
For each comparable dictionary we compute the share of its headwords attested in a running
corpus, using the Digital Corpus of Sanskrit as the common denominator. The vendored
[`../../VisualDCS/dcs_lemma_summary.json`](../../VisualDCS/dcs_lemma_summary.json) is the
**DCS-2021** asset: **83,239 attested SLP1 lemmas**, frequency-banded 1–5 (1 = hapax (1
occurrence), 2 = rare (2–9), 3 = uncommon (10–99), 4 = common (100–999), 5 = very-common
(1000+); source: Hellwig, DCS ~2021 snapshot, CC BY).

> **TODO (one denominator).** A40 must fix a single denominator and never mix releases. The
> DCS-**2026** release (A38) reports **98,606** distinct attested lemmas; **91,406** is the
> 2021 attested-by-LemmaId figure; **83,239** is the 2021 attested-lemma list in the committed
> file. We recommend pinning **DCS-2021 (83,239)**, because that is the file actually committed
> in this repository, and stating the release explicitly wherever an attestation rate appears.

### 3.4 The join, and its upper-bound caveat
The attestation rate is computed by intersecting each dictionary's headword key set with the
DCS lemma key set on surface form. Because homograph numbering (`<h>`) is collapsed and no
inflectional morphology is applied, a dictionary headword matches a DCS lemma on surface form
alone. **This is an upper bound**: collapsing homographs and ignoring inflection can only
inflate the apparent match. The reported rates in §4.3 are therefore ceilings, and the
submission applies a homograph control before drawing the corpus-facing/corpus-detached
conclusion. The cross-dict union behind this join —
[`union/union_headwords.tsv`](../HeadwordLists/union/union_headwords.tsv), 323,425 headwords
across 15 dictionaries with gender-confirmed feminine folding — is documented in
[`union/UNION.md`](../HeadwordLists/union/UNION.md).

> **TODO (homograph control).** Replace or supplement the bare-lemma join with a control that
> bounds the homograph inflation (count distinct homograph senses, or intersect on a
> sense-normalised key), and report both the naive ceiling and the controlled estimate.

## 4. Results

### 4.1 Aggregate growth (the 18 comparable lists)
Across the comparable lists, the headword inventory grows from **1,055,081 (2014) to
1,206,384 (2026)** — **+171,644 added, −20,341 removed, +14.3% net.** For scale, the grand
total of all 26 snapshots' 2014 line counts (including the format-migrated lists, which must
not be aggregated for growth) is **1,721,983**.

### 4.2 Growth is additive but uneven
The net growth is concentrated in a few actively-edited dictionaries; the canonical large
lexica are essentially frozen. Verified per-dictionary figures (comparable lists, from
[`NOW_VS_THEN.md`](../HeadwordLists/NOW_VS_THEN.md)):

| dictionary (list) | 2014 | 2026 | added | removed | overlap | growth |
|---|--:|--:|--:|--:|--:|--:|
| AP — Apte (key1) | 36,030 | 88,869 | 53,742 | 903 | 97.5% | **+146.7%** |
| AP — Apte (key2) | 36,126 | 88,829 | 56,024 | 3,321 | 90.8% | +145.9% |
| PWK — Böhtlingk kl. (key2) | 133,741 | 155,688 | 23,265 | 1,318 | 99.0% | +16.4% |
| PWK — Böhtlingk kl. (key1) | 131,918 | 151,349 | 19,617 | 186 | 99.9% | +14.7% |
| GRA — Grassmann RV (key1) | 10,315 | 11,108 | 975 | 182 | 98.2% | +7.7% |
| VCP — Vācaspatyam (key1) | 47,107 | 48,636 | 2,514 | 985 | 97.9% | +3.2% |
| SKD — Śabdakalpadruma (key1) | 40,551 | 40,817 | 807 | 541 | 98.7% | +0.7% |
| MW — Monier-Williams (key1) | 193,978 | 194,084 | 754 | 648 | 99.7% | **+0.1%** |
| PWG — Petersburg gr. (key1) | 106,085 | 106,082 | 149 | 152 | 99.9% | **−0.0%** |
| CCS — Cappeller (key2) | 29,317 | 29,233 | 3,328 | 3,412 | 88.4% | −0.3% |

The picture is clear: **Apte more than doubles** (+146.7%), **PWK adds ~20k headwords**
(+14.7%), and **MW/PWG do not move** (+0.1% / −0.0%). The high-overlap-but-nonzero-churn rows
(CCS −0.3% with 3,328 added *and* 3,412 removed) are mostly editorial re-keying rather than
inventory change. *(TODO: paste the full comparable table from `NOW_VS_THEN.md`.)*

### 4.3 Removals as an audit signal
The −20,341 removed headwords (present 2014, gone 2026) are merges, corrections, or accidental
deletions; the full per-list lists are in `HeadwordLists/_diff/<list>.removed.txt`. The
distribution is informative on its own: Apte's 903 key1 removals against +53,742 additions read
as a thorough re-edit, whereas PWG's 152 removals against 149 additions read as targeted
corrections. *(TODO: sample-classify a slice — e.g. AP's 903 key1 removals — into "genuine
correction" vs "possible data loss" so the removal count reads as QA, not churn.)*

### 4.4 Corpus grounding separates the lexica
Joining each dictionary's headwords against the **83,239 DCS-2021 attested lemmas** (bare-lemma,
**upper bound**) gives the following verified illustrative rates (key1, current 2026 snapshots):

| dictionary (key1) | headwords | in DCS-2021 | rate (upper bound) |
|---|--:|--:|--:|
| VEI — Vedic Index | 3,704 | 2,584 | **69.8%** |
| GRA — Grassmann RV | 11,108 | 7,569 | **68.1%** |
| VCP — Vācaspatyam | 48,636 | 23,742 | 48.8% |
| PWG — Petersburg gr. | 106,082 | 40,960 | 38.6% |
| PWK — Böhtlingk kl. | 151,349 | 47,366 | 31.3% |
| MW — Monier-Williams | 194,084 | 57,157 | 29.4% |
| AP — Apte | 88,867 | 19,338 | 21.8% |
| SKD — Śabdakalpadruma | 40,817 | 5,741 | **14.1%** |

Union-wide, **61,340 of 323,425** headwords match a DCS-2021 attested key (**19.0%**, upper
bound). The separation tracks each dictionary's *purpose*: the corpus-facing Vedic lexica
(VEI 69.8%, GRA 68.1% — both built directly off a fixed corpus) sit at the top; the
corpus-detached encyclopaedic-traditional lexica (SKD 14.1%) sit at the bottom; the general
descriptive dictionaries (MW, PWG, PWK ~29–39%) sit in between. This ~5× spread is the central
empirical result of the corpus-grounding analysis. *(TODO: recompute with the homograph control
and add the freq-band breakdown — how much of each dict's attested share is hapax band-1 vs
very-common band-5 — then state the controlled, not the ceiling, figures as the headline.)*

## 5. Discussion

Two portraits of the same collection emerge. The **longitudinal** portrait shows a collection
that grows by accretion concentrated in a handful of dictionaries: Apte's dramatic expansion
and PWK's steady accumulation drive almost all of the +14.3%, while the two canonical large
lexica are frozen reference points. For anyone re-running a downstream analysis (coverage
studies, alignment, frequency joins), this means **only a few dictionaries need re-processing
between editions** — a practical payoff of the census.

The **corpus-grounding** portrait is orthogonal to size. A dictionary's attestation rate is a
property of what it was built to describe, not how big it is: the small Vedic lexica are the
most corpus-grounded, the large traditional Śabdakalpadruma the least, with the descriptive
dictionaries in between. This is the kind of axis that a raw headword count actively hides — MW
and SKD differ by ~5× in headwords *and* ~2× in grounding, in opposite directions.

Read together, the two measurements argue that a dictionary collection is better described by a
**growth profile** and a **grounding rate** than by a single inventory number; both are cheap to
recompute and both expose structure a count cannot.

## 6. Limitations

- **Format-migrated lists are an encoding artefact, not growth.** Eight key2 lists migrated from
  legacy numeric transliteration to SLP1; their raw ~100% diff is meaningless and is excluded from
  the growth aggregate. Folding them in would be the single biggest way to produce a wrong number.
- **The DCS attestation rate is an upper bound** in this draft (bare-lemma join, homographs
  collapsed, no inflection); the submission applies a homograph control and reports the controlled
  estimate as the headline.
- **The 2026 side drifts.** csl-orig is edited daily; the census must pin a SHA. The unreconciled
  AP 88,869/88,867 discrepancy is a live example.
- **One denominator only.** DCS-2021 (83,239) is the committed file; the 2026 release (98,606) and
  the 2021-by-LemmaId figure (91,406) are *different numbers* and must never be mixed into the same
  rate.
- **PD (Deccan College dictionary) has no csl-orig source** locally, so it is censused only on its
  2014 snapshot and excluded from the growth and grounding tables.

## 7. Conclusion

A twelve-year, controlled census of the Cologne Digital Sanskrit Dictionaries shows additive but
uneven headword growth — +14.3% overall, driven almost entirely by Apte (+146.7%) and PWK
(+14.7%) while Monier-Williams and the Petersburg dictionary stand still — with ~20k removals
that serve as a correction-and-data-loss audit. A per-dictionary attestation rate against a single
corpus denominator separates corpus-facing from corpus-detached lexica by roughly fivefold. A
growth profile plus a grounding rate is a more faithful description of a dictionary collection than
any headline inventory number, and both are reproducible from the committed diff machinery.

## Data and reproducibility

The census, every figure, and the comparable-vs-format-migrated verdicts live in
[`../HeadwordLists/NOW_VS_THEN.md`](../HeadwordLists/NOW_VS_THEN.md); the generator is
[`../HeadwordLists/headword_diff.py`](../HeadwordLists/headword_diff.py)
(`python headword_diff.py` rebuilds the table + `_diff/`; `headword_diff.py now` rewrites
[`now-2026/`](../HeadwordLists/now-2026/)). Frozen 2014 snapshots are in
[`then-2014/`](../HeadwordLists/then-2014/); the cross-dict union and DCS/Catalan/Huet coverage
tags are in [`../HeadwordLists/union/`](../HeadwordLists/union/) (builder
[`build_union.py`](../HeadwordLists/build_union.py)). The corpus denominator is
[`../../VisualDCS/dcs_lemma_summary.json`](../../VisualDCS/dcs_lemma_summary.json) (DCS-2021,
83,239 attested SLP1 lemmas, CC BY). Reproduction requires pinning the csl-orig commit (TODO:
SHA — `4f342dc4` at scaffolding) and stating the single DCS release used. The work is a census and
a coverage measurement only — it never edits csl-orig. *(TODO: add A38's DOI to the reference list
once minted.)*
