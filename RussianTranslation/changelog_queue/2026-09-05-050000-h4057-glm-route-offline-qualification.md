_Created: 05-09-2026 · Last updated: 05-09-2026_

- H4057: **the GLM 5.3 Flash route is offline-qualified behind the existing paid-call kernel —
  qualification can no longer be blocked on an absent adapter, and unknown cost can no longer
  reach dispatch.** New
  [`GlmFlashAdapter`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_pipeline/providers.py)
  (route `glm-flash`, operator name `glm`) shares the `_OpenAICompatibleAdapter` body — same
  reservation ledger, strict request/response schema, raw response receipts, usage provenance,
  timeout, serialized bounded calls — with the actually-resolved identity `glm-5.3-flash`
  (OpenCode default `zai-coding-plan/glm-5.3-flash`, read from config metadata, not from chat
  memory; local slug spellings disagree, the observed value wins). **No price card is installed:**
  `estimate_cost_usd` refuses the route, the kernel now converts that refusal into an accounted
  `KernelRefusal(cost_ceiling)` BEFORE any reservation (previously an uncaught `ProviderError`
  past `assert_budget`), and token usage without a card normalizes to `cost_basis: unevaluable`
  — no Claude/xAI/DeepSeek price is borrowed, so a dollar-bounded GLM campaign fails closed with
  0 dispatches and 0 reservations. Offline replay
  ([tool](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4057_glm_route_qualification.py),
  sealed
  [report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4057_glm_route_qualification.json),
  verdict `QUALIFIED_OFFLINE`): pure gloss / Sanskrit `{#…#}` / apparatus `<ls>`+Nachtr. /
  homonyms / long card parse with source strings verbatim; malformed, missing-usage and
  route-substitution replies each fail terminally accounted; the kernel mechanics run against a
  `synthetic-qualification-only` price card, stamped so no receipt can be misread as observed
  economics. Zero provider calls, zero Claude CLI invocations, canonical store untouched.
  The sealed 30-card live manifest builder, the three-gate rubric (model-route validity /
  mechanical fidelity / independent semantic quality) and the exact capped live instructions
  stay in the
  [qualification packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/H4057_GLM_ROUTE_QUALIFICATION_PACKET_05-09-2026.md),
  staged behind separately-authorized prerequisites (canary-fence extension ruling, verified
  z.ai list prices, `ZAI_API_KEY`, endpoint confirmation). Production remains on the current
  authorized headless route. Proven by
  [`tests/test_pwg_pipeline_glm_route.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_pwg_pipeline_glm_route.py)
  (13 tests); `pytest -k pwg_pipeline` 142 passed.

_Dr. Mārcis Gasūns_
