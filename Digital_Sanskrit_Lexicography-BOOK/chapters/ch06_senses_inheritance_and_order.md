# Chapter 6 — Senses: Inheritance and Order

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is a genuine **merge** of two journal articles, not a conversion
> of one: its first half is the book-form version of *Condensation, Not Inflation: Sense
> Inheritance in the Sanskrit Dictionary Family, 1822–1957* (source draft:
> [paper_sense_inheritance.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md)),
> and its second half is the book-form version of *Genetic, Not Historical: How the
> 19th-Century European Sanskrit Dictionaries Order Senses* (source draft:
> [A33_sense_ordering_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md)).
> The merge follows the ruling recorded in
> [BOOK_PLAN.md §3](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
> (MG, 10-07-2026): sense *inheritance* (how the set of senses behaves across descent) as the
> chapter's first half, sense *order* (how the senses within an entry are sequenced) as the
> second, both reframed against Apresjan's account of lexicographic sense-structure so the
> chapter tests a theory rather than restating one. Each article remains independently citable
> in its journal version. Every count and table below is carried over from the two articles
> unchanged. Section numbering is chapter-internal (§1–§9).

If the dictionary is an evidence graph, the sense is its most contested node. Before a sense can
carry a grade of evidence it must exist as a discrete thing to grade — and whether a dictionary
"sense" is a real entity or an artifact of the dictionary's own structure is the oldest open
question in the theory of the lexical entry (Hanks; Sinclair; the debate surveyed in Lew 2013).
This chapter takes that node and asks two questions of it that the digital corpus, for the first
time, lets us answer at scale. The first is a question of **inheritance**: when one dictionary
descends from another, what happens to its senses — do they multiply, persist, contract? The
second is a question of **order**: within a single entry, in what sequence are the senses
printed, and what principle governs the sequence? The two questions are the diachronic and the
synchronic face of the same object, and the chapter's unifying finding is that both answers cut
against the same received intuition. Senses do not inflate over time and dictionaries do not sort
them by history; granularity and order are alike **traits of a lexicographic school**, not
functions of the calendar.

The theoretical anchor for both halves is the same. Apresjan's systematic lexicography treats an
entry's senses not as an unordered bag but as a *structured* object in which senses stand in
regular, largely derivable relations — regular polysemy propagating a sense from one lemma to its
neighbours, and a synchronic-derivational ordering in which a basic sense generates the rest by
rule (Apresjan 2000). Read through that lens, the two empirical questions become tests of a
theory: does inheritance behave as regular polysemy predicts (the senses that survive are the
structurally central ones), and does the historical European dictionary order its senses by the
*genetic* principle Apresjan formalises rather than by chronology? The chapter's contribution is
to answer both against a documented dictionary family, at corpus scale, rather than at the
preface level where the question has always been left.

---

## Part I — Inheritance: condensation, not inflation

## 1. The inflation intuition, and why it is testable here

A persistent intuition in the history of lexicography holds that later dictionaries are richer:
more senses, finer divisions, fuller treatment. The intuition is rarely tested, because testing
it requires a set of dictionaries with documented lines of descent, a way of counting senses that
respects each dictionary's own conventions rather than imposing one, and a way of aligning senses
across dictionaries — and, in the Sanskrit case, across three description languages (German,
English, Sanskrit) — so that survival and drift can be measured sense by sense. The second of
these is the classical microstructural problem, segmenting and comparing senses on each
dictionary's own terms (Zgusta 1971; Wiegand 1989; Atkins and Rundell 2008), here sharpened by a
corpus that mixes four marking regimes across three languages.

The Cologne corpus supplies all three requirements. Eleven general lexica span 1822–1957 with
genealogy documented both philologically and by the headword-containment measurement of
Chapter 9: Wilson (1832) is the ancestor of Śabda-Sāgara (1900) and Yates (1846); Apte's 1890
dictionary was revised into the 1957 edition; the Petersburg lexicon stands behind
Monier-Williams. Alongside the European line stand the two indigenous encyclopaedic lexica whose
microstructure descends from the *kośa* tradition (Chapter 4, Chapter 7). I ask three questions
of that record: **H1 (inflation)** — do sense counts per entry rise with publication year?
**H2 (survival)** — when a dictionary inherits from an ancestor, which senses survive, and does
the citation apparatus predict survival? **H3 (drift)** — do descendants expand, copy, or
condense? A methodological question is prior to all three: can senses be counted and aligned at
all across conventions as different as Apte's numbered bullets, the Petersburg structural
divisions, Monier-Williams's run-on glosses, and the *iti*-closed prose units of the indigenous
lexica?

## 2. Counting senses on each dictionary's own terms

No single sense-segmentation rule fits the corpus, because it contains four distinct marking
regimes, and the splitter therefore implements four parser families, each using the dictionary's
own convention: explicit Western markers (Apte's `{@N@}` / bullet, Wilson's `.²N`, the Petersburg
`<div>` divisions); lumped glosses (Monier-Williams, Schmidt, Cappeller mark no senses, so
semicolon-delimited meaning-clauses with citations stripped serve as a calibrated proxy);
indigenous prose (SKD and VCP close each unit with the quotative *iti*, so *iti*-units are the
proxy); and a reverse index (Apte's English–Sanskrit volume). Cross-dictionary alignment never
compares gloss translations: each sense carries a **Sanskrit fingerprint** — the SLP1 tokens it
quotes plus its citation sigla — and senses align by Jaccard overlap of fingerprints, which is
what lets a German Petersburg sense align with an English Apte sense with no translation step.

That the count is convention-relative is not a nuisance but the chapter's first result. A review
checkpoint isolated the ten highest-risk lemma/dictionary pairs and put them to a source-faithful
re-count against the printed page. In the high-drift cases the *legacy* static count, not the
source window, proves to be the artifact: for Petersburg ¹*gam* the first-pass splitter counted
`<div>` nesting *depth* (30) where Böhtlingk prints seven top-level senses; for Benfey *gam* the
legacy 23 was the root plus the first participle, an arbitrary cut through a forty-two-run
derivative block. A sense count is only meaningful relative to a dictionary's own marking
convention — the same lesson the whole book draws about conventions, here at the level of the
sense itself.

## 3. H1 — granularity is a family trait, not a function of time

Across the eleven dictionaries the correlation of sense-units per entry with publication year is
**r = 0.036** — no trend (Table 1). The variance is captured instead by lexicographic *family*:
Benfey 2.42 sense-units per entry, the Apte family 2.12, Monier-Williams 2.00, Wilson 1.71,
Cappeller 1.36, the Petersburg line 1.13, the indigenous lexica 1.00 (a register floor, not
emptiness — Part I §5).

**Table 1.** Granularity by dictionary (sense-units per entry).

| Year | Dictionary | Family | Entries | Sense-units/entry |
|---:|---|---|---:|---:|
| 1822 | Śabdakalpadruma | indigenous | 42,531 | 1.00 |
| 1832 | Wilson | Wilson | 44,577 | 1.71 |
| 1855 | Petersburg (PWG) | Petersburg | 123,366 | 1.13 |
| 1866 | Benfey | Benfey | 17,310 | 2.42 |
| 1872 | Monier-Williams 1872 | Monier-Williams | 55,388 | 2.85 |
| 1873 | Vācaspatya | indigenous | 50,135 | 1.00 |
| 1890 | Apte 1890 | Apte | 34,882 | 2.52 |
| 1891 | Cappeller | Cappeller | 40,069 | 1.36 |
| 1899 | Monier-Williams 1899 | Monier-Williams | 286,560 | 1.15 |
| 1928 | Schmidt | Petersburg | 29,125 | 1.14 |
| 1957 | Apte 1957 | Apte | 90,654 | 1.73 |

Two confounds were controlled. The per-entry metric penalises dictionaries that split compounds
into separate headwords — Monier-Williams 1899's 286,560 entries dilute its ratio (1.15) far
below its own 1872 edition (2.85), a headword-policy artefact, not a temporal one — so a fixed
panel of 28–30 simple nouns present across the corpus removes it; the panel correlation is
**r = 0.093**. Neither correlation is significant, but with eleven dictionaries across seven
families the pooled correlation is *underidentified*, not a measured null: it cannot separate a
year effect from family composition. The decisive test holds family fixed, and each of the four
families spanning more than one edition is flat-to-*declining* in granularity over time (fixed
panel: indigenous −0.014, Apte −0.027, Petersburg −0.049, Monier-Williams −0.349 sense-units per
lemma·year). Apte 1957 does not enumerate more finely than Apte 1890. Inflation is not merely
undetected but contradicted in direction. The corrective matters for practice: any
cross-dictionary measure normalised "per sense" silently encodes the school of the dictionary
unless family is controlled — "later = finer" is, on this corpus, false.

## 4. H2 and H3 — cited senses persist, and descendants condense

**Survival (H2).** On the 28-noun panel, cited ancestor senses (those carrying at least one
`<ls>` citation) survived into the descendant at **0.762** against **0.705** for uncited senses.
But the cited senses are not spread across the panel: 82 of the 84 fall on a single edge, Apte
1890 → 1957, so the clean test is *within* that edge, where cited senses survive at **0.768**
against **0.661** for uncited — a two-proportion *z* = 1.80, *p* = 0.07, **not significant**. A
pooled logistic model that borrows strength across edges returns an odds ratio of ≈ 3 that *looks*
significant, but it is unstable: changing how an unrelated edge is parsed moved it from ≈ 1.75 to
≈ 3.0 without touching a single cited sense. The honest reading is that citation **co-varies** with
persistence but is not established as an *independent* predictor of it on this corpus — a caution
that echoes the broader lexical-survival literature, where an apparent survival predictor is often
a proxy for usage frequency (Pagel, Atkinson, and Meade 2007) unless the confound is controlled.
That the surviving senses tend to be the cited, central, early-position ones is exactly what
regular polysemy would predict — the structurally basic sense propagates and persists while the
peripheral extension is the first to drop — but the corpus cannot yet separate that mechanism from
edge composition.

**Drift (H3).** Across the three measurable edges the movement is copy or condense, **never
expansion** (Table 2). Śabda-Sāgara's glosses are 90.6 % word-identical to Wilson's, sense by
sense — a near-verbatim copy that confirms the lemma-level containment edge of Chapter 9 at
microstructural resolution. The Apte revision contracts from 10.8 to 7.8 sense-units per lemma
without adding any. Wilson → Yates, once read as a dramatic 9 → 1 abridgement, was an extraction
artifact (Yates marks senses with semicolons, not numbers); counted correctly it is a genuine
condensation, ≈ 9 → 5.7. No measured edge adds senses.

**Table 2.** Inheritance edges (28-noun panel).

| Edge | Mean senses (anc → desc) | Drift | Gloss overlap | Pattern |
|---|---|---:|---:|---|
| Wilson 1832 → Śabda-Sāgara 1900 | 9 → 9 | 0 | 0.906 | near-verbatim copy |
| Wilson 1832 → Yates 1846 | 9 → 5.7 | −3.3 | 0.256 | condensation |
| Apte 1890 → Apte 1957 | 10.8 → 7.8 | −3.07 | 0.565 | revision, condensation, no expansion |

Combined with H1 the result inverts the inflation intuition twice over: later dictionaries are
not finer-grained in general, and on the edges where inheritance is directly measurable the
movement is toward faithful copying or contraction.

## 5. The indigenous register: sense and citation as one unit

The indigenous lexica sit at 1.00 units per entry — a floor that measures the absence of a
European convention, not absence of content (the zero-meaning rule of Chapters 4 and 7). The
promotion experiment sharpens this into a structural finding: the *Śabdakalpadruma*'s *dharma*
entry closes its synonym run *ity Amaraḥ*, so the listed synonyms and the citation that licenses
them sit in the same *iti*-unit — definition and attestation are structurally fused. A
corpus-scale count over every SKD and VCP record shows the fusion is pervasive but tracks *record
type*: 43.3 % of SKD records and 76.7 % of VCP records contain an authority-marked unit, and
among those units SKD splits near-evenly (53.3 % authority-terminal) while VCP skews to fusion
(77.6 %), the difference driven by short encyclopaedic entries versus long discursive commentary
rather than by dictionary identity. Wherever a citation lands inside a unit's own definitional
run, the European sense/apparatus distinction cannot be imposed without loss — the same *iti*-unit
that Chapter 7 identified as the kośa's microstructural atom and Chapter 10 measured as its
citation register. Digital lexicography that aims to align the traditions must model the fusion,
not filter it out.

---

## Part II — Order: genetic, not historical

## 6. The sense-ordering question

Part I asked what happens to the *set* of senses; Part II asks how the senses *within* an entry
are sequenced. Macrostructure — the order of headwords — is alphabetical in all these
dictionaries and is not at issue. The question is microstructural: given a polysemous word, in
what order are its senses printed? Four principles are conceivable — *historical* (oldest
attestation first), *logical-semantic* (commonest or most pedagogically useful first),
*etymological/genetic* (root meaning first, then derived), and *frequency* (no printed frequency
dictionary of Sanskrit exists). The received view, repeated in handbooks, is that the
comparative-philology generation ordered senses historically.

The field's own vocabulary already anticipates that this is a spectrum, not a binary: dictionaries
are *weakly* or *strongly* historical in their sense arrangement (Considine 2013), and
sense-order indeterminacy — the fact that no single principle fully determines the sequence — is a
named open problem in the practical literature (Jackson 2002, §14.5; Kipfer 1984), with intra-entry
order treated as a deliberate editorial choice (Partridge 1963). The theoretical claim I test is
sharper than "historical vs. not." Apresjan's synchronic-derivational principle holds that a
well-ordered entry leads with the *basic* sense and derives the rest from it by regular operations
(literal → figurative by removal of an assertive component), so that the lead sense is the
*generative* one, not necessarily the oldest. The empirical question is whether the European
Sanskrit dictionaries follow *that* principle — and the answer is that they largely do, which is
why the chapter must engage Apresjan rather than merely report a percentage.

## 7. PWG and Monier-Williams order senses genetically

Using the CDSL editions and a citation-dating map that assigns every `<ls>` siglum a date and a
Renou language-state (covering 70.9 % of PWG's 801,788 citations), I segment the printed senses of
each entry, extract the dated citations per sense, and ask whether the first printed sense is the
oldest-attested and how strongly printed order correlates with date order (Table 3).

**Table 3.** Sense order vs. attestation date, the two philological dictionaries.

| Metric | PWG | MW |
|---|---|---|
| Multi-sense entries with ≥2 dated senses | 11,882 | 13,822 |
| Printed sense 1 = oldest-attested sense | **73.5 %** | **69.4 %** |
| Kendall τ (printed order vs date order) | **0.375** | **0.367** |
| Citations within a sense strictly oldest→newest | 25.4 % | 55.0 % |
| Adjacent citation pairs non-decreasing in date | 76.8 % | 67.6 % |

The two dictionaries are statistically almost the same animal — unsurprising, since MW's
dependence on the Petersburg lexicon is established (Chapter 12) and a shared ordering regime is
one more inherited convention. The lead sense is the oldest about 70–74 % of the time: high, but
far from the ~100 % a true historical sort would give, and equally far above the **date-agnostic
chance floor of 52.7 %** (old senses are plentiful, so a lead sense picked with no regard to date
is oldest half the time anyway). The observed 73.5 % covers 44 % of the floor-to-ceiling span, and
τ = 0.375 against a shuffle floor of ≈ 0 covers 38 % of its span. The signal is **real but
partial** — the calibrated, quantitative form of "genetic, not historical." Inside a sense,
citations *lean* old-to-new (76.8 % of adjacent PWG pairs) but are strictly sorted only a quarter
of the time, because the editors also group citations by sub-sense and construction.

This matches what the prefaces say. PWG's preface states no sense-ordering rule but a method of
meaning-recovery anchored in the Veda; Grassmann's — the one preface to state the rule — is
explicitly etymological-genetic ("the basic concept is *das Erstrebte*… **therefore** 1) goal;
2) work…"); Monier-Williams describes only the etymological macrostructure and a punctuation
convention for grouping adjacent senses by affinity. The numbers and the prefaces agree, and both
agree with Apresjan: the lead sense is the *generative* root sense, chronology a tendency in the
citation stream rather than the sort key. One class of vocabulary mixes axes — for grammar and
philosophy technical terms (*prakṛti, vṛtti, nyāya*) PWG leads with the Classical/Pāṇinian
technical sense, following logical-semantic salience exactly as a śāstra reader needs — so sense
ordering is not even a single global policy within one dictionary.

## 8. Apte and Kochergina order by salience

The discriminator that separates the philological from the pedagogical tradition cleanly is
**Vedic-citation density**: the fraction of cited senses reaching at least one Vedic source
(Table 4).

**Table 4.** Vedic-citation density.

| Dictionary | Vedic-citation density | basis |
|---|---|---|
| PWG (Böhtlingk–Roth) | **23.4 %** | 113,012 cited senses |
| MW (Monier-Williams) | **24.8 %** | 99,716 cited senses |
| AP90 (Apte 1890) | **2.3 %** | 19,163 cited senses |
| Koch (Kochergina 1978/87) | **0.0 %** | 29,177 records (5 dated cites total) |

Apte and Kochergina drop by an order of magnitude or to zero. Their first sense is the one a
student needs first: Apte's *dharma* opens with "Religion," relegating the etymological core "that
which is established, ordinance" to sense 2, where PWG and MW open *dharma* with the root meaning
"that which is held fast." Their order is logical-semantic and pedagogical, by editorial choice
(Apte) or by being a citation-free learner's dictionary (Kochergina) — frequency/salience-first
ordering being the modern practical default (Walter 2010; Atkins and Rundell 2008). The
Vedic-density axis thus recovers empirically the same split the theory names: the strongly
historical/genetic dictionary versus the weakly historical, salience-ordered one.

## 9. Consequence, and the unifying finding

Because every sense can now be auto-dated, it is tempting to "improve" a historical dictionary by
re-sorting its senses oldest-first. The measurement shows the cost: such a re-sort would change the
lead sense for **26.5 %** of PWG's multi-sense entries, impose a stricter chronology than Böhtlingk
and Roth used, and actively mis-serve the śāstra vocabulary of §7. The right move for a digital
re-edition is to **preserve the source order** and attach the attestation period as per-sense
display metadata — a Vedic / epic / classical badge — with an optional, explicitly-labelled
"sort by oldest attestation" view. Editorial order is an authorial stance; chronology and frequency
are lenses laid over it. In the book's terms, the sense's *order* is itself an evidence-graph
property — a graded, provenance-bearing statement about the editor's judgement — that a re-edition
must record rather than silently overwrite.

The two halves of the chapter converge on one thesis. Sense *granularity* is a signature of
lexicographic school, flat-to-declining in time (Part I); sense *order* is likewise a school trait
— genetic in the philological dictionaries, salience-driven in the pedagogical ones — and neither
is the simple function of history the received view assumes. Inheritance copies or condenses; it
does not inflate. Order leads with the generative sense; it does not sort by the calendar. Both are
exactly what a theory of the entry as a *structured* object, rather than a chronological list,
predicts — and both are now measured, edge by edge and entry by entry, against a documented
dictionary family, which is what turns Apresjan's account from a stipulation into a tested claim.

## References

Apresjan, Jurij D. 2000. *Systematic Lexicography.* Trans. Kevin Windle. Oxford: Oxford
University Press.

Atkins, B. T. Sue, and Michael Rundell. 2008. *The Oxford Guide to Practical Lexicography.*
Oxford: Oxford University Press.

Considine, John. 2013. "Historical Dictionaries: History and Development; Current Issues." In
*The Bloomsbury Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury. [Weakly vs.
strongly historical dictionaries.]

Hanneder, Jürgen. 2020. "Woher hat er das? Zum Charakter des *Sanskrit-English Dictionary* von
Monier-Williams." *Zeitschrift der Deutschen Morgenländischen Gesellschaft* 170 (1): 107–117.

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.
[§14.5, sense-order indeterminacy.]

Kipfer, Barbara Ann. 1984. *Workbook on Lexicography.* Exeter: University of Exeter.

Lew, Robert. 2013. "Identifying, Ordering and Defining Senses." In *The Bloomsbury Companion to
Lexicography,* ed. Howard Jackson. London: Bloomsbury. [Sense individuation: senses as discrete
entities vs. artifacts of dictionary structure — Hanks, Sinclair.]

Pagel, Mark, Quentin D. Atkinson, and Andrew Meade. 2007. "Frequency of Word-Use Predicts Rates
of Lexical Evolution Throughout Indo-European History." *Nature* 449: 717–720.

Partridge, Eric. 1963. *The Gentle Art of Lexicography.* London: Deutsch.

Renou, Louis. 1956. *Histoire de la langue sanskrite.* Lyon and Paris: IAC.

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature V.4.) Wiesbaden:
Harrassowitz.

Walter, Elizabeth. 2010. "Using Corpora to Write Dictionaries." In *The Routledge Handbook of
Corpus Linguistics,* ed. Anne O'Keeffe and Michael McCarthy, ch. 31. London: Routledge.
[Frequency-based ordering as the modern default; corpus-unattested dictionary senses.]

Wiegand, Herbert Ernst. 1989. "Der Begriff der Mikrostruktur." In *Wörterbücher / Dictionaries /
Dictionnaires,* vol. 1 (HSK 5.1), 409–461. Berlin and New York: Walter de Gruyter.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.) Prague:
Academia; The Hague and Paris: Mouton.

Zgusta, Ladislav. 1988. "Copying in Lexicography: Monier-Williams' Sanskrit Dictionary and Other
Cases (Dvaikośyam)." *Lexicographica* 4: 145–164.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL), Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/); the eleven
dictionaries of Part I and the citation-dating map of Part II are itemised in the source articles.
Kochergina, V. A. 1987. *Sanskritsko-russkij slovar'.* 2nd ed. Moscow: Russkij Yazyk.

_Dr. Mārcis Gasūns_
