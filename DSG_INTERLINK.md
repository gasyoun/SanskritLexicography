# Reusing & interlinking DSG (*Dictionary of Sanskrit Grammar*)

**DSG** = K. V. Abhyankar, *A Dictionary of Sanskrit Grammar* (Gaekwad's Oriental Series 134,
Baroda 1961) — **~4,000 technical grammatical terms**: every kṛt/taddhita **pratyaya**
(`ghañ`, `ṇvul`, `kta`, `tal`, `matup`…), augment, substitute, Pāṇinian term, and grammarian /
text name, each with numbered (chronological) senses + citations to the Mahābhāṣya, Kāśikā,
Vākyapadīya, Aṣṭādhyāyī, Prātiśākhyas. Browsable at
[samskrtam.ru/sanskrit-lexicon/dsg/](https://samskrtam.ru/sanskrit-lexicon/dsg/).

It is the natural companion to the affix tooling here: those 27 affixes ARE DSG headwords, so a
learner clicking `ghañ` in the [affix explorer](RussianTranslation/research/affix_explorer.html)
should land on its full Pāṇinian definition.

## Decisions (user, 2026-06-24)
- **Mode: ingest + deep-link** (both). Pull a structured DSG locally to enrich/cross-reference,
  AND deep-link each term to its canonical entry on samskrtam.ru.
- **Surfaces (all four):** affix explorer/poster/quiz · WhitneyRoots reader · pwg_ru merged cards ·
  the CDSL spine (DSG as another cross-linked dictionary).
- **Source:** user will provide the DSG digitization file.
- **Links:** we will (re)build the samskrtam.ru DSG page so every term has a **stable per-term link**.

## The stable per-term link scheme

**One static page, one SLP1 `#`-anchor per entry:**

```
https://samskrtam.ru/sanskrit-lexicon/dsg/#t-<slp1>
   ghañ → #t-GaY      ṇvul → #t-Rvul     kta → #t-kta     ṭāp → #t-wAp     lyuṭ → #t-lyuw
```

Why SLP1 (`<k1>`) as the anchor key:
- **ASCII / URL-safe** — no percent-encoding, unlike IAST `ṇvul` or Devanāgarī.
- **Unique & reversible** — `ghañ` vs `ghana` don't collide (IAST-stripped `ghan` would).
- **The ecosystem's join key** — it's exactly the CDSL `<k1>`, so DSG ↔ MW ↔ Apte ↔ Whitney
  roots all join on the *same* string. One key, every cross-link.
- **No backend needed** — a single page + `id="t-<slp1>"` anchors gives durable deep links that
  survive forever (no server, no DB, like the rest of `sanskrit-lexicon/`).

Alternatives considered: per-term files `…/dsg/GaY.html` (more files, same effect — fine if you
prefer it); a `?q=` search endpoint (needs a backend, links are less stable). The anchor scheme is
the lowest-maintenance and is what [`build_dsg.py`](RussianTranslation/research/build_dsg.py) emits.

## Pipeline — [`build_dsg.py`](RussianTranslation/research/build_dsg.py)

1. **You drop** the CDSL DSG digitization (`<L>/<k1>/<k2>` `.txt`, like
   [`pd.txt`](SanskritLexicography/../SanskritSpellCheck/external_src/pd/pd.txt)) under
   `RussianTranslation/research/external/dsg.txt` (gitignored).
2. `python build_dsg.py ingest external/dsg.txt` →
   - `dsg.json` — structured `{k1(slp1), term_iast, term_deva, body, slug}` per entry.
   - `dsg.html` — the **deep-linkable static page** (`id="t-<slp1>"` per entry + filter box) to
     deploy at `samskrtam.ru/sanskrit-lexicon/dsg/` (the "remake with stable links").
   - `dsg_affix_crosswalk.tsv` — affix pratyaya → DSG entry, **verified present**.
3. Already shipped (no source needed): `python build_dsg.py anchors` →
   [`affix_dsg_anchors.tsv`](RussianTranslation/research/affix_dsg_anchors.tsv) — the 27 affix
   pratyayas → their SLP1 anchor + DSG URL (the crosswalk seed; verified against `dsg.json` at ingest).

## Interlinking the four surfaces

| Surface | Link to DSG | How |
|---|---|---|
| **Affix explorer / poster / quiz** | each pratyaya pill → its DSG entry | `affix_pedagogy.json` gains a `dsg_url` field from `affix_dsg_anchors.tsv`; the explorer renders a `📖 DSG` link per card |
| **WhitneyRoots reader** | grammar §§ / technical terms → DSG | the reader already links Wikisource §§; add a DSG link for any term whose SLP1 is a DSG `<k1>` |
| **pwg_ru merged cards** | grammar abbreviations / Pāṇinian terms → DSG | resolve `<ab>`/term tokens against `dsg.json` keys at render |
| **CDSL spine** | DSG ↔ MW ↔ Apte ↔ roots | all join on `<k1>` (SLP1); DSG entries for affixes reverse-link to the affix explorer + Whitney roots |

**Reverse links** (DSG → us): a DSG affix entry (`ghañ`) links back to the affix explorer
(`affix_explorer.html#…`) and to the roots that take it (via the affix→root examples), closing the loop.

## What's done now vs. waiting on the source

- ✅ Link scheme fixed; ingest + site generator written; **affix→DSG anchor seed shipped**
  (`affix_dsg_anchors.tsv`, 27 terms, SLP1 verified).
- ⏳ **Needs the DSG source file** → run `build_dsg.py ingest` to produce `dsg.json` + the
  deep-linkable `dsg.html` (deploy to samskrtam.ru) + the verified crosswalk, then wire the live
  `dsg_url` into the affix tools and the reader.
- ⏳ Confirm: deploy the generated `dsg.html` at `…/dsg/` (replacing the current page), or host the
  anchored page alongside it?
