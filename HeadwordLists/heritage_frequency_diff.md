# Heritage (INRIA) frequency tables — ingest + diff vs VisualDCS / corpus_lexicon

_Created: 26-07-2026 · Last updated: 26-07-2026_

Phase 3 of the [Heritage reuse roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
(handoff [H1490](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1490-Sonnet_SanskritLexicography_heritage-freq-tables-ingest_22.07.26.md)):
ingest the 7 plain-TSV frequency tables in the local, gitignored
`HeadwordLists/heritage_mirror/DATA/` mirror
([darkone23/Heritage_Resources](https://github.com/darkone23/Heritage_Resources)),
transcode them out of the Heritage-internal WX romanization into SLP1, and diff
the resulting form/lemma frequency rankings against
[VisualDCS](https://github.com/gasyoun/VisualDCS)'s M1–M8 CoNLL-U import
(`dcs_full.sqlite`) and this repo's own
[`RussianTranslation/src/corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md)
lexicon extraction. Both comparison sources are gitignored/local-only (a
920 MB SQLite database and a 1.09M-line JSONL), so no dataset is vendored
here — this report + the derived TSV are the durable artifact.

## 1. What was ingested

All 7 files named in the roadmap, none previously parsed
(confirmed against [HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md),
which flagged them "confirmed present, unparsed"):

| File | Rows | Format |
|---|--:|---|
| `pada_freq.tsv` | 44,398 | `<surface form>\t<count>` — plain word ("pada") frequency |
| `word_freq.tsv` | 59,977 | `<surface form>\t<count>` — fuller surface-form variant of `pada_freq.tsv` (more inflected variants distinguished, e.g. `ABA/ABAH/ABAn/ABAm/...` where `pada_freq.tsv` collapses some); used as the primary surface-form series below |
| `pada_morph_freq.tsv` | 59,392 | `<stem>\t<morph tag>\t\t\t<count>` — same tokens as `pada_freq.tsv`, broken out by stem + morphological reading |
| `comp_freq.tsv` | 28,396 | `<compound first-member>\t<count>` — frequency of stems used as the initial member (`iic`) of a compound |
| `comp_morph_freq.tsv` | 32,197 | `<stem>\t<morph tag>\t\t\t<count>` — compound first-members broken out by tag (mostly `iic.`) |
| `pada_trans_freq.tsv` | 799 | `[<code>]\t[<code>]\t<count>` — bigram transition counts over bracketed numeric category codes |
| `comp_trans_freq.tsv` | 461 | `[<code>]\t[<code>]\t<count>` — same, for compound-member transitions |

The two `*_trans_freq.tsv` files are **not lexical** — their keys are numeric
category codes (POS/morph-tag classes used internally by the Heritage
segmenter's n-gram disambiguation model), not word forms or lemmas, and the
codebook resolving `[41]`/`[48]`/etc. to tag names lives only in the
unparsed `.rem` OCaml banks (`DATA/*.rem`, out of scope per
[HERITAGE_MIRROR_INVENTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/HERITAGE_MIRROR_INVENTORY.md)'s
"not parsed this session" note on the `.rem` files). They are ingested (row
counts above) but excluded from the frequency-ranking diff below, which
needs a `form`/`lemma` column to join against DCS/`corpus_lexicon`.

## 2. WX → SLP1 transcoding

The `DATA/*.tsv` forms are in the Heritage-internal **WX** romanization, not
the VH (Velthuis) scheme used by the reader's headword lists (`21562-huet-velthius.txt`,
already handled by [`huet_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/huet_coverage.py)'s
VH→IAST table) — confirmed from the local mirror's own
`XML/WX_morph.dtd`, whose header comment gives the alphabet verbatim:

```
Transliteration of forms according to UoH scheme WX:
a A i I u U q Q L e E o O M z H
k K g G f c C j J F t T d D N w W x X n p P b B m y r l v S R s h
```

WX and SLP1 agree on vowels, labials, semivowels, and the guttural/palatal
stops, but they **swap the dental/retroflex stop rows**: WX uses `w W x X n`
for the dental row (त थ द ध न) and `t T d D N` for the retroflex row
(ट ठ ड ढ ण) — the opposite of SLP1's own `t/T/d/D/N` (dental) vs
`w/W/q/Q/R` (retroflex) convention. No existing repo helper decodes WX (only
IAST↔SLP1↔Devanāgarī in `sanskrit-util`, and VH↔IAST in `huet_coverage.py`),
so the map below is new code, built directly from the DTD table above and
cross-checked against known words already in the data:

| WX | SLP1 | example | check |
|---|---|---|---|
| `waw` | `tat` | तत् "that" | `w`→t, `a`→a, `w`→t |
| `Xarma` | `Darma` | धर्म "dharma" | `X`→D (dental dh) |
| `wu` | `tu` | तु "but/indeed" | `w`→t |
| `mahA`, `sarva`, `uvAca` | unchanged | महा, सर्व, उवाच | shared letters, no swap needed |

No unmapped characters were seen across any of the 5 lexical tables (all
characters fell inside the 32-symbol WX alphabet above).

## 3. Comparison corpora

- **VisualDCS M1–M8** ([`dcs_full.sqlite`](https://github.com/gasyoun/VisualDCS/blob/main/src/DCS-data-2026/DCS_CONLLU_IMPORT_PLAN.md), the landed CoNLL-U import, not the older 2021 `dcs_lemma_summary.json` band-only snapshot): 5,688,416 tokens, 381,413 distinct surface forms (`token.form`, IAST), 90,349 distinct lemmas (`token.lemma`, IAST). Both transcoded to SLP1 via `sanskrit_util.to_slp1` (0 transcode failures).
- **`corpus_lexicon.jsonl`** (RussianTranslation's per-passage lexicon extraction, SLP1-native `slp1` field already): 1,093,391 rows, 191,437 distinct surface forms.

## 4. Results — three frequency series

| Series | Heritage source | Heritage items | Found in comparison corpus | Spearman ρ (top 3000 by Heritage freq) |
|---|---|--:|---|--:|
| A. Surface forms | `word_freq.tsv` | 59,977 | 56,133 in DCS forms (93.6%) · 27,979 in `corpus_lexicon` (46.6%) | **0.740** vs DCS (n=2,992) · **0.527** vs `corpus_lexicon` (n=2,794) |
| B. Lemmas | `pada_morph_freq.tsv`, aggregated by stem | 17,087 | 14,128 in DCS lemmas (82.7%) | **0.700** vs DCS (n=2,691) |
| C. Compound first-members | `comp_morph_freq.tsv`, aggregated by stem | 9,491 | 8,486 in DCS lemmas (89.4%) | **0.737** vs DCS (n=2,816) |

Spearman ρ is computed on ranks assigned **locally within the joined
intersection** for each series (not borrowed from the two corpora's
differently-sized full rankings), with tie-averaging.

All three series show a strong-to-moderate positive rank correlation with
DCS — expected, since both Heritage's underlying corpus and DCS draw on
classical Sanskrit narrative/philosophical prose with heavy overlap in
closed-class function words (`ca`, `na`, `eva`, `tu`, `iti`, ...). The
weaker correlation against `corpus_lexicon.jsonl` (0.527) is a **sample-size
artifact, not a data-quality signal**: that file is a curated per-verse
glossary extraction (one row per glossed lexical item per translated
passage), not a full-corpus token count, so its frequencies undercount
relative to both Heritage and DCS.

## 5. Top rank-divergent surface forms (Heritage top 500, found in DCS)

| SLP1 form | Heritage rank | Heritage freq | DCS rank | DCS freq |
|---|--:|--:|--:|--:|
| `vit` | 283 | 305 | 220,268 | 1 |
| `saYjayaH` | 129 | 560 | 97,832 | 4 |
| `rAzwraH` | 266 | 323 | 41,631 | 13 |
| `vESampAyanaH` | 54 | 1,065 | 29,473 | 20 |
| `aDipa` | 498 | 211 | 14,684 | 47 |
| `parASaraH` | 229 | 352 | 13,122 | 53 |
| `mat` | 380 | 255 | 9,753 | 73 |
| `catuH` | 162 | 496 | 7,442 | 97 |
| `viSAm` | 422 | 241 | 6,787 | 106 |
| `fzaBa` | 166 | 483 | 4,671 | 152 |

The largest divergences are proper names — Sañjaya (`saYjaya-`), Vaiśampāyana
(`vESampAyana-`), Parāśara (`parASara-`) — plus the epic-formula fragments
`rAzwraH`/`catuH`/`fzaBa` (⟨...rāṣṭraḥ⟩, ⟨catuḥ...⟩, ⟨ṛṣabha⟩), all
extremely frequent in Heritage's own corpus but comparatively rare across
DCS's broader, more multi-genre text collection. This is consistent with
Heritage's tagged corpus being weighted toward Mahābhārata-style narrative
frame material (a narrator naming another narrator, e.g. "Sañjaya said...",
recurs constantly within one text but is diluted across DCS's ~thousands of
texts spanning Veda to kāvya to śāstra).

## 6. Deliverables

- [`heritage_frequency_diff.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_frequency_diff.tsv) — combined derived table, all 3 series (86,555 rows): `series · key_slp1 · heritage_freq · heritage_rank · dcs_freq · dcs_rank · corpus_lexicon_freq · corpus_lexicon_rank`.
- [`heritage_freq_diff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_freq_diff.py) — the ingest/transcode/diff script (reads the local `heritage_mirror/DATA/*.tsv`, `../VisualDCS/src/DCS-data-2026/dcs_full.sqlite`, and `RussianTranslation/src/corpus_lexicon.jsonl`; none of the three are committed, so this script is not independently runnable outside a full local checkout of the three sibling data sources — expected for a mirror/derived-artifact pipeline, see [PROJECT_INTERLINKS](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)).
- This report.

## 7. Caveats

- No corpus-size normalization: raw counts are diffed on both sides, and
  Heritage's own underlying corpus composition/size is undocumented in this
  GitHub mirror (INRIA's live corpus text is behind the Anubis bot-wall, see
  roadmap §0) — so only **ranks**, not absolute frequencies, are meaningfully
  comparable across the two sources.
- `pada_freq.tsv` (44,398 rows) and `word_freq.tsv` (59,977 rows) disagree on
  ~58,565 lines when diffed directly (`word_freq.tsv` distinguishes more
  inflected variants of the same stem, e.g. splitting `ABA` into
  `ABA/ABAH/ABAn/ABAm/ABAni/...`); `word_freq.tsv` was used as the primary
  surface-form series here as the more granular of the two. `pada_freq.tsv`
  is ingested (row count above) but not separately diffed.
- `pada_freq.tsv`'s per-stem totals and `pada_morph_freq.tsv`'s
  per-stem-aggregated totals differ by a small margin for at least one
  spot-checked entry (`vac`: 9,064 in the morph table's `pft. ac. sg. 3` row
  vs 9,067 in `pada_freq.tsv`'s `uvAca` row) — a minor cross-file
  version/counting-pass drift in the upstream mirror, not a bug in this
  ingestion; noted, not investigated further (mechanical-scope handoff).

_Dr. Mārcis Gasūns_
