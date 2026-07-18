# Chapter 11 — What the Tradition Cites: The Citation-Frequency Graph

_Created: 18-07-2026 · Last updated: 18-07-2026_

> **Provenance.** This chapter is the book-form version of the study *What the Sanskrit
> Lexicographic Tradition Cites: A Citation-Frequency Graph of `<ls>` Source Tags across
> 11 Cologne Dictionaries* (source draft:
> [A50_ls_citation_frequency_graph.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/A50_ls_citation_frequency_graph.md)),
> which is being published separately in a journal version; where the article must remain
> independently citable, cite that version. Every count, table, and statistic below is
> carried over unchanged from the committed dataset
> ([`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations)
> in the atlas repository); only the framing has been converted from journal to book form.
> Two standing disclosures govern the chapter. First, it is written to the
> statistical-practice contract of Chapter 2 §6.3 from the first figure — at this
> chapter's scale, effect sizes with dispersion and explicit denominators do the
> evidential work, and a significance statistic appears only beside its effect size and
> its N. Second, the text→tradition map that names the citation communities in §4 is
> **inferred, not reviewed**: as of 18-07-2026, zero of its 119 rows have passed the human
> review gate of Chapter 2 §4, and every community name below is written and read under
> that status. Section numbering is chapter-internal (§1–§6).

Chapter 10 established that the corpus holds two citation registers and that no citation
statistic is well-defined until the register is named. This chapter stays inside the
register that can be aggregated — the European tagged apparatus — and asks the question
those denominators make answerable: **what does the Sanskrit lexicographic tradition
actually cite?** Aggregated over the family's largest citation dataset, the answer is the
citation-frequency graph: the dictionary family's collective bibliography, the measured
shape of its textual canon — which authorities carry the record, how steeply their use
falls away, and how differently the dictionaries weight them. The finding is a negative
with structure: the "canon of Sanskrit literature" implied by the dictionaries is not one
canon at all.

## 1. Introduction

A bilingual dictionary of a classical language is, among other things, a compressed claim
about a corpus: *these* are the texts worth excerpting, and *this* is how often each one
settles a question of meaning. For Sanskrit, the great nineteenth-century dictionaries
made that claim explicit on every page — Böhtlingk and Roth's *Sanskrit-Wörterbuch* alone
carries over 800,000 source citations. The Cologne digitisations preserve these citations
as `<ls>` tags, each wrapping the lexicographer's own abbreviation for the work cited
(`<ls>MBH. 7,9283</ls>`, `<ls>Spr. 2790</ls>`). Read across dictionaries, the tags form a
bipartite citation network — dictionary × cited text — that lets a question usually
answered by impression be answered by measurement.

Two sub-questions structure the chapter, and they are topologically distinguishable.
*Is there a shared canon* — a core set of texts every lexicon leans on, with idiosyncratic
authorities as decoration? Or *do the dictionaries partition into citation communities* —
Vedic, classical-kāvya, Buddhist — whose overlap is thinner than the "one tradition"
framing suggests? A shared canon predicts a *nested* matrix: dictionaries citing few texts
cite subsets of what broader dictionaries cite. Communities predict a *modular* one:
blocks of texts private to groups of dictionaries. §4 tests both against
degree-preserving nulls.

The comparative frame sharpens what is at stake. The European habit of citing from a
bounded authority list is ancient — Chapter 10 introduced Nonius Marcellus's fixed roster
of some forty *auctores*, cited in the regular order Lindsay codified (Ferri 2019, essay
by Gatti) — and the instructive contrast is one of closure. Nonius's canon was closed by
design: a finite reading list, known in advance, constitutive of the work. The Sanskrit
dictionaries' collective bibliography, measured below, is an *open* graph of 912 resolved
text identities in which no text reaches all eleven dictionaries and two-thirds of the
nodes are private to a single lexicon. The asymmetry is real and should not be
flattened — a designed forty-author roster and an emergent 912-node citation field are
different objects — but precisely that difference is the finding: the "tradition" cited
by these dictionaries is a union of school reading lists, not a Nonius-style canon scaled
up.

Within the book, the chapter's lane is fixed by its neighbours, and the anti-salami
discipline of the plan of record applies. Chapter 10 owns the *registers* — citational
versus grammatical quotation, `<ls>` versus *iti* — and supplies the volume denominators
this chapter's shares divide; it is not re-derived here. Chapter 12 owns the *forensic*
use of citations — shared-rare and shared-erroneous citations as descent evidence between
specific dictionary pairs. This chapter is the *frequency* layer neither covers:
whole-tradition counts, not pair-level fingerprints. Methodologically, the topology test
imports standard bipartite-network measures — NODF nestedness (Almeida-Neto et al. 2008)
and Barber's (2007) bipartite modularity — under the permutation-testing discipline
argued for language data by Dror et al. (2018). On the lexicographic side, the
descriptive inventories of the Sanskrit dictionary tradition characterise each
dictionary's sources qualitatively (Vogel 1979; Zgusta 1971 for the general theory); a
quantitative citation census across the Sanskrit dictionaries has, to my knowledge, no
predecessor.

## 2. Data and method

**Source.** The dictionary digitisations in
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig), the per-dictionary
abbreviation keys in
[`abbreviations.json`](https://github.com/sanskrit-lexicon/csl-guides/blob/main/src/data/abbreviations.json),
and the committed builder
[`build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py);
full method detail and change log in the dataset's
[README](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md).

One extraction note reconciles this chapter's totals with its predecessor's. The graph
builder reads **every `<ls>` element, including the attribute-bearing form** `<ls n="…">`
that the Petersburg digitisation uses at scale; Chapter 10's register census counts the
bare form. For the Petersburg dictionary alone the difference is large — 568,730 bare
against 233,058 attribute-bearing spans in the committed source file (recounted from
csl-orig for this chapter) — which is why the builder's raw total below (1,496,302 tags
over the eleven keyed dictionaries) exceeds the census's corpus-wide figure (1,245,644
over all forty-four) despite covering fewer dictionaries. The two are
extraction-convention variants over the same canonical source, each committed with its
generator; they are never pooled, and every figure in this chapter uses the builder's
convention.

