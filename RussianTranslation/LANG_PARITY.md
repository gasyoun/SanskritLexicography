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
      "src/pwg_mask.py": "5bbb029b2dc287f52d4efd4f9f44ff4a12952a15984554568afa645eec2804bd",
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94",
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94",
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94"
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
      "src/pilot/translation_memory.py": "11d32e2cdb5ca2faeb18a6d8ac67c30e2927c073baf493c2a963150d12b55d60"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94"
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
      "src/pilot/prompt_rule_audit.py": "bbd3fe10ff72b9d58e6d763069352129df8c246d4cb18ae41520ddcf6fee7525",
      "src/pilot/audit_window.py": "8ab1aee803e6102fa4125a22006e929d254422854e5f1983030d6a3b21dcbd89",
      "src/pilot/audit_window_en.py": "850e51292b6885dc7786d92164b880118581fe67d26b0da3bacc93793c09d4d2"
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
      "src/pilot/requeue_from_audit.py": "a121e99b5e4a5f2a205e094de0a49e1b86674a4ceabf382a67d89b70f875f2cf"
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
      "src/promote_final_cards.py": "abb57e9a41e8969346e854fd4d4682b97abdabf203a102b6a5d11fa657eaaa22",
      "src/promote_en.py": "7c9b24b12371937735efb7cb3eb7f9b51238614d34b357621b1e8f1715c21420"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94",
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
      "src/promote_final_cards.py": "abb57e9a41e8969346e854fd4d4682b97abdabf203a102b6a5d11fa657eaaa22",
      "src/promote_en.py": "7c9b24b12371937735efb7cb3eb7f9b51238614d34b357621b1e8f1715c21420"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94",
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
      "src/promote_final_cards.py": "abb57e9a41e8969346e854fd4d4682b97abdabf203a102b6a5d11fa657eaaa22",
      "src/dict_merge.py": "81cbd01bf4033177c684e11b6d369a594532736cea05ab915459e8ada6fd2d17"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94",
      "src/promote_final_cards.py": "abb57e9a41e8969346e854fd4d4682b97abdabf203a102b6a5d11fa657eaaa22"
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
      "src/pilot/gen_opt_harness2.py": "cee7dc9df489e2f6852dbce84b665e822cdbb3e58486e8b01aea371df0542c94",
      "src/pilot/perf_preflight.py": "7ec7ab37753ecde0eebc20f1ce251565e8bfbf59963592460be460016dee2a43",
      "src/pilot/window_selftest.py": "8fada81bc466f11acf10680fd017c72f1f308d44ba4872b67e64f67f706e205c"
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
