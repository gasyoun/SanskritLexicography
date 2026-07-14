# PWG gold-sample fidelity judgment — Fable window S7 (quality bar for the bulk EN run)

_Created: 02-07-2026 · Last updated: 02-07-2026_

**Session:** Fable window S7 · **Judge:** Fable 5 (`claude-fable-5`) · **Ground truth:** faithful
to the PWG German source ([FU1 locked decision 6](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md)
— Monier-Williams is a cross-check, never the standard). This memo is the FU1 judge-tier output
that sets the quality bar for the PWG→EN bulk tranche and for Phase 2 (merge → judge → human gold).

## Headline

| sample | unit | n | faithful | acceptable-loss | unfaithful | clean rate (F+AL) | unfaithful 95 % CI (Wilson) |
|---|---|---:|---:|---:|---:|---:|---|
| RU, Slice C+D promoted | card | 50 | 28 | 20 | **2** | **96.0 %** | 4.0 % [1.1 %, 13.5 %] |
| EN, all 16 pilot roots | sense row | 68 | 33 | 34 | **1** | **98.5 %** | 1.5 % [0.3 %, 7.9 %] |
| combined | — | 118 | 61 | 54 | **3** | **97.5 %** | 2.5 % [0.9 %, 7.2 %] |

Zero omissions of sense content, zero register drift, zero semantic term mistranslations at the
gloss level. **All three unfaithful verdicts are the same failure class: unsourced ADDITION** —
the pipeline occasionally annotates instead of translating.

### The three unfaithful cases (full)

1. `yaj~~h0_04_ati` (RU, *addition*): German has one gloss {%mit dem Opfer übergehen%}; the
   Russian renders it correctly, then **adds a second interpretive gloss** «пропустить
   (кого-либо) при раздаче жертвенного» that the German does not contain.
2. `vah~~h0_01_sec_1` s7 (RU, *addition*): German attributes the derivation to Benfey alone
   («wird von BENFEY … zurückgeführt»); Russian says «возводится BENFEY **и другими**» —
   an invented scholarly attribution.
3. `g_a~~h0_14_a_byastam` (EN, *addition + mw-tm-contamination*): German {%untergehen vor, bei,
   während einer Handlung%}; English adds **"(of a heavenly body)"** — a parenthetical in
   Monier-Williams' characteristic style ("to go down, set (as heavenly bodies)") with no German
   counterpart. The single confirmed MW-translation-memory leak in the sample.

### Failure classes (all severities)

| class | RU (50 cards) | EN (68 rows) | reading |
|---|---:|---:|---|
| markup-loss | 17 | 32 | dropped `{%..%}` gloss markers / `<div>` wrappers, meaning intact — the dominant residual, **systematic on the EN path** (~47 % of rows) |
| addition | 5 | 3 | 3 of these are the unfaithful cases above; the rest are harmless header/gloss doubling |
| grammar | 2 | 0 | trivial Russian agreement slips |
| omission | 1 | 0 | a German editorial note retained **verbatim untranslated** (`v_a~~h1_18_sam`) — coverage gap, nothing lost |
| term-mistranslation | 0 | 1 | minor: "zu verbinden" → "to be read with" (should be "construed together") |
| register-drift | 0 | 0 | — |
| mw-tm-contamination | — | 1 | case 3 above |

## Verdict: **PROCEED**, with two prompt tightenings and one gate

The generation quality is at the bar the FU1 plan assumed (this Fable-tier pass independently
corroborates the [2026-06-30 Opus 4.8 interim](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FIDELITY_JUDGE_2026-06-30.md):
98 % clean, defects markup/grammar not meaning). Note honestly: FU1 Phase-1 EN **generation already
ran** (2026-07-01, Sonnet 5, 94.9 % coverage), so this verdict operationally gates **Phase 2**
(promote_en → dcs_freq → judge inlining → human gold → G5) and **every future tranche** under the
standing bilingual policy. No re-generation and no re-judging with a changed rubric is required.

**Tighten before the next generation tranche (prompt-level, both languages):**

1. **"Translate, don't annotate."** Add to [`src/pilot/tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt)
   and the RU counterpart: never add parenthetical domain clarifications, extra glosses, or
   attributions ("and others") beyond what the German states. All 3 unfaithful cases die here.
2. **Explicit MW-TM guard (EN path):** the MW reference may inform *wording* of a sense the
   German attests, never *add content*; if MW has detail the German lacks, omit it.

**Gate to add (deterministic, no quota):** extend the audit (`audit_window.py` /
[`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py))
with a `{%..%}`-pair-count soft flag (DE vs target) — markup-loss is ~⅓ of RU cards and ~half of
EN rows; it is mechanically detectable and mechanically fixable, and should stop riding on judge
samples. The untranslated-editorial-note case belongs to the existing `fix_german_connectives`
family.

### Follow-ups — IMPLEMENTED (2026-07-02, Opus 4.8 `claude-opus-4-8`; A/B generation Sonnet 5 `claude-sonnet-5`)

