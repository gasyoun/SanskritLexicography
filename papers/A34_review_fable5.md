# A34 (Register, not just period) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [papers/A34_renou_register_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_renou_register_note.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass in the A10/A33/A36 mold; three parallel `fact-check-against-source` agents (also Fable 5, `claude-fable-5`): coverage/headline claims, cross-axis/§3.5 findings, Renou-structure + link integrity.
**Prior verification:** [A34_corpus_absent_verification.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A34_corpus_absent_verification.md) (headline 484/68.3 % confirmed from committed indices, [PR #115](https://github.com/gasyoun/SanskritLexicography/pull/115)).
**Verdict: MINOR-to-MAJOR REVISION → all agent-doable findings fixed same pass.** The paper's empirical spine is unusually solid — every §3.3/§3.5 figure and all five worked épigraphique examples reproduce from committed TSVs, and all seven Renou-structure claims (p. 94, p. 139, the p. 133 *durci* quote, the five-chapter mapping) verify against the [Renou 1956 TOC transcription](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md) and the OCR'd book. The defects were apparatus-level: no References section, a companion doc contradicting the headline (63.0 % vs 68.3 %), one coverage claim contradicted by the committed system doc, and one unverifiable audit figure.

---

## 1. Figure re-verification

**Confirmed exact (committed artifact → paper):** 770,292 entries / 8 dicts (per-dict sum recomputed); épig 709 rows / 484 empty-state = 68.3 % (from [epigraphic_vocabulary.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/glossaries/epigraphic_vocabulary.md) itself); bhāṣya 14,498 / 10,320 ≥2-dict (recounted); kāvya 26,973; bauddha 25,740; jaina 286 with 0 % corpus-absent; 19/20 registers populated, `hors_inde` = 0; min-support 9.9 % pruned, 0 % of states II/V; §3.3 slices 6,895 / 20,758 / 25,220 (all three TSVs recounted); akṣobhya coordinate; all five épigraphique examples (akṣayanīvī, abhayagirivihāra, ajayavarman, akkādevī, akabara) present and corpus-absent; §3.5 8.8 % / 44.5 % / 92 % (10,511 of 11,454) / 12.4 % / 56.7–65.0 / 10.0–22.2 / nominal-style 14.4→6.7 and 6.25 vs 7.48; the 20-code lattice (`renou_register.py` REGISTERS tuple recounted); all 13 manuscript links resolve.

## 2. Major findings

**M1 — No References section, zero formal citations.** Renou 1956, Edgerton, the dictionaries, DCS — all invoked, none cited; and the obvious comparandum a Lexikos/IJL referee names first — **Sircar's *Indian Epigraphical Glossary* (1966)**, an existing curated inscriptional-Sanskrit glossary — was absent entirely, exposing the épigraphique deliverable to "this already exists." *Fix (applied):* References section (verified works only: Renou 1956, Edgerton 1953, Sircar 1966, Salomon 1998, Vogel 1979, PWG/MW editions, Hellwig DCS, CDSL, companion A08) + a "Relation to prior work" paragraph in §1 positioning the glossary as the citation-derived counterpart of Sircar's corpus-derived one, and §4 wiring the EI/CII validation to that comparison.

**M2 — The companion findings doc contradicts the headline.** [RENOU_FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_FINDINGS.md)'s per-register table prints épig corpus-absent **63.0 %** against the paper's 68 %; the paper's side is the correct one (the committed glossary has exactly 484/709 empty-state rows). A referee following the paper's own §3.5 link hits the contradiction immediately. *Fix (applied):* staleness banner on the table naming the defect, pointing to the verification memo, and instructing "trust the glossaries where they disagree"; full regeneration from `renou_audit.py` queued in the paper's to-do (it needs the gitignored indices — `renou_pipeline.py --all` — so it is a pipeline run, not a text edit; bauddha's 12.4 % re-check flagged in the same item).

**M3 — §3.1's coverage range "19–100 %" was unsourced and contradicted the committed system doc.** [RENOU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU.md) says "~38–41 % of entries carry ≥1 register"; the 19 % per-dict floor exists in no committed file (needs the regenerated indices); only the BHS 100 % endpoint is supported (by construction, all 17,839 entries). *Fix (applied):* restated as aggregate ~38–41 % with the BHS 100 % per-dict endpoint; the unsourced floor dropped.

**M4 — "1.43 M register assignments" is unverifiable from the repo.** The audit report that carries it is gitignored by design. *Fix (applied):* number dropped; sentence now names `renou_audit.py` and states the report regenerates with the indices.

## 3. Minor findings

**m1 — Abstract/§3.2 "68 %" now states its criterion.** Conservative reading (no corpus *or* enriched state) = 484/68.3 %; strict corpus-only = 518/73.1 %. *Fix (applied)* in abstract + table.

**m2 — The abdhi/samudra example was attributed to a companion doc that doesn't contain it.** Data-true (abdhi III·IV in the TSV; samudra I–V) but absent from RENOU_CROSSAXIS.md. *Fix (applied):* example kept with its states inline, no longer implied to be one of the CROSSAXIS worked examples.

**m3 — "≈¼ dictionary-specific" was slice-ambiguous.** True of the born-in-kāvya slice (5,073/20,758 = 24.4 %); the kāvya register overall runs 19.8 %. *Fix (applied):* both numbers stated.

**m4 — §3.5(iv) dropped a load-bearing qualifier.** nāṭya/kāvya are the specificity peaks *among the literary registers* (23.8 %/19.8 %) — epic (21.7 %) sits between them and bauddha (44.5 %) is the overall maximum by a different mechanism. *Fix (applied):* qualifier + the three comparison values inline.

**m5 — Rounded brackets tightened.** 57–65 % → 56.7–65.0 % (upaniṣad is 56.7); 10–22 % → 10.0–22.2 % (kāvya is 22.2). *Fix (applied).*

**m6 — 20-code lattice slightly over-attributed to the TOC doc.** The structure doc's own coding table proposes 14; six more are TOC-derivable but were added in the plan/code. *Fix (applied):* one clarifying clause in §2.

**m7 — 13 relative links upgraded to full blob URLs** per the repo doc contract (all targets resolve; the two VisualDCS URLs were already correct). *Fix (applied);* the verification memo added to §5.

## 4. Data-side notes (no paper change)

- RENOU_FINDINGS.md:50 and RENOU_NOMINAL_STYLE.md:14 spell the Renou section title singular ("Caractère linguistique du bhāṣya") where the TOC transcription and the paper have the plural — fix in the FINDINGS regen pass.
- The §3.3 slice counts are hand-copied into three places (paper, RENOU_CROSSAXIS.md, CHANGELOG) — any glossary regen must touch all three.

## 5. Checked and sound (no action)

- The central claim — register as an orthogonal, provenance-carrying axis that recovers a corpus-invisible stratum — survives scrutiny; the jaina 0 % contrast is verified and does the argumentative work the paper asks of it.
- The Renou philology is faithful: all page placements, the chapter-to-state mapping, and the p. 133 quote splice verify against the TOC transcription and the OCR'd *Histoire*.
- §3.4's "no-op by construction" argument is supported by the committed register-source design (typed sources only).
- Title and framing match the finding. Venue fit: Lexikos/IJL/eLex are all plausible for a register-tagging resource note; the choice stays an MG @DECIDE, not a HOLD.

## 6. Remaining gates

- **Author/MG:** venue @DECIDE (Lexikos vs IJL vs eLex); byline block.
- **Data (agent-doable, pipeline run):** regenerate RENOU_FINDINGS.md's table via `renou_pipeline.py --all` + `renou_audit.py`; re-check bauddha 12.4 % and the singular/plural section title.
- **Human/data:** the EI/CII (or Sircar 1966 proxy) validation sample for the inscription-marker detector's precision/recall — the paper's own named referee-number.

_Dr. Mārcis Gasūns_
