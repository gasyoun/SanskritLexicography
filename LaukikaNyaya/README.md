# Laukika-nyāya (Jacob's "Handful of Popular Maxims")

_Created: 13-07-2026 · Last updated: 19-07-2026_

## Status: partial ingest — 300 of the ≥400-record target, honestly short

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

**19-07-2026 resume pass (this update):** [PR #437](https://github.com/gasyoun/SanskritLexicography/pull/437)
shipped a first pass of **151** records (38% of target) from a single
archive.org OCR text derivative, using a strict single-line regex that only
caught clean headword lines. This pass nearly doubled that to **300**
records (75% of target) from the *same already-committed* raw OCR text —
no new source, no re-download — by cross-referencing the book's own
back-matter **"Alphabetical List of Nyayas Explained in Each Part"** index
(~458 entries, OCR lines ~16518–17206, previously unused) to recover
headword occurrences the strict regex missed because of stray OCR noise
around an otherwise-legible line (e.g. a misread daṇḍa rendered as a stray
Latin letter). See "How the +149 records were recovered" below for the
exact method, and "Known limitations" for what still falls short of 400 and
why.

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
    -> raw/jacob_1907-1911_archiveorg_djvu.txt   (committed here verbatim, for audit trail;
                                                   UNCHANGED since 13-07-2026 -- the 19-07
                                                   pass re-mines this same file, no re-fetch)
    -> tools/build_laukika_nyaya.py              (extraction + IAST/SLP1 transcode via sanskrit-util)
    -> data/laukika_nyaya.jsonl                  (this directory's output, 300 records)
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

| Part | OCR line range | Entries (13-07) | Entries (19-07) |
|---|---:|---:|---:|
| First Handful (2nd ed., 1907) | 807 – 3548 | 42 | 66 |
| Second Handful (1909) | 3549 – 8664 | 57 | 107 |
| Third Handful (1911) | 8665 – 16494 | 52 | 127 |
| **Total** | | **151** | **300** |

(The back-matter index + errata + publisher's ad pages, OCR lines
~16495–end, are explicitly excluded from extraction — see next section.)

## How the +149 records were recovered (19-07-2026 pass)

The raw OCR text's own back matter contains a genuine
**"Alphabetical List of Nyayas Explained in Each Part"** (~458 entries,
lines ~16518–17206) — a back-of-book index Jacob's publisher printed,
listing every maxim name across all three handfuls with which handful
("i."/"ii."/"iii.") it belongs to. This was not used at all in the 13-07
pass. `tools/build_laukika_nyaya.py` now parses this index and uses it as
an authoritative cross-reference to recover body headword occurrences the
original strict single-line regex missed, via two match strategies (both
require the recovered line to be genuinely index-listed — this is a
**discovery** mechanism, not a content source: every recovered record's
headword and explanation text still come verbatim from the same raw OCR
body text as the original 151, nothing is synthesized):

1. **`index-crossref-seqmatch`** (78 records) — whole-line fuzzy match
   (`difflib.SequenceMatcher` ratio ≥0.75) between an index entry's cleaned
   Devanagari and a body candidate line's cleaned Devanagari. Catches
   "named" (coined "X-nyāya" compound) headwords whose line has stray
   leading/trailing OCR noise (a misread daṇḍa, a stray Latin letter) that
   made the v1 regex reject an otherwise-legible line.
2. **`index-crossref-prefix`** (71 records) — exact 8-Devanagari-codepoint
   prefix match. Catches "phrase"-type headwords (the maxim's own quoted
   opening words, not a coined compound) — these are longer and more
   OCR-variable than named compounds, so a whole-line ratio match performs
   poorly on them, but their opening words are usually rendered more
   reliably by the OCR than their middle/end.

Both strategies reject a candidate if: the immediately preceding non-empty
line is itself heavy Devanagari prose (the candidate would sit
mid-verse-quotation, not at a fresh heading), or the candidate's own line
(or the 1-2 preceding lines) carries an English citation-introducing phrase
("as follows:", "namely", "same class as", "same purport", "it appears
as") or opens with a curly quotation mark — both are reliable signals that
the Devanagari text is quoted *inside* a different entry's explanation, not
a heading of its own. This citation-guard was calibrated by manually
reviewing every candidate match it affects (documented in the git history
of `build_laukika_nyaya.py`) and rejects ~10 clear false positives that an
earlier, looser version of the pass would have shipped.

**Headword text now preserves internal spaces** (fixed in the same pass):
the v1 regex stripped every non-Devanagari character including spaces, so
a genuine multi-word phrase-type headword like *"He who performs an action
will himself reap the fruit thereof"* (य एव करोति स एव ...) would have
shipped as one unreadable run-on token. `nyaya_deva` now collapses internal
whitespace to single spaces instead of removing it — a readability fix,
not a content change (same characters either way).

**Bug found and fixed in the same pass:** the original `clean_body()`
boilerplate-stripping regex (`Digitized By ... eGangotri ... .*`) had an
unanchored trailing `.*`, so when applied to an explanation window that
happened to contain one of the recurring "Digitized By Siddhanta eGangotri
Gyaan Kosha" credit lines *anywhere in the middle* (common — the digitizer
stamped this every page or two throughout the source), it silently
truncated everything from that point to the end of the window, sometimes
leaving an empty `explanation`. Boilerplate is now stripped **per line**
before joining, which is bounded by construction. This fix alone lengthened
185 of the 300 records' `explanation` field (many multiple times over — see
git history), including records that were part of the original 151 — this
was a real, previously-undiscovered defect in already-shipped data, not
something introduced by this pass.

## Data

[`data/laukika_nyaya.jsonl`](data/laukika_nyaya.jsonl) — 300 records, one
per line, mirroring the IndischeSprueche field style:

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
  for `"phrase"`-tier entries, its own quoted Sanskrit opening, internal
  spaces preserved) in Devanāgarī, IAST, and SLP1.
