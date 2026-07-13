# Chapter 12 — Apparatus, Not Errors: How Monier-Williams Inherited the Petersburg Lexicon

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Apparatus, Not Errors:
> How Monier-Williams Inherited the Petersburg Lexicon* (source draft:
> [article_21_apparatus_not_errors.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md)),
> which is being published separately in a journal version (venue: *Digital Scholarship in the
> Humanities*); where the article must remain independently citable, cite that version. Every
> count and table below is carried over unchanged and regenerable from the committed forensic
> suite
> ([`scripts/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/scripts/forensic),
> [`data/forensic/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/forensic)).
> Only the framing has been converted from journal to book form — the abstract folded into the
> opening, companion-paper labels remapped to this book's chapters, and the stemmatic and
> comparative literature engaged at the monograph's depth. Section numbering is chapter-internal
> (§1–§7).

This is the chapter where the book's descent argument is put to its hardest test. Chapters 9
and 10 established, on the cross-reference graph and the citation apparatus, that the Sanskrit
dictionaries are *related* and that relatedness must be calibrated and cleaned before it earns a
copying claim. Here I take the single most-alleged inheritance in the whole family — that
Monier-Williams built his 1899 *Sanskrit-English Dictionary* on Böhtlingk and Roth's
*Großes Petersburger Wörterbuch* — and ask not *whether* but *how* he inherited, with the full
apparatus of textual stemmatics brought to bear. That the later dictionary rests on the earlier
is, in itself, no discovery: it is a lexicographic truism that "all dictionaries are based on
preexisting works" (Jackson 2002; Landau 2001), and the field even has a name for the forensic
study of such genetic affiliation — *dictionary archaeology* (Hartmann and James 1998). What is
new is the *decomposition and the measurement*: separating three distinct senses of "copied,"
quantifying each at corpus scale, and reaching a verdict precise enough to be wrong.

The verdict is a distinction the raw containment numbers cannot draw. Monier-Williams inherited
Böhtlingk's **apparatus** — which words to enter, which texts to cite and *in what order*, how
to divide homonyms — but **not** his mechanical errors and not his prose. He is, in the
chapter's phrase, heir of the scholarship and author of the prose. The result also settles a
loose end from the book's method chapter: the size-confounded "MW absorbed 89–94 % of PWG"
reading (Chapter 2, §3.1, the containment-is-a-floor rule; the raw stemma of the redundancy
material now folded into Chapter 9) is resolved here into a defensible statement about *what
kind* of inheritance the number reflects.

## 1. The question: three senses of "copied"

"MW copied Böhtlingk" can mean three different things: (i) MW reproduced the *headword
inventory*; (ii) MW reused the *citation apparatus*; (iii) MW carried over Böhtlingk's *errors*.
Only (iii) — a shared mistake — is decisive proof of copying in classical stemmatics. This is
the Lachmann common-error principle: a correct reading can be reached independently, but the
same error is near-impossible to invent twice (Maas 1958; West 1973; for its digital extension,
Andrews and Macé 2013), and it is the same comparative-method logic — shared innovation, not
shared retention, is what subgroups a family — that Chapter 9 borrowed for the cross-reference
graph. The three claims are routinely conflated; I separate them and test each on its own
signal.

The concealment of borrowing that makes this a *forensic* rather than a bibliographic question
is not peculiar to Sanskrit or to the nineteenth century. The Arabic lexicographical tradition
records a millennium of documented and *concealed* inheritance — Ibn Manẓūr absorbing much of
Ibn al-Athīr's *Nihāya* into the *Lisān al-ʿArab* "without mentioning him as his source"
(Baalbaki 2014) — and the humanist Latin dictionaries grew by open accretion, each edition of
Calepino's *Dictionarium* swelling into Estienne's *Thesaurus* (Ferri 2019, essay by Furno).
Even the ancient scholia had an explicit technology for layering inherited material: the Homeric
*Viermännerkommentar* stacked four commentators' notes with a recorded source-precedence
ordering — a pre-digital layered evidence graph (Dickey 2007). Reading the MW–Petersburg
relation as one instance of that general phenomenon is what keeps the chapter's forensics from
reading as an accusation; inheritance is the genre's normal condition, and the interesting
question is always its *kind*.

## 2. Method — a ladder of language-neutral signals

