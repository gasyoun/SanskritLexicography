# Chapter 13 — Register, Not Just Period: Renou's Subsections as an Orthogonal Axis

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the research note *Register, Not
> Just Period: Renou's Subsections as an Orthogonal Axis for Evidence-Graded Sanskrit
> Lexicography* (source draft:
> [A34_renou_register_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md)),
> which is being published separately in a journal version (target: *Lexikos* / *IJL* / *eLex*);
> where the article must remain independently citable, cite that version. Every count and table
> below is carried over from the article unchanged. Only the framing has been converted from
> journal to book form — the abstract and status apparatus removed, the companion-paper label
> remapped to this book's chapters, the headline "68.3 % corpus-absent" figure reframed as an
> explicit statement about *DCS-corpus coverage* per the corpus-absence caveat, and the
> comparative register literature engaged at the monograph's depth. Section numbering is
> chapter-internal (§1–§5).

The book's final movement turns from descent to the *living* dictionary — the labels by which
an entry marks what kind of Sanskrit a word belongs to. This chapter adds a second, orthogonal
badge to the evidence graph. Digital work routinely reduces Louis Renou's *Histoire de la
langue sanskrite* to five language-states — Vedic, Pāṇinian, Epic, Classical, Buddhist/Jaina —
and treats them as a period scale. But Renou's chapters are themselves divided into
subsections that are **registers, not periods**: the commentarial *bhāṣya* opens the Classical
chapter and is given its own grammar; *le sanskrit épigraphique* is filed inside the
Pāṇinian-norm chapter as a witness to real attested usage against the grammarians' ideal. A flat
I–V period tag cannot express either. This chapter operationalises both axes — a diachronic
*state* axis and an orthogonal, multi-label *register* axis — as two independent per-sense
badges, each carrying its evidential provenance.

The chapter is the direct heir of Chapter 10. There the citation *register* was a property of
the dictionary's evidential practice (the European `<ls>` apparatus versus the indigenous
*iti*-quotation); here Renou's *language* registers become a per-sense annotation axis on the
same evidence graph. And its headline result rhymes with the book's recurring theme that the
instrument shapes what is seen — but with a crucial reframing that this chapter is careful to
make: of 709 headwords tagged *épigraphique*, 484 have **no attestation in the DCS literary
corpus**. Read naively that is a claim about the words; read correctly it is a statement about
the *corpus's coverage* — and the register axis exists precisely to make that coverage boundary
measurable rather than invisible.

## 1. The problem: register cross-cuts period

Diachronic tagging of Sanskrit lexicon entries has converged on Renou's five states, treated as
a period scale. This is useful but lossy in a specific way: register cross-cuts period. A
commentary (*bhāṣya*) can gloss a Vedic, epic, or classical base text; its language — terse,
formulaic, meta-textual — is a register of its own that does not reduce to "Classical."
Inscriptional Sanskrit is, for Renou, not a period at all but a documentary *witness*,
deliberately placed beside the discussion of the spoken norm. The Classical chapter alone holds
four distinct registers (*bhāṣya*, *kathā* narrative, the *théâtre* dialogue, *kāvya* poetry),
and the Pāṇinian-norm chapter hosts the épigraphique witness. None of these is a fifth, sixth, or
seventh *state*; they are an orthogonal dimension.

Register labelling is not a Sanskrit novelty but a lexicographic universal, and naming its
precedents places this chapter's contribution precisely. The classical grammarians already
sorted usage by register: Servius' scholia grade diction as *grandiloquus / medius / humilis*
(Ferri 2019, essay by Maltby) — the same three-register decorum system whose *sexual* extreme
opened this book in Chapter 1 — and the Atticist lexica of Greek marked usage normatively,
admitting or proscribing words by register (Dickey 2007). The modern counterpart is
*diasystematic* labelling — the temporal, regional, and stylistic marks a dictionary attaches to
a sense — now increasingly derived from corpus metadata rather than editorial intuition (Geyken
and Lemnitzer 2009), and its informal end has a lexicographic pedigree in Partridge's graded
slang/colloquial/vulgarism scales (Partridge 1963). What is new here is the operationalisation of
Renou's *subsections* — as opposed to his five chapter-states — as a multi-label tagging scheme
over a dictionary corpus, each tag provenance-graded.

