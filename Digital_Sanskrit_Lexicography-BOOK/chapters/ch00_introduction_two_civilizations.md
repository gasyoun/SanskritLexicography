# Introduction — Two Lexicographic Civilizations, One Layered Graph

_Created: 18-07-2026 · Last updated: 18-07-2026_

> **Provenance.** Unlike the fourteen chapters, which are book-form versions of the
> author's journal articles, this Introduction is **new writing for the book**, drafted
> under the work order recorded in
> [BOOK_PLAN.md §3](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)
> and the A61 ruling of 18-07-2026
> ([BOOK_PLAN.md §10](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md)):
> it reworks the *argument* of the author's companion report on the Cologne project's
> history — why this dictionary family survived digitization — while leaving that report's
> institutional chronicle, testimony, and quotations entirely outside the book. Framing
> decisions open to the author's veto are listed in
> [SIGNOFF_M01_glue_framing_calls.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/SIGNOFF_M01_glue_framing_calls.md).
> Section numbering is chapter-internal; the book-wide renumbering and bibliography merge
> are a later production pass.

## 1. Two answers to one question

Ask two dictionaries what fire is.

Monier-Williams's *Sanskrit-English Dictionary* of 1899 answers with an entry: the
headword *agni*, a gender tag, a stack of numbered senses descending from the element to
the god to the digestive humour, and behind nearly every sense a string of abbreviated
citations reaching from the Ṛgveda to the law-books. The entry is a small argument. It
asserts that these senses exist, that they divide *here* and not there, that each is
attested in *these* texts, and — silently, in its typography and its order — that this is
how a word's meaning ought to be laid out for a reader.

The *Amarakośa*, composed perhaps thirteen centuries earlier, answers without any entry at
all. Fire stands in a verse, strung together with its synonyms — *vahni*, *agni*,
*pāvaka* and their kin — inside a section of the first book, among the gods and the
luminous things. There is no gloss, no citation, no grammatical tag visible to a European
eye. And yet the verse asserts everything the entry does, by other means: that these words
name one thing, that the thing belongs *here* in an ordered map of the world, and that the
educated reader will carry this map in memory, whole. The lexicographic act is the
placement.

These are not a primitive answer and a mature one. They are two complete, internally
coherent technologies for the same task — recording what words mean and on what authority
— developed by two lexicographic civilizations that met, late and asymmetrically, in the
nineteenth century, and that now sit side by side, machine-readable, in a single digital
corpus. This book is about what can be known, and how securely, when both are measured on
their own terms.

## 2. Two civilizations, one corpus

The first civilization is compact and well documented. Between 1832 and 1957 — from
Wilson's Calcutta dictionary to the revised Apte — European scholarship produced the
bilingual Sanskrit dictionaries that Indology still works with daily: the two Petersburg
lexica of Böhtlingk and Roth, Monier-Williams in two editions, Cappeller, Benfey,
Grassmann's Vedic concordance-dictionary, Schmidt's supplement, Apte on the English side
of the family. These are dictionaries in the fullest European sense: semasiological,
alphabetically ordered, sense-divided, citation-bearing — an apparatus of headwords,
glosses and source sigla whose direct ancestors are the classical philology of the same
century and whose house style the Petersburg school stamped on everything that followed.
They speak *about* Sanskrit in German, English, or — exactly where the matter turned
delicate — in Latin (Chapter 1).

The second civilization is neither compact nor, in the European sense, documented; it is
canonical. The indigenous Sanskrit tradition built its lexical record over roughly
nineteen centuries in two great genres: the versified synonymic *kośa* — the *Amarakośa*
and its successors — in which meaning is encoded by placement in a concept-ordered,
memorised text (Chapter 4); and the vast nineteenth-century Sanskrit-through-Sanskrit
prose lexica, the *Śabdakalpadruma* and the *Vācaspatya*, which fold the grammatical
tradition of Pāṇini into the dictionary itself — citing by quotation formula, deriving
headwords by rule, and encoding a verbal root's grammar in conventions a European
part-of-speech detector cannot even see (Chapters 7 and 8). This tradition speaks
Sanskrit *in* Sanskrit. It has no outsider to screen against, no bilingual reader to
serve, and no reason to distinguish dictionary from grammar in the European way.

