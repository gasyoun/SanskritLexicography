# H1226 — persisting the pre-restore `{Tn}` pairing so the TNMASK false-flag rate becomes measurable

_Created: 19-07-2026 · Last updated: 19-07-2026_

_Model: Opus 4.8 (`claude-opus-4-8[1m]`), H1226._

## Problem

[H1150](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md)
returned **`DO_NOT_ARM`** for `TNMASK_HARD_REJECT` on an *insufficient-evidence*
verdict: denominator **1** (a single synthetic canary). The structural reason —
not a shortage of runs — is that **TNMASK's real check compares two things that
the promoted store never keeps**:

- `want` — the masked source **skeleton's** `{Tn}` multiset, `tokensOf(INPUTS[k].skeleton)`;
- `got` — the pre-restore **candidate's** `{Tn}` multiset, `cardTokens(c)`.

The comparison lives in
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
`accept()` (the H960 grammar-`{Tn}` guard), **before** `restoreCard` runs:

```js
const tok = cardTokens(c), want = tokensOf(INPUTS[k].skeleton)
if (tok !== want) { TNMASK_MISMATCHES++; TNMASK_DETAIL.push({key:k, got:tok, want}); ... }
```

`restoreCard` then turns every `{Tn}` back into real markup, so the promoted
store row holds only **post-restore** text — the `(got, want)` pairing is
transient and is dropped on every card. With nothing preserved, the false-flag
rate cannot be recomputed offline from the store, and there are zero real
`(pre-restore-candidate, masked-skeleton)` pairs to measure against.

This handoff makes that pairing **durable** so the rate becomes measurable once
real windows accrue. It does **not** measure and does **not** arm
(`TNMASK_HARD_REJECT` stays `= false`, byte-unchanged).

## Why only the main `accept()` path needs it (not heal / TM / degenerate)

The main `accept()` path is the **only** path where a TNMASK `{Tn}` mismatch
survives *un-rejected* into a promoted card:

- **Main `accept()`** — the `{Tn}` guard is **SOFT** (`TNMASK_HARD_REJECT=false`):
  a mismatch is counted as telemetry and the card is **kept**. So a real
  soft-flag can reach the store here — this is exactly the population whose
  false-flag rate H1150 could not measure.
- **Heal / self-heal (`selfHeal` → `acceptFrag`)** — `acceptFrag` **hard-rejects**
  any fragment whose `cardTokens(c) !== tokensOf(grp[fi].skeleton)`
  (`fragment-fidelity-reject`). A `{Tn}` expansion in a fragment drops that
  fragment; it never stitches into a promoted card. A healed card that survives
  therefore carries no un-rejected `{Tn}` mismatch — nothing to measure.
- **TM passthrough / degenerate passthrough** — cache hits harvested from prior
  *successful* resolves (which themselves passed `accept()`/`acceptFrag`), or a
  source-identity degenerate row. Neither can introduce a novel expansion.

So instrumenting `accept()` alone is not a coverage gap — it is precisely where
the measurable phenomenon lives. Cards from the other paths simply carry no
`tnmask` field, and the offline detector reports them as **not measurable**
(honest), never as clean.

## The persisted field — shape and placement

`accept()` stamps, on the accepted card, a bounded pairing **before** restore:

```js
c.tnmask = { got: <sorted candidate {Tn} multiset>, want: <sorted skeleton {Tn} multiset> }
```

