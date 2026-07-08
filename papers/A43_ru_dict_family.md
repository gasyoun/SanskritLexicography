---
paper_id: A43
title: "Russian Sanskrit Lexicography as a Digitized Comparable Family: Five Dictionaries, One Headword Space"
status: draft (skeleton, 2/5) — scaffolded 2026-07-08 (H393)
readiness: 2/5
venue: "Восток (Oriens) / Вопросы языкознания (ВЯ) — venue choice open (a human decides)"
author: "Mārcis Gasūns, independent scholar ([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)), gasyoun@ya.ru — venue + byline to confirm (a human decides)"
data_source: "RussianTranslation/src/{koch,kow,kna,smirnov,fri}.jsonl (local artifacts, 57,634 entries total; not committed — size + per-source rights); every figure recomputed 2026-07-08 by the committed RussianTranslation/src/a43_family_stats.py"
---

# Russian Sanskrit Lexicography as a Digitized Comparable Family: Five Dictionaries, One Headword Space

_Created: 08-07-2026 · Last updated: 08-07-2026_

> **Draft status (2026-07-08, H393, Fable 5 `claude-fable-5`).** Manuscript skeleton
> scaffolded from scratch (readiness 1/5 → 2/5) per the `/paper-scaffold` discipline.
> Every numeric figure in this file was **recomputed in the scaffolding pass** by
> [`RussianTranslation/src/a43_family_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/a43_family_stats.py)
> from the five local dictionary JSONLs — nothing below is transcribed from an earlier
> chat or handoff claim. (The pre-existing informal claim "4-dict comparison, ~41k
> union headwords, 222 shared-by-all" was traced to its exact frame and superseded —
> see §4.2.)
> **Open before submission:** (1) **[@DECIDE]** venue (Восток·Oriens vs ВЯ) and
> byline/ORCID confirmation (a human decides); (2) **[@DECIDE]** rights scope for any
> data release — Kochergina 1987 is in copyright, so the release ships **headword keys
> + provenance + overlap statistics, never the glosses** (§3.4, §6, §8); the
> per-source rights of the Smirnov and Frisch layers are unverified TODOs (§3.1);
> (3) §2 Related work is a **labelled stub** — no citations are faked at 2/5; a
> verified literature pass (ACL Anthology + Russian orientalist journals) is the main
> 2/5 → 3/5 lever; (4) exact bibliographic records for the Smirnov and Frisch editions
> (§3.1) are TODO; (5) the digitization provenance section (§3.2 — who digitized which
> source, when, from which scan/edition) is a skeleton awaiting the per-source audit
> trail.

## Abstract

Russian Sanskrit lexicography spans more than 170 years — from Kossowich's
Санскрито-русскій словарь (1854), among the earliest Sanskrit–Russian dictionaries
anywhere, through Knauer's textbook glossary (1908), the mid-20th-century
Mahābhārata glossaries of Smirnov and the reader glossary of Frisch, to
Kochergina's standard Санскритско-русский словарь (1987). Unlike the German and
English traditions, this family has never been digitized into a single comparable
headword space, and no quantitative account of its internal coverage exists. We
present exactly that: five digitized dictionaries (**57,634 entries**) reduced to a
shared SLP1 headword key, yielding a union of **44,972 distinct headwords**, of
which only **166 occur in all five sources** and **37,450 (83%) occur in exactly
one** — a quantitative demonstration that the Russian tradition is cumulative and
complementary, not repetitive. Pairwise overlaps expose the family's structure:
each smaller dictionary shares more with Kochergina than with any sibling,
confirming her 1987 dictionary as the tradition's integrating hub, while
Kossowich's 1854 torso contributes the largest body of headwords found nowhere
else (**9,592**). The comparison establishes a diachronic Russian baseline
(1854–1987) against which both the digitized Western dictionary families and the
new corpus-attested Sanskrit→Russian layers can be measured. The digitized keys,
per-source provenance, and full overlap statistics are released openly;
in-copyright gloss text is not.

## 1. Introduction

The great digitization wave in Sanskrit lexicography — the Cologne Digital Sanskrit
Dictionaries — covers the German tradition (Böhtlingk–Roth, Böhtlingk, Grassmann,
Schmidt), the English tradition (Monier-Williams, Apte, Macdonell), and beyond, but
the Russian tradition is absent from it. The Russian line is not minor: Kossowich
1854 predates both Böhtlingk–Roth's completion and Monier-Williams; Kochergina 1987
remains the standard desk dictionary for Russian-speaking Sanskrit students; and
between them lie a textbook glossary (Knauer 1908) and two translation-anchored
glossaries (Smirnov's Mahābhārata lexicon, Frisch's reader). Each was digitized
separately within this project; this paper is the first to put them into a single
comparable headword space and measure the family's structure.

Our claims:

1. **A digitized comparable family.** Five Russian-gloss Sanskrit dictionaries
   (1854–1987), 57,634 entries, reduced to one length-preserving SLP1 headword key
   with per-source provenance — the first machine-comparable digitization of the
   Russian Sanskrit lexicographic tradition.
2. **A measured family structure.** Union 44,972 headwords; shared-by-all-five core
   of 166; 83% of the union attested in exactly one source; pairwise overlaps that
   identify Kochergina 1987 as the hub and Kossowich 1854 as the largest unique
   contributor (§4).
3. **A diachronic Russian baseline.** The family spans 1854–1987 under one key, so
   coverage questions ("what did a Russian student of 1854 vs 1908 vs 1987 have
   access to?") become computable (§5).
4. **An honestly-scoped release.** Keys, provenance, and statistics ship openly;
   Kochergina's in-copyright gloss text does not, and each source's rights are
   stated per-source, not blanket-claimed (§8).

## 2. Related work

> **⬜ STUB (readiness 2/5)** — to be written in a verified literature pass; no
> citations are faked here. Position against three axes: (a) **dictionary
> digitization and comparability studies** — the Cologne Digital Sanskrit
> Dictionaries as the reference digitization family; dictionary-crosswalk and
> sense-alignment work (e.g. the Wilson–Yates sense-alignment line at ISCLS;
> [[A09]]/[[A35]] own the crosswalk problem for the Western family); MUDIDI-style
> dictionary-digitization benchmarks; (b) **histories of Russian indology and its
> lexicography** — the scholarship on Kossowich, Knauer, Smirnov, Kochergina as
> philologists (Russian orientalist literature, to be verified against actual
> sources, not summarized from memory); (c) **quantitative comparisons of
> dictionary families** — headword-census methodology as used for the CDSL family
> in [[A40]]. The novelty claim to land precisely: not "we digitized five
> dictionaries" but "the Russian tradition is now a *measured, comparable family*
> with a computable internal structure — the first non-Western-European Sanskrit
> dictionary family so treated."

## 3. Data and method

### 3.1 The five sources

| code | source | year | entries (rows) | distinct headword keys | gloss language | rights |
|---|---|---|--:|--:|---|---|
| `kow` | Kossowich, Санскрито-русскій словарь (unfinished; published portion) | 1854 | 13,488 | 13,144 | Russian (pre-reform orthography), 100.0% Cyrillic | public domain |
| `kna` | Knauer, glossary to Учебник санскритскаго языка | 1908 | 3,271 | 3,228 | Russian (pre-reform orthography), 100.0% Cyrillic | public domain |
| `smirnov` | Smirnov, glossary to his Mahābhārata translations (exact edition **TODO**) | mid-20th c. | 3,547 | 3,419 | Russian, 99.9% Cyrillic | **TODO — verify** (author d. 20th c.; likely in copyright) |
| `fri` | Frisch, Sanskrit-reader glossary (exact edition **TODO**; digitized via Cologne 2015) | mid-20th c. | 8,151 | 7,967 | Russian, 94.1% Cyrillic (residual entries are grammatical index lines) | **TODO — verify** |
| `koch` | Kochergina, Санскритско-русский словарь | 1987 | 29,177 | 28,315 | Russian, 100.0% Cyrillic | **in copyright** — glosses never ship (§8) |

Total: **57,634 entries**. Each digitized source is a JSON-lines file with the
uniform schema `{source, slp1, iast, gloss}` — one dictionary entry per line, the
headword in both SLP1 and IAST, the gloss as digitized (Kossowich and Knauer retain
pre-reform Russian orthography; Knauer rows carry page references to the 1908
textbook). The gloss-language percentages above are computed, not assumed
(Cyrillic-presence scan per row, same script §3.3).

### 3.2 Digitization provenance

> **⬜ SKELETON** — per-source digitization audit trail (which scan/edition, which
> OCR/keying pass, which correction rounds) to be assembled from the project's
> changelogs before readiness 3/5. What is already fixed: the five JSONLs are the
> project's own digitizations, held locally in
> [`RussianTranslation/src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src)
> (uncommitted — size + rights), and every figure in this paper is recomputable
> from them by the committed script (§3.3).

