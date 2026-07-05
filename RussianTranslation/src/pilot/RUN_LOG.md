# PWG → Russian — Max run log

One block per Max run. **Record the model tier on every step** (Sonnet / Opus /
Haiku / none), not just runtime and tokens. Failures are logged, not hidden.
History of how the harness got here: [`EVOLUTION_TIMELINE.md`](EVOLUTION_TIMELINE.md).

## Stage A+B summary (2026-06-29) — all **Sonnet**, no Opus

| root | cards | Max tokens | clean | clean % | gates: nws / sense_dupes |
|---|---:|---:|---:|---:|---|
| sTA (2 rounds) | 123 (+33 rq) | 5,310,934 | 96/123 | 78% | PASS / PASS |
| BU | 59 | 2,022,803 | 45/59 | 76% | PASS / PASS |
| as | 98 | 3,353,816 | 81/98 | 83% | PASS / PASS |
| i (2 chunks) | 204 | 6,768,657 | 179/204 | 88% | PASS / PASS |
| **total** | **484** | **~17.46 M** | **401/484** | **83%** | all PASS |

- **Tier:** every translate agent = **Sonnet**; every audit gate = **no LLM**
  (free Python). **Zero Opus** spent across the whole staged run. The optional
  Opus LLM-judge of the per-root judge samples is still a separate, not-run step.
- **Throughput / quota:** ~17.5 M Max tokens for 484 sub-cards (~36 k/card);
  no weekly cap fired. Wall-clock ~65 min of translate across the roots (less
  with the concurrent `i` chunks).
- **Dominant residual is a documented false positive,** not a quality problem:
  `suspicious_attested_without_text_signal` is 60–70% of every root's risks
  because `has_text_signal()` ignores NWS owner citations — see F-gate-nws-fp.
  The NWS attribution gate itself PASSES on all four roots (the owner-map feed
  works); sense-dupe gate PASSES on all four.
- **Real, fixable residual** (Sonnet ceiling): `untranslated_braced_german_gloss`
  on citation-dense cards — the legitimate candidates for an Opus retranslate.

---

## 2026-06-29 — Stage C preflight: stale generated inputs pruned

No LLM / no Max spend. Ran the required handoff preflight:

```powershell
python src\pilot\root_window_status.py gam --prune-stale
python src\pilot\root_window_status.py yuj --prune-stale
python src\pilot\root_window_status.py vid --prune-stale
python src\pilot\root_window_status.py han --prune-stale
```

Results:

| root | stale generated files pruned | status after recheck | sub-cards | next command |
|---|---:|---|---:|---|
| `gam` | 206 | PASS, 127/127 raw + 127/127 portrait, 0 stale | 127 | `python src\pilot\gen_opt_harness.py gam` |
| `yuj` | 90 | PASS, 60/60 raw + 60/60 portrait, 0 stale | 60 | `python src\pilot\gen_opt_harness.py yuj` |
| `vid` | 70 | PASS, 55/55 raw + 55/55 portrait, 0 stale | 55 | `python src\pilot\gen_opt_harness.py vid` |
| `han` | 128 | PASS, 78/78 raw + 78/78 portrait, 0 stale | 78 | `python src\pilot\gen_opt_harness.py han` |

Decision: the Stage C stale-input hold is cleared structurally. Continue
one root at a time, starting with `gam`; generate the optimized harness, run
Max Workflow, save `wf_output.json`, and audit with `audit_window.py --root gam
--write-requeue`.

Open follow-ups remain non-blocking for Stage C: fix F-gate-nws-fp in
`has_text_signal()`, and optionally escalate the handful of real
`untranslated_braced_german_gloss` cards to Opus.

---

## 2026-06-29 — Stage B: BU

### Round 1 — full window (59 cards)

| step | tool / model | result |
|---|---|---|
| pre-check | `root_window_status.py BU` — **no LLM** | ready, 59/59 raw+portrait (PASS) |
| harness gen | `gen_opt_harness.py BU` — **no LLM** | 59 cards, mode body |
| translate | Workflow `run_pilot_wf.opt.js`, **59 × Sonnet** agents, 1 retry, tools:[] | 59/59 translated; no Opus spent |
| audit | `audit_window.py` — **no LLM** | **FAIL → needs_requeue** |

