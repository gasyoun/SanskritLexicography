# Chapter 8 — Comparative Derivation: Pāṇinian *Vyutpatti* Across Ten Lexica

_Created: 13-07-2026 · Last updated: 13-07-2026_

> **Provenance.** This chapter is the book-form version of the article *Cross-Dictionary
> Consistency of Pāṇinian Derivation in the Cologne Lexica* (source draft:
> [PAPER_DRAFT.md](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/etymology_stats/PAPER_DRAFT.md)),
> which is being published separately in a journal version (target: *International Journal of
> Lexicography* / *Lexicographica*, with the International Sanskrit Computational Linguistics
> Symposium as a parallel venue); where the article must remain independently citable, cite
> that version. Every count and table below is carried over from the article unchanged and is
> regenerable from the committed pipeline
> ([`csl-orig/v02/*/​*_etymology.tsv`](https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02/etymology_stats)
> via `stats_etymology.py`). Only the framing has been converted from journal to book form —
> the internal submission-planning and technique-assessment memos removed, the abstract folded
> into the opening, cross-references remapped to sibling chapters, and the comparative
> metalexicography engaged at the monograph's depth. Section numbering is chapter-internal
> (§1–§6).

The two preceding chapters read descent off the dictionary's outward and inward pointers —
its citations (Chapter 10) and its cross-references (Chapter 9). This chapter reads a third,
deeper layer: the *derivation* each dictionary assigns to a word — its root, its affix, and
the grammatical relation (*kāraka*) that affix expresses. Derivation is where the European and
indigenous traditions are least alike in idiom and, it turns out, most alike in substance. The
Cologne corpus bundles three scholarly lineages — the indigenous Sanskrit grammarians
(Śabdakalpadruma, Vācaspatya, and their kin), the English Indologists (Wilson, Monier-Williams,
Apte), and the German Petersburg school — each stating a word's derivation in its own
notation. The question is whether, under the notation, they *agree*.

The chapter earns its place in the book on two counts. First, it is the positive image of the
"two traditions" argument: where Chapters 1, 4, and 10 showed the European instrument going
*blind* to the indigenous one, here the two are made commensurable and found to converge — the
indigenous prose lexica agree on a headword's Pāṇinian affix in over 90 % of cases, and the
English and German traditions agree on its root about two-thirds of the time. Second, it is a
case study in the book's own measurement discipline turned reflexively on itself: the one
apparent outlier (Wilson 1832) is not left as an anecdote but decomposed — half of its
"divergence" is measurement noise in my own extractor, and most of the remainder is Pāṇinian
*taxonomy*, not different derivations. Following that decomposition to its end is the more
interesting result than the agreement it qualifies.

## 1. The question, and why derivation is the deepest layer

Derivation sits at the join of grammar and lexicon. To state that *karaṇa* is *kṛ* + *lyuṭ* in
the *bhāve* is to make a grammatical analysis serve a lexicographic entry — and that join is
not incidental to lexicography but constitutive of it. The oldest complete Arabic dictionary,
al-Khalīl's *Kitāb al-ʿAyn*, is organised on the derivational principle of *al-ištiqāq* (root
extraction) and stands beside Sībawayhi's grammar as its twin: in that tradition, as in the
Pāṇinian one, the dictionary is a projection of the grammar (Baalbaki 2014). The Sanskrit
*vyutpatti* is the same instinct — every derived headword is, in principle, a rule-governed
output of root plus affix — and the indigenous lexica record it densely. The European
dictionaries record it too, in their own conventions: Wilson's free English prose, Monier-
Williams's √-notation, the Petersburg "von Wurzel." Three idioms for one grammatical fact, and
the empirical question is whether they name the same fact.

That question must be posed carefully, because the temptation is to treat all "etymology" in a
dictionary as one thing. It is not. The rule-governed Pāṇinian *vyutpatti* recovered here — a
closed vocabulary of affixes, each with a defined grammatical function — is a different object
from the associative, rhetorical etymologizing of the classical European grammarians, for whom
a proposed origin was often a figure of learning rather than a derivation under a rule (on the
Latin case, and the caution against reading it as rule-governed, see the essays in Ferri 2019,
esp. Pieroni). I therefore measure agreement only on the layer where the traditions genuinely
share an object — the root, the affix name, the kāraka — and say so at each step. The frame for
that measurement is the comparative method of historical linguistics (shared morphological
states as evidence of a common analysis; Bowern and Evans 2014, chapters by Koch and
Mailhammer), applied not to reconstruct a proto-form but to test whether independent
lexicographers reconstructed the *same* form.

