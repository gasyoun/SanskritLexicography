# Chapter 3 — The Headword Inventory: Coverage, Growth, and the Corpus-Grounding Bridge

_Created: 18-07-2026 · Last updated: 18-07-2026_

> **Provenance.** This chapter is the book-form version of the study *Twelve Years of
> Headwords: A Controlled 2014-vs-2026 Census of the Cologne Digital Sanskrit Dictionaries
> and Their Corpus Grounding* (source draft:
> [A40_headword_inventory_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A40_headword_inventory_note.md)),
> which is being published separately in a journal version; where the article must remain
> independently citable, cite that version. Every count and table below is carried over
> from the committed census artifacts unchanged — the census itself in
> [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md),
> the cross-dictionary union in
> [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md),
> the overlap matrix in
> [HEADWORD_OVERLAP_UNION15_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md) —
> and only the framing has been converted from journal to book form. The chapter observes
> the denominator policy of the source study (one corpus denominator per table, the release
> always stated) and inherits Chapter 2 §6 — the bounded-witness disclosure, the
> absence-inference rule, and the statistical-practice contract — by citation rather than
> restatement. Section numbering is chapter-internal (§1–§8).

The bridge to this Part put the point in one sentence: before a dictionary says anything
about any particular word, it has already made its largest single assertion — the list
itself. This chapter audits that assertion across the collection, as a *set* and over
*time*. It fixes three quantities the rest of the book stands on: how large the digitised
headword record actually is once redundancy is accounted for; how the record moved across
twelve years of continuous editing; and how much of it the reference corpus can currently
see. The first two are the documentary baseline — everything Parts III and IV measure
lives inside inventories whose size and growth this chapter states. The third is the
**corpus-grounding bridge**: the point where the evidence graph acquires its attestation
layer, and where the discipline of Chapter 2 §6 — the corpus as a bounded witness — is
first exercised at full width.

## 1. Introduction

A dictionary collection is usually described by a single number: "194,000 headwords,"
"36,000 entries." That number is a snapshot of one edition at one moment, and it conflates
two things a lexicographer actually cares about — how the inventory is *changing*, and how
much of it is *grounded in attested language* rather than inherited from earlier lexica or
generated as nonce compounds. Worse, the number is not even well-defined until a chain of
counting decisions has been made. What counts as a headword — whether a compound or
derived form earns its own entry or is subordinated under a root — is a structural
decision of documentary lexicography, with named criteria in the field's own manuals
(Coward and Grimes 2000, §6.1 on headword-status criteria, §4.6 on root- versus
lexeme-oriented database organization), and it silently conditions every inventory count
compared in this chapter. The indigenous half of this book's corpus takes one side of that
fork — the *dhātu*-organised lexica of Chapter 7 are root-oriented databases in Coward and
Grimes's exact sense — while the European dictionaries take the other, and Sanskrit
sharpens the choice to its limit: a language whose compound formation mints new types on
demand keeps the headword-versus-construction boundary permanently contested. The *ādi*-
compounds are the textbook case — *indrādi* "Indra and so on" is formally a compound but
functionally a category-building construction, and whether such forms are lexical entries
or grammatical products is a live analytical question (Inglese and Geupel 2018) that every
one of these dictionaries had to answer implicitly, entry by entry. Counting standards
matter for the same reason at the opposite end of the pipeline: whether one counts types,
lemmas, or word families changes the magnitude of any vocabulary figure (Szudarski 2018),
and the census below is explicit that its unit is the dictionary's own normalised headword
key, nothing finer.

The Cologne Digital Sanskrit Dictionaries are an unusually clean testbed for separating
change from grounding. The same ~36 dictionaries are marked up in a uniform XML, each
entry carrying a normalised computational key (`<k1>`) and a closer-to-print key (`<k2>`);
and a frozen 2014 export of those keys has been preserved alongside the continuously
edited live source, giving a genuine twelve-year baseline rather than a reconstructed one.
Two questions organise the chapter:

1. **How has the headword inventory changed, 2014 → 2026, when measured honestly?**
   "Honestly" is the operative word: a naive diff of every committed list against the
   current source reports nonsense for the lists whose 2014 snapshot was in a legacy
   transliteration since migrated to SLP1. The census isolates the **comparable** lists
   (same key format then and now) from the **format-migrated** ones and aggregates growth
   only over the former.

