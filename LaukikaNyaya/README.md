# Laukika-nyāya (Jacob's "Handful of Popular Maxims")

_Created: 13-07-2026 · Last updated: 13-07-2026_

## Status: partial ingest — 151 of the ≥400-record target, honestly short

This directory delivers a genuine, non-fabricated OCR ingest of Colonel
G. A. Jacob's *Laukika-nyāyāñjaliḥ* ("A Handful of Popular Maxims Current
in Sanskrit Literature") — the canonical laukika-nyāya (popular-maxim)
collection named in the
[2004 AIOC-Varanasi manifesto](https://github.com/gasyoun/Uprava/blob/main/history/PROGRAMME_ORIGIN_AIOC_VARANASI_2004.md)
bibliography item №41, mirroring the
[`IndischeSprueche/`](https://github.com/gasyoun/SanskritLexicography/tree/master/IndischeSprueche)
pattern. It closes the last-open 2004-manifesto deliverable
("Сентенции и афористические цитаты") **partially** — see below for exactly
what is and is not done, per
[Uprava H803](https://github.com/gasyoun/Uprava/blob/main/handoffs/H803-Sonnet_SanskritLexicography_laukika-nyaya-jacob-ingest_12.07.26.md).

**Why this is partial, not the full ≥400 the handoff asked for:** Jacob
published the collection in three parts ("handfuls," 1907/1909/1911). Only
**one** archive.org scan (identifier
[`YKTn_a-handful-of-popular-maxims-vol-1-...`](https://archive.org/details/YKTn_a-handful-of-popular-maxims-vol-1-collected-by-colonel-g-a-jacob-1907-tukaram-javaji-bombay),
digitized by Siddhanta eGangotri Gyaan Kosha) turned out to have OCR clean
enough to extract structured entries from — and it turned out, on inspection,
to bind **all three** handfuls together, not just the first. The two other
standalone archive.org uploads of the individual handfuls have OCR too
degraded to use (see "Known limitations" below). The extraction script found
**151 genuine entries** across all three parts combined from this one
source; reaching ≥400 requires either a better-OCR'd source for the
same three parts or genuine page-image (vision) OCR of the scan — both
flagged as follow-up, not attempted to fake by inflating the count.

## Rights

**Public domain.** Jacob died 1918; all three parts were published
1907–1911 (2nd ed. of Part 1 shown here is 1907) → out of copyright
worldwide. The source scan itself is marked CC-0 by its digitizer
("CC-0. Prof. Satya Vrat Shastri Collection", stamped on every page in the
OCR text). No permission gate applies (contrast the Mayrhofer KEWA/EWA
rights gate elsewhere in this org).

## Provenance

```
archive.org item YKTn_a-handful-of-popular-maxims-vol-1-collected-by-colonel-g-a-jacob-1907-tukaram-javaji-bombay
  ("A Handful Of Popular Maxims Vol 1 ... 1907 - Tukaram Javaji Bombay", 360 scanned pages,
   digitized by Siddhanta eGangotri Gyaan Kosha, CC-0)
    -> _djvu.txt OCR text derivative (downloaded 13-07-2026)
    -> raw/jacob_1907-1911_archiveorg_djvu.txt   (committed here verbatim, for audit trail)
    -> tools/build_laukika_nyaya.py              (extraction + IAST/SLP1 transcode via sanskrit-util)
    -> data/laukika_nyaya.jsonl                  (this directory's output, 151 records)
```

Regenerate with:

```sh
cd LaukikaNyaya/tools
python build_laukika_nyaya.py
```

Requires the sibling [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util)
repo checked out next to this one (`GitHub/sanskrit-util/py`) — used for
`deva_to_iast` / `deva_to_slp1`, per the org's "never re-type the SLP1 table"
rule. No new transliteration logic was written.

### The scan actually contains all three "handfuls" — a real find, not the plan

The handoff's own framing ("OCR one volume ... stop after the first full
volume") assumed one archive.org item = one handful. On inspection, this
single item's OCR text contains three internal title pages
(`ठोकिकन्यायाञ्ञलिः ॥ प्रथमो भागः ॥` / `हितीयो भागः ॥ A SECOND HANDFUL...` /
`तृतीयो भागः ॥ A THIRD HANDFUL...`), so it is actually a bound reprint of
**all three** parts under one consistent OCR pass. The section boundaries
were found by grepping the raw OCR text for these markers and are hard-coded
in `build_laukika_nyaya.py`:

| Part | OCR line range | Entries extracted |
|---|---:|---:|
| First Handful (2nd ed., 1907) | 807 – 3548 | 42 |
| Second Handful (1909) | 3549 – 8664 | 57 |
| Third Handful (1911) | 8665 – end | 52 |
| **Total** | | **151** |

## Data

[`data/laukika_nyaya.jsonl`](data/laukika_nyaya.jsonl) — 151 records, one per
line, mirroring the IndischeSprueche field style:

```json
{
  "num": 1,
  "nyaya_deva": "अजाकृपाणीयन्यायः",
  "nyaya_iast": "ajākṛpāṇīyanyāyaḥ",
  "nyaya_slp1": "ajAkfpARIyanyAyaH",
  "gloss_en": "The maxim of the she-goat and the sword.",
  "explanation": "It is founded on some story of a goat's being suddenly killed by accidental contact with a sword ...",
  "source": "Jacob, A Handful of Popular Maxims, 2nd ed., Bombay (Tukaram Javaji / Nirnaya-Sagara Press), 1907 (First Handful)",
  "_ocr_line": 807,
  "_headword_tier": "named"
}
```

- `nyaya_deva` / `nyaya_iast` / `nyaya_slp1` — the maxim's coined name (or,
  for the 4 `"phrase"`-tier entries, its own quoted Sanskrit opening) in
  Devanāgarī, IAST, and SLP1.
- `explanation` — Jacob's own note, lightly cleaned (de-hyphenated,
  digitization-credit boilerplate stripped) but **not otherwise rewritten**;
  OCR noise in the Sanskrit quotations Jacob himself cites is left as-is.
- `source` — **edition/part-level citation only, deliberately without a
  page number** — see "Known limitations" below for why.
- `_ocr_line` — internal, non-citable: the line offset into
  `raw/jacob_1907-1911_archiveorg_djvu.txt` where the entry's headword was
  found, kept so a future correction pass can re-locate the exact source
  text without re-running the whole extraction.
- `_headword_tier` — `"named"` (147 records, headed by a coined "X-nyāya"
  compound) or `"phrase"` (4 records, headed by the maxim's own quoted
  Sanskrit line rather than a coined name).

## Known limitations / OCR fidelity (spot-check log)

Per the handoff's own framing ("judgment-gated on OCR fidelity"), this
section **is** the spot-check — every fixable defect found during
extraction was fixed in the parser (not hand-patched in the data); every
defect below is a genuine, left-as-found characteristic of the OCR text,
disclosed rather than silently corrected:

1. **Target count not met.** 151 of the ≥400 the handoff's stop condition
   named. See "Why this is partial" above. Root cause is source
   availability (only one of the three archive.org scans of this specific
   work has usable OCR), not extraction effort — the extractor further
   recovers a "phrase"-tier headword class (4 records) beyond the initial
   "named"-only pass specifically to close part of this gap, with limited
   effect.
2. **Per-entry page citation dropped as unreliable, not shipped wrong.**
   An automatic per-entry printed-page number was attempted (nearest
   preceding isolated digit-only OCR line) but found contaminated by
   footnote/citation numbers embedded in Jacob's own scholarly apparatus,
   which also appear as isolated bracketed numbers in the OCR text —
   producing plausible-looking but wrong low page numbers for entries
   hundreds of lines into the book. Rather than ship a wrong `p. N`, the
   citation was left at edition/part level only. The archive.org item does
   carry a `_page_numbers.json` sidecar that would give real page-to-leaf
   mapping, but every fetch attempt 500'd during this session (archive.org
   was intermittently overloaded) — a concrete, scoped follow-up.
3. **Devanagari OCR noise, left as-is (not silently corrected):**
   consonant-cluster misreads are the dominant error mode, e.g. record #2
   `अन्तदींपिकान्यायः` is almost certainly a misread of
   `अन्तर्दीपिकान्यायः` (dropped र, spurious anusvāra) and record #6
   `अहिकुण्डठन्यायः` of `अहिकुण्डलन्यायः` (ल misread as ठ). Manual review
   of ~40 individual entries against the raw OCR text (well beyond the
   nominal 20-record sample) found this class of single-character
   consonant/vowel-sign confusion in roughly **1 in 10–15 headwords** —
   consistent with the source being a 1907–1911 print scanned and OCR'd by
   a general-purpose engine, not a Sanskrit-aware one.
4. **False-positive headword lines, found and removed during parsing** (not
   present in the shipped 151): (a) mid-explanation quoted śloka couplets
   that happen to match the "isolated Devanagari line containing न्याय"
   pattern — filtered by rejecting a candidate whose next non-empty line is
   itself a matching candidate line (a couplet, not a heading); (b) the
   book's own running title (`लौकिकन्यायाञ्जलिः` and OCR variants)
   re-appearing at each of the three part-breaks — filtered by an explicit
   exclusion list plus a substring guard (`न्यायाञ्जलि` never occurs inside
   a genuine individual maxim's name).
5. **Image-level (scan) cross-check not completed this session.** The
   handoff's Definition of Done asks for a 20-record spot-check "against the
   scan" (the page images), not just the OCR text. The 118 MB source PDF
   (360 scanned pages) was downloading from archive.org for genuine visual
   cross-checking, but archive.org was intermittently returning `502`/`500`
   errors throughout this session (also seen on several sidecar-file
   fetches, item 2 above) and the download had not completed by the time
   this pass closed. What **was** done instead: extensive direct manual
   reading of the raw OCR text itself (`raw/jacob_1907-1911_archiveorg_djvu.txt`)
   against ~40 individual extracted records, catching and fixing the false
   positives in item 4. A true image-based check against the actual page
   scans is flagged as the concrete next step (below), not skipped silently.
6. **Third Handful (1911) and Second Handful (1909) standalone scans are
   unusable, confirmed not just assumed:** the separately-uploaded
   archive.org item for the Second Handful alone (`qqlv_laukika-nyaya-anjali-second-handful-...`,
   digitized by Arya Samaj Foundation Chennai) yields **zero** recoverable
   Devanagari headword lines when run through the same extraction logic —
   its Devanagari OCR is not merely noisy but essentially unrendered. The
   standalone Third Handful item (`ukZa_laukika-nyayanjali-third-handful-...`)
   has legible-ish headwords but heavily garbled English explanation text
   (large runs of digit/symbol noise where prose should be). Neither was
   used; all 151 records come exclusively from the bound-in combined scan.

## Follow-up (concrete, not "someone should look into this")

1. **Fetch and use the `_page_numbers.json` / `_hocr_pageindex.json.gz`
   sidecars** from the `YKTn_...` archive.org item (both existed in its
   metadata file list at check time, both 500'd on every fetch attempt this
   session) to add real per-entry page citations.
2. **Vision-OCR the ~209 pages of front matter/entries not yet double-checked
   against the actual scan images** — the 118 MB source PDF is a legitimate
   target; a future session should let the download complete (or fetch
   individual page images via the archive.org BookReader image API) and do
   the literal 20-record image-based spot-check the Definition of Done asks
   for.
3. **Broaden phrase-tier recall** — only 4 non-`न्याय`-headed entries were
   recovered this pass via a deliberately strict gate (exact `"The maxim
   of"` match within 3 lines). A human-reviewed relaxation of that gate
   would likely recover more of Jacob's phrase-headed entries.
4. **FEATURES_INDEX.md registration deferred** until either the ≥400 target
   or an explicit reduced-scope sign-off is reached — registering a
   dataset as a finished F-series asset while it is 38% of its own stated
   target would misrepresent it to any future consumer.

_Dr. Mārcis Gasūns_
