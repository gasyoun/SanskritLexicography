# R. (Bomb.) book 7 — measured verdict: the numbering was never the blocker

_Created: 27-07-2026 · Last updated: 27-07-2026_

**Handoff:** [H1705](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1705-Opus_SanskritLexicography_ramayana-bombay-book7-etext_26.07.26.md) ·
**Model:** Opus 5 1M (`claude-opus-5[1m]`) ·
**Scope:** PWG's plain `R.` book 7 (Bombay ed. 1859) citation reuse.

## Stop condition, and which branch was taken

H1705 offered two exits: build a Bombay e-text → corpus concordance, **or** return a
measured verdict that the Bombay uttarakāṇḍa maps ≈1:1 onto the corpus text so a
direct-with-offset scheme is honest. The measurements below reject the second exit
outright — and then reject the first one too, on a ground H1705 did not consider: the
concordance would have **no consumer**. Nothing in this pass was OCRed.

## What H1705 assumed, and what is actually true

The handoff's Context reads: *"The corpus HAS `07_ramayana-uttarakanda.jsonl` — the
missing piece is the Bombay-numbering bridge, not the RU side."* Both clauses fail.

| # | claim under test | measurement | verdict |
|---|---|---|---|
| 1 | the corpus file backs a Russian translation | `07_…jsonl` holds **2,690 `sa` segments and 0 `ru`**; `06_…jsonl` likewise (4,436 `sa`, 0 `ru`). Kāṇḍas 1/2/3/5 are fully paired (2,268 / 4,307 / 2,447 / 2,859 of each) | ❌ the RU side **is** the missing piece |
| 2 | that Sanskrit is the Southern text of record | **2,688 of 2,690** rows in [`ramayana_southern_critical_concordance.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_southern_critical_concordance.tsv) pair kāṇḍa-7 verses with the DCS **critical** edition at the *identical* `sarga.verse`, 95.5% at score 1.0. Kāṇḍa 6: 99.8% identity. Kāṇḍas 1/2/3/5: **1.2–3.0%** | ❌ kāṇḍas 6–7 are critical-edition text wearing a "Southern" label ([SL#822](https://github.com/gasyoun/SanskritLexicography/issues/822)) |
| 3 | Bombay ≈1:1 with the corpus numbering | Bombay **111** sargas + **13** interpolated vs the corpus's **100**; identical max-verse in **11 of 100** shared sargas; delta −14…+18, mean **+4.7** | ❌ no offset scheme is honest |
| 4 | the prize justifies an OCR pass | **1,765** plain `R.` book-7 citations in the full csl-orig digitisation (4.5% of 39,222 located plain-`R.` refs), sargas 1–111, plus 16 edition-qualified ones (`R. ed. Bomb.` 14, `R. SCHL.` 2) — of which **127 cite a sarga > 100**, structurally unresolvable against a 100-sarga text | ⚠️ real mass, zero reachable payoff |

### Why the corpus file exists but cannot help

There is no Russian Uttarakāṇḍa. The [RussianRamayana](https://github.com/gasyoun/RussianRamayana)
pipeline's own `data/project-status.json` lists book IV `blocked` (awaiting Serebryany's
introduction), book V `in-progress` (manuscript ~2027), book VI `draft-ready` (~2029);
**book VII is not in the pipeline at all.** Gryntser's academic translation stopped after
book 3, Leonov's covers Sundara. A Bombay↔critical verse map would resolve an `R. 7,x,y`
locus to a Sanskrit passage nobody can pair with Russian — which is not what
`citation_tm` exists to do.

That is why the OCR budget H1705 authorised was **not spent**. It is not that the pass is
hard; §473's recipe would carry most of it. It is that its only product has no consumer
until a translation exists that is at minimum three years and one blocked introduction away.

## Delta 3 in full — Bombay vs the corpus, kāṇḍa 7

Bombay-only sargas: **101–111** (11 sargas the corpus text does not contain).
Corpus-only sargas: none. Interpolated Bombay sargas, which `R. 7,<sarga>,<verse>` cannot
address at all: `23.1–23.5`, `37.1–37.5`, `59.1–59.3`.

| delta (Bombay − corpus max verse) | sargas |
|---|---:|
| −14 | 2 |
| −7 … −1 | 12 |
| 0 (identical) | **11** |
| +1 … +5 | 35 |
| +6 … +10 | 19 |
| +11 … +18 | 21 |

The shape is philologically coherent rather than noisy: the vulgate runs longer than the
critical text almost everywhere (mean +4.7), which is exactly what a critical edition that
excises secondary material should produce. It is also exactly why an offset cannot work —
the excess is per-sarga and unpredictable, not a constant.

## What was shipped instead

1. **[`src/ramayana_bombay_inventory.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_bombay_inventory.tsv)** —
   the Bombay structural inventory for **all 7 kāṇḍas**, 658 sargas: `kanda sarga
   n_verses volume page_first page_last ipage_first ipage_last flags`. Read off the
   [ramayanabom](https://github.com/sanskrit-lexicon-scans/ramayanabom) scan-viewer's
   hand-made per-page index (`app1/pywork/indexv{1,2,3}.txt` @ `841764ad`), **no OCR**.
   Same shape as the Gorresio inventory H1656 built, and the artifact that makes a future
   OCR pass cheap rather than exploratory.
2. **`build-bombay`** in [`build_ramayana_concordance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py)
   — rebuilds the inventory and re-runs the numbering study, so every number above is one
   command away from re-derivation:
   `python src/build_ramayana_concordance.py build-bombay --index-dir <ramayanabom>/app1/pywork`
3. **A retyped miss** in [`citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py):
   kāṇḍas 4/6/7 return `ru-translation-unpublished` with a `blocker` field naming the
   kāṇḍa, instead of sharing `locus-not-in-corpus` with genuine coverage holes. Plain `R.`
   book 7 now lands there too (it previously fell through the same branch but under the
   misleading reason). Five selftest checks pin it, one of them an out-of-range sarga.
4. **Nine selftest checks** over the inventory, including the two that make the verdict
   non-regressible: *111 consecutive sargas* and *exceeds the corpus by 11*.

## Scan-side findings for whoever does eventually OCR this

Recorded in full as [FINDINGS §480](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md);
in short, the Gorresio recipe (§470/§473) does **not** transfer unmodified:

- **The text layer is a decoy.** `page.get_text()` returns ~1,100–2,300 chars per page — and
  every one of them is Latin garbage (`*kitihtell18.1b1,1111qhMakkhd-lie Ifkkt12111414A`),
  a Latin-alphabet OCR of Devanagari. §470's check must test the **script**, not the
  byte count.
- **Never extract the embedded image here.** Each `ram-III-NNN.pdf` is 1128×420 pt
  (pothi/landscape) but embeds a **2-up** 4700×3500 scan that the PDF *crops in half*.
  §473's "take the largest image by pixel area" returns two pages at once. Render the
  page (`get_pixmap(dpi=300)` is native resolution) instead.
- **Page numbering is clean**: `ram-III-NNN.pdf` **is** printed page N, offset 0, verified
  visually at p. 505 (uttarakāṇḍa incipit, `śrīgaṇeśāya namaḥ ॥ prāptarājyasya rāmasya…`)
  and p. 810. The `ipage` column is the printed folio and **restarts at 1 for kāṇḍa 7**
  inside vol III — a naive page→folio map is ~250 folios out.
- **Three zones per page, all verse-numbered.** Small-font commentary above and below the
  large-font mūla, each carrying its own `॥N॥`. A whole-page `॥N॥` split multiplies the
  verse count several-fold — measured on the rendered pages, 14 markers whole-page vs 3
  in the height-filtered mūla band (p. 600) and 22 vs 1 (p. 700). Neither figure is the
  truth: the mūla band itself is under-recalled, because `--psm 6` merges lines across
  zones on this wide layout, so a word-height filter cuts real mūla lines as readily as
  commentary. Zone segmentation is unsolved here and is the real cost of the pass.
- **Colour vs bilevel pages differ**: most pages embed DeviceGray/JBIG2 at 4700×3500, but
  some (incl. p. 505) embed a sepia DeviceRGB JPEG at half that; those OCR to nothing
  without binarisation.

## Index defects found upstream (ramayanabom)

- **`app1/pywork/index.txt` is not the Rāmāyaṇa index.** It is Śatapatha-brāhmaṇa template
  residue — 14 kāṇḍas, `brāhm.`/`kaṇḍikā` columns — left from the app this one was cloned
  from. The live files are `indexv1/2/3.txt` (as `readme.txt` says). A session that reads
  the obvious filename gets a different work's index with no error.
- **The last uttarakāṇḍa sarga is typed `11` where `111` is meant** (pages 810–812, verses
  1–11), colliding with the genuine sarga 11 at pages 538–541. Page 810's colophon reads
  `इत्यार्षे … दशाधिकशततमः सर्गः ॥ ११० ॥` and the mūla under it restarts at `॥१॥`, so the
  block is the 111th and last. Repaired explicitly in the builder
  (`BOM_INDEX_REPAIRS`, flag `index_typo_111`) and asserted in selftest.
- **Kāṇḍa 6 in `indexv3.txt` reaches sarga 130 with 70, 122 and 123 absent** (127 present
  against the vulgate's 128). Out of scope for book 7 — **observed, not repaired**; anyone
  keying book-6 work off this inventory must resolve it first.

> **Counting correction, 27-07-2026 (same day).** The first pass reported 1,781 plain
> `R.` book-7 citations out of 39,845. Its abbreviation regex ended in a bare `R\.`
> alternative, so `R. ed. Bomb.` and `R. SCHL.` fell into the plain-`R.` bucket — 16
> book-7 refs, 623 across all books. Re-counted with every edition qualifier split out:
> **1,765 plain of 39,222**. The 127 out-of-range figure and every conclusion are
> unchanged. Worth keeping in view separately: PWG carries **319** explicit
> `R. ed. Bomb.` citations across all books (only 14 of them in book 7), so Böhtlingk
> names the Bombay edition well outside the book-7 default.

## Reproduce

```sh
python RussianTranslation/src/build_ramayana_concordance.py build-bombay \
    --index-dir <ramayanabom clone>/app1/pywork
python RussianTranslation/src/build_ramayana_concordance.py selftest
python RussianTranslation/src/citation_tm.py selftest
```

## What would change this verdict

One thing only: **a Russian Uttarakāṇḍa**. On the day one is translated and ingested, the
work queues in this order — (1) ingest the RU against the *vulgate* numbering PWG actually
cites, not the critical one currently in the corpus file; (2) OCR the 308 Bombay pages
(505–812) per the notes above, zone segmentation first; (3) build the verse concordance
against whichever Sanskrit the translation follows. Step 1 decides whether steps 2–3 are
needed at all — if the translator works from the vulgate, `R. 7` resolves directly.

_Dr. Mārcis Gasūns_