### 3.3 The comparison key

Headwords are compared on a **length-preserving SLP1 key**: the digitized SLP1
headword, stripped of surrounding whitespace and edge hyphens only (compound-member
entries like `-akza` and prefix entries like `a-` reduce to their letter material).
Case and vowel length are never touched — SLP1 is case-significant, and the naive
NFD-strip-combining-marks normalization that destroys vowel length and retroflex
dots (a documented pitfall in this project) is explicitly avoided. Multi-form
headword fields (e.g. Frisch's root entries listing several stem variants
separated by `/ /`) are kept as-is in this pass, which makes the cross-source
matching **conservative**: a variant-listing entry that fails to string-match a
sibling's single-form headword counts as non-shared, so the overlap figures below
are floors, not ceilings (§6). Implementation:
[`RussianTranslation/src/a43_family_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/a43_family_stats.py)
(stdlib-only, deterministic, re-runnable).

### 3.4 Rights-aware release design

The comparison is designed so that its open release never requires shipping
in-copyright text: the released artifact is the **headword-key space** (SLP1/IAST
keys, per-source membership, overlap statistics) plus per-source provenance.
Kochergina 1987 gloss text stays local; the 1854 and 1908 gloss layers are public
domain and releasable; the Smirnov and Frisch layers stay gloss-local until their
rights are verified (§3.1). This mirrors the release discipline used elsewhere in
the project for third-party-derived layers.

## 4. Results

All figures recomputed 2026-07-08 by
[`a43_family_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/a43_family_stats.py)
over the five local JSONLs; counts are distinct normalized headword keys (§3.3)
unless labelled "rows".

