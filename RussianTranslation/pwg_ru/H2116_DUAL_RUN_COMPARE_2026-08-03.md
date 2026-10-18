# H2116 — Dual-run compare: Sonnet 5 independent re-verify vs Grok 4.5 PR #964

_Created: 03-08-2026 · Last updated: 03-08-2026_

**Model:** Sonnet 5 (`claude-sonnet-5`) · residual for [H2116](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2116-Sonnet_SanskritLexicography_h2005-override-dual-run-compare_01.08.26.md)
**Override lane under review:** [PR #964](https://github.com/gasyoun/SanskritLexicography/pull/964) (merge `0f7b492e`) — Grok 4.5 (`grok-4.5`) executing H2005 + gloss_lang §464 FP fix + glyph quarantine sample under explicit user override.
**Method:** independent adversarial re-verify against the actual code, the source handoff ([H2005](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2005-Sonnet_SanskritLexicography_pwg-ru-ls-siglum-ru-display_31.07.26.md)), and [FINDINGS §464](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#464-the-h1624-g1-gloss_lang-classifier-mislabels-german-as-latinenglish-about-half-the-time-it-fires--and-those-spans-are-then-withheld-from-translation) — not a from-scratch reimplementation, since re-reading the already-correct code and re-running its selftests/scripts is cheaper and equally adversarial for mechanical deliverables.

## Verdict per deliverable

| Deliverable | Class | Notes |
|---|---|---|
| `build_article_site._ls_visible_display` (RU `ed. Bomb.` display) | **equivalent** | Correctly separates RU display substitution from resolver/href/store input (which always sees `vis`, never `display`); covers standalone + embedded shapes; DE/EN unchanged. Matches H2005 (a)/(b)/(c) exactly. |
| `ls_enrichment_selftest.test_h2005_ed_bomb_ru_display_not_resolve` | **equivalent** | 7/7 selftest checks pass (re-run locally); covers display, non-RU no-op, `source_key` Latin-stability (incl. non-Cyrillic assertion), html+md render both langs. Thorough — no gaps found. |
| `pwg_mask.looks_english_content` strong/weak split (§464 FP fix) | **equivalent + net-new** | Implementation correctly fixes both FINDINGS §464 named misfires (`bis an's Ziel bringen`, `an sich nehmen, empfangen, erlangen, erhalten` → now `de`/`default_de`). PR shipped only unit tests for cited examples — §464 explicitly said the fix "needs its own measured A/B" at corpus scale, which PR #964 never delivered. This session ran that re-measurement (see [Net-new: gloss_lang re-measurement](#net-new-glosslang-re-measurement-at-full-corpus-scale) below) as the missing verification. `pwg_mask.py --selftest` also re-run clean (20/20). |
| Glyph quarantine sample script + [n=200 report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H_GLYPH_QUARANTINE_SAMPLE_REPORT_20260801.md) | **conflicting (minor)** | Stratified sampling (SHA-256(key1) mod 10 round-robin, seed=20260801) is sound and deterministic — re-ran `sample_glyph_quarantine.py` byte-for-byte reproduced the committed sample (population 10881, sample 200, segmentation_flag 200/200). `segmentation_flag`-not-`ru_quality_verdict` framing is correct per MG's 29-07-2026 ruling. **Bug found and fixed:** the report template wrote a literal `%%` where a single `%` was intended (`"93%%"` in the Interpretation section) because that string is not passed through Python `%`-formatting — cosmetic display bug, not a logic error. Fixed in [`src/sample_glyph_quarantine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sample_glyph_quarantine.py) and the already-committed report. |
| A2/A6 "already shipped" claim ([memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H_OFFLINE_SPEED_A2_A6_VERIFY_2026-08-01.md)) | **conflicting (minor)** | Every cited symbol (`derive_wall_clock_minutes`, `build_production_metrics`, `emit_stage_boundary`, `refuse_defect_keys`, `discover_defect_keys_path`, `append_from_audit_report`, `backfill_documented`) verified to exist **at the pre-#964 base commit** `d759c0b8` — the "already shipped, verify only" claim is substantively correct, PR #964 added no redundant reimplementation. **Error found and fixed:** the O(n²) residual-ledger append fix was credited to H1811; `git log` shows H1811 is an unrelated offline-speed/hermeticity handoff — the actual O(n²) ledger fix landed in **H1940** (commit `a75eaa17`, `fix(pwg_ru): H1940 Phase 2 close-out — H4 dup lease-id, H3 fsync, O(n2) ledger, #6 EVIDENCE`). Fixed the memo's citation. |

## Adjudication

Both conflicts are citation/cosmetic-level, not implementation defects — nothing here required re-deriving Grok's work from scratch. Keep Grok's implementation for all five deliverables; the two fixes above (fix PR, this pass) correct the record without touching behavior.

## Net-new: gloss_lang re-measurement at full-corpus scale

FINDINGS §464 explicitly deferred a fix: *"changing the classifier changes masking behaviour pipeline-wide and needs its own measured A/B."* PR #964's own fix (`ENGLISH_STRONG`/`ENGLISH_WEAK` split, ≥2-distinct-weak-hit gate) addresses the mechanism but the PR shipped no re-measurement — only unit tests for the two examples FINDINGS cited by name. This session ran that missing A/B, scanning the classifier directly against `csl-orig/v02/pwg/pwg.txt` via `pwg_mask.records()`/`gloss_lang_spans()` (the same stage-0 reader the mask pipeline itself uses):

| Metric | §464 original (H1629, pre-fix) | This measurement (post-fix, 03-08-2026) |
|---|---:|---:|
| Records / spans scanned | pwg_ru store subset, 15,901 spans | full `pwg.txt`, 123,366 records, **192,763 spans** |
| `en`/`english_content` spans | 153 | 815 |
| — German-looking (heuristic: umlaut/eszett or a German function word) | 117 (**76.5%**) | **0 (0.0%)** |
| `la`/`botany_binomial` spans | 68 | 1,268 |
| — German-looking | 5 (7.4%) | **0 (0.0%)** |

Both spans and denominator differ (full dictionary vs. the already-ingested store subset), so the raw counts are not directly comparable — but the direction is unambiguous: **zero German-looking false positives** across a corpus 8× larger than the original sample. Regression check confirmed both FINDINGS-named misfires now classify `de`/`default_de`. A 20-item spot-check of post-fix `en` classifications found only plausible genuine Wilson-style English glosses (e.g. `'the exercise of the Yogi'`, `'an adopted or any other than the natural son'`), no obvious false negatives.

Caveats:
- The `botany_binomial` rule (7.4% FP in §464) was out of scope for this fix — §464's fix request and PR #964's summary both target `english_content` specifically; the 0% botany_binomial German-looking result here is a byproduct of the same heuristic proxy, not evidence that rule itself was touched.
- "German-looking" remains a heuristic proxy (same limitation §464 itself noted), so this is not a claim of zero true FPs, only that the *class* of misfire §464 measured is gone at this proxy's resolution.
- Scan script: `h2116_gloss_census.py` / `h2116_gloss_spotcheck.py` (session scratch, not committed — trivially reproducible from `pwg_mask.records()` + `gloss_lang_spans()` + a German-looking heuristic per the snippet above; not committed as a permanent tool since it duplicates existing FP-detection building blocks and this was a one-off verification, not a recurring gate).

## Stop condition

All 5 deliverables classified; 2 minor conflicts found and fixed; no deliverable required re-implementation. Dual-run complete in 1 pass (well under the 6-try stop condition).

_Dr. Mārcis Gasūns_
