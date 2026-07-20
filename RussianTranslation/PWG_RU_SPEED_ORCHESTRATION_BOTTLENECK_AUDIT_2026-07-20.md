# PWG→RU speed & orchestration audit — bottleneck ledger + adversarially verified action map

_Created: 20-07-2026 · Last updated: 20-07-2026_

> **Provenance.** Handoff [H1403](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1403-Fable_RussianTranslation_pwg-ru-speed-orchestration-audit_20.07.26.md).
> Produced by a 22-agent ultracode Workflow run (`wf_1b45f9b1-8f3`): 5 subsystem miners →
> 1 synthesizer → 16 adversarial verifiers (two lenses per recommendation — prior-art/standing-ruling
> and real-wall-clock-impact), every agent Fable 5 (`claude-fable-5`); ~2.13 M subagent tokens,
> 341 tool calls, ~29 min wall. Question answered: *"How to improve even more speed of PWG
> translation? How to improve orchestration?"* All claims below carry file-level evidence gathered
> read-only; no pipeline file was changed by the audit itself.

## 0. Headline result

**0 of 8 synthesized recommendations survived adversarial verification unmodified — 6 WEAKENED,
2 REFUTED.** The dominant weakening/refutation reason was *"this already exists, shipped or
queued"*: the pipeline is not short of speed ideas. The binding constraints are (a) an external
transport outage with the one validated fallback lane sitting parked, (b) the human operator loop
around a strictly serial control plane, and (c) telemetry non-compliance that keeps every
width/lane/model decision open-loop. The fastest path to more speed is **executing already-minted
work and closing the telemetry loop**, not designing new mechanisms.

## 1. Staleness caveat — audit tree vs origin

The miners read the local main checkout (v1.36.0-era, commit `1cfc2a88`); origin/master was at
v1.45.0 the same day. The gap was reviewed post-hoc: the only throughput-relevant landing is
**H1339 factory hardening** (merged 20-07, commit `0bb6a11e`): offline factory path total
−23.0 % (store-write −49.8 %), batched multi-lease promotion, real requeue materialisation
(`::rqNN` jobs), h1209-lane fixes B05–B07. This is *consistent* with the ledger below — the
offline Python path was already ranked a non-bottleneck (§2 row 9) — and it *strengthens* the
row-2 refutation (the supervised driver exists and is being hardened, not missing). No gap
commit contradicts any verdict. H1349 (GlossTM) and H1350 (data layers) are off the
throughput-critical path.

## 2. Bottleneck ledger (ranked by wall-clock magnitude)

