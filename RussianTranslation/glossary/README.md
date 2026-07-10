# Sanskrit → Russian glossary (surface · lemma · root)

_Created: 01-07-2026 · Last updated: 01-07-2026_

**🔎 Live searchable glossary + all data:** **[gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian)**
→ <https://gasyoun.github.io/SanskritRussian/> — type an SLP1 root/word (`gam`, `BU`) or a
Russian word and browse the ranked translations. The glossary has its own repo because this
repo's GitHub Pages slot serves the PWG article dashboard (`gh-pages` branch). **This directory
holds only the generation pipeline** (`../src/build_*.py`) — the data is git-ignored here
(regenerate locally); the committed data + live site live in that repo.

A full inventory of **how every Sanskrit word is rendered into Russian** in the aligned
corpus, at three granularities:

| Layer | Question it answers | Key |
|---|---|---|
| **surface form** | how is the *attested form* `gamemahi` translated? | corpus SLP1 form |
| **lemma / stem** | how is the *stem* `mahāratha` / verb-lemma `saṃgam` translated? | DCS / Vidyut lemma |
| **root** | how is *√gam* translated across **all** its forms and prefixed verbs? | verb root (dhātu) |

Built from [`RussianTranslation/src/corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_lexicon.jsonl)
— **1,091,528** word-aligned Saṃskṛta→Russian tokens (SLP1), the alignment asset described in
[`RENOU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md).
Scope: **everything, all n ≥ 1** — hapax kept, `kind=translation` **and** `kind=commentary`
kept (each entry records the split).

## The `gam` example, answered

`root_glossary` for **√gam** aggregates **678 surface forms** across **44 verb lemmas**
(`gam, āgam, saṃāgam, abhigam, adhigam, upagam, anugam, …`), **7,116 occurrences**, ranked:

> пришел (195) · отправился (176) · ушел (140) · пришли (100) · достигает (99) · явился (92)
> · ступай (79) · пошел (77) · отправились (77) · идет (73) · удалился (73) · направился (64) …

The four `gamemahi` lines you started from are one surface entry inside this rollup.

## Files

The scripts regenerate these locally; here they are **git-ignored** (the committed copies live
in [gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian)). The 140 MB raw
`surface_glossary.jsonl` exceeds GitHub's 100 MB file limit, so it ships (in that repo) as
`surface_glossary.jsonl.gz` **and** as a per-initial-letter split under `surface/<X>.jsonl`
(26 parts, max ~22 MB; `cat surface/*.jsonl` reconstructs the whole). `index.html` there is the
searchable front-end over the root/lemma TSVs.

Bucket filenames are **case-folded to upper** (`a` and `A` share one file): SLP1 is
case-significant but Windows' filesystem is case-insensitive, so separate `a`/`A` files would
collide and truncate. The phonemic distinction is preserved inside each record's `slp1` field.

| File | What |
|---|---|
| `surface_glossary.tsv` + `surface/<X>.jsonl` (+ `.jsonl.gz`) | **Layer 1** — 190,838 forms → Ru with counts, registers, works, kinds |
| `md/surface/<X>.md` | human-readable surface glossary, one file per initial SLP1 letter |
| `lemma_glossary.jsonl` / `.tsv` + `md/lemma/` | **Layer 2** — 40,370 lemmas → Ru (nouns' stem, verbs' lemma) |
| `root_glossary.jsonl` / `.tsv` + `md/root/` | **Layer 3** — 2,021 verb roots → Ru (aggregated over lemmas & forms) |
| `dcs_form2lemma.tsv` | DCS map: 408,660 `form → lemma` pairs (SLP1) |
| `dcs_lemma2root.tsv` | DCS map: `verb-lemma → root` (via DCS root inventory, longest-suffix) |
| `vidyut_form2lemma.tsv` | Vidyut fallback: 28,567 DCS-missed forms → lemma/pos |
| `surface_dcs_misses.tsv` | forms DCS could not lemmatize (stable **input to the Vidyut pass**) |
| `surface_unresolved.tsv` | forms **no tier** resolved (DCS+Vidyut+marker) — the typology input |
| `ambiguity_homographs.tsv` | forms whose top DCS lemmas span different POS / are close in count |

Every rollup record carries a `source` field (`dcs` vs `vidyut`) so provenance is auditable.

## Method