## 2. Related work and the validation stance

This study is the derivational counterpart to the indigenous-microstructure analysis of
Chapter 7 (*Grammar Without Tags*), and the two share a corpus and a method. Chapter 7 studies
the *root entry* and its conjugational metadata — which records are roots, and each root's
gaṇa/pada — and shows that five indigenous lexica agree on the grammar they record (gaṇa
compatible in 85.5 % of 1,526 doubly-classified roots). This chapter studies the complementary
object, the *derived headword* and its analysis into root + pratyaya + kāraka; the two layers
are orthogonal, and where Chapter 7 excludes the European dictionaries (they carry only a
handful of root entries each), this chapter includes them, because stating the derivation of a
headword is exactly what Wilson, Monier-Williams, and the Petersburg dictionaries *do*.

From Chapter 7 I adopt the central methodological stance, and apply it reflexively: a near-zero
score from a tag-based detector over an indigenous lexicon is a measurement artefact, not an
absence of content, and **cross-source agreement is the validation** when no gold standard
exists. The reflexive turn is that this chapter's own headline outlier, Wilson, is decomposed
into measurement artefact versus genuine divergence *before* it is interpreted (§4). The nearest
Sanskrit-specific predecessor is the word-sense alignment of Wilson and Yates by Patel and
Kulkarni (2024), which cross-aligns *senses* between two dictionaries; this chapter is its
sibling on the *derivation* layer. The character-level segmentation models of Hellwig and
Nehrdich (2018) and the unified ByT5-Sanskrit model (2024) are the computational-NLP context,
not techniques adopted here: the dictionaries have already segmented root from affix in stating
the etymology, so this pipeline's hard problem is affix-vocabulary normalisation and root-form
folding, not sandhi resolution.

## 3. Method

A family of extractors sharing one affix knowledge base and one canonical dhātu list was run
over ten dictionaries. The derivation marker differs by idiom (Table 1): English prose (Wilson)
tags an `<ab>E.</ab>` block with `{#root#} … {#affix#}`; Sanskrit prose (SKD, VCP, AP90, AP,
SHS, KRM) writes `[upasarga +] root + KĀRAKA pratyaya`; the structured/√ dictionary (MW) carries
`parse="X+Y"` and `fr. √ root`; German prose (PWG, PW) marks `Von {#src#}` / `Wurzel`. Two
dictionaries that superficially qualify are deliberately excluded: MD and CAE also carry the
`<ab>E.</ab>` tag, but there it marks the *Epic register* of a form, not an etymology — feeding
them to a Wilson-style extractor would produce noise.

**Table 1 — The ten dictionaries and their derivation markers.**

| Idiom | Dictionaries | Derivation marker | Extracted |
|---|---|---|---|
| English prose | WIL | `<ab>E.</ab>` block: `{#root#} … {#affix#} aff.` | root + affix |
| Sanskrit prose | SKD, VCP, AP90, AP, SHS, KRM | `[upasarga +] root + KĀRAKA pratyaya` | root + kāraka + affix |
| structured / √ | MW | `parse="X+Y"`, `fr. √ root` | root + parse |
| German prose | PWG, PW | `Von {#src#}` / `Wurzel` | source root |

The extraction yields **68,510 derivational statements**. They are typed, and the types matter,
because Wilson alone contributes 39,650 rows of which not all are derivations proper: 18,957
root+affix (incl. uṇādi), 17,686 compound-member analyses (no affix), 1,406 prefix+word, 1,214
multi-derivation, 212 single-stem, 175 cross-reference/unparsed. All cross-dictionary
comparisons use only the rows that state the compared object — compounds and cross-references
never enter a denominator.

