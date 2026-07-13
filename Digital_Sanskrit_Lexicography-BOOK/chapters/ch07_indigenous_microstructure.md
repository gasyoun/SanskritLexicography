# Chapter 7 — Grammar Without Tags: The Verbal-Root Microstructure of the Indigenous Kośa

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Grammar Without Tags:
> The Verbal-Root Microstructure of the Indigenous Sanskrit Kośa* (source draft:
> [paper_indigenous_microstructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_indigenous_microstructure.md)),
> which is being published separately in a journal version (target: *International Journal of
> Lexicography*, with the World Sanskrit Conference 2027 as an indological alternate); where the
> article must remain independently citable, cite that version. Every count and table below is
> carried over unchanged and reproducible from the committed data
> ([`data/lexico/indigenous_roots.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/indigenous_roots.csv),
> [`root_agreement.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/root_agreement.json)).
> Only the framing has been converted from journal to book form — the abstract and keywords
> removed, companion-paper "P-numbers" remapped to this book's chapters, and the comparative
> and Moscow-school metalexicography engaged at the monograph's depth. Section numbering is
> chapter-internal (§1–§7).

Chapter 5 anatomised the European entry at full microstructural depth; Chapter 4 showed the
kośa's *macro*structure carrying the whole lexicographic load. This chapter completes the pair
by recovering the kośa's *micro*structure — the grammar packed inside the entry — and in doing
so states the book's "zero means nothing" doctrine in its strongest form. Run any European-style
microstructure detector (for part of speech, gender, or a tagged source apparatus) over the
Sanskrit-to-Sanskrit *kośa*s of the Cologne corpus and it scores close to zero. That zero is a
measurement artefact, not an absence of content: the indigenous lexica encode a rich and
recoverable verbal-grammatical apparatus through conventions of their own, and this chapter
decodes it, measures it, and — the decisive step — shows five independently compiled lexica
agreeing on the grammar they record.

The chapter is the microstructural instantiation of the estimator Chapter 2 defined as
root-parser agreement (§3.9), and it is the companion to the derivational study of Chapter 8:
where Chapter 8 measures the *derived headword* (root + affix + kāraka), this chapter measures
the *root entry* and its conjugational metadata (class, voice, transitivity). Together the three
chapters — macrostructure (Chapter 4), root microstructure (here), derivation (Chapter 8) —
establish that the indigenous tradition is not a scatter of untagged prose but a coherent,
measurable grammatical system, invisible only to an instrument built for the other tradition.

## 1. Introduction

A digital dictionary corpus invites measurement: count the part-of-speech tags, the gender
markers, the source citations, and you have a microstructural profile of each dictionary.
Applied across the dictionaries of the Cologne Digital Sanskrit Lexicon (43 at the 2026-06
measurement snapshot the numbers here reflect), such measurement produces a striking and
recurring result — the two great Sanskrit-to-Sanskrit *kośa*s, the *Śabdakalpadruma* (SKD) and
the *Vācaspatya* (VCP), score at or near **zero** on almost every European-style detector. They
carry no `<lex>` part-of-speech tags, no `<ls>` source-citation elements, no structural `<div>`
sense markers.

It is tempting, and wrong, to read that zero as thinness. This chapter makes the opposite case
with three measurements: the verbal root — the organising object of the indigenous Sanskrit
grammatical tradition — is almost *only* recorded in these dictionaries (§4.1); what looks like
an absence of grammatical tagging is in fact a different *technology* of grammatical encoding,
one that can be decoded (§4.2–4.3); and the decode is not a private reading, because five
indigenous lexica, encoding root grammar four different ways, agree on it (§4.4). The
methodological moral — never read a convention-specific detector's zero as absence of content —
is stated in §5, and it is the same rule the macrostructure chapter reached from the other
direction.

## 2. The indigenous lexica and the zero-meaning problem

The European Indological dictionaries tag grammar explicitly: Monier-Williams writes
`<lex>m.</lex>` for a masculine noun, `<ls>Pāṇ. 3,1,86</ls>` for a source. The indigenous
*kośa*s descend instead from the *dhātupāṭha* and *kośa* traditions (Palsule 1961; Vogel 1979;
on their transmission into the printed lexica, Gerow 1978), in which a root's grammar is conveyed
by **position and convention** — the company a root keeps, the indicatory letters attached to it,
the prose formula that closes a sense. A detector written for the European apparatus finds none
of its expected markers and returns zero.

