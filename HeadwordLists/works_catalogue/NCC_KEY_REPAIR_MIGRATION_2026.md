# NCC `match_key` repair — what moved, row for row

_Created: 26-07-2026 · Last updated: 26-07-2026_

Handoff [H1671](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1671-Opus_SanskritLexicography_acc-ncc-p0p1-ncc-key-repair-rerun_26.07.26.md)
· executor **Opus 5 1M (`claude-opus-5[1m]`)** · closes
[integrity issue #779](https://github.com/gasyoun/SanskritLexicography/issues/779), found and
measured but deliberately not acted on by
[H1657](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1657-Opus_SanskritLexicography_acc-ncc-p2-agent-adjudication-49k_26.07.26.md)
(whose non-goals forbade re-running P1).

New totals live in their own generated files —
[`P0_COUNTS.md`](P0_COUNTS.md), [`P1_COUNTS.md`](P1_COUNTS.md),
[`P2_COUNTS.md`](P2_COUNTS.md), [`P2_PRECISION.md`](P2_PRECISION.md). This file is the
**before/after**: new totals alone cannot show whether the repair found true links or merely
reshuffled artefacts, and that is the only question worth asking about a 91,156-row swing.

## 1. The fix

One line in [`parse_ncc.py`](parse_ncc.py): case-fold (and NFC-normalize) the IAST headword
*before* transliteration, because `sanskrit_util.to_slp1` is case-preserving and has no
uppercase IAST keys, so a capital fell through its `.get(ch, ch)` default into the SLP1
string, where `slp1_simplify` read it as a different phoneme.

| NCC headword | key P1 used | key it should be | what the capital became |
|---|---|---|---|
| Kalāpatattvārṇava | `khalapatattvarnava` | `kalapatattvarnava` | `K` = kh |
| Rāmāyaṇa | `namayana` | `ramayana` | `R` = ṇ |
| Yogasūtra | `nogasutra` | `yogasutra` | `Y` = ñ |
| Ekāvalī | `aikavali` | `ekavali` | `E` = ai |
| Bhāgavata | `bhhagavata` | `bhagavata` | `B` = bh |
| Śivastotra | `śivastotra` | `sivastotra` | `Ś` not transliterated at all |

Pinned by [`test_parse_ncc.py`](test_parse_ncc.py), which asserts both the correct key and
the absence of the specific corrupt one, so a regression fails by name instead of surfacing
two pipeline stages later as an unexplained recall drop.

## 2. Key level

| | before | after | Δ |
|---|---:|---:|---:|
| NCC records | 152,526 | 152,526 | — |
| keys changed by the repair | — | 91,548 (60.0%) | — |
| …of which the **first letter** changed | — | 31,953 (20.9%) | — |
| distinct NCC keys | 124,801 | 124,523 | −278 |
| keys containing non-ASCII | 20,571 | 643 | −19,928 |
| **exact-key overlap with ACC** | **8,397** | **22,775** | **+14,379 / −1** |

The 31,953 first-letter changes are the recall story: P1 blocks Tier D by first letter and
bisects Tier C by prefix, so for those rows **no candidate was ever emitted to adjudicate**.
They were not rejected — they were never proposed.

## 3. Tier level

| Tier | before | after | Δ |
|---|---:|---:|---:|
| A (exact key) | 107,815 | 241,970 | +134,155 |
| B (nasal/geminate fold) | 12,426 | 7,832 | −4,594 |
| C (prefix containment) | 5,353 | 9,039 | +3,686 |
| D (edit distance) | 43,666 | 1,575 | **−42,091** |
| **total candidate rows** | **169,260** | **260,416** | **+91,156** |

Tier D all but vanishes because it was never mostly a fuzzy-match tier: it was the corrupted
keys' landing zone, one edit away from their own correct spelling.

## 4. Row-for-row migration

Rows tracked by their `(acc_L, ncc_id)` identity, so a row that changed tier is followed
rather than counted twice.

| from | to | rows | what this is |
|---|---|---:|---|
| A | A | 107,761 | unaffected exact matches |
| NEW | A | 86,892 | pairs P1 never compared — the recall hole, now proposed |
| D | A | 40,757 | §0's prediction: exact title matches wearing a Tier D label |
| B | A | 6,560 | fold-tier pairs that are in fact exactly equal |
| B | B | 5,759 | unaffected fold matches |
| NEW | C | 5,580 | newly reachable prefix candidates |
| C | C | 3,296 | unaffected prefix candidates |
| C | GONE | 2,057 | see §5 |
| D | GONE | 1,493 | see §5 |
| NEW | B | 1,486 | newly reachable fold candidates |
| NEW | D | 909 | newly reachable edit-distance candidates |
| D | D | 666 | genuine edit-distance candidates, unaffected |
| D | B | 587 | promoted to the fold tier |
| D | C | 163 | promoted to the prefix tier |
| B | GONE | 107 | see §5 |
| A | GONE | 54 | see §5 |

**Survived: 165,549 · newly appeared: 94,867 · disappeared: 3,711.**

The single most load-bearing row is `D → A: 40,757`. H1657's §0 predicted exactly that
number from the repaired keys without re-running P1; the re-run reproduces it, which is what
makes the rest of this table trustworthy.

## 5. Every disappeared row, accounted for

A repair that silently deletes true links would be worse than the bug. All 3,711 were
classified; **none is unexplained**.

| old tier | why it disappeared | rows |
|---|---|---:|
| A | corruption-manufactured **exact** collision, now correctly separated | 54 |
| B | corruption-manufactured fuzzy match, now correctly separated | 55 |
| B | key unchanged; superseded — its key now has an exact Tier A partner | 52 |
| C | key unchanged; superseded — its key now has an exact Tier A partner | 1,915 |
| C | corruption-manufactured fuzzy match, now correctly separated | 136 |
| C | key unchanged; its ACC key moved to an earlier tier with another partner | 6 |
| D | corruption-manufactured fuzzy match, now correctly separated | 1,137 |
| D | key unchanged; superseded — its key now has an exact Tier A partner | 335 |
| D | key unchanged; its ACC key moved to an earlier tier with another partner | 21 |

Two mechanisms, no third:

1. **1,382 rows were the corruption's own false positives.** The clearest are the 54 Tier A
   ones, which were *exact* matches only because the key was wrong — ACC `Nāmamuktāvalī`
   matched NCC `Rāmamuktāvali` (`R`→`n`), ACC `Dhanasāra` matched NCC `Dānasāra` (`D`→`dh`),
   ACC `Nāgeśvara` matched NCC `Yāgeśvara` (`Y`→`n`). Different works, joined by a
   transliteration bug. Removing them is the repair working.
2. **2,329 rows were superseded by the tier partition**, not refuted. A pair is assigned to
   the *first* tier it qualifies for, and a key that lands in Tier A is excluded from B/C/D
   — so when an ACC key acquires an exact partner, its weaker fuzzy candidates stop being
   emitted. That is P1's existing partition semantics (changing it is an explicit H1671
   non-goal), and it is worth stating plainly as a **known limitation**: an ACC key with a
   genuine Tier-B/C variant partner *and* an exact partner now only proposes the exact one.

