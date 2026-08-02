# VERIFICATION — PWG→RU nonstop multilane

_Created: 02-08-2026 · Last updated: 02-08-2026_

Index: [PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md)

## Acceptance criteria (per Wave-1 deliverable)

| Deliverable | Proves it works |
|---|---|
| Data repo migration | `data_migrate.py --verify` reports 100% byte-parity (sha256) between local set and fresh `pwg-ru-data` clone; secrets scan clean; pipeline selftests green with `--data-root` pointed at the clone. |
| Auto-promote | A clean bounded window promotes with ZERO human commands, and the promotion record binds manifest hash + audit report exactly as /pwg-window-close does today; a window dated past `--auto-promote-until` refuses. |
| Spot-check + halt | Inject 2 synthetic sev-3 defects into a day's sample → `lane_guard.py` freezes the lane and reverts its unreviewed windows; other lanes' schedulers keep ticking. Inject 1 → no freeze. |
| Park-and-skip | Feed one unclassifiable card → `parked/` entry with reason, window completes with remaining cards. |
| Scheduler | 72h soak on PC + prod lanes: ≥95% of eligible ticks produced a window or a recorded pause reason (quota-hang / frozen / no-GO); zero unexplained idle ticks — the metric that kills "lost month" waiting. |
| Prod-box fence | Load test the runner while probing Systema endpoints: p95 latency unchanged; `systemd-cgtop` shows caps binding. |
| Digest/packet | 7 consecutive daily digests + 1 weekly packet generated from real ledgers; packet lists the staged decisions due (auto-promote renewal, account map). |
| CI gates (stub) | A PR with a failing TNMASK card is blocked; with all-green gates + telemetry block, auto-merge label applies. |

## Experiment verdicts (pre-declared, Wave 3)

- E1: DeepSeek wins a production draft role iff its gate-pass rate is within 5 pp of c4 AND blinded judge severity distribution is not worse at p<0.05 — else it gets, at most, mechanical-QA lanes.
- E2: Grok replaces Opus as judge iff κ ≥ 0.8 against Opus on ≥60 already-reviewed cards.
- E3: Routine lane is a peer lane iff per-card quality parity (same rule as E1) and cost/card within 1.5× of CLI lane.

## Risks & spikes register

| Risk | Likelihood | Mitigation / spike |
|---|---|---|
| Routine sessions can't sustain a full window (session length/limit) | medium | Spike in Wave 2: one 5-card mini-window in-cloud before building the full loop. |
| LFS quota/cost on GitHub for bulk layers | medium | Inventory sizes first (step 1); if >5 GB hot set, sparse-checkout per window; only then consider paid data packs. |
| Quota-hang detection misfires (kill vs throttle vs latency, §270 classes) | medium | Reuse `reservation_timeline.py` differencing; soak-test verdicts reviewed in week-1 packet. |
| Auto-promote lets a subtle register/quality drift through (gates are structural, not stylistic) | medium | The 10% judge pass in `spot_check_daily.py` is the stylistic net; week-1 review rules on staying auto. |
| 4-account telemetry attribution errors | low | `STOP_PROFILE_UNBINDABLE` stays fatal; per-lane ledger columns keyed by fingerprint. |
| Prod-box co-tenancy harms Systema | low | Fence R4.3c enforced by systemd caps; load test before enabling the timer. |
| DeepSeek/OpenRouter ToS or data-handling surprise | low | E1 uses non-sensitive dictionary text only; rights-uncertainty is not a stop (standing policy), confirmed-prohibition would be. |

_Dr. Mārcis Gasūns_
