# Conclusion — The Evidence Graph as a General Model

_Created: 18-07-2026 · Last updated: 18-07-2026_

> **Provenance.** Like the Introduction, this Conclusion is **new writing for the book**
> under
> [BOOK_PLAN.md §3](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/BOOK_PLAN.md);
> vetoable framing calls listed in
> [SIGNOFF_M01_glue_framing_calls.md](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/SIGNOFF_M01_glue_framing_calls.md).
> Section numbering is chapter-internal; the book-wide renumbering and bibliography merge
> are a later production pass.

## 1. What the probes established

The Introduction promised a book of probes: every chapter a quantitative sounding into
one structural layer of a two-civilization dictionary corpus, under one discipline. The
findings are each chapter's to state in full; what belongs here is the pattern they make
when laid side by side — five lessons that recurred until they stopped looking like
findings and started looking like properties of the object.

**The school beats the calendar.** Where the received story expects historical drift —
senses inflating over time, order following chronology — the measurements found
*tradition*: sense granularity is a family trait, flat to declining across a century of
descent; sense order is genetic in the philological school and salience-driven in the
pedagogical one; the entry's block-anatomy is an economy imposed by the single-volume
form. The dictionary family behaves less like a sediment accumulating by year and more
like a set of schools, each reproducing its own design.

**A zero measures the instrument.** The single most consequential methodological fact in
the book appeared at every structural level: the great indigenous lexica score zero on
European detectors of microstructure (Chapter 7), of entry-hood itself (Chapter 4), and
of citation (Chapter 10) — and every one of those zeros dissolved under an instrument
built for the convention actually in use, revealing a complete grammar, a total
macrostructure, and one of the corpus's densest citation practices. The doctrine — zero
means the absence of a convention, never of content — is this book's chief export to
anyone who would measure a heterogeneous textual tradition.

**No statistic before the register.** Twice the corpus proved to contain two systems
where one was assumed — citation (the tagged apparatus against the *iti*-quotation) and,
inside the European half, the two metalanguages of candour Chapter 1 measured. In each
case a per-dictionary statistic was not merely inaccurate until the register was named;
it was *undefined*. Convention is a variable, and every honest number in this book
carries its convention with it.

**Descent decomposes.** The relatedness of the family — asserted for a century and a
half — survived measurement, but only by being taken apart. Containment is a floor;
pointer-graph overlap needs a positive control and a convention subtraction; and the
strongest inheritance claim in Sanskrit lexicography resolved into a three-part verdict
— apparatus inherited, prose original, errors not shared — that no single similarity
score could have expressed. The airtight stemmatic coup, a shared error, was measured to
its null: the apparatus Monier-Williams inherited was accurate enough to leave no error
to share. Inheritance is real, layered, and gradeable — which is the only way a truism
becomes knowledge.

**Attention, not error rate.** The living layers read the same way. A register label
maps the boundary of what the corpus can witness; a correction record maps where the
community chose to look. Both are evidence about the *system of observation* as much as
about the object — and treating them so, rather than as verdicts on the language or the
lexicographers, is what kept the book's largest datasets inside their bounds.

Beneath all five runs the two-civilizations verdict the book set out to test. Measured
on their own terms, the indigenous kośa and Pāṇinian lexica are not a picturesque
prelude to scientific lexicography; they are a mature, internally consistent
lexicographic technology — agreeing on their derivational layer at rates above ninety
percent, carrying complete grammatical and citation apparatus in conventions of their
own, and organising meaning by a principle the European tradition also possesses but
never pushed as far. The European dictionaries, for their part, emerge not diminished
but *specified*: their genius is the locator — the addressable, resolvable, auditable
citation — and the disciplined entry economy, and both are exactly the properties a
digital evidence layer needs most. Two technologies, each carrying half of what a
layered evidence graph requires: one the semantics of placement and the
grammar-integrated entry, the other the address system. The book's measurements are the
first in which they function as a single evidentiary system.

## 2. The graph, generalised

The evidence graph can now be restated as what the fourteen chapters have made of it: a
tested model, not a proposal. Its content is four annotations on every lexicographic
statement — source and convention; an evidence grade (`observed`, `derived`, `inferred`,
`reviewed`); corpus attestation, bounded; and review provenance — and its discipline is
the one Chapter 2 fixed: every claim a `Claim → Evidence → Source` path, machine
proposing, human ratifying, no model inference in a published figure.

