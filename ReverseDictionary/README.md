# Reverse Dictionary of Sanskrit — working materials

_Created: 06-07-2026 · Last updated: 18-07-2026_

## What this is

This directory holds the working materials for an **unpublished reverse dictionary of
Sanskrit** (a dictionary sorted by the *last* letter of each word rather than the first —
used for finding rhymes, verse endings, and grammatical suffix patterns) compiled primarily by
Mārcis Gasūns, with algorithmic sorting work by Dhaval Patel (reverse-Devanagari sort,
[`reverse15.php`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/reverse15.php)) and statistical appendices by Anton Pilyuganov. The compiler's
own preface (see [`Обратный словарь санскрита.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8C%20%D1%81%D0%B0%D0%BD%D1%81%D0%BA%D1%80%D0%B8%D1%82%D0%B0.mdx)) frames the
project as unprecedented in scale for Indology — merging **~30 source dictionaries spanning
1822–2005** (Böhtlingk & Roth's *Petersburger Wörterbuch*, PWK, Monier-Williams, Apte, Macdonell,
Turner, Schmidt's *Nachträge*, Kochergina, Grassmann, Vachaspatyam, Śabdakalpadruma, and others —
full list in [`Словари-источники.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D0%B8%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8.mdx)) into a single reverse index of
**≈266,820 headwords** (`.doc.pdf/266820-reverse-Gasuns.txt` — deliberately local-only and
gitignored, so it has no GitHub URL; see "Data location, integrity & backups" below),
roughly double the size of its main predecessor (Wolfgang Schwarz's 1974 German reverse
dictionary, ~130,000 words, 14 years in the making).

A German-language annotation attributed to Manfred Mayrhofer, quoted in the preface, frames why
this matters: a reverse (rückläufiges) dictionary of Old Indic has been a *desideratum* of
Indo-European studies for decades — Latin and Greek have had one for a long time, Sanskrit did
not — because a reverse index enables systematic word-formation research and helps identify
partial word-forms in damaged manuscripts.

**This is a data/research workspace, not a finished publication.** A transliteration (IAST) draft
of the dictionary was laid out in InDesign at 1,014 pages (see
[`Колонтитул от Евгения/reverse.indd`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9A%D0%BE%D0%BB%D0%BE%D0%BD%D1%82%D0%B8%D1%82%D1%83%D0%BB%20%D0%BE%D1%82%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D1%8F/reverse.indd)); a Devanagari-script
edition was estimated at 832 pages (18% shorter) but, as far as these files show, was never
actually typeset. Several parallel drafts exist at different headword counts (250,026 /
255,882 / 266,820) representing different stages of the compilation, not different editions.

## What's inside — and what's not