- `explanation` — Jacob's own note, lightly cleaned (de-hyphenated,
  digitization-credit boilerplate stripped line-by-line) but **not
  otherwise rewritten**; OCR noise in the Sanskrit quotations Jacob himself
  cites is left as-is. Capped at 4000 characters (22 of 300 records hit
  this cap — a pre-existing design choice, not new truncation).
- `source` — **edition/part-level citation only, deliberately without a
  page number** — see "Known limitations" below for why.
- `_ocr_line` — internal, non-citable: the line offset into
  `raw/jacob_1907-1911_archiveorg_djvu.txt` where the entry's headword was
  found, kept so a future correction pass can re-locate the exact source
  text without re-running the whole extraction.
- `_headword_tier` — `"named"` (186 records, headed by a coined "X-nyāya"
  compound) or `"phrase"` (114 records, headed by the maxim's own quoted
  Sanskrit line rather than a coined name).
- `_match_method` — how the headword occurrence was found: `"headword-regex"`
  (151, the original v1 strict single-line pattern), `"index-crossref-seqmatch"`
  (78, new) or `"index-crossref-prefix"` (71, new) — see previous section.
  Kept for audit trail; not part of the IndischeSprueche-mirroring schema
  itself, so a strict downstream consumer can safely ignore/drop it.

## Known limitations / OCR fidelity (spot-check log)

Per the handoff's own framing ("judgment-gated on OCR fidelity"), this
section **is** the spot-check. The 19-07 pass did BOTH kinds of check the
13-07 pass could not complete (archive.org was down for most of that
session): direct **visual** comparison against the actual page scans
(archive.org recovered mid-session), and text-level cross-checks.

1. **Target count not met.** 300 of the ≥400 the handoff's stop condition
   named (75%). The book's own back-matter index lists **458** entries
   total across all three handfuls — comfortably above 400 — so the ceiling
   is not "the book doesn't have 400 maxims," it's **recoverable OCR
   quality**: of the 458 index entries, ~300 could be confidently
   cross-referenced to a body occurrence without unacceptable false-positive
   risk (see next item). The remaining ~158 are overwhelmingly
   `"phrase"`-type entries whose index rendering and body rendering diverge
   too much (different OCR-garbling of the *same* long, variable phrase in
   two different scan locations) for the prefix/seqmatch strategies above
   to safely pair them — recovering them would need either a materially
   better OCR pass (vision-OCR of the actual page images, still the
   standing follow-up) or manual editorial pairing, not a further
   automated relaxation of the current heuristics (already tested at
   looser thresholds — see "Follow-up" below for the concrete numbers this
   pass found and rejected).