Nothing in that statement is Sanskrit-specific, and the transfer conditions can be
stated exactly, because the book has been living on them. A dictionary family can carry
an evidence graph when three things hold. **Canonical, versioned sources**: the texts
are held in one corrected line of record, so that a claim has a stable target to be a
claim *about* — the property the Cologne collection's serial self-conversions preserved
and the derivative scrape-sites lost. **Stable statement addresses**: entries (and
ideally sub-entry structures) carry identifiers that survive correction, so that
evidence and review can accumulate *on* a statement across years. **A review gate**:
some human process ratifies machine proposals before they touch the record, so that the
`reviewed` grade means something. Breadth of convention — a family spanning more than
one structural idiom — is not a precondition but a stress test: it is what forced this
book's instrument to say precisely what it meant by a statement, and any transfer to a
comparably heterogeneous tradition (the Arabic lexicographical corpus is the obvious
candidate) would be forced the same way, to the same benefit.

The model's epistemic ambition should be restated with equal care, because the corpus
conditions of this book are the *normal* conditions of historical languages. The
reference corpus behind every attestation claim here is one to two orders of magnitude
below the size at which corpus lexicography operates; it has no sampling frame; its
frequency structure makes absence the statistical default. Chapter 2 §6 turned those
facts into a rule — every absence figure is a statement about coverage, phrased so and
bounded so — and thirteen chapters then showed the rule to be livable-with: differential
absence mapped register geography, corpus holes became measured boundaries, and not one
claim needed the corpus to testify beyond its competence. That is the general lesson for
digital philology in small-corpus conditions: the choice is not between corpus evidence
and none, but between bounded corpus statements and unbounded ones, and only the first
kind survives review (McEnery and Brezina 2022).

## 3. The infrastructure the graph requires

A model of graded evidence is only as good as the data infrastructure beneath it, and
the book should close its own loop on that point honestly.

What the graph requires is, in current vocabulary, FAIR data — findable, accessible,
interoperable, reusable (Wilkinson et al. 2016) — but required at a granularity the
deposit-level FAIR literature rarely reaches: per statement, per artifact, per revision.
The book's working practice already operates at that granularity — every published
figure walks back to a committed, licensed, assumption-carrying artifact; every
correction is a dated, attributed event; the maintenance ledger is itself a released
dataset — and the enveloped artifact is, in effect, a minimal machine-readable data
statement. What the practice still lacks, at the time of writing, is the *findability*
half at institutional grade: persistent identifiers minted for the datasets the book
cites, deposited in an archival repository rather than a repository host. That gap is
infrastructure, not method — the deposits are prepared, and nothing in the analyses
depends on it — but a book about evidence should name its own weakest evidence-layer,
and this is it.

Two further infrastructure lessons follow from the measurements themselves. First,
**addressability is the multiplier**. The dictionary-to-book gap Chapter 10 measured —
half a million citations that name a work but not a place — is exactly the difference
between a citation as decoration and a citation as an edge; and the same holds one level
up, where a stable per-entry address is what lets every external resource that quotes a
Sanskrit word become an inbound link to the maintained record rather than to a frozen
copy. An evidence graph is only as connectable as its nodes are addressable. Second,
**verification does not scale by machine alone**. The corpus and alignment resources now
available would permit generating lexicographic statements wholesale; the book's own
discipline — `inferred` is a grade, not a publication — marks the boundary. A generated
statement without a review path is not cheap evidence; it is deferred liability. The
scaling path that remains consistent with everything measured here is the one the
correction ledger already instantiates in miniature: distributed human verification,
recorded as provenance, on addressable statements — the reader-and-slip method of the
great historical dictionaries (Jackson 2002), re-founded on a versioned substrate.

## 4. What the two traditions teach lexicography at large

A comparative book owes the field a statement of what travels. Four lessons, two from
each civilization, and a fifth they teach jointly.

From the indigenous tradition, first, the **semantics of placement**: a lexicographic
statement need not be a sentence in a metalanguage — position in a designed structure
can assert meaning, register and relation at once, and can do so with a durability
(nineteen centuries of intact transmission) that no prose gloss has matched. Modern
structured lexicography, which increasingly *is* placement — a node in a schema — has
more to learn from the kośa's discipline than its designers suspect. Second, the
**integrated entry**: the indigenous entry presupposes the grammar and is organised by
it, root before word, derivation as analysis — the integration the Moscow school argued
for on theoretical grounds (Apresjan 2000) and the Arabic tradition institutionalised
(Baalbaki 2014), here practiced at corpus scale and measurably consistent across
independent compilers.