This folder is a **general personal materials dump**, not a curated project folder — alongside
the dictionary data it contains ~140 unrelated files (legal correspondence, music-teaching
concert programs, devotional/liturgical PDFs, photos). [`INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/INDEX.md) catalogs **every
file** (413 total) with a relevance classification:

| Category | Count | Meaning |
|---|---|---|
| **Core** | 124 | The dictionary manuscript itself and its direct source data/statistics |
| **Related** | 69 | Supporting reference material — endings lists, root lists, sorting/typography notes |
| **Literature** | 47 | Comparative reverse-dictionary scholarship for other languages (German, Armenian, Albanian, Hindi, Akkadian, Greek...) and predecessor works (Schwarz, Stiehl, Zalizniak) |
| **Background** | 22 | Production assets not specific to this project (Indological fonts, a general Sanskrit-literature catalog) |
| **Needs review** | 10 | Relevance unclear even after a content sample (mostly scanned PDFs with no extractable text) |
| **Out of scope** | 141 | Personal/business/music-teaching/devotional material unrelated to the dictionary |

Only the first four categories were in scope for this pass, per the working decision to keep
this README and the conversion below focused on the dictionary project rather than the whole
folder.

## The core dataset

| File | What it is |
|---|---|
| `.doc.pdf/266820-reverse-Gasuns.txt` *(local-only, gitignored — no GitHub URL; see "Data location, integrity & backups" below)* | **The current master word list** — 266,820 data lines (266,819 CRLF-terminated + 1 unterminated final line, per [`SCHEMA.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md)), tab-separated `SOURCE_ABBREV<TAB>word`, sorted for reverse lookup. This is the working canonical dataset; the `.doc`/`.pdf` variants elsewhere are earlier milestones (250,026 / 255,882 headwords) kept as historical snapshots, not alternate editions. |
| `.doc.pdf/153593-reverse-Stiehl.txt` *(local-only, gitignored)* | Ulrich Stiehl's 2004 reverse-dictionary compilation (153,593 words, from the Cologne Monier-Williams digitization) — reference/comparison corpus. |
| `.doc.pdf/29008-reverse-Koch.txt` *(local-only, gitignored)* | Kochergina's reverse list (29,008 words) — reference/comparison corpus. |
| `187992 headwords.txt` *(local-only, gitignored)* | Headwords attested in 2+ source dictionaries, each tagged with its source abbreviations (`aMSagaRa:IEG,PD` format). |
| [`Словари-источники.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D0%B8%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8.mdx) / preface §"Аббревиатуры" | The 30-source bibliography with single-letter codes (A–Z, Ā, Ś, Ü, ß) used throughout the corpus. |
| [`Состав и строй словаря.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BE%D1%81%D1%82%D0%B0%D0%B2%20%D0%B8%20%D1%81%D1%82%D1%80%D0%BE%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8F.mdx) | The editorial rulebook (§1–§10): sort order (by final letter, then penultimate, etc.), what's excluded (inflected forms, pronoun case forms, comparative/superlative degrees unless independently lexicalized...), homonym handling, accent-mark sourcing. |
| [`reverse15.php`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/reverse15.php) | Dhaval Patel's Devanagari reverse-sort algorithm (2013) — the actual sorting engine referenced in the preface. |
| [`Колонтитул от Евгения/reverse.indd`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9A%D0%BE%D0%BB%D0%BE%D0%BD%D1%82%D0%B8%D1%82%D1%83%D0%BB%20%D0%BE%D1%82%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D1%8F/reverse.indd), `reverse-import-from-txt.indd` | The InDesign layout files for the transliteration print edition (1,014 pp draft). |
| Statistical appendices (`.doc.pdf/Statistica/`) | Syllable-structure (CVC), stress-position, prefixoid/suffixoid distribution tables — the planned book appendices. |

## Methodology, in brief

From the compiler's preface and the editorial rulebook:

- **Sort key**: final letter → penultimate letter → antepenultimate letter, recursively — i.e.
  true suffix-reverse order, not simple string reversal (Devanagari conjuncts and codas that are
  only legal word-finally make naive reversal wrong).
- **Source priority**: PWK (the "small" Petersburg dictionary, merged with Schmidt's *Nachträge*)
  is the implicit default/unmarked source; every other source is tagged with its letter code only
  when a word is *not* in PWK. This mirrors Schwarz's citation convention (3 primary + 5
  secondary sources cited per entry) rather than tagging all ~30 sources on every line.
