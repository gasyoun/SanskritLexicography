# Chapter 9 — Pointing Inward: Cross-Reference Graphs as a Signal of Dictionary Descent

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Pointing Inward:
> Cross-Reference Graphs as a Signal of Dictionary Descent* (source draft:
> [paper_xref_lineage.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_xref_lineage.md)),
> which is being published separately in a journal version (target: a digital-humanities /
> metalexicography methods venue, with the World Sanskrit Conference 2027 as an alternate);
> where the article must remain independently citable, cite that version. It also **absorbs**
> the two short companion notes on descent methodology (the "three axes" decomposition and
> the redundancy-and-descent material) that the journal series kept as separate papers, so
> that inside this book the convention/content/microstructure decomposition is stated here
> rather than pointed at. Every count and table below is carried over from the article
> unchanged and is reproducible from the committed data
> ([`data/lexico/xref_lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_lineage.json),
> [`data/lexico/xref_edges.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_edges.csv));
> the framing has been converted from journal to book form — abstract and keywords removed,
> companion-paper "P-numbers" remapped to this book's chapters, one edition-label slip in the
> source's §3.2 corrected against Table 1, and the mediostructure literature engaged at the
> monograph's depth. Section numbering is chapter-internal (§1–§7).

The book's method chapter (Chapter 2) defined a cross-reference-graph estimator among its
ten and stated its limit once: a shared cross-reference edge is a lineage signal, not proof
of copying, and pairs with few shared source lemmas are not interpretable. This chapter is
that estimator's dedicated instantiation — the mediostructural coordinate on the inheritance
problem that Chapters 5 and 6 approach through the entry and the sense, and that Chapter 12
approaches through shared error. It asks a single, old philological question in a measurable
form: is the Monier-Williams cross-reference network the *same graph* as the Petersburg
lexicon's, or only a related one?

The chapter is worth its place in the book for a reason beyond the answer. The
mediostructure — the web of internal pointers a dictionary lays over its own headword list —
is the one macrostructural component the field's own reference work admits it has not yet
learned to study systematically: the *Dictionary of Lexicography* notes that for the
cross-reference apparatus "a framework for their systematic study … is still to be developed"
(Hartmann and James 1998). That admission is this chapter's warrant. What follows is one such
framework — a calibrated, convention-cleaned way to read pointer-graph overlap as descent —
built on the same discipline the rest of the book insists on: measure the marked signal, not
the raw count, and scale it against a known-answer control.

## 1. Introduction

A cross-reference is the dictionary talking to itself — the pointer apparatus that
lexicographic theory treats as a designed component of entry structure (Wiegand 1989; Atkins
and Rundell 2008) and classical metalexicography as part of the dictionary's information
economy (Zgusta 1971), and that current digital lexicography frames as the *linking* layer of
a dictionary's access structure (Engelberg, Müller-Spitzer, and Schmidt 2009). *Cf.*, *see*,
*Vgl.* — each pointer links one headword to another and asserts that the two belong together:
variant spellings, cognate roots, members of a compound family, semantically related words.
Over a whole dictionary these pointers form a directed graph, and that graph is a structural
fingerprint distinct from the word list and from the prose of the entries. It is also a
plausible vehicle of descent: a lexicographer who works from an earlier dictionary inherits
not only its headwords but its sense of which words point to which, so two related
dictionaries should share cross-reference edges.

The question this chapter asks is whether the Monier-Williams `cf.` network and the
Petersburg `Vgl.` network are the *same graph*. The methodological obstacle is that
cross-reference graphs overlap for three different reasons, only one of which is descent. Two
Sanskrit dictionaries will independently record that *Ayu* is a variant of *Ayus* or that
*bala* relates to the root *bal*, because both lexicographers know the language — a **content
coincidence**. Both will point many entries to high-frequency prefixes and compound heads —
*a°*, *mahā°*, *su°* — because both mark compound families that way, a **convention artefact**
that manufactures graph hubs out of house style rather than shared knowledge. And only some
overlap is genuine **inheritance**, one network built on the other. This
content / convention / inheritance decomposition is the analytic spine the chapter shares
with the rest of the book's descent argument, and a single overlap number cannot separate its
three strands.

