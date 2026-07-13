# Chapter 4 — Order Is the Dictionary: The Macrostructure of the Versified Synonymic *Kośa*

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Order Is the
> Dictionary: A Macrostructural Model of the Versified Synonymic Kośa* (source draft:
> [paper_kosha_macrostructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md)),
> which is being published separately in a journal version (target: *International Journal
> of Lexicography*, with the World Sanskrit Conference 2027 as an indological alternate);
> where the article must remain independently citable, cite that version. Every count and
> table below is carried over from the article unchanged and is reproducible from the
> committed data
> ([`data/lexico/kosha_macrostructure.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosha_macrostructure.json),
> generator
> [`scripts/lexico/m6_kosha_macrostructure.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_kosha_macrostructure.py));
> only the framing has been converted from journal to book form — the abstract and keywords
> removed, companion-paper "P-numbers" remapped to this book's chapters, and the secondary
> literature engaged at the depth the monograph's readership expects. Section numbering is
> chapter-internal (§1–§7); the book-wide renumbering and bibliography merge are a later
> production pass.

The Introduction posed the book's governing contrast: two lexicographic civilizations, the
European philological dictionary and the indigenous kośa, meeting in one digital corpus and
demanding to be measured on their own terms. Chapter 1 found the European tradition
*self-censoring* in the very language of its glosses. This chapter crosses to the other
civilization and asks the prior question — not what a kośa says inside an entry, but whether
it has "entries" at all — and answers that the genre's entire lexicographic content is
something a European entry-measure cannot even see: its **arrangement**. Where Chapter 5
anatomizes the European entry at full microstructural depth, this chapter shows the opposite
limiting case, a dictionary that is *only* structure, and so it is the sharpest test in the
book of the measurement discipline Chapter 2 laid down: a zero under a convention-specific
detector measures the absence of the convention, not the absence of content.

It is also the upstream end of the book's inheritance story. Because the kośa
sense-divisions descend, through the Fort William College pandits and Wilson, into the
European Sanskrit–English dictionaries whose descent Chapters 5, 6, and 9 measure, modelling
the kośa is modelling where those English sense-lists came from. And it is the macrostructural
companion to Chapter 7, which recovers the indigenous *micro*structure of the verbal-root
lexica; together the two chapters establish the book's "zero means nothing" doctrine at both
structural scales.

## 1. Introduction

A European dictionary is *semasiological*: it is ordered by the word (alphabetically) and, at
each word, tells you the meanings. The classical Sanskrit *kośa* is the inverse —
*onomasiological*: it is ordered by the concept, and at each concept lists the words (on the
semasiological/onomasiological division see Zgusta 1971; Svensén 2009). There is no alphabet,
no headword-then-definition entry, no citation apparatus. The *Amarakośa*, the genre's
exemplar, is 1,500 memorisable verses grouped by subject; to know that *vahni*, *agni* and
*pāvaka* are synonyms is simply to find them strung together in the fire-verse. The
lexicographic act is the *placement*.

The onomasiological ordering is neither exotic nor primitive; it has a European pedigree the
book should name, precisely so that the kośa is read as a mature member of a general
lexicographic type rather than as an oddity. Thematic, concept-ordered word-hoards run from
the mediaeval *hortus* and *nomenclator* traditions through Roget, and the historiography of
that onomasiological line (Hüllen; McArthur) is surveyed in Jackson's *Lexicography*
(ch. 12). The kośa is the Sanskrit instance of that type — and, being versified and
canonical, its most disciplined instance. Even the European alternative it is contrasted
with, alphabetical order, is not one thing and not a neutral default: the Arabic tradition
alone practised at least three distinct formal orders — phonetic-permutative, alphabetical,
and rhyme (final-radical) — and its own practitioners debated retrieval-convenience against
semantic-map fidelity (Baalbaki), while even within "alphabetical" the historical partial
orderings (Greek first-letter/first-syllable arrangement; Dickey) show the alphabet itself to
be a designed, imperfect compromise (Partridge). Against that comparative background the
kośa's choice of a concept-hierarchy over the alphabet is one considered access-structure
among several, not the absence of one.

This makes the *kośa* a stress test for digital metalexicography. Every structural measure
the field has built — and that this book applies across the Cologne Digital Sanskrit Lexicon
(CDSL) — keys on a European convention: a part-of-speech tag, an `<ls>` source siglum, a
`<div>` sense block. The *kośa* has none of these, and so reads as **empty** under all of
them. Chapter 2 records this as the *zero-meaning* rule: a zero under a convention-specific
detector measures the absence of that convention, not the absence of content. Chapter 7
demonstrates the rule for the indigenous *micro*structure (the verbal-root apparatus). This
chapter demonstrates it for the *macro*structure — and the demonstration is sharper here,
because the *kośa* has *no* microstructure to recover: its entire content is its arrangement.

