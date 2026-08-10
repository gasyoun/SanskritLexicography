# Served-model + usage attestation for the router.cheap Agent bridge (H2537)

_Created: 10-08-2026 · Last updated: 10-08-2026_

**Model:** Opus 5 (`claude-opus-5`). Handoff H2537 (**Opus 5**) — *Capture served-model + usage
from the harness transcript so router.cheap qualification evidence is observed, not
self-asserted*. Predecessor: H2533 (**Codex**, `gpt-5.6-sol`) — *Build the durable router.cheap
Agent reserve/record bridge*, released as
[`v1.144.27`](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.27).

## Why this exists — the defect H2534 hit before spending anything

[H2534](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2534-Opus_SanskritLexicography_router-cheap-live-canary-gateway-w1_10.08.26.md)
(**Opus 5**) — *Run the released router.cheap two-ticket live canary and mint gateway-w1 only on
GO* — asked for two paid Agent calls whose PASS criteria included "exact returned route/model"
and "truthful usage/cost-evaluability". Preflight found those two facts **unobservable** from the
session that was supposed to attest them:

| Field | Who supplied it, pre-H2537 | Independently checked? |
|---|---|---|
| `returned_model` | the operator, typed into the response wrapper | **No** — [`_validate_response_binding`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_external.py) required it to equal the *requested* model, so it only enforced self-consistency of the assertion |
| `model_matches_request` | hardcoded `True` in `record_external` | **No** — and the envelope schema pinned it to `{"const": true}`, so a substitution was **unrecordable by construction** |
| `usage` | the operator, or absent | **No** — absence fell back to the waiver as `cost_evaluable=false` |

The Agent tool returns **text only**: no served-model string, no token counts. Every
`ANTHROPIC_DEFAULT_*_MODEL` alias in the session environment is empty, so alias→model resolution
happens router-side, invisibly to the caller. Executing H2534 as written would therefore have
hash-sealed operator assumptions into an envelope that *reads* as cryptographic proof — the
reconstructed-as-recovered mislabel class. H2534 was returned **NO-GO with zero calls**, and this
work removes the blocker instead of spending against it.

## What was built

[`gateway_attestation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gateway_attestation.py)
— a read-only module that reads the local Claude Code session transcript
(`~/.claude/projects/<slug>/<session>.jsonl`), which the harness writes independently of the
operator. Each `assistant` event there carries `message.model` (the model the endpoint reported)
and a full `message.usage` block; Agent-tool turns are flagged `isSidechain: true`.

It emits a canonical, self-hashed `pwg.gateway_external_attestation.v1` record: served models
observed in the call window, token totals, turn counts, and `unparseable_lines`. Bridge changes:

- `record-external` takes an optional `--attestation`; the record must bind to the same
  run/reservation/requested-model and cover the wrapper's exact window, and its self-hash must
  verify. A mis-bound attestation is **refused**, never ignored.
- `model_matches_request` is now computed: `true`/`false` from the attestation, or **`null` when
  no attestation exists** — "not independently established", never a bare `True`.
- Envelope schema relaxed from `{"const": true}` to `boolean|null` and extended with
  `model_attested`, `attested_model`, `attestation_sha256`, `attested_usage_totals`,
  `attestation_ambiguous`. This is the load-bearing change: the format can now *express* a
  substitution.
- An attested mismatch is sealed truthfully as `model_matches_request: false`,
  `failure_class: model_substituted`, `schema_compliant: false`, with no result and no cost
  claim — recorded rather than refused, so the evidence of the substitution survives.
- Two or more distinct served models in one window ⇒ `ambiguous: true` and `attested_model: null`.
  It never guesses which turn served the ticketed call.

No HTTPS client, no `c4` alias, no Max fallback, no alternative model, and
`ANTHROPIC_AUTH_TOKEN` is never read, printed or persisted.

## Verification

| Gate | Result |
|---|--:|
| Released bridge selftest `gateway_external_selftest.py` | **PASS 11/11**, semantic signatures **unchanged** (`request=a1f31521…`, `schema=d695c9f4…`, `result=d0c45566…`) |
| New `gateway_attestation_selftest.py` | **PASS 9/9** |
| `py_compile` on all three changed/added modules | OK |
| Envelope schema JSON validity · trailing whitespace · EOF newline | OK · 0 · OK |

Signatures being byte-identical is the point: the released contract is extended, not redesigned.

End-to-end on a **real** transcript (this session's own, read-only, zero spend):

| Measure | Value |
|---|--:|
| Assistant turns in window | 115 |
| `models_observed` | `['claude-opus-5']` (unanimous) |
| `attested_model` / `model_matches_request` | `claude-opus-5` / `true` |
| `output_tokens` | 60,955 |
| `input_tokens` | 897,055 |
| `cache_read_input_tokens` | 9,200,264 |
| `cache_creation_input_tokens` | 510,617 |
| Turns with usage · unparseable lines | 115 · 0 |

So both previously-unobservable fields are now recoverable from real harness data. Counted tokens
also mean a cost claim can rest on arithmetic instead of the unknown-cost waiver.

## Trust boundary — stated, not implied

`message.model` is **the endpoint's own claim as recorded by the client**, not a cryptographic
proof from the router. A dishonest or misconfigured gateway could still report a model it did not
run. Attestation narrows the trust boundary from *"the operator asserted it"* to *"the harness
observed the endpoint assert it"*, and makes substitution and token usage **detectable**. It does
not establish physical model identity, and an attested envelope must never be described as if it
did.

Two further residuals: attestation windows are matched by timestamp, so a concurrent unrelated
Agent call inside the same window shows up as `ambiguous` rather than being disambiguated; and
`sidechain_only` (the default) assumes the ticketed call is an Agent-tool turn, with
`--include-main-turns` as the explicit opt-out.

## Consequence for H2534

The blocker is removed: a re-run can now bind `returned_model` and `usage` to an independent
observation, so a GO would rest on observed facts. H2534 stays **open** — it is a paid two-call
sitting that a human still has to authorise; this handoff deliberately spent nothing.

_Dr. Mārcis Gasūns_
