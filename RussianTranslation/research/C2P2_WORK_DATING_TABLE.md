# C2 phase 2 — curated per-work dating table with scholarly sources

_Created: 01-09-2026 · Last updated: 01-09-2026_

_Handoff [H3790](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3790-Opus_SanskritLexicography_ceiling-c2-phase2-work-dating-table_31.08.26.md) · roadmap item [C2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md) · phase 1 is [C2P1_ATTESTATION_WINDOW.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/C2P1_ATTESTATION_WINDOW.md)_

_Dr. Mārcis Gasūns_

**What this is.** Phase 1 joined every numbered PWG sense to the works its `<ls>` citations
name, using the 45 point dates in
[ls_source_map.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json).
Those 45 numbers had no provenance: nothing said where `MBH → 80 CE` came from or how far it
could be trusted. This phase supplies the citable half — for each of the 45 sigla a **range**
instead of a point, the **scholarly source** the range comes from, and an honest label for how
firm it is. The machine-readable table is
[work_dating_table.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/work_dating_table.json);
this file is its human-facing render.

## The three fences this phase honours

1. **Never a claim about sense-emergence.** A range here says when a *work* was composed, as
   stated by a named scholar. Phase 1's windows remain *«per Böhtlingk–Roth's citations»* — a
   fact about what the dictionary's editors chose to cite. Nothing in this table converts an
   attestation window into a date of origin for a meaning, and no downstream consumer may
   read it that way.
2. **Every date carries a citation; a date without one is a gap, not a guess.** Enforced
   mechanically: `c2p2_dating_table.py --check` fails any row whose `sources` list is empty,
   whose `ref` does not resolve in the bibliography, or which claims an on-disk quote without
   a printed page.
3. **Contested datings are surfaced, never self-ruled.** Where named scholars hold materially
   different positions, the row is labelled `contested`, routed to a `C2P2-D*` decision, and
   left open. The table records *both* positions; it does not pick one.

## Method

- **Consume, do not re-derive.** `ls_source_map.json` and
  `pwg_sense_attestation_window.jsonl` are read-only inputs. Neither is modified by this
  phase, and no second window store is written. Where the curated range contradicts phase 1's
  point date, the conflict is *recorded* (`map_date_conflict`) and reported — the committed
  map is left exactly as phase 1's store consumed it.
- **Two verification grades, kept apart.** `on-disk-quote` means the claim is quoted from a
  source held in this repository with its printed page, and any future session can re-read it
  without a library: that is Vogel's *Indian Lexicography* (HIL V.4, 1979), OCR'd at
  [literature/md/Lexicography-Manuals/A history of Indian literature_ Vol_ 5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/literature/md/Lexicography-Manuals/A%20history%20of%20Indian%20literature_%20Vol_%205.md).
  `reference-only` means the range is the position of the named standard handbook, given with
  its full bibliographic reference but **not** checked against the printed page from here.
  That distinction is the honest one and it is kept in the data, not just in prose.
- **Four confidence grades.** `anchored` (a hard chronological fixed point — the author dates
  himself, a dated colophon, a dated translation as terminus ante quem, a securely dated
  patron) · `consensus` (the handbooks agree, no live dispute) · `contested` (a decision is
  owed) · `dating-invalid` (the siglum is not a datable Sanskrit work at all).

## Two findings that change how phase 1's windows should be read

**`Spr.` is not a Sanskrit work.** *Indische Sprüche* is Böhtlingk's **own** anthology of
gnomic verse (St. Petersburg 1863–1865, 2nd ed. 1870–1873) — the editor of PWG citing his own
collection. Its verses come from across the whole of Sanskrit literature, so the anthology's
date bounds nothing about any verse in it. Phase 1 gave it `600 CE` and 12,976 citations
inherited that anchor. The C2P1 hand-check sample shows the effect directly: `ruc / sense #0`
cites only `Spr. (II) 6939` and `ṚV. 1,165,12`, and comes out as a window of −1125…**600** —
where the 600 is an artefact of Böhtlingk's title page.