The founding gesture of comparative metalexicography — Zgusta's programme of setting the
Western dictionary against its non-Western counterparts — supplies the frame this book
inherits (Zgusta 1980); the indigenous tradition itself has authoritative surveys in
Vogel's *Indian Lexicography* (1979) and Patkar's history (1981). But the two Sanskrit
civilizations have almost never been treated as *one object of measurement*. The European
dictionaries have been studied philologically, entry by entry; the kośas philologically,
verse by verse; and where the two meet — for they do meet: the kośa synonym-lists flow
through the Fort William pandits and Wilson into the very sense-columns of the European
dictionaries (Chapter 4) — the connection has been asserted far more often than counted.

What makes counting possible now is the corpus. The Cologne Digital Sanskrit Lexicon
(CDSL) holds forty-four dictionaries — European bilinguals in four gloss languages,
reverse bilinguals, specialised indices, and the great indigenous lexica — digitised in a
shared, lightly-marked source format, continuously corrected, and versioned in public.
Around it stand the resources that turn a text collection into an evidentiary system: a
union index of 323,425 headwords across the collection; a citation graph of 828,505
literary-source references resolving to 912 distinct texts; a twelve-year ledger of
52,498 documented corrections; and cross-links to the Digital Corpus of Sanskrit, the
only large morphologically disambiguated corpus of the language. Both civilizations,
one data structure. That conjunction — not any single dictionary, however great — is the
book's real subject.

## 3. Why Sanskrit is the testbed — the substrate that survived

A thesis about measuring dictionaries could, in principle, be tested on any digitised
dictionary family. It is worth stating exactly why this one — a corpus of Sanskrit
dictionaries maintained from Cologne — is the right testbed, because the reasons are not
decorative. They are the load-bearing preconditions of everything the following chapters
do, and each is rarer than it looks.

The first requirement is **breadth of the right kind**. An evidence model earns nothing
on a single dictionary; it needs a *family* — related works that inherit, condense,
contradict and cite one another — and ideally a family spanning more than one convention
system, so that the model is forced to say what it means by a "statement" when the
statement is a verse-placement rather than a numbered sense. The CDSL is precisely that:
two civilizations, half a dozen gloss languages, a century and a quarter of European
print (1832–1957, with digitised editions reaching back to 1822) and nineteen centuries
of indigenous depth, all in one markup convention.

The second requirement is **depth of attestation**. The evidence graph's corpus layer
needs a reference corpus that is lemmatised, morphologically disambiguated, and honestly
bounded; Sanskrit has one, and Chapter 2 §6 states once, for the whole book, what its
5.7 million tokens can and cannot witness.

The third requirement is the decisive one, and it is historical rather than structural:
**the substrate survived, and survived in a form that can carry evidence**. Digitised
historical dictionaries are not rare. Digitised historical dictionaries that are still
*maintained* — whose source files are corrected continuously, whose corrections are
themselves versioned, dated, attributed and public — are nearly unique, and the
distinction is everything for this book, because a dictionary's maintenance record is one
of the four annotation layers the thesis requires (§4). The Cologne collection is the
reference repository of digital Sanskrit lexicography not because it was first — an
earlier attempt at digitising the same material had already failed for lack of funding
before the Cologne project began in 1994 — but because it kept converting itself into
whatever infrastructural form survival required: from typed transcriptions verified by
redundant double-entry, through structural character codes, to XML, to a lossless
phonemic transliteration, to the current line-oriented source files keyed by stable
numeric entry identifiers, and — since 2014 — to openly versioned repositories where
every correction is a public, attributable event. Each conversion preserved the data
while replacing the technology around it.

