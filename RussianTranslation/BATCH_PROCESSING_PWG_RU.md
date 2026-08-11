# PWG→RU Message Batches — offline-ready operating contract

_Prepared 11-08-2026. No live API call is authorised by this document._

The current cash policy is **subscription-credit first, then Batch for extra
volume or asynchronous throughput**. The active planning baseline is Claude Max
20x ($200/month) plus the separately claimed $200/month Agent SDK credit for
`claude -p`. A claim must be evidenced in the execution manifest before the CLI
counter is classified as credit consumption. Otherwise billing stays unknown.
The CLI's `total_cost_usd` is never treated as incremental subscription cash.

For the attested two-ticket workload (41,320 input, 4,263 output, 116,439
one-hour cache-write, 974,856 cache-read tokens), the pinned Opus 5
counterfactual is $1.964993 standard and $0.9824965 Batch. Thus $200 corresponds
to roughly 102 standard units or 204 Batch units. These are list/rate-card
equivalents, not observed `router.cheap` cash. See Anthropic's
[subscription-credit policy](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
and [Message Batches documentation](https://platform.claude.com/docs/en/build-with-claude/batch-processing).

## Offline workflow

Batch-ready manifests are generated with an explicit output ceiling, for
example `--batch-max-output-tokens=32768`. Without that opt-in declaration,
the batch compiler refuses the manifest. This preserves existing golden
manifests byte-for-byte. The compiler accepts only the exact model in the
source manifest (`claude-sonnet-5` or `claude-opus-5`); there is no model
override.

```powershell
python src/pilot/pwg_batch.py prepare `
  --manifest <execution-manifest.json> `
  --out <batch-plan.json> --max-requests 100 --cost-ceiling 10

python src/pilot/pwg_batch.py check --plan <batch-plan.json>
```

Both commands are credential-free and make zero network calls. The sealed
`pwg.batch_plan.v1` binds the source-manifest bytes, model, output limit, schema,
prompt bytes, one-hour cached prefix, volatile suffix, stable `custom_id`, and
the 100,000-request/256 MB/24-hour/29-day provider assumptions. The project
default remains 100 requests.

Wave 0 contains the manifest's existing whole-card batches and uncached
presplit fragment groups. Fetch matches unordered provider results only by
`custom_id`; only unresolved cards/fragments are compiled into wave 1 and later.

## Credential-gated future workflow

```powershell
python src/pilot/pwg_batch.py check --plan <batch-plan.json> --live
python src/pilot/pwg_batch.py submit --plan <batch-plan.json>
python src/pilot/pwg_batch.py status --plan <batch-plan.json>
python src/pilot/pwg_batch.py fetch --plan <batch-plan.json> `
  --out <results-dir> --next-plan <heal-wave-1.json>
```

`submit` reserves every request and persists submission intent before provider
creation. A lost create response seals `ambiguous_submit` and is never retried
automatically. Terminal succeeded, errored, canceled, and expired results are
finalized exactly once; explicit non-billed terminal evidence retains zero
tokens/cash rather than inventing missing usage.

All plans and results are `synthetic_control`, `promotable: false`. This path
does not alter the production default, promotion allowlist, store, or TM.

## Offline acceptance evidence

On 11-08-2026, a freshly generated real 100-card nominal manifest compiled to
10 requests, 501,650 request-body bytes, and a tokenizer-free conservative
$4.94624075 Batch
upper estimate. Replay produced the same plan hash
`feb86bb52b1edb3a873908c79042fdb5c37c4cc4dcb4f0ec5b814e0f3ca4e3f5`.
No credential, network request, reservation, store/TM write, or promotion was
used.
