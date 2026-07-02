# Renou register catalog — the full subsection lattice

_Created: 26-06-2026 · Last updated: 02-07-2026_

Renou's *Histoire de la langue sanskrite* (1956) is usually reduced to its **five
chapters** = the five **states** (I Vedic · II Pāṇinian · III Epic · IV Classical ·
V Buddhist/Jaina). But each chapter is divided into **subsections that are registers,
not periods** — e.g. the *bhāṣya* (commentary) has its own grammar section (p. 139) and
*épigraphique* is a documentary witness (p. 94), but the same is true of every one of the
twenty: drama, narrative, the Purāṇa, the grammarians' norm — each is a register in its own
right, treated here on equal footing. This is the canonical
list of the **20 registers** (`renou_register.REGISTERS`), the orthogonal axis built in
[`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md) / designed in
[`RENOU_SUBSECTIONS_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_SUBSECTIONS_PLAN.md);
the source structure is transcribed in
[VisualDCS/docs/Renou_1956_structure.md](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md).

**Read this right:** the **State** column is the Renou *chapter* where the register is
*discussed* — it is **not** a parent. A register cross-cuts states (a *bhāṣya* can comment
on a Vedic base; an inscription can be classical in date). Detector legend: **G** = DCS
corpus genre · **N** = DCS text-name stem · **L** = `<ls>` source siglum/genre · **D** =
dedicated citation-text detector. "Headwords" = distinct IAST headwords carrying the
register across all 8 dictionaries (PWG · MW · PW · AP · AP90 · BEN · SCH · BHS).

---

## State I — Période védique (chap. I, p. 5)

| Code | Renou subsection (page) | Covers | Detector | Headwords |
|---|---|---|---|--:|
| `rgveda` | La langue védique du Ṛgveda (p. 10) | the oldest mantra layer (Ṛksaṃhitā) | G·N·L | 15,370 |
| `atharva` | L'Atharvaveda · autres *mantra*'s · *gāthā* (p. 32–38) | Atharvan & non-Ṛgvedic mantra verse | N·L | 8,512 |
| `yajus` | Les *yajus* (p. 39) | Yajurvedic mantra-prose (Taittirīya / Vājasaneyi / Maitrāyaṇī / Kāṭhaka) | N·L | 11,015 |
| `brahmana` | La prose *brāhmaṇa* (p. 41–43) | the Brāhmaṇa expository prose | G·N·L | 16,562 |
| `upanisad` | La langue des Upaniṣad (p. 50) | Upaniṣadic prose & verse | G·N·L | 4,831 |
| `sutra` | La langue des Sūtra (p. 53) | Vedic / ritual sūtra (Śrauta-, Gṛhya-, Dharma-) | G·N·L | 18,893 |

## State II — Pāṇini et le problème de la langue parlée (chap. II, p. 62)

| Code | Renou subsection (page) | Covers | Detector | Headwords |
|---|---|---|---|--:|
| `vyakarana` | L'enseignement de Pāṇini → l'autorité des *śiṣṭa* (p. 62–80) | the grammarians' normative metalanguage (Pāṇini, Kātyāyana, Patañjali, later grammar) | G·N·L | 22,429 |
| `epig` | Le sanskrit épigraphique (p. 94) | inscriptional Sanskrit — a witness to real usage vs the grammarians' ideal | D (`Insch?r` marker) | 709 |

## State III — La langue épique et ses prolongements (chap. III, p. 101)

| Code | Renou subsection (page) | Covers | Detector | Headwords |
|---|---|---|---|--:|
| `epic` | Caractères généraux · Grammaire de l'Épopée (p. 101–110) | the epics proper — Mahābhārata, Rāmāyaṇa | G·N·L | 48,713 |
| `purana` | Les Purāṇa · Le Bhāgavata (p. 115, 120) | Purāṇic literature (incl. the Bhāgavata) | G·N·L | 31,255 |
| `tantra` | Les Tantra (p. 122) | Tantra / Āgama | G | 5,416 |
| `smrti` | La Smṛti (p. 124) | dharmaśāstra / smṛti (Manu, Yājñavalkya) | G·N·L | 17,546 |
| `karika` | Autres textes versifiés, style « *kārikā* » (p. 125) | versified śāstra in the kārikā manner | N·D | 3,021 |

## State IV — Le sanskrit classique : le bhāṣya, la kathā, le kāvya (chap. IV, p. 133)

| Code | Renou subsection (page) | Covers | Detector | Headwords |
|---|---|---|---|--:|
| `bhasya` | Le commentaire (*bhāṣya*) · Caractères linguistiques du bhāṣya (p. 133, 139) | commentary language — terse, formulaic, meta-textual; its own grammar | N·L (name-stems `*bhāṣya/ṭīkā/vṛtti/vārttika`) | 14,498 |
| `katha` | Le sanskrit narratif (*kathā*) (p. 146) | narrative prose (Pañcatantra, Kathāsaritsāgara, Daśakumāra) | G·N·L | 24,393 |
| `natya` | Le dialogue du théâtre (p. 150) | dramatic dialogue (Śākuntala, Mṛcchakaṭikā, …) | G·N·L | 12,611 |
| `kavya` | La poésie savante (*kāvya*) (p. 158–185) | high poetry (Kālidāsa, Bhaṭṭi, the Śatakas, …) | G·N·L | 26,973 |

