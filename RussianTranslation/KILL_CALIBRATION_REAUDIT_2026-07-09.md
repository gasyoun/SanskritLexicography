# Kill-calibration + Windows/encoding re-audit (H426, adversarial)

_Created: 09-07-2026 · Last updated: 09-07-2026_

Read-only adversarial re-verification of the two H426 concerns on `origin/master`
**[`9ac9ed1`](https://github.com/gasyoun/SanskritLexicography/commit/9ac9ed1)**:
(1) does each launch lane use the right timeout *model*, not just a timeout, and is a
kill cascade *diagnosable* rather than guesswork; (2) are the Windows/encoding/path traps
each deterministically guarded. Model: Opus 4.8 (`claude-opus-4-8`). One of four adversarial
re-audits (H423–H426).

**Verdict: 🟢 re-verified clean.** No wrong or missing budget model; no unguarded encoding
trap. **One open diagnosability flag** — per-window `gen_model` still unstamped in the
launch-outcome population (H390 item 4) — spec'd below, not fixed (the H426 fix-PR scope is
budget-model / encoding-trap only, and this scope item explicitly says "flag if still
unstamped").

---

## 1. Per-lane runtime-budget model

Each of the five ledger lanes has its **own** budget model — none inherits the dense-root
default blindly. Sources: [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py),
[`synth_dispatch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py),
[`perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py).

| Lane | Where set | Budget model | Correct? | Failure a wrong budget would cause |
|---|---|---|---|---|
| **dense verb roots** | `killBudgetMs` (`gen_opt_harness2.py:1271`) | byte-scaled per call: `2.0 × (20 000 ms + 45 ms/skel-byte)`, clamped `[45 s, 180 s]`; SLOPE set **above** the observed 44 ms/byte ceiling | ✅ | too-strict → mis-kills a legit slow dense call; the factor+slope headroom means no legit call (even +50 % variance) is killed, while a ~5× retry-cap stall blows past |
| **nominal no-PWG singles** | `killBudgetForCur` → `KILL_CEIL_MS` = 180 s (`:1283`, H220) | fixed CEIL because a single fragment with `!hasFallback` has **no smaller lane** for the gate to route to | ✅ | the dense byte budget (53–104 s) is below a tiny single's fixed StructuredOutput latency (55–105 s) → the `NO_PWG_DIAG` 6/6-null kill-timeout incident (H220) |
| **presplit fragments** | `PRESPLIT_GROUP_CITE_BUDGET` = 60 / `PRESPLIT_GROUP_SENSE_CAP` = 18 (`:83`, `:86`, H189) + the per-call byte gate above | citation-weighted grouping cap to amortize the ~25–30 k-token framework prompt across a presplit-PRIMARY card | ✅ | grouping at 12 under-amortizes the framework prompt → the `pril10_w1` ~$80 / 3-card cache-write blow-up (H189) |
| **topups (StructuredOutput retry cap)** | bounded topup/acceptance rule; class = **`structured-output-limit`**, kept separate from `kill-gate-calibration` | acceptance-cap, NOT a wall-clock budget | ✅ | folding it into the kill-gate class misdiagnoses a retry-cap residual as a timeout — the `DAH_TAIL` separation the ledger insists on |
| **synthesis fan-out** | `synth_dispatch.py`: `MAX_CONCURRENT_DEFAULT` 3 / `HARD_CAP` 4 (`:60`), `KILL_AFTER_S` 600 **output-file-growth** stall (`:62`), confirmed-dead-before-redispatch, sealed outputs | liveness = output-file growth, never transcript bytes | ✅ | a byte/transcript-byte kill false-stalls on buffered or 0-byte transcripts — the H234 Arm-B 10-wide fiasco |

**Window-level backstop (all lanes):** `MAX_AGENTS = ⌈expected × 3⌉ + 10`, size-proportional
so a small window can't burn a flat-40 floor before the switch fires (`gen_opt_harness2.py:189`,
`:193`, `:197`). **Preflight cost gate:** `COST_CEIL_PER_CARD_USD` = 2.00 (`perf_preflight.py:42`),
calibrated from the `pril10_w1` figures (184 k tok/agent, $0.347/agent), `--refuse-over-cost`
for unattended callers.

### Kill-cascade diagnosability — can the operator tell miscalibration from transient API?

