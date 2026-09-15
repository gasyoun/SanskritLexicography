_Created: 03-09-2026 · Last updated: 15-09-2026_

# cyrillic_proper_noun_slp1.meta.md — metadoc for `cyrillic_proper_noun_slp1.tsv`

_Created: 03-09-2026 · Last updated: 15-09-2026 (H3985: table built, GAPS §6 half-closed, FINDINGS §629 added and §495 corrected · H4750: +88-row onomasticon backfill, 534→622 rows)_

This is a **metadoc** — a document *about* a dataset. Its subject is
[RussianTranslation/data/cyrillic_proper_noun_slp1.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv).
It does not duplicate the data; it records everything *around* it.

## Subject

- **Dataset:** [RussianTranslation/data/cyrillic_proper_noun_slp1.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv) — 622 rows, 631 distinct SLP1 keys, two intake passes (H3985 witness-first 534 · H4750 onomasticon-first 88).
- **Purpose:** the one sanctioned mapping from a Cyrillic Sanskrit proper noun (as printed in Russian scholarly indices) to an SLP1 key. It exists so that no session ever invents Cyrillic→SLP1 *character rules*, which [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §60 established are unsafe (Russian orthography collapses distinctions SLP1 needs: retroflex/dental, long/short, aspirates).
- **Audience:** any pipeline aligning a Russian-language name index, glossary or translation against Sanskrit keys — `pwg_ru`, `mw_ru`, SamudraManthanam name glossaries, csl-atlas onomastic work.
- **Schema:** `cyrillic · slp1 · iast_witness · validation · onomasticon · witness_count · seeds`.
  - `iast_witness` — the IAST form of the name: either the form actually printed beside the Cyrillic name in the source (H3985 rows) or the IAST rendering of the dictionary headword the key was copied from (H4750 rows).
  - `validation` tiers: `onomasticon` 534 · `lexicon` 50 · `iast-witness-only` 38.
  - `witness_count` / `seeds` — how many source files attested the pair, and which.

## The invariant

`rule_derived_keys: 0` is what makes this table citable. Nothing is ever transliterated *out of* Cyrillic. Two intake paths preserve that, each with the key taken from a named authority rather than from the Russian spelling:

1. **Witness-first (H3985):** key = `sanscript.transliterate(iast_witness, IAST, SLP1)` over a witness a human typeset next to the Cyrillic form in the seed line.
2. **Onomasticon-first (H4750):** key COPIED VERBATIM from a Cologne `inm`/`pui` `<k1>` headword; the project's IAST→Cyrillic proper-name renderer ([src/iast_to_cyrillic.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py)) is used only as an EXACT-MATCH join key to locate the corpus-attested Russian spelling in the fully-Cyrillic indices; render-collapsed spellings (one Cyrillic form, 2+ keys — 96 of them, e.g. Бхадра ← `BadrA|Badra`) are recorded in [reports/H4750_cyr_slp1_backfill.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4750_cyr_slp1_backfill.json) and never shipped.

**Sync rule:** change the table ⇒ refresh the validation reports **in the same PR** — H3985 via [tools/h3985_cyr_slp1_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_cyr_slp1_table.py), H4750 backfills via [tools/h4750_cyr_slp1_backfill.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4750_cyr_slp1_backfill.py) (`--selftest` hermetic, `--apply` writes table + report; stated in [CLAUDE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) § Cyrillic proper nouns).

## Provenance

- **Created:** 03-09-2026, handoff H3985 (Opus 5, `claude-opus-5`), shipped in
  [v1.144.145](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.145) /
  [v1.144.146](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.146).
- **Backfilled:** 15-09-2026, handoff H4750 (OxAlpha, `zai-coding-plan/glm-5.3-flash`) — +88 rows from inm/pui `<k1>`,
  onomasticon tier 446→534, coverage Эрман–Тёмкин 36.4→46.7 % / Гринцер 33.1→43.3 % / Потапова 39.3→43.3 %.
- **Predecessor:** [tools/gaps_s6_cyrillic_name_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/gaps_s6_cyrillic_name_probe.py) (H1746, Grok 4.5) — the probe that named the recoverable path ("a validated proper-noun LOOKUP table seeded from IAST-bearing indices … not character rules"). Its own seed counts were **wrong** and are corrected by FINDINGS §629: it hard-coded a Windows `SEARCH_ROOTS` path and rglob'd worktree duplicates, inflating 32/20 into 61/47.
- **Seed inventory:** [tools/h3985_seed_inventory.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_seed_inventory.py) — 85 files scanned, 32 carry inline IAST, 20 are Cyrillic-heavy with none.
- **Epistemic residue:** [GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) §6 🟠 → 🟡 HALF-CLOSED; [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §629 (new) and §495 (corrected).

## What it does NOT cover

Measured coverage of the fully-Cyrillic name indices after the H4750 backfill is **~43–47 %, not a half**:
Erman–Temkin 223/478 = 46.7 % · Кадамбари 170/393 = 43.3 % · Потапова 141/326 = 43.3 %.
(The Potapova HTML twin reports 2/77 — a disclosed parser artifact of that file's markup, not a coverage claim.)
Still unkeyed after H4750: a **146-pair unambiguous join pool** the 88-row census batch left unshipped, **96 render-collapsed
ambiguous spellings** (disclosed in the H4750 report), and whatever neither intake reaches. Closing those needs the same
deterministic join at a bigger cap, plus human adjudication for the genuinely ambiguous — not more code, and never a character rule.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Supply an onomasticon (e.g. a digitised Sanskrit name dictionary) for the 20 pure-Cyrillic indices | The only path that raises coverage without violating the no-rules invariant | **done 15-09-2026** — H4750 used the existing inm/pui Cologne onomasticon this way (+88 rows, tier recount 446→534) |
| 2 | Fix the Potapova HTML twin's parser so its 2/77 becomes a real number | A disclosed artifact still reads as a coverage failure to anyone skimming the report | parked — cosmetic; the TSV twin already carries the real 43.3 % |
| 3 | Ship the 146-pair unambiguous join pool the census batch left unshipped | Same deterministic tool, one `TARGET_NEW_ROWS` bump, zero new epistemic surface | open — natural follow-up to H4750 |
| 4 | Extend seeds beyond RussianTranslation (SamudraManthanam name glossaries were unreachable on this box) | More IAST-bearing witnesses ⇒ more rows at zero epistemic cost | parked — cross-repo, needs the SamudraManthanam clone present |

_Dr. Mārcis Gasūns_
