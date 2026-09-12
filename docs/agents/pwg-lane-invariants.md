_Created: 13-09-2026 · Last updated: 13-09-2026_

# pwg_ru lane invariants — full detail (H3948 / H3748 / H3751 / H4349 / H3959)

> On-demand companion extracted from [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md) (H4580 slim). One-line invariants stay in CLAUDE.md; this file carries the full rules verbatim. Read it before touching any pwg_ru gate, key, or builder.

## Control plane (H3714)

[`src/pwg_pipeline/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pwg_pipeline) — supported PWG-lifecycle facade: one campaign DB, one
paid-call kernel, pure audit, journal-only promotion. Strangler layer over
the proven headless engine; legacy PWG-TM writers still run
([`compat.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/compat.py)). Wave 1 closed **PARTIAL** (no provider canary, no
independent review, no cutover):
[WAVE1_REPORT](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/WAVE1_REPORT_RussianTranslation_PWG_CONTROL_PLANE_31-08-2026.md). Tools:
[`cohort_engine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_engine.py), [`no_pwg_residual_ledger.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residual_ledger.py).

## Enumeration tiers are FOUR, not two (H3948)

[`microstructure.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py) is the one sanctioned reading of PWG's four
printed tiers — never re-derive from a marker's shape. Tier-rule change ⇒
re-run [`microstructure_four_tier_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure_four_tier_selftest.py) + re-measure with
[`pwg_four_tier_store_impact.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_four_tier_store_impact.py) same PR
([report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3948_four_tier_store_impact.json): 28.02% affected). A tier ambiguous in print
stays unsplit, counted unresolved — **never guessed**
([FINDINGS §453](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)).

## Gate-evidence contract (H3748)

Every pwg_ru gate builds its verdict *through* [`gate_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gate_evidence.py) — hashed inputs, hit counts, a JSON
sidecar, `assert_nonvacuous()` (a vacuous PASS is a hard FAIL, #1803).
Legitimate emptiness is pre-registered by name (`LEGITIMATE_EMPTY` +
[the spike](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md)), never inferred from silence. New/changed gate registers a
`gate_id` via `GateEvidence` — CI's `gate_evidence.py --require <gate_id>`
fails on a missing sidecar. G9 (`validate_interop.py`) is expected **RED**
on shipped [`release/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release) (12,374 duplicated ids, #1798) — re-cutting is a
publication decision, not a code fix.

## Printed-locus invariant (H3751)

`~~h<N>` in a pwg_ru sub-card key is a 0-based `enumerate` index over PWG records,
**never** the printed homonym number (source `<h>` starts at 1 — conflating them was
#1801). Resolve positionally via
[`pwg_homonym.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_homonym.py); never re-spell the key. FINDINGS §617.

## `DHĀTUP.`→Palsule concordance — a same-author source is not an independent witness (H4349)

The concordance in
[`build_dhatup_palsule.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dhatup_palsule.py)
fills a coordinate from PWG first, then from **sibling passes** that run
beside it rather than widening `_L` in place. MW may break a PWG tie — it is
a different author, which is the whole coverage argument of H4339. **pw and
PWG's dotted-id articles may not**: both are Böhtlingk, so a same-book
claimant adds a vote to a tie the multi-claimant filter exists to drop, and
may not invent a coordinate PWG never cites (Böhtlingk renumbered between
editions — pw's `33,67` is pwg's `33,88`). Both classes are measured and
**empty**; that is the result, not a gap. **Sync:** any change to the builder
or a new sibling pass re-runs
[`dhatup_h4349_verify.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/dhatup_h4349_verify.py)
(17 checks, re-derives every published number from the artifact and the raw
corpora **without importing the builder**; exits **2** when csl-orig is
absent — a green run with zero checks was a real defect) **and**
`ls_enrichment_selftest.py` in the same PR, and passes `same_book_conflicted`
+ `pwg_cited` to the new pass. **Since H4386 both are keyword-only with no
default** — forgetting one is a `TypeError`, not an unscreened pass, which is
exactly how the first cut shipped two wrong rows — and an empty `pwg_cited`
raises rather than admitting everything. **The artifact is pinned to its
builder:** `_stats.builder_sha256` carries the sha256 of
`build_dhatup_palsule.py`, so a builder change without a rebuild fails the
selftest; rebuild and commit the JSON in the same PR
(`python src/build_dhatup_palsule.py --xls <the gitignored Palsule XLS>`).

## Abbreviation invariant (H3959)

Every `<ab>` token belongs to one of three disjoint sets in
[`pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) — `RU_MAP` (Bucket A, **must** be Cyrillic),
`BUCKET_B` (grammatical, stay Latin), `RESIDUE` (undecided, per-token
reason). **Sync:** reclassifying a token runs `python pwg_ab_ru.py census`
same PR. Never route Bucket-A to Latin. Ruling: [CONTRADICTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md);
style rules 3.1–3.5: [style guide](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md).

## `<ab>`/`<ls>` tooltips + RU-column purity

Grammatical abbreviations stay Latin with a tooltip, editorial ones translate
to Russian: [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md).

_Dr. Mārcis Gasūns_
