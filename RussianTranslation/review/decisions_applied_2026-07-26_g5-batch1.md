# G5 batch 1 — decisions applied + reviewer abort acted on (H1655)

_Created: 26-07-2026 · Last updated: 26-07-2026_

Audit record per the `/decisions-apply` runbook for
[review/locks/g5-live-queue-batch1-2026-07-25.lock.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/g5-live-queue-batch1-2026-07-25.lock.json)
(sheet `g5-live-queue-batch1-2026-07-25`, 150 cards). The decisions export
(`review/g5-live-queue-batch1-2026-07-25_decisions.json`) is a personal voting
artifact and stays uncommitted; its binding was validated against the lock
(`sha256:cea166b52217…`) before anything was applied. Applied by Fable 5
(`claude-fable-5`), reviewer MG.

## Verdict counts

| verdict | n | route |
|---|---:|---|
| approve (print-ready) | 3 | `apply_decisions.py --gate G5` → `src/_review_queue.csv` → `run_batch.py apply_review` → store `review_status=approved` |
| reject | 2 | same pipeline → store `review_status=needs_review`, reviewer note preserved in `human_review.notes` |
| unvoted | 145 | reviewer ABORTED the round at 5/150 — see below; unvoted cards return to the queue and are re-presented in batch1v2 |

Store backup made by `apply_review`: `pwg_ru_translated.jsonl.backup.20260726070803`.

## The abort and what it mandated

Reject note on `row:000243:subcard:_bid~~h0_00_pwg00#head` (verbatim, the
operative part): «Я не должен искать немецкие слова в русском переводе. Ты
должен. Перед тем как мне показывать. … Я не буду дальше голосовать. Переделай
все». Diagnosis of the two rejected cards:

- `_adika#1` — RU shows `<ab>` token `s. u.` (German „siehe unter"). This token
  IS render-translated to «см.» by
  [src/pwg_ab_ru.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py)
  — but batch 1 displayed **raw store markup**, so the reviewer saw the German
  token, not the print rendering.
- `_bid#head` — `fg.` (German „folgende") survives inside an `<ls>` citation
  tail; the H1302 prose scanner deliberately masks `<ls>` spans, so no
  mechanical layer covered this class before a human saw it.

## Actions taken (same pass)

1. **Reader-visible German gate** —
   [src/review_residue_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_residue_gate.py):
   three layers (H1302 prose scan class-b · H1303 `<ab>` classification vs
   `RU_MAP` · `<ls>`-tail `fg./fgg.`). Live-queue sweep: **637 of 11,163 cards
   (5.7%) flagged** (457 prose hits, 371 ls-tail, 145 German-`<ab>`), 10,526
   clean.
2. **batch1v2 sheet** — `g5-live-queue-batch1v2-2026-07-26` (150 cards), built
   by the updated
   [src/build_g5_review_sheet.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_g5_review_sheet.py):
   gate-screened candidates only, already-decided cards excluded, and the RU
   panel now shows the **print rendering** (`RU_MAP` applied, original token in
   a hover tooltip) with the raw store markup in a second panel for
   note-quoting. Lock:
   [review/locks/g5-live-queue-batch1v2-2026-07-26.lock.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/g5-live-queue-batch1v2-2026-07-26.lock.json).
   All 150 cards verified German-free post-build.
3. **Positional-id drift fix** — 2 of 5 votes initially failed
   `validate_review` («not found in store»): `row:NNNNNN:` review-ids embed the
   store line position at queue-mint time (queue minted 06-07 against an
   11,163-row store; store now 11,603 rows). `run_batch.py` lookups now fall
   back to the stable `subcard:<sub>#<tag>` tail when the positional id goes
   stale; pinned by a new case in `apply_decisions.py --selftest`, and the
   whole H1404 selftest lane (binding · validate · apply · residue gate ·
   H1302 scan) is now wired into CI.

## Reviewer-note directives carried forward (not closed here)

- **Source-translation cross-check before human review** (notes on all 3
  approvals): before a card reaches a sheet, check whether its `<ls>` sources
  have published RU/EN/DE translations (RU via SamudraManthanam, EN via
  Wisdomlib, DE via archive.org scans) and surface them next to the card —
  otherwise the human has nothing to verify against. Queued as follow-up work
  in the H1655 handoff.
- **Orthographic-note markup class** (note on `_as#1`): spans like `{#AstizWa#}`
  after „Bisweilen wird der nachfolgende Laut …" are orthographic remarks, not
  translations — need a dedicated markup class. Queued likewise.

Handoff:
[H1655](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1655-Fable_SanskritLexicography_g5-batch1-decisions-german-residue-gate_26.07.26.md).
Rejected cards never re-enter a sheet unless their store text changes
(`/decisions-apply` contract; both rejects sit in `needs_review` with the
reviewer notes attached).

_Dr. Mārcis Gasūns_
