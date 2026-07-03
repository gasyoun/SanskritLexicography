# Huet / INRIA Heritage word list vs the Cologne (CDSL) wordlists + DCS

**File analysed:** [`21562-huet-velthius.txt`](then-2014/21562-huet-velthius.txt) — 21,562 lines, UTF-8 **with BOM**, in Huet's **VH (Velthuis) transliteration**.
**Source work:** the stem list of the **INRIA "Sanskrit Heritage" reader** ([sanskrit.inria.fr/DICO/reader.fr.html](https://sanskrit.inria.fr/DICO/reader.fr.html), Gérard Huet) — an **older export**, non-Cologne.
**Date:** 2026-06-26 · script: [`huet_coverage.py`](huet_coverage.py)

A non-Cologne control alongside the [Catalan-Pujol study](Catalan-Pujol/Sanskrit-Catalan-Wordlist-vs-Cologne.md): an independent Sanskrit headword spine, measured the same two ways — coverage by the CDSL dictionaries, and attestation in the DCS corpus.

## 1. Transliteration

Huet's VH is decoded to IAST (then to SLP1 via [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util), same normalisation as the Catalan scripts). Key mappings: `aa ii uu` = ā ī ū · `.r .rr .l` = ṛ ṝ ḷ · `.t .d .n` = ṭ ḍ ṇ · `.s` = ṣ · **`z` = ś** · **`f` = ṅ** (`akalafka` = akalaṅka) · `~n` = ñ · `.m` = ṃ · `.h` = ḥ. 21,562 lines → **21,055 unique normalised keys**.

## 2. Coverage by the CDSL dictionaries

Greedy marginal coverage (which dictionary adds the most new lemmas, in turn):

| Dictionary | adds | cumulative | cum % |
|---|--:|--:|--:|
| **MW** (Monier-Williams) | 17,588 | 17,588 | **83.5 %** |
| PW (Petersburg, shorter) | 291 | 17,879 | 84.9 % |
| WIL, VCP, AP90, BUR, CAE, MW72, PWG, GRA, BOR, YAT, BEN, SHS | +558 total | 18,146 | **86.2 %** |
| *uncovered by any CDSL dictionary* | — | 2,909 | **13.8 %** |

Like the Catalan list, it is **MW-dominated** — MW alone covers 83.5 %, and every other dictionary together lifts coverage only to 86.2 %.

## 3. Corpus attestation (vs DCS-2021)

| | share of the 21,055 Huet keys |
|---|--:|
| Dictionary-covered (any of 15 CDSL dicts) | **86.2 %** |
| **DCS corpus-attested** | **60.0 %** |
| DCS-attested but in **no** CDSL dictionary | 131 (0.6 %) |

## 4. Huet vs Catalan-Pujol — the interesting contrast

| | **Catalan-Pujol** (61,266 lemmas) | **Huet / INRIA** (21,562 lemmas) |
|---|--:|--:|
| unique normalised keys | 59,377 | 21,055 |
| MW alone | 88.5 % | 83.5 % |
| any CDSL dictionary | 91.0 % | 86.2 % |
| **DCS corpus-attested** | **46.4 %** | **60.0 %** |
| corpus-attested, no CDSL entry | 0.3 % | 0.6 % |

- **Both are MW subsets** (~84–88 % MW), confirming the modern-bilingual-dictionary pattern: a new Sanskrit lexicon is built on the Monier-Williams headword spine.
- **The Huet list is far more corpus-attested (60 % vs 46 %).** It is a *reader's* working lexicon — selected toward forms a parser actually meets in texts — so it carries much less of the dictionary "dark matter" (rare/Vedic/grammarians' forms) that inflates a full dictionary spine like Pujol's. Smaller list, denser corpus signal.
- **Both have a tiny corpus-but-no-CDSL corner** (0.3–0.6 %); as in the Catalan case these are dominated by lemmatisation-convention differences (prefixed/denominative verbs, productive derivatives) rather than genuine missing words.

## 5. Use cases

1. **A corpus-weighted core vocabulary.** At 60 % DCS-attested, the Huet stem list is a higher-precision base for a learner's lexicon or a parser dictionary than a full dictionary spine — most of it is vocabulary actually met in texts.
2. **VH↔SLP1 bridge for ingesting INRIA Heritage data.** The validated Velthuis→IAST→SLP1 map in [`huet_coverage.py`](huet_coverage.py) lets the INRIA Heritage reader's output be joined to the CDSL/SLP1 and DCS ecosystems on a common key — the prerequisite for linking Heritage analyses to Cologne entries.
3. **Lemmatisation-interoperability check.** The 131 corpus-attested-no-CDSL keys map INRIA's lemmatisation conventions (prefixed/denominative units) onto CDSL's root-based headwording — a small crosswalk for tools that consume both.
4. **A control/benchmark.** Side by side with Pujol it quantifies the "reader's lexicon vs dictionary spine" axis (60 % vs 46 % corpus density at similar ~85 % MW coverage) — a reusable yardstick when evaluating any new Sanskrit wordlist's character.

---

## 6. Current mirror vs the 2014 export (03-07-2026)

Phase 1 of the [Heritage reuse roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md):
the 2014 file above is the *reader's* curated stem list; the
[darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources)
GitHub mirror's `DICO/` HTML is the **full current Heritage dictionary** — a
different-scope asset, not a version bump of the same list, so the comparison
below is "reader export vs. full dictionary," not "2014 vs 2026 of the same
thing." [`heritage_stem_extract.py`](heritage_stem_extract.py) pulls
38,343 unique current stem keys from `DICO/`'s anchor index (see
[HERITAGE_MIRROR_INVENTORY.md](HERITAGE_MIRROR_INVENTORY.md) for the
anchor-normalisation rules); [`heritage_coverage_current.py`](heritage_coverage_current.py)
reruns `huet_coverage.py`'s pipeline on it and diffs against the 2014 set.