### 4.1 The union and the shared core

| quantity | value |
|---|--:|
| entries across the five sources (rows) | **57,634** |
| union of distinct headword keys (5-dict family) | **44,972** |
| shared by all five sources | **166** |
| shared by the four non-Frisch sources (koch/kow/kna/smirnov) | **226** |
| attested in exactly one source | **37,450** (83.3% of the union) |

The shared-by-all core is tiny — 166 headwords, essentially the unavoidable
high-frequency vocabulary (*ācāra*, *ācārya*, *āditya*, *āhāra*, *ālaya* …) — while
more than four-fifths of the union lives in exactly one dictionary. The Russian
tradition is **cumulative, not repetitive**: each dictionary added vocabulary the
others lack, rather than re-covering a common canon.

### 4.2 Provenance of the superseded "~41k / 222" claim

An earlier informal claim ("4-dict comparison, ~41k union headwords, 222
shared-by-all") circulated in project notes. Recomputation traced it exactly: it is
the **koch + kow + kna + smirnov** frame (Frisch excluded) on **raw** (unstripped)
keys — union 41,247, shared 222. Under this paper's normalized key the same frame
gives union 41,145 / shared 226; the full five-source family gives **44,972 /
166** (§4.1). The old figures were an artifact of frame and key choice, not an
error, and are superseded by the recomputed family-wide numbers.

### 4.3 Pairwise structure: Kochergina as hub

Pairwise overlaps (distinct normalized keys):

| pair | shared keys | share of the smaller side |
|---|--:|--:|
| koch ∩ fri | 3,614 | 45.4% |
| koch ∩ kow | 3,104 | 23.6% |
| koch ∩ kna | 2,290 | 70.9% |
| kna ∩ fri | 1,509 | 46.7% |
| koch ∩ smirnov | 1,244 | 36.4% |
| kow ∩ fri | 1,184 | 14.9% |
| smirnov ∩ fri | 819 | 24.0% |
| kow ∩ kna | 813 | 25.2% |
| kna ∩ smirnov | 774 | 24.0% |
| kow ∩ smirnov | 487 | 14.2% |

Every smaller dictionary overlaps **Kochergina more than any sibling** (top
overlap partner for kow, kna, smirnov, and fri alike): the 1987 dictionary
functions as the tradition's integrating hub. Knauer's compact teaching glossary is
the most absorbed (70.9% of its headwords are in Kochergina); Kossowich is the
least (23.6%) — the 1854 torso is not subsumed by the tradition that followed it.

### 4.4 Unique contributions

Headwords attested in exactly one source: **koch 21,528 · kow 9,592 · fri 3,827 ·
smirnov 1,930 · kna 573** (sum 37,450). Two findings stand out. First, Kossowich's
unfinished 1854 dictionary still contributes **9,592 headwords found in no later
Russian dictionary** — nearly three-quarters of its stock (73.0% of 13,144) —
making it a live lexicographic source, not a historical curiosity. Second, even
the two translation-anchored glossaries (Smirnov, Frisch) each carry a
four-digit or high-three-digit unique layer, reflecting their text-specific
(epic, reader-canon) vocabularies.

### 4.5 What "comparable" enables next

> **⬜ TODO (3/5 lever):** one worked qualitative comparison — a sampled set of
> shared headwords read across all five glosses (sense inventory growth
> 1854→1987), and a sampled set of Kossowich-only headwords checked against the
> Western family (are they genuinely rare words, or Kossowich's own
> lemmatization choices?). Sampling protocol per the project's spot-check
> discipline; not faked at 2/5.

## 5. Discussion

Three uses follow from a measured family. (1) **History of scholarship,
quantified:** the 1854–1987 axis makes Russian indology's lexicographic coverage a
computable trajectory rather than an anecdote — what a Russian reader could look up
in 1854, 1908, or 1987 is now a query. (2) **A baseline for the corpus-attested
layer:** the corpus-induced Sanskrit→Russian alignment lexicon ([[A42]]) records
what translators *actually wrote*; this family records what dictionaries *said*.
The two layers share the SLP1 key discipline, so "attested in translations but in
no Russian dictionary" becomes a computable gap list — the natural successor
study. (3) **A candidate extension of the digitized-dictionary canon:** the
Cologne family covers the German and English traditions; a keys-and-statistics
release of the Russian family (rights-clean by construction, §3.4) extends the
comparable space to a third national tradition.

## 6. Limitations

- **String-level comparison only.** Headwords are compared as normalized SLP1
  strings; no sense alignment, no lemma unification across the sources' differing
  lemmatization conventions (e.g. root vs 3sg-present citation for verbs,
  multi-variant headword fields kept unsplit). Overlap figures are therefore
  **conservative floors** (§3.3); a lemmatization-harmonized pass would raise
  them.
- **Digitization completeness varies per source.** The row counts reflect the
  digitized artifacts, not necessarily the full printed dictionaries; the
  per-source digitization audit (§3.2) is open. In particular, Kossowich 1854 was
  never completed in print — its 13,488 rows describe the published torso.
- **The five sources are not the whole tradition.** Reader glossaries, specialist
  indices, and the Soviet-era teaching literature beyond Knauer are not yet
  digitized; the family is the five machine-comparable members, not a closed
  canon.
- **Rights constrain the release.** Kochergina's glosses are in copyright and do
  not ship; Smirnov's and Frisch's rights are unverified TODOs — until resolved,
  the open artifact is keys + provenance + statistics only (§3.4, §8).
- **Local-only source artifacts.** The five JSONLs are not committed (size +
  rights); reproducibility rests on the committed statistics script plus the
  planned keys-only release, not on public source files (§8).

## 7. Conclusion

Five Russian Sanskrit dictionaries spanning 1854–1987 now live in one comparable
headword space: 57,634 digitized entries, a union of 44,972 headwords, a
shared-by-all core of only 166, and 83% of the union attested in a single source.
The measured structure shows a cumulative tradition with Kochergina 1987 as its
integrating hub and Kossowich 1854 as its largest unassimilated contributor. The
family gives Russian indology a quantitative lexicographic baseline, gives the
corpus-attested Sanskrit→Russian layer a dictionary-side counterpart, and extends
the digitized comparable dictionary space beyond the German and English
traditions. The remaining work is the verified literature pass, the per-source
digitization and rights audit, and the keys-and-statistics public release.

## 8. Data and reproducibility

The source artifacts are five JSON-lines files
(`koch.jsonl`, `kow.jsonl`, `kna.jsonl`, `smirnov.jsonl`, `fri.jsonl`; schema
`{source, slp1, iast, gloss}`) in
[`RussianTranslation/src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src),
held **locally, uncommitted** — for size and because the Kochergina gloss layer is
in copyright and the Smirnov/Frisch layers' rights are unverified (§3.1). Every
figure in this paper is recomputed from them by the committed, stdlib-only script
[`RussianTranslation/src/a43_family_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/a43_family_stats.py):

```sh
python a43_family_stats.py   # per-source rows/keys/gloss-language + union/overlap tables
```

**Release plan (rights-gated, a human decides the scope):** a keys + provenance +
statistics dataset (SLP1/IAST headword keys with per-source membership flags; no
gloss text for in-copyright sources; public-domain 1854/1908 gloss layers
releasable) via the project's standard FAIR release path with a DOI. **DOI:** *TODO
— to mint at release, after the rights ruling.*

## 9. Claim → artifact inventory

| # | Claim | Figure(s) | Artifact | Status |
|--:|---|---|---|---|
| 1 | Family scale | 57,634 rows; per-source rows/keys table (§3.1) | [a43_family_stats.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/a43_family_stats.py) over the local JSONLs | ✅ script committed; ⚠️ JSONLs local-only (rights + size) |
| 2 | Union and core | 44,972 union · 166 shared-by-all-5 · 226 shared-by-4 (§4.1) | same | ✅ recomputed 2026-07-08 |
| 3 | Single-source share | 37,450 keys in exactly one source (83.3%) (§4.1, §4.4) | same (unique-to-one table) | ✅ recomputed 2026-07-08 |
| 4 | Kochergina-as-hub | pairwise table (§4.3); koch is every sibling's top overlap partner | same (pairwise table) | ✅ recomputed 2026-07-08 |
| 5 | Kossowich unique layer | 9,592 kow-only keys = 73.0% of its 13,144 (§4.4) | same | ✅ recomputed 2026-07-08 |
| 6 | Gloss-language composition | Cyrillic-presence per source (§3.1) | same (per-source scan) | ✅ recomputed 2026-07-08 |
| 7 | Provenance of the old "~41k/222" claim | raw koch+kow+kna+smirnov = 41,247/222 (§4.2) | reproduced during the H393 pass; the committed script prints the normalized 4-dict frame (41,145/226) | ⚠️ raw variant not in the committed script — documented here only |
| 8 | Per-source bibliographic records + rights | §3.1 rights column | — | ⬜ TODO: Smirnov/Frisch editions + rights unverified |
| 9 | Digitization audit trail | §3.2 | — | ⬜ TODO before 3/5 |

## 10. Scope versus companion papers (anti-salami)

- **[[A41]] (SamudraManthanam parallel-corpus descriptor)** owns the verse-aligned
  Sanskrit↔Russian corpus. A43 does not touch corpus data.
- **[[A42]] (corpus-attested Sa→Ru alignment lexicon)** owns the corpus-induced
  translation-evidence layer. A43 owns the **printed, digitized dictionary family
  and its comparability** — the diachronic Russian dictionary baseline. The two are
  designed to join on the same SLP1 key discipline (§5) and cross-cite; neither
  re-describes the other's object.
- **[[A40]] (CDSL headword census)** owns the Western (Cologne) dictionary family's
  headword inventory. A43 applies census-style methodology to the Russian family;
  any Russian↔Western cross-family comparison is future work that would cite both,
  owned by neither alone.
- A43 leads with exactly what nothing else owns: **the Russian Sanskrit
  lexicographic tradition as a digitized, measured, comparable family**.

## 11. References

> **⬜ STUB (readiness 2/5)** — primary sources listed; scholarship to be added in
> the verified literature pass (§2), never faked.

- Kochergina, V. A. (Кочергина, В. А.). 1987. *Санскритско-русский словарь.*
  Moscow: Русский язык.
- Kossowich, K. A. (Коссович, К. А.). 1854. *Санскрито-русскій словарь.*
  St. Petersburg. (Unfinished; published portion.)
- Knauer, F. (Кнауэр, Ф. И.). 1908. *Учебник санскритскаго языка.* Leipzig.
- Smirnov, B. L. (Смирнов, Б. Л.). Mahābhārata translation glossaries — exact
  edition **TODO** (§3.1).
- Frisch (Friš), O. Sanskrit-reader glossary — exact edition **TODO** (§3.1).
- ⬜ A40 / A42 self-citations to be finalized once their venues/DOIs freeze.

_Dr. Mārcis Gasūns_
