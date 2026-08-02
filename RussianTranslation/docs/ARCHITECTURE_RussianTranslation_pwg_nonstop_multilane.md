# ARCHITECTURE — PWG→RU nonstop multilane system

_Created: 02-08-2026 · Last updated: 02-08-2026_

Index: [PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md)

## Component map

```
pwg-ru-data (private repo + LFS)          SanskritLexicography (code, unchanged home)
├─ layers/    PW SCH PWKVN NWS            └─ RussianTranslation/src/pilot/*  (pipeline)
├─ tm/        translation-memory store (promoter-only writes)
├─ manifests/ per-window manifest-v2 + plans
├─ raws/      card raw inputs
├─ telemetry/ per-call usage ledger rows (cache fields split)
├─ gatelogs/  live-gate + canary receipts
├─ parked/    park-and-skip queue (R4.2)
└─ .github/workflows/gates.yml  (CI re-runs deterministic gates on PRs)

Lane A: PC (Windows)     Lane B: samskrte.ru      Lane C: Anthropic routine
account 1 (c4)           account 2, own OS user   account 3 (web login)
Task Scheduler tick      systemd timer            scheduled routine
headless CLI route       headless CLI route       in-session translation
direct promote (gated)   direct promote (gated)   gated PR → CI → auto-merge

account 4 = interactive (MG) — never automated (fence R4.3d); may backfill Lane A manually.
```

## Key contracts

1. **One quality bar, three lanes.** The deterministic gates (`ru_coverage.py`,
   `lang_parity_check.py`, sense-count, TNMASK, `canary_gate.py`) are pure Python and run
   identically: pre-promotion on CLI lanes, in-cloud + again in CI for Lane C. A card enters
   `tm/` only through the promoter path, whatever lane produced it.
2. **Scheduler semantics** (new `nonstop_scheduler.py`): loop of live-gate → bounded window →
   auto-promote → next; any hang at the kill ceiling is classified quota-first (§270,
   `reservation_timeline.py` differencing) and pauses the lane, resuming on the next tick after
   the weekly reset. `--cost-ceiling` is set at weekly scale (R3.2) — mandatory flag satisfied,
   no daily throttle.
3. **Auto-promote trial** (R2.1): `--stop-before-promote` is replaced by promote-on-clean-audit
   for 7 days from first use; the spot-checker (10% daily, full gates + one judge pass) and the
   halt rule (R4.1) are the compensating control. Authority expires at day 7 (contract §5).
4. **Telemetry is append-only and committed** — every call's `cache_creation_input_tokens` /
   `cache_read_input_tokens` split + TTL bucket (per the H2158/H2152 findings), per-lane, so the
   week-1 verdict and E3 read from one ledger.
5. **Fingerprints**: each CLI lane binds its own `config_dir_fingerprint`
   (`STOP_PROFILE_UNBINDABLE` stays fatal); profiles reach the prod box via scp only.

## Build vs reuse (prior-art verdicts)

| Piece | Verdict | Basis |
|---|---|---|
| Bounded window executor | REUSE `bounded_staged_run.py` / `headless_worker.py` | production route, R9/R10 bounds proven |
| Live gate + canary | REUSE `h963_c4_gate0_probe.py` + `canary_gate.py` receipts | H2159 mechanical GO |
| Audit/quality gates | REUSE `audit_window.py` + gate scripts | same bar all lanes |
| Cost/usage ledger | REUSE `economy_ledger.py`, extend per-lane column | exists |
| Scheduler loop | BUILD `nonstop_scheduler.py` (thin) | nothing loops today — this is the idle-time fix |
| Spot-check + halt | BUILD `spot_check_daily.py` | new control, R4.1 |
| Digest/packet | BUILD `digest_daily.py` / `weekly_packet.py` | new, R4.4 |
| Cloud worker (Lane C) | BUILD routine prompt + `cloud_window.py` entry | deliberate route extension, R2.4 |
| OpenRouter/DeepSeek client | BUILD minimal `openrouter_worker.py` (E1 only until a win) | no org-canonical client exists (SHARED_CODE checked) |
| A/B harness | REUSE `/ab-experiment` skill contract | org-standard frozen-manifest experiments |
| Multi-account bounds | REUSE `--max-accounts` + fingerprint validation | documented mode, now exercised |

## Risks pinned by design

- **Systema co-tenancy** on 193.232.229.92 → own user + systemd CPU/mem/IO caps (fence R4.3c).
- **LFS bloat / clone weight** → routines clone `pwg-ru-data` shallow + sparse (layers needed per window only).
- **Cloud lane bypassing telemetry** → PR template REQUIRES the usage block; CI fails the PR without it.
- **Auto-promote regression** → R4.1 freeze + revert of unreviewed windows; TM writes promoter-only.

_Dr. Mārcis Gasūns_
