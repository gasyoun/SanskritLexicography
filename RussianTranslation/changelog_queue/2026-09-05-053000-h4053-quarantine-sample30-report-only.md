- H4053: **the missing bounded report-only sample translate path exists — "translate N
  pre-selected quarantine keys, report only, never promote" is now a runnable, offline-proven
  workflow with a frozen 30-card packet.** New
  [`src/pwg_quarantine_sample30.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_quarantine_sample30.py)
  (`freeze` / `run` / `selftest`) on the shared paid-call kernel: exact supplied key list or
  frozen packet only, immutable input hashes, isolated caller-supplied evidence dir,
  `promotable=False` campaigns, **no promote/apply code path in the module at all**. Proven
  6/6 offline against the fake provider
  ([pytest](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_h4053_quarantine_sample30.py)):
  max-call reservation strictly before provider I/O (ceiling refusal = `budget_refusal`, 0
  provider calls on the refused slot); resume without duplicate provider spend (crash-injected
  run: interrupted call with no sealed response is terminally accounted
  `interrupted_no_provider_io` and re-executes under a derived resume key in a fresh `-rN`
  campaign namespace; a call WITH a sealed response is left open for human reconciliation and
  never re-dispatched — 2+4 dispatches deliver 6 cards, each translated exactly once); per-row
  attribution (call_id, reservation, request/response SHA-256, usage, served model); store/
  mirror/queue hashed before+after and refused on drift, absent surfaces recorded as
  `guard_absent_surfaces`, never fabricated; dry run = zero dispatches, zero reservations.
  Frozen nested sample
  [`reports/H4053_quarantine_sample30_frozen.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4053_quarantine_sample30_frozen.json):
  exactly 30 distinct identities from the 01-08 200-row sample (freeze seed 20260904); all 200
  parent identities still resolve in the fresh 10,902-row quarantine — `unavailable` and
  `deterministic_substitutions` empty. Label discipline preserved in code and packet:
  10,902/11,519 is a **segmentation-change flag, NOT an observed bad-translation rate**; every
  row ships `ru_quality_verdict: unknown_not_measured`, the five review classes
  (segmentation_only / semantic_mistranslation / sanskrit_loss / apparatus / ambiguous) are
  assigned only by independent human review after actual paid generation. Runbook with exact
  dry-run, replay and separately-gated execute commands:
  [`pwg_ru/h4053/H4053_QUARANTINE_SAMPLE30_RUNBOOK.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4053/H4053_QUARANTINE_SAMPLE30_RUNBOOK.md).
  Recorded dependency: `glm-flash` still has no price card, so a dollar-bounded GLM execute
  fails closed (`cost_ceiling`) before any reservation — live execute stays blocked until real
  GLM list prices land; no Claude Code invocation from the GLM lane. Zero provider calls and
  zero store writes were made by this work; the quality verdict remains unmeasured by design.