**Pipeline** (each step auditable in the committed artifacts):

1. **Extraction.** Every `<ls>…</ls>` span is read from each dictionary's csl-orig text —
   1,496,302 raw tags across the 11 dictionaries of Table 1.
2. **Abbreviation resolution.** The leading abbreviation is resolved by longest-prefix
   match against that dictionary's *own* published key (case-insensitive fallback). A
   dictionary's citation is interpreted by its own conventions, not a global gazetteer.
3. **Non-text filter (Monier-Williams).** MW reuses `<ls>` for grammatical voice and case
   markers (`A.`, `mn.`, `ind.`), editorial markers (`ibid.`, `Cat.`, `col.`), and the
   `L.` = "lexicographers" tag. 63,582 such markers are excluded via an explicit stoplist
   and counted in
   [`ls_citation_nontext_filtered.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nontext_filtered.tsv)
   — an audited exclusion, not a silent drop.
4. **Placeholder filter.** Abbreviations whose Cologne expansion is `? [Cologne Addition]`
   — unidentified by the digitisers themselves — count as unresolved, never as a text
   node.
5. **Key-borrow.** Three `<ls>`-bearing dictionaries have no key of their own but a
   documented shared convention and borrow one: Apte's revised edition from Apte 1890
   (same author), Schmidt's *Nachträge* and the PW *Nachträge* from the Petersburg key
   (the *Nachträge* tradition). Borrowed-key resolution rates are reported separately
   (Table 1) and are a named limitation (§5).
6. **Canonical folding.** Editorial tails are stripped; nodes fold under a diacritic- and
   case-insensitive key (`ṚGVEDA` ≡ `Ṛg-veda` ≡ `Ṛgveda`); a small hand-verified alias
   table folds the highest-count author's-genitive and title-synonym forms (`MANU'S
   Gesetzbuch` + `Mānavadharmaśāstra` → *Manusmṛti*). Every alias is a well-established
   identification; the long synonymy tail is deliberately left unmerged and quantified in
   §5. The alias table is the review-gate discipline of Chapter 2 §4 applied to node
   identity — merges are adjudicated, never automatic.

**Table 1 — corpus and coverage.** Source: the dataset
[README](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/README.md)
coverage table and
[`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv)
(distinct texts recomputed 11-07-2026; where the README's per-dictionary distinct-text
counts differ by a few units, the committed edge list is authoritative). `% text` =
resolved ÷ (raw − non-text). `*` = borrowed key.