- Max wall-clock: **~11.4 min** (681,259 ms) · Max total tokens: **2,022,803** · cap fired: **no**
- Coverage: **57/59** (2 flagged: `h2_00_pwg00`, `zz_pwkvn`) · clean **45/59** · requeue **14** · judge sample **19**
- Gate exits: coverage=1 (2), prompt_semantic=1 (11), nws=**0 PASS**, sense_dupes=**0 PASS**, translation=1 (1)
- Risk mix (151 risks / 33 keys / 23 high-confidence): **same pattern as sTA** —

| rule | count | nature |
|---|---:|---|
| `suspicious_attested_without_text_signal` | 91 (60%) | **F-gate-nws-fp** (same documented false positive) |
| `collapsed_synonym_string` | 18 | quality flag (soft) |
| `untranslated_braced_german_gloss` | 12 | real defect |
| `untranslated_german_residue` | 9 | mixed |
| `likely_circular_gloss` / `suspicious_lexicographic_with_text_signal` / other | ~21 | mixed, low volume |

**Decision: ACCEPT BU** at 45/59 clean — residual dominated by the documented
F-gate-nws-fp, same as sTA, so the operator's accept-and-advance strategy applies.
No Sonnet re-loop (would chase the 91 FPs). NWS gate PASSED (owner-map feed works).
Proceeded to root `as`. No Opus spent.

---

## 2026-06-29 — Stage B: i (split into 2 sub-windows)

`i` (204 sub-cards) hit **F-harness-size-limit**: the full harness is 567 KB,
over the Workflow 512 KB `scriptPath` cap. Split into two 102-card sub-windows via
`gen_opt_harness.py i body --keys=...` (316 KB + 274 KB), run **concurrently** as
two **Sonnet** Workflows, to be reassembled into one root-scoped `wf_output.json`
for a single `i` audit.

| chunk | model | cards | tokens | wall-clock | task |
|---|---|---:|---:|---:|---|
| 1 | Sonnet | 102 | 3,371,012 | ~11.4 min | `w2mv6pwyl` |
| 2 | Sonnet | 102 | 3,397,645 | ~10.7 min | `wc37hznuc` |
| **total** | Sonnet | **204** | **6,768,657** | ~11.4 min (concurrent) | — |

Both chunk outputs reassembled into one root-scoped 204-card `wf_output.json`
(union of `results` **and** `meta.input_hashes` — the first merge attempt failed
the stale-check because only chunk-1 hashes were carried; fixed by merging both
hash maps), then a single `audit_window.py --root i`:

- **clean 179/204** (88% — best ratio of the run) · requeue 25 · judge sample 43
- Gates: coverage=1 (7), prompt_semantic=1 (16), translation=1 (3), nws=**0 PASS**, sense_dupes=**0 PASS**
- Risk mix: `suspicious_attested_without_text_signal`=263 (**F-gate-nws-fp**, ~70%),
  `collapsed_synonym_string`=40, `possible_sense_compression`=38,
  `untranslated_braced_german_gloss`=22, others ~26.
- **Decision: ACCEPT** at 179/204 (same documented-FP pattern). No Opus spent.

---

## 2026-06-29 — Stage B: as

| step | tool / model | result |
|---|---|---|
| pre-check + gen | `root_window_status.py as` / `gen_opt_harness.py as` — **no LLM** | ready, 98/98; harness 98 cards |
| translate | Workflow, **98 × Sonnet** agents, 1 retry, tools:[] | 98/98 translated; no Opus spent |
| audit | `audit_window.py` — **no LLM** | needs_requeue |

