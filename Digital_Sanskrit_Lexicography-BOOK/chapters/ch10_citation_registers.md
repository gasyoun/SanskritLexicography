# Chapter 10 — Two Citation Registers: The European Apparatus and the Indigenous *iti*-Quotation

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Two Citation
> Registers and the Dictionary-to-Book Gap in the Cologne Digital Sanskrit Lexicon* (source
> draft:
> [paper_citation_registers.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md)),
> which is being published separately in a journal version (target: *International Journal of
> Lexicography*); where the article must remain independently citable, cite that version.
> Every corpus count and table below is carried over unchanged and is reproducible from the
> committed artifact
> ([`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json),
> generator
> [`scripts/obs/citation_register_gaps.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/citation_register_gaps.py));
> only the framing has been converted from journal to book form — abstract and keywords
> removed, companion "P-numbers" remapped to this book's chapters, and the comparative
> metalexicography engaged at the monograph's depth. Section numbering is chapter-internal
> (§1–§7).

If Chapter 9 measured how a dictionary points *at itself*, this chapter measures how it points
*outward* — to the texts on whose authority each sense stands. Source citation is the
evidential backbone of a scholarly dictionary and, in the book's terms, the layer of the
evidence graph where a lexicographic statement names its corpus attestation. Chapter 2 defined
two estimators over it: how many citations a dictionary carries and in what register (§3.4),
and what fraction can be resolved from a bare reference to an actual passage (§3.5). This
chapter instantiates both at corpus scale across the forty-four dictionaries of the Cologne
Digital Sanskrit Lexicon (CDSL), and in doing so uncovers the same structural surprise the
book meets again and again: the instrument built for one tradition is blind to the other.

The surprise here is sharp enough to invert a ranking. Measured by the European
critical-apparatus tag, the *Śabdakalpadruma* — one of the densest-citing dictionaries in the
entire corpus — scores a flat zero and ties for last, indistinguishable from a dictionary that
cites nothing. It is the citation-register analogue of the "zero means nothing" doctrine that
Chapters 4 and 7 established for macro- and microstructure: a zero under a convention-specific
detector is a fact about the instrument, never about the text. The chapter's principal finding
is that the CDSL holds **two disjoint citation systems**, and that no per-dictionary citation
statistic is even well-defined until the register is named.

## 1. Introduction

Source citations are the evidential backbone of a scholarly dictionary: the abbreviation
*Rām.* or *MBh.* after a sense tells the reader on whose authority it stands — what the field's
own reference work calls the dictionary's "source code" (Hartmann and James 1998). The modern
apparatus has a documented origin in the great historical dictionaries: the *OED*'s citations
were built from millions of quotation slips returned by volunteer readers against Murray's
printed reading instructions (Jackson 2002), so that a citation is not an ornament but the
physical trace of the evidence-gathering that made the entry. When such a dictionary is
digitised, its citations acquire a second life as potential hyperlinks — from the lexical
entry to the cited text and, ideally, to the exact passage. Realising those links across a
large historical corpus is the "dictionary-to-book" problem, and its tractability is an
empirical question: it depends on how regular the citations are and on whether the source
abbreviations can be resolved to a controlled list of works.

This chapter measures the problem for the CDSL, which encodes forty-four Sanskrit dictionaries
in a shared markup with an explicit source-citation tag. I ask three questions. *How many
citations are there, and how densely do the dictionaries cite?* *What fraction carry enough
information — a locator — to be resolved to a passage rather than merely to a work?* And *how
large and how skewed is the inventory of cited sources, once abbreviation variants are
normalised?* A fourth question proves to be prior to all of these: *do all the dictionaries
cite in the same way at all?* The answer — that two of the corpus's lexicographic traditions
use mutually unintelligible citation registers — reframes every per-dictionary statistic and
is the chapter's principal finding.

## 2. Background

### 2.1 The `<ls>` apparatus