MW is English; PWG and PW are German. Gloss prose is therefore a weak, cross-lingual channel;
the load is carried by signals that survive translation — headword sets, citations (`<ls>`
tags), and homonym structure. Each signal is calibrated against a *null* of demonstrably
unrelated dictionaries (e.g. the Buddhist Hybrid Sanskrit dictionary, Edgerton 1953; the
indigenous Śabdakalpadruma and Vācaspatya are excluded from the citation analysis because they
cite in the untagged *iti*-register of Chapter 10, not for lack of citations). This is the
forensic-linguistics logic of authorship fingerprinting — measure the features an imitator
cannot help sharing, against a baseline of the unrelated — applied to dictionaries rather than
disputed texts (cf. the forensic methods surveyed in O'Keeffe and McCarthy 2010).

**Table 1 — The ladder of signals.**

| Signal | What it measures |
|---|---|
| headword containment, size-corrected (L0.8) | shared inventory, de-confounded |
| **F1** citation overlap | shared apparatus |
| **F2** homonym-split concordance | shared structure |
| **F3** gloss-length tracking | translation of prose |
| **F5** citation-order agreement | worked *from* the article |
| **F6** gloss DE→EN (offline MT) | prose translated? |
| **F4b** shared-error test | copied *mistakes* |

## 3. What MW inherited — the apparatus

**3.1 Headword inventory.** Raw containment is size-confounded (it is *highest*, 0.94, for the
unrelated tiny Bopp glossary, because MW's 194k lemmas trivially contain any small dictionary's
common core — the very confound Chapter 2, §3.1 warns is a floor, not proof). The size-corrected
**rare-lemma containment** — the fraction of a source's *rare* headwords (document-frequency ≤ k
across 41 dictionaries) recurring in MW — inverts that ranking and isolates descent: PWG→MW 0.70
(df≤3) / 0.82 (df≤5), PW→MW 0.71, MW72→MW 0.57, against the unrelated Bopp→MW at 0.35.
**17,007 headwords occur in only MW and PW** in the entire corpus.

**3.2 Citation apparatus (the strongest signal).** Both traditions tag references with `<ls>`.
MW shares a per-lemma citation **source-Jaccard of 0.16–0.19** with PWG/PW, versus **0.004
(BHS) – 0.017 (Apte)** for the unrelated nulls — a 9.5–49× separation. Intermediate values
(Benfey 0.10, Grassmann 0.04) sit between lineage and null, consistent with Benfey's own
Petersburg exposure. **587 rare exact references are shared for the *same headword*** — each
attested at ≤4 lemmas corpus-wide, 203 of them occurring nowhere else in the corpus at all
(e.g. `ullApya → SĀH. 545`, `dAsatA → VEṆĪS. 175`, `granTakAra → VEDĀNTAS. 1`, all three
corpus-unique) — plus 565 exact Harivaṃśa line-numbers. MW further reduces Böhtlingk's full
verse references to a bare sigil **41,552 times** — a directional PWG→MW compression. The method
self-validates: it ranks known same-apparatus pairs at the top (PW/PWKVN 0.87, SCH/PW 0.62,
AP/AP90 0.76) and the nulls at the floor.

**3.3 Homonym structure.** On the discriminative *deep* (3+) homonym splits, MW matches the
Petersburg divisions 64–77 % of the time (MW/PWG 65 %, MW/PW 64 %, MW/MW72 77 %) versus ~32–36 %
for index-type nulls; the same-author PW/PWG ceiling is 81.5 %. Homonym division is partly
linguistically forced, so this corroborates rather than proves.

**3.4 Citation order — MW worked *from* PWG's articles.** Sharing *which* texts to cite (§3.2)
is consistent with merely using the same sources; sharing their *order* is not. Over 3,593
shared headwords for which both works cite ≥3 common sources, MW reproduces PWG's citation
**sequence** at **0.811** concordance, with **47.8 % of entries in perfectly identical order** —
against a random baseline of 0.50 concordance and only ~5–17 % chance-identical for k≥3 sources
(a 3–10× excess). For *droṇa*, both cite MBH · YĀJÑ · SUŚR · HARIV · VP in that order; for
*pratikartavya*, MBH · HARIV · ŚAṂK · R · PRAB · SUŚR (six sources, identical sequence — random
odds 1/720). The effect is Petersburg-*specific*: agreement falls monotonically with distance
from the tradition — PWG 0.81 > PW 0.73 > Benfey 0.68 (itself Petersburg-influenced) > the
independent Apte 0.42. MW did not merely consult Böhtlingk's sources; it assembled its entries
*following Böhtlingk's entry*. This is the strongest single copying signal in the suite, and it
is structural, not lexical — the dictionary-archaeology analogue of the *Viermännerkommentar*'s
recorded ordering (§1).

## 4. What MW did *not* inherit — the errors