- Max wall-clock: **~10.8 min** (648,635 ms) · tokens: **3,353,816** · cap fired: **no**
- **clean 81/98** · requeue 17 · judge sample 26
- Gates: prompt_semantic=1 (10), coverage=1 (7), translation=1 (1), nws=**0 PASS**, sense_dupes=**0 PASS**
- Risk mix: `suspicious_attested_without_text_signal`=92 (**F-gate-nws-fp** again),
  `untranslated_braced_german_gloss`=21, `possible_sense_compression`=17,
  `collapsed_synonym_string`=16, others ~13.
- **Decision: ACCEPT** at 81/98 (same documented-FP pattern); advanced to `i`. No Opus spent.

---

## 2026-06-29 — Stage A: sTA

Operator: Claude Code Max. Handoff: [`../../H027-Sonnet_RussianTranslation_claude_code_max_29.06.26.md`](../../H027-Sonnet_RussianTranslation_claude_code_max_29.06.26.md).

### Round 1 — full window (123 cards)

| step | tool / model | result |
|---|---|---|
| pre-check | `root_window_status.py sTA` — **no LLM** | `stale_artifact`, 123/123 raw+portrait present, structurally ready (PASS) |
| translate | Workflow `run_pilot_wf.opt.js`, **123 × Sonnet** agents, 1 retry, tools:[] | 123/123 translated; no Opus spent |
| audit | `audit_window.py` — **no LLM** (deterministic gates) | **FAIL → needs_requeue** |

- Max wall-clock: **~22 min** (1,295,437 ms)
- Max total tokens: **4,170,022** · weekly cap fired: **no**
- Coverage: **119/123** (4 flagged: `ud`, `pratyupa`, `pari`, `vi`)
- Clean keys: **90** · Requeue: **33** · Judge sample: **42** (seed `c04c04593372f356`)
- Semantic risks: **571** across 51 keys; **61 high-confidence** (29 keys)
- Gate exits: coverage=1 (4), prompt_semantic=1 (29), nws=0, translation=1 (3), sense_dupes=0
- Dominant high-confidence risks: `untranslated_german_residue` /
  `untranslated_braced_german_gloss` (real defects — German left untranslated:
  `anu`, `sam`, `pwg11b03`); plus lower-confidence
  `suspicious_attested_without_text_signal` cluster on NWS cards `pw00–07`.

### Round 2 — requeue (33 cards)

| step | tool / model | result |
|---|---|---|
| requeue gen | `requeue_from_audit.py sTA` — **no LLM** | harness rescoped to 33 keys (CARDS=33, META.generated_at 2026-06-29) |
| translate | Workflow `run_pilot_wf.opt.js`, **33 × Sonnet** agents, 1 retry, tools:[] | 33/33 translated; no Opus spent |
| audit | `audit_window.py` — **no LLM** | **FAIL → needs_requeue** |

- Max wall-clock: **~9.8 min** (590,562 ms) · Max total tokens: **1,140,912** · cap fired: **no**
- Convergence: requeue **33 → 27** (only **6 cleared**); cumulative clean ≈ **96/123**
- Round-2 risk mix: 220 risks / 27 keys / 56 high-confidence

| rule | count | nature |
|---|---:|---|
| `suspicious_attested_without_text_signal` | 146 (66%) | **gate false positive on the NWS layer** (see finding below) |
| `untranslated_braced_german_gloss` | 17 | **real defect** — German left in braces: `{bleibe}`, `{eröffnen}`, `{sich halten an, streben nach}` |
| `untranslated_german_residue` | 37 | mixed — several fire on legitimately-kept `{#Sanskrit#}` quote spans |
| collapsed_synonym_string / likely_circular_gloss / other | ~20 | mixed, low volume |

### 🔴 Finding F-gate-nws-fp (2026-06-29) — the requeue loop chases a gate false positive

`suspicious_attested_without_text_signal` is the dominant flag (66% of round-2
risks; **80 on `pw01` alone**) and it **cannot be cleared by re-translation**.
Verified in source: [`prompt_rule_audit.py:321`](prompt_rule_audit.py) —
`has_text_signal()` returns true only for `TEXT_CITATION` (literary sigla: `<ls`,
ṚV, MBH, Manu, …) **or** a non-empty `stratum`. NWS **owner** citations
(`MW : 47`, `Graßmann 1873 (1996) : 70`, `Geldner 1907`) are NOT in `TEXT_CITATION`,
so any NWS sense the model (correctly) marks `source_type=attested` with only an
owner citation and no stratum fires this flag by construction. `pw01` scored
810→**1430** between runs — *worse* — purely from emit-noise, not regression.