That the grammar should live *inside* the lexical entry rather than in a separate tag layer is
not a defect of the kośa but a design principle it shares with the most theorised model of the
dictionary–grammar relation. In the Moscow school's integrated description, the dictionary entry
*presupposes* the grammar and encodes exactly what the general rules cannot predict (Apresjan
2000); the kośa is a strong instance — a root's entry is a pointer into the *dhātupāṭha*'s
system, and the *anubandha* letter is the minimal residue that individuates this root against the
class the grammar already defines. The structure also has a close comparative analogue: the
Arabic lexicographical tradition organises the entire lexicon by the consonantal root (*jaḏr*)
and the morphological pattern (*wazn*), so that a word's grammar is read off its position in a
root-and-pattern macro/microstructure rather than from an attached tag (Baalbaki 2014). The
*dhātu*-organised kośa and the *jaḏr*-organised Arabic lexicon are two independent solutions to
the same problem — encode grammar structurally — and naming the parallel keeps the kośa from
reading as merely "untagged."

The project records the hazard as the *zero-meaning* rule: a zero under a European detector
measures the absence of a European convention, not the absence of content. The *Śabdakalpadruma*'s
own front matter states the principle for its root apparatus in so many words — the *anubandha*
of each root is determined, and roots that have none get a dot or a zero — so that a `0` in the
slot means "no indicatory letter," never "no verb." This chapter turns the rule from a caution
into a measured demonstration.

## 3. Data and method

I extract, from the canonical CDSL source files, every entry that records a verbal root across
the five indigenous root-bearing lexica — SKD, VCP, the *Kṛdantarūpamālā* (KRM), Yates (YAT), and
the *Śabda-Sāgara* (SHS) — and, for control, the European dictionaries. For each root entry the
extractor recovers, where the dictionary encodes them, the verbal class (*gaṇa*, ten classes),
the voice (*pada*: *parasmai-*, *ātmane-*, *ubhaya-*), and transitivity (*sa-/akarmaka*),
together with the *signal* by which the dictionary conveyed each — a cited authority, a prose
annotation, an *anubandha* slot, or a conjugation paradigm.

The *Śabdakalpadruma* slot is decoded with the key in Durgādāsa Vidyāvāgīśa's *Dhātudīpikā* — his
commentary on Vopadeva's *Kavikalpadruma*, reproduced in SKD's front matter — which assigns a
*phala* (grammatical effect) to each of forty-six *anubandha* letters: some mark *gaṇa* (`ka`/`ki`
→ *curādi* class 10, `ga`/`gi` → *kryādi* class 9, …), two mark *pada* (`ṅ` → *ātmanepada*, `ñ` →
*ubhayapada*, with *parasmaipada* the unmarked default), and the rest mark morphophonemic
operations. The key was first recovered empirically from an SKD∩VCP cross-walk and then corrected
by the primary source, which reassigned the gaṇa markers the cross-walk had mistaken for *pada*
signals; Palsule's edition of the *Kavikalpadruma* independently corroborates it.

To test whether the recovered grammar is real rather than an artefact of one decoder, I measure
**cross-dictionary agreement**: grouping all entries by SLP1 root, I ask whether two or more
dictionaries that classify the same root give a compatible label. *Compatible* tolerates
legitimate homonymy (a root spelled alike but belonging to two classes is not a self-conflict);
*unanimous* is the stricter all-agree rate. Disagreement conflates genuine cross-tradition
difference with homonymy, so it is reported as an upper bound on real conflict, not a review
queue — the same agreement-as-validation logic the book uses wherever no gold standard exists
(Chapter 2, §3.9).

## 4. Results

### 4.1 The verbal root is an indigenous object

The verbal-root apparatus is almost entirely confined to the indigenous lexica (Table 1). The
five indigenous root dictionaries carry hundreds to thousands of root entries each; every
European dictionary in the corpus carries **eight or fewer**.

**Table 1.** Root entries per dictionary (selected).

| Dictionary | Root entries | dict. total entries |
|---|---:|---:|
| SKD — *Śabdakalpadruma* | 2,544 | 42,531 |
| VCP — *Vācaspatya* | 2,230 | 50,135 |
| KRM — *Kṛdantarūpamālā* | 1,757 | 2,061 |
| YAT — Yates (conjugation) | 1,643 | 45,206 |
| SHS — *Śabda-Sāgara* | 463 | 47,326 |
| PWG — Petersburg (große) | 8 | 123,366 |
| PW — Petersburg (kürzere) | 3 | 170,556 |
| MW72 — Monier-Williams 1872 | 1 | 55,388 |

A microstructural census that keyed "verbal grammar" to a European tag would conclude that the
CDSL barely records roots at all. The truth is the reverse: it records them densely, in the
dictionaries the tag cannot read.

### 4.2 The *anubandha* system, decoded at scale