The corpus stores **only surface forms** — no lemma. Roots/lemmas are attached by a
*context-free* join (robust for an aggregate glossary; a per-passage alignment would fight
270 texts' mismatched ref schemes):

1. **DCS morphology (primary).** [VisualDCS `dcs_full.sqlite`](https://github.com/gasyoun/VisualDCS/tree/main/src/DCS-data-2026)
   — 5.69M annotated tokens (IAST). Grouped to a `form → lemma` map, transcoded IAST→SLP1
   (`indic_transliteration.sanscript`). Root for a prefixed verb lemma = the **longest member
   of DCS's own simple-root inventory** that is a suffix of the lemma (`saṃgam` → `gam`),
   which sidesteps preverb sandhi (`uddhṛ` ← preverb `ut`, not `ud`).
2. **Vidyut kosha (fallback).** Forms DCS misses are lemmatized by the Pāṇinian FST
   (`vidyut.kosha`, v0.4.0). Tinanta → dhātu (root); Subanta → stem.
3. **Morpheme-marker recovery.** Forms both lexica miss but that carry a corpus boundary
   mark (`A+gam` = ā+√gam) are split on `[+-]`: the joined string is retried as a form, else
   the rightmost element is taken when it is a known root/lemma (`source='marker'`).
4. **Unresolved** forms are kept in Layer 1 and characterised below.

Join keys strip a leading avagraha/apostrophe on both sides (`'gacchat` == `gacchat`).
Homographs: a form's Ru distribution is attributed to its **highest-count** lemma; alternates
are logged in `ambiguity_homographs.tsv`, never double-counted.

### Coverage (of 190,838 distinct forms / 1,091,528 tokens)

| Stage | forms resolved | token coverage |
|---|--:|--:|
| DCS only | 80,949 (42.4 %) | 79.1 % |
| + Vidyut fallback | 109,516 (57.4 %) | 86.6 % |
| + morpheme-marker recovery | 111,996 (58.7 %) | **87.1 %** |
| unresolved | 78,842 (41.3 %) | 12.9 % |

Distinct-form hit rate is far below token coverage because the misses are the **rare long
tail** — DCS/Vidyut resolve nearly every common form.

## Failure typology (78,842 unresolved forms · 140,667 tokens)

| Type | forms | tokens | Example | Why it misses |
|---|--:|--:|---|---|
| unrecognized simplex | 48,646 | 91,548 | `maratejasi`, `ABArizam` | rare inflection / sandhi-altered stem absent from both lexica |
| long compound (≥14 chars) | 20,823 | 25,482 | `ADArmikajanAvfta`, `ADUtadvajapawam` | samāsa the FST won't split without a *chedaka* |
| ends in a known root | 4,695 | 10,267 | `ABAz`, `ABijIvanam` | derived stem, but not a bare lemma either lexicon lists |
| proper name | 3,094 | 8,945 | `ABIrya` (Абхиры), `ABar` | names/vocatives outside the lexica (Ru gloss capitalised) |
| morpheme-marker residual | 1,389 | 2,312 | `A-brahma-BuvanAt` | has `+`/`-` marks but rightmost element is itself inflected, not a bare root |
| short form / particle | 195 | 2,113 | `ABf`, `Ahf` | too short / clitic |

**Join-side edge cases** (handled, not part of the 78,842):

- **Homographs** — 9,521 forms carry ≥2 DCS lemmas of differing POS/near-equal count
  (`ambiguity_homographs.tsv`). Attributed to the dominant lemma.
- **Morpheme markers** — corpus forms embedding `+`/`-` marks (`A+gam` = ā+√gam) are now
  recovered (tier 3, `source='marker'`, 2,480 forms); only 1,389 whose rightmost element is
  itself inflected remain unresolved.
- **Avagraha / apostrophe** — leading `'`/`’` normalised away before the join.
- **Compound-split spacing** — a few corpus forms keep a space (`vācas pati`); these key on the
  spaced string.
- **Nominal roots** — Layer 3 (root) is **verbal only**; a noun stem has no verbal root in this
  pipeline, so nominal lemmas appear at Layer 2 but not Layer 3 by design.

## Regenerate

From [`RussianTranslation/src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src):

```sh
python build_dcs_maps.py            # DCS form→lemma + lemma→root maps   (needs VisualDCS dcs_full.sqlite)
python build_surface_glossary.py    # Layer 1
python build_rollup_glossaries.py   # 1st pass: emits surface_dcs_misses.tsv (Vidyut input)
python build_vidyut_fallback.py <kosha_dir>   # lemmatize the DCS misses (needs vidyut.download_data())
python build_rollup_glossaries.py   # 2nd pass: folds in Vidyut + marker tier -> Layers 2 & 3
```

Two-pass bootstrap: the rollup emits the DCS-miss list the Vidyut stage consumes, so run it
once before Vidyut and once after. `surface_dcs_misses.tsv` is deterministic (snapshotted
before the Vidyut supplement), so the second pass does not disturb the Vidyut input.

Vidyut data: `python -c "import vidyut; vidyut.download_data('vidyut_data')"` then pass
`vidyut_data/kosha` to the fallback. Transcoding uses `indic_transliteration`; both are pip-installable.

_Dr. Mārcis Gasūns_
