# router.cheap canary contract + exact-dispatch attestation repair

_Created: 10-08-2026_

Handoff: **H2554 (Codex) — Repair the router.cheap canary prompt/schema contract and bind attestation to one Agent dispatch**.

## Verdict

**OFFLINE REPAIR PASS. Zero live calls, reservations, gateway probes, or translations were made.**
H2539 remains sealed **NO-GO** and its v1 attestations remain explicitly
`legacy_window` / `dispatch_attested=false` / non-promotable.

## Prompt/schema RED → GREEN

[`gateway_canary_contract.py`](../../src/pilot/gateway_canary_contract.py) owns one typed v2
fixture and generates both the operator prompt and complete Draft 2020-12 schema. The response
`german` field deliberately keeps the least-lossy full skeleton line, including `— N〉 `.

The regression first parses H2539's committed prompt. Its prompt-derived instance contains
`— 1〉 {%eine Schildkröte%}.` and the frozen H2539 schema rejects it because that schema pins
`{%eine Schildkröte%}.`. The same prompt-derived construction validates against the generated
v2 schema. Mutations of sense number, markup span, ordering, key, provenance hash, and
cardinality all reject.

## Exact Agent dispatch binding

Protocol v2 binds an immutable ticket contract to one concrete Claude Agent `tool_use.id`:

1. The ticket seals `dispatch_binding` with tool name `Agent`, scheme
   `claude-agent-tool-use.v1`, and SHA-256 of the exact request prompt.
2. The public wrapper declares the actual `dispatch_id`.
3. The attestor requires exactly one matching Agent `tool_use` and exactly one matching
   `tool_result.tool_use_id`; it verifies the tool-use prompt hash and the result event's
   `sourceToolAssistantUUID`.
4. Only `toolUseResult.status=completed` can attest. Served model, `agentId`, and usage come
   from that one result—not from adjacent main/sidechain turns or a time-window consensus.
5. The v2 attestation and envelope seal ticket hash, request-prompt hash, dispatch ID, model,
   usage, scope, and their own canonical hashes.

This works for both main-turn and sidechain dispatch events. It refuses missing, malformed,
wrong, duplicate, cross-ticket/replayed, incomplete, error/refused, source-mismatched, prompt-
substituted, and malformed-transcript evidence. Unknown usage remains unknown:
`cost_evaluable=false`, `observed_cost_usd=null`.

## H2539 own-data replay

[`h2539_dispatch_replay.py`](h2539_dispatch_replay.py) structurally replayed the two successful
H2539 tool-use/result pairs without printing prompts or results. Both resolve uniquely to
`status=completed`, `resolvedModel=claude-opus-5`, and different immutable dispatch IDs; both
were recorded as main turns. The old operator prompts contained the ticket prompt but were not
byte-identical to it, so the replay records `contained_not_exact` and **does not upgrade** the
old v1 evidence. Machine-readable hashes and IDs are in
[`h2539_dispatch_replay.json`](h2539_dispatch_replay.json).

## Verification

- `gateway_canary_contract_selftest.py`: 3/3 groups
- `gateway_attestation_selftest.py`: 9/9 groups
- `gateway_external_selftest.py`: 11/11 groups
- `gateway_route_selftest.py`: 10/10 groups
- `window_selftest.py`: full suite green
- headless worker, max-account orchestrator, coordinator hardening, bounded supervisor,
  bounded staged run, promotion journal, final-card promotion, translation-memory, and
  language-parity suites: green
- `python -m compileall -q src/pilot`: green
- `git diff --check`: green

The new canary and dispatch matrices are called by CI. All changes are language-agnostic
control-plane evidence and apply identically to RU/EN.

_Dr. Mārcis Gasūns_
