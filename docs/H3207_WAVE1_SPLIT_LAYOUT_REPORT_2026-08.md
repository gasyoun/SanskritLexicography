# H3207 Wave 1 report — DE|RU split vote layout

_Created: 21-08-2026 · Last updated: 21-08-2026_

Override executor: Grok 4.6 (`grok-4.6`) on a Sonnet-named file
([H3207 (Sonnet 5) — Wave 1 exec: DE|RU split vote layout](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3207-Sonnet_SanskritLexicography_h3199-wave1-exec_20.08.26.md)).
Grok × non-Fable: no dual-run residual.

Index:
[PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_RussianTranslation_REGLUE_VOTE_DE_RU_SPLIT_2026-08.md).

## What shipped

| Delivery | Status |
|---|---|
| W1.A `split_layout` in csl-pyutil 0.22.0 | shipped — PR against [sanskrit-lexicon/csl-pyutil](https://github.com/sanskrit-lexicon/csl-pyutil); 320 tests green including `tests/test_split_layout.py` |
| W1.B h180 reglue v6 | shipped — 15 cards, `digest_guard` green (sense bodies `7c9d3081…`, raw panel `094c4e88…`) |
| W1.C G5 `--pin-ids` recut | **STOP 2** — 1/150 cards drifted (see below). No new batch. Hub G5 file not overwritten. |
| W1.D hub | v6 copied to [h180_reglue_v6.html](https://gasyoun.github.io/vote/sheets/h180_reglue_v6.html); v5 kept |

## Stop 2 — G5 pin-ids

Command (worktree builders, store from the shared checkout):

`--pin-ids review/locks/g5-live-queue-batch1v3-2026-07-26.lock.json`

Result: **1 of 150** pinned cards changed content since the lock:

`row:001509:subcard:_sam~~h0_zz_nws00#NWS-1` (lock digest `2654403586604a1c`).

`card_digest` hashes the store `ru` and `de` **text**, not the HTML wrapper, so this is not the split-layout chrome. The recut refused, as the gate requires. Residual work: inspect that one store row against the lock-era text, then retry `--pin-ids`. Do not cut a fresh 150-card party.

## Решения, принятые без человека

| What was unclear | Chosen | The other fork |
|---|---|---|
| Architecture compressed H1808's three G5 panels; H1847 added a fourth (NWS tag legend) | Keep the tag legend in the **right** column under the print view | Dropping it would lose the facet explanation on tagged cards |
| `print_panel` on `pwg_de` runs `mark_cyrillic` | New `print_panel_de` — same Cologne renderer, no Cyrillic wrap | Would fail the "no Russian bodies in `.col-de`" selftest if a German string ever grew a Cyrillic run, and paints nothing useful today |
| Cologne has not merged 0.22.0 | Pin SanskritLexicography to the PR branch `h3207-split-layout` | Wait on the tag — the hub would stall |
| G5 digest drift on one card | Stop the recut (stop 2). Ship v6 anyway | Weakening `--pin-ids` or cutting a new `sheet_id` |

## v6 identity

- `sheet_id`: `h180-reglue-spotcheck-v6-2026-08-21`
- Output: gitignored `review/h180_reglue_v6_sheet.html`
- Sample: [h180_reglue_v6_sample.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/h180_reglue_v6_sample.jsonl)
- Lock: [h180-reglue-spotcheck-v6-2026-08-21.lock.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h180-reglue-spotcheck-v6-2026-08-21.lock.json)
- Fence held: no write to `pwg_ru_translated.jsonl`, no `reglue_delta.py` edit, no csl-orig.

## Browser pass

See the session close; v6 `gā` is the long-card canary.

_Dr. Mārcis Gasūns_