## 2. Method: two independent axes, each provenance-graded

I tag every dictionary sense on **two independent axes**, each multi-label (a word can carry
several values) and each value carrying a provenance set:

- **State (I–V)** — Renou's five chapters, from three deterministic signals plus a tertiary one:
  the entry's own `<ls>` citation resolved through a curated siglum→state map; DCS-corpus
  attestation (each text typed to a state by genre/name/date); Edgerton's BHS set membership for
  state V; and a partial tradition tag.
- **Register** — a 20-code lattice of Renou's subsections, built from the same two primary
  signals plus dedicated detectors: a genre/name→register map over the corpus texts (commentary
  caught by name-stems `*bhāṣya/ṭīkā/vṛtti/vārttika`, since the corpus has no commentary
  *genre*); the `<ls>` siglum's source genre (the only route to *jaina*); and a dedicated
  **épigraphique detector** — an inscription marker (PWG German `Inschr.`, MW/Apte `Inscr.`)
  inside any citation, the sole route to a register the corpus contains none of.

Both axes share one noise-control policy. The corpus index is *lossless* — it stores, per lemma,
the per-state and per-register evidence depth — and a min-support filter is applied at tagging
time: a corpus state is kept only if attested in ≥2 texts *or* in one authoritatively-typed
text, pruning the thin date-fallback tail (9.9 % of corpus state-assignments). The two axes are
kept in disjoint vocabularies and separate fields; an independent data-integrity audit confirmed
entry-count invariance, provenance coherence, and zero leakage between axes. This is the
per-sense operationalisation of the book's evidence-grade discipline (Chapter 2): every tag
carries whether it rests on a lexicographer's citation, a corpus attestation, or a register
membership. The substrate is eight machine-readable Cologne dictionaries (PWG, MW, PW, AP, AP90,
BEN, SCH, BHS) — **770,292 entries** — and the DCS 2026 corpus snapshot.

## 3. Results

### 3.1 Coverage

The register axis is populated across all eight dictionaries (~38–41 % of all entries carry ≥1
register; 100 % for BHS, every entry being Buddhist by construction). The commentary register is
large and robust — *bhāṣya* tags **14,498 distinct headwords** (10,320 attested in ≥2
dictionaries); the poetic and Buddhist lexica reach 26,973 (*kāvya*) and 25,740 (*bauddha*).
Nineteen of the twenty lattice registers are populated; only *hors-de-l'Inde* (Sanskrit abroad)
is empty, having no source in either signal.

### 3.2 The headline: épigraphique is largely invisible *to this corpus*

Of **709 headwords tagged épigraphique, 484 (68.3 %) have no attestation in the DCS literary
corpus** (the conservative reading; the strict corpus-only reading gives 518, 73.1 %). The
figure must be read for exactly what it is — a statement about **corpus coverage**, not about the
language. It does not say these words are absent from Sanskrit; it says they are absent from *the
DCS as it currently stands*, which is a curated corpus of *literary* texts and contains, by
construction, no inscriptions. The corpus-absence caveat of corpus linguistics applies at full
strength: absence of a form from a bounded corpus is not evidence of its absence from the
language, because low frequency and true non-occurrence are indistinguishable in a finite sample
(McEnery and Brezina 2022). For the épigraphique register that caveat is not a weakness to be
apologised for but the very point being measured: these are words the *literary* corpus
structurally cannot contain, recoverable only because the lexicographers preserved the
inscription citation.

