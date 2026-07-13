# pwg_ru — changelog

How the Russian edition of the Petersburg Dictionary (PWG, Böhtlingk–Roth)
evolved. Newest first. This is the *project* changelog (method + pipeline); the
data stores are gitignored and versioned by their build provenance.

See also: [METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md) (where we want to go),
[failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md) (what went wrong and
how it got better), [APRESJAN.md](APRESJAN.md) (the theory we build on).

## [Unreleased]

- **H858 no-PWG sense-fidelity: fixed a STRANDED-ANCHOR false positive; reclaimed 7
  cards, zero regeneration.** `_pilot_collect.render()` rendered the model's free-text
  `notes` verbatim, so a `notes` mention of a masking token (*"Masked span {T1} is a
  citation…"*) tripped `stage2_pregate`'s stranded-anchor scan on otherwise-clean
  cards. New `_pilot_collect.strip_mask_tokens()` strips `{T<n>}`/`{Tn}` from the notes
  render (deliverable german/russian untouched); pinned by a `window_selftest` case.
  Re-audit clean counts rose w08 1→2, rq1 6→11, w09 3→9; 7 distinct cards promoted
  (store 11,567 → 11,577). Two real residual bugs documented for follow-up (grammar-field
  stranding; `{#…#}`-span drops needing german-field source-anchoring). See
  [`src/pilot/RUN_LOG.md`](src/pilot/RUN_LOG.md) 2026-07-13 H858 block.
- **H852 — H818 Windows headless-invocation defects fixed + verified live.**
  `claude_argv_prefix()` (node-direct, bypasses the `.cmd`/cmd.exe `--json-schema`
  corruption) in `headless_worker.call()`/`live_probe`/`profile_status`; `--claude-bin`
  threaded through `staged-run → run_once → run_claimed`; `is_rate_limited()` ignores
  the `manifest_sha256` (no false 429 park); `staged-run` parked-account halt (no
  busy-loop). Re-run: presplit canary GO, generation `done`/`success`, no false park,
  no livelock. Adds D-A/D-C unit tests; LANG_PARITY re-verified SHARED.
- H818 Windows-100 readiness: headless Workflow-parity retry/split/heal/stitch,
  deterministic 5×20 preparation, credential-safe append-only run events and bug
  census, strict headword/subcard and positive store-delta GO gates, a non-promoting
  live presplit canary, and scheduler/promotion fault injection.
- **H818 Windows live acceptance (13-07-2026): NO-GO — auth resolved, headless
  generation non-functional on Windows.** `init` + ≥5 KB `live_probe` passed, all
  offline gates green, store present (11,562), but the presplit canary and step-4
  window failed before any promotion (store unchanged). Four defects: `.cmd`-shim
  cmd.exe corruption of the `--json-schema` argv (fix = `node cli-wrapper.cjs`
  direct, verified); `run_claimed` not forwarding `--claude-bin`; `RATE_LIMIT`
  regex matching the `manifest_sha256`; `staged-run` parked-account livelock.
  Report: [H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md](H818_WINDOWS_LIVE_ACCEPTANCE_2026-07-13.md);
  fixes: [H852](https://github.com/gasyoun/Uprava/blob/main/handoffs/H852-Opus_SanskritLexicography_h818-windows-headless-invocation-fix_13.07.26.md).

### H834 — nominal key-echo tolerance also accepts the SLP1 headword + `~~<layer>` suffix
- [`gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py): the H220 nominal re-key tolerance now
  recovers a card when the model echoes the clean SLP1 headword **with the sub-card suffix kept**
  (`avyAhata~~h0_zz_pw` for the stem `avy_ahata~~h0_zz_pw`), not only the bare SLP1 — still gated on
  `META.nominal` + a single unambiguous rival (PWG-root strict matching untouched). Fixes the
  `missing-or-mismatched-key` failure on the H255 `avy_ahata` content-hard card. Extended
  `window_selftest.test_nominal_key_echo_tolerance_scoped`; suite + `lang_parity_check.py` green.
- **Finding:** verify (`no_pwg_contentfix`) confirmed the key fix (avy_ahata now gets past the key)
  and revealed that **both** H255 "content-hard" cards (`avy_ahata`, `avyagra`) share ONE remaining
  root cause — the model drops **short embedded derived-form `{#…#}` spans** (`˚tva`, `˚m`,
  single-letter forms). That placeholder-fidelity/omission issue needs a separate fix (deterministic
  german-field anchoring or a prompt change), tracked as the precise residual.

### H833 / E2 (H350 backlog #3) — sense-genre vs DCS attestation: thesis NOT supported
- New research analysis [`research/analyze_sense_genre_attestation.py`](research/analyze_sense_genre_attestation.py)
  tests memo §E2: does per-sense citation-genre predict DCS corpus attestation
  *better* than the lemma's aggregate genre? Reuses `annotate_genres.genres_for_text`
  (H339) for genre; no reimplementation, no DCS→feature leakage.
- **Result (n=1316 headword lemmas, 49.8% DCS-attested):** sense-resolution genre
  (Model B, AUC 0.710) shows **no advantage** over the lemma-union representation
  (Model A, AUC 0.716); ΔAUC(B−A) = −0.006, 95% bootstrap CI [−0.020, +0.009]
  (straddles 0). The W4 "per-sense granularity is the right unit" claim is **not
  vindicated for corpus-attestation prediction** at current scale.
- **Real signal that does hold:** attestation is dominated by citation *volume*
  (size-only baseline AUC 0.700; genre adds only ~+0.016); and a *pure* sense in
  kāvya/purāṇa/kośa/śāstra significantly raises attestation odds (OR 2.2–3.5, CI>1)
  while Vedic-only senses do not (OR 1.06) — an antiquarian-vocabulary signal.
- Committed: script + [`research/SENSE_GENRE_ATTESTATION_FINDINGS.md`](research/SENSE_GENRE_ATTESTATION_FINDINGS.md)
  + `sense_genre_attestation_metrics.json` + `research/figures/sense_genre_attestation.png`;
  inputs (store + `dcs_freq_dims.json`) stay gitignored. `--selftest` green.
  Analysis by Opus 4.8 (`claude-opus-4-8`).

### H823 — presplit cite-trigger floor + single-card CEIL kill budget (no-PWG lane fix)
- [`gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py): the CITATION presplit trigger now fires
  only when `(1+<ls>) > max(OUTPUT_BUDGET, PRESPLIT_SOLO_CITE_FLOOR=40)` (new
  `--presplit-solo-cite-floor=N`). Fixes a misfire under `--output-budget=1` (the no-PWG
  single-card lane): there the batch budget is 1, so ANY citation-bearing card "exceeded" it and
  was force-routed to the fragment heal lane, where its byte-scaled kill budgets (~60 s) died on a
  slow host (the H255 presplit-cohort `selfheal-nothing-resolved` loss). Tiny cards translate whole
  fine (`sam` is fine at 34 `<ls>`); only genuine 150-`<ls>` fail-solo giants presplit now. For
  `OUTPUT_BUDGET ≥ 40` (default 90) it's a no-op.
- `killBudgetForCur` now gives **ANY single-card batch** the CEIL kill budget (180 s), not just
  no-fallback singles — a lone card has no batch-mates to starve and the heal lane is no better
  budgeted on a slow host (clean H220 generalization).
- Unit-tested (`window_selftest.test_presplit_cite_floor_and_single_ceil`); full suite +
  `lang_parity_check.py` green (new `presplit_cite_floor_h823` SHARED entry). **Live verify
  (`no_pwg_presplitfix`, 6 cards) recovered 0/6:** fix verified applied (presplit_keys emptied,
  kills moved 60 s→180 s CEIL) but the cohort didn't recover on the *further-degraded* host today
  (4 exceed even 180 s; 2 are genuine content-fidelity failures, tracked separately). Correct-by-
  design; lands the cohort once the host returns to ~54 s.

### H818 — four-account Max headless orchestration
- add a canonical generation manifest, `claude -p --json-schema` worker, coordinator-imported SQLite scheduler for four isolated Max profiles, immutable attempt logs/hashes, rate-limit parking, crash recovery, systemd deployment, and an audit/runbook. Live proof remains gated on four owner-authenticated foreign-host profiles.

### H809 — PWG→RU scale-unblock (W1 rootmaps · W2 rate label · W3 window-index guard)
- **W1 (done):** generated the 687 missing verb rootmaps via `ROOT_SPLIT_MIN=0` on the
  positional verb-root splat (`_pilot_gen_merged.py --root-split @blocked`) — non-giant roots
  now get a rootmap instead of falling through to a whole-card write. `verb_worklist.py`
  runnable **14 → 701 / missing rootmap 687 → 0**; `verify_root_glue.py` **ALL GATES PASS**;
  0 tracked-file noise (all under gitignored `src/pilot/input/`). See
  [`src/pilot/RUN_LOG.md`](src/pilot/RUN_LOG.md) 2026-07-12.
- **W2 (done):** confirmed the Sonnet 5 (`claude-sonnet-5`) LIST rates via `/claude-api`
  ($3/$15; cache-write 5m $3.75, cache-read $0.30) and relabeled
  [`src/pilot/parse_workflow_cost.py`](src/pilot/parse_workflow_cost.py)'s `PRICE` comment.
  The numbers were **already correct** (Sonnet 4.6 and Sonnet 5 share $3/$15 list pricing), so
  the golden-window $79.83 / `PER_AGENT_USD=$0.347` are unchanged; a formula-pinning test lives
  in [`src/pilot/h809_selftest.py`](src/pilot/h809_selftest.py). Completing the previously
  **deferred** half (H811's blocking parity debt was cleared the same day): the H189 cost-gate
  comment and the live `rate_basis` string in
  [`src/pilot/perf_preflight.py`](src/pilot/perf_preflight.py) are now Sonnet-5-labeled — **no
  `Sonnet 4.x` remains in any live string** (only a historical as-run comment keeps it). The
  relabel is a lang-agnostic label-only change (no RU/EN branching, no numeric value touched),
  so its `LANG_PARITY` entry `presplit_lane_amortization_and_budget_guards_h189` was re-verified
  **SHARED** and its `perf_preflight.py` hash refreshed; `lang_parity_check.py` (46 entries, no
  drift) and `window_selftest.py` both green. W2 acceptance now fully met.
- **W3-code (done):** [`src/pilot/no_pwg_scale_plan.py`](src/pilot/no_pwg_scale_plan.py) gains
  `used_window_indices()`/`next_free_index()` (scan `run_pilot_wf.<prefix>NN.js` +
  `wf_output.<prefix>NN.json`, `_rqN` requeues count as their base index); `--start-index`
  default → `None` (auto = max-used+1, min 2); new `--force-index`; an explicit colliding
  `--start-index` now `SystemExit`s naming the next-free index (was a silent label knob whose
  stale `.ai_state` value 4 collided with already-run w04/w05). `--plan-only` never blocks.
- **W0/W4 (NO-GO):** the generation API is still degraded (SERVER_OUTAGES row 29, re-confirmed
  H566 682,753 ms; paid probes banned this sprint week) — no fresh probe fired, no drain/canary
  run. W1/W2/W3 are the not-API-gated subset, shipped standalone.

### H811 — ≤N-wide staggered dispatch (boundedParallel) for degraded-API requeues
- [`src/pilot/gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py) gains `--max-wide=N` +
  `--stagger-ms=M`: the emitted top-level dispatch now runs through a
  `boundedParallel(thunks, width, staggerMs)` worker-pool (≤N units in flight, first N starts
  staggered) instead of the runtime `parallel()`. **Default 0 = unbounded (no regression).**
- Root of the H255 w07 finding: the Workflow runtime caps width at ~10, and on a degraded
  generation API a tiny card that completes in **~54 s alone** is inflated past the **180 s
  kill CEIL** at ~10-wide (w07: 32/36 kill-timeouts on 128–500 B skeletons). A `--max-wide=3`
  requeue keeps each card near its isolated latency. Requeue recipe:
  `gen_opt_harness2.py <root>_rq1 --nominal --keys=<null-keys> --output-budget=1 --no-tm
  --max-wide=3 --stagger-ms=2000`.
- Verified: new [`src/pilot/boundedparallel_test.js`](src/pilot/boundedparallel_test.js)
  behavioral test (against the REAL emitted fn — caps concurrency, staggers, order-preserving,
  null-on-throw) wired into `window_selftest.test_lowwide_staggered_dispatch`; full
  `window_selftest.py` + `lang_parity_check.py` green; new `lowwide_staggered_dispatch_h811`
  SHARED LANG_PARITY entry (the width control is language-independent, emitted identically for
  RU/EN).

### H390 Phase 1 — per-window `gen_model` instrumentation (12-07-2026, Opus 4.8 `claude-opus-4-8`)
- The window ledger now records **which model generated each window**. [`gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py)
  stamps `meta.gen_model` (the model pinned on the translate `agent()` calls — `claude-sonnet-5`
  for EN, the `sonnet` alias for RU, per the existing `sonnet5_explicit_model_pin_en` divergence);
  [`window_reports.py`](src/pilot/window_reports.py) `append_ledger` writes it onto every
  `window_ledger.jsonl` row; [`harvest_launch_stats.py`](src/pilot/harvest_launch_stats.py) adds a
  **§1b population-by-model** table + a `gen_model` coverage line + a `gen_model` CSV column.
- This is the "enabling phase" for the H390 Fable-vs-Sonnet A/B (Phase 3): per-model rates
  (hard-fail %, clean %) are now computable straight off the ledger, which previously could not
  see the generating model at all. Existing 458-window population is all `(unstamped)` (predates
  the instrumentation), reported honestly as a coverage gap, never folded into a real model.
- Pinned by `test_ledger_stamps_gen_model` in [`window_selftest.py`](src/pilot/window_selftest.py)
  (asserts the ledger row carries `gen_model`, and that a run with no `workflow_meta` degrades to
  `None` instead of raising). Classified **SHARED** in [`LANG_PARITY.md`](LANG_PARITY.md)
  (`gen_model_ledger_stamp_h390`). Phases 2–4 remain: cost backfill is largely blocked (recent
  launches' transcripts died with their worktrees, per the H462 ledger audit), the A/B itself is
  blocked on a healthy generation API (12-07 census NO-GO), and the paper depends on both.

### H809 — PWG→RU scale-readiness census (12-07-2026): NOT ready for nonstop; blocker is infra
- [`SCALE_READINESS_CENSUS_2026-07-12.md`](SCALE_READINESS_CENSUS_2026-07-12.md) — a
  read-only 8-agent workflow (Opus 4.8 `claude-opus-4-8`, ~1.0 M tokens) verified the
  three lanes against live state. Verdict: the *code* no longer "falls as before"
  (H189/H220/H304 fixes hold, re-verified), but the **generation-API host is degraded**
  (11-07 schema-carrying probe 682,753 ms → gate NO-GO), so every lane times out. Verb
  drain cannot run at scale (**687 of 701 remaining roots lack rootmaps**, only 14
  runnable); no-PWG lane ~27% drained; medium50 still blocked (split-pool #311
  unvalidated under load). Audits are essentially finished (only H178 Part B open). Fixes
  handed to Opus in
  [H809](https://github.com/gasyoun/Uprava/blob/main/handoffs/H809-Opus_RussianTranslation_pwg-ru-scale-unblock-fixes_12.07.26.md).

### H771 — RENOU `renou_dcs`/`renou_ls` divergence adjudicated: CORRECTION (old chain safe to delete)
- [`RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md`](RENOU_DCS_INDEX_REGRESSION_INVESTIGATION_12.07.26.md)
  settles the H692 `@DECIDE`: the 25‑06 canonical `{code}.renou.jsonl`
  regeneration is a **correction, not a regression**, for all 7 codes
  (ap/ap90/ben/bhs/mw/pw/sch). A positional (homonym‑exact) comparison of the
  old underscore chain vs the canonical dot‑files finds **28,662 / 646,926 rows
  (4.4 %) diverge in `renou_dcs`, 100 % of them `canon ⊂ old`** — pure removal,
  zero additions, zero mutations, **zero KEPT‑ANOMALY**. Every removed state is
  a documented DCS noise class: a thin single‑text `n=1, conf=low` tail
  (min‑support pruning, introduced in `ecc7bb96` *after* the old chain was
  built) or an Epic `III` date‑fallback attestation (index refresh; lemma‑absent
  drops are **100 % single `["III"]`**). Mechanism identified in the script/index
  diff, not timestamps: the old chain computed `dcs_states = dcs['renou']` **raw**
  (unfiltered) against the pre‑refresh index. `renou_ls` shows **zero real
  divergence** (positionally byte‑identical, all codes) — H692's sampled mw 22.8 %
  was a homonym‑misalignment artifact of key1‑keyed sampling; the LS source maps
  never changed (23‑06). **The ~379 MB old underscore chain is safe to delete**
  (deletion stays a human `@DO`). Zero data files touched — read‑only, per
  [H771](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H771-Opus_RussianTranslation_renou-dcs-index-regression-investigation_12.07.26.md).

### H805 — canonical shared store path so worktree drain windows don't silently drop promotions
- New [`src/store_path.py`](src/store_path.py) `canonical_store()` resolves the ONE logical
  translated store (`$PWG_RU_STORE` override → the **MAIN checkout's** store when running inside a
  linked `git worktree` → local default). Root-fixes a data-loss bug: the gitignored store was
  resolved per-checkout, so `no_pwg_w06` (run in an isolated worktree, [PR #366](https://github.com/gasyoun/SanskritLexicography/pull/366))
  promoted 11,505→11,558 into a worktree store that was **discarded with the worktree** — the live
  store is still 11,505, and w06's 29 sub-cards / 53 sense rows are lost (regenerable only).
- Wired into both promotion writers — [`src/promote_final_cards.py`](src/promote_final_cards.py) (RU)
  and [`src/promote_en.py`](src/promote_en.py) (EN, same latent bug, fixed for parity) — with a
  visible `store: … (canonical/shared)` provenance line; their existing `PromoteClaim` lock now
  serialises concurrent promotions on the shared path. Also wired the no-PWG dedup readers
  [`src/pilot/no_pwg_scale_plan.py`](src/pilot/no_pwg_scale_plan.py) +
  [`src/pilot/nominals_worklist.py`](src/pilot/nominals_worklist.py).
- New `canonical_store_path_h805` SHARED entry in [`LANG_PARITY.md`](LANG_PARITY.md); the 5
  promotion-tracked parity entries re-verified (verdicts unchanged) + re-hashed. `store_path.py
  --selftest`, `promote_final_cards.py --selftest`, full `window_selftest.py`, and
  `lang_parity_check.py` (43 entries, no drift) all green. Follow-up: apply `canonical_store()` to
  the `annotate_*.py` writers too (same latent bug, lower risk — they run post-promotion).

### H777 — expand per-card stats (layer/markup/QA/xref + dcs_freq + grammar join), 3 grains
- [`src/annotate_stats.py`](src/annotate_stats.py) extended from the H422 lemma block to the
  full accepted count menu (MG ruling 12-07-2026) at **three granularities** —
  `sense_stats` (per row), `record_stats` (per homonym), `stats` (per lemma): layer/5-merge
  provenance (`n_layers`, `layers_present`, `n_senses_supplement`), markup density (`n_ls`,
  `n_lex`, `n_ab`, `n_xref`, `n_labels`), translation/QA (`equivalence_types`, `source_types`,
  `review_statuses`, `n_differentia`, `n_null`), frequency (`dcs_freq_max`, exact-iast DCS
  join), and the **grammar-block join** (`grammar_join`, `n_whitney_homonyms`,
  `n_irregularities`, `root_class`, `stem_final`).
- **`n_irregularities` no longer stuck at 0** — joined from `whitney_grammar.grammar_for`
  for single-Whitney-homonym roots (32/205 lemmas, 46 irregularities on the current store);
  ambiguous-homonym roots (17) are left `null`, not guessed (hand PWG-h ↔ Whitney alignment
  owed). `dcs_freq_max` is exact-iast-or-null (170/205 matched) — prefixed forms DCS doesn't
  lemmatise stay null rather than force-matched (the Renou-classifier lesson).
- Schema `stats` block + `sense_stats`/`record_stats` documented in
  [`schemas/pwg_ru_final_card.schema.json`](schemas/pwg_ru_final_card.schema.json); every
  grammar-join state validates. `pipeline_versions.json` `script` bumped 1.0.0 → 1.1.0
  (re-froze SHA; `annotate_stats.py` added to the tracked set) so cached blocks
  self-invalidate. Extended fixture selftest.

### H778 — freeze the PWG government census to a committed sidecar (no re-scan)
- [`src/government_census.py`](src/government_census.py) gains a `freeze` command +
  `build_sidecar`/`load_sidecar`/`census_or_load`: the corpus-level marker census over the
  whole raw `pwg.txt` is frozen to the committed [`src/census_stats.json`](src/census_stats.json)
  (**3,853 markers over 123,366 entries**), validated by the source SHA — `government_census.py
  census` now prints `census source: cached` and skips the end-to-end re-scan when `pwg.txt`
  is unchanged. [`src/government_queries.py`](src/government_queries.py) gains `--summary` for
  the store-free corpus answer. Per-row listing queries still stream the store (rows not
  frozen). Sidecar round-trip covered by the selftest.
- Both are language-neutral analysis layers (operate on `de`/store structure) — no
  LANG_PARITY entry required. Store fields are materialised locally by re-running the
  annotator chain; the store is gitignored, so the code + sidecar are what ship.

### H772 — PWG++: glue the derivable layers onto the German original, not only the RU
- New `de-lexicon` mode in
  [`src/export_lod.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py)
  emits a first-class German `ontolex:LexicalEntry` per PWG homograph
  (`entry/<key1>[-N]/de`) into a **separate** graph (`pwg_de_lexicon.ttl`) that
  federates on the **same** `lemma/<key1>` node as the RU lexical graph and the
  DCS-frequency graph. German glosses, `<lex>` POS, `<ls>` citations, diasystem,
  Renou strata and the shared dated `StratumAttestation` land on the German entry
  with **zero translation**; DCS frequency reaches it via the shared lemma. The
  German dictionary is sourced from the full ~120k `assembled_cards` (the German
  source), so it is **decoupled from the ~11.5k translated subset**. Sense split
  reuses `pwg_mask.restore` + `microstructure.split_senses/sense_node` (no
  reinvention). RU + DCS output stays byte-identical.
- [`src/lod_acceptance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/lod_acceptance.py)
  gains block **C** (three-way DE×citation×DCS-freq federated join, German
  entry/sense invariants, RU+DE-share-one-lemma, source coverage, byte-stable
  regen) + query
  [`release/query/de_sense_citation_dcsfreq.rq`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/query/de_sense_citation_dcsfreq.rq).
  Full gate **PASSED**. Design + layer inventory:
  [`PWG_PLUS_GERMAN_ENRICHMENT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_PLUS_GERMAN_ENRICHMENT.md).
  ([H772](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H772-Opus_SanskritLexicography_pwg_plus_german_enrichment_lod_12.07.26.md), Opus 4.8 `claude-opus-4-8`)

### H775 — capability roadmap cards 5 + 23: MFS baseline + government sidecar (local-only)
- New [`src/mfs_baseline.py`](src/mfs_baseline.py) (roadmap card 5): groups the
  store by `key1` and emits a deterministic most-frequent-sense candidate per
  lemma — the WordNet first-sense heuristic (DCS frequency is per-lemma, so it
  cannot rank senses), with an explicit `unknown` outcome when the lemma is
  absent from DCS. Live coverage over the 11,505-row store: **205 lemmas, 179
  polysemous, 169 MFS candidates, 36 unknown**. Reuses `annotate_dcs_freq.freq_block`.
- New [`src/government_sidecar.py`](src/government_sidecar.py) (roadmap card 23):
  applies `government_census.extract_government` to every row's German `de` and
  emits a **collision-free per-subcard sidecar** (not an in-place store rewrite,
  which would race the concurrent drain lanes). Live census: **508 rows carry
  government, 614 markers, 48 distinct `key1`** (436 paren-single, 176 mit-phrase,
  2 variation) — corroborates the H335 `government_census` "store backfill surface
  ~510 rows". Reuses `extract_government`.
- Both outputs are gitignored (derived from the local-only store); scripts +
  fixture selftests committed and wired into CI. Observatory
  ([`CAPABILITY_OBSERVATORY.md`](CAPABILITY_OBSERVATORY.md)) cards 5 + 23 bumped
  `not-started → prototype` (prototype count 4 → 6). The **accuracy/precision
  acceptance metrics for both cards are gold-gated** — documented in
  [`GOLD_SLICE_NEEDS_CAPABILITY_ROADMAP.md`](GOLD_SLICE_NEEDS_CAPABILITY_ROADMAP.md).
- Language-neutral analysis layers (operate on `de`/sense structure, no RU/EN
  translation divergence) — no LANG_PARITY entry required.

### H692 — assembled_cards/renou stage-redundancy: verify + deletion PROPOSAL (no deletion)
- [`RENOU_STAGE_REDUNDANCY_AUDIT_12.07.26.md`](RENOU_STAGE_REDUNDANCY_AUDIT_12.07.26.md)
  verifies the two progressive-enrichment series the census flagged as
  possibly dead (~1.4 GB, all gitignored/local-only/single-copy under
  `src/`). **Series A** (`assembled_cards.jsonl` → `.renou` → `.renou.bhs` →
  `.renou.bhs.wl`): every row verified clean — earlier stages are fully
  content-contained in the final stage (only the monotonically-additive
  `renou_provenance`/`renou_enriched` tracking fields change value) →
  **PROPOSE DELETE** the first 3 stages (~607 MB). **Series B** (per-dict
  `{code}_renou*` old chain vs canonical `{code}.renou.jsonl`, `.`-vs-`_`
  naming drift across ap/ap90/ben/bhs/mw/pw/sch): NOT redundant — the
  canonical dot-files, regenerated ~a day later against a refreshed DCS
  index, diverge from the old chain by 3–23% of rows (field-dependent:
  `renou_ls`/`renou_dcs`/`renou_enriched`) → **DO NOT DELETE**, `@DECIDE`
  raised on whether that regeneration was a correction or a regression.
  Zero data files touched this session — proposal only, per
  [H692](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H692-Fable_RussianTranslation_assembled-cards-dedup-verify_11.07.26.md)'s
  stop condition. Verification script:
  [`src/renou_stage_redundancy_check.py`](src/renou_stage_redundancy_check.py).

### H429 — PWG page/column co-location index (`<pc>` → who shared a printed column/page)
- New [`src/pwg_page_index.py`](src/pwg_page_index.py) parses the `<pc>`
  volume-column marker on every entry header in
  [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
  (123,366 entries, 100% coverage) and emits three views:
  [`pwg_columns.tsv`](src/pwg_columns.tsv) — column mode, 8,171 Böhtlingk-Roth
  *Spalten* → entry IDs + headwords; [`pwg_pages.tsv`](src/pwg_pages.tsv) —
  2-column page mode, 4,329 physical pages (`page = ⌈col/2⌉`, as printed);
  [`pwg_entry_locations.tsv`](src/pwg_entry_locations.tsv) — reverse lookup,
  entry → start column, page, all spanned columns (incl. cross-volume Nachträge).
- `--annotate` adds `volume`/`column`/`page`/`pc_all`/`page_all` to the
  gitignored `pwg_ru_translated.jsonl` cards (11,239/11,261 matched;
  22 non-source-headword forms unmatched), idempotently.
- Served from kosha's DB as the `/api/v1/page` + `/api/v1/neighbors` endpoints
  (kosha H434, [PR #33](https://github.com/gasyoun/kosha/pull/33)); this is the
  raw-source view of the same co-location concept.
  ([PR #286](https://github.com/gasyoun/SanskritLexicography/pull/286)).

### H428 — opt2 generation schema slimmed to reachable-AND-model-generated fields, unblocking the classifier
- The Workflow tool's `agent()` safety classifier was blocking 100% of opt2
  translation calls (67/67 in [H389](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H389-Sonnet_RussianTranslation_pwg-ru-medium50-resume_08.07.26.md),
  52/52 in H388's B-arm) with `output schema too large to classify safely`, at
  0 subagent tokens — the reachable `CARDS_SCHEMA` had grown to 10,940 chars
  after H335 (`government`)/H405 (`evidence`/`evidence_summary`)/H422 (`stats`)
  each added a legitimately-`$ref`'d field. See [Uprava/FINDINGS.md §30](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).
- New `_strip_post_generation_fields()` in
  [`src/pilot/gen_opt_harness2.py`](src/pilot/gen_opt_harness2.py) drops every
  field a *downstream deterministic annotator* adds after generation —
  `government`/`labels`/`renou`/`renou_oldest`/`evidence` (sense),
  `renou_oldest_sense` (record), `evidence_summary`/`stats` (card) — from the
  per-call generation schema only; `promote_final_cards.py` + the annotator
  scripts still add them back from the unmodified schema file on disk.
  Reachable schema: 10,940 → 1,698 chars (84% reduction); `$defs` collapse
  from `{card,record,sense,evidence_item,evidence_summary,stats}` to
  `{card,record,sense}`.
- New `--dump-schema` CLI flag prints the live generation schema + char length
  without needing a Workflow-tool probe.
- Verification: a single diagnostic `agent()` call (nominal window, root
  `vinasa`) returned a valid card with 75,774 subagent tokens spent (vs 0
  tokens / classifier-blocked pre-fix). Pinned by new
  `window_selftest.py:test_generation_schema_carries_no_post_generation_field`.
  Full `window_selftest.py` (107 tests) and `lang_parity_check.py` (37
  entries) both green.
- Unblocks H389 (medium50 windows), H388 B-arm, and the H151 verb-root drain.
### H429 — PWG page/column co-location index (`<pc>` → who shared a printed column/page)
- New [`src/pwg_page_index.py`](src/pwg_page_index.py) parses the `<pc>`
  volume-column marker on every entry header in
  [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
  (123,366 entries, 100% coverage) and emits three views:
  [`pwg_columns.tsv`](src/pwg_columns.tsv) — column mode, 8,171 Böhtlingk-Roth
  *Spalten* → entry IDs + headwords; [`pwg_pages.tsv`](src/pwg_pages.tsv) —
  2-column page mode, 4,329 physical pages (`page = ⌈col/2⌉`, as printed);
  [`pwg_entry_locations.tsv`](src/pwg_entry_locations.tsv) — reverse lookup,
  entry → start column, page, all spanned columns (incl. cross-volume Nachträge).
- `--annotate` adds `volume`/`column`/`page`/`pc_all`/`page_all` to the
  gitignored `pwg_ru_translated.jsonl` cards (11,239/11,261 matched;
  22 non-source-headword forms unmatched), idempotently.
- Served from kosha's DB as the `/api/v1/page` + `/api/v1/neighbors` endpoints
  (kosha H434, [PR #33](https://github.com/gasyoun/kosha/pull/33)); this is the
  raw-source view of the same co-location concept.
  ([PR #286](https://github.com/gasyoun/SanskritLexicography/pull/286)).

### H409 — `has_meaning()` short-token stemmer gap fixed, RATIO-scoring regression caught and reverted
- New [`corpus_gate.ru_has_content()`](src/corpus_gate.py): relaxes the
  `>=3-char-after-stemming` floor for tokens already `<=3` letters before
  stemming — `оно` ("it") was being stemmed to `он` (2 chars) and discarded
  as no-meaning even though the whole word is a real Russian pronoun.
  `koch_xref.has_meaning()`/`fri_xref.has_meaning` now use it. Census across
  the RU family: 77 entries reclassified no-meaning → has-meaning
  (koch 27, fri 27, kna 9, smirnov 3, kow 11). koch's bare-`см.` xref count
  drops 3,472→3,471 (resolved 3,204→3,208); fri's drops 340→337 (rate
  32.6%→32.9%).
- **A ratio-scoring regression was caught by re-measuring before shipping,
  not silently absorbed.** The same relaxed floor applied to
  `annotate_evidence.ru_tokens_full()`/`corpus_gate.ru_tokens()` — which feed
  `best_relation()`'s token-containment ratio, not a boolean presence check —
  measurably regressed classification (107 previously-correct `supports`
  verdicts lost vs 37 gained on the live store: a short function word like
  `что` inside `что-либо` ("something") inflated the ratio's denominator).
  Reverted those two functions to their pre-H409 stemming; the relaxed floor
  lives only in the new `ru_has_content()`. Store backfill
  (`annotate_evidence.py --dry-run`) confirmed **unchanged** vs the pre-H409
  baseline for every source.
- A second data-quality artifact caught in the same census: 9 fri/smirnov
  entries whose entire gloss is a leaked Excel `#ИМЯ?` ("#NAME?") formula
  error — fixed with a narrow `corpus_gate._SPREADSHEET_ERR_RE` guard so the
  real word `имя` embedded in the error string doesn't count as meaning.
- See [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md — W2b correction](PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#w2b-correction--has_meaning-short-token-stemmer-gap-fixed--executed-09-07-2026-h409)
  for the full census table and worked examples.
- LANG_PARITY: `koch_xref_resolution_h397`/`fri_xref_resolution_h404`
  INTENTIONAL-DIVERGENCE verdicts re-affirmed, hashes refreshed.

### H405 — Stage-2 mechanical pre-gate (`stage2_pregate.py`), PIPELINE_CAPABILITY_AUDIT W5
- New [`src/stage2_pregate.py`](src/stage2_pregate.py): a deterministic mechanical
  pre-gate for the Stage-2 QA judge, implementing the W5 recommendation of
  [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](PIPELINE_CAPABILITY_AUDIT_2026-07-08.md).
  `pregate(de, ru)` hard-fails the format invariants the judge prompt already declares
  must not affect the verdict — untranslatable-span preservation (LS/SAN/AB/IS/LEX/LANG,
  category regexes kept in sync with `pwg_mask.PAIRED` by the selftest), `{Tn}` anchor
  multiset equality, stranded/never-restored `{Tn}`, unmask-leak — and emits `NO-RUSSIAN`
  as a **soft warning** (not a block), because a `{%…%}`-with-no-Cyrillic card is as often
  a form-citation apparatus stub as a real untranslated defect. Failed cards are requeued,
  never judged; the judge rubric can then drop the mechanical criteria.
- Measured over the live store (11,261 rows): 99.72% CLEAN, 0.18% WARN, 0.10% (11) hard
  FAIL — surfaced 13 real format defects (giant verb-root apparatus loss + 2
  stranded-anchor mask-restore bugs) in already-promoted data. Result table persisted in
  the W5 "BUILT" subsection of the capability audit.
- `python src/stage2_pregate.py --selftest` → PASS (11 cases + a `pwg_mask.PAIRED`
  sync assertion). LANG_PARITY: `stage2_mechanical_pregate_h405`, SHARED (structure-only,
  language-agnostic).
- **Wired into the RU window auditor (09-07-2026).** New `--wf <wf_output.json>` mode emits
  `FLAGGED_JSON` of hard fails over the same `.raw.txt`/`.merged.md` pairs the fidelity gate
  reads; registered in [`src/pilot/audit_window.py`](src/pilot/audit_window.py) as the
  `stage2_mechanical` gate, so a hard-failed card joins the requeue. Mechanical criteria
  stripped from both judge prompts ([`2_qa_sudya_opus.txt`](pwg_ru_prompts/2_qa_sudya_opus.txt)
  + YandexGPT twin) — the judge now rules only on semantics (`anchors` kept as a backstop).
  `window_selftest.py` green.
- **EN auditor wired too (09-07-2026).** [`src/pilot/audit_window_en.py`](src/pilot/audit_window_en.py)
  audits in-process per-sense, so `audit_sense(german, english)` now calls `pregate(g, e)` and
  folds in only the net-new hard flags its own checks lack — `IS-LOSS` (the EN `AB` regex omits
  `<is>`), `STRANDED-ANCHOR`, and the anchor-leak/mismatch backstops — while `LS/SAN/AB` stay
  owned by `audit_sense` (no double-reporting); these were added to the `HARD` tuple so `--strict`
  fails on them. Parity GAP closed: `stage2_pregate_en_wiring_h405` → SHARED. Both editions now
  run the same `pregate()` module; only the adapter differs (RU: subprocess `--wf` over file
  pairs; EN: in-process per-sense).

### H404 — cross-reference count/resolve generalized to every gate source (H397 generalization)
- **Part A (RU family).** Measured `kna`/`fri`/`smirnov`/`kow` against koch_xref's
  `is_bare_xref` primitive: kna 0.2%, smirnov 1.0% (corrects H397's unpersisted
  ~1.4% claim), kow 0.0% — all below the ~2% materiality bar, not touched. **fri
  clears the bar at 4.2%** (340/8,151) via its OWN convention — Latin apparatus
  (`v.`/`cf.`/`q.v.`), not koch's `см.`. New [`src/fri_xref.py`](src/fri_xref.py)
  resolves 111/340 (32.6%) via `build_src.iast_to_slp1` (existing prior art) +
  `corpus_gate.form_key`, wired into `annotate_evidence.py` alongside koch. A
  mojibake-corruption bug (`v. II apaгa;` — stray Cyrillic г) that silently
  mis-resolved to the wrong headword was caught by the 20-sample spot-check and
  fixed (truncated-token matches now refuse instead of guessing).
- **Part B (English/German CDSL: MW, PWG, GRA, PWKVN, AP90).** New
  [`src/part_b_xref_discovery.py`](src/part_b_xref_discovery.py) (read-only,
  count-only over `csl-orig`): discovered each dictionary's actual redirect
  marker before counting (MW `q.v.`, PWG `s.`/`vgl.`, GRA `s. d. v.`, PWKVN
  `Vgl.`; AP90 has none — its `[cf. ...]` is etymology, not a same-dict
  redirect). **Headline: PWG itself carries 5,303/123,366 (4.3%) bare
  redirects** — more material proportionally than koch's own count. Resolution
  is out of scope here (csl-orig changes require the correction-workflow, not
  an ad-hoc resolver); flagged as a fork for a human ruling on a future
  handoff. See [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md §W2b](PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#w2b--cross-reference-countresolve-generalized-to-every-gate-source--executed-09-07-2026-h404-h397-generalization).
- LANG_PARITY: `fri_xref_resolution_h404`, INTENTIONAL-DIVERGENCE.

### H397 — koch `см. X` cross-reference resolution for the evidence lane (H337 follow-up)
- New [`src/koch_xref.py`](src/koch_xref.py): resolves koch's bare `см. X` redirects
  (3,472 of koch's 4,048 no-meaning entries — a headword pointing to a different
  headword's real gloss) instead of reporting them as `silent`. Builds a Devanagari →
  SLP1 crosswalk from koch's own self-describing `<devanagari> /iast/` headword prefix
  (no external transliterator needed), resolves one hop (chain-safe up to 2, visited-set
  cycle guard), and leaves genuinely unresolvable pointers untouched. 3,204/3,472
  (92.3%) resolve dictionary-wide. `annotate_evidence.py`'s `gather()` now resolves the
  koch lane before relation classification (`--no-resolve-xref` reproduces H337
  exactly); resolved glosses carry a `«см.→» ` provenance prefix. Store backfill:
  koch `provides` 143→155, `supports` 560→578, `silent` 79→74 (145-lemma current
  store — the dictionary-wide 92.3% lift materializes further as more lemmas are
  translated). See [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md §W2](PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#w2-extension--koch-см-x-cross-reference-resolution--executed-09-07-2026-h397).
- Spot-checked 20 randomly-sampled resolved xrefs: all matched the redirect's stated
  target headword, zero fabricated meanings.
- LANG_PARITY: `koch_xref_resolution_h397`, INTENTIONAL-DIVERGENCE (koch is
  Sanskrit→Russian only).

### H337 — per-sense evidence provenance retrofit + annotation_report query CLI (H335 W2)
- New [`src/annotate_evidence.py`](src/annotate_evidence.py): deterministic, LLM-free
  backfill of corpus_gate's 7 evidence lanes onto the store as queryable per-sense
  provenance. Per Russian authority (koch/kna/fri/smirnov/kow/grin12/grin3) it records
  `provides` (exact Russian equivalent) / `supports` (token containment ≥
  `corpus_gate.THRESHOLD`) per sense, and `contradicts` / `silent` per lemma; the
  non-Russian lanes (apte_hi/vedic_rituals_hi/kosha_syn/meulenbeld/corpus) are recorded
  as lemma-level presence corroboration. A source with no usable Russian meaning gloss
  is `silent`, never `contradicts` (guards against false disagreement on Smirnov
  citation-lists / Kossovich transliteration). `leonov` reserved in the schema enum,
  not built.
- Schema (D1, [DECISIONS_PIPELINE_CAPABILITY_H335.md](DECISIONS_PIPELINE_CAPABILITY_H335.md)):
  optional `evidence[]` on `$defs.sense` + lemma-level `evidence_summary` on `$defs.card`
  in [`schemas/pwg_ru_final_card.schema.json`](schemas/pwg_ru_final_card.schema.json).
- New [`src/annotation_report.py`](src/annotation_report.py): the single query surface —
  `<selector>` full row dump, `--by-source X [--relation]` (answers "which senses did
  Grintser/Kossovich support?"), `--source-summary`, `--silent-for <key1>`. H338/H339
  fold their queries in here.
- Backfill executed over the full gitignored store (D2: retrofit all): 11,261 rows /
  145 lemmas, 2,239 (19.9%) with ≥1 evidence entry. Per-source table in
  [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md § W2](PIPELINE_CAPABILITY_AUDIT_2026-07-08.md).
- LANG_PARITY: `evidence_retrofit_annotate_h337` = INTENTIONAL-DIVERGENCE (RU-only; the
  lanes are Sanskrit→Russian sourced). Pinned by `test_annotate_evidence_relation_semantics`.

### H361 — Elizarenkova RV citation/context witness (VedaWeb, CC BY 4.0)
- New [`src/vedaweb_ru_witness.py`](src/vedaweb_ru_witness.py): RV `location` →
  Elizarenkova's published Russian rendering, reading the committed
  [`VisualDCS/non-derived/vedaweb/elizarenkova_ru_1989_1999.json`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/elizarenkova_ru_1989_1999.json)
  feed (10,552 stanzas, CC BY 4.0 confirmed 08-07-2026). Advisory/citation-context
  only — never written into `headword_index.tsv` or any reviewed store data. See
  [CORPUS_PROVENANCE.md § RV citation witness](CORPUS_PROVENANCE.md#rv-citation-witness-vedaweb-cc-by-40--distinct-from-the-corpus-above)
  for why this is a distinct rights posture from the grey-rights Elizarenkova copy
  already inside the `SamudraManthanam` corpus DB.

### H350 / E7 — flat OntoLex export → real LOD graph (OntoLex + vartrans + PROV-O + LiLa)
- New [`src/export_lod.py`](src/export_lod.py): upgrades the flat one-way string
  export ([`src/export_interop.py`](src/export_interop.py) → `release/ontolex.ttl`,
  placeholder `example.org` IRIs, string-only `ontolex:usage`, no query surface)
  into a real Linked-Open-Data graph — **real configurable IRIs** (`--base-iri`),
  **`vartrans`** sense↔sense relations (from `pwg_ru_relationships.jsonl`),
  **PROV-O evidence grades** (a SKOS scheme; the citable release is now a SPARQL
  filter, not a separate build), per-sense **`<ls>` citations as first-class
  `pwglex:Citation` resources**, and the **Renou stratum** (`pwg_sense_stratum.jsonl`)
  as dated `pwglex:StratumAttestation`. `export_interop.py` is untouched (still owns
  TEI Lex-0 + reverse-index).
- **LiLa-style lemma bank:** one shared `ontolex:Form`/`lila:Lemma` node per `key1`
  (SLP1 spine) is the join hub; the **separate** DCS-frequency graph
  (`export_lod.py dcs-freq` → `dcs_freq.ttl`) keys `pwglex:dcsCount`/`dcsBand` to the
  *same* lemma IRI, so cross-dataset queries join on it.
- **Acceptance gate** [`src/lod_acceptance.py`](src/lod_acceptance.py) (exit ≠ 0 on
  failure): (A) a **federated SPARQL join** [`release/query/sense_citation_dcsfreq.rq`](release/query/sense_citation_dcsfreq.rq)
  sense → `<ls>` citation **+** lemma DCS frequency; (B) **lossless round-trip** —
  byte-identical regeneration, parse↔serialise graph-isomorphism, and source-coverage
  (every `<ls>`, stratum, grade recounted from the jsonl survives as a triple);
  plus structural invariants + **SHACL** [`release/shapes.ttl`](release/shapes.ttl).
  Fixture-only mode is CI-safe (no gitignored source needed). Committed fixture
  [`release/fixture/`](release/fixture/) (`rakz`+`a`/`aMSa`/`aMSaka`, 4157 triples).
- Design + before/after coverage table + modelling boundaries: [`LOD_GRAPH.md`](LOD_GRAPH.md).
- **Boundary:** generator + data stay here; the published graph + SPARQL surface are
  routed to `csl-standards` (G2); full data publication gated on G5 approvals. IRI
  publication domain is an open `@DECIDE` (placeholder w3id PURL until ruled).

### H6 Zipf agreement (Renou hypothesis programme step 3) — 08-07-2026
- New [`src/renou_h6_zipf.py`](src/renou_h6_zipf.py): among 172,845 entries across
  the 8 canonical dicts carrying both `<ls>` and `dcs` era spans, bins by
  log10(DCS lemma text frequency) and fits a logistic curve to `ls`–`dcs` exact
  agreement. **H6 confirmed**: exact agreement 66.7% → 0.2% across the frequency
  range, `dcs_adds` 9.3% → 97.8% in lockstep; 50% crossing at freq ≈ 2.7 DCS
  texts. See [`RENOU_H6_ZIPF.md`](RENOU_H6_ZIPF.md) (F7 in `RENOU_FINDINGS.md`).
  Recommends (no code change) a frequency-gated confidence flag as an
  alternative to `renou_portrait.py`'s state-count `LOW_INFO_MIN_STATES`
  heuristic. Computed by Sonnet 5 (`claude-sonnet-5`).

### H290 (H215 Slice 4a) — oral TEXT + PDF front-end
- New [`src/build_oral_l0.py`](src/build_oral_l0.py): the text+PDF front-end for oral
  transcripts that are **not** a pre-aligned subtitle pair (what `ingest_oral.py`
  needs). Reads one transcript (+ optional PDF/DOC companion), **detects** which of
  three shapes MG defined — `bi` (interleaved Sa+Ru), `sa+pdf` (Sanskrit-only + Russian
  handout), `ru+cit` (Russian lecture quoting Sanskrit) — routes it, and emits the
  **same** `corpus_builder/<work>.jsonl` seg-rows `ingest_oral` does, tagged `orality`
  + `source_type`. Ambiguous input is flagged for human review, never guessed.
- **PDF-role classifier** (`classify_pdf_role`): `edited-ru` / `sanskrit-source` /
  `commentary` from language mix + structure; the `edited-ru` case is emitted as a
  **multi-reference** (separate `work`, shared verse `passage`) so a spoken rendering
  and its written handout become a consensus signal. Companion PDF/DOC → `.mdx` via the
  `/docx-to-md` skill only (never a flat `.md`); no PDF extraction is re-implemented.
- Reuse, not fork: emission delegates to a minimally generalized
  `ingest_oral.to_corpus_rows(..., extra=)`; `build_l0.py` now carries `orality`/
  `source_type` through to the L0 unit. Script detection treats **SLP1/HK romanization**
  as Sanskrit (the earlier IAST-only test missed it). `selftest` covers all of the
  above on a synthetic fixture; written TMX and the Slice-4 selftests byte-unchanged.
- **Scaffold only** (data-independent). The `sa+pdf` sentence aligner is a labelled
  index/verse-key **placeholder** (`align='placeholder-*'`); the real LaBSE+Vecalign
  backend + heuristic calibration + series ingest are gated on a representative sample
  (MG `@DO`). **Open policy conflict surfaced, not silently resolved:** MG ruling 4
  (oral → A when it agrees with a *written* translation) vs the merged Slice-4
  `oral_cap` (oral A→B unless human-adjudicated) — reconciliation deferred to the
  real-data step, tracked `@DECIDE`. See [`src/ORAL_INGEST.md`](src/ORAL_INGEST.md)
  "Slice 4a".

### H215 Slice 4 — oral register of the publication-grade TM
- New [`src/ingest_oral.py`](src/ingest_oral.py): a deterministic converter turning a
  *cleaned* timecoded transcript (WebVTT/SRT/JSON, or `--pairs` JSONL) of spoken
  Sanskrit + its Russian rendering into the `corpus_builder/<work>.jsonl` schema the
  L0 pipeline already consumes — tagged `modality=oral` with `t_start`/`t_end` time
  anchors, `source_media`, optional `asr_conf`, and a canonical `iast_to_slp1` key. No
  ASR, no cleaning (that is [H174](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H174-Opus_spoken-sanskrit-corpus_spoken_sanskrit_corpus_scaffold_04.07.26.md)'s
  upstream stage — this is the Sa→Ru-alignment half). Parallel tracks pair by index;
  a cue-count mismatch is a hard error, never a silent `zip()` truncation.
- **Lowered base grade for oral** in one place: shared `build_tmx.oral_cap()` forbids
  grade A for an oral unit on automatic signals (capped at B; only human adjudication
  lifts it), plus `tm_grade.ORAL_PENALTY` (0.15) on the composite. `build_l0.py` and
  `build_tmx.py` thread `modality`/anchors through unchanged for written sources.
- Design + shared schema (coordinated with H174): [`src/ORAL_INGEST.md`](src/ORAL_INGEST.md).
  Fixture pilot: end-to-end ingest→L0→grade→TMX validates; same corroborated units
  grade **6×A written vs 6×B oral** (mean composite 0.892→0.743). Selftests added to
  `ingest_oral.py`, `build_tmx.py`, `tm_grade.py`.

## [1.4.0] - 2026-07-06

### no-PWG supplement-chain lane (H214) — PWG-missing headwords become translatable
- PWG-missing headwords that carry a PW/SCH/PWKVN/NWS record now render as
  standalone **supplement-chain sub-cards** (`<key>~~h0_zz_<layer>`) via new
  [`_pilot_gen_merged.no_pwg_parts()` / `gen_no_pwg_card()`](src/_pilot_gen_merged.py) —
  **no fabricated PWG base portrait** (supersedes decisions #2/#4 of
  [PWG_MISS_RENDER_PATH_DECISIONS.md](PWG_MISS_RENDER_PATH_DECISIONS.md)). Reuses
  `dict_merge.merged()`; renders raw NWS + the authoritative owner map. Run through the
  nominal harness (keymap `subcard→key1`, no rootmap). Layer identity survives raw →
  sub-card id (`dict_merge.layer_of`) → provenance → promoted `layer`.
- **Per-card `source_profile`** on every promoted row (`no_pwg_supplement_chain` /
  `pwg_with_supplements` (MIXED) / `pwg_only` / `pwg_supplement_subcard`) via
  [`gen_opt_harness2.card_source_profile()`](src/pilot/gen_opt_harness2.py) →
  [`promote_final_cards.provenance()`](src/promote_final_cards.py) — filter
  `pwg_with_supplements` to find all mixed cards.
- [`nominals_worklist.py`](src/pilot/nominals_worklist.py): the 232 PWG-miss lemmas
  become a `no_pwg_runnable` lane, kept separate from PWG-rooted counts.
- **Fixed — `{{Lbody=NNNN}}` leak:** it is a Cologne alternate-headword pointer (~12,186
  PW records); [`dict_merge.resolve_lbody()`](src/dict_merge.py) + `id_index()` resolve it
  to the referenced entry's real gloss in `merged()`, so it no longer leaks into `russian`.
- **Fixed — nominal audit crash:** [`audit_window.py`](src/pilot/audit_window.py) skips the
  root-glue step for a nominal / no-rootmap window instead of crashing, so the content gates
  run to a real verdict.
- First live run (`no_pwg_w1`, 24 headwords) validated end-to-end; **5 verified-clean
  sub-cards promoted** (store 11,163→11,185, held for G5). Residual: low single-card
  translation throughput (~36%) tracked in [H220](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H220-Sonnet_RussianTranslation_pwg_ru_no_pwg_throughput_06.07.26.md)
  and the [RUN_LOG.md `no_pwg_w1` block](src/pilot/RUN_LOG.md).

### Upstream-change watcher (H182) — Cologne + NWS monthly drift → stale worklist
- Added [`src/pilot/layer_versions.py`](src/pilot/layer_versions.py) +
  append-only [`src/pilot/layer_version_log.jsonl`](src/pilot/layer_version_log.jsonl):
  logs *which* upstream commit/scrape each source layer (pwg/pw/sch/pwkvn/nws) was
  drawn from — answers "do we log when each layer was added?". Backfilled once.
- Added [`src/pilot/watch_upstream.py`](src/pilot/watch_upstream.py): `cologne`
  diffs each csl-orig layer file `last-seen..HEAD` (git `show`, read-only) → changed
  headwords via the `dict_merge`/`pwg_mask`/`form_key` parse → cross-references the
  promoted store by `(form_key, layer)` and emits a monthly
  `upstream_changes/<YYYY-MM>.md` + `.stale.json` worklist carrying each flagged
  headword's stamped `input_raw_sha256` (the H170 re-run primitive). `nws` re-fetches
  only the ~48 promoted headwords from Halle (polite, resilient to downtime).
- The watcher **only flags** — re-translation stays on the drain discipline (H179/H151).
  Wired a monthly schedule: [`.github/workflows/upstream-watch.yml`](../.github/workflows/upstream-watch.yml)
  (opens/updates a drift issue) + a local `schtasks` recipe, documented in
  [UPSTREAM_WATCHER.md](UPSTREAM_WATCHER.md).

## [1.3.0] - 2026-07-05

### Nominal-window guardrails — H191 verified, optimized, staged
- Verified the H189 `pril10_w1` post-mortem deterministically: the aborted
  top-size nominal run reproduces to **42,316,604 tokens / ~$79.83**, confirming
  that fragment-level `agent()` fan-out and repeated cache writes caused the
  blow-up.
- Reduced generated harness size for cached/retry windows by omitting
  non-agent cards from `INPUTS`/`PH`; TM-resolved and degenerate pass-through
  cards now remain self-contained in `TM_RESOLVED` / `DEGENERATE_RESOLVED`.
- Hardened monster handling in two places: citation-dense single-line senses are
  split only at complete `<ls>...</ls>` spans, and `perf_preflight.py` now emits
  `cost_partition.run_now` / `cost_partition.defer_monster` with grouped totals.
  Mixed windows can run their cheap cards while routing `kAla`-class cards to a
  human-budgeted lane.
- Staged the first safe nominal follow-up:
  [`src/pilot/NOMINAL_W1_100SMALL.md`](src/pilot/NOMINAL_W1_100SMALL.md) records
  100 small Приложение 5 heads, 95 live inputs, 5 degenerate pass-through cards,
  0 deferred monsters, 3 expected agents, and an estimated **~745k tokens / ~$1.41**.
  Codex did not run Max/Workflow generation; the downstream Sonnet/Max run is
  delegated to Uprava H201.

## [1.2.0] - 2026-07-04

### Production ramp — runnable work, not wishful work
- Added the live PWG->RU ramp planner (`src/pilot/ramp_plan.py`) for the
  100 -> 1,000 -> 10,000 card progression. It prices each runnable root with
  the same preflight machinery used before Max spend, reports card/agent/batch
  counts, and marks the 10,000-card mode as a root-by-root drain with default
  concurrency 1 and hard ceiling 3 until the store/merge discipline is proven
  at larger volume.
- Made the H151 verb-root worklist runnable-aware (`src/pilot/verb_worklist.py`):
  the operator queue now filters DCS-attested remaining verbs to roots with an
  existing rootmap, while preserving the missing-rootmap backlog for audit and
  expansion planning. Current live plan: 702 DCS-attested verb roots remain, 13
  are runnable, and 689 are blocked on rootmap generation/recovery.
- Locked the first controlled ramp target to runnable roots (`tyaj`, `dah`,
  `kzip`): 106 cards/sub-cards, 45 expected agents, 4 presplit cards. The
  current runnable pool reaches 810 cards, so the 1,000-card milestone requires
  at least 190 more cards from newly generated or recovered rootmaps.

### QA gates — fail loud, then requeue
- Hardened the RU audit gate so child auditors must emit strict
  `FLAGGED_JSON`; missing or malformed verdict lines now crash loud and requeue
  the whole window instead of silently clearing flagged cards.
- Added a real EN duplicate-sense hard gate and ported the gate-bug fixes across
  the EN path, closing the language-parity gap that could have hidden identical
  English senses under soft-report wording.
- Fixed the Latin/Greek cue masking leak: `<ab>lat.</ab>` behind a placeholder
  is now expanded for classification, so cognate glosses such as `ignis` are not
  treated as German translation material.
- Made collection/store writes safer: robust JSON-string result parsing, one
  parsed batch pass, and coalesced appends reduce the stranded-run and torn-line
  failure surface.

### Publication assets — schema-validated translation memory
- Added publication and terminology export commands for the translation-memory
  lane. The RU publication feed is checksum-locked and schema-validated under
  `release/translation_memory/`; the separate `sa_ru_terminology` DOI lane is
  intentionally empty until curated term suggestions exist.
- Added fuzzy-speed reporting and ranking profiles for TM reuse, keeping exact
  reuse machine-gated while allowing fuzzy matches to remain advisory until
  validated.
- Verified the current publication-facing RU TM: 2,392 publication records pass
  `translation_memory.py validate --lang ru --publication`.

### Review discipline — changelog after major reviews
- Added a blocking `review_changelog_guard.py` hook for authored review/audit
  documents and roadmap review JSON. Major review edits must now update this
  changelog in the same diff, or carry an explicit `Changelog: not applicable`
  marker so the bypass is auditable. The guard is wired into both local
  pre-commit and CI.

### Pipeline versioning — stamp WHICH tooling produced each translation
- New `src/pipeline_version.py` + manifest `src/pipeline_versions.json`: a semver
  per output-affecting component family — **prompt** (`pwg_ru_prompts/`),
  **glossary** (`glossaries/`), **script** (`src/` deterministic code) — orthogonal
  to the Claude model version and to this CHANGELOG release. Bump rule is by re-run
  impact: MAJOR = rows below MUST be re-translated, MINOR = re-run recommended,
  PATCH = no re-run. `min_valid` per component is the re-run threshold. This answers
  "a bug was fixed in the tooling — which stored translations predate the fix and
  need a batch re-run?", which the model version alone could not.
- Every new row now carries `provenance.pipeline` (flat `<comp>_version`/`<comp>_sha`
  keys + echoed `model_version`), wired into both store producers: `run_batch.py`
  and `promote_final_cards.py`.
- **Forgotten-bump guard**: the manifest records the content SHA each version was
  frozen at; `pipeline_version.py check` (and a WARNING in `run_batch.py collect`)
  fires when the prompt/glossary/script files changed but the version was not bumped.
  Run `pipeline_version.py freeze` after a deliberate bump.
- `audit_translation_provenance.py` now reports pipeline-version groups, missing-stamp
  count, and stale (below-`min_valid`) rows. `pipeline_version.py stale` lists rows
  needing re-translation; `stamp-md` refreshes a `_pipeline …_` footer on rendered
  `.md` cards; `backfill` stamps legacy unversioned rows with *explicitly asserted*
  versions (never guessed), mirroring the no-guessing philosophy of the provenance audit.
- The `.md` footer is now written automatically at render time, not only via a batch
  `stamp-md` pass: `_pilot_collect.py` stamps each whole card it emits (model + date from
  the wf meta), and `root_glue_translated.py` stamps the assembled `.NESTED.md` once at
  the end. Split-root **sub-cards deliberately carry no footer** — `root_glue`'s `body_of`
  keeps everything after the title, so a per-sub-card footer would scatter through the
  glued article; the glue step stamps the whole card instead. The render-side files are
  intentionally NOT in the `script` hash set (a footer-format tweak must not force a
  re-translation), so this changes no component version.
- Live store state at introduction: 10,794 rows, all pre-versioning → bucketed as
  "unversioned legacy" (NOT flagged stale, so the deploy does not falsely mark every
  historical row for re-run). Baseline frozen at prompt/glossary/script v1.0.0.

## 2026-07-03

### Translation provenance audit/backfill
- Added `src/audit_translation_provenance.py` to report RU/EN provenance counts,
  input-hash gaps, partial-card rows, and workflow/date/model groups for
  `src/pwg_ru_translated.jsonl`. In `--write` mode it conservatively marks
  ambiguous legacy `sonnet` rows as unresolved without inventing an exact model
  version.
- Hardened `src/promote_final_cards.py`: future RU promotions must pass
  `--gen-model-version <exact-model-id>` when workflow metadata lacks an exact
  version. The stale implicit default is gone.
- Live store finding: 10,856 rows; 10,446 older RU rows had no exact
  `model_version`, 410 RU rows already had `claude-sonnet-5`, and 8,574 EN
  provenance rows were already exact-versioned. The older RU rows were marked
  unresolved locally; no translation text or review status changed.

## 2026-07-02

### Renou H4 citation bias + Step-0 pilot review sheet — step 1 executed
- **H4 confirmed**: the epic is under-cited relative to corpus usage in **all 8
  dictionaries** (log2 bias PWG −1.65, MW −2.24, PW −4.21, AP −2.54, AP90 −2.34,
  BEN −0.97, SCH −6.62, BHS −6.86; all 95% bootstrap CIs exclude zero); rgveda
  under-cited in 7/7 reachable dicts; kāvya over-cited in 5/8 (PWG, MW, AP, AP90,
  BEN) and under-cited in the 3 sparsest citation profiles (PW, SCH, BHS).
  Method: entry-level `<ls>`-route register shares vs
  [renou_corpus_map.py](src/renou_corpus_map.py) attestation-level
  baseline, log2 ratio, 1,000-rep bootstrap CI over entries, scope-guarded to
  both-route registers. Write-up:
  [RENOU_H4_CITATION_BIAS.md](RENOU_H4_CITATION_BIAS.md); tool
  [src/renou_h4_citation_bias.py](src/renou_h4_citation_bias.py); dumbbell figures
  [research/figures/renou/h4_citation_vs_usage_{dict}.svg](research/figures/renou/);
  appended as F6 to [RENOU_FINDINGS.md](RENOU_FINDINGS.md).
- **Step-0 pilot sample + review sheet**: deterministic 70-entry stratified sample
  (seed 42, 5 strata — dcs-only states, bhs-only V, maximal-span suspects,
  single-era dcs_adds, corroborated controls) across all 8 dictionaries, each item
  carrying full evidence (provenance, resolved `<ls>` citations re-extracted
  read-only from csl-orig, DCS state_support detail). Sampler:
  [src/renou_pilot_sample.py](src/renou_pilot_sample.py) → committed
  [src/renou_pilot_sample.jsonl](src/renou_pilot_sample.jsonl). Interactive
  single-file HTML review sheet (approve/reject/defer + note, localStorage
  autosave, decisions.json export, no server/CDN):
  [review/renou_pilot_sheet.html](review/sanskritlexicography-renou-hypotheses_pilot_review.html), generated by
  [src/build_renou_pilot_sheet.py](src/build_renou_pilot_sheet.py). Awaiting MG's
  votes → `RENOU_VALIDATION.md` (step 2 of the programme).
- Computed by Sonnet 5 (`claude-sonnet-5`), per
  [RENOU_HYPOTHESES.md](RENOU_HYPOTHESES.md) execution order step 1.

### Renou hypothesis-testing programme (H1–H7) — spec locked
- **[RENOU_HYPOTHESES.md](RENOU_HYPOTHESES.md)** — executable specification for seven
  hypotheses on the Renou tagging system, written for fresh-session (Sonnet-tier)
  execution: H4 dictionary citation bias (first, no gate), Step-0 pilot human
  validation (70 entries, 5 contested strata, interactive review sheet), H6 Zipf
  agreement (principled `renou_low_info` threshold), H1 Vedic survival curves,
  H5 MW–PWG citation-lineage containment, H3 register disjointness, H2 compound
  inflation (cross-repo, VisualDCS). Three-track visualization workplan
  (audit-report charts → paper figures → gated GH-Pages portrait demo). Locked
  MG decisions 02-07-2026: destination = pwg_ru infrastructure + citation-bias
  study, findings paper later; pilot-size validation; all hypotheses in order.
  Spec authored by Fable 5 (`claude-fable-5`); execution tier per step in the doc.
- [RENOU.md](RENOU.md) links the programme from its cross-axis section.

## 2026-06-29

### Structured grammar layer — nominal grammar, Zaliznyak index, reverse dictionary
- **Nominal grammar layer** ([GRAMMAR_LAYER.md](GRAMMAR_LAYER.md)): `nominal_grammar.py`
  (`nominal_grammar_for` — stem class from the SLP1 final, Whitney §§ from a hand-verified
  concordance, vidyut subanta paradigm with the `nyap` fix for feminine ā/ī/ū stems) +
  `mw_compounds.py` (106,603 MW `<k2>` em-dash compound segmentations, accent-stripped).
- **Whitney exception §§** folded into the root layer (`whitney_grammar.json`, 289 records by
  whitney_no, capped against high-frequency over-match).
- **A/B test → grammar-in-translation REJECTED** ([NOMINAL_GRAMMAR_AB.md](NOMINAL_GRAMMAR_AB.md),
  per-card evidence in [NOMINAL_GRAMMAR_AB_DETAIL.md](NOMINAL_GRAMMAR_AB_DETAIL.md)): wired
  per-card injection (`gen_opt_harness2.py --nominal [--no-grammar]`), ran arm B (grammar ON) vs
  arm A (OFF) on 8 stratified headwords + blind Opus judge → **A 5 / tie 2 / B 1**; 0 nulls,
  100% markup fidelity both arms. Decision: nominal windows run grammar **OFF**; portraits left
  untouched so the harness never inlines grammar.
- **Zaliznyak inflection index** ([ZALIZNYAK_INDEX.md](ZALIZNYAK_INDEX.md)): `zaliznyak_index()` →
  compact token `G·T S F` (gender · Whitney type 0–8 · Vedic stress a/b/— · flags `*°+N`),
  e.g. agni `m·3b`, rājan `m·8n*`, abaddhamukha `mfn·1+2`.
- **Reverse dictionary + per-word dataset** (`reverse_index.py`): over all 123,366 PWG entries →
  98,639 indexed → 335 paradigm tokens. FAIR outputs: `headword_index.tsv` (per-word grammar:
  `k1·hom·lex·accented·index·stem_class·compound·irregularities`), `reverse_paradigm_index.json`,
  `paradigm_stats.tsv`. **Declension display**: `--show <token>` / `--table <SLP1> <lex>` render
  the vidyut paradigm.
- **Accent a–f axis** documented as an encoding task (not a missing source): Whitney's per-case
  accent rules are already ingested (§§315–319/350/372/390/423/446), PWG `key2` gives per-word
  accent, and **VedaWeb** ([reference](https://vedaweb.uni-koeln.de), CC BY 4.0, C-SALT-linked)
  is the validation set. Logged in [../FINDINGS.md](../FINDINGS.md).
- **Released v0.0.32** (GitHub release; published after an api.github.com TLS-timeout window).
- **VedaWeb accent-axis probe CONFIRMED**: VedaWeb 2.0 API live (`vedaweb.uni-koeln.de/api`,
  FastAPI); `POST /api/search {type:quick,q:agni}` returns the udātta word-split from the Casaretto
  et al. (2025) annotation resource (RV 6.59.3: `…agnī́; ávasā; …devā́`), position-aligned with
  lemma+morphology layers + a bulk `export` endpoint. The accent axis is de-risked — only the
  Whitney-rule encoding + join remain. Turnkey API path + resource IDs in [ZALIZNYAK_INDEX.md](ZALIZNYAK_INDEX.md).
- **FAIR data package** [`src/datapackage.json`](src/datapackage.json) (Frictionless, CC-BY-SA-4.0)
  over the five grammar resources with field schemas, sources (PWG/MW/Whitney/WhitneyRoots/vidyut),
  and deterministic-rebuild provenance; archivable on its own DOI track ([DOI_PLAN.md](DOI_PLAN.md)).

### Fast print/DH acceleration review
- Added [PRINT_DH_ACCELERATION_REVIEW.md](PRINT_DH_ACCELERATION_REVIEW.md), a compact
  next-review queue for speed, Digital Humanities/FAIR readiness, and print
  feasibility. It preserves the current verdict: bulk translation can continue
  after fresh `sTA`, while print publication remains blocked by G5/G6/G7/G10.
- Added [roadmap/print_dh_acceleration_review.json](roadmap/print_dh_acceleration_review.json)
  with P0/P1/P2 items for fresh `sTA`, deterministic audit, semantic queueing,
  traceability, G5/G6/G7, renderer decisions, reproducibility, front matter, and
  DOI/citation finalization.
- Added [NEXT_REVIEW_PACKET.md](NEXT_REVIEW_PACKET.md), the executable narrow
  checklist for the actual next move: fresh `sTA` audit, mechanical stop/go,
  minimal semantic review, `BU` hold/advance decision, and print renderer
  feasibility from `agni`, `akzara`, and `ap`.
- Locked the Max batch-size decision into [NEXT_REVIEW_PACKET.md](NEXT_REVIEW_PACKET.md)
  and [src/pilot/RUN_FREQ_MAX.md](src/pilot/RUN_FREQ_MAX.md): do not translate
  10 big dhātus at once yet. Run staged evidence instead: fresh `sTA`, then
  clean-ready `BU`/`as`/`i`, then prune/recheck `gam`/`yuj`/`vid`/`han`.
- Added [H027-Sonnet_RussianTranslation_claude_code_max_29.06.26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/archive/H027-Sonnet_RussianTranslation_claude_code_max_29.06.26.md),
  a current Claude Code Max handoff with Stage A/B/C commands, root status,
  audit return artifacts, token/time fields to preserve, and print-feasibility
  side checks.

### F-gate-nws-fp fix — `has_text_signal()` now counts NWS owner citations
- Fixed false-positive flood in `suspicious_attested_without_text_signal` for `*_zz_pw*`
  cards and NWS cards. Root cause: `citation_blob()` skips `equivalence_type` (where
  `[NWS: OWNER]` tokens land), and PW cards have `<ls>` citations only in the `head` sense —
  so 70+ numbered verb senses per card each fired the flag independently.
  Fix: (1) `has_text_signal()` now scans all sense field values (not just `citation_blob()`)
  for `[NWS:\s` patterns; (2) `semantic_risks()` computes a card-level
  `card_has_text_signal` (restricted to `source_type='attested'` senses) and suppresses
  per-sense FPs when the card as a whole already has a text signal.
  Added `test_nws_fp_suppressed()` to
  [`src/pilot/window_selftest.py`](src/pilot/window_selftest.py) covering both the PW
  card case (head `<ls>` suppresses numbered senses) and the NWS card case
  (`[NWS: Graßmann…]` in `equivalence_type`). All 13 selftests pass.

## 2026-06-28

### Print, DH, and speed readiness review
- Added [PRINT_DH_SPEED_REVIEW.md](PRINT_DH_SPEED_REVIEW.md), a ranked review pack for
  scaling speed, Digital Humanities/FAIR readiness, print readiness, and lexicographic QA.
  It distinguishes five readiness levels: continuing bulk translation, reviewed core tranche,
  immutable digital edition, printed bilingual dictionary, and full PWG tail.
- Added [roadmap/print_dh_speed_review.json](roadmap/print_dh_speed_review.json), a
  machine-readable companion with `P0 blocks scale/print`, `P1 slows production`, and
  `P2 improves scholarly polish` items. The P0s are explicit: fresh `sTA` Max output,
  human G5/G6/G7 gates, zero print-ready rows, and stale semantic-risk evidence.
- Re-ran the status/release checks used as evidence: `root_window_status.py sTA`,
  `prompt_rule_audit.py --cards wf_output.json --review-limit 25`,
  `preflight_remaining_gates.py`, `release_readiness.py`, and `window_selftest.py`.
- Added [HUMAN_REVIEW_MINIMIZATION.md](HUMAN_REVIEW_MINIMIZATION.md) and
  [PRINT_ENTRY_SPEC.md](PRINT_ENTRY_SPEC.md) as the next practical layer: exact G5/G6/G7
  reviewer files, editable columns, validation commands, and the target printed bilingual
  entry shape. [roadmap/print_review_minimum.json](roadmap/print_review_minimum.json)
  records the same minimum human-review queue in machine-readable form.
- Added [PRINT_ENTRY_EXAMPLES.md](PRINT_ENTRY_EXAMPLES.md) and
  [roadmap/print_entry_examples_review.json](roadmap/print_entry_examples_review.json),
  using real local `agni`, `akzara`, and `ap` merged cards to test the printed-entry spec
  while labeling them as non-print-ready layout/QA prototypes.

### Fast low-human audit hardening
- **Manual-rule drift is now part of the canonical window audit.**
  [src/pilot/audit_window.py](src/pilot/audit_window.py) runs the new `prompt_semantic`
  gate on every non-stale workflow audit. The gate reuses
  [src/pilot/prompt_rule_audit.py](src/pilot/prompt_rule_audit.py) to verify that both the
  committed template and generated optimized harness still carry the live manual-derived
  rules. Missing required prompt/manual wiring is a blocking audit failure.
- **Semantic triage stays cheap and mostly non-blocking.** The same gate writes a ranked
  semantic-risk queue for low-interaction review, while only high-confidence mechanical
  defects feed requeue: empty Russian glosses, broken markup, unbalanced Sanskrit delimiters,
  translated sigla/grammar abbreviations, German residue, and conservative `{%...%}` gloss
  leaks. Noisy evidence heuristics such as suspicious `source_type` signals remain review
  hints, not automatic reruns.
- **Focused PWG `{%...%}` gloss audit added.** German braced glosses are checked for leakage
  into Russian, while Latin/English/binomial literal glosses are checked for accidental
  alteration when a target braced literal is present.
- **Reports now show theory coverage.** `audit_window.report.*` and `window_status.*` surface
  the live harness coverage: Apresjan, Hartmann, Gonda/Vogel, Tubb, Baalbaki,
  Apte/Gillon/Inglese-Geupel, and Mitrenina/Zaliznyak-Paducheva/Ruppel. Riemer and Klosa are
  explicitly reported as methodology/design inputs unless later promoted to hard live rules.

### Audit guardrails and operator use cases
- **NWS filename resolution hardened for root-split windows.** [src/nws_split.py](src/nws_split.py)
  now resolves `~~` sub-card stems literally before safe-name fallbacks, so root-window NWS
  checks can read the same files the optimized harness translates. It also distinguishes
  `NO-RAW`, `NO-CARD`, and neutral `NO-NWS` states.
- **Audit requeue policy made explicit.** [src/pilot/audit_window.py](src/pilot/audit_window.py)
  requeues missing raw/card outputs, leaves cards without an NWS layer neutral, and quarantines
  only true NWS owner misattribution.
- **Harness scope is now part of root preflight.** [src/pilot/root_window_status.py](src/pilot/root_window_status.py)
  requires the optimized harness selected-key list to match the intended full or pending root
  scope before recommending a Max run.
- **Operator docs refreshed.** [README.md](README.md) now lists the active guardrails, and new
  [USE_CASES.md](USE_CASES.md) maps common production tasks to their command paths: preflight,
  fresh Max runs, stale-output recovery, requeue, sampled judging, dashboard monitoring, release
  checks, and corpus API retry.

### Cleanup — legacy workflow archive and flaky-network resilience
- Archived the superseded a-section runbook and old Workflow-derived harness under
  [src/pilot/archive/legacy_max_2026-06-27/](src/pilot/archive/legacy_max_2026-06-27/).
  The active operator path is now only the frequency-window loop documented in
  [src/pilot/RUN_FREQ_MAX.md](src/pilot/RUN_FREQ_MAX.md).
- Generated dashboard/status snapshots are ignored and treated as local runtime artifacts:
  `release/gate_status_snapshot.{json,md}` and `src/pilot/output/*status/report/queue*`.
- `build_corpus_lexicon.py` now treats flaky DeepSeek/OpenRouter calls as retry debt:
  configurable retries/timeouts/backoff, visible failure logging to
  `src/corpus_lexicon.failures.jsonl`, and `--retry-failed` for later catch-up.

## 2026-06-27

### Live operations dashboard
- **Local browser dashboard for Max-run + print-gate status.** New
  [src/pilot/dashboard_server.py](src/pilot/dashboard_server.py) serves
  `http://127.0.0.1:8765/` with `/api/status`, reading the latest window status,
  audit report, ledger, event log, requeue list, print-gate snapshot, and file
  freshness. The page refreshes every 5 seconds and degrades missing optional
  files to "not available yet".
- **Append-only operational event log.** New
  [src/pilot/dashboard_events.py](src/pilot/dashboard_events.py) writes
  `src/pilot/output/dashboard_events.jsonl`; [src/pilot/audit_window.py](src/pilot/audit_window.py)
  records stale refusals, audit starts/ends, gate summaries, requeue counts,
  glue results, and crash states. [src/preflight_remaining_gates.py](src/preflight_remaining_gates.py)
  records print-gate snapshot events after writing G5/G6/G7/G10 summaries.

### Production hardening — provenance, stale guards, and print-gate dashboard
- **Optimized Max workflows are now provenance-bearing and tool-locked.**
  [src/pilot/gen_opt_harness.py](src/pilot/gen_opt_harness2.py) emits top-level workflow
  `meta` (root, mode, selected keys, rootmap SHA-256, raw/portrait SHA-256 values, generator
  version, timestamp) and asserts every translate `agent(...)` call has `tools: []`.
- **Stale workflow outputs now fail before mutation.** [src/pilot/audit_window.py](src/pilot/audit_window.py)
  compares workflow provenance against the current rootmap and inputs before collect/gates/glue;
  missing meta, key drift, rootmap drift, or input-hash drift records `stale_artifact`. The old
  106-card `sTA` `wf_output.json` correctly refuses to audit against the regenerated 123-card
  rootmap; `--allow-stale` is reserved for forensic inspection.
- **Window state is ledgered.** `audit_window.py` writes latest status plus append-only
  `window_ledger.jsonl`; [src/pilot/root_window_status.py](src/pilot/root_window_status.py)
  now reports rootmap/input hashes before Max spend. A one-card matching fixture exercised the
  normal collect + free-gate + glue path without model tokens.
- **Print-gate dashboard.** [src/preflight_remaining_gates.py](src/preflight_remaining_gates.py)
  now writes `release/gate_status_snapshot.json` and `.md` with G5/G6/G7/G10 counts while
  leaving all human labels and review decisions untouched.

### Token optimization for the Max bulk run — "weeks not days" (BALANCED tier)
- New [TOKEN_OPTIMIZATION_2026-06-27.md](TOKEN_OPTIMIZATION_2026-06-27.md): measured the real
  quota driver and re-architected the bulk run so a single Max seat sustains weeks of work
  instead of burning out in 3–4 days. **Finding 1** — the cost is `cache_read ≈ context × turns`,
  not prompt size; **Finding 2** — the multiplier is *assistant turns*, driven by agents
  re-`Read`ing `raw.txt`/`portrait.json` 4–12× per card. One giant root at the old config ≈
  **9–10 M tokens**.
- **A/B measured (tyaj baseline vs optimized):** agents 28→14, turns 138→47, Read calls 60→19
  (**3.2×**), `cache_read` 2.74 M→0.85 M (**3.2×**), wall-clock 6.6→2.5 min, transient failures
  3→**0**. Net ~2× on the headline metric, ~3.2× on the real driver.
- **QA reshape — "Python at max, LLM at minimum."** The LLM judge's only irreplaceable job is
  catching *mistranslation*; everything mechanical is now free and 100%-coverage in Python. New
  gate [src/audit_coverage.py](src/audit_coverage.py) catches silently dropped/fabricated senses
  (COVERAGE-LOW <80% / COVERAGE-OVER >150%, NWS/supplement cards n/a). Per-card LLM judge dropped
  → free gates (`audit_translation.py` markup + `audit_coverage.py` senses + `nws_split.py` owner
  map) on every card, LLM judge only on Python-gate flags + a ~5–10% mistranslation sample.
- **Gate false-positive guard.** Both free gates got an absolute-difference floor so a ±1
  span/sense gap on a 1–4-span card no longer false-flags, while the giant-head citation dump
  (e.g. 7/125) still trips: [src/audit_translation.py](src/audit_translation.py) needs ≥2 absolute
  `<ls>`/`{#}` loss in addition to the 90/85% ratio; `audit_coverage.py` uses `(raw−card)≥2` /
  `(card−raw)≥3`.
- **Head lane — sense-aware Python split (Finding 5).** Giant HEAD cards (`*_pwg00`, ~1 per root)
  overflow a single pass and shed their citation apparatus. New `sense_chunks()` in
  [src/_pilot_gen_merged.py](src/_pilot_gen_merged.py) splits the head at `<div n=…>` SENSE
  boundaries (not line count), grouping senses until their combined `<ls>` count exceeds
  `HEAD_CIT_BUDGET` (=18) so each part is citation-light and flows through the cheap single-turn
  lane. tyaj head: 1 dense 146-`<ls>` blob → 8 sense-parts; whole root 19 sub-cards (15 single-turn
  / 4 multi-turn). The multi-turn no-abridge lane survives only as the rare fallback for a lone
  over-budget sense.
- **Reliability.** Optimized harness adds 1 automatic retry per stage + a post-run missing-key
  re-queue (Finding 4: ~10–20% transient `Connection closed mid-response` rate across gam/tyaj).
- **Decision (M.G.):** BALANCED tier adopted — single-turn inlined inputs + free Python gates +
  sampled judge. Open headroom: restrict the Read tool to force true single-turn (residual 19
  reads → 0). [src/pilot/RUN_FREQ_MAX.md](src/pilot/RUN_FREQ_MAX.md) updated with the optimized
  run loop and the three-gate QA stack.

### Head lane LOCKED — two structural bugs fixed, deterministic dup guard added
- **Finding 7 — dense-lane over-production.** The first head lane let "dense" cards read their
  sibling part-files (multi-turn), so `pwg00` rendered the WHOLE head (13 senses) and `pari`
  173 `<ls>` vs its 86 — duplicating senses other parts also produce. Fix in
  [src/pilot/gen_opt_harness.py](src/pilot/gen_opt_harness2.py): BOTH lanes inline their own part
  only (single-turn) + an anti-roaming/anti-memory guard; dense cards got cheaper too. The
  production generator is now committed + portable (regenerates the harness per root).
- **Finding 8 — causative tail mis-tag.** A secondary-conjugation section (caus./pass./desid.)
  RESTARTS numbering at 1 and its `<ab>caus.</ab>` marker rides at the END of the previous
  sense's line; the split orphaned caus.1/2/3 → the model tagged them bare 1/2/3, colliding with
  simple-verb senses. Fix in [src/_pilot_gen_merged.py](src/_pilot_gen_merged.py) `sense_chunks`:
  detect the numbering reset, merge the whole secondary tail into one chunk, relocate the trailing
  `<ab>caus.</ab>` marker to its head, and label the part `(CAUSATIVE … tag each "caus. N")`.
  Model now tags `caus. 1/2/3`.
- **New deterministic gate (free) — [src/audit_sense_dupes.py](src/audit_sense_dupes.py).** Flags
  any numbered sense rendered by >1 head-part of the same homonym; namespaces secondary-section
  senses via the raw LAYER header so a legitimate caus-renumber passes while genuine
  over-production fails. Validated: FAILs the Finding-7 output (8 dups), PASSes the fixed output.
- **Final tyaj A/B (locked harness):** 19 cards, 640 k tok, 3.4 min, **0 failures**; dup guard
  PASS, NWS PASS, fidelity 18/19 (the 1 miss = homonym-3 head dropped 2 paradigm spans → normal
  re-queue). `pwg07` tagged `caus. 1/2/3`; glue → `tyaj.NESTED.md`, no duplicated senses.
- **The Workflow-tool harness runs from-chat.** Because the optimized harness inlines its inputs
  (no `node:fs`), the freq-queue run no longer "needs a human-driven Max session" — it drives
  from the in-chat Workflow tool. Next: the first real freq window (sthā/bhū/gam), run-to-cap for
  the absolute weekly-quota number. See [H026-Sonnet_RussianTranslation_freq_run_27.06.26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/archive/H026-Sonnet_RussianTranslation_freq_run_27.06.26.md).

### Finding 5 tail — dense single-sense citation batching
- **Single over-budget senses now split deterministically.** The first `sTA` run exposed the
  remaining Finding-5 tail: `pwg00` sense 1 packed 125 `<ls>` citations inside one `<div>`, so
  whole-sense splitting could not prevent citation loss. [src/_pilot_gen_merged.py](src/_pilot_gen_merged.py)
  now citation-batches any single over-budget head sense with `HEAD_CIT_BATCH_BUDGET` (defaulting
  to `HEAD_CIT_BUDGET=18`) and records `batch_of` / `batch_index` / `batch_count` in the rootmap.
- **Batch-aware gates and glue.** [src/audit_sense_dupes.py](src/audit_sense_dupes.py) permits a
  repeated sense tag only when every duplicate is a rootmap-declared citation batch for that exact
  canonical sense; ordinary cross-part duplicates still fail. [src/root_glue_translated.py](src/root_glue_translated.py)
  labels these packages as citation batches in the nested article.
- **sTA regeneration result.** Re-splitting `sTA` yields 123 sub-cards with 26 declared
  citation-batch entries; each batch has ≤18 raw `<ls>` tags and lettered batches keep canonical
  tags such as `9a` / `9b` (no bare-letter drift). Verified locally with `py_compile`,
  `verify_root_glue.py`, `audit_sense_dupes.py`, and positive/negative duplicate-batch smoke tests.
  The remaining acceptance step is a Claude/Max translation re-run of the generated batch cards,
  not a Codex-shell requirement.
- **Review follow-up — stale inputs + headtest.** Root-split regeneration now removes old
  `root~~*.raw.txt` / `.portrait.json` generated inputs before rewriting a rootmap, so stale
  unbatched cards cannot leak into glob-driven tools. `gen_opt_harness.py headtest` now selects
  the first homonym-0 `pwg00` / `pwg00b*` section from rootmap metadata; for `sTA` it correctly
  picks `s_t_a~~h0_00_pwg00b00`. Verification: stale raw/portrait count 0 after `sTA` regen,
  `verify_root_glue.py` PASS, `git diff --check` clean.

### Audit workflow orchestrator — one deterministic window report
- Added [src/pilot/audit_window.py](src/pilot/audit_window.py), a single command for the free
  deterministic gates:
  `python src/pilot/audit_window.py wf_output.json --root sTA --write-requeue`. It runs
  collection/NWS attribution, markup fidelity, sense coverage, and sense-duplicate checks against
  the same workflow key set, optionally glues the root, preserves each gate's stdout in JSON, and
  prints a compact final table.
- Machine-readable artifacts now land in `src/pilot/output/`: `audit_window.report.json`,
  `audit_window.report.md`, and `requeue.keys.txt`. The command exits non-zero when any card must
  be requeued or a gate crashes.
- `audit_translation.py` gained `--wf wf_output.json` so it audits workflow keys instead of the
  default manifest while preserving the manifest compatibility path. `audit_coverage.py` now marks
  missing/stale raw inputs as `NO-RAW`, so rootmap reshapes cannot silently pass coverage.
- On the stale pre-batch `sTA` workflow output, the orchestrator writes 20 requeue keys: obsolete
  unbatched `pwg00*` labels plus the known residual `ud`, `ni`, and `pw07`.
- **Speed pass.** `audit_window.py` now bypasses the legacy `run_real_test.py audit` subprocess
  loop: it collects once, calls `nws_split.check_result()` in-process, delays any quarantine until
  read-only gates finish, and runs the free gates concurrently. Current `sTA` window timing:
  ~1.26 s vs ~8.62 s for the legacy audit path.
- **Production-line pass.** The frequency runbook now documents `audit_window.py` as the single
  audit path. `audit_window.py` also writes `window_status.json` / `.md`; new helpers
  `root_window_status.py` and `requeue_from_audit.py` preflight root splits and generate exact
  rerun harnesses from `requeue.keys.txt`, respectively.

## 2026-06-26

### Stale-doc cleanup — align planning/runbook docs with the current pipeline
- Triaged the pwg_ru `.md` set against current ground truth (judge = Sonnet-bulk + Opus-on-reject;
  four prompt nits done-in-harness; harvest ported; `pwg_preverb1.txt` sandhi-join dropped;
  `--root-split` hook done). Fixed present-tense contradictions, kept correct history intact:
  - **STRATEGY.md** (judge-every-card now attributes Sonnet-bulk/Opus-on-reject),
    **FREQ_TEST_RUNBOOK.md** (step-2 judge model; +dropped-`pwg_preverb1` note; +four-nits/`nws_split`
    done-status note), **HANDOFF** (judge-model line scoped to the validation pass; dropped the
    `pwg_preverb1` follow-up).
  - Superseded-pointers added to the pre-Max-harness plans **IMPLEMENTATION_PLAN.md** /
    **PIPELINE_ARCHITECTURE.md**; **PILOT_COST.md** §7 "now-implemented" note; **research/ROOT_ENTRY_ARCHITECTURE.md**
    `--root-split`-done note. `JUDGE_POLICY.md` is the single source of truth for the judge policy.
- `tmp.md` (chat-narration scratch) left untouched — it is gitignored (`.gitignore:6`), never in the repo.

### Judge escalation implemented — Sonnet bulk, Opus only on the hard cases
- Flipped [src/pilot/run_pilot_wf.js](src/pilot/run_pilot_wf.js) from "Opus judges every card" to
  the decided [research/JUDGE_POLICY.md](research/JUDGE_POLICY.md) policy: **Sonnet judges every
  card; Opus re-judges ONLY a reject** (`isHard` = `ok=false || severity>=3`). The Opus verdict is
  final (becomes `judge`; Sonnet's original kept as `judge_sonnet`, `escalated:true`). Publishable
  cards (sev 1–2) spend **zero Opus tokens** → weekly-quota headroom (PILOT_COST §6/§7), the binding
  constraint on a single Max seat.
- Pipeline now 3-stage (Translate · Judge · Adjudicate); judge prompt factored model-neutral
  (`judgePrompt`/`CHECKS`). Justified by the A/B in JUDGE_AB.md (κ=1.0 over 474 cards, ~0.5 %
  disagreement). `node --check` clean; `_pilot_collect.py` reads `judge` (now the final verdict)
  unchanged. JUDGE_POLICY.md + RUN_FREQ_MAX.md marked implemented. **TODO:** wire the periodic ~5 %
  Opus audit of clean-passed cards (rollout step 3) into the window loop.

### Pre-launch audit + harvest ported into the production Max harness
- **Launch-readiness audit (Track A).** Verdict: **Sonnet translator is GREEN to start the
  first instrumented window.** All 4 "pre-run prompt nits" are confirmed already encoded in
  [src/pilot/run_pilot_wf.js](src/pilot/run_pilot_wf.js) (HARD RULES 3/4/5 + the NWS owner-map);
  all 8 harness/gate scripts exist and are wired (`nws_split.py` quarantine + `audit_translation.py`
  fidelity gate). The only true finding: the harness **inlines its own prompt** and does not read
  `pwg_ru_prompts/*.txt`, so the literature-harvest refinements had not reached the run.
- **Harvest ported into the live harness.** Added Sanskrit-microstructure rendering guidance to
  `run_pilot_wf.js` (samāsa right-headedness + `-ādi`=hypernym, the *yad…tad* correlative map,
  śāstric formulas, synonym-string cardinality, comma/semicolon sense-grouping, manner/position
  forcing) + judge check 7. Apresjan discrimination, the kośa two-source principle, and
  equivalence-type were already live. `node --check` clean.
- **Runbook refreshed.** [src/pilot/RUN_FREQ_MAX.md](src/pilot/RUN_FREQ_MAX.md): the stale "one-time
  nits" section is now a verification checklist (all done-in-harness); the window loop gained the
  `SECTION='a'→'freq'` warning and the `audit_translation.py` fidelity-gate step.
- **Findings status map.** [MANUALS_FIVE_DEEP_DIVE.md](MANUALS_FIVE_DEEP_DIVE.md) closing section
  rewritten from a "queued" list to a per-finding **pipeline-status table** (live / ported /
  deferred). Riemer's sense-distinctness battery and Klosa's display layer are marked deliberately
  out of scope for the bulk translation step (PWG sense division is authoritative; display is a
  post-translation frontend concern). pwg_ru.md gains a "теоретическая основа" pointer block.

### Literature shelf mined for pwg_ru → folded into prompts, glossary, and docs
- New [LITERATURE_FOR_PWG_RU.md](LITERATURE_FOR_PWG_RU.md): three-pass full-text harvest of
  the whole `literature/md/` reference shelf, distilled into drop-ins **by insertion point** —
  §1 glossary tables (canonical RU grammar terms, the *yad…tad*→correlative map, a 19th-c.
  German→RU spelling/term decoder, the Apresjan register tagset), §2 translator-prompt rules,
  §3 QA-judge defect classes, §4 corpus-gate/strata rules, §5 web display.
- New per-manual audit [MANUALS_FOR_PWG_RU.md](MANUALS_FOR_PWG_RU.md): walks all **37**
  `Lexicography-Manuals/` one at a time with a verdict each — **19 drive theory · 2 marginal ·
  15 serve other repos · 1 OCR-blocked** (Rātānjanakar; not a run blocker).
- New deep-dive [MANUALS_FIVE_DEEP_DIVE.md](MANUALS_FIVE_DEEP_DIVE.md): detailed,
  text-grounded theoretical input of the 5 load-bearing manuals (Apresjan · Riemer ·
  Hartmann & James · Gonda–Vogel · Klosa) for the Sanskrit–Russian dictionary, with
  quotations + page/chapter anchors, a "→ Sa–Ru application" per point, and a
  "how the five compose" synthesis (Riemer→Hartmann→Apresjan decision chain;
  Apresjan⇄Klosa glossary/reverse-index loop).
- **Folded into the live prompts:** [pwg_ru_prompts/1_perevod.txt](pwg_ru_prompts/1_perevod.txt)
  gains compound-type (samāsa) rendering, case-absolute constructions, śāstric formulas, and a
  pointer to the new manual glossary; [pwg_ru_prompts/2_qa_sudya_opus.txt](pwg_ru_prompts/2_qa_sudya_opus.txt)
  gains the matching judge defect classes.
- New hand-curated glossary [glossaries/de_ru_translation_aids.md](glossaries/de_ru_translation_aids.md)
  (compound-type RU names, case-absolute constructions, śāstric formulas, the correlative map,
  the 19th-c. German orthography decoder), each row sourced to a `LITERATURE_FOR_PWG_RU.md`
  section. This is the **one manually-maintained** file in `glossaries/` (the rest are
  `renou_glossary.py`-generated).

### Renou register glossaries — first tangible artifacts from the register axis
- New [src/renou_glossary.py](src/renou_glossary.py): filter the Renou-tagged dictionaries
  by register / state / provenance → a deduplicated headword glossary (aggregated by IAST
  across the 8 dicts; each row = states · register provenance ls/dcs · dicts · senses).
  Supports `--state`, `--exclude-state` (cross-axis slices), `--prov`, `--min-dicts`,
  `--state-only`, md/tsv.
- Shipped **8 glossaries** in [glossaries/](glossaries/README.md): register lexica —
  **épigraphique** (709 inscriptional words: `akṣayanīvī`, `abhayagirivihāra`, dynastic
  names), **bhāṣya** (14,498; 10,320 in ≥2 dicts), **kāvya** (26,973), **bauddha** (25,740),
  **jaina** (286); cross-axis slices — Vedic-in-commentary (`bhasya∩I`, 6,895), born-in-kāvya
  (`kavya∖I`, 20,758), Vedic-only archaisms (`state I` only, 25,220). Headline finding:
  **484 of 709 épig words (68 %) are corpus-absent** — attested only in inscriptions, so a
  corpus-only method never sees them. The clearest proof the register axis adds signal the
  state axis can't.

### Comparison tables — rows sorted chronologically by edition year
- [`../article-comparison/*.table.md`](https://github.com/gasyoun/SanskritLexicography/tree/master/article-comparison)
  rows now run **oldest → newest** by edition year (WIL 1832 → YAT 1846 → BOP 1847 →
  PWG Bd. I 1855 → … → AP 1957 → PE 1975 → PD 1976), so the side-by-side reads as the
  tradition developing. `#` renumbered; sort lives in `src/_build_tables.py` (stable on
  prior order for same-year ties). (semver `[0.0.12]`)

## 2026-06-25

### Comparison tables — full untruncated entries + the builder, committed
- The side-by-side [`../article-comparison/*.table.md`](https://github.com/gasyoun/SanskritLexicography/tree/master/article-comparison)
  capped each cell at ~800 chars with a trailing ` …`; long entries (STC, PWG, AP90,
  VCP, PE…) showed only a fragment. **Every cell now carries the complete entry**
  (citations `[ ]` stripped, SLP1→IAST, paragraphs joined with ▸); **40** truncated
  cells expanded. PD stays its full sense skeleton (verbatim PD is 20–234 KB).
- Committed the previously-uncommitted table builder as
  [src/_build_tables.py](src/_build_tables.py): regenerates all four tables from the
  full `*.iast.md` sections + the `*.pd-min.md` skeleton, no length cap, with
  **nested-citation-safe** bracket stripping (fixes a stray `]` the old run left on
  nested refs like `[m., [RāmatUp.]]` in akṣara/MW). (semver `[0.0.11]`)

### agni gloss review — agent draft pass over the 130 hand-authored RU glosses
- Produced [`../article-comparison/agni.gloss-review.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/agni.gloss-review.md):
  an Opus-4.8 editorial review of agni's 130 hand-authored Russian sense-glosses against
  the English PD sense, the Sanskrit term, and Russian Indological convention
  (Kochergina / Elizarenkova). **The glosses are untouched** — the output is a
  sign-off worklist for the human editor. Findings: **1 H** (the *agnicayana*
  altar↔rite category error at 4i/4vi), **3 M** (ахаванья→ахавания, hotṛ
  "возливатель"→"призыватель", udātta precision), **3 L** polish, **4** optional
  add-glosses, **6 FYI** English-source OCR typos the RU already corrects.
- This is the **agent-doable half** of the remaining Track B item; the final scholarly
  sign-off on the proposals is the human step. (semver `[0.0.10]`)

### Comparison tables — dictionary edition year on every quote
- Each row of [`../article-comparison/*.table.md`](https://github.com/gasyoun/SanskritLexicography/tree/master/article-comparison)
  now carries the source dictionary's **edition year**, not just the four EN dicts
  that already had one. Years are pulled from the authoritative
  [CDSL front page](https://www.sanskrit-lexicon.uni-koeln.de/) catalog (mirrored in
  `csl-guides/src/data/dictionaries.json`): PWG 1855, pw/PWK 1879, AP90 1890,
  AP 1957, GRA 1873, SHS 1900, VCP 1873, SKD 1886, BUR 1866, CAE 1891, WIL 1832,
  BEN 1866, MW 1899 / MW72 1872, YAT 1846, BOP 1847, STC 1932, PE 1975, PD 1976.
  Header provenance note added. (semver `[0.0.8]`)

### Track B tail — Max-LLM residual per-sense assignment (article-comparison closed)
- **What.** Closed the per-sense corpus tail for the comparison study. Every attested
  Russian rendering that the deterministic matcher dropped into the
  `### Не привязано к значению` bucket of each
  [`../article-comparison/*.persense-ru.md`](https://github.com/gasyoun/SanskritLexicography/tree/master/article-comparison)
  was adjudicated by an **Opus-4.8** pass against the full bilingual PD sense
  skeleton and routed to its specific sense — or kept as honest *other*.
- **Coverage** (per-sense, of aligned occurrences): **agni 100 %** (det 2199 + LLM 16),
  **akṣara 99 %** (237 + 28), **anya 97 %** (1104 + 46), **ananta 97 %** (141 + 13).
  The deterministic pass alone was 97–99 %; the LLM pass closes the synonym /
  paraphrase / pre-1918-orthography tail (e.g. `Агни-Джатаведас`→*as jātavedas*,
  `жертвах`→*sacrifice*, `не гибнет`→*imperishable*, `иныхъ`→*another/other*).
- **How — reproducible, not a one-off LLM call.** Decisions are frozen as an
  `LLM_ASSIGN` override map in [src/_build_persense_ru.py](src/_build_persense_ru.py)
  (surface form → 0-based sense ordinal), mirroring the existing `SYN`/`ROUTE`
  mechanism. Re-running the builder reproduces the assignment deterministically.
  LLM-assigned renderings carry a **°** marker in the table; the coverage line now
  reports the deterministic-vs-LLM split; the residual heading documents that the
  pass ran and what genuinely remains (function words, context fragments,
  off-headword names with no PD sense to bind).
- **Flagship pair (agni + akṣara) priority** per the 2026-06-25 handoff; anya/ananta
  done as supporting examples (confident routes only — the rest left honestly in
  *other*, since anya is a pronoun with a long function-word tail).
- **Still open (heavier editorial pass, not this commit):** publication-quality review
  of the hand-authored RU sense-glosses for the flagship pair (`agni`'s 130 senses).

### Judge-model A/B settled — Sonnet for the bulk judge, Opus for repass + audit
- **Question:** can a cheaper **Sonnet** QA judge replace the **Opus** judge for the scale-up?
  Tested across 5 runs / ~650 judged cards ([research/JUDGE_AB.md](research/JUDGE_AB.md),
  [research/JUDGE_POLICY.md](research/JUDGE_POLICY.md)).
- **Result — indistinguishable.** Run 3 (201 real a-section cards): 191/191 verdict agreement,
  κ = 1.0, 0 Sonnet false-clears. Run 4 (250-item **ground-truth** defect battery — dropped
  anchor / falsified citation / dropped sense / translated Latin / changed number): both **99 %
  recall, 0 % false-positives**, head-to-head 208/208 with each model missing one *different*
  card. No Opus power advantage for the mechanical core of judging.
- **Decision:** Sonnet judges the bulk (≈ halves the judge token cost / Max-quota), Opus
  re-judges every **reject** + a periodic **~5 % audited sample** (halt if false-clear > 1 % or
  κ < 0.7). New [src/judge_disagreements.py](src/judge_disagreements.py) emits a full-context
  queue of the rare Opus-vs-Sonnet conflicts for editor adjudication;
  [src/judge_ab_score.py](src/judge_ab_score.py) scores any A/B.
- **Dropped the synthetic semantic-defect test** on the editor's objection: a wrong-but-related
  gloss (`Theil` → часть vs доля) is **undecidable from a word pair** without the full entry +
  the Sanskrit sense; the decidable cases are rude ones Sonnet already catches. The only honest
  semantic ground truth = real Opus-vs-Sonnet disagreements adjudicated in context — and those
  run **~0.5 %** (0 in run 3, 2 in run 4), so the adjudication queue is near-empty.
- **Lesson kept:** don't build a synthetic test whose ground truth you can't defend; for
  translation correctness the only honest ground truth is the entry in full context.

### Renou *register* axis — subsections as an orthogonal tag (épigraphique, bhāṣya, …)
- **Reread the source.** Renou's five states = his five *chapters*; his *subsections* are
  distinct registers a flat I–V tag can't express. Verified the table des matières from
  the scan → [`../../VisualDCS/docs/Renou_1956_structure.md`](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md):
  **`épigraphique`** lives in Ch. II (p. 94) and **`bhāṣya`** (commentary, its own grammar)
  leads Ch. IV (p. 133) — neither fits the five states. Design in
  [RENOU_SUBSECTIONS_PLAN.md](RENOU_SUBSECTIONS_PLAN.md).
- **New orthogonal `renou_register` field** (multi-label, 20-code lattice), parallel to
  the state — a word can carry registers across eras (a *bhāṣya* on a Vedic base). Two
  provenance-tagged detector routes, same lossless min-support policy as states:
  - **DCS corpus** ([src/build_dcs_renou.py](src/build_dcs_renou.py)): per-lemma `register`
    + `register_support {n,conf}` in the same scan; genre→register + name-stem detectors
    (esp. `bhāṣya` by `*bhāṣya/ṭīkā/vṛtti/…` — DCS has no commentary genre).
  - **`<ls>` citation** ([src/renou_register.py](src/renou_register.py), new): siglum's
    map record → register(s) (PWG genre / MW name); the only route for **`jaina`** (288 MW)
    + `bhāṣya` corroboration (Sāy/Kāś/Pat). Inline dicts (ap/ben/bhs) via
    `renou_sigla.SIGLUM_REGISTER` + `bhs`→`bauddha` wholesale.
  - **dedicated `épig` detector**: an inscription marker in `<ls>` text (`Insch?r`) →
    `epig` (MW 687, AP 17, PWG 9; sparse, as inscriptions are).
- **Wired end-to-end**: `renou.filter_dcs_registers`, the taggers emit `renou_register` +
  `renou_register_provenance` (`ls`/`dcs`/both), `renou_audit.py` register mode
  (coverage + per-register provenance + low-info), `renou_portrait.py` register sub-label
  + a `bhāṣya` editorial note. Coverage ~19–100 % of entries/dict; every lattice register
  populated except `hors_inde` (no source). **The state axis is unchanged.** Use cases in
  [RENOU.md](RENOU.md#use-cases).

### TRIAGE: pre-sorted the legacy `needs_review` queue for the human reviewer
- New tool [src/triage_review_queue.py](src/triage_review_queue.py) reads the
  gitignored `_review_queue.jsonl` (217 legacy `needs_review` cards already scored
  by the Opus QA judge) and **buckets the existing verdicts by defect type** —
  it does **not** re-judge or auto-edit anything. Classifies on the judge's
  *defect clauses* (not whole-reason keywords, which false-match the pass-narration)
  into: **C** source-data defect, **A** mechanical/format (untranslated German
  function-word, anchor/structure damage), **B** translation-quality doubt, plus a
  **FAST** likely-clean tier; orders by the judge's own severity.
- Result: **0 C · 13 A · 19 B · 185 FAST** (217 total). Only **23 cards score
  sev ≥ 2** — the real work; every "source quirk" was faithfully mirrored, so
  nothing escalates to Cologne. **197/217** carry an attested-dictionary
  corroboration. Ranked worklist → gitignored `src/_review_queue.triage.csv`;
  one-page reviewer guide → [REVIEW_QUEUE_TRIAGE.md](REVIEW_QUEUE_TRIAGE.md).
  Final adjudication stays human.

## 2026-06-24

### AUDIT: pruned 6 non-synonym kośas from the synonym channel (9.4 %→7.8 %)
- A data-quality audit of the just-shipped kośa fold (095bee1) found the first-pass
  inclusion of 10 kośas too loose: **6 inject non-synonymy** and were removed from
  [src/build_kosha.py](src/build_kosha.py) `KOSHAS`:
  `anekArthadhvanimanjarI` (homonym/polysemy lexicon — `svarga`↦गो/अक्षि/जल =
  cow/eye/water), `bhUtasankhyA` (number-code words, grouped only as "0"),
  `upasargArthachandrikA` (root↔prefixed-root derivation pairs), `jhaLkI-bhIma-nyAya`
  (word↔its-own-visarga-variant), `vaiShNava`/`shaiva-kosha` (HTML-table category
  labels — विष्णु "≈" ब्रह्मन्).
- Kept = the 4 true synonym (nāmamālā-genre) kośas: `amara-onto`, `nAmamAlikA`,
  `abhidhAnachintAmaNiparishiShTa`, `abhidhAnachintAmaNishilonCha`. Rebuilt:
  **103,518→88,839 rows, 9.4 %→7.8 % of PWG headwords.** Synonyms now clean
  (`svarga`→नाक/त्रिदिव/सुरलोक). Docs (eval §4b, README, prompt Rule 5) corrected.
- Cross-fact-check of all other indic-dict numeric claims (apte_hi 111,235, Hindi
  coverage 32.7 %, Meulenbeld 453/235, `heuristic()` isolation, vei/acc/ieg/pgn/snp =
  Cologne) — all re-derived and CONFIRMED accurate.

### indic-dict 2nd sweep — Sanskrit synonym-kośas + Meulenbeld binomials folded
- Full-repo survey of indic-dict cross-checked against csl-orig codes (the check caught
  4 false-new dupes: Vedic-Index=`vei`, Aufrecht-CC=`acc`, epigraphical-glossary=`ieg`,
  Gupta-names=`pgn`; Meulenbeld=`SNP`). Two genuinely non-Cologne assets folded:
- **Sanskrit synonym-kośas** → gate's `skd_vcp_synonyms` (Rule 5, Sanskrit-side
  corroboration; the first real source there — SKD/VCP were never wired).
  [src/build_kosha.py](src/build_kosha.py) parses 10 synonym/homonym kośas (Amarakośa
  `amara-onto` with its explicit `समानार्थक:` field, anekārtha-, nāmamālikā, Abhidhāna
  supplements, …) → **103,518 rows, 9.4 % of PWG headwords**. Verified: `arka`→अरुण/
  अर्यमन् (sun), `deva`→अमर/अमर्त्य, `aMSa`→भाग. Excluded after sampling: `amara-sudhA`
  (Pāṇinian prakriyā/derivation — not synonyms), `laxaNa-sangraha` (nyāya definitions),
  `ekAkSharanAmamAlA` (verse-only), `e-bhAratI-sampat`.
- **Meulenbeld plant→Latin binomial** (= SNP). [src/build_meulenbeld.py](src/build_meulenbeld.py)
  → **453 plants, 235 with a binomial** (`ajamodA`→*Apium graveolens*); surfaces as
  card `latin_binomials` — deterministic fix for the binomial-left-untranslated failure.
- `corpus_gate.py`: `load_kosha_index`/`lookup_synonyms` + `load_plant_index`/
  `lookup_binomials`; `build_card` now populates `skd_vcp_synonyms` + `latin_binomials`;
  coverage cmd + lookup print extended. Prompt Rule 5 + input schema updated.
  Full survey (incl. the 5 header-checked en-entries: MT-Slang/pract/pund_v1/Vaidya/
  laukika — all low-value) in [INDIC_DICT_EVALUATION.md](INDIC_DICT_EVALUATION.md) §4b.

### Freq test — Opus judge pass: 37/38 publishable (sev ≤ 2)
- Judged all 38 outputs (38 Opus agents, 2.4 min, 2.06 M tok): severity **{1: 24, 2: 13, 3: 1}**,
  discrimination "good" on every polysemous unit. The judge caught issues the fidelity gate +
  3-agent spot-check missed: **`idam` (sev 3)** = translator swapped NWS owner rows Geldner↔Graßmann
  (the F12 the owner-map prevents) — but the authoritative map is CORRECT, so it's a translator slip
  on a hard double-Geldner case that the production `nws_split.py check` gate catches (my test was
  translate-only). `k_arya` (sev 2) dropped 2 Nachträge patches; `jana`/`pw00` (sev 2) minor sigla
  (token merge; `Bed.`→«значением»). Prompt-tuning findings recorded in the runbook; the pipeline
  is scale-ready pending those nits + wiring `nws_split` into the loop.
- **Item dropped — sandhi-join prefix portrait is FUTILE**: validated only **3/15** of `man`'s
  prefixed surface forms are corpus-attested (anuman/abhiman/avaman) regardless of sandhi spelling —
  `pwg_preverb1.txt`'s join gives the SAME strings; the limit is **corpus coverage**, so the
  `root-fallback`+defer-to-German interim is already optimal. Large-non-giant overflow: 4/64 top
  freq nouns >400 lines (kāla 530, ka 522, śrī 412, para 401, ~6%) — head-splitter extension is a
  conditional follow-up (overflow at ~520 lines untested).

### Freq 38-unit test TRANSLATED + glued + audited (split→translate→glue end-to-end)
- Ran the prepped freq test (8 nouns + giant `man`, 38 units) via the Workflow tool
  (38 Sonnet agents, ~14-way concurrency) → **38/38 translated**; `root_glue_translated.py man`
  → **30/30 sub-cards glued, 0 pending** → `man.NESTED.md` (797 lines, correct structure:
  Омоним 1 simple-verb → caus/desid → 18 prefixes; Омоним 2 + PW/SCH/PWKVN last). **10.5 min,
  1.61 M tokens** (avg inflated by the 8 big nouns; `man` sub-cards median 9 output lines).
- **Apresjan evidence-weighting validated live**: the `ava` agent used the corpus hint
  «смотреть свысока» but rejected it as colloquial for the scholarly «презирать» (avamāna =
  contempt); `pari` saw `evidence_scope='root-fallback'` and deferred to the German gloss.
- **Audited.** New deterministic gate [src/audit_translation.py](src/audit_translation.py)
  (judge-independent; complements the Opus judge + `nws_split` owner-map check): **38/38 clean**
  — `<ls>` citations ≥90 % preserved, `{#…#}` Sanskrit ≥85 %, Russian present everywhere.
  Semantic spot-check (3 `fact-check-against-source` agents): `anu`/`nara` PASS (NWS owner-map
  12/12 verbatim, EN glosses from EN), `ava` substantively PASS. 2 trivial nits: `ava`
  "ein Schol."→«один» (borderline-correct gloss prose), `nara` a Hoernle multi-cite NWS row
  compressed (NWS guard-4 follow-up). The Opus severity judge was **not** run (translate-only,
  to bound cost) — run separately before print-ready. Outputs gitignored.

### Frequency-first queue RUN at volume + root-split hardened + audited
- **Freq queue runs** (`_pilot_gen_merged.py --manifest freq --root-split`): top-50 =
  40 giant roots → 2,316 single-pass sub-cards, none overflow. Two fixes unblocked the
  volume run: **resumability composition** (`is_done`/`is_giant` — a giant root with only a
  stale whole-card input is still re-split; the superseded whole-card is then removed), and
  the **multi-homonym fix** (hit 19/50 top roots): `gen_root_split` segmented only `bufs[0]`,
  so a giant verb root at a non-zero homonym index (√i at hom 2 = 114 prefixes; mā/As/vā/iṣ)
  was missed and extra giant homonyms (gam/as/dā) dropped. Now segments **every** homonym,
  splits each giant one, keeps small ones whole, attaches supplements once; rootmap gains a
  `hom` field; `root_glue_translated` orders (hom→seg→part), supplements last; secondary
  (caus/desid, `<div n="p">— <ab>caus.</ab>` via `SEC_DIVP_RE`) preserved + nested with the
  simple verb.
- **Apresjan evidence on sub-cards (interim)**: the split path wrote `[]` portraits →
  evidence-blind giants. `subcard_portrait` now writes real `corpus_synonyms` keyed by the
  right form — head/secondary → the root (`man` → считать/думать); prefix → the prefixed
  SURFACE form (`anu+man` → одобрять, `ava+man` → смотреть свысока, unlike bare `man`),
  `evidence_scope='prefixed-form'` when the corpus has it, else `root-fallback` (weak hint;
  the translate prompt is told to defer to the German gloss). Residual: sandhi/stacked
  prefixes need `pwg_preverb1.txt`'s `join_prefix_verb` surface form (proper later fix).
- **Sub-card plumbing through Max**: `run_pilot_wf.js` (`fileOf`) and `_pilot_collect.py`
  keep a `~~` sub-card stem verbatim instead of re-`safe_name`-ing it, so
  `<subkey>.raw.txt` → `<subkey>.merged.md` flows into the glue. 38-unit freq test
  ([pilot/FREQ_TEST_RUNBOOK.md](src/pilot/FREQ_TEST_RUNBOOK.md): 8 nouns + giant `man`).
- **Audited** ([src/audit_root_split.py](src/audit_root_split.py) + the maintainer's
  [src/verify_root_glue.py](src/verify_root_glue.py)): corpus-wide losslessness PASS (1226
  records, 0 failures); 60/60 top giant roots LOSSLESS · all homonyms split · glue-complete
  · portraits present (3,035 sub-cards); whole-card regression OK; csl-orig untouched.

### indic-dict Hindi sense signal folded into the stage-4 gate
- **License cleared** (free use with attribution, all four Indic-gloss dicts, by email)
  → folded the two Hindi ones as a soft **third-language sense signal** (which sense is
  primary), never a correctness vote. New [src/build_indic.py](src/build_indic.py)
  parses the `.babylon` exports (Devanagari headword → Hindi gloss) into SLP1-keyed
  JSONL: **111,235 `apte_hi` + 6,166 `vedic_rituals_hi`**. apte-hi cites nominatives
  (अग्निः→`agniH`), so each row also carries a `stem` key and is indexed under both.
- **Gate:** [src/corpus_gate.py](src/corpus_gate.py) gains a `SENSE` index +
  `lookup_sense()`; `build_card` emits `hindi_sense`; kept **out** of the Russian-token
  `heuristic()`. [pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt)
  gains Rule 8 + the `hindi_sense` input field + `"Hindi"` in `corroborated_by`.
- **Coverage:** Hindi sense gloss for **32.7 %** of PWG headwords (apte_hi 31.7 %,
  vedic 2.3 %) — ~2× the Russian correctness coverage (16.4 %). Verified joins: `agni`
  (4 senses incl. the three ritual fires), `arTa`, `aMSa` (कंधा = «плечо»).
- Kannada (`shabdArtha_kaustubha`) / Tamil (`samskritam-tamizham`) held pending a
  reader. Full assessment in [INDIC_DICT_EVALUATION.md](INDIC_DICT_EVALUATION.md).

### indic-dict / stardict-sanskrit evaluated as a source — declined, deferred
- New [INDIC_DICT_EVALUATION.md](INDIC_DICT_EVALUATION.md). Most of the repo
  (en-head reverse indexes, EN/FR/DE/SA gloss sets) is **Cologne-generated** —
  csl-orig already holds fresher copies, so it adds nothing. The only net-new content
  is four **Indic-language gloss** dictionaries: `apte-hi` (Hindi, 19.6 MB, Apte→Hindi),
  `vedic-rituals-hi` (Hindi, Vedic-ritual, 3.3 MB), `shabdArtha_kaustubha` (Kannada,
  34.9 MB — `bookname` mistags it `sa-sa`), `samskritam-tamizham` (Tamil, blog scrape).
- **Role:** none is Sa→Ru, so none is a translation layer. At most a **soft cross-lingual
  sense vote** in the stage-4 gate — corroborates *which sense is primary*, never the
  Russian wording; `apte-hi` is the standout (Apte-aligned → structured sense map).
- **Blocker:** the repo has **no license** (SPDX `none`; `.babylon` headers carry only
  `#bookname`). Decision: note the gap, record the technical fit, **defer ingestion**.
  Pointers added to [DICTIONARY_CHAIN.md](DICTIONARY_CHAIN.md) and
  [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §2.

### Renou tag validation + DCS over-tag min-support fix
- **Validation by inter-signal agreement** (no human labels): new
  [src/renou_audit.py](src/renou_audit.py) cross-tabulates the four provenance
  signals per dictionary, treats `<ls>` (the lexicographer's citation) as the trusted
  anchor, and quantifies the dominant accuracy risk — `dcs` over-tagging. The DCS index
  is keyed by bare lemma, so homographs collapse to one entry carrying the *union* of
  all eras (`akāra`, the letter, inherited I–V), and the tagger kept only the state list
  — a one-text state was indistinguishable from a hundred-text one. Findings:
  `dcs`-widening is the dominant disagreement (MW 52 %, BEN 76 %, AP90 79 % of both-
  signal entries) and 42–90 % of `dcs` assertions are uncorroborated by `ls`/`bhs`.
  Report → gitignored `src/renou_audit_report.md`.
- **The fix (applied):** [src/build_dcs_renou.py](src/build_dcs_renou.py) now records
  lossless per-state `state_support` `{n_texts, best_confidence}`, and
  `renou.filter_dcs_states()` ([src/renou.py](src/renou.py)) applies the policy at
  *tagger* time (tunable, no rescan): **keep a `dcs` state iff ≥`DCS_MIN_SUPPORT` (=2)
  texts OR ≥1 confidently-typed text** (authoritative DCS genre / curated Buddhist–
  grammar name hint). Wired into `tag_dict_from_source.py` / `tag_mw_from_source.py`
  (`--dcs-min-support N`). Effect: **9.9 % of `dcs` state-assignments pruned** (14.8 %
  of lemmas) — almost all spurious **IV** (9,736; the `date≥400` fallback bucket) and
  **I** (2,923); **0 state-II / 0 state-V** dropped (those come only from typed
  Vyākaraṇa / Buddhist texts, so the curated signal is untouched). The residual
  `ca`/`idam`/`akāra` = I–V breadth is *not* pruned — it is corpus-accurate (high-conf
  support in every era), merely uninformative → a display concern, not an error.
- Index + all 8 `{code}.renou.jsonl` regenerated; [RENOU.md](RENOU.md) gained a
  Validation section + refreshed post-policy coverage table. The `wl` (wisdomlib) layer
  was reconstructed losslessly from surviving intermediates (V-by-source `wl` counts
  match the originals exactly). Shipped in `ecc7bb9` (core) + `9666591` (docs/audit).

### Root-entry segmenter suite (the giant-root fix) + external resources
- **The structural fix for "translation pass dies on bhū/vid":** a root mega-record is now
  split into per-prefix sub-cards and gluable back. Built one at a time in
  [research/](research/) (full write-up: [research/ROOT_ENTRY_ARCHITECTURE.md](research/ROOT_ENTRY_ARCHITECTURE.md) §BUILDS A–C):
  - `root_segment_proto.py` — lossless `<div n="p">` slicer; `root_glue.py` — SPLIT→NESTED
    glue (PWG + MW), cap-aware via the link table; `root_units.py` — segments a root record
    into per-prefix **translation units** in the `compile_translatable` manifest shape
    (`BU`→380 units).
  - `lex_noun_link.py` — PWG nominal→root chain table (34.8 % linked, dict-field-first);
    `mw_deriv.py` — MW derivation oracle + link table (133.7 k rows) from Funderburk's
    `MWderivations`; `root_merge.py` — PWG↔MW merged comparative article (bhū 33/41 aligned);
    `apte_parse.py` — Apte Sanskrit–Hindi → independent root oracle (1,654 dhātus, 793 not in
    verbs01) + `productivity` (affix-productivity from 38,757 `+`-etymologies: upasarga×root —
    `vi`>`sam`>`pra` — and kṛt/taddhita pratyaya×root — `kta`>`ṭāp`>`lyuṭ`>`ac` — cross-listed
    with MWderivations' `wsfx` surface-suffix counts `-tva`>`-tā`>`-vat`; → `apte_productivity.tsv`).
    `apte_parse.py crossmap` + curated `affix_map.tsv` **bridge the two lenses**
    (Pāṇinian pratyaya ↔ surface suffix ↔ MW wsfx, via anubandha-stripping): they OVERLAP on
    transparent taddhita but MW≫Apte there (`tva` 11 vs 1996 — Apte rarely cites the obvious
    suffix), while Apte alone covers the kṛt formation affixes (`kta`/`ghañ`/`lyuṭ`/`ṭāp`, MW
    wsfx=0 — lexicalised headwords). Complementary coverage, now quantified.
- **Teaching layer (for Sanskrit affixation):** one dataset `affix_pedagogy.json` (27 affixes in
  13 function groups, with surface form, Pāṇinian pratyaya, anubandha-stripping steps, Apte
  productivity, MW count, real example derivatives) feeds four artifacts: `affix_explorer.html`
  (interactive, function-grouped, productivity bars, click-to-decode — also wired into the
  **WhitneyRoots** reader, [PR #21](https://github.com/gasyoun/WhitneyRoots/pull/21)),
  `affix_poster.html` (printable one-page wall chart), `affix_quiz.html` (data-driven MCQ drill),
  and `affix_flashcards.tsv` (Anki/Quizlet-importable). Built by `affix_pedagogy.py` +
  `build_affix_explorer.py` + `build_affix_teaching.py`.
- **Wired into the pipeline (the unblocker):** `_pilot_gen_merged.py --root-split` (also
  `--manifest freq --root-split`) auto-detects a giant root (≥8 prefix divisions) and explodes
  it into one single-pass-sized sub-card per prefix — HEAD card keeps the simple verb + all
  supplements + NWS owner map; each prefix sub-card is its own `<div n="p">` block — plus a
  `<safe>.rootmap.json` for `root_glue` reassembly. `BU`→41 sub-cards (head 820 lines + 93-entry
  owner map; `anu` prefix card 87 lines vs the 1315-line whole record), `gam`→63. This lets the
  frequency-first queue (top = sthā/bhū/gam) run without the single-pass death.
- **Glue-after-translate (round-trip closed):** `root_glue_translated.py <root>` reads the
  `rootmap.json` + each sub-card's translated `<subkey>.merged.md` and stitches them back into
  one `<safe>.NESTED.md` Russian article (head → prefixes by seg order; missing → pending).
  Demoed on `BU`: 3 prefix sub-cards (anu/abhi/ud) translated → glued into the 41-sub-card
  nested article, each in its slot, Sanskrit/sigla preserved. SPLIT→translate→GLUE confirmed.
- **Head-card sense-splitter (the gate confirmed it was needed):** a single-pass translation of
  the 820-line `bhū` HEAD overflowed the 32k-token output limit and wrote nothing. So
  `_pilot_gen_merged.py` now splits the head into single-pass parts — simple-verb senses chunked at
  `<div`/blank boundaries (budget 100, cap 1.5×), each supplement layer (PW/SCH/PWKVN) chunked, the
  NWS owner map batched (25/unit); prefix sub-cards are chunked the same way. `BU` → 56 sub-cards
  (14 head-parts + 40 prefix), **every one ≤143 lines**; `gam` → 81. PWG side stays lossless.
  `root_glue_translated.py` orders by (seg_index, part) and labels the parts.
- **Scale-proven:** `scale_test.py` segments **all 1,163 PWG verb roots, 100 % LOSSLESS**;
  the slicer's 8,588 prefix-divisions vs verbs01's 8,361 vetted upasargas (+227 FP gap, 159
  roots) confirm the false-positive guard is needed at scale.
- **Reuse, not reinvention** (per *check-prior-art*): the segmenter sits on Jim Funderburk's
  [`PWG/verbs01/`](https://github.com/sanskrit-lexicon/PWG/tree/master/verbs01) (sandhi join +
  MW alignment already done) and [`MWderivations`](https://github.com/funderburkjim/MWderivations)
  (220 k MW headwords classified pfx/cpd/wsfx). Cross-check: `MWderivations/compounds.txt` is
  byte-identical to `WhitneyRoots/MW_compounds_12610.txt`. External data vendored gitignored
  under `research/external/`; `research/apte_roots.tsv` + `research/lex_noun_link_pwg.tsv` tracked.

## 2026-06-23

### Scaled + handed off (translation pipeline)
- **Owner-map feed — F12 eliminated by construction.** `_pilot_gen_merged.py` appends
  an AUTHORITATIVE "PRE-PARSED OWNER MAP" (deterministic `nws_split` triples) to each
  card's NWS layer; the translator emits one row per entry with the owner VERBATIM and
  never re-derives attribution. `run_pilot_wf.js` HARD RULE 5 + Guard 7 consume it.
- **Re-validated on fresh cards:** `ātman` CLEAN (13/13, incl. French TAK *le soi*→RU);
  `ās` went MISATTRIBUTION (3 owner-swaps, pre-fix) → **CLEAN** (0 mismatches) after the
  owner-map feed. First coverage-first batch of 6 (`as`/`A`/`anu`/`akṣa`/`arjuna` clean,
  `as` with 60 NWS owners CLEAN) = **5/6 first-pass clean**; `Ap` quarantined + re-queued.
- **Full a-section staged for the Max workflow:** regenerated **4,264 NWS a-cards** with
  owner maps (`--manifest a`); runbook archived at
  [src/pilot/archive/legacy_max_2026-06-27/RUN_ASECTION_MAX.md](src/pilot/archive/legacy_max_2026-06-27/RUN_ASECTION_MAX.md)
  (per-window prep → run `run_pilot_wf.js` on Max → `run_real_test.py audit`; rejects
  auto-re-queue). Window 1 (`[0,50)`, 37 fresh) prepped.
- **Failure gallery:** F10 (Windows case-insensitive filename collision — would lose
  ~15 k headwords), F11 (editorial-intent fabrication), F12 (NWS cite-after-gloss
  off-by-one inherited by the judge). See [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md).
- **Cost & feasibility re-grounded** — [PILOT_COST.md](PILOT_COST.md) §6: measured
  **0.78 tok/byte**; a-section ≈ **0.5–0.8 B** tokens, whole PWG dict ≈ **4–7 B**;
  throughput ~7 k cards/day at 24/7 (~15 days *continuous*) but **quota-bound to ~1–2
  months on one Max seat**. Documents the data gaps (Max weekly quota, typical-card
  cost, total size) and the one instrumented-window experiment that resolves them.

- **Frequency-first ordering (DCS) built + validated.** `freq_route.py` ranks PWG
  headwords by hybrid token×breadth×richness → `scale_manifest.freq.json` (41% DCS-attested;
  ~3.8k band-4+5 core). Top cards = verbal **roots** (sthā 379 senses, i 272, gam 213). Freq-
  first pipeline validated: `rūpa`/`rasa` CLEAN through the owner-map gate. **Finding:** roots
  (`vid` 74, `bhū` 131) fail single-pass translation ("connection closed mid-response") →
  root-entry sectioning is the open design question before scaling (pending manuals review).

- **Lexicography design studies — 3 handoff chats spawned.** The giant-root failure opened the
  microstructure question; decided the **two-mode root architecture** (SPLIT cards for translation +
  `root_key` linkage → glue to a NESTED root article on demand) and created 3 grounded research briefs
  in [research/](research/) — (A) root architecture, (B) sense ordering, (C) homonym/gloss/citation/
  run-on conventions — each spun off as its own cold handoff chat (`task_740ea467`/`task_2242dc13`/
  `task_9b9ce8db`) to read the OCRed prefaces + probe entries and fill a per-dict comparison table
  before scaling.

### Added
- **Renou language-state (I–V) tag on every cited sense.** Each dictionary
  *meaning* is now classified into one of Louis Renou's five states of Sanskrit
  (*Histoire de la langue sanskrite*, the five chapters): **I** Vedic, **II**
  Pāṇinian/grammarians', **III** Epic & prolongements, **IV** Classical, **V**
  Buddhist/Jaina. Derivation is **deterministic from the sense's `<ls>`
  citations** — no LLM — so it is fully auditable. A sense is **multi-label**
  (a meaning attested across eras carries all applicable states, e.g.
  `["I","III"]`), and its **oldest citation** is flagged separately
  (`renou_oldest`, plus `renou_oldest_sense` on the record) to answer "in which
  era was this meaning first attested".
  - [src/build_ls_map.py](src/build_ls_map.py): every curated PWG source in
    `CANON` carries a `renou` state; `ls_source_map.json` regenerated with it.
    PWG coverage — I 123 806 · II 25 291 · III 199 075 · IV 211 071 · V 0
    citations (PWG's curated canon has no Buddhist/Jaina source).
  - [src/build_ls_map_mw.py](src/build_ls_map_mw.py) (new): MW-side map
    (`ls_source_map_mw.json`), with an MW-specific siglum extractor (no `n=""`
    attribute; lowercase-roman volume refs stripped; `L.` kept as
    lexicographers). 77 sources, 84.1 % of MW `<ls>` citations; **state V
    populates here** (Buddh./Lalit./Divyāv./SaddhP./Jaina — 4 611 citations).
  - [src/renou.py](src/renou.py) (new): `states_for_text/keys` resolves
    citations → states, dict-aware (`pwg`/`mw`).
  - [src/annotate_renou.py](src/annotate_renou.py) (new): idempotent, BOM-free,
    temp-swap backfill of `renou` / `renou_oldest` onto final-card senses (and
    `renou_oldest_sense` per record); `--report` prints the I–V distribution,
    multi-label count and first-attestation breakdown.
  - [schemas/pwg_ru_final_card.schema.json](schemas/pwg_ru_final_card.schema.json):
    `renou` (array of I–V) and `renou_oldest` added to the sense as **optional**
    fields, and `renou_oldest_sense` to the record — existing MW/PWG cards stay
    valid.
  - Ran record-level on the legacy PWG store (`pwg_ru_translated.jsonl`, 217
    cards): **184 tagged (84.8 %)**, 45 multi-label · I 70 · II 21 · III 48 ·
    IV 106 · V 0.

- **DCS corpus enrichment of the Renou tag (second, provenance-tagged signal).**
  `<ls>` is authoritative but narrow (only cited sources); the Digital Corpus of
  Sanskrit (DCS, 2026 CoNLL-U, 270 texts / 5.46 M words) shows where a headword
  *lemma is actually attested*, recovering states the citations miss.
  - [src/build_dcs_renou.py](src/build_dcs_renou.py) (new): resolves each DCS text
    → Renou state (genre from VisualDCS `dcs_texts_clean.json`, name-hints for the
    Buddhist **V** / grammar **II** texts it misses, date fallback), then scans the
    corpus (lemma = CoNLL-U col 3) → `dcs_lemma_renou.json` (gitignored build
    artifact): **90 346 lemmas** → `{renou states, oldest text/date, n_texts}`.
  - [src/enrich_renou_dcs.py](src/enrich_renou_dcs.py) (new): joins the index to
    cards on `key1`→IAST, adding `renou_dcs`, `renou_dcs_oldest`, `renou_dcs_texts`,
    `renou_enriched` (ls ∪ dcs) and `renou_provenance` (`{state:["ls","dcs"]}`).
    DCS is per-lemma, so it merges at the card/record level and **never overwrites**
    the per-sense `<ls>` tag.
  - On the 217 PWG cards: 127 (58.5 %) DCS-hit, 83 gained ≥1 state; **state V
    went 0 → 37 cards** (Buddhist attestation `<ls>` never supplied). Enriched
    coverage I 93 · II 30 · III 90 · IV 136 · V 37.
  - **Scaled to the whole dictionary** — ran on `assembled_cards.jsonl`, all
    **120 173 PWG headwords** (key1→IAST join, no translations needed): **54 519
    (45.4 %) DCS-hit** → corpus-grounded Renou states. Coverage I 22 075 · II 4 926 ·
    III 31 187 · IV 35 544 · **V 10 171** (e.g. *akaniṣṭha, akṣayamati, akṣobhya* —
    Buddhist headwords `<ls>` never marks). DCS is itself built from GRETIL e-texts,
    so it already subsumes the raw-corpus layer; the 45.4 % ceiling is the
    exact-lemma-form join (rare/variant/compound headwords miss).
  - [src/add_corpus_renou.py](src/add_corpus_renou.py) (new): reusable augmenter
    that folds a raw IAST text (no lemmatiser) into the index at a given Renou
    state, word-FORM level — additive, idempotent (`__sources__` meta guards
    re-runs). Applied to GRETIL's **Skandapurāṇa Revākhaṇḍa** (state III): 25 075
    forms → 23 765 new form-keys + 184 existing lemmas gained III (index 90 346 →
    114 111). **Data-availability finding:** GRETIL serves only the Revākhaṇḍa for
    Skanda (the `sa_skandapurANa1-31` critical edition is listed but 404s in all
    formats); the Revākhaṇḍa is *already in DCS lemmatised*, so the fold is near-zero
    marginal on the 217-card sample (III unchanged). The full 81 k-verse vulgate is
    not available as clean Sanskrit e-text on GRETIL — the augmenter is ready for it
    when a source surfaces.
  - **Third tier — wisdomlib (built; reuses the existing Samudra crawler).** A word's
    wisdomlib **tradition** sections (Buddhism/Jainism/Ayurveda/Vyakarana/Vedic/…) give
    a tertiary, lower-confidence Renou hint (Buddhism/Jainism → **V**). New
    `SamudraManthanam/web/corpus_builder/wisdomlib/definitions.py` fetches `/definition/`
    pages **reusing `crawl.py`'s** polite fetch + `is_block_page`, parses tradition
    headings → `word_traditions.jsonl`. Consumer
    [src/enrich_renou_wisdomlib.py](src/enrich_renou_wisdomlib.py) (new) folds it into
    `renou_wl` + `renou_provenance` as source `"wl"` — never overriding `<ls>`/DCS; a
    state backed by `wl` alone is the weakest evidence. Join is on a diacritic-free key
    (wisdomlib ASCII slug `akshobhya` ↔ SLP1→IAST `akṣobhya`); consumer + parser
    self-test pass. **Blocked on live fetch:** wisdomlib is Cloudflare-gated per-IP (the
    crawler README's documented reality — `http=000` here), so `word_traditions.jsonl`
    must be produced gently from a residential connection, validating the parser with
    `definitions.py parse <page>` on the first real page.
  - **Parser validated on real pages (2026-06-24)** once the IP cooled: `akshobhya`/
    `bodhisattva` tradition extraction correct; fixed two bugs the run exposed — force
    HTTP/1.1 (wisdomlib drops HTTP/2 from this egress) and gloss count via
    `class="suffix source"` (Samudra PR #15). A real BHS batch (16,837 slugs) re-tripped
    the per-IP block, exposing + fixing two more: resumable (don't persist transient
    failures) and a timeout-aware circuit breaker.

- **BHS → PWG/MW/AP deterministic V transfer ([src/enrich_renou_bhs.py](src/enrich_renou_bhs.py), new).**
  Edgerton's Buddhist Hybrid Sanskrit dictionary *is* the state-**V** register, so any
  headword present in BHS but lacking V in a mainstream dict is a missed attestation —
  filled deterministically, no fetching (what the Cloudflare-blocked wisdomlib batch was
  approximating). Adds V with provenance source `"bhs"` (an attestation claim, so common
  words used in Buddhist texts — e.g. *viṣṇu* — correctly gain a V-register attestation,
  marked `bhs`-only and distinguishable from `ls`/`dcs`/`wl`). **New V tags: MW 15 239 ·
  PWG 5 734 · AP 2 364 (23 337 total), plus 23 911 corroborated.** Join on the
  diacritic-free key; outputs `{store}.bhs.jsonl` (gitignored).

- **Consolidated into one pipeline + [RENOU.md](RENOU.md).**
  [src/renou_pipeline.py](src/renou_pipeline.py) (new) chains the four signals —
  `<ls>`+DCS (`tag_dict_from_source`) → BHS V (`enrich_renou_bhs`) → wisdomlib
  (`enrich_renou_wisdomlib`) — into one canonical `{code}.renou.jsonl` per dictionary,
  keyed by `key1`, with a states / V-by-source report. `--all` ran the **8 LS-rich
  dicts = 770 292 entries** (PWG 123 366 · MW 286 560 · PW 170 556 · AP 90 654 · AP90
  34 882 · SCH 29 125 · BEN 17 310 · BHS 17 839). [RENOU.md](RENOU.md) documents the
  five states, the four provenance sources + their trust, the per-dict coverage, and
  how to reproduce. Canonical indices are gitignored (regenerated by the pipeline).

- **Editorial layer — [src/renou_portrait.py](src/renou_portrait.py) (new).** Turns the
  signals into editor-facing output: `portrait(entry)` renders a headword's Renou era
  label (Russian), its first attestation, and a confidence note — a V supported only by
  `bhs` is flagged *register-only* (e.g. *viṣṇu* "V: только регистр (BHS)" vs *akṣobhya*
  V from `dcs+bhs+wl`). `order_senses_oldest_first(card)` reorders a structured card's
  senses earliest-attested-first (uses `renou_oldest_sense`; ready for the per-sense
  store, no-op without it). Demoed on MW.

- **Renou tagging extended to Monier-Williams (both layers).** The MW *Russian*
  cards live in a separate working repo, but the Renou tag is language-independent
  (headword + `<ls>`), so [src/tag_mw_from_source.py](src/tag_mw_from_source.py)
  (new) derives it straight from the MW source `csl-orig/v02/mw/mw.txt` and keys it
  by `key1` (joins to the Russian cards later) → `mw_renou.jsonl` (gitignored).
  All **286 560 MW entries**: **59.1 % `<ls>`-tagged**, **47.6 % DCS-hit**. The two
  signals now cross-check — `<ls>` state **V** = 4 503 (citation-based:
  Buddh./Lalit./Divyāv./SaddhP./Jaina), DCS state **V** = 38 200 (attestation-based),
  enriched union **41 195**, of which **1 508 are corroborated by BOTH `<ls>` and
  DCS** (e.g. *aṭaṭa* — a Buddhist hell — `ls=[V] dcs=[V]`). Per-entry
  `renou_provenance` records which signal(s) back each state.

- **Renou tagging extended to the 6 remaining LS-rich dictionaries (8 total).**
  Ranked the whole csl-orig corpus by `<ls>` richness and tagged the leaders:
  **AP** (Apte), **AP90**, **PW**, **BEN** (Benfey), **SCH** (Schmidt), **BHS**
  (Edgerton). New [src/renou_sigla.py](src/renou_sigla.py) holds the curated
  Apte/Benfey siglum→state tables (Apte `R`=Raghuvaṃśa, `Mv`=Mahāvīracarita — *not*
  Rāmāyaṇa/Mahāvastu) and the BHS rule (**default-V** + a meta blocklist of
  editors/dictionaries); [src/tag_dict_from_source.py](src/tag_dict_from_source.py)
  generalises the MW tagger over any dict (Petersburg dicts PW/SCH **reuse the PWG
  map**; AP/AP90/BEN use the inline tables; BHS the default-V rule) and emits
  `{code}_renou.jsonl` (gitignored). **360 366 more entries tagged:**
  - **BHS** 17 839 — 73.8 % `<ls>`-tagged, **all V** (13 172; the pure Buddhist
    signal: *dharma/buddha/bodhisattva* `ls=[V]`, corroborated by DCS).
  - **BEN** 17 310 — 70.0 % `<ls>` (citations concentrate in ~30 sigla).
  - **AP** 90 654 / **AP90** 34 882 — 26–29 % `<ls>` (long Apte siglum tail), DCS V
    4 774 / 3 646.
  - **PW** 170 556 / **SCH** 29 125 — `<ls>` partial (10–13 %; their Petersburg sigla
    exceed the PWG canon), but DCS carries them (PW enriched V = 10 340).
  Together with PWG + MW, all eight LS-rich dictionaries now carry the two-layer,
  provenance-tagged Renou state, keyed by `key1`.

### Fixed
- `nws_split.py` OWNER citation now stops at `;` so the trailing-tag
  sub-entry variant (`gloss … <DIATAG> ; SOURCE:page`, e.g. `aYj`) keeps
  only the SOURCE as owner, not the diasystem tag.
- `nws_split.py check` locates card rows on word boundaries instead of raw
  substring, killing a false MISATTRIBUTION where the short Sanskrit
  locator `apāṃ` matched inside the compounds `apāṃpitta`/`apāṃnidhi`
  (the `ap` cross-reference `apāṃ napāt → s.v. napāt` has no card row).
- **Root cause of the `av` `+ upa` owner slide:** `compile_translatable`
  `mask_nws_gloss` now strips the leading owner *bleed*. A roman-numeral
  co-owner cite (`Rivelex (2) : XLV`) that `nws_split`'s digit-only OWNER
  can't tag rode onto the FRONT of the next gloss as `<tag> ; Source :
  page > …`, putting a competing source in the to-translate prose of
  glosses whose deterministic owner was already correct — which led the
  LLM assembly to attribute `+ upa` to Rivelex instead of Geldner. The
  strip fires only on real bleeds (5 `av` glosses) and leaves
  `nws_split.py` itself untouched (parsing the roman co-owner there
  destabilises lemma/gloss alignment).
- Hand-corrected the slid `av` `+ upa` block in the (gitignored) merged
  card to the reading-direction owners (Geldner → Graßmann → NṚV → NṚV →
  Rivelex); all other prefix blocks verified already-correct.

- `nws_split.py` OWNER trailing parenthetical now spans one level of
  nested parens and no longer requires the `s.v.` prefix, so cites like
  `BHSD : 154 (s.v. ekoti -(° tī -) bhūta)`,
  `Olivelle 2015 : 391 (s.v. ṣaḍvidha (- bala))` and bare headword
  variants `MW : 756 (bhā́s)` / `MW : 759 (bhujiṣyà)` resolve their owner
  instead of being dropped. Found by the b-section split-preview audit;
  `selftest` + all 10 a-section checks still CLEAN.
- `scale_route.py` accepts any single-letter section (e.g. `b`), not just
  `a`/`all`, emitting `scale_manifest.<letter>.json`.
- **`nws_split.nws_fragment` no longer swallows the appended owner map.**
  `_pilot_gen_merged.py` writes an authoritative `NWS — PRE-PARSED OWNER
  MAP` layer after the net-new NWS addendum, but `nws_fragment` captured
  `(.*)\Z` from the first `=== LAYER: NWS` marker to EOF, so on any
  owner-map input it re-parsed that map as source content — corrupting
  `split()`, the F12 gate (`check`) and `compile_translatable` (the
  d-section first showed 1,380 phantom empty-gloss + 33 phantom no-owner
  entries). It now captures only up to the next `=== LAYER:` marker and
  skips the `PRE-PARSED` header. Found while auditing the d-section (first
  section generated with the owner-map injection); `selftest` + all 10
  a-section checks still CLEAN, `compile_translatable('day')` → 7 clean
  units, 0 map artifacts.
- **`nws_owner_map` debleeds the injected owner map.** The roman co-owner
  bleed (e.g. `Hillebrandt 1885 : IV`) that `compile_translatable` already
  strips also contaminated the appended `PRE-PARSED OWNER MAP`: `split`'s
  `lemma_tag` scatters the bled segment into an entry's leading gloss, its
  tag (stray `; Name : page`) and a punctuation-only lemma (`{#,#}`). The
  owner stays correct, so this is cosmetic for what the translator reads.
  `nws_owner_map` now strips the leading-bleed from the gloss, removes a
  bled-in `Name : page` cite from the tag, and drops punct-only lemmas
  (mirrors `mask_nws_gloss`). The owner field is never touched; clean
  sections are no-ops. Found in the g-section (`gam`).

### Added
- `run_real_test.py audit` is now a true **NWS attribution gate**: a fresh
  (non-protected) card whose NWS owners disagree with the deterministic
  `nws_split` parse is rejected — its `<safe>.merged.md` is moved to
  `<safe>.merged.REJECTED.md` so the next `prep` re-queues it — and the
  command exits non-zero. Protected hand-authored cards are audited but
  never quarantined. Verified end-to-end (slid card → FAIL → quarantined →
  exit 1; clean card → PASS → exit 0). `selftest` + all 10 audited keys
  CLEAN.

### Audited
- **Full b-section deterministic split-preview** (all 4,613 b-keys → 971
  NWS-bearing, 2,655 entries): **0 roman-cite bleeds** — the `av`-class
  F12 owner slide does not occur anywhere in the b-section. After the
  trailer-paren fix above, only 11 entries are unowned: 4 benign
  empty-segments + 7 real losses confined to the two known-limitation
  sources below.
- **Full c-section deterministic split-preview** (all 2,366 c-keys → 719
  NWS-bearing, 1,828 entries): **0 roman-cite bleeds**. 17 unowned = 8
  benign empty-segments + 9 real losses, all in the known-limitation
  sources below (8 × Meister `(2.1)`, 1 × Böhtlingk `*NNN`).
- **Full d-section deterministic split-preview** (all 6,019 d-keys → 1,439
  NWS-bearing, 3,808 entries): **0 roman-cite bleeds**. First section
  generated with the owner-map injection, which surfaced the
  `nws_fragment` over-capture bug fixed above; after that fix only 4
  entries (0.10%) are real losses — one each Meister `(2.1)`, roman page,
  Böhtlingk `*NNN`, plus one page-less cross-reference
  (`duHzvapnya → s.v. duṣvápnya (Graßmann 1873 (1996))`, no `: page` to
  parse). The 14 remaining unowned are benign empty terminal segments.
- **Full e-section deterministic split-preview** (all 663 e-keys → 203
  NWS-bearing, 470 entries): **0 roman-cite bleeds**, cleanest section so
  far. 3 unowned = 2 benign empty + 1 page-less cross-reference
  (`eta → s.v. éta . Rivelex (2) (s.v. éta)`, no `: page` to parse); none
  of the Meister/roman/Böhtlingk classes appear. Cross-checked against the
  injected owner map: 470 map entries with exactly 3 `[NWS: ?]`, matching
  the split-preview one-for-one — confirming the `nws_fragment` fix and
  owner-map generation are consistent. The page-less cross-reference (no
  `Name : page` cite exists) is a recurring benign category, not a parser
  gap — it also appears once in d (`duHzvapnya`).
- **Full f-section deterministic split-preview** (all 339 f-keys [SLP1 `f`
  = ṛ] → 156 NWS-bearing, 502 entries): **0 roman-cite bleeds, 0 real
  losses** — the only unowned entry is a benign empty terminal segment, no
  Meister/roman/Böhtlingk/page-less cases. Owner-map cross-check: 502 map
  entries, exactly 1 `[NWS: ?]`, matching the split-preview one-for-one.
- **Full g-section deterministic split-preview** (all 3,354 g-keys → 974
  NWS-bearing, 2,866 entries): **2 roman-cite bleeds** (both `gam`,
  `Hillebrandt 1885 : IV`) — the first bleeds since the a-section; the
  owner stays correct (`Geldner 1907 : 52`), and the cosmetic owner-map
  contamination is fixed by the `nws_owner_map` debleed above. 9 unowned =
  8 benign empty + 1 Meister `(2.1)` (0.03% real loss). Owner-map
  cross-check: 2,866 entries, 9 `[NWS: ?]`, matching the split-preview.
- **Full h-section deterministic split-preview** (all 2,027 h-keys → 466
  NWS-bearing, 1,353 entries): **0 roman-cite bleeds**. 10 unowned = 8
  benign empty + 2 real (1 Meister `(2.1)`, 1 page-less cross-reference
  `hriRIy → s.v. hṛṇīy (TŚPC 3)`, no `: page`) = 0.15%. Owner-map
  cross-check: 1,353 entries, 10 `[NWS: ?]`, matching the split-preview,
  and **0 inputs with residual contamination** — confirming the
  `nws_owner_map` debleed produces clean maps on fresh generation.
- **Full i-section deterministic split-preview** (all 777 i-keys → 281
  NWS-bearing, 1,045 entries): **0 roman-cite bleeds**. 4 unowned = 3
  benign empty + 1 real (`in → … : XLVII (als Lemma in Rivelex 1, S. 561
  hinzuzufügen)`, a roman-page owner trailed by an editorial note — the
  roman-page known limitation) = 0.10%. Owner-map cross-check: 1,045
  entries, 4 `[NWS: ?]`, matching the split-preview, 0 residual
  contamination.
- **Full j-section deterministic split-preview** (all 2,089 j-keys → 506
  NWS-bearing, 1,207 entries): **0 roman-cite bleeds, 0 real losses** — the
  6 unowned entries are all benign empty terminal segments, with no
  Meister/roman/Böhtlingk/page-less cases (0.00% real loss). Owner-map
  cross-check: 1,207 entries, exactly 6 `[NWS: ?]`, matching the
  split-preview one-for-one, 0 residual contamination.
- **Full k-section deterministic split-preview** (all 8,637 k-keys → 2,590
  NWS-bearing, 6,530 entries — the largest section): **3 roman-cite
  bleeds** (all `kar`, `Hillebrandt 1885 : IV`, the same g-section pattern;
  owner stays correct and the cosmetic owner-map contamination is cleaned
  by the `nws_owner_map` debleed — **0 residual contamination**). 39 unowned
  = 28 benign empty + 11 real (0.17%): 6 × Meister `(2.1)`, 2 page-less
  x-ref, 1 roman page, 1 Böhtlingk `*NNN`, all known limitations, plus **1
  source-data typo** — `vṛtrakhādá → … NṚV 2B : 79 (s. (2. khād )` has an
  **unbalanced** trailing parenthetical (a stray extra `(`, a digitization
  error for `(s.v. 2. khād )`); its two sibling entries with the identical
  owner `NṚV 2B : 79` (`amitrakhādá`, `vikhādá`) parse correctly, so this is
  bad input, not a parser gap — admitting unbalanced parens is the kind of
  destabilising relaxation already reverted, so no code change. Owner-map
  cross-check: 6,530 entries, 39 `[NWS: ?]`, matching the split-preview
  one-for-one.
- **Full l-section deterministic split-preview** (all 1,464 l-keys → 286
  NWS-bearing, 735 entries): **0 roman-cite bleeds**. 11 unowned = 6 benign
  empty + 5 real (0.68%), all known limitations: 4 × Böhtlingk `*NNN` + 1
  page-less x-ref; no Meister/roman/OTHER cases. The 0.68% real-loss rate is
  the highest section so far only because the small 735-entry base magnifies
  one `*NNN` cluster — not a new gap. Owner-map cross-check: 735 entries, 11
  `[NWS: ?]`, matching the split-preview one-for-one, 0 residual
  contamination.
- **Full m-section deterministic split-preview** (all 6,350 m-keys → 1,425
  NWS-bearing, 3,495 entries): **0 roman-cite bleeds**. 28 unowned = 17 benign
  empty + 11 real (0.31%), all known limitations: 6 × Meister `(2.1)` + 4 ×
  roman page + 1 page-less x-ref; no Böhtlingk `*NNN`/OTHER cases. Owner-map
  cross-check: 3,495 entries, 28 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full n-section deterministic split-preview** (all 4,278 n-keys → 1,022
  NWS-bearing, 2,407 entries): **0 roman-cite bleeds**. 27 unowned = 24 benign
  empty + 3 real (0.12%), all known limitations: 2 × page-less x-ref + 1 ×
  roman page; no Meister `(2.1)`/Böhtlingk `*NNN`/OTHER cases. Owner-map
  cross-check: 2,407 entries, 27 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full o-section deterministic split-preview** (all 461 o-keys → 129
  NWS-bearing, 306 entries): **0 roman-cite bleeds**, **0 unowned** — the
  cleanest section so far (0.00% real loss; no benign empties, no known-
  limitation classes, no OTHER). Owner-map cross-check: 306 entries, 0
  `[NWS: ?]`, matching the split-preview one-for-one, 0 residual contamination.
- **Full p-section deterministic split-preview** (all 11,095 p-keys → 2,878
  NWS-bearing, 6,863 entries): **0 roman-cite bleeds**. 90 unowned = 73 benign
  empty + 17 real (0.25%): 8 × page-less x-ref + 6 × Meister `(2.1)` + 2 ×
  roman page + **1 new known-limitation class** — a multi-page citation
  (`TPSI 3 : 19, 22` on `prakaraRasama`). The fragment's terminal owner closes
  with a comma-joined page list, which OWNER's single-token page class
  (`\d+[A-Za-z]?`) cannot represent, so the owner does not close the gloss and
  is dropped — structurally the same digit-only-page cause as the roman/
  asterisk-page limitations (single TPSI multi-page cite in the section; not a
  typo, not a bug). Owner-map cross-check: 6,863 entries, 90 `[NWS: ?]`,
  matching the split-preview one-for-one, 0 residual contamination.
- **Full q-section deterministic split-preview** (all 105 q-keys [SLP1 `q` =
  retroflex ḍ] → 18 NWS-bearing, 42 entries): **0 roman-cite bleeds**. 2
  unowned = 1 benign empty + 1 real, a single Meister `(2.1)`; no OTHER. The
  2.38% real-loss rate is purely the 42-entry small base magnifying one
  Meister cite, not a new gap. Owner-map cross-check: 42 entries, 2
  `[NWS: ?]`, matching the split-preview one-for-one, 0 residual contamination.
- **Full r-section deterministic split-preview** (all 2,905 r-keys → 656
  NWS-bearing, 1,770 entries): **0 roman-cite bleeds**. 9 unowned = 8 benign
  empty + 1 real (0.06%), the multi-page-cite known limitation again
  (`Ensink 1964 : 156, viii` on `ratnasaMBava` — a comma-joined page list, the
  second token a lowercase roman; single page `Ensink 1964 : 156` parses, the
  `, viii` breaks the close). No Meister/Böhtlingk/roman/OTHER cases. Owner-map
  cross-check: 1,770 entries, 9 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full s-section deterministic split-preview** (all 18,140 s-keys → 4,297
  NWS-bearing, 10,588 entries — the largest section): **0 roman-cite bleeds**.
  88 unowned = 73 benign empty + 15 real (0.14%): 6 × Meister `(2.1)` + 3 ×
  multi-page cite (`TPSI 3 : 235, 238`, `213, 216`, `248, 249, 251`) + 3 ×
  page-less x-ref (incl. `śelu → Olivelle 2013 : śelu (s.v. śleṣmātaka )`, a
  word locator, no numeric page) + 2 × roman page + **1 new known-limitation
  class** — a lowercase parenthetical source name (`succhardís → s.v. suchardís
  Graßmann 1873 (1996). (pw) : 1531`). OWNER's name class is capital-initial, so
  `(pw)` is not matched (the canonical `PW : 1531` parses); it is a rare,
  well-formed citation style, not a typo. Owner-map cross-check: 10,588 entries,
  88 `[NWS: ?]`, matching the split-preview one-for-one, 0 residual
  contamination.
- **Full t-section deterministic split-preview** (all 3,477 t-keys → 821
  NWS-bearing, 1,968 entries): **0 roman-cite bleeds**. 15 unowned = 12 benign
  empty + 3 real (0.15%): 1 × Meister `(2.1)` + 1 × roman page + 1 × multi-page
  cite (`taTAgata → Ensink 1964 : 73, vii`, comma-joined page list, as in
  r/s). No new classes, no OTHER left after classification. Owner-map
  cross-check: 1,968 entries, 15 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full u-section deterministic split-preview** (all 2,903 u-keys → 1,126
  NWS-bearing, 2,656 entries): **0 roman-cite bleeds**. 39 unowned = 34 benign
  empty + 5 real (0.19%): 2 × page-less x-ref + 2 × Meister `(2.1)` + 1 ×
  roman page; no new classes, no OTHER. Owner-map cross-check: 2,656 entries,
  39 `[NWS: ?]`, matching the split-preview one-for-one, 0 residual
  contamination.
- **Full v-section deterministic split-preview** (all 9,658 v-keys → 2,418
  NWS-bearing, 6,526 entries): **0 roman-cite bleeds**. 79 unowned = 65 benign
  empty + 14 real (0.21%): 8 × Meister `(2.1)` + 2 × page-less x-ref + 2 ×
  roman page + 1 × multi-page cite (`vErocana → Ensink 1964 : 180, viii`) + 1 ×
  source-data typo (`vftraKAda` = vṛtrakhāda → `NṚV 2B : 79 (s. (2. khād )`).
  The typo is the **same upstream NWS defect** already in the errata (an
  unbalanced trailing paren); it surfaces here under the v-keyed headword and
  in the k-section under the khād-root fragment (`KAd`), so it costs an owner
  in both section-fragments — one source defect, two losses. No new classes,
  both OTHER classified. Owner-map cross-check: 6,526 entries, 79 `[NWS: ?]`,
  matching the split-preview one-for-one, 0 residual contamination.
- **Full w-section deterministic split-preview** (all 92 w-keys [SLP1 `w` =
  retroflex ṭ] → 19 NWS-bearing, 45 entries): **0 roman-cite bleeds**, **0
  real** (1 benign empty), 0 OTHER. Owner-map cross-check: 45 entries, 1
  `[NWS: ?]`, one-for-one, 0 residual contamination.
- **Full x-section deterministic split-preview** (all 3 x-keys [SLP1 `x` =
  vocalic ḷ] → 2 NWS-bearing, 9 entries): **0 roman-cite bleeds**, **0
  unowned**, 0 OTHER — the smallest section. Owner-map cross-check: 9 entries,
  0 `[NWS: ?]`, one-for-one, 0 residual contamination.
- **Full y-section deterministic split-preview** (all 1,810 y-keys → 420
  NWS-bearing, 1,286 entries): **0 roman-cite bleeds**. 3 unowned = 1 benign
  empty + 2 real (0.16%): 1 × roman page + 1 × Böhtlingk `*NNN`; no new
  classes, no OTHER. Owner-map cross-check: 1,286 entries, 3 `[NWS: ?]`,
  one-for-one, 0 residual contamination.
- **Full z-section deterministic split-preview** (all 302 z-keys [SLP1 `z` =
  ṣ] → 64 NWS-bearing, 112 entries): **0 roman-cite bleeds**. 2 unowned = 1
  benign empty + 1 real, a single Böhtlingk `*NNN`; no OTHER. The 0.89%
  real-loss rate is the 112-entry small base magnifying one cite, not a new
  gap. Owner-map cross-check: 112 entries, 2 `[NWS: ?]`, one-for-one, 0
  residual contamination. **This completes the full SLP1 key universe (a–z,
  with capital/long-vowel sections folded into their lowercase counterparts by
  the case-insensitive section router).**

### Known limitations
- **`Meister 1988 (2.1) : 397`** — a source name carrying a `.` *inside* a
  parenthetical volume number (`(2.1)`) is not recognized as an owner,
  because OWNER's name class excludes `.` on purpose (to stop names like
  `Hoernle 1893-1912 (II) 30.81` / `EI Vol. XV` from swallowing whole
  sentences — guarded by the `aMSa` selftest). Drops 4 b-section owners
  (`BadrapIWa`, `boDimaRqa`, `BadraraTa`, `BUmiKaRqa`).
- **`Walter 1893 : XXXII`** — a roman-numeral page is not matched, because
  OWNER's page is digit-only. Admitting roman pages globally is what
  destabilised the parser earlier (it turns co-owner segments into
  gloss-closers → lemma-stuffing) and was reverted, so it stays out.
  Drops 3 b-section owners (`brahmagranTi`, `brahmaranDra`, `brahmadvAra`).
- **`Böhtlingk 1887 : *163`** — an asterisk-prefixed page is not matched,
  because OWNER's page is digit-only. Extending it to `\*?\d+` was tried
  and reverted: like roman pages, admitting `*NNN` turns segments such as
  `Böhtlingk 1887 : *150 >` into gloss-closers and regressed `ap`/`av` to
  MISATTRIBUTION. Drops 1 c-section owner (`ci`).
- **`TPSI 3 : 19, 22`** — a multi-page citation (comma-joined page list) is
  not matched, because OWNER's page is a single token (`\d+[A-Za-z]?`) and the
  owner must close the gloss; the trailing `, 22` leaves residue after `: 19`,
  so the owner does not close and is dropped entirely. Same digit-only-page
  family as roman/asterisk pages: broadening the page class to swallow
  comma-joined lists would let trailing comma-separated gloss content be read
  as page numbers, destabilising segment/owner alignment, so it stays out by
  design. Drops `prakaraRasama` (p), `ratnasaMBava` (r,
  `Ensink 1964 : 156, viii`), 3 s-section owners (`savyaBicAra`,
  `saMSayasama`, `sADyasama`, all `TPSI 3 : …, …`), `taTAgata` (t,
  `Ensink 1964 : 73, vii`) and `vErocana` (v, `Ensink 1964 : 180, viii`).
- **`(pw) : 1531`** — a lowercase parenthetical source name is not matched,
  because OWNER's name class is capital-initial (the canonical `PW : 1531`
  parses); admitting lowercase parenthetical tokens would let parenthetical
  gloss asides be read as owners, so it stays out by the same name-class design
  as `Meister (2.1)`. Drops 1 s-section owner (`sucCardis → s.v. suchardís
  Graßmann 1873 (1996). (pw) : 1531`); a rare, well-formed citation style, not
  a typo.
- These are rare (b: 7 / 2,655 = 0.26%; c: 9 / 1,828 = 0.49%), terminal,
  and confined to a few works (Meister 1988, Walter 1893, Böhtlingk 1887);
  the safely-fixable nested/variant-paren gap is already fixed. Roman and
  asterisk pages share one cause — admitting them as page tokens
  destabilises segment/owner alignment — so both stay out by design.

## 2026-06-20

### Added
- `schemas/pwg_ru_final_card.schema.json` and
  `validate_final_card_schema.py` define the final translated-card + judge
  contract, including auditable Apresjan `differentia` evidence.
- `validate_assembled_export.py` checks deterministic assembled-card JSONL
  exports, with full count-match mode and bounded supervised-sample mode.
- `run_batch.py validate_review` and `run_batch.py apply_review` make the
  review store gate machine-checkable before any row can become print-ready.
- `gold_validate.py`, `gold_ingest.py`, and `gold_agreement.py` validate human
  gold labels, ingest release-bound JSONL, and compute Wilson precision plus
  double-review agreement metrics.
- `export_interop.py` and `validate_interop.py` generate and validate minimal
  TEI Lex-0, OntoLex, and Russian reverse-index artifacts.
- `make_edition_cut.py`, `validate_release.py`, `CITATION.cff`, and
  `DOI_PLAN.md` add the immutable edition-cut skeleton and manifest hash check.
- Nonhuman print-gate helper tooling now prepares reviewer work without filling
  human decisions: `run_batch.py review_report`, `gold_status.py`,
  `gold_packet.py`, `gold_double_review_queue.py`, and `release_readiness.py`.
- `gold/REVIEWER_HANDOFF.md` gives reviewers one place for allowed enum values,
  protected columns, validation commands, and the G5-G7 handoff flow.
- `gold_packet_verify.py`, `gold_double_review_verify.py`, and
  `preflight_remaining_gates.py` verify reviewer packets, second-review queues,
  and the compact "what's left?" status without inferring any human labels.
- `gold_ingest_double_review.py` bridges filled wide double-review queues into
  long-form reviewer JSONL that `gold_agreement.py` can score.
- Review-gate fixture coverage now exercises blank decisions, invalid approvals,
  explicit `apply_review`, and fail-closed interop export without touching the
  real local translation store.

### Changed
- `assemble.py build` now writes to temp files and installs outputs only after
  successful completion, protecting `assembled_cards.jsonl` from killed-run
  corruption.
- Failed atomic replacement now leaves the previous assembled export untouched
  and keeps the temp file for manual recovery instead of unlinking the old file.
- `assemble.py build` now precomputes corpus evidence once per build, uses
  `corpus_lexicon.jsonl` rows for export-time examples instead of per-card
  SQLite FTS, and supports grouped-card chunks via `--offset`, `--out`, and
  `--quarantine`.
- The top-level AI/release status now says the core release machinery is ready
  but print remains blocked by human review, human gold labels, double-review
  agreement, and a real immutable edition cut.
- `roadmap_check.py` now detects gate status drift between the aggregate
  scientific-hardening JSON and the JSONL gate ledger.
- Release manifest validation now rejects missing/null gate status maps and
  checks manifest gate statuses against the edition's copied gate ledger.
- The monorepo CI/local fixture checks now exercise final-card schemas,
  gold-label packets, double-review queues, interop fixture exports, and a
  fixture edition cut without requiring local gitignored production data.
- `run_batch.py` and `release_readiness.py` accept `PWG_RU_STORE`,
  `PWG_RU_REVIEW_Q`, `PWG_RU_REVIEW_CSV`, and `PWG_RU_REVIEW_REPORT` path
  overrides so review-gate tests can run against disposable fixture stores.
- Full interop export now validates: `release/tei_lex0.xml` and
  `release/ontolex.ttl` each cover 120,173 lexical entries, and
  `release/reverse_index.jsonl` has 209,319 Russian-to-Sanskrit rows.

## 2026-06-19

### Added
- Machine-readable scientific-hardening roadmap and print-blocking quality gates:
  `roadmap/scientific_hardening.json`, `roadmap/quality_gates.jsonl`, and
  `src/roadmap_check.py`.
- `src/pilot/run_real_test.py` audit preflight was exercised with a synthetic
  `ap` workflow output, proving the collect → protected-card preservation →
  `nws_split.py check` → report path before the June-22 Max run.
- `run_batch.py review_csv` exports `_review_queue.jsonl` to a spreadsheet-ready
  `_review_queue.csv` with blank human-review columns (`reviewer_id`, `decision`,
  `edit`, `notes`) while leaving review state unchanged.
- `gold/HUMAN_GOLD_PROTOCOL.md` defines the human gold-set labeling protocol,
  double-review/adjudication workflow, and acceptance criteria; `gold_review_csv.py`
  exports the existing 320-row balanced scaffold for reviewers.
- `schemas/pwg_ru_lexicographic_portrait.schema.json` and
  `validate_portrait_schema.py` define and check the v1 Apresjan portrait
  contract for live `microstructure.portrait()` output.

### Changed
- Modern Sanskrit-Russian sources with project approvals are now marked
  publishable with attribution/provenance, not evidence-only; see
  [RIGHTS_APPROVALS.md](RIGHTS_APPROVALS.md).
- Shared the case-collision-safe filename encoder across NWS scrape/split/audit,
  pilot generation, and merge lookup; forbidden Windows filename characters are
  escaped reversibly.
- `_pilot_collect.py` now writes audited `<safe>.merged.md` files directly using
  `safe_name()`; the real-test auditor no longer needs a brittle external
  `<key>.md` copy bridge and uses the same filename encoder as the rest of the
  pipeline.
- `run_real_test.py prep` was refreshed for the June-22 batch window
  (`OFFSET=0`, `LIMIT=10`): `as As Ap api amfta agni Atman anu arjuna arTa`,
  now correctly all fresh after exact-case output checks.
- `run_pilot_wf.js` now loads the canonical final-card schema instead of
  carrying a prompt-local schema copy.

### Fixed
- Corpus harvest no longer lemmatizes Sanskrit proper names such as `Агни` to
  unrelated Russian verbs such as `агнуть`.
- `scale_route.py` now routes by the protected microstructure sense parser.
- `assemble.py` quarantines lossy round-trip records instead of emitting them
  into the normal assembled card stream.
- `run_batch.py migrate_legacy` backfills old translation-store rows and marks
  unverifiable legacy cards `legacy_needs_review`.
- Protected hand-authored pilot cards (`aMSa`, `anna`, `ap`) are preserved during
  real-test collection/audit, while still being audited by `nws_split.py`.
- Legacy `.merged.md` compatibility checks now require exact filenames, avoiding
  Windows case-insensitive false positives such as `Ap` being treated as protected
  because `ap.merged.md` exists.
- Generated the missing writable a-section input for `arI|a` (`|` escaped as
  `~007c`); pilot inputs now cover 12,156/12,156 a-section manifest cards.
- Materialized the human review worklist with `run_batch.py review`: 217
  `legacy_needs_review` cards, severity-sorted, with no reviewer decisions
  advanced.

## 2026-06-16

### Added
- **Corpus harvest layer** ([HARVEST.md](HARVEST.md)): `build_ls_map.py` +
  `ls_source_map.json` (PWG `<ls>`→stratum, 45 sources = 72.4% of 772k
  citations, 29.8% corpus-harvestable) and `corpus_harvest.py` — SLP1 key →
  Russian renderings, lemma-grouped (pymorphy3), POS-filtered, stratified, with
  the `<ls>`-cited stratum first and a `--raw` escape for particle headwords.
- **Recurring deterministic integrity auditor** (`_audit.py`): flags
  placeholder leak / non-Cyrillic / `ru==sa` / `√`-keys / dups / stratum
  mismatch; run at each build milestone; exit-code verdict.
- **Live cost/ETA watcher** (`_watch.py`): progress bar, $ spent / needed, ETA,
  measured over a live window (not the append-only file's stale ctime).
- **Methodology review** ([METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md)):
  grounded 5-lens review (FAIR/DH, bilingual lexicography, corpus-NLP eval,
  standards/interop, editorial) → prioritized roadmap.
- **Priority-1 fixes**: per-card **provenance** (model ids, prompt hash,
  `pwg.txt` commit, run id, timestamp + persisted senses); **human-review state
  machine** + `run_batch.py review` editor worklist; **per-sense rights gate**
  (`corpus_gate.RIGHTS`/`publishable()`) + **CC BY-SA 4.0** data licence
  ([DATA_LICENSE.md](DATA_LICENSE.md)).
- **Coverage honesty check** (`corpus_harvest.py coverage`): per-stratum rows /
  groups-done flags EMPTY/thin strata.
- **Apresjan theoretical grounding** ([APRESJAN.md](APRESJAN.md)) and a
  **failure gallery** ([failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md)).

### Changed
- Corpus-lexicon build **batched** (~8 verse-units / DeepSeek call, 12 workers,
  biggest-first); quality verified equal to single-call, ~3–4× faster.
- `build_strata.count_groups()` now requires a Cyrillic translation, so sizes /
  ordering reflect genuinely-translated material (78,139 → 58,897 genuine groups).

### Fixed
- **Placeholder fabrication (build-stopping)**: untranslated `…` verses were fed
  to DeepSeek, which hallucinated 166k/204k rows (81%). Fixed with a Cyrillic
  guard; recovered to 26,277 genuine rows. See the gallery.
- Footnote-overwrites-translation; `√` leaking into keys; commentary
  cross-segment duplication; biggest-first cost mis-projection; frozen/dead-build
  liveness misreads. See [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md).

## 2026-06-15

### Added
- **Source extraction** (`build_src.py`): 5 Sanskrit–Russian dictionaries
  (Кочергина, Кнауэр, Фриш, Смирнов, Коссович) pulled from SamudraManthanam →
  gitignored `src/*.jsonl` (~57,640 keyed entries).
- **Stage-4 corpus gate** (`corpus_gate.py`): SLP1 join over the 5 dicts + the
  parallel-corpus query; non-blocking 2-signal annotation (correctness vs
  independent dicts; reference-agreement vs KOW). Coverage measured honestly
  (correctness 16.4% / KOW 8.0% / corpus ~14–15%; dominant `no-check`).
- **Pipeline** (`pwg_mask.py` masker, `assemble.py` harvest, `run_batch.py`
  driver): mask German skeleton → harvest attested senses → translate (Sonnet
  4.6 on Max) → judge (Opus 4.8) → re-translate. Pilot: 6/6 then ~88–95%
  first-pass publishable.
- **Stratification** (`build_strata.py` + `corpus_strata.json`): 121 corpus
  texts by genre (Renou) + date (Dharmamitra Gibbs median + 95% CI) + period.

### Changed
- Strategy pivots: **harvest-first** (assemble Russian from existing material;
  harvested meanings become additional *attested senses*), then **corpus-first**
  (build the corpus word-alignment lexicon before bulk translation), then
  **quality-over-quantity** (it becomes a printed scholarly dictionary).

## 2026-06-14

### Added
- **pwg_ru kit scaffolded** (committed `384fedb`), mirroring the completed
  `mw_ru`: editor doc [pwg_ru.md](pwg_ru.md) + stage prompts
  ([pwg_ru_prompts/](pwg_ru_prompts/)) (translate → 2 QA judges → re-translate →
  corpus check). Headline format rule: PWG `{%…%}` wraps both German glosses
  (translate) and Latin (leave). Model unified to Opus 4.8.