| Code | Dictionary | Raw `<ls>` | Non-text filtered | Resolved text citations | % text | Distinct texts |
|---|---|--:|--:|--:|--:|--:|
| pwg | Böhtlingk & Roth, *Sanskrit-Wörterbuch* (1855–1875) | 801,790 | 0 | 536,172 | 66.9 % | 475 |
| ap\* | Apte, *Practical Sanskrit-English Dictionary*, revised ed. (1957–1959) | 68,273 | 0 | 57,113 | 83.7 % | 155 |
| pw | Böhtlingk, *Sanskrit-Wörterbuch in kürzerer Fassung* (1879–1889) | 98,484 | 0 | 50,701 | 51.5 % | 243 |
| ben | Benfey, *Sanskrit-English Dictionary* (1866) | 49,234 | 0 | 49,003 | 99.5 % | 96 |
| bhs | Edgerton, *Buddhist Hybrid Sanskrit Dictionary* (1953) | 48,419 | 0 | 40,875 | 84.4 % | 136 |
| ap90 | Apte, *Practical Sanskrit-English Dictionary* (1890) | 43,894 | 0 | 37,993 | 86.6 % | 149 |
| mw | Monier-Williams, *Sanskrit-English Dictionary* (1899) | 320,830 | 63,582 | 20,250 | 7.9 % | 5 |
| lrv | Vaidya, *Standard Sanskrit-English Dictionary* (1889) | 16,650 | 0 | 16,469 | 98.9 % | 106 |
| sch\* | Schmidt, *Nachträge zum Sanskrit-Wörterbuch* (1928) | 31,041 | 0 | 11,496 | 37.0 % | 160 |
| pwkvn\* | *Petersburger Wörterbuch* (PW) *Nachträge und Verbesserungen* | 17,629 | 0 | 8,386 | 47.6 % | 172 |
| md | Macdonell, *Sanskrit-English Dictionary* (1893) | 58 | 0 | 47 | 81.0 % | 4 |
| **total** | | **1,496,302** | **63,582** | **828,505** | **57.8 %** | **912** |

