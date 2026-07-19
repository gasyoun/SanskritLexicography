_Created: 19-07-2026 · Last updated: 19-07-2026_

# IMPLEMENTATION — PWG data layers (wave-1, file-level, step-ordered)

Cover: [PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md). Architecture: [ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md).

**Setup (do first).** Work in a fresh worktree off `origin/master`: `git worktree add -b feat/pwg-data-layers ../SanskritLexicography-pwg-dl origin/master`. All Python scripts open outputs `encoding='utf-8'`, call `sys.stdout/stderr.reconfigure(encoding='utf-8')`, write no BOM, and are saved as `.py` files (never inline). Every step commits `ai-wip:` on completion.

---

### Step 1 — W1.1 canonical anatomy reference (no dependencies)

- **Read** the three sources (architecture §1). **Write** `docs/PWG_CARD_ANATOMY.md`: for each of the 24 pedagogical elements, a row giving `{element, pedagogical?, parse-rules tag+count?, portrait field?, divergence note}`.
- **Derive the coverage matrix** with a throwaway script `RussianTranslation/src/build_anatomy_crosswalk.py` that reads `csl-atlas/data/parse-rules/pwg.json` (counts) and the portrait schema (fields) and emits the matrix as a markdown table to stdout; paste into the doc. Do **not** re-parse pwg.txt for counts — read the measured census.
- **Acceptance:** every tag in `pwg.json` appears in the matrix with its count; every one of the 24 elements is mapped or explicitly marked "pedagogical-only".

### Step 2 — W1.2 RelaxNG grammar + validation run

- **Write** `RussianTranslation/schemas/pwg_markup.rnc` — a RelaxNG compact grammar for the `<L>…<LEND>` tag language (element inventory from Step 1). Model the paired spans (`<ls> <ab> <is> <lex> <lang> {#…#} {%…%}`), the record header (`<L>/<pc>/<k1>/<k2>/<h>`), and the `〉` sense-close.
- **Write** `RussianTranslation/src/validate_pwg_markup.py`: for each of the 123,366 records, attempt validation; on failure, classify into a typed bucket (`malformed-span`, `unknown-tag`, `glyph-class`, `unbalanced-delim`, `unexpected-but-attested`). Emit `RussianTranslation/reports/pwg_markup_validation.json`.
- **Guard (FINDINGS §129/§130):** no record is silently dropped — every record is `pass` or lands in exactly one bucket. Assert `sum(buckets)+passes == 123366`.
- **Acceptance:** the assert holds; zero `unclassified`. See [VERIFICATION](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_DATA_LAYERS.md) V2.

### Step 3 — W1.3 JSON Schema over the portrait

- **Extend** `RussianTranslation/schemas/pwg_ru_lexicographic_portrait.schema.json` (or add `pwg_portrait_structural.schema.json`) to cover the full sense tree + apparatus, not just the RU fields.
- **Write** `RussianTranslation/src/validate_pwg_portrait.py` running `microstructure.py` over all records → validate → emit `reports/pwg_portrait_validation.json` (same bucket discipline).
- **Acceptance:** 100% parse-or-bucket; the schema is referenced by the existing `validate_portrait_schema.py` harness.

### Step 4 — W1.4 `〉` full measure + quarantine (store untouched)

- **Write** `RussianTranslation/src/audit_sense_glyph.py`:
  1. re-segment all 123,366 records with the **corrected** splitter that recognises `〉` (the FINDINGS §447 fix; verify it matches the first-2500 audit in `_audit_micro.py`);
  2. for each record, count senses under the old (merged) vs corrected segmentation;
  3. join to the RU store **read-only** (`pwg_ru_translated.jsonl`) to find rows whose `senseId` was produced against merged segmentation;
  4. emit `reports/pwg_sense_glyph_audit.json` (totals + per-record deltas) and `reports/pwg_ru_glyph_quarantine.jsonl` (one row per contaminated store row).
- **Fence:** open the store `'r'` only. Never write `pwg_ru_translated.jsonl` or a rebuilt sibling (FINDINGS §9). Quarantine is the side file alone.
- **Acceptance:** the audit reports a single contamination number with a CI, and the quarantine file's row count equals the audit's contaminated-row total.

### Step 5 — W1.5 bounded LLM sanity check (skippable)

- **Write** `RussianTranslation/src/sanity_glyph_resegment.py`: stratified ≤50-card sample; ask DeepSeek (`--backend openai`, **no Anthropic key**) whether the corrected segmentation reads correctly vs the German. Emit a small verdict JSON + a one-line agreement rate.
- **On no backend / network:** log "sanity check skipped — no backend" to `.ai_state.md` Dev Notes and continue (stop condition (b), not a halt).
- **Acceptance:** either an agreement rate is reported, or the skip is logged. Never blocks.

