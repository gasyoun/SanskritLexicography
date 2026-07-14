# Handoff — test the homograph `(key1, h)` keying fix on 2 real cases

**For:** a fresh agent session. **Goal:** validate, on `dA` and `vah`, whether promoted
translations can be attributed to the *correct* homonym instead of multiplying across every
`assembled_cards` entry that shares a `key1`. Prior assessment said "blocked, no discriminator";
a closer look (below) found a **usable discriminator after all** — the leading PWG homonym
number. This handoff is to confirm it works on 2 real cases and, if so, scope the exporter fix.

## Background (1 paragraph)

The print bridge ([`src/promote_final_cards.py`](RussianTranslation/src/promote_final_cards.py)) writes one store
row per translated sense into `src/pwg_ru_translated.jsonl`, keyed on the **headword** `key1`
(= `meta.root`). [`src/export_interop.py`](src/export_interop.py) joins those translations onto
`src/assembled_cards.jsonl` by `key1` alone. **11.7 % of `key1` have >1 assembled entry**
(homographs), so in `--review-status ai_translated` preview a translation appears under *every*
homograph entry. It is **inert in production** (default export gate = `{approved, human_reviewed}`,
currently 0 rows — no G5 review yet), so this is a correctness/quality task for the edition
stage, not a live bug. See [`BRIDGE_FOLLOWUPS_2026-06-30.md`](BRIDGE_FOLLOWUPS_2026-06-30.md).

## The discriminator (the key insight to test)

Neither side has a clean homonym field (`ord`/`hom`/`records[].h` are all `None` on assembled;
the store/harness `h`-ordinal `h0..h9` is NOT the PWG number). **But both sides carry the PWG
homonym number inside their content:**

- **store row** `ru` begins with `"N. {#<root>#}…"` — e.g. `dā` rows start `1. {#dA#}`,
  `3. {#dA#}`, `4. {#dA#}`, … (the PWG headword number).
- **assembled** `record.de_skeleton` begins with `"N. {T1}¦…"` — the same masked German source,
  same leading PWG number (e.g. `dA` entry[0] record[0] = `"1. {T1}¦ ({T2}) A. Präsensformen…"`).

So the hypothesis to validate: **store homonym ↔ assembled record can be matched by the parsed
leading PWG number**, giving a real `(key1, pwg_no)` join that replaces the `key1`-only join.

### ⚠️ Pre-validated (2026-06-30) — the signal is real but AMBIGUOUS; do not assume a clean key

A quick extraction (regex `^\s*(\d+)\.\s*\{#` on store `ru`; `^\s*(\d+)\.\s*\{T\d+\}` on
assembled `de_skeleton`) gave:

- **`vah`** — store: `h0→1, h1→2, h2→None` (h2 is a `<hom>1.</hom>` vgl-stub); assembled record
  numbers `{1×2, 2×1}`. → the two real homonyms (1, 2) match; the stub is unmatched. **Workable.**
- **`dA`** — store: `h0→None(!), h1→3, h2→3, h3→4, h4→5, h5→6, h6→7, h7→8, h8→None, h9→None`;
  assembled record numbers `{1×3, 2×1, 3×3, 4×2, 5×1, 6×1, 7×3, 8×1}`. **Three problems:**
  1. **The dominant homonym `h0` (288 of 345 rows, 83 %) yields no leading number** — its first
     sense is the grammar/paradigm head (`{#dA#}¦ (…) A. Формы…`), which doesn't start with `N.`.
     So the leading-number rule misses the most important homonym.
  2. **Two store homonyms (`h1`, `h2`) both parse to `3`** — not 1:1.
  3. **Assembled record numbers repeat** (three `1`s, three `3`s, three `7`s) because the 4
     assembled entries overlap in content — so a number maps to several candidate records.

**Conclusion:** the leading PWG number is a useful signal for the *minor numbered* homonyms but
is insufficient alone — it fails for the main homonym and is non-unique. A robust attribution
needs to additionally (a) identify the **main homonym** (the largest store cluster / the
grammar-paradigm-head record, which lacks a leading number) and bind it to the main assembled
record, (b) de-duplicate repeated assembled records, (c) handle the prefix (`anu+dā`),
Nachträge-head, and `<hom>`-stub edge cases. The test below is to decide whether that is worth
building now, or whether the **de-dup interim** (one representative entry per `key1`) is the
right call until the `record.h` normalization derivation exists.

## Case 1 — `dA` (rich: 4 assembled entries, 10 store homonyms, 345 store rows)

**Store side** (group rows by the `subcard` h-ordinal; the PWG number is in the `ru`/`h` label):

