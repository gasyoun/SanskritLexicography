# H4057 — GLM 5.3 Flash Route Qualification Packet (offline, no cutover)

_Created: 05-09-2026 · Last updated: 05-09-2026_

**Executor:** OxAlpha — GLM 5.3 Flash (opencode/z-ai/glm-5.3-flash) · **Handoff:** H4057 · **Status:** offline deliverable complete, production route unchanged

## 1. Resolved installed model identity

Local records disagreed on slug spelling; the actual resolved identity, read
from OpenCode configuration metadata (never from chat memory or a guessed
slug):

| Field | Value |
|---|---|
| OpenCode default model | `zai-coding-plan/glm-5.3-flash` |
| Wire model id (API) | `glm-5.3-flash` |
| Route constant | `glm-flash` (`model.ROUTE_GLM`) |
| Base URL constant | `https://api.z.ai/api/paas/v4` (documented default; **confirm endpoint at live authorization**) |
| Credential env | `ZAI_API_KEY` (never committed; placeholder in `.env.example`) |
| Source | `~/.config/opencode/opencode.jsonc`, `model` key, 05-09-2026 |

The `zai-coding-plan` prefix is an OpenCode routing namespace; the wire model
id is the part after the slash.

## 2. What was implemented (adapter seam only)

1. `src/pwg_pipeline/model.py` — `ROUTE_GLM = 'glm-flash'` added to `ROUTES`
   and `BILLABLE_ROUTES` (a real paid API). Provenance routes
   (`claude-headless-shadow`, `deterministic-reuse`, `imported-draft`) remain
   non-billable — pinned by test.
2. `src/pwg_pipeline/providers.py` — `GlmFlashAdapter` (`glm`), sharing the
   `_OpenAICompatibleAdapter` body: same reservation ledger, strict
   request/response schema, raw response receipts, usage provenance, timeout,
   serialized bounded calls. No new orchestration, no direct SDK calls, no
   Claude CLI anywhere.
3. `src/pwg_pipeline/kernel.py` — `assert_budget` now converts a
   missing-price-card refusal into an accounted `KernelRefusal(cost_ceiling)`
   BEFORE reservation, instead of an uncaught exception.
4. **No price card for `glm-flash`.** Unknown cost stays unknown:
   `estimate_cost_usd` refuses, dollar-bounded GLM campaigns fail closed
   before any reservation, and token usage without a card normalizes to
   `cost_basis: unevaluable`. No Claude/xAI/DeepSeek price is borrowed.
   Dispatching GLM through the kernel requires a **verified z.ai list-price
   card** added to `PRICE_PER_MTOK_USD` first (that edit is a live-run
   prerequisite, deliberately not done offline).

## 3. Offline replay receipts

Sealed report: [reports/H4057_glm_route_qualification.json](../reports/H4057_glm_route_qualification.json)
(sha256 `df64a5a02bbd4e3cffb0692e8d57c23a80d63a3a6226fe25c48ba309f20612e6`,
verdict `QUALIFIED_OFFLINE`). Zero provider calls, zero Claude CLI
invocations, canonical store untouched. Reproduce with:

```bash
python tools/h4057_glm_route_qualification.py replay
```

| Case | Result |
|---|---|
| pure gloss / Sanskrit `{#…#}` / apparatus `<ls>`+Nachtr. / homonyms / long card | parsed, source strings verbatim in output, receipts sealed |
| malformed result (prose, non-list, empty) | `ProviderError`, never guessed |
| missing usage | `cost_evaluable: false`, kernel halts wave `unevaluable_usage` |
| route substitution (served ≠ requested) | `GlobalStop(route_substitution)`, terminal accounting exactly once |
| success path (synthetic qualification-only price card) | reserve → dispatch → seal → finalize exactly once, ledger spent = 1 |
| dollar-bounded campaign, real card-less state | `KernelRefusal(cost_ceiling)` BEFORE reservation: 0 dispatches, 0 reservations |

The synthetic card (`input 1.0 / output 1.0`) exists only to exercise the
kernel mechanics offline and is stamped `synthetic-qualification-only` in
every receipt; it is not a price observation.

Regression: `python -m pytest tests/ -k pwg_pipeline` → **142 passed**
(includes new `tests/test_pwg_pipeline_glm_route.py`, 13 tests).

## 4. Three separate gates (never conflated)

1. **Model-route validity** — the wire model id exists, is reachable under the
   resolved identity, and serves what was requested. Requires a LIVE canary;
   not provable offline.
2. **Mechanical fidelity** — markup/gloss/apparatus survival, sense coverage,
   NWS owner attribution, requeue hygiene over a bounded sample. Deterministic
   gates (`audit_window.py`-class), runnable on any live sample.
3. **Independent semantic quality** — human/judge review of Russian gloss
   quality against the control route. Requires the existing control-plane
   independent review; **no self-signing**: this OxAlpha run cannot grade its
   own semantics.

Gate 1 and 3 both require the authorized live run below.

## 5. Sealed 30-card qualification manifest

Built deterministically where the canonical `pwg_ru` store lives (the store is
local-only/gitignored, so it cannot be sealed from this worktree):

```bash
# 1. export 30+ candidate cards to cards.jsonl (fragment_id, fragment_class,
#    source_string, context — one JSON object per line)
# 2. seal:
python tools/h4057_glm_route_qualification.py build-manifest \
    --cards cards.jsonl --count 30 \
    --out reports/H4057_glm_live_manifest.json
```

Stride selection over the sha256-ordered card list is seedless and
reproducible; the output is sealed by `pwg.pipeline.evidence.seal`. Quarantine
sample cards may be substituted 1:1 by payload hash before sealing, with
substitutions recorded in the live run report.

## 6. Staged live qualification run (SEPARATELY AUTHORIZED — do not run now)

Prerequisites (all must hold, else the run is not GO):

1. A human ruling extends the canary fence to the GLM route — today
   `cli.CANARY_PROVIDERS == ('xai', 'deepseek')` is a ruling-pinned constant;
   the one-line extension is an authorization-time decision, not part of this
   handoff.
2. Verified z.ai list prices added to `PRICE_PER_MTOK_USD[ROUTE_GLM]`
   (unknown cost currently fails every dollar-bounded dispatch closed).
3. `ZAI_API_KEY` set from the gitignored `.env`; endpoint confirmed
   (`api.z.ai/api/paas/v4` vs coding-plan variant).
4. Fresh canary GO receipt for the profile (≤6 h), existing control-plane
   independent review booked for gate 3.

Capped command shape (after prerequisites), one campaign per call, nothing
promotable, `--stop-before-promote` semantics preserved:

```bash
python -m pwg_pipeline --database <run>.sqlite canary \
    --providers glm --max-calls 2 --cost-ceiling-usd 4 \
    --timeout-ms 120000 --workdir <workdir>
```

Then the bounded 30-card qualification window through the same kernel, capped
by `max_calls=30` and the campaign cost ceiling, outputs audited by the
deterministic gates of §4 before any quality claim is drafted.

## 7. Production status

Production remains on its current authorized headless route. Nothing in this
packet mutates the store, the Wave-1 dump, or any control-plane constant
beyond the adapter seam. No translation-quality claim is made or implied.

_Dr. Mārcis Gasūns_