2. **How corpus-grounded is each dictionary?** Using one common denominator — the
   attested lemmas of the Digital Corpus of Sanskrit (DCS), the witness disclosed in
   Chapter 2 §6.1 — a per-dictionary attestation rate separates corpus-facing from
   corpus-detached lexica, and is read throughout as coverage geometry under the
   absence-inference rule of Chapter 2 §6.2, never as a verdict on the lexicographers.

The chapter makes four claims. Growth is **additive but strikingly uneven** — the
comparable inventory grows +14.3 % in aggregate, but the growth concentrates in a few
actively edited dictionaries while the canonical large lexica are frozen. Removals are an
**audit channel**, not churn — most of the ~20 thousand headwords that vanished are the
digitisation cleaning its own keys, and the residue that is not self-evidently hygiene is
precisely where entry-level review is owed. A **common-denominator attestation rate
separates corpus-facing from corpus-detached lexica** — a property of a dictionary's
purpose, not its size. And the census is a **method, not a one-off count**: the diff
machinery is committed and re-runs against any pinned source checkout.

One historical control keeps the whole exercise from reading as a digital novelty. That a
headword list is a designed artifact — balanced, not merely accumulated — is as old as
systematic English lexicography: Thorndike built his teaching dictionaries by explicit
inventory balancing across frequency blocks, and the field's manuals treat the data
sources behind a word list as a named editorial decision (Jackson 2002). What the digital
collection adds is not the fact of design but its *measurability*: with every key
committed and versioned, inclusion policy stops being a preface claim and becomes an
auditable dataset — in this book's terms, each headword is a node of the evidence graph
carrying its source dictionary, and this chapter attaches to those nodes their first two
layers of evidence: longitudinal provenance and corpus attestation.

## 2. The census: two snapshots, one comparability rule

### 2.1 The two snapshots

Each frozen list in
[then-2014/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014)
is a 2014 headword snapshot whose filename records its line count at extraction (first
committed 2014-10-05; for three of the 26 files the census's actual *then* line count
differs slightly from the filename count, so the census table, not the filename, is
authoritative). The 2026 side is re-extracted from the live csl-orig source for the same
field, written to
[now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026),
and diffed by
[headword_diff.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py).
**Growth** = (now − then) / then; **overlap** = the share of the *then* keys still present
now. The 2026 side is extracted from a repository edited daily, so the journal version of
the census pins a single csl-orig commit; a symptom of the drift is already visible in the
committed record — Apte's live key1 count appears as 88,869 in the census table and 88,867
in the extraction filename, a two-headword edit between two extraction runs. Where the two
figures could disagree below, the census table's value is quoted.

### 2.2 key1, key2, and what may be diffed

`<k1>` is the normalised computational key, built for matching and deduplication; `<k2>`
is closer to print, retaining hyphens, accent marks, and parentheses. The decisive
methodological point is that **not every committed list can be honestly diffed.** A list
is *comparable* when its 2014 snapshot and the live 2026 field share a key format, so that
added and removed lines are genuine headword changes. A list is *format-migrated* when the
2014 `<k2>` snapshot is in the legacy Cologne numeric transliteration (`am2s4a` = *aṃśa*)
while the live source is now SLP1: the raw then-versus-now diff approaches 100 % and is an
encoding artifact, not a headword change. Six lists are format-migrated; the two lists of
the Deccan College dictionary (PD) have no csl-orig source and are set aside; the 26
snapshots therefore partition as **18 comparable + 6 format-migrated + 2 PD**, and every
growth figure below aggregates over the 18 alone. Folding the format-migrated lists into a
growth number would be the single easiest way to publish a wrong figure about this
collection.

## 3. Growth: additive, uneven, and audited

### 3.1 The aggregate

Across the 18 comparable lists the headword inventory grows from **1,055,081 (2014) to
1,206,384 (2026)** — **+171,644 added, −20,341 removed, +14.3 % net**. For scale, the
grand total of all 26 snapshots' 2014 line counts — including the format-migrated lists
that must not enter a growth figure — is 1,721,983. (Source:
[NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md),
TOTAL row; n = 18 comparable lists; "then" = the 2014-10-05 frozen export, "now" = the
2026 re-extraction.)

### 3.2 The per-dictionary profile