Yes, and the chain is now **fully closed**. The failure modes are separately classified with
distinct symptoms in
[`LAUNCH_FUCKUPS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md):

- `kill-gate-calibration` (`NO_PWG_DIAG`, H220) — a lane's budget is wrong.
- `structured-output-limit` (`DAH_TAIL`, H178) — retry-cap residual, **explicitly "not the H220
  kill-gate class"**.
- `concurrency/api` (`H317_MEDIUM50_3WIDE_KILL_CASCADE`) — root cause records **both** measured
  causes (3-wide is not a safe floor **and** a session-wide `Connection closed mid-response`
  outage present even at 1-wide), then marked **superseded** by
  `H389_MEDIUM50_SCHEMA_CLASSIFIER_BLOCK`: the block was neither kill-gate nor transient but the
  deterministic agent() output-schema safety classifier.
- `structured-output-limit` (`H428_OPT2_SCHEMA_SLIM_FIX`, landed this pass as
  [#290](https://github.com/gasyoun/SanskritLexicography/pull/290) / `9bd92a3`) — **FIXED**:
  `_strip_post_generation_fields()` drops annotator-added fields from the *generation* schema
  (reachable 10,940 → 1,698 chars, 84 %), pinned by
  `test_generation_schema_carries_no_post_generation_field`; a solo diagnostic call
  (`root=vinasa`) returned a valid card at 75,774 tokens vs 0 pre-fix. This unblocks H389,
  the H388 B-arm, and the H151 verb drain.

So an operator hitting a null window today has four mutually-exclusive classes, each with a
distinct symptom fingerprint and a distinct next action — no guesswork.
[`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
now (a) treats **3-wide as an upper bound, not a target** (line 346), (b) **requires a clean solo
1-wide reference window** before trusting any concurrent width in a session showing these
symptoms (lines 350–353), and (c) forbids porting one lane's kill-budget/cost/concurrency
envelope into another without a measurement (line 439).

---

## 2. Windows / encoding / path trap checklist

| Trap | Guard status | Evidence |
|---|---|---|
| **subprocess decoding** (cp1252 default) | ✅ GUARDED | every output-capturing `subprocess.run` in the pilot tree carries `encoding='utf-8'` (`audit_window.py:64`, `calibrate_perf_harness.py:166`, `requeue_from_audit.py:179`, `run_real_test.py:137`, `no_pwg_scale_plan.py:120`; org-tree `make_edition_cut`/`preflight_remaining_gates`/`release_readiness`/`coordinator`/`review_changelog_guard` too). Static pin: `test_subprocess_gate_calls_hardened` (`window_selftest.py:3457`). `lod_acceptance.py:207` captures **bytes** (no `text=`) and never decodes — not a decode trap. |
| **CRLF key-list readers** (H220 key-echo class) | ✅ GUARDED | key-consuming reads are CRLF-safe: `requeue_from_audit.py:64` uses `ln.strip()`; `read_lines_result` (`window_common.py:128`) uses `rstrip('\n')` but Python default text-mode read applies universal-newline translation (`\r\n`→`\n`) *before* it, so no `\r` survives into `--keys=` matching or `km[k]`. |
| **BOM add/strip** (inconsistent here — MW key1 has one, key2 doesn't) | ✅ GUARDED | `utf-8-sig` used **on read only** (`pwg_mask.py:44`, `ingest_oral.py:118`) — strips a leading BOM in-memory without rewriting the file, so source BOM state is preserved; CSV round-trips deliberately keep their BOM (`gold_*.py`, `preflight_remaining_gates.py`, `newline=''`). No blanket strip. |
| **exact-case filenames + safe-name/key round-trip** | ✅ GUARDED | H220 `nominal_keymap` (`gen_opt_harness2.py:1137`) re-keys a clean SLP1 portrait key back to its mangled `~~h0_zz_*` safe-name header when it maps to exactly one pending stem, gated on `META.nominal` (PWG strict matching untouched); the key-echo drop is fixed and selftest-pinned. |

---

## 3. Flag — diagnosability gap still open (H390 item 4)

Per-window **`gen_model` is still unstamped** in the launch-outcome population:

- [`window_reports.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_reports.py)
  `build_production_metrics` (`:88`) records `wall_clock_minutes` / `max_output_tokens` but
  **no model field**; `append_ledger` (`:125`) writes a compact `window_ledger.jsonl` row with
  no model field either.
- [`harvest_launch_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/harvest_launch_stats.py)
  `load_ledger` (`:100`) therefore surfaces no `gen_model`; `LAUNCH_STATS.md` contains 0
  occurrences of it.
- The **store** rows *do* carry `provenance.model_version` (`promote_final_cards.py:120`,
  selftest-pinned to the exact version) and the coordinator lease captures `model_version`
  (`coordinator.py:613`) — so per-*card* provenance exists, but the per-*window launch outcome*
  (the population for "which lane/model kills more") does not join to a model.

**Consequence:** "which lane/model kills more" stays unanswerable from `LAUNCH_STATS.md`, exactly
as H390 item 4 measured (1/450 windows had tokens, none had `gen_model`).

**Fix spec (cheap, deterministic — not executed here):** thread the resolved
`--gen-model-version` (already required at promote time) into `audit_window.py`'s ledger emit →
add `gen_model` to `build_production_metrics` → include it in the `append_ledger` compact row →
surface it in `harvest_launch_stats.load_ledger`, then add a per-model kill/requeue-rate
breakdown column to `LAUNCH_STATS.md`. No zero-touch path exists (most windows run the direct
production path, not the coordinator), so this needs the operator to pass the version at audit
time — hence flagged, not silently auto-fixed.

---

_Dr. Mārcis Gasūns_
