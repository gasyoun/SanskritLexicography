# H4747 — Indische Sprüche × DCS locus attestation report

_Built: 2026-09-15 · OxAlpha (opencode/z-ai/glm-5.3-flash)_

## Method

- Per-saying records: `IndischeSprueche/data/indische_sprueche.jsonl` (7,537, 2nd ed.).
- Match unit: pada (split on `/` `|`) as a normalized continuous letter stream
  (spacing/punctuation/avagraha stripped, `ṁ`→`ṃ`) — Böhtlingk prints continuous
  sandhi, DCS `text_sandhied` keeps annotator token boundaries, so spacing-sensitive
  matching would miss nearly everything.
- Whole-verse exact class checked first (`exact_verse`), then per-pada (`pada`).
- Candidate recall: long-word (≥7) inverted index over DCS sentences
  (≤10 loci kept per pada), verified by substring containment.
- **Keying:** loci are keyed on the synthetic DCS `sentence.id` PK. `sent_id` is
  NOT unique within a chapter (FINDINGS §9 / DEAD_ENDS §6) and travels only as a
  `dcs_sent_id_label` column.

## Coverage

- sayings: 7537; with ≥1 DCS locus: 1573 (20.9%)
- exact whole-verse matches: 0
- TSV row statuses: pada=2374, unattested=15060

## Coverage by source work (Böhtlingk's attribution, first 40 chars)

| source work | attested | unattested |
|---|---:|---:|
| SPHUṬAŚLOKA. | 1 | 48 |
| ŚĀRṄGADHARA. | 0 | 39 |
| BHARTṚ. ed. BOHL. und lith./Ausg. III 1, | 10 | 6 |
| KALPATARU. | 0 | 16 |
| PRASAṄGAR. | 0 | 13 |
| SABHĀTARAṂGA. | 0 | 12 |
| VIŚVAGUṆĀDARŚA. | 1 | 6 |
| BHARTṚ. ed. BOHL. und lith./Ausg. I 2, 9 | 4 | 2 |
| KALIVIḌAMBANA. | 0 | 5 |
| RASIKAJĪVANA. | 0 | 4 |
| SUBHĀṢ. 291. | 0 | 3 |
| MOHAM. | 0 | 3 |
| BHARTṚ. ed. BOHL. und lith./Ausg. II 2,  | 3 | 0 |
| Ebend. | 0 | 3 |
| BHĀMINĪVILĀSA. | 0 | 3 |
| VYĀSA in ŚĀRṄG. PADDH./SAṂTOṢAPRAŚAṂSĀ 1 | 1 | 1 |
| BHARTṚ. ed. BOHL. HAEB. lith./Ausg. I un | 1 | 1 |
| VṚDDHA-CĀṆ. 15, 15. | 0 | 2 |
| SUBHĀṢ. 135. | 0 | 2 |
| PRASAṄGĀBH. 15, a. | 0 | 2 |
| dieser Gemahl der Erde/(König) aber hat  | 0 | 2 |
| SUBHĀṢ. 171. c. पत्र st./यत्र die Hdschr | 0 | 2 |
| BHARTṚ. ed. BOHL. und lith./Ausg. I 3, 7 | 1 | 1 |
| SUBHĀṢ. 89. | 0 | 2 |
| KĀM. NĪTIS. 3, 5. | 0 | 2 |

## 30-saying verification sample (seed=4747)