| dictionary (list) | 2014 | 2026 | added | removed | overlap | growth |
|---|--:|--:|--:|--:|--:|--:|
| AP — Apte (key1) | 36,030 | 88,869 | 53,742 | 903 | 97.5 % | **+146.7 %** |
| AP — Apte (key2) | 36,126 | 88,829 | 56,024 | 3,321 | 90.8 % | +145.9 % |
| PWK — Böhtlingk kl. (key2) | 133,741 | 155,688 | 23,265 | 1,318 | 99.0 % | +16.4 % |
| PWK — Böhtlingk kl. (key1) | 131,918 | 151,349 | 19,617 | 186 | 99.9 % | +14.7 % |
| GRA — Grassmann RV (key1) | 10,315 | 11,108 | 975 | 182 | 98.2 % | +7.7 % |
| VCP — Vācaspatyam (key2) | 47,145 | 48,638 | 4,360 | 2,867 | 93.9 % | +3.2 % |
| VCP — Vācaspatyam (key1) | 47,107 | 48,636 | 2,514 | 985 | 97.9 % | +3.2 % |
| SKD — Śabdakalpadruma (key1) | 40,551 | 40,817 | 807 | 541 | 98.7 % | +0.7 % |
| SKD — Śabdakalpadruma (key2) | 40,595 | 40,817 | 2,281 | 2,059 | 94.9 % | +0.5 % |
| MW — Monier-Williams (key1) | 193,978 | 194,084 | 754 | 648 | 99.7 % | **+0.1 %** |
| BUR — Burnouf (key2) | 19,238 | 19,251 | 297 | 284 | 98.5 % | +0.1 % |
| CAE — Cappeller Eng. (key2) | 39,256 | 39,280 | 3,000 | 2,976 | 92.4 % | +0.1 % |
| VEI — Vedic Index (key1) | 3,703 | 3,704 | 18 | 17 | 99.5 % | +0.0 % |
| PWG — Petersburg gr. (key2) | 110,402 | 110,438 | 380 | 344 | 99.7 % | +0.0 % |
| PWG — Petersburg gr. (key1) | 106,085 | 106,082 | 149 | 152 | 99.9 % | **−0.0 %** |
| MD — Macdonell (key2) | 20,108 | 20,107 | 44 | 45 | 99.8 % | −0.0 % |
| INM — Sörensen Mbh. index (key2) | 9,466 | 9,454 | 89 | 101 | 98.9 % | −0.1 % |
| CCS — Cappeller Germ. (key2) | 29,317 | 29,233 | 3,328 | 3,412 | 88.4 % | −0.3 % |
| **TOTAL (18 comparable lists)** | **1,055,081** | **1,206,384** | **171,644** | **20,341** | — | **+14.3 %** |

*Source:
[NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md)
(n = 18 comparable of 26 snapshots; 2014-10-05 frozen export vs 2026 re-extraction).*

The picture is sharp. **Apte more than doubles** (+146.7 %; 36,030 → 88,869 headwords),
**the shorter Petersburg recension adds roughly twenty thousand headwords** (+14.7 % on
the normalised key), and **the two canonical large lexica do not move** — Monier-Williams
+0.1 %, the great Petersburg dictionary −0.0 %. Below those, genuine growth is modest and
targeted: Grassmann +7.7 %, the Vācaspatya +3.2 %, the Śabdakalpadruma +0.7 %; everything
else moves by well under one percent in either direction. Where a dictionary contributes
both a key1 and a key2 list, the rows agree on direction and roughly on magnitude, and the
key2 row always churns more (Apte 3,321 removed against 903; SKD 2,059 against 541),
because the closer-to-print key also absorbs punctuation and variant-notation cleanup the
normalised key never sees. The high-overlap-but-nonzero-churn rows — Cappeller's German
edition at −0.3 % with 3,328 added *and* 3,412 removed — are mostly editorial re-keying
rather than inventory change, which the removals typology below makes concrete. The
post-2014 editing wave this table records is the largest change to the collection since
the original digitisation, and it is visible *only* longitudinally: no synchronic
description of the collection contains it.

### 3.3 Removals as an audit signal