### Step 6 — W1.6 citation coverage extension

- **Write** `RussianTranslation/src/extend_ls_coverage.py`: collect the currently-unrecognised `<ls>` tail; match against `pwg_sources.py`'s `pwgbib.txt` + the Verzeichniss patterns; add new patterns to `ls_source_map.json` (or a sidecar `ls_source_map_ext.json`). Recompute recognition rate.
- **No LLM, no synthesised sources** (D8). Unresolvable tail → `reports/pwg_ls_unresolved.tsv` as a typed gap for a human bibliographer.
- **Acceptance:** recognition ≥85% OR a written explanation of why the ceiling is lower, with the unresolved tail catalogued. (Baseline 72.4%, FINDINGS §20.)

### Step 7 — W1.7 sense / xref / government layers

- **Senses:** extend `csl-atlas/data/lexico/senses_pwg.jsonl` with the corrected segmentation from Step 4 (via a csl-atlas worktree — R4).
- **Xrefs:** `RussianTranslation/src/resolve_xrefs.py` — resolve `s.`/`vgl.` redirects where the target `key1` is deterministically identifiable; emit `{src,type,tgt,resolved}` to extend `xref_edges.csv`. Unresolved stay `resolved:false` (never guessed).
- **Government:** extend the H1308 index with any senses the corrected segmentation newly exposes.
- **Acceptance:** each layer's row count and resolved-fraction reported; no fabricated targets.

### Step 8 — W1.8 OntoLex rollup

- **Extend** `RussianTranslation/src/export_lod.py de-lexicon` to attach citations (W1.6), corrected senses (W1.4), xref edges (W1.7), and government (W1.7) as new properties on `entry/<key1>/de`. Regenerate `release/fixture/pwg_de_lexicon.ttl`.
- **Fence:** additive only — the German lemma/text nodes are never altered, only new sibling properties added.
- **Acceptance:** the TTL parses (rdflib), node count grows by the expected layer cardinality, and a spot query for a known headword (e.g. `agni`) returns the new properties. See VERIFICATION V8.

### Step 9 — W1.9 defect staging (csl-corrections only)

- **Write** `RussianTranslation/src/stage_pwg_defects.py`: read the failure buckets from Steps 2/3/4 + the 12 PWG SanskritSpellCheck typos; emit **change files** in the csl-corrections change-file format into `csl-corrections/.../batch_pending/` (via a csl-corrections worktree).
- **Fence:** commit change files to csl-corrections **only**. Open **no** PR to csl-orig; merge nothing. Write a `PWG_DEFECTS_STAGED.md` manifest listing every staged item for MG's later [/cologne-batch-pr](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md).
- **Acceptance:** N change files staged, N rows in the manifest, zero csl-orig writes, zero PRs opened to a maintainer repo.

### Step 10 — W1.10 hub sync + release

- **FINDINGS:** append the `〉` contamination number, the RNG-gap-now-filled note, and the citation-coverage delta (SanskritLexicography FINDINGS for data, Uprava FINDINGS for infra) via [/findings-append](https://github.com/gasyoun/claude-config/blob/main/commands/findings-append.md).
- **PROJECT_INTERLINKS:** register `pwg_de_lexicon.ttl`'s new layers as consumable; **SHARED_CODE:** register `validate_pwg_markup.py` + the RNG grammar as the canonical PWG markup validator.
- **CHANGELOG** entry under `[Unreleased]`, then [/cut-release](https://github.com/gasyoun/claude-config/blob/main/commands/cut-release.md).
- **GTD:** `@DECIDE` row for MG to review the staged defects + run the batch PR; `@DECIDE` for the Wave-3 requeue budget.
- **`.ai_state.md`:** move finished items to Completed, point Next Steps at Wave 2.
- **Deliver:** push the SanskritLexicography branch, open PR, auto-merge + delete branch.

## Ambiguity defaults (apply + log, never block)

- Malformed record that fits no bucket → new `unexpected-but-attested` bucket, logged.
- csl-atlas push rejected → retry via `/branch-contention-recover`; if unresolved, stage the csl-atlas layer changes as a patch file in the SL repo and log a `@DECIDE`.
- Citation ceiling < 85% → accept, catalogue the tail, log the reason.
- Store join ambiguity (a `senseId` maps to multiple segmentations) → mark `ambiguous` in the quarantine file, never guess.

_Dr. Mārcis Gasūns_