The CDSL markup provides an `<ls>` ("literary source") element wrapping a source reference
within an entry. In the European Indological dictionaries this is the machine-readable trace of
the critical apparatus: *Rām.*, *MBh.*, *RV.*, *Pāṇ.*, often with a locator (*Bhag. 10. 33*).
A standing effort within the project — the "dictionary-to-book" link-target work — aims to turn
these into click-throughs to scanned source pages; its feasibility is exactly what a
corpus-level resolvability measurement quantifies. The tagged critical apparatus is itself the
heir of a long European tradition of the citation canon: Nonius Marcellus built his
*De compendiosa doctrina* on a fixed roster of some forty *auctores* cited in a regular,
work-ordered sequence — the regularity Lindsay codified as "Lindsay's law" (Ferri 2019, essay
by Gatti) — so that a machine-resolvable apparatus is the digital continuation of a
two-thousand-year-old habit of citing by a controlled source list.

### 2.2 Two traditions of citing

The indigenous Sanskrit lexicographic tradition does not use a European apparatus. The *kośa*s
cite by quotation: a phrase or definition is given and closed with the quotative particle *iti*
followed by the name of the authority — *iti Śabdaratnāvalī*, *ity Amaraḥ*, *iti Manuḥ*. The
project has already recorded, qualitatively, that the *Śabdakalpadruma* and *Vācaspatya* are
"among the densest citers in the corpus yet score zero on an `<ls>`-based counter" (the
`INDIG-CITE` finding). This chapter supplies the numbers behind that observation and draws out
its consequence for any corpus-wide citation statistic.

The two are not merely two markups but two *technologies of authority*, and the comparison has
a instructive third term outside the Indo-European frame. The classical Arabic lexicographers
theorised their witness system explicitly: the *šawāhid* (probative citations) were admissible
only from the *ʿuṣūr al-iḥtiǧāǧ*, the bounded "epochs of sound usage," and even a living
Bedouin informant was screened for the purity of his speech before his usage could license a
lexical entry (Baalbaki 2014). Against that doctrinally-theorised apparatus, the European
`<ls>` tag is a lightly-regulated convention and the Sanskrit *iti*-quotation a syntactic one;
naming the Arabic case keeps the chapter's "two registers" from reading as a local Sanskrit
peculiarity, and shows the *iti*-register to be one instance of a general fact — that a
citation apparatus is a designed evidence-admission policy, differently formalised in each
lexicographic civilization.

## 3. Data and method

### 3.1 Counting `<ls>` citations and their resolvability

I extract every `<ls>…</ls>` element from the canonical source files (`csl-orig/v02`) of all
forty-four dictionaries. A citation is classed as **locator-bearing** if its content contains a
numeral (a book, chapter, verse or page reference), and **bare** otherwise. Locator presence is
a generous proxy for resolvability — it is a necessary, not sufficient, condition for linking to
a passage — so the locator share is reported as the *upper* bound of a resolvability band. The
lower bound additionally requires the citation's source abbreviation to be a member of the
established source set (§3.2).

### 3.2 Normalising the source inventory

Source abbreviations vary by dictionary house style. Two folding layers reduce them to
canonical identities. The first is a **diacritic-and-case fold** (`foldSiglum`): *MBh* and
*MBH* both fold to *mbh*, *RV* and *ṚV* to *rv*. The second is a reviewed
**abbreviation-family** layer: length variants of one work — *R.*, *Rām.*, *Rāmāy.* → Rāmāyaṇa
— that the fold cannot catch. Because abbreviation merging is error-prone, it is generated as
*review candidates* (a prefix-clustering tool over the fold-keys) and adjudicated by hand into a
curated alias table; the tool deliberately surfaces false candidates (the *Rājataraṅgiṇī* and
*Rājanighaṇṭu* sigla share a prefix but are distinct works) so that they are *split*, not
merged. This human-adjudicated alias table is the operational form of the book's review-gate
discipline (Chapter 2, §4) applied to the citation layer.

### 3.3 The indigenous register

For the *kośa*s I count the quotative construction directly: occurrences of *iti* and its
pre-vocalic sandhi form *ity* at a word boundary — not adjacent to a Latin letter on either
side — which excludes the many in-word substrings (*prīti*, *nīti*) while still counting
quotatives that sit directly after markup or punctuation. The markup-aware boundary matters: the
*Kṛdantarūpamālā* wraps its Sanskrit in `<s>…</s>` tags, so most of its sūtra-citing *iti*
follows a tag close, and a naive space-preceded rule would miss some two-thirds of it. This is a
register *indicator*, not an exact citation count — it includes some grammatical *iti* — but the
contrast it reveals between registers is too large to be an artefact.

