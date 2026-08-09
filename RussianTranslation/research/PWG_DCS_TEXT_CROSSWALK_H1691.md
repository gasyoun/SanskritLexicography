# Mapping the rest of PWG's DCS-carried cited texts — 52 abbreviations adjudicated (H1691)

_Created: 26-07-2026 · Last updated: 26-07-2026_

_Measured by Opus 5 (`claude-opus-5[1m]`) for [H1691](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1691-Opus_kosha_pwg-dcs-text-crosswalk-beyond-five_26.07.26.md).
Deterministic, no LLM in the measurement path, no sampling, no RNG. Continues
[H1670](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1670-Opus_SanskritLexicography_pwg-dcs-sense-grounding-scale-levers_26.07.26.md)
([report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_GROUNDING_LEVERS.md))._

## The headline, and the classifier error it rests on

H1670 left a ranked backlog of 443 PWG `<ls>` abbreviations that DCS appeared to
carry but the aligner did not map — 102,546 citations, 13.9% of the dictionary's
`<ls>` mass — and warned that its candidate column was a loose name match, not a
crosswalk. Working that backlog top-down produced the expected result and one
unexpected one.

| | grounded leaf senses | grounded headword groups | verse-level locus rows |
|---|---:|---:|---:|
| H1670 as published (wide frame, full scan, 5-text map) | 7,372 | 6,663 | 12,280 |
| **H1691 (wide frame, full scan, 12 further texts)** | **8,208** | **7,303** | **14,661** |
| Δ | **+836 (+11.3%)** | +640 (+9.6%) | +2,381 |

The unexpected result is **where the largest additions came from**. The backlog's
candidate generator matches on the *resolved `pwgbib` entry*, which is **German
prose**, and PWG names its two most-cited authorities by author and language —
"PĀṆINI'S acht Bücher grammatischer Regeln", "MANU'S Gesetzbuch in der Ausg. von
LOISELEUR DESLONGCHAMPS" — never by Sanskrit title. So `P.` and `M.` were sorted
into `DCS-LACKS`, the class H1670 described as "a genuine corpus gap that no
crosswalk can close". DCS carries both: the Aṣṭādhyāyī and the Manusmṛti.

**41,910 citations — 5.7% of the entire dictionary's `<ls>` mass, the two largest
crosswalk wins available — were sitting in the class labelled untouchable.**
Together they account for 827 of the 1,152 newly grounded senses.

The class is wrong in the other direction too. `candidates()` returns every
name-alike and then keeps the one with the **most tokens**, so `SĀṂKHYAK` was
paired with the Sāṃkhyakārikā*bhāṣya* while DCS also carries the bare kārikā; and
six abbreviations were paired with a **different work** whose correct counterpart
DCS also carries (`TBR` with the Taittirīya*saṃhitā* rather than the *brāhmaṇa*;
`KĀTY. ŚR`, `ĀŚV. ŚR`, `ŚĀṄKH. BR`, `ŚĀṄKH. GṚHY`, `TAITT. ĀR`/`UP` likewise).
Neither `dcs_text` nor `DCS-LACKS` may be quoted as a fact about the corpus.
`DCS-LACKS` means only "no name-alike was found".

## How each verdict was reached

Every `DCS-HAS-UNMAPPED` abbreviation above 0.05% citation mass (≈370 citations)
was adjudicated on four independent legs, in this order, and nothing was mapped on
a name:

1. **The `pwgbib` entry**, read in full. PWG states its scheme in prose, and that
   alone settled several: `HIT` — "eine arabische [Zahl] --die Seite; die zweite
   Zahl bezeichnet dort den Śloka, hier die **Zeile**" (page and line, not book and
   verse); `VP` — "Es wird die WILSON'sche **Uebersetzung** citirt"; `KAUŚ` — "Die
   Kaṇḍikā sind **durchgezählt**".
2. **~20 sampled real `<ls>` strings** per abbreviation, with a component-count
   histogram and per-component maxima — which catches a bib entry the dictionary
   does not follow, and abbreviations with no bib entry at all. `DAŚAK`'s loci
   carry `ult` and `v. u.` (*letzte Zeile*, *von unten*): page and line, whatever
   the entry says. `KĀŚ` (389 citations) and `NIGH. PR` (919) turn out to carry **no
   address at all**.
3. **Containment** — do PWG's tuples exist as addresses in that DCS text, using the
   aligner's own `numeric_address()` so what is counted is exactly what the locus
   tier could ever see. Calibrated against the already-verified mappings, which
   score 25–98%; the four texts H1670 rejected on documented grounds score 0.0–1.4%.
