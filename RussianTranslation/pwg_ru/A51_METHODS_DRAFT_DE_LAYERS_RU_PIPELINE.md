# A51 methods draft — the German edition graph and the DE→RU pipeline (honest floors)

_Created: 26-07-2026 · Last updated: 26-07-2026_

Drafted by Fable 5 (`claude-fable-5`) under
[H1633](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1633-Fable_SanskritLexicography_pwg-human-gold-cut-methods-packet_25.07.26.md)
for paper **A51**
([PAPER_LLM_LEXICOGRAPHY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PAPER_LLM_LEXICOGRAPHY.md);
registered in [Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)).
**Status: DRAFT, parked for human sign-off.** Every number is cited from a
committed artifact (linked at first use); cells that await human votes or
unexecuted measurements are written as *pending*, never estimated in place.
The companion sample design is
[gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md).

## §3.1 Source: a five-layer 19th-century dictionary as an edition graph

The source is not a single text but the Petersburg tradition as a layered
object: PWG main text + PWG Nachträge + PW + Schmidt's Nachträge (SCH) +
PWK-derived corrections (PWKVN) + Neuwörterschatz (NWS), merged into one card
per headword with every span labeled by its source layer
([PWG_LAYER_COMBINATIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md);
merge code
[`_pilot_gen_merged.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py)).
Scale of the full source, from the frozen corpus census
([`src/census_stats.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/census_stats.json),
H778): **123,366 PWG entries / 288,991 sense units**; grouped by headword the
frame is **109,050 groups** (H1632,
[PWG_SENSE_DCS_FRAME_COMPARISON.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/PWG_SENSE_DCS_FRAME_COMPARISON.md)).

The digitized text arrives with its own machine-readable markup — Sanskrit
spans `{#…#}` (SLP1), citations `<ls>`, grammar abbreviations `<ab>`, sense
divisions `<div>`, inline glosses `{%…%}` — and the pipeline's first design
commitment is that **this German string is never rewritten**. All enrichment
attaches *beside* it
([EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EDITORIAL_PRINCIPLES_DE_LAYERS_2026-07.md)).

## §3.2 German-side enrichment layers (pre- and para-translation)

Shipped as the H1624 G1–G6 series, each with fixture selftests and a
cross-language parity ledger entry
([LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)):

| Layer | What it adds | Honest floor |
|---|---|---|
| G1 per-span `gloss_lang` (DE/LA/EN) on `{%…%}` | keeps Latin binomials and Wilson's English out of translation | rule-based; rule table published, not exhaustively validated |
| G2 structured government | case-government fields from `(<ab>Instr.</ab>)` etc. | corpus census counts **3,853 markers** ([RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md), 12-07-2026) — a *floor*: only explicitly marked government, not all valency |
| G3 normalized `<ls>` citation graph | machine edges to cited works (41,031 citations in the current store rollup) | resolver coverage partial; orphans reported, scan-page links out of scope (N15) |
| G4 `edition_rel` flags | supplement senses typed (restate / derived / correction …) | machine classes only; display-name votes pending (H180 sheets) |
| G6 compound/derivation portrait | split + derivation path per lemma | **4,226 of 39,539 (10.69%) layer conflicts flagged `needs_human`**, not auto-adjudicated (N11) |

G5 of that series (doublet / *v. l.* / *im Comp.* span tags) is
**human-gated** — it waits for the H1306 style vote and is *pending*, not
partially applied.

## §3.3 The DE→RU pipeline

Per card: (1) deterministic **masking** — Sanskrit, citations, and grammar
abbreviations become `{Tn}` placeholders so the model sees German prose only
([`pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py));
(2) **generation** by Sonnet 5 (`claude-sonnet-5`) through a manifest-driven
headless harness with translation-memory reuse; (3) **deterministic gates on
100% of cards** — placeholder integrity, sense coverage, sense-duplication,
NWS owner-map, German-residue detection
([`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py));
(4) **LLM judging on the gated residue**: Sonnet judges every card, Opus
re-judges rejects. The judge A/B on 474 real cards found κ=1.0 on
accept/reject with a ~0.5% disagreement rate, and on a 250-card
planted-defect ground-truth test both judges reached 99% recall at 0% false
positives ([JUDGE_POLICY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/JUDGE_POLICY.md)).
**These are LLM×LLM agreement figures — they calibrate the judging
machinery, they do not validate translation quality.** Machine-flagged cards
never reach a human print vote: they are auto-rejected into a repair queue
(P1 ruling, 26-07-2026), so all human effort lands on the machine-clean pool.

