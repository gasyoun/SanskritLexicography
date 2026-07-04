# LANG_PARITY.md — cross-language fix/feature parity ledger

_Created: 04-07-2026 · Last updated: 04-07-2026_

This repo runs the same PWG→Russian and PWG→English translation pipeline through
shared tooling (`src/pilot/gen_opt_harness2.py`, `src/pilot/translation_memory.py`,
`src/pilot/audit_window*.py`, …), parameterized by `--lang`. History shows fixes
land on one language path and quietly never reach the other — e.g. 3 gate-bug
fixes shipped 2026-07-03 (multi-layer sense over-count, German/Latin/French
misclassification guards, Sanskrit-span gloss-leak scrub) live only in the RU
audit path; `audit_window_en.py` reimplements its own gates from scratch and
never got them. A separate audit on 2026-07-04 also found `requeue_from_audit.py`
silently dropping the mandatory `--no-tm` flag on **both** paths at once.

## Policy (binding — read before closing out any fix/feature session)

1. **Same-session obligation.** Any session that fixes a bug or adds a mechanism
   on ONE language path must, before calling the work done, classify it as one
   of:
   - **SHARED** — the fix lives in lang-parameterized code and already applies
     to every language. Port it now if it doesn't.
   - **INTENTIONAL-DIVERGENCE** — the languages genuinely need different
     behavior. Write the one-line **why** in this ledger (a missing rationale
     is itself a defect, not a shortcut).
   - **GAP** — it should eventually apply everywhere but isn't ported yet.
     Record it here AND spawn a tracked follow-up (a task chip, handoff, or
     GTD row) — a GAP entry with no tracking reference is not allowed to sit
     silently.
2. **No silent single-language fixes.** Landing a fix only on RU (or only on
   EN, or only on a future 3rd language) without one of the three verdicts
   above is a process defect, not a style choice.
3. **Structure is per-language, not RU/EN-hardcoded**, so adding a 3rd
   language later is a new `languages` entry in the ledger below, not a
   doc rewrite.
4. **Mechanical enforcement.** [`src/pilot/lang_parity_check.py`](src/pilot/lang_parity_check.py)
   parses the ledger block below and is wired into
   [`window_selftest.py`](src/pilot/window_selftest.py) as
   `test_lang_parity_ledger_complete`. It fails the suite when:
   - a ledger entry has no verdict, or an `INTENTIONAL-DIVERGENCE` entry has
     no `note`, or a `GAP` entry has no `tracking` reference;
   - a file referenced by an entry has changed (sha256 drift) since the entry
     was last verified — this is a proxy for "someone touched parity-tracked
     code and didn't re-affirm parity still holds." Re-run
     `python src/pilot/lang_parity_check.py --update-hash <entry_id>` after
     confirming the change doesn't break the recorded verdict, and update
     `note`/`tracking` if it does.
   It does **not** attempt deep semantic diffing (no AST/behavior comparison)
   — it is a forcing function to make a human/session re-affirm the verdict,
   not a replacement for actually reading the diff.

## Ledger

Machine-readable block below (JSON, not YAML, to avoid an extra dependency in
`lang_parity_check.py`). Each entry:

```
id            stable slug, never reused/renumbered
mechanism     one-line human description
files         file paths this entry tracks for drift (relative to RussianTranslation/)
languages     languages this entry currently covers (["ru","en"], or the subset that's SHARED)
verdict       SHARED | INTENTIONAL-DIVERGENCE | GAP
note          required for INTENTIONAL-DIVERGENCE: the one-line why
tracking      required for GAP: task id / handoff / PR reference
verified_sha256   {file: hex} snapshot at last verification; drift trips the gate
```

