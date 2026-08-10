# router.cheap two-phase Agent bridge — offline delivery evidence

_Created: 10-08-2026 · Last updated: 10-08-2026_

**Handoff:** H2533 (Codex) — Build the durable router.cheap Agent reserve/record bridge,
then mint the Opus canary. **Executor:** Codex Sol (`gpt-5.6-sol`).

## Verdict

**PASS for offline bridge construction; no live call was made.** The interactive boundary is
now a durable four-command protocol:

1. `prepare-external` reserves one `pwg.call_reservation.v1` slot and publishes an immutable
   `pwg.gateway_external_ticket.v1` before any Agent turn;
2. the harness performs exactly the ticketed Agent call;
3. `save-response` validates and atomically publishes the complete public response wrapper;
4. `record-external` validates every binding, complete JSON Schema and timing evidence,
   finalizes the exact reservation, and seals `pwg.gateway_external_envelope.v1`.

`recovery-report` is read-only and distinguishes `reserved_without_ticket`,
`pending_with_ticket`, and `finalized`. A crash never refunds or silently reuses a call.

## Public surfaces

- Implementation: [`gateway_external.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_external.py)
- Fault/replay suite: [`gateway_external_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_external_selftest.py)
- Shared primitives: [`gateway_route.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_route.py) and [`call_reservation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py)
- Protocol schemas:
  - [`pwg_gateway_external_ticket.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_gateway_external_ticket.schema.json)
  - [`pwg_gateway_external_response.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_gateway_external_response.schema.json)
  - [`pwg_gateway_external_envelope.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_gateway_external_envelope.schema.json)
- Offline CI gate: [`ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)

CLI discovery:

```powershell
python src/pilot/gateway_external.py --help
python src/pilot/gateway_external.py prepare-external --help
python src/pilot/gateway_external.py save-response --help
python src/pilot/gateway_external.py record-external --help
python src/pilot/gateway_external.py recovery-report --help
```

The CLI has no transport command and reads no environment credential. It cannot invoke the
Agent tool, HTTPS, c4, Max, a Workflow fallback, the coordinator, store, TM, denylist or
promotion.

## Durable state machine

| State / fault | Durable truth | Resume result |
|---|---|---|
| `max_calls=0` or exhausted | no reservation, no ticket | refusal before authorization |
| death after reservation | spent pending reservation; no ticket | report names `reserved_without_ticket`; same prepare key recovers ordinal 1 |
| death during ticket temp write | spent pending reservation; destination absent | orphan temp is reportable; retry replaces once, no second spend |
| death after ticket replacement / before Agent | immutable ticket + pending reservation | retry returns the same ticket bytes |
| death during response write | ticket remains pending; partial scratch JSON is rejected | `save-response` republishes atomically, then record continues |
| death before finalization | complete wrapper + pending reservation | record retries the same response |
| death after finalization, before envelope replacement | response hashes are already sealed in ledger `finalization_evidence` | record reconstructs the identical envelope without double-folding usage |
| death during/after envelope replacement | finalized reservation + response-bound evidence | byte-identical no-op |
| divergent replay | finalized fingerprint differs | refusal; original usage/evidence unchanged |

Idempotent prepare is implemented inside the ledger's existing cross-process lock. The optional
`idempotency_key` is bound to run, ceiling, route, model, purpose, provenance, timeout, waiver,
request hash and schema hash. Optional `finalization_evidence` binds the public-response,
ticket and semantic-envelope hashes in the same atomic ledger update as telemetry. Legacy
callers omit both fields and retain their prior bytes and behavior.

## Validation and accounting

- Ticket validation recomputes the ticket, operation, embedded request and embedded schema
  hashes before the response file is opened.
- Response binding is exact for run, reservation, route, requested/returned model, purpose and
  nonce. Any substitution refuses while leaving the reservation pending.
- Final JSON is assembled only from `type=text` blocks. Thinking-only and malformed output are
  named failures; thinking content is absent from the result envelope.
- `jsonschema.Draft202012Validator` validates nested types, required fields, cardinalities,
  constants and additional properties. The in-process `GatewayCall` now consumes the same
  helper, replacing its old top-level-required-only check.