| Register | Distinct headwords | Corpus-absent (no DCS attestation) |
|---|--:|--:|
| **épigraphique** | **709** | **484 (68.3 %)** |
| jaina | 286 | 0 |
| bhāṣya | 14,498 | (corpus-rich) |

These are the words a corpus-only diachronic method never sees: donative and administrative
terms (*akṣayanīvī* "perpetual, non-confiscable endowment"), monastery names
(*abhayagirivihāra*), and above all the dynastic onomasticon engraved in stone (*ajayavarman*,
*akkādevī*, *akabara* = Akbar). The contrast with *jaina* (0 % corpus-absent — Jaina-tagged words
are literary words MW happens to cite from Jaina sources) sharpens the point: épigraphique is the
one register whose vocabulary lies *outside the literary timeline*, and a word attested only in an
undated inscription has no well-defined Renou state yet a perfectly definite register. The state
axis, by construction, cannot see it; the register axis can.

### 3.3 Composing the two axes

Because state and register are orthogonal, their intersection and difference define editorially
meaningful strata that neither axis alone can name:

| Slice | Definition | Headwords | What it is |
|---|---|--:|---|
| Vedic-in-commentary | register `bhāṣya` ∩ state I | 6,895 | Vedic vocabulary the commentarial tradition kept alive |
| born-in-kāvya | register `kāvya` ∖ state I | 20,758 | poetic words with no Vedic attestation (*abdhi* "ocean", III·IV only, vs Vedic *samudra* I–V) |
| pure archaisms | state I only | 25,220 | words dropped after the Saṃhitās |

The full coordinate per sense is `(state, register, provenance)` — e.g. *akṣobhya* = `III·V` /
`purāṇa·tantra·bauddha` / all-signals — an evidence-graded position, not a single label. The
*bhāṣya* register works as a Vedic reservoir, *kāvya* as a coinage engine (≈¼ of the
born-in-kāvya slice is dictionary-specific), and the inscription-only onomasticon (*vākāṭaka*,
*humāuṃ* = Humāyūn) is register in the *absence* of period.

### 3.4 Register quality rides on provenance, not on a frequency gate

The min-support filter that prunes the state axis is, on the register axis, a no-op by
construction: a register only ever derives from a *typed* source (a corpus genre, a curated
siglum, an inscription marker), so no register rests on the low-confidence date-fallback texts
that produce state-axis noise. Register quality therefore rides on the genre/name confidence
floor, not on a frequency gate — a result of the audit, not an assumption, and the reason the
épigraphique figure is a coverage statement rather than a noise artefact.

### 3.5 Further register findings

Beyond épigraphique, four register-metric results follow. (i) *bhāṣya* is a cross-disciplinary
*syntactic* register — Renou's own thesis (the nominal doctrinal style applied across all
disciplines) corroborated by its low 8.8 % dictionary-specificity, a standardised not
idiosyncratic vocabulary. (ii) *bauddha* is a second self-contained lexical world — 44.5 %
single-dictionary, 92 % of that recorded only by Edgerton's BHS, 12.4 % corpus-absent — a
parallel to épigraphique by a different mechanism. (iii) The doctrinal registers carry the
perennial lexicon (kārikā/tantra/upaniṣad, 56.7–65.0 % of headwords spanning ≥4 states) while
narrative/poetic/documentary registers are period-bound (épig/epic/kāvya, 10.0–22.2 %). (iv)
*nāṭya* and *kāvya* are the coinage registers among the literary ones (dictionary-specificity
23.8 % and 19.8 %), the śāstric ones the standardising — conservation vs invention, read
straight off the register metrics.

A fifth result steps off the headword axis onto running text: Renou's nominal-style thesis is
confirmed on the DCS corpus — finite-verb density more than halves across the states (Vedic
14.4 % → Classical 6.7 %) as participles and nominals rise, and **bhāṣya (6.25 %) is more nominal
than kāvya (7.48 %)**, the exact wording of *Histoire* p. 139 — corroborating the *bhāṣya*
finding from a second, syntactic direction.

