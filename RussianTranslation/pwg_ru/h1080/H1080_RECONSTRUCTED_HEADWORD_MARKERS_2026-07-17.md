# H1080 — marking the 468 reconstructed headwords

_Created: 17-07-2026 · Last updated: 17-07-2026_

Follow-up to [`H1080_STORE_REPAIR_REPORT_2026-07-17.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1080/H1080_STORE_REPAIR_REPORT_2026-07-17.md)
([PR #510](https://github.com/gasyoun/SanskritLexicography/pull/510)). Authorised by the owner
17-07-2026. **No `h` value was changed.** Only provenance was added.

## Why

PR #510's two halves are not the same kind of act, though its report gives them the same word.

| Class | What happened | Evidence-based? |
|---|---:|---|
| Placeholder rows | **668 of 670** restored from content-addressed raw inputs or historical harness placeholder maps bound to the recorded `input_raw_sha256` | **Yes** — re-computed, not guessed |
| C-42 pair | **2** rows quarantined, explicitly because "retaining their text would fabricate evidence" | **Yes** — refused to guess |
| Null `h` rows | **468** filled by `canonical_record_head()`, which *derives* a head from the row's own key (its docstring: "a stable display head from **immutable row/subcard identity**; the suffix encodes the upasarga") | **No** — derived from identity |

The derivation was not avoidable: the model-authored `h` was destroyed at the stitch flatten
before it was ever persisted — absent from the store, already `null` in the archived
`wf_output`, absent from real portraits, and the TM is built *from* the store
([Uprava FINDINGS §94](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)).

The problem was that it was **silent**. Provenance still read the original `generator` /
`generated_at`, so 468 derived values were indistinguishable from model-authored ones — the
packet's own **C-05** hazard — and `h is None` fell 468 → 0, clearing the one query that could
find them ([FINDINGS §95](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)).

## What was measured

Recovered by diffing PR #510's pre-repair backup (`…pre-h1080.cc1d544ed92d201c…bak`, SHA
verified against its report) against the live store. Alignment keys on `subcard` + `ru` + `de` —
fields the repair never rewrote — and the tool refuses to write unless every number matches
PR #510's own report.

| Check | Result |
|---|---:|
| Pre-repair backup SHA | `cc1d544ed92d201c…` ✓ matches report |
| Backup / current rows | 11,605 → 11,603 |
| Rows aligned | 11,603 |
| Unmatched (removed) | **2** — and they *are* the C-42 quarantine pair |
| `h` null before, derived now | **468** |
| …of which `iast` also synthesised | **462** |
| …of which `grammar` defaulted to `""` | **468** |
| **Distinct derived heads across all 468** | **14** |

That last row is the cost, quantified: 468 rows collapse onto **14** values (`'vid'` ×269,
`'vas'` ×88, `'dah'` ×56). `vid~~h0_00_pwg00` and `vid~~h2_00_pwg00` are *different homonyms by
their own keys* and both derive to `'vid'`. Since the store's commonest real `h` are homonym
**numbers** (920×`'1'`, 160×`'3'`) and real ones are rich free text (`'2. bhid'`,
`'PW 3 (с anu, отсылка к entry 5)'`), the true values were plausibly `'1'`/`'2'`.

## What was written

Each of the 468 rows gained, in `provenance` only:

```json
{
  "h_reconstructed": true,
  "h_reconstruction_pr": 510,
  "h_reconstruction_method": "canonical_record_head: identity-derived (row.iast if present, else key1 + the sub-card upasarga suffix); NOT recovered from source evidence",
  "h_reconstruction_note": "… no offline source exists (FINDINGS §94) … Re-translation is required for the real value."
}
```

plus `iast_reconstructed` (462) and `grammar_defaulted_empty` (468).

Verified by re-reading from disk: rows **11,603** (unchanged) · `h_reconstructed` **468** ·
`h == null` **0** (no `h` value altered). Control: the evidence-recovered row
`_bid~~h0_zz_pwkvn` (`h = '1. {#Bid#} [PWKVN supplement: sense 7 mit antar]'`) is correctly
**not** stamped — derived and recovered rows are now partitionable.

Backup: `pwg_ru_translated.jsonl.pre-hstamp.20260717T094406Z.bak` (uncommitted, gitignored, as
the store is).

## Reproduce / audit

```sh
python src/mark_reconstructed_headwords.py            # dry run, read-only
python src/mark_reconstructed_headwords.py --apply    # idempotent
```

Idempotent — a second run reports `already stamped: 468` and rewrites the same markers. It is
pinned to the pre-repair backup's hash and refuses if the store has moved, so it cannot be
aimed at a different state by accident.

## Open

The markers make the 468 **auditable**, not **correct**. The true headwords still require
re-translation, which needs live generation calls and remains owner-gated behind the pwg_ru
card-size ceiling ruling. Query them with
`provenance.h_reconstructed == true` — that is now the re-translation worklist.

_Dr. Mārcis Gasūns_
