# Huet / INRIA Heritage word list vs the Cologne (CDSL) wordlists + DCS

**File analysed:** [`21562-huet-velthius.txt`](21562-huet-velthius.txt) — 21,562 lines, UTF-8 **with BOM**, in Huet's **VH (Velthuis) transliteration**.
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

---

*Method: VH→IAST→SLP1, accent- and (where applicable) hyphen-insensitive lemma-identity match against `<k1>` of CDSL dictionaries in `csl-orig/v02` and against the DCS-2021 lemma index. Reproducible via [`huet_coverage.py`](huet_coverage.py) (includes a transcoder self-check).*