The *Śabdakalpadruma* encodes each root's class and voice in a string of *anubandha* letters
placed in a slot immediately after the headword separator. Applying Durgādāsa's key resolves the
*gaṇa* of **1,737** SKD roots and the *pada* of **1,498**, up from 1,117 and 1,167 recoverable
from surface markers alone — a gain of 55 % and 28 %. Of SKD's 2,544 root entries, 1,925 carry a
slot to decode. The resulting *gaṇa* distribution is linguistically correct: *bhvādi* (class 1,
the largest class) dominates (634 roots), followed by *curādi* (531) and *tudādi* (170), once the
unmarked *parasmaipada/bhvādi* defaults are restored from the visarga prose rather than read as
zero.

### 4.3 Five conventions, one grammar

The indigenous lexica do not share an encoding; they share a *subject*. SKD marks roots by
*anubandha* letters plus cited authority; VCP and SHS by prose annotation; KRM by a
*dhātupāṭha*-style annotation; YAT by a full conjugation paradigm (Table 2). Yet the *gaṇa*
distributions they produce agree in shape — *bhvādi* is the modal class in every one (SKD 634,
VCP 1,152, KRM 944, YAT 1,009, SHS 288), exactly as the grammatical tradition predicts.

**Table 2.** Encoding convention and resolved-feature counts, indigenous root lexica.

| Dictionary | Primary signal | *gaṇa* resolved | *pada* resolved | transitivity |
|---|---|---:|---:|---:|
| SKD | *anubandha* slot + citation | 1,737 | 1,498 | 1,156 |
| VCP | prose annotation | 1,954 | 1,897 | 2,183 |
| KRM | *dhātupāṭha* annotation | 1,755 | 1,378 | 1,735 |
| YAT | conjugation paradigm | 1,643 | 1,643 | — |
| SHS | prose annotation | 456 | 407 | 454 |

### 4.4 The lexica agree on the grammar they record

Agreement is the test that the decoded grammar is real. Across the 1,526 roots that two or more
indigenous lexica classify for *gaṇa*, a single class is compatible in **85.5 %** of cases
(unanimous in 69.9 %); only 221 roots (14.5 %) conflict, and that figure still includes homonyms.
Pairwise, the closest readers agree even more tightly — SKD–VCP 92.8 % (948 of 1,022 shared
roots), SKD–KRM 95.0 %, VCP–KRM 92.7 %. *Pada* is compatible in **75.3 %** (the lower figure
reflects the genuine *parasmai*-default ambiguity and YAT's bare-stem citation, which
undercounts), and transitivity in **81.4 %**. Five dictionaries, four conventions, one
grammatical tradition, measured.

### 4.5 The sense unit is the *iti*-group, not the gloss

The same convention-specificity governs the *kośa*'s sense structure. Where a European dictionary
separates a sense from its source, the *kośa* fuses them: a synonym run or definition is closed
by the quotative particle *iti* and the name of its authority (*ity Amaraḥ*, *iti Medinī*), so
that the unit of microstructure is the *iti*-closed group, in which enumeration and attestation
are a single construction. This is the microstructural root of the *iti*-citation register
Chapter 10 measures at corpus scale, and the reason the European sense/apparatus distinction
cannot be imposed on the *kośa* without loss — a consequence for sense counting developed in the
sense-inheritance chapter (Chapter 6). It also marks the boundary this chapter does not cross:
where a form sits between a lemmatised root and its participial derivative, the two traditions
draw the line differently (Lowe 2015), and the root key is deliberately conservative about it.

## 5. Discussion

**The zero-meaning rule, demonstrated.** A convention-specific detector's zero is an instrument
reading, not a property of the dictionary. The indigenous lexica score zero for European grammar
tags and carry, behind that zero, the corpus's densest verbal-root apparatus — decodable (§4.2),
cross-validated (§4.4), and organised on a different microstructural unit (§4.5). Any
cross-dictionary statistic that sums a European-keyed feature will therefore *systematically
erase* the indigenous tradition, reporting it as empty where it is in fact richest. Convention
must be a controlled variable in corpus-wide lexicographic measurement — exactly as it must be
for the macrostructure (Chapter 4), the citation apparatus (Chapter 10), and the entry count
(Chapter 9).

