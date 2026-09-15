# H4531 — Anthropic Message Batches API bounded probe: transport built, live arm BLOCKED on an invalid credential

_Created: 11-09-2026 · Last updated: 15-09-2026_

Model: Opus 5 (`claude-opus-5[1m]`), unattended handoff worker, pool=sonnet.
Handoff: [H4531](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4531-Opus_RussianTranslation_pwg-ru-messages-batches-api-probe_10.09.26.md)
(Opus, 🟡2 medium, class money — budget pre-authorized by MG 10-09-2026).
elapsed: ~75 мин (interactive session, no worker log — no tok/s figure is claimed).

## Re-probe 15-09-2026 — credential still invalid, branch relanded on current master

Worker 1 on executor Claude/c1, Opus 5 (`claude-opus-5[1m]`), re-dispatched by the pool=opus drain.

1. `python src/pilot/h4531_auth_probe.py` → **rc=4**,
   `{"authenticated": false, "model_available": false, "reason": "AuthenticationError:http_401"}`.
   `C:\Users\user\.secrets\anthropic.env` is the only Anthropic credential file on this box and
   its mtime is still 02-08-2026 — no key rotation has reached it since the 11-09 run. No
   `ANTHROPIC*` variable is set in the worker environment. The paid arm was therefore **not
   attempted** (a submit would only burn a fresh 23-call ceiling at $0, per § Finding).
2. The 11-09 commits were cherry-picked onto `origin/master` `fcffedb0e` in a fresh worktree
   (one conflict, `LAUNCH_FUCKUPS.md` — resolved by keeping both the H4527 and the H4531
   entries). Gates re-run on the rebased tree, all **PASS**: `anthropic_batches_route_selftest`,
   `execution_contract_selftest`, `route_compare_selftest` (10/10), `gateway_route_selftest`,
   `gateway_external_selftest`, `gateway_attestation_selftest` (9/9),
   `gateway_canary_contract_selftest` (3/3), `call_reservation_selftest`,
   `usage_accounting_selftest` (6/6), `lang_parity_check` (112 entries, no drift),
   `window_selftest` (225/225).
3. Verdict unchanged: **INCONCLUSIVE**, blind spot open, one valid key away from GO/NO-GO.
   The human step in § What unblocks the live arm is still the only way forward.

## Verdict: INCONCLUSIVE — neither GO nor NO-GO, and deliberately not a dead end

