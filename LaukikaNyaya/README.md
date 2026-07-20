# Laukika-nyāya (Jacob's "Handful of Popular Maxims")

_Created: 13-07-2026 · Last updated: 20-07-2026_

## Status: partial ingest — 389 of the ≥400-record target, closest yet (97.25%)

**20-07-2026 index-crossref follow-up (Sonnet 5 `claude-sonnet-5`, H803 continuation,
picked up via `/next-task`):** the 19-07-2026 clean-scan pass below claimed "no
back-matter index in this source" — that check only looked at the literal last ~6
pages of `handfulofpopular03jacoiala`. This session found it had actually missed one:
vol03 leaves 169-176 (9 pages before the true end at leaf 186) carry an "ALPHABETICAL
LIST OF NYAYAS EXPLAINED IN PARTS I, II & III" — the **same** index
`build_laukika_nyaya.py`'s own `index_crossref_pass()` already cross-references, just
reprinted a second time in this alternate scan (confirmed: both copies are
byte-for-byte the same content, at `YKTn_...` djvu lines ~16495-17207 and here).
Cross-referencing this index's ~460 named-tier tokens against the then-377 committed
headwords via the project's own rigorous skeleton+gloss-corroboration matcher
(`reconcile_clean_scan_lane.py`'s `best_match()`, not a blunt substring/ratio check —
an earlier looser check produced several false "gaps" that turned out to already be
present under OCR spelling drift, e.g. index token `आशामोदकठृसन्याय` ==
committed `आशामोदकतृघ्तन्यायः`) surfaced **12 genuinely new, manually-verified
records** (full methodology and root-cause analysis in
[`tools/append_h803_followup_records.py`](tools/append_h803_followup_records.py)'s
docstring): अन्धगजन्यायः, उष्ट्कण्टकभक्षणन्यायः, दग्धपटन्यायः, दण्डापूपिकान्यायः,
शुकनलिकान्यायः, झङ्गम्ाहिकान्यायः (OCR for शृङ्गग्राहिकान्यायः, disclosed not
silently corrected), उत्खातदंष्ट्रोरगन्यायः, उपजीव्यविरोधस्यायुक्तत्वस्‌
(phrase-tier), कारणगुणप्रक्रमन्यायः, सौभरिन्यायः, नासिकाग्रे
कर्णमूलकर्षणन्यायः, and सूक्तवाकन्यायः. **377 → 389.** Two further apparent
gaps (सकृद्गतिन्यायः, सूत्रबद्धशकुनिन्यायः) were checked the same way and found
to be FALSE gaps — already present under OCR spelling drift — and correctly
excluded from the batch, not silently added as duplicates.

