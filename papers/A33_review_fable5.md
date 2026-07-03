# A33 (Genetic, Not Historical — Sense Ordering) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [papers/A33_sense_ordering_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass per H123 (Fable window S14), in the A01/A03–A06 mold.
**Verdict: MINOR REVISION** — every figure re-verified exact against the committed metrics; the note is compact, honest, and its headline claim is well-calibrated. The gaps are apparatus: **no References section at all**, no related-work positioning, the Renou classification uncited, and relative links. All agent-doable findings applied in this pass; venue stays an MG `@DECIDE`.

---

> **Correction (same day, second pass).** §1 below verified the paper against the metrics
> docs *as first committed* (the 2026-06-24 run). A parallel session's data pass
> ([PR #103](https://github.com/gasyoun/SanskritLexicography/pull/103)) had already found
> that the committed scripts' `)`-only sense-delimiter regex never reproduced those
> figures as committed, fixed it (`[)〉]`), and re-ran on the current source: **every rate
> reproduces exactly** (73.5 % / τ 0.375 / density 23.4 %) but the **entry counts moved**
> (13,900 → 11,882 multi-sense entries; 118,528 → 113,012 cited senses; strict-chrono
> 26.2 → 25.4 %; adjacent 76.3 → 76.8 %), and a chance floor was added (sense-1-oldest
> 52.7 %, τ ≈ 0). The paper's PWG figures were re-synced to the reproducible values and
> the floor calibration added in the follow-up PR; the MW column awaits a same-snapshot
> re-run. §1's "all exact" therefore holds for the rates and the June-state docs, not the
> current-source Ns.

## 1. Figure re-verification — all CONFIRMED (against the 2026-06-24-state docs; see correction above)

Against [`sense_order_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sense_order_metrics.md) and [`cross_dict_metrics.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/cross_dict_metrics.md) (generators [`analyze_sense_order.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_sense_order.py), [`analyze_cross_dict.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/analyze_cross_dict.py)):

- §3.1 table, both columns: 13,900 / 13,825 entries; sense-1-oldest **73.5 % / 69.4 %**; Kendall τ **0.375 / 0.367**; within-sense strict chronology 26.2 % / 55.0 %; adjacent non-decreasing pairs 76.3 % / 67.6 % — all exact.
- §2 coverage: 772,567 PWG `<ls>` citation-keys, 559,243 dated = **72.4 %** — exact, including the catalogue-dominated unrecognised tail claim.
- §3.3 densities and bases: PWG 23.4 % (118,528) / MW 24.8 % (99,726) / AP90 2.3 % (19,163) / Kochergina 0.0 % (29,177 records, 5 dated citations) — all exact.
- §4's "~26.5 % of lead senses would change" = 100 − 73.5, consistent.
- The metrics doc's independent convergence check (71.9 % on a validation slice vs the 73.5 % corpus rate) further supports the headline; the paper correctly does not over-claim it.

## 2. Major findings

**M1 — No References section.** The note cites prefaces (PWG, Grassmann, MW), a classification (Renou's language states I–V), and a received handbook view — with no bibliography whatsoever. For Lexikos/IJL/eLex this is a desk-reject. *Fix (applied):* References section added — primary dictionaries (PWG/PW, MW, GRA, AP90, Kochergina 1978/1987), **Renou 1956** (the language-state classification the whole dating method rides on — the most consequential missing citation), and the secondary apparatus below.

**M2 — No related-work positioning.** The received "historical ordering" view is asserted but never anchored, and the classical sense-arrangement typology the paper is actually testing (historical vs logical vs frequency ordering) has standard statements. *Fix (applied):* a related-work paragraph added at the end of §1, positioning against Zgusta 1971 (the classical typology of sense arrangement), Atkins & Rundell 2008 (modern practice: frequency/salience-first), Hausmann & Wiegand 1989 (microstructure theory), Vogel 1979 (Sanskrit lexicographic tradition), and Zgusta 1988 / Hanneder 2020 (the PWG→MW dependence that makes the two dictionaries' near-identical ordering behaviour expected rather than surprising). **Note:** the FABLE index's suggested comparanda (Zaïane 2008, Cysouw 2013, Pereltsvaig 2019) could not be verified as real, on-topic sense-ordering literature and were **not** cited — if specific works were meant, that is an author call; citing unverifiable items is exactly what this review exists to prevent.

**M3 — Anti-salami: the A33 ↔ A02 ↔ A06 ordering cluster is unacknowledged.** ARTICLES.md pre-assigns the sense-ordering question across A33 (this note), csl-atlas A02 (sense inheritance) and A06 (kośa macrostructure/order); none is mentioned. *Fix (applied):* a companion note added to §5 — A02 owns sense *survival* along inheritance edges, A06 owns *macrostructural* (concept-order) arrangement, this note owns *within-entry sense order vs attestation date*; cross-cite, don't re-derive.

## 3. Minor findings

**m1 — Relative links** in §5 (`../RussianTranslation/research/…`) break outside the repo blob view. *Fix (applied):* full blob URLs.

**m2 — §2 numbering slip:** "compute (1) whether the first printed sense is the oldest-attested, and the Kendall τ …; (3) whether the citations *inside* a sense run oldest→newest" — item (2) is missing. *Fix (applied):* renumbered (1)/(2)/(3).

**m3 — Kochergina's dates.** "1978/87" appears once, References now state the editions properly (2nd ed. 1987). Kept as author-verifiable.

## 4. Not fixed (stays with the author / future work)

- **Venue** (Lexikos vs IJL vs eLex) — MG `@DECIDE`, now a GTD row; length trim follows the venue.
- **AP90 Vedic-siglum recall hand-check** and the **GRA/PW control columns** — genuine data work, honestly listed in the paper's own to-do; not blockers for 4/5.

## 5. Checked and sound (no action)

- The central calibration move — 73.5 % is "high but far from the ~100 % a true historical sort would give" — is exactly right and mirrors the series' floor/ceiling discipline.
- §3.2 (the śāstra pocket) is a genuine referee-proofing asset: it concedes the counter-case before a reviewer raises it.
- §4's digital-edition consequence is the note's practical payload and follows from the measurement without over-reach; the "optional view, not imposed" recommendation is well-argued.
- The MW granularity caveat (55 % strict chronology as an artefact of short records) is the right defensive footnote.

_Dr. Mārcis Gasūns_
