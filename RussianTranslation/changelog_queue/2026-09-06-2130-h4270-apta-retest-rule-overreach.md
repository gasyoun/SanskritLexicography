# H4270 — gloss-wrapper prompt hardening + one `_apta` c1 re-test: funded defect fixed, new single-sense defect named, audit requeue (no ship)

_Date: 06-09-2026 · Executor: OxAlpha (`glm-5.3-flash`, opencode lane) · 1 paid call on c1_

- `MASK_PREAMBLE` (gen_opt_harness2.py) gains the GLOSS WRAPPERS `{%…%}` preservation block
  (GAPS §17 GLOSS-DE-RESIDUE convention) with the `a〉 {%ein%} <is>Arhant</is> <ls>H. 25</ls>.`
  → `а) {%некий%} …` worked example; pinned by `test_gloss_wrapper_prompt_preservation_h4270`
  (rule clauses + worked example + end-to-end mini-manifest fixture asserting DE `{%…%}` stays
  inline in the masked skeleton and the rule survives into the generated JS). Canary golden
  manifest regenerated for the intended prompt change (`canary_manifest_build_selftest` PASS);
  `window_selftest` 221/222 (only the red-by-design parity gate fails).
- Live re-test on `_apta` (c1, manifest `h4270rh`, nominal, `--budget=1 --no-grammar --no-tm`,
  sha `9523136b…`): window success 139.9 s first attempt; **7/7 DE wrappers preserved**
  (H4015: 1/8), zero `markup_wrapper_dropped`, `<ls>`/`{#…#}`/`{#jawA#}` intact, zero «».
- Audit still requeues — on a NEW high-confidence defect the fix exposed: sense 4b, the model
  wrapped and translated a MASKED English span (`{%equation of a degree%}` →
  `{%уравнение степени%}`) instead of echoing `{Tn}` for deterministic verbatim restore
  (`foreign_gloss_translated`). `COVERAGE-OVER(17/7)` identical to H4015 (pre-existing).
  **AUDIT_DEFECT_REQUEUE, 3rd occurrence — named stop, no re-burn; store untouched;
  `_apta` stays on `H3654_defect_keys.txt`.** Decision to MG: one-clause rule tightening
  (`{Tn}` stays verbatim, never translate/wrap a masked span) + 4th-window authorization,
  or option b (hand-marking) / option c (unwrapped-acceptance).
- Record: [pwg_ru/h4270/H4270_C1_RETEST_RESULT_06-09-2026.md](../RussianTranslation/pwg_ru/h4270/H4270_C1_RETEST_RESULT_06-09-2026.md)