My contribution is a quantitative macrostructural model of the four CDSL koshas: the
*kāṇḍa*–verse–synonym-set hierarchy made measurable (§3), the comparative ordering of two
koshas and its theological signature (§4.1), the verse-as-unit and synonym-set statistics
(§4.2), the incommensurability of the two digitization models (§4.3), and the gender
apparatus and macrostructural inheritance across the Hemacandra corpus (§4.4). The discussion
(§5) draws the corpus-statistics moral and ties the koshas to the sense-division lineage that
reached the European dictionaries.

## 2. The genre and the data

### 2.1 The versified synonymic *kośa*

The synonymic *kośa* (*nāmamālā*, "garland of names") arranges the vocabulary by subject into
*kāṇḍa*s (books) and *varga*s (thematic sections), and within each section composes the
synonyms of a concept into metrical verse for memorisation. The genre's standard history is
Vogel's *Indian Lexicography* (1979), which distinguishes the synonymic (*nāmamālā*) from the
homonymic (*nānārtha*) *kośa*, traces the Amarakośa commentaries, and surveys the Hemacandra
corpus analysed below; it is this chapter's primary secondary source. The *Amarakośa* (not in
CDSL) is the prototype; at the 2026-06 snapshot analysed here the CDSL held four others
(Table 1), headed by the two I analyse: Halāyudha's *Abhidhānaratnamālā* (**ARMH**, ~10th c.)
and Hemacandra's *Abhidhānacintāmaṇi* (**ABCH**, ~12th c.), together with the latter's two
supplements, the *-pariśiṣṭa* (**ACPH**) and the *-śiloñcha* (**ACSJ**). A **fifth** kośa —
Bhoja's *Nāmamālikā* (**NMMB**) — was digitized into the CDSL in 2026-06, after this snapshot:
a grouped-model text whose `<syns>` lists carry *no* `<s>` wrapper (2,265 lexemes, 521
unique), i.e. yet a *third* digitization variant of the same genre; it is out of scope here
and queued for the next revision, and it independently reinforces §4.3's warning.

**Table 1.** The four CDSL koshas.

| Code | Title | Author | Date | Tradition |
|---|---|---|---|---|
| ARMH | *Abhidhānaratnamālā* | Halāyudha | ~10th c. | Brahmanical |
| ABCH | *Abhidhānacintāmaṇi* | Hemacandra | ~12th c. | Jain |
| ACPH | *Abhidhānacintāmaṇi-pariśiṣṭa* | Hemacandra | ~12th c. | Jain |
| ACSJ | *Abhidhānacintāmaṇi-śiloñcha* | Jinadeva (attr.) | ~12th c. | Jain |

These koshas matter to the wider CDSL lineage: the Fort William College pandits built
Wilson's (WIL) English sense-divisions from exactly this kośa tradition, and those divisions
descend into Monier-Williams.[^wilson] The *kośa*'s macrostructure is, in that sense, an
ancestor of the European microstructure — which is one more reason it must be measured on its
own terms rather than scored zero.

[^wilson]: The compilation claim rests on Wilson's own account of his kośa-based method in the
    preface to his *Dictionary, Sanscrit and English* (1819); the precise descent of those
    sense-divisions into Monier-Williams is asserted here at the level the sources support and
    is turned into a measured edge set only by the sense-alignment study flagged in §6. This
    chapter states it as lineage, not as a quantified inheritance rate.

### 2.2 Why a microstructure detector scores them zero

The koshas carry none of the European entry apparatus. ARMH's "entry" is a fragment of a
verse; ABCH's is a synonym-list. There is no `<lex>`, no `<ls>`, no definitional prose to
parse. The dictionary pages in the atlas already flag the koshas as "Common-block framework:
**Not applicable** (verse-synonym genre)." The content is real and dense; it is simply
*located in the arrangement*, which is what I now measure. In the vocabulary of access
structures (Hartmann and James 1998), the European dictionary is monoaccessible through its
alphabetical outer structure; the kośa's outer access structure *is* its concept-hierarchy —
a different door to the same building, not a missing one.

## 3. Data and method

