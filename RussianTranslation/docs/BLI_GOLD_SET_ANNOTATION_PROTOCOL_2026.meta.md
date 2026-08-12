# Metadoc — BLI gold-set annotation protocol

_Created: 10-08-2026 · Last updated: 12-08-2026_

Companion to [BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md).

## Purpose

Fix the design of the human-annotated stratified Sa→Ru gold set for ACL roadmap B1, so that
annotation effort is spent once, on a frame whose properties are measured rather than
assumed. It is the design-of-record two consumers read: MG (pass-1 annotation) and
[H2402](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2402-Sonnet_SanskritLexicography_bli-b1-p1-mrr-scorer_07.08.26.md)
(**Sonnet 5**, the P@1/P@5/MRR scorer, whose reporting contract §6 constrains).

## Audience

MG first (the protocol is written to be executable as an annotation task without further
design work), then the scorer implementer, then whoever writes the eventual BLI paper — §8's
limitations are the honest-caveats section of that paper in draft form.

## Provenance

- **Handoff:** [H2401](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2401-Fable_SanskritLexicography_bli-b1-gold-set-design_07.08.26.md) (**Fable 5**) — ACL B1: BLI gold-set design and annotation protocol.
- **Model:** Fable 5 (`claude-fable-5`), Claude Code, 10-08-2026.
- **Predecessor:** [H1521](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1521-Sonnet_RussianTranslation_bli-eval-corpus-lexicon-p1-mrr_23.07.26.md) (Sonnet 5) shipped the automatic 400-lemma baseline + `bli_eval.py`. Not superseded; §1 explains what the new instrument adds.
- **Roadmap home:** [ROADMAP_ACL_LESSONS_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_ACL_LESSONS_2026.md) B1 · [ROADMAP_ACL_ANTHOLOGY_FOOTPRINT_2026_2027.md](https://github.com/gasyoun/Uprava/blob/main/ROADMAP_ACL_ANTHOLOGY_FOOTPRINT_2026_2027.md) row B1/B2.
- **Standing ruling honoured:** model-as-annotator-2, human recruiting parked for 2026 (MG 08-07-2026) — the statistic is human–model agreement.

## What a fresh session would otherwise rediscover by trial and error

1. **The two DCS assets use different key schemes.** `dcs_lemma_summary.json` is SLP1-keyed,
   `dcs_freq_dims.json` is IAST-keyed. Joining Kochergina SLP1 against the IAST file
   directly silently loses ~75% of the overlap (3,534 vs 14,296 hits). This was hit live
   while building the frame, not anticipated.
2. **H1521's coverage of 0.995 is a frame artifact**, not a property of the lexicon. Presence
   falls to 0.00–0.32 in the lowest DCS band. Quoting 99.5% as "the lexicon's coverage" is
   the single most likely misreading of the prior finding.
3. **Kochergina has 711 homograph SLP1 keys** and the lexicon has no homograph index, so a
   pooled gold bag inflates P@1. The frame excludes them; a naive rebuild that pools them
   will report a better and wrong number.
4. **The frame carries no gold column on purpose.** A future session "helpfully" adding
   derived labels converts the dual-annotation design into a rule-based arm and invalidates κ.

## Improvement backlog (ranked)

1. **Polysemy as a real third stratum** — needs a larger budget (~1,000+ rows) so cells stay
   ≥ 20; currently observed-only.
2. **Corpus-weighted headline P@1** — implement the §7 re-weighting in the H2402 scorer so a
   single quotable number exists alongside the per-cell table.
3. **A homograph-aware sense-level variant** — the excluded 711 keys are the natural bridge
   to roadmap B2 (sense attestation / WSD); a sense-indexed gold would measure what BLI
   structurally cannot.
4. **Second gold-content dictionary** — Kochergina's register is one voice; a second
   independent Ru source would let §8's register caveat be measured rather than asserted.
5. ✅ **DONE 12-08-2026** — [H2551](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2551-Sonnet_SanskritLexicography_bli-b1-gold-annotation-sheet-500_10.08.26.md)
   (**Sonnet 5**) shipped [`build_bli_gold_b1_500_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/build_bli_gold_b1_500_sheet.py)
   ([PR #1660](https://github.com/gasyoun/SanskritLexicography/pull/1660), [v1.144.38](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.144.38)) — Russian, 500 class-(d)
   cards via `csl_pyutil.render_review_sheet`. Awaiting MG's vote; row in
   [`Uprava/REVIEW_SHEETS_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md).

## Limitations of this document

It designs and ships the frame; it does not annotate, score, or emit the voting sheet. The
per-cell presence figures are pinned to the frame's seed — regenerating with a different seed
or `--per-cell` changes them, and §7's table must then be regenerated from
`frame_presence_report.py` rather than edited by hand.

## Revision history

| Date | Change | Model |
|---|---|---|
| 10-08-2026 | Created with the protocol (H2401): frame design, homograph exclusion, per-stratum presence tables, scorer contract | Fable 5 (`claude-fable-5`) |
| 12-08-2026 | Backlog item 5 (emit sheet) marked done — [H2551](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2551-Sonnet_SanskritLexicography_bli-b1-gold-annotation-sheet-500_10.08.26.md) shipped the 500-card pass-1 vehicle | Sonnet 5 (`claude-sonnet-5`) |

_Dr. Mārcis Gasūns_