The async Batches arm was **built, gated and costed offline**; the **paid arm never ran**,
because the prepared credential is rejected with HTTP 401 `authentication_error` — "API key
is invalid". That is not a property of the Batches API, so recording a
[DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
entry would be a false negative: it would close a blind spot that is still open and would
tell a future session the route was measured and rejected when nothing about the route was
measured at all. The H1403 ledger #8 / A8 blind spot therefore **stays open**, one credential
away from a verdict.

What IS now settled, and was not before this pass:

1. The repo has a Batches transport that obeys the same money contract as the synchronous
   arm — reserve-then-submit, sealed non-promotable envelopes, 50 % batch pricing, the
   deterministic RU audit gate.
2. The probe is fully prepared on real data (root `dā`, 23 one-card requests), so the live
   arm is one `submit` away with no further design work.
3. A real defect in the reserve-then-submit contract surfaced the moment a credential
   failed — see § Finding below. It would have bitten the first live run either way.

## What was built

| Artifact | What it is |
|---|---|
| [src/pilot/anthropic_batches_route.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/anthropic_batches_route.py) | The `anthropic-batches` transport: `build_batch` · `submit` (reserve N, then one provider call) · `poll` · `retrieve` (one sealed envelope per request) |
| [src/pilot/anthropic_batches_route_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/anthropic_batches_route_selftest.py) | 31 hermetic assertions, B-01…B-09, zero network, zero spend |
| [src/pilot/h4531_batches_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_batches_probe.py) | The four-phase resumable driver: `build` → `submit` → `collect` → `report` |
| [src/pilot/h4531_auth_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_auth_probe.py) | Zero-token credential/model reachability check, $0, re-runnable after a key rotation |
| [src/pilot/h4531_pick_keys.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_pick_keys.py) · [src/pilot/h4531_cost_model.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_cost_model.py) | Card selection and the pre-submit cost estimate, both re-derivable without a paid call |
| [src/pilot/usage_accounting.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/usage_accounting.py) | New `SONNET_STANDARD_PER_MTOK_USD` + optional `rate_card=` on `build`/`equivalent_usd`. The Opus default is untouched, so no existing receipt changes meaning |
| [src/pilot/route_transport.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/route_transport.py) | New `ANTHROPIC_BATCHES_ROUTE` token + `batch_expired` / `batch_canceled` failure classes |

### Shape discipline, asserted not asserted-by-comment

- **One card per batch REQUEST** (the H4054 shape). The driver refuses a manifest batch with
  more than one key by name: `H2152-rejected shape: batch [...] carries N cards`. N cards in
  one request cannot be expressed by this module — it only accepts a list of single-card
  `pwg.transport_request.v1` objects.
- **No prompt-cache breakpoint.** The H2674–H2756 cache chain closed NO-GO "must not be
  rerun"; B-02 asserts no `cache_control` key rides a batch request. This is also why the
  batch arm is *not* expected to reproduce the synchronous arm's cache economics — the
  comparison is transport-vs-transport at plain-text pricing.
- **Synthetic, non-promotable by construction.** `build_request` pins
  `provenance_class=synthetic_control` / `promotable=false`, so the `--stop-before-promote`
  discipline lives in the artifact rather than in a flag a session could forget.

## Checks — actual output

| Command | Result |
|---|---|
| `python src/pilot/anthropic_batches_route_selftest.py` | **PASS** — 31/31 assertions (B-01…B-09) |
| `python src/pilot/window_selftest.py` | **PASS** — ran 223/223 defined, 223 passed, 0 failed |
| `python src/pilot/execution_contract_selftest.py` | **PASS** |
| `python src/pilot/route_compare_selftest.py` | **PASS** (10/10 groups) |
| `python src/pilot/gateway_route_selftest.py` · `gateway_external_selftest` · `gateway_attestation_selftest` · `gateway_canary_contract_selftest` | **PASS** (all four) |
| `python src/pilot/call_reservation_selftest.py` | **PASS** (0/1/N, race/resume, finalization, probes/cost, durations) |
| `python src/pilot/usage_accounting_selftest.py` | **PASS** (6/6) |
| `python src/pilot/lang_parity_check.py` | **PASS** — 109 entries, all verdicts complete, no drift |
| `python src/pilot/h4531_auth_probe.py` | **rc=4**, `{"authenticated": false, "model_available": false, "reason": "AuthenticationError:http_401"}` |
| `python src/pilot/h4531_batches_probe.py submit --max-calls 23` | **REFUSED by the provider** — `anthropic.AuthenticationError: 401 … 'API key is invalid.'` |

`window_selftest` failed once on the way through, on `test_lang_parity_ledger_complete`:
the parity ledger pins a SHA-256 of `route_transport.py`, which this pass edited. The
`pwg_transport_comparison_20260811` row's **INTENTIONAL-DIVERGENCE verdict still holds** —
the batches arm reuses that row's RU `audit_canary` verbatim, so the divergence remains the
RU content gate (three Russian senses, Cyrillic-only, no ё, no unresolved `{Tn}`), not the
transport. The row was extended to name `anthropic_batches_route.py`, the note records why
the verdict is unchanged, and the hash was refreshed with the prescribed
`lang_parity_check.py --update-hash`.

## The prepared probe, on real data

- **Root:** `dā` (`d_a`) — the one root in the lane's input tree that carries a rootmap, and
  therefore the only root a production-path manifest can currently be generated for.
  `verb_worklist.py --top` prints **0 runnable roots** (701 remaining roots all lack
  rootmaps), so "a real root from the worklist" resolves to `dā` today; the probe's 23 cards
  are its smallest real sub-cards by source bytes, picked by
  [h4531_pick_keys.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_pick_keys.py).
- **Manifest:** 24 selected keys → 23 batches of exactly 1 card (one key resolved from
  translation memory), generated through the production generator with `--output-budget=1`,
  `manifest_sha256 930c9748a388d8452b236418bdca6d03cf3d61cfde5887bdb56c117b8167d6bf`.
- **Requests:** 23 one-card `pwg.transport_request.v1` objects, 368 681 prompt bytes total
  (mean 16 029, min 15 740, max 16 094 per card), model `claude-sonnet-5` — the production
  lane's own model, so the comparison is apples-to-apples.

### Cost the ceiling was sized against (ESTIMATE, not a measurement)

`bytes/4` is not a tokenizer; these are order-of-magnitude figures from
[h4531_cost_model.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_cost_model.py),
to be replaced by provider `usage` on the first live run.

| Arm | Input tok | Output tok | USD |
|---|---|---|---|
| Sonnet-5 standard API | ~92 170 | ~27 600 (at 1 200/card) | **~0.69** |
| Sonnet-5 Batches (50 %) | ~92 170 | ~27 600 | **~0.35** |
| Production CLI lane (subscription) | same prompt bytes | same | **0 cash**, but jitter-bound |

The third row is why a GO is not a foregone conclusion even at half price: the synchronous
home lane spends **no cash at all** (Max subscription, `max_interactive` billing). The
Batches case is not "cheaper than the CLI lane" — it is "buys latency-immunity for ~$0.015
per card, where the CLI lane buys it with wall-clock gambling" (8.9 → 59.2 s jitter, ~⅓ of
windows over ceiling, per
[PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md)).
The live arm must produce that trade-off as numbers, not as this paragraph.

## Finding — reserve-then-submit burns the whole ceiling on a pre-billable failure

Observed, not theorised. The ledger after the 401:

```
max_calls 23 · calls_spent 23 · finalized_calls 0 · pending_calls 23 · observed_cost_usd 0.0 (cost_evaluable false)
```

