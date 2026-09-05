_Created: 03-09-2026 · Last updated: 05-09-2026_

# cyrillic_proper_noun_slp1.meta.md — metadoc for `cyrillic_proper_noun_slp1.tsv`

_Created: 03-09-2026 · Last updated: 03-09-2026 (H3985: table built, GAPS §6 half-closed, FINDINGS §629 added and §495 corrected)_

This is a **metadoc** — a document *about* a dataset. Its subject is
[RussianTranslation/data/cyrillic_proper_noun_slp1.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv).
It does not duplicate the data; it records everything *around* it.

## Subject

- **Dataset:** [RussianTranslation/data/cyrillic_proper_noun_slp1.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/cyrillic_proper_noun_slp1.tsv) — 534 rows, 518 distinct Cyrillic forms, 532 distinct SLP1 keys, 92,442 bytes.
- **Purpose:** the one sanctioned mapping from a Cyrillic Sanskrit proper noun (as printed in Russian scholarly indices) to an SLP1 key. It exists so that no session ever invents Cyrillic→SLP1 *character rules*, which [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §60 established are unsafe (Russian orthography collapses distinctions SLP1 needs: retroflex/dental, long/short, aspirates).
- **Audience:** any pipeline aligning a Russian-language name index, glossary or translation against Sanskrit keys — `pwg_ru`, `mw_ru`, SamudraManthanam name glossaries, csl-atlas onomastic work.
- **Schema:** `cyrillic · slp1 · iast_witness · validation · onomasticon · witness_count · seeds`.
  - `iast_witness` — the IAST form actually printed beside the Cyrillic name in the source. **A row without one cannot exist.**
  - `validation` tiers: `onomasticon` 446 · `lexicon` 50 · `iast-witness-only` 38.
  - `witness_count` / `seeds` — how many source files attested the pair, and which.

## The invariant

`rule_derived_keys: 0` in [reports/H3985_cyr_slp1_validation.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3985_cyr_slp1_validation.json)
is what makes this table citable. Every key is `sanscript.transliterate(iast_witness, IAST, SLP1)` over a witness
that a human typeset next to the Cyrillic form; nothing is transliterated *out of* Cyrillic. Adding a row whose
IAST witness you cannot point at breaks the contract the whole dataset rests on.

**Sync rule:** change the table ⇒ re-run
[tools/h3985_cyr_slp1_table.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_cyr_slp1_table.py)
and refresh the validation report **in the same PR** (stated in
[CLAUDE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) § Cyrillic proper nouns).

## Provenance

- **Created:** 03-09-2026, handoff H3985 (Opus 5, `claude-opus-5`), shipped in
  [v1.144.145](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.145) /
  [v1.144.146](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.146).
- **Predecessor:** [tools/gaps_s6_cyrillic_name_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/gaps_s6_cyrillic_name_probe.py) (H1746, Grok 4.5) — the probe that named the recoverable path ("a validated proper-noun LOOKUP table seeded from IAST-bearing indices … not character rules"). Its own seed counts were **wrong** and are corrected by FINDINGS §629: it hard-coded a Windows `SEARCH_ROOTS` path and rglob'd worktree duplicates, inflating 32/20 into 61/47.
- **Seed inventory:** [tools/h3985_seed_inventory.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h3985_seed_inventory.py) — 85 files scanned, 32 carry inline IAST, 20 are Cyrillic-heavy with none.
- **Epistemic residue:** [GAPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) §6 🟠 → 🟡 HALF-CLOSED; [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) §629 (new) and §495 (corrected).

## What it does NOT cover

Measured coverage of the fully-Cyrillic name indices is **roughly a third, not a half**:
Erman–Temkin 174/478 = 36.4 % · Кадамбари 130/393 = 33.1 % · Потапова 128/326 = 39.3 %.
(The Potapova HTML twin reports 2/77 — a disclosed parser artifact of that file's markup, not a coverage claim.)
The 20 pure-Cyrillic seed files are left **explicitly unkeyed**: closing them needs a human-supplied onomasticon,
not more code. That residual is why GAPS §6 is half-closed rather than closed.

## Improvement backlog (ranked)

| # | Improvement | Why | Status |
|---|---|---|---|
| 1 | Supply an onomasticon (e.g. a digitised Sanskrit name dictionary) for the 20 pure-Cyrillic indices | The only path that raises coverage without violating the no-rules invariant | parked — needs a human source decision, not an agent |
| 2 | Fix the Potapova HTML twin's parser so its 2/77 becomes a real number | A disclosed artifact still reads as a coverage failure to anyone skimming the report | parked — cosmetic; the TSV twin already carries the real 39.3 % |
| 3 | Extend seeds beyond RussianTranslation (SamudraManthanam name glossaries were unreachable on this box) | More IAST-bearing witnesses ⇒ more rows at zero epistemic cost | parked — cross-repo, needs the SamudraManthanam clone present |

_Dr. Mārcis Gasūns_
