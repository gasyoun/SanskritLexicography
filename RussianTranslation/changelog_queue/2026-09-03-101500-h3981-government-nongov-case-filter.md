- **H3981 — `extract_government()` now drops non-government cases per case, in both
  branches; the last 2 portrait schema violations are closed (Opus 5 `claude-opus-5`,
  03-09-2026; deterministic, zero provider calls, no store writes).** The extractor and
  the schemas had disagreed since H1624 G2 first put `government` on portrait senses:
  [`src/government_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py)
  skipped a parenthesis only when **all** its cases were non-government, so a mixed
  `(<ab>nom.</ab> oder <ab>acc.</ab>)` survived with `nom` still in `cases` (record
  81366, `key1=yaTAvftta`), and the `MIT_RE` branch applied no non-government filter at
  all, so `mit dem <ab>nom.</ab>` yielded `['nom']` (record 19236, `key1=ko`). Both
  violated the `sense.government.items.cases` enum `["acc","loc","instr","gen","dat","abl"]`
  that
  [`schemas/pwg_portrait_structural.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_portrait_structural.schema.json)
  and
  [`schemas/pwg_ru_final_card.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_final_card.schema.json)
  share, and contradicted
  [`src/government_sidecar.py:55`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_sidecar.py#L55),
  which states the exclusion already happens.
  **The fix filters the hits; the schemas were right.** A shared `_gov_only()` helper is
  applied per hit in **both** branches, a marker left with no government case emits no hit,
  and `variation`/`kind`/`connector` are derived from the *filtered* list — a group naming
  two cases but governing one is `paren-single`, `variation` false, connector empty. `span`
  still carries the verbatim source snippet, so the dropped token stays auditable. Both
  enums are unchanged; the two schema descriptions now name `form_notes` as the nom/voc home.
  **Zero information loss, verified rather than assumed:** in both defect records the
  dropped `nom` is already present in the sense's `form_notes`
  (`{"case":"nom","kind":"bare_ab"}` and `{"case":"nom","kind":"paren_ab"}`), because
  `form_labels.extract_form_notes()` scans the same DE segment independently — so the fix is
  pure subtraction, not a re-routing.
  **Blast radius measured before the edit:** 2,417 parenthesis hits + 1,556 `mit` hits over
  the corpus, of which exactly one mixed paren group and one all-nongov `mit` marker — two
  occurrences, matching the two reported violations exactly. No shipped artifact under
  [`release/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/release)
  carries `nom`/`voc` inside a `government` array, so nothing needs re-cutting.
  **The stale receipt is regenerated.**
  [`reports/pwg_portrait_validation.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_portrait_validation.json)
  had claimed 0 violations since 01-08-2026 only because it predated H1624 G2; it now
  genuinely reports **123,366 records / 123,366 passes / 0 parse-error / 0 schema-violation /
  0 unexpected-but-attested / 0 unclassified**, and `--assert-total` exits 0. Eight new
  regression assertions in `selftest_extract_government()` pin both defect shapes plus a
  three-case group that loses one non-government member and stays a variation.
  **Declared divergence, not an oversight:** the census path `scan_entry()` keeps the same
  unfiltered `mit` branch, because its tallies are frozen in
  [`src/census_stats.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/census_stats.json)
  and quoted in `RESULTS_LOG.md`, `CHANGELOG.md`, `GRAMMAR_LAYER.md`,
  `CAPABILITY_OBSERVATORY.md` and the A51 methods draft. Aligning it moves `mit-phrase`
  1556 → 1555 and invalidates five published citations — a re-freeze plus citation update,
  i.e. a publication decision rather than a code fix, for a 1-in-3,973 correction. The
  divergence and its exact size are now written into `scan_entry()`'s docstring instead of
  being implicit.