```json lang_parity_ledger
[
  {
    "id": "presplit_router",
    "mechanism": "Presplit router sends over-budget dense cards straight to the fragment lane",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433"
    }
  },
  {
    "id": "selfheal_binary_split",
    "mechanism": "Selfheal + binary-split recovery, on by default",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433"
    }
  },
  {
    "id": "output_budget_90",
    "mechanism": "OUTPUT_BUDGET=90 default (calibrated 2026-07-03, PR #101)",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433"
    }
  },
  {
    "id": "translation_memory_card_and_fragment",
    "mechanism": "Content-addressed TM, card-level + fragment-level reuse",
    "files": [
      "src/pilot/translation_memory.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "lang is a first-class parameter of the TM address (sha256(lang + ...)); --lang=ru|en both get full reuse.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/translation_memory.py": "41ff5b08afd961e166ee24f38ef00aa307803d6dcc4fd4eb6ca1806a67a4a1a3"
    }
  },
  {
    "id": "cards_schema_defs_pruning",
    "mechanism": "H130 fix: CARDS_SCHEMA only carries $defs reachable from 'card', not the whole shared schema file's judge/judge_issue defs",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "_reachable_defs() walks $ref pointers regardless of lang.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433"
    }
  },
  {
    "id": "annotator_fields_optional_schema_relaxation",
    "mechanism": "Sense schema 'required' trimmed to [tag, german/english, russian/english] — the 4 annotator fields (equivalence_type/source_type/stratum/differentia) optional",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "Applies identically on both paths per the 2026-07-01 EN-schema-relaxation commit; RU keeps the same optionality, not a stricter EN-only rule.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433"
    }
  },
  {
    "id": "sonnet5_explicit_model_pin_en",
    "mechanism": "EN path pins 'claude-sonnet-5' explicitly in the generated harness's agent() calls; RU path keeps the bare 'sonnet' alias",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "en"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "The bare 'sonnet' alias resolved to Sonnet 4.6 (not 5.0) on a prior EN run — pinned explicitly there after that surprise. RU's alias was never observed to misresolve, so it was left alone rather than touching a stable production path for a problem it doesn't have. Re-evaluate if RU is ever caught on a stale alias too.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433"
    }
  },
  {
    "id": "gate_fixes_20260703_ru_only",
    "mechanism": "3 gate-bug fixes (audit_coverage.py multi-layer sense over-count; prompt_rule_audit.py German/Latin/French misclassification guards; braced_gloss_risks Sanskrit-span gloss-leak scrub) exist only in the RU audit path",
    "files": [
      "src/audit_coverage.py",
      "src/pilot/prompt_rule_audit.py",
      "src/pilot/audit_window.py",
      "src/pilot/audit_window_en.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "GAP",
    "note": "audit_window_en.py reimplements its own gates from scratch rather than importing the RU modules (its own comment: 'the RU gate is wired around Russian-specific semantic checks'), so none of the 3 July fixes reached EN. EN cards from the same PWG/PW/SCH source have the same multi-layer/addenda structure, so the same false-positive classes plausibly apply there too.",
    "tracking": "spawned task chip task_d29bb788 (2026-07-04): 'Port RU gate fixes to audit_window_en.py' — running",
    "verified_sha256": {
      "src/audit_coverage.py": "8c54aa22943140624238273b5bb6a2cbe9aceded5f8295cb84cd36bd994904c0",
      "src/pilot/prompt_rule_audit.py": "293b580cdf8866c8ae0d892dd77981e34561398e2c0142623aed1127740019b0",
      "src/pilot/audit_window.py": "2f9e418010d2ed9bc5c49be934eb95d672cae9ad3f01aa4099756dc7cf0e44a1",
      "src/pilot/audit_window_en.py": "4775368d2da38f0d6aede470d838becb6cc863de4914a785aa855baf45735fd8"
    }
  },
  {
    "id": "requeue_no_tm_enforcement",
    "mechanism": "requeue_from_audit.py must append --no-tm on a defect/all requeue so TM can't silently re-serve gate-flagged content",
    "files": [
      "src/pilot/requeue_from_audit.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "Fixed 2026-07-04 (commit 8cb84f7): the helper is lang-agnostic (takes a root, not a --lang flag; gen_opt_harness2.py resolves lang from the rootmap), so the fix applies to any language's requeue in one place. Was a both-paths gap before the fix, not an RU/EN divergence.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/requeue_from_audit.py": "3dd94b3f20084a3db1b6211e149d7347ba86ffd479424ec2fb88084090ddcf5f"
    }
  },
  {
    "id": "promotion_scripts_separate",
    "mechanism": "Promotion into the store is two separate scripts (promote_final_cards.py for RU, promote_en.py for EN) rather than one --lang-parameterized script",
    "files": [
      "src/promote_final_cards.py",
      "src/promote_en.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "The two stores (pwg_ru_translated.jsonl vs the EN store) have different schemas and provenance history (RU predates the EN pilot by months); a merged script was never worth the risk of cross-contaminating the two promotion paths for a mechanical CLI split. Revisit only if the two stores' schemas converge.",
    "tracking": "",
    "verified_sha256": {
      "src/promote_final_cards.py": "572bb45477ce4856f6caba7e813e00a146bbeeedf3ae04b471e4616dafaa8935",
      "src/promote_en.py": "7d3ce9680e304fff8ba0bcaba843945c36c6f0894441a56e8695ec58a6b5ebfe"
    }
  },
  {
    "id": "presplit_agent_count_estimator",
    "mechanism": "agent_expected_after_tm counted len(presplit) (1 per giant) instead of len(frags[k]) (true fragment-call count per giant)",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "Fixed 2026-07-04: the estimator undercounted a 150+-<ls> presplit giant as 1 agent instead of its true ~10-20 fragment calls, making the vid preflight read 13 when the real run spent 102. Computed identically for both langs (frags/presplit/batches are lang-agnostic); fix + pinning test apply to both.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433",
      "src/pilot/window_selftest.py": "c0838db18869807a5b03da8b31542a38ffa10e17adfc8ba95ea9ebc0712b8a5a"
    }
  },
  {
    "id": "no_fallback_batch_isolation",
    "mechanism": "Batching separates no-selfheal-fallback keys (split_plan() < 2 fragments, or lossy fragment mask) into their own dedicated batch(es), never mixed with fallback-having keys, so a batch-wide hard failure never takes down an unrelated card",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "Fixed 2026-07-04 after the vid run showed 10/10 null cards traced to 2 batches that hard-failed the StructuredOutput retry cap outright, with every null a no-fallback card riding along with a fallback-having card in the same batch. batch_keys is split into fallback/no-fallback lists BEFORE _group_by_budget grouping (both grouped independently, same sizer/budget), which is lang-agnostic (frags/batch_keys carry no lang branching).",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "cde5e4c2243a293a9e958f7d76deae214489f3c61d4757d6404c3b47906c2433",
      "src/pilot/window_selftest.py": "c0838db18869807a5b03da8b31542a38ffa10e17adfc8ba95ea9ebc0712b8a5a"
    }
  }
]
```

