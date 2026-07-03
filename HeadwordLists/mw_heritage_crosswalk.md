# MW ↔ Heritage entry-level crosswalk

_Created: 03-07-2026 · Last updated: 03-07-2026_

Phase 2 of the [Heritage reuse roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md):
which Monier-Williams entries the Sanskrit Heritage Platform's lexicon covers,
built from the mirror's own MW↔DICO alignment (see
[HERITAGE_MIRROR_INVENTORY.md](HERITAGE_MIRROR_INVENTORY.md)) — no OCR or
fuzzy matching needed, since covered MW entries carry the DICO anchor key
directly (`<a name="H_<key>">`).

**Output:** [`mw_heritage_crosswalk.tsv`](mw_heritage_crosswalk.tsv) —
`mw_key1` (SLP1, via `huet_coverage.py`'s validated VH→IAST→SLP1 transcoder)
· `covered_flag` (`1`/`0`) · `heritage_entry_anchor` (`DICO/<file>.html#<key>`
or empty). Built by [`heritage_mw_crosswalk.py`](heritage_mw_crosswalk.py),
reported by [`heritage_crosswalk_report.py`](heritage_crosswalk_report.py).

## Coverage

| | count | % |
|---|--:|--:|
| MW entries (unique `mw_key1`) | 185,803 | — |
| Heritage-covered | 25,140 | **13.5 %** |
| covered rows resolved to a DICO anchor | 24,549 | 97.7 % of covered |

The 2.3 % unresolved-anchor remainder is a documented limitation, not a bug:
MW's plain anchor drops the `#N` homonym-disambiguation suffix that DICO
always keeps (e.g. MW's bare `a.mzaka` vs DICO's `a.mzaka#1`/`a.mzaka#2`); the
script picks the first homonym as a fallback, and a handful of keys have no
DICO-side match at all (see the script's homonym-fallback comment).

## Relation to the DCS-attested and kosha frequency layers

| | DCS-attested | in kosha's frequency layer |
|---|--:|--:|
| among Heritage-covered (25,140) | 15,998 (**63.6 %**) | 15,998 (**63.6 %**) |
| among all MW (185,803) | 53,660 (28.9 %) | 53,660 (28.9 %) |

The two right-hand columns are identical because
[kosha's `lemma_frequency.tsv`](https://github.com/gasyoun/kosha/blob/main/data/frequency/build_frequency_layer.py)
is itself built from the DCS corpus (VisualDCS `archive.sqlite`) — not an
independent corroboration, just the same DCS signal joined via kosha's SLP1
key. Still useful: of the 15,998 covered+ranked lemmas, the median kosha
frequency rank is **12,526** and **807 are in the kosha top-1,000** — Heritage
coverage skews toward genuinely common vocabulary (63.6 % corpus-attested vs.
28.9 % for MW as a whole), the same "reader's working lexicon, not the full
dictionary spine" pattern documented for the 2014 stem list in
[Huet-INRIA-Wordlist-vs-Cologne.md §4](Huet-INRIA-Wordlist-vs-Cologne.md).

## Hand-verification (12 sampled rows, per the roadmap's ≥20-row sanity check
combined with the 8 non-random boundary cases below = 20 total)

12 covered rows were checked against the actual `DICO/*.html` files (anchor
exists at the claimed file#key) — all 12 confirmed
(`devatva`→`DICO/33.html#devatva`, `viniyoga`→`DICO/59.html#viniyoga`,
`vanizWa`→`DICO/57.html#vani.s.tha`, `uttan`→`DICO/14.html#uttan`,
`tatpUrva`→`DICO/28.html#tatpuurva`, `uccEHSiras`→`DICO/13.html#uccai.hziras`,
`damaGoza`→`DICO/31.html#damagho.sa`, `daRqaDAra`→`DICO/31.html#da.n.dadhaara`,
`akledya`→`DICO/1.html#akledya`, `avanDya`→`DICO/7.html#avandhya`,
`aBicAra`→`DICO/5.html#abhicaara`, `BUzaRa`→`DICO/47.html#bhuu.sa.na`).
8 boundary cases were checked by hand against the raw MW HTML: `a` (first
`a`-homonym, correctly uncovered — no `H_` anchor in the source), 5 more
uncovered derived forms (`aMSakaraRa`, `aMSakalpanA`, `aMSaprakalpanA`,
`aMSapradAna`, `aMSabhAgin`, all confirmed `H_`-less in `MW/1.html`), and the
homonym-fallback case `aMSaka` (`H_a.mzaka#1`/`#2` in MW resolving to
`DICO/1.html#a.mzaka#1`, confirming the fallback logic).

## Consumer follow-ons (flagged, not built this session)

- **kosha ingest** — join `mw_heritage_crosswalk.tsv` onto kosha's `lemmas`
  table via `mw_key1`/`lemma_slp1` as a third coverage witness alongside the
  DCS-derived frequency layer. Needs its own H### handoff.
- **csl-atlas witness column** — add a Heritage-covered boolean/anchor column
  to the MW entry witness set. Needs its own H### handoff.

_Dr. Mārcis Gasūns_
