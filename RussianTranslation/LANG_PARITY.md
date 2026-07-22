# LANG_PARITY.md — cross-language fix/feature parity ledger

_Created: 04-07-2026 · Last updated: 22-07-2026 (H1386 post-H1339 review landing set: +1 entry)_

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
   - **(coverage guard)** a *language-aware* pipeline `.py` under `src/` or
     `src/pilot/` (name ends `_en.py`, or its text carries a `--lang` /
     `'english'` / `FIELD[` / `CARD_FIELD` selector) is NEITHER referenced by a
     ledger entry's `files:` NOR listed in the `lang_parity_coverage` `exempt`
     map below. This catches a **new** EN reimplementation / lang-branching file
     escaping parity tracking entirely — the exact hole the C1–C9 EN findings
     (`audit_window_en.py`, `promote_en.py`) grew in. The drift check above only
     guards files ALREADY in the ledger; this guards the *entry* into it. Fix by
     adding a ledger entry (SHARED / INTENTIONAL-DIVERGENCE / GAP) or an `exempt`
     row with a one-line reason (for a genuine non-surface: a read-only sampler /
     benchmark / QA-sheet generator). Enforced by `coverage_check` /
     `test_lang_parity_coverage`.
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
    "id": "citation_tm_ru_translation_of_record",
    "mechanism": "citation_tm.lookup/consult_card reuses an existing Russian translation of record for a PWG <ls> source citation (R./MBH./RV./KATHAS. ...) instead of retranslating; wired into corpus_gate.build_card as an additive citation_reuse field",
    "files": [
      "src/citation_tm.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "H1304: the citation translation-memory is RU-only by construction. The reuse assets are Russian translations of record (Elizarenkova RV, Leonov Ramayana, Ocean of Stories, ...); there is NO parallel English citation-TM corpus, so there is nothing to port to the EN path. If an EN citation-TM corpus is ever assembled, this becomes a GAP to port; until then RU-only is intended, not an oversight.",
    "tracking": "",
    "verified_sha256": {
      "src/citation_tm.py": "1916c6cc4c71cc560b1696babdc96c9182a27e246ec9343d4322e9d426cdc754"
    }
  },
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
    "note": "Code review 2026-07-04: <ab>lat.</ab>/<ab>griech.</ab> cues are masked to {Tn} in mask() step 1 BEFORE classify_pct runs, so the end-anchored LATIN_CUE regex matched the placeholder, not the cue; measured 33 Latin/Greek cognate glosses across all of PWG (e.g. ignis, uncus, ansa after `lat.`) were being sent for German translation and leaked verbatim into the translator prompt. Fix expands trailing placeholders back to source and strips tags in the classify context window. Masking is stage-0 and runs before any --lang branch, so the fix is identical for RU and EN. Round-trip stays lossless. Pinned by window_selftest.test_pwg_mask_latin_cue_behind_ab_tag. C8 (21-07-2026, Opus 4.8 claude-opus-4-8): the sibling LATIN_PHRASE heuristic matched German-capitalized homographs of Latin prepositions (In/Ab/Ex/Sub/Pro), so a German gloss like 'In der Regel' / 'In den Schlusssatz einfallen' was masked-and-dropped (never translated), invisibly (restore reinserts the identical German, so the round-trip still read 100% lossless). Fixed: a homograph opener stays 'la' only if NO German function word (der/die/den/mit/und) follows; 'De …' (not a German word) is an unguarded Latin opener. Measured 1/192,763 real occurrence, now kept inline. Round-trip stays lossless; also stage-0, identical for RU/EN. Pinned by test_pwg_mask_german_homograph_not_latin_c8.",
    "tracking": "",
    "verified_sha256": {
      "src/pwg_mask.py": "31abd637d86fc42db9979e31bb560b67f324147339e623ee9837002d2684e0e8",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "target_field_markup_fidelity_parity_c1",
    "mechanism": "The <ls>/{#..#} markup-count fidelity guard runs over the actual TARGET-language field (russian/english), not only the german source-echo, on EVERY promotable lane: JS batch accept() (pre-existing, H1152), JS selfHeal/presplit stitch, headless normalize_batch, headless selfheal stitch, and both autosplit stitch writers (cmd_merge + stitch_topup). A span kept in german but dropped from the translation column is rejected/requeued instead of silently promoted.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/headless_worker.py",
      "src/pilot/autosplit_requeue.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "C1 (bug-hunt review, Opus 4.8 claude-opus-4-8, 21-07-2026). The check keys off TARGET_FIELD (JS) / manifest['field'] (Python) = the per-language field, so it applies identically to ru and en with no language branching. Ported to every off-batch lane the batch accept() H1152 guard never reached: JS heal (stitched-translation-fidelity-reject), headless normalize_batch + selfheal stitch (translation-fidelity-reject / stitched-translation-fidelity-reject), autosplit cmd_merge + stitch_topup (complete-stitch fidelity drift -> reject). Tests: window_selftest test_heal_lane_target_field_fidelity_wired / test_autosplit_stitch_topup_rejects_target_field_drop / test_autosplit_merge_rejects_target_field_drop; headless_worker_selftest test_normalize_batch_translation_fidelity_reject / test_headless_heal_stitch_translation_fidelity_reject.",
    "tracking": "H1412",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/headless_worker.py": "bc43daf54de2d9065d55a2d77a7b49c51303bcfdc4d0ac5cb7ed362e3936d4c7",
      "src/pilot/autosplit_requeue.py": "59869969b9f7dd2625b27734c5ce68962c6ca18570e636085aaab7a6344462d4",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
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
    "note": "lang is a first-class parameter of the TM address (sha256(lang + ...)); --lang=ru|en both get full reuse. C3 (21-07-2026, Opus 4.8 claude-opus-4-8): the reuse was SHARED in address but NOT in the served card — the card-TM builder wrote the EN sense under the store COLUMN name FIELD['en']=='en' instead of the CARD field 'english', so the serve-side tm_card_sane refused 100% of EN card-TM hits ('sense missing english') while RU worked. Fixed by a single CARD_FIELD={'ru':'russian','en':'english'} used by both the card builder and the fragment lane (_FRAG_TRANSLATION_FIELD aliases it), so the two lanes can't drift. Test: window_selftest test_en_card_tm_serves_english_field_c3.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac"
    }
  },
  {
    "id": "cards_schema_defs_pruning",
    "mechanism": "H130 fix: CARDS_SCHEMA only carries $defs reachable from 'card', not the whole shared schema file's judge/judge_issue defs. H428 extension: _strip_post_generation_fields() additionally drops every field a deterministic annotator adds AFTER generation (government/labels/renou/renou_oldest/evidence on sense, renou_oldest_sense on record, evidence_summary/stats on card) BEFORE the reachable-defs walk, so evidence_item/evidence_summary/stats become unreachable too. Reachable schema: 10,940 -> 1,698 chars.",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "_reachable_defs() walks $ref pointers regardless of lang; _strip_post_generation_fields() runs before it and is called unconditionally in build() for both lang paths (no lang-specific field list).",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
    }
  },
  {
    "id": "sonnet5_explicit_model_pin_en",
    "mechanism": "RU and EN generation paths pin 'claude-sonnet-5' explicitly in Workflow harnesses and headless manifests",
    "files": [
      "src/pilot/gen_opt_harness2.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H818 closes the former divergence: exact model provenance is required across four accounts, so both RU and EN now request and stamp claude-sonnet-5. This prevents account/profile alias resolution from making cross-window provenance incomparable.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
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
      "src/audit_coverage.py": "a60b8c0ed3b0022a6527a029d1e818cedab3dfcbbb545fc2c78b6a5dd514dcfa",
      "src/pilot/prompt_rule_audit.py": "a937af2156a765a5496ee9ca69503f777d55a02238c255ffb0b12e0569435338",
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/audit_window_en.py": "73398beb59c272ceb8bbcfdb1649e241a83d4f8447f1aae33c4c3c1e3e5e2862"
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
    "tracking": "Uprava/handoffs/archive/H304-Fable_RussianTranslation_coordinator-driver-remake_07.07.26.md (EN-emitter port is the recorded follow-up)",
    "verified_sha256": {
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/window_reports.py": "bebcc79826bc74d676be5861f961c8aac3aa2f793f41bbe757c4fc02f0eb8720",
      "src/pilot/requeue_from_audit.py": "687f9861e3dbcc3ec10f730330cd83a88348f8ef59d3a17383950c77e7bd03d2"
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
      "src/pilot/requeue_from_audit.py": "687f9861e3dbcc3ec10f730330cd83a88348f8ef59d3a17383950c77e7bd03d2"
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
    "note": "The two stores (pwg_ru_translated.jsonl vs the EN store) have different schemas and provenance history (RU predates the EN pilot by months); a merged script was never worth the risk of cross-contaminating the two promotion paths for a mechanical CLI split. Revisit only if the two stores' schemas converge. C6 (21-07-2026, Opus 4.8 claude-opus-4-8): the SCRIPTS stay separate, but the {Tn}-residue promotion guard is now SHARED — promote_en.py imports TN_RE + UnrestoredPlaceholder from promote_final_cards.py rather than duplicating them, closing the gap where the RU C-01 path refused a card carrying an unrestored {Tn} while the EN attach() silently wrote it into the store. Pinned by the C6 block in promote_en.selftest(). C9 (21-07-2026, Opus 4.8 claude-opus-4-8): the EN backup used a second-resolution timestamp + a plain open('w'), so two lock-serialized runs in the SAME second overwrote the earlier .preEN recovery copy (defeating the docstring's per-run-backup promise). Fixed to a µs+pid+uuid name (_en_backup_path) + the RU lane's O_EXCL fsynced copier (_fsynced_backup, imported — single source). Pinned by the C9 block in promote_en.selftest(). H1425 W3 audit (21-07-2026, Opus 4.8 claude-opus-4-8): confirmed nothing new to share — the shared primitives (TN_RE / UnrestoredPlaceholder / _fsynced_backup) are already imported (C6/C9); the rest of promote_en (norm_de / en_index / match_en / attach) is EN-ATTACH-specific — it attaches an `en` field onto the existing RU store, a different job from promote_final_cards' RU store WRITER — and _en_backup_path's `.preEN` marker is intentionally per-lane. P9 (21-07-2026, Opus 4.8 claude-opus-4-8, H1421): the last shareable primitive is now SHARED too — promote_en.py imports _atomic_write_rows from promote_final_cards.py and its store write is fsync-before-replace durable. The old EN write was a bare open('w') + os.replace: atomic (the rename is all-or-nothing) but NOT durable — a crash/power-loss between the write and the metadata flush could leave a non-durable/truncated store even after the rename, and under --no-backup that write is the ONLY thing between an interrupted write and total loss. As a bonus both lanes now write the store byte-identically ('\\n' newlines; the old EN write CRLF-translated on Windows). Pinned by the P9 block in promote_en.selftest() (fsync-called + round-trip + single-source identity assertion). Adversarial verification note: bug-hunt P1 (merge_store_rows had no better-attempt-wins guard) was ALSO an H1421 item but was already fixed upstream by B08 (H1339) — merge_store_rows is better-attempt-wins with pinned regression selftests — so P1 needed no code change. INTENTIONAL-DIVERGENCE re-affirmed (the scripts stay separate; every low-level store-safety primitive — {Tn} residue, fsynced backup, durable atomic write — is now single-sourced from the RU lane).",
    "tracking": "",
    "verified_sha256": {
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/promote_en.py": "f801b86d267f346e2a11ebbee681103e68e01f6520da0e70e4a20b460ee27d9d"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
    "note": "H169 (2026-07-04 review, 'broken validators'): the advertised HARD DUP gate was never emitted -- the only within-record duplicate signal was soft SAME-GLOSS, gated on >=3 content words, so a short duplicate ('to go'/'to go') produced zero flags and --strict passed. Classified GAP-being-closed rather than INTENTIONAL-DIVERGENCE: RU's within-record duplicate protection is the cross-part audit_sense_dupes.py gate (already SHARED, see gate_fixes_20260703_ru_only/PR #135) plus the soft, all-senses-only identical_russian_glosses risk in prompt_rule_audit.py (MEDIUM, not high-confidence) -- neither is a pairwise HARD gate. EN now closes that with a real HARD pairwise DUP check; RU getting an equivalent pairwise HARD gate (rather than its current all-or-nothing soft signal) is left as a natural follow-up, not blocking this fix. Pinned by test_en_gate_dup_has_teeth in window_selftest.py. C2 (21-07-2026, Opus 4.8 claude-opus-4-8): the HARD gate keyed on prose(english), which STRIPS {#..#} Sanskrit and <ls>, so two senses distinguished only by their referent ('N. of a serpent-demon {#vAsuki#}' vs '…{#takzaka#}') collapsed to one string and the second was wrongly HARD-DUP'd, failing --strict on faithful output (310 real within-record cases). Fixed to key the DUP seen-dict on the normalized RAW english (referent preserved) while CIRCULAR keeps prose() norm; a true identical-english duplicate is still caught HARD. Pinned by test_en_dup_gate_preserves_sanskrit_referent_c2.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/audit_window_en.py": "73398beb59c272ceb8bbcfdb1649e241a83d4f8447f1aae33c4c3c1e3e5e2862",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/promote_en.py": "f801b86d267f346e2a11ebbee681103e68e01f6520da0e70e4a20b460ee27d9d"
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03"
    }
  },
  {
    "id": "presplit_lane_amortization_and_budget_guards_h189",
    "mechanism": "Presplit-PRIMARY cards are grouped at PRESPLIT_GROUP_CITE_BUDGET(60)/PRESPLIT_GROUP_SENSE_CAP(18) instead of the conservative SELFHEAL_GROUP_BUDGET(12), amortizing the ~27k framework across many fragments per agent() call; the wall-clock kill gate is recalibrated (floor 120s->45s, ceil 480s->180s) per MG's >60s-suspicious/>3min-unacceptable rule; the original window-level shared MAX_AGENTS kill-switch is retained as backwards-compatible total telemetry but superseded operationally by the independent translate/heal ceilings in split_agent_budget_pools_20260710; the generator warns + suggests a key-disjoint split when the harness exceeds MAX_HARNESS_BYTES(480k); perf_preflight adds a per-card / per-window cost gate that flags a window dominated by expensive cards",
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
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/perf_preflight.py": "3dc1d44f0054da4278e7c6eb34f03477b697431e22bcf7ea0c201afad2009e13",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pwg_mask.py": "31abd637d86fc42db9979e31bb560b67f324147339e623ee9837002d2684e0e8",
      "src/make_edition_cut.py": "5a24d8c96611f50f008689609f8140ef47b02731524dbc255438426b36d306fd",
      "src/preflight_remaining_gates.py": "00386c837b97986c9702abfceed9c29534736c3df3063af202ddfaae6b078b8f",
      "src/release_readiness.py": "db38a870bbc8b5dbe694e706e4a7b9089ba41211a3881ad9a1bd4eb02950c8a9",
      "save_and_audit.py": "e1d7a3b6c5a8c47dbc414dbcf991e9ead82b76a013e4624cffe76066e576c8b6",
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/autosplit_requeue.py": "59869969b9f7dd2625b27734c5ce68962c6ca18570e636085aaab7a6344462d4",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/corpus_gate.py": "65429923536739d8b0410092aa65a679ef7e8c69140ad0a3a95fa41ff0ec7a89",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/ls_resolver.py": "78f1a17e80d7b0ed9fb4dd79fdd5c076f8ef2f1fee245ab0cda9f5e4da8fcfec",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
    "note": "H335 (08-07-2026). The census reads raw pwg.txt below any --lang branch and never touches RU/EN translation code; the government-marker regexes operate on the German source markup shared by both editions. Read-only over the source; selftest-gated. Re-verified 12-07-2026 after H778 (#384) added a source_sha16-gated JSON sidecar freeze/cache layer (build_sidecar/write_sidecar/load_sidecar/census_or_load) plus a `freeze` CLI subcommand around the same run_census() function — still no --lang branch, verdict unchanged. Re-verified 19-07-2026 (H1308, Opus 4.8 claude-opus-4-8): the PAREN/CASE/MIT/CONNECTOR regexes were made case-INSENSITIVE so the PW zz_pw* CAPITALIZED stratum ((<ab>Instr.</ab>)) extracts alongside the PWG lowercase one, matched case tokens normalised to lowercase via the new _cases() helper. Both extract_government() (store de fields) and run_census() (raw pwg.txt) share the change; the raw ceiling rose 3853->3905 markers (the +52 are sentence-initial 'Mit dem <ab>...</ab>' prose government the lowercase regex missed). Still operates only on the shared German source markup below any --lang branch; verdict unchanged.",
    "tracking": "",
    "verified_sha256": {
      "src/government_census.py": "0a004740cc6ba9407c292fef015b07b60fcd62cd82b6252f08fc49a00de6d6d8"
    }
  },
  {
    "id": "government_index_page_h1308",
    "mechanism": "H1308 one-click government (Rektion) retrieval page: government_index()/government_meta()/emit_government() in build_article_site.py apply government_census.extract_government() over each sense's DE source text to produce government.html (case chips Instr./Loc./Gen./Acc./Dat./Abl. + variation bucket -> every card governing that case), an honest floor-vs-ceiling coverage banner, and index.html #g=<safe> deep-links to the full entry.",
    "files": [
      "src/pilot/build_article_site.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1308 (19-07-2026, Opus 4.8 claude-opus-4-8). government_index() reads s['de_raw'] (the German SOURCE sense text, identical across the RU and EN editions) via the shared extract_government() — the same authoritative reference set ab_frequency()/ls_stats() use — and marker spans render through the shared _render() layer. No RU/EN branch anywhere in the government surface; a future EN site build would show the identical government index. Language-neutral analysis layer, exactly like the H775 government sidecar precedent. Pinned by build_article_site.py --selftest (selftest_government).",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/build_article_site.py": "09ce9d51e88bcfdebfb86ac74b86d57317faa6f182922041a212b96871b24987"
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
      "src/promote_lock.py": "f8dda14a7423dfecac77893f10f7735361db8bd6c79297172243aafaf1d28ef4",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/promote_en.py": "f801b86d267f346e2a11ebbee681103e68e01f6520da0e70e4a20b460ee27d9d",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/requeue_from_audit.py": "687f9861e3dbcc3ec10f730330cd83a88348f8ef59d3a17383950c77e7bd03d2",
      "src/pilot/root_window_status.py": "ab13516c5ffa824ddc45b2dc0d482c09f06de57d5963dcc31d73ecc638a116f3",
      "src/pilot/window_reports.py": "bebcc79826bc74d676be5861f961c8aac3aa2f793f41bbe757c4fc02f0eb8720",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/window_common.py": "2d6926ba3a2e99f788641637b2cb6f2f9637ecb7f4e1b1c1561a367c8dd81e93",
      "src/pilot/window_reports.py": "bebcc79826bc74d676be5861f961c8aac3aa2f793f41bbe757c4fc02f0eb8720",
      "src/pilot/requeue_from_audit.py": "687f9861e3dbcc3ec10f730330cd83a88348f8ef59d3a17383950c77e7bd03d2",
      "src/pilot/layer_versions.py": "42e44f32db2628e3137522f5d15827cf0641b642bdacfdb76be04cdd41eaefba",
      "src/pilot/failure_capture.py": "c0ca940b54fc326e0a0b67320758c81aa5a48dd29247250996c38a85a7786e4d",
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/annotate_evidence.py": "641a96e9b111737d8e93eb88a508480a2360acc12aeff59d05db0b4399a084ef",
      "src/annotation_report.py": "747f46c0c213b178cfeba22c04314696f4312a55eaf738d946dac08ead06c9d0",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
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
      "src/pilot/coordinator.py": "e9b340cc17511e1268ae7fe839d1e74b92d0dac5c810332a3dfc7f4c2cb51e0a",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "genre_sense_join_h339",
    "mechanism": "Per-sense citation genre join (annotate_genres.py, H335 W4): resolves each sense's <ls> citations to ls_source_map.json's curated genre label(s) + a coarse rollup (kavya/veda/sastra/purana/epic/kosha), reusing renou.keys_in_text verbatim for siglum normalization; annotation_report.py folds the --in/--only/--genre-report query surface on top",
    "files": [
      "src/annotate_genres.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H339 (08-07-2026). The join reads <ls> citation markup shared verbatim by both RU and EN editions (renou.keys_in_text is the same siglum parser annotate_renou.py already treats as language-independent) and never touches translation text itself. Read-only over the store; selftest-gated.",
    "tracking": "",
    "verified_sha256": {
      "src/annotate_genres.py": "5eea7d5269c716d5c96ceb81be5c22358fe45542b066f66963a8fdd1562d89e3"
    }
  },
  {
    "id": "koch_xref_resolution_h397",
    "mechanism": "koch_xref.py resolves koch's bare `см. X` cross-reference glosses (a redirect with no meaning of its own, e.g. `-aSrika` -> \"см. अश्रि अश्रिक -aśrika\") to the target headword's real gloss via a Devanagari self-header crosswalk harvested from koch.jsonl itself, chain-safe up to 2 hops with a visited-set cycle guard; annotate_evidence.py's gather() calls resolve_koch_lane() on the koch lane before best_relation/source_meaning_tokens run, so a resolvable redirect counts as provides/supports evidence instead of H337's `silent` classification",
    "files": [
      "src/koch_xref.py",
      "src/annotate_evidence.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "H397 (09-07-2026, H337 follow-up). koch is a Sanskrit->RUSSIAN dictionary only (Кочергина); its `см.` (Russian \"see\") cross-reference marker and the Devanagari self-header crosswalk this module builds are RU-lexicographic conventions with no EN counterpart in this pipeline — same divergence basis already recorded for evidence_retrofit_annotate_h337 and corpus_gate_evidence_markers_fl7_h321. Pinned by test_koch_xref_resolution (koch_xref.py's own pure-function --selftest, no koch.jsonl file IO so it runs in CI).",
    "tracking": "",
    "verified_sha256": {
      "src/koch_xref.py": "b6b3c3524f446862a25cf0f086125d53977dabf02a26cc6724972d0a05c69013",
      "src/annotate_evidence.py": "641a96e9b111737d8e93eb88a508480a2360acc12aeff59d05db0b4399a084ef",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "stage2_mechanical_pregate_h405",
    "mechanism": "stage2_pregate.py — deterministic mechanical pre-gate for the Stage-2 QA judge. Given a (German source, translation) card pair it hard-fails the format invariants the judge prompt already declares must not affect the verdict: untranslatable-span preservation (LS/SAN/AB/IS/LEX/LANG, category regexes kept in sync with pwg_mask.PAIRED by --selftest), {Tn} anchor multiset equality on masked pairs, stranded/never-restored {Tn} on final cards, and unmask-leak; NO-RUSSIAN is emitted as a soft warning (never blocks) because a {%…%}-with-no-Cyrillic card may be a form-citation apparatus stub. A failed card is requeued, not judged, so the judge rubric can drop the mechanical criteria and rule only on the semantic part. The `--wf <wf_output.json>` window-gate mode reads audit_translation.py's IN/<stem>.raw.txt (source) vs OUT/<stem>.merged.md (output) file pairs and emits FLAGGED_JSON of hard fails; wired into src/pilot/audit_window.py's gate list as `stage2_mechanical` (parse_flagged_json), so a hard-failed card joins the requeue",
    "files": [
      "src/stage2_pregate.py",
      "src/pilot/audit_window.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H405 (09-07-2026, PIPELINE_CAPABILITY_AUDIT W5 recommendation). Language-agnostic by construction: it compares markup/anchor STRUCTURE across the source↔translation pair and never inspects meaning, so the RU and EN editions are gated identically (the untranslatable spans it preserves — <ls>/{#…#}/<ab>/<is>/<lex>/<lang> and {Tn} — are the same in both). The only language-touching check, NO-RUSSIAN, keys on presence of ANY translation-script letters and is a non-blocking warning; the EN edition would swap the Cyrillic class for a Latin-prose check but the SHARED gate logic is unchanged. The pregate MODULE + the RU audit_window.py wiring shipped first; the EN audit_window_en.py wiring followed same-day via an in-process per-sense adapter (see stage2_pregate_en_wiring_h405, now SHARED) — that edition audits in-process (audit_sense), not via the .raw.txt/.merged.md subprocess file-pair model this gate reuses for RU. Pinned by stage2_pregate.py's own pure-function --selftest (11 cases + a masker-sync assertion; no store file IO, runs in CI).",
    "tracking": "",
    "verified_sha256": {
      "src/stage2_pregate.py": "8f07422d3c416e32d1882f0777d56cc44ba781d19c8097fd9500ddefbfd22945",
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2"
    }
  },
  {
    "id": "stage2_pregate_en_wiring_h405",
    "mechanism": "RESOLVED — the Stage-2 mechanical pre-gate is now wired into the EN auditor (src/pilot/audit_window_en.py) too. Because that edition audits in-process per-sense (audit_sense(german, english)) rather than via the RU auditor's .raw.txt/.merged.md subprocess file pairs, the wiring is an in-process adapter: audit_sense calls stage2_pregate.pregate(g, e) and folds in ONLY the NET-NEW hard flag types the EN auditor's own per-sense checks don't already produce — IS-LOSS (<is> spans; the EN AB regex omits <is>), STRANDED-ANCHOR (leftover {Tn}), ANCHOR-LEAK/-MISMATCH — while LS/SAN/AB loss stay owned by audit_sense at its own thresholds to avoid double-reporting. Those net-new types were added to the HARD tuple so --strict fails on them",
    "files": [
      "src/pilot/audit_window_en.py",
      "src/stage2_pregate.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H405 (09-07-2026, resolved same day). Both editions now run the same pregate() module for the mechanical invariants; the difference is only the adapter (RU: subprocess --wf over file pairs; EN: in-process per-sense), not the logic. The partial-adoption (net-new flag types only) is deliberate — the EN auditor already reimplemented LS/SAN/AB/MISSING per-sense with its own thresholds, so pregate contributes exactly the invariants it lacked (<is>, stranded/leaked anchors) rather than duplicating. Verified by a functional test (clean / is-dropped→IS-LOSS / stranded→STRANDED-ANCHOR / ls-dropped→single LS-LOSS not double-flagged) + window_selftest.py green.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/audit_window_en.py": "73398beb59c272ceb8bbcfdb1649e241a83d4f8447f1aae33c4c3c1e3e5e2862",
      "src/stage2_pregate.py": "8f07422d3c416e32d1882f0777d56cc44ba781d19c8097fd9500ddefbfd22945"
    }
  },
  {
    "id": "fri_xref_resolution_h404",
    "mechanism": "fri_xref.py resolves fri's bare Latin-apparatus cross-reference glosses (v./cf./q.v. redirect with no Russian meaning of its own, e.g. `akārya v. akartavya;`) to the target headword's real gloss. Unlike koch, fri's targets are already IAST-like romanized (no Devanagari self-header crosswalk needed) — build_src.iast_to_slp1 converts the extracted target token, then corpus_gate.form_key joins into fri's own key1 index built straight from each entry's own slp1 field; one hop only. annotate_evidence.py's gather() calls resolve_fri_lane() on the fri lane before best_relation/source_meaning_tokens run, so a resolvable redirect counts as provides/supports evidence instead of `silent`. H404 measured kna (0.2%), smirnov (1.0%), kow (0.0%) as below the ~2% materiality bar H397 set — those three are NOT touched by this or any resolver.",
    "files": [
      "src/fri_xref.py",
      "src/annotate_evidence.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "H404 (09-07-2026, H397 generalization to a second RU source). fri (Фриш 1956) is a Sanskrit->RUSSIAN dictionary only; its v./cf./q.v. Latin-apparatus redirect marker is a fri-specific lexicographic convention with no EN counterpart in this pipeline — same divergence basis already recorded for koch_xref_resolution_h397 and evidence_retrofit_annotate_h337. Pinned by test_fri_xref_resolution (fri_xref.py's own pure-function --selftest, no fri.jsonl file IO so it runs in CI).",
    "tracking": "",
    "verified_sha256": {
      "src/fri_xref.py": "6574a4cc3a10e0697dce552b3b3082418410500b8417818c712c5abb02037233",
      "src/annotate_evidence.py": "641a96e9b111737d8e93eb88a508480a2360acc12aeff59d05db0b4399a084ef",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "per_card_heal_budget_h442",
    "mechanism": "Per-card heal-call ceiling from the H442 kill-gate recalibration. PER_CARD_HEAL_BUDGET (default on) makes selfHeal derive one shared {spent,max} per card sized ceil(nGroups*PER_CARD_HEAL_FACTOR)+PER_CARD_HEAL_HEADROOM and thread it through healGroup + its bisection recursion; once a card's own heal spend crosses max, healGroup returns a PARTIAL card (missing_fragments requeue-able). The follow-up split_agent_budget_pools_20260710 mechanism removes the shared-window ceiling that previously fired before these card caps on all-heal windows. --no-per-card-heal-budget tunes only this ceiling; kill-timeout bisection waste is tracked separately in heal_kill_timeout_no_bisect_h442.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H442 (10-07-2026, Opus 4.8 claude-opus-4-8). The heal/kill budget is language-agnostic: healGroup/selfHeal run identically for the RU and EN lanes (the only per-language pin is the model alias, already tracked in sonnet5_explicit_model_pin_en), so a per-card ceiling that bounds the RU-observed medium50 cascade applies verbatim to EN. Sibling of the SHARED wall_clock_kill_gate and selfheal_binary_split entries. Pinned by test_per_card_heal_budget_wired in window_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "heal_kill_timeout_no_bisect_h442",
    "mechanism": "Kill-timeout no-bisect guard from the H442 P0 fix. healGroup distinguishes KILL-TIMEOUT from malformed/missing/fidelity failures: after the first kill-timeout for a heal group, unresolved fragments are left as missing_fragments for transient requeue and no /A or /B recursive bisection is started. Soft/malformed exits still bisect, because smaller groups can plausibly help; slow-call kill-timeouts do not spend more heal calls on smaller fragments.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H442 P0 (10-07-2026). healGroup/selfHeal are language-agnostic generated harness logic shared by RU and EN; the guard keys on wall-clock kill-timeout behavior, not translation language. Pinned by test_heal_group_kill_timeout_does_not_bisect in window_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "launch_telemetry_counters_h462",
    "mechanism": "H462 returned run telemetry. The harness summary returns kill_timeouts / conn_errors / heal_calls / kill_bisect_blocked, counted centrally in agentKill (catch-and-rethrow, zero control-flow change) and in healGroup kill-timeout handling. classify_run.py turns the summary alone into clean / code-failure / infra-confounded, mechanizing the H442 hand rule; pre-H462 payloads classify as unclassifiable, never guessed.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py",
      "src/pilot/classify_run.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H462 (10-07-2026, Fable 5 claude-fable-5). The counters live in the language-agnostic generated harness JS (agentKill/healGroup are shared by --lang ru/en; the only per-language pin is the model alias, tracked in sonnet5_explicit_model_pin_en), and classify_run.py reads summary fields that exist identically for both lanes. Pinned by test_run_telemetry_counters_returned and test_classify_run_verdicts in window_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c",
      "src/pilot/classify_run.py": "6061958062ef7ae4b673aa77b2f2c9823663d8d083a61a792fabfbefb732fb71"
    }
  },
  {
    "id": "split_agent_budget_pools_20260710",
    "mechanism": "The generated Workflow runtime enforces independent translate and heal agent-call pools. Whole-card batches and resolveGroup binary splits spend MAX_TRANSLATE_AGENTS; fragment recovery and presplit cards spend MAX_HEAL_AGENTS. agent_budget.py derives the plan as pure Python: the heal ceiling equals the sum of per-card heal ceilings, so the window pool cannot fire before the per-card guards merely because many cards recover concurrently. The legacy --max-agents override remains one combined hard ceiling allocated across active pools. Summary/meta return both pool ceilings, spend, and trip flags while retaining backwards-compatible total fields.",
    "files": [
      "src/pilot/agent_budget.py",
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "10-07-2026, Codex/GPT-5. Budget planning and generated agentKill lane selection are language-agnostic: both RU and EN use the same batches, FRAGS, healGroup/selfHeal, label prefixes, and counters. The change does not touch prompt text, output fields, or model selection. Pinned by agent_budget.selftest, test_agent_budget_plan_separates_translate_and_heal_pools, test_split_agent_pools_all_heal_runtime (executes generated JS under Node with a null-returning mock agent), and test_budget_kill_switch_wired.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/agent_budget.py": "9683c7c24903b95e39e85839d64e4623ebe68dda1271f0cf85ec60c19251cb61",
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "mdf_export",
    "mechanism": "export_mdf_pwg_ru.py serializes promoted cards to MDF with \\de=RU national lane and \\ge=EN gloss lane in ONE code path (\\ge emitted only when promote_en.py attached en; never fabricated)",
    "files": [
      "src/pilot/export_mdf_pwg_ru.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "New mechanism 11-07-2026 (H727): both language lanes are handled by the same clean_prose/mdf_record path parameterized by lang; the RU <ab> Bucket-A display policy is the documented intentional per-language difference INSIDE the shared path (EN keeps the original token), per ABBREVIATIONS_RU.md. Design: docs/MDF_EXPORT_PWG_RU.md.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/export_mdf_pwg_ru.py": "1d32e10622d246295cc3b5f8300e166de76cb210e74719ca7d79ddc7170d2be4"
    }
  },
  {
    "id": "canonical_store_path_h805",
    "mechanism": "Both promotion writers resolve the translated store via the identical store_path.canonical_store() helper (env PWG_RU_STORE -> MAIN-worktree store -> local default), so a drain window run in an isolated git worktree promotes into the persistent MAIN checkout store instead of a discarded worktree copy (the H255 no_pwg_w06 loss vector). Applied symmetrically to promote_final_cards.py (RU) and promote_en.py (EN).",
    "files": [
      "src/store_path.py",
      "src/promote_final_cards.py",
      "src/promote_en.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "New mechanism 12-07-2026 (H805, root-fix for the H255 w06 store loss). The resolver is language-independent; both promotion paths import the SAME store_path.canonical_store and default --store to its result, so neither RU nor EN can silently drop promotions into a discarded worktree store. Strengthens promotion_claim_file_h336: both paths now lock the SAME canonical store path across worktrees. Deterministic selftest: python src/store_path.py --selftest.",
    "tracking": "",
    "verified_sha256": {
      "src/store_path.py": "4967ab7ea748da995367fd0520f89f4bf9a39b84c428310314291b85be26f73c",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/promote_en.py": "f801b86d267f346e2a11ebbee681103e68e01f6520da0e70e4a20b460ee27d9d"
    }
  },
  {
    "id": "lowwide_staggered_dispatch_h811",
    "mechanism": "gen_opt_harness2.py --max-wide=N / --stagger-ms=M route the emitted top-level dispatch through a boundedParallel(thunks, width, staggerMs) worker-pool (at most N units in flight, first N starts staggered by M ms) instead of the runtime parallel(); 0 = unbounded (default, no regression). Degraded-API requeue lane: at ~10-wide a tiny card that completes in ~54s ALONE is inflated past the 180s kill CEIL (H255 w07: 32/36 kill-timeouts on 128-500B skeletons).",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/boundedparallel_test.js",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "New mechanism 12-07-2026 (H811, from the H255 w07 concurrency finding). The dispatch width control is language-INDEPENDENT: the same MAX_WIDE/STAGGER_MS constants + boundedParallel helper are emitted for every --lang (the harness is lang-parameterized; nothing here branches on language), so a RU or EN requeue uses --max-wide=3 identically. Behavioral test: node src/pilot/boundedparallel_test.js against the REAL emitted fn (caps concurrency, staggers, order-preserving, null-on-throw), wired into window_selftest.test_lowwide_staggered_dispatch.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/boundedparallel_test.js": "3d768f874e13607e235e55f9300771dabd25f6173e256001e956150ce9b33401",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "headless_execution_manifest_h818",
    "mechanism": "The shared generator emits a versioned execution manifest including fragment recovery state; headless_worker implements Workflow-parity retry/split/heal/stitch and returns the existing result contract; the scheduler/planner dispatch manifests without reading dictionary text",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/headless_worker.py",
      "src/pilot/max_account_orchestrator.py",
      "src/pilot/coordinator.py",
      "src/pilot/headless_worker_selftest.py",
      "src/pilot/max_account_orchestrator_selftest.py",
      "src/pilot/no_pwg_scale_plan.py",
      "src/pilot/windows100_selftest.py",
      "src/pilot/run_observability.py",
      "src/pilot/run_observability_selftest.py",
      "src/pilot/proc_tree.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H818 Windows readiness uses one language-parameterized manifest and worker contract. Whole-card retries, binary split, fragment TM/restore/fidelity, per-card budgets, timeout-no-bisect, partial stitching, audit-clean subset promotion, staged dispatch, and credential-safe event/census telemetry do not branch on RU/EN. Production policy selects RU no_pwg for the first 100-headword proof; the mechanism preserves EN field/schema behavior.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/headless_worker.py": "bc43daf54de2d9065d55a2d77a7b49c51303bcfdc4d0ac5cb7ed362e3936d4c7",
      "src/pilot/max_account_orchestrator.py": "03a59329720faa2cdbb56dd71284128ef3db62e301fb650cf51d4a2d4fec3a68",
      "src/pilot/coordinator.py": "e9b340cc17511e1268ae7fe839d1e74b92d0dac5c810332a3dfc7f4c2cb51e0a",
      "src/pilot/headless_worker_selftest.py": "e6dbff6e754dc05fd77fc91a8f182671fb063420563f1454c0eba729a0caf1de",
      "src/pilot/max_account_orchestrator_selftest.py": "41d1060b729d2f2507224ee0c072b07437c01f2285405f528c70ab8bf7df40af",
      "src/pilot/no_pwg_scale_plan.py": "7e4bb02a2f2865a3447afe47cf1f4106209bdc24f403cb6dd2b8c524b6928d63",
      "src/pilot/windows100_selftest.py": "14898dd420cf0736d7dc54064231311844dd6d30205fecd02802f75b5dd1ef38",
      "src/pilot/run_observability.py": "eb21e08ba4f0e7ab7ab5dacf9db4e4d0d38234f2d63385157735ca8d7b8ced61",
      "src/pilot/run_observability_selftest.py": "75bc960a35080a0c84ca9b5ee62b63134a9e0bde334c5531d564b13019187b60",
      "src/pilot/proc_tree.py": "7b4eb10defbca8efe84b2db6eef1d63c1124e92d0851da78549c7440734f24c4"
    }
  },
  {
    "id": "gen_model_ledger_stamp_h390",
    "mechanism": "H390 Phase 1 per-window model instrumentation. gen_opt_harness2 stamps the model pinned on the translate agent() calls into the run's own meta (meta.gen_model); window_reports.append_ledger records it on every window_ledger.jsonl row (read from workflow_meta); harvest_launch_stats surfaces a population-by-model slice plus a gen_model coverage count. Makes per-model rates (the Fable-vs-Sonnet A/B) computable straight off the ledger, which previously could not see which model generated a window.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_reports.py",
      "src/pilot/harvest_launch_stats.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H390 Phase 1 (12-07-2026, Opus 4.8 claude-opus-4-8), extended by H818. gen_model is written into language-agnostic run meta and flows through the shared ledger writer and harvester identically for RU/EN; both paths now stamp exact claude-sonnet-5. Pinned by test_ledger_stamps_gen_model in window_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_reports.py": "bebcc79826bc74d676be5861f961c8aac3aa2f793f41bbe757c4fc02f0eb8720",
      "src/pilot/harvest_launch_stats.py": "751f4089cc2cbff3354d0f5b9506268a4ddd82e1c0f654755ffc88a11b8b6f3b",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "presplit_cite_floor_h823",
    "mechanism": "gen_opt_harness2 floors the CITATION presplit trigger at PRESPLIT_SOLO_CITE_FLOOR (--presplit-solo-cite-floor, default 40) so --output-budget=1 (the no-PWG single-card lane) no longer force-routes every citation-bearing card into the fragment heal lane; and killBudgetForCur gives ANY single-card batch the CEIL kill budget (not just no-fallback singles), since a lone card has no batch-mates to starve and the heal lane is no better budgeted on a slow API.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "New mechanism 12-07-2026 (H823, fixes the H255 presplit-cohort loss). Both the citation presplit trigger (_presplit_hit) and the single-card kill budget (killBudgetForCur) are language-independent — they key on <ls>/fragment counts and FRAGS, never on --lang; the same floor + CEIL apply to RU and EN identically. Extends no_fallback_single_kill_budget_and_nominal_key_echo (H220) from no-fallback singles to all singles. Pinned by test_presplit_cite_floor_and_single_ceil.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "sense_count_sanloss_guard_h920",
    "mechanism": "Deterministic SAN-LOSS (whole-dropped-sense) guard: sense_count.py counts a supplement source's top-level senses (N〉 close-glyph / line-anchored N) markers); gen_no_pwg_card stamps that count as portrait.source_senses and prepends a sense-completeness rule to >=2-sense no_pwg sub-cards; both auditors flag a card whose OUTPUT sense count is short of the portrait count (audit_window.py 'sense_loss' gate -> requeue defect; audit_window_en.py 'MISSING-SENSE' HARD flag)",
    "files": [
      "src/pilot/sense_count.py",
      "src/_pilot_gen_merged.py",
      "src/pilot/audit_window.py",
      "src/pilot/audit_window_en.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H920 (14-07-2026, Opus 4.8 claude-opus-4-8[1m]): closes the no_pwg/supplement SAN-LOSS gap the H911 gate surfaced (darv_i~~h0_zz_pw dropped source sense 1 'Löffel', output 2/3, and the harness accept() <ls>/{# token match passed it clean because the dropped gloss-only sense carried neither a citation nor a masked Sanskrit span). Every part is language-neutral: sense_count.py counts SENSE OBJECTS and source 〉/N) markers (never gloss language); the portrait source_senses stamp + the sense-completeness prompt rule live in _pilot_gen_merged no_pwg generation, which is pre-lang (the source is German for RU and EN alike); the audit guard is the SAME sense_count.scan_sense_shortfall/sense_shortfall wired into BOTH audit_window.py (RU 'sense_loss' gate -> requeue defect) and audit_window_en.py (EN 'MISSING-SENSE' HARD flag) — one shared primitive, no RU/EN reimplementation. Conservative: a portrait without source_senses (pre-H920) or a null card is skipped, never a false positive. Pinned by test_h920_sense_count_top_level_ordinals, test_h920_sense_shortfall_gate_flags_dropped_sense, test_h920_no_pwg_portrait_stamps_source_senses, test_h920_en_missing_sense_hard_flag. H960 (15-07-2026) hardened count_source_senses to count only line-opening ordinals (skipping mid-prose cross-reference ordinals) — still SHARED / language-neutral, an FP reduction, not a behavior split; the harness accept()-side consumption of this count lands in accept_sanloss_soft_gate_h960.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/sense_count.py": "e3ad886f8751f5e5ef877bf96219140bc5c8ccca5b02bb2e33f7f6620ec5db2c",
      "src/_pilot_gen_merged.py": "0c350f3ddfb9d33edf04e7e1a9fd88939ffa886066f05116e959255b29fa381f",
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/audit_window_en.py": "73398beb59c272ceb8bbcfdb1649e241a83d4f8447f1aae33c4c3c1e3e5e2862",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "accept_sanloss_soft_gate_h960",
    "mechanism": "Harness-side SAN-LOSS shortfall guard (H920's deferred deepest fix): gen_opt_harness2.py stamps the deterministic cross-reference-hardened source_senses (sense_count.count_source_senses) into each runtime input, and accept() compares the emitted top-level sense count to it — a shortfall is recorded as sanloss telemetry (SANLOSS_SHORTFALLS / sanloss_detail in the run summary) and, only when SANLOSS_HARD_REJECT is armed (owner-gated), rejected+requeued exactly like an <ls>/{# fidelity-reject.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/sense_count.py",
      "src/pilot/window_selftest.py",
      "src/pilot/accept_sensecount_test.js"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H960 (15-07-2026, Opus 4.8 claude-opus-4-8[1m]): closes H920's explicitly-deferred accept()-side sense-count consumption. Language-neutral: accept() counts SENSE OBJECTS (records[].senses[]), never a gloss language, and source_senses is sense_count.count_source_senses over the German source markers (identical for the RU and EN lanes — the source is German for both). SOFT by default (SANLOSS_HARD_REJECT=false): a shortfall is telemetry only (no reject/requeue), so live traffic can measure the true drop-vs-false-flag rate before the reject is armed (owner-gated ladder). The shared counter is hardened against the ~4.78%-of-cards cross-reference over-count the naive count carried (gam~~h2_31_pari 2->1, s_ud~~h0_05_pra 4->2, _a_srayatva 2->0); under-counting is the safe direction, never a false shortfall. Pinned by test_h960_accept_sanloss_soft_gate (builds the real harness, extracts the emitted accept()+countOf, asserts soft-keep / surplus-ok / FP-regression / ls-sk-first / armed-hard-reject via accept_sensecount_test.js) plus the 3 cross-reference fixtures in sense_count._selftest.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/sense_count.py": "e3ad886f8751f5e5ef877bf96219140bc5c8ccca5b02bb2e33f7f6620ec5db2c",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c",
      "src/pilot/accept_sensecount_test.js": "e3ef2b0fb016f6697bcf4c2d087c15b0f76d3422ee70193f064370ab34e3bad1"
    }
  },
  {
    "id": "h_reconstructed_regression_guard_h1149",
    "mechanism": "D-1 regression guard: assert_h_reconstructed_regression (cohort_clean_rates.py) asserts the store's provenance.h_reconstructed count stays exactly 468 unless an authorized re-translation manifest (schema pwg_ru.h_reconstructed_retranslation_manifest.v1) documents the exact decrease; wired into window_selftest.py as test_h_reconstructed_regression_guard.",
    "files": [
      "src/pilot/cohort_clean_rates.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1149 (17-07-2026, Sonnet 4.6 claude-sonnet-4-6): the guard counts provenance.h_reconstructed across the WHOLE store regardless of any language field -- it is not RU/EN-branched code at all (the store currently carries 0 EN rows, but the guard would cover EN rows identically the moment any exist). Guards the exact failure class from PR #510/Uprava FINDINGS §95 (h is None fell 468->0 and became invisible to the only query that could find it) from recurring silently. Pinned by test_h_reconstructed_regression_guard, which proves both directions against a synthetic (non-gitignored, deterministic) store: 467 markers -> AssertionError, 468 -> clean pass, and a matching authorized manifest -> accepted.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/cohort_clean_rates.py": "1d2a1da68eb4e897422696ec42c7845cecf9e94a2a0b8a587f8a68d3b44bfb7e",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "translation_field_fidelity_guard_h1152",
    "mechanism": "accept()'s countOf() fidelity check (see accept_sanloss_soft_gate_h960) counted <ls>/{#..#} occurrences ONLY in the sense.german source-echo field -- it proved the model copied the masked German back out faithfully, never that the TRANSLATION field (sense.russian / sense.english) preserved the same spans. A {Tn} could be dropped from the translation alone with zero effect on the guard. Added countOfField(card, TARGET_FIELD, re) and a second hard check in accept() running the identical count over the actual target-language field, TARGET_FIELD being a new JS const interpolated from the same Python `field` variable (`'english'`/`'russian'`) already used to build RESTORE_SPEC.",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/accept_sensecount_test.js"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1152 guard 2 (17-07-2026, Sonnet 4.6 claude-sonnet-4-6), closing H1070's r102 finding (PWG->EN FU1 pilot, vac~~h0_00_pwg00: a {#uc#} span inside a <F> footnote survived the german echo 33/33 but was dropped from english 32/33 -- invisible to the pre-existing check because it never reads the translation field). accept() is lang-parameterized code shared by both lanes (field = 'russian' or 'english', same code path); the new check is symmetric and applies identically to RU and EN generation. Verified against the live RU regression suite: window_selftest.py full run stays green (137/137 baseline, +2 new content-check tests for guards 1/3), and the new/updated fixtures in accept_sensecount_test.js reproduce the exact r102 shape (RED before this change -- proven via git-stash against the pre-fix accept(), the fixture is silently ACCEPTED -- GREEN after). No RU store data touched; this only changes the generation-time accept-path gate for FUTURE generation, never re-validates the 11,605 already-promoted RU rows.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/accept_sensecount_test.js": "e3ef2b0fb016f6697bcf4c2d087c15b0f76d3422ee70193f064370ab34e3bad1"
    }
  },
  {
    "id": "en_polyseme_judge_guard_h1152",
    "mechanism": "H1070 finding #1 (German homograph/polyseme mistranslation, e.g. r155 braut/Braut->betroth, r119 Vergleich->comparison): markup stays intact and the English reads fluently, so no deterministic gate can see this class. Guard 1 is judge-rubric + generation-prompt only -- a checklist line under term-mistranslation in gen_fidelity_judge_en.py's RUBRIC, and a matching HARD RULE 5 in tr_en.txt telling the generator to pick the sense the Sanskrit lemma licenses, never the frequent German sense.",
    "files": [
      "src/pilot/gen_fidelity_judge_en.py",
      "src/pilot/tr_en.txt"
    ],
    "languages": [
      "en"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "EN-only by construction: RU translation uses a separate prompt/judge pair (extract_conv_tr()/gen_fidelity_judge.py) with its own German-polyseme handling history (not audited by this handoff); tr_en.txt and gen_fidelity_judge_en.py are the EN-specific self-contained prompt/rubric pair H1070 named. Pinned by test_h1152_guard1_en_polyseme_checklist (content check: RUBRIC carries the named terms, tr_en.txt carries the HARD RULE).",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_fidelity_judge_en.py": "7e46d8084fdced586dfb8f59232c9089aae051354adaa95dbc2f2d696182b617",
      "src/pilot/tr_en.txt": "cd2fcb914c381fc466ac87c9d9885a24e45ff84a964f633dfe207fc8ae5556d2"
    }
  },
  {
    "id": "en_de_residue_soft_class_h1152",
    "mechanism": "H1070 finding #3 (12/170 FU1 rows: pure cross-reference rows and NWS German locked inside {#..#}, dominant residual, deterministically detectable): extends audit_window_en.py's soft-flag machinery (the DE-RESIDUE family) with XREF-ONLY (german carries no gloss prose, only a Vgl./s./fgg. cross-reference apparatus) and NWS-DE-LOCKED (German function-word/umlaut text trapped inside a {#..#} span -- an NWS masking miss, so it never reached the translator). Both SOFT (report-only, never --strict-blocking) -- meaning/markup stay intact; this is a coverage-accounting fix so these rows stop being counted as ordinary translated prose.",
    "files": [
      "src/pilot/audit_window_en.py",
      "src/pilot/window_selftest.py"
    ],
    "languages": [
      "en"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "EN-only by construction: the RU audit path (audit_window.py + prompt_rule_audit.py) is wired around .merged.md/.raw.txt files and Russian-specific semantic checks, per audit_window_en.py's own module docstring (\"the RU gate ... is wired around ... Russian-specific semantic checks, so the PWG->EN pilot ran with --no-audit. This is the EN sibling\"); XREF-ONLY/NWS-DE-LOCKED are new, EN-only soft flags with no RU counterpart to port -- the RU gate's own dropped_sanskrit_span in prompt_rule_audit.markup_sigla_risks already covers RU's analogous case and was not touched. Pinned by test_h1152_guard3_xref_only_and_nws_de_locked.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/audit_window_en.py": "73398beb59c272ceb8bbcfdb1649e241a83d4f8447f1aae33c4c3c1e3e5e2862",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c"
    }
  },
  {
    "id": "h1209_controller_worker_rig",
    "mechanism": "H1209 controller-worker Workflow rig (Opus controller + Sonnet workers): prep/inject/build scripts, canonical-aligned deterministic in-JS gates (HARD {Tn} multiset fidelity on german+translation, shortfall-only sense gate vs source_senses), and the authoritative post-run canonical audit (restore + accept()-battery + schema)",
    "files": [
      "src/pilot/h1209/wf_template.js",
      "src/pilot/h1209/prep_slice.py",
      "src/pilot/h1209/build_args.py",
      "src/pilot/h1209/canonical_audit.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "GAP",
    "note": "Validated 18-07-2026 on the RU 3-card slice (v1 exposed the naive-senses equality-gate defect: workers displaced source {Tn} spans into unrestorable card.notes; v2 gates are direction-aligned with accept()). canonical_audit.py is already field-parameterized (reads manifest field, russian/english); wf_template.js still hardcodes the russian target field and a RU controller prompt. The EN variant is owed by the same handoff’s mini-EN step, which must also wire the H1070/H1152 EN guards + audit_window_en gates.",
    "tracking": "H1209 (Uprava/handoffs/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md), mini-EN step",
    "verified_sha256": {
      "src/pilot/h1209/wf_template.js": "e233674cbfdd228afd7c121a0a6d2c97ad047a13af8076c8af8c6e1733a03460",
      "src/pilot/h1209/prep_slice.py": "d065d685dced6ef237ca9ba65836d0e3426105d563bcde7390a61572bcd9a59c",
      "src/pilot/h1209/build_args.py": "6f245108c60ae7c777c66900c1da4a53670399e949fbc474b6556d6bd0ed3024",
      "src/pilot/h1209/canonical_audit.py": "5866af157fd42ae76a903d448a1762a5224411e9842197eed870d21ee36d0315"
    }
  },
  {
    "id": "ls_link_enrichment_panini_spr_h1307",
    "mechanism": "H1307 <ls> link enrichment: Pāṇini P. gains guarded chapter/book browse patterns (2-param a,p -> /sutraani/a/p, 1-param a -> /sutraani/a; pada 1-4 / adhyaya 1-8 guarded so page-refs like 'P. II, S. 3' and bogus 'P. 1,23' never mislink); Spr. (II) N gains a full-text hover tooltip (IAST + German from the Indische Sprüche corpus) via spr_fulltext, with a 1st-ed edition guard (plain Spr. N never resolves against the 2nd-ed corpus); the shared _render()/_ls_tooltip layer carries both.",
    "files": [
      "src/ls_resolver.py",
      "src/spr_fulltext.py",
      "src/pilot/build_article_site.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1307 (19-07-2026). The enrichment is render-time and keys only on the citation abbreviation + numbers (P. adhyaya/pada/sutra, Spr. (II) saying number) — never on RU/EN translation prose — so both language editions' <ls> link-targets and tooltips share it with no --lang branch. The Spr. (II) saying text is identical across editions. Pinned by src/pilot/ls_enrichment_selftest.py.",
    "tracking": "",
    "verified_sha256": {
      "src/ls_resolver.py": "78f1a17e80d7b0ed9fb4dd79fdd5c076f8ef2f1fee245ab0cda9f5e4da8fcfec",
      "src/spr_fulltext.py": "446fe8ce8146cfdda3a0cd0b2e6f62c3b76e08cfb872823116549ed3992fe0d5",
      "src/pilot/build_article_site.py": "09ce9d51e88bcfdebfb86ac74b86d57317faa6f182922041a212b96871b24987"
    }
  },
  {
    "id": "german_prose_residue_h1302",
    "mechanism": "H1302 German-prose-residue detector + deterministic --store fixer + shared residue token list wired into BOTH gates. german_residue_scan.py masks protected spans ({%…%}/{#…#}/«…»/<ab|ls|is|lex>/<div…>/[Page…]/[NWS:…]) and flags untranslated German prose (citation zu/bei, 'mit dem <ab>acc.</ab>', 'so v. a.', connectives, 'mit Ergänzung von'), classing each hit a=deterministic-fixable / b=retranslate / c=proper-name-false-positive; fix_german_connectives.py --store applies the class-a subs to the RU field of the canonical store; foreign_literal_guards.GERMAN_PROSE_RESIDUE(_EN) is the single shared token source unioned into the RU gate (prompt_rule_audit GERMAN_RESIDUE/GERMAN_GLOSS_WORDS) and the EN gate (audit_window_en DE_WORDS).",
    "files": [
      "src/pilot/german_residue_scan.py",
      "src/pilot/fix_german_connectives.py",
      "src/pilot/foreign_literal_guards.py",
      "src/pilot/prompt_rule_audit.py",
      "src/pilot/audit_window_en.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "German residue is a defect in BOTH output languages, so the token source and the detector logic are shared. The EN gate unions only GERMAN_PROSE_RESIDUE_EN_SAFE (German-only tokens with no English homograph — 'so'/'als'/'aus'/'am'/'in'/'ein'/'wie' are DELIBERATELY excluded from the EN list so they never false-positive on ordinary English, while the RU gate uses the full set since none are legitimate Russian). Detector precision measured 50/50=1.00 on a hand-classified store sample (H1302, 19-07-2026); the deterministic --store pass fixed 690 class-a hits across 486 rows and repaired the 3 H178-DA-rejected cards.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/german_residue_scan.py": "95b23669fdf96759202a22a06512c6bdc2d9de6e8a1c73809bdead3a26e991db",
      "src/pilot/fix_german_connectives.py": "6a5cceb58cd7c989df819703dff777bb635ee979c7178c55ceccce199a3737a8",
      "src/pilot/foreign_literal_guards.py": "e7eaccfb846ff805b585b1c6413ec84b71970dd7fdddfc6abef90fcf04650b93",
      "src/pilot/prompt_rule_audit.py": "a937af2156a765a5496ee9ca69503f777d55a02238c255ffb0b12e0569435338",
      "src/pilot/audit_window_en.py": "73398beb59c272ceb8bbcfdb1649e241a83d4f8447f1aae33c4c3c1e3e5e2862"
    }
  },
  {
    "id": "tnmask_provenance_persistence",
    "mechanism": "accept() persists the pre-restore {Tn} pairing (candidate `got` vs masked-skeleton `want`, brace-stripped) on each card, and BOTH promote lanes carry it to provenance.tnmask, so a soft (un-rejected) TNMASK expansion is measurable offline from a promoted row (H1226; offline reader src/pilot/tnmask_offline.py)",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/promote_final_cards.py",
      "src/promote_en.py",
      "src/pilot/tnmask_offline.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1226: the {Tn} pairing is stamped in the SHARED accept() (runs for both languages) and BOTH promote lanes (promote_final_cards.py RU, promote_en.py EN) carry it to provenance.tnmask, so neither store silently drops the field accept() stamps. Only accept() stamps it: the heal path's acceptFrag hard-rejects fragment {Tn} mismatches, so no un-rejected expansion reaches a healed card. Makes the TNMASK false-flag rate MEASURABLE (H1150 DO_NOT_ARM, denominator 1); TNMASK_HARD_REJECT stays = false — arming is a human @DECIDE. Pinned by window_selftest.test_tnmask_persist_and_offline_detect + tnmask_offline.selftest.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/promote_en.py": "f801b86d267f346e2a11ebbee681103e68e01f6520da0e70e4a20b460ee27d9d",
      "src/pilot/tnmask_offline.py": "c857fe425fadbe18c1cdf398892f53b590709048ca66faf94fd05e046730ffea"
    }
  },
  {
    "id": "ru_style_mechanical_yo_terseness",
    "mechanism": "H1305 mechanical RU style sweep + gate: R1 no letter ё anywhere in RU output (whitelist: standalone «всё»/«Всё» only, disambiguating все/всё; «всё-таки» defaults to е like every other ё-word); R2 «вместо» -> «вм.» and R3 «в значении» -> «в знач.» in editorial metalanguage (measured 0/60 and 0/24 false positives respectively on the canonical store -- applied UNRESTRICTED, well under the handoff's <2% threshold); R4 `ed. Bomb.` -> «Бомбейская ред.» in free PROSE only (282 in-<ls> occurrences -- 221 standalone + 61 embedded citations -- left verbatim because src/pwg_sources.py.source_key()/resolve() key the citation off that exact Latin text; only 1 genuine free-prose occurrence in the whole store qualified). src/ru_style_sweep.py sweeps the canonical store (dry-run default, --apply, --selftest) and its scan_violations() is reused verbatim by the audit_window.py `ru_style` gate (--wf mode) so future-generation compliance and the historical-store sweep share one detector. Prompt HARD RULE 9 in run_pilot_wf.js CONV/TR wires the same rules into future generation; pinned in prompt_rule_audit.py RULES (ru_style_no_yo / ru_style_terse_metalanguage / ru_style_ed_bomb_siglum) so a future template edit that drops them fails --fail-on-missing.",
    "files": [
      "src/ru_style_sweep.py",
      "src/pilot/audit_window.py",
      "src/pilot/window_selftest.py",
      "src/pilot/prompt_rule_audit.py",
      "src/pilot/run_pilot_wf.js"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "Russian ё-orthography policy and Russian terse editorial metalanguage («вм.», «в знач.», «Бомбейская ред.») have no EN counterpart by construction -- EN output contains no Cyrillic and uses its own English editorial conventions (no ё letter, no «вместо»/«в значении» abbreviation question). Register §4's h178-vote row \"(SHARED)\" annotation is refined here: the GATE WIRING MECHANISM (an RU-only-detector slot added to audit_window.py's existing commands list, alongside translation/stage2_mechanical/coverage/sense_dupes) is SHARED-capable machinery -- a hypothetical 3rd Cyrillic-scripted language could reuse the same gate-list slot -- but the RULES THEMSELVES (R1-R4, the ё-whitelist, the вм./в знач. terse forms) are RU-only INTENTIONAL-DIVERGENCE, not something to port to audit_window_en.py, which this handoff deliberately does not touch.",
    "tracking": "",
    "verified_sha256": {
      "src/ru_style_sweep.py": "018aee3c3262405b493a5dac74f937684fcbac6f763923583d83604a4e5dcb93",
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/window_selftest.py": "e1f72d0b48a3df8fb57521f363ff6e7c713632d541b59536bba56d301bb82a7c",
      "src/pilot/prompt_rule_audit.py": "a937af2156a765a5496ee9ca69503f777d55a02238c255ffb0b12e0569435338",
      "src/pilot/run_pilot_wf.js": "b194ceb034b458ffc470e7feb2d9c921c6f391c88088e7f05a00a1e790bcf7a4"
    }
  },
  {
    "id": "h1339_store_promote_hardening",
    "mechanism": "H1339 B02/B03/B08/B20/B21: heal-stitched and TM-served cards are schema-complete at construction/serve (iast/notes + record h/grammar; legacy sidecar rows refused fail-closed); record.grammar joins PROMOTED_COMMON so tn_residue/backfill see the full store-written masked set; store --merge is better-attempt-wins (complete>partial, fewer missing fragments win); --gen-model-version cross-checked against manifest execution.model_identifier and prov.model derived from the version",
    "files": [
      "src/card_fields.py",
      "src/promote_final_cards.py",
      "src/pilot/translation_memory.py",
      "src/pilot/headless_worker.py",
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
      "src/card_fields.py": "976c5aa943a35da1691e2ce72e9cb4a14ac53d3bae37f8c68345cc68cb233e2b",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac",
      "src/pilot/headless_worker.py": "bc43daf54de2d9065d55a2d77a7b49c51303bcfdc4d0ac5cb7ed362e3936d4c7",
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561"
    }
  },
  {
    "id": "h1339_en_promote_parity_gap",
    "mechanism": "promote_en.py has NO {Tn}-residue gate, NO better-attempt-wins merge and NO model-identity cross-check — the EN twin of the B08/B20/B21 promote hardening classes",
    "files": [
      "src/promote_en.py"
    ],
    "languages": [
      "en"
    ],
    "verdict": "GAP",
    "note": "",
    "tracking": "H1339 Tier-B report pwg_ru/h1339/H1339_TIER_B_STATUS_2026-07-19.md — port before the first real promote_en run (EN store currently 0 rows; H1209 mini-EN is the first consumer)",
    "verified_sha256": {
      "src/promote_en.py": "f801b86d267f346e2a11ebbee681103e68e01f6520da0e70e4a20b460ee27d9d"
    }
  },
  {
    "id": "h1339_worktree_canonical_sidecars",
    "mechanism": "H1339 B04/B09: the four TM sidecars (card/suggest/denylist/frag) and the ru_coverage store/denominator resolve via store_path canonical resolvers — ONE logical sidecar set per checkout tree, worktree-safe (0-TM-hit worktree runs and empty-store coverage verdicts eliminated)",
    "files": [
      "src/store_path.py",
      "src/pilot/translation_memory.py",
      "src/pilot/ru_coverage.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/store_path.py": "4967ab7ea748da995367fd0520f89f4bf9a39b84c428310314291b85be26f73c",
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac",
      "src/pilot/ru_coverage.py": "bf08bc3e79a80907dfc7df4e59cead0c026e04cf9cc621359630daecc98b46c3"
    }
  },
  {
    "id": "h1339_requeue_materialisation_unattended",
    "mechanism": "H1339 A4/B16/B18: a supervisor requeue work-item materialises a REAL coordinator requeue attempt + ::rqNN-kind job (prepare-requeue -> import-requeue, idempotent, loud when unmaterialisable); cmd_run_once filters the roster to claim-eligible accounts BEFORE the concurrency slice; reset-failed is the audited scoped exit from the terminal failed state",
    "files": [
      "src/pilot/bounded_staged_run.py",
      "src/pilot/bounded_supervisor.py",
      "src/pilot/max_account_orchestrator.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/bounded_staged_run.py": "fe79ff9812e26ec5f3fd3ed9a0462855e801d7711b4634a2e9eeeffface4c68c",
      "src/pilot/bounded_supervisor.py": "d23e508463d5bca4e161e9a20769221186d85e7a68ef5c8e3878125997478446",
      "src/pilot/max_account_orchestrator.py": "03a59329720faa2cdbb56dd71284128ef3db62e301fb650cf51d4a2d4fec3a68"
    }
  },
  {
    "id": "h1339_fragment_prompt_evidence",
    "mechanism": "H1339 B01: heal/presplit fragment prompts carry the card's own evidence (per-card grammar — the only grammar in nominal windows — and the portrait) on BOTH twins (JS healGroup and headless fragment_prompt), matching the whole-card batch lane",
    "files": [
      "src/pilot/gen_opt_harness2.py",
      "src/pilot/headless_worker.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/gen_opt_harness2.py": "93376ed1c55d950327a368f7b11a854d9fbf289e629c7e241e5479e6af396561",
      "src/pilot/headless_worker.py": "bc43daf54de2d9065d55a2d77a7b49c51303bcfdc4d0ac5cb7ed362e3936d4c7"
    }
  },
  {
    "id": "h1339_requeue_blast_radius_guards",
    "mechanism": "H1339 B11/B12: requeue_from_audit refuses a CRASHED audit's blast-radius requeue list; the TM denylist gains an unblock supersede lifecycle and promote_final_cards clears exactly the denials its landed replacements supersede",
    "files": [
      "src/pilot/requeue_from_audit.py",
      "src/pilot/translation_memory.py",
      "src/promote_final_cards.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/requeue_from_audit.py": "687f9861e3dbcc3ec10f730330cd83a88348f8ef59d3a17383950c77e7bd03d2",
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03"
    }
  },
  {
    "id": "h1339_siglum_citation_precision",
    "mechanism": "H1339 B13: translated_source_siglum fires only on citation-shaped Russian (spelled-out work name + numeric locator; манускрипт excluded), no longer on legitimate prose",
    "files": [
      "src/pilot/prompt_rule_audit.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "RU-prose-specific detector over Cyrillic work names; the EN lane's residue checks are audit_window_en's own classes — nothing portable here",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/prompt_rule_audit.py": "a937af2156a765a5496ee9ca69503f777d55a02238c255ffb0b12e0569435338"
    }
  },
  {
    "id": "h1339_measurement_integrity",
    "mechanism": "H1339 B14/B15: perf_preflight prices per LANE (batched agents at the measured healthy 60K-tok calibration, presplit fragment agents at the pril10 184K monster calibration — healthy windows no longer refused on fiction, the kAla gate keeps its teeth); probe_log refuses all-null outcome rows, recovering figures from note key=int pairs first",
    "files": [
      "src/pilot/perf_preflight.py",
      "src/pilot/probe_log.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/perf_preflight.py": "3dc1d44f0054da4278e7c6eb34f03477b697431e22bcf7ea0c201afad2009e13",
      "src/pilot/probe_log.py": "bc5d21b48541c410eaed9b4bccb97619272b4ef542f6ce76257d247303efb067"
    }
  },
  {
    "id": "h1339_ru_audit_chain_routing",
    "mechanism": "H1339 B10/B19: save_and_audit passes --write-requeue (requeue singletons refreshed in the factory save pass); stage2_pregate/audit_translation resolve merged.md with the dual safe_name lookup (double-encoded collector output no longer false-flags NO-OUTPUT)",
    "files": [
      "save_and_audit.py",
      "src/stage2_pregate.py",
      "src/audit_translation.py"
    ],
    "languages": [
      "ru"
    ],
    "verdict": "INTENTIONAL-DIVERGENCE",
    "note": "the merged.md render chain and the requeue singleton files are RU-lane surfaces; audit_window_en has no requeue-singleton machinery (that asymmetry is the standing audit_window_en gap family, tracked by the existing en-lane entries)",
    "tracking": "",
    "verified_sha256": {
      "save_and_audit.py": "e1d7a3b6c5a8c47dbc414dbcf991e9ead82b76a013e4624cffe76066e576c8b6",
      "src/stage2_pregate.py": "8f07422d3c416e32d1882f0777d56cc44ba781d19c8097fd9500ddefbfd22945",
      "src/audit_translation.py": "0c8bb16fb854f18f31ca0838bc18e436eb0e75f55a28ff0e8f1336c09dcb7016"
    }
  },
  {
    "id": "en_coverage_card_done_semantics",
    "mechanism": "The FL4 coverage-complete rule (a card is done iff it has >=1 slot AND every German-bearing slot carries the target field) lives in ONE --lang-parameterized kernel, card_coverage.card_done(card, field), consumed by en_residual_keys.py (field='english')",
    "files": [
      "src/pilot/card_coverage.py",
      "src/pilot/en_residual_keys.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1425 W1 (21-07-2026, Opus 4.8 claude-opus-4-8): the card-done semantics were an EN-only reimplementation (en_residual_keys.en_coverage/card_done); extracted to the shared --lang kernel src/pilot/card_coverage.py (slot_coverage/card_done(card, field)), so a fix to the FL4 rule reaches any language that calls it — en_residual_keys is now a thin field='english' consumer (output byte-identical, verified against the pre-refactor inline logic). NOTE: ru_coverage.py (tracked under h1339_worktree_canonical_sidecars) does a DIFFERENT, coarser check — per-root sub-card PRESENCE in the store, not per-slot completeness — so it still carries the FL4 blindspot this kernel fixes (a 1/40-translated sub-card counts as 'present'); wiring card_coverage into ru_coverage is a behaviour change to a live gate, deferred as an H1425 follow-up. Pinned by window_selftest.test_card_coverage_lang_symmetric.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/en_residual_keys.py": "84d1c2f1f9e81ec30766d34ba477ceabd09047390cf0473b234626009393c0cb",
      "src/pilot/card_coverage.py": "45c2adbb142d9fc112324c3e7b43089e5d0c6243085470169d42b38c5b59a62c"
    }
  },
  {
    "id": "degenerate_xref_vocab_shared",
    "mechanism": "The cross-reference / degenerate-passthrough vocabulary (s., vgl., u., Nachträge, ...) is ONE shared frozenset (xref_vocab.DEGENERATE_XREF_WORDS), consumed by the RU generation lane (gen_opt_harness2.degenerate_passthrough_card) and the EN auditor (audit_window_en.xref_only)",
    "files": [
      "src/pilot/xref_vocab.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1425 W2 (21-07-2026, Opus 4.8 claude-opus-4-8): was two byte-identical independently-authored copies (gen_opt_harness2._DEGENERATE_WORDS + audit_window_en._XREF_WORDS) — the C-01 drift class the codebase already consolidated portrait_key_iast for. Extracted to a dependency-free module both import (the EN auditor deliberately cannot import gen_opt_harness2's heavy pwg_mask/corpus_gate stack for one word set). Pinned by window_selftest.test_degenerate_xref_vocab_single_source (asserts object identity, not just equality). REASSESSMENT (W2): the rest of audit_window_en's reusable surfaces are ALREADY converged — the German-residue word list via foreign_literal_guards.py, and the whole-dropped-sense SAN-LOSS gate via sense_count.py — and its remaining gates (DUP / MISSING-EN / MARKUP-LOSS / xref_only / nws_de_locked) are EN-audit-time-specific BY ARCHITECTURE (RU per-card fidelity is generation-time in the harness accept()/countOfField, not a symmetric Python auditor), i.e. intentional divergence, not a wholesale reimplementation to force-merge. So H1425 W2's convergence target is materially smaller than first scoped.",
    "tracking": "",
    "verified_sha256": {
      "src/pilot/xref_vocab.py": "922940d5ccb4667c361ac15f66f1fcf0a41446419a74aff7feea359585e7c5ec"
    }
  },
  {
    "id": "h1386_resume_recovery_and_medium50",
    "mechanism": "H1386 post-H1339 review landing set: C1 bounded --resume passes the lease-id SET to cmd_recover (+_scope_sql dict/str TypeError, None-output window fails loudly); C2 materialize_requeue resumes a post-audit origin with a completed ::rq job; C3 fragment-denylist-aware build_frags seen-scan + recursive '**' requeue-output harvest glob + append-order tiebreak in best_reusable; D1 h1209 payload v3 prompt_common hoist + WORKFLOW_SCRIPT_CAP refusal + prep_slice --keys/--chunk + canonical_audit chunk merge; D2 identity-checked promote-lock reclaim; D3 per-lease store_delta from the batch report; D4 PWG_COORDINATOR_DIR on all bounded coordinator subprocesses; D5 batch-mode --dry-run/--force/--init-store refusal; P3b canonical mw_en_tm resolution; P3c reset-failed origin-lease matching + failed-id messages; P3d/e run_py_inproc KeyboardInterrupt/string-exit semantics; P3f hermetic bench (PWG_INPUT_DIR/PWG_EVENTS_PATH sandbox + teardown); P3g batch null-subcard gate; P3h stale_check v2 execution/provenance cross-check; P3j probe_log falsy-zero clean recovery; OPT coordinator prepare-batch (in-process prepare children).",
    "files": [
      "src/pilot/bounded_staged_run.py",
      "src/pilot/bounded_supervisor.py",
      "src/pilot/max_account_orchestrator.py",
      "src/pilot/translation_memory.py",
      "src/pilot/coordinator.py",
      "src/promote_final_cards.py",
      "src/promote_lock.py",
      "src/pilot/audit_window.py",
      "src/pilot/window_common.py",
      "src/pilot/dashboard_events.py",
      "src/pilot/window_provenance.py",
      "src/pilot/probe_log.py"
    ],
    "languages": [
      "ru",
      "en"
    ],
    "verdict": "SHARED",
    "note": "H1386 (22-07-2026, Fable 5 claude-fable-5). Every fix is language-neutral orchestration/persistence mechanics -- none introduces a --lang branch. Lane facts checked per the handoff: the frag TM half of C3 (build_frags/load_frag_tm/best_reusable) is --lang-parameterized so both lanes get it; the recursive harvest glob + D3 per-lease store_delta + P3g batch gate live in the RU staged/coordinator lane ONLY because the EN promote lane (promote_en.py) by design has no fragment harvest and no batch transaction (its INTENTIONAL-DIVERGENCE ruling is H1425 W3, unchanged); P3b is the EN lane's own seed feed; the h1209 rig (D1) is field-parameterized (payload['field']), so a future EN slice inherits prompt_common/chunking as-is; PWG_INPUT_DIR (P3f) is honored by both audit_window and audit_window_en. Pinned by bounded_staged_run_selftest tests l/m, window_selftest test_h1386_c3_frag_unblock_serves_replacement + test_h1386_d1_medium50_script_size_cap, promote_lock/promote_final_cards selftests, and the h1339_offline_bench deterministic signature (batch == per-lease).",
    "tracking": "H1386",
    "verified_sha256": {
      "src/pilot/bounded_staged_run.py": "fe79ff9812e26ec5f3fd3ed9a0462855e801d7711b4634a2e9eeeffface4c68c",
      "src/pilot/bounded_supervisor.py": "d23e508463d5bca4e161e9a20769221186d85e7a68ef5c8e3878125997478446",
      "src/pilot/max_account_orchestrator.py": "03a59329720faa2cdbb56dd71284128ef3db62e301fb650cf51d4a2d4fec3a68",
      "src/pilot/translation_memory.py": "5027755b891fce785f8b119fe95cfbb6c2aca0322ebe6a4bc6844878bf2dfbac",
      "src/pilot/coordinator.py": "e9b340cc17511e1268ae7fe839d1e74b92d0dac5c810332a3dfc7f4c2cb51e0a",
      "src/promote_final_cards.py": "72e276422c5624d0849178c581f3267220050f5490cc09771b73ee7329dcef03",
      "src/promote_lock.py": "f8dda14a7423dfecac77893f10f7735361db8bd6c79297172243aafaf1d28ef4",
      "src/pilot/audit_window.py": "3ef6a0ef43d12578733a8db72dafe4aa31d5a457c220a4abfacdc605417817f2",
      "src/pilot/window_common.py": "2d6926ba3a2e99f788641637b2cb6f2f9637ecb7f4e1b1c1561a367c8dd81e93",
      "src/pilot/dashboard_events.py": "342dfa7e83ca2b4da78b719ec95126e2fe5a32b2e8d731fee323e3bc44fe7a7e",
      "src/pilot/window_provenance.py": "2f1240e321004228d94f6bea7ae661a896c4bc93c60f9d47871d248766900d50",
      "src/pilot/probe_log.py": "bc5d21b48541c410eaed9b4bccb97619272b4ef542f6ce76257d247303efb067"
    }
  }
]
```

```json lang_parity_coverage
{
  "note": "Curated exceptions for the coverage guard (lang_parity_check.coverage_check). A language-aware pipeline .py under src/ or src/pilot/ must be EITHER tracked by a ledger entry above OR listed here with a one-line reason. Each of these is a read-only sampler / QA-sheet generator / benchmark / triage reporter that mentions english/--lang but produces reports or samples, not pipeline behaviour — a change cannot cause RU/EN behavioural drift. Classified 21-07-2026 by an Opus 4.8 (claude-opus-4-8) 8-agent fan-out + adversarial audit (7 exempt; the 8th, en_residual_keys.py, became the en_coverage_card_done_semantics ledger entry).",
  "exempt": {
    "src/build_citation_index.py": "Read-only citation-coverage reporter: reads DE/RU/EN <ls> stores to count/resolve citations and writes only Markdown+JSON coverage reports; never writes the store, transforms cards, or emits gate/promote verdicts.",
    "src/fidelity_sample_en.py": "Read-only stratified sampler: reads wf_output.en.*.json and writes only fidelity_sample_en.jsonl for the Opus EN fidelity judge; no store write, no gate verdict, no card transform — a change alters only the eval sample's composition.",
    "src/gold_sample_en.py": "Read-only human-gold sampler: loads the store, selects rows carrying `en`, writes a working JSONL sample + blank reviewer CSV + METHODS note; never writes back to the store or emits a gate verdict.",
    "src/pilot/calibrate_perf_harness.py": "Benchmark scaffolding generator: builds scratch harness arms + manifest + REPORT_TEMPLATE and passes --lang straight through to gen_opt_harness2.py (the actual parity surface); never translates/audits/gates/promotes or writes the store.",
    "src/pilot/en_split_triage.py": "Pure triage reporter: json.load stores + read source inputs, then print() a SPLIT/RETRY/MISSING-INPUT report for a human (not piped into an automated requeue); no store write, card transform, or gate verdict.",
    "src/pilot/h1339_offline_bench.py": "Frozen offline benchmark: drives real coordinator/promote commands ONLY inside a scratch env-overridden sandbox with a deterministic fake model to time the path; defines no translate/audit/promote logic — a change alters timing/fixtures, not production behavior.",
    "src/pilot/lang_parity_check.py": "The parity-coverage guard ITSELF: it contains the LANG_SIGNAL detection regexes (english/--lang/FIELD[/CARD_FIELD) as string literals, so the detector matches its own patterns. Meta-tooling that ENFORCES parity, not a translation surface — a change alters the guard's behaviour, not RU/EN pipeline output.",
    "src/pilot/trilingual_sample.py": "Read-only join sampler: aligns already-produced RU (wf_output.sc.*) and EN (wf_output.en.*) senses by key, strips markup, prints/writes a DE|RU|EN comparison table; never transforms cards, writes the store, or emits gate verdicts."
  }
}
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