The −20,341 headwords present in 2014 and gone in 2026 are merges, corrections, or
accidental deletions, and the distribution alone is informative: Apte's 903 key1 removals
against +53,742 additions read as a thorough re-edit; the Petersburg dictionary's 152
against 149 read as targeted corrections. A surface-shape reading of the committed 40-item
samples per list shows the bulk of the removals to be **key hygiene, not lexical loss**,
each dictionary with a characteristic signature: field leakage repaired (trailing commas
baked into Apte keys, gender tags leaked into Śabdakalpadruma keys, truncated bracket
fragments in Macdonell); legacy-encoding residue purged (SKD keys still carrying the digit
notation of the pre-SLP1 transliteration); variant-notation normalisation (the
Vācaspatya's parenthetical alternates, the shorter Petersburg recension's asterisked
reconstructions); placeholder stubs dropped (Burnouf's 284 leading-asterisk scaffolding
entries); and misprint corrections (Monier-Williams's 648 removals are dominated by
recognisable typos of known lemmas). The residue that matters is the exception: Grassmann's
182 removals and Sörensen's 101 include plain, well-formed lemmas, and precisely because
those do *not* look like hygiene, each is either a deliberate merge or a candidate
accidental loss — the two lists where the audit reading earns its keep, and an open
adjudication item in the source study. The methodological point stands independent of that
adjudication: a removal count is not churn but a **stratified QA signal**, and most of its
mass here is the digitisation cleaning its own keys.

## 4. The union: one lexicographic core and its honest denominators

Per-dictionary counts, however audited, still double-count the family's shared inheritance.
The cross-dictionary union — built from the current `<k1>` of the 15 dictionaries that
have one, with 237 gender-confirmed *-inī* feminines folded onto their *-in* base
(323,662 raw keys → **323,425 union headwords**) — supplies the honest denominators
([UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)).
Its provenance distribution is itself a portrait of the collection:

| attested in *k* of 15 dictionaries | headwords |
|--:|--:|
| 1 | 142,673 |
| 2 | 61,514 |
| 3 | 46,834 |
| 4 | 28,778 |
| 5 | 17,250 |
| 6 | 10,319 |
| 7 | 5,852 |
| 8 | 3,934 |
| 9 | 2,928 |
| 10 | 1,876 |
| 11 | 967 |
| 12 | 493 |
| 13 | 188 |
| 14 | 45 |
| 15 | 11 |

*Source:
[UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)
(union over 15 dictionaries' current `<k1>`, exact SLP1 key equality, homographs
collapsed, gender-confirmed feminine folds).*

Only eleven headwords occur in all fifteen dictionaries; **142,673 — 44.1 % of the
union — occur in exactly one**. Against the union, the collection's headline size
overstates its lexical diversity by roughly a factor of five (1.72 million snapshot lines
against 323,425 distinct keys), and the pairwise-overlap matrix computed over the same
union — cited here, not recomputed
([HEADWORD_OVERLAP_UNION15_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md)) —
resolves that redundancy into structure. Three of its findings bear directly on how this
chapter's results must be read.

First, **the collection has one lexicographic core.** The highest Jaccard overlaps are
Cappeller's English and German editions of one dictionary (0.672), the large against the
small Petersburg recension (0.630), and Monier-Williams against the small Petersburg
recension (0.597); Monier-Williams and the great Petersburg dictionary share 94,753
headwords. The school-size dictionaries are almost fully subsumed in that
Böhtlingk–Monier-Williams lineage — Cappeller's German edition retains 0.6 % unique
headwords, the English 1.7 %, Macdonell 2.0 %, and the great Petersburg dictionary itself
only 2.4 %, its inventory surviving nearly whole in its own abridgements. This is the
macrostructural face of the descent that Part IV reads in cross-references and citations.

Second, **Apte's growth is not copying.** The census's most dramatic mover is also, after
Monier-Williams, the largest *unique* inventory in absolute terms: 35,762 headwords —
40.3 % of Apte — occur in no other dictionary of the union. The 2014–2026 re-edit did not
backfill Apte from the Böhtlingk–Monier-Williams core; it added material the rest of the
collection does not have.

Third, **the isolates are isolated for different reasons.** Edgerton's Buddhist Hybrid
Sanskrit dictionary (58.7 % unique), the Śabdakalpadruma (42.6 %), and Apte (40.3 %) are
near-disjoint from the Vedic lexica — the Śabdakalpadruma–Vedic Index Jaccard is 0.008.
Combined with the grounding rates of §5, the axes separate cleanly: the Śabdakalpadruma is
at once the least corpus-grounded and among the most lexically isolated — a genuinely
different lexicographic world, not a redundant copy of the core.

