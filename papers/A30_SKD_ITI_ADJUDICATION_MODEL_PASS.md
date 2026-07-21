# A30/A02/A08 — SKD *iti*-unit adjudication sample: MODEL PASS (not human gold)

_Created: 21-07-2026 · Last updated: 21-07-2026_

**This is a model-labelled pass by Fable 5 (`claude-fable-5`), 21-07-2026, under
[H1382](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1382-Fable_SanskritLexicography_a30-hostile-referee-pass-skd-vcp_20.07.26.md).
It is NOT the human adjudication that A30's limitation 1, A02's revision brief and A08's
C-M1 all require — that gate remains open.** Presenting model labels as the human gold would
reproduce the exact portfolio defect (§6.1 of
[PORTFOLIO_STATISTICAL_REDTEAM_2026H2.md](https://github.com/gasyoun/Uprava/blob/main/docs/PORTFOLIO_STATISTICAL_REDTEAM_2026H2.md))
this pass exists to expose. Companion to
[papers/A30_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_review_fable5.md).

Sample: the committed 102-row stratified draw in
[`REVIEW_SKD_ITI_ADJUDICATION.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html)
(same rows as
[`r2_kosa_fusion_sample.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion_sample.json)),
34 rows per classifier class, read at csl-atlas `origin/main` commit `a56444f`. Label
vocabulary as defined by the sheet: **citational** (names or quotes an authority — an
author, a work, a commentary) / **grammatical** (the *iti* closes a derivation,
definition-clause, or other non-citational construction) / **unclear** (not decidable out of
context).

## 1. Sample-readiness assessment (is the sheet fit for the human pass?)

1. **Stratification is right for classifier validation, wrong-by-omission for A08's
   question.** Equal 34/34/34 sampling per classifier class is the correct design for
   checking each output class — but the population is wildly unequal (authority-terminal
   12,831 · separable 11,256 · other-no-authority 98,604 = 10.5 % / 9.2 % / 80.4 %), and the
   sheet nowhere states the post-stratification weights needed to answer A08's "≥ X %
   citational" question from the votes. Add the weights note before the human pass.
2. **Sampling is systematic (every ⌊pool/34⌋-th row), not random** — fine for a review
   sheet, but say so; a referee asked to trust "a stratified ~100-unit sample" will ask.
3. **Blocking defect: rows are severed exactly before the deciding evidence.** The unit
   splitter cuts after standalone *iti*, so for the dominant `other-no-authority` class,
   15 of 34 rows end at "… iti" with the authority name (or its absence) sitting in the
   *next*, invisible unit. A human cannot decide these out of context any better than a
   model. **Regenerate the sheet with a following-context column** (the next unit's leading
   ~40 characters) before spending human time; otherwise ~44 % of the largest class's votes
   will be forced "unclear".
4. **The vocabulary needs one convention ruling:** Pāṇinian sūtra quotations inside
   derivations (rows 72, 80, 94 below: "… 4.2.19 . iti", "3.1.135 . iti", "3.3.93 . iti")
   *quote a work* but function as grammatical apparatus. Ruled **grammatical** here (the
   sheet's "derivation" clause); the human sheet should state the ruling either way, or the
   citational-share estimate moves by a few points on this convention alone.

## 2. Model labels — tally

| Classifier class | citational | grammatical | unclear | n |
|---|---:|---:|---:|---:|
| authority-terminal | 34 | 0 | 0 | 34 |
| separable | 34 | 0 | 0 | 34 |
| other-no-authority | 13 | 6 | 15 | 34 |
| **total** | **81** | **6** | **15** | **102** |

- **Among decidable units: 81/87 = 93 % citational.** The *iti*-register is overwhelmingly a
  citation register in SKD — A08's central premise survives this pass.
- **Population-weighted citational share: between ≈ 52 % and ≈ 87 %**, depending entirely on
  how the 15 severed-unclear rows (all in the 80.4 %-weight class) resolve. Their surface
  pattern — a sense enumeration closing "… . iti" with the source name in the next unit —
  is the standard SKD citation formula, so most would likely resolve citational, pushing the
  weighted share toward the top of that range; but that is exactly what the context column
  (§1.3) must let a *human* decide.
- **Both misclassification directions in the classifier are visible.** All 34 sampled
  "separable" units are citational — about 24 are bare severed name-tails (*medinī* ×13,
  *hemacandraḥ* ×11, …), plus genuinely fused short units (rows 39, 44, 62) pushed there by
  the 20-char threshold. And 13 of 34 "no-authority" units contain plain authority names the
  16-name curated list misses (*halāyudha*, *rājanirghaṇṭa* ×3, *trikāṇḍaśeṣa*,
  *durgādāsa*, *sāyaṇa*, …).

## 3. What the fusion figures would become if this split held

The headline 53.3 % (SKD) / 77.6 % (VCP) fusion rates are computed over the classifier's
24,087 / 42,980 "authority-marked" units. This pass shows that denominator is a **biased
~30 % subsample** of SKD's true citation register (A08 counts 80,164 *iti*-citations), with
both known misclassification streams landing one-sidedly in "separable". If the model split
held: the authority-marked denominator would roughly **triple**; the severed name-tails
(most of today's "separable" class) would rejoin their content units as *fused*; and the
20-char threshold would still misclass short fused runs. Net direction: **SKD's fusion rate
would rise, by an amount this sample cannot quantify** — so the published 53.3/77.6 contrast
should be treated as unstable under instrument repair, not as a measured register property.
Recomputation belongs to csl-atlas (the segmenter build), not to this paper's
no-new-computation scope.

## 4. Per-row model labels

Notes use: *severed-tail* = leading bare authority name (split artifact); *severed-before-name* =
unit ends "… iti", deciding name in next unit; *FP-trigger* = the classifier's authority match
was a non-citational formula even though the label here reflects the whole unit's content.

| # | L | headword | class | model label | note |
|---:|---|---|---|---|---|
| 0 | 1 | a | auth-term | citational | quotes varṇa-catalogue verse with authority close |
| 1 | 1201 | anṛjuḥ | auth-term | citational | *ityamaraḥ* |
| 2 | 2268 | arpisaḥ | auth-term | citational | *ity-uṇādikośaḥ* (hyphen-split) |
| 3 | 3336 | āḍhyaḥ | auth-term | citational | *ityamaraḥ*; also non-citational *ityādiḥ* (example closer) |
| 4 | 4361 | ukṣā | auth-term | citational | *ityamaraḥ* + Ṛgveda, Kumārasambhava |
| 5 | 5296 | ūrjasvī | auth-term | citational | *ityamaraḥ* + Bhārata |
| 6 | 6406 | kambuḥ | auth-term | citational | Mahābhārata quote |
| 7 | 7634 | kāsāraḥ | auth-term | citational | *ityamaraḥ* + Gītagovinda |
| 8 | 8904 | kaidāraḥ | auth-term | citational | **FP-trigger** *ityarthaḥ* (gloss formula); real citation = Bhāvaprakāśa |
| 9 | 10306 | gajaḥ | auth-term | citational | *ityamaraḥ* + Śabdārthacintāmaṇi |
| 10 | 11668 | glauḥ | auth-term | citational | *ityamaraḥ* + Atharvaveda |
| 11 | 13123 | jaḍimā | auth-term | citational | *ity-ujjvalanīlamaṇiḥ* |
| 12 | 14583 | talpam | auth-term | citational | *ityamarabharatau* + Manu |
| 13 | 16047 | darvikā | auth-term | citational | Rāyamukuṭa in Amara-ṭīkā |
| 14 | 17652 | dharaṇīdharaḥ | auth-term | citational | quote + *ityādi-gopīnāthatarkācāryaḥ* |
| 15 | 18988 | nimnagā | auth-term | citational | *ityamaraḥ* + Manu |
| 16 | 20228 | padmacāriṇī | auth-term | citational | *ityamaraḥ* |
| 17 | 21336 | pārśvaḥ | auth-term | citational | Pārśvanāthacarita quote |
| 18 | 22413 | paitram | auth-term | citational | *ityamaraḥ* + Mahābhārata |
| 19 | 23379 | prāṇathaḥ | auth-term | citational | *ity-uṇādikośaḥ* |
| 20 | 24544 | brāhmam | auth-term | citational | *ityamaraḥ* + Āhnikatattva |
| 21 | 25740 | maṇiḥ | auth-term | citational | uṇādi-sūtra + Raghuvaṃśa |
| 22 | 27099 | mādhavīlatā | auth-term | citational | Bharata in Amara-ṭīkā |
| 23 | 28294 | yajñaḥ | auth-term | citational | *ityamaraḥ* |
| 24 | 29568 | rāmaḥ | auth-term | citational | Padmapurāṇa + Adhyātmarāmāyaṇa |
| 25 | 30996 | vadhodyataḥ | auth-term | citational | *ityamaraḥ* + Bṛhaspati |
| 26 | 32260 | vāstu | auth-term | citational | vāstu verse quotations |
| 27 | 33476 | viṣyaḥ | auth-term | citational | *ityamaraḥ* |
| 28 | 34535 | vyūḍhakaṅkaṭaḥ | auth-term | citational | *ityamaraḥ* |
| 29 | 35699 | śivakaḥ | auth-term | citational | *ityamaraḥ* |
| 30 | 37137 | saṃyat | auth-term | citational | *ityamarabharatau*; also grammatical vārttika refs |
| 31 | 38079 | samupajoṣam | auth-term | citational | Rāmāśrama in Amara-ṭīkā |
| 32 | 39345 | sucelakaḥ | auth-term | citational | *ityamaraḥ* |
| 33 | 40809 | spṛṣṭāspṛṣṭi | auth-term | citational | Bṛhaspati in Ratnākara |
| 34 | 2 | a | separable | citational | severed-tail *medinī* + verse quote |
| 35 | 1248 | antargatam | separable | citational | severed-tail *hemacandraḥ* |
| 36 | 2304 | alam | separable | citational | severed-tail *hemacandraḥ* |
| 37 | 3568 | āviddhaḥ | separable | citational | severed-tail *medinī* |
| 38 | 4624 | udagadriḥ | separable | citational | severed-tail *hemacandraḥ* |
| 39 | 5630 | oḥ | separable | citational | **genuinely fused**, under 20-char threshold (*vrahmā . ityekākṣarakośaḥ*) |
| 40 | 6836 | kalācikā | separable | citational | severed-tail *hemacandraḥ* |
| 41 | 8000 | kuṇḍam | separable | citational | severed-tail *medinī* |
| 42 | 9150 | kauśikaḥ | separable | citational | severed-tail *medinī* |
| 43 | 10669 | garttikā | separable | citational | severed-tail *hemacandraḥ* + locus |
| 44 | 11871 | ghoṇī | separable | citational | **genuinely fused**, under threshold (*śūkaraḥ . ityamaraḥ*) |
| 45 | 12969 | chāyā | separable | citational | severed-tail *medinī* |
| 46 | 14141 | ḍhaḥ | separable | citational | *medinī* + *ityekākṣarakośaḥ* |
| 47 | 15476 | trāyantī | separable | citational | *ityamaraḥ* + medical verse |
| 48 | 16736 | duliḥ | separable | citational | severed-tail *medinī* + locus |
| 49 | 17962 | dhūrttaḥ | separable | citational | *medinī* + Mahābhārata, Pañcatantra |
| 50 | 19169 | nirvāṇam | separable | citational | *medinī* + Bhāgavata |
| 51 | 20551 | parimaṇḍalam | separable | citational | *hemacandraḥ* + Bhāgavata |
| 52 | 21728 | pītā | separable | citational | *ityamaraḥ* + Vaidyakaratnamālā |
| 53 | 22950 | pradoṣaḥ | separable | citational | *hemacandraḥ* + Māgha |
| 54 | 24149 | bahuphalī | separable | citational | severed-tail *medinī* + locus |
| 55 | 25508 | bhautī | separable | citational | severed-tail *hemacandraḥ* + locus |
| 56 | 26821 | mahāvīraḥ | separable | citational | severed-tail *hemacandraḥ* |
| 57 | 28137 | mokṣaḥ | separable | citational | *hemacandraḥ* + Gītā |
| 58 | 29461 | rājavartma | separable | citational | severed-tail *hemacandraḥ* + locus |
| 59 | 30713 | vam | separable | citational | severed-tail *medinī* + locus |
| 60 | 31946 | vānam | separable | citational | severed-tail *medinī*; unit also holds a grammatical *iti* |
| 61 | 33016 | virañciḥ | separable | citational | severed-tail *hemacandraḥ* |
| 62 | 34212 | vaidehaḥ | separable | citational | **genuinely fused**, under threshold (*baṇik . ityamaraṭīkāyāṃ bharataḥ*) |
| 63 | 35432 | śālāram | separable | citational | severed-tail *medinī* |
| 64 | 36833 | śvetaḥ | separable | citational | severed-tail *hemacandraḥ* |
| 65 | 38138 | samprahāraḥ | separable | citational | severed-tail *medinī* |
| 66 | 39327 | sugṛhaḥ | separable | citational | severed-tail *hemacandraḥ* |
| 67 | 40617 | sthāsnuḥ | separable | citational | *ityamaraḥ* + Bhaṭṭi |
| 68 | 1 | a | no-auth | unclear | severed-before-name (phonological definition "… iti") |
| 69 | 1501 | apācī | no-auth | citational | **missed name**: *halāyudhaḥ* |
| 70 | 2822 | aśvatthaḥ | no-auth | unclear | purāṇic quotation fragment, source severed |
| 71 | 4313 | īśam | no-auth | citational | **missed name**: *medinīkarahemacandrau* + Kumārasambhava |
| 72 | 5694 | audaśvitam | no-auth | grammatical | Pāṇini 4.2.19 quoted in derivation (see §1.4) |
| 73 | 6938 | kavarī | no-auth | grammatical | *(iti) bhāṣā* — vernacular register label |
| 74 | 8159 | kumbhīpākaḥ | no-auth | citational | **missed name**: Bhāgavata 6.26.7 (source typo *śrīmāgavate*) |
| 75 | 9421 | kṣattriyaḥ | no-auth | citational | **missed name**: Skandapurāṇa, Reṇukāmāhātmya |
| 76 | 10605 | gabhastimān | no-auth | unclear | severed-before-name (*sūryaḥ . iti* …) |
| 77 | 11736 | ghanaśyāmaḥ | no-auth | citational | Mahānāṭaka named + quoted |
| 78 | 12945 | chāgaḥ | no-auth | grammatical | nirvacana gloss *iti* |
| 79 | 14156 | ṇakha | no-auth | unclear | root entry, severed-before-name (Kavikalpadruma pattern) |
| 80 | 15395 | toyadhipriyam | no-auth | grammatical | Pāṇini 3.1.135 in derivation |
| 81 | 16657 | durārohaḥ | no-auth | citational | **missed name**: *rājanirghaṇṭaḥ* + Mahābhārata |
| 82 | 17951 | dhūmrapatrā | no-auth | citational | **missed name**: *rājanirghaṇṭaḥ* |
| 83 | 19244 | niśācarma | no-auth | citational | **missed name**: *trikāṇḍaśeṣaḥ* |
| 84 | 20548 | paribhāṣā | no-auth | unclear | severed-before-name (definition "… vāk . iti") |
| 85 | 21668 | pīḍa | no-auth | unclear | root entry, severed-before-name |
| 86 | 22951 | pradyu | no-auth | citational | **missed name**: Durgādāsa in Mugdhabodha-ṭīkā |
| 87 | 24204 | bahvapatyaḥ | no-auth | unclear | severed-before-name (sense run "… iti") |
| 88 | 25288 | bhūmayī | no-auth | unclear | severed-before-name |
| 89 | 26380 | marūkaḥ | no-auth | citational | **missed name**: *saṃkṣiptasāroṇādivṛttiḥ* |
| 90 | 27521 | mukhasuram | no-auth | grammatical | *(iti) bhāṣā* label |
| 91 | 28640 | yugāntaḥ | no-auth | unclear | severed-before-name |
| 92 | 29776 | rudrāṇī | no-auth | citational | **missed name**: *rājanirghaṇṭaḥ* |
| 93 | 30911 | vaṭakaḥ | no-auth | citational | Śārṅgadhara named; metrological verse closed by *iti* |
| 94 | 32087 | vāridhiḥ | no-auth | grammatical | Pāṇini 3.3.93 in derivation |
| 95 | 33424 | viṣuṇaḥ | no-auth | citational | **missed name**: *tadbhāṣye sāyaṇaḥ* |
| 96 | 34620 | śa | no-auth | unclear | severed-before-name (phonological definition) |
| 97 | 35797 | śīghrajanmā | no-auth | unclear | *bhāṣā* tail + quoted verse, source severed |
| 98 | 36954 | ṣaḍūṣaṇam | no-auth | unclear | quoted medical verse, source severed |
| 99 | 38283 | sarja | no-auth | unclear | root entry, severed-before-name |
| 100 | 39625 | suraktaḥ | no-auth | unclear | severed-before-name (sense run "… iti") |
| 101 | 40952 | syandaniḥ | no-auth | unclear | severed-before-name |

## 5. What remains for the human gate

1. Regenerate the sheet with the following-context column and the weighting note (§1), then
   the human pass — unchanged as the outstanding gate for A30 §6, A02's revision brief Part 4
   and A08's C-M1. This model pass may be shown beside the human votes afterwards as an
   inter-annotator comparison, never instead of them.
2. The convention ruling on Pāṇinian sūtra quotes (§1.4) is a one-line decision that should
   be recorded on the sheet itself.
3. The classifier repairs implied by §2 (name-aware splitting, expanded authority list,
   formula exclusion) are csl-atlas work, tracked via the A30 review's Disposition table —
   not this paper's scope.

_Dr. Mārcis Gasūns_