### 3.4 What the method does not claim

Locator presence is not verified linkability; a numeral may be ambiguous without a resolved
siglum. The *iti* count is an upper proxy for indigenous citations. Siglum disambiguation is
intrinsically hard, which is why merges are reviewed rather than automatic. These limits are
revisited in §6.

## 4. Results

### 4.1 Volume and per-dictionary density (the `<ls>` register)

The European dictionaries carry **1,245,644 `<ls>` citations**, about **0.83 per entry**
corpus-wide, but density is very uneven (Table 1). The *Großes Petersburger Wörterbuch* is the
most citation-dense major dictionary at 4.61 citations per entry (568,730 in total); Benfey,
the Buddhist Hybrid Sanskrit dictionary and Monier-Williams (312,160) follow.

**Table 1.** `<ls>` citation density, selected dictionaries.

| Dictionary | `<ls>` citations | per entry |
|---|---:|---:|
| PWG — Petersburg (große) | 568,730 | 4.61 |
| MW — Monier-Williams 1899 | 312,160 | 1.09 |
| BEN — Benfey 1866 | 48,603 | 2.81 |
| BHS — Buddhist Hybrid Sanskrit | 48,419 | 2.71 |
| AP — Apte 1957 | 62,672 | 0.69 |

*All figures from the committed artifact
[`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json),
generated by
[`citation_register_gaps.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/citation_register_gaps.py)
— an `<ls>` count over `csl-orig/v02` reusing the extraction convention of
[`parse_cslorig.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/parse_cslorig.py).*

### 4.2 The dictionary-to-book gap is ~41 %

**59.3 % of `<ls>` citations carry a locator** (738,173 of 1,245,644); requiring in addition an
established source siglum lowers this only marginally — by 0.7 percentage points in the 2026-06
siglum pass (then 59.8 % → 59.1 %) — that is, almost every locator-bearing citation already uses
a recognised source. The resolvability band is therefore tight, **≈58.6–59.3 %**, and robust.
Its complement is the measured ceiling of the **dictionary-to-book gap: ~41 % of citations,
roughly 507,000, are bare source abbreviations** that cannot be resolved to a passage without
further work. The figure is encouraging for automation — a clear majority of the European
apparatus is mechanically linkable — and it sizes the manual residue precisely. I am not aware
of a published corpus-level locator-resolvability figure for a comparable historical dictionary
portal to set this against; the closest available comparator is qualitative, not quantitative —
pre-critical (pre-twentieth-century) lexicography treats locator-bearing citation as the
exception rather than the rule, favouring bare authority names over chapter-and-verse
references — so a ~59 % locator rate, on a nineteenth-century corpus, already exceeds the
pre-digital expectation rather than falling short of it.

### 4.3 A small working apparatus behind a long tail

The cited-source inventory is steeply skewed. About **13,000 raw abbreviation strings** fold to
roughly **9,000 distinct sigla**, but only **2,166 sources are cited ten or more times** — the
genuine working apparatus — while the remainder are rare or one-off references. Concentration is
extreme: the **fifty commonest sigla account for about half of all citations**, led by the
Rāmāyaṇa, the Mahābhārata, the lexicographers (*L.*), Pāṇini, the Ṛgveda and the major
*purāṇa*s. The diacritic/case fold alone resolves the largest variant pairs (Mahābhārata
*MBH*+*MBh* = 75,548; Ṛgveda *ṚV*+*RV* = 32,316); abbreviation-family review then collapses
length-variant families (*Kathāsaritsāgara*, *Suśruta*, *Raghuvaṃśa* and others) further. I
adjudicated the high-frequency families into a reviewed alias table of canonical works, keeping
distinct works that merely share a prefix apart. The practical implication is that a **reviewed
source-abbreviation registry of low-thousands of entries suffices to resolve the great majority
of the European apparatus** — a working canon strikingly close in order of magnitude to Nonius'
forty *auctores* scaled to a corpus, and the direct descendant of that habit of citing from a
bounded list.

### 4.4 The hidden register: indigenous *iti*-citation

The `<ls>` count omits an entire citation system. The Sanskrit-to-Sanskrit *kośa*s carry **no
`<ls>` tags whatever**, yet cite densely by quotation (Table 2): the *Śabdakalpadruma* records
~80,000 *iti*-citations, the *Vācaspatya* ~15,600, and the *Kṛdantarūpamālā* the highest density
in the corpus at six per entry. An `<ls>`-only measure therefore mis-ranks precisely these
dictionaries as citation-poor when they are among the richest.

**Table 2.** Indigenous *iti*-register citation (zero `<ls>` in every case).

| Dictionary | `<ls>` | *iti*-citations | per entry |
|---|---:|---:|---:|
| KRM — *Kṛdantarūpamālā* | 0 | 12,359 | 6.00 |
| SKD — *Śabdakalpadruma* | 0 | 80,164 | 1.88 |
| VCP — *Vācaspatya* | 0 | 15,619 | 0.31 |

These dictionaries cite indigenous authorities — Amara, Trikāṇḍaśeṣa, Śabdaratnāvalī, Viśva,
Medinī, Manu — through the *iti* construction. Their dictionary-to-book problem is different *in
kind*: linking *iti X* to an indigenous source lexicon or text, not resolving a
chapter-and-verse locator.

The mis-ranking is not a rhetorical figure but a measured swap. Ranking all forty-four
discovered CDSL dictionaries by `<ls>` density places the *Śabdakalpadruma* **tied for last** —
twenty-eight of the forty-four source files carry no `<ls>` tag at all, and this measure cannot
distinguish SKD from any of them, that is, from a dictionary that cites nothing. Ranking the
same forty-four by *iti*-density instead places it **2nd of 44**
([`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json))
— behind only the *Kṛdantarūpamālā*, ahead of every European dictionary in the corpus,
including the *Großes Petersburger Wörterbuch* that leads Table 1. A single-register citation
statistic therefore does not merely under-count SKD; it inverts its standing in the corpus, from
apparently citation-poorest to among the two or three most citation-dense dictionaries in CDSL.
This inversion is the citation-layer twin of the kośa result of Chapter 4 and the verbal-root
result of Chapter 7: measure a tradition with the other tradition's instrument and it reads as
empty.

