# EntryAnatomy — Duden-style "how to read an entry" specimen pages

_Created: 12-07-2026 · Last updated: 15-07-2026_

Annotated specimen pages for the Sanskrit dictionaries, after the model of the
Duden *Deutsches Universalwörterbuch* entry-anatomy spread
([papers/duden_deutsches_universalworterbuch-page.pdf](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/duden_deutsches_universalworterbuch-page.pdf)):
real entries re-typeset from the Cologne digital text, with callout labels
wired by leader lines to highlighted spans, a facsimile inset of the same
entries in the printed original, and a print-ready single-sheet PDF export.

## The three pages

| Page | PDF | What it teaches |
|---|---|---|
| [pwg-entry-anatomy.html](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/pwg-entry-anatomy.html) | [pwg-entry-anatomy.pdf](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/pwg-entry-anatomy.pdf) | Böhtlingk & Roth (PWG, 1855–1875): 24 labelled elements — homograph numbers, Devanāgarī-only headwords, Vedic saṃhitā accents in citations, German glosses, exact-locus citations with run-on abbreviation, Dhātupāṭha/gaṇa apparatus, prefixed verbs nested in the root article |
| [mw-entry-anatomy.html](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-entry-anatomy.html) | [mw-entry-anatomy.pdf](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-entry-anatomy.pdf) | Monier-Williams (1899): 21 labelled elements — two-script headwords, typographic entry levels, compound runs with stem elision (— kakṣa), compressed citations, principal parts with grammarians' references, literal-meaning quotes |
| [cdsl-record-anatomy.html](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/cdsl-record-anatomy.html) | [cdsl-record-anatomy.pdf](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/cdsl-record-anatomy.pdf) | The digital layer: `<L>…<LEND>` record model, key1 vs key2, SLP1 with accent characters, `<ls n="…">` citation expansion, the MW `<e>` typographic-level code, the `<info>` machine layer — three raw records shown next to their rendering |

Both dictionary pages use the **same lemma family** (the *heman*
'impulse/winter/gold' homographs, plus a verbal root — √*cumb* for PWG, the
three *gup* roots for MW), so the two lexicographic traditions can be compared
on identical material.

## The /entry-specimen modes (H870)

The same engine now builds a specimen for **any headword of any CDSL
dictionary** and can annotate **any supplied picture** — the two modes of the
[/entry-specimen](https://github.com/gasyoun/claude-config/blob/main/commands/entry-specimen.md)
skill. Every specimen is ONE self-contained HTML document that serves both
outputs: a theme-aware interactive web page on screen (hover/click a callout
highlights its target and vice versa, pin by click, leader lines reflow on
resize, light/dark via `prefers-color-scheme` plus a toggle) and a
print-faithful single sheet in print (the H780 `@page` auto-size path).

```
python build_entry_anatomy.py --markup mw kAla
python build_entry_anatomy.py --image page.pdf --callouts spec.json --page 1
```

- `--markup <dict> <headword>` re-typesets every record whose `<k1>` equals
  the SLP1 headword from `csl-orig/v02/<dict>/<dict>.txt` (MW groups
  continuation records into print paragraphs by `<e>` level; PWG typesets one
  paragraph per record). Without `--callouts` the build proposes a first-pass
  callout set from the entry structure, each label marked *"proposed — verify"* —
  never presented as authoritative anatomy. The facsimile inset auto-pulls
  from the Cologne scan server (`servepdf.php` with `dict=`, MW and PWG;
  soft fallback when the server throttles) or comes from `--facsimile <img>`.
  Caution when supplying MW pages by hand: the portal hosts BOTH editions
  with colliding printed page numbers — 1899 per-page files are
  `mw<page>-<headword>.pdf`, the 1872 first edition's are `pg_NNNN.pdf`;
  check the running heads, see
  [FINDINGS §80](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
- `--image <path>` embeds a picture (a PDF page is rasterized first, `--page`,
  `--dpi`) as the annotation surface; callout targets are `x,y,w,h` regions in
  fractions of the image.
- `--callouts <json|tsv>` — rows of `side · target · note`; targets are CSS
  selectors, literal anchor text (markup mode), or fraction regions (image
  mode). `--pdf` / `--web` select outputs (default: both). `--out`, `--stem`,
  `--title`, `--caption` control naming.

Committed exemplars:
[mw-kAla-specimen.html](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-kAla-specimen.html)
([PDF](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/mw-kAla-specimen.pdf))
— the generalized markup mode on MW *kāla*, 39 records in 2 print paragraphs —
and
[duden-faser-image-specimen.html](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/duden-faser-image-specimen.html)
([PDF](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/duden-faser-image-specimen.pdf))
— the Duden *Faser* reference plate itself annotated in image mode, 13 regions
located from the PDF text layer
([spec](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/assets/duden_faser_plate_callouts.json)),
each English label mirroring the plate's own printed German label so the
annotation is verifiable against the original.

A specimen embeds a facsimile scan — run
[/publish-safety-check](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
before any specimen goes onto a public page (Cologne scans are
display-permitted; the Duden plate is © Dudenverlag and stays repo-internal
as a methodological reference).

## Rebuilding

```
python build_entry_anatomy.py
```

reads the sibling checkout of
[sanskrit-lexicon/csl-orig](https://github.com/sanskrit-lexicon/csl-orig)
(`v02/pwg/pwg.txt`, `v02/mw/mw.txt`) and the facsimile crops in
[assets/](https://github.com/gasyoun/SanskritLexicography/tree/master/EntryAnatomy/assets)
(cropped from the Cologne scan server: PWGScan `pwg7-1655.pdf`, MWScan
`mw1304-hetumAtratA.pdf`), and writes the three self-contained HTML files
(scans embedded as data URIs). PDF export, one command per page:

```
chrome --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 --print-to-pdf=<page>.pdf <page>.html
```

The page JS measures the laid-out sheet and injects a matching `@page` size,
so the PDF is a single sheet regardless of content height (serve the HTML over
HTTP or open from disk; both work for printing).

## Provenance

Entries: PWG L 117557–117563 (heman cluster), L 25758 (√cumb); MW L
264069–264139 (heman + hema- compounds, selection), L 65898–65906 (gup
cluster). Text: Cologne Digital Sanskrit Dictionaries, csl-orig v02.
Transliteration: `indic_transliteration` (SLP1 → Devanāgarī/IAST), Vedic
accents mapped `/` → U+0951, `\` → U+0952 (saṃhitā convention). Built by
Fable 5 (`claude-fable-5`), 12-07-2026.

_Dr. Mārcis Gasūns_
