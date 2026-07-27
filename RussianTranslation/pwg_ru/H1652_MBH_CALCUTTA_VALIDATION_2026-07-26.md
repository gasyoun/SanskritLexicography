# MBH. Calcutta↔critical: the candidate map, measured and rejected (H1652)

_Created: 26-07-2026 · Last updated: 26-07-2026_

MG ruled on 21-07-2026 (weekly `@DECIDE` sheet) that the Mahābhārata citation-reuse
gap should be **closed by building** the Calcutta↔critical concordance rather than
accepted, with the steer that a prior artifact might already exist. This report is
the outcome: the artifact does exist, the map it makes possible was built, and the
map **does not work**. `MBH.` stays `unmapped_locus_scheme` in
[`src/citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py).

Everything below is reproducible from
[`src/build_mbh_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_mbh_concordance.py)
(`build` · `validate` · `selftest`).

## The problem

PWG cites the **Calcutta edition (1834–39)**, which numbers ślokas continuously
within each parvan and gives no adhyāya coordinate: `MBH. 5,7331` means
Udyogaparvan śloka 7331 and nothing more. SamudraManthanam's `corpus.db` keys the
**BORI/Poona critical** edition as `parvan.adhyāya.verse`. With 3,199 two-number
`MBH.` citations in the RU store (5,512 references by the citation index's count,
the most-cited text in PWG), this is the largest single block of un-reusable
citations.

## The prior art MG remembered — it is real

