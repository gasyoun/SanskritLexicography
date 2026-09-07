# `pwg_mask` probe: the `_apta` sense-15 defect is a classifier miss, not a model failure — one missing article flips English to German; 66 real spans corpus-wide

_Created: 07-09-2026 · Last updated: 07-09-2026_

_Date: 07-09-2026 · Executor: Opus 5 (`claude-opus-5`), interactive · **0 paid calls** (offline)_

- **Measured, not inferred.** `classify_pct_detail` on the two English gloss spans of `_apta`:
  sense 12 → `gloss_lang: en`, `rule_id: wilson_en`, `translate: False`, masked to `{T4}`;
  sense 15 → `gloss_lang: de`, `rule_id: default_de`, `translate: True`, **never masked** —
  it survives verbatim into the skeleton the model sees.
- **The model and the prompt are exonerated.** Sense 15 arrived as a *visible* `{%…%}` gloss
  flagged for translation, and the GLOSS WRAPPERS rule requires a visible wrapper to reappear
  around its translated gloss. The H4277 `{Tn}`-verbatim clause could not apply: there was no
  `{Tn}`. `foreign_gloss_translated` correctly stayed silent — on that label a German gloss was
  correctly translated. **There is no detector gap**, which corrects §4 of the window result doc.
- **Root cause:** `looks_english_content` needs **≥2 distinct** weak markers from
  `{a, an, of, or, and, with, as, one, war}` (bar set by §464 so German/Latin residue does not
  take the verbatim path). `equation of **a** degree` scores `{of, a}` = 2 → English;
  `equation of degree` scores `{of}` = 1 → falls through to `default_de`. One article.
- **Blast radius, whole corpus (192 763 `{%…%}` spans):** 933 match the sense-15 shape, and they
  are **not one class** — `an` 678 and `a` 175 and `war` 14 are dominated by German/Italian
  homographs (`Mangel an Vertrauen`, `oltre a quindeci di`), which is exactly what the ≥2 bar
  protects. The genuinely English remainder is **66**: `or` 30, `of` 23, `and` 6, `with` 6,
  `as` 1 — `offence or guilt`, `sulphate of alumine`, `sighs of expiration`.
- **Proposed fix, NOT applied:** split the weak set — `an`/`a`/`war` are German homographs and
  keep the ≥2 bar; `of`/`or`/`and`/`with`/`as` are not German words and could pass on one hit.
  That catches the 66 while leaving all 867 homograph spans untouched. It changes masking
  corpus-wide, so it wants its own handoff, a two-way fixture (`equation of degree` → en,
  `Mangel an Vertrauen` → de) and a selftest before any paid call. A human decides.
- **Consequence for `_apta`:** a fifth window on the current classifier would reproduce sense 15
  exactly — nothing about the input would have changed. `_apta` stays on the defect list, store
  untouched.
- Record: [pwg_ru/h4277r/H4277R_PWG_MASK_PROBE_ENGLISH_GLOSS_07-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277r/H4277R_PWG_MASK_PROBE_ENGLISH_GLOSS_07-09-2026.md)

_Dr. Mārcis Gasūns_