**The agreement statistic.** For each pair of dictionaries, over the headwords that *both*
analyse with the compared object, two headwords "agree" if their extracted affix (resp. root,
resp. kāraka) *sets intersect*; agreement is a proportion with a 95 % Wilson score interval.
Three properties are stated up front. (a) It is *conditional on double coverage* — a word only
one dictionary analyses never enters the comparison, so it measures consistency, not coverage.
(b) Set intersection is mildly *inflationary* where a dictionary lists alternative derivations,
but the multi-affix share is small (VCP 6.6 % of headwords, others less) and an exact-match
variant moves no headline figure. (c) It compares affix *names*, which is stricter than
comparing derivational *outcomes* — two dictionaries that posit *ac* and *ghañ* both derive
surface *-a* but count here as disagreeing; §4 measures how much of observed disagreement is
exactly that.

**Vocabulary quality and root recovery.** The Sanskrit-prose extractions draw on a closed
Pāṇinian vocabulary — every affix they emit is one of 39 canonical pratyaya names, 100 % per
dictionary. Wilson's free-prose extraction also captures non-affix tokens: only **50.1 %** of
its 19,641 affix instances are canonical names, so every Wilson comparison is reported twice,
raw and vocabulary-filtered (both sides restricted to canonical affix names). Roots are
validated against a vendored dhātu list (the Vidyut dhātupāṭha plus the indigenous roots of the
sibling atlas) and recovered by a tiered, provenance-tagged pipeline — a local match adjacent to
the marker; the headword itself for root-organised dictionaries (KRM); a dhātu-validated
nearest-root match gated on a citation marker; a dhātupāṭha-join; an oracle-join against a
cross-dictionary (derived-word → root) index; and finally an LLM pass whose every proposed root
is validated against the canonical dhātu list before it is written. A deterministic root-form
normalisation folds surface variants onto their citation form (622 variants fold, consolidating
2,493 distinct roots to 2,090) — a fold applied by *every* extractor, including Wilson, who
prints roots in thematic surface form (*aṃśa* where the kośa cites *aṃś*); unfolded, that alone
collapses Wilson's root agreement to 8–20 %. Headline root-agreement figures are robust to
dropping the one sub-100 %-precision tier (nearest-root): MW↔PWG 64.2 % and PWG↔PW 93.9 % are
identical with and without it.

## 4. Findings

**F1 — The indigenous Sanskrit prose tradition is internally consistent on affixes.** For
headwords shared by two Sanskrit-prose dictionaries (inclusion rule: n ≥ 25 shared headwords),
the stated affix agrees in **over 90 %** of cases, per-pair range **91.7–100 %** (Table 2).
Independent 19th–20th-century compilations of the Pāṇinian analysis converge. One structural
exception is disclosed rather than hidden: VCP↔KRM agrees only 20.0 % (n=15, below the bar) —
but KRM is not a prose kośa; it is a *kṛdanta paradigm table organised by root*, whose affix
inventory is disjoint in kind, so the comparison is apples-to-oranges. "Indigenous consistency"
here is a claim about the prose kośas.

**Table 2 — Cross-dictionary affix agreement, Sanskrit-prose pairs** (n ≥ 25, proportion with
95 % Wilson interval).

| Pair | shared HW | agree (95 % CI) |
|---|--:|---|
| VCP ↔ SHS | 206 | 98.5 % [95.8–99.5] |
| AP90 ↔ AP | 178 | 100.0 % [97.9–100] |
| VCP ↔ AP | 97 | 96.9 % [91.3–98.9] |
| VCP ↔ AP90 | 93 | 96.8 % [90.9–98.9] |
| SKD ↔ AP90 | 84 | 91.7 % [83.8–95.9] |
| SKD ↔ VCP | 65 | 93.8 % [85.2–97.6] |
| SKD ↔ AP | 61 | 91.8 % [82.2–96.4] |
| AP ↔ SHS | 31 | 100.0 % [89.0–100] |
| AP90 ↔ SHS | 27 | 96.3 % [81.7–99.3] |

**F1c — The kāraka layer agrees as sharply as the affix layer.** For the same pairs, the stated
kāraka agrees **89–100 %** (VCP↔SHS 97.6 %, AP90↔AP 100 %, SKD↔VCP 89.2 %, the rest between) —
the traditions agree not only on the affix but on the grammatical relation it expresses. The one
low pair is again VCP↔KRM (26.7 %, sub-threshold), the same structural carve-out as F1.

**F2 — Wilson 1832 diverges; half of that divergence is my extractor, and I say which half.**
Raw agreement with the kośas runs 22.9–61.2 %. But Wilson states etymologies in free English
prose, and his affix field is only 50.1 % canonical: the non-canonical captures can never match
anything, mechanically depressing every raw Wilson figure. Vocabulary-filtered, Wilson agrees
**66.7–80.2 %** with the prose kośas — a real but far smaller gap (Table 3).

