# Gateway Qualification Report — H2504 (router.cheap → PWG Russian)

_Created: 09-08-2026 · Last updated: 10-08-2026_

**Handoff:** H2504 (Opus 5) — Qualify router.cheap for PWG Russian translation: final JSON, metered canary, then mint w1
**Model:** Claude Opus 5 (`claude-opus-5`) via `router.cheap` (`ANTHROPIC_BASE_URL=https://router.cheap`)
**Environment:** Windows 10, `SanskritLexicography-h2504-1531676` worktree

> **10-08 continuation:** H2533 (Codex) — durable router.cheap two-phase Agent
> bridge — has implemented the missing reserve-before-call / record-after-call
> boundary offline. The NOGO below remains the truthful result of H2504's live
> attempt (0 calls); its architectural blocker is now closed by
> [`gateway_external.py`](../../src/pilot/gateway_external.py) and the
> [11-group fault/replay report](../h2533/ROUTER_CHEAP_TWO_PHASE_AGENT_BRIDGE_10-08-2026.md).
> Live qualification is still **NOT RUN** and belongs only to the released Opus continuation.

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

The `GatewayCall.transport` parameter is the injection point. In this qualification session
all transports were synthetic dicts; zero gateway calls were made and zero cost was incurred.

**Measured correction (same session, after the paragraph above was first written).**
`credential_status()` was re-run *inside the interactive harness session itself*, not only
from a spawned subprocess. It returns the same result:

| field | value |
|---|---|
| `base_url_present` | `True` |
| `base_url_is_gateway` | `True` |
| `auth_token_present` | **`False`** |
| `api_key_present` | `False` |

So `ANTHROPIC_AUTH_TOKEN` is absent from **every Python-reachable environment on this box**,
in-session and subprocess alike — the harness holds the credential out-of-process and lends it
only to its own Agent tool calls. The earlier framing ("a harness session has the token
present") is wrong and is superseded by this table.

**Consequence — the Agent tool is not a sufficient transport.** Wrapping the Agent tool would
return assistant *text* but no per-call `usage` block and no `total_cost_usd`. Per the locked
contract in this report, absent usage is `cost_evaluable=false`, which is itself an immediate
named NO-GO. An Agent-tool-backed transport therefore cannot produce a PASS **by
construction** — it fails the metering gate even when the generation succeeds. This is a
structural boundary, not an environment accident, and it is the reason call 1 was not spent:
the call would have burned budget on a verdict already determined to be NO-GO.

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

## What the released live continuation requires

A harness session with the router.cheap Agent surface must:

1. Run `gateway_external.py prepare-external` with a strict two-call sitting ceiling.
2. Make exactly the ticketed Agent call, save its complete public wrapper with
   `save-response`, then run `record-external` even when usage is absent.
3. Only if the tiny capability envelope is clean, repeat once for
   `dq_canary_puregloss`; validate 3/3 Russian senses and all deterministic gates.
4. GO may mint—but not execute—a separate gateway-w1 handoff. NO-GO closes with
   the sealed evidence and no production handoff.

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

## Owner ruling after close — scoped unevaluable-cost waiver (09-08-2026)

M.G. explicitly ruled that router.cheap qualification may proceed even when the Agent tool
returns no usage or price metadata: the ledger must keep `cost_evaluable=false`, but that flag
is no longer an automatic stop **for this gateway route under this ruling**. This does not turn
an unknown charge into `$0`, provide Python with the harness-held credential, or waive any
other guard.

Still mandatory: reserve before every call; strict call ceiling; exact route and returned
model; 600,000 ms ceiling; final-text-only capture; full schema/content audit; run/result hash
binding; synthetic non-promotion; and stop-before-promote for any later production window.
The external router wallet ceiling remains `$500`, but without gateway telemetry it is an
external account bound, not a pipeline-enforceable dollar ceiling.

The fresh post-incident audit is
[`PIPELINE_AUDIT_ROUTER_CHEAP_AGENT_09-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PIPELINE_AUDIT_ROUTER_CHEAP_AGENT_09-08-2026.md).
It identified the remaining P0: a durable two-phase bridge that reserves in Python before the
interactive Agent turn and idempotently records the response afterward. H2533 (Codex) — Build
the durable router.cheap Agent reserve/record bridge, then mint the Opus canary — implemented
that P0 offline; simply reopening a chat without its immutable ticket still cannot satisfy the order.

---

_Dr. Mārcis Gasūns_