The overall resolution ceiling — 57.8 % of non-filtered tags resolve to a canonical
text — and its two largest causes (Monier-Williams's tag reuse, partial borrowed keys)
are treated as limitations in §5, not hidden in the denominator. All results below
describe the resolved graph: **828,505 citations of 912 distinct source texts, in 1,701
dictionary→text edges**.

## 3. The shape of the shared canon

**Concentration.** Citation mass is strongly top-heavy. Computed from
[`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv)
(n = 912 texts, 828,505 citations): the top 10 texts carry **33.7 %** of all citations,
the top 20 carry 49.7 %, the top 50 carry **71.0 %**, and the top 100 carry 84.9 %. A
working lexicographer's evidentiary world was, in volume terms, a few dozen texts deep.

**Table 2 — the most-cited texts.** Source: `ls_citation_nodes.tsv` (folded canonical
nodes). `#dicts` = how many of the 11 dictionaries cite the text at least once.

| Citations | #dicts | Text |
|--:|--:|---|
| 56,818 | 8 | Mahābhārata |
| 38,187 | 7 | Ṛgveda |
| 38,155 | 9 | Rāmāyaṇa |
| 26,365 | 7 | Manusmṛti |
| 21,791 | 3 | Aṣṭādhyāyī (Pāṇini) |
| 21,330 | 5 | Bhāgavata-Purāṇa |
| 20,232 | 7 | Śabdakalpadruma |
| 19,922 | 7 | Raghuvaṃśa |
| 18,073 | 3 | Abhidhānacintāmaṇi |
| 18,030 | 4 | Indische Sprüche |
| 17,015 | 9 | Kathāsaritsāgara |
| 14,918 | 8 | Amarakoṣa |
| 14,743 | 6 | Pañcatantra |
| 13,685 | 7 | Harivaṃśa |
| 13,246 | 6 | Medinīkośa |

Three observations sit on the surface of Table 2. The epics and dharmaśāstra dominate raw
volume (Mahābhārata, Rāmāyaṇa, Manusmṛti). The indigenous lexica — Śabdakalpadruma,
Amarakoṣa, Abhidhānacintāmaṇi, Medinīkośa — are themselves among the most-cited
*sources*: the European dictionaries cite the Indian dictionaries, descent made visible
as citation, and the macrostructural inheritance Chapter 4 traced through the Fort
William line here surfaces as apparatus. And two entries are artifacts of a single
dominant citer amplified through the fold: the Aṣṭādhyāyī's 21,791 is almost entirely the
Petersburg dictionary (21,509, its third-largest source), and *Indische Sprüche* is
Böhtlingk citing his own anthology — on whose verification see §5.

**Reach: the canon is thin.** Reach is nearly the inverse of volume. Computed from the
same node table:

| Cited by *k* dictionaries | Texts |
|--:|--:|
| 11 | 0 |
| 10 | 0 |
| 9 | 4 |
| 8 | 13 |
| 7 | 12 |
| 6 | 20 |
| 5 | 25 |
| 4 | 31 |
| 3 | 102 |
| 2 | 97 |
| 1 | 608 |

**No text is cited by all eleven dictionaries.** The widest-reach texts, at 9 of 11, are
the Rāmāyaṇa, the Kathāsaritsāgara, the Bhagavadgītā, and the Mārkaṇḍeya-Purāṇa. Only 29
texts (3.2 %) reach seven or more dictionaries — but those 29 carry 44.1 % of all
citation volume. Meanwhile **608 of 912 texts (66.7 %) are private to a single
dictionary**, jointly carrying 11.1 % of the volume. The picture is a thin,
heavily-cited universal head over a long private tail — which raises the topological
question: is the tail structured?

## 4. Tradition communities, not one canon

**The topology test.** If the dictionaries shared one canon, the binarised
dictionary × text matrix should be *nested*: a dictionary citing few texts should cite a
subset of what broader dictionaries cite. If instead each lexicographic school kept its
own authorities, the matrix should be *modular*: blocks of texts co-cited by a group of
dictionaries and absent elsewhere. Following the committed test
([`build-citation-canon.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs)
→ [`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json);
matrix 11 × 912, 1,701 edges, fill 0.170), the chapter computes NODF nestedness
(Almeida-Neto et al. 2008) and Barber (2007) bipartite modularity Q (label propagation,
best of 6 restarts), each against 1,000 degree-preserving (fixed-fixed) permutation
nulls, with permutation p = (r+1)/(n+1).

**Result: the matrix is significantly modular and, if anything, *less* nested than
chance.** NODF = 24.44 against a null mean of 28.98 ± 0.18 (z = −25.7; p = 1.0, i.e.
every permutation is more nested than the observed matrix); Barber Q = 0.4995 (9 modules)
against a null mean of 0.4295 ± 0.0008 (z = 83.8, permutation p = 0.001, n = 1,000).
Stated per the contract of Chapter 2 §6.3: the effect is a modularity excess of 0.070
over what the marginals force, roughly 88 null standard deviations — the p-value beside
it is confirmatory decoration, not the evidence. The shared-canon hypothesis is not
merely unsupported; the arrangement of citations runs the other way. Because the
degree-preserving null holds each dictionary's breadth and each text's popularity fixed,
this is a statement about *arrangement*, not a restatement of §3's concentration: given
how many texts each dictionary cites and how popular each text is, the specific
assignments cluster into communities more than that constraint forces.

**Naming the communities — under an inferred map.** The names below depend on a curated
119-text text→tradition map
([`tradition_tags.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/tradition_tags.tsv),
confidence-scored, covering 80.3 % of total citation volume). That map is
machine-assigned: **as of 18-07-2026, zero of its 119 rows have passed the human review
gate**, so in the evidence vocabulary of Chapter 2 §4 every tradition label here is
`inferred`, and the community names are working labels, not reviewed facts. The
*topology* result above is independent of the map; only the names in Table 3 rest on it,
and the journal version re-states this section over the reviewed map before submission.

**Table 3 — per-dictionary tradition profile** (inferred map; shares are of each
dictionary's *tagged* volume, with the tagged fraction given per row). Source:
`tradition_tags.tsv` joined to
[`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv).

| Dict | Tagged volume (share of dict) | Leading traditions (inferred) |
|---|--:|---|
| pwg | 416,050 (78 %) | lexical-kośa 21 % · classical-kāvya 20 % · epic 19 % · vedic 14 % |
| ap | 52,231 (91 %) | classical-kāvya 59 % · epic 15 % · dharmaśāstra 11 % |
| ben | 44,859 (92 %) | classical-kāvya 39 % · epic 30 % · dharmaśāstra 15 % |
| ap90 | 34,494 (91 %) | classical-kāvya 79 % · dharmaśāstra 10 % · epic 5 % |
| pw | 34,034 (67 %) | classical-kāvya 28 % · epic 21 % · dharmaśāstra 18 % · vedic 14 % |
| bhs | 32,405 (79 %) | **buddhist 98 %** |
| mw | 20,250 (100 %) | vedic 87 % · buddhist 9 % |
| lrv | 14,304 (87 %) | classical-kāvya 76 % · dharmaśāstra 15 % |
| sch | 9,944 (86 %) | classical-kāvya 26 % · lexical-kośa 24 % · epic 12 % |
| pwkvn | 6,755 (81 %) | classical-kāvya 27 % · epic 18 % · dharmaśāstra 13 % |
| md | 47 (100 %) | vedic 100 % |

Read under that inferred map, the communities are the ones a historian of the discipline
would draw freehand — now with magnitudes attached. Edgerton's dictionary is an almost
hermetically Buddhist community: 98 % of its tagged citation volume (Mahāvastu,
Mahāvyutpatti, Lalitavistara lead its edge list), with effectively zero Vedic or epic
citation. The Apte line and Vaidya are the classical-kāvya school — 59–79 % kāvya, led by
the Raghuvaṃśa in all three — the citation-apparatus face of the schoolroom function
their inventories showed in Chapter 3. The Petersburg lineage (the two recensions, their
*Nachträge*, and Schmidt) is the broad-spectrum community — no tradition exceeds 28 % in
any of the four — and is alone in citing the indigenous kośas at scale, a fifth of the
great Petersburg dictionary's tagged volume: the same descent-made-visible that Table 2
showed from the texts' side. Monier-Williams's small tagged residue and Macdonell read as
Vedic, though both on unrepresentative yields (§5). Benfey sits between the kāvya and
epic profiles, consistent with its chrestomathy-anchored design.

## 5. Limitations

1. **Resolution ceiling.** 57.8 % of non-filtered `<ls>` tags resolve to a canonical
   text. The unresolved remainder is dominated by unkeyed abbreviations and is
   inventoried per dictionary in
   [`ls_citation_unresolved_top.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_unresolved_top.tsv)
   — a worklist, not a mystery. Everything in §3–§4 describes the resolved graph.
2. **Monier-Williams's yield is structurally low (7.9 %).** After the audited removal of
   63,582 grammatical and editorial markers, MW contributes only ~20 thousand text
   citations under 5 coarse nodes (78.6 % of them "Ṛgveda"). MW's `<ls>` habits make it a
   poor frequency source; its Table 3 profile is *tagged residue*, not MW's true canon.
3. **Borrowed keys resolve partially.** Schmidt (37.0 %) and the PW *Nachträge* (47.6 %)
   share only part of the Petersburg abbreviation set; the Apte borrow is clean (83.7 %).
   Under-resolution biases these rows toward the shared Petersburg conventions and
   against their idiosyncratic sources.
4. **Keyless dictionaries are excluded** — notably Grassmann (Vedic-specific), while the
   epigraphic index cites inscription corpora, a separate citation universe deliberately
   outside the text graph.
5. **The title-synonymy tail is unmerged and inflates the private tail.** The curated
   alias table folds only hand-verified identifications, so spelling variants outside it
   remain separate nodes: Vaidya's `Raghuvanśa` (4,101 citations) does not fold into
   *Raghuvaṃśa* (19,922), nor `Manusmṛiti` (1,762) into *Manusmṛti*, nor `Rigveda` (837)
   into *Ṛgveda*. Each such miss both understates a major text's reach and adds spurious
   single-dictionary "texts" to the 608 of §3. The direction of the bias is therefore
   *against* the shared-canon reading: the modularity result is computed on the matrix as
   committed and would only sharpen if variants of shared texts were folded. The residual
   is quantifiable from the node table's `variant_forms` column and is the dataset's top
   QA item.
6. **Counts are per text, not per locus.** The graph discards the book-and-verse locus,
   so it cannot say whether a citation is *correct* — only that it was made. Per-locus
   verification is a companion program with first waves executed: the Harivaṃśa
   resolution census
   ([HARIVAMSA_CITATION_RESOLUTION_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md))
   and the *Indische Sprüche* verification census
   ([SPRUECHE_CITATION_VERIFICATION_CENSUS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md)),
   which checked all 15,877 Petersburg citations of Böhtlingk's own anthology and found,
   for the 6,320 second-edition references with a typed text to check against, 2,621
   corroborated against 443 text mismatches (plus 3,255 verse-without-quote references) —
   roughly one in seven checkable quotations diverges from the cited verse. The frequency
   graph is read with that error floor in mind.
7. **Topology statistics are presence/absence.** NODF and Q are computed on the binarised
   matrix; count weighting appears in the exploratory heatmap of the atlas's interactive
   view but not in the significance tests. Barber Q via label propagation is a heuristic
   lower bound, not an exhaustive optimum.
8. **The tradition map is inferred and unreviewed** (§4): community names await the
   119-row human review; the modularity statistic does not depend on them. Clearing the
   gate is a *human* task by construction — Chapter 2 §4's review gate does not accept a
   model's ratification — and the chapter's language stays inside the inferred status
   until it clears.

## 6. Conclusion

Read as a citation network, the Sanskrit dictionary tradition is not one tradition. Its
citation mass concentrates on a few dozen texts, but the *arrangement* of citations is
significantly modular: a Buddhist lexicon, a kāvya-schoolroom line, a Vedic profile, and
the omnivorous Petersburg lineage each kept their own authorities, sharing only a thin
universal head — Rāmāyaṇa, Mahābhārata, Ṛgveda, Manusmṛti — no single text of which
reaches all eleven dictionaries. The canon implied by the dictionaries is a union of
school reading lists, not an intersection; the closed, constitutive authority roster of
the Roman grammarians' tradition has no counterpart here, and the difference is now a
measured property of the record rather than an impression.

Within the book, the graph is built to be consumed. It gives the next chapter's descent
forensics a frequency baseline against which shared-*rare* citations become surprising —
the improbability that makes Chapter 12's fingerprint evidence probative; it takes its
volume denominators from the register census of Chapter 10; and its per-locus extension —
the verification censuses of §5 — turns the lexicographers' apparatus into checkable
claims against digital editions, the evidence-graph move of Chapter 2 applied to the
citation layer. In the graph's terms: each dictionary→text edge is a node-pair statement
carrying its resolution provenance, its register, and — where the verification program
has reached it — a measured error bound.

## References

Secondary references below are cited from standard editions; bibliographic details
flagged `[author-verify]` await the author's check against physical copies.

Almeida-Neto, Mário, Paulo Guimarães, Paulo R. Guimarães Jr., Rafael D. Loyola, and
Werner Ulrich. 2008. "A Consistent Metric for Nestedness Analysis in Ecological Systems:
Reconciling Concept and Measurement." *Oikos* 117 (8): 1227–1239.

Apte, Vaman Shivaram. 1890. *The Practical Sanskrit-English Dictionary.* Poona.

Apte, Vaman Shivaram. 1957–1959. *The Practical Sanskrit-English Dictionary.* Revised
and enlarged edition, ed. P. K. Gode and C. G. Karve. Poona: Prasad Prakashan.
`[author-verify]`

Barber, Michael J. 2007. "Modularity and Community Detection in Bipartite Networks."
*Physical Review E* 76: 066102.

Benfey, Theodor. 1866. *A Sanskrit-English Dictionary.* London: Longmans, Green.
`[author-verify]`

Böhtlingk, Otto. 1870–1873. *Indische Sprüche.* 2nd ed. St. Petersburg. `[author-verify]`

Böhtlingk, Otto. 1879–1889. *Sanskrit-Wörterbuch in kürzerer Fassung.* St. Petersburg.

Böhtlingk, Otto, and Rudolph Roth. 1855–1875. *Sanskrit-Wörterbuch.* St. Petersburg:
Kaiserliche Akademie der Wissenschaften.

Dror, Rotem, Gili Baumer, Segev Shlomov, and Roi Reichart. 2018. "The Hitchhiker's Guide
to Testing Statistical Significance in Natural Language Processing." In *Proceedings of
ACL 2018,* 1383–1392.

Edgerton, Franklin. 1953. *Buddhist Hybrid Sanskrit Grammar and Dictionary.* New Haven:
Yale University Press.

Ferri, Rolando (ed. contributions). 2019. In Robert Maltby et al. (eds.), *Studies on
Late Antique and Medieval Latin Glossaries and Dictionaries.* [Gatti on Nonius
Marcellus's *auctores* canon and the ordered-citation regularity known as Lindsay's law.]

Macdonell, Arthur Anthony. 1893. *A Sanskrit-English Dictionary.* London: Longmans,
Green.

Monier-Williams, Monier. 1899. *A Sanskrit-English Dictionary.* Oxford: Clarendon Press.

Schmidt, Richard. 1928. *Nachträge zum Sanskrit-Wörterbuch in kürzerer Fassung von Otto
Böhtlingk.* Leipzig: Harrassowitz. `[author-verify]`

Vaidya, Lakshman Ramchandra. 1889. *The Standard Sanskrit-English Dictionary.* Bombay.
`[author-verify]`

Vogel, Claus. 1979. *Indian Lexicography.* Wiesbaden: Otto Harrassowitz.

Zgusta, Ladislav. 1971. *Manual of Lexicography.* (Janua Linguarum, Series Maior 39.)
Prague: Academia; The Hague and Paris: Mouton.

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of
Indology and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/).

**Sibling chapters (this book).** Chapter 2 owns the statistical-practice contract
(§6.3 there) and the review-gate discipline (§4 there) this chapter writes under;
Chapter 10 owns the two citation registers and the volume denominators; Chapter 12 owns
the pair-level forensic use of citations this chapter's frequency baseline feeds;
Chapters 3 and 4 own the inventory and macrostructural faces of the same
dictionaries-citing-dictionaries descent that surfaces here in the apparatus.

*[Data note, 2026-07-18: all tables and statistics above are computed from committed
artifacts in the atlas repository —
[`ls_citation_edges.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_edges.tsv)
(1,701 edges),
[`ls_citation_nodes.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/ls_citation_nodes.tsv)
(912 nodes),
[`tradition_tags.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/tradition_tags.tsv)
(119 rows, inferred, 0 human-reviewed as of this writing),
[`citation_canon.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/citations/citation_canon.json)
(topology statistics with provenance sidecar). The graph rebuilds in about a minute with
[`build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py)
against sibling csl-orig and csl-guides checkouts; the topology statistics with the
committed
[`build-citation-canon.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-canon.mjs).
An interactive view (nested-order heatmap, canon curve, per-dictionary fingerprints, CSV
downloads) is committed as the atlas's
[citation-canon tool](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/citation-canon.md).
No dataset cited in this chapter carries a minted DOI at the time of writing; the
versioned data release is a pending packaging step, tracked in the book's plan of
record.]*

_Dr. Mārcis Gasūns_