[CommentaryStrategies](https://github.com/gasyoun/CommentaryStrategies) ships a
**Nīlakaṇṭha-vulgate ↔ critical verse concordance for all eighteen parvans**
(`data/edition_comparison_mbh/*/concordance.json`, built by its
`scripts/compare_editions_mbh.py` through content alignment of canonicalised IAST).
It had never been wired into anything in this repo. Registering it is a separate
deliverable of H1652 (see
[`Uprava/PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)).

Calcutta and the Nīlakaṇṭha vulgate belong to the same recension family, so the
missing step looked purely arithmetic: sum the vulgate's per-adhyāya verse counts,
and continuous śloka *N* falls in the adhyāya whose running total brackets it. That
sum is committed as
[`src/mbh_vulgate_cumulative.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mbh_vulgate_cumulative.tsv)
(2,110 rows). **It is documentation of a rejected hypothesis, not a lookup path.**

## First warning: the witness is too short

| parvan | vulgate verses (e-text) | highest PWG citation | shortfall |
|---|---:|---:|---:|
| 1 Ādi | 8,623 | 8,882 | −259 |
| 2 Sabhā | 2,713 | 2,846 | −133 |
| 3 Vana | **11,859** | **17,471** | **−5,612** |
| 4 Virāṭa | 2,270 | 2,359 | −89 |
| 5 Udyoga | 6,613 | 7,656 | −1,043 |
| 12 Śānti | 13,763 | 13,943 | −180 |
| 13 Anuśāsana | 7,469 | 7,735 | −266 |
| 14 Āśvamedhika | 2,845 | 2,871 | −26 |

Eight of eighteen parvans are shorter than the text PWG counts, catastrophically so
in the Vanaparvan (−32%). **145 store citations name a śloka past the end of their
entire parvan** — for those no ordinal exists at any accuracy. The remaining ten
parvans have plausible totals, which is a necessary condition, never a sufficient one.

## The measurement

Every `MBH. P,N` citation is carried by a card with a known headword. If the map is
right, the mapped verse should contain that headword. So: take *N* as the vulgate
ordinal, walk the concordance to the critical verse, fetch its IAST from `corpus.db`,
and ask where the folded headword stem actually occurs in that parvan.

A substring test has a background rate, so every figure is reported against a
**uniform-random null** — the same anchors with *N* replaced by a random ordinal of
the same parvan.

| test | n | within ±2 verses | within ±10 |
|---|---:|---:|---:|
| identity (N as the vulgate ordinal) | 1,327 | **11.2%** | 21.2% |
| uniform-random null | 1,327 | 2.5% | 7.0% |
| per-parvan linear rescale, held-out half | 668 | **16.3%** | 31.7% |
| identity on the same held-out half | 668 | 10.9% | 20.7% |
| unique-occurrence anchors (strictest) | 43 | **1 (2.3%)** | 2 (4.7%) |

The rescale row matters because the shortfall above suggests a proportional
correction might absorb it. A per-parvan scale was fitted by search over 0.30–1.40
on a random half of the anchors and scored on the other half: it lifts ±2 accuracy
from 10.9% to 16.3%. Real, and nowhere near enough.

The last row is the cleanest evidence. Restricted to citations whose headword stem
occurs **exactly once in the whole parvan** — where the true verse is not a
judgement call but the only candidate — the cumulative map is right **once in 43
tries**. Stem quality is not the limiting factor: filtering to simple headwords of
6 and of 8+ characters gives 10.7% and 12.2%, statistically the same as the 11.2%
overall.

## The chain below the failing step is sound

A negative result is worthless if the plumbing is broken, so the two lower links
were verified independently against a passage whose location nobody has to trust me
about — Bhagavadgītā 2.47, which sits inside the Bhīṣmaparvan:

- concordance: vulgate `6.26.47` → critical `6.24.47` (`variant`, similarity 0.96);
- corpus: `06_mahabharata-bhishmaparva:6.24.47#sa` = `karmaṇyevādhikāraste mā
  phaleṣu kadācana …`, and `karmaṇyevādhikāras` occurs at exactly that one key in
  the whole parvan.

So the concordance and the corpus keying both do what they claim. What fails is the
**first** step: PWG's Calcutta numbering is not the cumulative ordinal of this
vulgate witness.

## Hand-checkable anchors

Thirty of the 43 unique-occurrence anchors, seeded and reproducible via
`build_mbh_concordance.py validate`. "True ordinal" is the only verse in the parvan
carrying the headword; "off" is how far the cumulative map missed it.

| # | PWG citation | headword | predicted ordinal | true ordinal | true vulgate adhy.verse | true critical | off |
|---:|---|---|---:|---:|---|---|---:|
| 1 | MBH. 1,3668 | prati+gam | 3668 | 3695 | 93.5 | 1.88.5 | −27 |
| 2 | MBH. 1,4427 | abhiśru | 4427 | 8458 | 228.32 | 1.219.28 | −4031 |
| 3 | MBH. 4,652 | anucar | 652 | 242 | 8.13 | 4.7.11 | +410 |
| 4 | MBH. 4,1042 | antardhā | 1042 | 2161 | 69.14 | 4.64.32 | −1119 |
| 5 | MBH. 4,1683 | antardhā | 1683 | 2161 | 69.14 | 4.64.32 | −478 |
| 6 | MBH. 5,1195 | anvālabh | 1195 | 1170 | 35.14 | 5.35.10 | +25 |
| 7 | MBH. 6,466 | pravas | 466 | 4102 | 91.31 | 6.87.30 | −3636 |
| 8 | MBH. 6,2407 | saṃniviś | 2407 | 1379 | 39.15 | 6.37.15 | +1028 |
| 9 | MBH. 7,5812 | abhyāviś | 5812 | 5813 | 139.125 | 7.114.94 | **−1** |
| 10 | MBH. 11,125 | samanugam | 125 | 122 | 5.1 | 11.5.1 | +3 |
| 11 | MBH. 12,2036 | anuvihan | 2036 | 2015 | 56.51 | 12.56.51 | +21 |
| 12 | MBH. 12,4180 | pratilabh | 4180 | 4135 | 112.7 | 12.113.7 | +45 |
| 13 | MBH. 12,5272 | vinis+pat | 5272 | 5214 | 140.25 | 12.138.25 | +58 |
| 14 | MBH. 12,6108 | pari-vid | 6108 | 6036 | 165.68 | 12.159.63 | +72 |
| 15 | MBH. 12,6530 | abhyāhan | 6530 | 4228 | 116.21 | 12.117.19 | +2302 |
| 16 | MBH. 12,6839 | pra+bhid | 6839 | 6751 | 184.19 | 12.177.19 | +88 |
| 17 | MBH. 12,7002 | anusaṃcar | 7002 | 11035 | 301.111 | 12.290.106 | −4033 |
| 18 | MBH. 12,7415 | pratyādā | 7415 | 7314 | 202.22 | 12.195.22 | +101 |
| 19 | MBH. 12,9719 | abhy-ā-car | 9719 | 9567 | 270.14 | 12.262.12 | +152 |
| 20 | MBH. 12,10583 | samupa+śam | 10583 | 10415 | 287.32 | 12.276.31 | +168 |
| 21 | MBH. 12,10800 | anvāviś | 10800 | 4546 | 124.48 | 12.124.47 | +6254 |
| 22 | MBH. 12,12747 | antardhā | 12747 | 12560 | 335.51 | 12.322.48 | +187 |
| 23 | MBH. 12,13928 | pratyabhyanujñā | past the end (13,763) | 13748 | 364.4 | 12.352.4 | n/a |
| 24 | MBH. 13,18 | samupa+nī | 18 | 2715 | 55.5 | 13.55.5 | −2697 |
| 25 | MBH. 13,307 | upalabh | 307 | 2317 | 45.7 | 13.45.8 | −2010 |
| 26 | MBH. 13,2477 | ni+bandh | 2477 | 2344 | 46.11 | 13.46.10 | +133 |
| 27 | MBH. 13,4284 | apagam | 4284 | 2079 | 38.25 | 13.38.25 | +2205 |
| 28 | MBH. 13,5279 | adhyā+vas | 5279 | 6857 | 151.12 | 13.136.12 | −1578 |
| 29 | MBH. 13,7306 | pratisam+śru | 7306 | 6989 | 156.16 | 13.141.16 | +317 |
| 30 | MBH. 13,7541 | ni+bandh | past the end (7,469) | 2344 | 46.11 | 13.46.10 | n/a |

Two shapes are visible. Within the Śāntiparvan block (rows 11–22, excluding the
outliers) the miss grows smoothly with *N* — +21, +45, +58, +72, +88, +101, +152,
+168, +187 — a drift of roughly 1.5%, exactly what a slightly-shorter witness
produces. That is the part a linear rescale can absorb. The rest — ±2,000 to ±6,300
— is not drift at all; some of those are cases where the stem's single visible
occurrence is not the cited passage (the citation's verse carries the headword in a
sandhi'd or inflected form the substring test cannot see), which is precisely why
the aggregate figures are reported against a null rather than read raw.

## Verdict and what would actually close it

**REJECTED.** A ~16% verse-level accuracy would hand the translator model the wrong
verse's Russian five times out of six — the failure mode
[H1656](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1656-Opus_SanskritLexicography_gorresio-southern-critical-concordances_26.07.26.md)
had just finished removing from the `R.` path, where in-range Gorresio loci were
silently returning a Southern verse's translation. A miss stays a miss.

The handoff's autonomy clause reserved a middle band (60–90% anchor agreement) for a
human to set the threshold. That fork does not fire: 2–17% is unambiguously below it.

The root cause is not the method but the input. **We do not have the Calcutta
edition at all.** The sanatana.in Nīlakaṇṭha scrape is a different, shorter witness,
and no arithmetic over it can reconstruct a numbering it does not carry. A successor
needs one of:

1. **The Calcutta text (1834–39) itself**, then a content-based alignment of the
   H1656 kind (Calcutta → vulgate → the existing concordances → critical). This is
   the only route that closes the gap fully.
2. **A published Calcutta↔critical concordance.** None is known to this project;
   the critical edition's apparatus is not one.
3. **Accept the GAP** and leave `unmapped_locus_scheme` standing, which is the
   current, honest state.

Route 1 stands or falls on the text, so the useful next act is an acquisition probe
for a Calcutta-edition e-text or scan, not another modelling attempt.

## Addendum, same day — the probe ran, and route 1 is open

MG pointed at the scan; the probe (H1707) found both halves of what route 1 needs.

**1. The scan, with a citation-grade page index.**
[sanskrit-lexicon-scans/mbhcalc](https://github.com/sanskrit-lexicon-scans/mbhcalc)
holds the Asiatic Society four-volume printing (1834–39, BSB source scans) as 3,006
page PDFs, plus `parvanverse.js` — the exact analogue of the Gorresio `ksverse.js` this
project already consumes: `(parvan, continuous śloka) → (volume, page)`, i.e. **PWG's
citation scheme natively**. Measured against the store: **3,007 of 3,009 distinct
`MBH.` loci (99.9%) resolve to a page**; the two misses are single outliers in parvans
1 and 2. Parvan 12 matches to the exact śloka (index 13,943, PWG's highest citation
13,943). Page-level click-through for the most-cited text in the dictionary is therefore
available **today**, with no OCR and no alignment — the same surface `ls_resolver.py`
already provides for R. GORR.

The one caveat the index carries: Vanaparvan numbering is non-monotonic once (after
12,000 it drops to 10,195 before continuing to 17,478), a feature of the printed
edition's own numbering that PWG follows — the repo ships a `corrected.…index…txt`
alongside the raw one.

**2. An e-text, via a proxy — and it is better than OCR.** The page PDFs are
image-only (0 characters of embedded text; the Gorresio trick does not repeat here). A
single page was OCRed as a feasibility check — tesseract-5 `san` on `mbhcalc_2.319.pdf`
rendered at 4× produced readable but noisy Devanagari, roughly the H1689 Gorresio
quality. **That route is now unnecessary.** Sarkar, Jagadeeshan & Goyal, *Recovering the
Calcutta Edition of the Mahābhārata for Computational Analysis* (ISCLS 2026) aligned the
M. N. Dutta text — digitized in the Itihāsa dataset, and a Calcutta-recension witness —
back onto the printed Calcutta Edition, verse-level, ~88% coverage, released CC at
[sujoysarkarai/mahabharatace](https://github.com/sujoysarkarai/mahabharatace). Its
`ce_verse_number` column **is the continuous per-parvan śloka**: volume 5 runs 1..7,655
against `parvanverse.js`'s 7,657 and PWG's highest Udyoga citation 7,656. 9,125 of its
13,091 parvan-5 lines are `manual_anchor` — verified against the physical volumes.

**End-to-end proof on the citation that started this handoff.** `MBH. 5,7331` →
`mahabharatace` volume 5, `ce_verse_number` 7331 (`manual_anchor`) → «भीष्ममेव प्रपद्यस्व न
तेऽन्या विद्यते गतिः । निर्जितो ह्यस्मि भीष्मेण महास्त्राणि प्रमुञ्चता ॥» → verbatim in
`05_mahabharata-udyogaparva:5.187.1-4#sa` as verse ॥4॥ → and that key **has** its
Russian translation of record (Kalyanov, 537 chars, ending «И я побежден Бхишмой,
мечущим могучие виды оружия!»).

So the rejection above stands exactly as measured — the cumulative-adhyāya bridge over
the vulgate does not work — but the conclusion "closing this needs the Calcutta text"
is now a **task, not a blocker**. The remaining work is a content alignment of the
`mahabharatace` lines to the corpus's critical keying (the same n-gram + monotonic
anchoring machinery `build_ramayana_concordance.py` already runs), scoped by the ~88%
coverage and the `CONFLICT`/`unprocessed` rows the release flags honestly.

_Dr. Mārcis Gasūns_
