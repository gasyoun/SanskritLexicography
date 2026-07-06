# pwg_ru — error analysis (categories × frequencies × examples)

_Created: 07-07-2026 · Last updated: 07-07-2026_

An ACL-style error analysis of the PWG→Russian dictionary-translation pipeline, recast
from the engineering failure-mode catalog
([FAILURE_MODES_AND_KILL_GATE_2026-07-04.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md))
and the H178 forensic re-audit
([H178_REAUDIT_2026-07-06.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_REAUDIT_2026-07-06.md)).
Frequencies come from those two documents, from
[RUN_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md),
[REVIEW_QUEUE_TRIAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_QUEUE_TRIAGE.md)
and [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md);
no number below is new. Category set follows the MQM core typology (Lommel et al. 2014)
as operationalized for professional MT evaluation by Freitag et al. 2021
([Experts, Errors, and Context](https://aclanthology.org/2021.tacl-1.87/)); the
deterministic-gate-as-error-detector framing follows automatic error-classification
work in the Popović 2018 line (citation from model knowledge — verify).

## 1. Taxonomy — engineering gates mapped to MT-evaluation error categories

Every deterministic audit gate in
[audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)
is a proxy detector for one MQM-style category. Counts are the observed real
frequencies at the cited scope, not extrapolations.

| MQM category | Gate / heuristic proxy | Observed frequency (scope) | Severity | Representative example |
|---|---|---|---|---|
| **Omission** (accuracy) | coverage gate, `COVERAGE-LOW` (card senses < source senses); `possible_sense_compression` | 57 × `COVERAGE-LOW` (46 legacy windows, re-audit — upper bound, see §3); sense-compression 38 keys on `i` / 17 on `as` (RUN_LOG per-root risk tables) | major | `gam~~h2_01_sec_1` — 5/9 senses covered (gam run block, [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)) |
| **Untranslated** (accuracy) | `untranslated_braced_german_gloss` / `untranslated_german_residue` (DE-word regex over RU prose and `{%…%}` spans); Opus-judge check (c) | 12 keys on `BU`, 22 on `i`, 21 on `as`, 17 on `sTA` (RUN_LOG); 13/217 cards in the a-section PoC judge triage (bucket A) | major (blocks publication) but cheap to fix | `gam~~h0_13_antar` — braced gloss `{%intercedere, ausschliessen von%}` echoed untranslated into the RU column ([gam~~h0_13_antar.merged.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/gam~~h0_13_antar.merged.md)); German function words `im`/`und`/`also`/`von` left in otherwise-clean cards (`akz` — `und` ×4 + `oder` ×2; `aMSuhasta` — `{t6} im {t7}`; `aMSupawwa` — German `also`; [REVIEW_QUEUE_TRIAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_QUEUE_TRIAGE.md) bucket A) |
| **Addition** (accuracy) | sense-dupe gate (identical-Russian pair within a record ⇒ hard `DUP`); `COVERAGE-OVER` (card senses > source senses); judge-found unsourced additions | sense-dupe gate: 0 fails on all Stage A+B roots (RUN_LOG); 53 × `COVERAGE-OVER` (re-audit — mostly render drift, §3); 3/118 sampled items in the S7 Fable judge, all ADDITION-type | major when real (fabricated content) | S7 judge: invented attribution «и другими», MW-TM leak "(of a heavenly body)" ([.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md), S7 verdict block); `vas~~h0_zz_pw00` `COVERAGE-OVER(57/11)` — render drift, not addition (§3) |
| **Mistranslation** (accuracy) | no deterministic proxy — Opus QA judge + human bucket B only | 19/217 cards bucket B in the a-section PoC, of which 10 at severity ≥2 ([REVIEW_QUEUE_TRIAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_QUEUE_TRIAGE.md)) | major–minor | `ag` — `wegen` rendered «ради» (purpose) instead of «из-за» (cause); `akzayatftIyA` — gender slip «один {t7}» for feminine smṛti |
| **Terminology / attribution** | NWS owner-map gate (each NWS gloss must carry its true owning sub-source); F12 owner-misattribution check | NWS gate: 0 fails on all 4 Stage A+B roots (RUN_LOG); 2 candidate cards rejected at promotion in `no_pwg_w1` for NWS misattribution | critical for a citable dictionary | `devI~~h0_zz_nws00`, `mAyA~~h0_zz_nws00` — rejected 06-07 for NWS F12 owner misattribution + coverage-over (RUN_LOG `no_pwg_w1` resolution block); EN-source NWS glosses carried as tagged `[en]` literals in the `api` card (`[en: also, further, besides, even]`, Rivelex row, [api.merged.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/output/api.merged.md)) — policy-sanctioned, not a defect, but the English-word-in-RU-card surface the guard exists to police |
| **Fluency / formatting** | markup-fidelity: `{Tn}` placeholder count/order guard in `accept()`; `{%…%}` pair-count flag; `unbalanced_sanskrit_delimiters`; `markup_wrapper_dropped` | dropped `{%..%}` echo-markers: RU 17/50 cards, EN 32/68 rows in the S7 sample ([.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)) — the dominant *systematic* residual; `markup_wrapper_dropped` is one of the three classes behind the 16 promoted-as-is flagged keys (§3) | minor (recoverable mechanically) | `gam~~h0_11_anu` — `unbalanced_sanskrit_delimiters` alongside untranslated residue (gam residual list, [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)) |
| **Infrastructure (non-linguistic)** | StructuredOutput schema-emission retry cap; wall-clock kill gate; key-echo mismatch; API outage; budget kill-switch | see §2 — excluded from translation-quality statistics | n/a (cards recovered or held, never silently emitted) | `dah~~h0_zz_pw__s10p0` — single PW-addenda fragment hard-failed the StructuredOutput retry cap (5×) on both fresh attempts ([RUN_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md), 06-07 `dah` block) |

## 2. Linguistic vs infrastructural split

The single most important framing decision: **most raw "failures" in this pipeline are
infrastructural, not linguistic**, and they must be excluded from translation-quality
statistics because their outputs are never emitted — a failed call yields a null that is
retried, fragment-split, or held, never a bad translation in the store. The engineering
catalog's unifying model (all StructuredOutput stalls = one disease, excess output
volume, surfacing through whichever driver spikes first — citations, senses, gloss
prose, masked tokens, nesting, batch sums) is orthogonal to translation quality.

Observed infrastructural classes, with real frequencies:

- **StructuredOutput schema-emission stalls** (model emits a bare card instead of the
  `{cards:[…]}` envelope, burns the ~5-attempt retry cap): the H155 `tyaj~~h0_zz_pw`
  ~7-minute stall (35 senses); residually, `dah~~h0_zz_pw__s10p0` — 16/17 fragments
  recovered across two attempts, 1 hard failure, card promoted as a documented 🟡
  partial (residual class: *schema-emission retry-cap*, explicitly NOT the H220
  kill-gate class).
- **Wall-clock kill-gate false kills**: the calibrated gate
  (`KILL_FACTOR=2`, budget `2×(base + 45 ms/skel-byte)`, floor/ceil since recalibrated
  120 s→45 s / 480 s→180 s) was tuned on dense verb-root batches; on single-fragment
  nominal supplement cards it killed **6/6** in the H220 diagnostic — 4 of the 6 killed
  outputs were proven valid post-hoc. Fix (ceiling budget for no-fallback singles) +
  key-echo re-keying took the same 10-card window from 40 % to **10/10 (100 %)**.
- **Key-echo mismatch**: model echoes the clean SLP1 (`CAyA`) instead of the mangled
  sub-card stem (`_c_ay_a~~h0_zz_pw`) — deterministic on underscore-mangled stems,
  harvested as `missing-or-mismatched-key` nulls until the H220 scoped re-keying fix.
- **API outage**: `nominal_w1_100small` pass 1 — 5 ok / 95 null, every batch (even the
  4-card one) failing `Connection closed mid-response`; clean rerun recovered 93/100,
  final 100/100 promoted. Pure network, zero linguistic signal.
- **`{{Lbody=NNNN}}` body-pointer leak** (`_c_ay_a~~h0_zz_pw` in `no_pwg_w1`):
  initially looked like a masking/translation defect, root-caused as a *source-render*
  gap — Cologne alternate-headword pointers (~12,186 PW records) unresolved before
  prompting; fixed upstream in `dict_merge.resolve_lbody()`. Reclassified from
  "mistranslation" to infrastructure.

**What remains linguistic** — untranslated residue, mistranslation, real omission/
addition, terminology — is precisely what the H178 B-1 human-evaluation protocol will
quantify on a stratified sample; the deterministic gates only bound it from above.

## 3. Frequencies over the H178 A-1 re-audit sample — upper bounds, not verdicts

Scope: **65 artifacts / ~2,900 audited cards** (all 48 legacy promoted roots + `dah`,
`nominal_w1_100small`, `no_pwg_w1`), re-audited under the *current* gates in forensic
`--allow-stale --ephemeral` mode. Headline: 46 legacy verb windows show
**464 / 2,148 cards flagged (~22 %)** — a number that would be alarming if read as an
error rate, and decomposes as follows
([H178_REAUDIT_2026-07-06.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_REAUDIT_2026-07-06.md)):

| stratum | count | reading |
|---|---|---|
| Source-render drift | 53 × `COVERAGE-OVER` + 57 × `COVERAGE-LOW` across 52 root-reports | June-generation cards audited against **today's** render (post-PR-183 `{{Lbody}}` resolution, layer-routing changes). E.g. `vas~~h0_zz_pw00`: card 57 senses vs today's render 11 — the *render* moved, the store row set matches the card. Not translation errors |
| Superseded artifacts | 6 keys | flags point at artifacts whose promoted rows come from a later healed run (3 × `gam`, `_ap~~h3_00_pwg00`, `gam~~h0_01_sec_1_0`, `vid` autosplit) |
| Promoted-as-is, low-confidence heuristic flags | **16 keys** | `missing_required_sense_field` / `likely_circular_gloss` / `markup_wrapper_dropped`, all `high_confidence=0` — judge-sample material, not auto-requeue defects (`car~~h0_23_up_a`, `vas~~h0_zz_pw00…03`, `ji~~h3_00_pwg00`, `vid~~h0_10_ni` = the H188 SHA-less legacy rows, …) |
| High-confidence semantic-risk keys | **214** across 52 root-reports | the deterministic ~10 % judge sample the QA policy already routes to the LLM-judge lane |
| Nominal-window misfire | 93/100 + 7/7 keys flagged on `nominal_w1_100small` | reproduced known artifact: no rootmap ⇒ `--allow-stale` ⇒ `missing_required_sense_field` misfires (86 bogus "defects" on pass 2; manual inspection cleared the same keys — legitimately thin *see-under* stubs). **Not defects** |

**All of these are upper bounds pending human verdicts.** The re-audit's own verdict:
no mass re-translation is justified; the actionable residue is to fold the 16 keys +
a slice of the 214 into the B-1 human sample as a deliberate oversample of
suspected-weak cards, converting an untrusted forensic signal into a human-verdict
signal. For calibration, the only human-adjudicated sample so far (S7, 50 RU cards +
68 EN rows) measured **4.0 % unfaithful, CI [1.1, 13.5]** — an order of magnitude
below the raw 22 % flag rate.

## 4. Relation to the B-1 MQM rubric

The category set in §1 deliberately mirrors the deterministic gates so that B-1 MQM
annotation feeds this taxonomy directly rather than requiring a re-mapping pass:
coverage → Omission, sense-dupe / judge-ADDITION → Addition, DE-residue →
Untranslated, NWS owner-map → Terminology/attribution, markup fidelity →
Fluency/formatting, and Mistranslation as the human-only category no gate can see.
Each human verdict therefore lands in exactly one row of the §1 table and either
confirms or retires the corresponding upper bound of §3 — the same
gate-as-silver / human-as-gold design that MQM-based evaluations use to calibrate
automatic metrics (Freitag et al. 2021,
[https://aclanthology.org/2021.tacl-1.87/](https://aclanthology.org/2021.tacl-1.87/)).
The existing Opus-judge rubric
([2_qa_sudya_opus.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/2_qa_sudya_opus.txt))
already buckets its verdicts the same way (A mechanical / B quality / C source-defect
in [REVIEW_QUEUE_TRIAGE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_QUEUE_TRIAGE.md):
13 / 19 / 0 over 217 cards, 185 likely-clean).

## 5. Open error classes

Three classes are detected only heuristically today; each carries a stated confidence
caveat and is expected to be resolved (confirmed or retired) by B-1 human verdicts.

1. **Circular gloss** (`likely_circular_gloss`). Detection: RU gloss that
   substantially repeats the headword or its transliteration instead of translating.
   Confidence: low — one of the three `high_confidence=0` classes behind the 16
   promoted-as-is keys (§3); volume historically small (~21 mixed "other" risks on
   `BU`, ~20 on `sTA`). No confirmed true positive has yet been adjudicated.
2. **Untranslated braced German gloss** (`untranslated_braced_german_gloss`).
   Detection: German-word regex inside `{%…%}` spans of the RU output. Confidence:
   medium — real defects confirmed by the Opus judge (bucket A), but the detector has
   a documented false-positive class: German capitalization makes Latin binomials and
   French/Latin literals look German (the `LATIN_BINOMIAL` / `FRENCH_WORDS` /
   `AMBIGUOUS_DE_FR_WORDS` guard chain in
   [foreign_literal_guards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/foreign_literal_guards.py)
   exists precisely to suppress it), and mixed Latin-German glosses like
   `{%intercedere, ausschliessen von%}` (`gam~~h0_13_antar`) sit on the boundary.
3. **Sense compression** (`possible_sense_compression`). Detection: heuristic
   comparison of source sense-count vs distinct RU renderings (38 keys on `i`, 17 on
   `as`). Confidence: low — confounded with the §3 render-drift class (the same
   sense-count comparison against a moved render), so its true rate is unknown until
   human-verified against the render the card was generated from.

References: Lommel, Uszkoreit & Burchardt 2014, "Multidimensional Quality Metrics
(MQM): A Framework for Declaring and Describing Translation Quality Metrics"
(citation from model knowledge — verify); Freitag et al. 2021, "Experts, Errors, and
Context: A Large-Scale Study of Human Evaluation for Machine Translation", TACL,
[https://aclanthology.org/2021.tacl-1.87/](https://aclanthology.org/2021.tacl-1.87/);
Popović 2018, "Error Classification and Analysis for Machine Translation Quality
Assessment" (citation from model knowledge — verify).

_Dr. Mārcis Gasūns_
