# Indische Sprüche (Böhtlingk)

_Created: 03-07-2026 · Last updated: 03-07-2026_

Otto von Böhtlingk's **Indische Sprüche** (2nd ed., St. Petersburg, 1870–1873,
3 vols.) — ~7,537 Sanskrit gnomic verses / subhāṣitas, each given in Devanāgarī,
his own German translation, a source citation to the original text (epic,
dramatic, or gnomic anthology), and critical-apparatus notes on variant
readings. Public domain (Böhtlingk d. 1904).

This is a **separate publication from Böhtlingk's dictionaries** (PWG, PWK) —
not part of the Cologne XML dictionary corpus — but the two are tightly linked:
both dictionaries cite this collection internally as an attestation source,
abbreviated `Spr. N` (e.g. `Spr. 1249`):

| Dictionary | `Spr. N` citation count |
|---|---|
| PWG (`csl-orig/v02/pwg/pwg.txt`) | 6,666 |
| PWK (`csl-orig/v02/pwkvn/pwkvn.txt`) | 138 |

See [`H143_pwg_pwk_indische_sprueche_crosswalk.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H143_pwg_pwk_indische_sprueche_crosswalk.md)
for the scoped follow-on that resolves those citations against this dataset.

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
