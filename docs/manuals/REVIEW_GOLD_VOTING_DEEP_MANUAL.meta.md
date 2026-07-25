# REVIEW_GOLD_VOTING_DEEP_MANUAL.md — metadoc

_Created: 25-07-2026 · Last updated: 25-07-2026_

Companion record for
[REVIEW_GOLD_VOTING_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md).

## Purpose · audience · provenance

- **Purpose:** the deep operator manual for the RussianTranslation
  human-review subsystem — G5/G6/G7 gates, the 14-script gold chain, the HTML
  voting sheets, and the H1404 sheet↔decisions.json binding standard (voted.md
  item 8's ask).
- **Audience:** maintainer/operator (EN core, §1–§7); the human reviewer
  (§8, Russian).
- **Provenance:** authored 25-07-2026 by Fable 5 (`claude-fable-5`) under
  [H1404](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1404-Fable_SanskritLexicography_deep-manual-review-gold-voting-wave1_20.07.26.md)
  (Wave 1 of the org deep-manuals programme,
  [PLAN_ORG_DEEP_MANUALS_FABLE_WAVES_2026H2.md](https://github.com/gasyoun/Uprava/blob/main/docs/PLAN_ORG_DEEP_MANUALS_FABLE_WAVES_2026H2.md)).
  Script census cross-checked by an Explore subagent (Fable 5
  `claude-fable-5`) against the code, 25-07-2026.

## Staleness contract (H1246 detector)

```text
LAST_VERIFIED: 25-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1404
COMMANDS_SPOT_RUN: 9
```

## Verification block — what ran, 25-07-2026 (authoring pass)

Every executable claim in the manual was run during authoring; outputs are
quoted in the manual body. The nine commands behind `COMMANDS_SPOT_RUN`:

| # | Command | Result |
|---|---|---|
| 1 | `python src/review_binding.py --selftest` | OK — 14 checks (hash stability, 3 payload sites patched, chip, double-stamp refused, metadata-only lock, retro lock) |
| 2 | `python src/validate_decisions.py --selftest` | OK — 10 checks incl. the four demo refusals (corrupt sheet_id, hash mismatch, schema-invalid, unbound) + structural-fallback pair + legacy-accept logging |
| 3 | `python src/apply_decisions.py --selftest` | OK — validator-first abort proven; G6 route through real `gold_ingest.py`; G5 route through real `run_batch.py validate_review` (green) |
| 4 | `python src/validate_decisions.py review/decisions.json` | REJECTED (UNBOUND, named reason) — the handoff's gate |
| 5 | `python src/validate_decisions.py review/decisions.json --allow-legacy` | accepted against the `h178_da` retro lock; logged to `review/locks/allow_legacy.log` |
| 6 | `python src/build_g5_review_sheet.py --n 150` | 150 cards, `sha256:cea166b52217…`, lock written |
| 7 | `python src/build_g6_mqm_gold_sheet.py` | 20 cards, `sha256:e69ca4782356…`, lock written |
| 8 | simulated core-download exports of both starter sheets → `validate_decisions.py` | both OK (bound; 150/20 items) — the handoff's export gate |
| 9 | `python src/review_changelog_guard.py --selftest` | OK |

`/publish-safety-check` (25-07-2026, Fable 5 `claude-fable-5`): **GO** for all
H1404 public surfaces — locks verified metadata-only (0 Cyrillic card-body
chars; one structural sense-tag label «грамматическая рубрика» inside a card
id, ruled non-content), sheet HTML confirmed gitignored via `git check-ignore`,
secret grep clean, no personal data (reviewer fields empty).

## Ranked improvement backlog

1. Propose a native `content_hash` hook upstream in csl-pyutil (R2 follow-up)
   so `stamp()`'s string surgery can retire.
2. When the G5 core tranche is defined (DCS-frequency ranking), add a
   `--tranche` selection mode to `build_g5_review_sheet.py` (today: round-robin
   across roots).
3. A `validate_decisions.py --all` sweep mode over every `*_decisions.json`
   found under `review/`, for periodic hygiene.
4. G7 double-review sheet generator under the binding standard (today G7 runs
   on CSV packets only).
5. Wire `apply_decisions.py` into the org `/decisions-apply` skill text
   (claude-config side; the repo side is done).

## Limitations

- The Renou v1 export (`sanskritlexicography-renou-hypotheses_pilot_decisions.json`)
  is permanently unbindable: its sheet generation no longer exists, so no lock
  can be minted honestly. Documented in manual §4 as the motivating example.
- `apply_decisions.py` G5 assumes the operator's clone carries the gitignored
  queue CSV + store (they are absent in CI/worktrees by design); its selftest
  covers the logic with fixtures instead.
- The legacy `ord:N` judge annotations (32 defect rows) are routed, not
  requeued — the retranslation handoff is deliberately out of Wave-1 scope
  ([G5_REJECT_REQUEUE_AUDIT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/G5_REJECT_REQUEUE_AUDIT.md)).

## Revision history

| Date | Change | Model |
|---|---|---|
| 25-07-2026 | Manual + metadoc authored; binding standard shipped; starter packet generated (Wave 1, H1404) | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
