# Metadoc — WSD gold-set annotation protocol

_Created: 25-08-2026 · Last updated: 25-08-2026_

Companion to [WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md).
Twin of [BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.meta.md).

## Purpose

Fix the design of the token-in-context WSD gold set for ceiling **C1** and capability cards
**4** and **5**, so annotation effort is spent once on a frame whose properties are measured
rather than assumed. It also carries, in §5, the **shared annotator-2 freeze record** that
all three evaluation-spine gold sets (A/B/C, BLI, WSD) must be annotated under — that section
is deliberately cross-cutting and is referenced from the other two sets' documentation.

## Audience

MG first (the protocol is executable as an annotation task without further design work), then
whoever writes the WSD scorer (§6 constrains its reporting), then whoever writes the eventual
paper — §8's limitations are that paper's honest-caveats section in draft.

## Provenance

- **Handoff:** [H3172](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3172-Opus_SanskritLexicography_pwgru-shared-gold-wsd-bli_19.08.26.md) (**Opus 5**) — shared gold sets unblocking WSD (C1) and BLI (cards 1/3).
- **Model:** Opus 5 (`claude-opus-5`), Claude Code, 25-08-2026.
- **Sibling sets, not superseded:** [H1457](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive) shipped the A/B/C slice ([`gold/grade_gold.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/grade_gold.jsonl), 320 rows); [H2401](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2401-Fable_SanskritLexicography_bli-b1-gold-set-design_07.08.26.md)/[H2551](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2551-Sonnet_SanskritLexicography_bli-b1-gold-annotation-sheet-500_10.08.26.md) shipped the BLI frame and its sheet.
- **Emitter it unblocks:** [`src/mfs_baseline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mfs_baseline.py) (H775) — shipped long ago; only its *accuracy number* waited on this.
- **Standing ruling honoured:** model-as-annotator-2, human second-annotator recruiting parked for 2026 (MG 08-07-2026) — the statistic is human–model agreement.

## What a fresh session would otherwise rediscover by trial and error

1. **`distinct sense_tag` is not a sense count, and the error is 10–40×.** The store spans
   five dictionary layers (97 of 254 lemmas straddle more than one), mixes structural
   apparatus (`main`, `intro`, `Nachtrag`) and derived-stem slots (`caus`, `desid`) into the
   tag vocabulary, and stores `1` and `1)` separately. `han` reads as 430 senses naively and
   **11** correctly. This was not anticipated — the first cut of this design was *built* on
   the naive count and had to be discarded. [FINDINGS §583](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
2. **The bimodality that count implies is an artifact.** It makes PWG look like it has an
   unpickable 300–430-sense verb-root tail, which forces a separate free-gloss annotation
   tier — and any shortlist for such a tier can only be built from PWG dictionary order,
   which *is* the MFS baseline's prediction, so the shortlist would bias the gold toward the
   baseline on every row. Correcting the count dissolves the problem instead of solving it.
3. **Cross-layer duplicate subcards produce unanswerable menus** — `[1] раздувание, вздутие`
   vs `[PW] раздувание, вздутие`. Not merely redundant: two annotators pick at random and the
   κ measures coin-flips. A first cut of the frame carried 4 such rows plus 16 with partly
   duplicated options, out of 200.
4. **`token.lemma` is not indexed in `dcs_full.sqlite`** (only `lemma_id` is), so a per-lemma
   `WHERE lemma = ?` full-scans 5.7M rows *each time*; ~250 lemmas that way costs minutes.
   One `GROUP BY` pass, cached, is the fix.
5. **The frame carries no label column on purpose.** A future session "helpfully" adding
   derived labels converts the dual-annotation design into a rule-based arm and invalidates κ.

## Improvement backlog (ranked)

1. **Emit the pass-1 review sheet — for the 48-row pilot, not the 200-row frame.** The BLI set
   has a sheet; this does not. Build it via `csl_pyutil.render_review_sheet` ≥ 0.9.0 with
   `screening=`, `manifest=` and the V11 timer — the legibility hook blocks anything older.
   Size it to the pilot: 48 cards is a sitting, 200 is not, and the timer data from a 48-card
   sheet is exactly what decides whether the remaining 152 are worth building a sheet for.
2. **Widen the lemma base past 48.** The pool is capped by how much of PWG `pwg_ru` has
   translated (254 lemmas). Every further translated polysemous headword widens the frame;
   re-cut with a new seed and re-run the gate.
3. **Nominal coverage.** The frame is VERB 82% because verb roots are what carry ≥2 numbered
   senses in the current store. A nominal-heavy companion frame would let C1 say something
   about Sanskrit rather than about Sanskrit verbs.
4. **Sub-senses (`1a`/`1b`) and derived-stem senses** are excluded by the crisp rule in §2.
   A later, larger set could admit them as a separate labelled axis — derived-stem choice is
   partly *readable* from DCS morphology, so it should be scored separately, never pooled
   into a WSD accuracy.
5. **`m_wordsem` as a silver signal.** 531,747 of 5,688,416 DCS tokens (9.35%) carry a
   numeric `m_wordsem` value. It is not a PWG sense id and was not used here, but the overlap
   with this frame is worth measuring before a larger set is cut.

## Limitations of this document

It designs and ships the frame; it does not annotate, score, or emit the voting sheet. All
counts (48 lemmas, 370,688 candidate tokens, band sizes, the 82% VERB share) are pinned to
the frame's seed and to the current state of the local-only
`pwg_ru_translated.jsonl` — regenerating after more headwords are translated changes them,
and §4/§8 must then be regenerated from `probe_wsd_strata.py` output rather than edited by
hand.

## Revision history

| Date | Change | Model |
|---|---|---|
| 25-08-2026 | Created with the protocol (H3172): sense definition + layer measurement, degenerate-menu exclusion, band design, shared annotator-2 freeze record, scorer contract | Opus 5 (`claude-opus-5`) |
| 25-08-2026 | §5 pilot step added after MG pushed back that 200 rows is too large an ask — measured the real load (1,537 menu options, median 12 in `I10+`) and cut a 48-row one-row-per-lemma instrument check via `pilot_wsd_frame.py`; the 200-row frame is unchanged and the pilot is a strict subset of it | Opus 5 (`claude-opus-5`) |

_Dr. Mārcis Gasūns_
