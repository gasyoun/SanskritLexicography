# Metadoc — H920_NO_PWG_SANLOSS_ROOTCAUSE_AND_GUARD_2026-07-14.md

_Created: 14-07-2026 · Last updated: 14-07-2026_

- **Purpose.** Root-cause writeup + delivered-guard record for the no_pwg SAN-LOSS /
  `missing_senses` defect that made the [H911 gate](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md)
  FAIL. Read before touching the sense-count guard or reasoning about whole-dropped senses.
- **Audience.** A future session extending/validating the SAN-LOSS guard, or running the gated
  live acceptance that would exercise it end-to-end.
- **Provenance.** Handoff [H920](https://github.com/gasyoun/Uprava/blob/main/handoffs/H920-Sonnet_SanskritLexicography_pwg-ru-no-pwg-san-loss-missing-senses-offline-fix_14.07.26.md);
  executor Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode, owner-authorized higher-tier override of the
  minted Sonnet 5 tier. Offline only.
- **Evidence base.** H911 committed evidence; the immutable H818 fc1 snapshot
  (`darv_i~~h0_zz_pw` skeleton + output + `run_pilot_wf.h818_fc_w01.js` inputs, showing
  `senses:3` computed and discarded); the frozen `no_pwg_w05_rq1` audit report.
- **Key claims a reader relies on.** (1) The genuine silent SAN-LOSS class is (a) model omission,
  not (b) self-heal collapse or (c) split/merge drop — those flag `partial`. (2) `accept()` is only
  an `<ls>`/`{#` token match, blind to a dropped citation-free sense. (3) The no_pwg portrait's
  `senses:[]` left no expected count to compare against. All three are backed by quoted evidence.
- **Delivered artifacts.** `src/pilot/sense_count.py` (new shared primitive); portrait
  `source_senses` stamp + sense-completeness prompt rule in `_pilot_gen_merged.py`; `sense_loss`
  gate in `audit_window.py`; `MISSING-SENSE` HARD flag in `audit_window_en.py`; 4 `test_h920_*`
  pins in `window_selftest.py`; LANG_PARITY entry `sense_count_sanloss_guard_h920` (SHARED).
- **Limitations / follow-ups.** The deepest fix — consuming `INPUT[k].senses` in the harness
  `accept()` — needs a live run to validate and is deferred (gated by H911/H909). NWS-entry
  (`N.` format) drops are not counted by this guard. The guard fires only for sources with an
  explicit `〉`/`N)` numbered-sense count; a portrait predating the H920 stamp is skipped.
- **Revision history.** 14-07-2026 — created with the report at handoff-close.

_Dr. Mārcis Gasūns_