| # | Bottleneck | Magnitude (measured) |
|---|---|---|
| 1 | **Generation-transport availability (external)** — the validated fallback lane sits parked | 6 consecutive days 14-07→20-07 at **zero promoted cards** (store frozen at 11,605 rows); healthy-vs-degraded era differs ~10–100× (29-06: ~0.2–0.3 min/clean, 401 clean in ~65 min generation wall; 15-07: 1 and 5 clean per ~50-key window); c4 headless 98,625–104,870 ms vs 30 s ceiling. Same-day divergence proves transport-specificity: Workflow-`agent()` 15.74 s GO on 18-07 while c4 headless was NO-GO — yet the validated H1209 controller-worker lane has been parked pending its medium50 batch since 18-07 |
| 2 | **Human operator loop + strictly serial control plane** | Generation is only **~12–22 % of chain calendar**. Measured 12-07: 1 h 56 m probe→launch, 1 h 45 m window-end→requeue, vs 4.2–23 min generation walls and a **4-minute** rq1→rq2 turnaround when the operator was hot; chain delivered 27 clean in 4 h 25 m (~9.8 min/clean) of which ~73 s/clean was generation. Recoverable ≈ 2–4× calendar throughput per operator session |
| 3 | **Blended clean-rate metric hides two axes** | H911's ~41–69 % (median ~62 %) blend conflates infra-null transients (52–57 % transient on degraded windows; H920: w05_rq1 `missing_senses` were ALL infra-nulls) with genuine content defects (content-clean 401/484 = **83 %** on the only audited split). Defect requeues converge at 18 % (sTA rq2: 6/33, 190 K tok/clean = 4.1× tokens, 6.7× wall vs first pass); span-drop + darvī-class SAN-LOSS are requeue-immune, blocked on unshipped H858 Tier-1 / gated H920 arming |
| 4 | **Per-window floor: 55–105 s StructuredOutput latency × ≤3-wide cap, no re-widening path** | 20-card window floor ~6–12 min (observed 8.6–23 min). The cap is static in 4 places ([`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) `MAX_WIDE=3`, [`coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) `TRANSLATION_LIMIT=3`, runbook rule, runtime override), set entirely on degraded-transport evidence (Slice-D 18-wide; H811 ~10-wide; ≤3 → 78 % non-null); widths 4–8 never bracketed on healthy transport; per-window telemetry (`kill_timeouts`/`conn_errors`/`null_keys`) is consumed by nothing |
| 5 | **Zero cross-agent prompt-cache reuse, by construction** | ~25.3 K tokens cache-WRITTEN per `agent()` call and discarded at agent end — 46 % of cache-write and **27 % of the whole $80 pril10_w1 bill** at 230 calls ([`POSTMORTEM_pril10_w1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/POSTMORTEM_pril10_w1.md)). Token-economics first, wall-clock second |
| 6 | **Instrumentation blindness** — the pipeline cannot compute its own headline metric | Wall-clock recorded on 12/458 launched windows, output tokens 1/458, generating model 0/458; H911's economy gate returned INCONCLUSIVE (`tokens not_recoverable`) for exactly this reason. Every width/lane/prompt decision runs open-loop; the operator-gap numbers above had to be reconstructed by timestamp archaeology |
| 7 | **Waste lanes re-paying known outcomes** (largely fixed 15-07, residue remains) | Pre-#478: 35 % (7/20) of the 14-07 window were documented residuals hand-filtered via `--keys`. PR #478 shipped [`no_pwg_residuals.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residuals.jsonl) + planner consumption; residue = C-49 backfill (w02–w05 residuals unledgered, no reconciliation checker) and no auto-appender in [`requeue_from_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py). Exact-TM elimination on fresh roots is measured **0** (0/31, 0/19, 0/12, 0/100; byte-exact cross-card ceiling 0.36 %) — no offsetting free wins exist |
| 8 | **Idle validated capacity + one never-evaluated lane** | c5/c6 `loggedIn:false`, c1 unused during single-session drains (≤2× quota headroom idle, contingent on transport + H911 freeze). The **Anthropic Message Batches API — latency-immune by design (async 24 h, ~50 % cost) — was never probed, costed, or dead-ended** in 3+ weeks of latency-blocked lanes: zero grep hits repo-wide and across Uprava handoffs |
| 9 | **Measured NON-bottlenecks — spend nothing here** | Deterministic audit ~21 min cumulative across 3.5 weeks (~1–2 s/window); weekly token cap has not fired since the 27-06 reshape; prompt size ruled (lean-TR rejected); monster kāla-class windows parked by ruling; offline factory path further cut −23 % by H1339 (20-07) |

## 3. Verified action map — what actually moves the needle

Ordered by surviving value after the adversarial pass. "Status" = verdict of the two-lens
verification; the caveats are the verifiers', not softened.

### A1. Run the queued H1209 medium50 batch (status: WEAKENED-only-because-already-minted)

The single highest-value action, and it is **already minted work, parked since 18-07**
([H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md);
worklist `H317_medium50_worklist.08.07.26.json` on disk; rig complete under
[`src/pilot/h1209/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1209)).
On degraded-transport days baseline is 0 promoted cards, so the Amdahl case is clean: this
unblocks the only stage that matters on those days. Verifier caveats: (a) v2 slice wall was
~14.7 min/clean (n=3, all-complex, promote-DRY) — the per-call 15.74 s does NOT translate 1:1 to
per-clean wall; medium50 IS the missing measurement, do not scale past it blind; (b) adopting the
lane as *standing fallback* front-runs the handoff's own two-input gate (medium50 **plus** H1210
DeepSeek A/B) — codify the fallback rule only after both; (c) the 20–40 % token cut from
persistent-worker cache amortization is a **hypothesis** (whether Workflow `agent()` shares a
cached prefix across a worker's calls is explicitly unknown). Cheap adjunct worth one A/B window:
prefix reorder PREAMBLE + CONV_TR + GRAMMAR (currently GRAMMAR before CONV_TR at
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
~:1828/:2031) — a *reorder*, not the rejected lean-TR trimming; keep lean-mode NWS_RULE last.

### A2. Finish H390 methodology rule 4(a) — instrumentation as code, not operator discipline (WEAKENED = "finish it, don't design it")

The field list and backfill tool are already the repo's own standing rule
([`LAUNCH_FUCKUPS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
rule 4, H390) and Phase 1 (`gen_model` stamping) shipped 12-07. What is missing is the
**automation**: auto-derive wall-clock in
[`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)
instead of the almost-never-used `--wall-clock-minutes` flag (12/473 ledger rows carry it),
agent-call count per row, `stage_boundary` dashboard events for the in-chat lane (zero grep
hits), and actually running the prescribed
[`parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py)
transcript backfill. Verifier caveat: `meta.generated_at` is stamped at harness-generation time,
so generated_at→save-mtime alone conflates generation wall with operator idle — ship the
stage-boundary events with it, or the auto-stamp systematically overstates generation wall.
Effort S; this is what turns every later width/lane decision closed-loop.

### A3. Operator-loop residues — three small closures, NOT a new driver (core REFUTED, residues real)

The "write one supervised driver" recommendation was **refuted**: the chain already exists three
times over (`/pwg-drain` skill chain, [`bounded_staged_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py)/`BoundedSupervisor`,
and the H1209 rig with FREE in-run retry — better than a Python driver could, since a standalone
script cannot fire the Workflow tool at all). The verified residues worth doing: (a)
[`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py)
has **no defect-refusal flag** — the measured w02 promote-then-revert footgun
(`LAUNCH_FUCKUPS.md` H255_NO_PWG_W02) is still open; add refuse-defect-keys-without-`--force`;
(b) overlap next-root harness generation + preflight (pure Python) *during* a running window —
the whole-window barrier in `BoundedSupervisor` is real; (c) automate `ready_partial` clean-subset
promotion (supported, mandated by the runbook, unautomated). Realizable gain per operator session
≈ 2–3× (the 3–4× claim double-counted deliberate degraded-API caution inside the measured gaps).

### A4. Split content-clean from transport-yield — forward-only reporting (WEAKENED)

Add `content-clean = clean/(generated non-null)` + a separate transport-yield SLO to
[`cohort_clean_rates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cohort_clean_rates.py)
and future gate reports — the split fields are already computed per window; no tool forms the
rate. This kills the demonstrated misdiagnosis mode (chasing prompt fixes for transport nulls).
**Hard verifier limits:** do NOT re-run the 80 % gate retroactively — historical no_pwg audit
reports were overwritten (per-window split `not_recoverable`), the 83 % figure is
ruled-INSUFFICIENT_EVIDENCE for the current store population, the only recoverable in-cohort
datapoint reads 13/17 ≈ 76.5 % (still under the bar), and re-basing the gate denominator is
@DECIDE-gated under the "report the number that came out" ruling. Additive reporting only.

### A5. H858 Tier-1 german-field source-anchoring — scoped down (WEAKENED)

Still "the true content-fidelity lever" for the span-drop reject class, but: the
grammar-field-restore half **already shipped** (PR #510, `RECORD_MASKED = ('h','grammar')` in
[`card_fields.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/card_fields.py));
every measured instance of the class is confined to the **frozen no-PWG nominal lane** (zero
instances in verb-root windows — the entire remaining drain scope); and the cited 4.1×/6.7×
requeue economics belong to a different defect class (sTA untranslated-German). Right move:
implement german-as-deterministically-restored-skeleton (model emits only `russian`) and validate
it **inside the A1 medium50 run** — not as its own drain. Classify SHARED vs GAP in
[`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
before close.

### A6. Hygiene batch (each S-effort, verified-real residues)

- **C-49 backfill**: w02–w05 documented residuals never entered
  [`no_pwg_residuals.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_residuals.jsonl);
  the reconciliation selftest is already spec'd (H963 correction input §`test_documented_residuals_are_ledgered`) — land it.
- **Auto-appender**: teach `requeue_from_audit.py`/`audit_window.py` to append
  signature-matched second-identical-failures to `no_pwg_residuals.jsonl` — **NOT** to
  [`deferred_monsters.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/deferred_monsters.jsonl),
  which is the H304 over-ceiling COST queue by MG ruling. Do not pre-park before rq1 — 50–85 % of
  transient keys converge there; park only after the second identical failure (current manual
  practice, mechanized).
- **Fragment-TM compliance**: the sidecar is stale at 217 rows from gam+vid only (mtime 04-07)
  while un-harvested `frag_prov` exists — run the already-prescribed build-frags step at each
  promotion; the big brŪ-class saving additionally needs a build-frags harvest of the failed
  window's `wf_output` *between audit and requeue* (currently unspecified anywhere).
- **Doc contradiction**: [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
  line ~700 still says "`--no-tm` mandatory on requeue" (inside an MG-locked block) while
  [`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md)
  step 7 + `requeue_from_audit.py` implement the transient carve-out since 04-07 — a human
  should ratify the one-line amendment (MG-locked text).
- **Planning assumption**: record `tm_cards=0` as the expectation on fresh verb roots (measured
  0/31, 0/19, 0/12, 0/100) so nobody budgets fantasy TM wins.

### A7. Width-recalibration experiment — an experiment, not a raise (from ledger #4)

The ≤3-wide cap stands, but it was set entirely on degraded-transport evidence and widths 4–8
were never bracketed on a healthy transport. Sanctioned move: add a width arm to
[`calibrate_perf_harness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/calibrate_perf_harness.py)
and make the already-returned per-window telemetry drive an adaptive policy (re-widen on
measured-healthy, narrow below 3 on H317-class days). Only worth running once a lane is live
(A1) and instrumented (A2).

### A8. Probe the Message Batches API lane (from ledger #8 — a genuine blind spot)

The one Anthropic transport that is **latency-immune by design** (async, 24 h window, ~50 %
cost) was never evaluated while the paid lane sat latency-blocked for 3+ weeks. A bounded probe
(one root, H911-style acceptance gates, hard cost ceiling) is cheap to spec as a handoff; needs a
human @DECIDE on paid budget. Also: re-login c5/c6 remains the cheapest idle-capacity unlock,
gated behind transport recovery + the H911 quality freeze.

## 4. Do NOT build (refuted / measured-zero)

1. **A new window-chain driver** (`run_window_chain.py`) — exists three times over (see A3);
   a fourth implementation would duplicate shipped work and cannot fire the Workflow tool anyway.
2. **The SANLOSS counter fix as spec'd by the H1150 `fix_suggestion`** — attempted and
   **escalated with "no safe fix"** the day before this audit
   ([H1225 memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1112/H1225_SANLOSS_COUNTER_FIX_ESCALATION_2026-07-19.md),
   PR #573): boundary partition clears 5/8 false flags while blinding the guard on genuine
   multi-preverb Nachtrag cards; the offline verbatim check is tautologically untestable
   (source and candidate derive from the same store rows). Arming `SANLOSS_HARD_REJECT` is a
   parked human @DECIDE (options include accepting the measured 0.9 % noise floor — 8/865
   eligible, `true_drop` 0). Now registered as
   [DEAD_ENDS §12](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) —
   it previously lived only in the memo, invisible to registry-level planning.
3. **Retroactive re-gating of H911 on the content axis** — infeasible (reports overwritten) and
   ruling-blocked; forward split only (A4).
4. **Exact/fuzzy TM investment on fresh roots** — measured zero four times; cross-card
   byte-exact ceiling 0.36 %. The TM's value is intra-card fragment healing, not cross-root reuse.

## 5. Recommendation × verdict table

| # | Synthesized recommendation | Prior-art lens | Impact lens | Net | Surviving residue |
|---|---|---|---|---|---|
| 1 | H1209 medium50 → controller-worker fallback | WEAKENED (pre-existing minted work; fallback verdict needs medium50 + H1210) | CONFIRMED (baseline 0 on degraded days) | WEAKENED | **Run it** (A1) + prefix-reorder A/B |
| 2 | One supervised window-chain driver | REFUTED (exists ×3: /pwg-drain, BoundedSupervisor/staged-run, H1209 rig) | CONFIRMED (numbers verify) | REFUTED | 3 residues → A3 |
| 3 | First-class per-window instrumentation | WEAKENED (= repo's own H390 rule 4a; Phase 1 shipped) | CONFIRMED (S effort, foundational) | WEAKENED | **Finish it** (A2) |
| 4 | Content-clean vs transport-yield split | WEAKENED (@DECIDE-gated re-gate; history unrecoverable) | WEAKENED (pure reporting) | WEAKENED | Forward-only split (A4) |
| 5 | H858 Tier-1 german anchoring | WEAKENED (grammar half shipped PR #510) | WEAKENED (class confined to frozen lane) | WEAKENED | Scoped fix inside medium50 (A5) |
| 6 | Residual denylist + signature auto-park | WEAKENED (PR #478 shipped the core 15-07) | WEAKENED (35 % figure counts unpaid waste) | WEAKENED | C-49 backfill + auto-appender (A6) |
| 7 | Fragment TM on transient requeues | WEAKENED (carve-out shipped 04-07; rule text contradiction remains) | WEAKENED (~0.5–3 % of calendar) | WEAKENED | build-frags compliance + doc fix (A6) |
| 8 | Arm accept() with source sense count | REFUTED (H1225 escalation: no safe counter fix) | REFUTED (store incidence 0; audited ~0.4 %) | REFUTED | @DECIDE noise-floor option only |

## 6. Meta-findings

1. **Idea saturation.** Five independent miners + a synthesizer, all reading the same repo,
   produced almost nothing the repo had not already built, minted, or dead-ended — 6/8
   recommendations reduced to "finish/run/comply with existing work". The improvement frontier
   is *execution and telemetry*, not design. This is itself the strongest possible answer to
   "how to improve": run [H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1209-Opus_SanskritLexicography_pwg-ru-controller-worker-canary_17.07.26.md)'s
   medium50, finish H390 rule 4(a), close the three A3 residues.
2. **Dead-end registry gap (fixed in this PR).** The H1225 SANLOSS escalation — an expensive,
   twice-disproven fix attempt — was recorded only in its memo, absent from
   [`DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
   and [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md);
   this audit's own synthesis stage re-proposed the disproven fix at rank 8, demonstrating the
   cost of the gap live. Registered as DEAD_ENDS §12 in the same pass; the same pass also closed
   a second registry dangle — H1349 W3's vidyut-cheda NO-GO was referenced in
   [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
   as "DEAD_ENDS §11" but the entry was never landed; it now exists as the real §11.
3. **Verifier-caught errata in analyst numbers** (kept honest): `window_ledger.jsonl` carries
   12/473 wall-clock rows, not 0/473; the SANLOSS false-flag denominator is 865 eligible cards
   (0.9 %), not 2,489 (0.3 %); the 3–4× operator-loop gain is nearer 2–3× after deducting
   deliberate degraded-API caution inside the measured gaps.
4. **The blend-vs-axes lesson generalizes.** H911's single blended clean-rate drove a FAIL
   verdict whose remediation splits into two disjoint programs (transport vs content) with
   different owners; any future gate metric here should be born split (A4).

## 7. Method note

Pipeline: 5 parallel miners (wall-clock ledger · concurrency/scheduling · TM/input-reduction ·
lanes/transport · yield-economics) → synthesis capped at 8 ranked recommendations under the
standing-ruling constraint set (≤3-wide stands, lean-TR rejected, H255 frozen, headless NO-GO
external, gates non-negotiable) → per-recommendation adversarial verification (prior-art lens
with repo/DEAD_ENDS/CONTRADICTIONS search; impact lens with Amdahl arithmetic against the
ledger). Verdict rule: any REFUTED lens refutes; any WEAKENED lens weakens. The full agent
outputs live in the session workflow journal (`wf_1b45f9b1-8f3`); this document is the durable
distillation.

_Dr. Mārcis Gasūns_
