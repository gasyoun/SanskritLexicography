# pwg_ru methodology review (2026-06-16)

A five-lens expert review of the pwg_ru process against best **Digital Humanities**
and **bilingual ("dual") lexicography** practice. Each lens read the actual repo;
every proposed gap was then *grounded against the code* (REAL / PARTIAL /
ALREADY-DONE / MISTAKEN) so the roadmap proposes only what is genuinely missing.
Lenses: FAIR/DH data · bilingual-lexicography theory · corpus-NLP evaluation ·
standards & interoperability · editorial & print production.

> **Theoretical backbone:** for a Russian-*target* dictionary the native and more
> exacting tradition is the Moscow Semantic School of **Apresjan** —
> see [APRESJAN.md](APRESJAN.md), which grounds recs 4/6/7 in *лексикографический
> портрет*, *лексикографические типы*, *регулярная многозначность*, and
> near-synonym discrimination, and adds three concrete proposals.

## What is already strong (keep it)

- **Lossless masker with a per-card round-trip assertion** ([src/pwg_mask.py](src/pwg_mask.py),
  123,365/123,366; re-asserted in [run_batch.py](src/run_batch.py) and
  [assemble.py](src/assemble.py)); the one lossy `a` record is routed to manual review.
- **Per-sense provenance at emission**: [corpus_gate.py](src/corpus_gate.py) tags every
  gloss with source *and* role (INDEP kochergina/knauer/frish/smirnov vs REF kow vs
  soft corpus); [assemble.py](src/assemble.py) carries source/code/gloss per sense.
- **Deterministic auditor** ([src/_audit.py](src/_audit.py)) checks every known
  corruption mode and caught the 81% placeholder fabrication; the `has_cyr`
  truthiness-≠-translated guard is exemplary.
- **Length-preserving `form_key()`** avoids the NFD-strip trap; matches the sibling
  csl-standards SLP1 idiom.
- **Honest per-signal coverage** on a fixed-seed sample (16.4 / 8.0 / 14–15%), the
  dominant 84% `no-check` surfaced rather than hidden as passes.
- **Real diachronic apparatus**: [build_strata.py](src/build_strata.py) classifies
  154 texts by Renou genre + Dharmamitra date; [corpus_harvest.py](src/corpus_harvest.py)
  surfaces the cited-stratum Russian first.
- **Responsible rights baseline**: modern copyrighted dicts gitignored, PD-vs-modern
  per source; corpus queried in place, not duplicated.
- **Editor-grade QA rubric**: 9 PWG-specific error categories, severity 1–5 with
  anchored calibration, the German-vs-Latin rule, severity≥3 re-translate.

## Prioritized roadmap

### Priority 1 — now (cheap, load-bearing, unblock everything) — ✅ ALL SHIPPED 2026-06-16

1. **Freeze full provenance onto the published card** — ✅ *shipped.* — *FAIR R1.2; W3C PROV-O.*
   The LLM-translated card records no `model_id`, prompt hash, `pwg.txt` commit, or
   timestamp, and never persists the assembled attested senses → it cannot be
   reproduced or bisected. Stamp `model_id`, `prompt_sha`, `pwg_src_commit`,
   `run_id`+`generatedAt`, `schema_version` in [run_batch.py](src/run_batch.py)
   `cmd_collect`, persist the attested senses + the stage-4 verdict; pin a
   SamudraManthanam build id so corpus citations resolve to a fixed corpus version.
   *(effort S)*

2. **Human-review state machine + editor-queue emitter** — ✅ *scaffold shipped
   (`run_batch.py review` → `_review_queue.jsonl`; `review_status` field; κ pool TODO).* —
   *Human-in-the-loop QA; ELEXIS/Lexonomy; Fleiss/Cohen κ.* An LLM verdict cannot be final for a printed
   edition, but the store has no `review_status`/`reviewer`/sign-off and nothing
   emits a worklist. Add the state field (`mt_translated → judged → needs_review →
   human_reviewed → approved`), a `run_batch.py review` mode emitting a sorted
   worklist (severity ≥3 OR divergence OR key-mismatch) with evidence inlined, and
   gate the exporter on `human_reviewed`. Double-key a stratified sample and report κ.
   *(effort M)*

3. **Per-sense rights enforcement + a dataset licence** — ✅ *shipped
   (`corpus_gate.RIGHTS`/`publishable()`; per-sense `publishable` flag in
   `assemble.py`; [DATA_LICENSE.md](DATA_LICENSE.md) = CC BY-SA 4.0).* —
   *FAIR R1.1; Creative Commons; ELEXIS rights-metadata.* [assemble.py](src/assemble.py)/[run_batch.py](src/run_batch.py)
   write modern copyrighted glosses (Kochergina, Smirnov, Frisch) verbatim into the
   card body with no rights filter, and only a software MIT licence exists. Add a
   `publishable` boolean per sense (PD kow/kna → true; modern koch/smirnov/fri →
   false; KOW → attribution-needed); drop/hash non-publishable glosses out of the
   card *body* while keeping them as the correctness signal; add a dataset licence
   (CC BY-SA or CC BY-NC) distinct from MIT. *(effort M — needs a licence decision)*

