# Runbook — frequency queue on the headless CLI (manifest v2)

_Created: 09-07-2026 · Last updated: 07-08-2026_

Goal: scale the PWG→Russian production run in DCS-frequency order, with giant
roots split into single-pass units and re-glued after translation. This is the
post-judge path: the 38-unit freq test is complete, 37/38 were publishable, and
the lone sev-3 belongs to the NWS owner-row slip class that the deterministic
audit gate catches.

## Cold start (skills first)

| Phase | Skill | Stop |
|---|---|---|
| Gate | [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) | NO-GO or stale GO → do not spend |
| Spend | [`/pwg-bounded-run`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-bounded-run.md) | one profile, `max-wide=1`, `--stop-before-promote` |
| Drain | [`/pwg-drain`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-drain.md) | next worklist head only after gate |
| Close | [`/pwg-window-close`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-window-close.md) | unbound manifest / bad audit → no promote |

Live queue: [`../../.ai_state.md`](../../.ai_state.md). Operator depth + symptom cookbook:
[`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
§0 / §11. Never copy canary `--max-agents 1` onto multi-key windows.

**Production route (H1110, since 18-07-2026):** `headless_worker.py` under a
profile-bound **manifest v2** (`execution_route: claude-cli-headless`), driven
by `coordinator.py` / `bounded_staged_run.py`. The Max-Workflow lane
(`run_pilot_wf.opt2.js`) is **forensics only**.

**QA policy — BALANCED, token-optimized (2026-06-27, [`../../TOKEN_OPTIMIZATION_2026-06-27.md`](../../TOKEN_OPTIMIZATION_2026-06-27.md)):**
the bulk pass is **translate (Sonnet, single-turn inlined) + four FREE Python gates on 100 %
of cards**; the LLM judge is no longer per-card. The measured driver is `cache_read ≈ context ×
turns`, so the run is reshaped to "Python at max, LLM at minimum" — the A/B cut cache_read 3.2×
and eliminated the transient dropouts.

- **Free gates (0 tokens, every card):** the canonical command is
  [`audit_window.py`](audit_window.py). It renders workflow output once, runs NWS owner-map,
  markup fidelity, sense coverage, and sense-duplicate gates against the same key set, writes
  a report/status ledger, and emits the exact re-queue list.
- **Live dashboard:** start it locally with
  `python src/pilot/dashboard_server.py --port 8765` from the `RussianTranslation`
  repo root, then open `http://127.0.0.1:8765/`. It refreshes every 5 seconds and
  shows Max-run status, next action, requeue/sample queues, token/time metrics,
  recent audit events, file freshness, and the G5/G6/G7/G10 print-gate snapshot
  without inventing any human review labels.
- **LLM judge (the only QA spend):** runs ONLY on Python-gate-flagged cards + a deterministic
  ~10 % mistranslation sample written by `audit_window.py` to `judge_sample.keys.txt`.
  **Sonnet judges; Opus adjudicates ONLY its rejects** (`ok=false ||
  severity>=3`), Opus verdict final — see [`../../research/JUDGE_POLICY.md`](../../research/JUDGE_POLICY.md).
  Publishable cards spend no Opus tokens.

## Cross-language parity — read before closing out any RU/EN fix or feature

This pipeline runs RU and EN (and any future language) through the same
lang-parameterized tooling. A fix landing on only one language path and never
reaching the other is a recurring failure mode (3 gate-bug fixes shipped
2026-07-03 stayed RU-only for a day before an audit caught it). Before calling
any fix/feature session done, classify it in
[`../../LANG_PARITY.md`](../../LANG_PARITY.md) as SHARED / INTENTIONAL-DIVERGENCE
(with a one-line why) / GAP (with a tracked follow-up) — see that file's policy
section. `python src/pilot/lang_parity_check.py` enforces ledger completeness +
tracked-file drift and is wired into `window_selftest.py`
(`test_lang_parity_ledger_complete`).

## Current operating truth

- **Execution route (H1110):** production is the **headless CLI on manifest v2**, not
  Workflow-from-session. Bind a named profile (`CLAUDE_CONFIG_DIR` + roster slot) before
  any paid call; promotion hard-refuses unbound payloads (H1080 Stage 3).
- **Profile-surface strip (H2189 03-08-2026, flipped by H2251 06-08-2026) — DEFAULT ON.**
  Every headless spawn now carries `--safe-mode`, which strips the operator profile's
  CLAUDE.md/skills/commands/agents/hooks from the child. `execution.cli_safe_mode` is
  **tri-state**: absent takes the default (ON), `true` pins it on, and **`false` still pins
  the historical spawn** — the operator opt-out survives the flip and is asserted by
  `headless_worker_selftest.test_safe_mode_default_is_on_and_an_explicit_false_still_opts_out`.
  An unsupported CLI degrades to the historical argv with a loud stderr warning — never a
  hard failure — and the run's own `status` now records `cli_safe_mode_effective`, i.e. what
  the spawn DID rather than what the manifest asked for, so a silent downgrade is
  identifiable from artifacts instead of a lost console.
  - **The numbers, re-measured — H2189's headline did NOT fully replicate.** Those figures
    (create −69 %, output −49 %, wall −55 %, cost −61 %) were **n=1 per arm**. At n=6 per
    arm over 3 cards (H2251): create **−40 %**, output **−4.4 %**, wall **−12.3 %**, cost
    **−22.3 %**. The saving is real and worth having, but roughly a third of what was
    quoted; treat the output-halving claim as retired.
  - **The load-bearing argument is the CEILING, not the price.** On `sakft` the baseline ran
    **286 694 ms** and **266 349 ms** against the **300 000 ms** kill — twice within ~11 % of
    dying — where the safe arm ran 232 891 and 189 106. H2189 saw the same thing as an
    outright timeout. A window that completes beats a window that is 5 % cheaper.
  - **Quality, at n=12 draws:** zero content loss anywhere (every sense carries Russian, no
    `SAN-LOSS`/`UNMAPPED`), and sense segmentation moves as much *within* one arm as
    *between* arms — so card content is not a function of the spawn shape. The free-text
    `tag` vocabulary is not reproducible even with the flag held constant (mean within-arm
    Jaccard 0.535), which is the condition H2189 itself named as closing its §4.2 question;
    an arm-linked *style* component survives on top of that and is recorded as a residual.
  - Numbers and method: [H2251 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2251/SAFE_MODE_CANARY_GO_AND_TAG_DIVERGENCE_RULING_06-08-2026.md)
    · original [H2189 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md).
- **Durable call budget (25-07-2026 hardening):** the bounded run, its fleet probes,
  and every headless worker share one `pwg.call_reservation.v1` ledger keyed by
  `run_id`. `max_calls` is a strict pre-spawn ceiling: reserve first, then spawn;
  reservations survive crashes and are never refunded. `--resume` must reopen the
  same ledger/run ID and refuses a different saved ceiling.
- **Cost semantics:** `--cost-ceiling` is an observed-cost stop evaluated after
  completed calls, not a pre-spend dollar guarantee. Pending, absent, malformed, or
  otherwise unevaluable telemetry causes `STOP_COST_UNEVALUABLE`; it is never treated
  as zero. Use `--max-calls` for the strict upper bound on call count.
- **Profile/process isolation:** one `ActiveCallClaim` spans each complete warm-up +
  measured probe pair, and the same profile fingerprint lock spans generation. On
  Windows, Claude is assigned while suspended to a kill-on-close Job Object; timeout
  and exception cleanup terminate the descendant tree, not only the launcher.
- **Bound artifacts:** before a paid manifest-v2 spawn, the orchestrator rechecks the
  saved run ID, manifest SHA-256, profile binding, sealed preflight SHA-256 and exact
  selected-key scope, plus the reservation ledger. The worker seals its result SHA-256;
  `record-output`/`record-output-batch` require the matching run and result hash.
- **Run every headless call from a BARE cwd — not from the repo (02-08-2026, measured).**
  The CLI injects `CLAUDE.md` + git state into its prompt prefix, and that injection is worth
  **~11–17 k re-created cache tokens per call**. Measured on identical `--max-turns 1` calls:
  repo cwd **$0.3036 / 26–29 s**, bare cwd **$0.2040 / 19–20 s** — **−33 % cost, −30 % wall
  clock for changing one directory**, no code change and no guard weakened. Pass an empty
  scratch dir as the subprocess `cwd`; the manifest carries every input the worker needs, so
  nothing depends on being inside the repo.
  **✅ Fixed (H2249, 03-08-2026) — was an open defect for one day.** H2158's walk rejected an
  ancestor carrying a bare `CLAUDE.md` or a `.git`, but **not** one carrying
  `.claude\CLAUDE.md`, and its `%TEMP%` directory sits under the Windows user profile:
  **32 779 B** of operator memory (`C:\Users\user\.claude\CLAUDE.md` + `.claude\rules`)
  reached every paid call between H2158 and this fix, invisible because the spawn directory
  itself was empty. `bare_cli_cwd()` now **derives** candidates — an operator
  `PWG_RU_CLI_CWD` override, then the historical `%TEMP%` directory, then each FIXED
  filesystem root the OS reports (system drive last) — and returns one only after
  `h2189_min_profile.cwd_ancestry_scan` proves the whole ancestry clean, else `None` (the
  historical inherited-cwd behaviour). No drive letter is hardcoded. On this box it resolves
  to `D:\pwg_ru_cli_cwd`, **0 injectable bytes**. Verify any spawn dir yourself with
  `python src/pilot/h2189_min_profile.py --scan-cwd <dir>`; pinned by
  `headless_worker_selftest.test_bare_cwd_ancestry_is_clean_or_none` (an assertion since
  H2249 — it shipped as a report under H2189 precisely because it could not pass) plus
  `test_bare_cwd_candidates_are_derived_not_hardcoded` and
  `test_bare_cwd_refuses_a_dirty_ancestry_rather_than_returning_it`. `--safe-mode` merely
  **masked** this and is no longer what stands between the operator's global `CLAUDE.md` and
  a paid call; it remains the separate, opt-in **profile**-surface lever above.
- **The per-call cache IS reused across calls — but do not bank on any single call getting
  it. Rewritten 06-08-2026 ([H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md));
  the old "NEVER reused" was measured on CLI v1.127.0 and is false of v2.1.223.** In a
  purpose-built 7-call sequence, the cold call wrote **26 243** (read 28 882, total
  **55 125**) and six later calls reused it — five of them creating **0** and reading the
  cold call's `create + read` exactly, at gaps of 34 s / 94 s / 120 s / 128 s / 557 s.
  **The sixth re-created 20 740 at a 547 s gap while the call right after it, at a longer
  557 s gap, read the full prefix** — so the miss is not a decay curve and not TTL, and its
  prefix was also 14 tokens larger than the cached one. Operationally: **plan the cold
  write once per run, treat a mid-run re-create as possible but uncommon, and do not build
  a schedule that depends on hitting cache.** The write is a premium **cache create**
  (~$6/M) against a **read** (~$0.30/M), so the saving is real when it lands. Every write
  still goes to `ephemeral_1h_input_tokens`; `ephemeral_5m` is 0. The past-1 h gap is
  **not** measured — with a non-time-driven miss demonstrated in the same run, one datum
  there would be uninterpretable.
  Do **not** "fix" any of this by batching (see the shape ruling below) — that ruling is
  untouched. Report + committed envelopes:
  [pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md);
  confirms [H2189 report §7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2189/PROFILE_SURFACE_AB_SAFE_MODE_VS_MINIMAL_CONFIG_DIR_03-08-2026.md).
  **Single playbook of
  record** (ranked levers + Opus handoffs H2189–H2191 + H2158):
  [`PROMPT_CACHING_PWG_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md).
  Route change tracked in
  [H2158](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2158-Opus_RussianTranslation_pwg-messages-api-port_02.08.26.md);
  measurement in [`RESULTS_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md)
  + [Uprava FINDINGS §284](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).
- **Call shape: ONE card per call — and shape is not the lever (H2152, 02-08-2026).** Quota and
  the per-call wall-clock ceiling (`HARD_TIMEOUT_MS`) bind in **opposite** directions: a quota
  ceiling penalises *many* calls, a wall-clock ceiling penalises *large* ones. Whichever binds
  decides the shape, and as of 02-08 it is wall clock, so the small shape wins — which is also what MG's
  instrument-everything mandate asks for, so the two are not in conflict. `--output-budget=1`
  is the existing one-card lane; nothing needs building. **Do not flip to batching to save
  cost:** batching also makes one unevaluable call destroy per-card attribution for *all* N
  cards in it. Full reasoning: [`pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2152/AUDIT_C4_CALL_SHAPE_QUOTA_VS_WALLCLOCK_02.08.2026.md).
  > **Ceiling status, later the same day: `HARD_TIMEOUT_MS` is now 300 000, and the two lanes
  > diverged.** The heal lane WAS being killed by an outgrown bound — `heal:nakzatra#g2`
  > returned at **176 952 ms**, 3 048 ms inside the old 180 000. But `translate b0` died at
  > 180 044 ms *and* at 300 073 ms, converging on neither: the whole-card lane holds a
  > **non-terminating** call, so for it a higher ceiling strictly *increases* waste. Do not read
  > "the ceiling was raised" as "the timeouts are fixed" — that hang is a separate, still-open
  > defect (v1.130.0).
  >
  > **Still open on 06-08-2026 at CLI v2.1.223, and 300 000 is now demonstrably too low for
  > a whole card** ([H2250](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2250-Opus_SanskritLexicography_pwg-cli-cache-amortisation-remeasure_03.08.26.md),
  > incidental to a cache run). Five spawns of the production `build_prompt` surface on
  > `nakzatra`: **three killed** (two at 300 s, one at 900 s), one clean at **511 908 ms
  > wall / 494 603 ms api over 3 turns**, one at 48 414 ms over 4 turns that returned
  > **zero cards** and failed the schema. So the clean case now runs ~1.7× the 300 s
  > ceiling, and the non-terminating hang the note above records is still live at 900 s.
  > Same class as the 05-08 `gate-0 HEALTH_NOGO — the measured leg was killed at
  > 300 000 ms having returned nothing`
  > ([#1144](https://github.com/gasyoun/SanskritLexicography/issues/1144)). Raising the
  > ceiling remains the rejected fix (playbook rank —, "hides hang class"); the datum here
  > is that **the ceiling is no longer separating slow calls from hung ones at all.**
- **Live-gate before every paid window:** fresh
  [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md)
  (representative ≥5 KB health + separate `dq_canary_puregloss`). A previous session's GO
  never authorizes a new spend.
- **Generation model:** **always Sonnet 5 (`claude-sonnet-5`)** — the harness pins the
  exact id on every `agent()` call (H818, SHARED RU/EN). The interactive session model
  does not control generation.
- **`--max-agents` is a total-spawn cap** (translate + heal). Never set `--max-agents 1`
  on multi-key / heal-capable windows — it starves non-`b0` work (ledger
  `C2_M50_W1_MAX_AGENTS1_2026-07-24`). Prefer manifest budgets only.
- **The translated source is the 5-layer all-in-one** built by
  [`_pilot_gen_merged.py`](../_pilot_gen_merged.py) — PWG main+Nachträge + PW + SCH + PWKVN +
  NWS (owner-mapped) — live since commit `1dad0dd` (17-06-2026), never reverted.
  `csl-orig/v02/pwg/pwg.txt` is read-only and is only the **PWG layer input**, not "the
  source"; the `_zz_pw` / `_zz_sch` / `_zz_pwkvn` / `_zz_nws00` card-ID suffixes are the live
  per-layer routing (H178 A-4b).
- The optimized **translate-only** harness is generated per root by
  [`gen_opt_harness2.py`](gen_opt_harness2.py) and executed headless. It masks and batches
  raw/portrait inputs, disables translate-agent tools, auto-uses translation-memory
  sidecars when present, presplits over-budget dense cards into the selfheal lane, and
  returns provenance metadata used by the audit stale guard.
- Article-site/root dashboard lazy loading is already shipped; do not spend performance time
  re-implementing that path.
- Lean TR / prompt trimming was tested and rejected; keep the full production TR unless a new
  measured sequential calibration proves otherwise.
- Superseded a-section/manual harness notes are archived under
  [`archive/legacy_max_2026-06-27/`](archive/legacy_max_2026-06-27/). Do not use those
  files for current production windows.
- The corpus word-alignment lexicon exists; bulk throughput is no longer blocked on that asset.
- Deterministic gates are canonical for bulk acceptance: NWS owner-map, markup fidelity,
  sense coverage, and sense-duplicate checks all run through [`audit_window.py`](audit_window.py).
- Print readiness is a separate downstream gate: G5 review, G6 human gold, G7 double review,
  and G10 edition cut remain blocked until human review/gold work is done.
  `preflight_remaining_gates.py` and `release_readiness.py` are report-only by default; add
  `--fail-on-blocked` when using them as CI/go-no-go gates.
- **Scope ruling (MG, 04-07-2026): drain ALL remaining DCS-attested verb roots**, root-by-root.
  The worklist is enumerated reproducibly by [`verb_worklist.py`](verb_worklist.py) (verbs01
  universe ∩ freq manifest − promoted store): 749 attested verb roots, **48 promoted /
  701 remaining** as of 24-07-2026 (~5.2 MB source). Operator `--top` output is filtered
  to roots with existing rootmaps; the JSON keeps the full backlog plus
  `blocked_missing_rootmap` (most remaining verbs still need rootmaps before they are
  runnable). H1339 rederived the whole remaining population at **5,580 unique**
  (701 verb + 4,757 nominal-PWG + 122 no-PWG). Drain discipline lives in the standing handoff
  [`H151`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md).
- The per-root loop below is unchanged — "all roots next batch" scales the QUEUE, not the
  width. Roots still run **one at a time** (global ordinary leases ≤3; bounded paid runs
  use `max-wide=1`); the Slice-D 18×-parallel collapse (117 transient nulls) is the standing
  counter-example.
- **H304 hardening (07-07-2026) — four operator-memory rules are now code paths:**
  (1) **cap-and-defer** — `coordinator.py claim/prepare` act on the `perf_preflight` cost
  gate: an over-ceiling (kAla-class) window is parked in
  `deferred_monsters.jsonl` (local-only run artifact) and refused (`prepare
  --allow-over-cost` only inside a dedicated human-budgeted monster session — MG ruling
  07-07-2026); (2) **gate-outcome memory** — the RU audit writes
  `output/requeue.defect.fshas.txt` and `requeue_from_audit.py` denylists those fragment
  addresses, so `--tm=auto` can never re-serve a gate-flagged fragment (EN emitter is a
  tracked GAP: `defect_fragment_denylist_h304` in [`LANG_PARITY.md`](../../LANG_PARITY.md));
  (3) **better-attempt-wins** — `save_and_audit.py --merge` keeps the better prior attempt
  per card (complete > partial, fewer `missing_fragments` > more), so a requeue can no
  longer regress a card; (4) **presplit topup is sound** — `autosplit_requeue.frag_groups()`
  reconstructs the fragment partition with the budgets of the run that minted the `gN:fM`
  ids (pass the wf `meta` + key), instead of always the heal budget.
- **Promotion closure (25-07-2026 hardening):** ready leases promote only through
  the coordinator's journaled batch path. `pwg.promotion_journal.v1` advances
  `prepared → store_committed → derived_validated → coordinator_committed →
  complete`, with one canonical-store claim held throughout. Every coordinator
  startup reconciles the single incomplete journal; a store/coordinator hash that
  matches neither sealed before nor expected-after state fails closed. Card TM,
  fragment TM, denylist state, coordinator bytes, and one deterministic
  promotion-registry event per lease/promotion are sealed and replayed
  idempotently.

The earlier "Opus-judged-every-card" framing was the validation phase; "Sonnet-bulk/Opus-on-reject"
was the 2026-06-26 escalation policy; the per-card LLM judge itself is now dropped from the bulk path.
The in-chat Workflow route is **retired for production** (H1110) — use headless manifest v2.
Workflow artifacts remain valid forensic inputs when replaying historical launches.

## Current preflight

Last local preflight: **2026-06-26**.

```powershell
cd RussianTranslation\src
python freq_route.py 8
python _pilot_gen_merged.py --manifest freq --root-split --limit 3
python verify_root_glue.py
```

Observed state:

- `scale_manifest.freq.json`: **43,968 / 106,082** PWG headwords are DCS-attested
  (**41%**).
- Frequency top lists are advisory unless they come from current
  `verb_worklist.py --top` runnable output; roots missing rootmaps are reported separately in
  `blocked_missing_rootmap`.
- Top 3 with `--root-split`: already generated locally (`0 to generate`), so the
  machine has the required rootmaps/sub-cards for `sTA`, `BU`, and `gam`.
- `verify_root_glue.py`: **ALL GATES PASS**; lossless round-trip, 0 secondary
  conjugation blocks still merged, 60 rootmaps with unique keyed subkeys.
- 2026-06-29 root status refresh: `sTA` is structurally ready but stale-output
  blocked; `BU` (59 sub-cards), `as` (98), and `i` (204) are clean-ready after
  harness generation; `gam`, `yuj`, `vid`, and `han` have stale generated
  raw/portrait inputs and must be pruned/rechecked before harness generation.

The preflight writes only gitignored pilot artifacts except when code/docs are
changed intentionally.

## Prompt/gate nits — DONE, encoded in the harness (verify, don't re-apply)

These four were folded into the inlined prompt of
[`run_pilot_wf.js`](run_pilot_wf.js) and the audit loop; this is now a
**verification checklist**, not a to-do:

- ✅ keep German abbreviations such as `Bed.`/`Schol.` verbatim, never expand —
  `CONV` line + **HARD RULE 3**;
- ✅ render **every** PWG Nachträge patch — **HARD RULE 4** ("ALL RECORDS,
  INCLUDING NACHTRÄGE … dropping any single patch fails coverage"); inputs are
  assembled by `_pilot_gen_merged.py` as the **5-layer all-in-one** (PWG main+Nachträge
  + PW + SCH + PWKVN + NWS), not main+Nachträge alone;
- ✅ treat `<is>...</is>` source italics as siglum text, never `{%...%}` gloss —
  `CONV` line + **HARD RULE 3**;
- ✅ `nws_split.py` owner-map gate — **HARD RULE 5** (authoritative pre-parsed
  owner map) + the deterministic auditor wired into `run_real_test.py audit`
  (quarantines misattribution → `*.merged.REJECTED.md`).

Also encoded (2026-06-26 literature-harvest port): Sanskrit-microstructure
rendering guidance (samāsa right-headedness, the *yad…tad* correlative map,
śāstric formulas, synonym-string cardinality, comma/semicolon sense-grouping,
manner/position forcing) as soft-judged guidance (judge check 7). Source tables:
[`../../glossaries/de_ru_translation_aids.md`](../../glossaries/de_ru_translation_aids.md).

## Window loop

The loop is fixed: **preflight → prepare a profile-bound manifest v2 → bounded
headless execution → sealed batch record + deterministic audit →
`AWAITING_REVIEW` → reviewed promotion or requeue**. Do not skip or reorder
these steps. The generated Workflow JS remains useful as historical/forensic
evidence, not as the production execution surface.

For enough data to estimate speed and quality, use the live runnable queue plus
`perf_preflight.py`:

1. Generate the current runnable queue with `python src\pilot\verb_worklist.py --top 20`.
2. Run `perf_preflight.py` over the next runnable roots and follow its recommended order.
3. Give any `defer-calibrate` root a dedicated calibration/session. Current calibration
   warning: `sTA` live preflight on 04-07-2026 reports 123 cards, 19 batches, 241 expected
   agents, `defer-calibrate`; do not use the older ~30-agent estimate.

```powershell
cd RussianTranslation\src

# Refresh the frequency manifest if VisualDCS data changed.
python freq_route.py 20

# Ensure the next manifest slice has root-split inputs.
python _pilot_gen_merged.py --manifest freq --root-split --limit 50
```

Preflight the root before spending Claude/Max tokens:

```powershell
python src\pilot\root_window_status.py sTA
python src\pilot\perf_preflight.py sTA
python src\pilot\verb_worklist.py --top 20
python src\pilot\perf_preflight.py sTA BU yuj as i tap dah ram
```

The first command prints the structural state plus one `next action` and one
`next command`; if it disagrees with stale notes elsewhere, trust the command
output and `src\pilot\output\window_status.json`. The second command is read-only
performance accounting: it reports card/fragment TM hits, degenerate pass-through,
presplit routing, batch count, and `agent_expected_after_tm` before paid spend. Use
`--json` when saving a machine-readable preflight report. With more than one root it
prints a compact comparison table plus a recommended order: zero-agent roots are skipped,
low-agent roots run first, and high-agent roots are deferred until cache refresh or
calibration. If presplit keys exist while `translation_memory.frag.<lang>.jsonl` is empty,
the preflight warns to run
`python src\pilot\translation_memory.py build-frags --lang ru` after a heal run emits
`frag_prov`; if no matching `wf_output*.json` contains `frag_prov`, the warning says so.

Generate the harness for the root. **Default: the batched + masked v2 harness**
([`gen_opt_harness2.py`](gen_opt_harness2.py)) — masks each card (pwg_mask), packs
several per agent call, and restores `{Tn}` to source markup in-JS so the result is a
canonical `wf_output.json` (audit consumes it unchanged, no extra step). Measured
**−72 % cost on a full mixed root** (gam: original per-card **\$16.14 → \$4.45**; a clean
small batch is −90 %). Current defaults: `--output-budget=90`, selfheal on,
binary-split on, presplit routing on, and `--tm=auto` (uses
`translation_memory.<lang>.json` + `translation_memory.frag.<lang>.jsonl` when present;
`--no-tm` is the explicit opt-out). Refresh TM after every promotion/heal harvest:
`python src\pilot\translation_memory.py build --lang ru` and, when fragment provenance was
created, `python src\pilot\translation_memory.py build-frags --lang ru`. See
[`../../TLONLY_PROTOTYPE.md`](../../TLONLY_PROTOTYPE.md).

```powershell
python src\pilot\gen_opt_harness2.py sTA            # default (batched+masked, TM auto, output-budget 90)
# -> writes the optimized harness and manifest inputs; do not run the JS manually in Max
# --output-budget=N tunes citation-weighted output packing (default 90).
# --budget=N without --output-budget keeps legacy byte-mode packing.
# --no-tm disables automatic card/fragment translation-memory reuse.
# A batch retries only its still-unresolved cards; a card whose restored <ls>/{#..#}
# counts don't match source is nulled -> requeue (never emitted garbled).
```

Remaining useful speed work is measured, not guessed: increase TM/fragment-TM coverage,
let conservative degenerate cross-reference stubs pass through without an LLM call, and use
[`calibrate_perf_harness.py`](calibrate_perf_harness.py) for scratch-only wider calibration
across fixed key sets (`--arm-set conservative` or `--arm-set wide`). Run live calibration
arms sequentially with cache cooldown; never run same-prompt arms in parallel.
Do not widen degenerate pass-through for editorial correction prose (`lies:`, `zu streichen`,
etc.); those rows stay in the normal LLM lane unless a future fixture proves exact
deterministic reconstruction is safe.

Legacy per-card harness (forensics/replay only; no masking/batching):

```powershell
python src\pilot\gen_opt_harness.py sTA             # -> run_pilot_wf.opt.js
```

Confirm the committed prompt template and generated artifacts still carry the
manual-derived semantic rules before any paid spend:

```powershell
python src\pilot\prompt_rule_audit.py --fail-on-missing
```

After this succeeds, a stale `window_status.json` from the previous audit is no
longer the next operator step. Follow the prepared manifest-v2 lease through
`bounded_staged_run.py --execute --stop-before-promote`, with explicit
`--max-calls`, a stable `--run-id`, and a durable `--call-reservation` path.
The command validates all scoped preflights before the first probe, then uses
the same reservation ledger for the fresh probe pair and worker calls.

The orchestrator writes and hash-seals the result itself; there is no manual
Workflow-save hand-off. `record-output-batch` records completed leases
sequentially and emits `RECORD_OUTPUT_BATCH_PROGRESS` after each durable commit.
If item N fails, only the exact earlier prefix is committed; item N and the
remaining leases are safe to retry. A clean
`--stop-before-promote` run writes the hash-bound
`pwg.awaiting_review.v1` checkpoint with status `AWAITING_REVIEW` and leaves
the canonical store/TM untouched. Do not run `run_pilot_wf.js`,
`run_pilot_wf.opt.js`, or `run_pilot_wf.opt2.js` manually for production.

Before the mechanical window audit, run the cheap translated-card semantic triage:

```powershell
python src\pilot\prompt_rule_audit.py --cards wf_output.json --review-limit 25
```

This writes the same ignored `prompt_rule_audit.{json,md}` report family with a
separate `card_risks` section and ranked `review_queue`. It is advisory by default;
start human/LLM semantic review from the `review_queue`, while mechanical reruns
still come only from `audit_window.py`. Add `--fail-on-risk` or `--fail-on-high-risk`
only for fixture/CI smoke checks, not for routine operator flow.

Lanes:

- **sparse** card (≤30 `<ls>`): single-turn, inputs inlined, **no tools** — the cheap path for
  the ~43 k normal sub-cards.
- **dense** card (>30 `<ls>`, e.g. a lone over-budget head sense): multi-turn, reads its own
  files, no-abridge directive. Heads are pre-split into citation-light parts by `sense_chunks()`
  (`_pilot_gen_merged.py`, budget `HEAD_CIT_BUDGET=18`), so this lane is a rare fallback.
- 1 automatic retry per stage; `judge:null` (the free Python gates own bulk QA).
- The optimized translate agents explicitly run with `tools: []`; any `Read`
  use in a Max run means an outdated harness file is being used.

Audit the window with the single deterministic command:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

If the CLI reports token/time numbers, record them on the same audit command so the ledger captures
the production economics:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue `
  --wall-clock-minutes 19 `
  --max-cache-read-tokens 6288668 `
  --max-cache-create-tokens 3697049 `
  --max-output-tokens 358884 `
  --max-total-tokens 10300000
```

If the weekly Max cap fires, add `--weekly-cap-fired --weekly-cap-cumulative-tokens N`.

For Stage B and later roots, change only `--root` and the prepared manifest
scope. Do not combine multiple roots into one `wf_output.json`; audit economics
and requeue keys must remain root-scoped.

The audit first compares workflow provenance against the current rootmap and raw/portrait
inputs. Stale output (missing `meta`, key mismatch, rootmap hash mismatch, or input hash
mismatch) stops before collect/gates/glue and records state `stale_artifact`. Check
`root_window_status.py`: if the optimized inputs and prepared manifest already
match the current rootmap, resume the bound headless attempt and record its
sealed result; regenerate only when the status command says the artifacts are
missing, invalid, or scoped to the wrong keys. Use `--allow-stale` only for
forensic inspection.
If stale output is refused, `--write-requeue` does **not** overwrite the existing
`requeue.keys.txt`; stale artifacts cannot produce a trustworthy mechanical requeue list.

The audit writes `audit_window.report.json`, `audit_window.report.md`, `window_status.json`,
`window_status.md`, `window_ledger.jsonl`, `requeue.keys.txt`, and
`judge_sample.keys.txt` under `src\pilot\output`.
Any NWS owner mismatch is quarantined as `*.merged.REJECTED.md`; markup-fidelity, coverage,
sense-duplicate, missing-card, or stale-input failures are re-queues, not accepts.
`prompt_rule_audit.py` is the no-token semantic wiring and translated-card triage check: before
Max it catches missing manual-derived prompt rules; after Max it flags cheap semantic-risk
patterns such as German residue, collapsed synonym strings, circular glosses, missing metadata,
markup/sigla leakage, formula drift, sense-compression signals, and suspicious source-type
evidence. Its ranked `review_queue` is the fastest human-first reading order; it does not
rewrite prompts, requeue cards, or replace human judgment.
`judge_sample.keys.txt` is the semantic review spend queue: all Python-gate failures plus a
deterministic 10 % sample of clean translated keys. It is NOT the mechanical requeue list.

## Concurrency — run a throttled driver, not N parallel chats

The coordinator enforces this distinction, rather than relying on operator arithmetic:

- `prepared` and `requeue_prepared` leases are durable reserved work and consume zero runtime slots.
- `coordinator.py begin-run --lease-id ...` atomically reserves runtime before dispatch. Standard
  mode is globally capped at three; `record-output` is refused unless the lease is `running`.
- `max_account_orchestrator.py staged-run` may use four only after every admitted profile passes
  the exact-model probe and the orchestrator writes a fresh receipt scoped to that run and lease
  set. Missing/failed/stale/mismatched evidence fails closed; no mode admits a fifth lease.
- Failed/retryable workers use `release-run --confirm-dead --reason ...`. A stale preparation or
  audit token uses `recover-operation --confirm-dead`; late subprocess completion is rejected by
  operation ID instead of overwriting the recovered state.

Preparation and audit subprocesses do not hold the global state lock. Their persisted
`preparing`/`auditing` operation tokens keep `status` and unrelated claims responsive, with a
10-minute preparation timeout and a 30-minute audit timeout.

**Default to one bounded headless window at a time; treat ordinary 3-wide as an
upper bound, not a target, and use `max-wide=1` for the bounded paid route.**
Each generated window may internally fan out to ~8–14 calls, so N concurrent roots
can still peak at N×~12 Sonnet calls on a single Max account. Slice D launched 18 at once →
~140–250 peak agents → ~80+ `Server is temporarily limiting requests` 429s → 117 transient
null cards. H317 then showed that even **3 concurrent medium windows** can collapse if the
session/provider is already unstable (0/38 clean, and the solo retry still saw repeated
`Connection closed mid-response`). In any session with fresh transport errors, first run a
single solo reference window and see it return mostly clean before trusting any concurrent
width. A clean sequential sweep is faster end-to-end than a collapsed wide run plus recovery.

**Running 3 accounts at once (3 clones, not 3 chats in one clone)?** Read the
[3-account operating protocol](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md#recommended-3-account-operating-protocol-no-code-changes-needed)
(H335 W1) first: one worktree per account (never a shared clone), shard roots via
`verb_worklist.py` before starting, only ONE account runs `promote_final_cards.py --merge`
per catch-up (single-promoter rule), and the ≤3-wide rule above is **global across all
accounts**, not per-account — 3 accounts × 3-wide each is the 429 danger band all over again.
H336 hardened the direct-path collision matrix that protocol documents (promotion claim file,
`--window-tag` output namespacing, JSONL append hygiene) — see
[promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py)
and `audit_window.py --window-tag` / `requeue_from_audit.py --window-tag` — but the operating
protocol (sharding + single-promoter) is still the primary defense; the hardening is a backstop,
not a substitute for it.

## Flaky API / Internet Policy

- There is no Claude API client in this repo for production PWG translation. Claude work runs
  through the profile-bound headless CLI; the coordinator, call-reservation ledger, process-tree
  cleanup, sealed results, and promotion journal make interruptions explicit and resumable.
- The generated optimized harness retries each card once. A still-null card is recorded by
  `audit_window.py`. The requeue list is **split** so a cheap re-run never triggers expensive
  rework: `requeue.transient.keys.txt` (null cards = rate-limit/dropout) vs
  `requeue.defect.keys.txt` (a gate flagged real content). A window whose only requeue is
  transient nulls reports state `transient_only` — re-run just those at low concurrency.
- The stale-provenance check is mandatory after any interrupted run. It prevents old
  `wf_output.json` files from being audited against newly regenerated rootmaps or inputs.
  Coordinator/headless runs additionally pass `--execution-manifest`: root, nominal mode,
  input hashes, and result keys must match that prepared contract, with every selected key
  present exactly once. A stale, duplicated, foreign, or unbound result is never promotable.
- A coordinator retry is a new execution attempt on the same lease. The lease seals the
  initial execution-manifest path and SHA-256 as its immutable key universe; every pending
  transient/defect key is bound to the path and SHA-256 of the audit report that classified
  it. `prepare-requeue` reads only this validated `pending_requeue` backlog, never a mutable
  split-key file. Changed reports, foreign/duplicate keys, overlapping classifications, or
  ambiguous legacy provenance fail closed.
- `prepare-requeue` accepts only `promoted_partial`, `needs_requeue`, or `transient_only`;
  promote a `ready_partial` clean subset first. Selecting one lane snapshots the other under
  `current_attempt.remaining_pending`, so a transient retry cannot discard pending defects
  (or vice versa). Clean rows with remaining work become `ready_partial`, promotion becomes
  `promoted_partial`, and the lease reaches `promoted` only after the backlog is empty.
- Each retry is preserved under `artifacts/<lease>/requeue/rqNN-{transient|defect}/` with its
  exact key file, conservatively collected defect-fragment hashes, harness, and execution
  manifest. Allocation advances past the highest state/history attempt and any existing
  `rqNN-*` directory. Unreferenced directories from hard interruptions are recorded as
  orphans and left untouched; only a newly created directory from a caught preparation
  failure is removed. Never copy retry output over prior artifacts or adopt/delete an orphan.
- Standalone `requeue_from_audit.py` remains compatible with the commands below. For a manually
  managed provenance-bound retry, add `--manifest-out <path>` and pass that exact manifest to
  `audit_window.py --execution-manifest <path>` when recording the result.
- `no_pwg_scale_plan.py` reads the tracked `no_pwg_residuals.jsonl` decision ledger and
  skips keys whose latest status is `blocked`. Append a later `retry` or `resolved` row to
  reopen one key, or use `--include-residuals` for a deliberate one-run override. Do not
  delete the history or repeatedly spend Max quota on a documented deterministic failure.
  A fully blocked chunk is listed in `omitted_windows` and does not consume
  `--limit-windows`; preparation advances to the next eligible deterministic index. Plan
  manifests retain plan-wide `selected_headwords` and separately report
  `prepared_headwords`. Staged acceptance uses only windows carrying prepared `headless`
  metadata, so future plan rows cannot inflate its window or headword denominators.
- DeepSeek corpus-lexicon API calls are append-only/resumable in `build_corpus_lexicon.py`.
  Use `DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`, `DEEPSEEK_READ_TIMEOUT`, and
  `DEEPSEEK_BACKOFF_BASE` to tune retry behavior; failed API batches are logged locally and
  can be retried later with `--retry-failed`.

If `requeue.keys.txt` is non-empty, generate the rerun harness directly from it (pass
`--transient` for the cheap null-only re-run, `--defect` for the rework-only set):

```powershell
python src\pilot\requeue_from_audit.py sTA --transient   # null cards only (state transient_only)
python src\pilot\requeue_from_audit.py sTA               # all requeue keys
```

Prepare the regenerated manifest as a coordinator requeue attempt and resume it
through the same bounded headless route. Do not manually run/save the generated
Workflow JS.

If `requeue.keys.txt` is empty and `judge_sample.keys.txt` is non-empty, send only those keys to
the sampled semantic judge outside Python. Do not block mechanical acceptance on unrelated
documentation cleanup or print-readiness gates.

## Instrumentation

For each bounded headless window, record:

- `OFFSET`, `LIMIT`, fresh units, rejected units, and successful merged cards;
- wall-clock minutes;
- CLI-reported input/output/cache tokens and observed cost, or the explicit
  unevaluable-cost stop;
- **`cache_creation_input_tokens` vs `cache_read_input_tokens` SEPARATELY, per call** — not a
  combined total. Creation is billed ~20× read, so the split is the whole cost story, and a
  combined figure hides it. Record the TTL bucket too (`cache_creation.ephemeral_1h…` vs
  `…_5m…`): that single field is what refuted the "cache expired" explanation without needing
  an experiment (FINDINGS §284). Note that `subagent_tokens` is a **legacy misnomer** for the
  sum of the four token fields — no subagents are involved; never read it as scaffolding cost;
- **`duration_api_ms` alongside wall clock**, and the derived `api_gap_ms` between them. Gating
  on wall clock alone silently encodes machine load and CLI startup into what is supposed to be
  a route measurement (§267/§270 both mis-attributed the same gap);
- whether the weekly cap fired, and cumulative tokens at that moment.

`audit_window.py` records the operational state, next action, sample counts, and any token/time
measurements in `window_status.json` and `window_ledger.jsonl`. Append milestone summaries to
`PILOT_COST.md` §6 when a root or run-to-cap tranche is complete. The point is to answer the
feasibility question: one Max seat over roughly two months vs a paid API bulk run.

## Post-launch closeout

Every headless/legacy-Workflow/API launch with a failure, null wave, stall, kill, stale-artifact refusal,
retry pass, cost drift, or suspicious residual must be registered in
[`../../LAUNCH_FUCKUPS.md`](../../LAUNCH_FUCKUPS.md) before the handoff is closed. The
entry must include expected vs actual agents/tokens, pass count, failure class, root cause,
guardrail/fix, and residual risk. This is the exhaustive incident register; the narrative
history in [`../../PIPELINE_HISTORY.md`](../../PIPELINE_HISTORY.md) only gets curated
phase-level lessons.

Closeout checklist:

```powershell
# Update the live state and launch evidence.
# - .ai_state.md: handoff result and next physical action
# - src\pilot\RUN_LOG.md: launch metrics and pass/fail narrative
# - LAUNCH_FUCKUPS.md: classified failure record for any non-clean launch

python src\pilot\check_launch_ledger.py --handoff H220
python src\pilot\check_launch_ledger.py --since 2026-07-05
```

Calibration is lane-specific. Keep separate evidence for `verb batch`, `nominal small`,
`nominal monster`, `no-PWG single`, `synth fan-out`, and `external API mining`; do not copy
one lane's kill-budget, cost, or concurrency envelope into another without a measured
launch/replay. H220 is the standing counter-example: the dense-root kill gate was correct
for verb batches but false-killed valid no-fallback no-PWG singleton cards.

## Worked example A — headless live-gate + canary (H1447, 22-07-2026) — **primary teaching case**

Real measured headless path (not Workflow). Full packet:
[`pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md).
Skill: [`/pwg-live-gate`](https://github.com/gasyoun/claude-config/blob/main/commands/pwg-live-gate.md) on profile **c4**.

### A0 — offline floor (no tokens)

```powershell
python src\pilot\window_selftest.py
python src\pilot\lang_parity_check.py
```

H1447: **180/180** selftests PASS; parity **73** entries no drift (counts grow — re-run).

### A1 — health (representative ≥5 KB)

Via [h963_c4_gate0_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py). **The pass rule is DERIVED, never
restated here:** the probe reads `probe_log.POLICIES[probe_log.CURRENT_POLICY]` and prints the
ceiling it judged by on its own `ceiling` header line — read that, not this page. The numbers
in the H1447 table below were taken under `production_v1` (30 000 ms wall, no route ceiling)
and are kept as **dated history**; the live policy has since been `production_v2` (65 000) and
is now `production_v3` (80 000 ms wall **and** 45 000 ms route). A runbook that names a live
threshold goes stale within days — this one had, and said "strict: measured ≥ 30 000 ms ⇒
NO-GO" for two policy generations after that stopped being true (H2254).

| Reading | Elapsed | Result |
|---|---|---|
| warm-up | 17 972 ms | success, 0 connection errors |
| measured | **16 621 ms** | **GATE-0 PASS** (under 30 s ceiling) |

Prompt was 6 828 B (≥ 5 KiB floor), schema-carrying. Contrast prior NO-GOs on the
same route (H963 104 870 ms; H1110 98 625 ms) — **today's** reading is what
matters; never reuse H1447's GO a day later.

### A2 — canary (`dq_canary_puregloss`) on headless manifest v2

| Field | Value |
|---|---|
| `execution_route` | `claude-cli-headless` |
| `profile_slot` | `c4` |
| `model_identifier` | `claude-sonnet-5` |
| `key_provenance` | `synthetic_control` (never promote) |
| senses | **3/3** |
| SAN-LOSS / TNMASK / unmapped / schema invalid | **0** |
| cost | **$0.573**, `cost_evaluable=true` |
| `--max-agents` | **1** is correct **only** for this single-key canary |

**The real command (H2245 — no longer "illustrative").** Build the manifest, then fire it.
Step 1 is offline and spends nothing; only step 2 is a paid call.

```
python src/pilot/canary_manifest_build.py --profile-slot c4 \
    --config-dir "D:\ClaudeTools\profiles\claude4\.claude" --outdir src/pilot/output/<hid>
```

It prints the manifest, harness, preflight and the `sha256` that step 2 needs, then the
exact `headless_worker.py` invocation to paste — `--only-profile c4 --max-agents 1
--timeout 300 --max-calls 3 --manifest-sha256 <sha> --preflight <path>
--call-reservation <path> --run-id <run-id>`. `--max-agents 1` is correct **only** here
(single-key canary); copying it onto a multi-key window re-creates the only-b0 starvation
class. Judge with [`canary_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_gate.py)
`judge`. Synthetic output is **never** promoted (`provenance_class =
synthetic_control`; the promoter's C-05 refusal is designed behaviour, not a failure).

A known-good manifest is committed beside the fixture —
[`dq_canary_puregloss~~h0_zz_pw.manifest.v2.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h994/canary/dq_canary_puregloss~~h0_zz_pw.manifest.v2.json)
— so a fresh build can be diffed against it;
[`canary_manifest_build_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/canary_manifest_build_selftest.py)
does exactly that (wired into `window_selftest.py`). The canary rides the **production**
`nominal_masked` prompt path: on pure gloss the mask is provably an identity transform
(zero `{Tn}` placeholders), so no canary-specific prompt variant exists or is wanted.

> **`--timeout` is part of the ceiling, not just a safety net (#983, 02-08-2026).** The
> effective per-call bound is `min(--timeout × 1000, budgets.timeout_ceil_ms,
> HARD_TIMEOUT_MS)`, so passing `--timeout 180` pins the old 3-minute ceiling **even after
> the constants were raised to 300000** — which is how a paid window returned zero cards
> with 12 of 16 calls killed at exactly 180 s. A sealed manifest's own
> `budgets.timeout_ceil_ms` clamps it too and only ever *lowers*, so an artifact prepared
> before this change must be re-budgeted, not merely re-run.
>
> **H2254 (07-08-2026) — above the maximum is now REFUSED, and the default IS the maximum.**
> 300 000 ms is an absolute maximum by owner ruling (03-08-2026); raising it again needs a
> new ruling backed by measured evidence. Three things changed, and the first is the one that
> bites an operator:
>
> - **`--timeout` now defaults to 300, not 7200.** The two-hour default only ever survived
>   because every route clamped it silently. Asking for nothing gets the maximum.
> - **A request ABOVE the maximum raises instead of rounding down** — on `--timeout`, on a
>   sealed `budgets.timeout_ceil_ms`, and in `validate_manifest` (so the planning routes
>   refuse it too, not just the executor). The refusal happens *before* any subprocess is
>   spawned, so a wrong request costs nothing. Lower values still bind exactly as before;
>   the `min()` above is unchanged.
> - **The number itself is imported, not copied.** `execution_contract.PRODUCTION_HARD_TIMEOUT_MS`
>   is the single source for `headless_worker.HARD_TIMEOUT_MS`, `gen_opt_harness2.KILL_CEIL_MS`,
>   the `KILL_CEIL_MS` baked into every generated `run_pilot_wf.*.js`, and the
>   `budgets.timeout_ceil_ms` each manifest seals — the five-places-one-inert-edit trap #983
>   documented.

### A3 — mechanical LIVE_GO → then stop or spend

H1447 derived **LIVE_GO**, then the production medium50 starter stopped honestly
at fleet warm-up (**zero production keys translated that session**). The teaching
point: gate GO is necessary; it does **not** auto-authorize spend without a
fresh gate at spend time and a prepared lease.

### A4 — production window shape after a fresh GO (template)

When the journal queues a real window (e.g. medium50 w1, 3 keys):

```powershell
# skills preferred: /pwg-bounded-run then /pwg-window-close
python src\pilot\gen_opt_harness2.py <root_or_window>
python src\pilot\coordinator.py prepare LEASE_ID `
  --profile-slot c4 --config-dir C:\path\to\claude-c4 `
  --executor-lane serial-whole-card
python src\pilot\bounded_staged_run.py `
  --plan <plan.json> --coord-dir <coordinator-dir> `
  --coordinator src\pilot\coordinator.py --cwd RussianTranslation `
  --events <events.jsonl> --only-profile c4 --max-accounts 1 `
  --max-windows 1 --max-calls <N> --cost-ceiling <USD> --run-id <stable-run-id> `
  --call-reservation <calls.json> --checkpoint <checkpoint.json> `
  --canary-receipt <canary_receipt.json> `
  --execute --stop-before-promote
# H2157: --execute now REQUIRES both --max-calls and --cost-ceiling (a paid run
# refuses to start unbounded); --allow-unbounded is the explicit escape hatch.
# H2159: --execute now also REQUIRES a fresh canary GO receipt — after the live-gate
# canary run `python src\pilot\canary_gate.py judge <out.json> --receipt <path>`;
# verdict/age(≤6h)/profile are validated mechanically. --skip-canary-gate is the
# explicit escape hatch.
# No --max-agents 1 on multi-key; clean output stops at AWAITING_REVIEW.
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
# /pwg-window-close: promote only if bound manifest-v2 + gates green
```

Omit `--max-agents` on multi-key / heal-capable windows so manifest
`max_translate_agents` / `max_heal_agents` apply. Worker hard-refuses
`N < selected_keys` before paid calls (H1618).

---

## Worked example B — historical Workflow scale sample (vid, 04-07-2026)

**Not the production executor.** Kept only for scale intuition (presplit fan-out,
token volume). New attempts use example A + headless.

A concrete run, with real numbers.
`vid` (55 sub-cards, 5 giant heads at 141-193 `<ls>` citations each):

1. **Preflight:** `python src\pilot\perf_preflight.py vid as BU yuj` → recommended
   order `vid, as, BU, yuj` (agent estimates as of the fixed estimator: 63/21/…).
2. **Generate:** `python src\pilot\gen_opt_harness2.py vid` → 55 cards in 8 batches,
   5 cards routed to presplit (each too dense for one call).

   A new CLI/headless production attempt must mint manifest v2 and bind the actual logical slot
   and config directory at preparation time, for example:

   ```powershell
   python src\pilot\coordinator.py prepare LEASE_ID `
     --profile-slot c4 --config-dir C:\path\to\claude-c4 `
     --executor-lane serial-whole-card
   ```

   `c4` is a roster slot, not evidence of billing identity. Later execution must repeat
   `--only-profile c4`; the orchestrator checks the slot and directory fingerprint against the
   sealed manifest. Old v1 manifests are historical-audit inputs only and cannot be promoted.
3. **Run:** the historical `vid` run drove `run_pilot_wf.opt2.js` via Workflow. Do not use that
   route for a new profile-bound v2 attempt: Workflow cannot prove `CLAUDE_CONFIG_DIR` or join the
   host-wide active-call claim, so a bound generated template now aborts before its first agent
   call. Run the execution manifest through the CLI/headless route instead: use the bounded
   command's default dry-run first, then explicitly add `--execute --only-profile c4`. Every
   admitted production entry point holds the global config-fingerprint claim, so a second c4
   launch fails closed instead of spending concurrently.

   **`--max-agents` is a TOTAL spawn ceiling (translate+heal), not concurrency width**
   (H1610 / ledger `C2_M50_W1_MAX_AGENTS1_2026-07-24`). Use `--max-agents 1` only for true
   single-spawn canaries (one key that must finish in one call). Multi-key / heal-capable
   windows must **omit** the flag so manifest `max_translate_agents` / `max_heal_agents`
   apply. `headless_worker` now refuses `N < selected_keys` before any paid call, and
   preserves `budget_exceeded*` notes instead of overwriting them with
   `selfheal-nothing-resolved`.

   Real result: **102 agents, 6,626,992 tokens, ~19 min wall-clock.**
4. **Capture:** read the workflow task's `.result` from its output file (holds the
   full `{meta, summary, results}` payload uncapped) and write it to `wf_output.json`
   directly — do not rely on the completion notification text, which truncates.
5. **Reorder before auditing:** the harness emits `results` in TM-lane /
   degenerate-lane / batch-completion order, which essentially never matches the
   rootmap's declared `meta.selected_keys` order even though every key is present.
   `window_provenance.stale_check` now compares as sets (fixed 04-07-2026), so this
   step is no longer mandatory, but reordering to `meta.selected_keys` order first
   is still good hygiene (keeps `wf_output.json` in a canonical, diffable shape).
6. **Audit:** `python src\pilot\audit_window.py wf_output.json --root vid --write-requeue`
   → 34/55 clean, 21 requeue (10 transient null, 11 defect), 8 partial-but-usable.
7. **Requeue:** `python src\pilot\requeue_from_audit.py vid` (now automatically
   appends `--no-tm` on anything but `--transient` — fixed 04-07-2026) → a 21-key
   harness, ~7 agents expected. Run it the same way as step 3, then repeat steps
   4-6 until requeue is empty or clearly diminishing (compare to the `gam` history:
   two rounds recovered most residuals, a stubborn few needed a manual resolution).
8. **Promote + rebuild TM:** `promote_final_cards.py --gen-model-version claude-sonnet-5`,
   then `translation_memory.py build --lang ru` (+ `build-frags` if any heal emitted
   `frag_prov`). Promotion requires the canonical store to exist: a missing or misresolved path is
   a hard refusal so backup/shrink/merge guards cannot be bypassed. `--init-store` is reserved for
   an explicit first-ever initialization and itself refuses an existing store. Never use it to
   recover a missing production path. Every candidate is revalidated for final-card schema,
   exact manifest-key membership, real (non-synthetic) provenance, and unresolved `{Tn}` tokens
   immediately before the atomic store replacement.
9. **Close out the launch ledger:** if the run had nulls, retries, kills, stale-artifact
   refusals, or cost drift, update `LAUNCH_FUCKUPS.md` and run
   `python src\pilot\check_launch_ledger.py --handoff H151` (or the active handoff ID).
10. **Micro-commit**, move to the next queued root.

What this run taught (folded into the process above, not left as trivia): the
preflight's agent-count estimate was badly wrong for presplit-heavy roots (now
fixed); 100% of the null cards traced to 2 batches that failed outright, and
specifically to the undersized cards inside them that have no fragment fallback
of their own (an open follow-up, not yet fixed — see `PIPELINE_HISTORY.md`).

## Done criterion

The frequency queue milestone is done when:

- every manifest entry in the target frequency window has a merged card or a
  glued nested article;
- zero `*.merged.REJECTED.md` files remain for that window;
- rootmap-backed giant roots have matching `*.NESTED.md` outputs;
- the cost/quota table has enough windows to estimate the run duration;
- every non-clean headless/legacy-Workflow/API launch in the window has a complete
  `LAUNCH_FUCKUPS.md` entry and passes `check_launch_ledger.py`.