The same history can be read as a controlled experiment in what survives. Over three
decades the project outlived the closure of the university department that founded it;
the loss of one of its architects, with whom the original interface code became
unbuildable — the code died, the data did not; and, most recently, the retirement of its
longest-serving maintainer. The asymmetry is the strategy: institutions and software are
fragile, but data that is versioned, forkable, licensed and mirrored is safe *by
construction*, recoverable by any future group with the will to continue. Meanwhile the
derivative websites that scrape the Cologne data illustrate the counterfactual: they
freeze a copy, strip the structural markup — beginning with the literary-source tags
that carry the citation apparatus, the collection's single most valuable evidentiary
asset — and drift silently out of date with every upstream correction they do not
receive. A frozen copy can serve a reader; only the maintained source can serve as
*evidence*.

That is the argument for the testbed, and it has a sobering converse which the book
states here once, plainly. Sanskrit lexicography still works, in substance, to
mid-nineteenth-century standards: the corpus revolution that remade European
lexicography — entries drafted from corpus evidence and verified against it — has not
yet reached it. The CDSL's corrected sources, stable identifiers and linked citations
are the *necessary substrate* for that transition, not the transition itself. This book
is written on the substrate, about the substrate, in the conviction that the transition
will be built — but no chapter of it claims the transition has happened.

## 4. The thesis: grading the statements

The book's organising claim can now be stated. **A digital dictionary is not a text but
a layered evidence graph.** Every lexicographic statement — a headword's existence, a
sense division, a gender assignment, a citation, a cross-reference, a register label —
is a node that carries, or should carry, four things: (a) its **source and convention**
— which dictionary asserts it, under which structural idiom, since a kośa verse-placement
and a numbered Monier-Williams sense are not the same kind of assertion and must not be
flattened into one; (b) an explicit **evidence grade** — in the vocabulary this book uses
throughout, `observed` (read directly off the source), `derived` (computed
deterministically from it), `inferred` (proposed by a model or heuristic), or `reviewed`
(ratified by a human); (c) **corpus attestation** where available — a bounded statement
about what a reference corpus witnesses, never more; and (d) **review provenance** — who
or what has examined the statement, when, and with what outcome.

Stated so, the claim invites a misreading that had better be blocked at once: the graph
part is not the news. That lexical resources can be modelled as graphs, that dictionaries
should be versioned with per-entry revision histories, that user communities can submit
and vote on corrections — all of this is established practice, stated as such in the
field's own current reference literature, emphatically including this book's series-mate
*Internet Lexicography* (Klosa-Kückelhaus 2024). Anyone claiming "the dictionary as a
graph" as a discovery in 2026 would be reinventing the encoding layer the field already
built. What the reference apparatus does *not* provide — not Hartmann and James's
*Dictionary of Lexicography*, where "evidence" appears only as an entry-level continuum
of source types; not Apresjan's systematic lexicography, which systematises what a
dictionary *says* rather than the evidential status of each thing said; not the
graph-and-versioning practice of the internet-lexicography literature — is an explicit,
machine-readable **evidence grade attached per statement**, with review provenance as a
first-class layer, applied across a whole dictionary family, and with an indigenous
lexicographic tradition entering the same graph as first-class structured data rather
than as exotic noise. Where existing standards and handbooks standardise the *encoding*
of dictionaries, this book standardises their *epistemics*. That is the delta, the whole
of it, and every chapter is a test of whether it can be done honestly at corpus scale.

The claim also takes a position, deliberately modest, in the field's oldest internal
debate. Metalexicography has asked for decades whether lexicography *has* a theory
(the question is posed in exactly that form in the Bloomsbury Companion; Piotrowski
2013), and its historiography records a discipline that professionalised its practice
faster than its epistemology (Bogaards 2013). This book does not offer a theory of
lexicography. It offers something smaller and, perhaps for that reason, usable: a theory
of the *evidential status of lexicographic statements*, with a measurement discipline
attached. In Hartmann and James's terms, it is dictionary *research* conducted at the
level of concreteness the field normally reserves for dictionary *making* (Hartmann and
James 1998). If a dictionary is simultaneously a record of a language and a reference
tool for a reader (Jackson 2002), this book is about the record half — about what kind
of record a dictionary is, and how good a record it can be shown to be.