One technical note keeps the union's totals from being misread against §3's: the union key
collapses homographs and folds the confirmed feminines, so its per-dictionary totals sit
marginally below the list counts (Monier-Williams 193,852 distinct keys against 194,084
list lines). Union figures are distinct-key counts; census figures are list line counts;
neither substitutes for the other.

## 5. The corpus-grounding bridge

### 5.1 The witness, already on oath

Everything in this section measures the dictionaries against the corpus witness that
Chapter 2 §6 disclosed and bounded: the Digital Corpus of Sanskrit — the only large
lemmatised, morphologically disambiguated corpus of Sanskrit in existence — with its
committed release figures, its lack of a sampling frame, and a frequency structure in
which 41.9 % of attested lemmas are hapaxes. None of that is restated here; this chapter
writes every figure below under Chapter 2 §6.2's absence-inference rule: **every
corpus-absence figure is a bounded statement about DCS coverage — phrased as *unattested
in DCS at the stated release*, never as *non-existent* — and travels with its denominator.**
The corpus-lexicography literature reaches the same posture from the practitioner's side:
even for well-resourced modern languages, the corpus behind a dictionary is "never good
enough" for the inventory decisions asked of it, and headword-list building from corpora
is an exercise in managed noise and bias (Kilgarriff 2013). A fortiori for a
5.7-million-token corpus of a classical language.

### 5.2 Attestation separates the lexica

Joining each comparable dictionary's current key1 headwords against the **83,239 attested
SLP1 lemmas of the DCS-2021 release** — a bare-lemma join, homographs collapsed, no
inflectional morphology, and therefore an **upper bound** on every rate it produces —
gives:

| dictionary (key1) | headwords | attested in DCS-2021 | rate (upper bound) |
|---|--:|--:|--:|
| VEI — Vedic Index | 3,704 | 2,584 | **69.8 %** |
| GRA — Grassmann RV | 11,108 | 7,569 | **68.1 %** |
| VCP — Vācaspatyam | 48,636 | 23,742 | 48.8 % |
| PWG — Petersburg gr. | 106,082 | 40,960 | 38.6 % |
| PWK — Böhtlingk kl. | 151,349 | 47,366 | 31.3 % |
| MW — Monier-Williams | 194,084 | 57,157 | 29.4 % |
| AP — Apte | 88,867 | 19,338 | 21.8 % |
| SKD — Śabdakalpadruma | 40,817 | 5,741 | **14.1 %** |

*Denominator: DCS-2021, the 83,239 attested SLP1 lemmas of
[dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json)
(one denominator per table); numerators = current 2026 key1 lists; bare-lemma join, upper
bound. The journal version of the census recomputes the headline against the DCS-2026
release denominator (98,606 distinct attested lemmas) with a homograph control; the
DCS-2021-by-LemmaId figure (91,406) is a third, distinct number, and the three are never
mixed in one rate.*

Union-wide, **61,340 of 323,425** headwords match a DCS-2021 attested key (**19.0 %**,
upper bound; same denominator and join). The separation tracks each dictionary's
*purpose*, not its size: the corpus-facing Vedic lexica — the Vedic Index at 69.8 % and
Grassmann at 68.1 %, both built directly off a fixed corpus — sit at the top; the
corpus-detached encyclopaedic-traditional Śabdakalpadruma sits at the bottom at 14.1 %;
the general descriptive dictionaries occupy the middle band (Monier-Williams to the great
Petersburg dictionary, roughly 29–39 %). This **~5× spread is the central empirical result
of the corpus-grounding analysis**, and it is robust in a way the individual rates are
not: the pending recompute against the DCS-2026 denominator will move every number, but a
ranking resting on a fivefold separation survives a denominator shift that no plausible
homograph control comes close to erasing.

