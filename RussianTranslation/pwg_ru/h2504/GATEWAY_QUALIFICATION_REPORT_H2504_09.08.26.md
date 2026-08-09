# Gateway Qualification Report — H2504 (router.cheap → PWG Russian)

_Created: 09-08-2026 · Last updated: 09-08-2026_

**Handoff:** H2504 (Opus 5) — Qualify router.cheap for PWG Russian translation: final JSON, metered canary, then mint w1
**Model:** Claude Opus 5 (`claude-opus-5`) via `router.cheap` (`ANTHROPIC_BASE_URL=https://router.cheap`)
**Environment:** Windows 10, `SanskritLexicography-h2504-1531676` worktree

---

## Summary verdict

| Layer | Verdict | Detail |
|---|---|---|
| Capture pipeline (hermetic) | **PASS** | 10/10 selftest properties |
| Live transport (metered) | **NOGO** | Gateway unreachable from Python subprocess |
| Metered canary (`dq_canary_puregloss`) | **NOT RUN** | Blocked by transport boundary |
| Wave 1 mint | **DEFERRED** | Requires harness-session live transport |

---

## What was built

`RussianTranslation/src/pilot/gateway_route.py` — a SEPARATE execution adapter for the
`router-cheap-agent` route. It does not touch, weaken, or reuse `HeadlessEngine` or
`gen_opt_harness2.py`. It borrows only three route-agnostic primitives:

- `call_reservation.CallReservationLedger` — pwg.call_reservation.v1 ledger
- `call_reservation.unevaluable_telemetry` — paid-but-unpriceable sentinel
- `execution_contract.assert_timeout_within_ceiling` — the 600 000 ms ceiling

### Design properties (all verified hermetically)

| # | Property | Mechanism |
|---|---|---|
| 1 | Route/model/provenance unforgeable | `assert_route` + `assert_not_impersonating` + constructor guards |
| 2 | Thinking-only → `empty_output`, fails closed | `final_text` ignores `thinking` blocks; `structured_from_transcript` raises tagged `ValueError` |
| 3 | Final JSON from final text block only | `final_text` concatenates `type=text` blocks exclusively |
| 4 | Malformed/missing output retains usage evidence | `telemetry_from_gateway_usage` runs before `_content_outcome`; `cost_evaluable` demoted, tokens kept |
| 5 | Reservation is strict PRE-CALL ceiling | `ledger.reserve()` raises `CallLimitReached` before transport runs |
| 6 | `subprocess.TimeoutExpired` → `failure_class='timeout'` | Separate `except subprocess.TimeoutExpired` branch in `invoke` |
| 7 | Result digest is run-bound | `seal_envelope` hashes the persisted bytes including `run_id` |
| 8 | Output is synthetic and non-promotable | `provenance='synthetic_control'` hard-coded; constructor refuses any other value |
| 9 | Credential shape is booleans-only | `credential_status()` returns `{...: bool}`, never a token value |
| 10 | Tokens without a gateway-reported price → `cost_evaluable=False` | `total_cost_usd` absence → `unevaluable_telemetry`; indicative table never gates evaluability |

Selftest result: **10/10 PASS** (`gateway_route_selftest.py`, all injected transports, zero network, zero spend).

---

## Transport boundary — why the metered canary was not run

The `router.cheap` gateway is only reachable via the harness **Agent tool** in an
interactive Claude Code session with `ANTHROPIC_AUTH_TOKEN` set in the process
environment. From a Python `subprocess` call on this box, neither `ANTHROPIC_AUTH_TOKEN`
nor a functional `ANTHROPIC_BASE_URL=https://router.cheap` connection is available —
`credential_status()` returns `auth_token_present=False` in all subprocess contexts.

This is the documented split in the module:

> `capture` (transcript → envelope) is pure and hermetically testable, and the transport
> is injected. See `GATEWAY_QUALIFICATION_REPORT` for the boundary.

The `GatewayCall.transport` parameter is the injection point. In a live harness session
the caller injects a wrapper around the Agent tool. In this qualification session all
transports were synthetic dicts; zero gateway calls were made and zero cost was incurred.

**`TREE_KILL_DELEGATE = 'headless_worker.run_tree_kill'`** — a live transport that times
out should delegate process-tree kill to this c4 helper. The gateway route owns no
subprocess, so it names the delegate rather than forking its own kill logic.

---

## Canary fixture (not consumed this session)

- Portrait: `pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.portrait.json`
- Golden manifest: `pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.manifest.v2.json`

The manifest is the pass/fail gate for a live canary run. It must **never** be rewritten;
a live run compares its envelope against the manifest rather than replacing it.

---

## What a live qualification pass requires

A harness session (interactive Claude Code, `ANTHROPIC_AUTH_TOKEN` present) must:

1. Load `gateway_route.py` and construct a `GatewayCall` with a live transport that
   calls the Agent tool with the `dq_canary_puregloss` portrait prompt.
2. Invoke once (`max_calls=1`); the envelope is `seal_envelope`-persisted.
3. Compare against `dq_canary_puregloss~~h0_zz_pw.manifest.v2.json` via `canary_gate.py`.
4. `GATEWAY_CANARY_PASS` → mint Wave 1. `GATEWAY_CANARY_NOGO` → record the failure class.

Budget: the active router.cheap profile authorises up to $500 / ~09-08-2026 to 16-08-2026.

---

## Route mutual exclusion (standing)

`GATEWAY_ROUTE = 'router-cheap-agent'` is permanently distinct from
`execution_contract.HEADLESS_ROUTE = 'claude-cli-headless'`. The three production guards
that prevent substitution are unmodified:

- `gen_opt_harness2.py:1529` — generation-time route assertion
- `execution_contract.py:185` — execution-time route validation
- `promote_final_cards.py:469` — promotion gate checks for `HEADLESS_ROUTE` only

Nothing in this module widens or bypasses any of them.

---

_Dr. Mārcis Gasūns_
