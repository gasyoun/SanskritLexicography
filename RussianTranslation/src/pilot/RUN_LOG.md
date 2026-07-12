# PWG → Russian — Max run log

One block per Max run. **Record the model tier on every step** (Sonnet / Opus /
Haiku / none), not just runtime and tokens. Failures are logged, not hidden.
History of how the harness got here: [`EVOLUTION_TIMELINE.md`](EVOLUTION_TIMELINE.md).

## 2026-07-06 — `dah` tail (H178 A-2) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Fable 5** (`claude-fable-5`) — ✅ 31/31 PROMOTED (1 documented 🟡 residual)

Finished the two 04-07 held `dah` cards via three Workflow runs (TM-denylisted):

| run | target | result | agents | subagent tokens | wall-clock |
|---|---|---|---|---|---|
| defect requeue | `dah~~h0_zz_nws00` (whole card, single-key requeue file) | ✅ 1/1 ok | 1 | 75,693 | ~68s |
| topup attempt 1 | `dah~~h0_zz_pw` — 17 missing fragments | 12/17 ok, 5 retry-cap nulls | 17 | 1,144,751 | ~67s |
| topup attempt 2 | same 17 | 15/17 ok, 2 retry-cap nulls | 17 | 1,147,780 | ~78s |

Union of both topup attempts = **16/17 fragments**; only `dah~~h0_zz_pw__s10p0` hard-failed the
StructuredOutput retry cap (5×) on BOTH fresh attempts → per the H178 2-attempt cap + the `vid`
precedent, the card is promoted as a **documented 🟡 residual** (residual class: single
PW-addenda sense fragment, StructuredOutput retry-cap schema-emission failure — NOT the H220
kill-gate class). Promotions via `promote_final_cards.py --merge --gen-model-version
claude-sonnet-5`: store **11,185 → 11,261 rows**; `dah` = **31/31 cards**. TM rebuilt (card
2,302 / frag 217 / publication 2,392, all validate green); provenance audit clean (11,261/11,261
model_version + pipeline stamps). Full memo:
[`pwg_ru/H178_REAUDIT_2026-07-06.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_REAUDIT_2026-07-06.md).

## 2026-07-06 — `no_pwg_w1` (H214 no-PWG lane, FIRST run) — gen **Sonnet 5** / orchestration **Opus 4.8** — ⚠️ VALIDATED-NOT-PROMOTED

First-ever translation run of the [H214](https://github.com/gasyoun/Uprava/blob/main/handoffs/H214-Opus_RussianTranslation_pwg_ru_no_pwg_supplement_cards_06.07.26.md)
**no-PWG supplement-chain lane** — 24 PWG-missing headwords (of the 232-lemma backfill queue) →
**58 supplement sub-cards** (`<key>~~h0_zz_<layer>`, pw/sch/pwkvn/nws). Branch
`pwg-ru/no-pwg-lane-drain-w1`. Preflight cost-gate: verdict `ok`, run-now-low, ~497 K tok / ~$0.94.

**Outcome: the render/plumbing path is VALIDATED end-to-end, but the output is NOT promotable yet.**

- **Plumbing works:** gen → nominal harness (keymap `subcard→key1`) → Workflow → wf_output →
  `source_profile`/`layer` all correct per row. Individual cards translate correctly when they
  land (e.g. `duṣkṛta~~h0_zz_pw` = a clean, complete RU card).
- **Throughput is poor (~36%):** 3 Workflow passes (batched → 9-batch → 46 single-card,
  `--no-tm`), ~3.4 M subagent tokens total → **only 21 / 58 distinct sub-cards ok** (11 headwords).
  Passes 1–2 tripped the budget kill-switch (multi-card StructuredOutput failures binary-split into
  an agent-budget cascade); single-card mode (pass 3, `--output-budget=1`) removed the cascade but
  still only ~15–20 %/pass, **stochastic** (a card null in passes 1–2 succeeds in pass 3) — abnormally
  low vs the ~90 % a clean rerun gives elsewhere. Suspected: strict subcard-key echo interacting with
  the masked nominal prompt + Workflow-runtime agent limits.
- **Quality is mixed:** of the 21 "ok", only ~7 are clean full RU translations; the rest are broken
  (`{{Lbody=205646}}` body-id leak into `russian`, e.g. `_c_ay_a~~h0_zz_pw`), degenerate cross-ref
  stubs (no gloss to translate), or carry untranslated `{%…%}` spans.
- **No nominal audit gate:** `audit_window.py` needs `--allow-stale` for a keys-based nominal window
  (no rootmap) and in that mode the glue gates crash (H201 caveat) — so these no-PWG cards can't be
  mechanically vetted before promotion.

**Initial decision: NOT promoted** (pushing `{{Lbody}}`-leak / untranslated rows would pollute the store).

### ✅ RESOLUTION (same day, 2026-07-06, Opus 4.8) — both blockers fixed, 5 verified-clean promoted

- **Blocker 1 root-caused + fixed:** `{{Lbody=NNNN}}` is not a masking bug — it is a Cologne
  **alternate-headword pointer** (record `205646.1` `CAyA` reuses the body of primary entry `205646`
  `CAya`; ~12,186 PW records / 7 % are these). Added `dict_merge.resolve_lbody()` + `id_index()`
  (L-id → body) and applied it in `merged()`, so every consumer now gets the referenced entry's real
  gloss instead of a bare pointer (e.g. `CAyA` pw → `…bedeutet nach J. BURGESS auch {%Abschrift,
  Copie%}`). Lang-agnostic (SHARED); pinned by `dict_merge.py resolve_lbody selftest`.
- **Blocker 2 fixed:** `audit_window.py` now **skips the root-glue step for a nominal / no-rootmap
  window** (`meta.nominal` or no rootmap on disk) instead of crashing, so the content gates
  (translation / coverage / sense-dupes / nws / prompt-semantic) run to completion and give a real
  clean/requeue verdict.
- **Promoted 5 verified-clean** (audit clean, 0 flags): `Bagavat~~h0_zz_nws00`, `SAKA~~h0_zz_nws00`,
  `SAKA~~h0_zz_pw`, `devI~~h0_zz_pw`, `duzkfta~~h0_zz_pw` → store **11,163 → 11,185** (+22 sense rows,
  `ai_translated`, held for G5). Every row carries `layer` + `provenance.source_profile =
  no_pwg_supplement_chain`. TM rebuilt (2,301 cards). The audit correctly **rejected 2 of the 7**
  leak/quality-clean candidates (`devI~~h0_zz_nws00`, `mAyA~~h0_zz_nws00` — NWS F12 owner
  misattribution + coverage-over), which is why only 5, not 7, were promoted.

**Still open before scaling to the full 232:** the low single-card yield (~36 % this window; stochastic
StructuredOutput failures on masked nominal supplement cards) is a **throughput** issue, not a
correctness one — the Lbody fix removes one failure class but the strict-key-echo / Workflow-runtime
interaction remains to be root-caused. Re-run w1's still-null keys (now Lbody-resolved) before adding
new lemmas. wf_outputs kept at `src/pilot/output/wf_output.no_pwg_w1*.json` (gitignored).

### ✅ H220 THROUGHPUT ROOT-CAUSE + FIX (2026-07-06, Opus 4.8 `claude-opus-4-8`) — 40 % → 100 % on a 10-card diagnostic

The ~36 % yield was root-caused from a fresh 10-card single-card diagnostic window (6 mangled-stem +
4 clean-stem controls, spanning pw/sch/nws) run through the Workflow tool, reading the run's own
`journal.jsonl` + kill-log lines. **Two compounding failure modes, both now fixed** in
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py):

- **DOMINANT — the wall-clock kill gate abandons valid-but-slow single supplement cards.** The kill
  budget (`KILL_BASE 20 s + KILL_SLOPE 45 ms/byte, ×2`, floor 45 s) was calibrated on dense
  multi-fragment `tyaj` **root batches**; a tiny single nominal card's wall-clock is dominated by fixed
  per-call StructuredOutput latency (~55–105 s), which exceeds its byte-derived budget (53–104 s here).
  The first diagnostic run killed **6/6 nulls** (kill-timeout logs `53 s`…`104 s`), and because no-PWG
  supplement sub-cards are **single-fragment (no selfheal split)**, a kill has no smaller lane to route
  to → permanent null. 4 of those 6 killed cards echoed the correct key and were proven (Python
  re-simulation of `accept()`) to pass the fidelity guard — pure kill-gate loss. **Fix A:** a single
  card with no selfheal fallback (`FRAGS[k]` empty) now gets the **CEIL budget (180 s)** via
  `killBudgetForCur(cur)`; the aggressive byte-scaled gate is kept for multi-card / splittable batches
  where a kill actually routes to binary-split / fragment heal.
- **SECONDARY — key-echo mismatch on mangled stems.** The `=== CARD <stem> ===` header carries the
  mangled sub-card stem (`_c_ay_a~~h0_zz_pw`), but the portrait JSON right below carries the clean SLP1
  `key1` (`CAyA`), pulling the model into echoing the SLP1 in its output `key1` → the harness's strict
  `km[k]` match drops it as `missing-or-mismatched-key`. Deterministic for leading/interior-underscore
  stems (`_c_ay_a→CAyA`, `g_ayatr_i→gAyatrI`, `t_a→tA`). **Fix B:** nominal windows recover such a card
  by re-keying it via `nominal_keymap` **only when the SLP1 maps to exactly one pending stem** in the
  batch (unambiguous); gated on `META.nominal` so PWG root windows keep strict matching
  (`test_generated_harness_strict_key_matching` still green).
- **Plus observability:** `selfHeal`'s generic `no-selfheal-fallback` reason was **overwriting** the real
  upstream cause (kill-timeout / mismatched-key) — the misleading message hid the kill-gate mass-kill for
  a whole session. It now preserves a pre-existing `FAIL[k]` reason.

**Verified:** the SAME 10-card window re-run with the fixed harness → **cards 10 / ok 10 / null 0
(100 %)**, `agents_spent 9` (no retries; was 12), **0 kill-timeouts** (was 6), kill-switch not tripped.
The journal shows the model still echoed `gAyatrI`/`tA` (SLP1) for 2 cards — both landed anyway because
Fix B re-keyed them, so both fixes are independently necessary. Pinned by 3 new `window_selftest.py`
tests (`test_no_fallback_single_gets_ceil_kill_budget`, `test_nominal_key_echo_tolerance_scoped`,
`test_selfheal_no_fallback_preserves_upstream_reason`); full suite green (83 PASS);
`lang_parity_check.py` clean (new SHARED entry `no_fallback_single_kill_budget_and_nominal_key_echo`).
**The 232-lemma no-PWG lane is UNBLOCKED for scaling.** wf_outputs kept at
`src/pilot/output/wf_output.no_pwg_w1*.json` + the diagnostic `wf_output.no_pwg_diag*` (gitignored).

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

---

## 2026-07-06 — nominal window `nominal_w1_100small` — ✅ RUN & PROMOTED (100/100) — gen **Sonnet 5** (`claude-sonnet-5`), orchestration **Opus 4.8** (`claude-opus-4-8`)

H201 executed on an Opus 4.8 Max/Workflow surface. Generation model resolved to **Sonnet 5
(`claude-sonnet-5`)** (harness pins `model:'sonnet'`; confirmed from the workflow subagent
`.jsonl` transcripts). Ran in **three Workflow passes** because the first pass hit a transient
network outage:

| pass | harness | result | agents | subagent tokens | wall-clock |
|---|---|---|---|---|---|
| 1 (full) | `run_pilot_wf.nominal_w1_100small.js` | ⛔ **5 ok / 95 null**, `budget_kill_switch_tripped` | 19/19 | 957,970 | ~10m30s |
| 2 (rerun) | `run_pilot_wf.opt2.js` (all 100 requeued) | ✅ **93 ok / 7 null** | 16/19 | 1,402,160 | ~11m49s |
| 3 (requeue) | `run_pilot_wf.nominal_w1_100small.requeue7.js` (7 transient) | ✅ **7 ok / 0 null** | 2/13 | 138,666 | ~42s |
| **total** | — | **100/100 promoted** | 37 | **2,498,796** | ~23m |

**Pass-1 root cause = transient infra, not content/batch-size:** all three batches (incl. the
**4-card** batch-0) failed with `API Error: Connection closed mid-response`; self-heal splits
also dropped, exhausting the 19-agent budget. Because even the 4-card batch failed, this was a
network outage during the run window, not a structural problem — a clean rerun recovered
(93/100), and the 7 residual nulls were a single contiguous masked sub-block of batch-1
(`mAza…nIla`), re-run to 7/7 in 42s.

**⚠ Audit caveat confirmed (nominal + `--allow-stale`):** a nominal keys-based window has
**no rootmap** (`rootmap_sha256:null`), so `audit_window.py` refuses (`no rootmap`) and needs
`--allow-stale`. In that forensic mode the `glue`/`glue-missing-nested` gates **crash** and the
`missing_required_sense_field` gate **misfires**, reporting a bogus **86 "defect"** on pass-2.
Manual inspection of `vedikA`, `prota`, `Apta`, `ucita` confirmed all are complete, well-formed
cards (the flagged ones are legitimately thin *see-under* cross-reference stubs). The runbook's
own warning holds: **allow-stale requeue counts are untrustworthy for nominal windows** — trust
the Workflow `summary.null_keys`, not the stale-audit `defect` count. `requeue_from_audit.py
--transient --nominal` handles the real nulls correctly.

**Promotion:** `promote_final_cards.py --glob wf_output.nominal_w1_100small.json --merge
--gen-model-version claude-sonnet-5` → **100 non-null cards / 306 sense rows**, store
`src/pwg_ru_translated.jsonl` now **11,163 rows** (`review_status=ai_translated`, NOT approved —
held out of the citable edition until G5 human review). TM rebuilt: `translation_memory.ru.json`
= **2,297 content-addressed cards**. No `frag_prov` rows → no `build-frags` needed. Requeue
residuals: **none**.

**Cost note:** the transient pass-1 loss doubled the intended spend (staged estimate ~745K tok /
$1.41 for one clean pass; actual ~2.5M tok across three passes). The `~745,200 tok / $1.41`
preflight gate refers to a *single clean* pass and held for pass 2.

**Next:** window is fully AI-translated and promoted; the 100 cards await **G5 human review** to
flip `ai_translated → approved`. No further agent run needed for this window.

---

## 2026-07-05 — nominal window `nominal_w1_100small` — ✅ STAGED & VERIFIED-READY (no Max/Workflow run) — prep by **Opus 4.8** (`claude-opus-4-8`)

H201 executed on a **Claude Code (Opus 4.8) session, which is NOT a Max Workflow surface** —
so the `agent()`-driven translation was **not** run here. Everything deterministic up to the
Workflow hand-off was done and verified on a clean worktree off `origin/codex/h191-pwg-ru-verify-optimize-100small`:

| check | result |
|---|---|
| base | `origin/codex/h191-…` (has H179 adapter #152 + **H189 cost guardrails** #158/#159 + staging) |
| preflight | 3 batches / **3 expected agents** / **745,200 tok / $1.41** / verdict `ok`, under per-card ($2) + window ($25) ceilings |
| harness | `run_pilot_wf.nominal_w1_100small.js` = **315,896 bytes** (< 480 KB cap), 100 cards / 3 batches [4, 69, 26], mode NOMINAL, `degenerate_passthrough=1` |
| `node --check` | **passed** |
| standalone `node` run | fails by design (no local `agent()`; top-level `return`) — confirms it needs the Workflow runtime |

**⚠ Gotcha (bash executors):** `NOMINAL_W1_100SMALL.keys.txt` is **CRLF**. The handoff's
PowerShell `(Get-Content …) -join ','` strips `
` correctly, but a bash `paste -sd,` keeps it —
every key becomes `n_ar_i
`, and `gen_opt_harness2.py` dies with `missing input for <key>`.
Strip it first: `tr -d '\r' < NOMINAL_W1_100SMALL.keys.txt | paste -sd,`. (Preflight is more
lenient and passed either way; only generation failed.)

**Note:** the fresh worktree lacks the gitignored `src/pilot/input/` (218K generated files); junction/copy it from an existing checkout before preflight/gen.

**Next:** run the generated harness on a **Sonnet Max Workflow** surface, save `wf_output.nominal_w1_100small.json`, then audit → promote per [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md). No run metrics (wall-clock / tokens / promoted count) exist yet — they get logged by the session that actually runs it.

---

## 2026-07-10 — no-PWG lane window `no_pwg_w02` (H255 scale drain, w1 still-null tail) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Sonnet 5** (`claude-sonnet-5`) — 🟡 16/47 PROMOTED, PAUSED on degraded generation API

Picked up [H255](https://github.com/gasyoun/Uprava/blob/main/handoffs/H255-Sonnet_RussianTranslation_pwg_ru_no_pwg_lane_scale_06.07.26.md) where the Codex prep session left it: `no_pwg_w02` = the 20-headword w1 still-null tail (`Atmavat`, `Bagavat`, `CAyA`, `GaRwA`, `SAKA`, `SamBu`, `Sreyas`, `dayita`, `duzkfta`, `gAyatrI`, `gagana`, `jananI`, `kumArI`, `mAtrA`, `mahat`, `medinI`, `ozaDI`, `saMDyA`, `sat`, `smita`) → 47 single-fragment supplement sub-cards. Regenerated inputs (`_pilot_gen_merged.py`), harness (`gen_opt_harness2.py --nominal --output-budget=1`, 38 batches), preflight GO ($0.47/card, under ceiling).

**Result: 27/47 transient (kill-timeout, mostly at the 180s `KILL_CEIL` on tiny 150–2200-byte skeletons), 4/47 defect (real content failures — `_s_a_k_a~~h0_zz_sch`, `g_ayatr_i~~h0_zz_pw/pwkvn/sch`), 16/47 clean.** Promoted only the 16 clean sub-cards (`Bagavat`/`CAyA`/`GaRwA`/`SAKA`/`SamBu`/`Sreyas`/`dayita`/`duzkfta`/`sat`); `gAyatrI` lost all 4 of its sub-cards to transient+defect and stays null. Store `src/pwg_ru_translated.jsonl`: 11,275 → **11,317 rows**. TM rebuilt (`translation_memory.ru.json`, 2,316 cards).

**⚠ Gotcha caught mid-promotion:** `promote_final_cards.py`'s default `--glob wf_output*.json` (relative to the RussianTranslation repo root, not `src/pilot/output/`) picked up **5 unrelated stray `wf_output*.json` files already sitting in the repo root** from earlier sessions and promoted 130 sub-cards across 88 other roots as a side effect — harmless (`--merge` only replaces matching sub-cards) but surprising. Always pass an explicit `--glob` pointing at your own window's output file. Also: `promote_final_cards.py` does **not** consult the audit gate's defect/transient split — it promotes every non-null card. First pass promoted all 20 non-null cards including the 4 defects; caught by diffing `audit_window.report.json`'s `requeue_defect` list, reverted from the `.premerge.*.bak`, filtered the wf_output to exclude the 4 defect keys, and re-promoted 16.

**Root cause: the SAME generation-API degradation already tracked in [`SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md) for the H442 medium50 heal lane** (`Connection closed mid-response`, 180s `KILL_CEIL` timeouts on tiny skeletons that cannot legitimately need that long) — but here it hit even the **cheap, single-fragment, no-heal-lane** no-PWG cards, at a 57% transient rate. This broadens the known impact beyond the medium50/heal-lane theory: it looks like host-level degradation, not heal-lane starvation specifically. Logged to `GENERATION_API_PROBE_LOG.md` via `probe_log.py append --kind launch`.