### 4.5 Two disjoint citation systems

The corpus thus contains two non-overlapping citation registers. The 59 % resolvability result
and the source-abbreviation registry apply to the European `<ls>` register alone; the indigenous
register is invisible to them and requires its own normaliser keyed on the *iti*-source
construction. **Any per-dictionary citation statistic that does not state its register is
therefore ill-defined** — the apparent "citation-poverty" of a *kośa* is an artefact of
measuring the wrong tradition's markup.

## 5. Discussion

**For digital lexicography.** The dictionary-to-book task is, for the European apparatus, about
60 % mechanisable: a clear majority of citations carry a locator and draw on a working set of
~2,000 sources that a reviewed registry can resolve. The ~41 % bare-abbreviation residue sizes
the manual or heuristic effort that remains. The abbreviation-normalisation pipeline —
automatic diacritic/case fold plus a reviewed alias table grown from machine-generated
candidates — is reusable infrastructure for any citation-linking project, and the deliberate
refusal to auto-merge prefix-similar sigla is the methodological safeguard that keeps distinct
works distinct.

**For the history and typology of lexicography.** That two lexicographic traditions cite in
mutually unintelligible registers is a finding of comparative metalexicography, not merely a
markup detail. The European critical apparatus, the indigenous *iti*-quotation, and — beyond the
corpus — the Arabic *šawāhid* system (§2.2) are three different technologies of authority, and
the CDSL, by placing the first two in one corpus, lets the difference be *measured*: register,
density, and source inventory are now quantities rather than impressions. This is the citation
face of the book's central comparison, and it pairs directly with the next chapter's map of
*what* the `<ls>` apparatus actually cites (Chapter 11, the citation-frequency graph).

**A methodological warning.** Aggregated dictionary statistics that sum across dictionaries of
different citation traditions will systematically under-credit the indigenous lexica. Register
must be a controlled variable in any cross-dictionary citation comparison — the same discipline,
applied to citation, that Chapter 9 applied to the cross-reference graph and Chapter 4 to the
entry count.