## Worked examples

**Case A — you just fixed a bug in lang-agnostic code.** (Real example,
`requeue_no_tm_enforcement` above.) You edited `requeue_from_audit.py`, which
doesn't take a `--lang` flag at all — it resolves language from the root's
own rootmap. Classify **SHARED**, add an entry with both `ru` and `en` in
`languages`, write a one-line `note` explaining *why* it's lang-agnostic (so
a future reader doesn't have to re-derive that), leave `tracking` empty, and
run `python src/pilot/lang_parity_check.py --update-hash <id>` to snapshot
the file. Run `python src/pilot/window_selftest.py` to confirm the gate
passes.

**Case B — you found a fix that landed on one language and not the other.**
(Real example, `gate_fixes_20260703_ru_only` above.) You don't fix the gap in
the same session unless it's trivial — classify **GAP**, write `note`
explaining the asymmetry (what's different about the two paths that let this
happen), and `tracking` MUST point somewhere real: a spawned task id, an
`H###` handoff, or a GTD row. `lang_parity_check.py` will refuse an empty
`tracking` field — this is the mechanism, not a suggestion.

**Case C — you touched a file a ledger entry already tracks, for an
unrelated reason.** `window_selftest.py` will fail with a drift message
naming the entry and file. Re-read that entry's `note` — if your edit didn't
touch the behavior it describes (e.g. you fixed an unrelated bug 40 lines
away), just re-snapshot: `python src/pilot/lang_parity_check.py --update-hash
<id>`. If your edit DID change that behavior (e.g. you made a SHARED
mechanism lang-specific), update the verdict and note honestly before
re-snapshotting — the drift check exists precisely to force this fork, not
to be rubber-stamped past.

**Case D — a 3rd language is proposed.** See the section below.

## When a 3rd language is proposed

Add its files/verdicts as new ledger entries (or extend `languages` arrays on
existing SHARED entries once verified) — do not restructure the JSON shape.
If the 3rd language needs its own audit script (as EN did), immediately add a
`GAP` row for every RU-only fix in the ledger above rather than discovering
the gap months later.

_Dr. Mārcis Gasūns_
