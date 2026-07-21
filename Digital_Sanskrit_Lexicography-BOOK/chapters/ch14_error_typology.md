# Chapter 14 — Surface, Not Substance: An Error Typology of Twelve Years of Collaborative Correction

_Created: 13-07-2026 · Last updated: 21-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Surface, Not Substance:
> A Two-Axis Error Typology of Twelve Years of Correction to the Cologne Digital Sanskrit
> Lexicon* (source draft:
> [paper-obs-t-error-typology.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)),
> which is being published separately in a journal version (target: LREC-COLING / *IJL*); where
> the article must remain independently citable, cite that version. Every count and table below
> is carried over from the article unchanged and is reproducible from the committed corpus
> ([`correction_events_release.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv),
> CC-BY-4.0). The figures are the released **52,498-event** snapshot (2014–2026); an earlier
> draft of the book's data inventory listed a 50,953-event cut, superseded here and since
> corrected in the plan itself (21-07-2026). Only the framing has been
> converted from journal to book form — the abstract and keywords removed, companion-paper
> labels remapped to this book's chapters, and the collaborative-lexicography literature engaged
> at the monograph's depth. Section numbering is chapter-internal (§1–§8).

This is the book's last data chapter, and it closes the arc that ran from the dictionary as a
finished object to the dictionary as a *living* one. Every earlier chapter measured what a
dictionary *says*; this one measures what was *wrong* with it — where, how, and how that changed
across twelve years — by reading the record of its corrections. That record is the most direct
possible instantiation of the book's thesis. The Introduction defined the evidence graph as
carrying, per statement, a *review provenance*; here the review provenance is the whole dataset,
52,498 dated edits by 208 named correctors, each stamped with an evidence label — `observed`,
`derived`, or `inferred` — that is literally the four-grade vocabulary of Chapter 2 applied to
the acts of maintenance themselves. The dictionary that Chapter 12 showed inheriting an
*apparatus without errors* is here caught in the act of removing the errors it did have.

The chapter also carries the book's most important reading rule, and states it as its own
title's caveat. What the corpus records is *corrected* events — where curators chose to look and
act — not a latent error rate. A dictionary with a high correction density may be *better*
maintained, not worse. Every share reported here is a share of curatorial attention, which is a
more human thing than a list of a dictionary's mistakes, and keeping that distinction visible is
the same evidence-grade honesty the whole book is built on.

## 1. Introduction

Digitised historical dictionaries are corrected continuously after publication, and the record
of those corrections is itself a dataset — one that answers a question rarely asked of a
dictionary: not *what does it say* but *what was wrong with it, where, and how did that change
over time*. For the Cologne Digital Sanskrit Lexicon (CDSL), that record spans twelve years, two
distinct collection regimes (a public correction form, then a source git repository),
forty-three dictionaries and several hundred contributors. This chapter assembles it into a
single typed corpus and reads an error typology off it.

That such a record is analysable at all rests on a data advantage: I hold both the corrections
*and* the XML-tagged source files (`csl-orig`) locally, so each edit can be *located* inside the
dictionary microstructure it repairs — a headword versus a definition versus a source citation —
rather than treated as an undifferentiated string change. That single capability turns a
changelog into a typology. The contributions are: a unified, IAST-normalised, evidence-labelled
corpus of 52,498 correction events (§3); a two-axis typology, *location* × *edit-type*, whose
orthogonality is established empirically (§4); three tested findings on the shape,
dictionary-dependence, and diachrony of the error profile (§5); and a released language resource
with a temporal split and reference baselines (§6).

The chapter sits at the meeting point of two literatures the book has otherwise kept apart. It is
a *case* of the collaborative-lexicography research on user participation — the
direct / indirect / accessory taxonomy of user contribution, user-submitted corrections, and
quality-voting that the digital-lexicography handbooks describe (Abel and Meyer 2014) — and its
correction workflow is close to a textbook instance of error-handling in the lexicographic
process (Klosa-Kückelhaus and Tiberius 2014). The versioned-dictionary infrastructure it
presupposes — per-entry revision histories, an editable published text — is the one the field
already built for the *OED* Online and documents as such (Herold, Meyer, and Wiegand 2014;
Brewer 2007), so this chapter cites that precedent rather than reinventing it. And its analytic
stance — treating a dictionary's error record as legitimate evidence about the dictionary — is
exactly the dictionary-criticism methodology the reference literature sanctions (Hartmann and
James 1998; Akasu 2013), extended from the review essay to a corpus of fifty thousand events.
Collaborative post-publication revision is itself no digital novelty: it is the mechanism behind
every great historical dictionary's supplements and the pre-digital slip-and-reader tradition
(Partridge 1963); what is new is that here it is *measured*.

## 2. Two questions, two tracks — and why two axes

A companion finding measures the correction *process* — who corrects, when, and how fast; this
chapter measures the corrected *content* — what was wrong and where. Error typologies in the
adjacent literatures are single-axis by construction: the grammatical-error-correction scheme
ERRANT (Bryant et al. 2017) types edits by operation × part-of-speech; the OCR/digitisation
literature types by substitution / segmentation / reading-order; classical textual criticism
(Katre 1941) types by omission / addition / substitution / transposition. Each is a
*kind-of-change* taxonomy. The dictionary adds a second, orthogonal question those schemes do not
ask — *which part of the entry* was repaired — and §4.3 shows that collapsing the two into one
column, as my own first design did, is a measurable error. The typology is therefore reported as
two axes, with the edit-type axis crosswalked to all three external schemes so a reviewer from
any tradition can read it. The *interpretation* of the location axis — what it means that a
dictionary's errors sit in its citations versus its definitions — connects directly to the
microstructure chapters of this book (citation registers, Chapter 10; sense inheritance,
Chapter 6; indigenous microstructure, Chapter 7).

## 3. Data

The corpus unifies five provenance layers, each event stamped with its `source_layer` so any
figure can be sliced or audited by origin: the 2014–2019 correction-form export (richest per
event, carrying the corrector's own description), the `csl-orig` git history (largest, extending
to the present), a hand log and printchange files, the formal change-batches of the recent
curated campaigns, and an org-metrics backdrop. One row is one correction event — a dated
old→new edit to a dictionary source, carrying dictionary, headword, normalised strings, a
verbatim audit copy, an edit-op trace, both typology axes, three crosswalk columns, the resolved
corrector, and an **evidence label** (`observed` / `derived` / `inferred`); no figure in this
chapter hides that label.

Normalising the form archive to IAST is not a formality but a finding. The form cells are
mixed-encoding across dictionaries — some correctors typed Devanagari, others Harvard-Kyoto
romanisation (`bharahezaravRtti` = *bharaheśaravṛtti*), while the sources are SLP1 — so a single
historical correction archive can carry three transliteration systems, and any cross-dictionary
statistic that does not unify them first will mis-segment the edits.

## 4. Method — the two-axis typology

**The edit-operation trace.** For every event I compute a Damerau–Levenshtein alignment over NFD
characters — so a diacritic is its own combining character and therefore its own edit — yielding
a typed operation list (`sub`/`ins`/`del`/`transpose` × `diacritic`/`vowel`/`consonant`/
`whitespace`/…). This trace drives both the edit-type axis and the three external crosswalks.

**Axis A — location.** Each event is attributed to the microstructure component it repairs by
joining to the `csl-orig` record and locating the changed text among its XML tags (`<k1>` →
headword, `<lex>` → grammar, `<ls>` → citation, definition prose → sense, tag delimiters →
markup). On the git layer the join is 100 % positional; on the form layer only 28.8 % join,
because the form's location cell is free text and the 2014-era record ids have *drifted* against
today's sources. Location is reported on derived labels only — join failures are labelled
`unattributed`, never guessed.

**Axis B — edit-type, and why the axes are separate.** My first design used a single "component"
column, filling it from the location-join where possible and from an edit-type heuristic
otherwise. A human-free reliability check exposed the mistake: on the 6,969 form events where
both signals are available, they agree only **0.1 %** of the time. That near-zero is structural —
the join answers *where* (a headword typo → `headword`) while the heuristic answers *what kind* (a
typo → `orthography`); they disagree because they measure different things. The 0.1 % is thus not
a data-quality failure but the measurement that justifies the paper's central methodological
move: derive location from the source join, keep edit-type in its own axis, and never file a type
value into the location column. The edit-type axis is additionally typed under ERRANT,
OCR/digitisation, and Katre's textual-criticism schemes — one corpus, four readings.

## 5. Results

**Headline.** 52,498 correction events over 2014-03-18 to 2026-05-30, across 43 dictionaries and
208 named correctors; **64.3 % carry a derived (non-heuristic) label** (33,755 derived / 18,743
inferred). Where a resolution date is recorded, the median correction latency is 12 days.

**Axis A — where corrections land.** On derived labels (n = 33,755), corrections concentrate most
strongly in **sense** fields (Table 1).

**Table 1.** Location of corrections (derived labels).

| Location | Events | Share |
|---|---:|---:|
| sense (definition) | 17,778 | 52.7 % |
| markup | 5,902 | 17.5 % |
| headword | 5,823 | 17.3 % |
| citation | 3,335 | 9.9 % |
| meta | 624 | 1.8 % |
| grammar | 293 | 0.9 % |

**Axis B — what kind of change.** Every edit-type is a surface change; the corpus contains **no
"content rewrite" category** (Table 2).

**Table 2.** Edit-type of corrections (all 52,498 events).

| Edit type | Events | Share |
|---|---:|---:|
| spelling | 11,683 | 22.3 % |
| spacing | 10,233 | 19.5 % |
| punctuation | 9,506 | 18.1 % |
| source-raw | 7,852 | 15.0 % |
| diacritic | 4,785 | 9.1 % |
| case | 3,813 | 7.3 % |
| digit | 2,907 | 5.5 % |
| (none) | 1,228 | 2.3 % |
| transposition | 491 | 0.9 % |

**H1 — surface edits, uneven by location.** Corrections are usually small: the median edit
distance is 2, and 63 % are ≤2 characters. What matters is how unevenly that surface signal
distributes by location (Table 3) — headword corrections are overwhelmingly small form fixes
(85.6 % minor), while markup, citation, and grammar involve longer structural edits.

**Table 3.** Minor-edit rate by location, with 95 % Wilson CIs.

| Location | n | minor-edit rate (95 % CI) |
|---|---:|---|
| sense | 17,778 | 38.2 % [37.5, 39.0] |
| markup | 5,902 | 5.2 % [4.6, 5.7] |
| headword | 5,823 | 85.6 % [84.7, 86.5] |
| citation | 3,335 | 25.0 % [23.6, 26.5] |
| meta | 624 | 66.2 % [62.4, 69.8] |
| grammar | 293 | 13.3 % [9.9, 17.7] |

**H2 — the location profile is a per-dictionary fingerprint.** A chi-square test of location ×
dictionary (top 15 by volume, derived labels) gives χ² = 26,192.5, dof = 70, with **Cramér's
V = 0.432** (commit-block bootstrap CI [0.407, 0.482]). Dictionaries differ in *where* their
errors sit, not merely how many they have.

**H3 — the profile shifts over twelve years.** Mann–Kendall trend diagnostics on yearly shares
show directional movement: headword corrections fall (τ = −0.462; 0.88 → 0.10 of the yearly
share), while markup rises (τ = 0.564; 0.00 → 0.17); after Benjamini–Hochberg correction the
series is best reported as directional rather than as significant trend claims. On the edit-type
axis, spacing, punctuation, and source-raw edits rise while spelling, case, and transposition
fall.

**The character-confusion signal.** Read through the external schemes, the same edits distribute
across OCR substitution/insertion/deletion/segmentation and Katre addition/substitution/omission
with a classical metathesis/haplography/dittography tail. The clean form-layer phoneme signal is
led by **b → v** (341), the classic Sanskrit orthographic merger, followed by *k*/*t*, *s*/*m*
and a retroflex/diacritic repair cluster — exactly the confusions a Sanskrit OCR or spell-checker
should target first.

**Who repairs what.** Correction labour is concentrated: Jim Funderburk (35,057 events, mostly
sense) and Dhaval Patel (8,248, sense) account for the large majority, with a long tail of named
volunteers. (These are the dataset's correctors, acknowledged as such; the chapter's authorship
is sole, and the process detail — latency, throughput, the contributor network — belongs to the
companion process study.)

## 6. The released resource and baselines

The corpus is released as `correction_events_release.csv` with a Gebru-style datasheet, per-event
evidence labels, three crosswalk columns, and a temporal split, under CC-BY-4.0. It supports
three tasks with stdlib-only reference baselines that *define* the task rather than tune a system:
error detection (a character-trigram LM prefers the corrected form at pairwise accuracy 0.516,
chance 0.5 — hard precisely because old and new differ by a single character); error correction (a
Norvig-style edit-1 model reaches acc@1 0.059, with 78.7 % of test errors within edit-distance-1
reach); and location classification (Naïve Bayes over edit-op features predicts the location
component at accuracy 0.638, macro-F1 0.453, majority baseline 0.402 — evidence the location axis
is *learnable* from surface features alone). These low numbers are the point of a baseline: they
establish headroom for the neural models the resource is meant to enable. In the terms of this
book, the release is the FAIR-data payoff of the evidence-graph programme — a corpus whose every
row carries its provenance and evidence grade, deposited for reuse.

## 7. Discussion

**Corrected ≠ wrong.** The single most important reading rule is that the corpus records
*corrected* events — where curators looked and acted — not a dictionary's latent error rate. A
dictionary with high correction density may be *better* maintained, not worse; the
falling-headword trend reflects a finished campaign, not improving typists. The alternative
reading — "dictionary X is the buggiest" — is both tempting and wrong, and the whole book's
insistence that a measurement carry its interpretive bounds applies here at full force.

**Surface dominance has a lesson for quality assurance.** That corrections are overwhelmingly
small surface edits, even in the definition and headword fields, means the highest-yield
automated quality tooling for digital Sanskrit lexicography is *not* semantic — it is spelling,
spacing, punctuation, and diacritic normalisation, targeted by the character-confusion profile.
The error mass is where a transducer can reach it.

**The two-axis lesson generalises.** The 0.1 % silver agreement is a cautionary result for any
digitisation-correction study: *where* an edit lands and *what kind* of edit it is are
orthogonal, and a single typology column that mixes them will be dominated by whichever axis its
fallback heuristic encodes. Separate the axes first — the same "measure one thing at a time"
discipline that separated convention from content in Chapter 9 and register from register in
Chapter 10.

## 8. Limitations and conclusion

Three limits bound the claims. Only 28.8 % of form-era events join to a current source record, so
the location axis leans on the git layer. The typology is machine-derived and checked against a
human-free *silver* standard; a human gold sample is staged but awaits a second annotator for an
inter-annotator agreement (κ) figure — reported here as derived, not adjudicated, exactly the gap
the book's own evidence-grade vocabulary is built to flag. And edit-type is computed from
character operations, so a meaning-changing correction that happens to be one character is
counted as small: the "surface, not substance" claim is about edit *size* and *location*, not a
claim that no correction ever changes meaning.

Twelve years of correcting the Cologne Digital Sanskrit Lexicon resolve into a clear and slightly
surprising picture: the corrections cluster exactly where meaning lives — in definitions and
headwords — yet are almost entirely small surface repairs; they form a per-dictionary fingerprint
rather than a uniform noise floor; and that fingerprint has visibly shifted as the project's
curatorial priorities moved from headwords to structure. Released as a language resource with its
two-axis typology, three crosswalk readings, and reference baselines, it is the book's final
demonstration that the maintenance history of a dictionary — the review-provenance layer of the
evidence graph — is itself first-class, gradeable, corpus-scale data, measuring the repairs a
community chose to make, which is a different and more human thing than a list of mistakes.

## References

Abel, Andrea, and Christian M. Meyer. 2014. "Model of a User Behaviour and User Participation."
In *Internet Lexicography.* [Direct/indirect/accessory user contribution; user-submitted
corrections; quality-voting.]

Akasu, Kaoru. 2013. "Dictionary Criticism." In *The Bloomsbury Companion to Lexicography,* ed.
Howard Jackson. London: Bloomsbury.

Boros, Emanuela, et al. 2024. "Post-Correction of Historical Text Transcripts with Large Language
Models: An Exploratory Study." *LaTeCH-CLfL 2024.*

Brewer, Charlotte. 2007. *Treasure-House of the Language: The Living OED.* New Haven: Yale
University Press. [OED revision layers — the versioned-dictionary precedent.]

Bryant, Christopher, Mariano Felice, and Ted Briscoe. 2017. "Automatic Annotation and Evaluation
of Error Types for Grammatical Error Correction." *ACL 2017.* [ERRANT.]

Gebru, Timnit, et al. 2021. "Datasheets for Datasets." *Communications of the ACM* 64 (12).

Hartmann, R. R. K., and Gregory James. 1998. *Dictionary of Lexicography.* London and New York:
Routledge. [Error analysis sanctioned as lexicographic evidence.]

Herold, Axel, Peter Meyer, and Herbert Ernst Wiegand. 2014. "Versioning and Revision Histories."
In *Internet Lexicography.* [Per-entry revision histories, OED Online.]

Katre, Sumitra M. 1941. *Introduction to Indian Textual Criticism.* Bombay: Karnatak Publishing
House.

Klosa-Kückelhaus, Annette, and Carole Tiberius. 2014. "Error Handling in the Lexicographic
Process." In *Internet Lexicography.*

Partridge, Eric. 1963. *The Gentle Art of Lexicography.* London: Deutsch.

Richter, Caitlin, et al. 2018. "Low-Resource Post Processing of Noisy OCR Output for Historical
Corpus Digitisation." *LREC 2018.*

Thomas, Alan, Robert Gaizauskas, and Haiping Lu. 2024. "Leveraging LLMs for Post-OCR Correction
of Historical Newspapers." *LT4HALA @ LREC-COLING 2024.*

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL), Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/), with the CDSL
correction record (`CORRECTIONS`, `csl-corrections`, and the `csl-orig` git history) as the
correction-event substrate.

_Dr. Mārcis Gasūns_
