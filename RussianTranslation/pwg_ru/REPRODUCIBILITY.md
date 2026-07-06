# PWG→RU pipeline — reproducibility checklist

_Created: 07-07-2026 · Last updated: 07-07-2026_

A consolidated reproducibility statement for the PWG→Russian translation pipeline, in the
spirit of the [ACL Responsible NLP Checklist](https://aclrollingreview.org/responsibleNLPresearch/)
and Dodge et al. 2019, "Show Your Work: Improved Reporting of Experimental Results"
([https://aclanthology.org/D19-1224/](https://aclanthology.org/D19-1224/)) (citations from model
knowledge — verify before external submission). Everything below consolidates facts already
recorded in the run ledgers and handoff memos; nothing is new measurement.

## 1. Models and exact versions

- **Generation (translation):** Sonnet 5 (`claude-sonnet-5`) — hardcoded as `model:'sonnet'` on
  every `agent()` call by the generated harness
  ([gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)).
  The session model picker does NOT control generation; the only requirement is a
  Workflow-tool-capable session (H178 A-4a).
- **Orchestration (session driving the Workflow / audits):** varies by session and is logged
  per run block in [RUN_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md):
  Opus 4.8 (`claude-opus-4-8`) and Fable 5 (`claude-fable-5`) both attested; earlier stages Sonnet.
- **Judge policy (sampled only):** Sonnet judges, Opus adjudicates only its rejects
  ([research/JUDGE_POLICY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/JUDGE_POLICY.md)).
- **DeepSeek** (`deepseek-chat`): one-time corpus word-alignment lexicon build
  ($18.35 actual bill, 1.09 M alignments) via
  [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py); no per-card use.
- **Per-row provenance:** every promoted store row carries `provenance.model_version`
  (11,261/11,261 = exact `claude-sonnet-5` as of 06-07-2026) and the H170
  `provenance.pipeline` stamp `1.0.0/1.0.0/1.0.0`, verified by
  [audit_translation_provenance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_translation_provenance.py).

## 2. "Hyperparameters" — harness knobs

All defined in [gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) unless noted; every value is emitted into each generated harness and overridable by flag.

| knob | value | meaning / flag |
|---|---|---|
| `OUTPUT_BUDGET` | 90 | citation-weighted output units per batch (`--output-budget=N`; default 90 since 03-07-2026) |
| `SENSE_PRESPLIT_BUDGET` | 20 | senses per card before presplit routing (`--sense-presplit-budget=N`; H155) |
| `PRESPLIT_GROUP_CITE_BUDGET` / `SENSE_CAP` | 60 / 18 | presplit-lane fragment-group re-batching (H189 guardrail 1) |
| `HEAD_CIT_BUDGET` | 18 | head sense-chunking budget, in [_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py) (`sense_chunks()`) |
| `KILL_FACTOR` | 2.0 | kill a call at 2× expected-for-complexity time (`--kill-factor=N`, `--no-kill`) |
| `KILL_BASE_MS` | 20,000 | fixed per-call latency term (lowered from 30,000 at H189 recalibration) |
| `KILL_SLOPE_MS` | 45 | ms per masked-skeleton byte (above the 44 ms/byte observed ceiling) |
| `KILL_FLOOR_MS` | 45,000 | never kill before 45 s (H189; was 120,000) |
| `KILL_CEIL_MS` | 180,000 | hard 3-min ceiling (H189; was 480,000). H220 exception: a single card with no selfheal fallback gets the CEIL budget directly |
| `MAX_AGENTS` | `⌈expected × 3.0⌉ + 10` | live budget kill-switch (`MAX_AGENTS_FACTOR=3.0`, `MAX_AGENTS_HEADROOM=10`, `--max-agents=N` override) |
| retries | 1 per card/stage | plus the runtime's internal StructuredOutput retry cap (~5) |
| TM | `--tm=auto` default | card + fragment translation memory; **requeue denylists TM** — [requeue_from_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) auto-appends `--no-tm` on anything but `--transient` (fixed 04-07-2026) |
| concurrency | ≤3 root harnesses | Slice-D 18-wide collapse (117 transient nulls) is the standing counter-example |

Kill-budget formula: `clamp(FLOOR, FACTOR × (BASE + SLOPE × skel_bytes), CEIL)`; design and
calibration in [FAILURE_MODES_AND_KILL_GATE_2026-07-04.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md).

## 3. Compute — measured tokens and wall-clock per window

Real numbers from [RUN_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md) and [PILOT_COST.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PILOT_COST.md) (§1, §6.1):

| window (RUN_LOG block date) | cards | tokens | wall-clock |
|---|---:|---:|---|
| pilot, 15 dense a-cards (PILOT_COST §1) | 15 | 1,800,897 | 7.9 min |
| `sTA` first freq window (§6.1, 2026-06-27) | 106 | 10.3 M total (6.29 M cache_read / 3.70 M cache_create / 358,884 out) | 19.0 min, 0 transient |
| Stage A+B: `sTA`+rq / `BU` / `as` / `i` (2026-06-29) | 484 | 5,310,934 / 2,022,803 / 3,353,816 / 6,768,657 = **~17.46 M** (~36 K/card) | ~65 min translate total |
| `vid` (RUN_FREQ_MAX worked example, 04-07-2026) | 55 | 6,626,992 (102 agents) | ~19 min |
| `pril10_w1` nominal — **ABORTED** (2026-07-05) | ~3/8 done | 42,316,604 (~$79.83 API-equivalent; 60 % cache-write) | 20.1 min, 230 agents |
| `nominal_w1_100small`, 3 passes (2026-07-06) | 100/100 | 2,498,796 (957,970 + 1,402,160 + 138,666) | ~23 min |
| `dah` tail, 3 Workflow runs (2026-07-06) | 1 card + 17 frags | 75,693 + 1,144,751 + 1,147,780 | ~68 s / ~67 s / ~78 s |
| `no_pwg_w1` (2026-07-06) | 21/58 ok → 5 promoted | ~3.4 M across 3 passes | — |

Direct money cost ≈ $0 (Claude Max subscription, not API); the only cash spent is the
one-time $18.35 DeepSeek lexicon (PILOT_COST §1). The binding constraint is the Max weekly
token quota (never yet measured to the cap) and human review hours.

## 4. Data provenance

- **Source:** the 5-layer all-in-one per-card input — PWG main+Nachträge + PW + SCH + PWKVN +
  NWS (owner-mapped) — built by
  [_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py),
  live since commit `1dad0dd` (17-06-2026, 14:56Z), never reverted. `csl-orig/v02/pwg/pwg.txt`
  is the PWG *layer input only*, read-only.
- **Per-row hashes:** every promoted row carries `input_raw_sha256` + `input_portrait_sha256`
  plus `generated_at`; workflow `meta` additionally records the rootmap SHA-256 and per-input
  SHA-256, enforced by the audit stale guard.
- **Known exception:** 9 legacy `vid` rows carry no `generated_at` / no input SHAs (H188
  stripped-meta autosplit merge; fixed forward by `_autosplit_meta()` in
  [PR #197](https://github.com/gasyoun/SanskritLexicography/pull/197); the 9 rows were not
  backfilled — content spot-checked complete, see
  [H178_REAUDIT_2026-07-06.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_REAUDIT_2026-07-06.md)).
- **Store partition:** 0 pre-merge (pure-PWG) roots in the live store; all 50 roots/windows are
  post-merge all-in-one (H178 A-1(b)).

## 5. Code availability

Committed (public repo, full paths under `RussianTranslation/`):

- [src/_pilot_gen_merged.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py) — 5-layer source builder + sense chunker
- [src/pilot/gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) — batched+masked harness generator (all knobs of §2)
- [src/pilot/run_pilot_wf.js](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js) — prompt template (HARD RULES, CONV lines)
- [src/pilot/audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) — the deterministic gate runner
- [src/pilot/prompt_rule_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py) — prompt-rule wiring + semantic-risk triage
- [src/pilot/requeue_from_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) — transient/defect requeue (TM-denylisted)
- [src/pilot/promote_final_cards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/promote_final_cards.py) — promotion with `--gen-model-version`
- [src/pilot/translation_memory.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py) — card/fragment TM build + validate
- [src/pilot/perf_preflight.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py) — read-only cost/agent preflight + cost gate
- [src/pilot/verb_worklist.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py) — reproducible worklist enumeration
- [src/pilot/audit_translation_provenance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_translation_provenance.py) — store-wide provenance audit
- [src/pilot/window_selftest.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) — pinning selftests (83 PASS as of 06-07-2026)

**Gitignored (not distributable):** the promoted store `src/pwg_ru_translated.jsonl`, the TM
sidecars (`translation_memory.*.json`/`.jsonl`), generated inputs (`src/pilot/input/`, ~218 K
files), and all `wf_output*.json` artifacts. Reason: they embed substantial verbatim source
dictionary text and derived translations whose print/publication rights are not yet settled
(G5–G10 print gates pending); the code that regenerates them deterministically from the
sources IS committed.

## 6. Deterministic gate definitions (one line each)

- **NWS owner-map** — every NWS entry must attribute to its pre-parsed authoritative owner; a mismatch quarantines the card as `*.merged.REJECTED.md` (HARD RULE 5).
- **Markup fidelity** — restored `<ls>` / `{#…#}` counts must match source exactly; a miscount nulls the card → requeue, never emitted garbled.
- **Sense coverage** — card sense count vs the source render; `COVERAGE-LOW`/`COVERAGE-OVER` → requeue.
- **Sense-dupe** — duplicate sense tags within a card, namespaced by canonical `_marker_tags()` tags (Finding 10 fix).
- **Loud-fail (H169)** — pipeline errors surface as explicit failures/nulls, never silently-passing partial output.
- **Presplit triggers (H155)** — citations (`1+<ls> > OUTPUT_BUDGET`) OR senses (`frag_count > SENSE_PRESPLIT_BUDGET`) route a card to the fragment lane before any agent call.
- **Provenance audit** — every store row checked for exact `model_version`, pipeline stamp, input SHAs, staleness ([audit_translation_provenance.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_translation_provenance.py)).

## 7. Known nondeterminism

- **LLM sampling** — translations are not bit-reproducible; acceptance is defined by the
  deterministic gates of §6, not by output equality. Per-row SHA-256 of *inputs* (not outputs)
  is the reproducibility anchor.
- **StructuredOutput retry-cap class** — a schema-emission stall can hard-fail one attempt and
  succeed the next (e.g. `dah~~h0_zz_pw` topups: 12/17 then 15/17, union 16/17; one fragment
  failed both → documented 🟡 residual).
- **Transient API outages** — the `nominal_w1_100small` pass-1 precedent (2026-07-06): a network
  outage produced 5 ok / 95 null with `budget_kill_switch_tripped`; a clean rerun recovered
  93/100. Policy: split requeues into `requeue.transient.keys.txt` vs `requeue.defect.keys.txt`
  and re-run transients cheaply at low concurrency.
- **Concurrency-induced 429 nulls** — >3-wide runs cause transient nulls (Slice-D); bounded by
  the ≤3-wide discipline, not eliminated.

_Dr. Mārcis Gasūns_
