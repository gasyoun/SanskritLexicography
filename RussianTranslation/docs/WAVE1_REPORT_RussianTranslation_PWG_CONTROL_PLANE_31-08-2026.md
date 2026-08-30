# WAVE-1 CLOSE REPORT — PWG translation control-plane strangler

_Created: 31-08-2026 · Last updated: 31-08-2026_

Parent: [PLAN — PWG translation control-plane strangler](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_PWG_CONTROL_PLANE_STRANGLER_2026H2.md)
· Handoff: [H3714](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3714-Codex_SanskritLexicography_pwg-control-plane-strangler-wave1_30.08.26.md)
· Executed by Opus 4.8 (`claude-opus-4-8`).

## Verdict: **PARTIAL**

Per [VERIFICATION § Cutover verdict format](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_PWG_CONTROL_PLANE.md),
`PARTIAL` preserves the landed offline infrastructure and **authorizes no
legacy-writer shutdown**. Every offline gate is green; the two things `GO`
additionally requires — the bounded provider canary and an independent
reviewer's receipt — were not obtainable in this unattended run and are
reported as unverified rather than assumed.

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| V1 | One request ⇒ exactly one reserved and finalized `Call` | ✅ | [`test_pwg_pipeline_repository.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_pwg_pipeline_repository.py) — success, empty, malformed, timeout, exception, unavailable |
| V2 | Ceilings refuse **before** provider I/O | ✅ | fake-adapter call counter stays at 0 for both the call and the cost ceiling |
| V3 | Route/model/usage sealed and route-distinguishable | ✅ | `providers.normalized_usage` + sealed request/response/result artifacts; `cost_basis` names reported vs derived |
| V4 | Transitions transactional and restartable | ✅ | compare-and-set + `job_transitions` audit; [`test_pwg_pipeline_faults.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_pwg_pipeline_faults.py) |
| V5 | Audit makes no filesystem change | ✅ | before/after `tree_digest` equality around every audit |
| V6 | Refill/migration lose no row across interruption | ✅ | 5 promotion boundaries + a hard subprocess kill, each recovered idempotently |
| V7 | Recursive validator scans every nested payload | ✅ | middle-row `{Tn}` at depth 3 located as `$[2].nested.deep[0].note`; `jsonschema`-absent fails closed |
| V8 | The existing placeholder rows are fenced, not rewritten | ✅ | **79 rows / 609 occurrences** reproduced exactly; canonical digest `b9ad8e9f…` unchanged |
| V9 | Four replays, zero unexplained mismatches | ✅ | [`replay --matrix … --exact`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/fixtures/pwg_pipeline) |
| V10 | Claude behavior unchanged | ✅ | window 219/219, headless, bounded-staged-run, orchestrator, promotion-journal, promote-final-cards, lang-parity all green; full `tests/` 358 passed |
| V11 | Legacy writers route through the facade or refuse | ✅ | [`compat.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/compat.py) maps every live verb; the old writer stays **enabled** by design |
| V12 | Independent review of money/store paths | ⚠️ **unverified** | packet sealed and hash-bound; **no receipt** — an unattended agent cannot be its own independent reviewer, and `review.sign` refuses self-signing |
| V13 | Live canaries obey the fence | ⚠️ **not run** | `XAI_API_KEY` and `DEEPSEEK_API_KEY` are both unset on this host; every fence property is nevertheless proved offline |

## What landed

[`RussianTranslation/src/pwg_pipeline/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pwg_pipeline) —
standard library only, no ORM, no workflow framework:

1. [`model.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/model.py) — `Campaign → Job → Attempt → Call → Artifact → Verdict → Promotion` and the legal transition graph.
2. [`schema/001_initial.sql`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/schema/001_initial.sql) + [`repository.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/repository.py) — WAL SQLite, `BEGIN IMMEDIATE`, compare-and-set, non-negative accounting, idempotency keys.
3. [`evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/evidence.py) — canonical UTF-8/LF sealing, atomic replace, byte-different collision refusal.
4. [`validation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/validation.py) — recursive JSONPath-located validation, fail-closed schema mode.
5. [`kernel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/kernel.py) + [`providers.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/providers.py) — one paid-call sequence; xAI, DeepSeek, and a read-only Claude shadow adapter.
6. [`audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/audit.py) / [`apply.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/apply.py) — pure verdicts, explicit intents.
7. [`promotion.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/promotion.py) — journaled, fenced, idempotently recoverable; scratch stores only.
8. [`import_legacy.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/import_legacy.py), [`replay.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/replay.py), [`review.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/review.py), [`compat.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/compat.py), [`cli.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/cli.py), [`faults.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/faults.py).

129 new tests across eight files; the whole `RussianTranslation/tests/` suite is
**358 passed**. The offline gate is wired into
[`ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)
as *PWG control-plane Wave-1 offline gate (H3714)*.

## Reproduce

```powershell
Set-Location RussianTranslation
$env:PYTHONPATH = "src"
python -m pytest tests/test_pwg_pipeline_*.py -q
python -m pwg_pipeline replay --matrix tests/fixtures/pwg_pipeline --exact
python -m pwg_pipeline validate --canonical release/pwg_tm_canonical/canonical.v1.jsonl --recursive --read-only --fence-existing
python -m pwg_pipeline.wave1_evidence --commit (git rev-parse HEAD)
```

The evidence bundle lands in
[`RussianTranslation/docs/evidence/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/docs/evidence):
`H3714_review_packet.json` (hash-bound), `H3714_cutover_verdict.json`, and
`H3714_validation_fence.json`.

## The 79 fenced rows

The recursive validator reproduces the audit finding **exactly**: 2,392 rows,
**79 defective, 609 `{Tn}` occurrences**, all `unresolved_placeholder`, canonical
SHA-256 `b9ad8e9ff99d561de72029e9af40664e9cf7bfabe1575faf7858d88b757bbe82`
before and after the pass. The rows are reported and fenced by identity; **not
one byte was rewritten** — repair is deliberately out of Wave-1 scope (R4.3,
fence item 1).

## What is NOT done, and why

1. **No provider canary.** Neither `XAI_API_KEY` nor `DEEPSEEK_API_KEY` exists
   on this host. Per the Wave-1 stop conditions an unavailable optional provider
   halts only its own track, and its unused call is never released to the other
   provider — so the run stopped both tracks and spent **USD 0.00** across
   **0 provider calls**. Every fence property (`max_calls=2`, USD 4,
   no retry, non-promotable, no canonical-path access, one campaign per provider)
   is nevertheless proved offline in
   [`test_pwg_pipeline_canary.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_pwg_pipeline_canary.py).
2. **No independent reviewer receipt.** V12 requires a reviewer other than the
   implementing agent; `review.sign` refuses a self-signed receipt by design, so
   this cannot be manufactured. The packet is sealed and ready to sign.
3. **No legacy-writer shutdown.** R3.5 requires two canaries plus a
   production-equivalent replay plus two exact shim-parity runs first;
   `compat.writer_disabled()` returns `False` and a test pins that.
4. **No canonical mutation, prompt change, or publication.** The Wave-1 fence
   held throughout.

## Rollback

Wave 1 adds a package, tests and a CI step and changes no production writer, so
**reverting the merge commit is a complete rollback**. Campaign databases and
evidence directories are disposable. An interrupted scratch promotion is
reconciled with `PromotionService.reconcile(<promotion_id>)` or abandoned by
deleting its journal and scratch store. There is no data-level rollback to
perform because no canonical byte changed.

_Dr. Mārcis Gasūns_
