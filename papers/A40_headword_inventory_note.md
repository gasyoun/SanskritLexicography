---
paper_id: A40
title: "Twelve Years of Headwords: A Controlled 2014-vs-2026 Census of the Cologne Digital Sanskrit Dictionaries and Their Corpus Grounding"
status: draft (skeleton, 3/5) — scaffolded 2026-06-26, advanced 2026-07-08 (H348)
readiness: 3/5
venue: "IJL / eLex"
author: "Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru"
data_source: "HeadwordLists/NOW_VS_THEN.md (census complete; figures regenerate from headword_diff.py against pinned csl-orig) + VisualDCS/dcs_lemma_summary.json (DCS-2021 attested lemmas; draft tables) + A38 / VisualDCS DCS-2026 release (98,606 lemmas — submission denominator, recompute pending)"
---

# Twelve Years of Headwords: A Controlled 2014-vs-2026 Census of the Cologne Digital Sanskrit Dictionaries and Their Corpus Grounding

_Created: 26-06-2026 · Last updated: 08-07-2026_

> **Draft status (2026-07-08, H348; scaffolded 2026-06-26).** Manuscript skeleton built
> directly on the completed census in
> [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md). All
> numerical claims below are transcribed from that synthesis and recompute from the
> frozen [then-2014/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014) snapshots vs the current
> [now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026) regeneration via
> [headword_diff.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py).
> **Home repo for the manuscript: SanskritLexicography `papers/`** — the census artifacts
> live in this repository; [gasyoun/VisualDCS](https://github.com/gasyoun/VisualDCS)
> contributes only the DCS denominator.
> **Advanced 08-07-2026 (readiness 2/5 → 3/5, H348, Fable 5 `claude-fable-5`):** §2
> Related work written; denominator policy locked (§3.3 — draft tables stay DCS-2021 as
> computed, the submission headline recomputes against A38's DCS-2026); the
> corpus-unattested ≠ ghost-word caveat and the lemmatizer-is-model-output caveat made
> first-class (§3.4, §6); claim→artifact inventory (§8) and companion-paper scope block
> (§9) added; the "eight format-migrated lists" miscount corrected to six.
> **Open before submission:** (1) pin a single csl-orig commit SHA and reconcile the
> AP 88,869/88,867 live-drift discrepancy; (2) recompute the attestation table against
> the DCS-2026 denominator (98,606) with a homograph control — until then the
> per-dictionary rates in §4.4 are **illustrative upper bounds** (bare-lemma join,
> DCS-2021); (3) venue + byline (a human decides); (4) add the A38 citation once its
> DOI is minted.

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

## 2. Related work

Three strands frame the contribution; none of them contains a controlled longitudinal
census of a digitized dictionary collection combined with a per-dictionary
corpus-grounding rate on one denominator — that combination is the novelty claim, not any
single count and not a new corpus.

**The collection as a digitisation project.** The Cologne Digital Sanskrit Dictionaries
([sanskrit-lexicon.uni-koeln.de](https://www.sanskrit-lexicon.uni-koeln.de/); source at
[sanskrit-lexicon/csl-orig](https://github.com/sanskrit-lexicon/csl-orig)) are documented
primarily as a digitisation and access programme: uniform XML markup over ~36
dictionaries, normalised headword keys (`<k1>`/`<k2>`), display and API layers. The
project's self-descriptions are synchronic — they state what the collection contains, not
how its inventory moves. Yet the post-2014 editing wave is the largest change to the
collection since the original digitisation (Apte's re-edit alone adds ~53k headwords,
§4.2), and it is visible only longitudinally. A40 treats the collection as a *versioned
object* with a measurable growth profile, exploiting the accident that a frozen 2014 key
export survived alongside the continuously edited source.

**Coverage studies of Sanskrit lexical resources.** Coverage comparisons across Sanskrit
resources exist mostly as engineering byproducts. Huet's *Sanskrit Heritage* lexicon
(Huet 2005) maintains its own headword inventory, whose overlap with the Cologne lists is
already tracked in this repository —
[coverage_additions_crosstagged.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/coverage_additions_crosstagged.tsv)
cross-tags our post-2014 additions against the Heritage and Catalan headword lists. The
Digital Corpus of Sanskrit (Hellwig; the DCS-2026 release is described in the companion
paper A38) supplies the attested-lemma inventory we use as denominator. What prior work
lacks is *symmetry*: each dictionary joined against the **same** corpus denominator, with
the join's upper-bound status stated, so that attestation rates are comparable across
lexica. That comparability is what §4.4 adds.

**Ghost words and lexicographer-only tradition.** Since Skeat's presidential address
coined the term (Skeat 1886), historical lexicography has known that corpus-unattested
entries are a mixture of transmission artefacts and genuine but text-poor tradition.
Sanskrit sharpens the distinction: the kośa lexica transmit real lexemes with thin or no
surviving textual attestation, and Monier-Williams marks senses resting on lexical
authority alone with `<ls>L.</ls>` ("Lexicographers"). The companion paper A45 works
through exactly this stratum for MW's botanical layer, and A39 states the matching
attestation-coverage caveats for verbal roots; A40 cites both rather than re-deriving
them. A low attestation rate is therefore read as a *property of a dictionary's purpose*
(corpus-facing vs corpus-detached, §4.4), never as an error rate.

## 3. Data and method

### 3.1 The two snapshots
Each `*-unique-key{1,2}-N.txt` file in [`then-2014/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014) is a frozen
2014 snapshot whose filename count `N` is its line count at extraction (first committed
**2014-10-05**, "Cologne headwords"; for three of the 26 files — AP-key2, MD-key2,
PD-key1 — the census's actual *then* line count differs slightly from the filename `N`,
so the census table's counts, not the filenames, are authoritative). The 2026 "now" side is re-extracted from the live
csl-orig source for the same field, written to [`now-2026/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026), and
diffed by [`headword_diff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py); full per-list word-level
diffs land under `HeadwordLists/_diff/`. We define **growth** = (now − then) / then and
**overlap** = the share of the *then* keys still present *now*.

> **TODO (pinning).** The 2026 side is extracted from a *live* repository that is edited
> daily, so a census must pin a single csl-orig commit. At scaffolding time csl-orig HEAD was
> `4f342dc4` (2026-06-26). The submission must quote one SHA and re-run against that exact
> checkout. A symptom of the drift is already visible: Apte's live key1 count appears as
> **88,869** in the census table but **88,867** in the prose and the `now-2026/` filename —
> a two-headword edit between two extractions; likewise AP key2 is **88,829** in the census
> table vs **88,828** in the on-disk `now-2026/` filename. Reconcile both to the pinned value.

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
is perfectly usable; it simply cannot be line-diffed against the numeric 2014 file). Six
lists are format-migrated: BHS, GRA-k2, MW-k2 (two snapshot variants), SCH, VEI-k2; the
two PD lists are set aside separately (PD has no csl-orig source, §6), so the 26 snapshots
partition as 18 comparable + 6 format-migrated + 2 PD.
[Verified in [`NOW_VS_THEN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md).]

### 3.3 The corpus-grounding denominator
For each comparable dictionary we compute the share of its headwords attested in a running
corpus, using the Digital Corpus of Sanskrit as the common denominator. The vendored
[`../../VisualDCS/dcs_lemma_summary.json`](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json) is the
**DCS-2021** asset: **83,239 attested SLP1 lemmas**, frequency-banded 1–5 (1 = hapax (1
occurrence), 2 = rare (2–9), 3 = uncommon (10–99), 4 = common (100–999), 5 = very-common
(1000+); source: Hellwig, DCS ~2021 snapshot, CC BY).

> **Denominator policy (locked 08-07-2026, H348).** One denominator per table, the release
> always stated, releases never mixed. Three distinct figures exist and must not be
> conflated: **98,606** distinct attested lemmas in the DCS-**2026** release (the companion
> paper A38; [VisualDCS CHANGELOG.md](https://github.com/gasyoun/VisualDCS/blob/main/CHANGELOG.md) +
> [m6_validation.md](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/m6_validation.md));
> **91,406** = the DCS-2021 attested-by-LemmaId figure; **83,239** = the DCS-2021
> attested-lemma list in the committed
> [dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json).
> The draft tables below are **DCS-2021 (83,239)** because that is the file the join was
> actually run against; the **submission headline recomputes against DCS-2026 (98,606)**,
> so that A40 cites its companion A38's release rather than a superseded snapshot. NB
> `dcs_lemma_summary.json` is the DCS-**2021** asset — never cite it for the 2026 figure
> (a conflation A39's fact-check pass already caught once).

### 3.4 The join, and its upper-bound caveat
The attestation rate is computed by intersecting each dictionary's headword key set with the
DCS lemma key set on surface form. Because homograph numbering (`<h>`) is collapsed and no
inflectional morphology is applied, a dictionary headword matches a DCS lemma on surface form
alone. **This is an upper bound**: collapsing homographs and ignoring inflection can only
inflate the apparent match. The reported rates in §4.4 are therefore ceilings, and the
submission applies a homograph control before drawing the corpus-facing/corpus-detached
conclusion. The cross-dict union behind this join —
[`union/union_headwords.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv), 323,425 headwords
across 15 dictionaries with gender-confirmed feminine folding — is documented in
[`union/UNION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md).

> **TODO (homograph control).** Replace or supplement the bare-lemma join with a control that
> bounds the homograph inflation (count distinct homograph senses, or intersect on a
> sense-normalised key), and report both the naive ceiling and the controlled estimate.

Two further caveats are first-class, not footnotes. **Corpus-unattested ≠ ghost word.** A
headword absent from DCS may be a transmission artefact — but equally a real lexeme of the
kośa tradition transmitted on lexicographer authority alone, the stratum Monier-Williams
explicitly marks `<ls>L.</ls>` ("Lexicographers"); the companion paper A45 works through
exactly this distinction for MW's botanical layer, and A39 carries the matching
attestation-coverage caveats for verbal roots. The typology in §4.4 therefore
*classifies* the unattested stratum; it does not condemn it. **The denominator is model
output.** DCS lemmatization is produced by the ByT5-Sanskrit pipeline (Nehrdich, Hellwig &
Keutzer 2024), so lemmatizer error bounds the join from both sides — a dictionary headword
can miss an attested lemma the model mis-lemmatized, and match a lemma the model invented.
The framing A39 applies to its root tables applies here unchanged.

## 4. Results

### 4.1 Aggregate growth (the 18 comparable lists)
Across the comparable lists, the headword inventory grows from **1,055,081 (2014) to
1,206,384 (2026)** — **+171,644 added, −20,341 removed, +14.3% net.** For scale, the grand
total of all 26 snapshots' 2014 line counts (including the format-migrated lists, which must
not be aggregated for growth) is **1,721,983**.

### 4.2 Growth is additive but uneven
The net growth is concentrated in a few actively-edited dictionaries; the canonical large
lexica are essentially frozen. Verified per-dictionary figures (comparable lists, from
[`NOW_VS_THEN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md)):

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

- **Format-migrated lists are an encoding artefact, not growth.** Six key2 lists migrated from
  legacy numeric transliteration to SLP1; their raw ~100% diff is meaningless and is excluded from
  the growth aggregate. Folding them in would be the single biggest way to produce a wrong number.
  More generally, headword-count comparability across dictionary generations is bounded by
  normalization and homonym-key drift between the 2014 extraction and the 2026 one — the
  comparable/format-migrated verdict per list is the census's control for exactly this.
- **The DCS attestation rate is an upper bound** in this draft (bare-lemma join, homographs
  collapsed, no inflection); the submission applies a homograph control and reports the controlled
  estimate as the headline.
- **The 2026 side drifts.** csl-orig is edited daily; the census must pin a SHA. The unreconciled
  AP 88,869/88,867 discrepancy is a live example.
- **One denominator only.** DCS-2021 (83,239) is the committed file the draft rates were computed
  against; the 2026 release (98,606, A38) and the 2021-by-LemmaId figure (91,406) are *different
  numbers* and must never be mixed into the same rate. The submission recomputes against DCS-2026
  (§3.3).
- **The denominator is model output.** DCS lemmatization is ByT5-Sanskrit output (Nehrdich,
  Hellwig & Keutzer 2024), not gold annotation; lemmatizer error propagates into every attestation
  rate (§3.4).
- **Corpus-unattested ≠ ghost word.** The unattested stratum includes the legitimate
  lexicographer-transmitted kośa layer (MW's `<ls>L.</ls>`); see §3.4 and the companion papers
  A45 (botanical layer) and A39 (verbal roots).
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

## 8. Claim → artifact inventory

Every headline claim, its figure, and the committed artifact it recomputes from
(per the `/paper-scaffold` discipline — a claim without a committed artifact is a gap,
flagged as such):

| # | Claim | Figure(s) | Artifact | Status |
|--:|---|---|---|---|
| 1 | Aggregate comparable growth 2014→2026 | 1,055,081 → 1,206,384; +171,644 added / −20,341 removed; +14.3% | [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) TOTAL row (18 comparable lists) | ✅ committed |
| 2 | Growth is concentrated: AP +146.7% (36,030 → 88,869), PWK +14.7% (131,918 → 151,349); MW +0.1%, PWG −0.0% | per-list table rows | [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) | ✅ committed |
| 3 | Six format-migrated lists excluded from the growth aggregate (BHS, GRA-k2, MW-k2 ×2, SCH, VEI-k2); 26 snapshots = 18 comparable + 6 migrated + 2 PD | verdict column | [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md) | ✅ committed |
| 4 | Removals are an audit channel (−20,341; per-list removed samples) | §4.3 | `_diff/<list>.removed.txt` — **not committed**, regenerated deterministically by [headword_diff.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py); 40-item samples inline in NOW_VS_THEN.md | ⚠️ regenerable |
| 5 | Per-dictionary attestation rates, VEI 69.8% … SKD 14.1% (~5× spread) | §4.4 table | [dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json) (DCS-2021) × current key1 lists | ⬜ upper bound; DCS-2026 + homograph-control recompute pending |
| 6 | Union-wide attestation 61,340 / 323,425 = 19.0% (upper bound) | §4.4 | [union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv) + [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md) | ✅ committed (same recompute pending) |
| 7 | DCS-2026 denominator = 98,606 distinct attested lemmas | §3.3 | A38 / [VisualDCS CHANGELOG.md](https://github.com/gasyoun/VisualDCS/blob/main/CHANGELOG.md) + [m6_validation.md](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/reports/m6_validation.md) | ✅ committed; ⬜ cite A38 DOI when minted |
| 8 | 2014 snapshot provenance (frozen export, first committed 2014-10-05, "Cologne headwords") | §3.1 | git history of [then-2014/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014) | ✅ committed |

## 9. Scope versus companion papers (anti-salami)

- **A38 (the DCS-2026 release)** owns the corpus: the treebank/SQLite release pipeline,
  its validation, and the 98,606-lemma inventory. A40 **cites** the denominator and never
  re-describes the release.
- **A39 (verbal-root disagreement)** owns the grammar-vs-dictionary-vs-corpus story for
  roots; A40 does not re-litigate root attestation.
- **A45 (botanical crosswalk)** owns the `<ls>L.</ls>` lexicographer-stratum attestation
  story for MW's plant names; A40 cites its treatment as the worked example of
  "unattested ≠ ghost".
- A40 leads with exactly two things nothing else owns: the **controlled 2014-vs-2026
  growth census** and the **per-dictionary attestation typology on one denominator**.

## Data and reproducibility

The census, every figure, and the comparable-vs-format-migrated verdicts live in
[`../HeadwordLists/NOW_VS_THEN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md); the generator is
[`../HeadwordLists/headword_diff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py)
(`python headword_diff.py` rebuilds the table + `_diff/`; `headword_diff.py now` rewrites
[`now-2026/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)). Frozen 2014 snapshots are in
[`then-2014/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014); the cross-dict union and DCS/Catalan/Huet coverage
tags are in [`../HeadwordLists/union/`](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/union) (builder
[`build_union.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/build_union.py)). The corpus denominator is
[`../../VisualDCS/dcs_lemma_summary.json`](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json) (DCS-2021,
83,239 attested SLP1 lemmas, CC BY). Reproduction requires pinning the csl-orig commit (TODO:
SHA — `4f342dc4` at scaffolding) and stating the single DCS release used. The work is a census and
a coverage measurement only — it never edits csl-orig. *(TODO: add A38's DOI to the reference list
once minted.)*

## References ⬜

- Cologne Digital Sanskrit Dictionaries (CDSL), Universität zu Köln —
  [sanskrit-lexicon.uni-koeln.de](https://www.sanskrit-lexicon.uni-koeln.de/); source markup at
  [sanskrit-lexicon/csl-orig](https://github.com/sanskrit-lexicon/csl-orig).
- Hellwig, O. *Digital Corpus of Sanskrit (DCS)* — DCS-2021 attested-lemma list via
  [dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json)
  (CC BY); DCS-2026 release via the companion paper A38.
- Huet, G. 2005. A functional toolkit for morphological and phonological processing,
  application to a Sanskrit tagger. *Journal of Functional Programming* 15(4): 573–614.
  (The Sanskrit Heritage platform — [sanskrit.inria.fr](https://sanskrit.inria.fr/).)
- Monier-Williams, M. 1899. *A Sanskrit-English Dictionary* — Cologne digitization
  ([csl-orig](https://github.com/sanskrit-lexicon/csl-orig)); the `<ls>L.</ls>`
  ("Lexicographers") source marker.
- Nehrdich, S., O. Hellwig & K. Keutzer. 2024.
  [One model is all you need: ByT5-Sanskrit, a unified model for Sanskrit NLP tasks](https://aclanthology.org/2024.findings-emnlp.805/).
  *Findings of EMNLP 2024*.
- Skeat, W. W. 1886. Report upon "ghost-words", or words which have no real existence
  (presidential address). *Transactions of the Philological Society* 1885–87.
- ⬜ A38, A39, A45 self-citations once their venues/DOIs freeze.

_Dr. Mārcis Gasūns_