**PAUSED per the H442 guardrail ("don't relaunch blind into a degraded env"):** did not requeue the 27 transient nulls this session. `no_pwg_runnable` count: was 172 pre-window; net -16 clean this window (still-null tail keys not yet all drained). **Next:** before the next no-PWG window, run a load-representative warm-up probe (`probe_log.py gate`, ≥5 KB skeleton, require 0 conn-errors + sub-30s) — if still degraded, wait for [H462](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md)'s telemetry work or host recovery before scaling further; only then requeue `no_pwg_w02`'s 27 transient keys (`--no-tm`) and continue the 232-lemma queue with `no_pwg_scale_plan.py --window-size 20 --limit-windows 1 --start-index 3`.

---

## 2026-07-11 — no-PWG lane window `no_pwg_w03` (H255 scale drain, requeue of `no_pwg_w02`'s 27 transient keys) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Sonnet 5** (`claude-sonnet-5`) — 🟡 11/27 PROMOTED, residual documented

**Pre-flight per the H442/H462 guardrail:** ran a fresh load-representative warm-up probe (own 6,431-byte translated-lines prompt, matching `probe_log.py prompt`'s ≥5,120 B floor) via the Workflow tool — **21.18 s, 0 conn-errors → GO** (`probe_log.py gate` exit 0). This is a real recovery signal: the most recent prior reading, [H566](https://github.com/gasyoun/Uprava/blob/main/handoffs/H566-Opus_RussianTranslation_h317-w1b-real-card-recovery_11.07.26.md)'s real-card probe earlier the same day (11-07-2026), had measured **682,753 ms** (NO-GO, worse than the 284.8 s reading before it). Logged both the probe and its outcome to [`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md).

Requeued `no_pwg_w02`'s 27 transient keys (pulled from `audit_window.report.json`'s `requeue_transient`, since no `no_pwg_w02.requeue.keys.txt` had been persisted) via `gen_opt_harness2.py no_pwg_w03 --nominal --keys=<27 keys> --output-budget=1 --no-tm`, cost-gated ($0.47/card, 27 cards, under ceiling), ran through the Workflow tool.

**Result: 13/27 cards returned non-null (0 conn-errors this time, an improvement); `audit_window.py` then downgraded 2 of those 13 to defect** (`gagana~~h0_zz_nws00`, `mahat~~h0_zz_pw` — real content flags, not transient) **→ 11/27 clean.** The other 14/27 were kill-timeouts, all at the 180 s `KILL_CEIL` on 150–2,200-byte skeletons (same signature as `no_pwg_w02`, transient rate 52% — still degraded, though `agents_spent`/`kill_timeouts` telemetry (H462) shows 0 conn-errors vs `no_pwg_w02`'s 3, and the fresh warm-up probe read 21 s vs the pre-window degraded readings of 285–683 s: a real but partial recovery, not a clean environment). Promoted the 11 clean sub-cards (`Atmavat`/`CAyA`/`duzkfta`/`gAyatrI`/`jananI`/`kumArI`/`mAtrA`/`medinI`); `SamDya`/`sat`/`smita`/`mahat`/`ozaDI` stay null or defect. Store `src/pwg_ru_translated.jsonl`: 11,317 → **11,344 rows**. TM rebuilt (`translation_memory.ru.json`, 2,327 cards).

**Per the H255 drain-loop rule ("requeue nulls once with `--no-tm`") — this was that one permitted requeue** (`no_pwg_w02`'s transients → `no_pwg_w03`); the 14 transient + 2 defect keys from `no_pwg_w03` are **documented residual, not requeued again this session** (the `vid`/`dah` precedent): `kum_ar_i~~h0_zz_nws00`, `m_atr_a~~h0_zz_nws00`, `mahat~~h0_zz_nws00`, `medin_i~~h0_zz_sch`, `oza_d_i~~h0_zz_nws00`, `oza_d_i~~h0_zz_pw`, `sa_m_dy_a~~h0_zz_nws00`, `sa_m_dy_a~~h0_zz_pw`, `sa_m_dy_a~~h0_zz_sch`, `sat~~h0_zz_nws00`, `smita~~h0_zz_nws00`, `smita~~h0_zz_pw`, `smita~~h0_zz_sch`, `gagana~~h0_zz_pw` (transient), `gagana~~h0_zz_nws00`, `mahat~~h0_zz_pw` (defect). `no_pwg_runnable` count: 160 (down from 172 pre-`no_pwg_w02`).

**Next:** the 232-lemma queue continues via `no_pwg_scale_plan.py --window-size 20 --limit-windows 1 --start-index 3`, picking fresh headwords (the w1 still-null tail is now exhausted of easy wins — its residual needs either a future warm-up-gated retry once the env fully recovers, or a manual review pass). Re-run `probe_log.py gate` before any future window; if latency climbs back toward the 90–680 s range seen 10/11-07, pause again per the H442 guardrail.

---

## 2026-07-11 — no-PWG lane window `no_pwg_w03` (H255 scale drain, fresh 6-headword window, `no_pwg_scale_plan.py --start-index 3`) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Sonnet 5** (`claude-sonnet-5`) — 🟡 39/47 candidate rows PROMOTED, residual documented

**⚠ Bug found + fixed first:** `no_pwg_scale_plan.py`'s `STORE` constant pointed at `src/pilot/pwg_ru_translated.jsonl` (doesn't exist) instead of the real store `src/pwg_ru_translated.jsonl` — `promoted_headwords_seen` was silently always `0`, so the planner's dedup against already-promoted headwords never fired. Caught before generation: the first `--start-index 3` plan offered a "still-null tail" window whose 19/29 subcards were **already promoted** (Bagavat/CAyA/GaRwA/SAKA/... from the prior `no_pwg_w02`/`no_pwg_w03` requeue sessions above). Fixed the path (`STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')`), verified with a throwaway store copy (`read_store_heads()` → 159 promoted heads, was 0), delivered via isolated worktree + PR ([SanskritLexicography PR #349](https://github.com/gasyoun/SanskritLexicography/pull/349), merged). Re-ran the planner with the fix live: `remaining headwords: 232→216`, a genuinely fresh 6-headword/13-subcard window (`gagana`/`mahat`/`ozaDI`/`saMDyA`/`smita`/`tA`).

**⚠ Naming collision noted (not fixed):** this session's fresh window and the prior session's requeue window both landed on the root name `no_pwg_w03` — `no_pwg_scale_plan.py --start-index 3` doesn't check which window-index roots already have entries in this RUN_LOG/registry, so re-running it on a later day silently reuses an already-used root. No data was lost (each window's `wf_output.<root>.json` in `src/pilot/output/` was distinct at generation time and both were promoted correctly with explicit `--glob`), but a future window should bump `--start-index` past any root already logged here, or the planner should track used roots itself.

**Pre-flight:** fresh load-representative warm-up probe (own 6,492-byte `probe_log.py prompt` payload) via the Workflow tool — **21.05 s, 0 conn-errors → GO**, matching the last GO reading (21.18 s) and clear of the 682.8 s NO-GO seen on H566. Logged to `GENERATION_API_PROBE_LOG.md`.

**Generation (`no_pwg_w03`, 13 cards/13 batches, `--output-budget=1`):** preflight cost gate GO (~$6/window, under the $25 ceiling). **Result: 11/13 clean, 2 null** (`oza_d_i~~h0_zz_pw`: StructuredOutput retry-cap exceeded; `t_a~~h0_zz_nws00`: kill-timeout 180s). `audit_window.py` additionally flagged 3 of the 11 as content defects (`STRANDED-ANCHOR`/circular-gloss on `gagana~~h0_zz_nws00`, `mahat~~h0_zz_pw`, `sa_m_dy_a~~h0_zz_sch`) → **8/13 truly clean this pass.**

**Requeue (`no_pwg_w03_rq1`, the one permitted requeue, `--no-tm`):** the 2 null keys only (not the 3 defects, per the drain-loop rule). **Result: 1/2 clean** (`oza_d_i~~h0_zz_pw`); `t_a~~h0_zz_nws00` failed the SAME kill-timeout again (180s @ skelBytes=4379) — **documented residual, not requeued a third time** (vid/dah precedent).

**⚠ Second gotcha at promotion:** ran `promote_final_cards.py --merge` with its **default** `--glob` first (matches `wf_output*.json` relative to the repo ROOT, not `src/pilot/output/`) — it silently ingested 5 unrelated stray root-level `wf_output*.json` files left over from earlier sessions (`wf_output.h442.h317_w1b.p0.json`, `wf_output.json`, `wf_output.nominal_w1_100small.json` + `.requeue7.json`, `wf_output.sc.dah.autosplit.json`) and "promoted" 130 sub-cards across 88 unrelated roots — **my actual no_pwg_w03/rq1 output was never touched** (store stayed at 11,344 rows). Verified harmless (diffed the `.premerge.*.bak` against the resulting store: 0 content-length differences — a pure no-op re-write of already-current rows), deleted the no-op backup, then re-ran with the correct **explicit** `--glob src/pilot/output/wf_output.no_pwg_w03.json` (and again for `..._rq1.json`). This is the SAME gotcha the `no_pwg_w02` entry above already flagged ("Always pass an explicit `--glob`") — repeating it here because it recurred even with that warning already in this file; a future fix could make `--merge` refuse the default glob when explicit output files exist in `src/pilot/output/`, or make the default glob scan `src/pilot/output/` instead of the repo root.

**Promoted 9 clean sub-cards total** (8 from `no_pwg_w03` + 1 from `no_pwg_w03_rq1`; 38+1 = 39 sense rows across 6 headwords). Store `src/pwg_ru_translated.jsonl`: 11,344 → **11,383 rows**. TM rebuilt (`translation_memory.ru.json`, 2,338→2,339 cards). `no_pwg_runnable` count: 160 → **154**.

**Documented residual (not requeued further):** `t_a~~h0_zz_nws00` (2× kill-timeout — infra-degraded, not content), `gagana~~h0_zz_nws00`/`mahat~~h0_zz_pw`/`sa_m_dy_a~~h0_zz_sch` (content defects — `STRANDED-ANCHOR`/circular-gloss, needs manual rework not blind retry).

**Next:** continue the 232-lemma queue via `no_pwg_scale_plan.py --window-size 20 --limit-windows 1 --start-index 4` (bump past `w03`'s reused index). Re-run `probe_log.py gate` before any future window.

---

## 2026-07-11 — no-PWG lane window `no_pwg_w04` (H255 scale drain, first genuine *queue-mode* window, `no_pwg_scale_plan.py --start-index 4`) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Sonnet 5** (`claude-sonnet-5`) — 🟡 33/48 candidate sub-cards PROMOTED, residual documented

**⚠ Bug found + fixed first:** `no_pwg_scale_plan.py`'s `existing_subcards()` scanned `OUT = os.path.join(HERE, 'output')` (`src/pilot/output/`) for the `<head>~~h0_zz_*.raw.txt` sidecars that `_pilot_gen_merged.py` actually writes to `src/pilot/input/` — a directory mismatch. It never surfaced before because every prior window (`w02`/`w03`) drained the `no_pwg_w1.still_null` **tail**, whose subcard keys come straight from `STILL_NULL` (a different code path that never calls `existing_subcards()`). The tail is now exhausted, so `--start-index 4` was the first window to hit **queue mode** (`tail_mode=False`) and the bug fired immediately: `_pilot_gen_merged.py` correctly generated 35 sub-card sidecars for the 20 fresh headwords, but the planner then found 0 of them and aborted (`FAIL: no_pwg_w04 produced no no-PWG subcards`). Fixed by pointing `existing_subcards()` at `os.path.join(SRC, 'pilot', 'input')` (`_pilot_gen_merged.py`'s real `OUT`) instead of the module's own `OUT`. Re-ran the planner with the fix live: prepared `no_pwg_w04` cleanly (35 sub-cards / 20 headwords), cost gate GO (~$15.93 est., under the $25 ceiling).

**Generation (`no_pwg_w04`, 35 cards/33 batches, `--output-budget=1`):** **Result: 22/35 non-null, 13 null** (all kill-timeout 180s except one `selfheal-nothing-resolved`). `audit_window.py` flagged 7 of the 22 non-null as content defects (circular-gloss/missing-senses risk signals) → **15/35 truly clean this pass.**

**Requeue (`no_pwg_w04_rq1`, the one permitted requeue, `--no-tm`):** the 13 null keys only (not the 7 defects, per the drain-loop rule). **Result: 11/13 non-null, 2 null** (`_gawik_a~~h0_zz_nws00`: SAME kill-timeout again at 180s; `_kowa~~h0_zz_pw`: selfheal-nothing-resolved). `audit_window.py` flagged 3 of the 11 as content defects → **8/13 truly clean this pass.**

**Promotion:** per the handoff's own guardrail ("Held for G5 — promoted rows are `ai_translated`, held from the citable edition until human G5 review"), `promote_final_cards.py` promotes every **non-null** card regardless of the audit's content-defect flag (it has no awareness of `audit_window.py`'s semantic risk scorer) — the defect flags are a quality signal for the eventual G5 human pass, not a promotion gate. Used the explicit glob (recurring gotcha from the `no_pwg_w02`/`w03` entries above — the default glob matches the repo root): `--glob "src/pilot/output/wf_output.no_pwg_w04*.json"` (a bracket-class glob like `w04[_rq1]` does **not** match the multi-char `_rq1` suffix — needs a real wildcard). **Promoted 33 non-null sub-cards** (15 audit-clean + 7 defect-flagged from `w04`, 8 audit-clean + 3 defect-flagged from `w04_rq1`; 53 sense rows across 20 headwords). Store `src/pwg_ru_translated.jsonl`: 11,383 → **11,436 rows**. TM rebuilt (`translation_memory.ru.json build --lang ru`): 2,339 → **2,371 cards**. `no_pwg_scale_plan.py`'s own remaining-headword count (232-lemma queue): 210 → **190**.

**Documented residual (not requeued further):** `_gawik_a~~h0_zz_nws00` (2× kill-timeout — infra, not content), `_kowa~~h0_zz_pw` (selfheal-nothing-resolved), plus the 10 content-defect-flagged sub-cards across both windows (`_b_azita~~h0_zz_nws00`, `_badr_a~~h0_zz_nws00`, `_badr_a~~h0_zz_sch`, `_dar_a~~h0_zz_sch`, `_gawik_a~~h0_zz_nws00`(defect+transient), `_kecar_i~~h0_zz_nws00`, `_kecar_i~~h0_zz_sch`, `_kowa~~h0_zz_nws00`, `_kowa~~h0_zz_pw`(defect+transient), `_s_alyodana~~h0_zz_nws00`) — all already promoted as `ai_translated` per the guardrail above, but flagged in `audit_window.report.json`/`window_status.json` for the G5 human review pass, not silently clean.

**Next:** continue the 232-lemma queue via `no_pwg_scale_plan.py --window-size 20 --limit-windows 1 --start-index 5` (the planner's own "next window" hint after this run reused a stale `no_pwg_w02` name — a residual instance of the `w03` naming-collision gotcha noted above; always pass an explicit `--start-index` past every root already logged in this file, don't trust the hint blindly). Re-run `probe_log.py gate` before any future window.

---

## 2026-07-11 — no-PWG lane window `no_pwg_w05` (H255 scale drain, `no_pwg_scale_plan.py --start-index 5`) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Sonnet 5** (`claude-sonnet-5`) — 🟡 40/65 candidate sub-cards PROMOTED, residual documented

Prepared cleanly with the `w04` OUT-path fix already live: 20 headwords / 44 sub-cards, cost gate GO (~$20.61 est., under the $25 ceiling).

**Generation (`no_pwg_w05`, 44 cards/41 batches, `--output-budget=1`):** **Result: 23/44 non-null, 21 null** (18 kill-timeout, 3 `selfheal-nothing-resolved`). `audit_window.py` flagged 7 of the 23 non-null as content defects → **16/44 truly clean this pass.**

**Requeue (`no_pwg_w05_rq1`, the one permitted requeue, `--no-tm`):** the 21 null keys only (not the 7 defects, per the drain-loop rule). **Result: 17/21 non-null, 4 null** (`_u_das~~h0_zz_pw`: SAME kill-timeout again, `_sibi~~h0_zz_pw`/`a_sud_da~~h0_zz_pw`/`aklizwa~~h0_zz_pw`: SAME `selfheal-nothing-resolved` again). `audit_window.py` flagged 4 of the 17 as content defects (one high-confidence: `ajagan_d_a~~h0_zz_pw` untranslated braced German gloss) → **13/21 truly clean this pass.**

**Promotion:** same explicit-glob discipline as `w04` — `--glob "src/pilot/output/wf_output.no_pwg_w05*.json"` (real `*` wildcard). **Promoted 40 non-null sub-cards** (16 audit-clean + 7 defect-flagged from `w05`, 13 audit-clean + 4 defect-flagged from `w05_rq1`; 69 sense rows across 20 headwords). Store `src/pwg_ru_translated.jsonl`: 11,436 → **11,505 rows**. TM rebuilt (`translation_memory.ru.json build --lang ru`): 2,371 → **2,411 cards**. `no_pwg_scale_plan.py`'s own remaining-headword count (232-lemma queue): 190 → **170**.

**Documented residual (not requeued further):** `_u_das~~h0_zz_pw` (2× kill-timeout — infra, not content), `_sibi~~h0_zz_pw`/`a_sud_da~~h0_zz_pw`/`aklizwa~~h0_zz_pw` (2× `selfheal-nothing-resolved` each), plus the 11 content-defect-flagged sub-cards across both windows (`a_smar_i~~h0_zz_nws00`, `_sy_am_a~~h0_zz_nws00`, `a_b_uta~~h0_zz_nws00`, `_sibi~~h0_zz_nws00`, `_su_r_w_i~~h0_zz_nws00`, `_su_r_w_i~~h0_zz_sch`, `_sy_am_a~~h0_zz_sch`, `a_sakta~~h0_zz_sch`, `ajagan_d_a~~h0_zz_pw`(high-confidence untranslated-gloss), `aklizwa~~h0_zz_sch`, `ambaz_w_a~~h0_zz_sch`) — all already promoted as `ai_translated` per the `w04` guardrail, flagged for the eventual G5 human review, not silently clean. `ajagan_d_a~~h0_zz_pw` in particular needs a manual German-gloss translation pass, not blind retry.

**Next:** continue the 232-lemma queue via `no_pwg_scale_plan.py --window-size 20 --limit-windows 1 --start-index 6`. Re-run `probe_log.py gate` before any future window.

## 2026-07-11 — no-PWG lane window `no_pwg_w06` (H255 scale drain, `no_pwg_scale_plan.py --start-index 6`) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Sonnet 5** (`claude-sonnet-5`) — 🟡 29/36 candidate sub-cards PROMOTED, residual documented

Ran from an isolated `git worktree` off `origin/master` (per the handoff's own guardrail) since the shared checkout was mid-flight on an unrelated stray branch (`docs/metadoc-template-v2-backfill-h663`) with uncommitted leftovers from another agent's session; the gitignored runtime store (`pwg_ru_translated.jsonl`, 11,505 rows) + TM sidecar were copied in from the shared checkout since they are local-only artifacts, not tracked. Prepared cleanly: 20 headwords / 36 sub-cards, cost gate GO (`perf_preflight.py --nominal --keys=... --output-budget=1`: $16.86 est., under the $25 ceiling; the `--nominal` flag is required or the tool fails with `no rootmap`).

**Generation (`no_pwg_w06`, 36 cards/30 batches, `--output-budget=1`):** **Result: 18/36 non-null, 18 null** (12 kill-timeout, 6 `selfheal-nothing-resolved`). `audit_window.py` flagged 7 of the 18 non-null as content defects (circular-gloss/missing-senses risk signals; `apratize_da~~h0_zz_pw` high-confidence) → **11/36 truly clean this pass.**

**Requeue (`no_pwg_w06_rq1`, the one permitted requeue, `--no-tm`):** the 18 null keys only (not the 7 defects, per the drain-loop rule). **Result: 11/18 non-null, 7 null** (`arvant~~h0_zz_pw`: SAME kill-timeout again at 83s; `apr_apta~~h0_zz_pw`/`as_a_dya~~h0_zz_pw`/`asa_mskfta~~h0_zz_pw`/`avy_ahata~~h0_zz_pw`/`avyagra~~h0_zz_pw`/`b_ahlika~~h0_zz_pw`: SAME `selfheal-nothing-resolved` again — these 6 are the `presplit_keys` cohort, a recurring shape worth flagging for a future harness fix rather than blind retry). `audit_window.py` flagged 3 of the 11 as content defects (2 high-confidence: `ativiz_a~~h0_zz_pw`/`ativiz_a~~h0_zz_pwkvn` untranslated braced German gloss) → **8/18 truly clean this pass.**

**Promotion:** same explicit-glob discipline as `w04`/`w05` — `--glob "src/pilot/output/wf_output.no_pwg_w06*.json"` (real `*` wildcard). Every non-null card is promoted regardless of the audit's content-defect flag (per the `w04` guardrail note — `promote_final_cards.py` has no awareness of `audit_window.py`'s semantic risk scorer; the flag is a G5-review signal, not a promotion gate). **Promoted 29 non-null sub-cards** (18 from `w06`, 11 from `w06_rq1`; 53 sense rows across 10 distinct headwords). Store `src/pwg_ru_translated.jsonl`: 11,505 → **11,558 rows**. TM rebuilt (`translation_memory.ru.json build --lang ru`): 2,411 → **2,440 cards**. `no_pwg_scale_plan.py`'s own remaining-headword count (232-lemma queue): 170 → **155**.

**Documented residual (not requeued further):** `arvant~~h0_zz_pw` (2× kill-timeout — infra, not content), `apr_apta~~h0_zz_pw`/`as_a_dya~~h0_zz_pw`/`asa_mskfta~~h0_zz_pw`/`avy_ahata~~h0_zz_pw`/`avyagra~~h0_zz_pw`/`b_ahlika~~h0_zz_pw` (2× `selfheal-nothing-resolved` each — all 6 are `presplit_keys`, i.e. cards whose `<ls>` count exceeded the output budget and got routed to direct fragment translation; worth investigating as a class in a future session rather than per-card), plus the 10 content-defect-flagged sub-cards across both windows (`anupapatti~~h0_zz_pw`, `anupapatti~~h0_zz_sch`, `apar_ajit_a~~h0_zz_sch`, `apratize_da~~h0_zz_pw`(high-confidence broken-markup), `arhaka~~h0_zz_pw`, `asteya~~h0_zz_pw`, `asvatantra~~h0_zz_pw`, `ativiz_a~~h0_zz_pw`(high-confidence untranslated-gloss), `ativiz_a~~h0_zz_pwkvn`(high-confidence untranslated-gloss), `ativiz_a~~h0_zz_sch`) — all already promoted as `ai_translated` per the guardrail above, flagged for the eventual G5 human review, not silently clean.

**Next:** continue the 232-lemma queue via `no_pwg_scale_plan.py --window-size 20 --limit-windows 1 --start-index 7`. Re-run `probe_log.py gate` before any future window.

---

## 2026-07-12 — no-PWG lane: store-persistence root-fix (H805) — **no Max/Workflow generation run** — orchestration **Opus 4.8** (`claude-opus-4-8`)

A session opened to run the `--start-index 7` window instead found + fixed a **data-loss bug** and, per MG's call, ran no generation this pass.

**Finding — w06's promotions are lost from the live store.** Reconciling against `origin/master`:

| store on disk | rows | = end of | note |
|---|---|---|---|
| main checkout `src/pwg_ru_translated.jsonl` | **11,505** | w05 | the live/canonical store |
| (nowhere) | 11,558 | w06 | RUN_LOG claims this, but no such store exists |
| `SanskritLexicography-h338/…` (stale) | 11,261 | H178 | old worktree, unrelated |

`no_pwg_w06` ran in an **isolated worktree** (this file's w06 block notes it), copied the 11,505 store in, promoted to 11,558 there — and that worktree + its store + its `wf_output.no_pwg_w06*.json` were removed after [PR #366](https://github.com/gasyoun/SanskritLexicography/pull/366) merged. **w06's 29 sub-cards / 53 sense rows are gone from every store on disk** (regenerable only). Because the planner dedups against the store, `--start-index 7` re-offered **w06's exact 20 headwords** (the `--start-index` flag only names the window; it never selects headwords — selection is always the first un-promoted `window_size`). So the "next window" was a re-run of w06's hardest cases, not fresh territory.

**Root cause + fix (H805).** Every consumer resolved the gitignored store relative to its own directory, so a worktree promoted into a discarded copy. New [`src/store_path.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py) `canonical_store()` resolves ONE logical store (`$PWG_RU_STORE` → MAIN-worktree store when in a linked worktree → local); wired into `promote_final_cards.py` (RU) + `promote_en.py` (EN, parity) + `no_pwg_scale_plan.py` + `nominals_worklist.py`. Redirect proven from a live worktree (planner `store_path` → `../../SanskritLexicography/RussianTranslation/src/…`; promote prints a `canonical/shared` provenance line). `window_selftest.py` green, `lang_parity_check.py` 43 entries no drift (new `canonical_store_path_h805` SHARED entry). Full account: [H805 handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H805-Opus_SanskritLexicography_pwg_ru_worktree_store_persistence_fix_12.07.26.md).

**Probe (12-07, Sonnet 5, 6.5 KB load-representative):** 0 conn-errors, clean full-length RU output, 48.5 K tok — a recovering regime vs the 285–683 s degraded readings of 10–11 Jul, **but 31.6 s total trips the 30 s ceiling → recorded NO-GO** in [`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md). Wait for a clean sub-30 s reading before the next window.

**Next:** resume the drain with `no_pwg_scale_plan.py --start-index 7` on a clean probe — its first window now correctly re-covers w06 (healing the loss) before advancing; the store is persistent from here.

---

## 2026-07-12 — no-PWG lane window `no_pwg_w07` (H255 scale drain, `--start-index 7`, post-H805) — gen **Sonnet 5** (`claude-sonnet-5`) / orchestration **Opus 4.8** (`claude-opus-4-8`)

**Resume + infra state.** First live drain window since the H805 store-persistence fix, so promotions now persist to the canonical main-checkout store instead of a discarded worktree copy. Two **plain-text** warm-up probes fired this session, **both NO-GO**: 31.6 s (13:45 UTC) then **35.7 s (15:07 UTC)**, each with **0 conn-errors + clean full-length RU output**. This is an *elevated* regime, not the catastrophic one — but a **genuine ~50 % slowdown** vs the **21 s** GO readings the same ~6.5 KB load-representative probe gave on 11-07 (so NOT a ceiling-calibration artifact; the same payload passed at 21 s yesterday). Still nowhere near the 285–683 s hangs of 10–11 Jul. Both readings recorded in [`GENERATION_API_PROBE_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md).

**Refinement (MG):** a plain-text translation probe under-tests the real path — production generation forces a **StructuredOutput / schema** call, which is where the kill-timeout latency actually lives (single-fragment cards have no self-heal lane, so a slow StructuredOutput = a permanent null). So the legitimate way to clear (or confirm) the gate is a **schema-carrying warm-up** through the real harness path, then re-check the gate — not a blind override of a plain-probe NO-GO. Machinery already exists (harness + reachable `CARDS_SCHEMA`); this is a launch decision.

**Window = w06 recovery + advance.** Because w06's 29 promotions were lost pre-H805, `--start-index 7` re-offers exactly w06's 20 headwords (the planner dedups against the store; `--start-index` only names the window, it never selects headwords). With the H805 fix, these promotions now land in the persistent store — healing the w06 loss. Cost gate: 36 sub-cards / 30 batches, `--output-budget=1`, **$16.86 est (verdict ok)**.

**Schema-carrying warm-up + generation (`no_pwg_w07`, 36 cards / 30 batches, `--output-budget=1`):** _<results appended after the run>_
