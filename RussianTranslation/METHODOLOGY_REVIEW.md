# pwg_ru methodology review (2026-06-16)

_Created: 07-07-2026 · Last updated: 10-07-2026_

> **Status refreshed 10-07-2026** (H455) against the code on `origin/master`.
> Priority 3 has substantially landed since this review was written; Priority 2
> is split — the gold-set scaffold shipped, human labelling and the
> lexicographic microstructure are still open. Each recommendation now carries a
> verified marker.

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
- **Responsible rights baseline**: extracted source data remains gitignored;
  modern Sanskrit-Russian sources now have project approvals for publication use,
  with attribution/provenance retained per source; corpus queried in place, not
  duplicated.
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

3. **Per-sense rights/provenance metadata + dataset licence** — ✅ *updated
   (`corpus_gate.RIGHTS`/`publishable()`; per-sense `publishable` flag in
   `assemble.py`; [DATA_LICENSE.md](DATA_LICENSE.md) = CC BY-SA 4.0; approvals
   recorded in [RIGHTS_APPROVALS.md](RIGHTS_APPROVALS.md)).* —
   *FAIR R1.1; Creative Commons; ELEXIS rights-metadata.* The earlier
   evidence-only restriction for modern sources is no longer needed: project
   approvals cover extensive use of Kochergina, Smirnov, and Frisch in the
   publishable card body. Keep source attribution and provenance; do **not**
   strip/hash approved modern-source text merely because it is modern.

### Priority 2 — next (the scholarly core)

4. **Held-out human-checked gold set + fix the fidelity probe** — 🟡 *PARTIAL:
   the stratified n=320 sample is frozen ([gold/gold_set.jsonl](gold/gold_set.jsonl)) and
   precision is reported with a Wilson CI (84.4%, 95% CI 80.0–87.9,
   [gold/precision_report.md](gold/precision_report.md)) — but the labels are **LLM-judged**,
   not human. [gold/HUMAN_GOLD_PROTOCOL.md](gold/HUMAN_GOLD_PROTOCOL.md) is the written,
   un-executed human pass; until it runs, the number must not be cited as print-grade
   precision. The κ figure additionally needs a second annotator, which is deferred
   through 2026.* — *Och & Ney AER; Wilson CIs.* The harvest ships senses with *unmeasured* precision, and the surface-
   overlap probe conflates correct lemmatisation (rājan→царь scored a miss because
   the verse has genitive rājño) with hallucination. Draw a stratified 300–500 sample,
   human-label correct/wrong-sense/hallucinated/lemma-only, report precision + 95%
   Wilson CI, freeze a checked-in gold set; make the probe lemma-aware. *(effort M)*

5. **Gate stratum-preference on real per-stratum coverage** — 🟡 *PARTIAL: the
   coverage-by-stratum report shipped (`corpus_harvest.py coverage`), but nothing in
   [src/corpus_harvest.py](src/corpus_harvest.py) labels a thin stratum as **fell-back**,
   so a Rigvedic sense still silently inherits Epic Russian. The disclosure exists; the
   gate does not.* — *corpus
   representativeness (Biber); honest disclosure.* Era-correct Russian is the headline
   feature, yet the lexicon currently covers ~9 of 121 texts (Epic + one AV book; **zero
   Rigvedic rows**), while [build_ls_map.py](src/build_ls_map.py) marks Rigveda/kāvya
   `harvestable` from *membership*, so a Rigvedic sense silently falls back to Epic
   Russian. Report coverage by stratum, label thin strata as fell-back, and assemble no
   Vedic-citation cards for print until those builds land. *(effort M — partly shipped, see below)*

6. **Build the lexicographic microstructure** — 🔴 *OPEN — the largest remaining gap
   between this pipeline and a publishable scholarly edition. Verified 10-07-2026:
   `HEAD_SENSE_ONLY = True` is still hard-coded at [src/corpus_gate.py:40](src/corpus_gate.py),
   and the `h` homonym number is still not threaded through [src/pwg_mask.py](src/pwg_mask.py)
   `parse()`, so 6,424 homograph records continue to pool into one card.* —
   *Atkins & Rundell; Zgusta;
   Adamska-Sałaciak; Hausmann marker typology.* [assemble.py](src/assemble.py) emits a
   flat sense-bag; the gate hard-codes `HEAD_SENSE_ONLY`; [pwg_mask.py](src/pwg_mask.py)
   `parse()` drops the `h` homonym number so 6,424 homograph records pool into one card;
   nothing marks translational-equivalent vs explanatory-gloss; strata are used only for
   ordering, never stamped as labels. Parse `div n` into a sense tree, key cards on
   `(key1, h)`, add a per-sense `equivalence_type` + diasystem label (Vedic/Classical/
   domain/register) from the `<ls>` stratum + PWG `ved./ep.` markers. *(effort L)*

