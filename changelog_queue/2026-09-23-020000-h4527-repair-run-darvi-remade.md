_Created: 23-09-2026 · Last updated: 23-09-2026_

- H4527: **the repair run re-made `darv_i` on Anthropic and promoted it; `kast_ur_i` is blocked by an audit-gate false positive, not by its card.**
  Run `h4527-repair-230923` (4 paid calls = the cap, plus 1 canary; all Anthropic ids) replaced the three GLM-made `darv_i~~h0_zz_pw`
  rows from 20-09 with a clean card (every audit gate PASS, store 11 534 → 11 534). `kast_ur_i~~h0_zz_pw` failed `prompt_semantic` a
  second time: `prompt_rule_audit.looks_foreign_literal` does not strip the PWG `<bot>` tag, so two Latin species names correctly kept
  verbatim read as untranslated German. Evidence:
  [H4527_REPAIR_RUN_DARVI_REMADE_KASTURI_GATE_FALSE_POSITIVE_23-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4527/H4527_REPAIR_RUN_DARVI_REMADE_KASTURI_GATE_FALSE_POSITIVE_23-09-2026.md).
