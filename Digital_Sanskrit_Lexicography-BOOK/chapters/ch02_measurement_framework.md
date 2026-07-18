# Chapter 2 — The Measurement Framework: Measuring the Dictionary Family

_Created: 09-07-2026 · Last updated: 18-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Measuring the
> Dictionary Family: A Traceable Measurement Framework for Computational Lexicography*
> (source draft:
> [paper_measurement_framework.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_measurement_framework.md)),
> which is being published separately in a journal version; where the article must remain
> independently citable, cite that version. Every figure and measured number below is
> carried over from the article unchanged; only the framing has been converted from
> journal to book form — with one exception: **§6, *The corpus as a bounded witness*, is
> book-only new writing** with no counterpart in the journal article, added 17-07-2026
> under the corpus-methods ruling of 13-07-2026
> ([LITERATURE_CROSSWALK.md §4.2](https://github.com/gasyoun/SanskritLexicography/blob/master/Digital_Sanskrit_Lexicography-BOOK/LITERATURE_CROSSWALK.md));
> its figures are carried unchanged from the committed corpus artifacts cited in place.
> Section numbering is chapter-internal (§1–§10); the book-wide renumbering and
> bibliography merge are a later production pass.

The Introduction stated this book's thesis: a digital dictionary is not a text but a
**layered evidence graph**, in which every lexicographic statement — headword, sense,
gender, citation, cross-reference — is a node carrying its source dictionary and
convention, an explicit evidence grade, corpus attestation where available, and review
provenance. This chapter supplies the methodological spine that makes the thesis
operational. Every later chapter of the book is a quantitative probe into that graph
from one structural angle; this chapter states, once, the instrument those probes share —
what each metric means, what it is a floor or a ceiling for, and how a reader can walk
any published number back to the dictionary line that produced it. Its closest companion
is Chapter 5, which turns the framework's microstructural estimators on a single
dictionary — the entry anatomy of Monier-Williams — at full depth.

## 1. Introduction

When a project sets out to quantify a family of related digital dictionaries, it quickly
accumulates a toolkit: a measure of how much two word lists overlap, a count of how finely
an entry divides its senses and how many survive into a descendant, a test of how many of
a dictionary's source citations can be resolved to a real locus, a comparison of how two
dictionaries organise an entry. Each of these is implemented as a script, emits an
intermediate file, and feeds a figure or a table. The toolkit is the real instrument of
the work — dictionary *production* has long had a codified counterpart in practical
lexicography (Atkins and Rundell 2008); dictionary *measurement* has not — but it is
usually left implicit, scattered across a results section and a code repository, with no
single statement of what each metric *means*, how it is computed, what it is a floor or a
ceiling for, and how a reader could walk a published number back to the dictionary line
that produced it.

This chapter makes that instrument explicit. It describes the measurement framework
behind an evidence atlas of the Cologne Digital Sanskrit Lexicon (CDSL), a corpus of 44
digitised dictionaries (as of the committed 2026-07 measurement envelope) whose digitised
print editions span 1832–1993 — first publications reach back to 1822, for the
Śabdakalpadruma — and presents it as a reusable methodology rather than a one-off. The
framework has three layers — a catalog of metrics (§3), a traceability discipline that
makes each metric publishable and re-checkable (§4), and a routing discipline that keeps
claims falsifiable and inside their bounds (§5) — and one governing commitment, stated
once here and assumed everywhere in this book: **every claim is a traceable
`Claim → Evidence → Source` path, and an automated measurement only proposes; a human
ratifies before anything is written back to the canonical text.** To the three layers
this book adds one standing disclosure, stated once and thereafter cited rather than
restated: §6, *The corpus as a bounded witness*, fixes what the reference corpus behind
every attestation claim can and cannot testify to, and the statistical practice every
quantitative chapter follows. §7 then walks a single inheritance edge through the three
layers on real data.

**This is not a measurement framework for the *project*.** A well-known and worthwhile
programme — quantifying the *production* of a digital edition through repository-health
KPIs, contributor activity, and data-richness typologies — is sometimes called a
"measurement framework for digital lexicography." That programme measures the project;
this one measures the dictionaries. They are different research objects with different
homes, and conflating them is exactly the boundary error this framework's routing layer
(§5) exists to prevent. Everything below concerns the dictionaries as research objects —
their headwords, senses, citations, cross-references, and microstructure — and nothing
concerns the workflow that produced them.

## 2. The measurement object

The unit of study is the **dictionary as a structured text**, and below it the *entry*,
*headword*, *sense*, *citation*, *cross-reference*, and *microstructural block*
(microstructure in Wiegand's (1989) sense). The CDSL serves each dictionary as a
line-oriented, lightly-marked source file (`<L>…<LEND>` entries, `<k1>` headwords, `<ls>`
source citations, `<lex>`/`<ab>` grammatical marking, kośa `<syns>` synonym sets), and
every estimator below reads those source files directly. Two properties of the object
shape the whole framework.

First, the family is **heterogeneous**. It runs from richly-tagged European dictionaries
(Monier-Williams, the Petersburg lexica) through reverse bilinguals (Apte
English–Sanskrit) to indigenous prose lexica and versified synonymic kośas that carry
*no* European microstructure — no part-of-speech tag, no source siglum, no numbered
sense. A metric that assumes the European entry shape silently mis-measures the
indigenous half; the catalog therefore states, per metric, which dictionaries it can
speak about.

Second, the source files are **canonical and external**: corrections belong upstream in
the CDSL, not in the atlas. This forces the framework's defining move — the atlas never
writes to the source; it *proposes* review items that a human ratifies before any
upstream change. Measurement here is advisory by construction.

## 3. The metric layer

Each metric is defined once, with a uniform shape — **Definition · Estimator · Output ·
Limits** — and then reused by the empirical chapters, which supply the worked results.
Every row already has a generator under `scripts/`, a committed artifact, and at least
one finding routed through the project's hypothesis index. Numbers below are illustrative
anchors from the committed data, not the chapters' full results.

### 3.1 Headword overlap (content floor)

- **Definition.** How much of one dictionary's word list another carries; the *content*
  relationship between two dictionaries.
- **Estimator.** Normalise headwords to a comparison key (accent-, gender-,
  homonym-folded); report the symmetric Jaccard *and* both directed containments |A∩B|/|A|
  and |A∩B|/|B| over the key sets.
- **Output.** Per-pair `intersection, union, jaccard, a_in_b, b_in_a, size_a, size_b`
  (e.g. Apte 1890 × 1957: J = 0.269, with the 1890 list 76 % contained in the 1957 one) —
  per the committed artifact
  [`data/dicts/pairwise-overlap.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/pairwise-overlap.json).
- **Limits.** Containment is **size-confounded** — a large descendant contains a small
  ancestor regardless of descent — so overlap is a *floor* for relatedness, never on its
  own proof of copying. This single rule governs every descent reading in the book.

### 3.2 Redundancy and entry→lemma collapse

- **Definition.** How much of the family's headword stock is repeated across dictionaries
  versus structurally novel.
- **Estimator.** Count raw `<L>` entries (plus kośa `<syns>` members) and distinct
  normalised lemmas corpus-wide; report the collapse ratio and the per-dictionary unique
  fraction.
- **Output.** 1,496,157 entries → 410,259 distinct lemmas (≈3.65 : 1), per the committed
  artifact
  [`data/obs/headword_collapse.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/headword_collapse.json);
  the redundancy is *structured* — general dictionaries mutually derivative, specialised
  and indigenous lexica novel.
- **Limits.** A shared headword is independent attestation in each dictionary, not
  necessarily a copy; the unique fraction is a floor for novelty, not a count of
  independent invention.

### 3.3 Sense granularity and survival

- **Definition.** How finely an entry divides meaning — the classical sense-division
  problem (Zgusta 1971) — and whether a cited ancestor sense persists into a descendant.
- **Estimator.** Count senses per lemma on a convention-respecting split (numbered markers
  where present, semicolon/inline proxies elsewhere); for survival, gloss-overlap of an
  ancestor sense against the descendant entry above a stated threshold, refit under
  controls (centrality, lemma-cluster-robust errors, edge fixed effects).
- **Output.** Granularity is a **family/marking-style** trait, not a date effect
  (within-family it declines, not inflates); naive cited-sense survival (0.762 vs 0.705)
  is citation-concentrated rather than robust — the citation signal rides on a single
  citation-bearing edge, and within that edge the gap is suggestive but not significant
  (two-sided *p* ≈ 0.07) — per the committed panel
  [`data/lexico/r2_h2_senses.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h2_senses.json).
- **Limits.** Gloss-overlap measures gloss persistence on one display language; the
  threshold must be swept; granularity proxies are validated only to ±13 % of an archived
  baseline.

### 3.4 Citation registers and `<ls>` resolvability

- **Definition.** Whether a dictionary cites through the European tagged-source apparatus
  (`<ls>`) or the indigenous quotative (`iti …`), and what fraction of citations resolve
  to a locus.
- **Estimator.** Count `<ls>` citations and the fraction bearing a resolvable locator;
  separately count indigenous `iti` citations; never pool the two registers.
- **Output.** 1,245,644 `<ls>` citations, 59.3 % locator-bearing (upper bound on
  resolvability); the kośas cite densely through `iti` (word-boundary `iti`/`ity` hits:
  SKD 80,164 / VCP 15,619 / KRM 12,359) at *zero* `<ls>` — all per the committed artifact
  [`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json).
  An `<ls>`-only measure mis-ranks the kośas as citation-poor.
- **Limits.** A locator is necessary, not sufficient, for resolution; the `iti` count is
  an upper bound (it includes grammatical and quotative uses).

### 3.5 Citation-link resolvability (dictionary-to-book)

- **Definition.** Whether an explicit-locus citation can be turned into a stable
  digital-edition link.
- **Estimator.** Parse the locus, validate it against the cited work's known structure,
  and resolve to a canonical edition URL; reject loci that fall outside the structure.
- **Output.** Of 15,916 Ṛgveda `<ls>` citations in Monier-Williams, 5,682 are verse-level
  (most of the rest cite at work level); these yield 3,942 distinct verse loci linking to
  VedaWeb, while a per-hymn stanza table rejects 60 citations whose verse exceeds the
  cited hymn (broken links the structure check catches) — per the committed artifact
  [`data/review/citation-link-pilot-review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/citation-link-pilot-review.json).
- **Limits.** A structurally valid locus is *possible*, not *correct*; the atlas proposes
  the link and a human ratifies it (§4).

### 3.6 Cross-reference graph overlap

- **Definition.** Whether two dictionaries' internal cross-reference graphs share directed
  edges — a descent signal independent of shared headwords.
- **Estimator.** Extract `<ls>`/cross-reference edges; on the shared-source sub-graph
  report directed inheritance rates and Jaccard, separating prefix-convention hub
  artifacts into controls.
- **Output.** Apte 1890 × 1957: 182 shared edges, J = 0.74, ≈85 % mutual inheritance
  (edition-continuity positive control); Monier-Williams × the large Petersburg dictionary
  (PWG): J = 0.069 (a shared core, not wholesale descent) — per the committed artifact
  [`data/dicts/xref-lineage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/dicts/xref-lineage.json).
- **Limits.** A shared edge is a lineage signal, not proof of copying; pairs with few
  shared source lemmas are not interpretable.

### 3.7 Structural register

- **Definition.** A two-axis position — citation style × grammar-marking style — that
  separates dictionary families.
- **Estimator.** Join the all-dictionary coverage layer with the microstructure
  fingerprint; emit one chart row per dictionary with citation-register mode and grammar
  percentage, against a curated family label.
- **Output.** Citation style plus grammar marking separates traditions; the European,
  indigenous-prose, index-catalogue, reverse-bilingual, and specialised families occupy
  distinct regions — per the committed coverage layer
  [`data/dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json).
- **Limits.** The family label is an interpretation aid, not proof of descent; register
  can reflect genre or detector coverage rather than lineage.

### 3.8 Microstructure fingerprint

- **Definition.** The macro/micro trade-off — whether a dictionary promotes derivatives
  and compounds to headwords or nests them inside an entry.
- **Estimator.** Per-dictionary counts of subentry, preverb, cross-reference, and root
  layers, normalised per 1,000 entries.
- **Output.** Monier-Williams promotes derivatives and preverb forms to headwords; the
  Petersburg dictionaries nest them — the same content at different structural depth —
  per the committed artifact
  [`data/lexico/microstructure_fingerprint.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/microstructure_fingerprint.json).
- **Limits.** Depth markers (`<div>`) are structural, not semantic; depth is not a sense
  count (a confound Chapter 6 controls explicitly).

### 3.9 Root-parser agreement

- **Definition.** Whether independent parsers of indigenous verbal-root dictionaries agree
  on the grammar they recover.
- **Estimator.** Align gaṇa, pada, and transitivity features across root dictionaries;
  report compatible-agreement rates.
- **Output.** 85.5 % agreement on gaṇa, 75.3 % on pada, 81.4 % on transitivity — high
  enough to validate the recovered grammar layer — per the committed comparison
  [`docs/MICROSTRUCTURE_ROOT_AGREEMENT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ROOT_AGREEMENT.md).
- **Limits.** Agreement can mask shared error; conflicts mix homonymy, real disagreement,
  and parser weakness.

### 3.10 Semantic-field coverage

- **Definition.** A dictionary's topical profile, projected onto the Amarakośa's native
  varga taxonomy.
- **Estimator.** Map each dictionary's headwords onto AMAR kāṇḍa/varga/upavarga fields;
  report per-field coverage.
- **Output.** Dictionaries show measurable, family-correlated topical bias on an
  indigenous taxonomy — per the committed review packet
  [`data/lexico/h4_semantic_field_review_packet.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/h4_semantic_field_review_packet.json).
- **Limits.** Headword coverage is not sense, corpus, or citation coverage; rows need
  source review before topical claims.

A comparative aside on the scaffold itself. Using the varga taxonomy as a measurement
frame is not an antiquarian convenience: the first crosswalk of SIL's 1,792
field-lexicography semantic domains to the Amarakośa
([SEMDOM_AK_CROSSWALK_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/SEMDOM_AK_CROSSWALK_2026.md);
paper A58) finds the two organizations agreeing on 67% of synset placements at the
section level — and, more telling for method, both taxonomies bolt a formal annex onto
their semantic scheme for the words meaning cannot organize. The Amarakośa's kāṇḍa 3
holds 46.4% of its synsets, but 35.7 points of that is nānārtha, a polysemy register
SIL absorbs structurally by listing a word under several domains; the form-class
residue proper is 10.7% against semdom's 9.4%
([FINDINGS §77](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).
A sixth-century verse thesaurus and a twentieth-century elicitation taxonomy converge
on both the semantic partition and the size of its formal remainder — which is
precisely the property a cross-epoch measurement scaffold needs.

The point of stating these together is that they are **independent estimators of
relatedness and structure**, not facets of one similarity score. §7 shows why that
independence matters.

## 4. The traceability layer

A metric is only publishable if a reader can check it. Four mechanisms, all enforced in
the codebase, make each number above citable and falsifiable.

**The dataset envelope.** Every generated artifact carries a fixed header —
`schemaVersion`, `generatedAt`, `license`, an `assumptions` list, and a `warnings` list —
emitted by a single shared helper so the discipline cannot drift between generators.
`generatedAt` is preserved across content-identical rebuilds, so a regeneration that
changes nothing changes no bytes; the data is reproducible rather than churning.
Assumptions and warnings travel *with the data*, not only in a chapter, so a downstream
reader meets a metric's bounds at the point of use.

**Graded evidence levels.** Each datum is labelled `derived` (a deterministic parse of
the source), `model-pending` (an external NLP cross-check, retained as review evidence
only), or `reviewed` (human-ratified). The labels enforce the framework's hardest rule:
**no model inference runs in the build.** A neural cross-check may inform a review queue,
but it is never an input to a published figure; the build is a deterministic function of
the committed source.

**Page-level trust statements.** Every interactive page states, in a fixed "trust block,"
what its number *is*, the panel or threshold limits behind it, and what it is *not*. The
bounds a referee would demand are on the page beside the chart, not buried in a methods
section.

**The human review gate.** Where a metric *proposes* a change to the canonical text — a
resolved citation link, a promoted parser rule, a gender reconciliation — it writes a
review item conforming to a published schema, carrying source pointers (dictionary, line,
URL) and the machine's proposed value, with empty human-decision fields. Decisions are
preserved by a stable `reviewId` across regenerations, so re-running a generator never
overwrites a human ruling. The atlas proposes; a human disposes; only then does anything
reach the source. This is the operational form of `Claim → Evidence → Source`.

## 5. The routing and boundary layer

Two rules keep the claims falsifiable and inside their bounds.

**One-owner routing.** A cross-repo hypothesis index assigns every claim to exactly one
repository, and a boundary document keeps corpus, standards, and *project* measurement
out of the dictionary atlas. This is what prevents the §1 boundary error: the project-KPI
programme is routed elsewhere by construction, so it cannot leak into a dictionary claim.

**Anti-over-claim rules.** Three are load-bearing across the book: containment is a
*floor* for relatedness, never proof of copying (§3.1); a refuted hypothesis stays
visible as a finding, because a negative result is still evidence (the
granularity-inflation hypothesis became its own refutation); and thresholds, panels, and
proxies are reported as bounds, not point measurements. These are not editorial niceties —
they are the difference between a measurement and an over-reading.

## 6. The corpus as a bounded witness

> **Status.** This section is the book's single, canonical statement of what its
> reference corpus can and cannot witness, and of the statistical practice every
> quantitative chapter observes. The corpus-facing chapters — the headword inventory
> (Ch. 3), the Monier-Williams entry benchmark (Ch. 5), the citation-frequency graph
> (Ch. 11), and the register study (Ch. 13) — cite this section instead of restating it,
> and every other chapter that touches corpus attestation inherits it the same way. If a
> passage anywhere in this book appears to claim more from a corpus figure than this
> section licenses, this section wins.

The metrics of §3 measure the dictionaries against each other. Several chapters go a
step further and measure the dictionaries against **text**: whether a headword is
attested in a corpus at all, how often, and in which registers. The moment the framework
takes that step it acquires a fourth witness — not a dictionary but a corpus — and that
witness must be examined under the same floor-and-ceiling discipline §3 imposes on every
estimator: what it is, what it can testify to, and what no honest reading can extract
from it. Corpus linguistics has stated this discipline for decades (McEnery and Brezina
2022 is the current synthesis); this section fixes its consequences for this book once,
so that no later chapter has to re-derive them — and no later chapter can quietly
outrun them.

### 6.1 The witness disclosed

Every attestation figure in this book is computed against one corpus: the **Digital
Corpus of Sanskrit** (DCS; Hellwig 2010–), release 2026 — the only large lemmatized,
morphologically disambiguated corpus of Sanskrit in existence, and the de-facto
substrate of computational Sanskrit studies. The committed snapshot used throughout
holds **5,688,416 content tokens (punctuation excluded) across 270 texts**, with an
attested vocabulary of **95,457 distinct disambiguated lemmas**. Within the evidence
graph, this corpus supplies the attestation layer — the "corpus attestation where
available" of the book's thesis statement — and every figure drawn from it is `derived`
in the sense of §4: a deterministic count over a pinned snapshot, enveloped and walkable
like every other artifact. Three properties of this witness bound everything it can say.

**It is small — by lexicographic standards, very small.** The corpus-lexicography
literature puts the working size for *sense-level* dictionary evidence at tens to
hundreds of millions of words (Biber 1993; Reppen 2010; Walter 2010): a sense is
captured only when a lemma is attested often enough for its uses to cluster into
patterns, which is why the corpus-driven dictionaries of the COBUILD line were built on
corpora three orders of magnitude larger than anything available for Sanskrit. DCS's
5.7 million tokens sit one to two orders of magnitude below that floor. The consequence
is not that the corpus is useless; it is that DCS can witness **attestation and
distribution** — this lemma occurs, in these texts, this often — but cannot adjudicate
**sense inventories**, and no chapter of this book asks it to. Where the graph records
corpus attestation for a headword, the datum is a presence signal with a frequency,
never a semantic verdict.

**It has no sampling frame.** DCS is an opportunistic corpus: it grew over two decades
by what had been digitized, philologically edited, and morphologically tagged, not by a
design that samples the language's registers in known proportions — representativeness
in Biber's (1993) sense is not claimed by its maker and cannot be claimed on its behalf.
Epic and śāstric prose dominate; inscriptions are absent by construction, since DCS is a
corpus of *literary* transmission; documentary, lyric, and technical registers enter
only as far as tagging projects have reached them. An absence can therefore reflect the
language, the archive, or merely the tagging queue — and nothing in the corpus itself
says which.

**Its own frequency structure guarantees absence.** In the committed hapax census of the
2026 release, **39,987 of the 95,457 attested lemmas — 41.9 % — occur exactly once**,
and 78.3 % occur fewer than ten times, while 0.8 % of lemmas carry most of the tokens:
textbook Zipf. A vocabulary whose attested half is this rare is the visible edge of a
much larger unseen mass — the next million tokens of tagged Sanskrit would, with
certainty, surface thousands of lemmas the current corpus has never seen. Productive
morphology sharpens the point: 42.3 % of those hapaxes are transparent nominal
compounds, hapax only because samāsa formation mints new types on demand. Against such a
distribution, the absence of any *particular* lemma is the expected continuation of the
frequency curve, not a fact demanding a special explanation.

### 6.2 The absence-inference rule

The tempting move — the one a dictionary-versus-corpus comparison invites on every
page — runs: *this headword is unattested in the corpus, therefore it is a
lexicographers' phantom; that dictionary stratum is two-thirds unattested, therefore it
records vocabulary that never existed.* McEnery and Brezina (2022) dissect this as the
problem of induction writ large: a corpus is a finite sample of performance, and
non-occurrence in a sample is not non-existence in the language. §6.1 gives the local
reasons the inference fails here with unusual force: the corpus sits below the size
floor (absence is under-powered), it has no sampling frame (absence may measure the
archive), and its frequency structure makes absence the statistical default (absence is
expected). In a 5.7-million-token corpus, a lemma that is merely *rare* and a lemma that
is truly *absent from the language* are observationally indistinguishable — the mirror
of the neologism caveat in corpus-based dictionary-making (Walter 2010). The inference
would begin to bear weight only where the corpus could be shown to cover the relevant
register at known depth — a condition met nowhere in this family today.

This book therefore operates under one rule, stated here once:

> **The absence-inference rule.** Every corpus-absence figure in this book is a bounded
> statement about **DCS coverage** — never about the Sanskrit language, and never about
> a dictionary's veracity. It travels with its denominator and its register or source
> composition where known, and it is phrased as *unattested in DCS*, never as
> *non-existent*.

The rule has a positive half. Precisely because absence measures coverage,
*differential* absence is informative — about the corpus and about the dictionaries, the
two things actually in view. Chapter 13 supplies the worked case: of 709 headwords the
Petersburg lexicographers tagged *épigraphique*, 484 (68.3 %) have no DCS attestation,
against 0 % for the *jaina*-tagged stratum — and the contrast reads straight off the
witness's own boundary, since DCS includes Jaina literary texts and, by construction, no
inscriptions. The register label predicts the corpus hole; the absence rate maps the
edge of the witness's competence; and that map is itself a publishable finding — an
agenda for digitization, not a verdict on the lexicographers. Chapter 3 does the same
corpus-wide: its per-dictionary attestation rates (from 69.8 % for the Vedic index VEI
down to 14.1 % for the Śabdakalpadruma) are read throughout as coverage geometry — which
strata of the dictionary record the corpus can currently see — under exactly this rule.

### 6.3 The statistical-practice contract

The second discipline concerns not what a figure means but how it is reported. At corpus
scale, classical significance testing stops discriminating: with N in the hundreds of
thousands, any non-trivial difference "rejects" at any conventional threshold, because
language is never random (Kilgarriff 2005). Chapter 11 operates on 828,505 citations;
several estimators of §3 run over a million and a half entries. At these sizes a bare
p-value is not evidence but decoration. Every quantitative chapter of this book
therefore observes five clauses:

1. **Effect size first, test second.** The claim is always a magnitude — a difference, a
   ratio, a containment, an association strength — with an uncertainty interval where
   the estimator admits one; a p-value may appear only beside its effect size and its N,
   never alone (the "new statistics" of McEnery and Brezina 2022; Desagulier 2017 for
   the working practice).
2. **Dispersion before generalization.** A corpus-wide or family-wide rate whose signal
   rides on one text, one edge, or one dictionary is reported as exactly that: §3.3's
   sense-survival gap is stated as citation-concentrated — 82 of 84 cited senses sit on
   a single edge — rather than as a family fact.
3. **Denominators travel with figures.** No naked percentages: 68.3 % arrives as
   484-of-709, granularity proxies arrive with their ±13 % validation bound, and
   normalized rates state their base (per 1,000 entries, §3.8).
4. **Minimally sufficient statistics.** The simplest statistic that answers the question
   (Egbert, Larsson, and Biber 2020); fitted models appear only where a confound
   genuinely requires a control — §3.3's cluster-robust refit — never as ornament.
5. **Negative results stay visible.** The routing layer's anti-over-claim rule (§5)
   applies to statistics too: a hypothesis that dies — the granularity-inflation reading
   refuted in §3.3 — is reported as its own finding, not silently dropped.

The book already contains the contract's instances: Chapter 5's benchmark reports κ and
per-type precision with its definitional boundaries disclosed; Chapter 14 reports
Cramér's V beside its χ² rather than the χ² alone; §3.3 above reports a two-sided
p ≈ 0.07 as suggestive but not significant, *with* its concentration caveat. Chapter 11,
drafted after this contract was fixed, is written to it from the first figure.

### 6.4 Where the discipline binds

Four chapters lean on this section by name and cite it rather than restating it:

- **Chapter 3 — the headword inventory.** The corpus-grounding bridge: per-dictionary
  DCS-attestation rates read as coverage geometry under §6.2, never as phantom rates.
- **Chapter 5 — the Monier-Williams entry benchmark.** Benchmark statistics (κ, per-type
  precision and recall, gold-sample construction) reported under §6.3's
  interval-and-disclosure clauses.
- **Chapter 11 — the citation-frequency graph.** N = 828,505: effect sizes,
  normalization, and dispersion in place of bare significance, per §6.3.
- **Chapter 13 — Renou's registers.** The worked case of the absence-inference rule:
  68.3 % as a coverage boundary, with the register labels supplying the map.

Every other chapter that touches corpus attestation — and any future one that will —
inherits the same two disciplines by citing this section. That is the sense in which the
corpus is this framework's bounded witness: fully admitted, heard on everything it can
see, and never asked to testify beyond it.

## 7. A worked example: one edition edge, end to end

Take the single inheritance edge from Apte's 1890 *Practical Sanskrit–English Dictionary*
(AP90) to its 1957 revised expansion (AP) — a *documented* edition continuity, used here
as a positive control. The framework assembles a descent statement about this edge from
independent estimators, each leaving a traceable trail.

1. **Content floor (§3.1).** The headword sets intersect at 26,055 lemmas; the 1890 list
   (34,277 headwords) is **76 % contained** in the 1957 list (88,667). High containment is
   *consistent with* edition continuity — but, being size-confounded, does not on its own
   establish it. The reading is held open.

2. **Cross-reference control (§3.6).** The two editions' internal cross-reference graphs
   share **182 directed edges at Jaccard 0.74**, with ≈85 % inheritance in *both*
   directions — a symmetric, high-overlap signal that the framework labels a positive
   control. Crucially, this is independent of headword overlap: a mere size relationship
   would not reproduce the *edge* structure. Contrast Monier-Williams × Petersburg (PWG),
   where the cross-reference Jaccard is 0.069 — a shared core, not an edition.

3. **Sense behaviour (§3.3).** Along this edge the sense drift is a **−3 revision**, not
   an expansion: the 1957 edition reorganises and tightens rather than inflating sense
   counts — the family-trait, not date-inflation, reading.

4. **Trust and gate (§4).** Each number above ships in an enveloped artifact with its
   assumptions and warnings; the cross-reference pair carries `reading:
   "positive-control"`; nothing here proposes a write to the source, so no review row is
   opened. A reader can follow each figure to its generator and to the CDSL source line.

The result is one **falsifiable, fully-sourced statement** — *AP90 → AP is an edition
continuity: word list largely carried, cross-reference graph symmetrically inherited,
senses revised downward* — built from three independent estimators that *agree*, each
reported against its own limit. A single similarity score could assert "AP90 and AP are
very similar" but could neither separate the carried word list from the inherited graph
from the revised senses, nor expose that the headword containment alone is
size-confounded. The framework's value is exactly this refusal to average.

## 8. Discussion

**Why a framework, not a pile of metrics.** Any one estimator above is unremarkable.
Their value is that they are *independent* and *traceable*: when three of them agree on
an edge (§7), the agreement is evidence; when one contradicts the others, the
contradiction is locatable. A single fused score destroys both properties. The framework
is the commitment to keep the estimators separate and every number walkable to its
source.

**Transferability.** Nothing in §§3–5 is specific to Sanskrit. Any project with a family
of related digital dictionaries — or, more broadly, related digital editions — has
headword-overlap, citation-resolvability, cross-reference, and structural questions, and
faces the same temptation to publish a number a reader cannot check. The envelope, the
three evidence levels, the trust block, and the review gate are a low-ceremony
alternative to ad-hoc data releases, implementable in any static-site or notebook
pipeline. The corpus discipline of §6 transfers just as directly, because its premise —
a reference corpus one to two orders of magnitude below the lexicographic size floor —
is the *normal* condition of historical languages, not a Sanskrit misfortune: only the
facts of the disclosure change; the bounded-witness rule and the statistical contract
port verbatim.

**Relation to existing practice.** The questions behind the descent metrics are
classical. That Monier-Williams depends on the Petersburg lexica has been established
philologically since Zgusta's (1988) study of copying in this very family — a study that
rested, exactly like the framework's cross-reference control logic (§3.6), on *shared
structure and shared error* as the decisive signal rather than on mere overlap — and the
question has recently been reopened in the same exemplary-probe mode (Hanneder 2020). The
framework's contribution to that line is scale and traceability: corpus-wide estimators
with committed, walkable artifacts, where the classical studies argued from hand-picked
probes. Sense-level comparison across same-language dictionaries likewise has an
established computational benchmark tradition (the ELEXIS monolingual word-sense-alignment
datasets; Ahmadi et al. 2020); the framework consumes that task differently — an
alignment model may only ever produce `model-pending` review evidence (§4), never a
published figure. And where digitization-quality frameworks measure how faithfully a
scanned dictionary is *converted* into structured text (e.g. MUDIDI; Setiawan et al.
2026), the metrics here assume the converted text and measure the *dictionaries'* mutual
relations; the two layers are complementary and meet at the canonical source file.

The traceability layer, in turn, operationalises at dataset granularity the
reproducibility and provenance norms that FAIR data principles (Wilkinson et al. 2016),
the W3C PROV provenance model (Lebo et al. 2013), and data-statement practice (Bender and
Friedman 2018) state at the level of whole deposits — an enveloped artifact is a minimal,
machine-readable data statement, and the review gate is an explicit provenance boundary
between machine proposal and human authority — while the no-inference-at-build-time rule
is the reproducible-research commitment that a published figure be a deterministic
function of the committed source (Peng 2011; Sandve et al. 2013). The contribution is the
*granularity and the enforcement* — every artifact, every build — rather than a new
principle.

## 9. Limitations

- **The catalog is the atlas's catalog.** Ten estimators cover the questions this project
  has asked; a different family might need others. The framework is the *discipline*, not
  a closed metric set.
- **Coverage is uneven.** Several estimators speak only about the European half of the
  family; the indigenous lexica enter some metrics (§3.4, §3.9) and are silent in others,
  and the catalog says so per metric rather than papering over it.
- **The worked example is a positive control.** AP90 → AP was chosen because the
  continuity is documented; the framework's harder test is a *cross-tradition* edge (e.g.
  Monier-Williams × Petersburg), where the estimators disagree and the reading is
  genuinely open — that case is carried by the sibling chapters, not resolved here.
- **Traceability is not correctness.** An enveloped, reviewed number is checkable, not
  thereby true; the framework lowers the cost of catching an error, it does not prevent
  one.
- **`model-pending` is a promissory note.** The evidence-level discipline keeps neural
  cross-checks out of the build, but a cross-check that never reaches human review adds no
  evidence; the gate must actually be worked.
- **The corpus disclosure maps known holes; it does not estimate bias.** §6 bounds what
  an absence may claim and fixes statistical practice, but it does not quantify DCS's
  sampling bias — there is no held-out digitization test. The coverage boundary is
  visible only where a register or source label exposes it (Chapter 13's épigraphique
  stratum is the worked case); unlabelled holes remain invisible by construction.

## 10. Conclusion

A digital dictionary family is only as credible as the toolkit that measures it and the
trail that leads from each published number back to a dictionary line. I have described
that toolkit as three reusable layers — ten independent, operationally-defined
estimators; a traceability discipline that envelopes, grades, and gates every datum; and
a routing discipline that keeps each claim falsifiable and in its lane — plus one
standing disclosure (§6) that keeps every attestation reading inside what a
5.7-million-token witness can actually testify to — under one rule:
every claim is a `Claim → Evidence → Source` path, and the machine only ever proposes.
Walked end to end on a single edition edge, the framework turns "these two dictionaries
are similar" into three independent, separately-bounded, source-linked statements that
happen to agree. That is the move the empirical chapters of this book — on kośa
macrostructure (Ch. 4), the Monier-Williams entry (Ch. 5), sense inheritance (Ch. 6),
indigenous grammar (Ch. 7), and cross-reference lineage (Ch. 9) — each rely on, and
which this chapter states once so that they can assume it.

## References

Ahmadi, Sina, John P. McCrae, Sanni Nimb, Fahad Khan, Monica Monachini, Bolette S.
Pedersen, et al. 2020. "A Multilingual Evaluation Dataset for Monolingual Word Sense
Alignment." In *Proceedings of the 12th Language Resources and Evaluation Conference
(LREC 2020),* 3232–3242. Marseille: European Language Resources Association.

Atkins, B. T. Sue, and Michael Rundell. 2008. *The Oxford Guide to Practical
Lexicography.* Oxford: Oxford University Press.

Bender, Emily M., and Batya Friedman. 2018. "Data Statements for Natural Language
Processing: Toward Mitigating System Bias and Enabling Better Science." *Transactions of
the Association for Computational Linguistics* 6: 587–604.

Biber, Douglas. 1993. "Representativeness in Corpus Design." *Literary and Linguistic
Computing* 8 (4): 243–257.

Desagulier, Guillaume. 2017. *Corpus Linguistics and Statistics with R: Introduction to
Quantitative Methods in Linguistics.* Cham: Springer.

Egbert, Jesse, Tove Larsson, and Douglas Biber. 2020. *Doing Linguistics with a Corpus:
Methodological Considerations for the Everyday User.* (Elements in Corpus Linguistics.)
Cambridge: Cambridge University Press.

Hanneder, Jürgen. 2020. "Woher hat er das? Zum Charakter des *Sanskrit-English
Dictionary* von Monier-Williams." *Zeitschrift der Deutschen Morgenländischen
Gesellschaft* 170 (1): 107–117.

Hellwig, Oliver. 2010–. *DCS — The Digital Corpus of Sanskrit.*
[www.sanskrit-linguistics.org/dcs/](https://www.sanskrit-linguistics.org/dcs/) (release
2026, CC BY-SA).

Kilgarriff, Adam. 2005. "Language Is Never, Ever, Ever, Random." *Corpus Linguistics and
Linguistic Theory* 1 (2): 263–276.

Lebo, Timothy, Satya Sahoo, and Deborah McGuinness (eds.). 2013. *PROV-O: The PROV
Ontology.* W3C Recommendation, 30 April 2013.
[www.w3.org/TR/prov-o/](https://www.w3.org/TR/prov-o/).

McEnery, Tony, and Vaclav Brezina. 2022. *Fundamental Principles of Corpus Linguistics.*
Cambridge: Cambridge University Press.

O'Keeffe, Anne, and Michael McCarthy (eds.). 2010. *The Routledge Handbook of Corpus
Linguistics.* London and New York: Routledge.

Peng, Roger D. 2011. "Reproducible Research in Computational Science." *Science* 334
(6060): 1226–1227.

Reppen, Randi. 2010. "Building a Corpus: What Are the Key Considerations?" In O'Keeffe
and McCarthy 2010.

Sandve, Geir Kjetil, Anton Nekrutenko, James Taylor, and Eivind Hovig. 2013. "Ten Simple
Rules for Reproducible Computational Research." *PLOS Computational Biology* 9 (10):
e1003285.

Setiawan, David, Temuulen Khishigsuren, Milind Agarwal, Pagnarith Pit, Aso Mahmudi, and
Ekaterina Vylomova. 2026. "MUDIDI: A Two-Stage Framework for Multilingual Dictionary
Digitization with Language Models." arXiv:2606.09435.

Walter, Elizabeth. 2010. "Using Corpora to Write Dictionaries." In O'Keeffe and McCarthy
2010.

Wiegand, Herbert Ernst. 1989. "Der Begriff der Mikrostruktur: Geschichte, Probleme,
Perspektiven." In Hausmann, Reichmann, Wiegand and Zgusta (eds.), *Wörterbücher /
Dictionaries / Dictionnaires,* vol. 1 (HSK 5.1), 409–461. Berlin and New York: Walter de
Gruyter.

Wilkinson, Mark D., et al. 2016. "The FAIR Guiding Principles for scientific data
management and stewardship." *Scientific Data* 3: 160018.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.)
Prague: Academia; The Hague and Paris: Mouton.

Zgusta, Ladislav. 1988. "Copying in Lexicography: Monier-Williams' Sanskrit Dictionary
and Other Cases (Dvaikośyam)." *Lexicographica* 4: 145–164.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

**Sibling chapters (this book).** *Order Is the Dictionary* (Ch. 4, kośa macrostructure;
instantiates §3.10); *The Block Economy of Monier-Williams* (Ch. 5, the European entry
anatomized; §3.8's microstructural object at full depth); *Senses: Inheritance and Order*
(Ch. 6, merges the former sense-inheritance and sense-ordering articles; instantiates §3.3);
*Grammar Without Tags* (Ch. 7, indigenous verbal-root microstructure; §3.9); *Pointing
Inward* (Ch. 9, cross-reference lineage and descent; §3.1, §3.6, §3.8, whose headword-level
corpus figures §3.2 anchors); *Two Citation Registers* (Ch. 10, citation registers; §3.4,
likewise). Each instantiates one or more of the metrics in §3
under the discipline of §§4–5; where this chapter quotes a sibling's headline figure
(§3.2, §3.4), the sibling chapter owns the full result and this chapter owns only the
metric's definition. The corpus-facing chapters — *The Headword Inventory* (Ch. 3),
*The Block Economy of Monier-Williams* (Ch. 5), *What the Tradition Cites* (Ch. 11), and
*Renou's Registers* (Ch. 13) — additionally cite §6's bounded-witness rule and
statistical contract rather than restating them (§6.4).

*[Data note, 2026-07-03: every §3 anchor is walkable to a committed enveloped artifact.
§3.4's corpus figures are regenerated from
[`data/obs/citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json)
(generator
[`scripts/obs/citation_register_gaps.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/citation_register_gaps.py));
§3.2's collapse (1,496,157 → 410,259, 3.65 : 1) from
[`data/obs/headword_collapse.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/headword_collapse.json)
(generator
[`scripts/obs/headword_multiplicity.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/obs/headword_multiplicity.py),
now format-aware for the `<s>`-less nmmb kośa added to csl-orig in 2026-06; the
previously doc-sourced 409,649 reflected the pre-nmmb corpus). §6's corpus figures are
per the committed DCS 2026 snapshot and hapax census in the sibling VisualDCS
repository: the 270-text snapshot import per the
[VisualDCS CHANGELOG](https://github.com/gasyoun/VisualDCS/blob/main/CHANGELOG.md); the
5,688,416 content tokens, the 95,457-lemma vocabulary, its frequency bands, and the
39,987-hapax census (41.9 %, compound split 42.3 %) per
[Gapaksy-DCS-2026](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Leksicheskie-issledovaniya/Gapaksy-DCS-2026/README.md)
(generator
[`gen_dcs_hapax.py`](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Leksicheskie-issledovaniya/Gapaksy-DCS-2026/gen_dcs_hapax.py),
deterministic, no network). Chapter 13's 484-of-709 épigraphique figure and Chapter 3's
per-dictionary attestation range are owned by those chapters and quoted here under §6.2.]*

_Dr. Mārcis Gasūns_
