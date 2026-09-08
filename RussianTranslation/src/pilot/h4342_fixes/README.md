_Created: 08-09-2026 · Last updated: 08-09-2026_

# H4342 fixes — written, not applied (harness-blocked)

Two fixes from the [H4342 PWG-RU stall audit](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4342-Sonnet_SanskritLexicography_pwg-ru-translation-stall-full-audit_08.09.26.md),
diagnosed and written this session but **not executed** — both hit Claude Code's
auto-mode permission classifier (store mutation / main-tree edit), which correctly
requires a human to run them. Full argument in the session report to MG; this
folder exists so the human doesn't have to re-derive the commands from prose.

## `h4342_requeue_sanloss.py` — item (e), break the SAN-LOSS freeze loop

Removes the three store rows that trip `store_san_loss_scan` every day (all three
predate the stricter head-line SAN-LOSS check, FINDINGS §589; none are
`human_touched`), quarantining them with a full backup so the daily spotcheck's
`lane_freeze_pc.json` stops re-firing at 07:00.

```
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot
python <path-to-this-file>\h4342_requeue_sanloss.py            # dry-run first
python <path-to-this-file>\h4342_requeue_sanloss.py --execute  # writes the store
```

After a clean `--execute`, delete `pwg-ru-data/gatelogs/lane_freeze_pc.json` — its
own text says this is a human act, and with the cause fixed it is one.

## `h4213_wave_launch_FIXED.ps1` — item (d), idempotent canary window id

Copy over the live (gitignored) launcher once reviewed:

```
Copy-Item h4213_wave_launch_FIXED.ps1 C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot\output\h4213_wave_launch.ps1 -Force
```

Root cause: `--prefix h4213can` always resolves to the same window id once
`next_free_index()` sees no leftover files for that prefix — any survivor of a
prior attempt (partial cleanup, an in-flight lock, an auto-restarted retry) makes
the retry fail with `headless window id already exists`, not a transient error.
The fix stamps a fresh timestamp into the prefix every run, so no attempt can ever
collide with an earlier one's files.

_Dr. Mārcis Gasūns_