Two structural commitments follow from the thesis, and the book's own vocabulary should
be located in the field's at the outset. The object decomposes along the canonical axes
of metalexicographic description — macrostructure, microstructure, mediostructure, and
the access and distribution structures around them (Hausmann and Wiegand 1989; codified
in Hartmann and James 1998) — and the book's five parts walk those axes in order:
traditions and method (Part I), the shape of the word-list (Part II), the interior of
the entry (Part III), the pointer and citation apparatus (Part IV), and the living
dictionary of labels and corrections (Part V). Second, the sense — the node on which
everything else hangs — is treated throughout as the *dictionary's assertion*, not as a
language-internal entity. Whether discrete senses exist in the language at all is a
genuinely open question in lexical semantics (the debate is surveyed in Lew 2013); the
graph takes no side, because it does not need one. It models what the dictionaries
*say*, grades the evidence for their saying it, and leaves the ontology of meaning to
those who study it.

## 5. What this book is not

Four scoping statements, each one paragraph, so that the reader knows the boundaries
before the measurements begin.

**It is production-side, not use-side.** Empirical research on dictionary *use* — who
looks words up, how, with what success — is a mature branch of metalexicography with its
own methods and its own handbook chapters (Nesi 2013; Pastor and Alcina 2013;
Müller-Spitzer and Wolfer 2014). This book contains no user study, and its claims about
structure and evidence imply nothing about look-up behaviour. The two programmes are
complementary: this one asks what the dictionaries assert and how well-evidenced the
assertions are; the use-research programme asks what readers manage to extract. A
complete science of the dictionary needs both; only the first is attempted here.

**It is function-agnostic.** The function-theoretic school rightly insists that a
dictionary is a tool designed for specific user situations, and that its content is
answerable to those functions (Fuertes-Olivera 2013; Nielsen 2013). The evidence graph
sits deliberately *below* that level: whatever function a dictionary serves — text
reception, translation, learning, historical documentation — the evidential status of
its statements is prior to, and independent of, the use to which they are put. A graded,
provenance-bearing record can be consumed by any function theory; it presupposes none.

**It treats the bilingual dictionaries as evidence sources, not as objects of
equivalence theory.** Most of the European half of the family is bilingual, and
bilingual metalexicography has its own central problem — the nature of interlingual
equivalence (Adamska-Sałaciak 2013). That problem is not engaged here. When this book
reads Monier-Williams or Apte, it reads them as structured records of assertions about
Sanskrit — headwords, senses, citations, labels — not as attempts to map Sanskrit onto
English, and nothing below depends on a theory of what a "good equivalent" is.

**It measures the dictionaries, not the project.** There is a worthwhile programme that
quantifies digital-edition *projects* — repository health, contributor activity,
workflow throughput. This book keeps that programme entirely outside its boundary
(Chapter 2 states the rule and polices it): every object measured below is a property of
the dictionaries as texts — their headwords, senses, citations, cross-references,
structures — and none is a property of the workflow that digitised them. For the same
reason, the institutional history of the Cologne project — who did what, when, and how
it was funded — is documented elsewhere and deliberately absent here; §3 took from that
history only its argument, because the argument, unlike the chronicle, bears on whether
the testbed can carry the thesis.

## 6. The instrument, in one page

The thesis needs an instrument, and the instrument is stated once, in full, in
Chapter 2. Its shape is worth one paragraph here.

Everything measured in this book passes through three disciplines. A **metric catalog**
defines each estimator operationally — what it measures, on which dictionaries it is
even meaningful, and what it is a floor or a ceiling for — because a family this
heterogeneous punishes any metric that silently assumes the European entry shape. A
**traceability discipline** makes every published number walkable back to the dictionary
line that produced it: every artifact ships with its assumptions and warnings, every
datum carries an evidence grade, and — the framework's hardest rule — no model inference
contributes to a published figure; a neural cross-check may propose, but only a
deterministic parse or a human ratification can assert. And a **routing discipline**
keeps every claim falsifiable and inside its bounds, under one governing commitment:
every claim is a `Claim → Evidence → Source` path, and the machine only ever proposes —
a human ratifies before anything touches the canonical text.

