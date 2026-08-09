# IMPLEMENTATION — PWG→RU nonstop multilane, Wave 1 (ordered)

_Created: 02-08-2026 · Last updated: 08-08-2026_

Index: [PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md).
Working dir for all steps: `C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation` (via a session-unique worktree — the main tree is guarded). Executor: Opus 5 (`claude-opus-5`) per [H2175](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2175-Opus_RussianTranslation_pwg-nonstop-multilane-wave1_02.08.26.md).

## Stage A — data repo (steps 1–4)

1. **Inventory the local-only working set.** Script `src/pilot/data_inventory.py` (new): walk the
   RussianTranslation data dirs (layers PW/SCH/PWKVN/NWS, TM store, manifests, raws, gate logs),
   emit `data_inventory.json` (path, size, sha256, class). No moves yet. Depends on: nothing.
2. **Create `gasyoun/pwg-ru-data` (private).** `gh repo create --private`; layout per the
   architecture doc; `.gitattributes` routing `layers/` and `raws/` bulk through LFS;
   `.github/workflows/gates.yml` stub. Depends on: 1.
3. **Migrate + verify.** `src/pilot/data_migrate.py` (new): copy per inventory, re-hash on the
   clone, byte-parity report; secrets scan (no profile dirs, no OAuth tokens — fence R4.3d)
   before first push. Register one dataset row in
   [kosha datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json). Depends on: 2.
4. **Repoint the pipeline.** Add `--data-root` to `coordinator.py` / `bounded_staged_run.py` /
   `headless_worker.py` path resolution (default = current local layout, so nothing breaks);
   selftests updated (`bounded_staged_run_selftest.py`). Depends on: 3.

## Stage B — auto-promote + controls (steps 5–8)

5. **Promote-on-clean-audit.** New flag `--auto-promote-until <ISO date>` on
   `bounded_staged_run.py`: a clean `AWAITING_REVIEW` checkpoint flows into the existing
   /pwg-window-close promotion path mechanically; refuses past the expiry date (contract §5).
   All `STOP_*` semantics unchanged. Depends on: 4.
6. **Spot-checker.** `src/pilot/spot_check_daily.py` (new): sample 10% of the day's promoted
   cards, run full gate suite + one judge pass, write `spotcheck_<date>.json` to
   `pwg-ru-data/telemetry/`. Depends on: 5.
7. **Halt + revert.** `src/pilot/lane_guard.py` (new): evaluates R4.1 (≥2 sev-3/day or any
   SAN-LOSS in store) → writes `lane_freeze.json` (schedulers refuse frozen lanes), reverts the
   lane's unreviewed windows via the existing quarantine/requeue path (`autosplit_requeue.py`
   evidence conventions). Depends on: 6.
8. **Park-and-skip.** Manifest-builder and gate unknown-verdict paths route the item to
   `pwg-ru-data/parked/<date>_<key>.json` with a one-line reason; lane continues (R4.2). Depends on: 4.

## Stage C — scheduler + prod runner (steps 9–12)

9. **`src/pilot/nonstop_scheduler.py`** (new, thin): tick = live-gate (`h963_c4_gate0_probe.py`
   + canary receipt) → prepared window → bounded run (`--auto-promote-until`) → telemetry commit
   → next; quota-hang classification via `reservation_timeline.py` → lane pause until post-reset
   tick; weekly-scale `--cost-ceiling` (R3.2). Depends on: 5, 7, 8.
10. **PC lane wiring.** Task Scheduler job running the scheduler tick hourly under profile c4;
    logs to `pwg-ru-data/telemetry/`. Depends on: 9.
11. **Prod-box runner.** Via /ssh on 193.232.229.92: user `pwgrun`; clone code + data repos;
    Python env; scp profile for account 2; systemd service+timer with `CPUQuota=`,
    `MemoryMax=`, `IOWeight=` caps (fence R4.3c — Systema untouched); same scheduler tick.
    Depends on: 9.
12. **Digest + weekly packet.** `src/pilot/digest_daily.py` + `weekly_packet.py` (new): read the
    ledgers, emit the 5-min daily digest and the 30-min weekly packet (throughput/cost/defects
    per lane, parked items, experiment verdicts, staged decisions due) to `pwg-ru-data` +
    a GitHub issue ping (R4.4). Depends on: 6, 9.

## Stage D — wave-2/3 stubs (steps 13–15, build-behind-flag)

13. **CI gates.** Fill `gates.yml`: on PR touching `tm/`-bound card payloads, run the
    deterministic gate suite + require the usage-telemetry block; auto-merge label on green
    (Lane C consumes this in Wave 2). Depends on: 3.
14. **Cloud worker entry.** `src/pilot/cloud_window.py` (new): window loop importable without the
    headless CLI (in-session translation for the routine), emitting the same manifest/telemetry
    shapes. Not scheduled in Wave 1. Depends on: 4.
15. **E1 scaffold.** `src/pilot/openrouter_worker.py` (minimal client) + frozen stratified
    ~40-card sample manifest under `experiments/E1_deepseek_vs_c4/` with the pre-declared verdict
    rule (R2.3/R3.4), staged until the API key lands (Wave 0). Depends on: 4.
    **H2439 (08-08-2026) retarget:** default generator model + PRICE_* table on
    [`deepseek_arm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/deepseek_arm.py)
    = DeepSeek-V4-Flash-0731 (`deepseek-v4-flash`, $0.14 / $0.0028 / $0.28); prep-pack
    sidecar producer [`prep_pack.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/prep_pack.py)
    (store_write never); E1 sample + Flash win rule under
    [`experiments/E1_deepseek_vs_c4/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/experiments/E1_deepseek_vs_c4/).
    Org pricing/role map:
    [DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md).
    Paid bulk E1 measurement still residual (scaffold only until deliberately run).

Each step lands as its own commit in the worktree branch; PR per stage; selftest green before the next stage starts.

_Dr. Mārcis Gasūns_
