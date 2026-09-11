_Created: 08-09-2026 · Last updated: 11-09-2026_

# H4342 fixes — applied 11-09-2026 (H4530)

Two fixes from the [H4342 PWG-RU stall audit](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4342-Sonnet_SanskritLexicography_pwg-ru-translation-stall-full-audit_08.09.26.md),
written 08-09-2026 but not executed then (Claude Code's auto-mode permission classifier
correctly holds store mutation / main-tree edits for a human). **H4530 reviewed, corrected
and executed both on 11-09-2026** — see the corrections below before re-reading the 08-09
prose, which described the pre-correction scripts.

## `h4342_requeue_sanloss.py` — item (e), break the SAN-LOSS freeze loop

Removes the three store rows that trip
[`spot_check_daily.store_san_loss_scan`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/spot_check_daily.py)
every day (all three predate the stricter head-line SAN-LOSS check,
[FINDINGS §589](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md);
none are `human_touched`), quarantining them with a full backup so the daily spotcheck's
`lane_freeze_pc.json` stops re-firing at 07:00.

```
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
python src\pilot\h4342_fixes\h4342_requeue_sanloss.py            # dry-run (default)
python src\pilot\h4342_fixes\h4342_requeue_sanloss.py --execute  # writes the store
```

**Three defects H4530 had to fix first, all of the H255/H3658 wrong-store class:**

1. `SRC` was hardcoded to the H4342 session's own worktree
   (`SanskritLexicography-h4342-27494`), long since removed — the script could not import
   at all from any other checkout. Paths now resolve from `__file__`.
2. `STORE` was hardcoded to `pwg-ru-data/tm/pwg_ru_translated.jsonl` — the **mirror**, not
   the canonical store. A run on 08-09 removed the three rows from the mirror while the
   canonical `RussianTranslation/src/pwg_ru_translated.jsonl` kept them, so
   `audit_store_gates.py` still reported `hard_flagged_rows=3` (and `only_src=3`) and the
   spotcheck kept re-freezing. Resolution is now
   [`store_path.canonical_store`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py)
   / `canonical_data_repo`, exactly what `promote_final_cards.py` and `audit_store_gates.py`
   use.
3. The quarantine/requeue filenames carried a frozen `DATE_TAG`, so a second run silently
   overwrote the first run's evidence. The tag defaults to today, is overridable with
   `--date-tag`, and an existing quarantine file is now refused rather than clobbered.

The write goes through
[`store_write.locked_store_rewrite`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_write.py)
(the H2146 lock: `PromoteClaim` across the read-guard-write window, unique fsynced backup,
atomic LF-only replace) rather than the draft's hand-rolled claim + `_atomic_write_rows`.

### Recovery runbook row (beside `restore_store_rows_from_mirror.py`)

| Symptom | Tool | Reversal |
|---|---|---|
| Mirror's `ru` drifted from src (GAPS §16) | [`src/restore_store_rows_from_mirror.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/restore_store_rows_from_mirror.py) `--write` | the tool's own `.bak` beside the store |
| Named rows re-trip a hard gate and re-freeze the lane | `src/pilot/h4342_fixes/h4342_requeue_sanloss.py --execute` | `--restore <quarantine.jsonl> --execute` (printed by the run) |

The removed rows stay in
`pwg-ru-data/gatelogs/h4342_sanloss_requeue_<tag>.quarantine.jsonl`, their keys in the
`.requeue.keys.txt` sibling, so the work is queued, not discarded.

After a clean `--execute`, `pwg-ru-data/gatelogs/lane_freeze_pc.json` is deleted **by a
human** — its own text says so, and with the cause fixed it is one line.

## `h4213_wave_launch_FIXED.ps1` — item (d), idempotent canary window id

Root cause: `--prefix h4213can` always resolves to the same window id once
`next_free_index()` sees no leftover files for that prefix — any survivor of a prior
attempt (partial cleanup, an in-flight lock, an auto-restarted retry) makes the retry fail
with `headless window id already exists`, not a transient error. The draft stamps a fresh
timestamp into the prefix every run.

**Already applied to the live (gitignored) launcher on 10-09-2026**, with one extra
improvement H4530 kept: the stale-lease sweep also drops every `h4213can*` lease, not just
the three named ids.

**H4530 upstreamed the fix one level down, where it survives a regenerated launcher.** The
launcher is gitignored, so a per-run timestamp in *that file* protects only that file. The
real defect was in
[`no_pwg_scale_plan.used_window_indices`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py):
a headless root's existence is decided by
`<coord_dir>/artifacts/<root>/execution_manifest.<root>.json`, but the index picker only
scanned `run_pilot_wf.<root>.js` and `wf_output.<root>.json` — so a run that prepared a
window and then died was invisible to the picker and fatal to the guard. It now counts
prepared-but-unfinished roots, bounded so a timestamp-prefixed leftover is not misread as a
giant index. Pinned by
[`src/pilot/h4530_window_id_collision_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4530_window_id_collision_selftest.py)
(5 checks) and demonstrated against the live coordinator dir, zero spend, by
[`src/pilot/h4530_live_rearm_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4530_live_rearm_probe.py).

_Dr. Mārcis Gasūns_