**Consequence:** another identical Sonnet requeue pass would spend ~1M tokens to
clear, at best, a few real `untranslated_braced_german_gloss` cards while leaving
all 146 false positives untouched. The loop has hit diminishing returns.

**Real residual defects (fixable):** `untranslated_braced_german_gloss` on
citation-dense cards (`anu`, `sam`, `55_pra`, `zz_sch`, `15_ava`, `43_samud`).
These are a genuine **Sonnet ceiling** → candidates for the harness's
designed-but-unused **Opus** retranslate tier, or a targeted prompt fix — NOT a
repeat Sonnet pass.

**Decision surfaced to operator (do not auto-loop):**
1. Teach the gate to count NWS owner citations as a text signal (kills 146 FPs), **or**
2. Escalate only the ~6 real braced-gloss failers to an **Opus** retranslate, **or**
3. Accept current state (96/123 clean + documented FP) and proceed to Stage B `BU`.

No Opus has been spent on sTA in either round; the Opus LLM-judge of the judge
sample is still a separate, not-yet-run step.

### Decision (operator, 2026-06-29): ACCEPT sTA → proceed to Stage B `BU`

sTA accepted at **96/123 clean** with the residual dominated by the documented
F-gate-nws-fp false positive. This satisfies the handoff's "fresh sTA is
mechanically clean **or has a targeted rerun plan**" gate for advancing to Stage B.
Open follow-ups left for later (not blocking BU): fix `has_text_signal()` to count
NWS owner citations; optional Opus retranslate of the ~6 real braced-gloss failers.

---

## 2026-07-05 — nominal window `pril10_w1` — ⛔ ABORTED (cost/latency blow-up) — **Sonnet 5** gen

First nominal production attempt: top-8 largest PWG heads (`kAla, rasa, rUpa,
brahman, arTa, sva, manas, antara`). Harness was 1.03 MB (> 512 KB cap), split into
3 sub-windows (wA/wB/wC) and run concurrently. **Killed by MG after ~20 min** — only
~3 of 8 cards done, agents burning 3–6.5 min and up to ~900 K tokens each.

| metric | value |
|---|---:|
| tokens (all 3, exact) | **42,316,604** |
| cost (Sonnet 4.x rates — order-of-magnitude) | **~$79.83** |
| cache-write share of $ | **60% ($47.77)** — framework re-cached per agent |
| wall-clock | 20.1 min (concurrent) |
| agents spawned | **230** (vs 174 est., +32%) over 581 turns |
| cards completed | ~3 of 8 |
| per intended card | ~5.29 M tok / ~$9.98 |
| max single agent | 390 s (6.5 min) / 903 K tok |
| agents > 60 s / > 120 s / > 180 s | 19 / 10 / 8 |

**Root cause (short):** in nominal+presplit mode every *fragment* is its own
`agent()` call (8 cards → 230 agents, ~29/card), each re-establishing the ~30 K
framework cache — so the opt2 batching amortization is defeated and **cache-write
dominates the bill**. Compare Stage A+B verb runs: **~36 K tok/card** (batched);
this nominal run: **~5.29 M tok/card** — ~145× worse. Extrapolation: 10 K entries
≈ $100 K, 50 K ≈ $500 K → not viable at scale. Kill gate (`KILL_CEIL_MS=480000`,
8 min) far too loose vs the MG rule that a subcard > ~60 s is suspicious.

