_Created: 23-08-2026 · Last updated: 05-09-2026_

# C2 phase 1 — per-sense attestation window (PWG × ls_source_map)

_Created: 23-08-2026 · Handoff [H3168](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3168-OxAlpha_SanskritLexicography_ceiling-c2p1-sense-attestation-window_19.08.26.md) · Roadmap item [C2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)_

_Dr. Mārcis Gasūns_

**What this is:** for every explicitly numbered PWG top-level sense in the
current canon, its `<ls>` citations are resolved to works via
[ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)
(45 dated works) and joined into a per-sense **attestation window**
(`earliest` / `latest` / `n_dated_works` / `n_undated_citations`), layered on the
committed Renou proxy [pwg_sense_stratum.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_stratum.jsonl)
(`renou_oldest`/`renou_youngest` joined from it where an entry's sense count
still pairs; the stratum itself is consumed, never re-derived or rewritten).

**Honesty contract:** every window is *«per Böhtlingk–Roth's citations»* — a fact about what
Böhtlingk–Roth chose to cite, i.e. about the **dictionary**, not about the
language. No field here is, or may be read as, a claim about when a sense
*emerged*. Unresolvable sigla are carried, not dropped: they are ceiling item
C7's standing residue, censused below.

**Phase fence:** the curated per-work dating table (scholarly source per date,
contested datings as @DECIDE) is Wave 2 and is deliberately NOT built here.

<!-- c2p1:generated:start -->

## Coverage table

| Bucket | Definition | Senses | Share |
| --- | --- | --- | --- |
| Windowed | >= 1 cited work carries a map date | 43990 (83.0%) |
| Undated-only | >= 1 resolvable citation, none dated | 0 (0.0%) |
| Unresolvable | citations present, none resolve to the map | 6785 (12.8%) |
| Citation-less | no `<ls>` element in the sense segment | 2228 (4.2%) |
| **Total** | all numbered senses (current canon) | **53003** | 100% |

## Segmentation note (stratum pairing)

- Committed Renou proxy `pwg_sense_stratum.jsonl`: 17763 headwords, 40452 senses.
- This build: 19454 headwords with >= 1 top-level numbered sense, 53003 senses. Sense counts pair with the stratum for the renou join in 29267 senses; the rest carry null `renou_*` (counted, not dropped).
- Known upstream drift (found here): csl-orig reflowed top-level sense markers from «`<div n="1">N)`» to «`<div n="1">N〉`», so the committed `sense_stratum.SENSE_RE` matches 0 senses against the live canon (`sense_stratum.py --head a` → `[]`). This builder segments the current text with a bracket-tolerant pattern; the committed stratum file itself is untouched.

## C7 residue census (unmapped `<ls>` sigla)

115354 citation instances across the whole corpus carry a siglum absent from ls_source_map.json (2607 distinct sigla). This is the standing C7 census; nothing was dropped.

**Bounded fallback (documented, deterministic):** 8258 further instances normalise to compound sigla whose final token is a pure roman-numeral volume marker («HIT. I», «PAÑCAT. II», «Spr. (II)»); these are retried ONCE with that token dropped and join the plain siglum already in the map. No other inference is made — section sigla («MED. gh.»), journals («Ind. St.») and catalogue refs («Verz. d. Oxf. H.») stay unresolved below.

Windows are therefore **conservative lower bounds**: a sense whose only citations fall in the residue may still name dated works in the printed entry.

| Siglum | Instances |
| --- | --- |
| `Verz. d. Oxf. H` | 7773 |
| `Ind. St` | 3395 |
| `SARVADARŚANAS` | 2155 |
| `N` | 2107 |
| `KAUŚ` | 2098 |
| `PRAB` | 1938 |
| `TBR` | 1905 |
| `BHAṬṬ` | 1827 |
| `Verz. d. B. H` | 1798 |
| `KĀM. NĪTIS` | 1666 |
| `PAÑCAR` | 1604 |
| `ŚĀṄKH. ŚR` | 1560 |
| `ed. Bomb` | 1501 |
| `ŚABDAR` | 1495 |
| `LĀṬY` | 1487 |
| `MṚCCH` | 1387 |
| `ĀŚV. ŚR` | 1291 |
| `CHĀND. UP` | 1258 |
| `DAŚAK` | 1212 |
| `VIKR` | 1202 |
| `ṚV. PRĀT` | 1168 |
| `ĀŚV. GṚHY` | 1121 |
| `SŪRYAS` | 1096 |
| `PAÑCAV. BR` | 1088 |
| `VID` | 1066 |
| … 2582 further sigla | 69156 |

## Deterministic hand-check sample (25)

Every 1759-th windowed sense in file order, with the verbatim `<ls>` elements from the digitized printed entry (csl-orig `v02/pwg/pwg.txt`, exact source segment for that row) and the works the join emitted.

