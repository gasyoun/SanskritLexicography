# Laukika-nyāya (Jacob's "Handful of Popular Maxims")

_Created: 13-07-2026 · Last updated: 19-07-2026_

## Status: partial ingest — 302 of the ≥400-record target, honestly short

**19-07-2026 combine pass (Sonnet 5 `claude-sonnet-5`, H803 continuation):** two
independent concurrent sessions had each continued this handoff the same minute —
[PR #577](https://github.com/gasyoun/SanskritLexicography/pull/577) (merged,
phrase-tier broadening, 151→240) and
[PR #576](https://github.com/gasyoun/SanskritLexicography/pull/576) (left open,
conflicting, an independent index-cross-reference recovery technique reaching
151→300 plus a genuine bug fix). This pass combined both techniques on top of
current master rather than picking one: 240 → **302** records (+62, 20%). See
"19-07-2026 combine pass" below for the merge, the QA finding that caught a
real false-positive class in the naively-ported technique, and why the count
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
**302 genuine entries** (151 → 240 via the phrase-tier broadening, then
240 → 302 via the combined index-cross-reference recovery pass, both below)
across all three parts combined from this one source; reaching ≥400 requires
either a better-OCR'd source for the same three parts or genuine page-image
(vision) OCR of the scan — both flagged as follow-up, not attempted to fake
by inflating the count.

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
    -> data/laukika_nyaya.jsonl                  (this directory's output, 302 records)
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

| Part | OCR line range | v1 (13-07) | v2 phrase-tier (19-07) | v3 combined (19-07) |
|---|---:|---:|---:|---:|
| First Handful (2nd ed., 1907) | 807 – 3548 | 42 | 51 | 62 |
| Second Handful (1909) | 3549 – 8664 | 57 | 88 | 109 |
| Third Handful (1911) | 8665 – end | 52 | 101 | 131 |
| **Total** | | **151** | **240** | **302** |

## Data

[`data/laukika_nyaya.jsonl`](data/laukika_nyaya.jsonl) — 302 records, one per
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
- `source` — **edition/part-level citation only, deliberately without a
  page number** — see "Known limitations" below for why.
- `_ocr_line` — internal, non-citable: the line offset into
  `raw/jacob_1907-1911_archiveorg_djvu.txt` where the entry's headword was
  found, kept so a future correction pass can re-locate the exact source
  text without re-running the whole extraction.
- `_headword_tier` — `"named"` (182 records, headed by a coined "X-nyāya"
  compound) or `"phrase"` (120 records, headed by the maxim's own quoted
  Sanskrit line rather than a coined name — see "19-07-2026 follow-up pass"
  below for how this tier grew from 4 to 93, then "19-07-2026 combine pass"
  below for the further growth to 120).
- `_match_method` — how the record was found: `"headword-regex"` (240,
  the original regex pass, phrase-tier broadened per the 19-07 follow-up),
  `"index-crossref-seqmatch"` (53, new in the combine pass) or
  `"index-crossref-prefix"` (9, new in the combine pass) — see "19-07-2026
  combine pass" below.

## Known limitations / OCR fidelity (spot-check log)

Per the handoff's own framing ("judgment-gated on OCR fidelity"), this
section **is** the spot-check — every fixable defect found during
extraction was fixed in the parser (not hand-patched in the data); every
defect below is a genuine, left-as-found characteristic of the OCR text,
disclosed rather than silently corrected:

1. **Target count not met.** 302 of the ≥400 the handoff's stop condition
   named (151 at the 13-07 pass, 240 after the 19-07 phrase-tier broadening,
   302 after the same-day 19-07 combine pass — see "19-07-2026 follow-up
   pass" and "19-07-2026 combine pass" below). Root cause is source
   availability (only one of the three archive.org scans of this specific
   work has usable OCR), not extraction effort.
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

## 19-07-2026 combine pass (Sonnet 5 `claude-sonnet-5`, H803 continuation)

Two independent concurrent Sonnet 5 sessions both continued this handoff in
the same minute (both PRs opened 09:18:12Z 19-07-2026), neither aware of the
other:

- [PR #577](https://github.com/gasyoun/SanskritLexicography/pull/577)
  (**merged** — the "19-07-2026 follow-up pass" above): 151→240 via the
  phrase-tier broadening + `_page_numbers.json`/image-cross-check follow-ups.
- [PR #576](https://github.com/gasyoun/SanskritLexicography/pull/576) (left
  open, then conflicting against the new master): 151→300 via a different,
  complementary technique — cross-referencing the OCR text's own back-matter
  "ALPHABETICAL LIST OF NYAYAS EXPLAINED IN EACH PART" (~458 entries) to
  recover headword occurrences the regex pass misses because of stray OCR
  noise around an otherwise-legible line, plus a genuine bug fix (the
  original `BOILERPLATE` regex's unanchored trailing `.*`, applied to a
  whole joined explanation string, silently truncated any entry whose OCR
  window happened to contain a mid-body digitization-credit stamp).

Per the handoff's own registry note, this pass rebased #576's technique onto
the merged #577 baseline and **combined both** rather than picking one --
the two recovery mechanisms are additive (broadened-regex catches
noise-*free* phrase headwords the original strict regex skipped;
index-crossref catches noise-*damaged* headword lines the regex can never
match at all), carrying the boilerplate bug fix forward for every entry:

1. **Naive port of #576's index-crossref pass onto the 240-baseline: 240 →
   341** (index-crossref-seqmatch: 53, index-crossref-prefix: 48).
2. **QA caught a real false-positive class before shipping, not after.** A
   length-by-method audit (`_match_method` was added specifically to make
   this auditable) showed `index-crossref-seqmatch` was clean (median
   headword length 16 codepoints, matching the regex tier's own 19-codepoint
   median, only 3/53 outliers >25 chars) but `index-crossref-prefix` was
   not: median 39 codepoints, **40 of 48** over 25 chars. Manual inspection
   of the long ones confirmed they were false positives -- mid-explanation
   citation fragments, multi-nyaya list-summary lines, and verse quotations
   that happen to share an 8-codepoint Devanagari prefix with an unrelated
   back-matter index entry, not fresh headwords (a genuine headword, named
   or phrase-tier, is short by construction -- that is exactly what the
   regex tier's own `HEADWORD_LINE` pattern already assumes, 5–60 chars).
   The prefix strategy's candidate-line length cap was tightened from 90 to
   30 codepoints (a small margin over the observed genuine max) rather than
   shipping the 40 known-bad long entries.
3. **Final combined result: 240 → 302** (index-crossref-seqmatch: 53 kept
   unchanged; index-crossref-prefix: 9 kept of the original 48). No exact
   duplicate `nyaya_deva` values and no duplicate `_ocr_line` values across
   all 302 records (checked programmatically).
4. **20-record text-level spot-check** (image-level scan check still
   blocked, see item 3 of the prior pass below) sampled across all three
   `_match_method` values -- 10 headword-regex, 7 index-crossref-seqmatch, 3
   index-crossref-prefix -- and verified each shipped headword + gloss
   against the raw OCR context at its cited `_ocr_line`. All 20 checked out:
   headword line, tier, and gloss/explanation text genuinely present at the
   cited line, OCR noise (stray Latin-letter misreads, isolated punctuation)
   left as-is per the existing disclosure policy, nothing fabricated.
5. **FEATURES_INDEX.md registration still deferred** -- 302/400 = 75.5% of
   the stated target, closer than either individual PR's count but still
   short of either the target or an explicit reduced-scope sign-off.

**A human should decide** whether 302/400 (75.5%), now the combined ceiling
of both known extraction techniques against this one usable scan, is worth
an explicit reduced-scope sign-off, or whether to wait for the vision-OCR
follow-up (blocked on the archive.org image-server outage, see item 3 below)
before deciding.

## Follow-up (concrete, not "someone should look into this")

1. **Vision-OCR the page images once archive.org's image server recovers**
   (check [SERVER_OUTAGES.md](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
   first) — either the full 118 MB PDF or per-leaf IIIF fetches — and do the
   literal 20-record image-based spot-check the Definition of Done asks for.
2. **A genuinely OCR-garbled-text recovery pass** (vision-OCR or a
   Sanskrit-aware OCR re-run of the same scan) is now the only remaining
   lever for further count growth from this source; both the pattern-matching
   and index-cross-reference extraction approaches are exhausted (see
   "Residual gap" above and the combine-pass QA above).
3. **FEATURES_INDEX.md registration** — hold until either ≥400 or an
   explicit reduced-scope sign-off (MG `@DECIDE`) accepting 302 (75.5%) as
   the final count given the confirmed source ceiling.

_Dr. Mārcis Gasūns_