**4.1 The decisive test.** A scholar-curated list (compiled by M. Ahlborn with P. Scharf and
J. Funderburk, 2011; extracted 2014) records 123 PWG headword spelling errors, several with MW's
form for the same word. **MW carries the PWG error in 2 of 123 cases (1.6 %)** — and both
(`asUya/asUy`, `vara/var`) are root-vs-stem citation conventions, not misspellings, so the
genuine figure is ≈ **0 %**. Where PWG erred, MW has the *correct* form (90 cases) or simply
lacks the word (31). The inheritance is independent of typesetting accidents.

**4.2 The null-test trap.** A naïve corpus null is misleading here: headwords corrected in
*both* a Petersburg dictionary and MW number 256 against 102.8 expected by chance — a lift of
**2.49** (hypergeometric p ≈ 4×10⁻⁴¹). Taken alone this *looks* like shared errors. It is not:
it is the *same hard words* attracting corrections in both works, with **different** errors in
each — convergence on difficult vocabulary, compounded by the editorial coupling of the Cologne
correction workflow. The direct test (4.1) settles what the null cannot.

**4.3 Corroboration — the prose is MW's own.** MW and PWG share **zero** documented print
errors. And MW's English gloss *length* tracks PWG's German no more than it tracks Apte's
independent English (Spearman 0.564 vs 0.576; differential −0.01) — MW recomposed the
definitions rather than translating Böhtlingk's prose. A direct test confirms it: translating
PWG's German gloss to English (offline MT) and measuring token overlap, MW resembles
translated-PWG *no more than the independent Apte does, in any stratum* — overall 0.104 vs
0.129, verb-root 0.044 vs 0.098, philosophical 0.086 vs 0.086 (against a random-pair floor of
~0.0005). The ~0.1 overlap is convergence on the fixed Sanskrit meaning, not derivation: even
philosophical terms sit at exact parity, and MW's terse verb-root glosses track PWG *least*. The
prose is MW's own throughout.

## 5. Discussion

The signals converge on one statement: **MW is a structural copycat of Böhtlingk's apparatus and
an independent typesetting.** It worked *from* the Petersburg articles — reproducing not only the
lemma inventory and the textual loci but their *order* within the entry (§3.4), the surest sign
that the German article lay open on the desk — yet it composed its own English prose and carried
over none of the German edition's mechanical errors. Heir of the scholarship, author of the
prose. This is the forensic complement to the convention-versus-content decomposition of
Chapter 9: MW absorbed the Petersburg *content* while recoding its *conventions*, and a
dictionary can inherit an apparatus wholesale yet share neither its house style nor its errors.

