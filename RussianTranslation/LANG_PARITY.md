# LANG_PARITY.md — cross-language fix/feature parity ledger

_Created: 04-07-2026 · Last updated: 07-07-2026_

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
    "id": "latin_cue_masking",
    "mechanism": "classify_pct recovers the Latin/Greek cue from masked {Tn} placeholders (expand + de-tag the preceding window) so a {%...%} cognate after <ab>lat.</ab> is masked as Latin, not leaked into the prompt as untranslated German",
    "files": [
      "src/pwg_mask.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "Code review 2026-07-04: <ab>lat.</ab>/<ab>griech.</ab> cues are masked to {Tn} in mask() step 1 BEFORE classify_pct runs, so the end-anchored LATIN_CUE regex matched the placeholder, not the cue; measured 33 Latin/Greek cognate glosses across all of PWG (e.g. ignis, uncus, ansa after `lat.`) were being sent for German translation and leaked verbatim into the translator prompt. Fix expands trailing placeholders back to source and strips tags in the classify context window. Masking is stage-0 and runs before any --lang branch, so the fix is identical for RU and EN. Round-trip stays lossless. Pinned by window_selftest.test_pwg_mask_latin_cue_behind_ab_tag.",
    "tracking": "",
    "verified_sha256": {
      "src/pwg_mask.py": "2c7697808e71e26fca3b9501f8effb68f9f3b2ad8d8880dcf78e6328ee659e9a",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18"
    }
  },
  {
    "id": "sense_presplit_trigger",
    "mechanism": "Second, orthogonal presplit trigger: a card whose deterministic fragment count (== sense-objects the model must emit) exceeds SENSE_PRESPLIT_BUDGET (20) is routed straight to the fragment lane, catching SENSE-dense cards the citation metric (1+<ls>) is blind to",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H155 (2026-07-04): tyaj~~h0_zz_pw (a PW addenda card compressing a whole root article — base verb + Caus/Desid + every prefix combo) packs 35 senses into 11 <ls>, so 1+<ls>=12 ranked it as trivial while its real output surface was the heaviest of the root; it deterministically blew the whole-card StructuredOutput retry cap and stalled ~7 min retrying the identical call. The frag-count trigger is computed from split_plan() length (lang-agnostic; no RU/EN branching) and applies whenever SELFHEAL is on, independent of the citation trigger and of byte/citation batching mode — so it protects both language paths identically. Validated live: the [sam, zz_pw] pair that stalled now returns ok:2/null:0 with zz_pw healed complete via 4 fragment groups.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "wall_clock_kill_gate",
    "mechanism": "Every schema-bearing agent() call is raced against a setTimeout budget scaled to its skeleton-byte output volume (KILL_FACTOR x (BASE + SLOPE x skelBytes)); a call that overruns is abandoned (KillTimeout) and its cards routed to the fragment lane, instead of waiting out the full StructuredOutput retry cap",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H155 follow-up (2026-07-04): the runtime BACKSTOP for whole-card StructuredOutput stalls whose driver isn't yet a structural presplit trigger (gloss volume, masked-token count, multi-layer nesting, novel shapes). Entirely lang-agnostic — the budget keys on masked-skeleton bytes (INPUTS[k].skeleton.length) and setTimeout, no RU/EN branching; both paths get the same gate. Budget calibrated from a tyaj --no-tm timing benchmark (skeleton bytes are the best single time predictor since output ~= 2x skeleton). setTimeout is a relative timer (Date.now() is banned); AbortController is unavailable so a killed call keeps running in the background until its own cap, but the harness stops blocking. Default ON; --no-kill / --kill-factor=N tune it. See FAILURE_MODES_AND_KILL_GATE_2026-07-04.md.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "no_fallback_single_kill_budget_and_nominal_key_echo",
    "mechanism": "H220 no-PWG throughput: (A) a SINGLE card with no selfheal fallback (FRAGS[k] empty) gets the CEIL kill budget via killBudgetForCur(cur) instead of the byte-scaled one — the kill gate has no smaller lane to route it to, so an early kill is pure loss; (B) nominal/no-PWG windows tolerate the model echoing the SLP1 headword (nominal_keymap[stem]) instead of the mangled sub-card stem, re-keying the card to the stem when the SLP1 maps to exactly one pending stem; (C) selfHeal's no-fallback branch preserves a specific upstream failure reason instead of overwriting it with 'no-selfheal-fallback'",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H220 (2026-07-06, Opus 4.8 claude-opus-4-8): root-caused the no-PWG lane's ~36% single-card yield to the wall-clock kill gate abandoning valid-but-slow single supplement cards. All three parts are entirely lang-agnostic — (A) keys on FRAGS emptiness + skeleton bytes + KILL_CEIL_MS (no RU/EN branch), (B) keys on META.nominal + nominal_keymap which both RU and EN builds emit identically, (C) is a FAIL[k] message-precedence guard. PWG root windows (nominal=False) keep strict key matching: the tolerance is gated on META.nominal so it is inert there (test_generated_harness_strict_key_matching still green). Pinned by test_no_fallback_single_gets_ceil_kill_budget, test_nominal_key_echo_tolerance_scoped, test_selfheal_no_fallback_preserves_upstream_reason. Extends wall_clock_kill_gate (the kill gate stays for multi-card/splittable batches).",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18"
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
      "src/pilot/translation_memory.py": "901ffd21e7db7e0ea6d0433c342166dab7caa5e1abe43ad04745a7a7f99b198a"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18"
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
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "RESOLVED 2026-07-04 (was GAP, task_d29bb788): audited audit_window_en.py against all 3 fixes. (1) multi-layer over-count is N/A -- EN has no analogous raw-marker-vs-card-sense coverage check to carry the bug. (2) the Sanskrit-span leak is already safe -- audit_window_en.py's prose() already scrubs {#..#} spans before residue matching, unlike RU's pre-fix braced_gloss_risks. (3) a REAL EN analogue existed in DE-RESIDUE: 'des' is both a German article and a French partitive article, and gen_fidelity_judge_en.py's own prompt preserves French/Latin literals verbatim -- fixed by extracting LATIN_WORDS/FRENCH_WORDS into a new shared src/pilot/foreign_literal_guards.py imported by both prompt_rule_audit.py and audit_window_en.py, with a French-context guard on the ambiguous 'des' hit. Pinned by test_en_de_residue_french_guard in window_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/audit_coverage.py": "d3e1966f0ec4cf914f85e3fb5d8336c9f2fc19662717f8300e2d4cab041f3d3f",
      "src/pilot/prompt_rule_audit.py": "d2c578eb62a1919c5c22c0726940df952dee7ead0791bf61d1a1bc7c83f26fdf",
      "src/pilot/audit_window.py": "4623e2f271a6d68cf2c76c0e144c3110bdd01a0526d55eb1804175cdf47059ef",
      "src/pilot/audit_window_en.py": "850e51292b6885dc7786d92164b880118581fe67d26b0da3bacc93793c09d4d2"
    }
  },
  {
    "id": "defect_fragment_denylist_h304",
    "mechanism": "audit emits requeue.defect.fshas.txt (the defect cards' frag_prov content addresses); requeue_from_audit appends them to the TM denylist so the fragment sidecar can never re-serve a gate-flagged fragment (build_frags harvests wf_output BEFORE gates run)",
    "files": [
      "src/pilot/audit_window.py",
      "src/pilot/window_reports.py",
      "src/pilot/requeue_from_audit.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "GAP",
    "note": "The denylist append and load_frag_tm filtering are lang-agnostic (fsha encodes lang; requeue_from_audit takes --lang), but the fshas EMITTER lives only in the RU auditor: audit_window_en.py reimplements its gates and does not compute requeue_defect_fshas or write the file, so an EN defect requeue does not auto-denylist its fragments.",
    "tracking": "Uprava/handoffs/H304-Fable_RussianTranslation_coordinator-driver-remake_07.07.26.md (EN-emitter port is the recorded follow-up)",
    "verified_sha256": {
      "src/pilot/audit_window.py": "4623e2f271a6d68cf2c76c0e144c3110bdd01a0526d55eb1804175cdf47059ef",
      "src/pilot/window_reports.py": "f2090d359ff49e798f474b26bb387f5a7309308442b4cfca01a11915d7c9192e",
      "src/pilot/requeue_from_audit.py": "2796a6b00232cb7a55e177e999a964633ea90026ddda754eee8f6b3922be0878"
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
      "src/pilot/requeue_from_audit.py": "2796a6b00232cb7a55e177e999a964633ea90026ddda754eee8f6b3922be0878"
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
      "src/promote_final_cards.py": "863b8e1a5ce294233dea1346dd3e139bac8c3f4d9b0a35f00102196f1b63369d",
      "src/promote_en.py": "84b79476e9a82df2e6dc08b3be29a3b798eef04fce6416155afb3dd0e9fac81b"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "en_dup_hard_gate_20260704",
    "mechanism": "audit_window_en.py's DUP check (two senses in one record share identical english) is promoted from a soft, >=3-content-word-gated SAME-GLOSS signal to a real HARD gate that fires regardless of gloss length, matching the docstring's advertised --strict failure set",
    "files": [
      "src/pilot/audit_window_en.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H169 (2026-07-04 review, 'broken validators'): the advertised HARD DUP gate was never emitted -- the only within-record duplicate signal was soft SAME-GLOSS, gated on >=3 content words, so a short duplicate ('to go'/'to go') produced zero flags and --strict passed. Classified GAP-being-closed rather than INTENTIONAL-DIVERGENCE: RU's within-record duplicate protection is the cross-part audit_sense_dupes.py gate (already SHARED, see gate_fixes_20260703_ru_only/PR #135) plus the soft, all-senses-only identical_russian_glosses risk in prompt_rule_audit.py (MEDIUM, not high-confidence) -- neither is a pairwise HARD gate. EN now closes that with a real HARD pairwise DUP check; RU getting an equivalent pairwise HARD gate (rather than its current all-or-nothing soft signal) is left as a natural follow-up, not blocking this fix. Pinned by test_en_gate_dup_has_teeth in window_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/audit_window_en.py": "850e51292b6885dc7786d92164b880118581fe67d26b0da3bacc93793c09d4d2",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "pipeline_version_stamp_en_gap",
    "mechanism": "promote_final_cards.py (RU) stamps provenance.pipeline (semver of the promotion tooling, orthogonal to the Claude model version) on every promoted row via pipeline_version.stamp(); promote_en.py (EN) now stamps the same pipeline block into en_provenance.pipeline",
    "files": [
      "src/promote_final_cards.py",
      "src/promote_en.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "RESOLVED same day (2026-07-04): PR #140 (feat(provenance): pipeline versioning) added pipeline_version stamping only to promote_final_cards.py; found as a GAP while re-affirming H169's parity re-hash, closed immediately. promote_en.py now calls `pipeline_version.stamp(model_version=gen_model_version)` inside `en_index()`'s per-subcard provenance block, stored as `en_provenance.pipeline` (mirrors RU's `provenance.pipeline`; a distinct field since EN attaches onto an existing RU row rather than owning it). Pinned by an added assertion in `promote_en.selftest()`.",
    "tracking": "",
    "verified_sha256": {
      "src/promote_final_cards.py": "863b8e1a5ce294233dea1346dd3e139bac8c3f4d9b0a35f00102196f1b63369d",
      "src/promote_en.py": "84b79476e9a82df2e6dc08b3be29a3b798eef04fce6416155afb3dd0e9fac81b"
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
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "layer_field_on_promoted_rows",
    "mechanism": "promote_final_cards.py writes an explicit `layer` field (pwg/pw/sch/pwkvn/nws, via dict_merge.layer_of parsing the sub-card key) on every promoted store row, so the deferred addenda re-glue/typology (H180) can group by layer without re-parsing keys",
    "files": [
      "src/promote_final_cards.py",
      "src/dict_merge.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H179 Step 1.1. The layer is derived purely from the sub-card KEY structure, which is identical for RU and EN. promote_en.py ATTACHES english onto the RU-owned row and leaves it otherwise untouched, so EN inherits `layer` for free — no EN-specific code needed. layer_of() pinned by dict_merge.py selftest + a promote_final_cards.selftest assertion.",
    "tracking": "",
    "verified_sha256": {
      "src/promote_final_cards.py": "863b8e1a5ce294233dea1346dd3e139bac8c3f4d9b0a35f00102196f1b63369d",
      "src/dict_merge.py": "0266e11980e3b8b12d0699665b2051b9f7b8b16ed89d5810adfe5a458e880eea"
    }
  },
  {
    "id": "nominal_meta_keymap",
    "mechanism": "gen_opt_harness2.py emits `nominal: true` + `nominal_keymap` (safe-name file stem -> true SLP1 headword) in the workflow meta for --nominal runs, so promote_final_cards recovers the real headword instead of mis-keying every card to the window LABEL passed as meta.root",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/promote_final_cards.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H179 Step 3 pre-run fix. Before this, the nominal promote path (meta.get('nominal') + nominal_keymap) existed in promote_final_cards but the harness never emitted those fields, so a --nominal run's cards would all key to the label (e.g. pril10_w1) instead of kAla/rasa/rUpa. The keymap is built from each card's portrait key1 (_slp1_lex_for_key), which is lang-independent — the identical meta is emitted for RU and EN nominal runs. Pinned by a promote_final_cards.selftest nominal-keying assertion.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/promote_final_cards.py": "863b8e1a5ce294233dea1346dd3e139bac8c3f4d9b0a35f00102196f1b63369d"
    }
  },
  {
    "id": "presplit_lane_amortization_and_budget_guards_h189",
    "mechanism": "Presplit-PRIMARY cards are grouped at PRESPLIT_GROUP_CITE_BUDGET(60)/PRESPLIT_GROUP_SENSE_CAP(18) instead of the conservative SELFHEAL_GROUP_BUDGET(12), amortizing the ~27k framework across many fragments per agent() call; the wall-clock kill gate is recalibrated (floor 120s->45s, ceil 480s->180s) per MG's >60s-suspicious/>3min-unacceptable rule; a window-level budget kill-switch aborts+requeues once agent() calls exceed MAX_AGENTS=ceil(expected*3)+10); the generator warns + suggests a key-disjoint split when the harness exceeds MAX_HARNESS_BYTES(480k); perf_preflight adds a per-card / per-window cost gate that flags a window dominated by expensive cards",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/perf_preflight.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H189 (2026-07-05): fixes the pril10_w1 nominal-window cost blow-up (230 agents / 42.3M tokens / ~$80 / ~3 of 8 cards). Every mechanism keys on lang-agnostic signals — citation/sense counts, masked-skeleton bytes, agent-call count, harness bytes, token/$ estimates — with NO RU/EN branching, so RU and EN get identical behaviour; the presplit lane already ran both languages through the same grouping. Also guards _slp1_lex_for_key against an empty-list portrait ([]) crashing the nominal_keymap emission (the real tyaj~~h0_zz_pw / addenda shape). See POSTMORTEM_pril10_w1.md + H189.",
    "tracking": "H189",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "700665baa30b550c59ca9f1dfc00adc2569bb3d5b91fe1eb0bddb922e7742a18",
      "src/pilot/perf_preflight.py": "a73a536d6f24e398faadd5507520e106a5d96c94c28e310c0e30366397b7d174",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "subprocess_and_bom_hardening_h316",
    "mechanism": "pwg_mask.records() reads utf-8-sig (BOM on the PWG source no longer drops the FIRST record) and warns loudly on a truncated final record instead of silently dropping it; every gate/driver subprocess.run that captures child output passes encoding='utf-8' (Windows cp1252 pitfall); save_and_audit/audit_window/autosplit_requeue shell-outs carry timeouts so a wedged child cannot hang the driver",
    "files": [
      "src/pwg_mask.py",
      "src/make_edition_cut.py",
      "src/preflight_remaining_gates.py",
      "src/release_readiness.py",
      "save_and_audit.py",
      "src/pilot/audit_window.py",
      "src/pilot/autosplit_requeue.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H316 code-hardening pass (2026-07-07). All fixes sit below the --lang branch: stage-0 masking (records feeds both RU and EN lanes), gate shell-out plumbing, and hang guards are language-agnostic by construction. Pinned by test_pwg_mask_bom_source_keeps_first_record, test_pwg_mask_truncated_final_record_not_silent, and the static wiring pin test_subprocess_gate_calls_hardened.",
    "tracking": "",
    "verified_sha256": {
      "src/pwg_mask.py": "2c7697808e71e26fca3b9501f8effb68f9f3b2ad8d8880dcf78e6328ee659e9a",
      "src/make_edition_cut.py": "5a24d8c96611f50f008689609f8140ef47b02731524dbc255438426b36d306fd",
      "src/preflight_remaining_gates.py": "00386c837b97986c9702abfceed9c29534736c3df3063af202ddfaae6b078b8f",
      "src/release_readiness.py": "db38a870bbc8b5dbe694e706e4a7b9089ba41211a3881ad9a1bd4eb02950c8a9",
      "save_and_audit.py": "14409a15772df0c07e1337d795112d9f99f60388b003df241c5b1ccaf03e4e97",
      "src/pilot/audit_window.py": "4623e2f271a6d68cf2c76c0e144c3110bdd01a0526d55eb1804175cdf47059ef",
      "src/pilot/autosplit_requeue.py": "17ac6103dbdb6743163bb312531d71deb4a12da35c777e3676baf5d95afe1792",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "frag_tm_fidelity_gate_h321",
    "mechanism": "build_frags refuses a corrupt/blanked frag_prov (frag_senses_sane) instead of first-seen-wins caching it, load_frag_tm applies the same fidelity filter at serve, and a later GOOD harvest of an fsha whose only cached rows are corrupt can override them",
    "files": [
      "src/pilot/translation_memory.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H321 (code review 2026-07-04 item #3b): the fragment sidecar is content-addressed on the fragment SOURCE and was harvested append-only first-seen-wins with NO fidelity check, so a hand-edited/corrupt wf_output*.json (blanked or malformed senses) permanently poisoned reuse and a later good harvest of the same fsha could never override it. frag_senses_sane(senses, lang) keys on the CARD-shaped translation field ('russian'/'english') and is applied at BOTH harvest (never cache garbage; a cached-corrupt fsha maps to False so a good row overrides it) and serve (load_frag_tm drops any corrupt historical row). Entirely lang-agnostic — lang is a first-class parameter of frag_address/frag_senses_sane/load_frag_tm/build_frags, no RU/EN branch. Pinned by test_frag_tm_fidelity_gate_and_override. Extends translation_memory_card_and_fragment.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/translation_memory.py": "901ffd21e7db7e0ea6d0433c342166dab7caa5e1abe43ad04745a7a7f99b198a",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "corpus_gate_evidence_markers_fl7_h321",
    "mechanism": "corpus_gate.build_card marks evidence_status (evidence_unavailable when NO independent Sanskrit-Russian authority is loaded) and corpus_status (db_absent / db_error / skipped_short_term / ok), so a missing source or a DB failure is no longer indistinguishable from a genuinely uncovered headword degrading silently to the LLM verdict",
    "files": [
      "src/corpus_gate.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "H321 (architecture audit FL7 / code review 2026-07-04 item #4). corpus_gate.py is the RU-only stage-4 correctness gate: it joins a PWG headword to the independent Sanskrit->RUSSIAN dictionaries (Кочергина/Кнауэр/Фриш/Смирнов/Коссович) and the SamudraManthanam RU-aligned verse corpus. The EN pilot has no analogous corpus gate (no Sanskrit-English authority set is wired here), so this fix is inherently Russian-only — an INTENTIONAL-DIVERGENCE, not a GAP to port. The marker mechanism (SOURCES_PRESENT / evidence_status() / corpus_examples_with_status) would generalize if an EN correctness gate is ever built; revisit then. Pinned by test_corpus_gate_evidence_and_db_markers.",
    "tracking": "",
    "verified_sha256": {
      "src/corpus_gate.py": "2257f04cdca96b2aea51cd6d097358c43109977e1847d39ff59476cc5cf50863",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "ls_resolver_rv_av_anchor_h321",
    "mechanism": "ls_resolver Ṛgveda/Atharva hymn-URL disambiguation is anchored on the leading citation abbreviation (_is_rv_prefix: startswith ṛv/rv) instead of a bare substring containment that mis-routed any citation merely containing rv/ṛ (parv., gṛ., kṛ.) to the RV scans; the two pattern-engine swallowed-exception sites now surface via _warn_swallowed",
    "files": [
      "src/ls_resolver.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H321 (code review 2026-07-04 item #5). ls_resolver resolves an <ls> citation to a scan/hymns URL independent of the translation language (it keys on the citation abbreviation + numbers, never on RU/EN prose), so both language editions' link-targets share it. The anchored _is_rv_prefix and the _warn_swallowed exception surfacing are pure link-resolution correctness, no lang branch. Pinned by test_ls_resolver_rv_av_anchored.",
    "tracking": "",
    "verified_sha256": {
      "src/ls_resolver.py": "583d0251cfd68e74b3f56b639dd95110477e531e13aa0cc2a67c6d5a8b667480",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "government_census",
    "mechanism": "Deterministic census of case-government markers (Rektion) over the raw csl-orig PWG source: parenthesized case groups ((<ab>loc.</ab>), (<ab>loc.</ab> und <ab>gen.</ab>)) and prose mit-phrases, counted per entry/sense-unit with POS breakdown (H335 W3a)",
    "files": [
      "src/government_census.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H335 (08-07-2026). The census reads raw pwg.txt below any --lang branch and never touches RU/EN translation code; the government-marker regexes operate on the German source markup shared by both editions. Read-only over the source; selftest-gated.",
    "tracking": "",
    "verified_sha256": {
      "src/government_census.py": "501c21da829cf32555fa086274f5cd01578b7d8f88cd76f3402b5c16b124fd9b"
    }
  },
  {
    "id": "promotion_claim_file_h336",
    "mechanism": "O_EXCL claim file (promote_lock.PromoteClaim) guarding the promotion read-guard-write window in promote_final_cards.py --merge and promote_en.py, plus a UNIQUE timestamped .premerge.<UTC>.bak / .preEN.<UTC>.bak backup name replacing the old fixed name (H335 W1 / H336 H-1)",
    "files": [
      "src/promote_lock.py",
      "src/promote_final_cards.py",
      "src/promote_en.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H336 (08-07-2026). The claim wraps whichever store path --store points at, and both promote_final_cards.py (RU bridge) and promote_en.py (EN attach) import the identical PromoteClaim class with identical TTL-only (no PID-liveness) staleness semantics and the same --steal-lock override — there is exactly one implementation, not a per-language reimplementation. Pinned by test_promote_claim_contention (pins promote_lock.py's own --selftest into the aggregate suite).",
    "tracking": "",
    "verified_sha256": {
      "src/promote_lock.py": "dca26a006a32ba4a9eeb98453fa059585ccb8504ada8423f5e22d3fe1b25310f",
      "src/promote_final_cards.py": "863b8e1a5ce294233dea1346dd3e139bac8c3f4d9b0a35f00102196f1b63369d",
      "src/promote_en.py": "84b79476e9a82df2e6dc08b3be29a3b798eef04fce6416155afb3dd0e9fac81b",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "window_tag_output_namespacing_h336",
    "mechanism": "audit_window.py --window-tag routes window_status/report/requeue/judge-sample artifacts to src/pilot/output/<tag>/ instead of the flat singletons (default tag = --root when the flag is bare); requeue_from_audit.py --window-tag and root_window_status.py --window-tag read from the same tag dir. Untagged invocation is unchanged (writes the flat singletons) — H335 W1 / H336 H-2",
    "files": [
      "src/pilot/audit_window.py",
      "src/pilot/requeue_from_audit.py",
      "src/pilot/root_window_status.py",
      "src/pilot/window_reports.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H336 (08-07-2026). window_reports.write_reports/write_window_status already took an out_dir parameter (pre-existing --out-dir escape hatch); --window-tag is a thin, lang-agnostic sugar layer over that same parameter computed once in audit_window.py and threaded through unchanged to requeue_from_audit.py/root_window_status.py. Neither RU nor EN branch differently. Pinned by test_audit_window_tag_routing.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/audit_window.py": "4623e2f271a6d68cf2c76c0e144c3110bdd01a0526d55eb1804175cdf47059ef",
      "src/pilot/requeue_from_audit.py": "2796a6b00232cb7a55e177e999a964633ea90026ddda754eee8f6b3922be0878",
      "src/pilot/root_window_status.py": "ab13516c5ffa824ddc45b2dc0d482c09f06de57d5963dcc31d73ecc638a116f3",
      "src/pilot/window_reports.py": "f2090d359ff49e798f474b26bb387f5a7309308442b4cfca01a11915d7c9192e",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "jsonl_append_hygiene_h336",
    "mechanism": "window_common.append_jsonl_line() writes ONE os.write() of a fully-encoded JSONL line per row (O_APPEND fd) instead of a buffered text-mode 'a' handle, used by every append-only sidecar (window_ledger, TM denylist, TM fragment sidecar, layer_version_log, auto_failures); translation_memory.load_denylist now WARNS loudly on a torn/undecodable line instead of silently dropping it (H335 W1 / H336 H-3)",
    "files": [
      "src/pilot/window_common.py",
      "src/pilot/window_reports.py",
      "src/pilot/requeue_from_audit.py",
      "src/pilot/layer_versions.py",
      "src/pilot/failure_capture.py",
      "src/pilot/translation_memory.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H336 (08-07-2026). append_jsonl_line is a single shared primitive (window_common.py) used identically by every JSONL append site regardless of --lang; the TM denylist stores 'ru'/'en' addresses in the same file with no per-language code path. Pinned by test_denylist_torn_line_warns.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/window_common.py": "0a26bac1b0aa1ca63d8af5fe0b3f4431c97df371f5fd20a0f400b6900f86d1ac",
      "src/pilot/window_reports.py": "f2090d359ff49e798f474b26bb387f5a7309308442b4cfca01a11915d7c9192e",
      "src/pilot/requeue_from_audit.py": "2796a6b00232cb7a55e177e999a964633ea90026ddda754eee8f6b3922be0878",
      "src/pilot/layer_versions.py": "42e44f32db2628e3137522f5d15827cf0641b642bdacfdb76be04cdd41eaefba",
      "src/pilot/failure_capture.py": "c0ca940b54fc326e0a0b67320758c81aa5a48dd29247250996c38a85a7786e4d",
      "src/pilot/translation_memory.py": "901ffd21e7db7e0ea6d0433c342166dab7caa5e1abe43ad04745a7a7f99b198a",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "evidence_retrofit_annotate_h337",
    "mechanism": "annotate_evidence.py retrofits per-sense evidence provenance (evidence[] + lemma evidence_summary) onto the store by re-assembling corpus_gate's 7 evidence lanes and classifying each Russian authority's relation (provides/supports/contradicts/silent) to each sense; annotation_report.py queries it ('which senses did Grintser support?')",
    "files": [
      "src/annotate_evidence.py",
      "src/annotation_report.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "H337 (08-07-2026). The evidence lanes are inherently Russian: corpus_gate joins a PWG headword to the independent Sanskrit->RUSSIAN dictionaries (Кочергина/Кнауэр/Фриш/Смирнов/Коссович), the Гринцер specialist glossaries, and the SamudraManthanam RU-aligned corpus; the relation classifier tokenises Russian glosses. The EN pilot has no Sanskrit-English authority set wired here, so evidence retrofit is inherently RU-only — the same divergence already recorded for corpus_gate_evidence_markers_fl7_h321. annotation_report.py is a lang-neutral query CLI but reads the RU store; it would generalise if an EN correctness gate is ever built. Pinned by test_annotate_evidence_relation_semantics (annotate_evidence.py's own pure-function --selftest, no gate-source file IO so it runs in CI).",
    "tracking": "",
    "verified_sha256": {
      "src/annotate_evidence.py": "4f3e3e4adb7b251de0e03ac407bab5c809f9d55275b84569baa8021f5bc6b491",
      "src/annotation_report.py": "de28ac29360ebc960f00dc3aebffb6255e8b428ed202f5fed2ad2528642b46fe",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
    }
  },
  {
    "id": "coordinator_claim_expiry_and_atomic_jsonl",
    "mechanism": "coordinator.py enforces TTL only for pre-prepare claimed leases so abandoned claims release the global translation cap, while prepared harness leases remain durable operator artifacts; coordinator registry/daily JSONL appends use the shared append_jsonl_line() single-write primitive",
    "files": [
      "src/pilot/coordinator.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "09-07-2026 orchestration audit. The coordinator governs Workflow leases before language-specific promotion/audit branches; lease target/state handling and JSONL append hygiene are lang-agnostic. The expiry guard deliberately does NOT expire prepared harnesses, because H151-style prepared artifacts can wait days for Workflow capture. Pinned by test_coordinator_expired_leases_release_cap.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/coordinator.py": "5e257d130318be4e903bb55444d70c88544af8725c115253235e5daed716ec51",
      "src/pilot/window_selftest.py": "cf021ca299425ee5c936f4ea7e9e94551ae5f55824dc46f349008d4cdbad3f75"
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
You don't fix the gap in the same session unless it's trivial — classify
**GAP**, write `note` explaining the asymmetry (what's different about the
two paths that let this happen), and `tracking` MUST point somewhere real: a
spawned task id, an `H###` handoff, or a GTD row. `lang_parity_check.py` will
refuse an empty `tracking` field — this is the mechanism, not a suggestion.
(`gate_fixes_20260703_ru_only` was this case originally, GAP + `tracking:
task_d29bb788`; that task closed the gap the same day by porting the one
sub-fix that actually applied to EN into a shared helper, so the entry was
re-verdicted to **SHARED** and `tracking` cleared — see its current `note`
for the worked resolution, including the two sub-fixes that turned out to be
non-issues on EN and shouldn't be "ported" at all.)

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