**`ŚKDR.` dates from Böhtlingk–Roth's own lifetime.** The *Śabdakalpadruma* was published at
Calcutta between 1821 and 1858. Phase 1 gave it `1830 CE` — which is right as a publication
date and useless as a language date. Its 20,110 citations pull thousands of windows' `latest`
into the 19th century; the C2P1 sample again shows it plainly, with `kāYci / sense #0`
emerging as a window of **1830…1830** and `prakzepa / sense #2` likewise.

Neither siglum is dropped here. Both are marked `dating_valid: false`, the impact is measured
below, and whether to exclude them from windows or keep them behind a flag is decision
**C2P2-D10** — a human call, because excluding them shrinks coverage and keeping them keeps a
known-false bound.

## What is NOT done here

- `ls_source_map.json` is not modified.
- `pwg_sense_attestation_window.jsonl` is not re-derived, re-windowed, or rewritten.
- No sense-emergence claim is made anywhere.
- The **C7 residue is untouched and carried forward unchanged**: 115,354 citation instances
  across 2,607 distinct sigla resolve to no work in the map at all, so every window remains a
  **conservative lower bound**. A work absent from the map is absent from this table too —
  curating the 45 does nothing for the 2,607, and this phase makes no progress against C7.

## Where the eleven decisions are voted