Read under Chapter 2 §6.2, the table is **coverage geometry** — a map of which strata of
the dictionary record the corpus can currently see. The Vedic lexica are two-thirds
visible because DCS is strong exactly where they look; the Śabdakalpadruma is six-sevenths
invisible because the kośa tradition's inventory — synonym stocks, śāstric
nomenclature, lexicographer-transmitted lexemes — lies mostly where a corpus of tagged
literary transmission does not reach at its current size. Differential attestation is
informative about the corpus and about the dictionaries, the two things actually in view;
what it never licenses is the inference from a low rate to a defective dictionary. That
reading has a name and a history in the field — Skeat introduced "ghost-words" for entries
with no real existence behind them (Skeat 1886) — and the distinction it demands is
exactly the one the join cannot make: a headword unattested in DCS at the 2021 release may
be a transmission artifact, but equally a real lexeme of the kośa tradition transmitted on
lexicographer authority alone, the stratum Monier-Williams explicitly marks with its
"lexicographers" source tag (`<ls>L.</ls>`). The project's companion studies work through
exactly this stratum — the botanical layer of Monier-Williams in the
[A45 crosswalk study](https://github.com/sanskrit-lexicon/MWS/blob/master/papers/A45_botanical_crosswalk_paper.md)
and the verbal-root attestation caveats in the
[A39 root-disagreement study](https://github.com/sanskrit-lexicon/MWS/blob/master/papers/A39_verbal_roots_disagreement_paper.md)
— and this chapter classifies the unattested stratum rather than condemning it.

Two further bounds are first-class here, carried from the source study. **The denominator
is model output**: DCS lemmatisation is produced by the ByT5-Sanskrit pipeline (Nehrdich,
Hellwig, and Keutzer 2024), so lemmatiser error bounds the join from both sides — a
dictionary headword can miss an attested lemma the model mis-lemmatised, and match a lemma
the model invented. And **the join is surface-form only**: no inflection, homographs
collapsed. Both push in the direction the upper-bound label already declares.

### 5.3 The bridge in the other direction

The attestation table asks what fraction of each dictionary the corpus can see. The
reverse question — when the corpus meets the dictionary record, does it find its lemmas
there? — has a committed pilot answer in the DCS↔CDSL crosswalk of the search-engine
repository
([dcs_cdsl_xref.tsv](https://github.com/sanskrit-lexicon/csl-apidev/blob/master/simple-search/dcs_xref/dcs_cdsl_xref.tsv)).
Its scope must be stated precisely, because both of its bounds run opposite to the table
above. The crosswalk covers the **13-text pilot slice** of the DCS-2026 CoNLL-U import —
15,902 lemmas carrying 134,047 tokens, not the full 270-text corpus — and its match
target is the engine's working key list (`wf0`), which is not a complete census of CDSL
headwords; a miss can be a real headword filed under a legacy spelling. Under those
semantics, **12,945 of 15,902 pilot lemmas (81.4 %) resolve to a CDSL key — a floor, not
a ceiling** — and the resolution is strongly frequency-ordered: weighted by token count,
94.7 % of the pilot's running text belongs to lemmas the dictionary record covers
(recomputed from the committed crosswalk artifact). The unresolved tail is dominated by
causative and derived stems, sandhi compounds, and spelling-normalisation casualties —
lemmatisation products more often than lexical gaps. Read together, the two joins say
something neither says alone: the corpus sees a minority of the dictionary record, but the
dictionary record covers nearly all of the corpus's running text. The dictionaries
over-supply the corpus by design — that surplus *is* the recorded tradition — while the
corpus's own working vocabulary is almost entirely inside the recorded inventory.

### 5.4 Inclusion policy has a measurable price

The evidence-graph framing of this book treats headword inclusion as a claim carrying a
grade, and there is a measured demonstration that the claim has downstream consequences.
The first benchmark of a lexical and part-of-speech tagger for Sanskrit found its
dictionary-derived lexicon burdened by exactly the redundancies this chapter quantifies —
derivable compounds and transparent formations carried as headwords (the benchmark's
worked example is a *suhṛdvākya* whose meaning derives directly from its members),
inflating lexical ambiguity that the tagger then had to resolve (Hellwig 2010). An
inclusion decision taken by a lexicographer in 1872 is, in 2026, a line item in a
tagger's error budget. That is the practical sense in which headword inclusion is a
gradable, reviewable claim rather than a fixed fact of the record — and why this book's
graph attaches evidence, not just existence, to every headword node.

## 6. Discussion: three axes, no single number

Two portraits of the collection emerge from the census, and a third from the union, and
they are mutually irreducible. The **longitudinal** portrait shows growth by accretion
concentrated in a handful of dictionaries — Apte's re-edit and the shorter Petersburg
recension's accumulation drive almost all of the +14.3 % — against frozen canonical
reference points; for anyone re-running a downstream analysis, only a few dictionaries
need re-processing between editions. The **grounding** portrait is orthogonal to size: a
dictionary's attestation rate is a property of what it was built to describe, and
Monier-Williams and the Śabdakalpadruma differ by ~5× in headwords and ~2× in grounding,
in opposite directions. The **uniqueness** portrait qualifies both: because the school
dictionaries are nearly subsumed in the core lineage, headline size overstates diversity
by roughly a factor of five, and because Apte's explosive growth lands mostly in its own
40.3 %-unique inventory, the census's biggest mover is enriching the union rather than
duplicating the core. Growth, grounding, and uniqueness are three independent axes — Apte
is high-growth, low-grounding, high-uniqueness; Grassmann low-growth, high-grounding,
low-uniqueness; the Śabdakalpadruma low-growth, low-grounding, high-uniqueness — and no
single inventory number predicts any of them from the others. A dictionary collection is
better described by a growth profile and a grounding rate, read against its overlap
structure, than by any headline count.

For the book's argument the section titles carry the load. Parts III and IV measure
senses, cross-references, and citations *inside* inventories whose size, movement, and
corpus-visibility are now fixed quantities; when Chapter 13 reads register labels against
corpus absence, or Chapter 11 weighs a citation canon of hundreds of thousands of tagged
citations, the denominators and the witness's limits are the ones stated here and in
Chapter 2 §6 — stated once, inherited everywhere.

## 7. Limitations

- **Format-migrated lists are an encoding artifact, not growth.** Six key2 lists migrated
  from the legacy numeric transliteration to SLP1; their raw ~100 % diff is excluded from
  every growth figure. More generally, count comparability across dictionary generations
  is bounded by normalisation and homonym-key drift between the two extractions; the
  per-list comparable/format-migrated verdict is the census's control for exactly this.
- **The attestation rates are upper bounds** (bare-lemma join, homographs collapsed, no
  inflection), computed against the DCS-2021 denominator; the journal version recomputes
  against DCS-2026 (98,606) with a homograph control. The three denominator figures —
  83,239, 91,406, 98,606 — are distinct objects and are never mixed in one rate.
- **The denominator is model output** (ByT5-Sanskrit lemmatisation), bounding the join
  from both sides.
- **The 2026 side drifts.** The live source is edited daily; the committed census predates
  a single-SHA pin, and the two-headword Apte discrepancy is the visible symptom. The
  direction and magnitude of every headline figure are unaffected; exact counts are quoted
  from the census table.
- **The reverse crosswalk is a pilot.** The 81.4 % resolution figure covers the 13-text
  pilot slice of the DCS-2026 import against the search engine's working key list — a
  floor under both scope and semantics — and is not a full-corpus coverage claim.
- **Corpus-unattested ≠ ghost word.** The unattested stratum includes the legitimate
  lexicographer-transmitted kośa layer; the classification of that stratum, beyond the
  worked companion studies, remains open.
- **PD is censused only at 2014.** The Deccan College dictionary has no csl-orig source
  and is excluded from growth and grounding alike.

## 8. Conclusion

Audited as a set and over time, the digitised Sanskrit headword record is neither a fixed
monument nor an undifferentiated heap. It grows — by +14.3 % across the comparable lists
in twelve years — but almost entirely where active re-editing concentrates, while the
canonical lexica stand still; it sheds headwords mostly as key hygiene, with an
identifiable residue owed entry-level review; it collapses, under the union, to 323,425
distinct keys of which 44.1 % belong to exactly one dictionary, organised around a single
Böhtlingk–Monier-Williams core with principled isolates; and it is corpus-visible in
proportion to each dictionary's purpose, from the Vedic Index's 69.8 % down to the
Śabdakalpadruma's 14.1 % under a stated, bounded join. The inventory layer of the evidence
graph is thereby in place: every headword node carries its dictionary provenance, its
longitudinal standing, and its corpus attestation under Chapter 2 §6's discipline. The
next chapter crosses to the tradition for which none of these instruments was built — the
kośa, where the list is not audited but *composed*, and the inventory question itself
changes shape.

## References

Coward, David F., and Charles E. Grimes. 2000. *Making Dictionaries: A Guide to
Lexicography and the Multi-Dictionary Formatter.* Waxhaw, NC: SIL International.

Hellwig, Oliver. 2010. "Performance of a Lexical and POS Tagger for Sanskrit." In *Sanskrit
Computational Linguistics: Proceedings of the 4th International Symposium* (Lecture Notes
in Computer Science 6465), 162–172. Berlin and Heidelberg: Springer.

Hellwig, Oliver. 2010–. *DCS — The Digital Corpus of Sanskrit.*
[www.sanskrit-linguistics.org/dcs/](https://www.sanskrit-linguistics.org/dcs/) (DCS-2021
attested-lemma list; DCS-2026 release, CC BY).

Huet, Gérard. 2005. "A Functional Toolkit for Morphological and Phonological Processing,
Application to a Sanskrit Tagger." *Journal of Functional Programming* 15 (4): 573–614.

Inglese, Guglielmo, and Ulrich Geupel. 2018. "The Encoding of Ad Hoc Categories in
Sanskrit." *Folia Linguistica* 52 (s39-1) [*Historica* series]: 225–252.

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.
[Thorndike's balanced inventories; data sources as editorial decision.]

Kilgarriff, Adam. 2013. "Using Corpora as Data Sources for Dictionaries." In Howard
Jackson (ed.), *The Bloomsbury Companion to Lexicography.* London: Bloomsbury.

McEnery, Tony, and Vaclav Brezina. 2022. *Fundamental Principles of Corpus Linguistics.*
Cambridge: Cambridge University Press. [Engaged through Chapter 2 §6, whose
absence-inference rule this chapter inherits.]

Nehrdich, Sebastian, Oliver Hellwig, and Kurt Keutzer. 2024.
"[One Model Is All You Need: ByT5-Sanskrit, a Unified Model for Sanskrit NLP Tasks](https://aclanthology.org/2024.findings-emnlp.805/)."
In *Findings of the Association for Computational Linguistics: EMNLP 2024.*

Skeat, Walter W. 1886. "Report upon 'Ghost-Words', or Words Which Have No Real Existence."
*Transactions of the Philological Society* 1885–87 (presidential address).

Szudarski, Paweł. 2018. *Corpus Linguistics for Vocabulary: A Guide for Research.* London
and New York: Routledge.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

**Sibling chapters (this book).** Chapter 2 owns the measurement discipline and the
bounded-witness disclosure this chapter cites (§6.1–§6.3 there); Chapter 4 crosses to the
kośa macrostructure whose digitisation conventions make entry counts non-comparable;
Chapter 9 reads the family's descent in cross-reference graphs, and Chapter 12 puts the
inheritance case to forensic proof — both inside inventories this chapter sizes; Chapter
13 is the worked case of the absence-inference rule on the register-labelled stratum.

*[Data note, 2026-07-18: every figure above is walkable to a committed artifact. The
census and the comparable/format-migrated verdicts:
[NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md)
(generator
[headword_diff.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/headword_diff.py);
frozen snapshots in
[then-2014/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014),
current extraction in
[now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026)).
The union and its provenance distribution:
[union_headwords.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/union_headwords.tsv)
+ [UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)
(builder
[build_union.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/build_union.py)).
The overlap matrix (§4):
[HEADWORD_OVERLAP_UNION15_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/data/HEADWORD_OVERLAP_UNION15_2026.md)
with
[headword_overlap_matrix.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_overlap_matrix.tsv)
and
[headword_unique_counts.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/data/headword_unique_counts.tsv)
— cited, not recomputed. The attestation denominator (§5.2):
[dcs_lemma_summary.json](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json)
(DCS-2021, 83,239 attested SLP1 lemmas, CC BY); the DCS-2026 denominator (98,606) per the
[VisualDCS DCS-data-2026 validation reports](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/README.md).
The reverse crosswalk (§5.3):
[dcs_cdsl_xref.tsv](https://github.com/sanskrit-lexicon/csl-apidev/blob/master/simple-search/dcs_xref/dcs_cdsl_xref.tsv)
with its
[readme](https://github.com/sanskrit-lexicon/csl-apidev/blob/master/simple-search/dcs_xref/readme.md)
(13-text pilot slice of the DCS-2026 import; `in_cdsl` = membership in the engine's `wf0`
working key list — floor semantics; the 94.7 % token-weighted figure recomputes from the
committed TSV's `token_count` column). No dataset cited in this chapter carries a minted
DOI at the time of writing; the data-release program is tracked in the book's plan of
record.]*

_Dr. Mārcis Gasūns_
