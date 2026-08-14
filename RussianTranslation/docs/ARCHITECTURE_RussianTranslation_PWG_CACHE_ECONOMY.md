# Architecture — PWG prompt-cache economy

_Created: 13-08-2026 · Last updated: 13-08-2026_

Plan index: [PWG cache economy](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CACHE_ECONOMY_2026Q3.md).

## Design

```text
card/work item
  → whole-card TM hit? return accepted artifact
  → fragment TM hits? fill exact fragments
  → retrieve versioned evidence/examples
  → provider-neutral prompt compiler
       stable prefix + volatile tail + hashes + token estimate
  → exact-prefix scheduler
  → provider adapter (DeepSeek streaming first; Claude existing surfaces)
  → sealed result + append-only event
  → deterministic gates → semantic sample/controller
  → experimental TM namespace only
```

## Identity model

`pwg.cache_request.v1` identifies one request by:

- provider and served/requested model;
- generation parameters and effort;
- prompt compiler version and response-schema version;
- stable-prefix SHA-256 and volatile-tail SHA-256;
- source-card/fragment hashes;
- TM, denylist, retrieved-evidence, grammar, NWS, and relevant corpus hashes;
- parent request ID and repair-variant code when applicable.

The request ID is the canonical serialization hash of those fields. A semantic headword ID is metadata, never cache identity. A changed prompt, schema, evidence asset, or repair variant necessarily creates a new ID.

## Prompt compiler

One PWG-local compiler returns an immutable object:

```text
stable_prefix_bytes
volatile_tail_bytes
stable_prefix_sha256
volatile_tail_sha256
request_identity
token_estimate
provider_envelope
```

The compiler reuses the existing translation, grammar, NWS, masking, and card builders. It must reconstruct legacy Claude and DeepSeek payload bytes for golden fixtures before a migrated mode is eligible. Provider adapters may add transport headers but may not reinterpret content.

Stable-left order remains `preamble → translation → grammar → optional NWS`; card/fragment content stays in the volatile tail. Calls are grouped by exact provider/model/prefix hash and executed contiguously. The first position is cold; later positions are warm candidates. No warm hit is assumed until provider telemetry proves it.

## Hierarchical reuse

1. Whole-card TM: exact content-addressed accepted card; zero model call.
2. Fragment TM: exact accepted fragments; generate only missing fragments.
3. Retrieval: versioned evidence/examples selected deterministically and included in request identity.
4. Provider prefix cache: billed prompt reuse, measured cold/warm.
5. Generation: only the unresolved tail.

The experimental TM namespace mirrors the canonical schemas but uses a separate root and explicit `experimental=true` provenance. No code path may promote it to the canonical store/TM.

## Event ledger

`pwg.cache_event.v1` is append-only JSONL. Each event binds run, request, prefix group, cold/warm ordinal, attempt, parent/variant, timestamps, transport outcome, requested/served model, usage buckets, pricing table/version, cost evaluability, latency, output termination, audit verdict, and accepted-artifact denominator. Missing usage is `null` plus a reason, never zero.

Sealed per-run manifests declare N, cost/call ceilings, schedule window, pricing version, cohort hashes, retry/escalation ladder, and acceptance rules before the first call. Reports are deterministic derivations from manifests, events, and audit artifacts.

## DeepSeek adapter

The adapter uses an official or OpenAI-compatible streaming client with persistent connection pooling, incremental event consumption, bounded connect/read/overall deadlines, and durable partial-failure classification. It records provider usage and cache-hit/miss fields without normalizing absent values to zero. The schedule gate refuses peak execution after 16-08-2026 16:00 UTC unless a new human ruling supersedes the standing policy.

## Retry and overrun state machine

1. `exact-retry`: same sealed request bytes and identity after a transient transport failure.
2. `compact-response`: new declared variant that strengthens concise schema-preserving output instructions.
3. `bounded-output-increase`: new declared variant within a sealed ceiling.
4. `partition`: deterministic card/fragment split, each child content-addressed and linked to the parent.

No free-form prompt mutation is allowed. Repeated systemic failures trip the run stop rather than walking the ladder indefinitely.

## Migration

Legacy manifests remain readable during wave 1. A deterministic converter creates v1 request records and records its source manifest hash, converter version, and any non-representable field. Conversion fails closed on ambiguity. New and legacy execution modes run side by side; rollback selects the legacy adapter and leaves v1 evidence intact. Promotion allowlists remain unchanged.

## Build-versus-reuse verdict

| Component | Verdict |
|---|---|
| Whole-card and fragment TM | Reuse unchanged; add namespace boundary and identity inputs. |
| Translation/grammar/NWS/card builders | Reuse; wrap in compiler. |
| Bare cwd, safe mode, stable-left order | Reuse existing Claude implementation. |
| TTL-aware cost accounting and Message Batches | Reuse and map into common ledger. |
| DeepSeek HTTP transport | Replace the failing non-streaming Pro path. |
| Common request identity, event ledger, prefix scheduler, converter | New PWG-local gap. |
| Shared cross-repo package | Defer until two PWG lanes pass. |

_Dr. Mārcis Gasūns_