7. **Translation-store auditor + cross-card terminology-consistency auditor** — 🟡
   *PARTIAL: [src/audit_translation.py](src/audit_translation.py) and
   [src/audit_translation_provenance.py](src/audit_translation_provenance.py) now guard the
   translation store. The **cross-card German-term concordance** — flagging a glossary key
   rendered more than one way across cards — has no implementation.* —
   *deterministic fail-closed build-gate; controlled-metalanguage enforcement.*
   [_audit.py](src/_audit.py) guards only the corpus lexicon; nothing guards
   `pwg_ru_translated.jsonl`. Add `_audit_translations.py` (no residual German outside
   masked spans; punctuation invariants; no surviving placeholder; Latin/English
   unaltered; unique ords; exit non-zero) and a German-term concordance flagging a
   glossary key rendered more than one way across cards. *(effort M)*

### Priority 3 — later (interoperability & citability) — 🟢 SUBSTANTIALLY SHIPPED

8. **Export to TEI Lex-0 / OntoLex; make the edition citable and reversible** — 🟢
   *SHIPPED, verified 10-07-2026.* The original text below described a state that no
   longer holds. What exists now: TEI Lex-0 export
   ([src/export_interop.py](src/export_interop.py) → `tei_lex0.xml`), OntoLex-Lemon
   ([release/ontolex.ttl](release/ontolex.ttl), 726k lines) with a SHACL
   [release/shapes.ttl](release/shapes.ttl), three versioned JSON Schemas under
   [schemas/](schemas/), a Russian→Sanskrit [release/reverse_index.jsonl](release/reverse_index.jsonl),
   an immutable edition cut ([src/make_edition_cut.py](src/make_edition_cut.py)), and a
   [CITATION.cff](CITATION.cff) — corrected under H455 to `CC-BY-SA-4.0` (matching
   [DATA_LICENSE.md](DATA_LICENSE.md)) with the ORCID byline. **Remaining:** the Zenodo
   DOI itself is unregistered and `CITATION.cff` stays at `version: unreleased` until the
   archival upload happens — see [DOI_PLAN.md](DOI_PLAN.md).
   *— TEI Lex-0; OntoLex-Lemon + vartrans + FrAC; CITATION.cff; Zenodo DOI; PROV-O.*

   > *Original 2026-06-16 text, kept for the record:* Output is bespoke gitignored
   > JSONL — no TEI, no OntoLex, no JSON Schema, no PID, no reverse (Russian→Sanskrit)
   > index, no edition freeze. The sibling **csl-standards** repo already has
   > `export-tei-lex0.mjs` / `export-ontolex.mjs` over the same SLP1 keys, so this is an
   > adapter + a Russian sense path. *(effort L)*

## Quick wins (small, independent)

- Stamp `model_id`+`prompt_sha`+`pwg_src_commit`+`generatedAt`+`schema_version` in
  `cmd_collect` (rec 1).
- Pin a `canonical_id` + SamudraManthanam build id on corpus citations (rec 1).
- Make the fidelity probe lemma-aware; report true hallucination rate (rec 4).
- **Print a coverage-by-stratum table** — exposes the empty Rigvedic/kāvya strata (rec 5). ✅ *shipped this session — `corpus_harvest.py coverage`.*
- Keep `publishable`/rights metadata per sense, with approved modern sources
  marked publishable and cited by source (rec 3).
- Commit a versioned JSON Schema for the assembled card (rec 8). ✅ *shipped — [schemas/](schemas/).*
- Thread the `h` homonym number through [pwg_mask.py](src/pwg_mask.py) `parse()` (rec 6). 🔴 *still open.*
- Add a `CITATION.cff` and list pwg_ru/mw_ru in the ROADMAP Zenodo/DOI plan (rec 8). ✅ *shipped; DOI registration still pending.*

---
*Method: 5 expert-lens agents + per-gap repo grounding + synthesis (34 agents).
Re-run by editing the workflow and re-invoking. This document is the canonical
to-do; check items off as they land.*

*Status markers refreshed 10-07-2026 under H455 by Opus 4.8 (`claude-opus-4-8`),
each verified against the code on `origin/master` rather than assumed.*

_Dr. Mārcis Gasūns_