The money contract requires the ceiling to be spent **before** the provider is called — that
is the whole point, and it held exactly as designed (acceptance criterion "ceiling reserved
pre-submit": met). The cost is that an authentication failure, which bills nothing, still
consumes the entire ceiling, so the retry cannot reuse the run: a second attempt needs a new
`run_id` or a raised ceiling, and the ledger permanently carries 23 pending reservations
against $0 of real spend.

This is inherited behaviour, not new: `anthropic_messages_route` documents the same
irreversibility ("reservation is irreversible"). It is recorded rather than patched because
"release the reservation when the provider refused" is exactly the hatch that, mis-scoped,
lets a real billable failure look free. The honest mitigation is cheap and already shipped:
**run [h4531_auth_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4531_auth_probe.py)
first** — it is a zero-token authenticated GET, it costs nothing, and it turns this class of
ceiling burn into a $0 rc=4.

## What unblocks the live arm (human, ~2 minutes)

A valid Anthropic API key must reach the lane. The agent must not author one, and no key is
typed in chat, in code, in a log or in an artifact.

1. Open the Anthropic console → API keys, create (or copy a live) key for the workspace that
   should carry this probe's spend.
2. On this Windows box, replace the single `ANTHROPIC_API_KEY=` line in
   `C:\Users\user\.secrets\anthropic.env` with the live value. The file already exists and is
   already the path
   [anthropic_messages_route.SECRETS_ENV](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/anthropic_messages_route.py)
   reads, so nothing else changes.
3. Prove it for $0 — expect `authenticated: true, model_available: true`:

```sh
cd ~/Documents/GitHub/SanskritLexicography/RussianTranslation
python src/pilot/h4531_auth_probe.py
```

4. Then the paid arm, ~$0.35, bounded by a fresh ceiling (`--max-calls 23`); `collect` is
   resumable and may be re-run later if the async window runs long:

```sh
python src/pilot/h4531_batches_probe.py build   --manifest pwg_ru/h4531/execution_manifest.h4531.json --out-dir pwg_ru/h4531/run2
python src/pilot/h4531_batches_probe.py submit  --out-dir pwg_ru/h4531/run2 --max-calls 23
python src/pilot/h4531_batches_probe.py collect --out-dir pwg_ru/h4531/run2 --wait-seconds 900
python src/pilot/h4531_batches_probe.py report  --out-dir pwg_ru/h4531/run2
```

**If it is done:** the cost/latency table above gets real provider numbers and H4531 reaches
a GO or NO-GO, closing a blind spot that has been open since 20-07-2026.
**If it is not done:** the transport sits green and unused, the blind spot stays open, and
latency-blocked lanes keep waiting on the jitter-dominated synchronous route. Nothing
degrades — there is no deadline on this — but no amount of further offline work can produce
the verdict.

## Second blocker — the branch could not be pushed, and no PR exists

`git push -u origin h4531-batches-probe` from this worktree was refused by the shared
pre-shell guard, verbatim:

> HANDOFF DUPLICATE-PUSH BLOCKED: origin/main already has a commit naming H4534 that this
> branch cannot reach — 5fd0a1d29 fill: H4534-H4538 acceptance+evidence sections (H4477
> follow-up batch, minted 10-09) + GTD pick-row closed (MG 'mint all' 10-09). Someone else
> likely already shipped this handoff (FINDINGS §288, H1991 class). Fetch + check before
> pushing a second implementation; if this really is a sanctioned adjacent-lane split, add
> the literal marker `[dup-push-ok]`.

Named as a shape, not acted on. Three probes say this is a **false positive**, and the
escape marker was deliberately NOT added — an agent does not issue itself a guard
permission (`rules/agent-never-self-authorizes-an-escape.md`, incident H3880):

1. `git ls-remote --heads origin | grep 4531` — no remote branch names this handoff.
2. `git log origin/master --grep=H4531` — empty; nothing in SanskritLexicography ships it.
3. The flagged commit `5fd0a1d29` is in **Uprava**, not this repo, and names **H4534** —
   an ID that appears nowhere in this branch, its commit message, or its files. The guard
   resolved `origin/main` against the session's primary working directory (Uprava, default
   branch `main`) instead of the repo being pushed (SanskritLexicography, default branch
   `master`), then matched an unrelated handoff ID.

**Consequence:** the commit `dd6d4460c` exists only on the local branch
`h4531-batches-probe` in the worktree `SanskritLexicography-h4531-583550`. That worktree was
therefore **deliberately left in place** instead of being gc'd — removing it before the push
would leave the only copy of this work in a dangling local branch. A human ruling on the
guard (or a push from a session whose primary directory is this repo) is what lands it.

## Inspect first

1. This report, then
   [src/pilot/anthropic_batches_route_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/anthropic_batches_route_selftest.py)
   — the B-01…B-09 list is the contract in executable form.
2. `pwg_ru/h4531/run/call_reservation.json` — the pre-submit ceiling, and the burn.
3. [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md),
   newest entry — the submit failure as a launch-failure row.

_Dr. Mārcis Gasūns_