### Priority 2 — next (the scholarly core)

4. **Held-out human-checked gold set + fix the fidelity probe** — *Och & Ney AER;
   Wilson CIs.* The harvest ships senses with *unmeasured* precision, and the surface-
   overlap probe conflates correct lemmatisation (rājan→царь scored a miss because
   the verse has genitive rājño) with hallucination. Draw a stratified 300–500 sample,
   human-label correct/wrong-sense/hallucinated/lemma-only, report precision + 95%
   Wilson CI, freeze a checked-in gold set; make the probe lemma-aware. *(effort M)*

5. **Gate stratum-preference on real per-stratum coverage** — *corpus
   representativeness (Biber); honest disclosure.* Era-correct Russian is the headline
   feature, yet the lexicon currently covers ~9 of 121 texts (Epic + one AV book; **zero
   Rigvedic rows**), while [build_ls_map.py](src/build_ls_map.py) marks Rigveda/kāvya
   `harvestable` from *membership*, so a Rigvedic sense silently falls back to Epic
   Russian. Report coverage by stratum, label thin strata as fell-back, and assemble no
   Vedic-citation cards for print until those builds land. *(effort M — partly shipped, see below)*

6. **Build the lexicographic microstructure** — *Atkins & Rundell; Zgusta;
   Adamska-Sałaciak; Hausmann marker typology.* [assemble.py](src/assemble.py) emits a
   flat sense-bag; the gate hard-codes `HEAD_SENSE_ONLY`; [pwg_mask.py](src/pwg_mask.py)
   `parse()` drops the `h` homonym number so 6,424 homograph records pool into one card;
   nothing marks translational-equivalent vs explanatory-gloss; strata are used only for
   ordering, never stamped as labels. Parse `div n` into a sense tree, key cards on
   `(key1, h)`, add a per-sense `equivalence_type` + diasystem label (Vedic/Classical/
   domain/register) from the `<ls>` stratum + PWG `ved./ep.` markers. *(effort L)*

7. **Translation-store auditor + cross-card terminology-consistency auditor** —
   *deterministic fail-closed build-gate; controlled-metalanguage enforcement.*
   [_audit.py](src/_audit.py) guards only the corpus lexicon; nothing guards
   `pwg_ru_translated.jsonl`. Add `_audit_translations.py` (no residual German outside
   masked spans; punctuation invariants; no surviving placeholder; Latin/English
   unaltered; unique ords; exit non-zero) and a German-term concordance flagging a
   glossary key rendered more than one way across cards. *(effort M)*

### Priority 3 — later (interoperability & citability)

8. **Export to TEI Lex-0 / OntoLex; make the edition citable and reversible** —
   *TEI Lex-0; OntoLex-Lemon + vartrans + FrAC; CITATION.cff; Zenodo DOI; PROV-O.*
   Output is bespoke gitignored JSONL — no TEI, no OntoLex, no JSON Schema, no PID, no
   reverse (Russian→Sanskrit) index, no edition freeze. The sibling **csl-standards**
   repo already has `export-tei-lex0.mjs` / `export-ontolex.mjs` over the same SLP1
   keys, so this is an adapter + a Russian sense path. Commit a versioned card JSON
   Schema now; add `CITATION.cff`; define an immutable `edition_vN.jsonl` cut; seed a
   reverse index from the pymorphy3 lemmas. *(effort L)*

## Quick wins (small, independent)

- Stamp `model_id`+`prompt_sha`+`pwg_src_commit`+`generatedAt`+`schema_version` in
  `cmd_collect` (rec 1).
- Pin a `canonical_id` + SamudraManthanam build id on corpus citations (rec 1).
- Make the fidelity probe lemma-aware; report true hallucination rate (rec 4).
- **Print a coverage-by-stratum table** — exposes the empty Rigvedic/kāvya strata (rec 5). ✅ *shipped this session — `corpus_harvest.py coverage`.*
- Add a `publishable` boolean per sense in [assemble.py](src/assemble.py) (rec 3).
- Commit a versioned JSON Schema for the assembled card (rec 8).
- Thread the `h` homonym number through [pwg_mask.py](src/pwg_mask.py) `parse()` (rec 6).
- Add a `CITATION.cff` and list pwg_ru/mw_ru in the ROADMAP Zenodo/DOI plan (rec 8).

---
*Method: 5 expert-lens agents + per-gap repo grounding + synthesis (34 agents).
Re-run by editing the workflow and re-invoking. This document is the canonical
to-do; check items off as they land.*
