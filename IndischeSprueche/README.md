# Indische Sprüche (Böhtlingk)

_Created: 03-07-2026 · Last updated: 03-07-2026_

## ⚠️ Read this first: canonical editions live elsewhere

Otto von Böhtlingk published **Indische Sprüche** in two editions, and **both
are already fully digitized, canonical, and live** in the org — this directory
is a secondary, offline-convenience mirror of one of them, not the source of
record:

| Edition | Repo | Sayings | Live per-verse URL |
|---|---|---:|---|
| 1st ed. (1863–5, 3 vols.) | [`sanskrit-lexicon-scans/boesp1`](https://github.com/sanskrit-lexicon-scans/boesp1) | 5,419 | `app1/?N` — PDF source courtesy **Mārcis Gasūns** |
| 2nd ed. (1870–73, 3 vols.) | [`sanskrit-lexicon-scans/boesp2`](https://github.com/sanskrit-lexicon-scans/boesp2) | 7,613 | `web1/boesp.html?verse=N` — digitized by Thomas Malten |

Both dictionaries cite this collection internally as `Spr. N`, and **that
citation crosswalk is already shipped**, not an open task: see
[`sanskrit-lexicon/PWG#87`](https://github.com/sanskrit-lexicon/PWG/issues/87)
(closed 2026-05-06). `csl-orig/v02/pwg/pwg.txt` already carries 10,366
`<ls>`-wrapped `Spr.` citations (6,666 distinct `Spr. N` occurrences; PWK's
`pwkvn.txt` carries 138), distinguishing 1st-ed. (`Spr. N`) from 2nd-ed.
(`Spr. (II) N`) references, and `csl-websanlexicon`'s `basicadjust.php`
already generates the live hrefs. **The 1st edition is the one PWG actually
cites**, per the issue title — do not assume `Spr. N` resolves against the
2nd-edition data below.

[Uprava H143](https://github.com/gasyoun/Uprava/blob/main/handoffs/H143_pwg_pwk_indische_sprueche_crosswalk.md)
was minted to build this crosswalk from scratch and **retracted the same day**
once the above was found — a genuine prior-art miss (the search that led here
never checked `funderburkjim`'s personal repos or the `sanskrit-lexicon-scans`
org). Kept as a retraction record, not an active task.

## What this directory actually is

Otto von Böhtlingk's 2nd-edition **Indische Sprüche** (St. Petersburg,
1870–1873, 3 vols.) — 7,537 Sanskrit gnomic verses / subhāṣitas (the official
count is 7,613; see the discrepancy note below), each given in Devanāgarī, his
own German translation, a source citation to the original text (epic,
dramatic, or gnomic anthology), and critical-apparatus notes on variant
readings. Public domain (Böhtlingk d. 1904).

Its only real value over `boesp2`'s live site: `boesp2` serves one verse per
page-load with no bulk export, so this JSONL is useful for offline/bulk local
queries. It is **not more authoritative** than `boesp2` — `boesp2` comes from
Thomas Malten's direct digitization; this JSONL comes from a Russian-team
Excel transcription (`Subhash_Bt.xlsx`) of unclear proofing rigor, and its
7,537 count is 76 short of `boesp2`'s verified 7,613 (likely a gap or merged
entries in the underlying spreadsheet — not independently re-verified against
the scans here).

## Provenance

```
VisualDCS/non-derived/Sanskritskie-izrecheniya/Subhash_Bt.xlsx   (digitized workbook)
    -> VisualDCS/src/DCS-data-2026/import_archive.py `subhashita` cmd (D4)
    -> VisualDCS/src/DCS-data-2026/archive.sqlite, table `subhashita`
    -> VisualDCS/src/DCS-data-2026/export_subhashita_jsonl.py
    -> data/indische_sprueche.jsonl  (this directory)
```

Regenerate with:

```sh
cd VisualDCS/src/DCS-data-2026
python export_subhashita_jsonl.py
```

**Excluded on purpose:** the `subhashita_ramayana` table (source: the "Btlnk,
Ram, Mh" workbook sheet) pairs subhāṣita rows with Rāmāyaṇa verses + Russian
translation, but the pairing looks positional/sequential rather than a genuine
cross-reference from Böhtlingk's own apparatus — it is a separate artifact, out
of scope for this edition, and not exported here.

**10 curated, hand-verified verses** (clean anuṣṭubh, metrically scanned) were
already imported separately into [`SanskritKaraoke/verses/data/`](https://github.com/gasyoun/SanskritKaraoke/tree/main/verses/data)
by [`SanskritKaraoke/tools/import_subhashita.py`](https://github.com/gasyoun/SanskritKaraoke/blob/main/tools/import_subhashita.py)
for the karaoke text-only feed — that subset is a curated derivative of the
full corpus here, not a duplicate source.

## Data

[`data/indische_sprueche.jsonl`](data/indische_sprueche.jsonl) — 7,537 records,
one per line:

```json
{
  "num": 1249,
  "saying_id": "Saying 1249",
  "page": "1.237",
  "deva": "उद्यमेन हि सिध्यन्ति कार्याणि न मनोरथैः।/नहि सुप्तस्य सिंहस्य प्रविशन्ति मुखे मृगाः॥",
  "iast": "udyamena hi sidhyanti kāryāṇi na manorathaiḥ |/nahi suptasya siṃhasya praviśanti mukhe mṛgāḥ ||",
  "translation_de": "Durch Anstrengung kommen ja Werke zu Stande, nicht durch Wünsche: ...",
  "source_attribution": "1249) Pañcatantra / Hitopadeśa ...",
  "notes": "critical-apparatus / variant-reading notes, or null"
}
```

`num` is the running Sprüche number — the same number cited in PWG/PWK as
`Spr. N`, and in secondary literature as "Böhtlingk, Spr. N" or "IndSpr N".

## Rights

Sanskrit text and Böhtlingk's German translation: public domain (author
d. 1904). No modern translation is included or implied.

---

_Dr. Mārcis Gasūns_
