# PWG `<ab>`/`<ls>` abbreviations — tooltips and RU-column purity

_Created: 10-07-2026 · Last updated: 19-07-2026_

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

## `<ls>` link enrichment (Pāṇini · Spr. · DHĀTUP.) — H1307

Three `<ls>` citation classes gain reader-facing enrichment on the pwg_ru
surfaces (article site now; review sheets via the shared `_render()`/`_ls_tooltip`
layer). Wired 19-07-2026 (Opus 4.8, `claude-opus-4-8`), born of MG's DA-sheet vote
(register rows N14 · N3(b) · N15 in
[H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md)).
All work extends the existing Cologne-port resolver
[`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
+ render layer — no second resolver.

### Coverage

| class | total | linked | linked % | tooltip | full-text enriched |
|---|--:|--:|--:|--:|--:|
| `P.` (Pāṇini) | 25351 | 25065 | 98.9% | 25349 | — (n/a) |
| `Spr.` (1st ed) | 13133 | 12953 | 98.6% | 13133 | — (n/a) |
| `Spr. (II)` (2nd ed) | 8684 | 8684 | 100.0% | 8684 | 8395 |
| `DHĀTUP.` | 2760 | 2659 | 96.3% | 2760 | — (n/a) |

- **Full-form Pāṇini `P. a,p,s` (3-param):** 25061 / 25061 linked (**100.0%**) — the H1307 DoD target.
- **`Spr. (II) N` (2nd ed):** 8684 / 8684 linked (**100.0%**), 8395 full-text enriched (96.7% of linked).

_Denominator: full source [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt) — the RU store
`src/pwg_ru_translated.jsonl` was absent on this machine, so per H1307 Prerequisite 1 the
count uses the whole PWG corpus (a superset of the RU-translated subset). Recompute against
the store when present: `python src/ls_coverage.py --md` (raw JSON → gitignored
`pwg_ru/eval/ls_coverage.json`). Generated 19-07-2026._

### Pāṇini `P.` → ashtadhyayi.com

The full form `P. adhyaya,pada,sutra` deep-links to
`https://ashtadhyayi.com/sutraani/{adhyaya}/{pada}/{sutra}` (unchanged; the N14
continuation form `n="P. 2,3,"` + visible `10.` resolves to `/sutraani/2/3/10` by
concatenation). **URL-form verification:** ashtadhyayi.com is a client-side SPA, so a
live HTTP 200 proves nothing (an invalid `/9/9/9` also returns 200 with the same shell).
The form was instead verified against the site's own authoritative backing data repo
[`ashtadhyayi-com/data`](https://github.com/ashtadhyayi-com/data) (`sutraani/data.txt`:
fields `a`=adhyaya, `p`=pada, `n`=number; 1.1.14 = निपात एकाजनाङ्), confirming the
adhyaya/pada/sutra decomposition. **Browse affordance** (MG's N14 "list of sūtras by
chapter and book"): a 2-param `P. a,p` links to the pāda list `/sutraani/{a}/{p}` and a
1-param `P. a` to the adhyāya list `/sutraani/{a}` — the site's own browse routes, no
local sūtra list built. Both patterns are **guarded** to Pāṇini's real ranges (pada 1–4,
adhyāya 1–8) so ambiguous or non-sūtra forms never mislink: `P. 1,23` (23 is no pada),
`P. 1,6` (pada 6), and the page-reference form `P. II, S. 3` (Böhtlingk vol. II, Seite 3
— **not** a sūtra) all correctly stay unlinked.

### `Spr.` / `Spr. (II)` → Indische Sprüche