Every store row carries model version, pipeline stage stamps, and content
hashes; the store itself stays unpublished pending rights clearance (N9), so
the paper's data availability statement points at the committed
methodology + metadata, not the text.

## §3.4 Evaluation design — measured, pending, and refused claims

The evaluation stack keeps three channels apart by construction and labels
every figure with its channel:

1. **Deterministic gates** (100% coverage) — structural fidelity only; a
   green gate is *not* a semantic verdict (gate ≠ gold).
2. **LLM-judged estimates** — the harvest-alignment gold scaffold reports
   84.4% precision (95% CI 80.0–87.9, n=320, stratified period×kind;
   [gold/precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md)),
   and it measures the **Sa→Ru harvest layer, not the DE→RU store**; it is
   flagged LLM-estimated wherever cited. The A/B/C grade gold is
   agent-adjudicated and PRELIMINARY
   ([gold/GRADE_GOLD_MEMO.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/GRADE_GOLD_MEMO.md));
   its near-zero κ against a surface-shape proxy is reported as evidence the
   *proxy* is inadequate — the standing lesson against relabeling channels.
3. **Human measurements** — (a) the four-rubric protocol bake-off (MQM ·
   Likert · DA · pairwise) on a shared 30-item held-out sample, *pending MG
   votes*
   ([EVALUATION_PROTOCOL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EVALUATION_PROTOCOL.md));
   (b) the store gold cut — stratified n≈400 from the machine-clean pool,
   typed six-label annotation, tiered agreement plan (inter-rater κ only if a
   second reviewer is staffed in 2026; otherwise intra-rater test–retest,
   explicitly labeled) — *designed, awaiting sign-off*
   ([gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/STORE_DE_RU_GOLD_CUT_SAMPLE_FRAME.md)).
   COMETKiwi remains a triangulation aid, unvalidated on 19th-century
   scholarly German → Russian dictionary glosses, and is blocked on a
   one-time license step.

Corpus-grounding honesty, adopted from H1632: **39.8%** of the 109,050 PWG
headword groups have a DCS lemma attestation (so 60.2% have none at any
granularity); sense-level attestation carries a ~11% corpus-property ceiling;
and grounding that was never computed is reported as *unknown*, never as
zero.

## §3.5 What this paper does not claim

- No human-validated precision for the DE→RU store *until the gold cut is
  executed* — the LLM-estimated figures are labeled as such in every table.
- No "AI outperforms the human tradition" claim (N13): that requires an
  adjudicated comparative design that does not exist.
- No quality claim for gate-rejected rows (they are in repair, not in the
  print pool), and no whole-dictionary claim while the drain is partial
  (store 11,603 sense rows as of 24-07-2026 vs 288,991 source sense units).
- No inter-annotator agreement figure of any kind exists yet; none is
  projected.

## Claims register — what remains human-gated before submission

| # | Claim the paper wants | Blocking gate / artifact | Register |
|---|---|---|---|
| C1 | human-measured store precision + CI | gold cut execution (sign-off §8 of the frame) → labels → report | N3 |
| C2 | inter- (or intra-)rater agreement | second-reviewer staffing decision; else test–retest pass | N3/N13 |
| C3 | chosen human-eval protocol + bake-off table | 4 × `decisions.json` from the h178 sheets (MG votes) | — |
| C4 | COMETKiwi correlation column | one-time HF license/token + `comet` run | — |
| C5 | abbreviation canon in rendered examples | [H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md) vote | N1 |
| C6 | doublet / *v. l.* / *im Comp.* handling as policy | [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md) decisions.json | N2 |
| C7 | any print-edition statement | G5 votes at release-slice scale + G6/G7 + G10 | N3 |
| C8 | compound-split layer as adjudicated | ~4.2k `differs` review-sheet sample | N11 |
| C9 | public data release / TM download | rights clearance | N9 |
| C10 | "quarantine ≈ bad RU" side-claim | ~200-row sample of the glyph quarantine | N18 |

Everything in the register is a human vote, a staffing decision, or an
unexecuted measurement — none of it is drafting work, which is why this
methods draft can be complete while every one of these cells stays open.

_Dr. Mārcis Gasūns_
