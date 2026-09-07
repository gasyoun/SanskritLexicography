# `pwg_mask`: split `ENGLISH_WEAK` into homograph vs non-homograph subsets — 66 English gloss spans stop leaking through the German default

_Created: 07-09-2026 · Last updated: 07-09-2026_

_Date: 07-09-2026 · Executor: Sonnet 5 (`claude-sonnet-5`), interactive · **0 paid calls** (offline)_

- **Applies the fix proposed in** [h4277r/H4277R_PWG_MASK_PROBE_ENGLISH_GLOSS_07-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h4277r/H4277R_PWG_MASK_PROBE_ENGLISH_GLOSS_07-09-2026.md).
  `looks_english_content` required ≥2 distinct weak markers from the whole
  `{a, an, of, or, and, with, as, one, war}` set (§464) before taking the
  `english_content → translate:False` path — correct for German/Italian homographs
  (`an`, `a`, `war`), but it also swallowed genuine single-marker English spans like
  `equation of degree`, which fell through to `default_de` and was never masked.
- **Split the weak set:** `ENGLISH_WEAK_HOMOGRAPH = {a, an, war, one}` keeps the ≥2-hit
  bar; `ENGLISH_WEAK_SINGLE = {of, or, and, with, as}` — no comparable German-prose
  collision — now passes on one hit. `ENGLISH_WEAK` kept as a back-compat union alias.
- **Two-way fixture added to `--selftest`:** `equation of degree` → `en`/`translate:False`;
  `Mangel an Vertrauen`, `an demselben Tage`, `reich an Fasern, Schossen, Stengeln` →
  `de`/`translate:True`.
- **Re-measured over all 192,763 PWG gloss spans:** 66 spans reclassify to
  `en`/`translate:False` (matches the probe's predicted count exactly); 823 remaining
  lone `a`/`an`/`war` spans correctly stay `de`/`translate:True` — the homograph
  safety property is intact.
- **Verified:** `pwg_mask.py --selftest` 20/20 OK; `pilot/window_selftest.py` 222/223
  (sole failure is the pre-existing red-by-design parity gate, confirmed identical on
  `master`'s own HEAD, unrelated to this change).
- Out of scope (per H4312): no paid call, no window, no store write, no promotion,
  `_apta` untouched.
- PR: [gasyoun/SanskritLexicography#2107](https://github.com/gasyoun/SanskritLexicography/pull/2107)
  (open, auto-merge armed, blocked by the pre-existing red `RussianTranslation gates`
  required check — a human merge is owed).

_Dr. Mārcis Gasūns_