| store h-ord | rows | h-label | leading PWG no. (from `ru`) |
|---|---:|---|---|
| h0 | 288 | `dā 1` | **1** |
| h1 | 7 | `dā (homonym 11, PWG-ROOT HEAD)` | **3** (Nachträge head — edge case) |
| h2 | 22 | `dā` | **3** |
| h3 | 9 | `dā 4` | **4** |
| h4 | 2 | `dā 5` | **5** |
| h5 | 1 | `dā 6` | **6** |
| h6 | 1 | `7` | **7** |
| h7 | 1 | `8` | **8** |
| h8 | 1 | `9` | `<hom>1.</hom>` (a "vgl." cross-ref stub — edge case) |
| h9 | 13 | `anu+dā` | prefix sub-section (no leading number — edge case) |

**Assembled side:** 4 entries with `#records` = 8 / 1 / 4 / 3, all carrying the *same*
`attested_senses.dict` koch glosses (दा I/II/III) — so the entries are NOT separable by glosses;
the homonym signal is the `record.de_skeleton` leading number.

## Case 2 — `vah` (clean: 3 assembled entries, 3 store homonyms, 135 store rows)

| store h-ord | rows | h-label | leading PWG no. (from `ru`) |
|---|---:|---|---|
| h0 | 133 | `vah` | **1** (`1. {#vah#}`) |
| h1 | 1 | `vah (2)` | **2** (`2. {#vah#}`) |
| h2 | 1 | `vah (3)` | **3** (`<hom>1.</hom>` vgl. stub — edge case) |

**Assembled side:** 3 entries, `#records` = 2 / 1 / 1, identical koch/kna glosses. The
`record.de_skeleton` leading numbers should be 1 / 2 / 3.

## The test (run these)

```powershell
cd RussianTranslation
# 0. Ensure the store exists (regenerate if needed; gitignored artifact).
python src/promote_final_cards.py            # writes src/pwg_ru_translated.jsonl

# 1. Reproduce the collision in preview for dA + vah (filter assembled to these two key1).
#    Build a 2-headword fixture and export with the preview flag, then count how many
#    times each translation appears (should be 4x for dA, 3x for vah today).
```

Concretely:

1. **Reproduce.** Filter `src/assembled_cards.jsonl` to `key1 in {dA, vah}` → fixture; run
   `python src/export_interop.py tei --cards <fixture> --store src/pwg_ru_translated.jsonl
   --review-status ai_translated --out-dir _hg`. Confirm each `dA` translation appears in all
   4 `<entry>`s and each `vah` in all 3 (the multiplication).
2. **Extract the PWG number both sides.**
   - store: regex the leading `^\s*(\d+)\.\s*\{#` from each row's `ru`.
   - assembled: regex the leading `^\s*(\d+)\.\s*\{T\d+\}` from each `record.de_skeleton`.
3. **Match** store-homonym → assembled-record by that number. Per the pre-validation: `vah`
   maps 1,2 cleanly (stub `h2` unmatched); `dA` maps the minor homonyms 3–8 but the **main
   homonym `h0` has no leading number** (bind it separately — it is the largest store cluster
   and the assembled record that is the grammar-paradigm head), and `3` is claimed by two store
   homonyms. Report the full mapping, the main-homonym binding, and every unmatched edge case.
4. **Decide:**
   - **If the number matches cleanly** for the main homonyms → the fix is a `(key1, pwg_no)`
     join: `promote_final_cards.py` stamps `pwg_no` on each store row (parse from `ru`), and
     `export_interop.card_glosses` attaches a translation only to the assembled record whose
     `de_skeleton` leading number equals it (falling back to the whole `key1` when either side
     lacks a number). Implement + re-run step 1 → each translation should now appear **once**,
     under the right homonym.
   - **If matching fails / too many edge cases** → the documented interim is de-dup (attach each
     translation once, to a single representative assembled entry per `key1`) + record that
     full per-homonym attribution needs the `record.h` normalization derivation. Do NOT ship a
     wrong-homonym attribution.

## Success criteria

- A printed mapping for `dA` and `vah`: store-homonym → assembled-record by PWG number, with the
  edge cases (prefix `anu+dā`, `<hom>`-stub, Nachträge head) explicitly listed as unmatched.
- A go/no-go on the `(key1, pwg_no)` exporter join, with the diff if go.
- Keep it preview-only safe: the **default export gate stays `{approved, human_reviewed}`** — do
  not change what production emits; this only fixes *attribution* for when G5-approved rows exist.

## Files / pointers

- store writer: [`src/promote_final_cards.py`](src/promote_final_cards.py) (add `pwg_no` stamp here)
- exporter + join: [`src/export_interop.py`](src/export_interop.py) (`card_glosses`, `approved_store`)
- data: `src/pwg_ru_translated.jsonl` (store, gitignored), `src/assembled_cards.jsonl` (structural)
- context: [`BRIDGE_FOLLOWUPS_2026-06-30.md`](BRIDGE_FOLLOWUPS_2026-06-30.md), PR #18 (the bridge)
- coordination: an autonomous account also works pwg_ru on `master`; do this on a branch + PR.