**Table 3 — Wilson pairs, raw vs vocabulary-filtered** (both sides restricted to canonical
Pāṇinian affix names).

| Pair | raw | vocabulary-filtered |
|---|---|---|
| WIL ↔ VCP | 61.2 % [58.7–63.7] (n=1504) | 80.2 % [77.8–82.4] (n=1149) |
| WIL ↔ SHS | 60.0 % [52.9–66.7] (n=190) | 78.1 % [70.7–84.0] (n=146) |
| WIL ↔ AP90 | 54.2 % [43.5–64.5] (n=83) | 71.4 % [59.3–81.1] (n=63) |
| WIL ↔ AP | 52.4 % [41.8–62.9] (n=82) | 71.7 % [59.2–81.5] (n=60) |
| WIL ↔ KRM | 22.2 % [12.5–36.3] (n=45) | 38.5 % [22.4–57.5] (n=26) |
| WIL ↔ SKD | 22.9 % [14.6–34.0] (n=70) | 66.7 % [46.7–82.0] (n=24) |

**F2b — And most of the *residual* disagreement is taxonomy, not etymology.** I hand-audited
every vocabulary-filtered WIL↔SKD disagreement (8) plus a random 40-case sample of WIL↔VCP
disagreements. Of the 48: **30 (62.5 %) are same-surface, different-affix-name** cases — Wilson
posits *ac*/*ap*/*yuc* where the kośa posits *ghañ*/*lyuṭ*, both deriving the identical surface
form (*-a*, *-ana*, *-ya*); 14 (29 %) are residual extraction artefacts on one side or the
other; and only **4 (8 %) are genuinely different derivational analyses**. Wilson's
"pre-critical" reputation survives only in that thin slice; the bulk of his divergence from the
kośas is a *choice among Pāṇinian affix names with identical output* — a taxonomic, not an
etymological, disagreement. This is the design fork the European tradition also faced, between
grouping words by cognate root and cross-referencing them individually (the Skeat–Weekley debate
in English etymological lexicography; Partridge 1963): Wilson and the kośa make different
notational choices over the same derivational reality.

**F3 — Cross-tradition root attribution holds at ~two-thirds.** The two large root-attributing
dictionaries, MW (English √-notation) and PWG (German "von Wurzel"), agree on the root for
**64.2 % [60.8–67.5]** of 782 shared headwords; PWG↔PW **93.9 %** (n=521). Within the Sanskrit
prose tradition root agreement runs 68.9–94.8 % — lower than the affix layer, because root
*identification* across citation conventions is noisier than affix naming, not because the
traditions disagree. Wilson illustrates the point at corpus scale: before the root-form fold his
root agreement was 8–20 % against *every* dictionary, including 8.4 % against MW (which
historically built on Wilson); after the fold, WIL↔AP90 73.8 %, WIL↔PWG 40.1 %, WIL↔MW 16.3 %
— the residual WIL↔MW gap a conventions gap (√-notation vs stem-citation), reported, not
interpreted.

**F4 — The kāraka × pratyaya structure is linguistically sound, and a dictionary's kāraka
profile fingerprints its purpose.** Pooling the Sanskrit-side dictionaries, *lyuṭ* concentrates
in *bhāve/karaṇe*, *kta* spreads across its three participial readings, *lyu* is monosemous
(*kartari*, entropy 0.33 bits), while *ḍa*, *anīyar*, *ac* are kāraka-generalists (entropy ~2
bits); *bhāve* dominates the overall distribution (51 %). But KRM inverts it — *kartari* 227 ≫
*bhāve* 30 — because the *Kṛdanta-rūpa-mālā* is built around agent-derivatives. The kāraka mix
identifies what a dictionary is *for*.

## 5. Discussion

The chapter's positive result is a corrective to a common impression. The indigenous prose
lexica are often read as a scatter of idiosyncratic compilations; measured on their derivational
layer they are the opposite — a tradition so consistent that independent 19th–20th-century kośas
agree on the Pāṇinian affix over 90 % of the time and on its kāraka nearly as often. That
consistency is the empirical trace of a shared grammar underneath the dictionaries, the same
grammar-as-substrate that Chapter 7 recovered in the verbal-root apparatus and that the Arabic
*al-ištiqāq* tradition made the organising principle of the lexicon itself. Across traditions
the agreement is looser (root ~64 %) but real, and where it is loosest it is a *conventions*
gap — Wilson's stem-citations against Monier-Williams's √-notation — not a disagreement about
the language.

The methodological result is the Wilson decomposition. It would have been easy, and wrong, to
report "Wilson agrees with the kośas only 23–61 %" and conclude that the pre-critical English
dictionary is derivationally unreliable. Filtering the extractor's own noise nearly doubles the
figure; auditing the residue shows five in six of the remaining disagreements are Pāṇinian
taxonomy (a choice of affix name with identical surface output) or measurement residue, leaving
genuine derivational disagreement at roughly one case in twelve. The lesson is the book's:
before a cross-dictionary gap is interpreted, it must be cleaned of the instrument's own
contribution — the same discipline Chapter 9 applied to prefix-convention hubs and Chapter 10 to
the two citation registers.

## 6. Data, limitations, and next steps

The released artefacts are per-dictionary TSVs, the cross-dictionary root oracle, the
per-affix/kāraka agreement CSVs, the 48-case hand audit, a Gebru-style datasheet, and an
interactive dashboard (kāraka × pratyaya heatmap, affix entropy, root-agreement matrices).
Everything is regenerable from the committed pipeline except the LLM-resolved root tiers, which
are committed inputs (every row dhātu-validated either way).

Three limits bound the claims. The tier-precision audit of the two *inferred* root tiers
(oracle-join ≈ 83 %, nearest-root ≈ 66–75 %) is currently judged by the same model family as the
LLM resolver; a human second-annotator audit of a 50-row sample per inferred tier is the one
remaining validation step before submission. The agreement statistic compares affix *names*,
which F2b shows overstates disagreement wherever two dictionaries choose different names for the
same surface affix; a follow-up metric on the *realised surface affix* rather than the pratyaya
name would separate taxonomic preference from derivational substance corpus-wide. And the
comparison is conditional on double coverage throughout, so it measures the consistency of the
tradition, never its completeness.

## References

Baalbaki, Ramzi. 2014. *The Arabic Lexicographical Tradition: From the 2nd/8th to the 12th/18th
Century.* (Handbook of Oriental Studies 1.107.) Leiden and Boston: Brill.

Bowern, Claire, and Bethwyn Evans (eds.). 2014. *The Routledge Handbook of Historical
Linguistics.* London and New York: Routledge. [Koch on etymology and morphological
reconstruction; Mailhammer on reconstruction methods.]

Ferri, Rolando (ed. contributions). 2019. In Robert Maltby et al. (eds.), *Studies on Late
Antique and Medieval Latin Glossaries and Dictionaries.* [Pieroni on Latin etymologizing as
associative/rhetorical — the caution against equating it with rule-governed *vyutpatti*.]

Hellwig, Oliver, and Sebastian Nehrdich. 2018. "Sanskrit Word Segmentation Using Character-Level
Recurrent and Convolutional Neural Networks." In *Proceedings of EMNLP 2018,* 2754–2763.
Brussels.

Partridge, Eric. 1963. *The Gentle Art of Lexicography.* London: Deutsch. [Cognate-grouping vs
cross-referencing as a design fork — the Skeat–Weekley debate.]

Patel, Dhaval, and Malhar Kulkarni. 2024. "Word Sense Alignment of Sanskrit Lexica." In
*Proceedings of the 7th International Sanskrit Computational Linguistics Symposium (ISCLS 2024).*

Nehrdich, Sebastian, Oliver Hellwig, and Kurt Keutzer. 2024. "One Model Is All You Need: ByT5-
Sanskrit, a Unified Model for Sanskrit NLP Tasks." In *Findings of EMNLP 2024.*

**Primary digital source.** Cologne Digital Sanskrit Dictionaries (CDSL). Institute of Indology
and Tamil Studies, University of Cologne.
[`sanskrit-lexicon.uni-koeln.de`](https://www.sanskrit-lexicon.uni-koeln.de/). Dhātu reference:
the Vidyut dhātupāṭha and the indigenous-root list of the sibling evidence atlas.

_Dr. Mārcis Gasūns_
