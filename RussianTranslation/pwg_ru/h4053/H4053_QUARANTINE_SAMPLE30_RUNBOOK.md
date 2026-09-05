# H4053 — Quarantine sample-30 report-only workflow: runbook

_Created: 05-09-2026 · Last updated: 05-09-2026_

**Executor model (this implementation):** OxAlpha — GLM 5.3 Flash
(`glm-5.3-flash` via opencode z-ai route). **No paid translation was run and
none is authorized by this document.**

## What exists now

- Entrypoint: [`src/pwg_quarantine_sample30.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_quarantine_sample30.py)
  — `freeze` / `run` / `selftest`. No promote/apply code path exists in the
  module; the campaign is created `promotable=False`.
- Frozen packet: [`reports/H4053_quarantine_sample30_frozen.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4053_quarantine_sample30_frozen.json)
  — exactly 30 distinct identities nested from the 01-08 200-row sample
  (seed 20260801) under freeze seed 20260904; all 200 parent identities
  still resolve in the fresh 10,902-row quarantine, so `unavailable` and
  `deterministic_substitutions` are both empty.
- Proof: `python3 src/pwg_quarantine_sample30.py selftest` — 6/6 offline
  (reservation-before-I/O, resume without duplicate provider spend,
  attribution, input preservation + unchanged store/mirror/queue guards,
  zero-I/O dry run, no-promote negative control).

## Label discipline

The 10,902/11,519 figure is a **segmentation-change flag, not an observed
bad-translation rate**. Every packet row carries
`ru_quality_verdict: unknown_not_measured` and
`review_class: unmeasured_pending_paid_read`; the five review classes
(`segmentation_only`, `semantic_mistranslation`, `sanskrit_loss`,
`apparatus`, `ambiguous`) are assigned only by independent human review
after an actual paid generation.

## Commands

### 1. Dry run (zero provider I/O, zero reservations — always safe)

```bash
python3 src/pwg_quarantine_sample30.py run \
  --frozen-packet reports/H4053_quarantine_sample30_frozen.json \
  --provider fake --max-calls 30 --cost-ceiling-usd 4.00 \
  --workdir /tmp/h4053_dryrun --evidence-dir /tmp/h4053_dryrun_ev \
  --dry-run
```

### 2. Offline replay proof (fake provider, no network, no spend)

```bash
python3 src/pwg_quarantine_sample30.py run \
  --frozen-packet reports/H4053_quarantine_sample30_frozen.json \
  --provider fake --max-calls 30 --cost-ceiling-usd 4.00 \
  --workdir /tmp/h4053_replay --evidence-dir /tmp/h4053_replay_ev
```

Rerunning it verbatim must report `calls_dispatched: 0, resumed_skipped: 30,
guard_unchanged: true` — resume without duplicate spend.

### 3. Execute (SEPARATELY GATED — read before running)

```bash
# GATE A (fresh, ≤6h old): /pwg-live-gate GO receipt for the target profile
# GATE B (fresh route health): wall < 80,000 ms, API < 45,000 ms, zero conn errors
# GATE C: store backup taken; no other session holds the store claim

python3 src/pwg_quarantine_sample30.py run \
  --frozen-packet reports/H4053_quarantine_sample30_frozen.json \
  --provider glm --model <resolved-glm-model-id> \
  --max-calls 30 --cost-ceiling-usd <USD-CEILING> \
  --timeout-ms 120000 --max-output-tokens 2048 \
  --workdir <run-dir> --evidence-dir <evidence-dir> \
  --store <canonical-store.jsonl> --mirror <mirror.jsonl> --queue <queue.jsonl>
```

Mandatory numeric caps: `--max-calls` (reserved per slot strictly before
provider I/O; the run stops closed at the ceiling) and `--cost-ceiling-usd`
(worst-case pre-dispatch check in the kernel). `--max-calls 30 --cost-ceiling-usd 4.00`
is the reviewed envelope for one full sample pass.

**Recorded dependency (blocking live execute on GLM):** the `glm-flash`
route has **no verified price card** (H4057), so the kernel's
`assert_budget` fails CLOSED — a dollar-bounded GLM execute refuses with
`cost_ceiling` before any reservation. Call-count capping alone does not
satisfy the H2157 both-ceilings rule. Live execute on `--provider glm`
therefore stays blocked until a real GLM price card lands in
`providers.PRICE_PER_MTOK_USD`; the xAI/DeepSeek routes are bounded today.
Do NOT invoke Claude Code from the GLM lane as a workaround.

## Inputs, evidence, guards

- Input identity: each card carries `input_hash` (SHA-256 of its fresh
  quarantine row); the packet file hash is sealed into the receipt.
- Evidence: `--evidence-dir` receives per-call sealed request/response
  receipts plus `H4053_review_packet.json` (source identity, old RU when the
  store is present, candidate RU, call/reservation ids, request/response
  SHA-256, usage, served model) and `H4053_run_receipt.json`.
- Store/mirror/queue: hashed before and after; the run refuses to end
  `guard_unchanged: false`. Surfaces absent on this box are recorded as
  `guard_absent_surfaces`, never fabricated.
- Interrupted runs: a call with a sealed response is left open for human
  reconciliation and skipped; a call with no response is terminally
  accounted `interrupted_no_provider_io` and the card re-executes under a
  derived resume key (the forfeited slot stays spent — no refund, no
  double-billing).

_Dr. Mārcis Gasūns_
