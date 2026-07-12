_Created: 12-07-2026 · Last updated: 12-07-2026_

# assembled_cards / *.renou* pipeline redundancy — verification report (H692)

Verifies the [DATA_LAYERS_CENSUS.md §2](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
claim that the `assembled_cards*.jsonl` and `*.renou*.jsonl` files in
[`RussianTranslation/src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src)
are redundant "progressive pipeline stages" of one another, with **~1.4 GB recoverable**
by deleting the earlier stages. Per the H692 handoff, **no file was deleted, moved, or
renamed** — this session stops at the verdict + proposal.

Reproducible via
[`verify_cards_renou_redundancy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/verify_cards_renou_redundancy.py)
(streaming, aggregates only — no data rows printed or committed).
Model: Opus 4.8 (`claude-opus-4-8`).

## Verdict — the redundancy does not exist. Recoverable = 0 MB.

Both halves of the census claim are **refuted** against the current disk state. Nothing
is a redundant stage of anything; every large file is single-copy, distinct, canonical
data. The census figure of ~1.4 GB recoverable exceeds the entire on-disk footprint of
the flagged set (**545 MB**), which is itself the tell that the "×4 stages" model is a
filename-glob artifact.

## Why the census was wrong

The census read the shell glob `assembled_cards*.jsonl` and `*.renou*.jsonl` as
enumerating **stages of one artifact**. In reality the glob spans two unrelated axes:

1. **Test fixtures vs. the one canonical output.** `assembled_cards.{chunk,smoke,test}`
   are 7/10/25-row dev fixtures and `assembled_cards.perf` a 5,000-row perf fixture. Only
   `assembled_cards.renou.bhs.wl.jsonl` (120,173 rows) is real corpus data. The census's
   "all 4 variants carry the identical 120,173 rows" is false — exactly **one** file has
   that count.
2. **No persisted intermediate stages ever existed.**
   [`renou_pipeline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pipeline.py)
   builds its `<ls>+DCS → +BHS → +wl` stages as `t1`/`t2` inside a
   `tempfile.TemporaryDirectory()` and writes **only** the final `{code}.renou.jsonl`
   (lines 44–57). The imagined `assembled_cards.jsonl → .renou.jsonl → .renou.bhs.jsonl
   → .renou.bhs.wl.jsonl` chain of "four ~200 MB stages kept side by side" was never
   written to disk. No `mw_renou.bhs.wl`-style sibling exists either.
3. **`*.renou.jsonl` is one file per SOURCE DICTIONARY, not per stage.** The eight
   `{dict}.renou.jsonl` files (mw/pw/pwg/ap/ap90/ben/bhs/sch) share a schema but hold
   disjoint headwords and distinct row counts — deleting any loses that dictionary.

## Series 1 — `assembled_cards*.jsonl`

| File | Rows | Size | Role |
|---|---:|---:|---|
| `assembled_cards.chunk.jsonl` | 7 | 14.3 KB | dev/CI fixture |
| `assembled_cards.smoke.jsonl` | 10 | 21.7 KB | smoke-test fixture |
| `assembled_cards.test.jsonl` | 25 | 64.3 KB | unit-test fixture |
| `assembled_cards.perf.jsonl` | 5,000 | 8.0 MB | perf fixture |
| **`assembled_cards.renou.bhs.wl.jsonl`** | **120,173** | **200.0 MB** | **CANONICAL — keep** |

Verdict: **keep the canonical file + all 4 fixtures; delete nothing.** The fixtures are
tiny (≈8 MB combined) and are consumed by the gate selftests referenced in the repo CI —
not redundant copies. **0 MB recoverable.**

## Series 2 — `{dict}.renou.jsonl` (8 dictionaries)

| File | Dictionary | Rows | Size | Fields |
|---|---|---:|---:|---:|
| `mw.renou.jsonl` | Monier-Williams | 286,560 | 101.8 MB | 13 |
| `pw.renou.jsonl` | Petersburg (small) | 170,556 | 69.7 MB | 13 |
| `pwg.renou.jsonl` | Petersburg (large) | 123,366 | 79.7 MB | 13 |
| `ap.renou.jsonl` | Apte | 90,654 | 27.1 MB | 13 |
| `ap90.renou.jsonl` | Apte 1890 | 34,882 | 21.3 MB | 13 |
| `sch.renou.jsonl` | Schmidt | 29,125 | 12.0 MB | 13 |
| `bhs.renou.jsonl` | BHS | 17,839 | 12.2 MB | 12 * |
| `ben.renou.jsonl` | Benfey | 17,310 | 12.2 MB | 13 |

\* `bhs` carries 12 fields, not 13: BHS is the register-transfer **source**, so
`renou_pipeline.py` skips the `renou_bhs` self-transfer (line 49–50). A correct schema
difference, not corruption.

Distinct row counts already prove non-identity. Sampled headword overlap (first 2,000
`key1` per file) confirms **disjoint content**, so no file is contained in another:

| Pair | ∩ | A-only | B-only |
|---|---:|---:|---:|
| mw ∩ pw | 817 | 555 | 1,128 |
| mw ∩ pwg | 634 | 738 | 1,285 |
| pw ∩ pwg | 1,114 | 831 | 805 |

Verdict: **keep all 8; delete nothing.** **0 MB recoverable.**

## Naming-drift catalog (`.` vs `_`)

The census flagged "dot-vs-underscore naming drift throughout `RussianTranslation/src/`".
There is **no true drift** — no logical file exists under both a `X.renou` and a
`X_renou` name. What exists is a **principled, consistent split**:

- **Data artifacts** use dotted stage-suffixes: `{dict}.renou.jsonl`,
  `assembled_cards.renou.bhs.wl.jsonl`. The dots chain the pipeline suffixes onto the
  artifact name.
- **Python modules** use underscores: `renou_*.py`, `enrich_renou_*.py`,
  `build_dcs_renou.py`. Dots are illegal in importable Python module names, so this is
  forced, not a style slip.
- A few **data** files use underscores (`dcs_lemma_renou.json`, `renou_pilot_sample.jsonl`,
  `renou_h6_zipf_result.json`) — each is the named input/output of a specific script and
  matches that script's stem. Not a drift pair.

The census's specific example pair `mw.renou` / `mw_renou.bhs.wl` does not exist:
`grep`-level search finds no `*_renou*.jsonl` data file at all. **Rename plan: none —
no renames are warranted.**

## Proposal (human executes — this session performs no deletion/rename)

1. **Delete nothing, rename nothing.** The single-copy canonical files and the small
   fixtures are all live; recoverable stage-redundancy is 0 MB, not ~1.4 GB.
2. **Correct the census.** [DATA_LAYERS_CENSUS.md §2](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
   rows for `assembled_cards*` (line 83, 102, 110–113) and `*.renou*` (line 105) should be
   struck / re-annotated: the "4 progressive ~210 MB variants (~810 MB)" and
   "~600 MB mw/pw/pwg dedup" items are glob-misreads, not real reclaim candidates. The
   `🟠 Dedup … (~1.4 GB recoverable)` action (line 154) should be closed as **not-a-defect**.
3. **If disk reclaim is still wanted**, the real (small) lever is the 8 MB
   `assembled_cards.perf.jsonl` perf fixture — but it backs a CI gate selftest, so keep it.

_Dr. Mārcis Gasūns_