4. **Competitive rank against all 270 DCS texts.** A plain hit rate is confounded
   by address-space size — a 2-tuple like (5,25) exists in almost any large text —
   so the confound-free question is whether the candidate explains *these* tuples
   better than every other text does. The known-good controls rank 1–2 (ṚV 1,
   Yājñavalkyasmṛti 1, Bhāgavatapurāṇa 2 behind only the Mahābhārata); `KATHĀS`
   ranks **193 of 220**.

Then, for every text actually mapped, **≥10 of its new `locus` rows were read** —
because a summary statistic is what H1670's Rāmāyaṇa false positives survived.

## What was mapped — 12 texts, per-text attribution

Per-text contribution to the final run, and the newly grounded senses each is
responsible for. Every one of the 1,152 fresh groundings is attributable to a
newly mapped text; no text added nothing.

| DCS text | PWG abbrev | citations | verse rows | chapter rows | senses | **new senses** | hand-checked |
|---|---|---:|---:|---:|---:|---:|---:|
| Manusmṛti | `M` | 20,605 | 2,038 | 0 | 1,312 | **474** | 10/10 ✓ |
| Aṣṭādhyāyī | `P` | 21,305 | 1,004 | 0 | 651 | **353** | 10/10 ✓ |
| Kātyāyanaśrautasūtra | `KĀTY. ŚR` | 8,099 | 389 | 0 | 287 | 120 | 10/10 ✓ |
| Pañcaviṃśabrāhmaṇa | `PAÑCAV. BR` | 2,089 | 226 | 1 | 124 | 69 | 10/10 ✓ |
| Kirātārjunīya | `KIR` | 644 | 135 | 0 | 110 | 51 | 10/10 ✓ |
| Āśvalāyanagṛhyasūtra | `ĀŚV. GṚHY` | 1,555 | 57 | 34 | 67 | 37 | 10/10 ✓ |
| Śāṅkhāyanaśrautasūtra | `ŚĀṄKH. ŚR` | 2,469 | 87 | 0 | 69 | 34 | 10/10 ✓ |
| Bṛhadāraṇyakopaniṣad | `BṚH. ĀR. UP` | 747 | 68 | 0 | 48 | 21 | 10/10 ✓ |
| Gītagovinda | `GĪT` | 1,138 | 47 | 0 | 39 | 21 | 10/10 ✓ |
| Kaṭhopaniṣad | `KAṬHOP` | 445 | 58 | 0 | 49 | 15 | 10/10 ✓ |
| Gobhilagṛhyasūtra | `GOBH` | 882 | 40 | 0 | 22 | 11 | 10/10 ✓ |
| Śatakatraya | `BHARTṚ` | 1,214 | 29 | 0 | 28 | 8 | 10/10 ✓ |
| **total** | | **61,192** | **4,178** | **35** | **2,553** | **1,152** | **120/120** |

The hand-checks are not a formality. Both halves were verified: the DCS address
equals an `<ls>` **on that very sense** (checked mechanically over all 4,127 new
rows, not only the sample — 100% for eleven texts, and the Āśvalāyanagṛhyasūtra's
apparent 62.4% was an artefact of the check itself, since a counter-less DCS
address renders as `…, 1, 12, None`); and the passage instantiates the gloss.
Representative:

- `padmāvatī` sense 3, "Bein. der Lakṣmī" — PWG's *sole* citation for that sense is
  `GĪT. 1,2`, and GītGov 1,2 reads *padmāvatīcaraṇacāraṇacakravartī*.
- `mahāvīra` 1b, "ein grosser irdener Topf … namentlich beim Pravargya gebraucht"
  — ŚāṅkhŚS 5,12,2: *mahāvīrapātrodvāsanaṃ sapravargye*.
- `pragraha` 5, "Zügel" — KaṭhUp 3,3: *manaḥ pragraham eva ca*, the chariot simile.
- `saṃnahana` 1, "das Zusammenbinden, Schnüren" — sole citation `ĀŚV. GṚHY. 1,10,3`;
  ĀśvGS 1,10,3 reads *idhmābarhiṣoś ca saṃnahanam*.
- `kanthā` 1, "ein geflicktes Kleid, wie es namentlich einige Büsser zu tragen
  pflegen" — `BHARTṚ. 3,16`; ŚTr 3,16: *vastraṃ viśīrṇaśatakhaṇḍamayī ca kanthā*.

**One caveat that must travel with the Aṣṭādhyāyī figure.** A DCS "passage" there
is a *sūtra*, and PWG cites `P.` as the grammatical **authority** for a word or
form — so the row attests that Pāṇini treats the word at that sūtra, not that a
passage uses it in the glossed sense. `rūpya` 3d is glossed literally "am Ende
eines comp. = P. 4,3,81". That is a legitimate and precisely-located attestation,
but it is a different evidentiary kind from a Ṛgveda verse, and the 353
Aṣṭādhyāyī-grounded senses should never be pooled with usage attestations without
saying so. Excluding it, the delta is **+483 senses (+6.6%)**.

