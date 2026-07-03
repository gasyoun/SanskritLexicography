# Heritage DICO French-gloss witness layer

_Created: 03-07-2026 · Last updated: 03-07-2026_

Phase 5 of the [Heritage reuse roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
(H106): the Sanskrit Heritage Dictionary's French gloss prose, extracted per
entry from the local DICO mirror and keyed to the same `mw_key1` (SLP1) space
as the Phase 2 [`mw_heritage_crosswalk.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv).
A **standalone witness/gloss layer to consume, not an automatic merge** into
any Cologne-sourced canonical field — see the license note below.

**Output:** [`heritage_dico_gloss.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss.tsv) —
`mw_key1` (SLP1) · `heritage_entry_anchor` (`DICO/<file>.html#<key>`) ·
`gloss_fr` (cleaned French prose, markup stripped, entities unescaped) ·
`cross_refs` (pipe-joined DICO anchor keys the gloss links to — both
navy-blue-class inline citation links and green-class trailing "see also"
links; the red-class declension/conjugation-generator CGI links are
excluded, they aren't cross-references to other entries). Built by
[`heritage_dico_gloss_extract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_dico_gloss_extract.py),
which reuses `heritage_mw_crosswalk.py`'s key-normalisation conventions
rather than re-parsing DICO's anchor scheme from scratch.

## Coverage

| | count | % |
|---|--:|--:|
| `mw_heritage_crosswalk.tsv` rows resolved to a DICO anchor | 24,549 | — |
| glosses extracted | 24,549 | **100.0 %** |
| skipped (no matching span / empty gloss) | 0 | 0.0 % |
| joined against kosha's `lemmas.slp1` (323,425 rows) | 24,543 | 99.98 % of gloss rows / **7.59 %** of `lemmas` |

The 6 gloss keys that don't join to `lemmas` are a residual key-normalisation
mismatch, not a parse defect — out of scope for this handoff (kosha ingest is
explicitly not being built here).

## Entry-boundary parsing — the non-obvious part

DICO's HTML nests three kinds of named anchors in the same running prose,
and only one kind is a genuine new-entry boundary:

1. **Fresh headword** — an anchor immediately preceded by its own Devanagari
   headword span (a new letter-group entry).
2. **Compound/sub-entry** — an anchor immediately preceded by a bare
   paragraph break with no Devanagari span (e.g. `aṃśavāda`, `aṃśahara` as
   sub-entries of `aṃśa`'s letter group) — this **is** a separate entry with
   its own distinct gloss.
3. **Inline cross-reference** — an anchor embedded mid-sentence in plain
   running prose (e.g. the proper noun `Aṃśa` mentioned inside `aṃśa`'s own
   definition: "...myth. véd. np. d'Aṃśa «Dispensateur»...", or a dual form
   like "du. aṃsau les deux angles d'un autel" inline within `aṃsa`'s
   gloss) — this is **not** a boundary; the surrounding text is part of the
   entry it's nested in and must not be truncated there.

The extractor (`is_entry_boundary`/`true_boundary_start` in
`heritage_dico_gloss_extract.py`) distinguishes (1)/(2) from (3) by checking
whether the anchor is preceded (modulo whitespace/entity noise) by a tag
close versus plain text — the first pass at this script naively broke on
*every* anchor and truncated entries like `aṃśa` mid-sentence before the
mythological gloss of `Aṃśa`; a second pass over-corrected and merged
`aṃśavāda`/`aṃśahara`'s distinct glosses into `aṃśa`'s. The boundary check
also had to resolve to the **start of the Devanagari span** (not the anchor
itself), else the next entry's headword text leaked into the tail of the
previous entry's gloss.

## Hand-verification (25 rows, exceeds the ≥20-row sanity check)

25 rows sampled (`random.seed(42)`, stratified by length — shortest 10,
longest 10, plus a random-25 pass) and checked against the raw DICO HTML:

- **Short one-liners** (`ayam`→"f.", `DOtI`/`aNgurI`/`aNgulI`/`azwapAda`/
  `azwAzazwi`/`vITI`/`kuwIra`→"id.") — confirmed correct: these are
  cross-reference stub entries in DICO itself (`id.` = "idem", pointing at a
  variant-spelling headword), not a parse truncation.
- **Long multi-clause mythological entries** (`Siva`, `udayana`, `kfzRa`,
  `cyavana`, `rAma`, `skanda`, `agasti`, `indra`, `arjuna`, `rAvaRa`, up to
  3,832 chars) — spot-checked `rAvaRa` end-to-end against the raw HTML: the
  extracted gloss ends exactly at the paragraph break before the next entry
  (`rāvaṇavadha`), confirming no overrun despite the entry running through
  several sub-clauses (genealogy, epithets, cross-refs) on separate lines.
- **Trailing "see also" links** (`sAyamaSana`→"...repos du soir. [see also]
  sāyam", `kOleyaka`→"...pali koleyyaka. [see also] kauleya") — initially
  misread as next-entry bleed-through during review; confirmed by raw-HTML
  inspection to be genuine trailing cross-references belonging to the
  current entry, which is why `cross_refs` captures both link-color classes
  used for cross-references (not just the inline-citation one).

## Where the French gloss adds information beyond the English/German Cologne glosses

- **`a`** (the privative prefix) — carries an explicit Greek/Latin/English
  cognate note absent from MW's entry: "gr. α, αν; lat. in; ang. un;
  fr. a, an" — a comparative-linguistics aside MW doesn't give for this
  headword.
- **`kOleyaka`** ("of noble family; dog") — gives the Pali cognate
  `koleyyaka`, a register/attestation detail (Pali parallel) not carried by
  the Sanskrit-only Cologne dictionaries.
- **`kfzRa`** (Kṛṣṇa) — the mythological sense expands with narrative detail
  (Vedic *asura* representing Dravidian peoples, later the 9th avatāra of
  Viṣṇu born at Mathurā) well beyond MW's terser gloss — useful editorial
  context, though this is prose commentary rather than a lexicographic fact
  and should be presented as Huet's own scholarly gloss, not merged silently
  into a Cologne field.
- **Redundant cases** — most grammatical/morphological entries (`aDruva`
  "mobile", `nizPala` "sans fruit, stérile", `SaraRada` "qui accorde sa
  protection") add essentially nothing beyond a direct French translation of
  the same sense MW already gives; the value-add is concentrated in
  mythological/proper-noun entries and etymological cognate notes, not in
  the bulk of ordinary headwords.

## License

LGPLLR content, composition with CC BY-SA approved by Gérard Huet
03-07-2026 (same terms as Phase 4/H105) — see
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
Phase 0/5. Treat `gloss_fr` as **quoted witness text with clear attribution**
to Huet's dictionary, not material to fold silently into Cologne-sourced
glosses.

## Consumer follow-ons (flagged, not built this session)

- **kosha UI surfacing** — whether/how kosha displays this as an additional
  witness field alongside the English/German Cologne glosses is a follow-on
  `@DECIDE`, not built here (see GTD).

_Dr. Mārcis Gasūns_
