# H1110 Phase 6 — c4 bounded ladder: `HEALTH_NOGO_BY_ENVIRONMENT`

_Created: 18-07-2026 · Last updated: 18-07-2026_

Terminal record for H1110 Phase 6 (bounded c4 live-acceptance ladder). The money-risk gate worked
exactly as designed: the c4 profile is mechanically proven and every offline pipeline gate is green,
but the Anthropic host is degraded. The ladder was first deferred with **0** paid calls; a single
**confirmation health probe** was later fired (18-07, at the owner's request) and **re-confirmed the
NO-GO** — so no canary, no batch, no production translation.

## Verdict

**`HEALTH_NOGO_BY_ENVIRONMENT` · CANARY NOT LAUNCHED · RUNG 3 NOT ENTERED · NO PRODUCTION TRANSLATION · 1 confirmation health call (still NO-GO), canary + batch unspent.**

## Mechanical profile proof — PASSED (offline, deterministic)

The profile binding is unambiguous — this is **not** `STOP_PROFILE_UNBINDABLE`:

| Fact | Value | Source |
|---|---|---|
| `c4` validated roster slot | `validated=1`, `parked_until=0` (exactly one `c4`) | `D:\ClaudeTools\pwg_ru\max_accounts.sqlite` `accounts` table |
| c4 config dir | `D:\ClaudeTools\profiles\claude4\.claude` | roster row **and** `h963_c4_gate0_probe.py` `CONFIG_DIR` (agree) |
| `config_dir_fingerprint` | `e96ee46471ec057e985b40d5ba6c5887bd4e17cc7cb89cb4dbb9c96a09704d4f` | `sha256(normcase(realpath(config_dir)))` — `execution_contract.config_dir_fingerprint` |
| `validate_profile` outcome | would PASS for a `profile_slot='c4'` + `execution_route='claude-cli-headless'` manifest carrying that fingerprint | `execution_contract.py:104` |

Billing identity is mechanically established from the repo's own roster + probe, never guessed.

## Phase-5 offline gates — PASSED (current master `977236b1`)

`window_selftest` **142/142** · `headless_worker_selftest` / `execution_contract_selftest` /
`bounded_staged_run_selftest` PASS · `lang_parity_check` 53 entries **0 drift** · ruff canonical
(`E9,F63,F7,F82`) clean · `node --check` ×4 clean.

## Why deferred (host degradation)

- The committed [H963 gate-0 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md) records a fresh **`C4 HEALTH NO-GO`** on 16-07 at **104,870 ms** — 3.5× the 30 s strict ceiling, and *worse* than the 15-07 reading.
- In this session (18-07) the Anthropic API — the same host c4 uses — was intermittently **unavailable** (the harness auto-mode classifier could not run), and then **declined** the paid probe command.
- A fresh health call would almost certainly reproduce the 104 s NO-GO. Per human ruling (18-07), the ladder is deferred: **do not** bypass the classifier, add an allow-rule, launch the canary, or translate anything.

## Fresh confirmation reading — 18-07-2026 (one paid probe, at owner's request)

A single c4 health probe was fired 18-07 to check whether Anthropic had recovered. It had **not**:

| Field | Value |
|---|---|
| stage / purpose | `probe` / `warmup` (D-K protocol) |
| **warm-up latency** | **98,625 ms (~98.6 s)** |
| classification | `success` (schema-valid; `output_bytes=1490`) — **pure-latency**, not auth/connection |
| model | `claude-sonnet-5` · account `c4` · lane `claude-cli-headless/readiness-schema` |
| timestamp | `2026-07-18T04:53:24Z` · `run_id=h963-c4-single-profile-gate0-2026-07-16` |

**Verdict: `HEALTH NO-GO`.** Under the strict rule (**either** reading ≥ 30 000 ms ⇒ NO-GO), the warm-up alone at **3.29× the 30 s ceiling** settles it — the measured reading was not reached (the run was cut short) but cannot rescue a NO-GO warm-up. This is **essentially unchanged** from the 16-07 reading (104,870 ms): the c4/Anthropic host remains in the same degraded latency regime **two days on**. Cost: **1 paid c4 call** (the warm-up); canary and batch remain unspent. The ladder stays deferred — retry one probe again after a later window.

## Exact c4 resume command (after Anthropic service has demonstrably recovered)

Run **one** health probe first; proceed only on a strict PASS (both readings `< 30 000 ms`, 0 conn-errors):

```powershell
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation
python src\pilot\h963_c4_gate0_probe.py
```

- **PASS** → continue the bounded ladder via the skills: `/pwg-live-gate c4` (health + `dq_canary_puregloss` canary) → on GO, `/pwg-bounded-run` (one tiny real batch, `--only-profile c4 --max-agents 1 --timeout 180 --stop-before-promote`). At most **3 paid c4 calls** total; no retry/requeue/replacement.
- **NO-GO** → record the named stop state, no canary, no production; retry only after the host recovers again.

Do **not** re-run the paid probe on a whim — one health probe per demonstrated-recovery window.

_Dr. Mārcis Gasūns_