From the European tradition, first, the **address**: the tagged, locator-bearing
citation — the Petersburg school's real bequest, inherited entry by entry and order by
order into Monier-Williams — is the single feature that makes a dictionary auditable at
scale, and it is the property every digital evidence layer should prize above prose.
Second, the **marked boundary of evidence**: the hedge by which the family's largest
dictionary flags a word it records but cannot attest is evidence-grading avant la
lettre — proof that the tradition's own best practice already understood the difference
between recording a claim and vouching for it.

Jointly, the two traditions teach the lesson the comparative bridges traced through the
Arabic, Latin and Greek civilizations as well: the deep problems of lexicography —
retrieval against semantic map, who counts as a witness and until when, how inheritance
is practiced and acknowledged — are civilizational constants, solved repeatedly,
independently, and *theorised* by the traditions themselves (Baalbaki 2014). The
evidence-graded model this book proposes is therefore best understood not as an import
of scientific method into a humanistic field, but as the digital continuation of what
mature lexicographic civilizations have always done: state, as explicitly as their
technology allowed, why the reader should believe the dictionary. What the digital
substrate adds is that the statement can now be made per claim, kept under version, and
audited by anyone.

## 5. The honest close

A book whose thesis is graded evidence must grade its own. What this book has
established, it has established as measurements under stated bounds: the school-trait
findings, the two-register findings, the descent decomposition, the coverage
geometries — each walkable to a committed artifact, each carried with its confounds
disclosed. What it has *not* established should be equally explicit. The `reviewed`
grade — the model's crown — rests, at the time of writing, on a review practice whose
inter-annotator reliability is unmeasured, because the reviewer pool has effectively one
member; recruiting the second annotator is the single most consequential next step for
the framework's credibility, and no rhetorical confidence can substitute for it. The
inferred tiers that some chapters carry — model-proposed roots, machine-mapped
traditions — remain `inferred`, awaiting the review gate they were built to feed. And
the corpus's unlabelled holes remain invisible by construction: the bounded-witness rule
maps the boundaries a label exposes, and cannot map the ones nothing exposes.

The direction of travel, though, is not in doubt. The futures the e-lexicographic
literature projects — dictionaries as continuously revised data services, user
communities as contributors, the dictionary dissolving into the language infrastructure
around it (Fuertes-Olivera 2013; Nielsen 2013; Klosa-Kückelhaus 2024) — all presuppose
exactly what this book has been building and testing: a substrate on which statements
are addressable, evidence is graded, and review is provenance. For Sanskrit, the
programme has a concrete horizon that has waited a long time: a community-validated
dictionary of record — the scattered, perishable correction-lore of individual readers
centralised, verified and preserved on the maintained substrate this family, alone among
its peers, still possesses. The corpus revolution that remade European lexicography has
not yet reached Sanskrit; the infrastructure for it now exists, and this book has tried
to show, claim by graded claim, that the two civilizations that built the record can
carry it.

A dictionary, this book began by saying, is not a text but a layered evidence graph.
The fourteen chapters have measured what that means when it is taken seriously: senses
and screens, verses and blocks, pointers and citations, labels and repairs — every one
of them a human decision, every one of them now a graded, sourced, reviewable statement.
The two civilizations that meet in this corpus each spent centuries teaching their
readers why the dictionary should be believed. The evidence graph is the same lesson,
taught to machines — and through them, once more, to readers.

## References

Apresjan, Jurij D. 2000. *Systematic Lexicography.* Trans. Kevin Windle. Oxford: Oxford
University Press.

Baalbaki, Ramzi. 2014. *The Arabic Lexicographical Tradition: From the 2nd/8th to the
12th/18th Century.* (Handbook of Oriental Studies 1.107.) Leiden and Boston: Brill.
[Including the Epilogue's cross-civilizational reading of the ordering trade-off.]

Fuertes-Olivera, Pedro A. 2013. "E-lexicography: The Continuing Challenge of Applying
New Technology to Dictionary Making." In *The Bloomsbury Companion to Lexicography,* ed.
Howard Jackson. London: Bloomsbury.

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.

Klosa-Kückelhaus, Annette (ed.). 2024. *Internet Lexicography.* (Lexicographica. Series
Maior 164.) Berlin and Boston: De Gruyter.

McEnery, Tony, and Vaclav Brezina. 2022. *Fundamental Principles of Corpus Linguistics.*
Cambridge: Cambridge University Press.

Nielsen, Sandro. 2013. "The Function Theory of Lexicography." In *The Bloomsbury
Companion to Lexicography,* ed. Howard Jackson. London: Bloomsbury.

Wilkinson, Mark D., et al. 2016. "The FAIR Guiding Principles for scientific data
management and stewardship." *Scientific Data* 3: 160018.

_Dr. Mārcis Gasūns_