Edition routing is unchanged and was **live-verified** this session: plain `Spr. N`
(1st ed) → [boesp1](https://sanskrit-lexicon-scans.github.io/boesp1/app1/?1415) and
`Spr. (II) N` (2nd ed) → [boesp2](https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?6145),
both via a **bare `?N`** query. Verified against the viewers' own `main.js`: boesp2 accepts
both `?N` and `?verse=N`; boesp1 accepts **only** `?N` — so the resolver's bare-`N` form is
the single one that works uniformly, and switching to `verse=N` (as one README documents)
would silently break every 1st-ed link. No resolver change was needed. **Full-text
enrichment** (MG's N3(b)): every `Spr. (II) N` gains a hover tooltip carrying the saying's
IAST verse + German translation from the recognized full text
([`indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl),
7,537 sayings numbered 1–7878 with 341 numbering gaps), while keeping the boesp2 href.
**Edition guard** ([PWG#87](https://github.com/sanskrit-lexicon/PWG/issues/87)): the 1st-ed
`Spr. N` (5,419 sayings) is a *different* edition and is never resolved against the 2nd-ed
JSONL — `spr_fulltext.second_ed_num()` matches only the `Spr. (II) <digit>` form. The 3.3%
of linked `Spr. (II)` refs left unenriched fall in the JSONL's numbering gaps (plus one
lone source-data typo, `Spr. (II) 15802`, beyond the edition's range — it links but cannot
enrich, never mis-enriches).

### `DHĀTUP.` → Palsule — SPEC'D-NOT-WIRED (acquisition spec)

MG's N15 asks that `DHĀTUP. x,y` citations cite the Palsule list. **Verdict: cannot be
wired from existing data — spec only.** A local hunt (SanskritGrammar
[`PALSULE_AUDIT.md`](https://github.com/gasyoun/SanskritGrammar/blob/main/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md),
WhitneyRoots, [kosha datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json),
SanskritLexicography [FINDINGS §63](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md))
found **no** machine-readable Palsule-numbered dhātupāṭha and **no** Böhtlingk/Westergaard→Palsule
concordance anywhere in the org. The only machine-readable list is the vidyut dhātupāṭha
(2,259 dhātus, keyed by gaṇa.sūtra, SLP1) — a *different* numbering. PWG's `DHĀTUP. x,y` is
Böhtlingk's own gaṇa-arranged edition (x=gaṇa, y=serial-within-gaṇa); Palsule assigns its
own ~3,690-entry numbering. The current resolver already links `DHĀTUP. x,y` to the
Westergaard scan viewer at gaṇa level (2,659/2,760 = 96.3%); that stays. **Acquisition spec
to deliver Palsule references:** (a) digitize Palsule's numbered list from the print source
(G.B. Palsule, *The Sanskrit Dhātupāṭhas*); (b) build a verified Böhtlingk-`DHĀTUP.`↔vidyut
gaṇa.sūtra crosswalk; (c) normalize ablaut/citation-form (per FINDINGS §90 and the H328
negative result: a naive it-stripped join matched only 454/930 Whitney roots). Natural owner:
article **A39** ([Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)).
**No fabricated links.**

## Mechanical RU style rules (no-ё, terse metalanguage) — H1305

A separate, purely mechanical style stream lives in its own doc, not here:
[RU_STYLE_MECHANICAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md)
— no letter ё anywhere in RU output (whitelist: standalone «всё»/«Всё» only), «вместо»→«вм.»,
«в значении»→«в знач.» in editorial metalanguage, and `ed. Bomb.` → «Бомбейская ред.» in free
prose only (never inside `<ls>…</ls>`, which this doc's `<ls>` tooltip/link-enrichment layer
above still resolves against the verbatim Latin siglum). Distinct from the `<ab>`/`<is>`
render-time abbreviation-translation policy documented above: R1–R4 are STORE-LEVEL fixed
substitutions (swept once into `pwg_ru_translated.jsonl`, not a render-time transform), and
purely orthographic/terseness, not a translation-of-record decision.

## Files touched

* [`RussianTranslation/src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py) — new; the DE→RU editorial-abbreviation map + coverage CLI.
* [`RussianTranslation/src/iast_to_cyrillic.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/iast_to_cyrillic.py) — new; best-effort IAST→Cyrillic transliterator for `<is>` proper names.
* [`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) — `_render()` gained a `lang` parameter; `<ab>`/`<ls>` tooltips; `<is>` Cyrillicization; new `abbreviations.html`/`abbreviations.js` dashboard (`ab_frequency()` + `emit_abbreviations()`).
* `RussianTranslation/article_site/` — regenerated output (147 roots, 11,275 senses at time of writing).

H1307 `<ls>` link enrichment (19-07-2026):

* [`RussianTranslation/src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) — guarded Pāṇini 2-param (`/sutraani/a/p`) and 1-param (`/sutraani/a`) chapter/book browse patterns.
* [`RussianTranslation/src/spr_fulltext.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/spr_fulltext.py) — new; Indische Sprüche 2nd-ed full-text lookup + `Spr. (II)` edition guard, for tooltips.
* [`RussianTranslation/src/pilot/build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) — `_ls_tooltip()` (Spr. (II) full text over source title), wired into the html tooltip + md link title.
* [`RussianTranslation/src/ls_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_coverage.py) — new; per-class `<ls>` coverage counter (store, else pwg.txt).
* [`RussianTranslation/src/pilot/ls_enrichment_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ls_enrichment_selftest.py) — new; fixture selftest, wired into the RussianTranslation CI gates.

H1305 mechanical RU style sweep (19-07-2026):

* [`RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RU_STYLE_MECHANICAL.md) — new; rules R1–R4, false-positive measurement, sweep counts.
* [`RussianTranslation/src/ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py) — new; store sweep + shared violation detector (`--apply`/`--selftest`/`--wf`).
* [`RussianTranslation/src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) — new `ru_style` RU-only gate.
* [`RussianTranslation/src/pilot/run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js) — HARD RULE 9 (R1–R4) in the `CONV`/`TR` template.
* [`RussianTranslation/src/pilot/prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py) — `ru_style_*` rule pins.

_Dr. Mārcis Gasūns_
