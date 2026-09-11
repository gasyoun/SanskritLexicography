# MW↔PWK corrigenda pair table — derived from MG's own 2013-2014 fuzzy-correction workbooks

_Created: 11-09-2026 · Last updated: 11-09-2026_

Handoff: [H4537](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4537-OxAlpha_SanskritLexicography_mw-pwk-corrigenda-pairs_11.09.26.md) · prior art: [H4477 census §4](https://github.com/gasyoun/SanskritLexicography/blob/master/YADISK_05_SANSKRIT_LEXICON_TREES_CENSUS_10-09-2026.md), [csl-corrections correction-workflow](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md), [`A_TYPO_QUEUE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/A_TYPO_QUEUE.md) · class: data (awaiting different-session Verifier, H4358) · **derived-only** (raw workbooks stay on yadisk, MG ruling 07-09-2026).

## ⚠️ Naming trap — MG's "PWK" is Cologne code `pwg`, not `pwk`

Per the [H4477 census §2 edition-code mapping](https://github.com/gasyoun/SanskritLexicography/blob/master/YADISK_05_SANSKRIT_LEXICON_TREES_CENSUS_10-09-2026.md#2--edition-code-mapping-pinned--prevents-the-classic-pwgpwk-mix-up):
MG's yadisk folder `1879-PWK` = *Sanskrit-Wörterbuch in kürzerer Fassung* (Böhtlingk 1879) = **csl-orig code `pwg`**. Cologne's own `pwk` code is a different dictionary entirely. **Any future filing of these pairs into csl-corrections targets `csl-orig/v02/mw/mw.txt` and `csl-orig/v02/pwg/pwg.txt` — never `v02/pwk/`.** This is exactly the mix-up class the census was written to prevent; repeating the caveat here because this table is the artifact most likely to be read out of context by a later filing session.

## What this is

MG's own fuzzy-match correction pairings between Monier-Williams (MW) and the Böhtlingk *kürzere Fassung* ("PWK" in MG's naming = Cologne `pwg`), worked in Excel 2013-11-26 to 2014, fetched from yadisk `Sanskrityatina/05_Sanskrit-Lexicon/corrigenda/` (4 files, ~21 MB, WebDAV recipe: [H4473 memory](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4473-OxAlpha_SanskritLexicography_yadisk-legacy-corpus-fetch_10.09.26.md) — no rclone on this Windows box, `curl` + prod `.env` creds instead) and consolidated here into one pair table.

- **Builder:** [`mw_pwk_corrigenda_pairs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_corrigenda_pairs.py) (point `CORRIGENDA_DIR` at a local copy of the 4 workbooks; not committed — derived-only).
- **Output:** [`mw_pwk_corrigenda_pairs.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwk_corrigenda_pairs.tsv) — **260,568 rows**, columns `source_workbook`, `source_sheet`, `row_id`, `script` (iast/slp1), `mw`, `pwk`, `verdict`.

## Source workbooks (own-data parity — every sheet re-derived and cross-checked against the H4477 census dims)

Three of the four files are near-duplicates of the same 2013-11-26 comparison pass (one plain `.xlsx`, one "peresortirovka" = re-sort in both `.xlsx` and `.xlsm`). Verified here: the `MW`/`PWK`/verdict columns are **byte-identical** across all three; only the resort copies' derived `LEN(PWK)`/`Book` helper columns went stale after the row reorder (formula references shifted, values did not get recalculated — 9,801 of 9,828 rows differ in those two columns alone). Only the plain `.xlsx` is read for the pair table; the two duplicates are counted for parity and skipped.

| Workbook | Sheet | Rows (re-derived) | Expected (census dims) | Parity |
|---|---|--:|--:|---|
| `Fuzzy-word-correction-MW-PWK_26112013.xlsx` (canonical) | Сравнительная1 | 9,828 | 9,829 (incl. header) | OK |
| " | fuzzy_DEV_FINISH | 27,080 | 27,081 | OK |
| " | fuzzy_IAST_FINISH | 28,519 | 28,520 | OK |
| " | Совпадения MW и НАДPWK | 1,163 | 1,164 | OK |
| `Fuzzy-word-correction-MW-PWK_26112013-peresortirovka.xlsx` (duplicate) | all 4 sheets | same dims as canonical | same | OK |
| `Fuzzy-word-correction-MW-PWK_26112013-peresortirovka.xlsm` (duplicate) | all 4 sheets | same dims as canonical | same | OK |
| `fuzzy-mw-vs-pwk-2014.xlsm` | Лист1 (no header row) | 193,978 | 193,978 | OK |

All four census-named files fetched byte-exact (WebDAV content-length matched the H4477 census size exactly for each).

## Per-sheet semantics

- **Сравнительная1** (IAST) — the curated comparison sheet; column D carries MG's actual editorial typo call where present (`PWK typoe`, `PWG typoe`, `MW typoe`, `Wilson typoe`, `PWK-Schmidt typoe`, or a free-text note) — this is the highest-confidence subset. Most rows carry no explicit call (`unreviewed`, or a bare `1`/`0` binary flag whose meaning is not labelled in the workbook, or `?` = uncertain).
- **fuzzy_DEV_FINISH** / **fuzzy_IAST_FINISH** — devanagari- and IAST-keyed fuzzy-match lists; `verdict` records only whether the pair also appears in the sibling list (`cross-dup`) or is unique to this one (`unique-to-*-list`) — a housekeeping/dedup flag, not an editorial call.
- **Совпадения MW и НАДPWK** — exact string matches between an MW headword and a PWK headword (`exact-match`), i.e. candidate duplicate entries across the two dictionaries rather than typo pairs.
- **Лист1** (`fuzzy-mw-vs-pwk-2014.xlsm`, SLP1, no header) — raw fuzzy-match candidate output with no human review column at all (`unverified-candidate`); this is the bulk of the table (193,978 of 260,568 rows) and is the least reliable tier.

## Verdict breakdown (260,568 total)

| verdict class | rows |
|---|--:|
| unverified-candidate (2014 raw list, SLP1, unreviewed) | 193,978 |
| cross-dup (appears in both dev+iast fuzzy lists) | 44,608 |
| unique-to-one-list (dev or iast fuzzy list only) | 10,991 |
| unreviewed (Сравнительная1, no editorial call recorded) | 9,673 |
| exact-match (MW string == PWK string) | 1,163 |
| flag:0/1 (binary Сравнительная1 flag, meaning not labelled in the source) | 114 |
| uncertain (`?` in Сравнительная1) | 24 |
| **typo (explicit editorial call)** | **17** |

## csl-corrections candidate-feed note

**No writes were made to `csl-corrections` or `csl-orig`.** Per the handoff's guard and the standing [`/cologne-batch-pr`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md) discipline, corrections only ever land in `csl-orig` through the monthly consolidated batch — this table is a **candidate feed** for that process, staged here in SanskritLexicography, not in csl-corrections.

**Filing priority for a future `/cologne-batch-pr` pass** (targets, per the naming-trap note above, are `v02/mw/mw.txt` and `v02/pwg/pwg.txt`):

1. **17 `typo:*` rows** — MG's own explicit editorial calls (e.g. `PWK typoe` = the pwg-side form is the typo, correct is the mw-side form or vice versa per the note). Highest confidence; still needs scan verification per [correction-workflow.md §3](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md#3-tutorial--one-correction-end-to-end) step 1 before filing as a `text-correction`-labelled batch entry, same discipline as [`A_TYPO_QUEUE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/A_TYPO_QUEUE.md).
2. **24 `uncertain` (`?`) rows** — MG flagged these as open questions at the time; need a fresh editorial call, not a mechanical filing.
3. **1,163 `exact-match` rows** — not typos; these are duplicate-entry candidates across MW/PWG, a `content-enhancement`/cross-reference question rather than a `text-correction` one. Out of scope for a typo batch.
4. **The remaining ~257,364 rows** (`unreviewed`, `cross-dup`, `unique-to-one-list`, `unverified-candidate`) are raw fuzzy-match output with no human verdict and **must not be bulk-applied** — same caution `assemble_typo_queue.py` states for its own queue. They are retained here as the full research trace, not as filing-ready candidates.

**Do not re-run this as a bulk `updateByLine.py` pass.** Every row that becomes an actual correction is verified against the printed scan first, exactly as [correction-workflow.md §8](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md#8-pitfalls-and-gotchas) and this repo's own `A_TYPO_QUEUE.md` insist.

## Reproduce

```sh
# fetch the 4 workbooks (WebDAV, H4473 recipe) into a local dir, then:
CORRIGENDA_DIR=/path/to/corrigenda python HeadwordLists/mw_pwk_corrigenda_pairs.py
```

_Dr. Mārcis Gasūns_