I measure the macrostructure directly from the canonical `csl-orig` source files with a
stdlib-only extractor
([`m6_kosha_macrostructure.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m6_kosha_macrostructure.py)),
which detects each kosha's encoding model and recovers its hierarchy. The two koshas use
**opposite digitization models**, and recognising this is itself part of the method:

- **ARMH — exploded.** Each synonym is its own `<L>` record carrying a verse locator `<vn>` =
  *kāṇḍa.section.subsection.verse*; the synonym-set is reconstructed by grouping all records
  that share a `<vn>`. (Five synonyms of "heaven" — *svar, svarga, surasadman,
  tridaśāvāsa, triviṣṭapa* — are five records, all tagged `<vn>1.1.1.3` and all repeating the
  same śloka.)
- **ABCH / ACPH / ACSJ — grouped.** A `;k{…kāṇḍaḥ}` header opens each book; one `<L>` record
  holds a whole concept-group in a `<syns>` field of `<eid>`-numbered lexemes, each carrying a
  gender tag (`-puM` masc., `-strI` fem., `-klī` neut., and combinations); every record is
  stamped `<info kvvv="…kāṇḍaḥ"/>`.

From these I count, per kosha: `<L>` records; distinct verses and *kāṇḍa*s (ARMH); *kāṇḍa*
headers and their order, lexeme (`<eid>`) counts, and the gender distribution (ABCH family);
synonym-set sizes (ARMH, by grouping on `<vn>`); and per-*kāṇḍa* record counts. The numbers
below are emitted to
[`kosha_macrostructure.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosha_macrostructure.json)
and are exact.

## 4. Results

### 4.1 Two orderings of one universe — and a Jain signature

Both koshas are onomasiological, but they order the conceptual universe **differently**
(Table 2). ARMH runs by **cosmic region** — *svarga* (heaven) → *bhūmi* (earth) → *pātāla*
(the nether/oceanic region, opening with *vaḍavāmukha*, the submarine fire) → *sāmānya*
(general) → *anekārtha* (homonyms). Hemacandra's ABCH runs by a **hierarchy of beings** —
*devādhideva* (the supreme Jinas) → *deva* (gods) → *martya* (mortals) → *tiryak* (animals) →
*naraka* (hell-beings) → *sāmānya* (general), closed by an *avyaya-varga* of indeclinables.

Two things are legible in the ordering. First, it is **Jain**: ABCH places the
*devādhideva-kāṇḍa* — the Arhats and Tīrthaṅkaras — *above* the Brahmanical gods, exactly
inverting the Amarakośa's *svarga*-first cosmology. The macrostructure encodes the worldview.
Second, the *order* is theological but the *mass* is anthropocentric: the **martya- (human)
*kāṇḍa* holds 811 of ABCH's 1,965 records** — more than gods (271+41) and animals (602) —
while the hell-*kāṇḍa* musters only **6**. A *kośa* is a map of what its culture had the most
words for, and that is the human world.

**Table 2.** Macrostructure of the two principal koshas (records per *kāṇḍa*).

| ARMH (cosmic region) | recs | | ABCH (hierarchy of beings) | recs |
|---|---:|---|---|---:|
| 1 *svarga* (heaven) | 1,462 | | 1 *devādhideva* (supreme Jinas) | 41 |
| 2 *bhūmi* (earth) | 3,959 | | 2 *deva* (gods) | 271 |
| 3 *pātāla* (nether) | 597 | | 3 *martya* (mortals) | 811 |
| 4 *sāmānya* (general) | 958 | | 4 *tiryak* (animals) | 602 |
| 5 *anekārtha* (homonyms) | 931 | | 5 *naraka* (hell) | 6 |
| | | | 6 *sāmānya* (general) | 203 |
| | | | *avyaya-varga* (indeclinables) | 31 |
| **total** | **7,907** | | **total** | **1,965** |

### 4.2 The verse is the unit; the synonym-set is the payload

In ARMH the lexical unit is the verse: **860 verse-locators** carry the **7,907**
synonym-records, a mean of **9.2 synonyms per verse** (median 8). Density is highest in the
heaven-*kāṇḍa* (**10.6** per verse) and lowest on earth (8.6) — the gods attract the most
names. The peak is emphatic: the single largest synonym-set is **56 names for Viṣṇu** (*viṣṇu,
kṛṣṇa, keśava, …*), followed by **47 for the Sun** (*āditya, savitṛ, bhāskara, …*) and **45
for Śiva** (*īśāna, paśupati, śaṅkara, …*). The theonymic richness of devotional Sanskrit is
directly visible as macrostructural density.

One honest qualification: ARMH's fifth *kāṇḍa* is *anekārtha* — **homonymic**, not synonymic.
Its verses use the *…api…* ("X also [means] Y") formula, e.g.
*"rudre'pi khaṇḍaparaśur vaiśravaṇe'py ekakuṇḍalaḥ…"* ("*khaṇḍaparaśu* also denotes Rudra;
*ekakuṇḍala* also denotes Vaiśravaṇa…"). The flat `<vn>` digitization explodes these word +
added-meaning pairs exactly as it explodes a synonym-set, so the per-verse figure for
*kāṇḍa* 5 (9.3) counts lexemes, not synonyms. I therefore report the synonym density on the
synonymic *kāṇḍa*s 1–4 (mean 9.18) and flag *kāṇḍa* 5 separately — the same
convention-awareness the genre demands, applied to its own internal sections.

### 4.3 Two digitization models, incommensurable counts

The headline methodological result is that the **same genre is digitized two opposite ways**
(Table 3). ARMH privileges the *headword* — one synonym, one record, alphabetically findable
— and so reports **7,907 "entries."** ABCH privileges the *concept-group* — one verse-set,
one record, preserving the onomasiological unit — and so reports **1,965 "entries"** holding
**4,619 lexemes**. Neither count is wrong; they measure different things. But it means **a
corpus statistic that sums "entries" across koshas is summing incommensurable units** —
ARMH's record is a lexeme, ABCH's is a synonym-set roughly nine lexemes deep. Any density,
coverage, or overlap figure computed over raw kosha record-counts is therefore an artifact of
digitization policy, not of the texts. The unit must be normalised (to the lexeme, or to the
verse) before koshas can be compared. The book's own corpus-collapse metric (Chapter 2, §3.2)
already implements this normalisation — kośa records enter the corpus count as their `<syns>`
lexemes, not as raw `<L>` records — so the hazard is real but, within this book, controlled.

**Table 3.** Two digitization models.

| Kosha | Model | Records | Lexemes | Verses / *kāṇḍa*s |
|---|---|---:|---:|---|
| ARMH | exploded (1 synonym = 1 record) | 7,907 | 7,907 | 860 v · 5 k |
| ABCH | grouped (1 concept = 1 record) | 1,965 | 4,619 | 6 k + *avyaya* |
| ACPH | grouped | 163 | 383 | 6 k |
| ACSJ | grouped | 240 | 491 | 6 k |

### 4.4 The gender apparatus, and macrostructural inheritance

Hemacandra's koshas carry a full **gender apparatus** layered over the macrostructure: every
lexeme in ABCH is tagged for *liṅga* — masculine (*puM*, 7,015 tags), neuter (*klī* =
*klība*, 3,110) and feminine (*strī*, 2,524), with dual-gender combinations (*puṃklī* "masc.
and neut.", 385; *puṃstrī*, 122) and number (*dvi*, *ba*) where relevant — 13,284 gendered
tags in all, the rarer combinations (*puṃdvi* 39, *strīklī* 29, *puṃba* 21, …) making up the
remainder beyond the five tags enumerated. This is grammatical information the European
dictionaries mark inconsistently and that Chapter 7 finds encoded *indigenously* in the
verbal-root lexica; here it rides on the synonym macrostructure, lexeme by lexeme.

Finally, the macrostructure is **inherited within the Hemacandra corpus**: the supplementary
*-pariśiṣṭa* (ACPH) and *-śiloñcha* (ACSJ) reuse the parent's six-*kāṇḍa* frame intact
(*devādhideva → deva → martya → tiryak → naraka → sāmānya*), adding gleaned material into the
existing books rather than re-ordering. The frame is a stable intellectual object,
transmitted across a textual tradition the way a European dictionary's alphabetisation is —
and just as measurable.

## 5. Discussion

**Order is the lexicographic act.** In a semasiological dictionary the semantic work is done
in the microstructure — the sense divisions, the glosses, the citations (the macro-/micro
structure division in the sense of Hausmann and Wiegand 1989). In the *kośa* it is done in the
macrostructure: to place *agni* in the fire-verse of the *svarga-kāṇḍa* is to assert its
meaning, its register and its synonymy in one stroke. A metalexicography that can only see
microstructure cannot see this lexicography at all. The *zero-meaning* rule, established for
the microstructure in Chapter 7, therefore reaches its strongest form here: the synonymic
*kośa* is **100 % macrostructure**, and a zero under any entry-level detector is a statement
about the instrument, never the text.

**Incommensurable counts are a corpus hazard.** §4.3 is a caution for the whole CDSL atlas
and for digital historical lexicography generally: when the same genre is digitized under
headword-primary and concept-primary models, raw entry counts cannot be summed or compared.
This is the macrostructural analogue of the citation-register and edit-type-axis confounds
the neighbouring chapters identify — convention must be a controlled variable, here the
*digitization* convention.

**A bridge to the lineage.** Because the kośa sense-divisions descend, through the Fort
William pandits and Wilson, into the European Sanskrit–English dictionaries, the
macrostructural model is also the upstream end of the inheritance graph this book measures
elsewhere (Chapters 5, 6, 9). The 56-synonym Viṣṇu verse is the ancestor of a column of
near-synonyms in Monier-Williams; modelling the *kośa* is modelling where those English
sense-lists came from.

## 6. Limitations and future work

The snapshot analysed holds four koshas — five since 2026-06, with NMMB (§2.1) awaiting its
own modeling pass — but not the *Amarakośa* itself, so the genre prototype is a comparandum
rather than data; adding a digitized Amara would anchor the model. ARMH's `<vn>` is not
*varga*-subdivided in the digitization (only the *kāṇḍa* and a running verse number vary), so
I model ARMH at *kāṇḍa* granularity and ABCH at *kāṇḍa*/*varga* granularity — a normalisation
the sources permit but do not yet expose uniformly. The gender figures count combined tags
toward each gender admitted, and the *kāṇḍa*-5 synonym density is reported as lexeme-density
for the reason given in §4.2. Finally, the model is structural; aligning the synonym-sets to
the European dictionaries' sense divisions — turning the lineage claim of §5 into a measured
edge set — is the natural next study, and the one that would convert the Wilson descent of
§2.1 from asserted lineage into a quantified inheritance rate.

## 7. Conclusion

The versified synonymic *kośa* is not a dictionary without structure; it is a dictionary that
is *only* structure. Its meaning lives in a concept-ordered *kāṇḍa*–verse–synonym hierarchy
that no European entry-measure can read, and that hierarchy is richly informative once
measured: it encodes a cosmology (Brahmanical in Halāyudha, Jain in Hemacandra), it
concentrates its mass in the human world, it peaks at fifty-six names for a single god, it
carries a complete gender apparatus, and it is transmitted intact across a textual tradition.
The two koshas' opposite digitizations make their entry-counts incommensurable — a warning
for any statistic that would sum them. The lesson is the book's lesson, raised one level: a
zero is a question about the instrument, and the architecture of the word-hoard is data.

## References

Baalbaki, Ramzi. 2014. *The Arabic Lexicographical Tradition: From the 2nd/8th to the
12th/18th Century.* (Handbook of Oriental Studies 1.107.) Leiden and Boston: Brill.

Hartmann, R. R. K., and Gregory James. 1998. *Dictionary of Lexicography.* London and New
York: Routledge.

Hausmann, Franz Josef, and Herbert Ernst Wiegand. 1989. "Component Parts and Structures of
General Monolingual Dictionaries: A Survey." In Hausmann, Reichmann, Wiegand and Zgusta
(eds.), *Wörterbücher / Dictionaries / Dictionnaires,* vol. 1 (HSK 5.1), 328–360. Berlin and
New York: Walter de Gruyter.

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.
[Ch. 12 on the European thematic/onomasiological tradition — Hüllen, McArthur.]

Partridge, Eric. 1963. *The Gentle Art of Lexicography.* London: Deutsch. [The alphabet as a
designed, imperfect compromise.]

Svensén, Bo. 2009. *A Handbook of Lexicography: The Theory and Practice of
Dictionary-Making.* Cambridge: Cambridge University Press.

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature, vol. V, fasc. 4,
ed. Jan Gonda.) Wiesbaden: Otto Harrassowitz.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.) Prague:
Academia; The Hague and Paris: Mouton.

### Primary sources

Halāyudha, *Abhidhānaratnamālā* (*Halāyudhakośa*), ~10th c.; Hemacandra,
*Abhidhānacintāmaṇi* with *-pariśiṣṭa*, ed. Śivadatta and Parab (Nirṇaya-sāgara Press,
Bombay, 1896); Jinadeva (attr.), *Abhidhānacintāmaṇi-śiloñcha*; Bhoja (attr.),
*Nāmamālikā* (NMMB, digitized 2026); Amarasiṃha, *Amarakośa* (*Nāmaliṅgānuśāsana*), as genre
comparandum. Wilson, Horace Hayman. 1819. *A Dictionary, Sanscrit and English.* Calcutta:
Hindoostanee Press (cited for the preface's account of the kośa-based compilation). All
dictionary texts consulted in the machine-readable editions of the **Cologne Digital Sanskrit
Dictionaries (CDSL)**, Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/); the
*sanskrit-kosha* digitization (Patel et al.).

_Dr. Mārcis Gasūns_