## 4. Consequence

For an evidence-graded digital dictionary the register is a second per-sense badge, independent
of the period badge, and the two compose into a queryable coordinate rather than a flat label —
the same "language of the gloss encodes the editor's stance toward the reader" axis this book
opened with in Chapter 1, now generalised from candour to the full diasystem. Two concrete
payoffs follow. First, **reusable register lexica**: eight deduplicated, provenance-tagged
glossaries ship with the study, the épigraphique list positioned as a *derived,
provenance-tagged complement* to Sircar's corpus-curated *Indian Epigraphical Glossary* (1966) —
where Sircar curated inscriptional vocabulary from the epigraphic corpus directly, this list
recovers it from the lexicographers' citation apparatus, so the two can validate each other.
Second, **honest negative coverage**: the 68.3 % corpus-absent figure is itself a finding about
the limits of corpus-driven lexicography, and the register tagging makes that gap *measurable*
instead of invisible — the épigraphique stratum is exactly the material Chapter 3's
corpus-grounding of the headword inventory cannot reach, named here rather than silently dropped.

## 5. Reproducibility

The tagger, resolvers, audit, glossary extractor, and the eight shipped glossaries are committed
alongside the study; the derived per-dictionary indices are regenerated by the pipeline, and the
headline 68.3 % corpus-absent figure reproduces exactly from the committed indices (superseding an
earlier stale 63.0 % hand-copy in one findings table). Every reported number is walkable to its
generator under the discipline of Chapter 2.

## References

Dickey, Eleanor. 2007. *Ancient Greek Scholarship.* Oxford and New York: Oxford University
Press. [Atticist lexica and normative register-marking.]

Edgerton, Franklin. 1953. *Buddhist Hybrid Sanskrit Grammar and Dictionary.* 2 vols. New Haven:
Yale University Press.

Ferri, Rolando (ed. contributions). 2019. In Robert Maltby et al. (eds.), *Studies on Late
Antique and Medieval Latin Glossaries and Dictionaries.* [Maltby on Servius' three-register
(*grandiloquus/medius/humilis*) system.]

Geyken, Alexander, and Lothar Lemnitzer. 2009. "Diasystematic Labelling from Corpus Metadata."
In *Internet Lexicography.* [Corpus-derived register/temporal/regional labelling as current
practice.]

Hellwig, Oliver. 2010–. *DCS — The Digital Corpus of Sanskrit.*
[www.sanskrit-linguistics.org/dcs/](https://www.sanskrit-linguistics.org/dcs/) (2026 snapshot).

McEnery, Tony, and Vaclav Brezina. 2022. *Fundamental Principles of Corpus Linguistics.*
Cambridge: Cambridge University Press. [The corpus-absence caveat: non-occurrence in a bounded
corpus is not absence from the language.]

Partridge, Eric. 1963. *The Gentle Art of Lexicography.* London: Deutsch. [Graded
slang/colloquial/vulgarism register scales.]

Renou, Louis. 1956. *Histoire de la langue sanskrite.* Lyon–Paris: Éditions IAC.

Salomon, Richard. 1998. *Indian Epigraphy: A Guide to the Study of Inscriptions in Sanskrit,
Prakrit, and the Other Indo-Aryan Languages.* New York: Oxford University Press.

Sircar, Dineschandra. 1966. *Indian Epigraphical Glossary.* Delhi: Motilal Banarsidass.

Vogel, Claus. 1979. *Indian Lexicography.* (A History of Indian Literature V.4.) Wiesbaden:
Harrassowitz.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/) — the eight
machine-readable dictionaries (PWG, MW, PW, AP, AP90, BEN, SCH, BHS) tagged here, with the DCS
2026 corpus snapshot as the state/attestation substrate.

_Dr. Mārcis Gasūns_