The methodological moral generalises the whole descent argument of the book. "Did X copy Y"
should be decomposed into inventory / apparatus / error descent and tested separately — the
apparatus signal (here, very strong) and the error signal (here, null) need not agree, and their
disagreement is the actual historical fact. That the field already calls this *dictionary
archaeology* is the point: what the classical study of copying in this very family established
by hand-picked probes (Zgusta 1988, carried into the book's method chapter) is here measured at
corpus scale, which is exactly M01's delta over the truism that dictionaries inherit.

## 6. Limits — and the decisive test, run to ground

The curated error sample is small (123) and weighted toward scan-era artefacts a
separately-keyed MW could not share in any case. And the citation result, however strong, proves
shared *sources/editions*, not yet a shared *mistake*: independent use of the same edition can
match. The airtight upgrade, in classical stemmatic terms, would be a shared *erroneous*
citation — a verse number wrong against the actual text, present in both dictionaries. I ran
that test twice, against the two corpora available.

**Against the DCS corpus the test is structurally blocked.** Of the 587 shared rare citations,
only **1** resolved to a DCS locus: 96 % are Harivaṃśa references, cited by the Petersburg
dictionaries in the Calcutta-vulgate continuous śloka numbering (running to 16,291), while DCS
carries the critical edition (118 chapters, ≈6,073 verses). 298 references provably exceed the
entire DCS Harivaṃśa. Nor would a vulgate↔critical concordance unblock it: a concordance maps a
vulgate address to a critical one *on the assumption the address is correct* — the very
proposition under test — so an erroneous citation and a correctly-cited vulgate-only verse both
emit "not found." The test requires the vulgate itself.

**Against the vulgate itself, the shared citations verify as correct.** I therefore resolved the
Harivaṃśa references directly against the Calcutta vulgate the Petersburg dictionaries actually
cite, using a free vulgate e-text (Kinjawadekar, Chitrashala 1936; 15,364 verses = 93.8 % of the
16,374-śloka vulgate). A per-adhyāya continuous index fitted on 14,471 PWG anchors and validated
on 815 held-out MW anchors (68.4 % land within ±3 of their cited śloka vs a 2.1 % shuffled-N
null, ≈33×) is trustworthy. Of the **565** shared rare Harivaṃśa citations, **206 (37.7 %)
corroborate at the exact cited vulgate śloka** (e.g. `kīrtimant HARIV. 62` → verse 1-2-9
*…kīrtimantaṃ ca…*) against a **0.5 % shuffled-N null — a ≈75× enrichment**. This upgrades the
citation evidence from *shared editions* to a **shared, verse-level, verifiably-correct
apparatus.** The *airtight* upgrade — a shared *erroneous* citation — is **not** obtained, and
the reason is positive rather than circumstantial: displaced cases fall *below* their shuffled-N
null (79 vs 200) with no clustering, so against the correct edition the shared citations verify
as correct and there is **no shared error to find** in this pool. The shared-mistake signal is a
measured null, not a data-availability block.

The verdict therefore stands at "very strong, not airtight" — the apparatus overlap, the
citation-order agreement, and the direct verse-level corroboration — with the common-error coup
unavailable precisely because the shared apparatus is accurate. It is a fitting outcome for a
book about evidence grades: the strongest positive evidence of copying and the absence of the
one signal that would make it airtight are, here, the *same fact* — MW copied an apparatus good
enough to leave no error behind.

## 7. Reproducibility

All figures regenerate from the forensic and content-lift scripts over the canonical `csl-orig`
source, the CDSL corrections corpus, and the headword snapshot; per-run provenance travels in
`.source.json` sidecars beside each dataset, and every reported number is walkable to its
generator under the discipline of Chapter 2.

## References

Andrews, Tara L., and Caroline Macé. 2013. "Beyond the Tree of Texts: Building an Empirical Model
of Scribal Variation through Graph Analysis of Texts and Stemmata." *Literary and Linguistic
Computing* 28 (4): 504–521.

Baalbaki, Ramzi. 2014. *The Arabic Lexicographical Tradition: From the 2nd/8th to the 12th/18th
Century.* (Handbook of Oriental Studies 1.107.) Leiden and Boston: Brill.

Dickey, Eleanor. 2007. *Ancient Greek Scholarship.* Oxford and New York: Oxford University
Press.

Ferri, Rolando (ed. contributions). 2019. In Robert Maltby et al. (eds.), *Studies on Late
Antique and Medieval Latin Glossaries and Dictionaries.* [Furno on the Calepino → Estienne
humanist-accretion chain.]

Hartmann, R. R. K., and Gregory James. 1998. *Dictionary of Lexicography.* London and New York:
Routledge. [The term "dictionary archaeology" for genetic-affiliation forensics.]

Jackson, Howard. 2002. *Lexicography: An Introduction.* London and New York: Routledge.

Landau, Sidney I. 2001. *Dictionaries: The Art and Craft of Lexicography.* 2nd ed. Cambridge:
Cambridge University Press. ["All dictionaries are based on preexisting works."]

Maas, Paul. 1958. *Textual Criticism.* Trans. B. Flower. Oxford: Clarendon Press.

O'Keeffe, Anne, and Michael McCarthy (eds.). 2010. *The Routledge Handbook of Corpus
Linguistics.* London and New York: Routledge. [Forensic-linguistics fingerprinting methods.]

West, Martin L. 1973. *Textual Criticism and Editorial Technique.* Stuttgart: Teubner.

Zgusta, Ladislav. 1988. "Copying in Lexicography: Monier-Williams' Sanskrit Dictionary and Other
Cases (Dvaikośyam)." *Lexicographica* 4: 145–164.

**Primary sources.** Böhtlingk, O. & Roth, R. (1855–1875). *Sanskrit-Wörterbuch* [PWG].
St. Petersburg. Böhtlingk, O. (1879–1889). *Sanskrit-Wörterbuch in kürzerer Fassung* [PW].
Monier-Williams, M. (1872, [MW72]; 1899, [MW]). *A Sanskrit-English Dictionary.* Oxford:
Clarendon Press. Edgerton, F. (1953). *Buddhist Hybrid Sanskrit Grammar and Dictionary* [BHS].
New Haven. All consulted in the machine-readable editions of the **Cologne Digital Sanskrit
Dictionaries (CDSL)**, Universität zu Köln,
[`www.sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/), with the
CDSL corrections corpus (`CORRECTIONS`, `csl-corrections`) used throughout §4.

_Dr. Mārcis Gasūns_