Three reading rules recur so often that the reader should carry them in from the start.
**Containment is a floor**: a large dictionary contains a small one's word-list
regardless of descent, so overlap alone never proves copying (Chapters 2, 9, 12).
**A zero is a question about the instrument**: when a European-style detector scores an
indigenous lexicon at zero, it has measured the absence of a convention, not of content
— the single most consequential methodological fact in the book (Chapters 4, 7, 10).
And **corpus absence is a coverage statement**: every "unattested" figure is a bounded
claim about one 5.7-million-token corpus, never about the Sanskrit language — the rule,
its reasons, and the statistical practice that accompanies it are fixed once in
Chapter 2 §6 and cited thereafter, not restated.

## 7. The shape of the book

**Part I — Two traditions, one method** — opens both stories the book tells. Chapter 1
is the historical door into the European civilization, through its most human habit: the
Latin discretion-screen, by which the Petersburg school and its heirs kept their
dictionaries complete and "decent" at once, glossing the obscene in a language that
filtered its readership. It is at once an origin story — how these dictionaries were
made, read, and self-censored — and the book's method in miniature, since counting the
screen honestly requires scoring each gloss against its own dictionary's register rather
than counting raw Latin. Chapter 2 then states the measurement framework entire: the
estimators, the traceability and routing disciplines, and the bounded-witness rule for
the corpus. Everything later leans on it.

**Part II — Macrostructure: the shape of the dictionary** — asks what a dictionary *is*
at the level of its word-list. Chapter 3 takes the European answer — the headword
inventory — and measures its coverage and growth across the collection and against the
corpus: which words the dictionaries record, how the record grew, and what fraction of
it the corpus can currently see. Chapter 4 takes the indigenous answer and shows that
the versified kośa is a dictionary that is *only* macrostructure — meaning encoded
purely in placement — and models that structure on its own terms, as the upstream end of
the very sense-lists the European dictionaries inherited.

**Part III — Microstructure: inside the entry** — crosses into the entry. Chapter 5
anatomises the European entry at full depth on the corpus's largest dictionary,
Monier-Williams, deriving a grounded five-construct framework and triangulating it
against three metalexicographic traditions. Chapter 6 takes the entry's most contested
component — the sense — and shows that both its granularity and its ordering are traits
of lexicographic *school*, not functions of the calendar. Chapters 7 and 8 then do for
the indigenous entry what 5 and 6 did for the European: Chapter 7 recovers the rich
verbal-root grammar hidden in conventions European detectors cannot see, and Chapter 8
measures Pāṇinian derivation across ten lexica, finding a tradition consistent enough to
agree on the derivational affix in over nine cases in ten.

**Part IV — Mediostructure and the citation apparatus** — turns to the pointers.
Chapter 9 reads the dictionaries' internal cross-reference graphs as a calibrated,
convention-cleaned signal of descent — the systematic mediostructural study the field's
own reference work says is still to be developed. Chapter 10 shows that the collection
holds two disjoint citation systems — the European tagged apparatus and the indigenous
*iti*-quotation — and that no citation statistic is well-defined until the register is
named. Chapter 11 maps what the tradition actually cites: the citation-frequency graph
over the largest citation dataset in Sanskrit lexicography. Chapter 12 closes the
descent argument forensically: Monier-Williams inherited the Petersburg *apparatus* —
inventory, citations, their very order — but not its errors and not its prose; heir of
the scholarship, author of the prose.

**Part V — The living dictionary** — reads the layers that keep a dictionary alive.
Chapter 13 operationalises Renou's register subsections as a second, orthogonal
annotation axis — register, not just period — and in doing so maps the boundary of what
the corpus can witness. Chapter 14 reads twelve years and 52,498 events of collaborative
correction as the review-provenance layer itself: where curatorial attention went, what
it repaired, and why a correction record measures the community's care rather than the
dictionary's badness.

The **Conclusion** then argues the general case: the evidence graph as a model for any
dictionary family, the FAIR infrastructure it requires, and what the two civilizations,
measured together, teach lexicography at large.