## 6. Adjudication (P2) — re-run, and what it invalidates

[`adjudicate_p2.py`](adjudicate_p2.py) had carried its own in-memory copy of the key repair
as a workaround; it now delegates to `parse_ncc.match_key_for` so the two cannot drift.

| | before (H1657) | after |
|---|---:|---:|
| Tier C/D rows to adjudicate | 49,019 | **10,614** |
| `exact_after_key_repair` (approve) | 40,757 | **0** |
| `fold_after_key_repair` (approve) | 615 | **0** |
| rows whose NCC key was corrupt | 42,989 (87.7%) | **0 (0.0%)** |
| approve / reject | 41,947 / 7,072 | 920 / 9,694 |
| strata | 16 | 17 |
| `works_crosswalk.tsv` rows | 120,241 | **249,802** |

The top two rules going to zero is the fix verifying itself: those 40,757 rows are now Tier
A upstream and never reach the adjudicator. `ncc_key_was_corrupt = 0.0%` is the invariant
confirming P0 really did ship repaired keys — if either number is non-zero again, the
candidate file is stale.

What is left — 10,614 rows, of which 6,489 were never adjudicated before — is the *genuine*
adjudication problem: person-vs-work, commentary extensions, unsupported prefix extensions.

**H1657's 686-card spot-check sample is void.** It was drawn from a 49,019-row population
that no longer exists, and 3,550 of its rows are not even candidates any more. It was
**never voted** (no `decisions.json` was ever saved beside it), so re-drawing discards no
human work — that was checked before this handoff ran, per its own prerequisite. The
replacement is a fresh 698-card sample over the 17 new strata, seeded and planned before the
draw:
[`p2_spotcheck_manifest.json`](p2_spotcheck_manifest.json) →
`review/sanskritlexicography-acc_ncc_p2_spotcheck.html` (local, gitignored).

No stratum is measured yet, so all 10,614 rows remain `defer` / agent-proposed and **none is
promoted into the crosswalk**. The precision bar is still unset — the
[`P2_PRECISION.md`](P2_PRECISION.md) consequence table prices each candidate bar.

## 7. Downstream — kosha

`works_crosswalk.tsv` goes **120,241 → 249,802 rows (+107.7%)**, and the increase is almost
entirely Tier A/B auto-confirmed rows (241,970 + 7,832 = 249,802), not adjudicated ones.
Anything serving this file serves roughly twice as many work links from the same catalogues.
Flagged rather than left to land silently, per H1671's prerequisite note.

## 8. Upstream — is `to_slp1` itself the bug?

Audited across the org; reported in full in
[`FINDINGS.md`](../../FINDINGS.md) and filed upstream. Short version: `to_slp1` maps
lowercase IAST and passes everything else through verbatim, which is defensible for a
transcoder — but the passthrough is **silent**, undocumented, and lands in an output alphabet
where case is *phonemic*, so a wrong answer looks exactly like a right one. The library
already distrusts it internally (`iast_to_devanagari` calls `to_slp1(text.lower())`), and
[csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) defends at two call sites with a
bare `.toLowerCase()` and no comment explaining why. Recommendation: keep `to_slp1`
byte-compatible, add a documented case-folding entry point + a test that pins the current
behaviour, and fix the one undefended caller found
([csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) `app.js` `rowSlp1()`, which
transcodes a user-typed IAST search term).

## Reproduce

```
python HeadwordLists/works_catalogue/test_parse_ncc.py
python HeadwordLists/works_catalogue/parse_ncc.py
python HeadwordLists/works_catalogue/build_works_crosswalk.py
python HeadwordLists/works_catalogue/adjudicate_p2.py
python HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py
python HeadwordLists/works_catalogue/p2_precision_gate.py
python HeadwordLists/works_catalogue/apply_p2_decisions.py HeadwordLists/works_catalogue/p2_gated_decisions.json
```

`parse_acc.py` is deliberately absent: ACC supplies genuine lowercase SLP1 and is untouched
by the repair.

_Dr. Mārcis Gasūns_
