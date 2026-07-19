# Laukika-nyāya (Jacob's "Handful of Popular Maxims")

_Created: 13-07-2026 · Last updated: 19-07-2026_

## Status: partial ingest — 390 of the ≥400-record target, honestly short

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
300-lane's bug fix won 120/150 of those picks). This file is now a **manual merge of two
independent extraction runs**, not directly reproducible by a single invocation of
[`tools/build_laukika_nyaya.py`](tools/build_laukika_nyaya.py) — re-running it reproduces
only one lane's subset. Full record-by-record accounting in the PR that landed this merge.

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
**240 genuine entries** (up from 151 after the 19-07-2026 phrase-tier
broadening below) across all three parts combined from this one source;
reaching ≥400 requires either a better-OCR'd source for the same three parts
or genuine page-image (vision) OCR of the scan — both flagged as follow-up,
not attempted to fake by inflating the count.

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
    -> data/laukika_nyaya.jsonl                  (this directory's output, 240 records)
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

| Part | OCR line range | Entries (v1, 13-07) | Entries (v2, 19-07) |
|---|---:|---:|---:|
| First Handful (2nd ed., 1907) | 807 – 3548 | 42 | 51 |
| Second Handful (1909) | 3549 – 8664 | 57 | 88 |
| Third Handful (1911) | 8665 – end | 52 | 101 |
| **Total** | | **151** | **240** |

## Data

[`data/laukika_nyaya.jsonl`](data/laukika_nyaya.jsonl) — 240 records, one per
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
  for the 93 `"phrase"`-tier entries, its own quoted Sanskrit opening) in
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
  compound) or `"phrase"` (93 records, headed by the maxim's own quoted
  Sanskrit line rather than a coined name — see "19-07-2026 follow-up pass"
  below for how this tier grew from 4 to 93).

## Known limitations / OCR fidelity (spot-check log)

Per the handoff's own framing ("judgment-gated on OCR fidelity"), this
section **is** the spot-check — every fixable defect found during
extraction was fixed in the parser (not hand-patched in the data); every
defect below is a genuine, left-as-found characteristic of the OCR text,
disclosed rather than silently corrected:

1. **Target count not met.** 240 of the ≥400 the handoff's stop condition
   named (151 at the 13-07 pass, 240 after the 19-07 phrase-tier broadening —
   see "19-07-2026 follow-up pass" below). Root cause is source availability
   (only one of the three archive.org scans of this specific work has usable
   OCR), not extraction effort.
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

## Follow-up (concrete, not "someone should look into this")

1. **Vision-OCR the page images once archive.org's image server recovers**
   (check [SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
   first) — either the full 118 MB PDF or per-leaf IIIF fetches — and do the
   literal 20-record image-based spot-check the Definition of Done asks for.
2. **A genuinely OCR-garbled-text recovery pass** (vision-OCR or a
   Sanskrit-aware OCR re-run of the same scan) is now the only remaining
   lever for further count growth from this source; the pattern-matching
   extraction approach is exhausted (see "Residual gap" above).
3. **FEATURES_INDEX.md registration** — hold until either ≥400 or an
   explicit reduced-scope sign-off (MG `@DECIDE`) accepting 240 (60%) as the
   final count given the confirmed source ceiling.

_Dr. Mārcis Gasūns_
