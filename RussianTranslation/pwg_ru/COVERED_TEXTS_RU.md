# Covered texts — Russian translations of record for PWG citations

_Created: 19-07-2026 · Last updated: 27-07-2026_

When a PWG card cites a passage of a text that **already has a published or aligned
Russian translation** (R., MBH., ṚV., KATHĀS., …), the card's citation should **reuse
that translation** rather than re-translate the Sanskrit — for every covered text,
everywhere, not ad hoc per citation. This is the registry of every text with an RU asset,
the per-text translation-of-record policy, and the lookup that wires reuse into the
pipeline. Born from MG's 19-07-2026 vote on the first H178 bake-off sheet (register rows
N1, N6, N9, N11, N18 —
[H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md),
fan-out [H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md)).

> **Rights (public repo).** Every RU translation of record below (Elizarenkova, Leonov,
> «Океан сказаний», Ignatiev, …) is **in-copyright**. This file commits **metadata,
> counts, loci, and policy only — never translation text**. The reuse lookup
> ([`src/citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py))
> returns RU text for a **generation-time consult only** (fed to the translator model so
> it does not re-translate a covered citation); that text is never persisted to a
> committed or public artifact. The 166k-hallucination lesson stands: a MISS stays a
> miss; a model never fills a missing translation-of-record from world knowledge.

## What the data says

The census crosses three measured inputs, none rebuilt here (§Prior art):

- **PWG `<ls>` citation frequency** — 36,546 distinct literary-source references across
  709 abbreviations, from
  [`src/build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
  over the RU store (the "PWG refs" column below is its distinct-reference count).
- **Verse-aligned RU corpus** — 119 works carry paired Sanskrit + Russian verse lines in
  SamudraManthanam's `corpus.db` (the `#sa`/`#ru` `canonical_id` pairs the lookup reads;
  richer than the 116 word-aligned works in
  [`aligned_works.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/aligned_works.txt)).
- **Ignatiev archive** — 23 Sanskrit-translation works (62 files) in the local-only
  `SamudraManthanam/archive_ignatiev_2026/`, not yet ingested (§Ignatiev queue).

The wins are at the intersection **PWG-cites × RU-exists**: the epics and saṃhitās (MBH.
5,512 refs, ṚV. 3,433, R. 2,970, KATHĀS. 1,419, AV. 1,110, Manu 1,444, RAGH. 566) are all
verse-aligned and locus-lookupable. The gaps are heavily-cited texts with **no** RU
(ŚAT. BR. 1,620 refs, HARIV. 867, SUŚR. 277) and one remaining **concordance gap**
(MBH. continuous-Calcutta — the candidate map was built, measured and rejected
26-07-2026, H1652). The second such gap — R. GORR. / Bengal recension — was
**closed 26-07-2026** by the H1656 CONTENT-BASED Gorresio↔Southern verse concordance
(reuse ON, § R. GORR.). Note the Gorresio scheme covers more than the 657 explicit
R. GORR. refs: PWG's plain `R.` is itself a three-edition composite (pwgbib 1.247 —
books 1–2 Schlegel, **books 3–6 Gorresio**, book 7 Bombay), verified against the
store's cited sarga ranges (H1656), so ~1,560 plain-`R.` book-3–6 refs ride the same
concordance — see §R. GORR.

## Census — every text with an RU asset

Tier: **verse-aligned** = paired `#sa`/`#ru` in `corpus.db`, locus-lookupable ·
**ingestion queue** = RU exists (Ignatiev/other) but not in the corpus · **not ingested**
= no known RU · **GAP** = RU exists but the citation scheme has no corpus map. "ToR" =
is this the translation of record for citation reuse. Counts computed by
[`build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
+ the `corpus.db` inventory, never hand-typed.

| PWG `<ls>` | text | RU translation of record | corpus work | tier | RU verses | PWG refs | rights | ToR |
|---|---|---|---|---|---:|---:|---|---|
| MBH. | Mahābhārata | SamudraManthanam (multiple RU translators, per parvan) | `01–18_mahabharata-*` | verse-aligned | (18 parvans) | 5512 | meta | Y — per-parvan alignment |
| ṚV. | Ṛgveda | Elizarenkova (1989–1999), 1:1 | `01–10_rigveda` | verse-aligned | (10 maṇḍalas) | 3433 | meta | Y — Elizarenkova 1:1 (MG N6); German divergence marked separately |
| R. | Rāmāyaṇa (composite: Schlegel 1–2 / Gorresio 3–6 / Bombay 7) | Leonov / Gryntser | `01–06_ramayana-*kāṇḍa` | verse-aligned | (4 kāṇḍas in corpus) | 2970 | meta | Y — books 1–2 direct (Schlegel≈vulgate); books 3–6 via the Gorresio concordance, hits flagged (§R. GORR.) |
| R. GORR. | Rāmāyaṇa (Gauḍīya/Bengal, ed. Gorresio) | Leonov via CONTENT-BASED concordance (H1656+H1689) | via map | verse-aligned (mapped share) | 5926 mapped vv | 657 | meta | Y — reuse ON, map class+score travels; typed misses for Bengal-only (§R. GORR.) |
| BHĀG. P. | Bhāgavata-purāṇa | Ignatiev (archive, NOT ingested) | `—` | ingestion queue | — | 2035 | meta | pending ingest |
| KATHĀS. | Kathāsaritsāgara | «Океан сказаний» (RU) | `kathasaritsagara` | verse-aligned | 3266 | 1419 | meta | Y |
| AV. | Atharvaveda | (RU, corpus) | `01–19_atharvaveda` | verse-aligned | (19 kāṇḍas) | 1110 | meta | Y |
| ŚAT. BR. | Śatapatha-brāhmaṇa | — (no full RU) | `—` | not ingested | — | 1620 | — | N |
| M. | Mānava-dharmaśāstra (Manu) | (RU, corpus) | `manavadharmashastra` | verse-aligned | 2686 | 1444 | meta | Y |
| HARIV. | Harivaṃśa | — (no full RU in corpus/archive) | `—` | not ingested | — | 867 | — | N |
| RAGH. | Raghuvaṃśa | (RU, corpus) | `raghuvamsha` | verse-aligned | 400 | 566 | meta | Y |
| PAÑCAT. | Pañcatantra | — (RU exists; not ingested) | `—` | ingestion queue | — | 482 | — | pending ingest |
| TS. | Taittirīya-saṃhitā | — (no full RU; partial TM only) | `—` | not ingested | — | 353 | — | N — TM-assisted fresh (MG N18) |
| MĀRK. P. | Mārkaṇḍeya-purāṇa | Ignatiev (Devī-māhātmya portion) | `—` | ingestion queue | — | 355 | meta | partial |
| KUMĀRAS. | Kumārasambhava | (RU, corpus) | `kumarasambhava` | verse-aligned | 614 | 139 | meta | Y |
| MEGH. | Meghadūta | (RU, corpus) | `megha-duta` | verse-aligned | 115 | 114 | meta | Y |
| KĀM. | Kāmasūtra (Vātsyāyana) | (RU, corpus) | `kama-sutra` | verse-aligned | 1502 | 0 | meta | asset-only |
| BHAG. | Bhagavadgītā | 12 RU versions (Smirnov, Semencov, Erman, …) | `bhagavadgita-*` | verse-aligned | (12 versions) | 205 | meta/pd | Y — choose ToR per policy |
| GĪT. | Gītagovinda | (RU, corpus) | `gitagovinda` | verse-aligned | 289 | 49 | meta | Y |
| AMAR. | Amaruśataka | (RU, corpus) | `amaru-shataka` | verse-aligned | 193 | 18 | meta | Y |
| BUDDH. | Buddhacarita | (RU, corpus) | `buddhacharita` | verse-aligned | 1033 | 0 | meta | asset-only |
| SUŚR. | Suśruta-saṃhitā | — (no full RU) | `—` | not ingested | — | 277 | — | N |

Beyond these, `corpus.db` carries verse-aligned RU for ~50 Upaniṣads and darśana texts
(Yoga-sūtra, Sāṅkhya-kārikā, Nyāya-bhāṣya, the principal Upaniṣads, …) — low individual
PWG citation counts but all locus-lookupable; the resolver covers the frequently-cited
subset first (§Locus mapping).

**Per-text notes.**

- **MBH.** — LOCUS GAP, and it stays one: PWG cites continuous Calcutta ślokas (MBH. 1,1090); corpus keys parvan.adhyaya.verse (critical). The cumulative-adhyāya candidate over the existing Nīlakaṇṭha-vulgate↔critical concordances was built and measured under H1652 (11.2% within ±2 verses against a 2.5% null; 1/43 on unambiguous anchors) and **rejected** — closing it needs the Calcutta text itself. See §Locus mapping.
- **ṚV.** — In-copyright (Elizarenkova); committed data is loci+counts only.
- **R.** — a three-edition composite (pwgbib 1.247): books 1–2 = Schlegel (~vulgate numbering; the human-validated R. 2,91,26 fixture lives here), **books 3–6 = Gorresio Bengal loci** — briefly `unmapped_locus_scheme` after the H1656 integrity find (~900 wrong-verse reuses closed), now resolved via the CONTENT-BASED Gorresio↔Southern concordance with the map class on every hit; book 7 = Bombay ed. (no RU translation exists → `locus-not-in-corpus`, see §Rāmāyaṇa kāṇḍas 4, 6, 7).
- **R. GORR.** — Gorresio Bengal ≠ Leonov Southern (~⅓ verse-for-verse). CONTENT-BASED verse concordance built under H1656 from the e-text recovered out of the Cologne scan PDFs' text layer, completed to all 7 kāṇḍas under H1689 (tesseract-5 `san` OCR of the image-only vols 2/4/uk); reuse ON (MG 26-07-2026), Bengal-only verses stay typed misses. See §R. GORR.
- **BHĀG. P.** — High-value: 2nd-most-cited purāṇa (2,035 refs); RU exists in the Ignatiev archive, absent from the corpus → top ingestion target.
- **KATHĀS.** — Verse-aligned in `corpus.db` (MG N9): digitized AND locus-lookupable. Caveat: PWG cites 2-number loci (KATHĀS. 17,32); the corpus keys 3-number `lambaka.taranga.verse` — the resolver maps this best-effort (§Locus mapping).
- **AV.** — All 19 kāṇḍas paired sa+ru.
- **ŚAT. BR. / HARIV. / SUŚR.** — heavily cited, no known full RU → clean miss (`text-not-covered`).
- **TS.** — Clean miss (MG N18); flag citations for TM-assisted fresh translation, not reuse.
- **MĀRK. P.** — the Devī-māhātmya (= Mārk. P. 81–93) is in the Ignatiev archive; the rest is not ingested → partial.
- **KĀM.** — PWG's `KĀM.` is Kāmandakīya Nītisāra (123 refs, a *different* text); Vātsyāyana Kāmasūtra is aligned but not PWG-cited under a matching abbr → asset held, low reuse value.
- **GĪT.** — PWG `GĪT.` (49 refs) = Gītagovinda (not the Bhagavadgītā, which is `BHAG.`).
- **BUDDH.** — RU-aligned asset held; not PWG-cited (Böhtlingk-Roth predates the convention) → asset-only.

## Ignatiev ingestion queue

The local-only `SamudraManthanam/archive_ignatiev_2026/Переводы с санскрита/` holds 23
RU translations from Sanskrit (62 files). MG's ruling (N9): the archive is **definitely
not fully ingested**. Ranked by PWG-citation value; ingestion itself is follow-on work —
queued here, not started.

| work | files | format | PWG relevance | est. effort |
|---|---:|---|---|---|
| Bhāgavata-purāṇa | 1 | doc | **BHĀG. P. — 2,035 refs (highest-value gap)** | high (12 skandhas) |
| Devī-māhātmya | 3 | doc/pdf | = Mārk. P. 81–93 (part of MĀRK. P. 355 refs) | low (13 chapters) |
| Mārkaṇḍeya-purāṇa (remainder) | — | — | MĀRK. P. 355 refs | medium |
| Kālikā-purāṇa | 8 | doc/docx/pdf | low PWG | medium |
| Liṅga-purāṇa | 2 | pdf | low | medium |
| Padma-purāṇa | 1 | doc | low | high |
| Mahābhārata (fragments) | 1 | docx | supplementary — corpus already has all 18 parvans | n/a |
| Devī-Bhāgavata-purāṇa | 22 | doc/docx/pdf | already ingested (`devibhagavata-purana`, 34,522 verses) | done |
| Adbhuta-Rāmāyaṇa | 1 | docx | not PWG-cited | low |
| tantras — Bṛhannīla, Guptasādhana, Yoginī, Yoni, Kulārṇava, Māyā, Nirvāṇa, Niruttara, Cīnācāra, Śāktisaṃgama | 1–2 each | doc/docx/pdf | negligible PWG | low, low-value |
| minor purāṇas — Devī, Mahābhāgavata, Nīlamata | 1–4 | doc/docx/pdf | low | low-value |
| Kāma-samūha, Kādambara-svīkaraṇa-kārikā, «Прочее» | 1–2 | doc/docx | none | skip |

**Ingestion priority:** Bhāgavata-purāṇa first (single largest PWG-cited gap), then the
Devī-māhātmya / Mārkaṇḍeya remainder. The tantras and minor purāṇas are low-value for
PWG citation reuse and can wait or be skipped.

## Translation-of-record policy

Per MG N6, the rule generalizes from the RV decision: a covered citation renders its RU
**translation of record**; where PWG's German rendering diverges, the divergence is
**marked separately** rather than silently overwriting. Concretely, a promoted card
schema gains three fields (schema, not prose):

- `citation_ru` — the RU translation-of-record segment for the cited locus (from the
  lookup; generation-time consult, not persisted as public text).
- `citation_ru_src` — the source id + tier (`aligned` / `queue`) + rights flag
  (`metadata-only`), so provenance travels with the segment.
- `divergence_note` — set when PWG's German diverges from the RU translation of record
  (e.g. Elizarenkova reads X where PWG's German implies Y); the note flags it, the RU ToR
  is not silently replaced.

Per-text translation-of-record assignment:

| text | translation of record | note |
|---|---|---|
| ṚV. | Elizarenkova, 1:1 (MG N6) | German divergence → `divergence_note`, never overwrite |
| R. | Leonov (Southern recension) | books 1–2 direct (Schlegel); books 3–6 via the Gorresio concordance (flagged hits); book 7 misses until a Russian uttarakāṇḍa exists — not until it is "ingested" (H1705) |
| MBH. | SamudraManthanam per-parvan alignment | **blocked on the Calcutta↔critical concordance** (§Locus mapping) |
| KATHĀS. | «Океан сказаний» | best-effort locus map (2-number PWG vs 3-number corpus) |
| AV. / Manu / RAGH. / KUMĀRAS. / MEGH. / GĪT. / AMAR. | corpus RU | clean locus map |
| BHAG. | **choose one** of 12 RU Gītās as canonical | recommend a public-domain edition where quality allows; `@DECIDE` if quality forces an in-copyright choice |
| TS.-class (no RU) | — | TM-assisted fresh translation, flagged as such — never reuse |

## Locus mapping — the hard part

Reuse needs the PWG citation locus to map to the corpus passage key. The schemes differ
per text; the resolver ([`citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py))
encodes the clean ones and reports a typed non-hit for the rest.

| text | PWG locus | corpus `canonical_id` passage | map |
|---|---|---|---|
| R. | `book,sarga,verse` (R. 2,91,26) | `0{book}_ramayana-{kāṇḍa}:{sarga}.{verse}` | clean (books 1–2, Schlegel); books 3–6 via the Gorresio↔Southern verse concordance (hit carries map class+score) |
| ṚV. | `mandala,sukta,verse` | `0{mandala}_rigveda:{sukta}.{verse}` | clean |
| AV. | `kanda,sukta,verse` | `0{kanda}_atharvaveda:{sukta}.{verse}` | clean |
| M. (Manu) | `adhyaya,verse` | `manavadharmashastra:{adhyaya}.{verse}` | clean |
| KATHĀS. | `taranga,verse` (2-number) | `lambaka.taranga.verse` (3-number) | best-effort |
| **MBH.** | **continuous Calcutta śloka** (5,7331) | `parvan.adhyaya.verse` (critical) | **UNMAPPED** — the cumulative-adhyāya candidate was built and measured 26-07-2026 (H1652) at 11–16% verse accuracy and REJECTED; needs the Calcutta text itself |
| **R. GORR.** (+ plain R. books 3–6) | Gorresio Bengal recension | Southern recension (Leonov) | **CONTENT-BASED verse concordance (H1656 + H1689)** — matched/fuzzy → hit; Bengal-only → `no-southern-counterpart`; kāṇḍas 4/6/7 → `ru-translation-unpublished` (`gorresio-etext-gap` extinct since the H1689 OCR pass) |
| **R. book 7** | Bombay ed. 1859 — 111 sargas + 13 interpolated (`23.1–23.5`, `37.1–37.5`, `59.1–59.3`) | corpus `07_ramayana-uttarakanda`, 100 sargas, **Sanskrit-only, critical text** | **NO MAP, and none is owed** — measured NOT ≈1:1 under H1705 (11/100 sargas share a verse count); 127 of 1,781 citations name a sarga the corpus cannot carry. Returns `ru-translation-unpublished`: no Russian uttarakāṇḍa exists |

The remaining UNMAPPED case returns `unmapped_locus_scheme` (a documented GAP, **not** a miss):

- **MBH. Calcutta↔critical — BUILT, MEASURED, REJECTED 26-07-2026 (H1652).** PWG
  (Böhtlingk-Roth) cites the Calcutta edition (1834–39), which numbers ślokas
  continuously within each parvan (MBH. 5,7331 = Udyogaparva śloka 7331); the corpus
  keys the critical (Poona) edition's `parvan.adhyaya.verse`. The prior artifact MG
  recalled (N1) **is real** — CommentaryStrategies carries a Nīlakaṇṭha-vulgate↔critical
  verse concordance for all eighteen parvans — so the candidate map was built: a
  cumulative adhyāya-length table turning a continuous śloka into a vulgate
  `adhyāya.verse`, then that concordance to the critical keying. **It does not
  reconstruct PWG's numbering.** Measured against the store: 11.2% of 1,327 locatable
  citations land within ±2 verses (uniform-random null 2.5%), 16.3% under a per-parvan
  linear rescale scored on a held-out half, and **1 of 43** on the anchors whose true
  verse is unambiguous. The vulgate witness is also shorter than the text PWG counts in
  8/18 parvans (Vanaparvan 11,859 against a citation reaching 17,471), so 145 citations
  have no ordinal at all. The lower links were verified independently (vulgate 6.26.47 →
  critical 6.24.47 → the corpus line that is Bhagavadgītā 2.47), so the failure is the
  continuous→vulgate step alone. Full tables:
  [H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1652_MBH_CALCUTTA_VALIDATION_2026-07-26.md);
  reproduce with
  [`src/build_mbh_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_mbh_concordance.py).
  The rejected cumulative table is committed anyway as
  [`src/mbh_vulgate_cumulative.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mbh_vulgate_cumulative.tsv)
  — a head start for a successor, **never a lookup path** (the selftest fails if code
  keys a citation through it). **The `@DECIDE` is closed:** MG ruled (а) build it, it was
  built, and the measurement says the input is wrong rather than the method. Closing the
  GAP needs the **Calcutta text itself** (or a published Calcutta↔critical concordance)
  plus a content-based alignment of the H1656 kind, so the useful next act is an
  acquisition probe for a Calcutta e-text or scan, not another modelling attempt.

## R. GORR. — the Gorresio concordance (MG N11 → ruled BUILD, H1656)

Gaspare Gorresio edited the **Gauḍīya (Bengal) recension** of the Rāmāyaṇa (1843–67);
Leonov (the R. translation of record) rendered the **Southern recension**. The two
recensions share only **~⅓ of the text verse-for-verse**, verse numbering differs
substantially, and **no published clean Gorresio↔Southern verse concordance exists**
(the Baroda Critical Edition gives an apparatus, not a concordance; IWLV-Rāmāyaṇa,
arXiv 2604.13078, aligns at *sarga* level only). MG ruled 21-07-2026 (weekly `@DECIDE`
sheet): **build it** — «NEVER propose to skip» citation reuse.

**Scope is bigger than R. GORR. (H1656 finding).** PWG's plain `R.` cites Gorresio for
**books 3–6** (pwgbib 1.247; only books 1–2 are Schlegel, book 7 Bombay). Verified
against the store's cited sarga ranges: R. 3 reaches sarga 79, R. 4 → 63, R. 5 → 94 —
exactly the Gorresio counts (79/63/95) and past the Southern ones (75/–/68). Before
H1656 the resolver keyed in-range book-3/5 loci into the Southern corpus and silently
returned the **wrong verse's RU** (~900 refs exposed); those books now return
`unmapped_locus_scheme` alongside R. GORR. Total Gorresio-keyed refs: **~2,200**
(657 R. GORR. + ~1,560 plain-R. books 3–6).

**What H1656 built** ([`src/build_ramayana_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py)).
The first pass assumed no Gorresio e-text exists; the same-day follow-on **overturned
that**: the Cologne page PDFs carry an embedded Google **text layer**, so a real e-text
was extracted and the concordance upgraded from structural draft to CONTENT-BASED
(items 3–5):

1. **Gorresio structural inventory**
   ([`src/ramayana_gorresio_inventory.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_inventory.tsv)) —
   all 672 sargas across kāṇḍas 1–7 with verse counts and edition volume/page ranges,
   recovered from the Cologne scan-viewer page index
   ([sanskrit-lexicon-scans/ramayanagorr `ksverse.js`](https://github.com/sanskrit-lexicon-scans/ramayanagorr/blob/main/ksverse.js),
   commit 609a2866) — the same index that already gives every R./R. GORR. citation a
   per-verse **scan-page link** via `ls_resolver.py`. Page-level click-through therefore
   already works for all ~2,200 refs; what is pending is *translation reuse*, not access.
2. **Southern↔Critical verse concordance**
   ([`src/ramayana_southern_critical_concordance.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_southern_critical_concordance.tsv)) —
   content-based (char-n-gram similarity + per-kāṇḍa monotonic anchoring) over the
   SamudraManthanam Southern corpus vs the DCS critical text (text_id 143): 18,993
   Southern verses → **81.4% matched/fuzzy** (15,459), 3,398 southern-only (CE-excised
   material; e.g. the R. 2,91 Bharadvāja-feast sarga is southern-only, as expected).
   Kāṇḍas 6–7 align near-identically — those corpus files are already CE-keyed.
3. **Gorresio e-text**
   ([`src/gorresio_etext.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gorresio_etext.jsonl)) —
   **19,852 verses in IAST — all 7 kāṇḍas, all 672 sargas** (H1689 closed the
   vols 2/4/uk gap 26-07-2026). Vols 1/3/5 (Bāla, Ayodhyā 1–9, Āraṇya,
   Kiṣkindhā-part, Yuddha): zero new OCR — the page PDFs' embedded Google text
   layer. Vols 2/4/uk (Ayodhyā 10–127, Kiṣkindhā-tail + Sundara, Uttara):
   image-only scans OCRed locally with tesseract 5.5 `san` on the full-res
   embedded page images (2,900×4,700 px class; 1,427 pages, 99–100% of pages
   yield verse markers). Both sources segmented by ॥N॥ markers anchored to the
   hand-made per-page verse ranges in `ksverse.js` (OCR drops digits — ॥91॥
   reads as ॥1॥ — so parsed numbers are trusted only inside the page's known
   range). Per-kāṇḍa verse recovery vs the structural inventory: 92/76/91/84/
   72/92/74% (k1–k7) — the OCR volumes recover less than the Google-layer ones,
   the residue stays typed misses, never invented loci.
4. **Gorresio↔Southern verse concordance, CONTENT-BASED**
   ([`src/ramayana_gorresio_southern_verse_map.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv)) —
   same n-gram + monotonic-anchoring machinery over the e-text: **2,377 matched +
   3,549 fuzzy = 5,926 verses mapped** to a Leonov-translatable Southern locus
   (was 4,066 before the H1689 vols-2/4/uk OCR pass — new coverage k2 sargas
   10–127: 581, Sundara: 345, Uttara: 760); 11,727 genuinely Bengal-only (honest
   misses); 270 `moved` excluded from reuse (the H783-identified error class);
   1,925 kiṣkindhā rows `no_southern_corpus`. Every scan-verified gold anchor
   reproduces: G 1,1,1→S 1,1 · G 1,10→S 11 · G 1,22,1→S 19,1 · G 1,29→S 26 ·
   G 3,36→S 32; the 4 audit-rejected pairs from the 26-07-2026 sheet are
   re-applied by the build itself (pair-keyed, so a rebuild can never silently
   resurrect a human-vetoed pair). H1689 spot-check: 12/12 sampled new-kāṇḍa
   pairs verified true correspondences.
5. **Sarga map regenerated CONTENT-BASED** (majority roll-up of the verse map;
   same file
   [`src/ramayana_gorresio_southern_sarga_map.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_sarga_map.tsv)).
   The first-pass content-blind DTW draft is superseded — scan-anchor checks showed
   it drifted ±1–3 sargas (e.g. it said G 1,22→S 21; the text says S 19).

**Census of the cited loci (26-07-2026, current store).** 375 distinct R. GORR. loci:
kāṇḍa 1 → 139, kāṇḍa 2 → 230, kāṇḍas 4/5/7 → 6 — i.e. **98% in books 1–2**, exactly
where plain `R.` means Schlegel and PWG had to name Gorresio explicitly; in books 3–6
plain `R.` already IS Gorresio (which is why the explicit form is rare there). All 375
loci fall inside the structural inventory's sarga/verse ranges (0 out-of-range — an
independent check of the ksverse-derived inventory). So the validation sample should
weight Bāla + Ayodhyā first.

**Cross-validation against H783.** The independently built Southern↔Critical map was
checked against the pre-existing H783 Sundara concordance
([CommentaryStrategies data/edition_comparison/concordance.json](https://github.com/gasyoun/CommentaryStrategies/blob/main/data/edition_comparison/concordance.json),
`compare_editions.py`, LCS-based): **98.7% agreement** (1,920/1,945 shared mapped
verses). Disagreements are almost entirely this build's `moved` class (formulaic
repeated verses matched off-backbone) — treat `moved` as lower-trust; H783's monotone
reading wins there. The two methods mutually validate; the H783 assets (Sundara +
gitasupersite kāṇḍas I–IV + yuddha alignment) remain the citation-grade source for the
kāṇḍas they cover, and this build extends coverage uniformly with scores.

**Reuse is ON (MG ruling 26-07-2026: «reuse always ON by default — the validation gate
can take months or years»).** `citation_tm.py` resolves R. GORR. and plain R. books 3–6
through the CONTENT-BASED verse concordance: `matched`/`fuzzy` rows return the Leonov
segment as a normal hit **with the map class + score attached** (`map` field travels
with every consult, so downstream can weight or display it); everything else is a
typed, honest state — `no-southern-counterpart` (Bengal-only verse, ~⅔ of the
recension) and `ru-translation-unpublished` (kāṇḍas 4, 6 and 7 — see the next section:
those are a **translation** gap, not an ingest queue; renamed from
`locus-not-in-corpus` 27-07-2026 under H1705, which found the shared string was being
read as an ingest/numbering gap); `gorresio-etext-gap` is **extinct since
26-07-2026** — the H1689 tesseract-5 `san` OCR pass put all 672 sargas in the e-text.
A miss never becomes an invented offset — the 166k lesson stands. The `/review-sheet` audit sheet
remains as a quality surface (votes refine the map), not a blocker.

**Audit round 1 (26-07-2026, voted same day).** 32 sampled pairs (incl. 5 scan-verified
gold anchors), agent-voted by Fable 5 (`claude-fable-5`) on MG's direct delegation:
**28 approve / 4 reject (87.5%)**. All 4 rejects are one systematic sub-class —
OCR lost a ॥N॥ marker, two half-verses merged, and the aligner paired the chunk with
the verse matching its TAIL (half-verse shift: G 1,12,28 · 1,48,11 · 1,62,8 · 2,4,7).
Those rows are switched off as `audit-rejected` in the verse map (loader reads only
matched/fuzzy). Detection heuristic for the residue: over-long G-chunks or chunks with
an interior ॥N॥ — queued into H1689's refinement pass. Vote record:
`review/sanskritlexicography-gorresio-southern-map_audit-26-07-26_decisions.json` (local).

## Rāmāyaṇa kāṇḍas 4, 6, 7 — a translation gap, not an ingest queue (H1652)

H1652 was written to "ingest kāṇḍas 4 and 6" on the premise that the alignments exist
and only corpus rows are missing. The census of `corpus.db`'s `sources` table overturns
the premise: **the Russian translations do not exist.** Registered Rāmāyaṇa sources are
Gryntser I (2006), II (2006), III (2014) and Leonov V (2022, podstrochnik) — Gryntser's
academic translation stopped after book 3, Leonov's covers Sundara. Nothing renders
kiṣkindhā, yuddha or uttara into Russian, so there is no translation of record to reuse
and no amount of ingest produces one.

What *does* exist is the Sanskrit and, for kāṇḍa 6, the alignment work:

| kāṇḍa | PWG refs (plain R. + R. GORR.) | Sanskrit available | Gorresio→Southern map | RU translation of record | what is actually missing |
|---|---:|---|---|---|---|
| 4 kiṣkindhā | 376 | yes — [CommentaryStrategies `data/valmiki_shlokas/kanda_4_kishkindakanda`](https://github.com/gasyoun/CommentaryStrategies/tree/main/data/valmiki_shlokas) (Gita Supersite, Southern) + a gitasupersite alignment (1,987↔2,235 vv) | no — all 1,004 rows are `no_southern_corpus` | **none** | the Russian, then a Southern corpus, then the map |
| 6 yuddha | 288 | yes — same source, 132 sargas | **yes — 1,172 matched + 1,123 fuzzy already in the verse map** | **none** | the Russian only |
| 7 uttara | 232 | yes — `07_ramayana-uttarakanda.jsonl`, 2,690 verses, **Sanskrit-only and CRITICAL-edition text** (H1705, see below) | inventory only | **none** | the Russian — and, before any map, a Bombay↔critical bridge the numbering does not give for free |

Kāṇḍa 6 is the sharp line: H1656's concordance already maps 2,295 Gorresio verses onto
Southern yuddha loci, so the day a Russian yuddhakāṇḍa is ingested, 288 PWG references
become reusable with no further alignment work. Kāṇḍa 4 needs the whole chain.

### Kāṇḍa 7 — what H1705 measured (27-07-2026)

H1705 was minted to bridge the Bombay numbering for book 7 on the reading that
"the corpus HAS `07_ramayana-uttarakanda.jsonl`, so the missing piece is the
numbering, not the RU side". Both halves of that reading are wrong, and the
measurements say so without ambiguity:

| question | measured | consequence |
|---|---|---|
| does the corpus file carry Russian? | **no — 2,690 `sa` segments, 0 `ru`** (kāṇḍa 6 likewise; kāṇḍas 1/2/3/5 are fully paired) | there is nothing to reuse even from a perfect map |
| is it the Southern text of record? | **no** — 2,688/2,690 rows of `ramayana_southern_critical_concordance.tsv` align to the DCS **critical** edition at the identical `sarga.verse`, 95.5% at score 1.0; kāṇḍas 1/2/3/5 sit at 1–3% identity | the "Southern" column is a mislabel for kāṇḍas 6–7 |
| is Bombay ≈1:1 with it? | **no** — Bombay 111 sargas + 13 interpolated vs 100; identical verse count in **11/100** sargas; delta −14…+18, mean +4.7 | a direct-with-offset scheme would be dishonest |
| how much PWG mass is at stake? | **1,781** plain `R.` book-7 citations in the full digitisation (4.5% of 39,845), sargas 1–111; **127** cite a sarga >100 | those 127 cannot resolve against a 100-sarga text at all |

So the blocker order for book 7 is **the Russian first**, and it is not near: the
[RussianRamayana](https://github.com/gasyoun/RussianRamayana) pipeline lists book IV
blocked, V in progress, VI draft-ready (~2029) — book VII is not in it. The OCR pass
that H1705 was authorised to run was **deliberately not spent**: its only product
would be a Bombay↔critical Sanskrit map with no RU consumer. The scan-side
groundwork that makes that pass cheap when it is finally worth running is committed
as [`src/ramayana_bombay_inventory.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_bombay_inventory.tsv)
(658 sargas, all 7 kāṇḍas, no OCR) and the traps are in
[FINDINGS §476](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

> Counting scope: the 232/288/376 figures in the table above are **store** counts
> (the pwg_ru working set); the 1,781 is every `<ls>` in the full csl-orig `pwg.txt`.
> Different denominators, both correct — do not compare them directly.

**Resolver consequence, applied 26-07-2026.** `_RAMA_GORR_WORK` in
[`citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py)
previously named `06_ramayana-yuddhakanda` and `07_ramayana-uttarakanda` — works
`corpus.db` does not carry. That did not fail loudly; it populated `canonical_id` with a
fabricated key for a passage nobody can fetch, so a consumer reading that field saw a
resolution where there was none. Those kāṇḍas now fall through to the covered-but-absent
branch: a typed miss with **no** `canonical_id`, pinned by three new selftest checks.
This is the same defect class H1656 removed from plain `R.` books 3–6, caught one layer
further in. **H1705 (27-07-2026) retyped that miss** from `locus-not-in-corpus` to
`ru-translation-unpublished`, carrying a `blocker` field naming the kāṇḍa: the old
string was shared with genuine corpus-coverage holes, and reading book 7's miss as an
ingest/numbering gap is what got a Bombay-concordance handoff minted for a book whose
real blocker is that nobody has translated it. Plain `R.` book 7 now lands on the same
typed miss as `R. GORR.` book 7 (two more selftest checks, one of them an
out-of-corpus-range sarga).

## Retro-application plan

The lookup is wired into the generation path (`corpus_gate.build_card` gains a
`citation_reuse` field consulting `citation_tm.consult_card` over a card's `<ls>`
citations — additive, import-guarded). Cards promoted **before** this wiring must be
audited and requeued where a covered citation was retranslated instead of reused:

1. **Scope the affected set.** Over the promoted store (`pwg_ru_translated.jsonl`,
   local-only), count cards whose `<ls>` citations resolve to a covered text (via
   `citation_tm.consult_card` — a `hit` means a reuse was available). That count is the
   retro-application backlog.
2. **Batch + requeue** per the pipeline's existing requeue mechanics
   ([PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)):
   process covered-citation cards in batches, re-running the verdict step with the
   `citation_reuse` consult active, so the RU translation of record is surfaced to the
   model.
3. **Downstream consumers.** The N17-class citation checks in
   [H1302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1302-Opus_RussianTranslation_pwg-ru-german-residue-sweep-reject-repair_19.07.26.md)
   and [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md)
   consume this: a card whose citation should reuse an RU ToR but doesn't is a repair
   target for those sweeps.

Volume is bounded by citation coverage: of 36,546 distinct `<ls>` refs, the reusable
share is those whose text is covered AND locus-mappable (the verse-aligned rows above,
minus the MBH/R. GORR. GAPs) — the exact figure comes from step 1 against the local store.

## Prior art (consumed, not rebuilt)

- 1.09M-pair verse-aligned corpus:
  [`src/build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)
  + [`aligned_works.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/aligned_works.txt).
- `<ls>` citation extraction + Cologne resolution:
  [`src/build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
  + [`src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
  + [`src/pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py).
- Corpus query (read-only reuse of SamudraManthanam `corpus.db`):
  [`src/corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py).
- Reuse-asset map + rights classes:
  [`REUSE_MAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md)
  + [`SAMUDRA_INTEGRATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/SAMUDRA_INTEGRATION.md).

**Sources (R. GORR. concordance research):** the Vālmīki Rāmāyaṇa Critical Edition (Baroda
Oriental Institute, 1960–75); [Clay Sanskrit Library, Rāmāyaṇa Book I ancillary
introduction](https://claysanskritlibrary.org/ramayana-book-i-boyhood-ancilliaries-introduction-page-3/);
[IWLV-Rāmāyaṇa sarga-aligned parallel corpus (arXiv 2604.13078)](https://arxiv.org/pdf/2604.13078).

_Provenance: census + policy + lookup built for H1304 by Opus 4.8 (`claude-opus-4-8`),
executed under an MG-authorized model-tier override (the handoff filename locks Fable 5;
the session was `/model`-switched to Opus mid-task and MG authorized running it on Opus)._

_Dr. Mārcis Gasūns_