The solution is calibration by a positive control (§3). Two editions of the same dictionary
must, by construction, share most of their cross-references; measuring how much they actually
share tells us what a descent signal *looks like* on this data and this method, and gives
every other pair a ceiling to be read against. With that ceiling in hand, the cross-tradition
comparisons become interpretable — and the answer is a qualified no: a shared core, not the
same graph. Reading structural overlap this way — as multi-dimensional, calibrated descent
evidence rather than a similarity score — follows the digital-stemmatology precedent of
Andrews and Macé (2013), and it borrows the vocabulary of the historical-linguistic
comparative method (trees and waves, shared innovation versus independent parallel; Weiss
2014; Hale 2014; François 2014; Dunn 2014): a coincident cross-reference is a shared *state*,
which counts as evidence of common descent only once the independently-derivable states and
the convention-driven ones are subtracted.

## 2. Data

Cross-reference markup differs by dictionary, so the graphs are extracted per source
convention. The Petersburg lexicon marks comparisons with `Vgl.`; Monier-Williams with `cf.`
in `<s>` tags; the Apte editions and Cappeller put `cf.` targets in `{#…#}` SLP1, mixing true
lemma pointers with multi-word quotes and cognates, which a parsing rule separates — a
`{#…#}` is kept as a graph **edge** only when it is lemma-like (a single SLP1 word, no spaces
or periods), and everything else is routed to a cross-reference-quote side file. The resulting
directed networks (Table 1) are the unit of analysis: each node is a normalised headword,
each edge a `source → target` pointer.

**Table 1. Cross-reference networks by dictionary (normalised).**

| Dictionary | Marker | Edges | Source lemmas |
|---|---|---:|---:|
| Petersburg (PWG) | `Vgl.` | 22,937 | 11,857 |
| Monier-Williams (MW) | `cf.` | 7,637 | 6,974 |
| Apte revised, 1957 (AP) | `cf.` `{#…#}` | 609 | 604 |
| Apte 1890 (AP90) | `cf.` `{#…#}` | 444 | 432 |
| Cappeller (CAE) | `cf.` `{#…#}` | 190 | 160 |
| Benfey (BEN) | `cf.` | **0** | — |

