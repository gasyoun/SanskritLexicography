# PLAN — PWG→RU nonstop multilane translation (2026)

_Created: 02-08-2026 · Last updated: 02-08-2026_

**Goal.** Kill the idle time in the PWG→RU pipeline. The constraint is NOT quota — the weekly
Opus caps were never reached; a full month was lost to windows waiting for a human to launch,
review, and promote. This plan turns the existing bounded-window pipeline into a nonstop,
multi-surface system: three runtime lanes (local PC · samskrte.ru prod box · Anthropic cloud
routines) on subscription Max accounts only, all data migrated to a private GitHub data repo,
auto-promotion on mechanical gates for a 1-week trial, and pre-registered A/B experiments that
decide — scientifically, never by assumption — what role cheap external lanes (DeepSeek /
OpenRouter / Grok 4.5) earn. Claude API is permanently out of scope by ruling.

Interview: 4 rounds / 16 rulings, MG, 02-08-2026, elicited by Fable 5 (`claude-fable-5`) via
`/ask`. Execution handoff: [H2175](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2175-Opus_RussianTranslation_pwg-nonstop-multilane-wave1_02.08.26.md).

## Layer docs

| Layer | Doc |
|---|---|
| Roadmap (waves, non-goals) | [ROADMAP_RussianTranslation_pwg_nonstop_2026Q3.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_pwg_nonstop_2026Q3.md) |
| Architecture (components, build-vs-reuse) | [ARCHITECTURE_RussianTranslation_pwg_nonstop_multilane.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_pwg_nonstop_multilane.md) |
| Implementation (ordered wave-1 steps) | [IMPLEMENTATION_RussianTranslation_pwg_nonstop_multilane.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pwg_nonstop_multilane.md) |
| Verification (acceptance criteria, risks) | [VERIFICATION_RussianTranslation_pwg_nonstop_multilane.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_pwg_nonstop_multilane.md) |

## Decisions taken (verbatim rulings, MG 02-08-2026)