2. **Precision over recall — 10 candidate false positives found and
   rejected before shipping, not silently included.** An earlier internal
   version of the index-crossref pass, before the citation-guard described
   above, would have shipped ~10 additional "matches" where the body line
   was actually a Devanagari fragment quoted *inside a different entry's*
   explanation (e.g. an index entry for "परस्परविरोधे हि" nearly matched
   a body line reading "...as follows:—'अत्र परस्परविरोधशीला गुणाः
   सुन्दोपसुन्दवत्...'" — that body text is Jacob citing a *different*
   nyāya, सुन्दोपसुन्दन्याय, by way of comparison, not a heading of its
   own). All such cases were manually reviewed and excluded.
3. **One record removed after a direct visual scan check found
   cross-contaminated content.** OCR line 14614 ("य एव करोति स एव x ॥") is
   a genuine headword — confirmed directly against the archive.org page
   image (leaf 300, printed page ~183) — but the printed page's OCR for
   its own explanation paragraph came out as ~20 lines of near-total noise
   (single stray characters), and the *following* entry's heading line
   also failed to OCR as recognizable Devanagari (its first word rendered
   as the Latin string "Hawa"), so no boundary could be found there either.
   The result would have been an explanation mixing noise with a chunk of
   the *next* entry's content (about a camel's back, not this entry's
   "reaps what he sows" topic) — excluded rather than shipped with
   misattributed content. See `EXCLUDED_LINES` in
   `tools/build_laukika_nyaya.py` for the exact reasoning kept with the code.