*Source:
[`xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json)
(normalised graphs) and
[`MICROSTRUCTURE_XREF_LINEAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_LINEAGE.md);
raw pre-normalisation scan counts (AP90 446, CAE 196) are in
[`xref_hub_review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/xref_hub_review.json)
(PWG: 123,366 entries scanned, 12,283 carrying a cross-reference). Note the CDSL codes:
**AP90 is the 1890 edition, AP the 1957 revision**. Benfey's `cf.` is purely cognate /
Roman-script, so it does **no internal Sanskrit cross-referencing** — a content fact, not a
markup gap.*

## 3. Method

### 3.1 Normalisation and intersection

Both ends of every edge are reduced to a common key: strip the compound-family marker (PWG
writes it `°`, MW writes it `-`, so `a°` ≡ `a-`), strip SLP1 accents and stray hyphens, and
deduplicate per dictionary. Two networks are then intersected on the set of **source lemmas
both dictionaries cross-reference** — there is no point asking whether MW and PWG agree about
a lemma only one of them points from. On that shared-source set I report the number of
identical `source → target` edges, the directed **inheritance rate** for each dictionary (what
fraction of *its* cross-references from shared sources the other also makes), and the Jaccard
overlap (Jaccard 1912). Edges are **directed**: a reciprocal pointer in the other dictionary
does not count as a match. (The metric's definition and limits are stated once for the book in
Chapter 2, §3.6; this chapter is its dedicated instantiation.) The normalisation is
deliberately conservative — a messy multi-part target that does not reduce cleanly simply
fails to match — so every number is a **floor**.

### 3.2 The positive control

Because overlap has no absolute scale, the method is anchored by a pair whose answer is known.
Apte 1890 (AP90) and the revised Apte (AP, 1957) are the same dictionary in two editions;
whatever descent does to a cross-reference graph, it must leave most of it intact across an
edition boundary. The overlap measured on AP × AP90 is therefore the **edition-continuity
ceiling** — the value the method assigns to genuine, near-total inheritance — and every
cross-tradition pair is read as a fraction of it. This is the same edition edge that
Chapter 2's worked example and the sense-inheritance analysis of Chapter 6 use as their
positive control; across headword list, senses, and now pointer graph, the two Apte editions
behave as one dictionary.

### 3.3 The prefix-hub control

Before any pair is read, the most-referenced targets of each dictionary are classified. A
target that is a bare prefix or compound head — *a°*, *mahā°*, *su°*, *vi°* — is a
**prefix-convention hub**: it accumulates hundreds of incoming edges because the dictionary
marks compound families that way, not because those edges carry rare lexical information. Such
hubs inflate raw overlap between any two dictionaries that share the convention, so they are
labelled and held out of the lexical-core reading. This is the *convention* axis of the
book's descent decomposition (§1) intruding on the *content* signal, and it must be subtracted
before cross-reference overlap can speak to descent.

## 4. Results

### 4.1 The spectrum, against the control

**Table 2. Cross-reference overlap for every measurable dictionary pair.** Inheritance rate
is directed (a-rate / b-rate); the reading is the machine review label.

| Pair | Overlapping edges | a-rate / b-rate | Jaccard | Reading |
|---|---:|---|---:|---|
| **AP × AP90** | 182 | **85.5 % / 84.7 %** | **0.740** | edition-continuity (positive control) |
| AP × PWG | 23 | 34.3 % / 7.4 % | 0.065 | too sparse to read |
| AP × MW | 19 | 28.8 % / 23.2 % | 0.147 | sparse |
| CAE × MW | 11 | 24.4 % / 20.0 % | 0.124 | sparse |
| **MW × PWG** | 641 | **21.8 % / 9.1 %** | 0.069 | lexical shared core |
| AP90 × PWG | 11 | 14.7 % / 2.8 % | 0.024 | too sparse |
| CAE × PWG | 7 | 12.5 % / 1.8 % | 0.016 | too sparse |
| AP90 × MW | 10 | 11.2 % / 8.6 % | 0.051 | sparse |

*Source:
[`xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json)
and
[`MICROSTRUCTURE_XREF_LINEAGE.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_XREF_LINEAGE.md).
The two remaining packet pairs, AP × CAE (1 edge) and AP90 × CAE (0 edges), are omitted as
empty.*

The control behaves as it must: two editions of Apte recover **~85 %** of each other's
cross-references, at Jaccard 0.74. That is the shape of descent — near-total preservation of
the pointer graph across an edition. Every other pair is read against it.

### 4.2 Monier-Williams and the Petersburg lexicon: a shared core

The headline pair is the largest. MW and PWG share 2,538 source lemmas; on those, MW makes
2,946 cross-references and PWG makes 7,022, of which **641 are identical** edges. That is an
inheritance rate of **21.8 %** from the MW side (and 9.1 % from the denser PWG side), at
Jaccard 0.069. The number cuts both ways. It is far above chance — in the ≈300,000-headword
union of the two dictionaries' key spaces, 641 coincident directed pointers on a 2,538-lemma
overlap is not what independent networks produce — so MW and PWG are demonstrably **related**,
as the philology has always held. But it is barely a quarter of the edition-continuity
ceiling, and roughly four in five of MW's cross-references — even from lemmas PWG also
cross-references — go where PWG does not. The sample of genuinely shared edges is telling:
*ARi → aRi*, *Ayu → Ayus*, *Bala → bal* — variant-form and cognate-root pointers that two
competent Sanskrit lexicographers would each record independently. The verdict is a **shared
cross-reference core with large independent expansion in each tradition** — common scholarly
substrate, very possibly some borrowing, but not a network MW lifted from Petersburg.

### 4.3 The hubs are convention, not content

The raw overlap would be higher, and misleadingly so, without the prefix-hub control. PWG's
most-referenced targets are not rare words but compound markers — *a°* (320 incoming edges),
*mahā°* (254), *su°* (160), *vi°* — each a hub that exists because Petersburg records compound
families by pointing to the bare prefix. Any dictionary that shares the convention will appear
to "agree" with PWG on these hubs while sharing no lexical knowledge at all. Held out as
convention artefacts, they stop inflating the lexical-core reading, leaving the 641 shared
edges to be adjudicated on their lexical merits.

### 4.4 A content finding: Benfey points nowhere inward

Benfey's dictionary records **zero** internal Sanskrit cross-references: its `cf.` slot holds
only cognates in other languages and Roman-script comparanda. This is not a markup limitation
the parser failed to read but a property of the dictionary — Benfey simply does not build an
internal pointer graph — and it means cross-reference descent is undefined for any edge into
or out of Benfey, however close the two dictionaries are on content or convention.

## 5. Discussion

### 5.1 What cross-reference overlap can and cannot show

Read naively, the MW × PWG overlap could be told either way — "21.8 % shared, the networks are
related!" or "78 % divergent, MW built its own graph!" — and both spins are true and useless.
The positive control dissolves the ambiguity: 21.8 % is not "high" or "low" in the abstract,
it is *a quarter of what descent looks like* on this method, measured on the same data.
Calibration, not the raw number, is what licenses the reading. This is the general lesson — a
structural-overlap measure means nothing without a known-answer pair to scale it, and the
cheapest such pair is two editions of one dictionary.

The move is the mediostructural analogue of the classical philologist's worked descent chains.
Latin lexicography preserves such chains explicitly — Verrius Flaccus epitomized by Festus and
Festus in turn by Paul the Deacon; Donatus's commentary expanded into the *Servius auctus* —
and their study reads exactly as a question of what each layer preserved, dropped, and added
(Ferri 2019, essays by Lhommé and Maltby). Where those chains are documented in the
manuscript record, the Sanskrit family's are latent in the pointer graphs, and the calibrated
overlap is the instrument that makes the latent chain measurable. A descent claim is a claim
about which dictionary is a later layer over which — and, as in the Latin case, it is
adjudicated by shared structure, not by a single similarity score.

### 5.2 Relation to the book's other descent chapters

The cross-reference graph is one coordinate on the inheritance problem the book studies, and
it decomposes the same way the content / convention / microstructure analysis of §1 requires.
The prefix-convention hubs (§4.3) are a pure *convention*-axis effect — shared marking style
that fakes content overlap — and must be subtracted before the graph speaks to descent; the
641 shared lexical edges are a *content*-axis signal, a floor for relatedness, never on their
own proof of copying. The AP × AP90 control is the same edition-continuity edge that the
sense-inheritance chapter (Chapter 6) reads as an Apte revision: across senses and now pointer
graphs the two Apte editions behave as one dictionary, which is exactly why they calibrate the
others. And Benfey's empty pointer graph (§4.4) is the cross-reference analogue of the
indigenous-microstructure move in Chapter 7 and the kośa move in Chapter 4 — a structural zero
that is a fact about the instrument's content, not a gap to be filled. That the same
edition-continuity edge and the same "zero means instrument, not absence" reading recur across
four structural coordinates is itself the book's central evidence that these are independent
estimators of one underlying descent.

## 6. Limitations

- **Floor, not ceiling.** Conservative normalisation means unmatched messy targets only
  *lower* the measured overlap; the true shared core is at least as large as reported.
- **Directed edges.** Only `source → target` matches count; a reciprocal pointer in the other
  dictionary is not credited, which understates symmetric relatedness.
- **Density asymmetry.** PWG cross-references roughly three times as densely as MW (22,937 vs
  7,637 edges), so the two directed inheritance rates are not comparable in magnitude and are
  reported separately rather than averaged.
- **Sparse pairs are unreadable.** Every cross-tradition pair except MW × PWG and the Apte
  control shares too few source lemmas (7–23 overlapping edges) to support a reading; they are
  reported for completeness only.
- **The labels are review prompts.** Edition-continuity, lexical-shared-core,
  prefix-convention, and too-sparse are machine triage classes over a 40-edge shared-core
  sample; the packet records no human lineage decision.
- **One positive control.** The calibration rests on a single same-dictionary pair (Apte); a
  second edition-continuity pair would strengthen the ceiling.

## 7. Conclusion

The graph a dictionary makes by pointing at itself is a real and measurable signal of descent
— but only once it is calibrated and cleaned. Two editions of Apte preserve 85 % of their
cross-references; against that ceiling, Monier-Williams and the Petersburg lexicon share just
21.8 %, and that fraction, stripped of the prefix-convention hubs that manufacture false
agreement, resolves into a common scholarly core of variant and cognate pointers rather than
an inherited network. The same discipline the rest of the book insists on holds here: overlap
is a floor, not a copy; a structural signal earns a descent claim only against a known-answer
control and only after convention is subtracted from content. The mediostructure — the
component the field's reference work still lists as awaiting a systematic method — turns out to
be measurable after all. Cross-references point inward, and read this way they point, faintly
but measurably, back along the line of descent.

## References

Andrews, Tara L., and Caroline Macé. 2013. "Beyond the Tree of Texts: Building an Empirical
Model of Scribal Variation through Graph Analysis of Texts and Stemmata." *Literary and
Linguistic Computing* 28 (4): 504–521.

Atkins, B. T. Sue, and Michael Rundell. 2008. *The Oxford Guide to Practical Lexicography.*
Oxford: Oxford University Press.

Bowern, Claire, and Bethwyn Evans (eds.). 2014. *The Routledge Handbook of Historical
Linguistics.* London and New York: Routledge. [Chapters by Weiss (comparative method), Hale
(neogrammarian regularity), François (trees and waves), and Dunn (computational phylogenetics)
— the vocabulary borrowed for dictionary stemmatics.]

Engelberg, Stefan, Carolin Müller-Spitzer, and Thomas Schmidt. 2009. "Semantic Relations and
Linking Structures in Electronic Dictionaries." In *Internet Lexicography.* [Linking and
access structures as the field's current frame for the cross-reference apparatus.]

Hartmann, R. R. K., and Gregory James. 1998. *Dictionary of Lexicography.* London and New
York: Routledge. [Mediostructure: "a framework for their systematic study … is still to be
developed" — the field's admitted gap this chapter fills.]

Ferri, Rolando (ed. contributions). 2019. In Robert Maltby et al. (eds.), *Studies on Late
Antique and Medieval Latin Glossaries and Dictionaries.* [Lhommé on the Verrius → Festus →
Paul epitome chain; Maltby on Donatus → Servius auctus — documented descent chains as
comparanda.]

Jaccard, Paul. 1912. "The Distribution of the Flora in the Alpine Zone." *New Phytologist* 11
(2): 37–50.

Wiegand, Herbert Ernst. 1989. "Der Begriff der Mikrostruktur: Geschichte, Probleme,
Perspektiven." In Hausmann, Reichmann, Wiegand and Zgusta (eds.), *Wörterbücher / Dictionaries
/ Dictionnaires,* vol. 1 (HSK 5.1), 409–461. Berlin and New York: Walter de Gruyter.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.) Prague:
Academia; The Hague and Paris: Mouton.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

_Dr. Mārcis Gasūns_