## 6. Limitations and future work

Locator presence bounds resolvability from above; verifying that a located citation actually
links to a retrievable passage (matching the resolved siglum to a digitised edition with the
right reference scheme) is the next step and will lower the figure. The *iti* proxy over-counts
indigenous citations by including grammatical and derivational *iti*; a parser keyed on *iti +
proper-name* would tighten it. The reviewed alias table covers the high-frequency families; the
long tail of low-frequency sigla remains in the review queue by design. Finally, the two
registers should be unified at the level of the cited *work*, so that a source cited as *MBh.*
in the apparatus register and quoted *iti …* in a *kośa* is recognised as the same authority —
the prerequisite for a corpus-wide, register-neutral citation graph, and the natural bridge to
the citation-frequency analysis of the following chapter.

## 7. Conclusion

The Cologne Digital Sanskrit Lexicon contains over 1.2 million explicit source citations, of
which **up to** a tight majority — 59.3 %, the locator-bearing upper bound — are resolvable in
principle to a passage, leaving a measured dictionary-to-book gap of at least some 507,000 bare
abbreviations, all drawing on a working apparatus of roughly two thousand sources. But this
European apparatus is only one of two citation registers: the indigenous *kośa*s cite densely
through *iti*-quotation — on an indicator that includes some grammatical *iti* and so bounds
their citation rate from above — and are wholly invisible to an `<ls>`-based measure. Citation
density, resolvability, and source inventory are all well-defined only once register is fixed.
Recognising the two registers — and building a reviewed source registry for each — is the
precondition for turning a digitised dictionary corpus into a navigable web of
dictionary-to-source links.

## References

Baalbaki, Ramzi. 2014. *The Arabic Lexicographical Tradition: From the 2nd/8th to the 12th/18th
Century.* (Handbook of Oriental Studies 1.107.) Leiden and Boston: Brill.

Ferri, Rolando (ed. contributions). 2019. In Robert Maltby et al. (eds.), *Studies on Late
Antique and Medieval Latin Glossaries and Dictionaries.* [Gatti on Nonius Marcellus' *auctores*
canon and the ordered-citation regularity known as Lindsay's law.]

Hartmann, R. R. K., and Gregory James. 1998. *Dictionary of Lexicography.* London and New York:
Routledge. ["Source code" as the field's term for citation sigla.]

Hausmann, Franz Josef, Oskar Reichmann, Herbert Ernst Wiegand, and Ladislav Zgusta (eds.).
1989–1991. *Wörterbücher / Dictionaries / Dictionnaires: An International Encyclopedia of
Lexicography.* 3 vols. Berlin and New York: Walter de Gruyter.

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.
[Murray's reader instructions and the OED citation-slip method.]

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature, ed. Jan Gonda,
vol. 5, fasc. 4.) Wiesbaden: Otto Harrassowitz. [The standard reference for the indigenous
*kośa* citation tradition discussed in §4.4.]

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.) Prague:
Academia; The Hague and Paris: Mouton.

### Primary sources

Böhtlingk, O. and Roth, R., *Sanskrit-Wörterbuch* [PWG] (St Petersburg, 1855–1875);
Monier-Williams, M., *A Sanskrit-English Dictionary* (Oxford, 1899); Benfey, T. (1866); Apte,
V. S. (rev. edn 1957–1959); Edgerton, F., *Buddhist Hybrid Sanskrit Dictionary* (1953);
Rādhākānta Deva, *Śabdakalpadruma* (1822–1858); Tarkavācaspati, *Vācaspatya* (1873–1884);
Bhaṭṭoji Dīkṣita (attrib.), *Kṛdantarūpamālā*. Cited Sanskrit sources named in the apparatus
(selection): *Rāmāyaṇa*, *Mahābhārata*, *Ṛgveda*, Pāṇini's *Aṣṭādhyāyī*, *Bhāgavata-purāṇa*,
*Kathāsaritsāgara*, *Suśruta-saṃhitā*, *Raghuvaṃśa*. All consulted in the machine-readable
editions of the **Cologne Digital Sanskrit Dictionaries (CDSL)**, Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

_Dr. Mārcis Gasūns_
