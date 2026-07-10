# PWG `<ab>`/`<ls>` abbreviations — tooltips and RU-column purity

_Created: 10-07-2026 · Last updated: 10-07-2026_

## Why this exists

MG flagged (10-07-2026, via the `mena` article on the public site) two problems
with the [PWG article site](https://gasyoun.github.io/SanskritLexicography/):

1. German `<ab>` grammar/usage abbreviations and `<ls>` literary-source sigla
   had no tooltip explaining what they stand for — unlike
   [sanskrit-lexicon.uni-koeln.de](https://sanskrit-lexicon.uni-koeln.de), whose
   convention this project is expected to match. He also asked for a
   corpus-wide dashboard of abbreviation usage, not just per-article.
2. The Russian (RU) column of the translated text still contained raw German
   inside `<ab>` tags — `s. u.` (German "siehe unter") is Russian `см.`, and
   must not be left untranslated in Russian prose. His own examples:
   `mena s. u. menā.` → RU should read `mena см. menā.`, and
   `Bein. Vṛṣaṇaśvaʼs` → RU should read `эпит. Вришанашва` (Cyrillic name, not
   IAST).

An audit of `RussianTranslation/src/pwg_ru_translated.jsonl` (11,275 rows,
2026-07-10) found this was not a small issue: **12,151 of 12,152 `<ab>`
occurrences in the RU field (99.99%) were still verbatim German/Latin**, across
265 distinct tokens.

## Architecture decision: fix at RENDER TIME, not in the data store

The translated JSONL store (`pwg_ru_translated.jsonl`) keeps the `<ab>`/`<is>`
tags and their **raw German/IAST content untouched** — this already matches
how `<ls>` citations and `{#...#}` Sanskrit lexical forms are stored (source-
faithful, presentation decided by the site generator). So the fix lives
entirely in
[`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py)'s
`_render()` function, which now takes a `lang` parameter (`'de'`/`'ru'`/`'en'`)
and treats `<ab>`/`<is>` differently per language column:

* **`<ls>` (literary-source sigla, e.g. `ṚV.`, `AV.`)** — unchanged text in
  every language, but now every resolvable siglum gets a `title=` tooltip with
  its full source name (from PWG's own 2,681-entry bibliography,
  [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)).
* **`<ab>` (grammar/usage abbreviations)** — every language gets a `title=`
  tooltip with the authoritative German/English expansion (PWG's own 791-entry
  table,
  [`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py)).
  **Only the RU column's visible text changes**, per the bucket below.
* **`<is>` (proper names embedded in prose)** — DE/EN keep the IAST spelling;
  RU transliterates to Cyrillic
  ([`iast_to_cyrillic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py)).

Because this is render-time, **it automatically covers every future
translated root with no prompt change and no reprocessing** — the fix is not a
one-time patch over the current ~11k-row store, it is permanent.

## Decision: grammatical-category abbreviations stay Latin

`<ab>` splits into two buckets, and which bucket a token is in is the whole
question MG asked to investigate ("нужно сделать расследование и понять, какие
[латинские] оправданы").

**Bucket B — grammatical categories (KEPT as international Latin, tooltip
only).** Case/mood/voice/tense/aspect/part-of-speech labels — `Acc.`, `Loc.`,
`caus.`, `pass.`, `aor.`, `sg.`, `masc.`, `partic.`, `subst.` … This is ~75% of
all `<ab>` volume (measured: 9,000 / 12,152). Decided via `AskUserQuestion`
10-07-2026: **keep as Latin**, matching both Cologne's own site and worldwide
Indological convention — a hover tooltip is the only change. No mapping table
needed; this is simply "no entry in `RU_MAP`" (the default/fallback path).

**Bucket A — editorial / cross-reference / deictic / domain-label
abbreviations (TRANSLATED to Russian).** These are plain German (or German-
flavoured Latin) function words with no comparable international-scholarly-
Latin status — `s.`/`s. u.` ("see"), `Vgl.` ("compare"), `Bed.` ("meaning"),
`Z.` ("line"), `dass.` ("the same"), and MG's own two examples `Bein.`
("epithet") and (implicitly, via `N. pr.`) "proper noun". The curated mapping
lives in
[`RussianTranslation/src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py)
(`RU_MAP`, ~95 entries as of this writing). Anything NOT in `RU_MAP` falls back
to the original token (still gets a tooltip) — an unclassified/rare token
never regresses, it just isn't (yet) translated.

Live coverage (see the [abbreviations dashboard](https://gasyoun.github.io/SanskritLexicography/abbreviations.html)
for the current numbers): **~43% of `<ab>` occurrences translated to Russian,
~52% kept Latin (Bucket B), ~5% unresolved** (rare tokens not in PWG's own
`pwgab` table at all — typically OCR noise or non-standard local abbreviations).

## Two data-level collisions found and fixed

Some already-translated cards paraphrase the abbreviation by hand in the
surrounding RU prose **and** leave the tag — both `_ab_display()` and
`_is_display()` in `build_article_site.py` guard against these with
lookaround context checks (see their docstrings for the exact mechanism):

1. **Doubled "see"**: stored RU text `см. <ab>s. u.</ab> menā` — the
   translator had already written `см.` by hand; rendering our own `см.` for
   the tag too produced `см. см.`. Fixed by checking the text immediately
   before the tag and suppressing a redundant repeat.
2. **Doubled vowel in transliterated names**: `<is>Vṛṣaṇaśva</is>а` — an
   a-stem Sanskrit name transliterates to `Вришанашва` (already ending in
   `-а`), and the translator had glued a bare Russian case-vowel `а` directly
   after the tag (assuming the tag's content was a bare consonant stem) →
   `Вришанашваа`. Fixed by checking the character immediately after the tag
   and dropping our own trailing vowel when it would collide with a glued-on
   Russian ending.

## Known residual risk / open items (not solved here — future work)

* **`iast_to_cyrillic.py` is a first-pass transliterator**, not a validated
  scheme. Known weak spots are documented in its own docstring (semivowel
  y/v-glide coalescence not modeled, visarga handling is a heuristic,
  capitalization only on the first word of a multi-word name). It has been
  spot-checked on the `mena` article's two names (`Vṛṣaṇaśva` →
  `Вришанашва`, `Himavant` → `Химавант`) but **not** validated across the
  full corpus of `<is>` spans. A dedicated QA pass (sample + human review, or
  cross-check against any names Кочергина/Елизаренкова already transliterate)
  is recommended before treating this as authoritative — see the mint
  handoff.
* **`'med.'`/`'medic.'`** resolve in `pwgab` as "Medizin/medicine" (a
  subject-domain label) and are translated to `мед.` on that basis. If a
  genuine grammatical "medium voice" sense shares the bare token `med.`
  anywhere in the corpus (pwgab's table only stores one meaning per token
  string), that occurrence would be mistranslated. Not observed in a spot
  check but not exhaustively verified either.
- **`RU_MAP` is a first pass covering the highest-frequency tokens (~95 of
  266 distinct)**, not an exhaustive audit of the full `pwgab` table (791
  entries) or even of all 266 tokens actually used in the corpus so far. The
  dashboard's "не найдены в таблице pwgab" bucket (~5% of occurrences, rare/
  OCR-noise tokens) and any newly-appearing rare Bucket-A tokens as the corpus
  grows are natural additions to `RU_MAP` over time — append, don't rebuild.
* **Scope is `pwg_ru` only.** `mw_ru`'s `<gram>` tag has a *documented*
  "deliberately left untouched, do not fix" convention in the org
  [`CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md)
  (a different, independent pipeline) — this change does **not** touch or
  override that. Whether `mw_ru` has the same German/Latin-leak problem is an
  open question, not investigated here.

## Files touched

* [`RussianTranslation/src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) — new; the DE→RU editorial-abbreviation map + coverage CLI.
* [`RussianTranslation/src/iast_to_cyrillic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py) — new; best-effort IAST→Cyrillic transliterator for `<is>` proper names.
* [`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) — `_render()` gained a `lang` parameter; `<ab>`/`<ls>` tooltips; `<is>` Cyrillicization; new `abbreviations.html`/`abbreviations.js` dashboard (`ab_frequency()` + `emit_abbreviations()`).
* `RussianTranslation/article_site/` — regenerated output (147 roots, 11,275 senses at time of writing).

_Dr. Mārcis Gasūns_