## 8. Conventions

Dictionaries are cited by their CDSL sigla — MW (Monier-Williams 1899; MW72 for 1872),
PWG and PW (the larger and shorter Petersburg lexica), AP90 and AP (Apte 1890 and the
1957 revision), SKD (*Śabdakalpadruma*), VCP (*Vācaspatya*), GRA (Grassmann), SCH
(Schmidt), and so on; each chapter glosses the sigla it uses at first mention. Sanskrit
is romanised in IAST in prose; the underlying data uses the SLP1 phonemic
transliteration, and conversions are lossless. Quantitative claims are tied to committed,
versioned artifacts in the project's public repositories, cited at the point of use;
"the corpus" always means the pinned Digital Corpus of Sanskrit snapshot disclosed in
Chapter 2 §6. Section numbers are chapter-internal; cross-references name the chapter.
Each chapter descends from a journal article recorded in its provenance note and remains
independently citable in that form; the articles and the book cite each other under the
disclosure recorded in the proposal.

## References

Adamska-Sałaciak, Arleta. 2013. "Issues in Compiling Bilingual Dictionaries." In *The
Bloomsbury Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Apresjan, Jurij D. 2000. *Systematic Lexicography.* Trans. Kevin Windle. Oxford: Oxford
University Press.

Bogaards, Paul. 2013. "A History of Research in Lexicography." In *The Bloomsbury
Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Fuertes-Olivera, Pedro A. 2013. "E-lexicography: The Continuing Challenge of Applying
New Technology to Dictionary Making." In *The Bloomsbury Companion to Lexicography,* ed.
Howard Jackson. London: Bloomsbury.

Hartmann, R. R. K., and Gregory James. 1998. *Dictionary of Lexicography.* London and
New York: Routledge.

Hausmann, Franz Josef, and Herbert Ernst Wiegand. 1989. "Component Parts and Structures
of General Monolingual Dictionaries: A Survey." In Hausmann, Reichmann, Wiegand and
Zgusta (eds.), *Wörterbücher / Dictionaries / Dictionnaires,* vol. 1 (HSK 5.1), 328–360.
Berlin and New York: Walter de Gruyter.

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.

Klosa-Kückelhaus, Annette (ed.). 2024. *Internet Lexicography.* (Lexicographica. Series
Maior 164.) Berlin and Boston: De Gruyter. [Graph data models, versioning, user
participation as established practice; the encoding layer this book's epistemics sits
on.]

Lew, Robert. 2013. "Identifying, Ordering and Defining Senses." In *The Bloomsbury
Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Müller-Spitzer, Carolin, and Sascha Wolfer. 2014. "Dictionary Users — Empirical Data on
Dictionary Use." In *Internet Lexicography.*

Nesi, Hilary. 2013. "Researching Users and Uses of Dictionaries." In *The Bloomsbury
Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Nielsen, Sandro. 2013. "The Function Theory of Lexicography." In *The Bloomsbury
Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Pastor, Verónica, and Amparo Alcina. 2013. "Researching the Use of Electronic
Dictionaries." In *The Bloomsbury Companion to Lexicography,* ed. Howard Jackson.
London: Bloomsbury.

Patkar, Madhukar Mangesh. 1981. *History of Sanskrit Lexicography.* New Delhi:
Munshiram Manoharlal.

Piotrowski, Tadeusz. 2013. "A Theory of Lexicography — Is There One?" In *The Bloomsbury
Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature, vol. V,
fasc. 4, ed. Jan Gonda.) Wiesbaden: Otto Harrassowitz.

Zgusta, Ladislav. 1980. *Theory and Method in Lexicography: Western and Non-Western
Perspectives.* Columbia, SC: Hornbeam Press.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/); source
repositories of the [sanskrit-lexicon](https://github.com/sanskrit-lexicon) GitHub
organisation. Corpus: Oliver Hellwig, *DCS — The Digital Corpus of Sanskrit* (2010–),
per the disclosure in Chapter 2 §6.

_Dr. Mārcis Gasūns_
