# ROADMAP — PWG→RU nonstop translation, 2026 Q3

_Created: 02-08-2026 · Last updated: 02-08-2026_

Index: [PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md)

## Wave 0 — prerequisites (human; non-blocking for Wave 1 build)

| Item | Owner | Unblocks |
|---|---|---|
| Logins for 3 non-interactive Max accounts (PC / prod / routines) | MG | Waves 1–2 full lane count (build proceeds on c4 alone) |
| DeepSeek or OpenRouter API key | MG | Wave 3 E1 |
| Grok 4.5 access route (session or API) | MG | Wave 3 E2 |

## Wave 1 — data repo + nonstop CLI lanes + auto-promote trial (H2175)

Deliverables, in dependency order:

1. **`pwg-ru-data` private repo + LFS** — full inventory and migration of the local-only working set (PW/SCH/PWKVN/NWS supplement layers, TM store, manifests, card raws, gate logs, telemetry ledger). Unblocked by: nothing.
2. **Auto-promote + halt machinery** — promote clean `AWAITING_REVIEW` windows mechanically; daily 10% spot-check; freeze-lane + revert on threshold breach (R4.1); park-and-skip queue (R4.2). Unblocked by: 1.
3. **Nonstop scheduler** — quota-aware loop (gate → window → auto-promote → next), hang-detected-as-quota pause, weekly-reset resume; runs identically on PC (Task Scheduler) and prod box (systemd timer). Unblocked by: 2.
4. **Prod-box runner** — dedicated OS user, systemd resource limits (fence R4.3c), profile scp sync, clone of code + data repos. Unblocked by: 3.
5. **Daily digest + weekly review packet generator** (R4.4). Unblocked by: 2.

Exit criterion: two lanes (PC + prod) run ≥3 consecutive days with zero human touches, all promotions gated, digest arriving daily.

## Wave 2 — routines lane (cloud translation)

1. Routine watchdog (monitor telemetry in `pwg-ru-data`, file alert issues).
2. Cloud worker: routine translates cards from the data repo, runs the deterministic gates in-cloud, opens a gated PR per window (R3.3); CI re-runs gates; auto-merge on green.
3. Promotion parity: cloud-landed cards flow through the same promoter/TM path as CLI lanes (fence R4.3a).

Exit criterion: one routine-produced window auto-merged green and promoted, with per-call usage telemetry recorded.

## Wave 3 — pre-registered experiments (in order; `/ab-experiment`)

| # | Question | Arms | Judge |
|---|---|---|---|
| E1 | Can DeepSeek draft PWG cards that survive the gates? | DeepSeek-draft vs c4-draft, frozen ~40-card stratified sample (incl. hard homonyms), identical prompts | blinded Opus + deterministic gates |
| E2 | Is Grok 4.5 a valid cheap judge? | Grok verdicts vs Opus verdicts on already-reviewed windows (κ target pre-declared) | agreement stats |
| E3 | Does the routine lane match CLI quality/cost per card? | routine-lane vs CLI-lane, same model, same sample | E2's winning judge |

Then compare all three; decide whether more experimenting makes sense (R3.4).

## Wave 4 — week-1 verdict + consolidation

- Rule on: end/renew auto-promote (contract expiry, R2.1); staged auto-launch → auto-review; account consolidation (4 → n, possibly 3 production accounts on the prod box, R3.1); production roles for cheap lanes (only on E1–E3 wins, R2.3).

## Non-goals

- Claude API in any form (R1.1 — permanent).
- More than 4 Max accounts; any quota-multiplication scheme.
- Batching multiple cards per call (H2152 ruling stands: one card per call).
- Any automated write to csl-orig / Cologne repos, or direct TM-store writes (R4.3).
- Weakening deterministic gates (SAN-LOSS/TNMASK/schema/sense-count) on any lane.

_Dr. Mārcis Gasūns_