| num | source | loci (sentence_id · sent_id label · ref) | DCS text (norm, 70ch) | saying (70ch) |
|---|---|---|---|---|
| 1062 | DAṂPATĪŚ. 16 b र्मूल/unsere Verbesserung | 447626 · 79298 · ManuS, 4 | nāsyakaścidvasedgeheśaktitonarcitotithiḥ | āsanāśanaśayyābhiradbhirmūlaphalenavānāsyakaścidvasedgeheśaktitonarcit |
| 4217 | HIT. ed. SCHL. II, 25. JOHNS./24. SĀH. D | 171064 · 352385 · Hitop, 2 | duḥkhīyatisukhahetoḥkomūḍhaḥsevakādanyaḥ | praṇamatyunnatihetorjīvitahetorvimuñcatiprāṇānduḥkhīyatisukhahetoḥkomū |
| 6330 | BHARTṚ. ed. BOHL. und lith./Ausg. II 2,  | 702867 · 573449 · ŚTr, 1 | vyālaṃbālamṛṇālatantubhirasauroddhuṃsamujjṛmbhatechettuṃvajramaṇiṃśirī | vyālaṃbālamṛṇālatantubhirasauroddhuṃsamujjṛmbhatechettuṃvajramaṇiṃśirī |
| 2104 | /wie soll ein durch's Alter abgenutzter/ | 546189 · 121650 · Rām, Ay, 98 ; 546190 · 121651 · Rām, Ay, 98 | gātreṣuvalayaḥprāptāḥśvetāścaivaśiroruhāḥ | gātreṣuvalayaḥprāptāḥśvetāścaivaśiroruhāḥjarayāpuruṣojīrṇaḥkiṃhikṛtvāp |
| 1374 | MBH. 5, 1014. | 325777 · 218041 · MBh, 5, 33 | ekayādveviniścityatrīṃścaturbhirvaśekuru | ekayādveviniścityatrīṃścaturbhirvaśekurupañcajitvāviditvāṣaṭsaptahitvā |
| 2423 | MBH. 5, 1250, b. 1251, a./Vgl. den folge | 326207 · 218471 · MBh, 5, 35 | jīrṇamannaṃpraśaṃsantibhāryāṃcagatayauvanām | jīrṇamannaṃpraśaṃsantibhāryāṃcagatayauvanāmśūraṃvijitasaṅgrāmaṃgatapār |
| 1835 | MBH. 5, 2698. b. ॰कर्षण/ed. Calc. | 328900 · 221164 · MBh, 5, 71 | mahāguṇovadhorājannatunindākujīvikā | kulīnasyacayānindāvadhovāmitrakarśanamahāguṇovadhorājannatunindākujīvi |
| 1886 | M. 11, 230. | 451305 · 82978 · ManuS, 11 | naivaṃkuryāṃpunaritinivṛttyāpūyatetusaḥ | kṛtvāpāpaṃhisantapyatasmātpāpātpramucyatenaivaṃkuryāṃpunaritinivṛttyāp |
| 5845 | /ein majestätischer Elephant dagegen/sie | 171150 · 352471 · Hitop, 2 ; 702917 · 573499 · ŚTr, 1 ; 171150 · 352471 · Hitop, 2 | lāṅgūlacālanamadhaścaraṇāvapātaṃbhūmaunipatyavadanodaradarśanaṃca | lāṅgūlacālanamadhaścaraṇāvapātaṃbhūmaunipatyavadanodaradarśanaṃcaśvāpi |
| 2546 | ist sie den Augen/entschwunden, so ist s | 703161 · 573743 · ŚTr, 2 | tāvadevāmṛtamayīyāvallocanagocarā | tāvadevāmṛtamayīyāvallocanagocarācakṣuḥpathādapagatāviṣādapyatiricyate |
| 667 | /blosses Wissen ohne Handeln ist, wie de | 170161 · 351482 · Hitop, 1 ; 170162 · 351483 · Hitop, 1 | avaśendriyacittānāṃhastisnānamivakriyā | avaśendriyacittānāṃhastisnānamivakriyādurbhagābharaṇaprāyojñānaṃbhāraḥ |
| 571 | KĀVYĀD. 2, 197. | 220106 · 355292 · KāvĀ, Dvitīyaḥ paricchedaḥ | dṛṣṭirodhakaraṃyūnāṃyauvanaprabhavaṃtamaḥ | aratnālokasaṃhāryamavāryaṃsūryaraśmibhiḥdṛṣṭirodhakaraṃyūnāṃyauvanapra |
| 2950 | MBH. 3, 13853, b. 13854, a./12, 12529. a | 312263 · 204150 · MBh, 3, 200 | daśamāsadhṛtāgarbhejāyantekulapāṃsanāḥ | devāniṣṭvātapastaptvākṛpaṇaiḥputragṛdhyibhiḥdaśamāsadhṛtāgarbhejāyante |
| 254 | MBH. 5, 1155. | 326019 · 218283 · MBh, 5, 34 | anarthamarthataḥpaśyannarthaṃcaivāpyanarthataḥ | anarthamarthataḥpaśyannarthaṃcaivāpyanarthataḥindriyairajitairbālaḥsud |
| 4226 | ŚIŚ. 9, 6. SĀH. D. 263./ŚUK. Pet. Hdschr | 721011 · 568085 · Śusa, 23 ; 721011 · 568085 · Śusa, 23 ; 721012 · 568086 · Śusa, 23 | pratikūlatāmupagatehividhauviphalatvametibahusādhanatā | pratikūlatāmupagatehividhauviphalatvametibahusādhanatāavalambanāyadina |
| 6242 | YĀJÑ. 3, 219. DAṂPATĪŚ. 25./KULL. zu M.  | 133881 · 546752 · GarPur, 1, 105 | vihitasyānanuṣṭhānānninditasyacasevanāt | vihitasyānanuṣṭhānānninditasyacasevanātanigragāccendriccendriyāṇāṃnara |
| 1484 | wer/durch den Herrschaftsrausch berausch | 326003 · 218267 · MBh, 5, 34 ; 326004 · 218268 · MBh, 5, 34 | aiśvaryamadapāpiṣṭhāmadāḥpānamadādayaḥ | aiśvaryamadapāpiṣṭhāmadāḥpānamadādayaḥaiśvaryamadamattohināpatitvāvibu |
| 1592 | 1592. (619.) Mancher garstige Mensch/gew | 171773 · 353094 · Hitop, 2 | pramadālocananyastaṃmalīmasamivāñjanam | kaścidāśrayasaundaryāddhatteśobhāmasajjanaḥpramadālocananyastaṃmalīmas |
| 1511 | HIT. ed. SCHL. II, 27. ed./JOHNS. 26. a. | 171067 · 352388 · Hitop, 2 ; 171068 · 352389 · Hitop, 2 | kathaṃnāmanasevyanteyatnataḥparameśvarāḥ | kathaṃnāmanasevyanteyatnataḥparameśvarāḥacireṇaivayetuṣṭāḥpūrayantiman |
| 2060 | BHARTṚ. ed. BOHL. 2, 87. lith/Ausg. I 89 | 170293 · 351614 · Hitop, 1 ; 703038 · 573620 · ŚTr, 1 | matimatāṃcavilokyadaridratāṃvidhirahobalavānitimematiḥ | gajabhujaṅgamayorapibandhanaṃśaśidivākarayorgrahapīḍanammatimatāṃcavil |
| 4779 | HIT. ed. SCHL. I, 41. JOHNS./48. KAVITĀM | 170277 · 351598 · Hitop, 1 | vinaśvarevihāyāsthāṃyaśaḥpālayamitrame | māṃsamūtrapurīṣāsthinirminesaminkalevarevinaśvarevihāyāsthāṃyaśaḥpālay |
| 4633 | ihr Leben vergänglich/wie das Wasser, da | 703353 · 573935 · ŚTr, 3 | bhogāmeghavitānamadhyavilasatsaudāminīcañcalāāyurvāyuvighaṭṭitābjapaṭa | bhogāmeghavitānamadhyavilasatsaudāminīcañcalāāyurvāyuvighaṭṭitābhrapaṭ |
| 4223 | ŚĀRṄG. PADDH. RĀJANĪTI 34/(31). d. परं s | 423663 · 316294 · MBh, 13, 136 | praṇītaścāpraṇītaścayathāgnirdaivataṃmahat | praṇītaścāpraṇītaścayathāgnirdaivataṃmahatevaṃvidvānavidvāṃścavrāhmaṇo |
| 463 | PAÑCAT. ed. KOSEG. I, 186. ed./orn. 136. | 447205 · 78877 · ManuS, 3 | apraṇodyotithiḥsāyaṃsūryoḍhogṛhamedhinā | apraṇodyotithiḥsāyaṃsūryoḍhogṛhamedhināpūjayātasyadevatvaṃprayāntigṛha |
| 4698 | HIT. ed. SCHL. und JOHNS. II,/37. d. स क | 171140 · 352461 · Hitop, 2 | manuṣyajātautulyāyāṃbhṛtyatvamatigarhitam | manuṣyajātautulyāyāṃbhṛtyatvamatigarhitamprathamoyonatatrāpisopijīvats |
| 3501 | M. 4, 129. ŚĀRṄG. PADDH./SADĀCĀRA 17. c. | 447825 · 79497 · ManuS, 4 | nasnānamācaredbhuktvānāturonamahāniśi | nasnānamācaredbhuktvānāturonamahāniśinavastraiḥsahanājasraṃnāvijñāteja |
| 4990 | MBH. 5, 1091. | 325895 · 218159 · MBh, 5, 33 ; 325895 · 218159 · MBh, 5, 33 ; 325896 · 218160 · MBh, 5, 33 | yaātmanāpatrapatebhṛśaṃnaraḥsasarvalokasyagururbhavatyuta | yaātmanāpatrapatebhṛśaṃnaraḥsasarvalokasyagururbhavatyutaanantatejāḥsu |
| 2972 | wenn sie sich aber/gegenseitig bekämpfen | 336345 · 228609 · MBh, 5, 192 | daivaṃhimānuṣopetaṃbhṛśaṃsidhyatipārthiva | daivaṃhimānuṣopetaṃbhṛśaṃsidhyatipārthivaparasparavirodhāddhisiddhiras |
| 5663 | MBH. 5, 1349. R. ed. GORR. 5,/88, 17. HI | 295654 · 187538 · MBh, 2, 57 ; 326407 · 218671 · MBh, 5, 37 | apriyāṇyāhapathyānitenarājāsahāyavān | yohidharmaṃsamāśrityahitvābhrtuḥpriyāpriyeapriyāṇyāhapathyānitenarājās |
| 618 | MBH. 12, 216, b. 217, a. R./ed. GORR. 6, | 383748 · 276183 · MBh, 12, 8 ; 383749 · 276184 · MBh, 12, 8 ; 566005 · 141468 · Rām, Yu, 70 | arthebhyohivivṛddhebhyaḥsaṃbhṛtebhyastatastataḥ | arthebhyohivivṛddhebhyaḥsaṃbhṛtebhyastatastataḥkriyāḥsarvāḥpravartante |

## Known limits / honest residual

- Unattested ≠ absent from the Indian tradition: DCS is a fixed corpus
  (the Bhagavadgītā is ABSENT from DCS; Nala is present), and Böhtlingk cites
  anthologies (SUBHĀṢ., etc.) that DCS does not carry.
- Sandhi-resolution variants (e.g. `jaganu...` vs `jagantu...`) and orthographic
  variants between Böhtlingk's IAST and DCS annotators reduce recall; no fuzzy
  matching was applied (honest exact/substring residual, by design).
- JSONL is the unproofed Excel-derived mirror (76 short of boesp2's 7,613);
  citation-facing work routes to boesp1/boesp2, per IndischeSprueche/README.md.
- The existing `Spr. N` `<ls>` citation crosswalk (PWG#87) is a DIFFERENT layer
  (dictionary-side citation hrefs); this TSV is the corpus-locus attestation layer.
