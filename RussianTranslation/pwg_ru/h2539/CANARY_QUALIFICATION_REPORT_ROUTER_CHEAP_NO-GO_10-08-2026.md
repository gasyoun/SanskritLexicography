_Created: 10-08-2026 · Last updated: 10-08-2026_

# router.cheap two-ticket attested canary — qualification report (NO-GO)

Handoff: **H2539 (Opus 5) — Run the attested router.cheap two-ticket live canary at v1.144.28 under authorised spend, and mint gateway-w1 only on GO**
([handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2539-Opus_SanskritLexicography_router-cheap-canary-attested-authorised_10.08.26.md)).

Executed by **Opus 5** (`claude-opus-5`) at repo version **v1.144.28** (commit `6c35ade31`),
run id `h2539-canary-1734943`, worktree `SanskritLexicography-h2539-1734943`.

## Decision

> ## ❌ NO-GO
>
> **No `gateway-w1` production handoff is minted.** Ticket 2's sealed envelope is
> `schema_compliant: false` (`failure_class: malformed_output`), and the handoff's GO
> criteria require a full schema PASS on Ticket 2. Both authorised reservations are spent,
> and the contract forbids spending a third call or manually repairing model output, so the
> sitting closes here.

The NO-GO is **not** attributable to the route, to model substitution, or to translation
quality. It was caused by a contradiction between two artifacts this session authored — see
[Root cause](#root-cause-a-harness-authored-promptschema-contradiction). That distinction is
recorded because it determines what a re-qualification would have to change; it does **not**
soften the verdict.

## Result table

| Field | Ticket 1 | Ticket 2 |
|---|---|---|
| Reservation id | `ea29cbcdc4dc466696675e1e7cc65ad4` | `ed6f34dfe8e641b2b49e70063da39cb5` |
| Reservation ordinal | 1 of 2 | 2 of 2 |
| Purpose | `canary_capability_probe_v1` | `canary_final_translation_v1` |
| Route | `router-cheap-agent` | `router-cheap-agent` |
| Requested model | `claude-opus-5` | `claude-opus-5` |
| **Attested served model** | **`claude-opus-5`** | **`claude-opus-5`** |
| **`model_matches_request`** | **`true`** | **`true`** |
| Attestation ambiguous | `false` | `false` |
| Waiver applied | `router-cheap-agent-owner-waiver-2026-08-09.v1` | same |
| Provenance class | `synthetic_control` | `synthetic_control` |
| Promotable | `false` | `false` |
| `wall_ms` (limit 600 000) | 27 549 | 125 254 |
| Timing valid | yes | yes |
| **`schema_compliant`** | **`true`** | **`false`** |
| `failure_class` | `null` | `malformed_output` |
| Cost evaluable | `false` (`usage_absent_or_malformed`) | `false` (`usage_absent_or_malformed`) |

Reservations: **exactly 2**, both finalized, `pending_calls: 0`.

Agent calls that reached a model: **exactly 1 per ticket (2 total)**. Three `Agent` tool_use
blocks exist in the transcript; two were **refused before dispatch** and never contacted a
model or spent anything — call #1 blocked by `guard_agent_subspawn.py`, call #3 rejected as
`Agent type 'router-cheap-agent' not found` (that string is the ticket's *route label*, not a
harness subagent type). Classified mechanically by
[inspect_agent_results.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/inspect_agent_results.py).

### Ticket 2 sense fidelity — 3/3, zero other defects

| Sense | Source German (fixture) | Russian returned | Type |
|---|---|---|---|
| 1 | `{%eine Schildkröte%}.` | черепаха | equivalent |
| 2 | `{%ein kleiner Fisch%}.` | небольшая рыба | explanatory |
| 3 | `{%eine Wasserpflanze%}.` | водное растение | equivalent |

All 13 of the handoff's enumerated deterministic defect classes were checked **independently
of the frozen schema** and came back clean: 3/3 senses present, no dropped/merged/reordered
senses, no untranslated German or Latin leak, no `{Tn}` placeholder leakage, `{%…%}` markup
intact, no `key1` drift, no synthetic-promotion claim, provenance hashes bound, no invented
`government`, exactly one card and one record, no letter ё. Deterministic defects other than
the gate failure: **0**. Full output:
[t2_defect_audit.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t2_defect_audit.txt).

## Root cause: a harness-authored prompt/schema contradiction

The Ticket 2 prompt instructed: *"reproduce that sense's German skeleton line EXACTLY as
given above"*. The skeleton lines in the frozen fixture carry a line-opening sense marker:

```
— 1〉 {%eine Schildkröte%}.
```

The model returned exactly that, for all three senses. But the frozen output schema pinned
`german` to the **gloss only**, without the `— N〉 ` prefix:

| | value |
|---|---|
| Fixture skeleton line | `— 1〉 {%eine Schildkröte%}.` |
| Schema pinned `const` | `{%eine Schildkröte%}.` |
| Model returned | `— 1〉 {%eine Schildkröte%}.` |

So the gate fired correctly on a real mismatch — but the mismatch was between two artifacts
authored in this session, not a defect in the route or the model. The model satisfied the
prompt it was given.

The 24-case schema selftest that ran before freezing
([t2_schema_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/t2_schema_selftest.py))
did not catch this: every fixture in it was written against the schema's own constants, so
prompt and schema were never cross-checked against each other. **That is the reusable
lesson — a schema selftest must validate at least one instance built from the prompt's own
inlined source text, not only instances built from the schema.**

## Every semantic hash

| Artifact | sha256 |
|---|---|
| T1 ticket | `02803ee314f65f6b911b5c2b38e817116cfd273975f56acc76aae37690973cd4` |
| T1 request | `b89c58f49bb806ecdb376a82f160beb780aa730e2d4334ee639310f574b77fec` |
| T1 schema | `1702b3d2eb219fb148fbda9a0eb12f06bdcde39e297a86e4ca7a0d4d62829afc` |
| T1 public response | `2ac6a3818e7313c8913457a7529a5c76c42a8f49bed99659959910f1ca589c2b` |
| T1 attestation | `49f8281229779b6006657c1b13e32ebd91246dd7d283275c9a53f2a0b02d8e59` |
| T1 envelope | `b3402bd55c390047ac490859d7debed626ea8d480a05dead3e8ec93ab13a3c5d` |
| T1 canonical result | `b7e054cf6a54a9cfc23a486261514ca7e6b5c48935d0a8ef2af3c126c3f44313` |
| T2 ticket | `b86b4aa700c69799c8cadef61c02be9b16f55fb2b9d7427414ac58d7cceb172a` |
| T2 request | `5a7ae996130a84b178aa55077072663075f7e9e1c21e172eb66ad28314b5957e` |
| T2 schema | `e903556bb71d0d1137333b2559114056d9af60fcdaccceb4d863856c9248ee31` |
| T2 public response | `dac4dc7623265c465cad939bc166fbf847440f6aa7e94a3389286ebb6fdafd5d` |
| T2 final text | `5e1af326eedd13fcc08b89a5e324f97e958019e78ac7bb698879e54af4f576f8` |
| T2 attestation | `d10a5c4124dcaf4ebf6690d145ab705c78008afa887ae9c54b60a1ffd537c50d` |
| T2 envelope | `905abbbd55b819b42c1ed60264ee38dde2786207d8d626d181116eca02479b83` |
| T2 canonical result | `null` (withheld — not schema-compliant) |
| Fixture raw | `152a3eec0b6b9c167a91950d649a10d1f2d413f96c076e17f01859a2eaa9058d` |
| Fixture portrait | `a43235e366573182884922f7fd42a2072c3148cef27de234d24c92fc75cbc4c7` |
| Session transcript | `cc11dcc8ef232a02b7923cc3f07a23284a06464b6861c0c7ff953ed612fc2056` |

Fixture hashes were cross-checked against the frozen v1.144.28 manifest before spend
(`manifest cross-check: OK`).

## Public artifacts

Evidence directory:
[pwg_ru/h2539/evidence/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2539/evidence)

- tickets [t1_ticket.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t1_ticket.json) · [t2_ticket.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t2_ticket.json)
- public responses [t1_response.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t1_response.json) · [t2_response.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t2_response.json)
- attestations [t1_attestation.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t1_attestation.json) · [t2_attestation.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t2_attestation.json)
- envelopes [t1_envelope.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t1_envelope.json) · [t2_envelope.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/t2_envelope.json)
- ledger [canary_ledger.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2539/evidence/canary_ledger.json)

All artifacts are `provenance_class: synthetic_control` and `promotable: false`. Nothing from
this sitting may be promoted into pwg_ru production data.

## Attestation residual — stated explicitly

The H2537 attestation gate is **detectable, not impossible to defeat**, and this sitting
narrowed it further rather than closing it:

1. **Main-turn widening was required.** `gateway_attestation.py` filters to
   `isSidechain: true` by default. This harness records `Agent` tool calls as **main turns**
   (`isSidechain: false`) — the whole transcript holds 101 main turns and **0** sidechain
   turns — so the default filter observed 0 turns and returned
   `model_matches_request: null`, i.e. NO-GO by the handoff's own rule. Both attestations
   here therefore ran with `--include-main-turns` (`sidechain_only: false`, recorded in the
   artifacts). That flag widens the observation window to turns the session itself also
   occupies, so the served model is attested for *the window*, not provably for *the one
   Agent dispatch inside it*. A same-model main turn adjacent to a substituted subagent turn
   would not be distinguished.
2. **The observation is self-reported by the same harness that made the call.** The
   transcript is written by the process under test; it is evidence against accident and
   silent drift, not against a determined adversary with write access to it.
3. **Usage/cost remains unevaluable.** Both envelopes carry
   `usage_policy_reason: usage_absent_or_malformed` and `cost_evaluable: false`; the response
   wrappers carried no `usage` block. Attested token totals exist
   (T2: 41 316 in / 3 945 out / 115 678 cache-creation / 659 914 cache-read) but are
   window-scoped for the same reason as (1), so no per-call cost was sealed. Ledger
   observed-cost floor is `0` and must not be read as "this was free".

Closing the residual needs a harness that emits a per-dispatch identifier binding one
`tool_use` id to one served-model record — not a wider time window.

## What a re-qualification would need (not scheduled here)

No production handoff is minted, per the NO-GO branch of the contract. Should a human
authorise a further sitting, the minimum changes are:

1. Make the Ticket 2 prompt and schema agree on `german` — either pin the full skeleton line
   including `— N〉 `, or instruct the model to emit the gloss span alone. One source of truth,
   generated from the fixture, never hand-typed twice.
2. Add a selftest case built **from the prompt's own inlined text** so a prompt/schema
   divergence fails offline instead of on a paid call.
3. Keep the `--include-main-turns` residual stated in whatever report follows; do not let the
   widened window be quietly reported as a clean per-call attestation.

_Dr. Mārcis Gasūns_