[`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py)
`provenance()` reads `card.get('tnmask')` and, when well-formed, carries it onto
the per-card `provenance` block that every store row of the card already shares
(the same mechanism as `partial_card` / `fidelity_drift`):

```json
"provenance": { …, "tnmask": { "got": "T1 T2", "want": "T1 T2 T3" } }
```

Design choices and their rationale:

1. **What, minimally.** The check is `got !== want`. Reproducing it offline needs
   exactly those two multisets — neither is recoverable from a restored row
   (`want` is an input; `got`'s `{Tn}` are gone after restore). Storing only a
   boolean verdict would preserve the *verdict* but not the *evidence* a
   re-measurement needs to hand-inspect a flag (expansion vs. benign reorder), so
   the pairing itself is the smallest **sufficient** form — smaller than the raw
   skeleton (128–500 B), and proportional to the masked-span count, not the card.
2. **Braces stripped.** Stored as `"T1 T2"`, not `"{T1} {T2}"`. The store's
   invariant is *"a raw `{Tn}` means an unrestored-placeholder defect"*; a
   provenance field full of `{Tn}` would blur that and risk tripping a future
   broad residue scan. Brace-stripping is a consistent bijection over both `got`
   and `want`, so multiset **equality is preserved** — `got !== want` is
   identical whether braces are present or not.
3. **Additive + backward-compatible.** New promotions carry `provenance.tnmask`;
   existing rows do not and are **not** back-filled (that evidence is gone). Every
   existing store reader uses `row.get(...)` / `row['provenance'].get(...)`, so an
   extra optional key is invisible to them. The flat store has no schema file to
   change.
4. **Not added to `pwg_ru_final_card.schema.json`.** `tnmask` is a
   *generation-time* provenance marker set by the harness in `accept()` — the
   same class as `partial` / `missing_fragments` / `presplit` / `frag_prov`,
   which are all emitted-card fields already absent from that schema. The strict
   card schema drives the **generation** schema (via `_strip_post_generation_fields`
   + reachable-defs, under a 5000-char Workflow-safety-classifier budget, H428 /
   Uprava FINDINGS §30) and is *documentation only* at runtime (the runtime gate,
   `validate_final_card_schema.validate_card`, is permissive on extras). Adding
   `tnmask` there would have forced a matching `_POST_GENERATION_CARD_FIELDS`
   entry to keep it out of the generation schema — extra surface for no
   correctness gain. It is documented here and in the `promote_final_cards.py`
   provenance handling instead.

## Offline detection

[`src/pilot/tnmask_offline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tnmask_offline.py)
reads the persisted pairing off a promoted row and applies the **same** equality
the harness's `accept()` applies:

- `tnmask_pairing(row)` → `(got, want)` or `None` (pre-H1226 / no field);
- `tnmask_measurable(row)` → whether the pairing is present;
- `tnmask_mismatch(row)` → `got != want` (a flag), or `None` when not measurable.

A future H1150-style pass computes the rate as `#mismatch / #measurable` over the
promoted store once real windows carry the field. The multiset **computation**
(`tokensOf` / `cardTokens`) is not re-implemented here — it ran at `accept()` time
and is persisted; the offline side only does the final comparison.

## What proves it

- **JS behavioral** —
  [`tnmask_persist_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tnmask_persist_test.js)
  extracts the **real** `accept()` / `tokensOf` / `cardTokens` / `RESTORE_SPEC`
  verbatim from a freshly generated harness (the `accept_sensecount_test.js`
  pattern, so it cannot drift from the generator) and asserts: a synthetic
  `{Tn}` expansion is stamped as `c.tnmask` with `got !== want` (and the card is
  still kept — soft), a faithful card gets `got === want`, the values are
  brace-less, and `RESTORE_SPEC` never lists `tnmask` (so restore can't strip it).
- **Python end-to-end** — `test_tnmask_persist_and_offline_detect` in
  [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
  runs the JS test, then feeds a card carrying an expansion pairing through the
  real `promote_final_cards.rows_for`, and shows the offline detector flags the
  resulting promoted row (**green with the field**) while an identical row with
  the field removed is reported as *not measurable* (**red without it**).

## Invariants held

`SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` both remain `= false` in
`gen_opt_harness2.py` (`window_selftest.py` pins both as literal needles). The
change persists provenance and adds an offline reader + tests; it arms nothing
and rejects nothing.

_Dr. Mārcis Gasūns_
