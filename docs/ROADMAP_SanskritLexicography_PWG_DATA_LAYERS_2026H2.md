_Created: 19-07-2026 · Last updated: 29-07-2026_

# ROADMAP — PWG data layers 2026 H2

Cover: [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md).

Wave 1 is the whole unattended run, internally ordered so each step de-risks the next and the earliest steps need no gates. Waves 2–3 are human-gated follow-ons that this run only *stages*, never ships.

## Wave 1 — the unattended run (deterministic-first, one bounded LLM check)

Ordered; each step states what unblocks it. Full file-level steps in [IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md).

| # | Deliverable | Unblocked by | Gate |
|---|-------------|--------------|------|
| W1.1 | **Canonical anatomy reference** — [`docs/PWG_CARD_ANATOMY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PWG_CARD_ANATOMY.md): index + measured crosswalk over the 24-element pedagogical list, the parse-rules tag census, and the microstructure portrait. | nothing (opener) | none |
| W1.2 | **RelaxNG grammar** `schemas/pwg_markup.rnc` over raw `<L>…<LEND>`, + validator run over all 123,366 records → typed failure catalogue `reports/pwg_markup_validation.json`. | W1.1 (element inventory) | none |
| W1.3 | **JSON Schema** extension over the parsed portrait + validator run → `reports/pwg_portrait_validation.json`. | W1.2 (shared tag vocabulary) | none |
| W1.4 | **`〉` full measure + quarantine** — re-segment all records with the corrected splitter, measure RU-store contamination, write `reports/pwg_sense_glyph_audit.json` + a **separate** quarantine marker `reports/pwg_ru_glyph_quarantine.jsonl` (store untouched). | W1.3 (portrait sense tree) | none |
| W1.5 | **LLM sanity check** — ≤50-card DeepSeek spot-check of the `〉` re-segmentation vs human judgement (`--backend openai`, no Anthropic key). Skippable on no-backend. | W1.4 | bounded, isolated |
| W1.6 | **Citation layer** — extend `ls_source_map` + `pwgbib` resolver; recompute `<ls>` recognition; target ≥85%. | W1.1 | none |
| W1.7 | **Sense / xref / government layers** — extend `senses_pwg.jsonl`, `xref_edges.csv` (resolve `s.`/`vgl.` where deterministic), government index. | W1.4, W1.6 | none |
| W1.8 | **OntoLex rollup** — attach W1.4/W1.6/W1.7 as new properties on `entry/<key1>/de`; regenerate `pwg_de_lexicon.ttl` via `export_lod.py`. | W1.6, W1.7 | none |
| W1.9 | **Defect staging** — turn the RNG/portrait/`〉` failure buckets + OCR hits into **csl-corrections change files** (no csl-orig PR). | W1.2, W1.3, W1.4 | staged only |
| W1.10 | **Hub sync + release** — FINDINGS/PROJECT_INTERLINKS/SHARED_CODE rows, CHANGELOG entry, `/cut-release`, GTD `@DECIDE` rows for the staged defects. | all above | none |

## Wave 2 — human-gated upstream (staged by W1.9, shipped later by MG)

- MG reviews the staged csl-corrections change files, runs [/cologne-batch-pr](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md) → one consolidated PR to csl-orig at most ~monthly.
- Sense-segmentation disagreements (an editorial claim about Böhtlingk, higher evidence bar) get a separate review sheet before any are proposed.

**Gate — three open `@DECIDE`s block Wave-2 execution** (filed from the 20-07-2026 Wave-1 pass
in [Uprava GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md);
restated here so this roadmap is self-contained and does not require cross-referencing
`.ai_state.md`/GTD):

1. **RU-store quarantine — re-translate or not.** W1.4 quarantined the `〉`-contaminated RU
   cards into a side marker (`reports/pwg_ru_glyph_quarantine.jsonl`) without touching the RU
   store itself. A human must rule whether those quarantined cards get re-translated against
   the corrected `〉` segmentation (this is also the trigger condition for Wave 3) or left as-is
   with the contamination flagged in place.
2. **`senses_pwg.jsonl` full-corpus build scope.** W1.7 extended `senses_pwg.jsonl` only over
   the data Wave 1 touched; a human must decide whether Wave 2 commits to a full-corpus
   `senses_pwg.jsonl` build (all 123,366 PWG records) versus staying scoped to the subset
   already covered.
3. **The untraceable "12 PWG typos" list.** A previously-cited count of "12 PWG typos" cannot be
   traced back to a concrete, itemized source list; a human must rule whether to (a) re-derive
   the list from the current typo-candidate pool, (b) treat the number as stale and drop it, or
   (c) accept it unverified for Wave-2 planning purposes.

Until all three are ruled, Wave-2 candidates (4)/(5) in
[PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md)
— the `〉` glyph-tier xref/OntoLex follow-ons and the DeepSeek sanity-check fix — can be staged
but not shipped.

## Wave 3 — requeue the `〉`-contaminated RU cards (budget-gated)

- Regenerate the quarantined RU rows against the corrected segmentation. Deferred out of this run because requeue burns generation budget and must not collide with the paused nominal lane / H1209 canary. Triggered only after the Wave-1 contamination number is known and a budget is authorized.

## Non-goals (explicit)

- **No edit, commit, or PR to `csl-orig`.** Ever.
- **No rewrite of the RU store**; the `〉` audit only quarantines via a side file.
- **No LLM resolution of citations or synthesised sources** — deterministic resolver only.
- **No launch of the paused nominal/promote/requeue lanes.**
- **No rewrite of the three existing anatomy docs** — the new reference indexes them.
- **No requeue of contaminated cards in this run** (that is Wave 3).

_Dr. Mārcis Gasūns_