All three recommendations are delivered (handoff [`H056-Opus_SanskritLexicography_pwg_s7_quality_gate_02.07.26.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H056-Opus_SanskritLexicography_pwg_s7_quality_gate_02.07.26.md)):

1. **Prompt "translate, don't annotate"** — a HARD RULE added to BOTH the RU template
   (`run_pilot_wf.js` `TR`, rule 6) and [`src/pilot/tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt)
   (rule 4): render exactly what the German states; never add interpretive glosses, scope
   qualifiers, or attributions («и другими» / "and others") the source lacks.
2. **MW-TM guard (EN)** — the injected MW block (`gen_opt_harness2.mw_tm_block`) and
   `tr_en.txt`'s MW REFERENCE paragraph now state MW is a **terminology cross-check only**:
   no phrase/parenthetical/sense copied unless the German licenses it (kills the
   "(of a heavenly body)" leak class).
3. **`{%..%}`-pair-count soft gate** — the deterministic check the memo asked for **already
   shipped** in [PR #78](https://github.com/gasyoun/SanskritLexicography/pull/78) (DharmaMitra
   crosswalk): RU `prompt_rule_audit.markup_wrapper_dropped` (soft/low, never a requeue) +
   EN `audit_window_en.MARKUP-LOSS` (soft, never fails `--strict`). This session pinned both
   with `window_selftest.py` fixtures (`test_markup_loss_soft_flag_ru/_en`); suite green.

**A/B validation** (yaj, 7 cards incl. the 208-`<ls>` dense head, old prompt vs new prompt,
generation Sonnet 5 `claude-sonnet-5`, ≤3-wide, saved to scratch — never promoted). On the 6
structurally-identical non-partial cards (same 13 German `{%..%}` pairs): marker retention
**2/13 → 13/13** (drop-rate **85 % → 0 %**); addition-class high-confidence risks
(`untranslated_braced_german_gloss`) **3 → 0**; coverage **7/7 ok, 0 null** in both arms (no
regression). The dense head stayed partial in both (self-heal fragment variance, not a prompt
effect). n is small and generation is stochastic — indicative, not conclusive — but the
direction is unambiguous and nothing regressed. Ground truth: faithful-to-the-German
([FU1 decision 6](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FU1_PLAN.md)).

## Sampling plan the bulk run must carry (binding for Phase 2)

1. **Re-run `promote_en.py` first** — state finding: the current store
   ([`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl))
   carries `en` **only on DA (700 rows)**; the earlier pilot EN merge was superseded by a later
   `promote_final_cards.py` rebuild. Phase-2 sampling over the store is meaningless until the EN
   layer is re-merged (join is idempotent, on German text).
2. **Human gold:** [`src/gold_sample_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_sample_en.py)
   `--n 300` (fixed seed) over the re-merged store — strata = DCS band × source_type × stratum,
   MW hidden; two annotators; κ + error rate via `gold_agreement.py`. Unchanged from the locked plan.
3. **LLM judge, full coverage:** per-sense verdicts inlined via `promote_en.py --judge`
   (judge tier ≥ Opus 4.8 (`claude-opus-4-8`); Fable-class for adjudicating disagreements).
4. **Acceptance gate:** unfaithful ≤ 2 % point estimate with Wilson upper bound ≤ 8 % at n ≥ 300;
   **zero unremediated `mw-tm-contamination`** instances (each found instance is hand-patched);
   markup-loss tracked but non-blocking (deterministic fix per the gate above).
5. **Every future generation tranche** carries a 50-card stratified per-tranche judge sample
   (rotate the seed; rubric = this memo's; unit = card for RU, sense row for EN).

## Method & provenance (per step, tier + version)

| step | tool / actor | model |
|---|---|---|
| RU sample draw (50 cards, seed 7, population 1,882 Slice C+D cards — independent of the 2026-06-30 seed-42 draw) | [`src/fidelity_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/fidelity_sample.py) `--glob "wf_output.s[cd].*.json"` | deterministic, no model |
| EN judge set (60-row seed-42 stratified draw + 8-row seed-7 naS/yaj supplement → 68 rows, all 16 pilot roots) | `src/gold_sample_en.jsonl` + `wf_output.en.{naS,yaj}.json` | deterministic, no model |
| Batch adjudication (5 RU + 2 EN batches, ≤3-wide) | Agent subagents, session-model inheritance | **Fable 5 (`claude-fable-5`)**, ~455 k subagent tokens |
| Adversarial verification of every unfaithful verdict, spot-check of 11 cards/rows, 4 documented overrides, batch-strictness reconciliation | main session | **Fable 5 (`claude-fable-5`)** |
| Source-integrity check (store DE vs csl-orig) | `su~~h1_05_ud` vs [`pwg.txt` l. 532606](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt) | PASS (only the known citation-period normalization differs) |
| Generation under judgment | RU Slice C+D: Sonnet 4.6 (`claude-sonnet-4-6`, alias `model:'sonnet'` at run time); EN pilot roots: Sonnet 4.6 (`claude-sonnet-4-6`) | — |

Judge-consistency notes: (a) the batch-2 EN subagent scored dropped `{%..%}` markers leniently;
I re-applied the strict batch-1 convention to 3 rows (63, 65, 67 — faithful → acceptable-loss),
so cross-batch class rates are conservative; (b) 1 RU agent verdict was downgraded
(`v_a~~h1_18_sam`: unfaithful → acceptable-loss — the German note is retained verbatim, not lost),
2 were confirmed on my own reading of the German; the EN unfaithful was confirmed against the
German gloss. All overrides are recorded in the evidence file. Senses were capped at 700 chars
for judging; nothing at/after a cap was penalized.

Evidence: [`fable_s7_verdicts_2026-07-02.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/fable_s7_verdicts_2026-07-02.json)
(all 118 verdicts + manifest + overrides). Samples regenerable deterministically (gitignored):
`src/pilot/output/fidelity_sample.s7.jsonl`, `src/pilot/output/en_judge_set.s7.jsonl`.

_Dr. Mārcis Gasūns_
