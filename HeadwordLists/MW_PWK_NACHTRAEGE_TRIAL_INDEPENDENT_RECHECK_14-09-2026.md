# Independent recheck of the MW-vs-Nachträge trial — second and third methods, verifier findings

_Created: 14-09-2026 · Last updated: 14-09-2026_

Recheck of [`MW_PWK_NACHTRAEGE_MISSING_ENTRIES_TRIAL_14-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_PWK_NACHTRAEGE_MISSING_ENTRIES_TRIAL_14-09-2026.md) against [csl-corrections#119 comment 4359094604](https://github.com/sanskrit-lexicon/csl-corrections/issues/119#issuecomment-4359094604). Two independent re-derivations were run from `csl-orig/v02` with **different scope and different tier thresholds** from the trial, plus a two-round DeepSeek verifier pass over the landed artifacts (paired-family verification, data class). Feeds [H4837](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4837-OxAlpha_SanskritLexicography_mw-missing-pw-nachtrag-adjudication_14.09.26.md).

## 0 · Counting conventions — read this before comparing any two numbers

The same dictionary yields four different "MW headword counts" in the two documents. They are not interchangeable:

| label | definition | value |
|---|---|---|
| MW raw `k1 ∪ k2` | unique verbatim `<k1>` and `<k2>` strings (markers `* ˚ —` kept) | **344,684** |
| MW `k1` entries | unique verbatim `<k1>` values only | **194,083** |
| MW cleaned union | `isalpha`-only `k1 ∪ k2` (trial builder's `clean()`) | **194,282–194,283** |
| MW annexure, `k1`-only | unique `<k1>` of entries carrying `<info n="sup"/>` | **6,067** |
| MW annexure, cleaned union | `isalpha`-only `k1 ∪ k2` of the same entries | **6,068** (recheck) / **6,082** (trial) |

The trial's §3 row "MW headwords (k1+k2) 194,283" is the *cleaned union* and sits numerically next to the `k1`-only 194,083 — same-looking labels, different metrics. Cite the definition, never the bare number.

## 1 · Method B — all `pwkvn` headwords vs MW (wider than the trial's `sup_7` slice)

Builder: [`mw_pwkvn_missing_entries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pwkvn_missing_entries.py) (stdlib only). Scope: the standalone Nachträge digitization `pwkvn.txt` (24,976 entries, 14,995 unique `k1`) — **not** the `sup_7`-tagged slice of `pw.txt`.

| metric | value |
|---|---|
| MW entries with `k1` | 194,083 |
| MW annexure (`info n="sup"`) entries | 6,067 |
| MW main = `k1 − sup` (proper partition) | 188,016 |
| MW raw `k1 ∪ k2` | 344,684 |
| `pwkvn` entries / unique `k1` | 24,976 / 14,995 |
| `pwkvn k1` ∩ MW | 9,758 |
| `pwkvn k1` − MW (rows / unique headwords) | **9,096 / 5,237** |
| — of which cite `MAHĀVY` | 305 |
| — of which also in `pw.txt` / `pwg.txt` | 9,072 / 423 |
| `pwkvn ∩ MWsup` | 1,971 / 6,067 = **32.5 %** |
| `pwkvn ∩ MWmain` | 7,787 / 188,016 = **4.1 %** |
| **annexure enrichment** | **7.84×** |

The enrichment is the method-independent form of Andhrabharati's dependency hypothesis: a Nachträge headword is **~7.8× more likely** to sit among MW's annexure entries than among MW's main entries. (Verifier round 2 caught an earlier 7.44× built on a non-partitioning denominator — the tag-absence set overlapped `mw_sup` on duplicate `k1`s; fixed in the builder, value now 7.84×.)

## 2 · Method C — the `sup_7` slice re-implemented with stricter tiers

