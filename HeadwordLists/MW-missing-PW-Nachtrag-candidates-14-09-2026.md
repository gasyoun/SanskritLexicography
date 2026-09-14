# MW-missing PW/PWK Nachtrag candidates — frozen list, method and counts (H4837)

_Created: 14-09-2026 · Last updated: 14-09-2026_

Companion of [`MW-missing-PW-Nachtrag-candidates-14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-missing-PW-Nachtrag-candidates-14-09-2026.tsv),
built by [`pw_nachtrag_vs_mw.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/pw_nachtrag_vs_mw.py),
adjudicated in [`MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-14-09-2026.tsv)
(builder [`pw_nachtrag_adjudicate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/pw_nachtrag_adjudicate.py)).
Feeds [H4837](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4837-OxAlpha_SanskritLexicography_mw-missing-pw-nachtrag-adjudication_14.09.26.md)
and [csl-corrections#119](https://github.com/sanskrit-lexicon/csl-corrections/issues/119).

## 0 · What this list is

Every headword of the PW (kürzere Fassung, `pw.txt`) and standalone Nachträge
(`pwkvn.txt`) digitizations whose `<k2>` carries the Cologne `*` insert marker —
the digitization's own "Nachträge insertion" flag — that is **absent from MW99**
(cleaned `k1∪k2` space). **3,353 unique headwords.** This is the frozen
adjudication list of H4837; verdict semantics live in the adjudication TSV.

## 1 · Frozen method (reproduces byte-identically)

1. Loose header regex `^<L>([^<]+)<pc>([^<]*)<k1>([^<]*)<k2>([^<]*)` — catches
   fractional `<L>` inserted sub-entries (`<L>46.1…`), 170,556 + 24,976 entries.
2. Keep entries whose `<k2>` starts with `*` (pw 30,791; pwkvn 975).
   `clean(k1) == clean(k2[1:])` holds for every such entry (verified).
3. `clean()` = SLP1 `isalpha()`-only (strips `*`, digits, marks). Dedupe by
   cleaned headword; keep the richest body (tie: smallest `(src, L)`) →
   30,602 unique starred headwords.
4. Candidate = absent from MW99's cleaned `k1∪k2` set (**194,283** — matches
   [the recheck's §0 cleaned-union convention](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md)
   exactly) → **3,353**.
5. Corroboration = membership in each of the 36 other Cologne dictionaries
   (cleaned `k1∪k2`), recorded per dict (`corr_dicts`) plus `corr_n` /
   `corr_n_ex_mw72`.
6. Per-candidate signals: SLP1+IAST forms, source+locus, `also_pwkvn`, body
   size, MAHĀVY citation + refs, MW stemkey-variant present, MW near-form
   (deterministic fuzzy, same tie-break rule as the trial fix), DCS-conllu
   lemma/form attestation.

## 2 · Counts

| metric | value |
|---|--:|
| pw.txt entries / starred-k2 | 170,556 / 30,791 |
| pwkvn.txt entries / starred-k2 | 24,976 / 975 |
| unique starred headwords | 30,602 |
| **missing from MW99** | **3,353** |
| — corroborated ≥2 dicts (tier A) | 889 |
| — corroborated exactly 1 (tier B) | 1,335 |
| — no corroboration (tier C) | 1,129 |
| cite MAHĀVY | **273** (matches the handoff's derived stat exactly) |
| MW stem-variant present (`variant-form-in-MW` verdict) | 610 |
| confirmed-missing (stem-space too) | 2,743 |
| DCS lemma attested among confirmed | 198 (+96 form-only) |
| clean adds (tier A, no risk flags) | 349 |

## 3 · Baseline reconciliation — read before quoting any number

[H4837's spec](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4837-OxAlpha_SanskritLexicography_mw-missing-pw-nachtrag-adjudication_14.09.26.md)
quotes 3,024 / A 618 / B 1,427 / C 979 from the mint session's run, whose
artifacts were never landed (the exact untracked-only trap). This rebuild
reproduces the handoff's **method** and its **derived stats exactly** (MAHĀVY
273; MW cleaned union 194,283; `kAritra` canary = missing, corroborated
`bhs;sch`, near-form `kArita` 0.923, MAHĀVY 245) but lands on **3,353**, not
3,024 (Δ 329). Twelve convention variants were tested (strict vs loose header
regex, k1-only vs union matching, mw72 subtraction, stem relaxation,
case-fold dedupe, pwkvn-all, pw-main filtering, guard classes); only the frozen
convention above reproduces MAHĀVY = 273 exactly, so it is the one frozen. The
residual Δ329 is an unstated nuance of the mint's untracked throwaway script.
Per [the recheck's directive](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_PWK_NACHTRAEGE_TRIAL_INDEPENDENT_RECHECK_14-09-2026.md)
("adjudicate on a single frozen list with explicit tier semantics, not on a
count"), adjudication proceeds on THIS list. Cite counts with their definition,
never bare.

## 4 · Adjudication semantics (frozen)

- `confirmed-missing` — absent from MW verbatim **and** stemkey space.
- `variant-form-in-MW` — MW carries the identical stem minus final vowel
  (PWK headword is a stem/citation-form doublet, e.g. `aScary` ↔ `aScarya`);
  an editorial call, not a clean omission.
- Risk notes (flags, never auto-verdicts): vowel-length/case fold-twin (SLP1
  case is phonemic — `Anumati` gaṇa-entry vs `anumati` are distinct words),
  orthographic doublet ≥0.95, false-friend near form (the `kAritra`~`kArita`
  class), pratyāhāra/short-form class.

## 5 · Verification

- 30-sample stratified spot-check (15 add / 10 check / 5 low-priority,
  seed 4837): every row hand-grepped against `mw.txt` (verbatim + fold) and its
  PWK body read — **30/30 real, absent, correctly classed; 0 false positives**
  (acceptance gate ≤1). Evidence: [`MW-NACHTRAG-SPOTCHECK-30-14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-SPOTCHECK-30-14-09-2026.tsv).
- Canary `kAritra`: absent from MW, present `pw.txt` L216013 (7-331-d) +
  `pwkvn.txt` L16013, corroborated bhs+sch, MAHĀVY 245/844, near-form
  `kArita` 0.923 flagged as false friend — the motivating case, reproduced.
- Builder rerun byte-identical (deterministic fuzzy tie-break; sorted output).

## 6 · Repro

```sh
export CSL_ORIG_V02=/path/to/csl-orig/v02   # e.g. ~/Documents/GitHub/csl-orig/v02
export DCS_CONLLU=/path/to/DCS-conllu       # optional, corpus columns
python -u HeadwordLists/pw_nachtrag_vs_mw.py       # ~16 min (dict parse dominates)
python -u HeadwordLists/pw_nachtrag_adjudicate.py  # ~10 s with DCS set
```

_Гасунс_
