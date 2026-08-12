_Created: 12-08-2026 · Last updated: 12-08-2026_

# router.cheap v1.144.32 two-call requalification — zero-call stop (route not bound)

Handoff: **H2581 (Opus 5) — Run the two-call router.cheap requalification on v1.144.32 with
exact dispatch attestation**
([handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2581-Opus_RussianTranslation_router-cheap-v1.144.32-two-call-requalification_11.08.26.md)).

Executed by **Opus 5** (`claude-opus-5`) at released version **v1.144.32** (commit
[`d5c8845b3060f9d2596b831ccbbb8cdda2293838`](https://github.com/gasyoun/SanskritLexicography/commit/d5c8845b3060f9d2596b831ccbbb8cdda2293838)),
worktree `SanskritLexicography-h2581-48350`, branch `h2581-router-cheap-requalification`.

## Decision

> ## ⛔ ZERO-CALL STOP — the authorised spend is NOT consumed
>
> **0 reservations · 0 dispatches · 0 tickets · 0 envelopes.** The four named offline
> selftests all pass, but this session is **not bound to the gateway under qualification**:
> `ANTHROPIC_BASE_URL` is absent, so `base_url_is_gateway = false`. An `Agent` dispatch made
> here would be served by the default endpoint, not by `https://router.cheap` — and every
> artifact would still be stamped `route: router-cheap-agent` under the router.cheap owner
> waiver. That is a **false provenance claim**, an explicit Fail in this handoff.
>
> **No `gateway-w1` production handoff is minted.** M.G.'s two-call authorisation of
> 12-08-2026 remains **unspent and valid** — it is preserved, not burned.

This is a **pre-spend stop, not a NO-GO verdict on the route.** Nothing here says router.cheap
would fail requalification; it says this sitting could not have tested router.cheap at all. The
distinction matters, because a NO-GO would close the question while spending the authorisation
on evidence about the wrong endpoint.

## Authorisation of record

M.G., 12-08-2026, in session, after reading the handoff:

> Authorising exactly two router.cheap reservations/dispatches for H2581 on v1.144.32

Fresh, explicit, post-dating the 11-08-2026 handoff, and naming the exact count — the entry
gate was **satisfied**. The stop below happened after it, on a different gate.

## Gate 1 — the four offline selftests: PASS

Run at the released commit before any reservation, exactly as the handoff enumerates.

| Selftest | Required | Result |
|---|---|---|
| [`gateway_canary_contract_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/v1.144.32/RussianTranslation/src/pilot/gateway_canary_contract_selftest.py) | 3/3 groups | **PASS (3/3)** |
| [`gateway_attestation_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/v1.144.32/RussianTranslation/src/pilot/gateway_attestation_selftest.py) | 9/9 groups | **PASS (9/9)** |
| [`gateway_external_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/v1.144.32/RussianTranslation/src/pilot/gateway_external_selftest.py) | 11/11 groups | **PASS (11/11)** |
| [`gateway_route_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/v1.144.32/RussianTranslation/src/pilot/gateway_route_selftest.py) | 10/10 groups | **PASS (10/10)** |

The H2554 contract repair holds: the prompt/schema contradiction that caused the H2539 NO-GO
is fixed and regression-pinned. Had the route been bound, this sitting would have proceeded.

## Gate 2 — route binding: FAIL, and it is the decisive one

`router-cheap-agent` is not a harness subagent type. It is the harness `Agent` tool **in a
session whose process environment points at the gateway** — the boundary
[H2504 documented](https://github.com/gasyoun/SanskritLexicography/blob/v1.144.32/RussianTranslation/pwg_ru/h2504/GATEWAY_QUALIFICATION_REPORT_H2504_09.08.26.md)
and measured. (H2539 confirmed the negative half independently: an `Agent` call passing
`agentType: 'router-cheap-agent'` is rejected as *"Agent type not found"* — that string is the
ticket's route label, not a dispatch target.)

Measured this session, credential shape booleans-only, no token value read:

| Field | H2504 (bound session) | **This session** |
|---|---|---|
| `base_url_present` | `true` | **`false`** |
| `base_url_is_gateway` | `true` | **`false`** |
| `auth_token_present` | `false` | `false` |
| `api_key_present` | `false` | `false` |
| `ANTHROPIC_*` env names present | `ANTHROPIC_BASE_URL` | **none — `[]`** |

`auth_token_present: false` is **not** the finding: H2504 established that the harness holds
the credential out-of-process and lends it only to its own tool calls, so `false` there is
normal in a correctly-bound session. The finding is `base_url_present: false`. H2504 measured
the base URL as visible **in-session and in subprocess alike**; only the token was hidden. So
its absence from a subprocess here is evidence of real absence, not of env stripping — that
discriminator is exactly what H2504 pinned down.

Machine-readable capture:
[evidence/prespend_gate.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2581/evidence/prespend_gate.json)
(`gate_verdict: ZERO_CALL_STOP`), produced by
[prespend_gate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2581/prespend_gate.py),
which reserves nothing and dispatches nothing.

## Why spending anyway would have been the wrong call

Four reasons, in order of weight:

1. **It would manufacture false provenance.** The ticket, attestation, and envelope all pin
   `route: router-cheap-agent` and `waiver_id: router-cheap-agent-owner-waiver-2026-08-09.v1`.
   Sealed around a dispatch that never touched router.cheap, that is a hash-bound artifact
   asserting something untrue — worse than no artifact, because the next session would read
   the seals as proof.
2. **The attestation would have passed while proving the wrong thing.** `resolvedModel` would
   read `claude-opus-5` and `model_matches_request` would be `true` — a green attestation of
   the *default* endpoint. The v2 exact-dispatch binding proves *which dispatch*; it does not
   prove *which gateway*. That residual is stated here rather than discovered later.
3. **It would burn a scarce, explicitly-counted authorisation** on a question it cannot
   answer. The authorisation is for two calls to router.cheap, not two calls to anywhere.
4. **The handoff forbids the recovery.** No retry, no reroll, no replacement reservation, no
   third call. A wasted pair could not be re-run under this handoff.

This is the same reasoning H2504 used when it declined to spend call 1 into a
verdict already determined — reused deliberately, not re-derived.

## What is required to actually run this

An **Opus 5** session launched with the process environment bound to the gateway:

```
ANTHROPIC_BASE_URL=https://router.cheap
```

plus the harness-held gateway credential (never read, printed, or persisted by any script
here). Verify **before** claiming, from inside that session:

```
python RussianTranslation/pwg_ru/h2581/prespend_gate.py
```

Exit **0** = `PROCEED` (bound + selftests green). Exit **3** = `ZERO_CALL_STOP`. That check is
now the mechanical form of this stop, so no future sitting has to rediscover it by reasoning —
which is the one durable improvement this pass produced.

The two-call authorisation carries forward to that session unchanged; it was not consumed.

## Ledger state — proof of zero spend

No reservation ledger was created for `H2581`. There is no `h2581` run id, no ticket, no
response wrapper, no attestation, and no envelope. `calls_spent` is not merely `0` — the
ledger does not exist, because `prepare-external` was never invoked.

## Residual, stated rather than implied

Being bound to `https://router.cheap` is itself observed from the client's own environment.
Attestation narrows the trust boundary from "the operator asserted it" to "the harness
observed the endpoint assert it"; it never becomes cryptographic proof of physical model
identity, and no report from this lane may describe it as such. The v2 exact-dispatch binding
closes the H2539 *window* residual (`--include-main-turns`), not this one.

_Dr. Mārcis Gasūns_
