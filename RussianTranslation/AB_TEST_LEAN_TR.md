# A/B test plan — lean masked-regime TR vs full production TR

**Question.** The opt2 cost is now dominated by per-batch prompt **cache-creation** of the
*full* production `TR` (all HARD RULES + microstructure, ~5–6k tokens). In the masked +
batched regime some of that prompt is dead weight. Can a **leaner TR** cut $/card without
degrading translation quality?

**Decision discipline.** We just measured real run-to-run noise (yuj clean 47 vs 43 on
identical inputs). So this is **non-inferiority** testing with replication, not a single
before/after. Adopt the lean TR ONLY if it is cheaper AND not-worse beyond that noise band.

---

## 1. The change under test (TR_lean spec)

Exactly one variable changes: the `TR` string. `TR_lean` = `TR_full` with these edits, each
justified by the masked/Python-owns-markup regime:

| TR_full section | TR_lean | rationale |
|---|---|---|
| CONV (register, translate-gloss, keep-sigla, two-source, Vedic hedge) | **keep verbatim** | core quality |
| TASK (corpus-candidates primary, Apresjan discriminate, equivalence_type) | **keep** | core quality |
| HARD RULE 1 NO FABRICATION · 2 COVERAGE · 4 NACHTRÄGE | **keep** | correctness/coverage |
| HARD RULE 3 — long "markup delimiters verbatim, fidelity gate counts {#..#}/<ls>…" prose | **compress to one line:** "keep every {Tn} placeholder verbatim and in order" | the model sees `{Tn}`, not markup; Python restores it (the fidelity guard already enforces this) |
| HARD RULE 5 — long NWS owner-map prose | **inject only for batches containing an NWS card** (the `~~h0_zz_*`/`pw` cards) | ~7 of 60 cards are NWS; for the rest this is pure dead weight |
| RENDERING GUIDANCE (samāsa, correlatives, śāstric, synonym cardinality, punctuation, manner, non-circular) | **keep** | quality — the microstructure the project cares about |

Expected prompt reduction: ~30–40% of `TR` (rule-3 prose + rule-5 for ~most batches).
Implementation: a `--lean` flag on `gen_opt_harness2.py` that builds `TR_lean` and gates the
NWS block per batch. **Verify the generated prompt actually changed** (grep — the file-read
bug taught us not to trust intent).

## 2. Design — within-subjects 2×2 (cards × arm), replicated

- **Same card set, both arms, same harness, same grammar injection, same budget, Sonnet.**
- **Test set:** a fixed **24-card sample of `gam`** (already accepted — re-running is pure
  measurement, zero Stage-C impact), stratified to be representative:
  - 2 dense root-head (`h0_00_pwg00/01`), 3 NWS layer (`h0_zz_pw00`, `pw01`, `sch`),
    1 medium prefix (`h0_45_upa`), and ~18 small prefix cards.
  - Fixed key list committed in the plan so both arms and both replicates use identical input.
- **Replication:** run **each arm twice** (full×2, lean×2 = 4 translate runs). The two
  same-arm runs measure the noise band; the cross-arm difference must exceed it to count.

## 3. Metrics

**Cost (primary):** `parse_workflow_cost.py` per run → **$/card**, split into
cache_create / cache_read / output. Also static: `TR_full` vs `TR_lean` token count.

**Quality — deterministic (free, every card):** `audit_window.py` per run →
- clean-key rate, `nws` PASS/FAIL, `sense_dupes` PASS/FAIL, coverage rate, **markup-fidelity
  (must stay 100%)**, semantic-risk count/card.

**Quality — semantic (the real test):** a **blind pairwise judge** workflow. For each of the
24 cards, give an Opus judge the German source + the two Russian renderings (full vs lean) in
**randomized, unlabeled order**; it picks better / tie on {correctness, completeness, register,
near-synonym discrimination} with a one-line reason. Report win/tie/loss for lean.

## 4. Decision rule

Adopt `TR_lean` as the default **iff all hold**:
1. **Cheaper:** mean $/card drop ≥ **15%** (lean vs full), beyond the 2-run spread.
2. **Deterministic non-inferiority:** `nws` and `sense_dupes` still PASS; **fidelity = 100%**;
   clean-rate not lower than full by more than the measured noise band (~±7%); semantic-risk
   count/card not higher beyond noise.
3. **Semantic non-inferiority:** lean **wins+ties ≥ 50%** of cards and shows **no systematic
   regression** (no quality dimension where lean loses on ≥ ~25% of cards).

If cost drops but quality regresses → keep full. If quality holds but cost barely moves → keep
full (not worth the divergence). Partial win (e.g. rule-3 compression safe, NWS-gating safe,
microstructure-trim unsafe) → adopt only the safe edits and re-document.