## What was NOT mapped — and why the rejections are the result

38 abbreviations were rejected and 2 recorded `unverifiable`; all 52 verdicts, with
their evidence and one-line reasons, are committed in
[`pwg_ls_dcs_scheme_verdicts.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_ls_dcs_scheme_verdicts.tsv)
so nobody re-litigates them. The recurring failure modes, in order of citation mass:

| failure mode | abbrevs | example |
|---|---|---|
| **page-and-line, not verse** | `HIT` (2,426), `DAŚAK` (1,656), `VP` (3,991), `BṚH. ĀR. UP. S` (682), `VET` | PWG cites an edition's pagination; DCS addresses verses |
| **different numbering of the same work** | `KATHĀS` (23,198), `KAUŚ` (3,021), `AK` (15,414), `TRIK` (8,519) | Brockhaus's 124 continuous taraṅgas vs DCS's 8 lambakas / 44 chapters |
| **arity mismatch** | `KĀṬH` (1,440), `PĀR. GṚHY` (778) | PWG stops at the anuvāka where DCS reaches the mantra; a 2-tuple can never equal a 3-tuple |
| **the candidate was the wrong work** | `ĀŚV. ŚR`, `ŚĀṄKH. BR`, `ŚĀṄKH. GṚHY`, `TAITT. ĀR`, `TAITT. UP` | DCS carries the right work in every case — and still does not correspond |
| **1-component locus** | `AMAR`, `CAURAP`, `SĀṂKHYAK`, `MEGH` | `verse_equal()` requires ≥2 components; a bare verse number cannot match |
| **no address at all** | `KĀŚ` (373), `NIGH. PR` (919), `BHĀVAPR` (489) | the citations are bare abbreviations |
| **DCS ref carries a named section** | `MEGH`, `VET`, `BHĀVAPR`, `BHAG` | `numeric_address()` abstains, by design (H1670 defect 1) |

Two are `unverifiable` rather than rejected, which is the verdict the handoff asked
for when evidence runs out:

- **`TBR`** (3,000 citations). The backlog's candidate was the wrong work and DCS
  does carry the Taittirīya*brāhmaṇa* — but at 15.4% containment it is **beaten by
  the Maitrāyaṇīsaṃhitā at 43%**. The Yajurveda prose texts share an address
  structure and cross-hit each other, so the pairing cannot be established from
  address evidence. Not mapped.
- **`VP`** (3,991). Ranks **1 of 220** on its multi-component minority, yet scores
  only 19.1% — between the verified band (25–98%) and the rejected band (0.0–1.4%)
  — and `pwgbib` is explicit that PWG cites Wilson's translation by page, with
  2,679 of 4,037 citations being bare page numbers up to 2087. H1670's rejection
  stands, now with a number attached.

`LĀṬY` (2,356) deserves its own line: DCS does **not** carry Lāṭyāyana, but it does
carry the Drāhyāyaṇaśrautasūtra, a parallel Sāmaveda Śrautasūtra that scores 29.4%.
Mapping it would be precisely the name-resemblance error this pass exists to avoid.

## The residue, re-classified

| class | H1670 | H1691 | what it now means |
|---|---:|---:|---|
| `MAPPED` | 269,287 (36.4%) | **330,479 (44.7%)** | 27 abbrevs, scheme verified |
| `ADJUDICATED-NO` | — | 120,523 (16.3%) | the corpus side exists and is identified; the **scheme** fails |
| `ADJUDICATED-UNVERIFIABLE` | — | 6,991 (0.9%) | evidence insufficient either way |
| `DCS-HAS-UNMAPPED` | 102,546 (13.9%) | **6,242 (0.8%)** | 406 abbrevs, every one below 0.05% mass |
| `DCS-LACKS` | 367,670 (49.7%) | 275,268 (37.2%) | no name-alike found — **not** proof DCS lacks it |

The actionable backlog above the threshold is **empty**: zero `DCS-HAS-UNMAPPED`
abbreviations above 0.05% remain without a verdict, the largest survivor being
`ṢAḌV. BR` at 0.0475%. The `DCS-LACKS` figure fell by 92,402 citations purely
because texts were found under names the German prose never mentioned — and it is
still an upper bound on the gap, not a measurement of it, for exactly that reason.

## A precision defect found and fixed on the way

H1670 fixed "chapter-level matches reported as exact-verse" by giving them their
own `locus-chapter` tier. The fix chose the tier **once per sense** while stamping
rows **per passage** — and a sense can match several passages at once whose
addresses bottom out differently. So **507 of H1670's own 12,280 `locus` rows
(4.13%) sat in the exact-verse tier at confidence 0.90 on an address that stops at
the chapter**; 504 of them Aitareyabrāhmaṇa, which the containment test
independently shows is a chapter-level-only text for PWG (verse 0.3%, chapter 95.9%).

The level now travels with the row. After the fix **zero** exact-verse rows carry a
counter-less address (522 moved to `locus-chapter` in the H1691 run), and the
sense-level tier reported in the log is the strongest level a sense achieved, so
the counters keep their meaning. This **tightens** the headline rather than
loosening it, and the grounded-sense count is unchanged at 8,208 either way — the
fix relabels rows within the locus family, it does not add or remove groundings.

## Regression evidence, stated precisely

- The pristine H1670 aligner re-run on the frozen 500 with `--locus-scan kwic`
  reproduces the committed wave-1 artifacts to **17 differing concordance lines** —
  exactly the figure H1670 reports for its Ṛgveda key fix. The pipeline reproduces.
- That same run contains **0** counter-less `locus` rows, so the tier fix is
  provably a **no-op on wave-1**. The wave-1 delta of 62 lines under H1691 is
  therefore attributable entirely to the 12 map additions, not to the tier change.
- The wide frame rebuilds to **16,208 groups** and the loci export to **189,301
  leaf-sense rows over 109,050 groups** — both identical to H1670.
- Re-measuring H1670's own concordance with the published harness returns
  **7,372**, its published number.

## What this does NOT claim

- **The net +836 is not 836 senses gained.** 1,152 senses were newly grounded and
  **316 lost** their grounding. All 316 belong to groups that still have a
  locus-grounded sense: the aligner assigns at most one sense per (headword, DCS
  lemma) link on a first-match-wins basis, so widening the text map **relocates**
  some groundings to a sibling sense as well as adding new ones. Where this was
  inspected the relocation was an improvement (`lohita` moved from sense 1a at
  `overlap` 0.5 to sense 1b at `locus` 0.9), but that has **not** been established
  at scale, and the sense-level count is sensitive to it.
- **The Aṣṭādhyāyī rows attest grammatical treatment, not usage** — see the caveat
  above. Excluding them the delta is +483 (+6.6%).
- Containment and rank are evidence of **scheme correspondence**, never of sense
  identity. That is what the 120 hand-checks are for, and they cover 2.9% of the
  new rows — the other 97.1% rest on the mechanical address-on-sense check.
- `DCS-LACKS` remains a statement about the name matcher, not about DCS. 37.2% of
  PWG's citation mass is an **upper bound** on the untouchable residue; this pass
  moved 92,402 citations out of it and did not audit the remaining 3,735 abbrevs.
- No predicate was relaxed. `verse_equal()` and `numeric_address()` are byte-identical
  to H1670; no heuristic or LLM matcher was substituted; the `overlap` tier stays out
  of every headline; the frozen 500 frame file and wave-1's committed artifacts were
  not touched.

## Reproduce

```sh
# 1 — the PWG side (needs csl-orig); bulk output is gitignored, the generator is the artifact
cd RussianTranslation/research
python export_frame_sense_loci.py --all
python ../../../kosha/scripts/select_sense_pilot.py \
    --input pwg_sense_loci.all.tsv --size 200000 --out frame_wide.tsv

# 2 — the evidence behind the verdicts
python probe_dcs_text_scheme.py                 # DCS ref/counter shapes
python probe_pwg_ls_scheme.py --from-backlog    # pwgbib entries + real <ls> samples
python probe_scheme_overlap.py --rank --null 6 --pair "KIR=Kirātārjunīya" ...

# 3 — the aligner, before and after the map addition (kosha)
python scripts/build_sense_corpus_concordance.py --input <loci> --pilot frame_wide.tsv \
    --out-dir run_h1691 --locus-scan full --no-ls-rows

# 4 — measure, attribute, hand-check
python pwg_sense_dcs_attestation_pilot.py --frame-mode file --frame frame_wide.tsv \
    --concordance <run>/sense_corpus_concordance.tsv --tag h1691
python h1691_handcheck.py --new <new> --base <base> --summary
python build_ls_text_crosswalk_backlog.py --loci pwg_sense_loci.all.tsv
```

The aligner and the text map live in
[`build_sense_corpus_concordance.py`](https://github.com/gasyoun/kosha/blob/main/scripts/build_sense_corpus_concordance.py);
the DCS master is `VisualDCS/src/DCS-data-2026/dcs_full.sqlite` (920,883,200 bytes —
the sibling `src/` and repo-root copies are 0-byte decoys and were not read).

_Dr. Mārcis Gasūns_