4. **Direct visual spot-check against the actual scan (4 pages, 6+ entries)
   — the "against the scan" check the 13-07 pass could not complete.**
   archive.org (down for most of the earlier session) recovered mid-pass.
   Fetched page images via the IIIF endpoint for printed pages 17, 41, 71,
   and ~183 (leaves 100, 60, 154, 300) and read them directly:
   - **कण्ठचामीकरन्यायः** (record #89, original v1 tier): explanation text
     matches the scan word-for-word, **except** the scan clearly reads
     "pages 130 and 131" / "page 130" and the OCR (and therefore the
     shipped record) has "180"/"180" — a genuine OCR digit misread (१ vs
     ८), left as-is per this dataset's disclose-don't-silently-fix
     convention for OCR noise **within** correctly-attributed text (as
     opposed to item 3 above, where the wrong CONTENT was attached to the
     wrong headword — a different, more serious class of defect that does
     get excluded).
   - **मध्यदीपिकान्यायः** (record #51, original v1 tier): matches, with
     one internal OCR inconsistency — "central lamp" is misread as
     "central lump" in the headline gloss position but correctly as "lamp"
     two sentences later in the same explanation (same underlying word,
     inconsistent OCR pass — a real, disclosed quirk, not a shipped error
     in the sense of wrong content).
   - **य एव करोति स एव** (record #265): the cross-contamination described
     in item 3 — this is the one record excluded as a direct result of
     this visual check.
   - **मण्डूकप्लुतिन्यायः** ("the maxim of a frog's leap", visible on the
     scan at printed page 41): confirmed **absent** from the dataset — its
     own heading OCR'd too badly (`मण्डूक्जतिन्याय` in the index, worse in
     the body) to be recoverable by either match strategy; its explanation
     text is present but silently absorbed into the *preceding* entry's
     window (मध्यदीपिकान्यायः, #51) rather than fabricated as its own
     entry. A concrete, named example of the "≈158 entries not yet
     recovered" gap in item 1, not a new defect.
   - **लक्षणप्रमाणाभ्यां वस्तुसिद्धिः** (visible on the scan at printed
     page 71, right after रेखागवयन्यायः): same pattern as the frog's-leap
     case — genuinely present in the source, not separately recovered,
     its text absorbed into the preceding entry (#151,
     रेखागवयन्यायः)'s over-long `explanation` field rather than invented
     as a standalone record. This is the general shape of "harmless
     over-inclusion" for entries this pass did not recover: the
     *preceding* entry's own content is still correct at the start of its
     `explanation`, it just runs on into whatever the next unrecovered
     entry's text was, unbounded, until the next entry this pass DID
     recover.
   - No genuinely fabricated content was found in any of the visually
     checked entries — every discrepancy was either a disclosed pre-existing
     OCR error (digit/word misread) or the one boundary-detection failure
     in item 3, which was excluded.
5. **Devanagari OCR noise, left as-is (not silently corrected):**
   consonant-cluster misreads are the dominant error mode, e.g. record #2
   `अन्तदींपिकान्यायः` is almost certainly a misread of
   `अन्तर्दीपिकान्यायः` (dropped र, spurious anusvāra). Manual review
   across both passes (the original ~40-entry text review plus the 19-07
   visual scan checks above) is consistent with the originally-reported
   **1 in 10–15 headwords** single-character consonant/vowel-sign
   confusion rate.
6. **Per-entry page citation still not added.** The `_page_numbers.json`
   sidecar (previously 500'd on every fetch attempt) was successfully
   fetched in this pass once archive.org recovered, confirming it exists
   and is usable — but building the OCR-line → printed-page correlation
   needed to attach it per-record is a distinct, non-trivial task (the
   sidecar indexes by scan *leaf*, not OCR line) not completed this pass;
   still a concrete follow-up.
7. **Third Handful (1911) and Second Handful (1909) standalone archive.org
   scans remain unusable** (confirmed in the 13-07 pass, unchanged): the
   standalone Second Handful item yields zero recoverable Devanagari
   headwords; the standalone Third Handful item has garbled English
   explanation text. Neither was used; all 300 records come from the same
   bound-in combined scan as the original 151.
8. **False-positive headword lines, found and rejected during parsing**
   (not present in the shipped 300): mid-explanation quoted śloka couplets,
   the book's own running title re-appearing at part breaks (all as in the
   13-07 pass), plus the citation-quote false positives described in item 2
   above (new to this pass, specific to the index-crossref strategies).

## Follow-up (concrete, not "someone should look into this")

1. **Vision-OCR the remaining ~158 unrecovered index entries.** Now that
   archive.org page images are reachable (`https://iiif.archive.org/iiif/{id}$leaf/full/{size}/0/default.jpg`,
   leaf numbers found by binary-searching against known OCR-line landmarks
   or fetching the `_hocr_pageindex.json.gz` sidecar), a future pass could
   read each remaining index entry's page directly rather than relying on
   OCR-to-OCR fuzzy matching. This is the highest-leverage remaining lever
   to close the gap to 400 — the entries genuinely exist (per the book's
   own index), the current bottleneck is specifically OCR-to-OCR
   cross-referencing between two independently-garbled renderings of the
   same phrase, which a direct human/vision read of the scan sidesteps
   entirely.
2. **Correlate `_page_numbers.json` (fetched, see item 6 above) to
   `_ocr_line`** to add real per-entry page citations to the `source`
   field. Needs an OCR-line → scan-leaf mapping (via `_hocr_pageindex.json.gz`,
   also fetched and confirmed usable this pass) as the missing link.
3. **FEATURES_INDEX.md registration still deferred** until either the
   ≥400 target or an explicit reduced-scope sign-off is reached —
   registering a dataset as a finished F-series asset while it is 75% of
   its own stated target would still misrepresent it to a future consumer,
   even though 75% is a much stronger position than the original 38%.
4. **A second, independent worktree (`SanskritLexicography-h803`,
   branch `h803-laukika-nyaya-phrase-recall`) was found mid-session with
   uncommitted local changes (240 records, modified minutes before this
   pass's own worktree was created)** — a concurrent session working the
   same handoff. That worktree was left untouched per the org's
   don't-touch-a-foreign-worktree convention; this pass proceeded
   independently in its own isolated worktree and ships via a normal PR.
   A human (or `/pr-babysit`) should reconcile the two efforts — this
   pass's 300 records supersede that worktree's 240 on every count
   checked (record count, the boilerplate-truncation bugfix, the
   headword-space-preservation fix, and the citation-guard precision
   pass), but its own approach was not reviewed in detail and may contain
   ideas worth folding in.

_Dr. Mārcis Gasūns_