## 5. Confounds & guards

- **Non-determinism:** handled by 2 runs/arm + the noise band; never conclude from N=1.
- **Prompt didn't actually change:** grep the generated harness for the removed strings.
- **Root cherry-pick:** the 24-card sample spans dense/NWS/small so a lean cut that only hurts
  one card-type is caught. (Optional: repeat on a second root, e.g. a `yuj` slice, before
  org-wide adoption.)
- **Judge bias:** randomize order, blind labels, source-grounded prompt.
- **Cost noise:** report cache_create separately (the lever) — that's where the lean win must show.

## 6. Execution steps (commands)

```
# 0. build TR_lean behind a flag, verify the prompt changed
python src/pilot/gen_opt_harness2.py gam --keys=<24-key list>            # arm A (full)
python src/pilot/gen_opt_harness2.py gam --keys=<24-key list> --lean     # arm B (lean)
grep -c "fidelity gate counts" run_pilot_wf.opt2.js   # expect 1 (full) / 0 (lean)

# 1. run 4 workflows (full×2, lean×2), save each result
# 2. cost:    python src/pilot/parse_workflow_cost.py <4 transcript dirs>
# 3. quality: python src/pilot/audit_window.py <each>.json --root gam
# 4. judge:   a small pairwise-judge workflow over the 24 cards (Opus)
# 5. apply the §4 decision rule
```

**Test budget:** 4 × 24-card translate runs (~$0.06/card → ~$1.4/run ≈ **$6**) + one Opus
judge pass over 24 pairs (small). Cheap relative to the per-root saving if lean wins (a 30%
prompt cut on every future root).

---

## RESULTS (2026-06-29) — lean REJECTED

**Quality (cache-independent, decisive):**

| arm | guard-nulls / 24 | risks/card |
|---|---:|---:|
| full run 1 / run 2 | **0 / 0** | 6.21 / 5.62 |
| lean run 1 / run 2 | **4 / 1** | 7.30 / 5.91 |

Lean regressed markup fidelity (5 guard-nulls vs 0; reproducibly nulled `h0_17_a_bi` in both
lean runs, all **non-NWS** cards). The only lean change touching those cards is the **rule-3
compression** (the detailed "keep `{#..#}`/`<ls>` verbatim, fidelity gate counts" instruction
→ one line). Removing it made the model lose `{Tn}` tokens → markup-count failures. **Fails
deterministic non-inferiority** (decision rule §4.2).

**Cost: INCONCLUSIVE — execution flaw.** The four arms were run **in parallel**, so same-prompt
runs **shared the prompt cache**: full run 2 rode full run 1's cache (cache_create 19.8k vs
308k); the lean pair partially shared too. Per-run cost is therefore confounded — only one
clean cold number exists (full cold **$2.65**/24 cards). Cannot claim lean cheaper.

**Methodology lesson:** a cost A/B must run **sequentially with cache cooldown** (or compare
only cold cache-creating runs), never parallel same-prompt — the 5-min cache makes the second
run artificially cheap.

**Decision:** **reject the lean TR as specified** (quality regression + unproven cost). The
**NWS-gating** edit is safe by mechanism (it cannot cause markup nulls; the NWS cards
translated fine) and remains a candidate, but its cost win was not isolated/measured here. To
pursue it: a clean **sequential** A/B of *NWS-gating-only* (full rule 3 kept) vs full.

## ROUND 2 — NWS-gating-only, SEQUENTIAL (2026-06-29) — also not worth it

Ran full (cold) then nws-gate (cold) one-at-a-time (no parallel cache sharing):

| arm (cold) | cache_create | nulls/24 | risks/card | $ cost |
|---|---:|---:|---:|---:|
| full | 210,662 | 0 | 6.50 | **$1.58** |
| nws-gate (rule 3 kept) | 180,688 | 0 | 6.00 | **$1.67** |

**nws-gate is SAFE** (0 nulls, equal quality — confirms the round-1 nulls were the rule-3
compression, not the NWS-gating) **but gives no net cost benefit** (slightly higher $, swung by
2 random retries; the ~461-tok × 3-batch NWS saving is below the noise floor). Decision rule
(≥15% cheaper) not met.

**Root finding: the TR is not the cost lever.** Per-batch `cache_create` ≈ 42k tokens is
dominated by the **inlined card content** (masked skeletons + portraits, esp. the dense `pw`
cards). TR (2,554) + schema (1,200) + NWS block (461) are a small slice — trimming them is
lost in run-to-run noise. **Keep the full TR.** If more cost reduction is wanted, the lever is
the **card content** (dense-card handling / portrait inlining / schema), not the prompt — a
separate optimization, separately tested.
