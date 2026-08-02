# pwg_ru — changelog

How the Russian edition of the Petersburg Dictionary (PWG, Böhtlingk–Roth)
evolved. Newest first. This is the *project* changelog (method + pipeline); the
data stores are gitignored and versioned by their build provenance.

See also: [METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md) (where we want to go),
[failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md) (what went wrong and
how it got better), [APRESJAN.md](APRESJAN.md) (the theory we build on).

## [Unreleased]

## [1.135.0] - 2026-08-02

### Added
- **H2158 Phase 1 — the pwg_ru route A/B, and the measurement that reframes it (02-08-2026, Opus 5 `claude-opus-5`):** two-arm harness [`h2158_route_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2158_route_ab.py) (CLI-headless vs Messages API with an explicit 1h `cache_control` prefix), [`h2158_route_ab_report.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2158_route_ab_report.py), [`h2158_liveness_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2158_liveness_probe.py); report [`ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2158/ROUTE_AB_MESSAGES_API_VS_CLI_HEADLESS_02-08-2026.md). Both arms send **byte-identical** `build_prompt` output — the harness asserts it and refuses to measure otherwise. **Measured (real `h1209_slice3` cards, bare cwd):** one card **completes in 375 s** — never hung, just **25 % past the 300 s ceiling**, which is why 3/3 runs at the production ceiling died with no envelope; H2011's "whole-card lane is non-terminating" is refined to *terminating but over the wall*. Cost **$0.8005**, decomposing to **output 34 215 tok = 64.1 %**, cache create 46 117 = 34.6 %, cache read 1.3 %. **Output dominates because Phase 0 worked:** against H2011's pre-bare-cwd card ($0.8661, creation **106 072 tok = 73.5 %**), creation fell **−57 %** — yet the total moved only **−7.6 %**, because output was always underneath. Since output bills identically on both routes, **the Messages API port addresses the smaller half**. **API arm not run** (no credential on this machine; the harness refuses to run one-armed rather than emit a half-table that reads like an A/B) → verdict **INCONCLUSIVE**, interim **NO-GO**; campaign band **$33–$243** over ≈465 cards against a CLI floor of **≈$372**, the 7× spread being entirely the unmeasured question of whether the CLI's 34 k output tokens are agent-loop overhead or real work. Two defects filed: `parse_workflow_cost.PRICE['cache_write'] = 3.75` is the **5-minute** rate while this lane's writes are `ephemeral_1h` (2× base = $6.00) — the *prose* in `RUN_FREQ_MAX.md`/1.132.0 already prices at $6, so anything **computed** from `PRICE` silently under-reports by 1.6×; and [`bare_cli_cwd()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py#L82) strips *project* but **not profile** context — a probe call **refused its own instruction**, citing a `⭐ Next:` rule from the profile's global `CLAUDE.md`, a correctness exposure and ~133 k tokens of prefix against a ~6–7 k-token task. Raw envelopes **committed, not gitignored**. No route flip, no bulk campaign, no `HARD_TIMEOUT_MS` raise. [PR #1015](https://github.com/gasyoun/SanskritLexicography/pull/1015).

## [1.134.0] - 2026-08-02

### Fixed
- **`b0` was never non-terminating — a per-card presplit floor was masked by the per-batch budget (H2160, 02-08-2026, Opus 5 1M `claude-opus-5[1m]`, [#983](https://github.com/gasyoun/SanskritLexicography/issues/983)):** the "non-terminating call" reading carried by 1.130.0 and 1.132.0 is **withdrawn**. `b0` is not a 3-key batch (w1 holds three separate 1-key batches; `b0` is `nakzatra` alone), and its death at 180 044 ms then 300 073 ms is **our own kill gate**: `killBudgetForCur` grants any single-card batch `KILL_CEIL_MS` unconditionally, so `b0`'s budget *is* the ceiling and the +44/+73 ms overshoot is `setTimeout` dispatch latency. It "converged on no bound" because the bound was re-firing at each new ceiling — the call has never been allowed to finish, so it has never been observed to hang. Nor is it whole-card-specific: **11 of 16 calls in the 180 s run died at 180 0xx–180 2xx ms and only one was whole-card** (five of `nakzatra`'s eight heal groups and all three retries died on the same gate), because `killBudgetMs` clamps to CEIL for any payload above ~1.6 KB. **This is the same conclusion H2011 reached independently and from the other direction** in 1.133.0 below — its calls 2–4 were the *identical* fragment `rAtra_f0` at 180.0 / 180.1 / **142.6 s success**. Between them the two runs pin it: the wall is **our ceiling meeting a heavy right tail**, not a lane, a card size, or a provider hang. The presplit defect this entry fixes is therefore **necessary but not sufficient** — it stops citation-heavy cards being spent on a doomed whole-card attempt, but fragments drawn from the same latency distribution still die at the wall (H2011 measured ~75 % kill on one small card), so throughput needs the ceiling-vs-variance question answered too. The defect itself: `_presplit_hit` routed on `(1+<ls>) > max(OUTPUT_BUDGET, PRESPLIT_SOLO_CITE_FLOOR)`, letting the per-**batch** packing cap (90) mask the per-**card** fail-solo floor (40) and leaving it inert at every default run ("For OUTPUT_BUDGET >= 40 (default 90) nothing changes"). w1's cards score 80/79/75 — above the threshold that says a card cannot be emitted whole, below the unrelated batch cap — so `presplit_keys` came out `[]` and all three were attempted whole and killed. The trigger now compares against `PRESPLIT_SOLO_CITE_FLOOR` alone. RED-verified pin `test_presplit_cite_floor_is_not_masked_by_batch_budget`; `window_selftest` **200/200**, `lang_parity_check` **90 entries no drift** (52 re-stamped; the one functional line is language-blind). Table: [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

### Added
- **`src/pilot/h2160_regen_medium50.py` — re-prepare the medium50 windows on the fixed predicate (H2160, 02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** replays the coordinator's own `prepare` invocation with every argument read back out of the existing manifest (no hand-retyped key lists), verifies the regenerated `config_dir_fingerprint` is unchanged, and prints the new manifest/harness SHA-256 that `headless_worker.py --manifest-sha256` needs. Across w1–w5 presplit coverage goes **10/48 → 44/48 keys**, leaving exactly the four cards scoring at or below the 40-unit fail-solo floor (`rAtra` 33, `spfS` 30, `idAnIm` 36, `prasU` 31) on the whole-card lane. ⚠️ `rAtra` is precisely the card H2011 spent 682 755 ms and 4 calls on for one partial result, so those four remaining whole-card keys are **not** thereby proven safe — they are simply below the citation threshold this fix acts on. Companion offline diagnostic `src/pilot/h2160_batch_shape_probe.py` reads batch shape, citation weight and presplit state straight out of the prepared manifests.
- ⚠️ **Unproven live.** `/pwg-live-gate` Step 1 returned **NO-GO** (measured 75 561 ms ≥ the 65 000 ms ceiling; warm-up 236 358 ms), so per policy no canary was built and **no translation call was made** — 2 paid probe calls, $0.9459, no window, no store write. Note this NO-GO is ~23 minutes after H2011's **PASS at 43 815 ms** on the same profile: a 1.7× swing in the gating number within the half-hour, which is the same variance finding arriving in the gate itself. The presplit route is implemented and gated but not yet demonstrated in production — residual [H2174](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2174-Opus_RussianTranslation_medium50-presplit-live-run-after-health-pass_02.08.26.md). Also filed there: the gate's prose says gate on `duration_api_ms` while `probe_log.derive_fails` gates on **wall**, and this run passes on the former (29 069 ms) and fails on the latter — the measured NO-GO was recorded and deliberately **not** overridden.

## [1.133.0] - 2026-08-02

### Added
- **c4 live gate returns `LIVE_GO` — first PASS of both halves, and the first per-CARD observed economics (H2011, 02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** `/pwg-live-gate` Steps 1–3 on c4, **3 paid calls** (2 gate + 1 canary), **no bounded window, no promotion, no store write, no constant moved.** Step 1 measured **43 815 ms** (`duration_api_ms` 26 386 / `api_gap_ms` 17 429) against the 65 000 ms ceiling — the fastest decomposed c4 reading on record — with the warm-up at 55 390 ms, both `success` and schema-valid. Step 2 ran the curated `dq_canary_puregloss~~h0_zz_pw` synthetic control through the headless CLI on a manifest v2 built by the **canonical builder** (never hand-written, so the prompt is production's own): **121 693 ms, 3/3 senses, 0 null**, and [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) clean 1/1 with the SAN-LOSS sense-count guard, sense-dupe gate, `ru_style` and coverage all PASS. **`gate_reason = LIVE_GO`, `verdict = GO`**, derived from the policy rather than asserted. The call's `$0.8660853` **reproduces exactly from list rates**, with **cache creation at 73.5 %** (106 072 tokens × $6/M) — so [#986](https://github.com/gasyoun/SanskritLexicography/pull/986)'s ~71 % on a heal call and [#994](https://github.com/gasyoun/SanskritLexicography/pull/994)'s 87.6 % on a trivial ping are now joined by a real schema-carrying translation, and the finding is not an artefact of trivial payloads. Two new measurements fall out: [`perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py) projected **$0.15** against an observed **$0.8661** — a **5.8×** underestimate on one card with `cost_evaluable: true`, sharper than the 4.7× in [#949](https://github.com/gasyoun/SanskritLexicography/issues/949) — and at `--output-budget=1` the citation-heavy cards (`divA` 47 `<ls>`, `SvAsa` 82 `<ls>`) **route to direct fragment translation**, so "one card per call" is one call only for small cards. **Step 3, the bounded window MG's spend GO was granted for — 5 paid calls, `--output-budget=1`, 3 real cards, `--ephemeral` audit, no promotion and no store write:** `completed_with_residuals`, **1 of 3 cards and that one only partial**. Four calls died at the wall (180 025 / 180 020 / 180 072 / 180 100 ms), one succeeded at 142 638 ms; `divA` → `timeout`, `SvAsa` → `budget_exceeded:heal`. **`rAtra`, the smallest real card in the input set (2 418 B), consumed 682 755 ms — 11.4 minutes — and 4 calls to produce one partial card**, so the morning's "16 calls, 0 cards" reproduces at the floor and is not a big-card problem. **The wall is variance, not size, which is new:** calls 2–4 were the *identical* fragment `rAtra_f0` at 180.0 / 180.1 / **142.6 s success**, i.e. the work fits inside the ceiling and a fixed 180 s wall simply clips a heavy right tail into a ~75 % kill rate. **Failure-class composition is the H1940 Phase 2 pass:** 3 requeue, **all `transient`, 0 `defect`** — no failure misfiled as a content defect (the H2a/H2b class), no hot-spin, no stranded cohort, no lost checkpoint. Throughput did not improve, exactly as the handoff warned it might not; attribution correctness did. Cost `$0.6206808` with **`cost_evaluable: false` and 4 of 5 calls unpriced**, so the ledger under-reports the window ~5×; the one priced call again decomposes to the cent with cache creation at **68.9 %**. Readings + full decomposition: [`H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/H963_C4_SINGLE_PROFILE_GATE0_HEALTH_2026-07-16.md) (eighth reading) and [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

### Fixed
- **The `h1339_offline_bench` byte-identity control is stale — filed, not silently re-baselined (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** H2011's Definition of Done requires re-verifying deterministic signature `9bd2a14297`. It does not reproduce at **any** commit tested — `586d012b3d` at master HEAD [`64a4fa62`](https://github.com/gasyoun/SanskritLexicography/commit/64a4fa62), at [`a75eaa17`](https://github.com/gasyoun/SanskritLexicography/commit/a75eaa17) (the [#911](https://github.com/gasyoun/SanskritLexicography/pull/911) close-out that *recorded* "signature `9bd2a14297` unchanged") and at [`005d2f0f`](https://github.com/gasyoun/SanskritLexicography/commit/005d2f0f), under both CPython 3.14.4 and 3.12, with the fixture content hash `569660c689d0659b` untouched since 25-07-2026 and the bench still reporting `deterministic outputs: True`. Determinism holds, so the control still works *relatively*; the **documented absolute value** has been carried in prose across at least three commits without anyone reproducing it, which makes every "outputs unchanged" close-out that quoted it unverified. Tracked as [#1000](https://github.com/gasyoun/SanskritLexicography/issues/1000) with a proposed `--expect-signature` pin so the control fails loudly instead of being quoted from memory.

## [1.132.0] - 2026-08-02

### Changed
- **The operator playbook now carries the H2152/H2158 cost rules — and a stale rule surfaced while propagating them (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** the measurements had landed in `RESULTS_LOG`/FINDINGS and the code fix in 1.130.0, but not in the docs a session reads *before* spending. [`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) § Current operating truth gains the bare-cwd rule, **"the per-call cache is never reused — budget for it, do not tune it"** (two identical calls re-created 49 153 → 49 165 with read pinned at 28 882; **not** TTL — the write is `ephemeral_1h`), and **"one card per call, because shape is not the lever"**; § Instrumentation now requires cache **creation vs read recorded separately** plus the TTL bucket, and `duration_api_ms`/`api_gap_ms` alongside wall clock (`subagent_tokens` flagged as a legacy misnomer for the sum of the four fields). [`AGENTS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md) carries the short form; [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) gains a dated entry tabulating each wrong reading of the 25-07→02-08 arc against its verdict. The shape bullet is annotated with the same-day ceiling divergence — heal lane genuinely outgrew 180 s, whole-card lane is **non-terminating** so a higher ceiling increases its waste — so "the ceiling was raised" is not misread as "the timeouts are fixed". **Config repos (outside this repo):** `/pwg-bounded-run` had **`--cwd .` hardcoded** in its command block; `/pwg-live-gate` gained the `duration_api_ms` gating rule plus "a hang is a quota candidate first, but our own kill is a third class" and "`auth status` proves credentials, not quota"; and the **Codex twin of `/pwg-live-gate` was still carrying the superseded `both readings < 30000 ms` health policy**, which would have NO-GOed the 02-08 `LIVE_GO` (warm-up 55 390 ms, measured 43 815 ms) — blocking a route MG unblocked on 31-07-2026. Corrected on both hosts. [PR #1004](https://github.com/gasyoun/SanskritLexicography/pull/1004).

## [1.131.0] - 2026-08-02

### Added
- **`src/pilot/canary_gate.py` — the canary half of the live gate, as code (H2159, 02-08-2026, Fable 5 `claude-fable-5`):** H2025 audit gap G4 (F-B2/F-B3, the largest non-money gap). The `/pwg-live-gate` canary verdict ("3/3 senses + zero SAN-LOSS/TNMASK") existed only as skill prose — nothing recorded it and `--execute` could not tell whether a gate had run, passed, or run two days ago. `canary_gate.py judge <wf_output> --receipt <path>` now derives GO/NO-GO mechanically (synthetic-key refusal via the promote lane's `SYNTHETIC_KEY_RE`, expected-sense shortfall, unresolved `{Tn}` via the same single-sourced `TN_RE` as the promote C-01 guard, literal SAN-LOSS/UNMAPPED markers) and writes an atomic `pwg.canary_gate_receipt.v1`; `bounded_staged_run.py --execute` now **refuses to start without a fresh (≤6 h) GO receipt for the same profile** (`--canary-receipt`; `--skip-canary-gate` is the explicit command-review-visible escape). Also lands the H2157 `AGENTS.md` paragraph that a case-mismatched path (`Agents.md`) silently dropped from PR #996. Docs synced: `RUN_FREQ_MAX.md`, `AGENTS.md`, `/pwg-live-gate` + `/pwg-bounded-run` skills (claude-config). Pinned by `test_q3_execute_requires_canary_go_receipt_h2159`; `bounded_staged_run_selftest` green, `window_selftest` 199/199, parity 3 entries re-derived (the gate reads `sense['russian']` — the RU-lane canary field — noted explicitly, no `--lang` branch added).

## [1.130.0] - 2026-08-02

### Added
- **The CLI child now spawns from a bare cwd, not the repo (02-08-2026, Opus 5 1M `claude-opus-5[1m]`, H2158/[#983](https://github.com/gasyoun/SanskritLexicography/issues/983)):** v1.127.0 measured the win (**−33 % cost, −30 % wall clock**) but made no code change. `proc_tree.run_tree_kill` had always accepted `cwd` and passed it to `Popen` — nothing ever supplied one, so the child silently inherited the repo and paid CLAUDE.md + git-state injection (~11–17 k volatile prefix tokens) on **every** call. New `bare_cli_cwd()` returns a **stable** directory (a fresh one per call would re-break the very prefix this stabilises) and **fails safe**: if the candidate still sits inside a git repo or under a `CLAUDE.md` it returns `None` and the historical inherited-cwd behaviour is kept, rather than silently spawning from a directory that still injects context. Pinned by `headless_worker_selftest.test_cli_spawns_from_a_bare_cwd`, which asserts both halves — that a cwd is passed at all, and that what it points at carries no `CLAUDE.md` and no `.git`. The wall-clock half matters beyond cost: a 30 % shorter call is 30 % more headroom against the ceiling.

### Fixed
- **The 300 s ceiling is validated for the heal lane and refuted for the whole-card lane (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** re-run `h1447-m50-2026-08-02b` after [v1.128.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.128.0), stopped externally after 4 calls but decisive. `heal:nakzatra#g2` returned at **176 952 ms** — **3 048 ms inside the old 180 000 ms bound** — and the same heal groups ranged 82–120 s and 134–177 s across the two runs, so the lane's upper tail was genuinely being killed by an outgrown ceiling. **But `translate b0` died at 180 044 ms and then at 300 073 ms**, converging on neither: it is a **non-terminating call**, not a marginally slow one, so for the whole-card lane a higher ceiling strictly *increases* waste (300 s burned per dead attempt instead of 180 s). This corrects the previous entry's framing, which read all 12 timeouts as one phenomenon. The whole-card hang is a separate, still-unfixed defect. Table: [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

## [1.129.0] - 2026-08-02

### Fixed
- **`--execute` now requires both ceilings (H2157, 02-08-2026, Fable 5 `claude-fable-5`):** H2025 audit gap G3 (F-B1) — `--max-calls` and `--cost-ceiling` both defaulted to `None`, `cost_ceiling_evaluable` explicitly passed when unset, and the supervisor skipped both checks on `None`: the lane's excellent fail-closed ceiling machinery was inert unless the operator remembered two flags, so a billed run had **no ceiling at all by default**. A paid `bounded_staged_run.py --execute` now refuses to start unless both are supplied; the explicit `--allow-unbounded` flag is the only escape, visible in command review. Dry-run and offline lanes unaffected. Operator docs synced in the same pass ([`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md), [`Agents.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/Agents.md), `/pwg-bounded-run` skill). Pinned by `test_q2_execute_requires_ceilings_h2157`; `bounded_staged_run_selftest` green, `window_selftest` 199/199, parity 3 entries re-derived (0 language-keyed diff tokens).

## [1.128.0] - 2026-08-02

### Changed
- **The per-call ceiling relaxed 180 s → 300 s, by explicit human ruling (02-08-2026, Opus 5 1M `claude-opus-5[1m]`, [#983](https://github.com/gasyoun/SanskritLexicography/issues/983)):** the standing `"NOTHING runs past 3 min (MG)"` rule (R4/C-15, H189) was the direct cause of a paid window returning **zero cards** — 12 of 16 calls died at exactly 180 04x–180 23x ms, and it was not tunable from below because heal groups were already at a **single fragment** while the kill gate `clamp(BASE + 45×bytes, FLOOR, CEIL)` saturates at CEIL for any fragment >~3.5 KB. Successful calls had crept to 67–**91 %** of the old budget. **The ceiling is enforced in five independent places and raising one is inert** — `headless_worker.HARD_TIMEOUT_MS`, `gen_opt_harness2.KILL_CEIL_MS`, each sealed manifest's `budgets.timeout_ceil_ms`, the `KILL_CEIL_MS` baked into every generated `run_pilot_wf.*.js`, and the operator's own `--timeout`, since the effective bound is their `min()`. The two source constants are now **pinned equal** by a new `headless_worker_selftest.test_kill_ceiling_in_step_with_harness` (verified RED against the drift it guards). 300 s keeps ~1.8× headroom over the worst observed success (164.3 s) and stays below the 390 s agent that prompted H189, so the anti-regression guard against the old 480 000 (8 min) is unchanged and still enforced. Gates: `window_selftest` **199/199**, `lang_parity_check` **90 entries no drift** (52 entries re-stamped; `wall_clock_kill_gate` re-derived in writing — the diff is three integer constants plus comments and greps ZERO hits for any language-keyed token).

## [1.127.0] - 2026-08-02

### Added
- **`src/pilot/cache_prefix_stability_probe.py` — settle WHY every call re-creates its cache (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** [#986](https://github.com/gasyoun/SanskritLexicography/pull/986) left two candidates — an unstable prefix across `claude -p` invocations, or a lapsing TTL. **It is the prefix; the TTL hypothesis is refuted.** Two arms (repo cwd vs bare cwd) × 2 identical `--max-turns 1` calls, **4 paid calls, $1.0469**. Every write went to `ephemeral_1h_input_tokens` and a **1-hour** TTL cannot lapse between calls issued seconds apart; two identical repo-cwd calls re-created **49 153 → 49 165** tokens with cache read pinned at 28 882, i.e. **the second re-wrote exactly what the first had just written and nothing carried over**. The prefix decomposes into a stable **~29 k** core plus a volatile **~49 k** segment; in a bare cwd the volatile part falls to ~32–38 k and is the only place any cross-call reuse appears (read **+5 553** / create **−5 553**, exactly complementary), so **CLAUDE.md + git-state injection is what breaks it**, worth ~11–17 k tokens per call. **Free measured win: running the lane from a bare cwd is −33 % cost and −30 % wall clock**, no code change and no guard weakened. Structural read: with `--max-turns 1` the floor is **~19–29 s of non-API overhead against ~2–3 s of API time** and ~32–49 k tokens re-written per call regardless of payload — a one-shot CLI subprocess **cannot amortise its own system prompt**, which is a property of the route, not a tuning knob. Table: [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md). Port tracked as [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md).

## [1.126.0] - 2026-08-02

### Fixed
- **H2144 D4b bracket-normalize unlock for the 63-row PWG fullwidth-paren residual (02-08-2026, Sonnet 5 `claude-sonnet-5`):** extends [`d4_boundary_wrap.try_boundary_wrap`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/d4_boundary_wrap.py) with an opt-in `normalize_brackets` param (default `False`, zero behavior change for existing rows) that treats DE's fullwidth/CJK corner-bracket numbering marker as equivalent to RU's ASCII parens before the exact-affix check, per the adjudication in [H1702_SONNET_DUAL_RUN_COMPARE_2026-08-01.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_SONNET_DUAL_RUN_COMPARE_2026-08-01.md). The comparison-only normalization always splices from RU's own bytes, so its native bracket form is never rewritten into DE's. Hand-checked all 63 newly-eligible rows (full population) — 100% clean, no anchor/citation swallowing. Applied to the live store: `ru_n==0` residual 1,109 -> 1,046. New apply script [`fix_d4b_bracket_normalize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_d4b_bracket_normalize.py) uses H2146's `locked_store_rewrite`. Report: [H1702_D4B_BRACKET_NORMALIZE_REPORT_2026-08-02.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_D4B_BRACKET_NORMALIZE_REPORT_2026-08-02.md). Also fixed a missing `store_write` import in `annotate_renou.py` inherited from H2146 that broke `master`'s own Python-lint CI. PR [#981](https://github.com/gasyoun/SanskritLexicography/pull/981).

## [1.125.0] - 2026-08-02

### Fixed
- **Fail-closed occupied-keys guard (H2154, 02-08-2026, Fable 5 `claude-fable-5`):** H2025 audit gap G2 (census S1-1/S1-2, the lane's only remaining duplicate-paid-spend path). The scheduler's `occupied` set — keys owned by queued/running jobs — was built under a per-manifest `except: pass`, so an unreadable/renamed/mid-write manifest contributed **zero** keys, the overlap check passed, and the same headwords could dispatch into a **second paid window**. Both import paths (`cmd_import_coordinator`, `cmd_import_requeue`) now share one `occupied_keys(db)` helper that **aborts the import** naming the job + manifest when a live job's manifest cannot be read; terminal jobs with lost manifests stay ignorable, and the manifest read no longer leaks a file handle (the Windows sharing-violation class). Pinned by `test_occupied_keys_guard_fails_closed_h2154` (`max_account_orchestrator_selftest` green; `window_selftest` 198/198; parity 3 entries re-derived, 0 language-keyed diff tokens).

## [1.124.0] - 2026-08-02

### Added
- **H2152 call-shape audit — quota is not the binding constraint; wall clock is (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** [`pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md) (+ sibling metadoc) resolves the tension [FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) opened against MG's one-card instrument-everything mandate. **Verdict: HOLD one-card, and stop treating call shape as the lever.** A same-moment ping (1 paid call, `$0.3456`) returned a real envelope in 58.8 s — not throttled — so the ceiling that binds today is `HARD_TIMEOUT_MS`, not quota, and the two pull in **opposite** directions: quota penalises many calls, wall clock penalises large ones. Under the binding one the small shape wins, so mandate and §270 are not in conflict right now. **Neither shape fixes the current failure** — single-fragment calls already time out, so there is no smaller shape left. Inventory finding: one-card is **not enforced anywhere in code** (default is batched, [`gen_opt_harness2.py:102`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L102)) and needs **no** engineering — `--output-budget=1` is an existing, already-hardened lane ([`:137`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py#L137), with `PRESPLIT_SOLO_CITE_FLOOR` existing solely to keep it from degenerating). Two corrections: the "~90 k cache-creation per call" premise carried by H2011/H2152 is a **two-call aggregate** (~45–50 k per call), halving the amortisation prize from batching; and `cost_evaluable=False` propagation ([`call_reservation.py:378`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L378)) means one unevaluable call destroys attribution for **all N** cards in its batch. Gate design: the cheapest quota classifier is not a new probe but attaching the already-drained streams at [`proc_tree.py:270`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py#L270) (§273) — zero paid calls. Audit only: no window, no store write, no constant moved. **Folded in same-night ([PR #989](https://github.com/gasyoun/SanskritLexicography/pull/989)):** the [#986](https://github.com/gasyoun/SanskritLexicography/pull/986) correction — `subagent_tokens` is a legacy misnomer for the sum of the token fields ([`call_reservation.py:92`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L92)), and the real per-call charge is **cache re-creation**. The recommendation is unchanged; the lever sharpens from "cut per-call overhead" to "stop re-creating the cache on every call". The audit ping corroborates it independently on a different call class: priced at list rates it reproduces the ledger to the fourth decimal (**$0.3456** vs recorded **$0.3456318**), with cache creation at **87.6 %** of the cost of asking for one word — a charge that is entirely payload-independent, so no call shape can avoid it.

## [1.122.0] - 2026-08-02

### Fixed
- **Correction to 1.121.0, and the actionable cost finding it was hiding (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** 1.121.0 reported "199 370 **subagent** tokens" for a single-fragment heal call, implying subagent scaffolding. That was a misreading and it pointed at the wrong remedy — `call_reservation.py:92` sets `subagent_tokens = sum(values.values())`, i.e. the **sum of the other four token fields** under a legacy misnomer (`economy_ledger.py:35-37` already documents it as "the blunt totalTokens"). **No subagents are involved.** The true composition: **every call re-creates 56–68 k tokens of cache at the premium write rate, ~71 % of the call's cost** (`g1`: cache_creation 63 860 × $6/M = $0.383 of $0.540, reproducing the recorded `0.5399832` exactly). The framework prompt is written to cache per invocation instead of amortised — `g2`/`g6` read only ~35.6 k while still creating ~56 k. Because writing ~60 k tokens also costs wall-clock, this is the one lever that attacks **both** the 4.7× cost overrun and the 180 s timeout wall without touching the `"NOTHING runs past 3 min (MG)"` ruling. Table: [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md); tracking [#983](https://github.com/gasyoun/SanskritLexicography/issues/983).

## [1.123.0] - 2026-08-02

### Fixed
- **Content-mass promote gate + one store serialization (H2153, 02-08-2026, Fable 5 `claude-fable-5`):** closes [#977](https://github.com/gasyoun/SanskritLexicography/issues/977) (H2025 audit gap G7). Forensics first: the "1.29 MB shrink at identical row count" was **pure serializer formatting, no content loss** — [`nws_ls_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py) (H1809, 29-07) rewrote the whole store with compact separators after taking `h1809.bak`, and a spaced-family writer flipped it back on 02-08 (canonical per-row compare: 11,489/11,603 rows byte-identical, 114 rows legitimate `ru`/`de` evolution, +168 chars mass, 0 rows lost). Fixes: (1) `refuse_content_mass_shrink` — a serializer-independent character-mass gate over the content fields (10% bound; batch lane refuses outright, single lane honors `--force`) now backs the row-count guard in both promote lanes; (2) the two compact-separator writers (`nws_ls_markup`, `backfill_tn_residue`) converge on the house spaced serialization, ending the ~1.3 MB formatting flip-flop; (3) `nws_ls_markup` — an 18th unlocked mutator the H2146 census missed — now writes through the locked `store_write` writer (its old text-mode backup copy also CRLF-translated on Windows). Selftests: `window_selftest` 198/198, `promote_final_cards --selftest` with mass-gate fixtures, `backfill_tn_residue_selftest` green.

## [1.121.0] - 2026-08-02

### Added
- **`src/pilot/reservation_timeline.py` — difference the ledger's `time_ns` stamps (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** H2056 Q2 noted `call_reservation.py` persists wall stamps that nothing differences. That gap is load-bearing, because an unevaluable call finalizes through `unevaluable_telemetry()` with no `duration_ms` at all — so its duration exists nowhere else, and "hung to the ceiling" cannot be told from "failed fast". Read-only reporter over an existing ledger; zero paid calls.

### Fixed
- *(diagnosis, no code change)* **medium50 w1 aborted — the heal lane cannot finish inside its own 3-minute ceiling (02-08-2026, Opus 5 1M `claude-opus-5[1m]`):** first paid run since 25-07 produced **zero cards** in 16 calls. Differencing the stamps put **12 of 16 calls at 180 04x–180 23x ms**, i.e. `HARD_TIMEOUT_MS = 180000` hit to the millisecond — a hard-timeout wall, not the §270 rate-limit hang and not content failure. It cannot be tuned at the group level: heal groups are already at the floor (six of `nakzatra`'s eight hold a **single fragment**) and single-fragment calls still time out, because one fragment's heal call burns **199 370 subagent tokens**. Successful calls ran 120.4→164.3 s, i.e. 67 %→**91 %** of budget, so the margin is gone and shrinking. Recorded `$2.1543` is a **floor** ([#949](https://github.com/gasyoun/SanskritLexicography/issues/949)) — the 12 dead calls burned real compute and contributed 0. Measured **~$0.53/call vs the $0.113** `perf_preflight` prices with (4.7×). Raising the ceiling is a human decision: `HARD_TIMEOUT_MS` carries the standing in-code ruling `"NOTHING runs past 3 min (MG)"` (R4/C-15). Table: [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md).

## [1.120.0] - 2026-08-02

### Fixed
- **Overlay-preserving promote + store-writer lock discipline (H2146, 02-08-2026, Fable 5 `claude-fable-5`):** closes the two [integrity] exposures from the H2025 audit ([#976](https://github.com/gasyoun/SanskritLexicography/issues/976), FINDINGS §513). (1) `merge_store_rows` and the full-rebuild (supersede) path now PRESERVE human-touched store rows — named `reviewer`, non-`ai_*` `review_status`, or an `editorial_decision*` stamp — refusing machine replacement unless the new explicit `--override-reviewed` is passed; the coordinator batch lane fails the bundle loudly on a protected subcard; the clean-subset (`ready_partial`) lane preserves unconditionally. (2) All 17 non-promote store writers (9 `annotate_*`, `backfill_tn_residue`, `mark_reconstructed_headwords`, `ru_style_sweep`, `apply_editorial_decisions`, `repair_h178_da_cards`, 3 pilot `fix_*`) now write through the new shared [`src/store_write.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_write.py) `locked_store_rewrite` — `PromoteClaim` held across the read-guard-write window + unique fsynced backup + atomic LF-only replace — ending the last-writer-wins seam against a concurrent promote (7 of them previously rewrote the store IN PLACE with a fixed backup name). Selftests: `window_selftest` 198/198 (incl. parity ledger re-derived, INTENTIONAL-DIVERGENCE stands, 0 language-keyed tokens in the diff), `promote_final_cards --selftest` with new overlay fixtures (approved/needs_review/editorial each protect; override lands; siblings still merge; `ClaimBusy` under a held claim), `store_write --selftest`, `promote_en --selftest`.

## [1.119.0] - 2026-08-01

### Added
- **First decomposed c4 probe readings, and c4 auth restored (01-08-2026, Opus 5 1M `claude-opus-5[1m]`):** the H2095 `duration_api_ms` instrumentation produced its first rows ever — warm-up wall 39 437 ms / API **21 171** ms, measured wall 50 336 ms / API **27 557** ms, so ~45 % of each wall reading (18.3 s / 22.8 s) is in-CLI scaffolding rather than route time. Both API readings clear the stricter 30 000 ms bar the `/pwg-live-gate` text names, so the gate did not need the widened 65 000 ms ceiling — an independent measurement of the same 30 s-vs-65 s divergence the H2025 audit reports below. Not a masked rate-limit, since both calls returned real envelopes where [FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) says a throttled CLI hangs. Evidence toward [#946](https://github.com/gasyoun/SanskritLexicography/issues/946)/H2138 but **not** its ≥5 paired readings (n=1 measured, no same-moment quota check). Separately, `claude auth status` on c4 now returns `loggedIn: true` / Max — the HTTP 403 that stopped the paid lane on 25-07-2026 is **cleared**. Table: [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md). Raw rows are gitignored (`.gitignore:67`), so that table is the only committed copy.

## [1.118.0] - 2026-08-01

### Added
- **H2025 Fable dual-run pipeline audit of the PWG->RU money lane (01-08-2026, Fable 5 `claude-fable-5`):** full `/pipeline-audit` with mandatory Phase 2b money checks at rev `b4db4259`, dual-compared against the same-day Grok 4.5 (`grok-4.5`) lane (H2089/PR #960 confirmed shipped). Headline residuals: the FINDINGS-hub overlay-wipe class is still live in `merge_store_rows` + supersede mode with 5 human-reviewed store rows exposed; 13 non-promote store mutators bypass `PromoteClaim`; cost/call ceilings default to `None` and pass when unset; the live-gate GO is never consumed by code (canary half prose-only, skill states the reverted 30 s policy vs the enforced 65 s); a scheduler swallow can dispatch a duplicate paid window; a 1.29 MB store content change passed the row-count-only delta gate invisibly. Memo with 10 ranked gap specs: [`PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026.md`](PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026.md).

## [1.117.0] - 2026-08-01

### Added
- **H1702 Grok override dual-run verify (01-08-2026, Grok 4.5 `grok-4.5`):** independent re-measure of the shipped D4 boundary-wrap pipeline against the live store — residual **1,109** with **byte-identical** ineligible breakdown vs the Sonnet report; dry-run eligible **0** (no store rewrite); selftest **198/198**, pytest **96/96**. Net-new probe only: `〉`/fullwidth-paren normalize would unlock **63** residual rows (not applied; needs precision bar). Report: [`pwg_ru/H1702_GROK_OVERRIDE_DUAL_RUN_VERIFY_2026-08-01.md`](pwg_ru/H1702_GROK_OVERRIDE_DUAL_RUN_VERIFY_2026-08-01.md).
- **Full Zaliznyak a–f mobility on the stress slot (H2103, Grok 4.5 `grok-4.5`, 01-08-2026):** citation-only `a`/`b` replaced by Whitney matrix schemes (`c` fully mobile monosyllables, `d` weakest-mobile -ant/-an/añc, `f` lexical irregulars). Rebuild: `python src/reverse_index.py --build`. Selftest covers c/d/f fixtures.

### Fixed — probe ceiling provenance: one table, one name per value (H2118, issue #946, 01-08-2026, Opus 5 `claude-opus-5[1m]`)

**The `production_v1` token had been re-pointed instead of bumped, and there were THREE
hard-coded copies of the ceiling, not two.** `probe_log.POLICIES` said 30 000 while
`max_account_orchestrator` and `coordinator` both said 65 000 — the third copy kept in step by a
comment rather than by code. A 50 000 ms reading **passed** `live_probe` and **failed**
`verdict_for()`, with both stamping the row `production_v1`.

- [`probe_log.POLICIES`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py) is now the **single source of truth**, with a new
  `ceiling_for()` accessor and `CURRENT_POLICY`. `max_account_orchestrator` and `coordinator`
  **derive**; nothing hard-codes a probe ceiling anywhere else. The old objection — "coordinator
  must not import the orchestrator" — is satisfied: it imports `probe_log`, a stdlib-only leaf.
- **`production_v1` frozen at 30 000** (rows stamped with it were genuinely judged there; moving
  it would retroactively falsify them). **`production_v2` = 65 000** added and stamped by the live
  gates. One policy name per ceiling value, pinned in `max_account_orchestrator_selftest`.
- H2095's deliberate divergence pin — which asserted the two ceilings *disagree* and fired the
  moment they were reconciled — has done its job and is **replaced**, not deleted, by pins on the
  derivation itself plus a no-two-names-share-a-ceiling guard.
- Receipts stamped `production_v1` are now rejected by `coordinator` — correct fail-closed
  behaviour (a receipt judged at 30 000 must not authorise dispatch at 65 000); receipts expire
  after 6 h regardless.

### Not changed — the ceiling VALUE (H2118)

`PROBE_LATENCY_CEILING_MS` remains **65 000 ms and was not re-derived**. The §270 quota check
that makes a reading trustworthy needs a credential read the harness classifier denied, so **zero
paid calls were made** and no ceiling is proposed. Measured while there:
**not one probe row in the tree carries `duration_api_ms`** — the H2095 instrumentation has never
produced a row — and of the 13 historical c4 rows only 5 are `success`, **three of which exceed
the 65 000 ceiling they were used to justify**. Report:
[H2118_PROBE_CEILING_PROVENANCE_2026-08-01.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2118/H2118_PROBE_CEILING_PROVENANCE_2026-08-01.md).
Residual: [H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md).
Gates: `window_selftest` **198/198**, `max_account_orchestrator_selftest` PASS,
`execution_contract_selftest` PASS; LANG_PARITY 6 entries re-derived, SHARED stands.

## [1.116.0] - 2026-08-01

### Added — offline Sonnet-tier batch (H2005 + glyph sample + gloss_lang, 01-08-2026, Grok 4.5 `grok-4.5`)

- **H2005:** RU article render substitutes `ed. Bomb.` → «Бомбейская ред.» inside
  `<ls>` (standalone + embedded) without rewriting the store or breaking
  `pwg_sources.source_key()` / href resolution. DE/EN unchanged.
  [`build_article_site._ls_visible_display`](src/pilot/build_article_site.py);
  pin [`ls_enrichment_selftest.test_h2005_ed_bomb_ru_display_not_resolve`](src/pilot/ls_enrichment_selftest.py).
- **Glyph quarantine sample (report only):** stratified n=200 from the 10 881-row
  quarantine; 200/200 `segmentation_flag` — not a RU-quality fail label.
  [`src/sample_glyph_quarantine.py`](src/sample_glyph_quarantine.py);
  [report](pwg_ru/H_GLYPH_QUARANTINE_SAMPLE_REPORT_20260801.md);
  [sample JSON](reports/pwg_ru_glyph_quarantine_sample_2026-08-01.json).
- **gloss_lang §464:** `english_content` no longer fires on a single weak marker
  (`a`/`an`/`of`/`and`/`or`/`with`/`as`/`one`/`war`); strong markers or dual `-ing`
  still mask as EN. Pins in `pwg_mask --selftest`.

## [1.115.0] - 2026-08-01

### Fixed — the last four H2056 integrity issues (H2095, issues #946 · #949 · #950 · #956, 01-08-2026, Opus 5 `claude-opus-5[1m]`)

**[#949](https://github.com/gasyoun/SanskritLexicography/issues/949) — `budget_spent` was published without the qualifier that makes it readable.**
A hung call finalizes with `unevaluable_telemetry()` (all-zero token fields), so it adds 0 to the
total: a run that burned real money on hung calls could publish `budget_spent: 0.0` with nothing in
the operator-facing artifact to say the number is a **floor**, not the cost. `summary()` now carries
`cost_evaluable`, `unevaluable_calls` and `pending_calls`, all already present in the ledger. The
`STOP_COST_UNEVALUABLE` gate arms only when a `--budget` cap is set, so on an uncapped run this
marker is the *only* signal — surfaced, but the stop policy itself deliberately unchanged.

**[#946](https://github.com/gasyoun/SanskritLexicography/issues/946) — a probe row could not be read standalone.**
Rows now record `latency_ceiling_ms`, the ceiling that actually judged them. The `policy` token was
never sufficient provenance, and this pass found why it is worse than reported: `PROBE_POLICY`
stayed `production_v1` across 30 000 → 33 000 → 65 000 on 31-07, **and
[`probe_log.POLICIES`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py)
still maps that same token to 30 000 ms** — so `probe_log.verdict_for()` and `live_probe` are two
mechanical gates sharing one policy name while disagreeing by 2.2×. A 50 000 ms reading passes one
and fails the other. **Deliberately not reconciled:** choosing a ceiling is the human call H2056
reserved, and 65 000 is itself suspect. The divergence is now documented at the table and pinned by
a selftest that will fail the moment someone unifies them, so it cannot be closed silently.

**[#950](https://github.com/gasyoun/SanskritLexicography/issues/950) — settled, no constant moved.**
The claim was that the healthy cost gate is calibrated below the real per-call floor
(`~90 485` tokens / `~$0.29` per call). Resolved from the committed H963 record, which states
`calls | 2`: **90 485 is a two-call aggregate** (~45 243/call) — the premise was wrong — while
`$0.5848 ÷ 2 ≈ $0.29`/call is correct. The comparison is category-confused regardless:
`PER_AGENT_TOKENS_HEALTHY` prices a *translation agent* in a batched lane (59 250 tok/agent c4
canary, ~60K/agent `nominal_w1_100small` — two independent sources), while those figures come from
a *readiness probe* dominated by CLI cache-creation scaffolding. Re-calibrating a spend gate off a
single 2-call sample would be worse than the fiction it replaced. The arithmetic is recorded so it
is not re-derived.

**[#956](https://github.com/gasyoun/SanskritLexicography/issues/956) — the EN twin of #947, and it was real.**
The question #947 left open is now answered by enumeration: **6 of the 11 EN `HARD` flags fire on
absence** (`MISSING-EN`, `MISSING-SENSE`, `LS-LOSS`, `SAN-LOSS`, `AB-LOSS`, `IS-LOSS`) — `SAN-LOSS`
being literally the gate named in #947's RU harm — so a card left incomplete by a dead call did land
in `requeue_defect` and the same H304 fsha denylist. `audit_window_en` now reads the same
`partial_cause_infra` marker the worker stamps language-agnostically, at **finer granularity than the
RU fix**: only absence-bearing flags are exempted, so `ANCHOR-*`, `SENSE-DUPE` and `DUP` still make a
partial card a defect — the EN mirror of `fidelity_nulls` overriding on RU.

`window_selftest` 196/196, pilot suite green, LANG_PARITY 89 entries with 45 re-derived (including a
first-ever note on `h1339_measurement_integrity`, which owns both files #946/#950 touched).

### Fixed — a dead heal call no longer reports itself as a content verdict (H2091, issue #948, 01-08-2026, Opus 5 `claude-opus-5[1m]`)

`_selfheal_stop_reason` tested only for `budget_exceeded:*`, so a `timeout` fell through to
`selfheal-nothing-resolved` — a **content** verdict, and the only per-key cause an operator or any
downstream tool ever sees (`row['error']`, `summary['failures'][key]`,
`report['failure_reasons'][key]`). The typed reason survived only on the discarded
`<key>_f<i>` fragment keys.

H2a's argument was never budget-specific: a heal lane that died because the **call** died is a
transient infrastructure stop whatever killed it. The test is now **ranked**, not flat:

1. the first `budget_exceeded:*` — H2a's invariant, deliberately unchanged;
2. failing that, the first other typed infrastructure reason (`is_infra_failure`) — new;
3. failing that, the historical `selfheal-nothing-resolved`.

**The ranking is the fix, not an implementation detail.** A flat "first infra wins" lets a
low-index `timeout` mask a budget stop and silently repeals H2a — caught by
`test_h2a_precedence_is_deterministic_and_budget_stays_observable` during this work, and now pinned
from both directions.

**Q3-F3 of the same issue needed no change and was verified rather than assumed.** The whole-card
lane bisects a failed batch *on purpose* — "isolate the slow one", and the JS twin does the same
deliberately — so bisecting after a plain timeout is correct. It was only wrong when the timeout was
really the account refusing, and H2063 already closed that by promoting an account-level cause to
`HardFailure`, which `resolve_group` does not catch. Now pinned on a **multi-key** batch (where the
bisect is actually reachable): an account refusal stops at exactly **one** call, while a plain
timeout still bisects.

Genuine content failures keep `selfheal-nothing-resolved` exactly as before — that string must keep
meaning "the model answered and nothing usable came back". LANG_PARITY 89 entries with 5 re-derived.

### Added — `duration_api_ms` is captured, so a latency reading can be decomposed (H2079, issue #945, 01-08-2026, Opus 5 `claude-opus-5[1m]`)

The measurement-integrity fix from the [H2056 review](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md),
and the one that makes the contaminated c4 series re-interpretable going forward.

Every latency gate in the paid path measured **wall clock**. Wall clock cannot distinguish a slow
route from a CLI retrying internally against a rate limit (it hangs rather than reporting 429 —
[FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). The discriminator,
`duration_api_ms`, was **already in the result envelope, already parsed, and discarded one line
away** — parsed nowhere in `src/*.py`. That is why the 15-07 (52 815 ms), 16-07 (104 870 ms) and
31-07 (78 415 ms) readings are unusable as route evidence, why the `PROBE_LATENCY_CEILING_MS` raise
30 000 → 65 000 ms was calibrated partly against backoff, and why a "~65 s CLI startup" claim was
published and then retracted rather than tested. Recommended in prose on 16-07 in the H963 report;
never implemented until now.

- [`telemetry_from_cli_wrapper`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/call_reservation.py#L52)
  now carries `duration_ms` / `duration_api_ms` into the durable reservation ledger, so every paid
  call's API time is persisted per call.
- `live_probe` emits `duration_api_ms` and `api_gap_ms` (wall − API) beside `elapsed_ms`, added to
  `run_observability.ALLOWED`.
- `_probe_call` gained an optional `timing_out` dict — no return-arity change, so every existing
  caller and test stub is untouched.

**Recording only — nothing is gated on it.** `elapsed_ms` remains the number the ceiling tests, and
no threshold moved: H2056 was explicit that re-deriving the suspect ceiling needs readings paired
with a same-moment quota check, which is separate work ([#946](https://github.com/gasyoun/SanskritLexicography/issues/946)).

**Backward compatibility is load-bearing and pinned.** The fields are **omitted when absent**, never
written as an explicit `None`: `_read()` re-validates every stored item and `finalize()` compares an
already-finalized item against a freshly normalized one, so a pre-H2079 ledger must normalize to
exactly the bytes it already holds. A malformed duration never demotes `cost_evaluable` —
evaluability is a statement about cost. Both properties are asserted, along with the ledger
round-trip and the absent-is-invisible probe row. `window_selftest` 195/195, pilot suite green,
LANG_PARITY 89 entries with 3 re-derived.

### Fixed — a quota hang no longer denylists a healthy card or discards its fragments' TM (H2077, issue #947, 01-08-2026, Opus 5 `claude-opus-5[1m]`)

The worst harm found by the [H2056 review](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md),
and the one with **permanent** consequences.

[`classify_harness_requeues`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py#L475)
split transient-vs-defect on output **shape** alone — `defect = (gate_set - null_set) | fidelity_nulls`.
A null key was exempt ("it fails coverage only because it is absent"), but a **partial** key was not,
even though the absent part is absent for the same reason. So a card left incomplete because its heal
call *died* (timeout, budget stop, quota hang) was filed as a content defect, and via
`requeue_defect` that (a) denylisted a **healthy** card and (b) discarded the `frag_prov` fshas of
the fragments that **did** translate — paid-for TM, permanently — and (c) wrote the key to
`no_pwg_residuals.jsonl` as `blocked`, the planner skip-list. All three consume the one
`requeue_defect` set, so all three are fixed at one point.

**The fix makes the split evidence-based instead of shape-based.** A partial card recorded *which*
fragments were missing but never *why*; it now also records **why**. `headless_worker._partial_cause()`
derives a typed cause from that card's own fragments' recorded call failures (same deterministic
ascending-numeric-index precedence as `_selfheal_stop_reason`), stamps `partial_cause` +
`partial_cause_infra`, and the audit subtracts explicitly-infrastructure partials from the defect lane.

Deliberately narrow — `INFRA_FAILURE_REASONS` is a **closed** list (timeout · budget_exceeded ·
rate_limit · authentication · connection). A partial card with a *content* cause, or with **no**
recorded cause (older wf files), behaves exactly as before, and `fidelity_nulls` still overrides the
exemption. Over-exempting would let a genuinely defective card back into the cheap-re-run lane — the
"stubborn null" loop the fidelity rule exists to stop.

Pinned by `test_h2077_947_infra_partial_is_not_a_content_defect`, which fixes all four quadrants
(infra→transient · content→defect · no-cause→defect · fidelity-override→defect), asserts the good
fragment's fsha stays out of the denylist, and pins the legacy set-shaped caller as unchanged.
`window_selftest` 195/195, pilot suite green, LANG_PARITY 89 entries with 44 re-derived.

**Surfaced, not silently assumed:** `audit_window_en.py` is a separate auditor with no partial-card
model at all, so the same defect cannot arise there in that form — but whether an EN card can be
hard-flagged for content a dead call never produced is a different question, filed as
[#956](https://github.com/gasyoun/SanskritLexicography/issues/956) rather than guessed at here.

### Fixed — a rate-limited account no longer looks like a local timeout (H2063, issues #943 + #944, 01-08-2026, Opus 5 `claude-opus-5[1m]`)

The first two fixes off the [H2056 review](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md).
A rate-limited Claude CLI does not return 429 — it hangs until our wall ceiling kills it
([Uprava FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)), and the pipeline
had no way to tell that apart from a slow call.

**[#943](https://github.com/gasyoun/SanskritLexicography/issues/943) — the signal was destroyed before any handler saw it.**
[`proc_tree.run_tree_kill`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py#L270)
drained the tree-killed child's stdout/stderr into locals and re-raised the original
`TimeoutExpired` carrying only `cleanup_trouble`, so the provider's own message died with the
frame. It is now attached to the exception (`.output`/`.stderr`). This was the **root blocker**:
wiring a classifier into either handler first would have classified an empty string.

**[#944](https://github.com/gasyoun/SanskritLexicography/issues/944) — a hung 429 was recorded as `done`/`success`.**
Both timeout handlers hardcoded `'timeout'`. New `classify_timeout()` reads the now-attached text
and promotes an **account-level** cause (429/401) to the *existing* `HardFailure` path, so the
worker exits 21, the run stops instead of spending into a locked account, and the orchestrator's
long-standing `is_rate_limited` → `park` + `requeue_rate_limited` finally fires. The probe in
[`max_account_orchestrator._probe_call`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py#L1182)
gets the same treatment — it was the only exit that skipped `_probe_err_class`.

Deliberately **narrower than `classify_process`**: only account-level causes are promoted. A
`connection`-looking string in a killed call stays `'timeout'`, because the call really did exceed
the ceiling — so a slow window is never mistaken for a quota stall and falsely parked.

Pinned by three new `headless_worker_selftest` cases (output actually attached; a hung 429 exits 21
and would park; a non-account hang stays a plain timeout). Full pilot gate green, `window_selftest`
194/194, LANG_PARITY 89 entries re-derived with no drift. **No ceiling was changed** — `#944`'s open
question (is 180 s right, should repeated `kill_timeouts` park?) is left for a human, per H2056.

### Added — H2056 call/retry/classification path review (01-08-2026, Opus 5 `claude-opus-5[1m]`)

[`pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2056/H2056_CALL_PATH_REVIEW_2026-08.md)
— an adversarially-verified defect report for the paid call path, commissioned by
[H2056](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2056-Opus_RussianTranslation_pwg-live-gate-retry-classification-code-review_01.08.26.md)
after [Uprava FINDINGS §270](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) established by
measurement that a rate-limited Claude Code CLI **hangs instead of reporting the 429**.

Method: a 22-agent Workflow (1 map · 5 review · 15 verify · 1 synthesise), every finding put through
three refute-primed lenses (correctness / does-it-reproduce / already-handled-elsewhere) with
majority-refute killing it. **24 findings raised, 13 survived, 11 refuted** — the refuted ones are
listed with their refutations, so the review is auditable rather than self-flattering.

Headline result: the rate-limit signal is destroyed **below** the two handlers that were suspected.
[`proc_tree.py:270`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py#L270)
drains the killed CLI's stdout/stderr into locals and re-raises without attaching them, so both
`except subprocess.TimeoutExpired` handlers hardcode `'timeout'` over text that no longer exists.
All sixteen time gates in the path are wall-clock; `duration_api_ms` — the one field that separates
route health from in-CLI backoff — is parsed nowhere in `src/*.py`. Worst permanent harm: a quota
hang can denylist a *healthy* card and discard its correctly-translated fragments' TM
([`audit_window.py:484`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py#L484)).

Review-only by construction: **no fixes applied, no ceiling changed, no gate re-run, zero paid calls.**
Eleven findings carry `data_integrity=true` and are filed as `[integrity]` issues.

### Changed — H1682 abbrev rules sheet content remake v3 (H2047, 31-07-2026, Grok 4.5 `grok-4.5` override for Opus comparison)

Regenerates `review/h1682_abbrev_rules_sheet.html` (sheet_id `h1682_abbrev_rules`,
gitignored + lock re-stamped) so cards meet the MG 31-07 content bar:

- **Cases stay Latin** (LOCKED): `build_h1303_abbrev_sheet.py` O overlay no longer
  proposes `Acc.→акк.` / `Loc.→лок.` etc.; proposed visible form is the Latin case
  itself; section citation + rule card frame stay-Latin ratification (tooltip/legend
  only for full Latin + RU case names).
- **Expansion + frequency + case-fold families** on rule cards (`caus.`/`Caus.` under
  one family with separate `n=`).
- **Up to 5 clickable KWIC** examples per bulk family / residue token (kosha colocation
  hrefs via `pwg_entry_href`).
- **Emitter hygiene:** `note_min_height_px=88` via `standard_config`; `mark_cyrillic`
  only on strings under judgment (not whole chrome).
- Residue (`geder.`, `d.`, …) framed as leave-original + tooltip, not invent RU.

Generators: `src/build_h1682_abbrev_rules_sheet.py`, `src/h1682_abbrev_collapse.py`,
`src/build_h1303_abbrev_sheet.py` (case O + `dopp.` note). Reproduce:
`python src/build_h1682_abbrev_rules_sheet.py` from `RussianTranslation/` (needs local
store). **Do not vote** until a human re-opens the sheet and confirms the case section.

## [1.111.5] - 2026-07-31

### Fixed — checkpoints and status files were atomic but never flushed to disk (H3 / H1940 Phase 2, 31-07-2026, Opus 5 `claude-opus-5[1m]`)

`headless_worker.atomic_json`, `bounded_supervisor._write_checkpoint` and
`cohort_engine._save_checkpoint` all wrote a temp file and `os.replace`d it — atomic, but
never durable. A power loss between the write and the OS flush leaves a valid-looking
truncated or empty file: for the checkpoint that means the crash-resume authority is gone
and completed work is re-audited; for the status sidecar it means the orchestrator reads a
window that never finished. All three now `flush()` + `os.fsync(f.fileno())` before the
replace, matching the durability `window_common.atomic_write_text` has always had.

Landed **inline rather than routed through the shared writer**, which is what the original
sketch proposed, because routing was measured and is not byte-neutral:
`atomic_write_text` passes no `newline=` to `os.fdopen`, so it emits CRLF on Windows and
drops the trailing newline (246 vs 232 bytes on the probe payload, diverging at offset 1).
Those bytes are hash-bound, and the same writer also emits the execution manifest whose
digest is `manifest_sha256` — so pinning the newline there is a hash migration across
gate-pinned artifacts, not a durability fix. The measurement is committed as
`src/pilot/h3_byte_probe.py` and the residual is recorded as Uprava FINDINGS §262.

### Fixed — `claim` accepted a duplicate `--lease-id` and persisted an unreachable second lease (H4 / H1940 Phase 2, 31-07-2026, Opus 5 `claude-opus-5[1m]`)

`coordinator.register_prepared_lease` has always refused a lease id that already exists;
`claim` did not, so `--lease-id <existing>` appended a *second* lease under the same id.
Because every lookup goes through `lease_by_id`, which returns the first match, that second
lease was unreachable but still persisted — it consumed a preparation slot, appeared in
`active_targets` and reserved-key scans, and broke the single-id CAS assumption the rest of
the coordinator is built on. `claim` now carries the same existence guard, placed before the
artifact-dir creation, the lease append and the state save, so a refused claim leaves
nothing behind. The guard also covers the auto-generated id, since `make_lease_id` embeds a
second-resolution timestamp and the pid and a collision there would itself be a duplicate;
two claims for the same *target* still get distinct ids and are unaffected.

### Changed — the residual ledger re-read itself once per key (O(n²) / H1940 Phase 2, 31-07-2026, Opus 5 `claude-opus-5[1m]`)

`append_residual` re-read the entire append-only ledger on every call, making
`append_from_audit_report` O(keys × ledger bytes) on a path that runs per audited window
against a file that only grows. It now accepts an optional pre-read snapshot; omitted, the
behaviour is exactly as before. On a successful append the new row is written back into the
snapshot, so batched dedupe stays identical to the per-call re-read — a batch containing the
same key twice still writes it once. `backfill_documented` had the same shape and the same
fix. Measured: a 12-key batch went from 13 ledger reads to 1.

### Fixed — a stalled window burned its whole iteration ceiling at full speed instead of stopping (H7 / H1940 Phase 2, 31-07-2026, Opus 5 `claude-opus-5[1m]`)

`bounded_staged_run.make_run_window`'s per-lease drain loop had no idle handling. When a
pass changed nothing — the standard case being a pending job that no admitted account can
claim — the loop simply went round again immediately: re-dispatch, re-record, and (unless
`--stop-before-promote`) another `promote-ready` subprocess, with no pause, until
`max_drain_iterations` (default **1000**) was exhausted. The run then died with
`exceeded 1000 drain iterations`, a message naming a counter rather than the stall, after
spending up to a thousand pointless subprocess spawns getting there.

The loop now computes a per-pass progress signature — `(pending, done_unrecorded, done)` —
and when it is unchanged from the previous pass it sleeps `DRAIN_IDLE_POLL_SECONDS` (3 s,
the same bound `max_account_orchestrator.STAGED_RUN_IDLE_POLL_SECONDS` already uses for the
staged C4 backstop) and counts the pass. After `DRAIN_NO_PROGRESS_PASSES` (20) *consecutive*
dead passes it fails closed, naming the lease and all three counters. Notes on the shape:

- The counter is **consecutive, not cumulative** — any real forward progress resets it, so a
  long window that stalls, recovers and stalls again still completes.
- `done` (total) is in the signature, not just the unrecorded slice: a requeue that lands a
  new pending job in the same pass another completes leaves the other two counters equal,
  and would otherwise be misread as a stall.
- The check sits *ahead* of the `if pending:` branch, so it also covers a done-but-
  unrecordable job — a stall shape the staged C4 backstop, guarded inside its own pending
  branch, does not catch. It sits *after* the existing clean-completion `break`, so the
  H1386 C2 resume path still breaks on its first pass and never reaches the backstop.
- `max_drain_iterations` is untouched and still bounds total passes; the new cap is a
  separate, earlier, more specific stop, deliberately not derived from it (that ceiling
  legitimately covers many *productive* passes).

Both stall shapes were measured against pre-H7 `origin/master` with the iteration ceiling
lowered to 30 for tractability: master ran the full 30 passes with **zero** polls and died on
the iteration count; the fixed loop stops after 20 passes and 19 polls, naming the stall.

### Fixed — a translate-budget retry erased the card's actual content diagnosis (H2b / H1940 Phase 2, 31-07-2026, OpenAI GPT-5.6 Sol `openrouter/openai/gpt-5.6-sol`, [PR #906](https://github.com/gasyoun/SanskritLexicography/pull/906), merged `9a5bddbc`)

`headless_worker.resolve_group` used the same unconditional failure-note write for every
whole-card call error. If attempt 1 returned a card-specific rejection and the next retry
was refused by the translate-agent ceiling, the blanket `budget_exceeded:translate` note
replaced the useful diagnosis on every pending key. Budget notes now preserve an existing
per-key note; non-budget errors retain the prior last-error behavior. A real two-attempt
selftest is RED on pre-H2b master (`translation-fidelity-reject` was overwritten) and GREEN
with the fix.

### Fixed — a malformed manifest crashed the worker with no status file, and the orchestrator retried it (H1 / H1940 Phase 2, 30-07-2026)

`headless_worker main()` read, hashed and decoded the execution manifest *before* entering
its configuration `try`. So the three ways that read can fail — the file is missing or
unreadable (`OSError`), the bytes are not UTF-8, the JSON is invalid — escaped `main()` as
a bare traceback. No status file was written at all. Two more escaped from *inside* the
try, because `KeyError` and `TypeError` were absent from its `except` tuple: a manifest
that decodes and passes `validate_manifest` can still be missing a section the executor
subscripts directly, or carry a scalar where a list is required.

Fixing the worker alone would not have stopped the retries, and the first draft of this
entry wrongly claimed it did. Measured against `origin/master`, the orchestrator had three
separate problems of its own:

- `max_account_orchestrator.run_claimed` hashes and `json.load`s the manifest **before**
  launching the worker, unguarded — so a missing file (`FileNotFoundError` out of
  `sha256_path`) or invalid JSON escaped `run_claimed` entirely. The worker's new status
  path was never even reached. Worse, the escaping exception left the job stuck
  `in_progress`, and `_claim_tx` refuses an account that already owns an `in_progress`
  row — so one unreadable manifest wedged the whole account.
- `fail_or_retry` decides purely on `attempts < max_attempts`, ignoring
  `failure_class` entirely. A `configuration` verdict — the worker's, or the
  orchestrator's own from `validate_profile`/preflight — went straight back to
  `pending`. Verified directly: on master a worker `configuration` result with
  `attempts=1, max_attempts=3` returns `'pending'`.
- The windows100 readiness report's hard-failure set omitted `configuration`, so a job
  that died on one would have vanished from the report with nothing saying why.

So H1 covers both halves.

**Worker side.**

- **The read is inside the try.** `open`/`read`/`sha256`/`json.loads` moved in, so all
  five shapes land on the existing `classification: configuration`, exit code 2, status
  written. `json.JSONDecodeError` and `UnicodeDecodeError` are already `ValueError`
  subclasses, so moving them in was sufficient for those; `KeyError` and `TypeError` were
  added explicitly.
- **The hash is never fabricated, and never discarded.** `manifest_hash` is pre-bound to
  `None` — which is what stops the move from introducing an `UnboundLocalError` at the
  unconditional status write, and what keeps a manifest whose bytes were never read from
  being attested with a hash. `null` is not a new convention: it is the absent-hash shape
  `bounded_staged_run` (`headless.get('manifest_sha256')`) and
  `max_account_orchestrator.emit_call_events` (`or 'call'`) already handle. When bytes
  *were* read, their hash is retained exactly as before, so an invalid-JSON status still
  carries real evidence of precisely what was rejected.
- **The new error details name their type.** `str(KeyError('inputs'))` is `"'inputs'"` —
  a bare key naming no cause. `KeyError`/`TypeError` are therefore qualified with the
  exception type. The pre-H1 types keep their exact wording deliberately:
  `max_account_orchestrator` feeds `status['error']` into `parse_reset` on the rate-limit
  path, so that text is not free to reword.

**Orchestrator side.** `run_claimed`'s pre-launch hash + decode is now guarded, and a new
`fail_terminal()` ends a job on the attempt that produced a **deterministic** verdict —
`configuration` or `manifest_drift`, the classes whose outcome cannot change on a re-run.
It is a separate entry point rather than a branch inside `fail_or_retry` on purpose:
transient classes (`process`, `timeout`, `result_drift`, an unclassified failure) keep
their retry budget byte-for-byte, and a single shared function deciding by class is the
shape in which that is easy to regress later. `configuration` also joins the readiness
report's hard-failure set, so a job it kills is still visible there.

Successful execution, the v2 manifest seal, preflight validation, the call reservation and
profile validation are untouched and still run in the same order. Zero paid calls on every
one of these failures — both worker-side structural pins reach their exception before any
reservation or spawn, and the two pre-launch orchestrator pins assert the spawn counter is
zero rather than assuming it.

Pinned by four new `headless_worker_selftest` tests — all four verified RED against pre-H1
master, where the exception escapes and no status file exists — and four new
production-path pins in `max_account_orchestrator_selftest` driving the real
`run_claimed` with `max_attempts=3`, so a `failed` state proves the *class* ended the job
and not exhaustion. Three of those four are master-failing (missing manifest → escapes;
invalid JSON → escapes; worker `configuration` → `'pending'`). The fourth is a deliberate
**regression guard**, green on master by construction: an ordinary `process` failure must
still return to `pending`. Stated rather than rounded up to "4/4 RED".

Gates: `headless_worker_selftest` PASS, `max_account_orchestrator_selftest` PASS,
`window_selftest` 194/194, `lang_parity_check` 89 entries no drift (SHARED verdicts
re-derived against the diff, not hash-refreshed). Landed as
[PR #904](https://github.com/gasyoun/SanskritLexicography/pull/904), merged `62993b6b`.

### Fixed — one hung preflight could wedge every coordinator operation (H8 / H1940 Phase 2, 30-07-2026)

`coordinator claim` takes the global state `DirLock` and holds it for the whole claim,
including `verb_candidates()`, which shells out to `perf_preflight.py` to cost-gate the
candidate roots. That `run_cmd` carried **no timeout**. A preflight that hung — a wedged
child, a stalled read, a machine under load — therefore held the lock indefinitely, and
every other coordinator operation (`claim`, `prepare`, `record-output`, `promote`, the
dashboard) blocked behind it until the lock's TTL expired. Nothing recovered sooner,
because a live holder is correctly never reclaimed: `DirLock.stale()` requires the owner
pid to be *dead*, and the wedged process was very much alive.

The fix is the one the H1811 review specified, and no more:

- **The claim-path preflight is bounded by `PREPARE_TIMEOUT_SECONDS`** — the same constant
  the requeue-preparation preflight and harness-generation calls already use, so there is
  now one timeout policy for every `perf_preflight` invocation rather than two.
- **A timeout is a deterministic operator error, not a hang.** `subprocess.TimeoutExpired`
  becomes a `SystemExit` naming the elapsed bound and the candidate count. `subprocess.run`
  kills and reaps the child before raising, so no orphan preflight is left behind.
- **The unwind is clean by construction.** The raise happens ahead of `os.makedirs` on the
  artifact dir, `leases.append` and `save_state`, so a timed-out claim leaves no lease, no
  artifact directory, no saved state and no registry row — and the `with DirLock(...)`
  block releases the lock on the way out, immediately.

Moving the candidate computation and the store/worklist scans *out* of the lock is the
larger refactor the review flagged; it stays deferred, and is unaffected by this change.

Pinned by two new `coordinator_hardening_selftest` tests, both verified RED against
pre-H8 master: the contract pin (the claim path must receive `timeout=600`, not `None`)
and the unwind pin, which runs a **real** hanging child under a short injected timeout and
asserts bounded termination, that the child pid is dead, and that no lease / artifact /
state / registry row survives — on master that pin shows the child running to completion
*and a lease being claimed anyway*. Gates: `coordinator_hardening_selftest` PASS,
`window_selftest` 194/194, `lang_parity_check` 89 entries no drift (four SHARED verdicts
re-derived against the diff, not hash-refreshed).

### Fixed — a heal-budget stop was filed as a content defect on presplit cards (H2a / H1940 Phase 2, 30-07-2026)

When `self_heal` finished with no senses, the base key was stamped
`selfheal-nothing-resolved` unconditionally. But the *actual* cause of a starved heal lane
is recorded on the FRAGMENT keys as a typed `budget_exceeded:heal` — so a transient
infrastructure stop arrived downstream looking like a content defect, which is the wrong
lane (C-49 residual triage) and the wrong remedy: the card needs re-running with budget,
not editorial attention.

The existing H1610 `preserve=True` guard could not catch this. Preserve only protects an
*earlier* note on the base key, and a presplit card never runs a whole-card translate
attempt — so there was no earlier note, and the soft stamp was written unopposed.

- **The typed reason is propagated.** If any of this card's own fragments recorded
  `budget_exceeded:*`, the base key reports that instead of the soft stamp. Genuine
  zero-resolution and content failures (fidelity reject, missing/mismatched key, timeout)
  are untouched and still report `selfheal-nothing-resolved`.
- **The fragment-key set is exact, never a prefix.** Fragment keys are `<key>_f<index>`,
  so matching on `startswith('ab_f')` also captures `ab_foo_f0` — a *different* card's
  fragment, whose budget stop would then be misattributed. The set is derived from
  `fragment_groups[key]` directly, so that mistake is not expressible.
- **Precedence is deterministic.** Fragments are examined in ascending *numeric* index
  (`_f2` before `_f10`, which plain lexicographic order gets backwards), so with several
  failed fragments the reported reason cannot depend on set iteration order. A non-budget
  error on a lower-numbered fragment does not mask a budget stop, and the typed reason
  remains readable on the fragment key itself.

Pinned by four `headless_worker_selftest` tests. Two go RED against pre-H2a master; the
exactness pin is instead verified RED against a deliberately prefix-matching
implementation (it cannot fail on master, which never propagates at all); the fourth is a
regression guard on the preserved content path. Gates: `headless_worker_selftest` PASS,
`window_selftest` 194/194, `lang_parity_check` 89 entries no drift.

### Fixed — NWS `[diasystem, domain]` tags still translated into Russian in 34 more places after H1809 (H1903, 30-07-2026)

H1809 migrated 17 domain-slot half-translations, but its regex anchored on a Latin
diasystem in slot 1 — so a row where the diasystem was *also* mistranslated, or one using
the unbracketed `DIA , DOM >` header form, slipped through untouched. Repaired store-side
(16 more Cyrillic-tag rows restored from the `de` field, 3 rows with a dropped `>`
separator, 10 rows where a manuscript date+place had run into the domain slot — confirmed
against the raw scraped NWS card — and one gloss-bracket false-positive reformatted so it
no longer collides with the tag-detector's shape). Store-wide verification: 0
Cyrillic-valued and 0 comma/digit-bearing tag slots across all 11,603 rows. A new
write-time guard, `validate_final_card_schema.nws_tag_defects()`, rejects a future
generation run that reintroduces either defect. The compensating Cyrillic aliases in
`g5_card_render.DOMAIN_RU` (no longer reachable by anything) are retired. See
[RESULTS_LOG.md § 30-07-2026](RESULTS_LOG.md#30-07-2026--nws-tag-half-translation-store-repair-beforeafter-h1903)
and [FINDINGS §504](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md#504-the-nws-tag-layer-reaches-only-22--of-the-ru-store--a-facet-bar-over-it-is-right-but-it-is-not-the-sheets-main-axis).

### Fixed — a transient probe failure could strand cohort leases forever, silently (H9 / H1940 Phase 2, 30-07-2026)

`cohort_engine` treated a probe exception as a **durable** verdict about a profile. The
failed profile was written into the checkpoint twice over: into `failed_profiles`, and
into `probed` (the in-process marker that stops a wave re-paying the ledger for a probe
it already attempted). On resume, both came back — so the profile was never re-probed,
`_is_window_runnable` kept rejecting it, the terminal barrier skipped its leases as
"no work will ever run here", and the wave still settled `promoted`/`tm_done=True`. Its
leases were then unreachable forever: a settled wave returns immediately on every later
resume. A transient network blip during one probe was enough to lose those leases with
**no error, no warning, and no trace in the summary** — the wave reported plain success.

Two changes, both surgical:

- **A probe failure is now per-life evidence, not a durable verdict.** `failed_profiles`
  is no longer persisted at all, and only *successfully* probed profiles are written to
  `probed`. A resumed life re-probes and, when the failure really was transient,
  dispatches the leases normally. Older checkpoints carrying the key are ignored, not
  read back.
- **Settling with undispatched leases is no longer silent.** When a wave settles while
  admitted, unparked leases were never dispatched, `stop_reason` now names each one with
  its profile and cause (`probe_failed` / `budget_exhausted`), and that reason is
  persisted to the checkpoint so an operator sees it without attaching to the process.
  It is recomputed on each settle, so a life that recovers the leases clears a stale
  reason from an earlier one.

Settling itself is deliberately unchanged — promoting the clean subset is the same
partial-wave behaviour the budget path already had. What changed is that it now says so.

Pinned by `cohort_engine_selftest` pins 8 and 9, **each verified to fail against the
pre-H9 engine** — the H1811 S3 lesson that a gate which passes both ways certifies
nothing. Gates: `window_selftest` 194/194, `lang_parity_check` 89 entries no drift
(`h1437_cohort_width_offline` SHARED verdict re-derived, not rubber-stamped).

### Fixed — the audit timeout could not cancel the audit, and provenance stamps could go stale (H1957, 30-07-2026)

Two correctness defects shipped inside H1811's speed work below. Both were invisible
to CI: every gate was green with them present, and one was actively *pinned* as
correct by a selftest.

**1. The audit timeout stopped waiting without stopping the work.** H1811 S1 ran
`audit_window` in-process via `run_py_inproc` on a **daemon thread**, which breaks
that function's own documented contract — *"callers must not run two of these
concurrently (sys.argv/stdout are process-global)"*. On timeout `run_audit` returned
rc=124 while the audit kept running, so: the abandoned thread continued **writing the
very `window_status.json` / report / requeue files the caller reads next**; the
coordinator's own `sys.argv`, cwd (`run_py_inproc` chdirs) and `stdout`/`stderr`
stayed hijacked meanwhile; and `run_py_inproc`'s `finally` restored argv/cwd at an
arbitrary later moment, clobbering whatever the main thread had set since. Fixed by
running `audit_window` in a **killable subprocess** under the same timeout — the only
boundary where a timeout can actually cancel the work. The stdout-hijack is not
theoretical: while reproducing this, the reproduction script's own diagnostic output
vanished into the abandoned thread's capture buffer and only resumed once that thread
finished.

**2. `stamp()` could certify a row with a hash of code that had already changed.**
H1811 S3 memoized `component_sha` in a module-global keyed on the component's file
*patterns* — never on content — so the cache had **no invalidation at all**. In any
process outliving a source edit (a `bounded_staged_run` / `cohort_engine` wave runs
for hours) every row stamped afterwards carried the **pre-edit `<name>_sha`**: a row
claiming to have been produced by code that did not produce it, which is precisely
the claim that field exists to make. `check()`/`freeze()` stayed exact, but they read
the manifest — they cannot repair provenance already written into the store. The memo
is removed; `stamp()` always re-reads.

The selftest for #2 asserted `st2['prompt_sha'] == st['prompt_sha']` with the message
*"stamp memo must return the first hash"* — i.e. it certified stale provenance as
correct behaviour. It now asserts the opposite. The timeout test for #1 monkeypatched
`run_py_inproc` and checked only the rc=124 mapping, so it passed either way; it is
replaced by one that drives a real child which sleeps and then writes a sentinel, and
fails if the sentinel ever appears. That replacement test fails against the old
implementation, which was verified rather than assumed.

**Honest cost.** Interleaved A/B against master `3070941b` (5 alternating pairs, host
under variable load, minimum per side as the robust estimator): **audit +34.7 %**
(3.95 s → 5.32 s, the restored interpreter spawn), **store-write +24.0 %** (4.00 s →
4.96 s, `stamp()` re-hashing per promoted row), **total +15.0 %** (10.79 s → 12.41 s).
This gives back most of the speed the entry below reports. The deterministic signature
`9bd2a14297` is byte-identical across both sides, so the outputs are unchanged.
S2 (`_pilot_collect` in-process), H5 and H10 are **retained** — only S1 and S3 are
reverted. Gates: `window_selftest` **194/194**, `lang_parity_check` **89 entries, no
drift**, `pipeline_version --selftest` OK. Model: Opus 5 (`claude-opus-5[1m]`).

### Changed — binary-samāsa ruling applied to the compound adjudicator (H1918, 30-07-2026)

MG's ruling: a samāsa's vigraha is always binary (dvandva excepted, and a
dvandva is never detectable from arity alone). Added `mw_recursive_decomposition`
to
[`src/pilot/adjudicate_compound_differs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/adjudicate_compound_differs.py):
when PWG's own list is binary and MW lists more members that concatenate to the
same string, the verdict is `pwg_members-right` — MW's extra granularity is the
recursive decomposition of the first member (`goṣṭhīpati` = `goṣṭhī + pati`; MW's
`go + ṣṭhī + pati` also decomposes `goṣṭhī` itself), not a rival split of the
headword. The 11 rows where PWG itself gives >2 members (possible dvandva) are
deliberately left out of scope for a human. `--selftest` green, `--write`
regenerated
([`research/pwg_compound_differs_adjudication.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv)):
28 rows now carry `mw_recursive_decomposition`.
[`src/pilot/build_compound_rule_ratification_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_compound_rule_ratification_sheet.py)
re-cut with the new rule's Russian gloss + claim in its `RULES` book (8 rules,
30 cards); preflight gate stays green. Per-stratum Wilson bounds in
[`research/pwg_compound_differs_promotion_plan.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_promotion_plan.json)
were recomputed by the same `--write`, not carried forward from the old
stratification.

### Changed — offline pipeline speed + hermeticity: in-proc audit chain, stamp memo, PWG_OUTPUT_DIR (H1811, 30-07-2026)

> **Superseded in part by H1957 above: S1 and S3 were reverted for correctness, so the
> speed figures in this entry no longer describe the shipped code.** They are kept as
> the record of what was measured at the time. Net effect after H1957 is roughly
> +15 % total against master — S2/H5/H10 remain.

Measured on the hermetic [`h1339_offline_bench`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1339_offline_bench.py)
(interleaved A/B vs `origin/master` `d5650afe`, medians of 3): **audit stage −39.3 %**
(3.60 s → 2.19 s), store-write −12.4 %, **total −22.9 %** (7.23 s → 5.58 s) —
with the deterministic output signature **and** store semantic hash byte-identical
on both sides. **Re-verified 30-07-2026 after rebase onto master `f15bcf0f`**
(26 commits later): **audit −36.9 %** (4.19 s → 2.64 s), **total −19.3 %**
(8.42 s → 6.80 s), signature `9bd2a14297` still byte-identical across both sides.
The smaller headline is base drift, not candidate regression — master's own total
rose 7.23 s → 8.42 s over those commits (fix log §5.1).
Executor: Kimi K3 (`moonshotai/kimi-k3`); rebase + re-verification: Opus 5
(`claude-opus-5[1m]`); review + fix log:
[`pwg_ru/h1811/H1811_PIPELINE_REVIEW_FIXLOG_2026-07-29.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1811/H1811_PIPELINE_REVIEW_FIXLOG_2026-07-29.md).

- **S1** — ~~`coordinator record-output` runs `audit_window` **in-process**~~ —
  **REVERTED by H1957**: the daemon-thread timeout could not cancel the audit. The
  `run_audit` seam is kept, now backed by a killable subprocess.
- **S2** — `audit_window` runs `_pilot_collect` in-process too (the last
  subprocess gate after H1339 Phase 3). **Retained.**
- **S3** — ~~`pipeline_version.stamp` memoizes `component_sha` per process~~ —
  **REVERTED by H1957**: the memo had no invalidation and stamped stale provenance.
- **H5** — a corrupt/missing `window_status.json` / audit report with rc ∈ {0,1}
  is now an audit error instead of a silent `unknown` lease state.
- **H10** — `PWG_OUTPUT_DIR` (output-side twin of H1386's `PWG_INPUT_DIR`) honored
  by `_pilot_collect`, `audit_window`, `audit_translation`, `root_glue_translated`
  and shared `window_common.OUT`; the "hermetic" bench no longer rewrites live
  `src/pilot/output` sidecars. Five readers needed patching — missing two of them
  produced first NO-OUTPUT false defects, then phantom `partial` states (the bench
  caught both).
- Gates: `window_selftest` **194/194** (new `test_h1811_inproc_audit_timeout_seam`;
  two coordinator fixtures moved to the `run_audit` seam); LANG_PARITY 89 entries,
  no drift (new SHARED entry `h1811_inproc_audit_pwg_output_dir`;
  `h1339_offline_bench.py` moved exempt → tracked).
- The first rebase surfaced a **193/194** suite, the one failure being
  `test_lang_parity_ledger_complete`: `citation_tm.py`, `corpus_gate.py` and
  `annotate_genres.py` had drifted under H1902 and were awaiting re-affirmation.
  Those three files are byte-identical between master and this branch, so the
  debt was master's, not this change's; it was paid separately in
  [#894](https://github.com/gasyoun/SanskritLexicography/pull/894) rather than
  `--update-hash`'d here. After rebasing onto that green master:
  `lang_parity_check` **89 entries, no drift**, `window_selftest` **194/194**.

## [1.111.2] - 2026-07-30

### Fixed — LANG_PARITY re-affirmed for the three files H1902 left drifting; master is green again (H1940, 30-07-2026)

H1902 ([#892](https://github.com/gasyoun/SanskritLexicography/pull/892)) unified
sibling-root resolution across `src/` but did not re-affirm the parity verdicts of
the three tracked files it touched, so `lang_parity_check` reported **3 violations
on master itself** and `test_lang_parity_ledger_complete` took the whole
`window_selftest` suite red. Every PR opened since inherited that failure —
[#893](https://github.com/gasyoun/SanskritLexicography/pull/893) is where it
surfaced, though it neither caused nor could fix it (the three files are
byte-identical between master and that branch).

Each verdict was re-derived rather than rubber-stamped. H1902's edit is the same
`+2/-1` substitution in all three files — the hard-coded
`os.path.join(HERE,'..','..','..')` guess replaced by `sibling_root(HERE)` — and
[`src/sibling_root.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sibling_root.py)
contains **no language-conditional logic whatsoever** (0 language tokens in 108
lines). Since all three verdicts rest on *which language assets exist*, not on how
paths resolve, none of their grounds moved:

- `citation_tm_ru_translation_of_record` — INTENTIONAL-DIVERGENCE holds; `GITHUB`
  feeds `CORPUS_DB` only, and no EN citation-TM corpus was assembled.
- `corpus_gate_evidence_markers_fl7_h321` — INTENTIONAL-DIVERGENCE holds; the
  marker mechanism and the wired authority set are unchanged, no Sanskrit-English
  authority was added.
- `genre_sense_join_h339` — SHARED holds, and is arguably *strengthened*: `GH`
  feeds the shared German `pwg.txt`, and the removed hard-coded guess was
  precisely what could resolve differently between checkouts.

The reasoning is recorded in each ledger note, not only here. Gates after:
`lang_parity_check` **88 entries, no drift**, `window_selftest` **193/193**.

### Fixed — FINDINGS citation-number collision from the H1910 propagation pass (30-07-2026)

The H1910 sweep appended four print-OCR findings as **§463–§466**. Those numbers were picked
by reading the repo's **main checkout**, which is frozen/diverged and showed a highest number
of §462 — but on `origin/master` the file already carried 166 findings and all four numbers
were taken (the `pwg_ru` `de`-field finding, the `gloss_lang` classifier, the PWG×DCS sense
collapse, and MW `cf.`/PWG `Vgl.`). So four §-numbers briefly carried two different claims
each, which the citation-identity ruling forbids outright: a §-number is a permanent citation
key, one claim per number.

- Renumbered the four intruders to **§506–§509**; the pre-existing claims at §463–§466 are
  untouched.
- **The next-free marker was itself stale** — it read `(currently §505)` while §505 was
  already used by the SamudraManthanam durable-reference finding that landed mid-session.
  That staleness is what caused the *second* mis-pick, so the marker is now at **§510** and
  the repair script asserts, as a post-condition, that the marker sits above every used
  number.
- Backfilled the four **Index** entries the original append also skipped, restoring Index
  parity. Anchors were generated by a slugger validated against this file's own anchors
  first — 138 of 163 reproduced exactly, and the 25 misses are pre-existing rot (20 from an
  older hyphen-collapsing slugger, so those are dead links today; 5 left stale by a later
  edit to their own heading), not a rule difference.
- Regenerated `findings_dashboard/data.json` and `epistemic_dashboard/epistemic.json`, which
  were stale at 161 vs 166.
- [`tools/epistemic_integrity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/tools/epistemic_integrity_check.py)
  now reports **OK — 166 distinct headings, Index parity holds, no duplicate §-numbers,
  dashboards in sync.**
- `FINDINGS.meta.md` records the episode, since the same append also skipped its metadoc row.

The generalisable lesson is now recorded as a fifth finding, **§510**: *a frozen local
checkout is an actively misleading source for any append-only registry.* Read the numbering
contract from `origin/<default>`, derive the ceiling from the actual headings rather than the
in-file marker (which is a cache only as good as the last appender), and assert as a
post-condition that the marker sits above every used number. It is the registry-side twin of
the existing §503 — in both, the *location* of the checkout rather than the code decided the
outcome, and in both the failure was silent. FINDINGS is now 167 entries with the marker at
§511.

## [1.111.1] - 2026-07-30

### Fixed — LANG_PARITY hash re-stamped on human authorisation; the selftest suite is fully green (H1910 follow-up, 30-07-2026)

1.111.0 shipped with one deliberate loose end: `src/tm_source_weights.json` had changed, so
the `rv_corpus_translation_witness_tm_tier` entry in
[`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
was carrying a stale `verified_sha256`. The agent that made the change did not stamp its own
work — re-stamping is the human reaffirmation that ledger exists to collect — and surfaced the
red gate instead. **A human authorised the stamp in-session the same day.**

- Before stamping, both structural grounds of the SHARED verdict were re-checked
  **mechanically rather than asserted** (9/9): no key in the weights file is language-keyed
  and no per-language section exists; `by_work` now carries **two** populated EN rows
  (`rigveda-griffith-en-1896` 0.68, `rigveda-jamison-brereton-en-2014` 0.92) where the verdict
  required only one, so H1910 *strengthened* it; the `lang` enum is still exactly `[ru, en]`;
  and `corpus_translation_witness` / `suggest_only` sit in their enums with no language
  condition on the tier. The reasoning is now in the ledger entry's own note, and the note's
  earlier "deliberately NOT refreshed" sentence is corrected rather than left contradicting
  the file it sits in.
- Ledger: **88 entries, all verdicts complete, no drift**; 25 language-aware files tracked or
  exempt.
- `python src/pilot/window_selftest.py` → **193/193, 0 failed**. This is the first fully green
  run: the parity gate is the one the harness itself documents as having been "RED BY DESIGN",
  and which — before the per-test isolation fix — took the last 27 tests dark with it.

## [1.111.0] - 2026-07-30

### Added — Jamison–Brereton 2014 as a fifth translation column, Renou EVP as a locus witness (H1910, 30-07-2026)

MG lifted R4's exclusion of Jamison–Brereton ("we can add Jamison, ignore copyright") and
asked for Renou in the chronology. The two additions are deliberately **not** symmetric, and
conflating them was the whole failure mode to avoid: J–B is a complete parallel translation
and becomes a fifth column; Renou's EVP is a selective commentary and stays a witness layer.

- **The fifth column.** [`src/rv_jamison_brereton_extract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_jamison_brereton_extract.py)
  extracts all **10,552 / 10,552** loci with **0 unmatched, 0 duplicate, 0 commentary leaks**
  from the archive.org OCR of the three print volumes. The OCR is an input and is never
  committed. Segmentation is positional, anchored on the VedaWeb canonical hymn sequence,
  because the printed numbers cannot be trusted: `^[IVX]+\.\d+` matches 2,303 lines that are
  overwhelmingly prose cross-references, the heading form differs between volumes (`I.l Agni`
  vs `IV.44(340) Asvins`), and the OCR renders Mandala II as `11`. Eight headings the OCR
  destroyed outright (`mil (527) Agni`, `m103(619) Frogs`) are recovered positionally rather
  than by loosening the pattern.
- **Requirement 3 is checked, not assumed.** Three kinds of J–B editorial matter were caught
  leaking into stanza text — a heading block, a `Mandala N` section introduction, and a
  hymn-group introduction — plus embedded page furniture affecting 1,031 stanzas. All four
  were invisible to the locus count, which read 10,552/10,552 throughout. Now gated, with the
  independently-extracted Griffith layer as control (2.50% vs 1.87% open-ended stanzas).
- **Renou stays out of the columns.** [`src/rv_renou_evp_witness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_renou_evp_witness.py)
  joins the committed 2,213-mention H1843 index onto **1,908 distinct loci** (458 with a
  quoted French fragment) as a witness file beside the spine. A `translations` column for EVP
  would be mostly `absent_from_source` and would corrupt `omitted_by_one`, whose meaning rests
  on absence being meaningful. `renou_fr_1955` enters the chronology (1955–69, between Geldner
  and Elizarenkova) as a witness; a test pins that it never becomes pair-eligible.
- **Consequences.** Translator pairs 6 → **10**; the deterministic omission arm now decides
  4 of 10 rather than 3 of 6; the flat TSV mirror 659,032 → 823,790 rows. Griffith is demoted
  from "the English column" to the *Victorian* English one, and H1908's asymmetry note is
  re-derived rather than kept — its claim that R4 excluded J–B is now false, and a test fails
  if it survives anywhere in the gate-sheet builder.
- **Gate sheet v5** carries the fifth translator and a Renou witness band (14 of the 100
  sampled items sit at a locus where Elizarenkova cites him). v4's voted lock is untouched.
- **Measured philological fact:** at RV 10.106.5–8, the four stanzas Geldner omits, J–B print
  transliterated Vedic rather than English — they decline to translate rather than skip.
- **One human action owed:** `src/tm_source_weights.json` changed, so the `LANG_PARITY.md`
  entry `rv_corpus_translation_witness_tm_tier` needs its `verified_sha256` re-stamped. The
  SHARED verdict was re-verified in the ledger note and is *strengthened* (EN now has two
  populated witness rows), but re-stamping is the human reaffirmation the ledger exists to
  collect, so `--update-hash` was deliberately not run by the agent that made the change.

### Changed — ratification sheet v2: eight corrections from MG's first read (H1907, 30-07-2026)

## [1.110.0] - 2026-07-30

### Changed — ratification sheet v2: eight corrections from MG's first read ([H1923](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1923-Opus_SanskritLexicography_ratification-sheet-v2-mg-eight-points_30.07.26.md), 30-07-2026)

> The merged commits and [PR #889](https://github.com/gasyoun/SanskritLexicography/pull/889)
> say **H1907** — an id that was never minted, invented as a label mid-session. H1923 is
> the real claim for this work. Merged history is not rewritten; this note is the pointer.

MG read the 30-card sheet and filed eight points; all eight applied. Three were
substantive rather than cosmetic:

- **The anusvāra was misrendered.** `index_members` splits MW's `jana—ṃ-tapa` at the
  em-dash, stranding the anusvāra on the second member so MW appeared to claim a word
  `ṃtapa` that does not exist. The card now shows **`janaṃ + tapa`** with a note on MW's
  notation. 107 rows.
- **Avagraha was printed bare.** `tejo—'hvā` — the apostrophe is an elided initial `a`
  from sandhi. Cards carrying `'` (21 rows) now say so and give the pre-sandhi form.
- **A samāsa has exactly two parts** (dvandva excepted), so MW's three-member list is a
  samāsa inside a samāsa, not a competing analysis — MG's ruling. Measured after: PWG
  gives exactly two members in **4,342 of 4,353 rows (99.7 %)**, and in all 66 rows where
  MW gives three, PWG gives two. Cards where MW lists >2 now carry the ruling. Applying it
  to the adjudicator (~31 further `unresolved` rows resolve for PWG) is queued as H1918,
  not done silently.

Also: statistics table (rule × rows × share × cards) in the header and a per-card row
count; «Указатель» → «MW split»; the rule label no longer printed three times (badge
dropped, `filters` bar emptied — it duplicated the facet bar); «MW оставляет с суффиксом,
PWG приводит основу»; the samāsa-type note moved off every card into the footer **with
what is missing to assign one**; the source cell collapses to «= членение» when it only
repeats the split, and German `von` (780 of 4,353 parens) is not treated as content.

The preflight gate caught two of my own defects while building this — a raw-SLP1 quotation
inside the new anusvāra note, and `mw_is_finer=True` transliterated to "thrue".

## [1.108.0] - 2026-07-29

### Fixed — NWS-layer citations in the Roman-numeral convention now resolve to Cologne links (H1809, 29-07-2026)

MG, voting `g5_batch1v3_sheet.html`: «ṚV(Sā) I 165, 11 is not clickable? Why? All such
entries are long ago clickable even at Cologne». The NWS (`Nachträge`) layer cites in its
own convention (Roman-numeral maṇḍala, optional `(Sā)` recension marker) that
`ls_resolver` — a faithful port of Cologne's `ls_service.dart` — cannot resolve without
normalisation.

- **[`src/nws_ls_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nws_ls_markup.py)**
  — census + apply: normalises the NWS convention into the `n=` attribute of a
  `<ls n="normalised-locus">` wrapper around the ORIGINAL, byte-identical span (so the
  `(Sā)` recension marker is never discarded — no ruling on its semantics was needed).
  Gated on PWG's own bibliography so no siglum is guessed into a fabricated link.
  Store-wide: 6 candidate spans (not ~230 as a linear scale-up from the 150-card sample
  would suggest) — 2 resolved (`ṚV(Sā) I 165, 11`, `ṚV IV 42, 8`), 4 honest residue
  (`ChU`/`Harisv`, not in PWG's bibliography).
- Same pass migrated the store's half-translated `[diasystem, domain]` tag values
  (`без уточн.` / `Мед.` / `Линг.` / `Лингв.` → canonical Latin `unsp`/`Med`/`Ling`,
  17 occurrences) — a second defect the citation census surfaced in the same bracket-tag
  scan.
- Full report:
  [`pwg_ru/H1809_NWS_LS_MARKUP_REPORT_2026-07-29.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1809_NWS_LS_MARKUP_REPORT_2026-07-29.md).
  Tests: [`tests/test_nws_ls_markup.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_nws_ls_markup.py).

## [1.106.0] - 2026-07-29

### Added — review sheets must reuse what the repo already knows, enforced before write (H1887, 29-07-2026)

MG, voting the 200-card compound-differs sheet: «Я не понимаю, зачем мне
голосовать». Measured: **191 of its 200 cards already had a machine verdict, a
named rule and cited evidence** in
[`research/pwg_compound_differs_adjudication.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv)
(H1681) — computed from the same two input files the sheet itself reads, sharing
4,246/4,246 row ids — and the sheet rendered none of it. Separately, 69 of the 200
cards (34.5 %) were not split disagreements at all, and 18 of the 44 cards showing
a «Пāṇini» line showed a structurally impossible reference.

- **[`src/review_evidence_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_evidence_preflight.py)**
  — a gate that runs BEFORE a sheet is written and raises instead of warning.
  Mechanical prior-art overlap (join it or state why not, per artifact) · evidence
  floor · Cyrillic/IAST script purity · SLP1 leakage · citation linkability ·
  structural validity of cited references. Replayed against the sheet MG
  complained about it returns **12 blocking findings**.
- **[`src/pilot/build_compound_rule_ratification_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_compound_rule_ratification_sheet.py)**
  — the replacement ask: **30 cards, not 200**. The human ratifies the seven
  auto-resolving rules, retiring **3,975 rows**. Every card carries both splits in
  IAST, both dictionaries' own printed text, the glossed difference, DCS frequency
  or a stated reason there is none, and 157 links across the sheet.
- **[`research/REVIEW_SHEET_EVIDENCE_REUSE_H1887.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/REVIEW_SHEET_EVIDENCE_REUSE_H1887.md)**
  — the full measurement, every one of MG's nine points checked, and why no
  existing layer caught it (the standard is entirely presentation; the H1628 sheet
  is fully standard-compliant and still unanswerable).

## [1.99.0] - 2026-07-29

### Added — RV multi-translation evidence spine, wave 1a: griffith/stanza/lemma/renou (H1843, 29-07-2026)

Executes wave 1a (steps 1-6) of
[IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_rv-multitranslation-evidence.md),
by Sonnet 5 (`claude-sonnet-5`). Five new committed feeds under
[`pwg_ru/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru),
built by three new deterministic scripts under
[`src/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src)
([`rv_griffith_extract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_griffith_extract.py),
[`rv_spine_build.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_spine_build.py),
[`rv_renou_citations.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/rv_renou_citations.py)),
all invariants pinned by
[`tests/test_rv_spine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_rv_spine.py)
(20/20 green):

- **`griffith_en_1896.json`** — the Griffith 1896 English RV layer, extracted from
  `rvlinks/RV_sa-hn-ru-de-en_1.html` (S1 spike: 10,552/10,552 loci matched the VedaWeb
  set, 0% unmatched — no K5 mapping decision needed).
- **`rv_stanza_translations.jsonl`** (10,552) + **`rv_lemma_occurrences.jsonl`** (9,961
  lemma/form-keyed groups, 164,758 tokens) + **`rv_translation_spine.tsv`** (659,032 rows,
  173.6 MB, under the 200 MB gitignore threshold) + `schemas/rv_translation_spine.schema.json`.
  Every VERIFICATION §2 hard invariant reproduced exactly: Geldner `absent_from_source`
  is 4 and exactly RV 10.106.5-8; Grassmann/Elizarenkova 0; zero empty rows; 164,758 tokens.
- **`rv_renou_citation_index.jsonl`** (2,213 mentions) — reproduces the handoff's stated
  grand total exactly via whole-word `Рену` counting over the ten
  `SamudraManthanam/.../NN_rigveda.no_tags` commentary files (an undocumented dialect:
  opening `<div>`/`<span>` tags carry attributes but no closing tags are ever emitted —
  a footnote runs to the next tag-open, not to a `</span>`).

**Two published reference numbers did not reconcile, logged rather than silently
forced** (full reasoning in
[`docs/DECISIONS_LOG_rv_multitranslation.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/DECISIONS_LOG_rv_multitranslation.md),
per the plan's R16 autonomy contract — did not stop, did not ask): VERIFICATION §1.1's
per-mandala Renou table (459/117/161/.../287) sums to 1,930, not the 2,213 it claims as
its own total; this script's per-mandala breakdown (527/124/179/.../333) is internally
consistent and used as the corrected reference going forward. Separately, the
"368 quoted_fr" invariant was not independently reproduced by any of three tried
heuristics (this script's literal ~25-char/Latin-script reading gives 459); recorded as
an open question for wave 1b rather than hand-tuned to match an unverified number.

Wave 1b (typing/alignment/wiring) is
[H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md),
still queued.

### Added — audit record for the Gorresio map audit sheet; G2.4.7 flagged for re-vote (29-07-2026)

The 26-07-2026 audit sheet (32 cards, 28 approve / 4 reject) was applied in
[#793](https://github.com/gasyoun/SanskritLexicography/pull/793) but never got the
`/decisions-apply` audit record its sibling sheets carry. Backfilled as
[`review/decisions_applied_29-07-2026_gorresio-southern-map-audit.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_29-07-2026_gorresio-southern-map-audit.md)
by Opus 5 (`claude-opus-5[1m]`) — no data changed; all 32 votes re-verified against the
committed TSV (28 reuse ON / 4 `audit-rejected` inert, no stray `audit-rejected` rows),
selftest all-green, and the 4 rejects confirmed to degrade to honest
`no-southern-counterpart` misses in `citation_tm.lookup`.

One finding for audit round 2: **G 2,4,7 → S 2,5,7 scored 0.286 when it was rejected and
scores 0.741 today** — the H1689 e-text rebuild changed the evidence under that judgement,
and 0.741 would classify `matched`. The full-pair denylist correctly held the veto; the row
stays off pending a fresh human vote rather than being flipped silently.

### Added — execution-ready plan: the Rig-Veda multi-translation evidence layer (H1843/H1844, 29-07-2026)

Five cross-linked layer docs under [`docs/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/docs),
authored by Opus 5 (`claude-opus-5[1m]`) via `/ask` after a 4-round interview (17 rulings):
[PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md)
(+ its [metadoc](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.meta.md)) ·
[ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_rv-multitranslation-evidence_2026H2.md) ·
[ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_rv-multitranslation-evidence.md) ·
[IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_rv-multitranslation-evidence.md) ·
[VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_rv-multitranslation-evidence.md).

The layer joins the Ṛgveda to four translations (Grassmann 1876–77 · Geldner 1951–57 ·
Elizarenkova 1989–99 · Griffith 1896) at lemma granularity, types where the translators diverge,
and wires the result into the pipeline three ways — judge witness, contradiction gate, and a new
TM tier serving **`ru` and `en` alike**. It extends the G6 evidence panel shipped the same day
([H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md),
after the `na` → «словно» reversal at id 122): that panel already routes a Vedic card to GRA's
sense list plus Russian passage context, but carries nothing about what the *other* translators
did with the same stanza — Geldner, Griffith, and Grassmann's own **translation** as distinct
from his dictionary. This layer supplies exactly that, plus the divergence signal.

**Measured during the audit, and load-bearing for the design** (full list in VERIFICATION §2):
the Ṛgveda has 10,552 stanzas and **164,758 tokens**; `lemmatization.json`'s `transformContext`
already carries `id_gra`/`id_pwg`/`id_mw` **per token**, so the dictionary anchor need not be
built; Grassmann and Elizarenkova cover all 10,552 stanzas but **Geldner covers 10,548** —
the four he does not translate are exactly **RV 10.106.5–8**, which turns the `omitted_by_one`
class into a regression test with known ground truth; and Elizarenkova's commentary carries
**2,213** mentions of Renou, **368** with a directly quoted French fragment.

No code and no data shipped in this entry — plan only. Execution is
[H1843](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1843-Sonnet_RussianTranslation_rv-multitranslation-spine-w1a_29.07.26.md)
(wave 1a, deterministic) and
[H1844](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1844-Opus_RussianTranslation_rv-multitranslation-typing-w1b_29.07.26.md)
(wave 1b, gated).

### Changed — the G5 card is legible: печатный вид, кликабельные цитаты, подсказки к пометам (H1808, 29-07-2026)

MG filed five defects while voting
[g5_batch1v3](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/g5-live-queue-batch1v3-2026-07-26.lock.json).
Two were the shared emitter's and were fixed a level down in
[csl-pyutil v0.6.0](https://github.com/sanskrit-lexicon/csl-pyutil/releases/tag/v0.6.0)
(a +150% default type scale — the panel `<pre>` holding the text under judgement had
been the *smallest* type on the page — and `csl_pyutil.anatomy`, the entry-anatomy
colouring previously reachable only from csl-atlas). Three were this repo's, and the
per-card rendering now lives in
[`src/g5_card_render.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/g5_card_render.py):

- **Citations are clickable.** «ṚV(Sā) I 165, 11 is not clickable? … All such
  entries are long ago clickable even at Cologne» — and they already were on our own
  public article site: the print panel now goes through the same
  `build_article_site._render()`, so `<ls>` becomes a Cologne scan/edition link (the
  [`ls_resolver`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
  port of Cologne's `ls_service.dart`) with a `pwg_sources` bibliography tooltip.
  Batch1v3: **988 links across 60 cards**, where the old sheet printed
  `&lt;ls&gt;…` as literal text on all 69 cards that carry citations.
- **The two RU panels are no longer indistinguishable.** Measured cause: on **50 of
  150** cards they were textually identical, differing only by the Cyrillic
  highlight. Panel 1 is now the rendered print view; panel 2 is the raw store markup
  **colour-coded by part class**; headings say what each is for, and a card whose two
  panels genuinely still read alike says so in one line instead of leaving the reader
  to diff them.
- **The NWS bracket tags have tooltips.** «почему аббревиатуры без tooltips?
  например [Gen, unsp] не очевидно что это» — `<ab>` had tooltips; the `[diasystem,
  domain]` tags never did, because they are not markup, just text. Both slots are now
  glossed in Russian from a store-wide census (11,030 rows): slot 1 Ved 103 · Śā 50 ·
  Gen 28 · Buddh 9 · Reg 8 …; slot 2 `unsp` 153 (= *не указан*) · Med 28 · Ling 11 ·
  Soc 8. `[ifc (Bhvr)]` and `[NWS: source : page]` are glossed too.

**Honest gap:** NWS-layer citations carrying no `<ls>` markup use a different siglum
convention from PWG's own (`ṚV(Sā) I 165, 11` vs `ṚV. 1,165,11`), so the resolver
returns nothing. There are exactly **3 such spans on 3 of 150 cards**; they are marked
as citations with a source tooltip and left unlinked rather than guessed at.
Normalising them store-side is
[H1809](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1809-Sonnet_SanskritLexicography_nws-bare-citation-ls-markup_28.07.26.md).

The sheet was **re-issued without disturbing the vote**: `--pin-ids <lock>` re-renders
exactly the locked ids after proving every card's content digest is unchanged (150/150
byte-identical), so the same `sheet_id` + same ids keep the browser's localStorage
votes bound. The lock now carries `item_digests` so the next presentation re-issue can
prove that from the lock alone. Recurrence is watched by a new claude-config hook.

### Added — the G6 gold card now carries its evidence BEFORE the vote (H1801, 29-07-2026)

- New [`src/gold_evidence_panel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_evidence_panel.py):
  four panels joined from assets the project already owns — a **period-routed
  dictionary sense list** (Vedic ⇒ GRA first, else MW + PWG), a **Whitney root
  line** (DCS `lemma2root` · `mw_etymology` · `pwg_etymology` → `mw_roots.tsv` →
  MW↔Whitney `root_crosswalk` → Whitney's own gloss), **attested contexts from
  the card's own work** with their published Russian, and the **ranked A2/A4
  Sa→Ru glossary**. Nothing new is derived.
- `build_g6_mqm_gold_sheet.py` renders them between the Russian rendering and
  the LLM label, so the evidence is read before the label is judged. New sheet
  id `g6-mqm-gold-starter-evidence-picker-2026-07-29`, which also carries
  H1802's required reject-label picker (the two H1796 follow-ups re-cut one
  sheet, so they share one generation; H1802's unvoted picker-only id is
  superseded). The H1796 lock is untouched and its votes stay validatable. `--no-evidence` reproduces the old layout for diffing.
- Coverage on the regenerated 20-card starter (identical ids): glossary 20/20,
  dictionary 16/20, contexts 14/20, root 8/20 — the 12 rootless cards are proper
  names, a pronoun and a particle, and say so.
  [`review/G6_EVIDENCE_PANEL_DIFF_2026-07-28.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/G6_EVIDENCE_PANEL_DIFF_2026-07-28.md).
- **Never fake completeness.** Every panel reports what it searched; an empty one
  prints `evidence not found: искали — …`. Context hits are graded
  `token`/`substring`/`glossary`; variant key hits are labelled; DCS homographs
  below 10 % of the top candidate's corpus count are rejected out loud (this
  stopped Grassmann's √mad being served as a sense of the particle `na`).
- `--selftest` (wired into CI) covers the four cases H1801 names plus the
  homograph guard, the key-variant layer and whole-compound-before-parts
  ordering; fixture-only, so it is green where none of the eight assets exists.

### Fixed — the reversed G6 card is id 122, not 118 (H1801, 29-07-2026)

- The H1796 commit message, the H1801 handoff and FINDINGS §499 all recorded the
  card reversed on withheld Rigvedic evidence as "id 118". Card 118 is
  `aruRAmSub` / `raghuvamsha`, ruled `defer`; the reversed card is **122**
  (`na` / `08_rigveda`). Corrected in FINDINGS §499; counts unaffected.

### Added — first human gold labels: the G6 MQM starter vote is applied (H1796, 28-07-2026)

- Sheet `g6-mqm-gold-starter-2026-07-25` (20 cards from the 320-row
  [`gold/gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl)
  scaffold) voted by MG and ingested through
  `validate_decisions.py` → `apply_decisions.py --gate G6` → `gold_ingest.py`:
  [`gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.labels.jsonl).
  16 LLM labels confirmed, 3 overturned (ids 2, 105, 221), 1 deferred (id 118).
- **Do not quote 84.2 % as pwg_ru label accuracy.** n=19 resolved rows gives a
  Wilson 95 % interval of [62.4 %, 94.5 %]; `hallucinated` was never exercised and
  `wrong-sense` was exercised once and overturned. The figure that will carry
  weight is the n=400 store cut (H1665, gate G6b).
- The vote could not be applied as cast: 5 of 6 rejects carried no typology
  label, so the all-or-nothing applier refused the whole file. MG ruled the five
  in chat; the adjudicated export sits beside the raw one (both gitignored) and
  every ruling is recorded in
  [`review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md).
  Root cause and the two structural fixes:
  [FINDINGS §499](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

### Fixed — `make_edition_cut.py`'s `release_manifest.json` sha256 was a property of the build host, not the content (H1769, 28-07-2026)

- `copy_file` was a bare `shutil.copy2` and `copy_tree` a bare `shutil.copytree`
  over CHANGELOG.md / DOI_PLAN.md / CITATION.cff / `schemas/` / `roadmap/` —
  none of which carry a `.gitattributes eol=lf` pin. On a Windows checkout with
  `core.autocrlf=true` those source bytes are already CRLF, so a Windows-cut
  edition and a Linux-cut edition of the identical commit pinned two different
  sha256 values for the same logical file in the "immutable" release manifest.
  `copy_file` now LF-normalises text assets before writing (binary assets pass
  through verbatim); `copy_tree` routes through the same helper. Regression:
  [`tests/test_make_edition_cut_lf_determinism.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_make_edition_cut_lf_determinism.py).
- `ru_style_sweep.py`'s `_write_rows_atomic` (the sole writer of the canonical
  `pwg_ru_translated.jsonl` store on `--apply`/`--repair-from --apply`) opened
  its temp file in plain text mode with no `newline=` guard, so a Windows run
  applied universal-newline translation to every row and silently converted
  the store's line endings to CRLF — and its `before_sha256`/`after_sha256`,
  recorded into the persisted repair report for audit, inherited the same
  host-dependence. Now opens with `newline='\n'`. Regression:
  [`tests/test_ru_style_sweep_lf_determinism.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_ru_style_sweep_lf_determinism.py).

### Changed — LOD namespace ruled: `pwg-ru` → `repwg` ("rePWG"), one namespace for all graphs (27-07-2026)

- Publication-IRI `@DECIDE` **closed** ([#809](https://github.com/gasyoun/SanskritLexicography/issues/809)).
  Namespace is now `https://w3id.org/sanskrit-lexicon/repwg/`, replacing
  `…/pwg-ru/` in every graph, SPARQL query, SHACL shape, fixture and generator —
  8,138 occurrences across 18 files.
- **Why `repwg` and not `pwg`:** the graphs carry derived structure and the RU
  side is machine translation (`gr:machine-preview`, non-citable), so a namespace
  reading as plain `pwg` would claim to *be* the Cologne text. `repwg` = "rePWG",
  a *re-edition* of PWG. Lowercase in the path (IRI paths are case-sensitive);
  spelled **rePWG** in labels and prose.
- **Why not `pwg-ru`:** it encoded a fact that stopped being true — four of the
  five graphs (DE enrichment, DE edition, DCS frequency, grammar) are not
  Russian, and the German material is public domain. A maintainer name in the
  path was considered and rejected for repeating the same mistake with a
  different contingent fact.
- A future project-owned domain changes **no IRI**: w3id.org is a redirector, so
  the w3id IRI stays the permanent identifier and the project domain becomes the
  redirect target behind it. Rationale recorded in
  [LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md)
  § Namespace ruling, which replaces the old `## Open decision` section.
- Still open, and now stated instead of implied: the w3id PURL is **not
  registered**, so these are permanent identifiers that currently 404 — the docs
  no longer claim dereferenceable IRIs. `dct:creator`/`dct:publisher` are still
  not emitted.

### Fixed — `release/.gitattributes` did not pin LF for the H1629 XML/JSON artifacts

- `*.ttl`/`*.rq`/`fixture.keys` were pinned; `pwg_de_edition.tei.xml` and
  `pwg_de_edition.manifest.json` were not, so a Windows checkout got CRLF while
  the generator writes LF — every regeneration looked like a full-file diff and
  would have broken the profile's byte-determinism selftest on a fresh clone.

### Added — H1703 second blind arm: every stratum of the compound `differs` queue can now be priced (26-07-2026)

- The H1628 arm samples along length × DCS-frequency × member-count, which cuts across
  the H1681 adjudicator's rules: it lands 139 cards in `same_split_pwg_lemma_form` and
  0–16 in each of the other seven strata, so it could promote 3,018 of 4,226 rows and
  **no more, however the human voted**. New
  [`src/pilot/compound_differs_arm2_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_arm2_sample.py)
  (seed 1703) draws a second arm stratified on the rules themselves — **232 cards**,
  35 per unpriced stratum, disjoint from arm 1, stamped + locked. 35 because
  `wilson_lower(35, 35) = 0.901` and `wilson_lower(34, 34) = 0.898`: it is the smallest
  arm that can clear the 0.90 gate at all.
- **Result: all 4,353 rows now sit in a priceable stratum** (was 3,018 promotable,
  1,208 unpriceable). Seven strata clear 0.90 on arm 2 alone; the 31-row
  `granularity_ic_vs_full_decomposition` is **censused in full** across the two arms, so
  it is promotable by direct vote with no interval to extrapolate — the plan records
  `promotion_basis: census` rather than pretending its 0.890 bound cleared.
- Arm 2 is blind by construction: the card shows the two member lists and the source
  PWG/MW text, never the stratum, rule, agent verdict or reason (asserted by selftest) —
  otherwise an arm stratified by the agent's own classification would be scoring the
  human against it.
- Binding verified end-to-end on both sheets rather than assumed: a complete synthetic
  export validates (200 / 232 items), and a tampered hash, a missing vote and an unknown
  card id are each rejected. **9 of arm 1's 200 cards left the queue** when the upstream
  repairs landed; the plan reports them (`cards_left_the_queue`) and arm 1 was not re-cut
  a second time — its lock is live and its 139 `same_split` cards still price that
  stratum at 0.973.
- Queue re-adjudicated against the repaired extractors: the three defect strata are gone
  (`pwg_layer_inner_chain` 75 → **0**, `pwg_layer_no_headword_paren` 82 → **2**,
  `mw_variant_fusion` 10 → **0**). The queue did **not** shrink as H1703 predicted — 118
  cards left, 241 entered (mostly new PWG coverage), 4,123 → **4,246 cards**. Report:
  [PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md §8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_COMPOUND_DIFFERS_AGENT_ADJUDICATION.md).
  Nothing applied to the store; no `human_reviewed` flag set. Opus 5 1M
  (`claude-opus-5[1m]`).

### Fixed — [integrity] MW `<k2>` variant fusion welded a non-word member ([#801](https://github.com/gasyoun/SanskritLexicography/issues/801), H1703, 26-07-2026)

- MW lists spelling/accent variants of a headword inside one `<k2>`, separated by `; `
  (`gaRa—kAri; gaRakAri`). [`mw_compounds.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_compounds.py)
  split on the em-dash first and cleaned second, and `_ACCENT_STRIP` removes both `;`
  and the space — so the variants were welded into a member that is not a word
  (`gaRa` + **`kArigaRakAri`**). The bogus member also inflated the arity, so
  `nominal_grammar._irregularities` emitted `compound:3_members` and the Zaliznyak
  index `+3` for a two-member compound (`citpati` shipped as `m·3a+3`).
- The variant list is now separated **first**, taking the first variant that actually
  carries the segmentation. **41 of 106,603** MW compound records corrected, 22 of them
  arity-corrected; [`headword_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv)
  (36 rows), `paradigm_stats.tsv` and `reverse_paradigm_index.json` regenerated
  accordingly. New `--selftest` (7 fixtures), wired into CI. Opus 5 1M
  (`claude-opus-5[1m]`).

### Added — H1702 boundary-anchored auto-wrap for the H1651 D4 `ru_n==0` sub-pattern (26-07-2026)

- H1651 flagged 2,539 rows where `de` carries a `{%...%}` gloss but `ru` never wraps its
  (present, correct) translation, and declined to auto-fix pending a boundary-anchored
  method. This pass builds it: exact-affix positional anchoring on invariant markup
  (`{#...#}`, `<ls>`, `<ab>`, `<is>`) never guesses a boundary it can't verify
  byte-for-byte. 1,430/2,539 rows fixed; 1,109 left as a manual-review worklist (joins
  the pre-existing 46-row D3 residual, left untouched by a guard added mid-pass after it
  was found to be at risk of detector-masking). New CI gate
  `test_h1702_boundary_wrap_gate`. Full report:
  [pwg_ru/H1702_D4_BOUNDARY_ANCHORED_WRAP_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1702_D4_BOUNDARY_ANCHORED_WRAP_REPORT_2026-07-26.md).

## [1.82.0] - 2026-07-26

### Added — H1689: Gorresio vols 2/4/uk OCRed, e-text now covers all 7 kāṇḍas — `gorresio-etext-gap` extinct (26-07-2026)

- The 1,427 image-only Cologne pages (vol 2 Ayodhyā sargas 10–127 · vol 4
  Kiṣkindhā-tail + Sundara · uk Uttara) OCRed locally with tesseract 5.5 `san`
  on the full-resolution embedded page images;
  [gorresio_etext.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gorresio_etext.jsonl)
  grows 10,225 → **19,852 verses (all 672 sargas)**, the
  [verse map](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv)
  4,066 → **5,926 mapped** (new: k2 581 · Sundara 345 · Uttara 760); 12/12
  sampled new pairs verified true; the 4 audit-rejected pairs are now
  re-applied by the build itself (pair-keyed veto in
  [build_ramayana_concordance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py)).
- `citation_tm` fixture flip: R. GORR. 2,16,46 (MG's original N11 locus) is
  `no-southern-counterpart` — genuinely Bengal-only (best Southern score 0.109
  vs 0.25 floor); R. GORR. 5,10,1 resolves to `05_ramayana-sundarakanda:2.51`.
  Segmentation hardened: `।।`→`॥` normalization (tesseract double-daṇḍa split).
  Method + traps: [FINDINGS §473](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

### Added — H1682: h1303_abbrev review-sheet rule-collapse (26-07-2026)

- New review sheet `review/h1682_abbrev_rules_sheet.html` (sheet_id
  `h1682_abbrev_rules`, H1404-stamped + locked) replaces the 273-card
  `h1303_abbrev` (never voted) with 33 cards: 12 rule cards (one per
  `build_h1303_abbrev_sheet.py`'s own `O`-overlay section header) + 17
  individually-flagged ambiguous tokens + 3 `ls`-border + 1 meta-card. No
  token reclassified; every proposed RU/precedent is unchanged from H1303
  Session 1. New modules:
  [`h1682_abbrev_collapse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h1682_abbrev_collapse.py),
  [`build_h1682_abbrev_classification_tsv.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h1682_abbrev_classification_tsv.py),
  [`build_h1682_abbrev_rules_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_h1682_abbrev_rules_sheet.py).
  Full report:
  [H1682_ABBREV_RULE_COLLAPSE_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1682_ABBREV_RULE_COLLAPSE_REPORT_2026-07-26.md).
  Old sheet marked superseded-unvoted in `REVIEW_SHEETS_INDEX.md`, never
  deleted.

## [1.79.0] - 2026-07-26

### Changed — Gorresio map audit round 1: 28/32 approve; 4 half-verse-shift rows switched off (26-07-2026)

- The 32-card audit sheet was voted (agent vote by Fable 5 `claude-fable-5` on MG's
  direct delegation) — 28 approve incl. all 5 scan-verified gold anchors; the 4 rejects
  are a single OCR-segmentation sub-class (merged half-verses pairing with the tail
  verse) now marked `audit-rejected` in
  [ramayana_gorresio_southern_verse_map.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv)
  and inert for reuse (selftest pins the 4 rows). Detection heuristic queued into H1689.

### Added — H1651 store wrapper-defect sweep D1-D4, live gate follow-up (26-07-2026)

- Main pass ([#789](https://github.com/gasyoun/SanskritLexicography/pull/789)): D1
  repaired (34 rows/58 spans, closes
  [#752](https://github.com/gasyoun/SanskritLexicography/issues/752)); D3 ruled and
  bulk-applied (343/463 rows, 46 residual); D4 triaged (2,860 rows, no auto-fix — see
  [pwg_ru/H1651_WRAPPER_DEFECT_SWEEP_REPORT_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1651_WRAPPER_DEFECT_SWEEP_REPORT_2026-07-26.md)).
- Addendum (this follow-up): the main pass's CI gate only tested the standalone scan/fix
  tools, not the live per-card generation-time audit. New
  `cyrillic_in_sanskrit_wrapper` (HIGH_CONFIDENCE) and `gloss_wrapper_became_guillemet`
  (report-only) risks in
  [prompt_rule_audit.markup_sigla_risks](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)
  close that gap.

## [1.78.0] - 2026-07-26

> Backfilled section (26-07-2026): the v1.78.0 tag + GitHub release (H1670) were cut
> by a concurrent session WITHOUT a changelog section, and a second same-day cut then
> claimed the [1.78.0] heading for different content — renumbered to [1.79.0] above.
> This section reconstructs the released content from the frozen release body.

### Fixed — H1670: PWG-sense × DCS grounding 0.67% → 12.25% (26-07-2026)

- The H1632 conclusion that sense-level grounding was capped by data availability was a
  **reach artefact**: the matcher's reach, not the corpus, was the limiting factor.
  H1670 raised sense-level grounding **0.67% → 12.25%**
  ([PR #791](https://github.com/gasyoun/SanskritLexicography/pull/791),
  [release v1.78.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.78.0),
  [H1670](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1670-Opus_SanskritLexicography_pwg-dcs-sense-grounding-scale-levers_26.07.26.md)).

## [1.77.0] - 2026-07-26

### Added — H1656 follow-on: Gorresio e-text recovered; Rāmāyaṇa citation reuse ON (26-07-2026)

- **MG ruled: reuse always ON by default** — the validation gate is an audit, not a
  months-long blocker. And the "no Gorresio OCR exists" premise fell the same day:
  the Cologne [ramayanagorr](https://github.com/sanskrit-lexicon-scans/ramayanagorr)
  page PDFs carry an embedded Google **text layer**. New `build-gorresio` subcommand
  ([src/build_ramayana_concordance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py))
  extracts the full **Gorresio e-text**
  ([src/gorresio_etext.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gorresio_etext.jsonl),
  10,225 verses, ॥N॥ segmentation anchored to ksverse per-page ranges) and builds a
  **CONTENT-BASED Gorresio↔Southern verse concordance**
  ([src/ramayana_gorresio_southern_verse_map.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ramayana_gorresio_southern_verse_map.tsv)):
  **4,066 verses mapped** (1,857 matched + 2,209 fuzzy), 4,955 Bengal-only, 200
  `moved` excluded. All scan-verified gold anchors reproduce (G 1,22,1→S 19,1 at
  0.774 etc.). `citation_tm` now resolves R. GORR. + plain R. books 3–6 through the
  map — hits carry `map` class+score; misses are typed (`no-southern-counterpart`,
  `gorresio-etext-gap`). Coverage bound: vols 2/4/uk scans are image-only (Ayodhyā
  bulk, Sundara, Uttara) — queued for a modern-OCR pass.

### Fixed — shingle phase-parity bug in the concordance aligner (26-07-2026)

- Candidate retrieval indexed AND probed shingles on the same stride, so shared runs
  at an off-phase relative shift were invisible — G 1,22,1 ↔ S 19,1 scored 0.774 yet
  was never retrieved. Index now covers every offset. Southern↔Critical rebuilt:
  **81.4% matched/fuzzy** (was 74%); the sarga map is a content-based majority
  roll-up of the verse map (the content-blind DTW draft drifted ±1–3 sargas and is
  superseded; `build` no longer clobbers it).

## [1.76.0] — 2026-07-26

### Changed — H1664 voting-queue triage: every pending sheet ruled A/HYBRID/HUMAN-ONLY (26-07-2026)

Fable 5 (`claude-fable-5`). The 2,962-judgment pending queue (42 sheets org-wide) now
carries a verdict per sheet with the enabling dataset named —
[audit §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md);
after the routed adjudications run, the human owes ~1,329 (−55 %). pwg_ru lanes: compound
`differs` → В2 full-queue adjudication (H1681, the 200-sheet becomes the blind verification
arm), h1303_abbrev → rule-collapse (H1682, 273 → ~30), article-comparison → pre-vote
source-check (H1683); G6/G5v3/h1306/Renou-pilot stay HUMAN-ONLY with the reason recorded.
Results table: [RESULTS_LOG.md 26-07-2026](RESULTS_LOG.md).

## [1.75.0] — 2026-07-26

### Changed — H1633 rulings R1–R5 recorded; G6b gate born; A51 deferred to 2028 (26-07-2026)

- MG ruled the five gold-cut sign-off items in one pass (chat, 26-07-2026):
  **R1** n=400 · **R2** six-label DE→RU vocabulary adopted · **R3** no second
  reviewer — «not even in 2027», intra-rater test–retest is the permanent
  agreement plan · **R4** the cut is named gate **G6b** · **R5** sequenced
  after the g6 starter + g5 batch1v3 votes. Recorded in
  [gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md) §8;
  G6b wired into [HUMAN_REVIEW_MINIMIZATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HUMAN_REVIEW_MINIMIZATION.md)
  (gate table, G6b section, print-evidence path).
- **A51 deferred until 2028** (same ruling) — deferral banner on
  [pwg_ru/PAPER_LLM_LEXICOGRAPHY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PAPER_LLM_LEXICOGRAPHY.md);
  methods draft re-marked BANKED, claims register C1–C3 updated (h178 arms
  retired per P1/A2; no inter-annotator cell anywhere per R3).
- Execution routed: [H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md)
  (gold cut, hard-gated) and [H1664](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1664-Fable_SanskritLexicography_voting-queue-agent-adjudication-triage_26.07.26.md)
  (triage of the 2,818-judgment voting queue for agent-ruleable sheets — MG:
  «2818 judgments is too much»).

## [1.74.0] - 2026-07-26

### Fixed — "a bigger corpus" was the wrong lever for H1632 constriction 1 (26-07-2026)

- The H1632 frame-comparison report and SL FINDINGS §465 said the 60.2% of PWG
  headwords absent from DCS needs "a bigger corpus". **Misleading as written**
  (MG): *DCS already is the largest **tagged** Sanskrit corpus*; the corpora that
  are bigger carry **no markup** — wisdomlib, currently under scrape.
- Both now state the split precisely: an untagged corpus **can** raise
  *lemma-level* attestation (shrinking the "absent everywhere" class) but
  **cannot** raise *sense-level* grounding, since there are no sense tags to bind
  to. Conflating the two is a category error; the rates stay in separate tables.
- Points at the existing `wl` wisdomlib period-state signal (§14) so a second
  wisdomlib lane is not opened, and at the Cloudflare constraint before any scrape.
- Follow-on work minted as
  [H1670](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1670-Opus_SanskritLexicography_pwg-dcs-sense-grounding-scale-levers_26.07.26.md):
  the only real levers on the sense-level number are running the H1455 aligner
  past its own 500 headwords, and adding texts / locus crosswalks.

### Added — H1666: Wave-2 coverage monitor + monthly cloud routine (26-07-2026)

- [`research/WAVE2_COVERAGE_MONITOR.md`](research/WAVE2_COVERAGE_MONITOR.md) tracks
  `verb_worklist.py`'s promoted/749-DCS-root % against
  [ROADMAP_ACL_LESSONS_2026.md](research/ROADMAP_ACL_LESSONS_2026.md)'s Wave-2
  "~50% coverage" trigger — currently 48/749 ≈ 6.4%, stalled since 04-07-2026. A
  monthly `claude.ai` cloud routine (RemoteTrigger) recomputes and appends a row,
  and flags a GTD `@DECIDE` in Uprava once coverage crosses 50%. Registered in
  `research/README.md`'s Living monitors table.

## [1.73.0] - 2026-07-26

### Added — H1656 Rāmāyaṇa recension concordances (Gorresio↔Southern + Southern↔Critical) (26-07-2026)

- MG ruled 21-07-2026 (weekly `@DECIDE`): build the Gorresio↔Southern concordance —
  «NEVER propose to skip» citation reuse. New
  [src/build_ramayana_concordance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ramayana_concordance.py)
  builds three committed, metadata-only TSVs: the **Gorresio structural inventory**
  (672 sargas, verse counts + volume/page, from the Cologne
  [ramayanagorr](https://github.com/sanskrit-lexicon-scans/ramayanagorr) scan-viewer
  page index — no OCR chased, none exists), the **Southern↔Critical verse
  concordance** (18,993 Southern verses vs DCS critical, content-based, 74%
  matched), and a **Gorresio↔Southern sarga map** (DTW over verse-count profiles,
  DRAFT-STRUCTURAL: 319 plausible / 212 weak / 165 unpaired). Selftest wired into
  the CI gates job. R. GORR. stays `unmapped_locus_scheme` until the validation
  gate in [pwg_ru/COVERED_TEXTS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/COVERED_TEXTS_RU.md)
  § R. GORR. passes (≥30-pair scan spot-check + human review sheet).

### Fixed — plain R. books 3–6 are Gorresio-keyed; resolver was silently wrong (26-07-2026)

- **Integrity find (H1656):** PWG's plain `R.` is a three-edition composite
  (pwgbib 1.247): books 1–2 Schlegel, **books 3–6 Gorresio (Bengal recension)**,
  book 7 Bombay. Verified against the store's cited sarga ranges (R. 3 → 79,
  R. 4 → 63, R. 5 → 94 = exactly Gorresio's counts; Southern has 75/–/68).
  `citation_tm.py` keyed in-range book-3/5 loci into the Southern corpus and
  returned the **wrong verse's RU translation** silently — ~900 refs exposed.
  Books 3–6 now return `unmapped_locus_scheme` (selftest fixture added) until the
  Gorresio↔Southern concordance validates. ~2,200 refs total ride on that
  concordance (657 R. GORR. + ~1,560 plain-R. books 3–6).

## [1.72.0] — 2026-07-26

### Added — H1491: Leonchenko Sinonimy digitized to a synonym evidence lane (26-07-2026)

- [`research/sinonimy/sinonimy.jsonl`](research/sinonimy/README.md) (47,273 rows) digitizes
  V.V. Leonchenko's Sinonimy xlsx workbooks (`VisualDCS/derived-data/Sinonimy`) into
  sense-inventory + gloss-anchored synonym-ring rows, per
  [ROADMAP_ACL_LESSONS_2026.md](research/ROADMAP_ACL_LESSONS_2026.md) B2/Wave 1. Also
  registered in [REUSE_MAP.md](REUSE_MAP.md) §5. Dedup finding: the folder's four named
  source groups reduce to three distinct datasets — S_P_D_F/Works-Share-Syn hold confirmed
  duplicate re-exports, not new content. Evidence-only, not yet wired into `corpus_gate.py`.

### Added — H1633 human gold cut design + A51 methods packet (26-07-2026)

- **Store gold-cut sample frame** (design only, parked for sign-off):
  [gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md)
  — the first sampling design for a **human-measured DE→RU store precision**
  figure, distinct from the existing Sa→Ru harvest gold (320) and the A/B/C
  grade gold. Population = the machine-clean G5-eligible pool (post
  residue-gate, P1 auto-reject); 12 strata (entry class × edition layer × DE
  length terciles); recommended n=400 with the cluster penalty stated;
  proposed six-label DE→RU vocabulary (needs a D6-style ruling); tiered κ plan
  honest about the 2026 second-annotator deferral — **no κ target, no
  placeholder κ**. Binding per the H1404 standard.
- **A51 methods-section draft** with honest floors:
  [pwg_ru/A51_METHODS_DRAFT_DE_LAYERS_RU_PIPELINE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/A51_METHODS_DRAFT_DE_LAYERS_RU_PIPELINE.md)
  — source graph, G1–G6 layer floors, pipeline + judge-policy figures kept as
  LLM×LLM calibration (not quality validation), three-channel evaluation
  design, refused-claims section, and a 10-row **claims register** mapping
  every submission claim to its blocking human gate (N1/N2/N3/N9/N11/N13/N18 +
  h178 votes + COMETKiwi license).
- Metadocs for both; pwg_ru.md §8.3 N3 row now points at the frame.

## [1.71.0] — 2026-07-26

### Added — H1628: stratified 200-item review sheet for the compound `differs` queue (26-07-2026)

- [`src/pilot/compound_differs_review_sample.py`](src/pilot/compound_differs_review_sample.py)
  draws a deterministic (seed=1628), two-stage stratified sample of 200 from the ~4226-row
  PWG-vs-index compound `differs` queue (H1624 G6 residual): a flat 20-item quota for the
  rare `member_count_diff` sub-class, the rest proportional across length x DCS-frequency
  cells. Sample frame committed
  ([`review/sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv`](review/sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv));
  the interactive sheet stays gitignored (personal voting artifact). Vote → store contract
  documented in [RESULTS_LOG.md](RESULTS_LOG.md) so applying the vote can never bulk-overwrite
  `derivation.human_reviewed` beyond the sampled ids. Does not close the ~4.2k queue —
  ~4026 rows stay `needs_human` pending a future sampling round.

### Added — first intrinsic BLI quality gate for corpus_lexicon.jsonl (H1521, 26-07-2026)
[`src/eval/bli_eval.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/bli_eval.py)
streams `corpus_lexicon.jsonl` (never loads it whole) and scores P@1/MRR/coverage
against a frozen 400-lemma gold set,
[`src/eval/gold_sa_ru_koch_400.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/gold_sa_ru_koch_400.tsv),
built by [`build_gold_koch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/build_gold_koch.py)
from Kochergina (`src/koch.jsonl`, independently authored, never derived from the
corpus) ranked by VisualDCS's independent `dcs_lemma_summary.json` frequency band —
the obvious default gold source, the corpus's own 3-layer glossary, was rejected as
circular (it is a group-by aggregation OF `corpus_lexicon.jsonl`, so grading against
it would score the file against itself). **Result: P@1 = 0.402, MRR = 0.539,
coverage = 0.995 (398/400)** — first quantitative quality number for the
1.09M-pair lexicon. Fixture selftest (`python src/eval/bli_eval.py selftest`) wired
into CI's RussianTranslation gates.

## [1.69.0] - 2026-07-26

> Version numbering follows the repository's **git tag** sequence (…v1.67.0,
> v1.68.0), which had drifted ahead of the version headings in this file (last
> heading was `[1.62.0]`). Continuing the tag sequence, per `/cut-release`.

### Added — H1632 scale-up: unbiased random frame + full-PWG run (26-07-2026)

- The original H1632 pilot ran on a frame **selected DCS-attested**, so its "100%
  attested at lemma level" was true by construction. Two unbiased frames now
  answer the question it could not — a seeded random sample (2,000 groups) and
  **every PWG headword (109,050 groups)**. Synthesis:
  [research/PWG_SENSE_DCS_FRAME_COMPARISON.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_FRAME_COMPARISON.md).
- **Lemma-level attestation is ~40%, not 100%.** 43,352 / 109,050 PWG headword
  groups (39.8%) have a DCS lemma — so **60.2% have no DCS attestation at any
  granularity**. The 2,000-group sample estimates 40.4% (±2.2% at 95%) and its
  interval covers the population value, validating the sampling frame.
- **The sense-tag ceiling is a corpus property, not a frame artefact** — 10.8% /
  11.9% / 11.2% of DCS token mass across the three frames.
- **Grounding is reported as *unknown*, never as zero.** The H1455 aligner covers
  500 of 109,050 groups; the rest are classed `R0_grounding_not_computed`.
  Publishing 0% there would manufacture a dictionary-wide rate out of the absence
  of a job. Selftest asserts the join rates come back `None`, not `0.0`.
- New `--frame-mode kosha|random|all` (+ `--n`/`--seed`) on the pilot script,
  `--all` on the loci exporter, and
  [research/compare_frames.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/compare_frames.py),
  which reads the three `meta.json` files so the synthesis cannot drift from the runs.

### Added — edition-diff reading surface over edition_rel (H1631, N14 pilot, 26-07-2026)

- New
  [`src/pilot/build_edition_diff_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_edition_diff_site.py):
  a fixture-driven static page showing the PWG sense skeleton with PW/SCH/PWKVN/NWS
  supplements attached at their `edition_rel` insertion point, each badged with its
  H1624 G4 subtype (`base`/`restate`/`pw_correct`/`sch_star`/`derived_sense`/`a2a`/
  `nws_at_sense`/`foreign_fragment`) — no new typology, no re-translation, DE text
  read-only. `--selftest` uses a synthetic fixture (never real store content — N9) and
  is wired into CI. See [RESULTS_LOG.md](RESULTS_LOG.md) 26-07-2026 for the pilot
  subtype counts (7 REGLUE_SPEC roots, 1077 rows). Partial N14 close — see
  [`pwg_ru/REGLUE_SPEC.md`](pwg_ru/REGLUE_SPEC.md) Sec.7.

### Added — H1632 PWG-sense × DCS attestation pilot join (26-07-2026)

- New
  [research/PWG_SENSE_DCS_ATTESTATION_PILOT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_ATTESTATION_PILOT.md)
  + generator
  [research/pwg_sense_dcs_attestation_pilot.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_sense_dcs_attestation_pilot.py)
  and input builder
  [research/export_frame_sense_loci.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/export_frame_sense_loci.py):
  the first join of **PWG's own sense divisions** to DCS attestation *and*
  frequency, on the frozen H1455/H1456 500-headword frame.
- **The number: sense-level attribution collapses.** 500/500 groups attest at
  lemma level (by construction — the frame was selected DCS-attested), but only
  **52 of 7,746 PWG leaf senses (0.67%)** are grounded to a DCS attestation by a
  shared locus. 10.8% of the frame's 943,877 DCS tokens carry a `m_wordsem` tag
  at all — that is the ceiling on *any* sense-level claim over this corpus.
- **Two ceilings separated.** 12,953 `<ls>` citations hang on structural parent
  sense nodes, unattributable to a leaf sense by PWG's own structure — before DCS
  is consulted at all. The corpus-side residue (86.8% of groups, class `R3`) fails
  on missing texts and vulgate↔BORI locus drift, not on absence of evidence.
- Reuses, never rebuilds: H1453 `sense_frequency.tsv` (`wn` = `m_wordsem` gold),
  H1455 `sense_corpus_concordance.tsv`, H1456 `microstructure.leaf_senses`.
  Deterministic, no LLM in the measurement path; all five inputs SHA-256 pinned.

### Hardened — Codex pipeline-hardening audit, step 1 of 2 (26-07-2026)

- New
  [PIPELINE_HARDENING_AUDIT_2026-07-25.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HARDENING_AUDIT_2026-07-25.md):
  a current-code audit of the single-Max-account headless route, its
  coordinator/audit/promotion boundary, and the offline orchestration cost —
  with the actual one-profile call graph and P0/P1/P2 findings.
- **Two P0-class fixes landed from it.** (1) A Windows timeout could leave a
  **paid descendant alive**, so a killed generation attempt risked an orphaned
  grandchild still burning quota —
  [`proc_tree.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py)
  tree-kill hardening. (2) An unguarded `future.result()` in the threaded audit
  gates meant one worker exception lost the **whole durable audit report**; it now
  becomes a durable rc=3 gate result that conservatively requeues that gate's
  exact keys, and an NWS-quarantine replace failure preserves the previous
  destination instead of destroying it.
- The audit's own release verdict stands: **live promotion is NO-GO** until the
  store/coordinator/TM close seam has a durable journal and startup
  reconciliation. That sealing is **step 2** — it invalidates 7 existing fixtures
  that still pass placeholder preflight paths and v1 outputs, tracked in
  [pwg_ru/CODEX_HARDENING_REBASE_STATUS_2026-07-26.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/CODEX_HARDENING_REBASE_STATUS_2026-07-26.md).

### Added — DE edition-graph export profile: OntoLex-Lemon + TEI Lex-0 (H1629)

- New
  [src/export_de_edition.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py):
  serializes the **German** edition graph — one entry per (key1, homonym) over the
  PWG/PW/SCH/PWKVN/NWS editions — carrying all five H1624 layers (`gloss_lang`
  spans G1, `government` G2, `form_notes`, `citation_edges` G3, `edition_rel` G4)
  as OntoLex-Lemon Turtle **and** TEI Lex-0 XML, plus a manifest. Federates with
  the existing RU / DCS-frequency / grammar graphs on the shared `lemma/<key1>` IRI.
- Rights fence (N9): input allowlist → Cyrillic quarantine → post-serialization
  guard on the emitted bytes. The store's `h` field is deliberately excluded (it
  carries Russian prose); a Russian `sense_tag` is reduced to its ASCII skeleton
  and logged in the manifest rather than exported.
- Golden fixture
  [release/fixture/de_edition/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release/fixture/de_edition)
  from a 22-row DE-only fixture that exercises every layer and every edition
  layer; `--selftest` fails if any layer's count drops to zero, if a TEI pointer
  dangles, or if the output stops being byte-deterministic.
- Mapping + provenance + limitations:
  [DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DE_EDITION_EXPORT_PROFILE_ONTOLEX_TEI.md)
  (+ metadoc). LANG_PARITY entry `de_edition_export_profile_h1629` (SHARED).
- **Not** done: TEI Lex-0 ODD validation (structure-checked only), RDF-parser /
  SHACL round-trip, full-store run, base-IRI `@DECIDE`.

### Documented — data-integrity findings surfaced by the DE export (H1629)

- Measured and reported, **not** silently worked around: 11 store rows carry
  Russian tokens inside the German `de` field; ~110 rows carry Russian
  `sense_tag` prose; and the G1 `gloss_lang` classifier mislabels ~122 of 229
  non-DE spans as Latin/English (77% false-positive rate on the
  `english_content` rule), which also masks those German glosses out of the
  translate path upstream. See
  [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  and the tracking integrity issues
  ([#749](https://github.com/gasyoun/SanskritLexicography/issues/749),
  [#750](https://github.com/gasyoun/SanskritLexicography/issues/750)).

### Documented — German-side editorial principles datasheet (H1634)

- New
  [pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md)
  (+ metadoc): field inventory after H1624 G1–G6 — **derived / voted / undecided**
  with confidence, design fence, G5 (H1306) and G7 (Palsule) blockers, form_notes
  and form_labels. Cross-linked from [pwg_ru.md](pwg_ru.md) §8.0 / §8.4 and deep
  manual §2c.
- Does **not** invent style or abbrev policy; does not rewrite the store.

## [1.62.0] - 2026-07-25

### Added - H1404 Wave 1: review/gold/voting deep manual + sheet↔decisions binding standard

- Deep manual [REVIEW_GOLD_VOTING_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.md)
  (+ metadoc): G5/G6/G7 gate map, 14-script gold-chain census, sheet lifecycle,
  per-gate instrument ruling D6 (DA/Likert/pairwise pilots retired with
  rationale), rights boundary, RU reviewer chapter — answers voted.md items 2+8.
- Binding standard (voted.md item 8): [review_binding.py](src/review_binding.py)
  (`content_hash` stamp + metadata-only `review/locks/*.lock.json`),
  [decisions.schema.json](schemas/decisions.schema.json),
  [validate_decisions.py](src/validate_decisions.py) (rejects unbound/mismatched/
  drifted exports; `--allow-legacy` logged escape),
  [apply_decisions.py](src/apply_decisions.py) (validator-first; G5→run_batch,
  G6→gold_ingest). All 4 sheet generators retrofitted to stamp+lock; retro locks
  minted for h178_da, Kochergina, Renou-v2.
- Starter packet (D10): [build_g5_review_sheet.py](src/build_g5_review_sheet.py)
  (150 live-queue cards) + [build_g6_mqm_gold_sheet.py](src/build_g6_mqm_gold_sheet.py)
  (20 gold cards, MQM 6-label typology); HTML gitignored, locks committed.
- Fixed: [triage_review_queue.py](src/triage_review_queue.py) crash on ord-less
  queue generations + missing `review_id` column; legacy judge-flagged defects
  routed to [review/G5_REJECT_REQUEUE_AUDIT.md](review/G5_REJECT_REQUEUE_AUDIT.md)
  (no retranslation — fenced downstream). Deep-manual §9 rights claim amended
  (2 tracked sheets, `/publish-safety-check` GO).

### Documented - H1624 DH follow-up handoff batch H1626–H1635

- Minted+filled 10 handoffs after German-layers G1–G6: post-vote H1303/H1306,
  compound differs review-sheet, OntoLex/TEI export, citation top-N scans,
  edition-diff UI, DCS pilot, gold methods, editorial principles, Zenodo sidecars.
- Registry: [Uprava handoffs README](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md);
  programme [H1624](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1624-Opus_SanskritLexicography_pwg-german-layers-backlog-ordered_25.07.26.md).

### Added - H1624 G6: derivation/compound conflict flags on portraits

- [enrich_portrait_derivation.py](src/pilot/enrich_portrait_derivation.py):
  conflict / 
eeds_human when compound_status is differs (~4.2k; not
  auto-adjudicated); human_reviewed overlays preserved; --conflict-rate census.
- Portrait structural schema documents the derivation block. LANG_PARITY SHARED
  derivation_conflict_flags_h1624_g6.

### Added - H1624 G4: edition_rel flags on every subcard sense

- [edition_rel.py](src/edition_rel.py) classifies H180 machine subtypes
  (restate, sch_star, a2a, nws_at_sense, derived_sense, pw_correct, …).
- Stamped on promote; [annotate_edition_rel.py](src/annotate_edition_rel.py)
  backfill with PWG gender index; [build_relationships.py](src/build_relationships.py)
  reuses the classifier for sidecar + rollup TSV.
- DE text unchanged. Docs: pwg_ru L8 / Q12; ADDENDA_TYPOLOGY raw-vs-structured table.
  LANG_PARITY SHARED edition_rel_h1624_g4.

### Added - H1624 G3: normalized DE <ls> citation_edges

- [citation_edges.py](src/citation_edges.py) extract_citation_edges: edges
  {raw_ls, siglum, work_id?, renou?, page?, resolver_status map|bib|orphan}.
- Stamped on promote + portrait; [annotate_citation_edges.py](src/annotate_citation_edges.py)
  backfill; raw <ls> remains in de. Coverage: citation_edges.py report.
- Docs: [CITATION_COVERAGE.md](CITATION_COVERAGE.md); LANG_PARITY SHARED
  citation_edges_h1624_g3.

### Added - H1624 form_notes: dedicated nom/voc form-note field

- New top-level store/portrait field orm_notes via
  [extract_form_notes](src/form_labels.py): {case: nom|voc, kind, span}.
- Separate from government (Rektion) and from multi-axis orm_labels.
- Stamped on promote + microstructure; [annotate_form_labels](src/annotate_form_labels.py)
  backfills both fields. LANG_PARITY SHARED orm_notes_nom_voc_dedicated_h1624.

### Added - H1624 form_labels: number / gender / nom-voc / voice markup from DE

- New [form_labels.py](src/form_labels.py) extract_form_labels - structured sibling of
  Rektion government (gender from lex, number sg/du/pl, case_form nom/voc, voice
  act/med/pass). Bare ab n. is not treated as gender.
- Stamped on promote ([promote_final_cards](src/promote_final_cards.py)) and portrait
  ([microstructure](src/microstructure.py)); store retrofit
  [annotate_form_labels.py](src/annotate_form_labels.py).
- Schema fields on final card + portrait structural; LANG_PARITY SHARED
  form_labels_number_gender_voice_h1624.

### Added - H1624 G2: structured government on every DE sense at promote + portrait

- [promote_final_cards.rows_for](src/promote_final_cards.py) stamps government
  from DE via xtract_government (no wait for annotate backfill).
- [microstructure.sense_node](src/microstructure.py) attaches the same field on
  portrait senses; [enrich_portrait_government.py](src/pilot/enrich_portrait_government.py)
  backfills older portraits; schema: [pwg_portrait_structural.schema.json](schemas/pwg_portrait_structural.schema.json).
- [annotate_government.py](src/annotate_government.py) remains the store retrofit.
- LANG_PARITY SHARED government_on_promote_and_portrait_h1624_g2. Floor-only;
  PW capitalized (Instr.) still caught (H1308).

### Added - H1624 G1: durable gloss_lang on PWG {%…%} (DE|LA|EN)

- Stage-0 [pwg_mask.py](src/pwg_mask.py): classify_pct_detail / gloss_lang_spans
  emit {span, gloss_lang, rule_id, offsets} without rewriting DE text; mask treats
  Latin + Wilson English + botanical binomials as {Tn} placeholders.
- Residue [prompt_rule_audit.looks_foreign_literal](src/pilot/prompt_rule_audit.py)
  prefers the same classifier so faithful LA/EN preservation is not requeued.
- Docs: [pwg_ru.md](pwg_ru.md) §4 rule table + §8.0/L0; LANG_PARITY SHARED
  gloss_lang_spans_h1624_g1. Pins: pwg_mask --selftest,
  	est_pwg_mask_gloss_lang_g1.

### Documented — German-original layers + fully clickable Q/N links

- [pwg_ru.md](pwg_ru.md) §8.0: what is layered onto the **German** source in the
  translation process (merge / portrait / NWS owners / mask / Renou·government derived
  from DE) vs post-LLM RU/evidence/review.
- All Q/N detail cells use clickable markdown links (blob + local relative for
  store/review sheets). Deep manual §2b–§2c mirrors this.

### Documented — markup-layer capability map (what Q/N questions layers answer)

- [`pwg_ru.md`](pwg_ru.md) §8: full RU tables — layers L0–L10, **Q1–Q15** answerable
  now (with caveats), **N1–N18** not yet (human gates, drain, rights, WSD, 403 host…).
  Each Q/N row now has a **Детали** cell linking handoff / md / review sheet / live site.
- Deep manual §2b English summary with primary detail links per Q/N
  ([RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)).

### Documented — PWG manuals UX pack (cold start, skills, cookbook, census, H1447 example)

- Deep manual §0 cold start; §5.0 skill-primary path; §11 symptom cookbook;
  §10 points at generated
  [`src/pilot/SCRIPT_CENSUS.md`](src/pilot/SCRIPT_CENSUS.md) via new
  [`src/pilot/script_census.py`](src/pilot/script_census.py) (306 files as of 24-07).
- [`RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md): headless worked example A (H1447
  live-gate + canary); `vid` demoted to historical example B.
- Re-harvested [`LAUNCH_STATS.md`](LAUNCH_STATS.md): **473** windows / 62 roots
  (hard-fail 23.89%); honest note that date span is still mostly Workflow-era.

### Documented — PWG translation manuals truth-pass (headless-first, 24-07-2026)

- Editor manual [`pwg_ru.md`](pwg_ru.md) rewritten from pre-run *plan* framing to **live
  production** status (store 11,603; headless manifest v2; deterministic gates first;
  Sonnet 5 pin; open human gates listed).
- Operator deep manual
  [`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
  §5 production loop rewritten around `/pwg-live-gate` → coordinator prepare → headless
  execute → audit → promote; lanes/counts/parity/selftests stamped 24-07-2026.
- Aligned: [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md), [`AGENTS.md`](AGENTS.md),
  [`README.md`](README.md), [`USE_CASES.md`](USE_CASES.md), [`PIPELINE_HISTORY.md`](PIPELINE_HISTORY.md)
  live-status block, parent [`Claude.md`](../Claude.md) pwg_ru section,
  [`docs/manuals/MAINTAINER_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md).

## [1.60.0] - 2026-07-24

### Fixed — H1618 unpaid four tracks (max-agents guard, cohort engine, C-49 residuals, LANG_PARITY)

- **Track 1 (H1610 structural):** `headless_worker.note(..., preserve=True)` for
  `selfheal-nothing-resolved` / `no-selfheal-fallback` so earlier `budget_exceeded*` notes
  survive; `refuse_starvation_max_agents` hard-refuses `--max-agents N` when `N < selected_keys`
  before any paid call; pins in `headless_worker_selftest.py`; operator note in
  [`RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md).
- **Track 2 (H1437 offline):** new [`src/pilot/cohort_engine.py`](src/pilot/cohort_engine.py)
  + Fable Phase-0 suite `cohort_engine_selftest.py` — **7/7 GREEN** (fake workers only:
  concurrent width, reverse-completion determinism, crash-resume, rejection batching,
  promotion-barrier idempotence, atomic `max_calls` reservation, admitted/parked + coord_dir).
- **Track 3 (telemetry + C-49):** `append_ledger` stamps `translate_agents_spent` /
  `heal_agents_spent` / `budget_stops` / kill/conn; [`no_pwg_residual_ledger.py`](src/pilot/no_pwg_residual_ledger.py)
  backfill+check of H255 w02–w05 documented residuals; defect requeue path records residuals
  by default (`requeue_from_audit --no-residual` to skip).
- **Track 4 (LANG_PARITY):** EN `audit_window_en` wires `build_production_metrics` +
  `--write-requeue` fsha emit (h304 SHARED); h1553 wall_clock half SHARED; h1339 narrowed
  (TN refuse already C6; better-attempt still GAP). Ledger hash-refresh clean.

### Documented — c2 medium50 w1 only-b0/all-nulls forensics (`--max-agents 1` total-spawn starvation)

- [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) id `C2_M50_W1_MAX_AGENTS1_2026-07-24`: measured
  0/3 nulls with single `b0` attempt were **operator misuse of `--max-agents`**, not c2 Pro
  host failure. The flag caps **total** translate+heal spawns; `N=1` starves multi-key
  windows; `selfheal-nothing-resolved` overwrites `budget_exceeded` notes while
  `budget_stops` (23–24) is the smoking gun. Fix re-run without the flag multi-spawned then
  hit a separate c2 Pro **session** limit (`rate_limit`, reset 15:30 Europe/Moscow).
- Comparison table: [`RESULTS_LOG.md`](RESULTS_LOG.md) (24-07-2026 entry). Guardrail: never
  copy canary `--max-agents 1` onto multi-key/heal-capable windows.

### Added — H1458 Track C: publication/release prep for the Sa→Ru TM (D13 terminology + rights-partitioned bundles + datasheet)

- **C1** [`src/terminology_build.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/terminology_build.py)
  populates the curated Sa→Ru terminology dataset (D13, previously a 0-term stub): 2,175 terms,
  one per PWG headword with a `{%...%}` primary-sense gloss span, extracted from the own/PD PWG
  translation memory (sidesteps the D9 MW-English restriction by not touching MW at all this
  wave). `doi_status: reserved` in `release/sa_ru_terminology/manifest.ru.json`.
- **C2** [`src/build_release_bundles.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_release_bundles.py)
  emits rights-partitioned bundles under `release/corpus_tm/`: `public_full.{jsonl,tmx}` (2,392
  own/PD PWG records) and `derived_only.jsonl` (1,093,391 `corpus_lexicon.jsonl` rows,
  structure-only, NO `ru` field — sample of 2,000 committed, full file gitignored/regenerable).
  Rights are classified fail-closed per source work against the canonical
  [SamudraManthanam RIGHTS_TABLE.md](https://github.com/gasyoun/SamudraManthanam/blob/main/nkrya-parallel/export/RIGHTS_TABLE.md)
  (all 131 sources `needs_review`, 0 cleared). `--audit-rights` mechanically asserts 0 grey RU
  surface strings in any tracked bundle — **PASS** on this build.
- **C3** [`TRANSLATION_MEMORY_DATASHEET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TRANSLATION_MEMORY_DATASHEET.md)
  rewritten from a blank template to a filled datasheet per
  [Bender & Friedman (Q18-1041)](https://aclanthology.org/Q18-1041/) + Gebru et al., with the
  per-source rights table for both artifact pools.
  [`papers/A42_corpus_lexicon_resource.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A42_corpus_lexicon_resource.md)
  §8 documents that the rights-partition tooling now mechanizes A42's "RU-translation IP
  documentation" gate (clearance itself remains a human @DO).
- **C4** [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) A42 row
  updated to record the mechanized rights gate.
- **C5** [`release/PUBLISH_PACKET.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/PUBLISH_PACKET.md)
  assembled for the human `/publish-safety-check` gate: what's ready now (own/PD artifacts),
  the per-source clearance checklist for the 131 `needs_review` corpus works, and ordered
  DOI-mint steps. **No publish/DOI/visibility action taken by the agent** — H215/H1458 fence.
- Tracks A (COMET-QE/awesome-align/LaBSE hardening, [H1457](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1457-Sonnet_RussianTranslation_pubgrade-tm-track-a-technical-hardening_22.07.26.md))
  and B (oral corpus, [H290](https://github.com/gasyoun/Uprava/blob/main/handoffs/H290-Opus_RussianTranslation_oral_text_pdf_tm_ingest_07.07.26.md))
  have not landed yet as of this pass (H1457 queued; H290 blocked on an MG-supplied calibration
  sample) — the terminology dataset and release bundles cover the PWG-derived pool only; rerun
  both build scripts once A2/B4/B5 land their graded units.

### Added — H1457 Track A: Sa→Ru TM technical hardening (COMET-QE/awesome-align/LaBSE spike)

- Spike S1 (`src/nn_api.py`): LaBSE embeddings serve locally in-env (no HF token needed);
  COMET-QE does NOT (no cp314 `unbabel-comet` wheel + no local compiler, HF Inference API
  401s unauthenticated, no LLM-judge key available) — logged in
  `research/nn_api_smoketest.md`, per the plan's stop condition this blocks A2 only.
- A1 (`src/build_grade_gold.py`): froze `gold/grade_gold.jsonl` — the H136 320-row sample
  extended with an A/B/C grade via two independent raters (label-policy + qe_composite);
  Cohen's κ ≈ -0.004, itself confirming FINDINGS §70 (proxy-QE is a poor semantic judge),
  not a defect in the frozen labels. Agent-adjudicated, not human — flagged preliminary.
- A2 (`src/tm_grade.py`): wired `--qe comet` through `nn_api.qe()` first, legacy local
  `unbabel-comet` second; added `calibrate-gold` (Spearman ρ vs frozen gold). Proxy ρ≈-0.035
  (well under the 0.40 floor) — PRELIMINARY, activates automatically once QE serves.
- A3 (`src/tm_align.py`): awesome-align-style per-pair `agreement` confidence (LaBSE cosine,
  the independent-aligner check); calibrated gate `agreement>=0.20` beats the flat 97% rate
  (P=1.000, R=0.966 on the committed 30-row precision sample) — `src/ALIGN_GATE.md`.
- A4 (`src/mined_filter_bicleaner.py`): Bicleaner-style composite (length-ratio + A3's
  alignment signal + fluency proxy); gate beats the H224 single-model baseline (P=1.000 vs
  96.7%, R=0.931) on the precision sample. The real 10,132-row mined file is absent from
  every local checkout — documented, not faked; `promote` is ready the moment it exists.
- A5 (`src/tm_saru_align_labse.py`): LaBSE-embedding + margin scoring + a compact
  Vecalign-style monotone DP; pilot on the Leitan Sundarakāṇḍa (2859 L0 units) —
  Vecalign precision@sample = 0.966 (floor 0.80, **PASS**); `src/LABSE_ALIGN.md`.
- A6 (`src/tm_retrieval_eval.py`): retrieval-measurement harness (no-TM vs graded-TMX-as-
  fuzzy-context), engine-pluggable, selftested against mock engines. BLOCKED for a live run
  (no DeepSeek/Anthropic key in this environment) — `src/RETRIEVAL_EVAL.md`.
- CI: new `RussianTranslation gates` step runs all six new/touched scripts' fixture-only
  selftests (no network/model calls).

### Added — editorial decisions dry-run apply (H1556 Track D)

- **`src/pilot/apply_editorial_decisions.py`** — default dry-run CLI over
  `pwg_ru/eval/h1303_abbrev.decisions.json` + `h1306_style.decisions.json` (and
  extra `--decisions` paths). Missing votes → `status: pending_votes` exit 0.
  Real store stamp requires `PWG_RU_ALLOW_EDITORIAL_APPLY=1` (wave-1 never sets).
- Pinned by `python src/pilot/apply_editorial_decisions_selftest.py` (4/4; D1–D3).

### Added — promotion receipt scaffold (H1554 Track B)

- **`src/pilot/promotion_receipt.py`** — pure offline schema v1:
  `AttemptRunBinding`, `PromotionReceipt` (`pwg_ru.promotion_receipt.v1`),
  `write_receipt` / `load_receipt` / `load_receipts`, and
  `reconcile_startup(receipts, observed_store_keys) → ReconcilePlan`
  with buckets `{promote_missing, skip_already_present, error_inconsistent}`.
- Fixtures under `src/pilot/fixtures/cohort_scaffold/` (three reconcile cases).
- Pinned by `python src/pilot/promotion_receipt_selftest.py` (6/6).
- Scaffold only for H1437 Phase-1 prerequisites — **no** multi-profile live
  scheduler, no coordinator wiring, no paid gen, no live store write.

### Added — H1403 A2+A3 production residues (H1553 Track A)

- **Wall-clock auto-derive** in `window_reports.derive_wall_clock_minutes` /
  `build_production_metrics`: when `--wall-clock-minutes` is omitted, derive from
  `mtime(wf_output) - meta.generated_at` and stamp `wall_clock_source` ∈
  `{cli, derived_mtime, unavailable}` on the ledger (never invent tokens).
- **`stage_boundary` events** via `dashboard_events.emit_stage_boundary`, emitted at
  audit start/end so later economy analysis can separate generation wall from operator idle.
- **Promote defect-key refusal** in `promote_final_cards.py`: auto-discovers
  `requeue.defect.keys.txt` (or `--defect-keys`); intersection with incoming keys
  exits non-zero unless `--force` (closes the H255_NO_PWG_W02 promote-then-revert footgun).
- **`promote_ready_partial_clean`** helper + CLI `--ready-partial-report` (default dry-run;
  `--apply` required to write; wave-1 tests use temp stores only).
- Pinned by `test_h1553_wall_clock_auto_derive`, `test_h1553_stage_boundary_emit`, and
  the promote selftest defect/ready_partial block. LANG_PARITY entry
  `h1553_wall_clock_defect_ready_partial` (GAP vs EN; helpers lang-agnostic).

### Added — full-audit improvement umbrella plan (2026 H2)

- `/ask` layered plan after a full RussianTranslation audit: offline wave-1 portfolio
  (H1403 production residues · promotion-receipt scaffold · docs umbrella), then
  health-gated drain, then existing TM/gloss/editorial programmes. Docs under `docs/`:
  [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_full_audit_improvement_2026H2.md)
  (+ `.meta.md`),
  [ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_full_audit_improvement_2026H2.md),
  [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_full_audit_improvement.md),
  [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_full_audit_improvement.md),
  [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_full_audit_improvement.md).
- Indexes (does not supersede) the pubgrade-TM and Sa→Ru gloss `/ask` plans. Wave-1 fences:
  no paid generation, no live store mutation. One handoff per track (A–E).

### Added — PWG per-sense `<ls>`-loci export for kosha sense-reconciliation (H1456)

- `microstructure.py export_sense_loci` — new command, reuses the existing
  `header()`/`split_senses()`/`clean_de()` sense-tree parser (no rewrite). Emits
  `pwg_sense_loci.tsv` (`slp1 hom sense_id gloss_de ls_loci`, one row per leaf sense;
  `ls_loci` = that sense's `<ls>` citations `;`-joined verbatim, unresolved) — the sole
  external input to kosha's
  [sense-reconciliation plan](https://github.com/gasyoun/kosha/blob/main/docs/PLAN_KOSHA_SENSE_RECONCILIATION_2026H2.md).
  Full run: 123,366 records → 189,301 rows, 106,082 headwords, 89.3% non-empty `ls_loci`,
  byte-identical on re-run. Fixed in scope: PWG Nachträge back-references glue two sense
  markers together with no separating space ("1〉b〉…", 2,273 occurrences), which the
  shared `MARK` regex's whitespace lookbehind couldn't see — misattributing the addendum's
  locus to the parent sense; fixed via a local-only preprocess inside the new export path,
  the shared parser used elsewhere in this file is untouched. `pwg_sense_loci.tsv` is
  gitignored (regenerable); `pwg_sense_loci.sample.tsv` (500 headwords, 2,742 rows) is
  committed.

### Added — plan: finish the Publication-Grade Sa→Ru TM (H215) as three parallel tracks

- `/ask` layered plan for **finishing** [H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md)'s
  Publication-Grade Sa→Ru Translation Memory (it is ~70 % built) — new docs under `docs/`:
  [PLAN](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md)
  (+ `.meta.md`),
  [ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_pubgrade_tm_2026H2.md),
  [ARCHITECTURE](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_pubgrade_tm_oral.md),
  [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_pubgrade_tm_oral.md),
  [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_pubgrade_tm_oral.md).
- Three parallel wave-1 tracks from a 5-round `/ask` interview: **(A)** technical hardening (COMET-QE
  grade replacing the proxy, awesome-align calibrated gate, Bicleaner mined-tier filter, LaBSE/Vecalign
  sentence-aligner for prose + oral, a TM-as-retrieval measurement); **(B)** oral-corpus formalization
  from user-provided transcripts (schema-extend SamudraManthanam + a new oral converter, three
  granularities); **(C)** publication/release prep (populate the D13 terminology dataset, fold the TM into
  A42, a Bender/Friedman data statement, rights-partitioned release bundles). Nothing auto-publishes —
  the final publish stays a human `/publish-safety-check` gate.

## [1.55.0] - 2026-07-22

### Fixed — offline control-plane audit and speed hardening (Codex)

- Profile-bound manifest-v2 jobs are now claimed only by their configured account; required slots
  are selected before concurrency slicing and unavailable/parked/unprobed/busy owners fail loudly.
  Valid active jobs in older SQLite queues are crash-safely backfilled; corrupt/unreadable active
  manifests remain unclaimable but retryable after repair, and fail before the dispatch poll loop.
- Missing or corrupt coordinator/Workflow evidence and a crashed sense-shortfall detector now
  fail the bounded run before checkpointing instead of becoming a synthetic zero-clean success.
  Current `summary.usage` cost telemetry is read at its real schema path; explicit unevaluable,
  negative, NaN, and infinite figures remain fail-closed.
- Cached immutable main-worktree discovery (without caching Git failures), one case-exact
  output-directory snapshot per audit,
  and promotion receipt row counters remove repeated Git launches, directory scans, and two full
  26 MB store scans. On the frozen H1339 fixture, the one-run offline smoke retained the exact
  output signature while total time fell 17.842→11.354 s (−36.4%). Full gates at landing (after
  rebase onto the merged H1386 set): 180/180 window tests twice under random hash seeds and
  73/73 language-parity entries clean. See
  [`../docs/PIPELINE_AUDIT_pwg_ru_2026-07-21.md`](../docs/PIPELINE_AUDIT_pwg_ru_2026-07-21.md).

## [1.49.0] - 2026-07-21

### Fixed — coordinator concurrency/durability plausibles P2/P10/P11 (H1420)

- Three PLAUSIBLE findings from the Opus 4.8 adversarial pwg_ru bug-hunt
  ([issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632); C1–C9 shipped in
  v1.47.0), each verified real against the code + callers and fixed in
  [`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py),
  one selftest pinned per defect:
  - **P2** — `_win32_pid_alive` reported DEAD for *every* `OpenProcess` error except `ERROR_ACCESS_DENIED`
    (5), contradicting its own fail-safe comment: a transient/unexpected probe error would falsely reclaim a
    **live** lock into two writers (the A1 double-writer window, H1283). It now leans ALIVE on any error
    except the definitively-dead `ERROR_INVALID_PARAMETER` (87 = no such pid); the classification is extracted
    to a pure `_win32_alive_on_openprocess_error` and pinned by
    `test_h1420_p2_win32_openprocess_error_leans_alive`.
  - **P10** — `promote_ready` commits the store in one all-or-nothing batch, then rebuilt the RU TM *after* the
    per-lease state loop; a raise between the store commit and the rebuild (unreadable batch report,
    no-landed-subcards, a per-lease state error) left store and TM divergent until the next clean run. The
    rebuild now runs in a `finally` (extracted to `rebuild_ru_translation_memory`), pinned by
    `test_h1420_p10_promote_rebuilds_tm_in_finally`.
  - **P11** — `record-output` gated only on `state=='running'`, so after a run was released/recovered and the
    lease re-run, a stale `workflow_result` from the prior run could record against the new run (silent
    misattribution). A new optional `--run-id` (the identity sealed at `begin-run`) must now match the running
    lease's `run_id`; a mismatch is refused before any state is persisted. Pinned by
    `test_h1420_p11_record_output_binds_run_id`.
- All three are lang-agnostic coordinator/lock/promotion machinery (no RU/EN divergence); the two
  `coordinator.py` `LANG_PARITY.md` SHARED entries were re-verified and re-hashed. `window_selftest` 175/175;
  `lang_parity_check` no drift.

### Fixed — EN promotion store write is now durable (fsync-before-replace); P1 verified already-fixed (H1421)

- **P9 (bug-hunt plausible, now fixed):** [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py)'s
  tri-lingual store write was a bare `open('w')` + `os.replace` — **atomic but not durable**: a
  crash/power-loss between the write and the metadata flush could leave a non-durable/truncated
  store even after the rename (and under `--no-backup` that write is the ONLY thing between an
  interrupted write and total loss). It now reuses the RU lane's fsynced `_atomic_write_rows`
  (imported from [`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) —
  `flush()`+`os.fsync()` before `os.replace`), single-sourcing the store writer across both lanes
  (as a bonus both now write `\n` newlines; the old EN write CRLF-translated on Windows). Pinned by
  a new P9 block in `promote_en.selftest()` (fsync-called + round-trip + single-source identity).
  The `promotion_scripts_separate` LANG_PARITY note records the SHARED reuse.
- **P1 (bug-hunt plausible, verified already-fixed):** the concern that `merge_store_rows` replaced
  by sub-card unconditionally — silently downgrading a complete store card when an older/partial
  `wf_output` is re-promoted — was **already resolved upstream by B08 (H1339)**: `merge_store_rows`
  is better-attempt-wins (complete > partial, fewer missing fragments win, ties favour the incoming
  attempt) with pinned regression selftests. No code change needed; recorded for the audit trail.

### Changed — EN/RU convergence W2: shared cross-reference vocabulary + audit reassessment (H1425)

- The cross-reference / degenerate-passthrough vocabulary (`s.`, `vgl.`, `u.`, `Nachträge`, …)
  was two **byte-identical independently-authored copies** — `gen_opt_harness2._DEGENERATE_WORDS`
  (RU generation lane) and `audit_window_en._XREF_WORDS` (EN auditor) — the C-01 drift class the
  codebase already consolidated `portrait_key_iast` for. Extracted to a **dependency-free** shared
  module
  [`xref_vocab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/xref_vocab.py)
  both import (the EN auditor deliberately can't pull in the harness's heavy `pwg_mask`/`corpus_gate`
  stack). Behaviour-preserving; pinned by `test_degenerate_xref_vocab_single_source` (asserts object
  identity). New SHARED ledger entry `degenerate_xref_vocab_shared`.
- **Reassessment finding (recorded in the ledger):** reading both auditors showed W2's convergence
  target is materially smaller than first scoped. `audit_window_en`'s reusable surfaces are *already*
  shared — the German-residue word list via `foreign_literal_guards.py`, the whole-dropped-sense
  SAN-LOSS gate via `sense_count.py` — and its remaining gates (`DUP`/`MISSING-EN`/`MARKUP-LOSS`/
  `xref_only`/`nws_de_locked`) are EN-audit-time-specific **by architecture** (RU per-card fidelity is
  *generation-time* in the harness `accept()`/`countOfField`, not a symmetric Python auditor), i.e.
  intentional divergence — not a wholesale reimplementation to force-merge.

### Changed — EN/RU convergence W1: card-done coverage rule extracted to one shared `--lang` kernel (H1425)

- First wave of shrinking the EN-reimplementation surface (the root cause of the RU/EN drift the
  coverage guard polices). The **FL4 coverage-complete rule** — a card is done iff it has ≥1 slot
  and *every* German-bearing slot carries the target field (not the old ">=1 translated sense" rule
  that hid a 1/40 card) — was an EN-only reimplementation inside `en_residual_keys.py`. Extracted to
  a shared `--lang`-parameterized kernel
  [`card_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/card_coverage.py)
  (`slot_coverage`/`card_done(card, field)`); `en_residual_keys.py` is now a thin `field='english'`
  consumer (output **byte-identical**, verified against the pre-refactor inline logic). A fix to the
  rule now reaches any language that calls it. The `en_coverage_card_done_semantics` ledger entry
  flips **INTENTIONAL-DIVERGENCE → SHARED**. Pinned by `test_card_coverage_lang_symmetric`. NOTE:
  `ru_coverage.py` does a *different*, coarser check (per-root sub-card presence) and still carries
  the FL4 per-slot blindspot this kernel fixes — wiring it in is a tracked H1425 follow-up (a
  behaviour change to a live gate, deferred from this warm-up).

### Added — LANG_PARITY coverage guard: new RU/EN-lane files can't silently escape the ledger

- The parity ledger's drift check only re-verifies files **already** tracked; a brand-new
  language-aware file (a fresh `*_en.py` reimplementation, or a new `--lang`-branching gate) could
  escape parity tracking entirely — the exact hole the C1–C9 EN findings (`audit_window_en.py`,
  `promote_en.py`) grew in. New **coverage guard** in
  [`lang_parity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py)
  (`coverage_check`, wired as `test_lang_parity_coverage`): every language-aware pipeline `.py`
  under `src/`/`src/pilot/` must be **either** referenced by a ledger entry's `files:` **or** listed
  in a new `lang_parity_coverage` `exempt` map with a one-line reason — else CI fails and names the
  file. The 8 existing untracked candidates were classified by an Opus 4.8 (`claude-opus-4-8`)
  8-agent fan-out + adversarial audit: **7 exempt** (read-only samplers / benchmarks / QA-sheet
  generators, each with a recorded reason) and **1 promoted to a ledger entry**
  (`en_residual_keys.py` → `en_coverage_card_done_semantics`, the EN twin of `ru_coverage.py` whose
  card-done semantics must stay aligned). Ledger now 71 entries; coverage 22 language-aware files,
  all tracked or exempt. Verified end-to-end (a synthetic new `*_en.py` fails the guard).

### Fixed — build-frags glob (C7) + German-as-Latin mask drop (C8) + EN backup collision (C9) (H1418)

- **C7 — `build-frags` built the fragment TM from the wrong tree under a custom coordinator dir.**
  In [`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py)
  `promote_ready`, the `frag_prov` **detection** globbed `paths()['artifacts']` (honors
  `PWG_COORDINATOR_DIR`) but the **build-frags** call hardcoded the default-tree glob — so a
  per-run/worktree coordinator dir detected fragments yet built the fragment TM from the empty
  default tree, silently dropping the just-promoted window's fragments. Both sides now use one
  `_frag_prov_glob()` derived from `paths()['artifacts']`.
- **C8 — German glosses opening `In…`/`Ab…`/`Ex…`/`Sub…`/`Pro…` were masked as Latin and dropped.**
  [`pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)'s
  `LATIN_PHRASE` matched German-capitalized homographs of Latin prepositions, so a `{%In den
  Schlusssatz einfallen%}`-style gloss was masked to `{Tn}` and never translated — invisibly
  (restore reinserts the identical German, so the round-trip stayed "100% lossless"). Fixed: a
  homograph opener stays Latin only if **no** German function word follows; `De …` (not a German
  word) remains an unguarded Latin opener. Measured **1 of 192,763** `{%…%}` spans, now kept inline.
- **C9 — the EN store backup could clobber an earlier recovery copy.**
  [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py)
  named the backup with a **second-resolution** timestamp and wrote it with a plain `open('w')`, so
  two lock-serialized runs in the same second overwrote the earlier `.preEN` backup. Fixed to a
  µs+pid+uuid name (`_en_backup_path`) plus the RU lane's **O_EXCL** fsynced copier
  (`_fsynced_backup`, imported — single source).
- Found by the Opus 4.8 (`claude-opus-4-8`) adversarial bug-hunt review (C7/C8/C9 of
  [issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)) — the last of the 9
  confirmed findings (C1–C6 shipped in #634/#636/#638). Selftests: `window_selftest`
  (`test_frag_prov_glob_honors_coordinator_dir_c7`, `test_pwg_mask_german_homograph_not_latin_c8`)
  and `promote_en --selftest` (C9 block).

### Fixed — audit/mask robustness plausibles P3–P8, verified and fixed (H1422)

Six LOW-severity PLAUSIBLE findings from the same Opus 4.8 adversarial bug-hunt
([issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)) that shipped C1–C9
above — verified against real code/callers, all six real, all fixed:

- **P3 — the degenerate cross-reference pass-through lane leaked German into the RU/EN field.**
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  `degenerate_passthrough_card` assigned `field: body` — the German source text, verbatim — for
  stubs it correctly identified as untranslatable (`vgl.`/`s.`/`ff.` cross-reference particles).
  These German tokens are not even covered by `german_residue_scan.py`'s wordlist (it requires
  3+-letter function words), so the leak was previously undetectable by any existing audit. Now
  the target field stays empty; the German remains visible via the `german` key for editorial
  reference.
- **P4 — sense-tier splitting had no open-span guard, unlike the citation-batch tier.**
  [`autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py)
  `_blocks` detected sense boundaries purely from lines matching `_SENSE` ("1)", "2)", …), with no
  `_span_open` awareness — unlike `_cit_parts` (H155). A multi-line `<ls>`/`{#..#}` citation whose
  interior contained a `_SENSE`-shaped locator could be torn across two (sub)sense blocks. Fixed
  by applying the same balanced-span deferral to sense-boundary detection.
- **P5 — `audit_sense_dupes.norm()` stripped `)`/`〉` but not a trailing `.`.**
  [`audit_sense_dupes.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_sense_dupes.py):
  tag `1.` and plain `1` hashed to different buckets, so a real cross-part duplicate with
  mismatched locator punctuation was missed by the dupe check. Now strips trailing `.`/`)` in
  any order; an interior period (`caus. 2`) stays untouched.
- **P6 — `audit_window.run_py`'s subprocess call had no error handling.**
  [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py):
  a `TimeoutExpired`/`OSError` re-raised straight through `collect_cards`/`root_glue_translated.py`
  and crashed the whole audit with no report or requeue, even though `main()`'s gate loop already
  handles a non-`{0,1}` returncode gracefully. Now converts either exception into that same result
  shape (returncode `124`/`-1`) instead of propagating.
- **P7 — the EN `MISSING-EN` hard gate treated cross-ref/abbrev residue as translatable prose.**
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py):
  `has_gloss` fired on ANY non-empty German prose residue, including a bare cross-reference
  apparatus (`vgl. {#foo#} fgg.`) that `xref_only()` already recognizes as non-target — hard-failing
  a sense that was never a translation target the moment its english field was correctly left
  empty. Now `has_gloss` also requires `not xref_only(g)`.
- **P8 — EN `MARKUP-LOSS` summed two marker classes before comparing, letting one mask the other.**
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py):
  `{%..%}` gloss-wrapper count and `<div>` count were added into one combined number, so a dropped
  gloss wrapper could be masked by an unrelated `<div>` gained in the english (net count unchanged).
  Now counts and compares each marker class separately.

LANG_PARITY.md re-verified: `target_field_markup_fidelity_parity_c1` (P3's degenerate lane is
structurally exempt from the C1 fidelity guard — it bypasses `translateBatch`/`healOnly`
entirely) and `subprocess_and_bom_hardening_h316` (P6 only adds error handling around the
existing `encoding='utf-8'`/`timeout=1800` call, both left unchanged) verdicts confirmed to
still hold; 49 stale hashes re-verified and updated. Selftests: `window_selftest`
(`test_degenerate_passthrough_no_german_in_target`, `test_sense_split_never_tears_open_span`,
`test_sense_dupe_norm_strips_trailing_period`, `test_run_py_survives_timeout_and_oserror`,
`test_p7_missing_en_not_fired_on_xref_only_residue`, `test_p8_markup_loss_not_masked_by_unrelated_div`).

### Fixed — EN DUP gate false-flags distinct referents (C2) + EN promote {Tn} guard (C6) (H1414)

- **C2 — the EN within-card `DUP` HARD gate false-flagged distinct proper-name senses.**
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py)
  keyed the duplicate check on `prose(english)`, which **strips** `{#..#}` Sanskrit and `<ls>`
  citations — so two senses distinguished only by their referent (`N. of a serpent-demon
  {#vāsuki#}` vs `…{#takṣaka#}`) normalized to one string and the second was reported as a HARD
  `DUP`, failing `--strict` on faithful output (310 real within-record cases across the EN
  wf files). Fixed to key the DUP `seen`-dict on the normalized **raw** english (referent
  preserved), matching the gate's own contract ("the exact same english"); the `CIRCULAR` check
  keeps prose-`norm`, and a true identical-english duplicate is still caught HARD.
- **C6 — the EN promote lane had no unrestored-`{Tn}` guard.** `promote_en.py` `attach()` wrote
  `r['en'] = en` with no residue check, while the RU lane refuses a card carrying a `{Tn}` mask
  placeholder (`promote_final_cards` C-01 → `UnrestoredPlaceholder`). Fixed by **importing** the
  RU lane's exact `TN_RE` + `UnrestoredPlaceholder` (single source — a look-alike copy is the
  drift that C3 was) and refusing loudly, before any backup/store write.
- Found by the Opus 4.8 (`claude-opus-4-8`) adversarial bug-hunt review (findings C2/C6 of
  [issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)). Selftests:
  `window_selftest` (`test_en_dup_gate_preserves_sanskrit_referent_c2`) and
  `promote_en --selftest` (C6 refusal block). Recorded in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
  (`en_dup_hard_gate_20260704`, `promotion_scripts_separate`).
### Fixed — dead EN card-TM (C3) and rate-limit job-stranding busy-loop (C4) (H1413)

- **C3 — EN whole-card translation memory was 100% dead.** `translation_memory.py build --lang en`
  wrote each sense's translation under the store **column** name (`FIELD['en']=='en'`) instead of
  the **card** field name `'english'`, but the serve-side guard (`tm_card_sane`) and the final-card
  schema require `'english'` — so every EN card-TM hit was silently refused (`sense missing
  english`) and the EN lane re-translated whole cards it already had (wasted spend; RU was
  unaffected). Fixed with a single `CARD_FIELD = {'ru': 'russian', 'en': 'english'}` used by both
  the card builder and the fragment lane (`_FRAG_TRANSLATION_FIELD` now aliases it, so the two
  can't drift again). Classified SHARED in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md).
- **C4 — a rate-limited job could become permanently unclaimable and busy-loop `staged-run`.**
  `max_account_orchestrator.py` incremented `attempts` at claim time but the 429/rate-limit path
  called `finish(…, 'pending', …)` without giving the attempt back (unlike `release_db_claims`), so
  after `max_attempts` rate-limits a job sat `pending` with `attempts == max_attempts` — never
  re-selected by `claim` (`WHERE attempts < max_attempts`), never marked `failed` — permanently
  stranded, and `cmd_staged_run` spun on the un-drainable `pending` count. Fixed by treating a 429
  as a non-defective attempt (`requeue_rate_limited` decrements `attempts` atomically), plus a
  no-progress poll backstop so any residual unclaimable-but-pending state polls instead of
  hot-spinning.
- Found by the Opus 4.8 (`claude-opus-4-8`) adversarial bug-hunt review (findings C3/C4 of
  [issue #632](https://github.com/gasyoun/SanskritLexicography/issues/632)). Selftests:
  `window_selftest` (`test_en_card_tm_serves_english_field_c3`) and
  `max_account_orchestrator_selftest` (C4 rate-limit block).
### Fixed — target-field markup-fidelity guard ported to every promotable lane (C1 / H1412)

- The `<ls>`/`{#..#}` markup-count fidelity guard now runs over the actual **target-language
  field** (`russian`/`english`), not only the `german` source-echo, on **every** lane that can
  promote a card. Previously only the JS batch `accept()` lane carried this check (H1152); the
  heal/presplit stitch, the headless `normalize_batch` (now the production route) and its
  selfheal stitch, and both autosplit stitch writers (`cmd_merge` + `stitch_topup`) counted
  only `german` — so a translation faithful in the German echo but missing a Sanskrit/citation
  span in the Russian/English column (the live H1070 r102 pattern: german 33/33, english 32/33)
  was stitched and promoted with the span silently dropped. All off-batch lanes now reject →
  requeue on a target-field span mismatch. Found by the Opus 4.8 (`claude-opus-4-8`) adversarial
  bug-hunt review; the autosplit change also closes the `<ls>`-only / non-blocking gap (C5).
  Selftests: `window_selftest` (`test_heal_lane_target_field_fidelity_wired`,
  `test_autosplit_stitch_topup_rejects_target_field_drop`,
  `test_autosplit_merge_rejects_target_field_drop`) and `headless_worker_selftest`
  (`test_normalize_batch_translation_fidelity_reject`,
  `test_headless_heal_stitch_translation_fidelity_reject`); classified SHARED in
  [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
  (`target_field_markup_fidelity_parity_c1`).

### Added — speed & orchestration audit: bottleneck ledger + verified action map (H1403)

- [`PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_SPEED_ORCHESTRATION_BOTTLENECK_AUDIT_2026-07-20.md)
  (Fable 5 `claude-fable-5`, 22-agent ultracode workflow: 5 miners → synthesis → 2 adversarial
  lenses per recommendation). **0/8 recommendations survived unmodified (6 weakened, 2 refuted)**
  — the speed frontier is executing already-minted work, not new design: run H1209 medium50
  (parked since 18-07), finish H390 rule 4(a) instrumentation, close three operator-loop
  residues; generation is only ~12–22 % of chain calendar. Registered
  [DEAD_ENDS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
  (H1225 SANLOSS counter fix) and landed the dangling §11 (W3 vidyut-cheda NO-GO).

### Added — Sa→Ru gloss layer wave-4 read-only TM lookup (H1349 W4 — H1349 complete)

- `src/saru_gloss_tm.py` (`GlossTM`) exposes the lemma + root gloss layers as a **read-only**
  lookup for the pwg_ru/mw_ru card path: a Sanskrit lemma/root (SLP1) → ranked candidate
  Russian renderings. Additive consumer only — does not touch the harness TM / store / the
  safety-plan #547/#550 coordinator runtime. Smoke-tested on the published SanskritRussian
  data (`gam`→пришел/отправился/…, `karman`→действия/деяния/…); fixture-backed regression
  test `tests/test_saru_gloss_tm.py` wired into CI. Closes H1349 (waves 1–4).

### Added — Sa→Ru gloss layer wave-3 coverage spike: vidyut-cheda NO-GO (H1349 W3)

- Measured whether `vidyut.cheda` compound segmentation can recover the 78,842 unresolved
  forms. `src/build_compound_split.py` applies a strict precision gate (≥2 tokens + every
  member glossable) and recovers 36.4% (28,673 forms) — but a 2-judge panel scored those
  recoveries at **18% gloss precision / 60% outright wrong**, vs the wave-2 baseline of 85.3%.
  **NO-GO: not wired into the rollup** — vidyut-cheda is a running-text segmenter and shatters
  isolated OOV forms into stem + spurious glossable particle. The 85% layer stays unregressed;
  recommended path (backlog) is the DharmaMitra neural segmenter over the aligned verse text.
  Finding: `gold/saru_gloss_wave3_cheda_coverage.md`; gate has a regression test
  (`tests/test_saru_gloss_wave3.py`, wired into CI).

### Added — Sa→Ru gloss layer measured precision (H1349 wave 2)

- **First accuracy measurement** of the gloss layer (every prior number was coverage). A
  new tier×frequency stratified sampler (`src/saru_gloss_sample.py`) + panel aggregator
  (`src/saru_gloss_aggregate.py`) run a **model-vs-model LLM panel** (Opus 4.8 / Sonnet 5 /
  Haiku 4.5, adversarially adjudicated by Fable 5) over 110 resolutions, judging lemmatization
  and gloss separately (D6). Result: lemmatization **86.1%** (95% CI 78.3–91.4), gloss **85.3%**
  (77.5–90.8) — with the **vidyut** tier the lemmatization weak spot (71.8% vs dcs 94.9% /
  marker 93.3%). Report: `gold/saru_gloss_precision_report.md`; numbers in `RESULTS_LOG.md`.
- `build_rollup_glossaries.py` now also emits `surface_resolution.tsv` (per-form tier · lemma ·
  top-gloss) as the sampling frame — backward-compatible (a new output; existing ones unchanged).
- Panel labels + the frozen sample committed under `gold/` as the scaffold for a human
  spot-check; runs cleanly through the existing `gold_agreement.py` double-review machinery.
  Wave-2 scaffold has its own regression tests (`tests/test_saru_gloss_wave2.py`, wired into CI).

### Fixed — Sa→Ru gloss layer wave-1 defects (H1349 W1.1–W1.3)

- **Pseudo-roots (W1.1).** `build_dcs_maps.py` no longer keeps prefixed verb lemmas that
  fail the root-suffix match as their own roots: the 434 self-mapped `unresolved` rows are
  split into `dcs_lemma2root_unresolved.tsv`, and `build_rollup_glossaries.py` excludes them
  from the root layer (root inventory 3,570 → 3,147 distinct keys; `root_glossary` 1,853).
- **Homograph completeness (W1.2).** The rollup's ambiguity report inspected only the single
  runner-up `cands[1]`; a genuine 3rd+ homograph was silently dropped. It now records the
  full trail over `cands[1:]` (9,521 → 11,289 alternate rows across 9,733 forms).
- **Vidyut ambiguity trail (W1.3).** `build_vidyut_fallback.py` incremented a bare
  `ambiguous` counter; it now writes the competing `(lemma, pos, n)` candidates to
  `vidyut_ambiguity.tsv` (5,952 rows over 4,133 forms), mirroring the DCS schema.
- Each fix carries a regression test in `tests/test_saru_gloss_pipeline.py` (wired into the CI
  RussianTranslation-gates job); `vidyut`/`indic_transliteration` are now imported lazily so
  the pure helpers are testable without the heavy deps. Before/after in
  [RESULTS_LOG.md](RESULTS_LOG.md); the pipeline `glossary/README.md` is now a build runbook
  pointing at the canonical [gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian)
  doc. Published data is **not** regenerated (D8 fences republish behind a human GO).

### Fixed — scoped RU style gate and conflict-safe H1305 repair

- The `ru_style` workflow gate now audits only structured
  `card.records[].senses[].russian` values. Rendered Markdown notes, `differentia`, German
  source text, headings, and footer metadata are excluded. Multiple violating senses still
  aggregate to one original workflow key; ambiguous R2/R3 matches are diagnostic warnings,
  never `FLAGGED_JSON` defects. The EN audit path is unchanged.
- R2/R3 now share one high-precision contextual classifier between rewriting and auditing.
  Matches inside `«…»` or `{%…%}` are protected; only the ratified correction,
  replacement-object, and lexical-use cues are hard. A complete re-audit corrected H1305's
  sampled false-positive claim: of 291 pre-sweep «вместо» occurrences, 279 are hard and 12
  ambiguous; of 24 «в значении» occurrences, 20 are hard and 4 ambiguous.
- Added dry-run-by-default `--repair-from` reconciliation against the original H1305 backup.
  Stable row hashes exclude translation/review/provenance fields and use occurrence ordinals
  for duplicates. Only original, legacy-swept, or newly scoped values are recognized;
  divergent later edits fail the entire apply. The canonical repair restored all 16 reviewed
  ambiguous occurrences with 0 conflicts and preserved the 11,603-row population. Final
  store audit: 0 hard violations, 12 R2 + 4 R3 warnings.
- Every apply now makes an exclusive UTC-timestamped backup, verifies its SHA-256 and row
  count, re-hashes the live store immediately before atomic replacement, and writes an
  ignored JSON evidence report. Consecutive applies were verified to create distinct backups.
  The derived RU card translation memory was rebuilt and validated after repair.

### Added — mechanical RU style sweep: no-ё, terse editorial metalanguage (H1305)

- **Four ratified, deterministic RU style rules applied store-wide and wired for future
  generation** (MG's DA-vote, register rows N7/N12 + the terseness half of N4):
  **R1** no letter ё anywhere in RU output — write е everywhere; the only exception is the
  standalone token «всё»/«Всё» (disambiguating все/всё); the edge case «всё-таки» defaults
  to е («все-таки») like every other ё-word, per the ruling. **R2** «вместо» → «вм.» and
  **R3** «в значении» → «в знач.» in editorial metalanguage. The original sampled
  **0/60** and **0/24** false-positive claim and unrestricted application are superseded by
  the review fix above: the full population contains 12 ambiguous R2 and 4 ambiguous R3
  cases, all restored and now non-blocking. **R4** `ed. Bomb.` → «Бомбейская ред.» in
  **free prose only** — 282 of 283 occurrences (221 standalone `<ls>ed. Bomb.</ls>` + 61
  embedded in a longer citation, e.g. `<ls>R. ed. Bomb. 3,69,4</ls>`) sit inside
  `<ls>…</ls>` and were left **verbatim**: [`src/pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)'s
  `source_key()`/`resolve()` key the citation off that exact Latin text against PWG's own
  bibliography (`pwgauth/pwgbib.txt`, all-Latin index) — rewriting to Cyrillic would break
  source resolution outright; only the store's single genuine free-prose occurrence was
  swept. The in-`<ls>` population (282 occurrences) is a render-time display concern,
  explicitly out of scope here and NOT covered by [H1307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1307-Opus_RussianTranslation_pwg-ru-ls-link-enrichment-panini-spr-dhatup_19.07.26.md)
  either — handed off as a PROPOSED follow-up.
- **Initially applied to the canonical store** (11,603 rows, row count unchanged): 2,029
  substitutions across 1,485 rows (R1=1,713, R2=291, R3=24, R4=1). The scoped repair above
  restored 16 ambiguous R2/R3 values, leaving 2,013 ratified substitutions
  (R1=1,713, R2=279, R3=20, R4=1) and 0 hard residual violations.
- **New** [`src/ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
  (stdlib-only; dry-run default, `--apply`, `--selftest`, `--wf` for the window-gate mode) —
  resolves the store via `store_path.canonical_store` (prints the resolved path before
  writing, per the H805/w06 worktree-loss guard) and exposes `scan_violations()`, a
  read-only detector reused verbatim by the new `ru_style` gate.
- **New `ru_style` gate** in
  [`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)'s
  RU gate commands (same `.merged.md`-reading / `FLAGGED_JSON` shape as
  `translation`/`stage2_mechanical`/`coverage`/`sense_dupes`) — RU-only, deliberately never
  wired into `audit_window_en.py`. Tests in
  [`src/pilot/window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
  (`test_h1305_ru_style_mechanical`) cover ё-word flagging, the «всё»/«Всё» whitelist, the
  «всё-таки» edge case, metalanguage «вместо»/«в значении» flagging, in-`<ls>` `ed. Bomb.`
  (standalone AND embedded) staying unflagged, and a genuine free-prose `ed. Bomb.` hit —
  150/150 green.
- **Prompt HARD RULE 9** added to the `CONV`/`TR` template in
  [`src/pilot/run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
  states R1–R4 for the model; `gen_opt_harness2.py` extracts `TR` from this file by regex,
  so every future-generated optimized harness inherits the rule automatically (verified by
  direct extraction — no separate derivative file to keep in sync). Pinned in
  [`src/pilot/prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)'s
  `RULES` (`ru_style_no_yo` / `ru_style_terse_metalanguage` / `ru_style_ed_bomb_siglum`) so
  a future template edit that drops the rule fails `--fail-on-missing`.
- **LANG_PARITY** entry `ru_style_mechanical_yo_terseness` (INTENTIONAL-DIVERGENCE) — the
  gate-wiring MECHANISM is SHARED-capable (a slot in `audit_window.py`'s existing commands
  list), but the RULES THEMSELVES have no EN counterpart by construction (EN output carries
  no Cyrillic, no ё, no «вместо»/«в значении» abbreviation question). `lang_parity_check.py`
  green (59 entries, no drift after re-affirming 38 pre-existing entries whose tracked
  files' sha256 drifted from this session's additive edits — none of those entries'
  described behavior was touched).
- Full rule table, false-positive measurement, and `ed. Bomb.` markup-placement analysis:
  [`pwg_ru/RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md).
  Provenance: [H1305](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1305-Sonnet_RussianTranslation_pwg-ru-style-mechanical-yo-terseness-sweep_19.07.26.md), Sonnet 5 `claude-sonnet-5`.

## [1.31.0] - 2026-07-19

### Investigated — SANLOSS Nachtrag/corrigenda counter fix ESCALATED, no safe fix found (H1225)

- **[H1225](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1225-Sonnet_SanskritLexicography_sanloss-counter-fix-nachtrag-overcounting_18.07.26.md) set out to fix `count_source_senses`'s over-count on H1150's 8 flagged Nachtrag/corrigenda cards — escalated instead, per the handoff's own conflict rail.** Both of H1150's proposed fix directions were tested against the live store and disproven as *general* fixes: partitioning by `— {#headword#}` sub-lemma boundary (cap to 1 on ≥2 distinct names) fixes 5/8 flags but silently caps three real, currently-healthy, genuinely multi-row Nachtrag cards (`_ap~~h3_00_pwg00` 7 rows→1, `vah~~h3_00_pwg00` 3→1, `iz~~h8_00_pwg00` 10→1), blinding SANLOSS to a future drop of nearly all their real senses; the content-verbatim-check alternative is untestable via the existing offline harness, since `softguard_falseflag_measure.py`'s own reconstruction builds "source" and "candidate" from the *same* store rows, making any verbatim-presence comparison tautologically true. Root cause: the fact that actually distinguishes a bundled-into-one-row card from a genuinely-split-into-many-rows card is the model's own generation-time decision, unknowable when `count_source_senses(raw)` runs pre-generation. **No code changed** — `SANLOSS_HARD_REJECT`/`TNMASK_HARD_REJECT` remain `= false`, byte-unchanged. Evidence: [`src/pilot/sanloss_bundling_fix_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sanloss_bundling_fix_probe.py) → [`pwg_ru/h1112/sanloss_bundling_fix_probe.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/sanloss_bundling_fix_probe.json); full writeup: [`pwg_ru/h1112/H1225_SANLOSS_COUNTER_FIX_ESCALATION_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1225_SANLOSS_COUNTER_FIX_ESCALATION_2026-07-19.md). Provenance: Sonnet 5 (`claude-sonnet-5`), H1225.

### Added — pre-restore {Tn} pairing persisted so the TNMASK false-flag rate is measurable (H1226)

- **`accept()` now persists the pre-restore `{Tn}` pairing TNMASK compares** — the candidate multiset (`got`, `cardTokens(c)`) vs the masked-skeleton multiset (`want`, `tokensOf(INPUTS[k].skeleton)`), stamped on the card as `c.tnmask` **before** `restoreCard` in [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py). Both promote lanes carry it to `provenance.tnmask` on every store row ([`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) RU + [`promote_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py) EN). [H1150](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md) returned **`DO_NOT_ARM` (denominator 1)** precisely because the store dropped this transient pairing — only post-restore text survived; this makes the rate **measurable offline** going forward. **Braces stripped** (`'T1 T2'`, never `'{T1} {T2}'`) so it never reads as a raw `{Tn}` residue in the store; equality is preserved (same bijection both sides). **Additive + backward-compatible:** the 11,603 existing rows are unaffected and **not** back-filled (0 carry the field; the rate stays honestly UNMEASURABLE, not a fabricated 0, until real windows accrue it).
- **Why only `accept()`:** the heal path's `acceptFrag` hard-rejects fragment `{Tn}` mismatches, so no un-rejected expansion reaches a healed/cached card — the main soft-guard path is the only one where a measurable flag survives. Design note: [`pwg_ru/h1226/H1226_TNMASK_PROVENANCE_DESIGN_2026-07-19.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1226/H1226_TNMASK_PROVENANCE_DESIGN_2026-07-19.md).
- **Offline reader** [`src/pilot/tnmask_offline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tnmask_offline.py) applies the *same* equality (`got != want`) off a promoted row (`tnmask_mismatch` / `tnmask_measurable` / `rate_over_rows`); a future H1150-style pass computes `#mismatch / #measurable`. Proven by [`src/pilot/tnmask_persist_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tnmask_persist_test.js) (extracts the real `accept()` from a generated harness — cannot drift) + `window_selftest.test_tnmask_persist_and_offline_detect` (GREEN with the field, RED/not-measurable without it). LANG_PARITY entry `tnmask_provenance_persistence` (SHARED). **`SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` both remain `= false`** — this makes arming decidable on evidence; arming stays a human `@DECIDE`. Provenance: [H1226](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1226-Opus_SanskritLexicography_tnmask-preserve-prerestore-candidates_18.07.26.md), Opus 4.8 `claude-opus-4-8[1m]`.

### Fixed — German-prose-residue store sweep + 3 rejected-card repair (H1302)

- **Store-wide German-prose-residue sweep** ([report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H1302_GERMAN_RESIDUE_SWEEP_REPORT_2026-07-19.md), answering H178 DA-vote rows N16/N17/N19): new detector [`src/pilot/german_residue_scan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/german_residue_scan.py) flags untranslated German prose in the `ru` field outside protected markup (citation *zu*/*bei*, *mit dem <ab>acc.</ab>*, *so v. a.*, connectives, *mit Ergänzung von*), classing each hit a=deterministic / b=retranslate / c=proper-name-FP. **Detector precision 50/50 = 1.00** on a hand-classified sample; the deterministic [`fix_german_connectives.py --store`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_german_connectives.py) pass fixed **690 hits across 486 rows** in the canonical store (citation `zu`→«к», `bei`→«у», `mit Ergänzung von`→«с восполнением», `Mit {#prefix#}`→«С», und/oder/ohne/auch). 465 class-b hits (273 rows / 45 roots) parked to a committed requeue worklist for the next `--no-tm` window.
- **3 rejected cards repaired + re-promoted in place** ([`repair_h178_da_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/repair_h178_da_cards.py)): `nI|…|5)` "Schol. zu"→«Schol. к» (N16), `DA|…|8` "mit Ergänzung von"→«с восполнением» (N19), `gam|…|1` doublet→single attested «возвышаться» (N17); each keeps `review_status=ai_translated` with a `provenance.repairs` note. KATHĀS. 26,9 (N17 arbiter) is absent from every local TM → citation check deferred to [H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md).
- **Prevention (SHARED RU+EN):** shared residue token list in [`foreign_literal_guards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/foreign_literal_guards.py) wired into the RU gate (`prompt_rule_audit`) and EN gate (`audit_window_en`, German-only subset); LANG_PARITY entry `german_prose_residue_h1302` (SHARED); prompt rule added to `1_perevod.txt`/`run_pilot_wf.js` with `prompt` component bumped 1.0.0→1.1.0; `window_selftest.py` fixture added (148/148 green). Provenance: [H1302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1302-Opus_RussianTranslation_pwg-ru-german-residue-sweep-reject-repair_19.07.26.md), Opus 4.8 `claude-opus-4-8[1m]`.

### Added — citation translation-memory: reuse RU translations of record for PWG citations (H1304)

- **[`pwg_ru/COVERED_TEXTS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/COVERED_TEXTS_RU.md)** — census of every text with a Russian translation asset, crossing PWG `<ls>` citation frequency (36,546 distinct refs / 709 abbreviations, via `build_citation_index.py`) against the 119 verse-aligned works in SamudraManthanam `corpus.db` and the 23-work Ignatiev archive. The high-value intersections (MBH. 5,512 refs · ṚV. 3,433 · R. 2,970 · KATHĀS. 1,419 · Manu 1,444 · AV. 1,110 — all verse-aligned) plus the gaps (ŚAT. BR. 1,620 · HARIV. 867 · SUŚR. 277 — no RU; MBH-continuous-Calcutta and R. GORR.-Bengal-recension — no locus concordance). Includes the Ignatiev ingestion queue (Bhāgavata-purāṇa = the top gap), the translation-of-record policy + card schema (`citation_ru` / `citation_ru_src` / `divergence_note`), the per-text locus-mapping scheme, and the retro-application plan. Metadata/counts/loci only — no in-copyright translation text (public repo).
- **[`src/citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py)** — `lookup(prefix, locus)` maps a PWG citation to its corpus passage and returns the RU translation of record (generation-time consult only, never persisted). Two layers: a DB-independent resolver (R./ṚV./AV./Manu clean; KATHĀS. best-effort) and a DB-gated `corpus.db` fetch. Typed non-hits: `text-not-covered` (TS., N18), `locus-not-in-corpus` (uningested Rāmāyaṇa kāṇḍas), `unmapped_locus_scheme` (MBH. Calcutta↔critical + R. GORR. Bengal recension — documented concordance GAPs, **not** misses). `consult_card()` is wired into `corpus_gate.build_card` as an additive, import-guarded `citation_reuse` field. `python src/citation_tm.py selftest` (R. 2,91,26 → hit · TS. 2,3,1,4 → clean miss · MBH./R. GORR. → unmapped) hooked into the CI gates job; parity ledger records the RU-only lookup as INTENTIONAL-DIVERGENCE (no EN citation-TM corpus exists). Provenance: [H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md), Opus 4.8 `claude-opus-4-8` (Fable-locked handoff, MG-authorized tier override).

### Added — gaṇa membership wired into the pwg_ru derivation layer (H1282 follow-up)

- **`pwg_derivation_layer.py` + `enrich_portrait_derivation.py` now carry the Pāṇinian gaṇa** from the external Gaṇapāṭha join ([SanskritGrammar PR #445](https://github.com/gasyoun/SanskritGrammar/pull/445)). The sidecar gains `ganas · gana_sutras · gana_corroborated`, and the portrait block a `gana` sub-block (gaṇa(s) + governing sūtra(s) + a `corroborated` flag when PWG cites that sūtra). **3,264 index rows** get a gaṇa (k1-level — membership is lexical). e.g. aṃśa → saṅkāśādiḥ / P.4.2.80. `--selftest` extended. Opus 4.8 `claude-opus-4-8[1m]`.

### Changed — PWG derivation layer now homonym-precise (H1282 follow-up)

- **`pwg_derivation_layer.py` + `enrich_portrait_derivation.py` upgraded from k1-only attach-all to homonym-precise** via the new SanskritGrammar [`pwg_lid_hom_map`](https://github.com/gasyoun/SanskritGrammar/tree/main/data/pwg_lid_hom_map) (PWG states each entry's homonym as `<h>N`; 100 % of this index's `(k1, hom)` pairs resolve). Derivation and compound carry per-occurrence `L_id`, so each is now pinned to the **exact `(k1, hom)`** — **21,915 of the sidecar's rows are homonym-pinned** (was 0); the enrich script matches each portrait's homonym from its `~~h<N>` filename token and attaches the matching block, k1-level fallback otherwise. Pāṇini stays k1-level by design (its `word2sutra` is headword-aggregated). Sidecar column `homonym_ambiguous` → `homonym_precise`. `--selftest` extended (filename-homonym parse). Opus 4.8 `claude-opus-4-8[1m]`.

### Added — PWG derivation layer for the lexicographic portraits (H1282)

- **PWG derivation/Pāṇini/compound layer joined onto the headword index** ([`src/pwg_derivation_layer.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_derivation_layer.py) → committed sidecar [`src/pwg_derivation_layer.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_derivation_layer.tsv)). Joins the three SanskritGrammar PWG data layers onto `src/headword_index.tsv` by `k1`: **39,266 headwords** gain ≥1 layer — derivation (taddhita base+suffix+class+`<ls>` citation) **5,730**, Pāṇini licensing sūtra(s) **22,322**, PWG compound split **16,788**. Compound is a **cross-check** against the index's existing `compound_members` (47% filled): PWG **agrees 6,176 · fills 6,382 gaps · differs 4,230** (the differs are a review queue). Homonyms: attach-all-and-flag (`homonym_ambiguous`), the same policy as `enrich_portrait_grammar.py`, since no `L_id↔hom` map is committed upstream. Deterministic; reads the canonical SanskritGrammar datasets read-only.
- **[`src/pilot/enrich_portrait_derivation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/enrich_portrait_derivation.py)** bakes a `derivation` block (sibling of `grammar`/`corpus_synonyms`) into a headword's local portraits from the sidecar, following the `enrich_portrait_grammar.py` pattern (dry-run / `--apply`). The portrait store (`pilot/input/`) is local-only, so `--apply` runs on the maintainer's local portraits; a `--selftest` proves the block-attachment logic (attaches to every homonym, preserves fields, sidecar parses). Provenance: [H1282](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1282-Opus_SanskritLexicography_pwg-ru-derivation-portrait-enrichment_19.07.26.md), Opus 4.8 `claude-opus-4-8[1m]`.

### Added — H1110 Phase 6 terminal record + Phase 3/7 residue closed

- **Phase 6 bounded c4 ladder terminated at `HEALTH_NOGO_BY_ENVIRONMENT`** ([PR #534](https://github.com/gasyoun/SanskritLexicography/pull/534),
  confirmation reading [PR #538](https://github.com/gasyoun/SanskritLexicography/pull/538)). The c4 profile is
  mechanically proven bound (`config_dir_fingerprint e96ee464…`, validated roster slot) and every offline
  gate is green, but the measured c4 health latency is **98,625 ms against the strict 30,000 ms ceiling** —
  a `success`/pure-latency reading, not auth or connection, and essentially unchanged from the 16-07
  reading of 104,870 ms. **1 paid confirmation call; canary and batch unspent; zero promotions, zero
  canonical-store writes, zero TM rebuilds.** Resume is one health probe per demonstrated-recovery
  window, never a reroll. Terminal record:
  [H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1110/H1110_PHASE6_C4_LADDER_HEALTH_NOGO_BY_ENVIRONMENT_2026-07-18.md).
- **The production execution route is now the headless CLI (manifest v2)**; the Workflow-from-session
  run route is retired and is forensics metadata only. Recorded as a standing section in
  [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
  so an older runbook's "run it as one `agent()` call from THIS session" no longer reads as current.
- **FINDINGS §93 — declared, validated, and never enforced.** The audit's headline finding (the headless
  executor read a manifest `budgets{}` block it did not obey, with every offline gate green) generalised
  into the execution-route parity discipline: grep for the *enforcement* site, not the config key.

### Added — enforceable coordinator runtime state machine

- Prepared translation leases are now reservations, not runtime. `begin-run` atomically moves a
  batch to `running`; `record-output` requires that reservation and releases it through `auditing`.
  Ordinary execution is capped globally at three. A fourth slot exists only for `staged-run` with
  a fresh, run- and lease-scoped four-profile probe receipt; a fifth lease always fails closed.
- `release-run --confirm-dead --reason ...` records abandoned attempts and restores their prior
  prepared state. `recover-operation --confirm-dead` recovers stale preparation/audit tokens, while
  compare-and-swap completion checks prevent an old subprocess from overwriting newer lease state.
- Preflight, harness generation, normalization, requeue generation, and audit now run outside the
  coordinator state lock with explicit 10-minute preparation and 30-minute audit timeouts.
  Dashboards distinguish reserved and running leases and retain `active_translation_leases` as a
  one-cycle deprecated alias of the running count.
- The four-profile orchestrator writes a credential-safe probe receipt, reserves every dispatch
  batch before workers start, releases retryable/failed workers, and routes successful workers
  through the required audit transition. Real contention tests also closed the mkdir/`owner.json`
  lock-creation race that could previously admit two simultaneous claimers.

### Fixed — canonical-store backup and nominal lease collision safety

- Promotion backups now use exclusive, collision-resistant names and never move or overwrite
  the live canonical store. Identical recovered workflow cards deduplicate, while divergent
  translations or generation provenance fail closed before promotion.
- Nominal coordinator leases persist every canonical input key in `reserved_keys`. Legacy
  active leases are migrated from claim details or execution manifests; an unresolved active
  reservation blocks new nominal work instead of permitting an overlapping paid run.

### Added — H1150 W1-B: offline false-flag rate for `SANLOSS_*`/`TNMASK_*`, with a per-guard arming recommendation

- **Measures; does not arm.** `SANLOSS_HARD_REJECT` and `TNMASK_HARD_REJECT` in
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  both remain `= false`, byte-unchanged. Arming stays a human `@DECIDE`.
- New committed measurement scripts: `src/pilot/softguard_falseflag_measure.py` (verifies
  `pwg_ru/h963/artifact_manifest.sha256` against the git **blob** content first — the
  Windows `core.autocrlf` checkout makes a raw `sha256sum -c` spuriously fail on every text
  file — then recomputes SANLOSS `source_senses` via the real, imported
  `sense_count.count_source_senses` over the promoted store) and
  `src/pilot/softguard_falseflag_accept_run.js` (runs the **REAL** `accept()`, extracted
  verbatim out of an offline-generated harness, the `accept_sensecount_test.js` technique —
  never a hand-copied re-implementation, the [Uprava FINDINGS §82](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)
  anti-pattern).
- **SANLOSS: `FIX_COUNTER_FIRST`.** 8/8 flags found in the frozen promoted-store evidence
  (865-card denominator) are false flags (0 true drops) — every one is a Nachtrag/corrigenda
  card bundling correction points across multiple distinct sub-lemma blocks into one stored
  sense; `count_source_senses` correctly finds each sub-block's own line-opening ordinal (a
  class H960's mid-prose cross-reference hardening doesn't target), inflating the expected
  count even though no content is missing. Fix suggestion recorded in the report.
- **TNMASK: `DO_NOT_ARM`.** Zero usable frozen evidence: TNMASK's real check compares the
  pre-restore candidate to the masked source skeleton, and the promoted store holds only
  post-restore text — that pairing is not preserved for any real historical card. Zero
  residual `{Tn}` tokens across all 11603 promoted rows (corroborating H1110 C-42) and zero
  non-zero `tnmask_mismatches` readings anywhere in the tracked repo. Insufficient-evidence
  verdict, not a verdict on the guard's expected quality.
- Output: [`pwg_ru/h1112/softguard_falseflag_rate.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/softguard_falseflag_rate.json) +
  [`H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md).
  Honest limit stated in both: frozen evidence is one route under one payload regime — the
  rate bounds the false-flag class, it does not prove the live rate. Regression gate
  re-measured green: `window_selftest.py` 142/142, `lang_parity_check.py` clean, both
  `HARD_REJECT` consts unchanged.

### Added — H1152: the EN lane's three offline guards named by H1070's conditional GO (scaffolding, not activation)

- **Honest framing, stated once and not softened anywhere in this entry:** none of this
  unblocks the EN lane. The store still carries **0 EN rows**; `promote_en.py` was not run
  (`git diff origin/master --stat -- src/pilot/promote_en.py` is empty); no live judge call was
  made. This is offline scaffolding so H1070's conditional GO is cashable the hour a
  judge-tier profile frees — a human `@DO`, not something this session performed.
- **Guard 2 (the only hard guard) — root cause, not a counter patch.** `accept()`'s
  `<ls>`/`{#..#}` fidelity check (`countOf()` in
  [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py))
  counted spans **only in `sense.german`**, the source-echo field the model reproduces
  verbatim — never in the actual translation field (`sense.english`/`sense.russian`). Proven
  against the live H1070 r102 row (`vac~~h0_00_pwg00`): `german` carried 33/33 expected
  `{#..#}` spans (the pre-existing check passed clean) while `english` carried only 32/33 —
  the `{#uc#}` inside a `<F>` footnote was dropped **only** from the field this guard never
  inspected. Added `countOfField(card, field, re)` and a second hard check in `accept()`
  running the identical count over the real target-language field (`TARGET_FIELD`, the same
  `field` constant already used to build `RESTORE_SPEC`). Landed in the accept path (not the
  `audit_window_en.py` HARD-flag fallback H1070 named) — SHARED code, both lanes get the
  fix. Fixture: [`accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js)
  reproduces the exact r102 shape, proven RED before this change (against the pre-fix
  `accept()` via a `git stash` diff, the fixture is silently accepted) and GREEN after.
- **Guard 1 (cheap):** a German-polyseme checklist under `term-mistranslation` in
  [`gen_fidelity_judge_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_fidelity_judge_en.py)'s
  judge RUBRIC (Vergleich, braut/Braut, gelten, Zug, anführen, …) and a matching HARD RULE 5
  in [`tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt):
  pick the sense the Sanskrit lemma licenses, never the frequent German sense. Markup stays
  intact and the English reads fluently for this error class (H1070 r155/r119) — no
  deterministic gate can see it, so this is judge-rubric + prompt only.
- **Guard 3 (cheap):** extended
  [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py)'s
  soft-flag machinery with `XREF-ONLY` (a sense whose German is nothing but a
  cross-reference apparatus — "Vgl. {#foo#} fgg.") and `NWS-DE-LOCKED` (German prose trapped
  inside a `{#..#}` span — an NWS masking miss that never reached the translator), so
  coverage stats stop counting H1070's dominant residual class (12/170 FU1 rows) as
  translated. Both SOFT — never `--strict`-blocking.
- [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md):
  3 new ledger rows (guard 2 `SHARED`; guards 1 and 3 `INTENTIONAL-DIVERGENCE`, each with its
  EN-only rationale) plus 38 collateral hash refreshes (`--update-hash`, no logic touched —
  pure same-file co-location drift from this session's purely-additive diff, individually
  confirmed against the diff before refreshing). `lang_parity_check.py` clean at 53 entries
  (baseline **50**, not the handoff-cited 49 — `origin/master` has moved since H1152 was
  minted).
- `window_selftest.py`: 2 new content-check tests
  (`test_h1152_guard1_en_polyseme_checklist`, `test_h1152_guard3_xref_only_and_nws_de_locked`);
  the existing `test_h960_accept_sanloss_soft_gate` now also exercises guard 2 via the
  updated `accept_sensecount_test.js`. Full suite: **139/139 green** (baseline measured this
  session: **137/137**, not the handoff-cited 135/135 — same staleness).

### Added — H1110 Phase 2: enforce headless fidelity and spend bounds (12 live-route gaps)

The post-H1080 audit ([PR #524](https://github.com/gasyoun/SanskritLexicography/pull/524)) ranked 12
live-route gaps; this fix closes them, each behavior-pinned (assert the value at the executing
boundary, not a constant):

- **R3 agent-budget enforcement** — `headless_worker.py` enforces `manifest['budgets']`
  (`max_translate_agents`/`max_heal_agents`/`max_agents`) + a `--max-agents` override at the `call()`
  choke point; a refused call consumes no spawn. The budgets block was previously never read by the
  executor.
- **R4 timeout clamp** — every subprocess clamped to `min(operator, budgets.timeout_ceil_ms, 180000 ms)`.
- **R5 cost telemetry** — the CLI wrapper's usage/cost survive into `summary['usage']` (summed across
  calls, authoritative `observed_cost_usd`, `cost_evaluable`, `missing_usage_calls`) instead of being
  discarded — no more silent `STOP_COST_UNEVALUABLE`.
- **R2 grammar-token twin** — `card_token_multiset` counts `record.grammar` + `sense.german` via the
  shared `card_fields.TOKEN_FIDELITY_FIELDS`, matching JS `cardTokens`.
- **R6 fragment-TM v2** — per-sense `owners[]` flow harvest → sidecar → serve → stitch; a v1
  (ownerless) row is a live cache miss (re-translated, still audit-readable), so a warm stitch no
  longer regenerates null-`h` rows.
- **R7 degenerate-card schema** — a degenerate stub emits `{h:'', grammar:''}` (honest source
  identity), so `validate_final_card_schema` passes and one xref stub cannot refuse a whole paid window.
- **R8 / P-1 manifest gates** — duplicate `selected_keys` rejected (multiset via `Counter`);
  `batches`/`presplit` keys outside `selected_keys` refused before any spawn.
- **R9 kernel-backed active-call lock** — `ActiveCallClaim` holds an OS lock (fcntl/msvcrt) the kernel
  releases on process death (no PID/TTL/stale reclaim), so a tree-kill no longer strands a permanent
  per-profile DoS. This is also the P-2 cross-process serialization ("two launches on one fingerprint
  serialise"); `max_wide`/`stagger` are marked advisory intra-process hints.
- **P-3 route enforcement** — a foreign `execution_route` is refused at execution, before any call.
- **R10 `--stop-before-promote`** — skips promotion and writes a durable, self-hashing, hash-bound
  `AWAITING_REVIEW` terminal checkpoint after a clean audit (store and TM untouched; audit-rejected
  output never becomes AWAITING_REVIEW).

### Changed

- Operator docs (`AGENTS.md`, `README.md`) now name the **headless / manifest-v2** route as
  production; the Max-Workflow lane (`run_pilot_wf.opt2.js`) is retained for forensics only.

## [1.16.0] - 2026-07-17

### Added — H1151: behavioral pin for the grammar-`{Tn}` restore (premise found already fixed)

- **The handoff's diagnosed defect no longer exists on master.** The 13-07-2026 H858 diagnosis
  (RUN_LOG:909, live on `gokzuraka` — `"grammar": "{T2}"` promoted) predates the C-01
  centralization ([H963](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/card_fields.py)/H1080):
  both restore lanes (plain `restoreCard` and the heal/stitch path, which restores `rec.h`/`rec.grammar`
  **before** `owners.push`) now read `RESTORE_SPEC = card_fields.js_restore_spec(field)`, whose record
  level is `('h', 'grammar')`. Verified empirically, not by reading: a synthetic harness generated from
  current master restores `record.grammar` `{T2}`→value in 8/8 behavioral checks. Stated per the
  honest-close pattern — this release pins the fixed behaviour, it does not fix anything.
- [`src/pilot/grammar_restore_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/grammar_restore_test.js)
  — behavioral pin in the house pattern ([FINDINGS §82](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md):
  extract the REAL emitted `restore()`/`restoreCard()`/`RESTORE_SPEC` from a generated harness, never a
  hand-written copy). 8 checks: spec keeps `grammar`+`h` at record level; the gokzuraka shape (`{T2}` in
  `record.grammar`) restores; card/sense fields unregressed; no `{Tn}` survives; out-of-range `{T9}`
  stays literal (C-42: never synthesise). Wired into `window_selftest.py` as
  `test_grammar_field_restore_behavioral` (synthetic-harness generation, zero paid calls) — suite now
  **136/136 green**; a future edit that drops `grammar` (or `h`) from the record-level restore fails
  the suite, not the store.
- **Blast radius, report-only (store untouched):** the main-tree `pwg_ru_translated.jsonl`
  (11,603 rows) carries **zero** `{Tn}` tokens in ANY field — the promoted store rows have no
  `grammar` field at all (grammar is card-level, read by consumers from cards, not store rows), and
  the historical `{Tn}` residue (670 rows incl. gokzuraka's class) was already repaired by
  [PR #510](https://github.com/gasyoun/SanskritLexicography/pull/510)/[PR #517](https://github.com/gasyoun/SanskritLexicography/pull/517).
  Nothing to repair; nothing was repaired. `node --check` on a fresh generated harness: OK.
- LANG_PARITY ledger: 28 entries tracking `window_selftest.py` re-verified and re-hashed
  (`--update-hash`); the added test is language-agnostic (RESTORE_SPEC is lang-parameterized;
  the record level does not branch on `--lang`).

### Added — H1080 follow-up: the 468 reconstructed headwords are now marked (owner-authorised 17-07-2026)

- **`provenance.h_reconstructed` on 468 rows** (+ `iast_reconstructed` 462, `grammar_defaulted_empty`
  468). [PR #510](https://github.com/gasyoun/SanskritLexicography/pull/510) repaired the store, and its
  `{Tn}` half is evidence-based (668/670 restored from content-addressed sources; the 2 unrecoverable
  `banD` rows quarantined rather than guessed). Its `h` half is not: `canonical_record_head()` *derives*
  a head from the row's own key (`gam~~h0_45_upa` → `'upagam'`, every `vid~~*` → `'vid'`), because the
  model-authored `h` was destroyed at the stitch before it was ever persisted and no offline source
  exists ([Uprava FINDINGS §94](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). The
  derivation was unavoidable; being **silent** was not — provenance still read the original
  `generator`/`generated_at`, so 468 derived values were indistinguishable from model-authored ones,
  and `h is None` falling 468 → 0 cleared the only query that could find them (§95). **No `h` value was
  changed**; the markers make them auditable, not correct. Query `provenance.h_reconstructed == true`
  for the re-translation worklist.
- [`src/mark_reconstructed_headwords.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mark_reconstructed_headwords.py)
  — recovers the 468 by diffing PR #510's pre-repair backup (SHA-pinned to its report), aligning on
  fields the repair never rewrote, and refusing to write unless every number matches that report.
  Dry-run by default, idempotent. Report:
  [`pwg_ru/h1080/H1080_RECONSTRUCTED_HEADWORD_MARKERS_2026-07-17.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1080/H1080_RECONSTRUCTED_HEADWORD_MARKERS_2026-07-17.md).
  Measured cost of the derivation: 468 rows collapse onto **14** distinct heads, and
  `vid~~h0_00_pwg00`/`vid~~h2_00_pwg00` — different homonyms by their own keys — both derive to `'vid'`.

### Added — H1149: per-cohort clean-rate report (W1-A) + the D-1 debt worklist + regression guard

- **`src/pilot/cohort_clean_rates.py`** — stdlib-only, read-only per-cohort clean-rate report
  (Ruling R3 of the [PWG_RU_UNFREEZE plan](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md):
  narrow-and-measure before draining — **gates every pwg_ru drain in the repo, including H255's
  no-PWG lane**). Partitions the 11,603-row store into `no_pwg` (layer ∈ {pw,sch,nws,pwkvn},
  5,696 rows excl. debt) / `root_upasarga` (pwg-layer keys resolving into `verb_worklist`'s
  verbs01 root universe, 5,120 rows) / `nominal` (pwg-layer, everything else, 319 rows) — 0
  unassigned, `rows + 468 == store_rows`. `no_pwg`'s clean rate (**62% median, range 41–69%**) is
  **consumed verbatim** from the H911 census, never recomputed; verdict **BELOW_BAR**.
  `root_upasarga`/`nominal` are reported **INSUFFICIENT_EVIDENCE**: the one RUN_LOG.md sample for
  each cohort (Stage A+B's 401/484 for 4 verb roots; `nominal_w1_100small`'s 100/100 promoted)
  cannot be bound to the cohort's CURRENT store population — Stage A+B's specific roots
  (`sTA`/`BU`/`as`/`i`) are verifiably absent from today's store, and the nominal window's own
  RUN_LOG entry documents that `audit_window.py`'s glue gates crash on nominal windows, so
  "promoted" there is a generation-success count, not an audit-clean count. **All-cohorts
  non-CLEARS_BAR is a PASS of this deliverable** — the measurement is commissioned to be capable
  of killing the 80% bar with data, not to reach a good number; whether/how to lower the bar is a
  human `@DECIDE`. Outputs:
  [`pwg_ru/h1112/cohort_clean_rates.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/cohort_clean_rates.json) +
  [`pwg_ru/h1112/H1112_COHORT_CLEAN_RATES_2026-07-17.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1112_COHORT_CLEAN_RATES_2026-07-17.md).
- **D-1 debt worklist, `pwg_ru/h1112/h_reconstructed_worklist.jsonl`** — 468 lines, one per
  `provenance.h_reconstructed == true` row, collapsing onto the **14** distinct derived heads PR
  #510/#517 already measured. The standing re-translation worklist; discharge requires an
  authorized live run, not this read-only report.
- **D-1 regression guard, `cohort_clean_rates.assert_h_reconstructed_regression`** — asserts the
  store's `h_reconstructed` count stays exactly 468 unless an authorized re-translation manifest
  (`pwg_ru.h_reconstructed_retranslation_manifest.v1`) documents the exact decrease. Guards the
  precise failure class that already happened once: PR #510's underlying `h is None` count fell
  468 → 0 and became invisible to the only query that could find it
  ([Uprava FINDINGS §95](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). Wired into
  `window_selftest.py` as `test_h_reconstructed_regression_guard` (proven both directions against
  a deterministic synthetic store: 467 markers → `AssertionError`, 468 → clean pass, a matching
  authorized manifest → accepted); **live-proven against a scratch copy of the real canonical
  store** (mutate to 467 → guard fails; restore → guard passes; the shared canonical store itself
  was never written to). Suite now **137/137 green**; LANG_PARITY ledger: 28 stale entries
  re-verified/re-hashed (pure `window_selftest.py` append, no logic they track changed) + 1 new
  SHARED entry `h_reconstructed_regression_guard_h1149` — **50/50, no drift**.
- **Read-only this wave:** the canonical store was never mutated (verified: 11,603 rows / 468
  markers, unchanged before and after). `SANLOSS_HARD_REJECT`/`TNMASK_HARD_REJECT` remain `false`;
  `promote_en.py` never ran (store still carries 0 EN rows).

- **Manifest-v2 production launch contract.** New live manifests bind a logical profile slot,
  canonical `CLAUDE_CONFIG_DIR` fingerprint, execution route/lane, exact model and validation
  method, plus an exact per-key `real | synthetic_control` map. V1 remains readable for historical
  audit but cannot be newly promoted. Synthetic controls are never promotable.
- **Profile and concurrency enforcement.** Coordinator prepare/requeue accepts the profile binding;
  orchestrator and bounded staged-run expose `--only-profile`, verify both roster slot and config
  fingerprint, and every headless manifest holds one cross-process active-call claim keyed by that
  fingerprint. Two c4 manifests therefore cannot call concurrently across admitted production entry
  points; `max-wide=1` remains an independent within-manifest limit. Because Workflow cannot prove
  its config directory or join that host lock, profile-bound v2 production is CLI/headless-only and
  a bound generated Workflow template aborts before its first agent call.
- **Windows CLI and probe policy fail closed.** Bare `claude` is resolved with `shutil.which`; a
  Windows npm shim is invoked through its Node CLI entry or refused, never handed back unresolved.
  Probe telemetry names its policy and lane, requires a representative schema-valid response, zero
  connection errors, and latency strictly below 30 seconds; a supplied verdict that contradicts the
  measured gate is refused.
- **Bounded staged-run retained from PR #495.** The dry-run-default, opt-in execution adapter keeps
  cumulative window/call/clean/cost ceilings, checkpoint restart, prepared-plan scope, and strict
  unevaluable-cost failure. It is carried by the replacement launch-control branch rather than
  merged independently.

- **H963 correction-evidence reconciliation.** Reclassified the 2 h 10 min offline campaign
  honestly (108-agent subworkflow: 98 minutes): 87 provisional candidates resolve to 49 confirmed,
  9 plausible, 1 mixed, 19 merged, and 9 refuted/dropped. Withdrawn the unsupported
  `SAFE` / `COIN-FLIP` / `DOOMED` and route-independent deliverability projections while preserving
  raw pilot outputs and the append-only correction history. Regenerated the three evidence JSONLs
  with explicit `null` withdrawal fields and a repo-relative artifact manifest. `window_selftest.py`
  now executes and reports every defined test even when an earlier test fails. The three pre-existing
  SHARED parity diffs were reviewed as language-neutral, and ledger hashes were updated only through
  `lang_parity_check.py --update-hash`; parity is green.

- **H1070 — PWG→EN Fable-tier gold adjudication vs the MW TM + scale-up go/no-go.** First
  Fable-grade verdict on the FU1 (Sonnet 5) tranche and re-adjudication of the exact S7
  frame with Monier-Williams quoted per entry as the adversary: 170 sense rows, combined
  wrong-sense 4/170 = 2.35% Wilson [0.92%, 5.89%], FU1 3/102 = 2.94%, zero new
  MW-TM contamination, zero register-mismatch. Verdict **GO (conditional)** with a standing
  per-tranche decision rule (≤5% GO / >10% NO-GO / omission always blocks) and three named
  guards (German polyseme judge line, `{#..#}`-in-footnote token check, DE-RESIDUE
  cross-ref/NWS extension). Evidence + rulings: `pwg_ru/h1070/` (adjudication report,
  go/no-go memo, 170-row gold JSONL, recomputable stats scripts). Adjudicator Fable 5
  (`claude-fable-5`); generation under judgment Sonnet 4.6 (`claude-sonnet-4-6`, pilot) and
  Sonnet 5 (`claude-sonnet-5`, FU1).

### Fixed — H1080 / H963 packet Step 2 (C-01, C-02, C-42, C-04)

- **Canonical store repaired and sealed.** A hash-locked dry run and atomic replacement repaired
  668 placeholder rows and 468 null record owners, quarantined only the two irrecoverable `banD`
  rows, and produced a clean 11,603-row store (zero raw `{Tn}`, zero null `h`). The original
  11,605-row store and the two quarantine payloads remain uncommitted but hash-addressed; the
  tracked `pwg_ru/h1080/` report records before/after, backup, quarantine, and one-time TM hashes.
  A second repair invocation is a verified no-op.
- **Promotion now fails closed independently.** `save_and_audit`, `audit_window`, autosplit/top-up,
  and `promote_final_cards` preserve and validate record `h`/`grammar` plus homonym boundaries.
  Promotion refuses invalid final schema, unresolved tokens, malformed or foreign provenance,
  synthetic controls, duplicate results, and a missing store unless the operator explicitly uses
  first-run-only `--init-store`. Backups are copied/fsynced and replacement is atomic.

- **One field set for restore and promote ([`src/card_fields.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/card_fields.py), C-01).**
  `restore_card` and its JS twin unmasked 3 fields while `promote_final_cards.rows_for` read
  6, so `card.iast` / `record.h` / `sense.tag` / `sense.differentia` were promoted with their
  `{Tn}` intact — **670 of 11,605 store rows carry a raw placeholder, 223 of them a headword
  reading literally `{T104}`** (re-verified against the live store this pass). Both lanes and
  the promoter are now driven from one constant; the JS list is interpolated, not re-typed.
  `promote_final_cards` additionally refuses any row still holding a `{Tn}`.
- **The stitch keeps record identity (C-02).** Both stitch lanes built `records: [{senses}]`,
  dropping record-level `h`/`grammar` unconditionally and collapsing homonyms into one flat
  record — hence **468 rows / 20 sub-cards with `h: null`** (403 `batched-masked` + 65
  `topup`). The flatten now carries each sense's owning `(h, grammar)` and `stitch_records`
  rebuilds one record per owner, preserving document order.
- **Out-of-range `{Tn}` is counted and refused (C-42).** `restore_text` returned an unmapped
  token verbatim with no counter, no log and no reject; both lanes now count it and refuse
  the card rather than promote known-corrupt content.
- **The record contract runs on live output (C-04).** `validate_final_card_schema` — the only
  component encoding `record.required = {h, grammar, senses}` — had **no live caller**: its
  sole invocation was a CI step against a hand-made *passing* fixture. It is now wired into
  `save_and_audit` **before** the write and has no production escape hatch. Audit and promotion
  independently run the same contract. `RECORD_REQUIRED` is not relaxed.
- **`window_selftest` no longer stops at the first failure.** The runner was a bare
  `for test in tests: test()`, and the human-gated language-parity gate sits at position 105
  of 131 — so **27 tests (20.6%) were dark indefinitely**, including `pwg_mask` and four
  heal-lane tests. Now isolated, reporting `ran/defined`: **135/135 run, 134 pass**, the lone
  failure being the parity gate that is red by design.

### Added

- [`src/backfill_tn_residue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/backfill_tn_residue.py)
  — dry-run-first, source-hash-locked restoration from exact raw inputs or historical harness
  placeholder maps. The complete evidence chain deterministically repairs **668/670** placeholder
  rows and all **468** null headwords; only two malformed `banD` rows require quarantine.

- **Bounded staged-run integration (opt-in, default-off) — H963.** New standalone module
  [`src/pilot/bounded_staged_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py)
  drives the max-account staged-run path (`probe_fleet` → `cmd_run_once` → `cmd_record_done`
  → coordinator `promote-ready`) under the `bounded_supervisor` control loop, one prepared
  lease per window. Zero edits to `max_account_orchestrator.py` / `coordinator.py`; every
  existing command and default is unchanged. The **default action is a dry-run planning view**
  that makes ZERO generation calls (prints the scoped work, ceilings, account allocation,
  checkpoint path and stop policy); a live drain requires the explicit `--execute` opt-in AND
  a healthy fleet probe. Lease scoping (`only_external_ids={root}` + per-`--lease-id`
  promotion) keeps transient/defect/pending/historical/unrelated-plan work out of the current
  run; deterministic restart from the checkpoint re-runs no completed lease (exactly-once, on
  both the loop's `completed_window_ids` and the coordinator's promoted-terminal idempotence).
- **Bounded-supervisor ceilings + cost fail-closed — H963.**
  [`bounded_supervisor.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_supervisor.py)
  gains opt-in `max_calls` (`STOP_CALL_COUNT`), `max_clean` (`STOP_CLEAN_QUOTA`) and a
  `strict_cost_fn`; a window whose cost is UNEVALUABLE under an active cost ceiling now stops
  the run closed with the distinct `STOP_COST_UNEVALUABLE` reason instead of the legacy
  silent-zero. `calls_spent`/`clean_total` persist across the checkpoint. All new params are
  `None`-default, so the existing behaviour and all prior tests are unchanged.
- **Economy-ledger opt-in strict gate — H963.**
  [`economy_ledger.gate(..., strict=False)`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/economy_ledger.py)
  and a `--strict` CLI flag: legacy (default) still SKIPS a ceiling whose value is `None`
  (unchanged for every existing caller); `strict=True` treats a requested-but-unevaluable
  ceiling as a fail-closed breach (distinct `unevaluable` marker). Missing accounting data is
  never treated as within-ceiling. Both modes are covered by tests.
- **Tests + CI.** New
  [`bounded_staged_run_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run_selftest.py)
  (9 cases: plan scope, dry-run-makes-no-call, historical-jobs-excluded, clean completion,
  restart/no-dup, ceiling exhaustion, cost fail-closed, consecutive-empty, audit seam), +5
  bounded-supervisor cases, +1 economy-ledger both-modes case; wired into the CI gate block.
  No translation prompt or semantic-policy change; no live generation, promotion, store write
  or TM rebuild.

- **Provenance-bound mixed-lane requeues.** Each lease now seals its initial execution
  manifest as the immutable key universe and stores every pending retry key with the path
  and SHA-256 of the audit report that classified it. `record-output` rejects duplicate,
  overlapping, foreign, or category-drifted retry sets; selecting one transient/defect lane
  carries the other through promotion and later attempts. Attempt directories materialize
  their exact key set and conservative defect-fragment hashes, while orphaned `rqNN-*`
  directories are preserved, reported, and skipped by allocation.

- **Requeue provenance and staged-scope follow-up.** Coordinator requeues now create an
  immutable attempt directory and execution manifest for the exact retry keys, retain the
  initial and prior manifest history, and read the next retry list from the latest audit.
  An unpromoted `ready_partial` lease must promote its verified subset before retry preparation.
  Staged acceptance counts only prepared headless windows, while residual-only planner chunks
  are reported and skipped until the requested number of eligible windows is prepared.

- **Audit-bound promotion and restart safety.** Coordinator recording now fails closed:
  only a provenance-valid `clean` audit becomes ready, and only explicit
  `needs_requeue`/`transient_only` audits can expose a verified clean subset. Every
  coordinator result is bound to its execution manifest with exact-one key coverage;
  promotion revalidates the audit and clean-artifact hash. Control files use atomic
  replacement, record-level grammar masks restore in Workflow/headless paths, staged
  orchestration is plan-scoped, and the no-PWG planner skips durable known residuals.

- **Four-profile production-readiness — verify H920 + earn every offline-earnable scale gap (H960, offline).**
  Verified H920 (every offline gate green) and closed the six load-bearing gaps blocking four-profile
  nonstop scale, each pinned by a selftest and each **SOFT / report-only by default** (telemetry, no
  reject/requeue — arming a hard reject is a deliberate owner-gated step measured on live traffic).
  (1) **`accept()` sense-count** — H920's deferred deepest fix: `gen_opt_harness2.py` stamps the hardened
  `source_senses` and `accept()` records a `SANLOSS_SHORTFALLS` shortfall (`SANLOSS_HARD_REJECT` owner-gated);
  [`sense_count.py`](src/pilot/sense_count.py)'s counter is hardened to skip cross-reference ordinals (the
  ~4.78%-of-cards over-count the naive `\d+〉` findall carried: `gam~~h2_31_pari` 2→1, `s_ud~~h0_05_pra`
  4→2, `_a_srayatva` 2→0). (2) **Grammar `{Tn}` multiset** — `accept()` now runs the heal path's `{Tn}`
  multiset check on the main path (`TNMASK_MISMATCHES`, owner-gated), catching a dropped `<lex>` grammar
  span the `<ls>/{#` count is blind to. (3) **German `{#..#}` span drop** (H911 backlog #3) —
  [`prompt_rule_audit.py`](src/pilot/prompt_rule_audit.py) `dropped_sanskrit_span`, a content-multiset
  source-vs-target diff, **LOW / report-only** (never requeues), excluding structural head-label spans (the
  measured 95%-FP class). (4) **Economy telemetry** (H911 backlog #4) — new
  [`economy_ledger.py`](src/pilot/economy_ledger.py) derives `agents_per_clean` + a bounded `$/clean` band
  from the frozen probe log (metrics H911 called `not_recoverable` actually sit there), `gate()` on aggregate
  breach. (5) **Four-profile `staged-run`** — [`max_account_orchestrator.py`](src/pilot/max_account_orchestrator.py)
  guard relaxed from exactly-one to ≥1 account; `probe_fleet()` probes each profile, STOP-on-any-NO-GO
  (`--drop-unhealthy` opt-in), `probe_latency_ms` rewired to a per-account map; the claim/dispatch/recover
  substrate was already N-account-proven. (6) **Bounded supervisor** — new
  [`bounded_supervisor.py`](src/pilot/bounded_supervisor.py): injectable `run_window` seam, bounds on
  window-count / budget / clean-target / consecutive-empty, requeues partials, atomic checkpoint + crash
  resume. New selftests: `test_h960_accept_sanloss_soft_gate` (node, extracts the real `accept()`),
  `test_h960_dropped_sanskrit_span`, `economy_ledger_selftest.py`, `bounded_supervisor_selftest.py`,
  +N=4 cases in `max_account_orchestrator_selftest.py`; all wired into CI. LANG_PARITY entry
  `accept_sanloss_soft_gate_h960` (SHARED). No live generation — the residual NO-GO is exactly the
  owner-gated live ladder (auth → latency → canary → arm → 10 → 20 → multi-profile). Gate report:
  [pwg_ru/h960/H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md](pwg_ru/h960/H960_FOUR_PROFILE_PRODUCTION_READINESS_GATE_2026-07-15.md).

- **SAN-LOSS (whole-dropped-sense) guard — the H911 FAIL-branch #1 defect (H920, offline).**
  Root-caused `missing_senses`/SAN-LOSS in the no_pwg / supplement lane to **model omission**, made
  silent by three compounding facts: the no_pwg portrait declares `senses:[]` (no expected count), the
  only whole-card guard is `accept()`'s `<ls>`/`{#` token match (blind to a dropped citation-free
  sense), and `partial`/`missing_senses` are only set in the fragment-heal / autosplit lanes. Live
  evidence: `darv_i~~h0_zz_pw` dropped source sense 1 ("Löffel"), output 2/3, passed **clean** — the
  harness even computed `senses:3` and discarded it. Fix (SHARED, language-neutral): a new
  [`sense_count.py`](src/pilot/sense_count.py) primitive (`count_source_senses` counts top-level
  `N〉`/`N)` ordinals, `scan_sense_shortfall` compares to the output); `gen_no_pwg_card` stamps each
  sub-card's `source_senses` into its portrait and prepends a **sense-completeness rule** to
  ≥2-sense sources; a `sense_loss` gate in `audit_window.py` (→ requeue defect) and a `MISSING-SENSE`
  HARD flag in `audit_window_en.py`. Conservative — a null card or a pre-H920 portrait is skipped
  (never a false positive). Pinned by 4 `test_h920_*` selftests; LANG_PARITY entry
  `sense_count_sanloss_guard_h920` (SHARED). No live generation — validated on fixtures + frozen
  evidence; consuming `INPUT[k].senses` in the harness `accept()` is the deferred, live-gated deepest
  fix. Root cause + guard:
  [pwg_ru/h911/H920_NO_PWG_SANLOSS_ROOTCAUSE_AND_GUARD_2026-07-14.md](pwg_ru/h911/H920_NO_PWG_SANLOSS_ROOTCAUSE_AND_GUARD_2026-07-14.md).

## [1.9.9] - 2026-07-14

- **No-PWG promotion command safety.** `no_pwg_scale_plan.py` now emits a directly
  executable, single-window `promote_final_cards.py` command with an explicit output glob
  and exact generation model id. `promote_final_cards.py --merge` now refuses its implicit
  repo-root `wf_output*.json` glob, preventing the recurring ingestion of unrelated stale
  workflow artifacts.

- **H911 LOCAL-READINESS quality/economy gate — verdict `FAIL` (offline; Opus 4.8 executor-override
  of Fable 5).** Reconciled all recoverable H818 acceptance-canary + H255 no_pwg evidence into a
  denominator-honest [census](pwg_ru/h911/h911_quality_economy_census.json), ran a two-phase
  **blind** review of 40 frozen Workflow subcards (v1 freeze invalidated for `prior_outcome_exposure`;
  v2 re-frozen before scoring), and applied the locked gates. **Population audit-clean ~41–69%
  (median ~62%, H818 report "~60–65%") < the 80% bar** and **recurring SAN-LOSS/`missing_senses`** →
  hard-gate FAIL. Projected economy $58.09/100hw ≤ $75 PASS (projected only); **observed
  calls/clean and $/clean INCONCLUSIVE** (tokens `not_recoverable`). Foreign generation, four-account
  scale, and H841–H843 stay **blocked**; a narrow SAN-LOSS offline fix handoff was minted. Reviewer
  `[NWS:]`/`{%…%}`-delimiter findings downgraded to stylistic concerns (audit passes them). Report:
  [H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md](pwg_ru/h911/H911_LOCAL_READINESS_QUALITY_ECONOMY_GATE_2026-07-14.md).
- **Latency-policy investigation — foreign-route decision rule PRE-REGISTERED (frozen before any
  foreign data).** Locked the exact thresholds in *Method step 2* Step C — ceiling 30 000 ms;
  per foreign window median ≤ 30 000 ms AND ≤ 1/5 breaches, N ≥ 5; aggregate breaches/total ≤ 0.10
  across ≥ 2 windows; **causality ratio 0.70**; identical warm-up policy excluded from stats — with
  an explicit "do NOT tune post-hoc to obtain a preferred verdict" clause (git history is the
  tamper-evidence). Noted the lock in `latency_sweep_analyze.py`'s `--causality-ratio` help. No
  behaviour change; diagnostic still owner-gated and NOT yet run.
- **Latency-policy investigation — foreign-route runbook refined + probe telemetry extended
  (diagnostic-only; NOT yet run).** Tightened *Method step 2* per review: **exact** decision rule
  (per foreign window median ≤ 30 000 ms AND ≤ 1/5 breaches with N ≥ 5; aggregate breaches/total
  ≤ 0.10 across ≥ 2 windows — not "≈ 10–20 %"), **A-B-B-A paired crossover** order (same account
  authenticated per host, exact model/CLI/SHA/prompt/schema; sequence position + UTC recorded),
  **two separate conclusions** (route causality vs foreign operational readiness; diagnostic PASS
  ≠ production GO), and the **byte correction** (`padding_bytes` 6491 ⇒ `actual_prompt_bytes`
  **6554**, PREFIX 63 B). Extended [`latency_payload_sweep.py`](src/pilot/latency_payload_sweep.py)
  with route/window/sample-index/account-pseudonym/git-SHA/CLI-version/warm-up telemetry (warm-ups
  excluded from stats; never credentials or full outputs) and
  [`latency_sweep_analyze.py`](src/pilot/latency_sweep_analyze.py) with a `--decision-rule` mode
  that computes readiness + causality per route×window. 30 000 ms ceiling unchanged; Linux
  production + H841–H843 stay blocked.
- **Latency-policy investigation — foreign-route comparison runbook prepared (diagnostic-only,
  owner-gated; NOT yet run).** Appended *Method step 2* to
  [PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md](PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md):
  exact owner-authentication + paired 6.5 KB probe commands reusing
  [`latency_payload_sweep.py`](src/pilot/latency_payload_sweep.py) / `_probe_call` (exact
  `claude-sonnet-5`, byte-identical prompt/payload/schema off the same commit), guardrails
  (probe-only — no jobs/translations/promotions/store or TM writes; owner-only `/login`, never
  copy the Windows profile), a robust decision rule (foreign median ≤ 30 000 ms + low breach-rate
  over N ≥ 5 across ≥ 2 windows while Windows stays ~40 s), and the on-confirmation next step
  (4 profiles + a new acceptance handoff). Linux production + H841–H843 stay blocked; the
  30 000 ms ceiling is unchanged.
- **H895 — H818 acceptance resume: second consecutive measured-probe NO-GO; latency-policy
  investigation opened.** Ran exactly one integrated warm-up+measured two-phase probe staged-run
  (run_id `h895-run1-arvant`, gen `claude-sonnet-5`, orch Opus 4.8 `claude-opus-4-8[1m]`): warm-up
  41 159 ms / measured **40 339 ms** `success` but over the 30 000 ms ceiling → honest NO-GO, no
  re-roll; probe gated before import, `arvant` never ran, canonical store unchanged (11,579).
  Second NO-GO after run5's 40 925 ms — pure latency (both `success`), warm-up ≈ measured so it is
  steady-state, not cold-start. Did **not** weaken the threshold; opened
  [PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md](PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md)
  (payload-size sweep + foreign-route method; the fix is the H818 4-account foreign-server route,
  not the ceiling). A-vs-B (`arvant` D-J vs content-specific) still unresolved; H818 OPEN.
  Backfilled the required append-only `LAUNCH_FUCKUPS.md` ledger entry
  (`H895_RUN1_LATENCY_NOGO_2026-07-13`) that CI's launch-ledger gate demanded. **The raw run1
  telemetry (`src/pilot/output/h895_accept/run_events.jsonl`, gitignored/local-only) was LOST
  when the `h895` staged-run worktree was removed and was never archived** — surviving run1
  evidence is this RUN_LOG entry + the latency-policy doc; the Uprava H899 archive holds the
  earlier run5 + `durgA` evidence, not run1. H895's one-run allowance is consumed — do not rerun.
- **H879 — fix the German (PWG++) sense-splitter's missing `〉` glyph handling (~50%
  under-count, org-wide).** `microstructure.py`'s `MARK` regex only ever matched ASCII `)`
  as a closing sense-marker, never `〉` (U+3009 RIGHT ANGLE BRACKET) — PWG's own standard
  notation ("1〉", "a〉"), used 87,680 times in `csl-orig/v02/pwg/pwg.txt`. Surfaced as a
  4-key `pwg_de_lexicon.ttl` fixture drift (committed fixture claimed 34 senses, a fresh
  rebuild yielded 22); root-caused, fixed, and reverified — the correct 4-key count is
  **47**, and a 2500-card `_audit_micro.py` before/after shows senses-per-card rising from
  a flat 1.0 to 1.5 with zero new anomalies (citation/abbreviation resolution unchanged or
  improved). `pwg_de_lexicon.ttl` and `grammar.ttl` fixtures regenerated (the grammar
  layer's nominal branch derives `<lex>` POS tags from the same sense split, surfacing one
  genuinely new irregularity for lemma `a`); full `lod_acceptance.py` gate (A/B/C/C5/C6/D/
  D2/D3) PASSES. Scope: only `export_lod.py`'s DE-lexicon export and `scale_route.py`'s
  sense-count routing heuristic call the fixed function — the core RU translation
  prompt-building path is unaffected, no pinned test broke. Full writeup:
  [`FINDINGS.md` §447](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#447-pwgs-own-closing-sense-marker-glyph--was-never-recognized-by-the-sense-splitter--50-of-german-senses-were-silently-merged-into-their-first-sub-sense).

- **H818 D-K — two-phase probe protocol (fixes the cold-start flap without lowering the
  ceiling).** The single-sample D-F gate NO-GO'd on a transient cold reading (a 30151 ms
  flap on an otherwise ~8–10 s warm profile). `live_probe` now runs a deterministic
  sequence: **exactly one warm-up call** (same profile + exact model; its latency is
  EXCLUDED from the acceptance gate — it only stabilizes the cold connection) then
  **immediately exactly one measured ≥5 KB probe** that IS gated (rc 0, auth/model/
  output-size checks, latency **≤30000 ms unchanged**). A warm-up failure
  (auth/model/malformed/rate-limit/timeout) is an immediate STOP; a failed or over-ceiling
  *measured* probe is an honest NO-GO with **no retry and no manual pre-warming**. Both calls
  are recorded separately in telemetry (`purpose` warmup/measured, latency, model,
  output_bytes, classification); `build_census` keeps probe calls distinguishable from
  translation, excludes the warm-up from acceptance latency, but **still counts warm-up
  rate-limits in total quota observations**. `output_bytes` is measured from encoded UTF-8
  bytes, not character count. Both probe calls use the shared D-J tree-kill runner (now
  extracted to `proc_tree.py`, used by both `headless_worker` and `max_account_orchestrator`),
  so a hanging probe kills its whole parent→child→grandchild tree before generation begins.
    **Fix (same day):** `_probe_call` now validates the `claude -p --output-format json` result *envelope* strictly instead of demanding a bare top-level `{"ok":true}` (which flagged every real wrapper `malformed`): rc 0 is not enough — `type==result`, `subtype==success`, not `is_error`, and the structured schema result (`structured_output`, or `result` parsed as a JSON string) must be `{"ok":true}`. A non-success subtype / `is_error` => `process`, `{"ok":false}` => `content`, a missing/non-envelope result => `malformed`, and auth/rate-limit text is detected even inside an rc-0 error wrapper. Six result-envelope fixtures cover it.
  Also: `taskkill`/`tasklist` now launch with `CREATE_NO_WINDOW` (Windows-only) via a shared `proc_tree.windows_hidden_flags()` used by all three sites, so tree-kill/liveness checks no longer flash a console window.
  Regression tests: exactly one warm-up + one measurement, 30000 passes / 30001 NO-GO,
  warm-up failure STOPs before the measured call, encoded output_bytes, census
  distinguishability + quota, and a real 3-level hanging-probe tree-kill. (13-07-2026, Opus
  4.8 `claude-opus-4-8`, H818 lineage.)
- **H818 D-J — Windows process-tree kill on timeout (bounded best-effort).** A timed-out
  generation call was killed with `subprocess.run(timeout=)`, whose Windows kill hits only
  the immediate `node cli-wrapper.cjs` process — **orphaning the `spawnSync`'d native claude
  binary** (confirmed at the wrapper source) that keeps holding the API call. That is the
  bounded-scope diagnosis (defect A) of the arvant multi-minute non-termination (a
  content-specific problem B is not ruled out until a post-merge bounded retry). Fix: a
  `run_tree_kill` (Popen + `communicate(timeout=)`) that on timeout performs **bounded
  best-effort** whole-tree termination — `taskkill /PID <pid> /T /F` while the parent is
  alive on Windows, `killpg` on POSIX — always falling back to `proc.kill()`, draining pipes
  and reaping within the remaining kill budget, and recording cleanup trouble diagnostically
  without changing the primary `timeout` classification. Applied at every claude-spawning
  kill point (worker calls, the outer worker subprocess, `live_probe`, `profile_status`,
  presplit-canary worker). Not race-free (tree enumeration still races exit/spawn) —
  correctness is asserted by a **parent→child→grandchild** regression test that fails if any
  descendant survives. (13-07-2026, Opus 4.8 `claude-opus-4-8`, H818 lineage.)
- **H818 acceptance hardening (follow-up) — D-G real-concurrency race + D-I telemetry
  cardinality.** Two further acceptance defects, following the D-E…D-H batch. The D-G
  selftest was strengthened to a **real** concurrency race — two independent SQLite
  connections opened *before* a barrier fire the claim transaction (`_claim_tx`) at the
  same instant, repeated ×8 — proving exactly one winner + one still-pending job with no
  `SQLITE_BUSY`; plus an explicit `connect()` busy_timeout. **D-I** fixed a
  telemetry-cardinality bug where one model call was logged once *per key*, inflating
  latency p50/p95 and classification counts on batches: each real call now emits one
  call-level `model_call` event (stable `call_id` covering the retry/split path,
  `key_count`, preserving `lease/window/attempt/account/manifest`), per-key relations go to
  `model_call_key` events excluded from the latency/classification census, and
  `build_census` dedups by `call_id` (crash/restart re-appends are idempotent) and surfaces
  conflicting duplicates. Regression tests in `max_account_orchestrator_selftest.py`.
  (13-07-2026, Opus 4.8 `claude-opus-4-8`, H818 lineage.)
- **H818 Windows acceptance hardening — four defects (D-E…D-H) fixed + regression-tested.**
  A live Windows re-acceptance of the H852-fixed headless pipeline surfaced four defects
  beyond the D-A…D-D invocation fixes: **D-E** `translation_memory.py` hardcoded a
  worktree-local `DEFAULT_STORE` and did not use `store_path.canonical_store`, so
  `coordinator.promote_ready`'s post-promotion `translation_memory.py build` failed
  `store not found` under a git worktree (latent until the first successful worktree
  promotion); **D-F** `live_probe` enforced only `rc 0`, not the repository probe gate,
  so 50,991 ms / 36,684 ms readings proceeded instead of NO-GO — it now also requires
  payload ≥ 5 KB, exact model `claude-sonnet-5`, and latency ≤ 30000 ms; **D-G** the
  SQLite `claim` did not refuse an account already running an `in_progress` job, so the
  "one account, strictly sequential" contract was not atomic — now enforced inside the
  `BEGIN IMMEDIATE` transaction (race test added); **D-H** promotion telemetry reported
  any non-positive delta as `conflict`, mislabelling the common audit-`needs_requeue`/
  zero-clean case (which never attempts promotion) — now `success` / `not_attempted` /
  `conflict` are distinguished. Regression tests land in
  `max_account_orchestrator_selftest.py`, `store_path.py --selftest`, and
  `translation_memory.py selftest` (RU+EN); CI runs the store_path + translation_memory
  selftests; LANG_PARITY SHARED entries re-verified. (13-07-2026, Opus 4.8
  `claude-opus-4-8`, H818/H852 lineage.)

### H781 — grammar layer (Whitney root / nominal) as its own LOD graph on the shared lemma spine
- New `grammar` mode in
  [`src/export_lod.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py)
  emits the **third** derivable layer onto the shared `lemma/<key1>` spine (after
  `dcs-freq` and H772's `de-lexicon`): one grammar block per `key1` into a
  **separate** graph (`grammar.ttl`). Sources reused, not recomputed —
  [`whitney_grammar.grammar_for()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/whitney_grammar.py)
  for verb roots (`class`, `ppp`, `section_refs`, `irregularities`) and
  [`nominal_grammar.nominal_grammar_for()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nominal_grammar.py)
  for non-root headwords (`stem_class`, declension/paradigm/compound/derivation
  §§, `zaliznyak_index`), with a single aggregated `<lex>` tag per non-root card
  (dedupe across all PWG senses, then the same concrete-noun-gender priority pick
  `enrich_portrait_nominal_grammar.py` already uses). Whitney §§ land as
  first-class `pwglex:GrammarSection` resources (mirrors the `pwglex:Citation`
  pattern); gender maps to `lexinfo:gender`/`lexinfo:masculine` etc. where clean;
  gaṇa class doubles as `lexinfo:conjugationClass`. **Homonym-safety guardrail
  (§5 of the handoff):** a key1 with >1 Whitney homonym record gets ONLY a
  `pwglex:homonymAmbiguous true` marker — never a guessed class/ppp/irregularity
  from the wrong homonym (does not occur in the 4-key fixture; `rakz` is
  single-homonym, verified `whitney_no 613, class I, ppp rakṣitá`). RU/DCS/DE
  emitters and their fixtures untouched — `pwg_ru_lod.ttl`/`dcs_freq.ttl` regen
  byte-identical, verified against a full ~120k `assemble.py build`.
- [`src/lod_acceptance.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/lod_acceptance.py)
  gains block **D** (grammar × lemma's RU/DE entry × DCS-freq federated join,
  covering BOTH the root and nominal branches via `UNION`; `stemClass` ⇒
  `zaliznyakIndex` and `GrammarSection`-has-a-label structural invariants;
  byte-stable regen; source-coverage recompute against
  `whitney_grammar.grammar_for`/`nominal_grammar.nominal_grammar_for`) + query
  [`release/query/grammar_lemma_dcsfreq.rq`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/query/grammar_lemma_dcsfreq.rq).
  Block D **PASSED** on every attempt (3/3 full-gate runs). **Pre-existing,
  out-of-scope gap surfaced, NOT introduced by this change:** blocks C5/C6
  (H772 German-enrichment byte-regen/source-coverage) fail against a freshly
  rebuilt `assembled_cards.jsonl` — confirmed via a stash test running
  *pristine* origin/master `export_lod.py`/`lod_acceptance.py` (no H781 code)
  against the same full-corpus rebuild, same two failures. The `pwg_de_lexicon.ttl`
  fixture (H772, committed 2026-07-12) no longer matches a from-source regen;
  root cause not yet isolated (`csl-orig/pwg.txt` unchanged since 2026-06-27,
  `pwg_mask.py`/`microstructure.py`/`assemble.py` unchanged in git history — data
  or environment drift, needs its own follow-up). Per this handoff's explicit
  guardrail ("do NOT alter the lexicon/dcs-freq/de-lexicon emitters"), left
  untouched here.
  ([H781](https://github.com/gasyoun/Uprava/blob/main/handoffs/H781-Sonnet_SanskritLexicography_grammar_layer_lod_graph_12.07.26.md), Sonnet 5 `claude-sonnet-5`)

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
  [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt)
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
  [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt)
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