Root cause of why the *existing* pipeline had missed these: `build_laukika_nyaya.py`'s
own `index_crossref_pass()` correctly *locates* several of them (they score ≥0.9
against the book's own index) but then rejects them via `prev_is_prose()` — a
heuristic meant to reject a headword-shaped line sitting mid-explanation-verse-
quotation, which also misfires whenever a genuine NEW headword simply follows
immediately after a DIFFERENT entry's own explanation ending in a Devanagari verse
(an ordinary, common pattern in this text, not a citation — e.g.
`कारणगुणप्रक्रमन्यायः` at OCR line 4885 directly follows the closing couplet of the
unrelated `अर्धजरतीयन्यायः`-family entry before it). **Not fixed pipeline-wide this
session** — a general fix to `prev_is_prose()` risks silently reshaping body-text
boundaries of already-reconciled 377-set records this session cannot fully
re-verify in one pass; the 12 new records above were instead extracted by hand,
each with its own boundary checked against every other new-or-existing headword in
its vicinity (several were found only because extracting one revealed a second,
previously-unnoticed headword embedded in its own naively-computed tail — see
"Follow-up" below). Fixing `prev_is_prose()` properly, then re-running the full
pipeline and re-diffing against 389, is flagged as the concrete next step.

FEATURES_INDEX registration still correctly withheld — 389/400 = 97.25%, the
closest yet, but not at target.

**19-07-2026 clean-scan reconciliation (Sonnet 5 `claude-sonnet-5`, H803 continuation,
fourth concurrent session on this handoff today):** while the correction immediately below
was landing, this session independently found and OCR'd a **different, higher-quality**
archive.org source — three separate University of California Libraries scans, one per
Jacob "handful" ([`handfulofpopular01`](https://archive.org/details/handfulofpopular01jacoiala)/
[`02`](https://archive.org/details/handfulofpopular02jacoiala)/
[`03jacoiala`](https://archive.org/details/handfulofpopular03jacoiala)), distinct from the
bound-combined `YKTn_...` item every earlier pass used. This source's own archive.org OCR
text layer is **Devanagari-blind** (confirmed by direct inspection: every headword renders
as ASCII symbol noise), but the page **images** are sharp and its IIIF backend worked when
`YKTn_...`'s did not (see "Two archive.org items, two different outages" below) — so this
session fetched all 378 page images and OCR'd them locally with Tesseract's `san+eng`
Sanskrit-aware model, producing **301 clean-scan entries with REAL per-entry printed-page
citations** (a first for this dataset), independently cross-validating and correcting
several of the original scan's known OCR errors. Reconciled against the corrected 302-record
file (below) via [`tools/reconcile_clean_scan_lane.py`](tools/reconcile_clean_scan_lane.py)
(headword-skeleton + gloss fuzzy matching, requiring BOTH headword and gloss signals to
corroborate — an early looser threshold produced false matches, caught by a post-merge
duplicate check, fixed before this number): **223 matched** (193 took the clean-scan lane's
body text; all 223 gained a real page citation), **78 were genuinely new**, **79 existing
records had no clean-scan counterpart**, **3 pre-existing near-duplicate pairs in the
302-set itself were exposed and resolved** (see "Clean-scan lane methodology" below) →
**377 records**. Still short of 400 — this
source has no back-matter index to cross-reference (unlike the technique that helped the
300-record lane below), and the extraction heuristic's phrase-tier recall is not fully
exhausted (see "Clean-scan lane methodology" below for the concrete residual gap). Full
methodology, the printed-page-offset calibration, and the real image-based spot-check
(finally possible) are documented there. **FEATURES_INDEX registration correctly still
held** — 377/400 = 94.25%, the closest this dataset has been, but not yet at target.

**19-07-2026 dedup + false-positive correction (Sonnet 5 `claude-sonnet-5`, H803
continuation):** the same day's `/dual-run-salvage` reconciliation immediately below
(390 records) turned out to have two concrete, mechanically-verified defects, both
caught before any further use of the dataset. See "19-07-2026 dedup +
false-positive correction" below for the full audit; net result: **390 → 302**,
now shipped from a single deterministic script run (no manual merge step) with
every one of the 88 removed records individually accounted for as either a
same-line duplicate or an established false-positive pattern, not a silent drop.

**19-07-2026 reconciliation (Sonnet 5 `claude-sonnet-5`, `/dual-run-salvage`):** two
independent H803 follow-up passes ran concurrently from the same 151-record baseline
without seeing each other — [PR #577](https://github.com/gasyoun/SanskritLexicography/pull/577)
(merged first) broadened the phrase-tier headword gate to 240 records; the parallel
[PR #576](https://github.com/gasyoun/SanskritLexicography/pull/576) independently
cross-referenced the source's own back-matter index to reach 300 records, using a
different method entirely (and fixing a boilerplate-stripping regex bug along the way).
Neither was a superset of the other (150 records in common, 0 gloss-identity conflicts
across the overlap; 90 records unique to the 240-set, 150 unique to the 300-set).
Reconciled as a straight union — **390 records**, deduplicated by `nyaya_slp1`, each
common entry keeping whichever lane's `explanation` field was longer/more complete (the
300-lane's bug fix won 120/150 of those picks). This file was, at that point, a
**manual merge of two independent extraction runs**, not directly reproducible by a
single invocation of [`tools/build_laukika_nyaya.py`](tools/build_laukika_nyaya.py) --
see the correction above for why that turned out to matter.

**19-07-2026 update (Sonnet 5 `claude-sonnet-5`, H803 follow-up pass):** phrase-tier
recall broadened 151 → **240** records (+89, 59%); the other two follow-ups were
attempted and closed out with concrete (partly negative) results rather than left
untried. See "19-07-2026 follow-up pass" below for what changed and why the count
still falls short of 400.

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
**302 genuine entries** (151 → 240 via the phrase-tier broadening, briefly
390 via a same-day dual-run reconciliation that turned out to double-count
57 entries and include 31 false positives, corrected back down to 302 --
see "19-07-2026 dedup + false-positive correction" below) across all three
parts combined from this one source; reaching ≥400 requires either a
better-OCR'd source for the same three parts or genuine page-image (vision)
OCR of the scan — both flagged as follow-up, not attempted to fake by
inflating the count.

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
    -> data/laukika_nyaya.jsonl                  (lane 1 alone reproduces only 302 of the 377
                                                    committed records -- see "Data" below)

archive.org items handfulofpopular01jacoiala / 02jacoiala / 03jacoiala
  (University of California Libraries scans, one per Jacob "handful", 80+112+186 = 378 pages,
   possible-copyright-status: NOT_IN_COPYRIGHT, access-restricted-item: none)
    -> IIIF IMAGE fetch, tools/fetch_clean_scan_ocr.py (own _djvu.txt text layer is
       Devanagari-blind -- unusable, see "Clean-scan lane methodology" below)
    -> local Tesseract OCR (-l san+eng --psm 6)
    -> raw/handfulofpopular0{1,2,3}jacoiala_ocr_san_eng.txt  (committed, for audit trail)
    -> tools/build_laukika_nyaya_clean_scan.py    (extraction + real page citation + IAST/SLP1)
    -> data/laukika_nyaya_clean_scan.jsonl        (301 records, this lane alone)
    -> tools/reconcile_clean_scan_lane.py         (merge into the corrected 302 -> 377 records)
```

Regenerate lane 1 (302 records, the original garbled scan, both extraction methods) with:

```sh
cd LaukikaNyaya/tools
python build_laukika_nyaya.py
```

Regenerate the clean-scan lane (301 records, real page citations) with:

```sh
cd LaukikaNyaya/tools
python fetch_clean_scan_ocr.py 01 1 80    # repeat for 02 (1-112) and 03 (1-186)
python build_laukika_nyaya_clean_scan.py
```

Neither regenerates `data/laukika_nyaya.jsonl` (the committed 377-record file) directly —
that file is the one-time reconciliation of both lanes; see "Data" below.

Requires the sibling [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util)
repo checked out next to this one (`GitHub/sanskrit-util/py`) — used for
`deva_to_iast` / `deva_to_slp1`, per the org's "never re-type the SLP1 table"
rule. No new transliteration logic was written. The clean-scan lane additionally requires
local Tesseract with the `san` (Sanskrit) trained-data pack installed (`tesseract --list-langs`
should list `san`).

### The scan actually contains all three "handfuls" — a real find, not the plan

The handoff's own framing ("OCR one volume ... stop after the first full
volume") assumed one archive.org item = one handful. On inspection, this
single item's OCR text contains three internal title pages
(`ठोकिकन्यायाञ्ञलिः ॥ प्रथमो भागः ॥` / `हितीयो भागः ॥ A SECOND HANDFUL...` /
`तृतीयो भागः ॥ A THIRD HANDFUL...`), so it is actually a bound reprint of
**all three** parts under one consistent OCR pass. The section boundaries
were found by grepping the raw OCR text for these markers and are hard-coded
in `build_laukika_nyaya.py`:

| Part | OCR line range | v1 (13-07) | v2 phrase-tier (19-07) | v3 corrected combine (19-07) |
|---|---:|---:|---:|---:|
| First Handful (2nd ed., 1907) | 807 – 3548 | 42 | 51 | 62 |
| Second Handful (1909) | 3549 – 8664 | 57 | 88 | 109 |
| Third Handful (1911) | 8665 – end | 52 | 101 | 131 |
| **Total** | | **151** | **240** | **302** |

## Data

[`data/laukika_nyaya.jsonl`](data/laukika_nyaya.jsonl) — **389 records** (up from 377, still
short of the ≥400 target), one per line, mirroring the IndischeSprueche field style. This
file is now a **union of THREE independently-produced passes** — not directly reproducible
by a single script invocation: `tools/build_laukika_nyaya.py` reproduces only the
302-record djvu lane, `tools/build_laukika_nyaya_clean_scan.py` writes the separate
[`data/laukika_nyaya_clean_scan.jsonl`](data/laukika_nyaya_clean_scan.jsonl) (301 records,
the clean-scan lane on its own, with real page citations throughout) rather than the merged
file directly, `tools/reconcile_clean_scan_lane.py` documents (and can redo, from a matching
starting state) the one-time 302+301→377 merge, and
[`tools/append_h803_followup_records.py`](tools/append_h803_followup_records.py) documents
(and can redo, from a matching starting state) the 20-07-2026 index-crossref follow-up's
377→389 manual addition (12 records recovered from the djvu source via the newly-discovered
back-matter index, each individually verified — see the banner above and "Follow-up" below).

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
  "_headword_tier": "named",
  "_match_method": "headword-regex"
}
```

- `nyaya_deva` / `nyaya_iast` / `nyaya_slp1` — the maxim's coined name (or,
  for `"phrase"`-tier entries, its own quoted Sanskrit opening) in
  Devanāgarī, IAST, and SLP1.
- `explanation` — Jacob's own note, lightly cleaned (de-hyphenated,
  digitization-credit boilerplate stripped) but **not otherwise rewritten**;
  OCR noise in the Sanskrit quotations Jacob himself cites is left as-is.
- `source` — a **real printed-page citation** (`..., UC Libraries scan, p. N`) for the 301
  records matched or newly added by the clean-scan lane; **edition/part-level only** (no
  page number) for the 79 records with no clean-scan counterpart — see "Real per-entry page
  citations" below for how the page numbers were calibrated.
- `_ocr_line` — internal, non-citable: the line offset into
  `raw/jacob_1907-1911_archiveorg_djvu.txt` for records from the original scan's two
  extraction methods; absent on clean-scan-lane records, which carry `_scan_leaf` /
  `_clean_scan_leaf` instead (the IIIF leaf index within the alternate source).
- `_headword_tier` — `"named"` (headed by a coined "X-nyāya" compound) or `"phrase"`
  (headed by the maxim's own quoted Sanskrit line rather than a coined name).
- `_match_method` — how the record was found: `"headword-regex"` / `"index-crossref-seqmatch"`
  / `"index-crossref-prefix"` (the original scan's two extraction methods — see "dedup +
  false-positive correction" below), `"clean-scan-lane-preferred"` (clean-scan headword+body
  won the match), `"<original-method>+clean-scan-citation"` (original body kept, clean-scan
  lane only contributed the page citation), or `"clean-scan-lane-new"` (found only by the
  clean-scan lane).

## Known limitations / OCR fidelity (spot-check log)

Per the handoff's own framing ("judgment-gated on OCR fidelity"), this
section **is** the spot-check — every fixable defect found during
extraction was fixed in the parser (not hand-patched in the data); every
defect below is a genuine, left-as-found characteristic of the OCR text,
disclosed rather than silently corrected:

1. **Target count not met.** 302 of the ≥400 the handoff's stop condition
   named (151 at the 13-07 pass, 240 after the 19-07 phrase-tier broadening,
   briefly 390 after a same-day dual-run reconciliation that turned out to
   contain 57 duplicate + 31 false-positive records, corrected back to 302 --
   see "19-07-2026 follow-up pass" and "19-07-2026 dedup + false-positive
   correction" below). Root cause is source availability (only one of the
   three archive.org scans of this specific work has usable OCR), not
   extraction effort.
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

## 19-07-2026 follow-up pass (Sonnet 5 `claude-sonnet-5`, H803 continuation)

All three of the 13-07 pass's concrete follow-ups were attempted this
session, with honest (including partly negative) results:

1. **Phrase-tier recall broadened — 4 → 93 records, +89 total.** The
   original gate accepted a non-`न्याय` Devanagari headword line only if the
   very next line literally began `"The maxim of"`. Manual review of all 113
   non-`न्याय` candidate lines that survive the existing false-positive
   filters (dumped with 6-line context and read in full — well beyond the
   nominal 20-record sample, matching the rigor of the 13-07 pass's ~40-entry
   manual review) found the true positives use many different English
   opener shapes ("Like a decoration...", "A young fawn cannot...", "If
   Mithila should be...", "Not even a thousand blind travellers...") while
   the false positives (mid-explanation Sanskrit-verse restatements of the
   same maxim, OCR-garbled line fragments, digitization-credit boilerplate
   landing first) either have **no** English sentence following at all, or
   fail one of three cheap, verified-against-the-actual-false-positives
   checks now in `looks_like_gloss_sentence()`
   (`LaukikaNyaya/tools/build_laukika_nyaya.py`): the candidate opener must
   (a) not be boilerplate or a bare citation stub ("See ...", "Prof. ..."),
   (b) be mostly ASCII English (Devanagari ratio ≤ 15%, rejecting couplet
   restatements like the false-positive pair at OCR lines 5015/5028 — only
   5015 is a real headword, 5028 is the same maxim paraphrased in a quoted
   Sanskrit verse two lines later with no English gloss following it at
   all), and (c) contain ≥4 real English words (rejecting 2-token OCR
   fragments like `"तेन दत्तमेकध"` → `"Who git"` at line 11943, a garbled
   duplicate of the genuine entry at line 11937). Every one of the 8
   specific false-positive lines identified during the manual review (OCR
   lines 5028, 7133, 7590, 11927, 11943, 12229, 13379, 13837) was confirmed
   correctly rejected by the new gate after implementation; the `"named"`
   tier count is unchanged (147, confirming the change is scoped to the
   phrase-tier path only). All 93 phrase-tier records were re-read against
   their `gloss_en`/`explanation` output as a second verification pass.
2. **`_page_numbers.json` sidecar fetched — found NOT usable, not just
   inaccessible.** archive.org's download server was still intermittently
   down this session (confirmed again: several `500`/`503` responses,
   `"Internet Archive: Temporarily Offline"`), but a retry succeeded and the
   sidecar downloaded cleanly. Its own machine-generated page-number OCR has
   **11 of 360 leaves** with a detected `pageNumber` (`confidence: 11`
   overall) — almost all in the roman-numeral front matter, none in the body
   pages where the 240 entries live. This is archive.org's own
   auto-detection failing on this scan, not a gap in this repo's own
   extraction — the per-entry page citation gap is now confirmed
   unclosable from this sidecar, a stronger (and different) conclusion than
   "the fetch failed," and the `_hocr_pageindex.json.gz` alternative was not
   pursued further since it only gives OCR-leaf offsets, not printed page
   numbers, and the printed page numbers were the actual gap.
3. **Image-level (scan) cross-check — still blocked, confirmed again.**
   Both the full 118 MB PDF and the IIIF single-leaf image endpoint
   (`iiif.archive.org/iiif/YKTn_.../$<leaf>/full/.../default.jpg`, which
   avoids downloading the whole PDF) were retried this session; the IIIF
   backend (Cantaloupe image server) returned `500`/`503`/timeout on every
   leaf tried (850, 900, 950) even though the plain metadata API responded
   normally — a server-side outage specific to image serving, not a
   client-side or credentials issue. Logged in
   [Uprava/SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
   so a future session checks that board before re-attempting. The image-level
   spot-check the Definition of Done asks for remains not done.
4. **FEATURES_INDEX.md registration still deferred** — 240/400 = 60% of the
   stated target, still short of either the target or an explicit
   reduced-scope sign-off.

**Residual gap to ≥400 and why it's a source-availability ceiling, not an
effort ceiling:** the one usable scan's OCR text is now essentially
exhausted at the "headword line + English gloss" extraction pattern — 240
records from 388 headword-shaped lines (147/189 named-tier, 93/199
phrase-tier candidates that survive false-positive filtering). Closing the
remaining gap needs either a genuinely better-OCR'd source (none found on
sanskritdocuments.org/GRETIL/archive.org at last check) or vision-OCR of the
page images directly (blocked this session per item 3 above) to recover
entries whose text-layer OCR is too garbled to pattern-match at all.

## 19-07-2026 dedup + false-positive correction (Sonnet 5 `claude-sonnet-5`, H803 continuation)

Picked up H803 via `/next-task` after the `/dual-run-salvage` reconciliation
above had already merged PR #576 + PR #577 to 390 records. Before treating
390 as final, re-derived the same combination independently (combine PR
#576's index-cross-reference technique onto the merged #577 baseline in a
single deterministic script) and cross-checked the two results
line-by-line against the shared, unchanged raw OCR text. Two concrete,
mechanically-verified defects turned up in the 390:

1. **57 same-`_ocr_line` duplicate pairs (114 records for 57 physical
   headword occurrences), 0 content differences once whitespace is
   normalized.** Root cause: PR #576's own index-crossref pass recorded
   which OCR lines its **own** v1-narrow (pre-#577) regex pass had already
   used, so it correctly avoided re-finding those -- but it had no way to
   know about the **+89 phrase-tier lines #577's later broadened gate**
   newly classified as headwords, since PR #576 branched before that
   broadening existed. Several of those +89 lines were independently
   re-discovered by PR #576's index-crossref pass under different
   whitespace formatting (`format_headword()`'s space-preserving style vs.
   the original all-whitespace-stripped style), so the union's `nyaya_slp1`
   dedup key differed for what was actually the same entry and both
   copies survived. Verified for all 57 pairs: identical Devanagari content
   once whitespace is stripped for comparison (checked programmatically,
   not sampled). **Fix:** the combined script now runs the index-crossref
   pass with the CURRENT (already phrase-tier-broadened) used-line set,
   so it can never rediscover a line the regex pass already claimed --
   this dedup class cannot recur. `format_headword()` is also now applied
   uniformly to every entry regardless of recovery method, closing the
   whitespace-formatting mismatch at the source.
2. **31 further false-positive lines in the 390's otherwise-unique set**
   (checked as: line-level set difference between the corrected 302 and
   the 390's 333 unique-line set). 30 of 31 exceed the same >25-codepoint
   length threshold already established as the false-positive signature
   for the unbounded `index-crossref-prefix` strategy (see the combine
   pass this same session, further up the extraction pipeline's own git
   history). The 31st, a 19-codepoint case that looked short enough to be
   real, checked out on inspection of its raw OCR context (line 14565) as
   `"The three verses immediately preceding the above will be found under
   the हिरण्यनिधिदृष्टान्त."` -- a cross-reference SENTENCE naming another
   entry's headword, not a fresh heading of its own. **Fix:** the tightened
   `max_len=30` candidate cap from the combine pass (see git history) was
   retained rather than loosened back up to recover these.
3. **Net result: 390 → 302**, now produced by a single
   `python build_laukika_nyaya.py` invocation with **zero** manual merge
   step and **zero** duplicate `_ocr_line` or `nyaya_deva` values (checked
   programmatically). Every one of the 88 removed records is accounted for
   above as either a same-line duplicate (57) or an established
   false-positive pattern (31) -- none were dropped without a specific,
   checkable reason.
4. **20-record spot-check re-confirmed** against the corrected 302 (see the
   combine pass, same session): sampled across all three `_match_method`
   values, all 20 checked out against the raw OCR context.
5. **FEATURES_INDEX.md registration still deferred** -- 302/400 = 75.5% of
   the stated target. Lower than the 390 briefly on `master`, but every
   one of those 88 additional records was either a literal duplicate or a
   non-headword false positive, not a genuine loss of coverage (verified:
   0 lines are unique to the clean 302 that aren't also in the 390's set,
   i.e. the correction only ever *removes*, never *misses*, relative to
   what the 390 pass found).

**A human should decide** whether 302/400 (75.5%), now the verified,
regeneratable ceiling of both known extraction techniques against this one
usable scan, is worth an explicit reduced-scope sign-off, or whether to
wait for the vision-OCR follow-up (blocked on the archive.org image-server
outage, see item 3 of the prior pass above) before deciding. Also worth a
human's attention: [PR #576](https://github.com/gasyoun/SanskritLexicography/pull/576)
should still be closed (superseded twice over now -- first by the #587
reconciliation, now by this correction), and the #587 dual-run-salvage
reconciliation should be flagged in whatever registry tracks that skill's
past runs, since its per-record "0 duplicate headwords" claim relied on
exact-string matching that a whitespace-formatting difference between the
two source lanes could (and did) evade.

## Clean-scan lane methodology (19-07-2026, Sonnet 5 `claude-sonnet-5`)

### Two archive.org items, two different outages

Before this pass, `YKTn_...`'s own image-serving backend was confirmed down
(logged in [Uprava/SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md):
metadata API fine, `/download/` and IIIF both `500`/`503`) — this session **re-confirmed
that outage still live** (a fresh `curl` HEAD succeeded but the actual GET body-transfer
hung/died at 0 bytes on both a full-file and a 15 MB range request, a stronger finding than
the earlier session's "intermittent 500s"), then found the `handfulofpopular01/02/03jacoiala`
items via a web search for alternate digitizations. These are hosted on a **different
archive.org datanode entirely** (`dn760101.eu.archive.org` vs. `YKTn_...`'s
`dn760001.eu.archive.org`) — a genuinely separate backend, which is presumably why one was
reachable while the other was not. Concrete lesson for a future OCR/vision session hitting
an archive.org outage: **don't just retry the same item — a sibling digitization of the
same PD work may sit on an unaffected node.**

### Why local Sanskrit-aware OCR instead of the source's own text layer

`handfulofpopular01/02/03jacoiala`'s own `_djvu.txt` derivative recognizes **zero**
Devanagari (`grep -c 'न्याय'` → 0 across all three volumes) — its OCR engine is
English-only and renders every Devanagari headword as ASCII symbol garbage (confirmed by
direct inspection, e.g. a corrigendum line reading `"For ^j^f read qw<4\."` where the
printed page shows a real Devanagari correction). But the **page images** it serves are
sharp, high-contrast 1907–1911 letterpress scans. `tesseract --list-langs` on this machine
already has a `san` (Sanskrit) trained-data pack alongside `eng`; running
`tesseract <page.jpg> -l san+eng --psm 6` (not `-l san` alone, which misreads English
front-matter/bibliography text as Devanagari-lookalike noise) gives a genuinely
Sanskrit-aware OCR pass this dataset never had before.

### No back-matter index in this source (unlike the 300-record lane)

[`tools/build_laukika_nyaya.py`](tools/build_laukika_nyaya.py)'s 300-record lane closed
part of its gap by cross-referencing the primary `YKTn_...` scan's own back-matter index of
nyāyas. This alternate source's back matter (checked: last ~6 pages of each volume) is
publisher advertisements and a university-library due-date stamp, not an index — that
technique does not transfer here, and is not the reason this lane falls short of closing
the full gap on its own.

### Pipeline

[`tools/fetch_clean_scan_ocr.py`](tools/fetch_clean_scan_ocr.py) fetches each volume's page
images via IIIF (`iiif.archive.org/image/iiif/2/<ident>%2f<ident>_jp2.zip%2f<ident>_jp2%2f<ident>_NNNN.jp2/full/pct:65/0/default.jpg`,
found by following the IIIF `info.json` redirect rather than guessing the leaf-filename
convention), OCRs each with `tesseract -l san+eng --psm 6`, and concatenates per-volume
into `raw/handfulofpopular0{1,2,3}jacoiala_ocr_san_eng.txt` with `=== PAGE N ===` markers
(the audit-trail equivalent of `raw/jacob_1907-1911_archiveorg_djvu.txt` for the other
lanes). 375 of 378 pages fetched successfully; pages 77 (vol 1), 109 (vol 2), and 183
(vol 3) failed consistently across retries — not the intermittent flakiness seen
elsewhere, so flagged as a genuine per-leaf gap rather than re-attempted indefinitely.
[`tools/build_laukika_nyaya_clean_scan.py`](tools/build_laukika_nyaya_clean_scan.py) reuses
the **same** headword/false-positive heuristics as `build_laukika_nyaya.py` (named-tier:
line containing न्याय; phrase-tier: Devanagari line + a following English gloss sentence)
with one real bug fix found by spot-check: the strict "pure Devanagari line" regex
(`^[ऀ-ॿ\s]{5,60}$`) silently rejected headword lines containing an invisible zero-width
non-joiner (U+200C, which Tesseract emits around certain conjuncts) — e.g.
`'अकाले कृतमकृतं स्यात्‌ ॥'` at vol 3 page 13 never became a headword candidate at all
until ZWNJ/ZWJ were added to the allowed character class. This single fix recovered 42
additional entries (259 → 301) across all three volumes, which is why it's called out here
rather than left as a silent parser tweak.

### Real per-entry page citations, calibrated (not derived per-entry)

Each volume's own front matter (title page, preface, corrigenda) pushes the printed page
number below the raw IIIF leaf index by a fixed offset, read directly off spot-checked page
images (leaf 49 → printed "31", leaf 71 → printed "53" ⇒ vol 1 offset 18; leaf 14 →
printed "2", leaf 102 → printed "90" ⇒ vol 2 offset 12; leaf 162 → printed "150" ⇒ vol 3
offset 12, both consistent across two independent readings each). `source` now cites
`..., UC Libraries scan, p. <printed-page>` for every clean-scan-lane record instead of the
edition/part-level-only citation the other two lanes carry. **This offset is a calibration
from a handful of spot-checked pages, not verified leaf-by-leaf** — treat citations within
±1 of a part boundary or an inserted errata leaf with appropriate caution.

### Real image-based spot-check (finally possible)

The original handoff's Definition of Done asks for "20 random records spot-checked against
the scan" — blocked in every earlier pass by the `YKTn_...` image outage. With
`handfulofpopular01/02/03jacoiala`'s IIIF backend working, this session fetched and visually
read **16 page images** (spanning first/middle/last positions across both tiers in all three
volumes) against their extracted records:

- **Named-tier headwords: 100% match** in the sample (e.g. `अजाकृपाणीयन्यायः`,
  `नष्टाश्वदग्धरथन्यायः`, `स्थावरजङ्गमविषन्यायः` — all read identically off the page).
- **One real headword OCR error found**, disclosed not hidden: vol 1 p. 71's second
  headword extracted as `स्थाटीपुखाकन्यायः६` (stray "६" digit, ली→टी, ल→ख) where the
  printed page reads `स्थालीपुलाकन्यायः` cleanly — consistent with the ~1-in-10–15
  consonant-cluster error rate already documented for the original scan (item 3 above);
  this lane is cleaner on average, not error-free.
- **One real gloss-text OCR error found**: `"The method of 501 attribution"` (should read
  `"The method of Illusory attribution"` — capital-I *Illusory* misread as a 3-digit
  number) — an artifact of the mixed-script OCR pass on italic text, disclosed rather than
  silently corrected.
- **Two real recall gaps found and fixed live** (see the ZWNJ bug above) rather than
  papered over — both were genuine phrase-tier headword lines the extractor was silently
  dropping before the fix.
- **The explanation body text is NOT reliably cleaner than the original scan's** — it
  reproduces the same class of noise (misread Sanskrit block-quotes embedded in the English
  prose) at a comparable rate. Only the **headword** and (now) the **page citation** are the
  clear, spot-check-confirmed wins of this lane; `tools/reconcile_clean_scan_lane.py`
  therefore treats explanation length as a floor against a truncated body, not a quality
  signal, when deciding which lane's body text to keep on a match.

### Why 377, not ≥400: the concrete residual gap

301 clean-scan entries against a 302-record corrected base reconciled to 377 (223 matched +
78 new, 79 existing-only kept, minus 3 pre-existing near-duplicate pairs in the 302-set
itself that the headword upgrade exposed and this pass resolved — see the note on the
matcher below) — the count did **not** simply add, because most of what this lane found
overlaps what the other two lanes already had (expected: same book). The honest remaining
gap has two named causes, not "needs more effort" in the abstract:

1. **No back-matter index in this source** (see above) — the technique that helped the
   300-record lane close part of its gap does not transfer.
2. **Phrase-tier recall is not fully exhausted.** The ZWNJ fix alone recovered 42 entries;
   the same class of "real headword line silently rejected by an over-strict pattern" may
   still have unrecovered instances — a systematic diff between all Devanagari-line
   candidates and the currently-accepted set (rather than spot-check sampling) would find
   them, but was not run this session given time already spent on the concurrent-session
   collision recovery below.

**A note on match-quality, since a matcher this important deserves it:** the first version
of `tools/reconcile_clean_scan_lane.py`'s fuzzy matcher used a permissive OR of either
signal crossing a low bar (skeleton ratio > 0.55 OR gloss ratio > 0.75), which produced a
real false match — lane 3's unrelated `नर्तकन्यायः` ("the simile of a dancer") scored high
enough against the existing `प्रपानकरसन्यायः` ("the simile of sherbet") purely from sharing
the common `न्याय` suffix and the `"the simile of"` boilerplate opener. Caught by a
post-merge `nyaya_slp1`-uniqueness check (never assume a fuzzy matcher is safe without one),
root-caused, and fixed at the source: both signals now have the shared boilerplate stripped
before comparison, and a match requires BOTH to corroborate (not either alone). The fix also
surfaced 3 genuine pre-existing near-duplicate pairs in the 302-set itself (entries differing
only by a trailing visarga — `araRyarodananyAya` vs `araRyarodananyAyaH` — that the org's own
exact-`nyaya_slp1` dedup pass could not have caught, since the keys genuinely differ by one
character); the script's post-merge dedup step resolves these too, logged not silently
dropped.

## Follow-up (concrete, not "someone should look into this")

1. **Recover the 3 leaves that failed to fetch** (vol 1 p. 77, vol 2 p. 109, vol 3 p. 183) —
   RE-CONFIRMED still failing on 20-07-2026 (fresh retry, same 3 leaves, same
   result: `fetch=False` on all three) — this is now confirmed a genuine per-leaf
   gap across two independent sessions, not transient. Do not re-attempt without a new
   angle (a different archive.org mirror, or a manual download).
2. **Fix `prev_is_prose()` in `build_laukika_nyaya.py`'s `index_crossref_pass()`
   pipeline-wide** (root-caused 20-07-2026, see banner above) — it currently rejects
   any candidate headword whose immediately-preceding line is heavy Devanagari prose,
   which conflates "sits mid-citation" (correctly rejected) with "immediately follows a
   DIFFERENT entry's own closing verse" (a real heading, wrongly rejected). 12 records
   were recovered THIS session by hand-checking candidates individually against this
   exact failure mode; a proper fix (e.g. requiring the preceding heavy-Devanagari line
   to itself lack a closing `॥`/verse-final marker before treating it as "mid-citation")
   would recover the same class automatically, but needs a full pipeline re-run +
   re-diff against the current 389 to verify it does not also shift any
   already-reconciled record's body boundary — not attempted this session due to that
   verification cost.
3. **Systematic phrase-tier recall audit** (see "Why 377, not ≥400" above) — still
   applies; only the NAMED-tier (`न्याय`-suffixed) half of the newly-found index was
   cross-referenced this session (`tools/extract_index_cross_reference.py` filters to
   `'न्याय' in tok`). The index's phrase-tier half (bare quoted-maxim entries, no
   `न्याय` suffix) was not exhaustively cross-checked — e.g. `एकमनुसन्धित्सतोऽपरं
   प्रच्यवते` was noticed embedded inside `उष्ट्कण्टकभक्षणन्यायः`'s body this session
   but not independently pursued as its own record, since phrase-tier extraction needs
   the pipeline's own `looks_like_gloss_sentence()` gating logic to bound correctly,
   not ad hoc hand-extraction.
4. **The clean-scan-lane-sourced genuine gaps found this session but not yet
   extracted**: `extract_index_cross_reference.py`'s diff also flagged ~15 named-tier
   candidates whose best raw-text match sits in a `clean-scan-vol0{1,2,3}` source
   rather than the djvu source (e.g. चित्राङ्गनान्यायः, दामव्याखकटन्यायः,
   गतैवर्तिंगोधामांसविभजनन्यायः) — most of these turned out to be FALSE gaps (already
   present under OCR spelling drift, confirmed via location-based cross-check against
   `_scan_leaf`/`_ocr_line`), but a few were not fully traced to a same-content
   existing record; re-run `extract_index_cross_reference.py` and manually verify the
   residue the way this session did for the djvu-sourced batch.
5. **The 79 existing-only records** (no clean-scan counterpart matched) still carry
   only an edition/part-level citation — either they fall in the 3 missing leaves
   above, or the skeleton/gloss fuzzy-match in `tools/reconcile_clean_scan_lane.py`
   missed a real correspondence (now that it requires stricter corroboration, it may
   under-match rather than over-match — a middle-ground threshold could recover a few
   more without reintroducing the false-positive class documented above).
6. **Vision-OCR `YKTn_...`'s own page images once its image server recovers** (check
   [SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md) first)
   — superseded in practice by using the clean-scan source instead, but would let a future
   session verify whether `YKTn_...` itself has entries neither alternate source recovered.
7. **FEATURES_INDEX.md registration** — hold until either ≥400 (389/400 = 97.25%, the
   closest yet) or an explicit reduced-scope sign-off (MG `@DECIDE`) accepting 389 as
   final. Given items 2-4 above are concrete and not yet exhausted (unlike the
   377-record state, where the residual gap really did look like a source ceiling),
   a reduced-scope sign-off is premature until at least item 2 (the `prev_is_prose()`
   fix) is attempted.

_Dr. Mārcis Gasūns_