- **Normalization to stem form**: nominal endings stripped to the bare stem (प्रातिपदिक), verbs
  cited as roots with MW's prefixes attached; ~20,000 inflected "false" word-forms were removed
  this way from the Vācaspatyam/Śabdakalpadrumaḥ/Apte lists specifically.
  Sandhi-final-consonant ambiguity (e.g. *saraṭ* vs. *sarah*) is resolved case-by-case, not by a
  blanket rule.
  See "Форма основы" in [`Обратный словарь санскрита.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8C%20%D1%81%D0%B0%D0%BD%D1%81%D0%BA%D1%80%D0%B8%D1%82%D0%B0.mdx).
- **Explicit exclusions** (§5 of the rulebook): words marked "incorrect" in a source; modern
  Cyrillic-letter names; prefixes standing alone; case/gender-inflected pronoun and numeral forms;
  participles with no independent adjectival/adverbial sense; regularly-derived adverbs given
  inside another entry; compounds shown in light type inside another entry.
- **Typo/error correction**: cross-checking against Monier-Williams as a control list surfaced
  dozens of digitization and print errors, some of which were fed back upstream to the Cologne
  Digital Sanskrit Dictionaries project (this is, per the preface, part of how the
  `sanskrit-lexicon` GitHub organization's correction-submission culture began).
- **Known gaps acknowledged by the compiler**: the ~123,000-word Vedic Word Concordance
  (1973–1976) and Bandhu's word list were never digitized/available and so are absent.

## What was converted this session

Per a working decision on scope (large/duplicate/scanned files were excluded — see rationale
below), 38 Core/Related `.doc`/`.docx`/`.pdf` files under 3MB were converted to `.mdx`:

- `.doc` → LibreOffice headless → `.docx` → Pandoc → `.mdx` (tables forced to pipe/grid form,
  grid tables wrapped in a ` ```rst-table ` fence — consistent with the org's
  [`/docx-to-md`](https://github.com/gasyoun/SanskritGrammar) convention).
- `.pdf` (with an extractable text layer) → `pdftotext -layout` → `.mdx`, wrapped in a fenced code
  block to preserve columnar dictionary layout (these are word lists/tables, not prose — Markdown
  structure would not help and would risk mangling alignment).

**Deliberately not converted:**

- **Large duplicate manuscript drafts** (`reverse-250026*.doc`, `reverse-255882.doc`,
  `reverse-FULL.doc`, `reverse-index-full.doc`, 10–26 MB each, under
  [`.doc.pdf/`](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary/.doc.pdf)) — these are superseded snapshots of the same word list already
  available in plain, more usable `.txt` form (`266820-reverse-Gasuns.txt`). Converting a
  26 MB Word file containing a sorted word list to Markdown produces a 26 MB Markdown file with
  no structural benefit.
- **The `Литература по обратным словарям/` comparative-literature PDFs** (50–70 MB scanned
  library/Google Books exports of Schwarz 1974, Zalizniak 1974, and reverse dictionaries of
  German, Armenian, Albanian, Akkadian, Hindi, Greek) — mostly image-only scans; OCR-ing ~900 MB
  of 19th–20th century scholarship was judged out of proportion to this session's ask. They're
  cataloged by filename in [`INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/INDEX.md) as a to-do (see below).
- One image-only PDF with no text layer ([`Biconsonantal conjuncts.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/Biconsonantal%20conjuncts.pdf))
  was skipped for the same reason.
- `.xlsx`/`.xlsm` spreadsheets (comparison tables, hyphenation rules, statistics) and the InDesign
  `.indd`/`.idml` layout files were left as-is — neither format is meaningfully representable as
  Markdown without losing the thing that makes them useful (formulas, page layout).

## Use cases

**Sanskrit poets and composers** — the primary classical use of a reverse dictionary: finding
words that end in a given syllable/suffix for verse composition (rhyme, alliteration, meeting a
metrical foot). The master list (`.doc.pdf/266820-reverse-Gasuns.txt`, local-only — see
"Data location, integrity & backups") is already reverse-sorted; a poet composing in a
fixed meter can scan a suffix block directly.

**Linguists and lexicographers** — the editorial apparatus itself is a research object: the
30-source merge methodology, homonym/part-of-speech disambiguation rules, and the frequency
tables (final letter / final digram / final trigram, in the planned appendices) support
morphological and word-formation studies that no single source dictionary could support alone.
The [`Литература по обратным словарям/`](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary/%D0%9B%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0%20%D0%BF%D0%BE%20%D0%BE%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D0%BC%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8F%D0%BC) folder is directly
useful here as comparative method — how German, Armenian, Akkadian, and Hindi reverse
dictionaries solved the same sorting/normalization problems.

**Students learning Sanskrit grammar** — [`249-types-of-pratyayas-MW.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/249-types-of-pratyayas-MW.txt)
(suffix frequency ranked from MW: `-ta` 12,489 occurrences down to rare types),
[`nounend.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/nounend.txt)/[`verbend-dev.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/verbend-dev.txt) (case/number-tagged noun and verb
ending paradigms), and [`Bucknells Index to Endings.doc`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/Bucknells%20Index%20to%20Endings.doc)
give a suffix-first view of the grammar that a front-alphabetized dictionary can't.

**Digital humanities / corpus researchers** — the headword lists, per-text frequency counts
([`Список слов из Махабхараты.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D0%BB%D0%BE%D0%B2%20%D0%B8%D0%B7%20%D0%9C%D0%B0%D1%85%D0%B0%D0%B1%D1%85%D0%B0%D1%80%D0%B0%D1%82%D1%8B.txt),
[`Список слов из Рамаяны.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D0%BB%D0%BE%D0%B2%20%D0%B8%D0%B7%20%D0%A0%D0%B0%D0%BC%D0%B0%D1%8F%D0%BD%D1%8B.txt),
[`Список слов из Ригведы SLP1.xml`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA%20%D1%81%D0%BB%D0%BE%D0%B2%20%D0%B8%D0%B7%20%D0%A0%D0%B8%D0%B3%D0%B2%D0%B5%D0%B4%D1%8B%20SLP1.xml), the "500 most
frequent words in..." files for Sūryasiddhānta/Ṛgvedāṅgajyotiṣa/Ṭikanikayātrā), and the
tab-separated source-tagged headword format are machine-readable data assets reusable outside the
print-book context — e.g. as a crosswalk key or a frequency baseline, the way this org's
[`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)/[`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
hubs already track other derived Sanskrit datasets.

## Towards a 2-volume book

The compiler's own page-count data makes a 2-volume split concrete rather than speculative:
1,014 pp. for the transliteration draft at 246 words/spread, vs. an estimated 832 pp. for the same
~250,000 words set in Devanagari (18% shorter, because Devanagari conjunct clusters are more
compact than their multi-letter IAST transliteration). Recommended split, matching the use cases
above to what each volume is actually for:

- **Volume 1 — Devanagari edition.** The reverse index alone, no critical apparatus, set in
  Devanagari (~830 pp. per the compiler's own estimate). This is the volume poets, chanters, and
  grammar students actually use at the point of composition/study — a fast word-ending lookup,
  not a scholarly apparatus.
- **Volume 2 — Transliteration edition + apparatus.** The same index in IAST (needs the extra
  width IAST requires) *plus* everything the linguist/DH audience needs: the 30-source
  bibliography, the editorial rulebook (§1–§10), the preface's methodology essay, the frequency
  and statistical appendices (final letter/digram/trigram tables, syllable-structure and
  stress-position distributions from `Statistica/`), and an explicit comparison table against
  Schwarz (1974), Stiehl (2004), and Zalizniak — currently scattered across
  [`Сопоставление обратных словарей.xlsx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BE%D0%BF%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%20%D0%BE%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D1%85%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B5%D0%B9.xlsx) and the
  preface prose, never consolidated into one comparison table.

This is a genuine restructure, not a repackaging of the existing InDesign files: the existing
`reverse.indd`/`reverse-import-from-txt.indd` under
[`Колонтитул от Евгения/`](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary/%D0%9A%D0%BE%D0%BB%D0%BE%D0%BD%D1%82%D0%B8%D1%82%D1%83%D0%BB%20%D0%BE%D1%82%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D1%8F) already typeset the transliteration index
*without* the apparatus, which is closer to a "Volume 1 in the wrong script" than to either
proposed volume — reusable as a starting layout template, but the content split above is new.

### What needs updating before either volume is publishable

- **No single canonical word list has been declared.** Three headword counts exist
  (250,026 / 255,882 / 266,820) without a written note on why the list grew between drafts
  (new sources added? error corrections? both?). Before typesetting, the 266,820-entry list needs
  a dated changelog entry establishing it as canonical, and the older `.doc` drafts should be
  marked superseded (or removed) rather than left as same-looking duplicates.
- **No Devanagari-sorted edition exists yet.** Only the transliteration draft was ever laid out;
  producing Volume 1 requires re-running the canonical list through the reverse-Devanagari sort
  ([`reverse15.php`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/reverse15.php)) and choosing/acquiring a Devanagari print typeface — the
  fonts in [`fonts-emeneau/`](https://github.com/gasyoun/SanskritLexicography/tree/master/ReverseDictionary/fonts-emeneau) (Charter Indologique, Clarendon Indologique) are IAST
  transliteration faces, not Devanagari.
- **Outstanding errata are unresolved.** [`Опечатки которые не успели.pdf`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%BF%D0%B5%D1%87%D0%B0%D1%82%D0%BA%D0%B8%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%B5%20%D0%BD%D0%B5%20%D1%83%D1%81%D0%BF%D0%B5%D0%BB%D0%B8.pdf)
  ("typos we didn't get to") lists known corrections not yet applied to the master list.
- **The statistical appendices are draft specimens, not final tables**
  (`Statistica/tmp/reverse-statistics-specimen.doc`, unfinished Excel `SUMPRODUCT` formulas quoted
  inline in the preface) — these need to be run to completion against the canonical 266,820-entry
  list, not the older drafts they were originally built against.
- **Source coverage stops at 2005.** The Cologne Digital Sanskrit Dictionaries project continued
  digitizing and correcting dictionaries after this compilation (the same `sanskrit-lexicon`
  GitHub organization this repo's parent tree works in) — a currency check against `csl-orig`'s
  present state would likely surface both new source dictionaries and corrections to the ones
  already merged.
- **The comparative-literature folder needs OCR** before it's more than a filename list —
  `Литература по обратным словарям/` holds 47 scans (900 MB+) of the actual predecessor works
  (Schwarz, Zalizniak, and reverse dictionaries of other languages) that Volume 2's comparison
  section should cite directly rather than through the compiler's paraphrase alone.
- **[`Сопоставление обратных словарей.xlsx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BE%D0%BF%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%20%D0%BE%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D1%85%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B5%D0%B9.xlsx)** (the
  comparison spreadsheet) was never turned into the comparison table the preface promises —
  worth doing before Volume 2's apparatus is drafted, not after.

## Publication-prep documents (added 07-07-2026, [H270](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H270-Sonnet_SanskritLexicography_reverse-dict-publication-prep_07.07.26.md))

- [`ACL_DH_COMPATIBILITY_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md) — venue landscape, DH data-standard gap analysis, and the licensing `@DECIDE` with per-source facts.
- [`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md) — canonical-version declaration (`266820-reverse-Gasuns.txt`) and the outstanding-errata investigation.
- [`SCHEMA.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md) — TSV column semantics, source-code→bibliography-key table, encoding audit.
- [`DATA_STATEMENT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/DATA_STATEMENT.md) / [`CITATION.cff`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CITATION.cff) — Bender & Friedman data statement + citation metadata (distribution tier honestly marked undecided pending the licensing ruling).

## Data location, integrity & backups

The canonical dataset and its sibling data files are **deliberately never committed**
(personal-materials-dump folder policy — the `.gitignore` here whitelists only the `.mdx`
conversions and docs). Blob URLs to them can never work; this section is the authoritative
pointer instead. State as of 18-07-2026, recovered and verified under
[H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md)
after the 07-07-2026 fast-forward had silently moved the whole untracked tree out of the
clone (see [`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md)):

- **Working copy (canonical):** `ReverseDictionary/.doc.pdf/266820-reverse-Gasuns.txt`
  in the canonical local clone (`C:\Users\user\Documents\GitHub\SanskritLexicography`).
- **Backup 1 (full dump, drive C):**
  `C:\Users\user\Documents\GitHub\ReverseDictionary.untracked-backup.20260707T093250\` —
  the complete pre-conversion folder (470 files, 1.7 GB) including all `.doc`/`.pdf`
  milestones (250,026 / 255,882) and reference corpora.
- **Backup 2 (full dump, drive D):**
  `D:\ReverseDictionary.untracked-backup.20260707T093250\` — robocopy mirror of Backup 1,
  made 18-07-2026, 470/470 files verified.
- **Integrity anchor:** `266820-reverse-Gasuns.txt` = 4,135,335 bytes, 266,820 data lines,
  UTF-8 with BOM, SHA-256
  `925e696f533d5a9607ea90fb71fae2d2e51d2cc3cb21f332c81cc43e150b9970` (identical in all
  three copies).
- **Off-machine backup:** still an open @DO — the Yandex Disk WebDAV path in
  [`Uprava/BACKUPS.md`](https://github.com/gasyoun/Uprava/blob/main/BACKUPS.md) needs its
  app-password env vars set before `backup_census_priority.py` can carry this file.
- **Distribution tier:** undecided — publication of the full list is gated by the rights
  ruling in [`RIGHTS_LEDGER.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/RIGHTS_LEDGER.md)
  (a "PD-only" subset cannot be certified on available data), so no public release asset
  exists yet by design.

## See also

- [`INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/INDEX.md) — full 413-file inventory with relevance classification.
- [`../CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) — Sanskrit Lexicography repo conventions (encoding/BOM caveats
  apply to the `.txt` corpora in this folder too — check before re-saving any of them).
- [`../FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — org-wide capability inventory; this reverse
  dictionary is not yet registered there — registration follows the licensing ruling
  (see `ACL_DH_COMPATIBILITY_ANALYSIS.md` §4 step 7).

_Dr. Mārcis Gasūns_
