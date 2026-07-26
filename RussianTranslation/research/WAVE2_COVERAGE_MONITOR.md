# Wave-2 coverage monitor — pwg_ru verb-root drain vs the B2/B1/B3 gate

_Created: 26-07-2026 · Last updated: 26-07-2026_

Living monitor (append-only, like [ACL_ANTHOLOGY_MONITOR.md](ACL_ANTHOLOGY_MONITOR.md))
tracking [ROADMAP_ACL_LESSONS_2026.md](ROADMAP_ACL_LESSONS_2026.md)'s Wave-2 trigger:
"**Wave 2 (after ~50% coverage):** B1 gold set + scoring, B2 synset crosswalk +
benchmark packaging (including [sinonimy/](sinonimy/README.md)'s standalone
PWG-sense crosswalk, scoped out of H1491), B3 milestones 4–5." Minted H1666
(26-07-2026) after a user question about when Sinonimy gets wired in — the
roadmap gates that on this number, not a date.

## Metric

`RussianTranslation/src/pilot/verb_worklist.py`'s own defined scope: the
`verbs01` case-header universe (1,882 PWG roots) ∩ `scale_manifest.freq.json`
DCS-attestation → **749 DCS-attested roots**, the fixed denominator. Coverage
= roots promoted into `src/pwg_ru_translated.jsonl` / 749. **50% = 375/749
promoted.**

Recompute:
```sh
cd RussianTranslation && python src/pilot/verb_worklist.py
```
Reads the `promoted: N REMAINING: M` line from stdout; `N` is the numerator.

**Not the metric:** the store also holds 11,000+ sense rows across 254
`key1` cards — most are non-root sub-cards (derived nominals, PW/SCH
addenda) that don't count toward the 749-root universe. Root-count is the
only metric the roadmap's "coverage" language maps to (Wave-1's translation
drain is root-by-root).

## Log

| Date | Promoted | Denominator | % | Δ since last | Source |
|---|---|---|---|---|---|
| 04-07-2026 | 48 | 749 | 6.4% | — | `.ai_state.md` line 1123 |
| 26-07-2026 | 48 | 749 | 6.4% | +0 (3-week stall) | H1666 dig — fresh re-run of `verb_worklist.py` reproduced the identical 04-07-2026 figure |

## Watcher

A monthly `claude.ai` cloud routine (RemoteTrigger, created H1666) re-runs the
recompute command above on the 1st of each month, appends a row to the Log
table, and — the first time promoted/749 ≥ 0.50 — opens/updates a GTD
`@DECIDE` row in
[Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
flagging the Wave-2 gate as reached, then stops flagging (one-time flip, not
recurring noise). See H1666 for the routine ID and prompt.

_Dr. Mārcis Gasūns_