Builder: [`mw_pw_sup7_missing_entries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_pw_sup7_missing_entries.py). Same source slice as the trial (`pw.txt` `<info n="sup_7"/>`), but near-form is limited to a ±200 alphabetical window at difflib ≥ 0.92 (the trial uses a first-char × length bucket at ≥ 0.80).

| metric | trial | recheck (Method C) | reconciliation |
|---|--:|--:|---|
| `sup_1..sup_7` tagged entries | 22,611 | 22,611 | exact match |
| `sup_7` tagged entries | 13,208 | 13,208 | exact match |
| `sup_7` rows tiered | 13,129 (79 dropped by guard) | 13,208 | trial builder's `len(hw) < 3` guard |
| unique `sup_7` headwords | — | 13,094 | dedup convention |
| exact present in MW | 8,978 | 9,051 | `clean()` vs verbatim join |
| stem-normalized | 482 | 456 | different stem rule |
| near-form (review flags) | 1,918 | 399 | threshold 0.80/bucket vs 0.92/±200 |
| **absent (candidates)** | **1,751** | **3,302** | the near tier absorbs the difference |
| — rank A / B / C | 547 / 800 / 404 | 704 / 2,598 / 0 | rank = best neighbour; the trial's C requires no neighbour in the whole headword space |
| reverse: MW annexure ∩ `sup_7` | 1,800 / 6,082 (30 %) | 1,798 / 6,067 (**29.6 %**) | denominator convention (§0) |

**Robust, convention-independent findings:** `sup_7` = 13,208 entries; the reverse share is **~30 %** under every convention tried (29.6 %, 30 %); `kAritra` is absent from MW and present in both `pw.txt` (L216013, pc 7-331-d) and `pwkvn.txt` (L16013, pc 7-331-d); `kArApaka` is an MW annexure entry (L48659.2). The **absent-candidate count is method-dependent (1.7k–3.3k)** and must never be quoted without its tier definition — that is the adjudication's job (H4837), not the trial's.

## 3 · The motivating case, re-verified

- `kAritra` occurrences in `mw.txt`: **0** (grep + set join).
- `pw.txt` L216013 `<pc>7-331-d<k1>kAritra<k2>*kAritra`, body `<info n="sup_7"/>` — the starred Nachträge headword.
- `pwkvn.txt` L16013 `<pc>7-331-d<k1>kAritra<k2>*kAritra`; gloss `{#*kAritra#}¦ n. = {#cezwita#} MAHĀVY. 245. 844. Vgl. {#cAritra#}` — neuter abstract noun ("activity", = `ceṣṭita`), **not** the causative participle `kārita` it fuzzy-matches at 0.923.
- `pwg.txt` contains **neither** `kAritra` nor `kArApaka` — corroborating the edition-code table in the trial report (§1) and [CONTRADICTIONS §18](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).

## 4 · DeepSeek verifier passes (paired family, data class)

**Round 1** (raw extracts): PASS on `kAritra` absent-from-MW / present in `pw`+`pwkvn` at the stated loci, `kArApaka` annexure entry, `sup_7` = 13,208, `sup_1..7` = 22,611, MW raw `k1∪k2` = 344,684, `kAritra`~`kArita` = 0.923, `pw`/`pwg` edition identities (from the headers), Method C `stem` = 456 and `near` = 399, TSV row counts. **Defect found and fixed:** the trial report's §3 tier rows summed to 13,129, not 13,208 — the builder's `len(hw) < 3` guard silently drops **79** short headwords (`A`, `Am`, `Ap`, `As`, `BI`, `BU`, `DA`, `DU`, `E`, `I`, `Ir`, `Ra`, …); verified by direct count (exactly 79). The trial report §3 now carries the accounting note.

**Round 2** (spot-checks after the fix): **VERDICT: PASS**, **60/60 spot-checks with zero counterexamples** — 20 `Y` and 20 `N` rows of the reverse-overlap TSV verified against the raw headword extract, 20 absent-rows verified against the MW key extract, plus the guard-class check and the tier arithmetic. It also caught four internal inconsistencies in *this note's* first draft, all fixed here: the 7.44× enrichment denominator (§1), the mislabeled "13,129 (implied) unique headwords" row (§2 — 13,129 is the trial's post-guard *row* count, not a unique-headword count), the conflated +1/+15 annexure deltas (§0), and the label collision (§0 conventions table).

**Tooling limits of the verifier sandbox** (not data defects): it has no shell and a 100-match grep cap, so set joins and exact large-tier counts were not recomputable there; the reverse intersection, the 194,283 cleaned union and `pwg`-absence were recomputed in this note instead (§1–§3).

## 5 · Repro

```sh
python HeadwordLists/mw_pwkvn_missing_entries.py   # Method B  (~40 s)
python HeadwordLists/mw_pw_sup7_missing_entries.py # Method C  (~40 s)
# both read C:/Users/user/Documents/GitHub/csl-orig/v02 (override: CSL_ORIG_V02)
```

## 6 · What this changes for H4837

1. The trial's headline is confirmed by two independent methods: detection is cheap (~1 min), recall is high, and the reverse-dependency share (~30 %) is robust.
2. The **candidate count is tier-definition-dependent** (1,751 / 3,302 / 5,237 / 7,421 across the passes) — H4837 must adjudicate on a single frozen list with explicit tier semantics, not on a count.
3. Three named precision traps for the adjudicator: the `len(hw) < 3` short forms (79), the `kAritra`~`kArita` false-friend class, and the `clean()`-vs-verbatim join convention.
4. `pwg` (Böhtlingk–Roth 1855–75) is a *separate, noisier* comparison (MW deliberately omits most of its material) — out of scope for H4837 unless ruled otherwise.

## 7 · MW72 baseline — separating "never saw it" from "saw and skipped" (added 14-09-2026, MG question)

MG's point: MW72 (55,390 entries; 51,162 unique verbatim `k1∪k2`) predates every printed part of the *kürzere Fassung* (one part per year, 1879 through 1889 — per-volume years, never a blanket range: MG 15-09-2026) and all of the great PW's volumes (Bd 1 1855 · 2 1856 · 3 1857 · 4 1858 · 5 1861 · 6 1863 · 7 1872–75), so MW72 never saw the later material. Crossing the `sup_7` headwords with **both** MW editions splits the candidate pool into classes a single MW99 diff conflates — builder [`mw72_baseline_sup7.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw72_baseline_sup7.py), output [`mw72_baseline_sup7.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw72_baseline_sup7.tsv):

| class (of 13,094 unique `sup_7` headwords) | n |
|---|--:|
| **never-seen** — absent from MW72 AND MW99 (the `kāritra` class proper) | **4,112** |
| **dropped** — MW72 had it, MW99 lost it | **27** |
| kept — in both editions | 2,865 |
| added-since-MW72 — new in MW99 | 6,090 (annexure 1,474, main 4,616) |

MW99 took **~60 %** of the `sup_7` pool MW72 lacked (6,090 of 10,202) — and skipped 4,112 outright. `kAritra` is absent from MW72 (0×), consistent with 1872. The 27 dropped entries are a distinct correction class (deleted-between-editions), worth their own adjudication pass.

Caveat: MW72's coverage is **flat ~20 % across all layers** (`sup_1` 19 % … `sup_7` 22 %), so the layer index is *not* a clean chronology proxy for what MW72 could have seen — the Nachträge sections also add entries for pre-existing words. The flatness rather says MW72 was a smaller dictionary that omitted rare words generally; the MW72-baseline pool is still the right denominator, but "printing timeline" alone does not explain it. (Convention note: this section's MW99 annexure set is the raw `k1∪k2` of `<info n="sup"/>` entries, 11,066 — a superset of the §0 `k1`-only 6,067.)

_Гасунс_

_Гасунс_