| | 2014 reader export | Current DICO (full dict) |
|---|--:|--:|
| unique normalised keys | 21,055 | 38,343 |
| any CDSL dictionary | 86.2 % | 80.1 % |
| DCS corpus-attested | 60.0 % | 50.1 % |
| DCS-attested, no CDSL | 131 (0.6 %) | 304 (0.8 %) |

- **Overlap:** 20,172 of the 2014 keys survive in the current dictionary (95.8 %);
  883 do not appear in the current `DICO/` anchor index (likely renamed/merged
  entries, or reader-only forms never in the full dictionary — not re-verified
  against the live site, which is Anubis-walled).
- **18,171 keys are new** since 2014 — expected, since the full dictionary is
  ~1.8× the reader's curated subset. Of those, 72.1 % already have a CDSL entry
  and 37.7 % are DCS-attested; **187 are DCS-attested with no CDSL entry**,
  parked (unvetted, artifact-heavy) in
  [COVERAGE_ADDITIONS.md](COVERAGE_ADDITIONS.md#heritage-inria-current-mirror-candidates-03-07-2026-unvetted).
- **Coverage % dropped** (86.2→80.1 any-CDSL, 60.0→50.1 DCS) because the full
  dictionary carries far more of the "dictionary dark matter" (grammatical
  affix entries, comparative/superlative derived forms, rare proper nouns) that
  the reader's corpus-driven subset filtered out — consistent with the §4
  finding that the reader list is denser in corpus-attested vocabulary
  precisely because it is a *selection*, not the full spine.

---

*Method: VH→IAST→SLP1, accent- and (where applicable) hyphen-insensitive lemma-identity match against `<k1>` of CDSL dictionaries in `csl-orig/v02` and against the DCS-2021 lemma index. Reproducible via [`huet_coverage.py`](huet_coverage.py) (includes a transcoder self-check).*