Full post-mortem + fix mandate: [`Uprava/H189`](https://github.com/gasyoun/Uprava/blob/main/handoffs/H189-Opus_RussianTranslation_pwg_ru_nominal_cost_blowup_postmortem_05.07.26.md).
No Max windows to run until H189 §5 guardrails land. Post-mortem by **Opus 4.8
(`claude-opus-4-8`)**.

### 2026-07-05 — H189 fixes LANDED (Opus 4.8, `claude-opus-4-8`)

Every §4 hypothesis **CONFIRMED** (economics reproduced to the digit via
[`parse_workflow_cost.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/parse_workflow_cost.py))
— full verified breakdown in
[`POSTMORTEM_pril10_w1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/POSTMORTEM_pril10_w1.md).
Five guardrails shipped (all SHARED, 68/68 selftests green):

1. **Presplit-lane re-batching** (`PRESPLIT_GROUP_CITE_BUDGET=60`/`SENSE_CAP=18`):
   `pril10_w1` **174 → 69** fragment-group calls; real `gam` giants **18 → 6** agents.
2. **Kill-gate recalibration**: floor 120 s → **45 s**, ceil 480 s → **180 s** (MG rule).
3. **Live budget kill-switch**: window self-aborts + requeues past
   `MAX_AGENTS = ⌈expected×3⌉ + 10 (size-proportional)`.
4. **Harness-size guard**: generator warns + prints an exact key-disjoint split > 480 KB.
5. **Preflight cost gate**: `perf_preflight.py` estimates tokens/$/per-card and flags
   (or `--refuse-over-cost` refuses) a window over ceiling — flags `pril10_w1` (~$4/card
   **even post-fix**) → monster-card windows route to a human-budgeted lane, not bulk.

Also fixed a latent nominal-generation crash (`_slp1_lex_for_key` on an empty `[]`
portrait). **Standing rule remains: do not launch a window of `kAla`-class monsters as
bulk** — the amortization fix cuts the presplit lane ~2.5× but such heads are intrinsically
expensive; the cost gate is the guardrail that keeps them out of the pipeline.

### 2026-07-05 — H191 deterministic verification + 100-small nominal staging (Codex/GPT-5)

Executed H191 as a deterministic Codex pass only; no Max/Workflow translation run was started.

**Verification:** `window_selftest.py` PASS; `lang_parity_check.py` clean (20 entries);
`translation_memory.py selftest` PASS; `py_compile` PASS for the touched modules; generated
`run_pilot_wf.nominal_w1_100small.js` passes `node --check`. The H189 economics reproduce to
the digit from the three aborted `pril10_w1` transcript directories:

| metric | value |
|---|---:|
| input tokens | 5,306,817 |
| cache-write tokens | 12,738,510 |
| cache-read tokens | 23,668,772 |
| output tokens | 602,505 |
| total tokens | **42,316,604** |
| estimated cost | **~$79.83** |

**H191 fixes:** B1 prunes harness `INPUTS`/`PH` to agent-reachable keys only (TM-resolved and
degenerate cards stay self-contained in `TM_RESOLVED` / `DEGENERATE_RESOLVED`); B2 splits a
single citation-dense physical line into budgeted complete-`<ls>` chunks; B3 adds
`cost_partition` JSON (`run_now`, `defer_monster`, grouped totals, recommendation) to
`perf_preflight.py`. Pinning selftests are in `window_selftest.py`; parity ledger hashes were
refreshed for the shared/lang-agnostic changes.

**100-small nominal window staged:** selected the 100 cheapest runnable Приложение 5 nominal
heads after generating missing local inputs. Preflight has **0 `defer_monster`**, 5 degenerate
pass-through cards, 95 live inputs, 3 batches / 3 expected agents, harness **274,848 bytes**,
and estimated **745,200 tokens / ~$1.41**. Tracked staging artifacts:
`NOMINAL_W1_100SMALL.keys.txt`, `NOMINAL_W1_100SMALL.selection.json`,
`NOMINAL_W1_100SMALL.preflight.json`, and `NOMINAL_W1_100SMALL.md`.

**Next:** Sonnet/Max executes
`C:\Users\user\Documents\GitHub\Uprava\handoffs\H201-Sonnet_RussianTranslation_pwg_ru_nominal_w1_100small_run_05.07.26.md`.