| # | Fork | Ruling |
|---|---|---|
| R1.1 | Goal | Max-within-caps on **subscription only**. **Never** Claude API. The problem is idle time, not the weekly cap — "we never reach it; we have lost 1 month in waiting". |
| R1.2 | Budget / models | 4 Max accounts exist now; test down to possibly 1. DeepSeek API / any OpenRouter model SHOULD be considered for the simplest non-judgment tasks; Grok 4.5 subscription (3 months) in the mix. "Combine. Orchestrate. Test everything, take nothing for granted. Be scientific." |
| R1.3 | Runtime | Move ALL local-only data to GitHub repos first. Routines wanted, **additional to** local PC and samskrte.ru prod box — three surfaces total. |
| R1.4 | CLI accounts | 2–3 accounts with distinct `config_dir_fingerprint`s (the documented multi-account mode). |
| R2.1 | Bottleneck | **Auto-promote now, for 1 week.** After that reconsider staged auto-launch → auto-review. Human time is limited. |
| R2.2 | Data home | New private data repo + Git LFS (`pwg-ru-data`); code stays in SanskritLexicography. Credentials/profile dirs NEVER in git — scp to prod box only. |
| R2.3 | Cheap lanes | Pre-registered A/B first (frozen sample, one variable, blinded judge, pre-declared verdict rule); a lane gets a production role ONLY on a measured win at its price point. |
| R2.4 | Routines | **Routines also translate** — in-cloud lane from the data repo, same deterministic gates; a deliberate extension of the production route beyond headless-CLI-only. |
| R3.1 | Account map | 1 PC + 1 prod + 1 routines + 1 interactive. If the PC lane's limit ends, the interactive account may backfill it. After week-1 measurement judge again — possibly 3 production accounts on the prod box, if it makes sense. |
| R3.2 | Ceilings | **No per-day ceiling; the weekly quota is the only wall.** The tooling's mandatory `--cost-ceiling` (H2157) is satisfied with a weekly-scale bound, not a daily one. |
| R3.3 | Cloud landing | Gated PR per window: routine runs the deterministic gates in-cloud, opens a PR with cards + gate report + usage telemetry; CI re-runs gates; auto-merge on green during the trial. |
| R3.4 | Experiments | Order: **E1** DeepSeek-draft vs c4-draft → **E2** Grok 4.5 judge vs Opus judge → **E3** routine-lane vs CLI-lane. Then compare; see if more experimenting makes sense. |
| R4.1 | Halt rule | Daily automated spot-check of 10% of promoted cards (full gate suite + one judge pass). ≥2 sev-3 defects in a day, or ANY SAN-LOSS reaching the store → freeze that lane and revert its unreviewed windows; other lanes continue. |
| R4.2 | Ambiguity | Park-and-skip: unclassifiable item → `parked/` queue with a one-line reason; lane continues; parked items surface in the weekly review. |
| R4.3 | Fence | All four: (a) TM store written ONLY by the promoter path; (b) csl-orig + Cologne dictionary repos never touched by automation; (c) on samskrte.ru the runner gets its own user + systemd CPU/memory/disk limits, zero contact with the Systema stack; (d) profile dirs scp-only, and the interactive account is never used by an automated lane. |
| R4.4 | Human loop | 5-min daily digest + one 30-min weekly review (packet: per-lane throughput/cost/defect table, parked items, experiment verdicts, staged decisions due). |
| R5.1 | Profile fallback (amendment, MG 02-08-2026) | If c4 does not work, try **c1, c5, c6 in this order** for the Claude CLI lane — the scheduler's live-gate NO-GO/unbindable path walks this roster (each slot still needs its own validated fingerprint; `STOP_PROFILE_UNBINDABLE` semantics unchanged). |
| R5.2 | External-lane credentials (amendment, MG 02-08-2026) | Agent finds the OpenRouter/DeepSeek credentials in the org, not MG: **DeepSeek key is live in `ORS-FAQ/.env`** (`DEEPSEEK_API_KEY`, base `https://api.deepseek.com/`); **OpenRouter key sits in Systema prod `.env`** on 193.232.229.92 (fetch via `/ssh`; local clone has only the `.env.example` placeholder). Key VALUES never enter a repo — runners read them from env/`.secrets`. |

## Autonomy contract (binding on every automated lane)

1. **On ambiguity:** park-and-skip (R4.2). Never improvise a classification; never block the lane.
2. **Stop conditions:** the R4.1 halt rule; a quota hang (no 429 — the CLI *hangs*, §270) pauses
   the lane until the next scheduler tick after the weekly reset; `STOP_PROFILE_UNBINDABLE`,
   `STOP_COST_UNEVALUABLE` and every existing `STOP_*` semantic stays binding.
3. **Commit authority:** lanes commit/PR only to `pwg-ru-data` (gated, auto-merge on green) and
   telemetry paths; infra changes to SanskritLexicography land as PRs under H2175's scope.
4. **The fence:** R4.3, enforced by permissions/config (repo access lists, systemd units,
   separate OS user), not prose.
5. **Trial expiry:** auto-promote authority EXPIRES 7 days after the first auto-promoted window;
   the week-1 review (R4.4) must explicitly renew or replace it (staged auto-launch → auto-review).

## Prerequisites (Wave 0 — human, non-blocking for the wave-1 build)

- @DO MG: provide logins for the 3 non-interactive Max accounts (PC, prod box, routines) — the build proceeds with c4 alone until then (fallback roster c4 → c1 → c5 → c6 per R5.1).
- ~~@DO MG: DeepSeek/OpenRouter API key~~ — resolved by R5.2 (02-08-2026): DeepSeek key found live in `ORS-FAQ/.env`; OpenRouter fetchable from Systema prod `.env` via `/ssh`. Agent-doable, no human input needed.
- @DO MG: confirm Grok 4.5 access route for E2 (subscription session or API).

_Dr. Mārcis Gasūns_
