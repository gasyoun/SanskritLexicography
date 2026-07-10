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