- Start, end and wall evidence are mandatory. The timestamp interval must equal `wall_ms`
  within 1 ms, and `wall_ms > 600000` is `timeout`.
- Missing usage is accepted only for route `router-cheap-agent` with waiver
  `router-cheap-agent-owner-waiver-2026-08-09.v1`. The envelope records
  `cost_evaluable=false`, `observed_cost_usd=null`; the ledger independently retains its
  numeric observed-cost floor (`0` when nothing was reported). The same missing usage on c4,
  headless, or without the exact waiver refuses.
- Every envelope is `provenance_class=synthetic_control`, `promotable=false`; the existing
  promotion contract remains headless-only.

## RED → GREEN fault matrix

The acceptance file was committed first and failed at the deliberately absent module. The
implementation then made all **11/11 test groups PASS**:

| Group | Coverage |
|---|---|
| prepare contract | route/provenance/waiver/timeout/model/purpose; `max_calls=0/1/N` |
| competing prepares | same-operation idempotence and different-operation ceiling race |
| prepare faults | post-reserve, ticket-temp and post-replace recovery + read-only report |
| success/accounting | all hashes, unknown-cost separation, hidden-thinking exclusion |
| protocol schemas | real ticket, response and envelope validate against committed schemas |
| record faults | pre/post-finalize and envelope-temp/post-replace convergence |
| substitution | wrong run/reservation/route/requested/returned model/purpose/nonce/schema |
| incomplete/replay/timing | missing/partial/divergent response and missing/malformed/over-ceiling time |
| response durability | temp-write/post-replace fault convergence and byte identity |
| complete JSON Schema | thinking-only, malformed JSON, nested type/cardinality/const/additional-property failures |
| waiver/non-promotion | exact router-only waiver and permanent synthetic refusal |

Pinned semantic fixture signatures:

| Object | SHA-256 |
|---|---|
| request | `a1f3152184a29d5042817e1c92e96e7c7ef483c593178f972f91fab21c5fe806` |
| complete output schema | `d695c9f4df763e9592c22d2b990c21dfdeeabfdf3c0695eee8e9ba711d07f9d0` |
| canonical valid result | `d0c45566293f713f3e248bb5626518edd6e60c3ee29e781ddf9451c5e4e3021d` |

Each transaction additionally seals exact ticket, request, schema, public-response, final-text,
canonical-result and semantic saved-envelope hashes. Replay tests require the persisted ticket,
response and envelope bytes to remain identical.

## Regression evidence

| Check | Result |
|---|---|
| `gateway_external_selftest.py` | 11/11 groups PASS |
| `gateway_route_selftest.py` | 10/10 PASS |
| `call_reservation_selftest.py` | PASS (`0/1/N`, race/resume, finalization, cost, durations) |
| `window_selftest.py` | 210/210 PASS |
| `headless_worker_selftest.py` | PASS |
| `canary_manifest_build_selftest.py` | PASS |
| `coordinator_hardening_selftest.py` | PASS |
| `promotion_journal_selftest.py` | 3/3 PASS |
| `promotion_receipt_selftest.py` | 6/6 PASS |

The handoff named four pre-existing 09-08 master-gate failures separately. On the mandated
fresh base (`v1.144.26`, after PR #1619) none reproduce: the returned-model acceptance defect,
missing gateway CI invocation, host-dependent H1339 benchmark signature, and parity/window
ledger drift were prerequisite repairs, not bridge changes. This branch does not rebaseline or
disguise them; its full regression run starts from their released green state.

## Remaining boundary

The bridge proves safe preparation and recording but deliberately does not qualify live
router.cheap output. After merge and patch release, one Opus 5 continuation may spend at most
two reservations: a tiny final-envelope capability turn, then—only on clean PASS—the existing
[`dq_canary_puregloss`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.portrait.json)
three-sense synthetic canary. A NO-GO records durable evidence and mints
no production handoff. A GO may mint, but not execute, a separate gateway-w1 handoff.

_Dr. Mārcis Gasūns_