## State V — Sanskrit bouddhique et jaina ; le sanskrit hors de l'Inde (chap. V, p. 206)

| Code | Renou subsection (page) | Covers | Detector | Headwords |
|---|---|---|---|--:|
| `bauddha` | Sanskrit bouddhique · sanskrit « hybride » (p. 206, 220) | Buddhist Sanskrit incl. Edgerton's Hybrid (BHS) | G·N·L·D (BHS set; `bhs`→`bauddha`) | 25,740 |
| `jaina` | Sanskrit jaina (p. 222) | Jaina Sanskrit | L (Jaina sigla) | 286 |
| `hors_inde` | Le sanskrit hors de l'Inde (p. 229) | Sanskrit abroad (Central-/SE-Asian usage) | — | 0 |

---

## Notes on coverage

- **Single-route registers.** `epig` (709) and `jaina` (286) come **only** from `<ls>`
  citations — the corpus contains no inscriptions and no separate Jaina genre; `tantra`
  and `karika` come **only** from the corpus — the curated siglum CANON has no Tantra or
  kārikā source. `atharva` (8,512) is corpus-invisible too (DCS has no Atharvaveda
  directory) and is recovered entirely through the AV citation siglum.
- **`hors_inde` is empty (0).** No source exists in either signal — no Central-/SE-Asian
  corpus text, no such siglum in the maps. It is kept in the lattice for completeness and
  flagged honestly, not silently dropped.
- **`bauddha` is the only register with all four detector routes**, because state V has a
  dedicated set (Edgerton's BHS), so `renou_bhs` → `bauddha` wholesale (all 17,839 BHS
  entries; every BHS-dictionary headword is Buddhist by construction).
- **Coverage spans three orders of magnitude** — from `epic` (48,713) and `kavya` (26,973)
  down to `jaina` (286) and `epig` (709) — but every register is one of Renou's own
  subsections and carries equal standing here; a small count reflects a thin *source*
  (few inscriptions, few Jaina sigla), not a lesser register.

## Numbered index — chapter-relative (Scheme A)

Each register gets a strict number **within its Renou chapter** (`{state}.{n}`):

- **I.1** rgveda · **I.2** atharva · **I.3** yajus · **I.4** brahmana · **I.5** upanisad · **I.6** sutra
- **II.1** vyakarana · **II.2** epig
- **III.1** epic · **III.2** purana · **III.3** tantra · **III.4** smrti · **III.5** karika
- **IV.1** bhasya · **IV.2** katha · **IV.3** natya · **IV.4** kavya
- **V.1** bauddha · **V.2** jaina · **V.3** hors_inde

## Numbered index — global unique (Scheme B)

Each subcategory also gets one **unique running number** `(1.)–(20.)`, carried alongside
its chapter-relative code, so every register has a single stable id across the whole lattice:

| # | Chapter-rel. | Register | Headwords |
|--:|---|---|--:|
| (1.) | I.1 | rgveda | 15,370 |
| (2.) | I.2 | atharva | 8,512 |
| (3.) | I.3 | yajus | 11,015 |
| (4.) | I.4 | brahmana | 16,562 |
| (5.) | I.5 | upanisad | 4,831 |
| (6.) | I.6 | sutra | 18,893 |
| (7.) | II.1 | vyakarana | 22,429 |
| (8.) | II.2 | epig | 709 |
| (9.) | III.1 | epic | 48,713 |
| (10.) | III.2 | purana | 31,255 |
| (11.) | III.3 | tantra | 5,416 |
| (12.) | III.4 | smrti | 17,546 |
| (13.) | III.5 | karika | 3,021 |
| (14.) | IV.1 | bhasya | 14,498 |
| (15.) | IV.2 | katha | 24,393 |
| (16.) | IV.3 | natya | 12,611 |
| (17.) | IV.4 | kavya | 26,973 |
| (18.) | V.1 | bauddha | 25,740 |
| (19.) | V.2 | jaina | 286 |
| (20.) | V.3 | hors_inde | 0 |

## See also

- [`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md) — the two-axis tagging system (states + registers).
- [`glossaries/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossaries/README.md) — shipped register glossaries (épig, bhāṣya, kāvya,
  bauddha, jaina + cross-axis slices), generated by `renou_glossary.py REGISTER`.
- [`papers/A34_renou_register_note.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md) — the data
  note (the 68 %-corpus-absent épigraphique finding).

_Dr. Mārcis Gasūns_