**For the history of grammar.** That five independently compiled indigenous lexica agree on
*gaṇa* at 85.5 % is, beyond a data-quality check, a measurement of the *coherence of the
dhātupāṭha tradition* as transmitted into nineteenth-century lexicography: the
*Kavikalpadruma*/*Dhātudīpikā* line (SKD, KRM) and the prose-grammar line (VCP, SHS) converge on
the same classification of the same roots. It is the empirical counterpart, on the microstructural
scale, to the derivational consistency Chapter 8 measures on the derived headword.

**For digital standards.** Encoding this microstructure in an interoperable form requires
treating the *anubandha* slot and the *iti*-unit as first-class structures, not as untagged prose
to be flattened — a requirement a baseline lexicographic schema (TEI Lex-0; Tasovac, Romary et
al. 2018) meets only with a *kośa*-specific customisation, exactly the kind of microstructural
specificity the metalexicographic survey tradition anticipates (Hausmann and Wiegand 1989). This
is where the book's evidence-graph programme and the encoding-standard programme meet: the graph
needs the structure named before it can grade a statement drawn from it.

## 6. Limitations and future work

Disagreement (§4.4) conflates cross-tradition difference with homonymy — same SLP1 spelling,
different roots — and so over-states genuine conflict; resolving it needs a homonym-aware root
key. Yates cites bare stems where the others keep the *uccāraṇārtha* final *-a*, so YAT's
cross-dictionary agreement is conservative; a normalising pass is held back because it collides
homographs (it lowers SKD–YAT *gaṇa* agreement from 86.0 % to 81.2 %). SKD and SHS have lower
feature coverage than VCP/KRM and so contribute fewer opinions. The *anubandha* key rests on a
single primary source (Durgādāsa), corroborated by Palsule's edition; a second manuscript witness
would harden the few contested letters. Finally, the decode is at the level of the root's lexical
grammar; aligning it to a corpus of attested verb forms is the natural next step.

## 7. Conclusion

The Sanskrit *kośa* does not lack microstructure; it carries a microstructure no European-keyed
detector can see. The verbal root is an almost exclusively indigenous object in the CDSL, its
grammar encoded by *anubandha* letters and prose convention rather than tags, decodable at scale
from the tradition's own *Dhātudīpikā* key, and agreed upon at better than five-in-six by five
independently compiled lexica. The practical lesson is a single discipline for corpus
lexicography, and it is the book's: a zero is a question about the instrument before it is a fact
about the dictionary.

## References

Apresjan, Jurij D. 2000. *Systematic Lexicography.* Trans. Kevin Windle. Oxford: Oxford
University Press. [The integrated grammar–dictionary description: the entry presupposes the
grammar and encodes the unpredictable residue.]

Baalbaki, Ramzi. 2014. *The Arabic Lexicographical Tradition: From the 2nd/8th to the 12th/18th
Century.* (Handbook of Oriental Studies 1.107.) Leiden and Boston: Brill. [Root-and-pattern
(*jaḏr*/*wazn*) organisation as the Arabic structural analogue of *dhātu* organisation.]

Gerow, Edwin. 1978. "Indian Lexicography." In *Current Trends in Linguistics.* [Framing note on
the transmission of the indigenous grammatical apparatus into the printed lexica.]

Hausmann, Franz Josef, and Herbert Ernst Wiegand. 1989. "Component Parts and Structures of
General Monolingual Dictionaries: A Survey." In Hausmann, Reichmann, Wiegand and Zgusta (eds.),
*Wörterbücher / Dictionaries / Dictionnaires,* vol. 1 (HSK 5.1), 328–360. Berlin and New York:
Walter de Gruyter.

Lowe, John J. 2015. *Participles in Rigvedic Sanskrit: The Syntax and Semantics of Adjectival
Verb Forms.* Oxford: Oxford University Press. [The participle/root lemmatization boundary.]

Palsule, Gajanan Balkrishna. 1961. *The Sanskrit Dhātupāṭhas: A Critical Study.* Poona:
University of Poona.

Tasovac, Toma, Laurent Romary, et al. 2018. *TEI Lex-0: A Baseline Encoding for Lexicographic
Data.* DARIAH Working Group on Lexical Resources.

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature, vol. V, fasc. 4, ed.
Jan Gonda.) Wiesbaden: Otto Harrassowitz.

**Primary sources.** Rādhākānta Deva, *Śabdakalpadruma* (Calcutta, 1822–1858), with the
*Dhātudīpikā* of Durgādāsa Vidyāvāgīśa in the front matter; Vopadeva, *Kavikalpadruma,* ed. G. B.
Palsule (Poona, 1954); Tarkavācaspati, *Vācaspatya* (Calcutta, 1873–1884); *Kṛdantarūpamālā*;
Yates, W., conjugation tables (1846); *Śabda-Sāgara* (1900). All consulted in the machine-readable
editions of the **Cologne Digital Sanskrit Dictionaries (CDSL)**, Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

_Dr. Mārcis Gasūns_
