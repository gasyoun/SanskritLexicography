# Covered texts — Russian translations of record for PWG citations

_Created: 19-07-2026 · Last updated: 26-07-2026_

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
(ŚAT. BR. 1,620 refs, HARIV. 867, SUŚR. 277) and two **concordance gaps** where an RU
translation exists but its verse scheme does not map to PWG's citation scheme (MBH.
continuous-Calcutta, R. GORR. Bengal recension). The Gorresio gap is **larger than the
657 explicit R. GORR. refs**: PWG's plain `R.` is itself a three-edition composite
(pwgbib 1.247 — books 1–2 Schlegel, **books 3–6 Gorresio**, book 7 Bombay), verified
against the store's cited sarga ranges (H1656), so ~1,560 plain-`R.` book-3–6 refs are
Bengal-keyed too — see §R. GORR.

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
| R. | Rāmāyaṇa (composite: Schlegel 1–2 / Gorresio 3–6 / Bombay 7) | Leonov / Gryntser | `01–06_ramayana-*kāṇḍa` | verse-aligned | (4 kāṇḍas in corpus) | 2970 | meta | Y for books 1–2 only; books 3–6 are Gorresio-keyed → §R. GORR. |
| R. GORR. | Rāmāyaṇa (Gauḍīya/Bengal, ed. Gorresio) | — (Leonov is Southern; concordance DRAFT built, H1656) | `—` | GAP → DRAFT | — | 657 | — | N until draft validates (§R. GORR.) |
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

- **MBH.** — LOCUS GAP: PWG cites continuous Calcutta ślokas (MBH. 1,1090); corpus keys parvan.adhyaya.verse (critical). Needs a Calcutta↔critical concordance — see §Locus mapping.
- **ṚV.** — In-copyright (Elizarenkova); committed data is loci+counts only.
- **R.** — a three-edition composite (pwgbib 1.247): books 1–2 = Schlegel (~vulgate numbering; the human-validated R. 2,91,26 fixture lives here), **books 3–6 = Gorresio Bengal loci** → `unmapped_locus_scheme` since H1656 (an in-range book-3/5 locus keyed into the Southern corpus returned the WRONG verse's RU silently — ~900 refs were exposed), book 7 = Bombay ed. (not ingested → `locus-not-in-corpus`).
- **R. GORR.** — Gorresio Bengal ≠ Leonov Southern (only ~⅓ verse-for-verse; no published concordance). DRAFT structural concordance built under H1656 — stays UNMAPPED until it validates. See §R. GORR.
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
| R. | Leonov (Southern recension) | books 1–2 (Schlegel) only; books 3–6 are Gorresio-keyed → unmapped until the concordance validates; book 7 misses until ingested |
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
| R. | `book,sarga,verse` (R. 2,91,26) | `0{book}_ramayana-{kāṇḍa}:{sarga}.{verse}` | clean (books 1–2, Schlegel); **books 3–6 UNMAPPED — Gorresio-keyed (H1656)** |
| ṚV. | `mandala,sukta,verse` | `0{mandala}_rigveda:{sukta}.{verse}` | clean |
| AV. | `kanda,sukta,verse` | `0{kanda}_atharvaveda:{sukta}.{verse}` | clean |
| M. (Manu) | `adhyaya,verse` | `manavadharmashastra:{adhyaya}.{verse}` | clean |
| KATHĀS. | `taranga,verse` (2-number) | `lambaka.taranga.verse` (3-number) | best-effort |
| **MBH.** | **continuous Calcutta śloka** (5,7331) | `parvan.adhyaya.verse` (critical) | **UNMAPPED — needs a concordance** |
| **R. GORR.** (+ plain R. books 3–6) | Gorresio Bengal recension | Southern recension (Leonov) | **UNMAPPED — different recension; DRAFT concordance built (H1656), pending validation** |

The two UNMAPPED cases return `unmapped_locus_scheme` (a documented GAP, **not** a miss):

- **MBH. Calcutta↔critical.** PWG (Böhtlingk-Roth) cites the Calcutta edition (1834–39),
  which numbers ślokas continuously within each parvan (MBH. 5,7331 = Udyogaparva śloka
  7331). The corpus keys the critical (Poona) edition's `parvan.adhyaya.verse`. There is
  no 1:1 map without a Calcutta↔critical verse concordance. MG noted (N1) a prior
  "Nīlakaṇṭha vs Critical Mahabharata" comparison — that comparison artifact, if it
  carries a verse concordance, is the input to close this GAP. **`@DECIDE`: build the
  Calcutta↔critical MBH concordance, or leave MBH citations un-reused.**

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

**What H1656 built** ([`src/build_ramayana_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py);
no Gorresio e-text exists — scans + rough OCR only — so no OCR was chased, per MG):

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
   Southern verses → 74% matched/fuzzy, 4,820 southern-only (CE-excised material;
   e.g. the R. 2,91 Bharadvāja-feast sarga is southern-only, as expected). Kāṇḍas 6–7
   align near-identically — those corpus files are already CE-keyed.
3. **Gorresio↔Southern sarga map, DRAFT-STRUCTURAL**
   ([`src/ramayana_gorresio_southern_sarga_map.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_sarga_map.tsv)) —
   DTW over verse-count profiles only (content-blind): 319 sarga pairs plausible,
   212 weak, 165 unpaired. MG's N11 fixture R. GORR. 2,16 (47 verses) → Southern 2,19
   (40), the known Bengal↔vulgate Ayodhyā offset.

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

**Validation gate — R. GORR. (and R. books 3–6) stay `unmapped_locus_scheme` until it
passes.** The sarga map is structural evidence only; before any citation reuse flips on,
a **content-level check** must confirm it: sample ≥30 `plausible` sarga pairs spread
over kāṇḍas 1–3/5, read the Gorresio scan page for the mapped verse (links above) against
the Southern verse, and require ≥90% agreement; a human review sheet gates the flip
(`/review-sheet`, per the standing no-silent-flip rule). Verse-level mapping inside a
validated sarga pair additionally needs position interpolation checked on the same
sample. Until then the draft is a navigation aid and a research artifact, not a
translation-reuse key.

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