Not in chat and not in this file: the eleven contested rows are one interactive sheet,
published to the public vote hub in the same pass that built the table —
[gasyoun.github.io/vote/sheets/pwg_c2p2_work_dating_11.html](https://gasyoun.github.io/vote/sheets/pwg_c2p2_work_dating_11.html)
(11 cards, 🟢 ≤15 cards / 5–15 min, `sheet_id` `c2p2-work-dating-2026-09-01`). Each card
proposes one reading in a full sentence with a recommendation and what would reverse it;
approving adopts it, rejecting takes the alternative the select names. Generator:
[src/build_c2p2_dating_sheet.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_c2p2_dating_sheet.py).

**The seven map-date corrections are NOT on that sheet.** `AMAR`, `GĪT. GOV`, `KATHĀS`,
`RĀJAN`, `SĀH. D`, `VOP` and `Spr` each have a citation that settles them, so they are
applied to the curated table and reported here rather than voted — an evidence-decidable row
never becomes a card.

## Reproduce

```sh
cd RussianTranslation/research
python c2p2_dating_table.py --selftest   # fixture tests for the validator + re-window maths
python c2p2_dating_table.py --check      # gate: 45/45 covered, every date sourced, contested routed
python c2p2_dating_table.py --report     # regenerates the block below
```

<!-- c2p2:generated:start -->

## The table — 45 sigla, every date sourced

Sorted by the curated `earliest`. `map` is the point date phase 1 used; a **bold**
map value falls outside the sourced range and is an evidence-decidable correction.

| Siglum | Work | Curated range | map | Confidence | Source(s) | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| `ṚV` | Ṛgveda | 1500 BCE – 1000 BCE | 1125 BCE | ⚖ contested | witzel1995, witzel1997 | C2P2-D1 |
| `AV` | Atharvaveda | 1200 BCE – 900 BCE | 940 BCE | ○ consensus | witzel1989, witzel1997 | — |
| `VS` | Vājasaneyi-Saṃhitā | 1200 BCE – 800 BCE | 900 BCE | ○ consensus | witzel1997 | — |
| `TS` | Taittirīya-Saṃhitā | 1000 BCE – 800 BCE | 1000 BCE | ○ consensus | witzel1997 | — |
| `AIT. BR` | Aitareya-Brāhmaṇa | 900 BCE – 600 BCE | 700 BCE | ○ consensus | witzel1997 | — |
| `ŚAT. BR` | Śatapatha-Brāhmaṇa | 800 BCE – 600 BCE | 800 BCE | ○ consensus | witzel1997 | — |
| `NIR` | Nirukta (Yāska) | 700 BCE – 400 BCE | 500 BCE | ⚖ contested | kahrs1998, sarup1920 | C2P2-D4 |
| `P` | Pāṇini, Aṣṭādhyāyī | 500 BCE – 350 BCE | 400 BCE | ⚖ contested | cardona1997, scharfe1977 | C2P2-D3 |
| `KĀTY. ŚR` | Kātyāyana-śrautasūtra | 500 BCE – 200 BCE | 400 BCE | ○ consensus | gonda1977, witzel1997 | — |
| `R` | Rāmāyaṇa | 400 BCE – 300 CE | 70 CE | ⚖ contested | brockington1998 | C2P2-D2 |
| `R. GORR` | Rāmāyaṇa (Gorresio rec.) | 400 BCE – 300 CE | 70 CE | ○ consensus | brockington1998, gorresio1843 | C2P2-D11 |
| `R. SCHL` | Rāmāyaṇa (Schlegel rec.) | 400 BCE – 300 CE | 70 CE | ○ consensus | brockington1998, schlegel1829 | C2P2-D11 |
| `MBH` | Mahābhārata | 400 BCE – 400 CE | 80 CE | ⚖ contested | brockington1998, hiltebeitel2001 | C2P2-D2 |
| `BHAG` | Bhagavadgītā | 200 BCE – 200 CE | 200 CE | ○ consensus | brockington1998, malinar2007 | C2P2-D11 |
| `GĪT` | Bhagavadgītā | 200 BCE – 200 CE | 200 CE | ○ consensus | malinar2007 | C2P2-D11 |
| `SUŚR` | Suśruta-Saṃhitā | 200 BCE – 500 CE | 400 CE | ⚖ contested | meulenbeld1999 | C2P2-D8 |
| `HARIV` | Harivaṃśa | 100 CE – 300 CE | 200 CE | ○ consensus | brockington1998 | — |
| `M` | Manusmṛti | 100 CE – 300 CE | 150 CE | ○ consensus | kane1930, olivelle2005 | — |
| `YĀJÑ` | Yājñavalkya-Smṛti | 100 CE – 500 CE | 300 CE | ⚖ contested | kane1930, olivelle2019 | C2P2-D5 |
| `PAÑCAT` | Pañcatantra | 200 CE – 550 CE | 300 CE | ○ consensus | edgerton1924, olivelle1997 | — |
| `MĀRK. P` | Mārkaṇḍeya-Purāṇa | 250 CE – 600 CE | 550 CE | ⚖ contested | rocher1986 | C2P2-D9 |
| `VP` | Viṣṇu-Purāṇa | 300 CE – 500 CE | 450 CE | ⚖ contested | rocher1986 | C2P2-D9 |
| `KUMĀRAS` | Kumārasambhava | 375 CE – 470 CE | 420 CE | ⚖ contested | lienhard1984, warder_ikl | C2P2-D7 |
| `MEGH` | Meghadūta | 375 CE – 470 CE | 420 CE | ⚖ contested | lienhard1984 | C2P2-D7 |
| `RAGH` | Raghuvaṃśa | 375 CE – 470 CE | 420 CE | ⚖ contested | lienhard1984 | C2P2-D7 |
| `ŚĀK` | Abhijñānaśākuntala | 375 CE – 470 CE | 420 CE | ⚖ contested | lienhard1984 | C2P2-D7 |
| `AK` | Amarakośa | 400 CE – 700 CE | 450 CE | ⚖ contested | vogel1979 | C2P2-D6 |
| `VARĀH` | Varāhamihira | 505 CE – 587 CE | 550 CE | ⚓ anchored | pingree1981 | — |
| `VARĀH. BṚH. S` | Varāhamihira, Bṛhatsaṃhitā | 505 CE – 587 CE | 550 CE | ⚓ anchored | pingree1981 | — |
| `AMAR` | Amaru-śataka | 650 CE – 800 CE | **450 CE** | ○ consensus | lienhard1984, warder_ikl | — |
| `HIT` | Hitopadeśa | 800 CE – 1373 CE | 1000 CE | ○ consensus | sternbach1974, warder_ikl | — |
| `BHĀG. P` | Bhāgavata-Purāṇa | 850 CE – 1000 CE | 950 CE | ○ consensus | hardy1983, rocher1986 | C2P2-D9 |
| `HALĀY` | Halāyudha, Abhidhānaratnamālā | 925 CE – 956 CE | 950 CE | ⚓ anchored | vogel1979 | — |
| `KATHĀS` | Kathāsaritsāgara | 1063 CE – 1081 CE | **1050 CE** | ⚓ anchored | warder_ikl | — |
| `H` | Hemacandra, Abhidhānacintāmaṇi | 1088 CE – 1172 CE | 1150 CE | ⚓ anchored | vogel1979 | — |
| `H. an` | Hemacandra, Anekārthasaṃgraha | 1088 CE – 1172 CE | 1150 CE | ⚓ anchored | vogel1979 | — |
| `TRIK` | Trikāṇḍaśeṣa | 1100 CE – 1160 CE | 1150 CE | ⚓ anchored | vogel1979 | — |
| `RĀJA-TAR` | Rājataraṅgiṇī | 1148 CE – 1150 CE | 1150 CE | ⚓ anchored | stein1900 | — |
| `GĪT. GOV` | Gītagovinda | 1170 CE – 1200 CE | **1048 CE** | ○ consensus | lienhard1984, miller1977 | — |
| `MED` | Medinīkośa | 1200 CE – 1275 CE | 1200 CE | ⚓ anchored | vogel1979 | — |
| `VOP` | Vopadeva, Mugdhabodha | 1260 CE – 1300 CE | **1250 CE** | ○ consensus | scharfe1977 | — |
| `SĀH. D` | Sāhityadarpaṇa | 1300 CE – 1384 CE | **1400 CE** | ○ consensus | gerow1977 | — |
| `RĀJAN` | Rājanighaṇṭu | 1375 CE – 1500 CE | **1300 CE** | ○ consensus | vogel1979 | — |
| `ŚKDR` | Śabdakalpadruma | 1821 CE – 1858 CE | 1830 CE | ✖ dating-invalid | radhakanta1821, vogel1979 | C2P2-D10 |
| `Spr` | Indische Sprüche (Böhtlingk's anthology) | 1863 CE – 1873 CE | **600 CE** | ✖ dating-invalid | bohtlingk1870, sternbach1974 | C2P2-D10 |

**Shape:** 9 anchored · 20 consensus · 14 contested · 2 dating-invalid. 8 of the citations are quoted from a source held in this repository (Vogel 1979, with printed page); the rest name the standard reference and are marked `reference-only` — page-level verification is an open residual, not a claim.

**Map-date conflicts (7):** `AMAR`, `GĪT. GOV`, `KATHĀS`, `RĀJAN`, `Spr`, `SĀH. D`, `VOP` — recorded here, **not** written back into `ls_source_map.json`, which phase 1's committed store consumed.

## Dating-invalid sigla — what phase 1's windows are actually reporting

Two sigla in the map are not datable Sanskrit works. `Spr.` is Böhtlingk's own
anthology (St. Petersburg, 1863–1873) and `ŚKDR.` a Calcutta compilation of
1821–1858. Both were given ordinary point dates in phase 1 and both therefore
set window bounds that mean nothing about the language.

| Measure | Windows |
| --- | --- |
| windows with at least one dated work | 43,990 |
| … containing a dating-invalid siglum | 11,771 (26.8%) |
| … of which cite `ŚKDR` | 7,508 |
| … of which cite `Spr` | 4,653 |
| … whose ONLY dated works are invalid (window would vanish) | 2,873 |
| windows whose `latest` is set by an invalid siglum | 9,082 |

**If the curated table replaced the point dates:** `earliest` would move on 39,027 windows and `latest` on 39,823, out of 43,990. Most of that is not error correction but the point→range change itself: a work that was one number is now a bracket, so almost every bound shifts by construction. The 7 map-date conflicts and the two dating-invalid sigla are the part that is a correction. The re-window is deliberately NOT performed here — phase 1's store is consumed, not re-derived (H3790), and which convention to use for growth-span works is itself an open decision (C2P2-D2).

## Contested datings — 11 decisions, none self-ruled

- **C2P2-D1** — Ṛgveda anchor: does the window's earliest use the composition span's start (c. -1500) or the collection/redaction (c. -1000)? _(sigla: `ṚV`)_
- **C2P2-D2** — Growth-span epics (MBh, Rām): does a work spanning centuries enter the window as its full span, or as a single conventional point date? _(sigla: `MBH`, `R`)_
- **C2P2-D3** — Pāṇini: mid-5th century BCE or mid-4th century BCE? _(sigla: `P`)_
- **C2P2-D4** — Yāska's Nirukta: pre-Pāṇinian (c. -700…-500) or later? _(sigla: `NIR`)_
- **C2P2-D5** — Yājñavalkya-Smṛti: Kane's 1st–3rd century CE or Olivelle's 4th–5th century CE? _(sigla: `YĀJÑ`)_
- **C2P2-D6** — Amarakośa: Vogel states the date problem is unsolved — which working range does the project adopt? _(sigla: `AK`)_
- **C2P2-D7** — Kālidāsa (4 sigla): the Gupta consensus c. 400–450 CE, or the minority Vikramāditya-era early date? _(sigla: `KUMĀRAS`, `MEGH`, `RAGH`, `ŚĀK`)_
- **C2P2-D8** — Suśruta-Saṃhitā: the early core or the Nāgārjuna redaction as the anchor? _(sigla: `SUŚR`)_
- **C2P2-D9** — Purāṇas (3 sigla): does the project assign point dates at all, given Rocher's caution? _(sigla: `BHĀG. P`, `MĀRK. P`, `VP`)_
- **C2P2-D10** — Dating-invalid sigla (Spr., ŚKDR.): drop from windows entirely, or keep with a flag? _(sigla: `Spr`, `ŚKDR`)_
- **C2P2-D11** — Siglum identity: BHAG/GĪT are one work; R/R. GORR/R. SCHL are three editions of one work — does the window count them once or three times? _(sigla: `BHAG`, `GĪT`, `R. GORR`, `R. SCHL`)_

## Bibliography

- **`bohtlingk1870`** — Böhtlingk, Otto. 1870–1873. Indische Sprüche: Sanskrit und Deutsch. 2nd ed., 3 vols. St. Petersburg: Kaiserliche Akademie der Wissenschaften. (1st ed. 1863–1865.) The publication fact IS the finding: Spr. is Böhtlingk's own anthology, not a Sanskrit work.
- **`brockington1998`** — Brockington, John. 1998. The Sanskrit Epics (Handbuch der Orientalistik II.12). Leiden: Brill.
- **`cardona1997`** — Cardona, George. 1997. Pāṇini: A Survey of Research. 2nd ed. Delhi: Motilal Banarsidass. (1st ed. The Hague: Mouton, 1976.)
- **`edgerton1924`** — Edgerton, Franklin. 1924. The Panchatantra Reconstructed, 2 vols. New Haven: American Oriental Society.
- **`gerow1977`** — Gerow, Edwin. 1977. Indian Poetics (A History of Indian Literature V.3). Wiesbaden: Otto Harrassowitz.
- **`gonda1977`** — Gonda, Jan. 1977. The Ritual Sūtras (A History of Indian Literature I.2). Wiesbaden: Otto Harrassowitz.
- **`gorresio1843`** — Gorresio, Gaspare (ed.). 1843–1858. Rāmāyaṇa: poema indiano di Valmici, 10 vols. Paris: Imprimerie Nationale.
- **`hardy1983`** — Hardy, Friedhelm. 1983. Viraha-Bhakti: The Early History of Kṛṣṇa Devotion in South India. Delhi: Oxford University Press.
- **`hiltebeitel2001`** — Hiltebeitel, Alf. 2001. Rethinking the Mahābhārata: A Reader's Guide to the Education of the Dharma King. Chicago: University of Chicago Press.
- **`kahrs1998`** — Kahrs, Eivind. 1998. Indian Semantic Analysis: The nirvacana Tradition. Cambridge: Cambridge University Press.
- **`kane1930`** — Kane, P. V. 1930–1962. History of Dharmaśāstra, 5 vols. Poona: Bhandarkar Oriental Research Institute.
- **`lienhard1984`** — Lienhard, Siegfried. 1984. A History of Classical Poetry: Sanskrit — Pali — Prakrit (A History of Indian Literature III.1). Wiesbaden: Otto Harrassowitz.
- **`malinar2007`** — Malinar, Angelika. 2007. The Bhagavadgītā: Doctrines and Contexts. Cambridge: Cambridge University Press.
- **`meulenbeld1999`** — Meulenbeld, G. Jan. 1999–2002. A History of Indian Medical Literature, vols. IA–IIB. Groningen: Egbert Forsten.
- **`miller1977`** — Miller, Barbara Stoler. 1977. Love Song of the Dark Lord: Jayadeva's Gītagovinda. New York: Columbia University Press.
- **`olivelle1997`** — Olivelle, Patrick. 1997. The Pañcatantra: The Book of India's Folk Wisdom. Oxford: Oxford University Press.
- **`olivelle1998`** — Olivelle, Patrick. 1998. The Early Upanisads: Annotated Text and Translation. New York: Oxford University Press.
- **`olivelle2005`** — Olivelle, Patrick. 2005. Manu's Code of Law: A Critical Edition and Translation of the Mānava-Dharmaśāstra. New York: Oxford University Press.
- **`olivelle2019`** — Olivelle, Patrick. 2019. Yājñavalkya: A Treatise on Dharma. Murty Classical Library of India. Cambridge, MA: Harvard University Press.
- **`pingree1981`** — Pingree, David. 1981. Jyotiḥśāstra: Astral and Mathematical Literature (A History of Indian Literature VI.4). Wiesbaden: Otto Harrassowitz.
- **`radhakanta1821`** — Rādhākāntadeva Bahādur. 1821–1858. Śabdakalpadruma, 5 vols. Calcutta. A 19th-century Sanskrit-language encyclopaedic compilation, contemporary with Böhtlingk-Roth themselves.
- **`rocher1986`** — Rocher, Ludo. 1986. The Purāṇas (A History of Indian Literature II.3). Wiesbaden: Otto Harrassowitz. Rocher's standing methodological caution — a Purāṇa is a fluid, repeatedly re-edited text, so dating one «as a whole» is not a well-formed question — governs all three Purāṇa rows below.
- **`sarup1920`** — Sarup, Lakshman. 1920–1927. The Nighaṇṭu and the Nirukta. Lahore / London: Oxford University Press.
- **`scharfe1977`** — Scharfe, Hartmut. 1977. Grammatical Literature (A History of Indian Literature V.2). Wiesbaden: Otto Harrassowitz.
- **`schlegel1829`** — Schlegel, August Wilhelm von (ed.). 1829–1846. Rāmāyaṇa id est carmen epicum de Ramae rebus gestis. Bonn: Weber.
- **`stein1900`** — Stein, M. A. 1900. Kalhaṇa's Rājataraṅgiṇī: A Chronicle of the Kings of Kaśmīr, 2 vols. Westminster: Archibald Constable.
- **`sternbach1974`** — Sternbach, Ludwik. 1974. Subhāṣita, Gnomic and Didactic Literature (A History of Indian Literature IV.1). Wiesbaden: Otto Harrassowitz.
- **`vogel1979`** — Vogel, Claus. 1979. Indian Lexicography (A History of Indian Literature V.4). Wiesbaden: Otto Harrassowitz. ISBN 3-447-02010-5. _(held in this repository: [literature/md/Lexicography-Manuals/A history of Indian literature_ Vol_ 5.md](literature/md/Lexicography-Manuals/A history of Indian literature_ Vol_ 5.md))_ OCR of the printed volume; the running heads preserve the printed page numbers cited below.
- **`warder_ikl`** — Warder, A. K. 1972–2004. Indian Kāvya Literature, 8 vols. Delhi: Motilal Banarsidass.
- **`witzel1989`** — Witzel, Michael. 1989. «Tracing the Vedic dialects.» In Colette Caillat (ed.), Dialectes dans les littératures indo-aryennes, 97–265. Paris: Collège de France / de Boccard.
- **`witzel1995`** — Witzel, Michael. 1995. «Early Indian history: Linguistic and textual parameters.» In George Erdosy (ed.), The Indo-Aryans of Ancient South Asia: Language, Material Culture and Ethnicity, 85–125. Berlin: de Gruyter.
- **`witzel1997`** — Witzel, Michael. 1997. «The Development of the Vedic Canon and its Schools: The Social and Political Milieu.» In Michael Witzel (ed.), Inside the Texts, Beyond the Texts: New Approaches to the Study of the Vedas, 257–345. Cambridge, MA: Harvard Oriental Series, Opera Minora 2. The five-level periodization (Rgvedic → Mantra → Samhita prose → Brahmana prose → Sutra) used for every Vedic row below.
<!-- c2p2:generated:end -->

_Dr. Mārcis Gasūns_
