# Pipeline audit — router.cheap Agent route (09-08-2026)

_Created: 09-08-2026 · Last updated: 10-08-2026_

Changelog: not applicable — this post-release edit only replaces forward-looking delivery
language with the actual PR, release and successor handoff; no runtime contract changed.

**Mode:** post-incident audit after H2504 (Opus 5) — qualify `router.cheap` for PWG
Russian translation—proved that the interactive Agent tool is outside every Python-reachable
credential and usage surface. M.G.'s subsequent ruling permits this route to run with
`cost_evaluable=false`; it does not permit fabricated `$0`, unreserved calls, model
substitution, promotion, or reuse of c4 provenance.

Primary implementation:
[`gateway_route.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_route.py)
· tests:
[`gateway_route_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_route_selftest.py)
· incident report:
[`GATEWAY_QUALIFICATION_REPORT_H2504_09.08.26.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2504/GATEWAY_QUALIFICATION_REPORT_H2504_09.08.26.md).

## 10-08 implementation closure

H2533 (Codex) — durable router.cheap two-phase Agent bridge — closes build specs 1–4
offline. [`gateway_external.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_external.py) now supplies
`prepare-external`, `save-response`, `record-external`, and a read-only
`recovery-report`; three committed protocol schemas and an 11-group fault/replay suite
pin the contract. `GatewayCall.invoke()` remains for injected in-process tests and now
shares full Draft 2020-12 validation with the external recorder. No live call was made.
Full evidence: [`ROUTER_CHEAP_TWO_PHASE_AGENT_BRIDGE_10-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2533/ROUTER_CHEAP_TWO_PHASE_AGENT_BRIDGE_10-08-2026.md).
[PR #1623](https://github.com/gasyoun/SanskritLexicography/pull/1623) merged green and
[v1.144.27](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.27) is
published. The bounded live successor is H2534 (Opus 5) — Run the released router.cheap
two-ticket live canary and mint gateway-w1 only on GO.

The tables below preserve the 09-08 diagnosis as history. Their “open” labels are
superseded by this closure section; only the harness-owned live canary remains.

## Real call graph

| Stage | Code edge | Reads | Writes / side effects | Current capability |
|---|---|---|---|---|
| Construct | `GatewayCall.__init__` (`gateway_route.py:284–305`) | explicit route, requested model, timeout, synthetic provenance | none | Refuses c4/headless identity, non-synthetic provenance, invalid timeout, and a non-ledger caller. |
| Reserve | `GatewayCall.invoke → CallReservationLedger.reserve` (`gateway_route.py:348–353`; `call_reservation.py:314–346`) | run ID, strict `max_calls`, purpose/profile | atomically increments durable calls spent and creates a pending reservation | Correct pre-call ceiling for an in-process transport. |
| Transport | `GatewayCall.invoke → self.transport(request)` (`gateway_route.py:354–367`) | Python callable | paid external call, if a callable exists | Hermetic injection works; the interactive Agent tool is not callable here. |
| Account | `telemetry_from_gateway_usage` (`gateway_route.py:179–204`) | transcript usage | telemetry folded into reservation | Missing price remains truthfully unevaluable. Owner waiver now permits continuation with that flag; it does not change the value. |
| Validate | `_content_outcome` (`gateway_route.py:308–338`) | returned model, final text, shallow schema requirements | in-memory verdict | Final text excludes thinking; exact returned-model enforcement added by this audit. Full JSON Schema validation is still absent. |
| Finalize | `CallReservationLedger.finalize` (`call_reservation.py:348–390`) | reservation ID + normalized telemetry | idempotent ledger finalization | Correct when reserve/call/capture occur in one Python stack. |
| Seal | `seal_envelope` (`gateway_route.py:426–431`) | complete envelope | atomic JSON + SHA-256 | Hash binds saved bytes, run ID, reservation, route/model and result. |
| Downstream | no gateway production consumer | synthetic envelope | none | Deliberately non-promotable; no w1 execution path exists yet. |

The declared route and the real route agree **only inside injected tests**. There is currently
no code edge from the Agent tool to `GatewayCall.invoke`; a manual response pasted after the
fact would skip the pre-call reservation, while reserving and then leaving Python to call the
Agent tool cannot return into the same stack. That boundary is the controlling gap.

## Money and side-effect gates

| Gate / side effect | Enforced? | Recovery / evidence |
|---|---|---|
| strict call count | yes for `invoke`; not yet for an external Agent turn | durable reservation file; missing two-phase bridge is P0 |
| cost ceiling | impossible on this route without usage/price | owner explicitly waived evaluability; record a cost floor/unknown, never `$0` |
| 600,000 ms wall ceiling | yes for an in-process transport | an external bridge must persist reserve/start/finish timestamps |
| process-tree kill | no process is owned by this adapter | `TREE_KILL_DELEGATE` is documentation, not an invoked kill edge |
| result/store write | envelope only | atomic temp + fsync + replace; synthetic provenance and `promotable=false` |
| store, denylist, coordinator, TM | no code edge | zero mutation; promotion route remains headless-only |

## Silent-failure census

| Rank | Location | Class | What is lost | Status |
|---|---|---|---|---|
| P0 | `gateway_route.py:308–338,392–394` | declared-versus-enforced model provenance | A substituted returned model was recorded as `model_matches_request=false` but still accepted as `schema_compliant=true`, producing a result hash that could pass a shallow canary consumer. | **Fixed here:** exact mismatch now returns `failure_class=provenance`, no result, no result hash; RED→GREEN regression added. |
| P0 | `gateway_route.py:348–386` | execution boundary / irreversible spend | `reserve`, Agent call, capture and `finalize` exist only as one in-process operation, but the live Agent tool is out-of-process from Python. There is no safe command sequence that reserves first and records later. | Open build spec 1. |
| P1 | `gateway_route.py:329–336` | schema overclaim | `schema_compliant=true` checks only top-level required-key presence; types, nested required fields, cardinality and additional properties are unchecked. | Open build spec 2. |
| P1 | `gateway_route.py:354–369` | timeout / liveness evidence | `wall_ms` measures only a Python callable. An externally performed Agent turn has no durable start/finish pair or enforceable 600 s kill. | Open build spec 1. |
| P1 | `gateway_route.py:79–82` | inert safety declaration | `TREE_KILL_DELEGATE` is a string constant and no call site invokes it. | Open; external Agent turns require a harness-owned cancellation contract, not the c4 subprocess helper. |
| P1 | qualification policy | waiver ambiguity | `cost_evaluable=false` previously meant immediate NO-GO. Without a versioned waiver field, future reviewers cannot distinguish authorized router.cheap evidence from an accidental missing envelope. | Open build spec 1. |
| P2 | `gateway_route.py:359–367` | overbroad exception capture | `BaseException` converts `KeyboardInterrupt`/`SystemExit` into transport failure. It protects reservation finalization, but may make operator cancellation look like an ordinary route defect. | Preserve for now; the two-phase bridge should classify operator cancellation explicitly. |

## Ranked build specs

1. **P0 — durable two-phase external-call bridge.** Add `prepare-external` and
   `record-external` commands around `GatewayCall`: prepare must reserve and fsync an immutable
   request ticket before the Agent turn; record must require that ticket's run ID, reservation
   ID, requested model, route, request hash and timestamps, ingest final response blocks only,
   finalize idempotently, and seal the envelope. A pending ticket survives process death and
   cannot be reused for a second call. Pin `max_calls=0/1/N`, duplicate record, wrong run/model,
   stale/substituted ticket, missing final text, missing usage under the owner waiver, and crash
   between every phase.
2. **P1 — real JSON Schema validation.** Compile the supplied schema with the repo's installed
   `jsonschema` validator and reject every validation error; do not label a required-key subset
   `schema_compliant`. Pin nested/type/additional-property/cardinality negatives using the real
   `dq_canary_puregloss` schema.
3. **P1 — waiver provenance.** Seal `cost_policy=owner_waiver_router_cheap_2026-08-09`,
   `cost_evaluable=false`, `observed_cost_usd=null` (not zero), external wallet cap `$500`, and
   the strict call ceiling into every ticket/envelope. The waiver is route- and date-scoped and
   must never be accepted by c4/Max or promotion.
4. **P1 — external liveness/cancellation receipt.** Record harness-visible start/end/cancel
   evidence and classify timeout separately from operator cancellation. Do not claim process
   tree kill for a tool call Python does not own.
5. **P2 — only after synthetic GO:** build a separate, non-synthetic gateway-w1 route that
   re-prepares keys on released code and stops at hash-bound `AWAITING_REVIEW`. The current
   adapter correctly refuses real provenance and must stay that way.

## Capability verdict (updated 10-08)

The capture core refuses exact-model substitution, and the released-next bridge now supplies
the legal money sequence: durable reservation before the call and idempotent evidence capture
after it. Missing usage remains unknown, not zero, under the exact versioned waiver. The only
remaining qualification work is the bounded Opus live continuation: one tiny capability turn,
then at most one synthetic canary. No production translation or promotion is authorized by
this audit or by the bridge.

## Not audited

This focused post-incident pass did not re-audit the c4 headless generator, coordinator,
promotion journal, canonical store, denylist, TM builders, or unrelated model routes. It made
no network/model call and touched no production data.

_Dr. Mārcis Gasūns_