- **aBiDA / sense #0 (no 1)** — raw (1): `<ls>VS. 22,3</ls>` → dated: Vājasaneyi-Saṃhitā (window -900…-900)
- **ADmAna / sense #1 (no 2)** — raw (8): `<ls>SUŚR. 2,44,5</ls>; <ls n="SUŚR. 2,">194,5</ls>; <ls n="SUŚR. 2,">200,12</ls>; <ls n="SUŚR. 2,">202,5</ls>; <ls n="SUŚR.">1,257,14</ls>; <ls n="SUŚR. 1,">50,7</ls>; <ls n="SUŚR. 1,">198,4</ls>; <ls n="SUŚR. 1,">277,3</ls>` → dated: Suśruta-Saṃhitā (window 400…400)
- **upAKya / sense #1 (no 2)** — raw (1): `<ls>RĀJA-TAR. 4,677</ls>` → dated: Rājataraṅgiṇī (window 1150…1150)
- **kAYci / sense #0 (no 2)** — raw (2): `<ls>UṆĀDIK.</ls>; <ls>ŚKDR.</ls>` → dated: Śabdakalpadruma (= SKD) (window 1830…1830)
- **kzataGna / sense #1 (no 2)** — raw (3): `<ls>H. 686</ls>; <ls>ŚKDR.</ls>; <ls>WILS.</ls>` → dated: Hemacandra, Abhidhānacintāmaṇi, Śabdakalpadruma (= SKD) (window 1150…1830)
- **graB / sense #54 (no 4)** — raw (7): `<ls>GOBH. 2,2,16</ls>; <ls>CHĀND. UP. 4,2,4</ls>; <ls>LĀṬY. 7,8,1</ls>; <ls>ŚAT. BR. 3,5,3,17</ls>; <ls n="ŚAT. BR.">6,4,3,6</ls>; <ls>TS. 2,1,7,1</ls>; <ls n="TS.">5,1,2</ls>` → dated: Taittirīya-Saṃhitā, Śatapatha-Brāhmaṇa (window -1000…-800)
- **jaraRa / sense #2 (no 4)** — raw (5): `<ls>WILS.</ls>; <ls>VARĀH. BṚH. S. 5,81</ls>; <ls n="VARĀH. BṚH. S.">88</ls>; <ls n="VARĀH. BṚH. S.">91</ls>; <ls>ṚV. 10,40,3</ls>` → dated: Varāhamihira, Bṛhatsaṃhitā, Ṛgveda (window -1125…550)
- **tEjasa / sense #3 (no 4)** — raw (7): `<ls>AK. 2,9,9</ls>; <ls>TRIK. 3,3,444</ls>; <ls>H. 1039</ls>; <ls>ŚKDR.</ls>; <ls>SMṚTI.</ls>; <ls>MBH. 9,2723</ls>; <ls n="MBH.">3,7035</ls>` → dated: Amarakośa, Hemacandra, Abhidhānacintāmaṇi, Mahābhārata, Trikāṇḍaśeṣa, Śabdakalpadruma (= SKD) (window 80…1830)
- **draviRa / sense #1 (no 2)** — raw (7): `<ls>VP.</ls>; <ls>MBH. 1,2585</ls>; <ls>HARIV. 155</ls>; <ls>VP. 120</ls>; <ls>BHĀG. P. 4,22,54</ls>; <ls>BHĀG. P. 5,20,22</ls>; <ls>BHĀG. P. 5,20,15</ls>` → dated: Bhāgavata-Purāṇa, Harivaṃśa, Mahābhārata, Viṣṇu-Purāṇa (window 80…950)
- **nirjara / sense #2 (no 3)** — raw (6): `<ls>TRIK. 3,3,359</ls>; <ls>H. an.</ls>; <ls>MED.</ls>; <ls>H. an.</ls>; <ls>MED.</ls>; <ls>H. an.</ls>` → dated: Hemacandra, Anekārthasaṃgraha, Medinīkośa, Trikāṇḍaśeṣa (window 1150…1200)
- **parimlAyin / sense #1 (no 2)** — raw (2): `<ls>SUŚR. 2,317,18</ls>; <ls n="SUŚR. 2,">342,12</ls>` → dated: Suśruta-Saṃhitā (window 400…400)
- **prakzepa / sense #2 (no 3)** — raw (2): `<ls>VAIDYAKAPARIBH.</ls>; <ls>ŚKDR.</ls>` → dated: Śabdakalpadruma (= SKD) (window 1830…1830)
- **bahala / sense #0 (no 1)** — raw (19): `<ls>H. 1447</ls>; <ls>SUŚR. 1,45,4</ls>; <ls n="SUŚR. 1,">64,11</ls>; <ls n="SUŚR. 1,">343,5</ls>; <ls n="SUŚR.">2,310,15</ls>; <ls>RĀJA-TAR. 4,367</ls>; <ls>PRAB. 5,7</ls>; <ls n="PRAB.">55,5</ls> … +11 more` → dated: Hemacandra, Abhidhānacintāmaṇi, Kathāsaritsāgara, Rājataraṅgiṇī, Suśruta-Saṃhitā (window 400…1150)
- **maDumant / sense #0 (no 1)** — raw (39): `<ls>ṚV. 7,47,1</ls>; <ls n="ṚV. 7,47,">2</ls>; <ls n="ṚV. 7,">69,3</ls>; <ls n="ṚV.">1,13,2</ls>; <ls n="ṚV. 1,">142,2</ls>; <ls n="ṚV.">7,90,1</ls>; <ls n="ṚV.">8,9,4</ls>; <ls n="ṚV.">5,63,4</ls> … +31 more` → dated: Atharvaveda, Kumārasambhava, Kātyāyana-Śrautasūtra, Mahābhārata, Taittirīya-Saṃhitā, Vājasaneyi-Saṃhitā, Śatapatha-Brāhmaṇa, Ṛgveda (window -1125…420)
- **meDas / sense #0 (no 2)** — raw (5): `<ls>HARIV. 415</ls>; <ls>MATSYA-P. 9</ls>; <ls>ŚKDR.</ls>; <ls>VP. II, 100</ls>; <ls>WILSON</ls>` → dated: Harivaṃśa, Viṣṇu-Purāṇa, Śabdakalpadruma (= SKD) (window 200…1830)
- **Dvajin / sense #0 (no 3)** — raw (1): `<ls>BHĀG. P. 10,76,18</ls>` → dated: Bhāgavata-Purāṇa (window 950…950)
- **rAzwra / sense #0 (no 1)** — raw (90): `<ls>P. 2,4,31</ls>; <ls>TRIK. 3,5,13</ls>; <ls>MBH. 13,3050</ls>; <ls>AK. 3,4,25,184</ls>; <ls n="AK. 3,4,25,">186</ls>; <ls>H. 947</ls>; <ls n="H.">an. 2,449</ls>; <ls>MED. r. 79</ls> … +82 more` → dated: Aitareya-Brāhmaṇa, Amarakośa, Atharvaveda, Harivaṃśa, Hemacandra, Abhidhānacintāmaṇi, Indische Sprüche (gnomic anthology), Kathāsaritsāgara, Mahābhārata, Manusmṛti, Pāṇini, Aṣṭādhyāyī, Rāmāyaṇa, Rāmāyaṇa (Gorresio rec.), Taittirīya-Saṃhitā, Trikāṇḍaśeṣa, Varāhamihira, Bṛhatsaṃhitā, Vājasaneyi-Saṃhitā, Yājñavalkya-Smṛti, Śatapatha-Brāhmaṇa, Ṛgveda (window -1125…1150)
- **varUTa / sense #7 (no 8)** — raw (1): `<ls>TRIK. 3,3,201</ls>` → dated: Trikāṇḍaśeṣa (window 1150…1150)
- **vidura / sense #1 (no 2)** — raw (22): `<ls>H. an.</ls>; <ls>MED.</ls>; <ls>MBH. 1,95</ls>; <ls n="MBH. 1,">2213</ls>; <ls n="MBH. 1,">2245</ls>; <ls n="MBH. 1,">2426</ls>; <ls n="MBH. 1,">2442</ls>; <ls n="MBH. 1,">2721</ls> … +14 more` → dated: Bhāgavata-Purāṇa, Harivaṃśa, Hemacandra, Anekārthasaṃgraha, Indische Sprüche (gnomic anthology), Mahābhārata, Medinīkośa, Viṣṇu-Purāṇa (window 80…1200)
- **vEjayanta / sense #0 (no 1)** — raw (24): `<ls>H. 178</ls>; <ls>MED. t. 220</ls>; <ls>MBH. 2,872</ls>; <ls>NĪLAK.</ls>; <ls n="MBH.">3,1721</ls>; <ls>AK. 2,8,2,67</ls>; <ls>H. an. 4,126</ls>; <ls>R. 2,89,20</ls> … +16 more` → dated: Amarakośa, Harivaṃśa, Hemacandra, Abhidhānacintāmaṇi, Hemacandra, Anekārthasaṃgraha, Mahābhārata, Medinīkośa, Rāmāyaṇa (window 70…1200)
- **SuBaMyu / sense #1 (no 2)** — raw (5): `<ls>RAGH. 8,6</ls>; <ls>Verz. d. Oxf. H. 44,a,5</ls>; <ls>BHAṬṬ. 1,20</ls>; <ls>PĀRŚVANĀTHAK. 4,41</ls>; <ls>AUFRECHT</ls>` → dated: Raghuvaṃśa (window 420…420)
- **saMDay / sense #6 (no 6)** — raw (2): `<ls>MĀRK. P. 95,14</ls>; <ls>BHĀG. P. 5,1,22</ls>` → dated: Bhāgavata-Purāṇa, Mārkaṇḍeya-Purāṇa (window 550…950)
- **sidDi / sense #4 (no 5)** — raw (1): `<ls>YĀJÑ. 1,266</ls>` → dated: Yājñavalkya-Smṛti (window 300…300)
- **sTARqila / sense #1 (no 2)** — raw (1): `<ls>P. 4,3,76</ls>` → dated: Pāṇini, Aṣṭādhyāyī (window -400…-400)
- **ruc / sense #0 (no 4)** — raw (2): `<ls>Spr. (II) 6939</ls>; <ls>ṚV. 1,165,12</ls>` → dated: Indische Sprüche (gnomic anthology), Ṛgveda (window -1125…600)
<!-- c2p1:generated:end -->

_Dr. Mārcis Gasūns_
