# Compound-marker typography across the Sanskrit dictionaries — consolidated census

_Created: 17-08-2026 · Last updated: 17-08-2026_

Consolidates FINDINGS **§553–§558, §561 and §564** ([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)),
measured over the [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
digitizations, `RussianTranslation/src/koch.jsonl` (local-only, gitignored —
in-copyright content, never on GitHub),
[wg_text.txt](https://github.com/gasyoun/WhitneyRoots/blob/main/src/wg_text.txt) and the
[csl-whitroot print scans](https://github.com/sanskrit-lexicon/csl-whitroot/tree/master/jpg).
Trigger: the pwg_ru compound-position glyph vote (лист `h2805_q3_deploy` on the
[vote hub](https://gasyoun.github.io/vote/)). PRs:
[#1760](https://github.com/gasyoun/SanskritLexicography/pull/1760) ·
[#1761](https://github.com/gasyoun/SanskritLexicography/pull/1761) ·
[#1762](https://github.com/gasyoun/SanskritLexicography/pull/1762) ·
[#1763](https://github.com/gasyoun/SanskritLexicography/pull/1763) ·
[#1765](https://github.com/gasyoun/SanskritLexicography/pull/1765) ·
[#1768](https://github.com/gasyoun/SanskritLexicography/pull/1768) ·
[#1769](https://github.com/gasyoun/SanskritLexicography/pull/1769).

## 0. Заключение — one conclusion over all the typographic aspects

Два века санскритской лексикографии знают ровно **четыре стратегии** показать
читателю устройство сложного слова, и все четыре решают РАЗНЫЕ задачи, а не
конкурируют за одну: **кружок** экономит набор (не перепечатывай общее —
элизия у PW/Каппеллера/Apte/Кочергиной, усечение у PWG/Schmidt/MW-1872);
**шов в лемме** печатает сам разбор (дефис Грассмана → тире MW-1899 →
транслит Макдонелла), и только этой линии нужны спецзнаки для сандхи-сплава
(`‿` у MD, внутрисловный `˚` у MW); **ведущий дефис** классифицирует основу
как связанную (Уитни, унаследовано леммами Кочергиной); **прозаический
разбор** объясняет (E. Уилсона → i. e. Бенфея → скобки PWG). Знак при этом
почти не менялся — менялась его грамматика: один и тот же петербургский Kreis
значит «не повторяю» у Бётлингка, «допиши слово» у него же в цитатах, «здесь
шов, но сандхи склеило» у Monier-Williams и «позиция в композите» у
Макдонелла (`˚—`/`—˚`). Следствие для нас: (1) парсер обязан знать словарь и
позицию знака, прежде чем разворачивать кружок — «элизия» верна почти всегда
для CAE/CCS/PW и лишь в ~¼ случаев для PWG; (2) заголовочное слово везде
слитное — членение живёт в `<k2>`/теле, и любой census, читающий `<k1>`,
слеп; (3) для карточек pwg_ru выбор глифа `˚` — не вкусовщина, а
присоединение к главной линии традиции, а прецедент пометы ПОЗИЦИИ — пара
Макдонелла, где начало/конец различаются порядком знаков, не новым глифом.
Десять следующих замеров того же метода закреплены хэндоффами H2978–H2987
(§5 ниже).

## 1. The four traditions, in one map

| Strategy | Sign | Dictionaries | What it means |
|---|---|---|---|
| **Ring-elision** | `˚` before the fragment | PW · Cappeller CAE/CCS · Apte AP/AP90 · Macdonell (partly) · Kochergina `°` | "the shared first member is not reprinted" |
| **Ring-truncation** | `˚` after the fragment | PWG (majority) · Schmidt · Benfey (in conjectures) · MW72 (both ways) | "the rest of the word is to be supplied" |
| **Seam in the lemma** | hyphen / em-dash / undertie | Grassmann `agni-jihvá` → MW-1899 `agni—hotra` + `aṃ˚soccaya` · Macdonell translit `agni-hotrá` + `a-kravya‿ad` · Whitney (bound stems `-kartin`) | the analysis is printed in the headword itself |
| **Prose analysis** | parenthesis / `E.` / `i. e.` | PWG `(agni + hotra)` 34 752× · Wilson `E.` 39 713× (89 %) · Benfey `i. e.` 9 168× (53 %, sandhi-resolved) · Whitney Grammar `rājendra (rāja-indra)` | decomposition stated in words |

Constant across ALL sources: the CDSL `<k1>` headword is normalized solid —
**every census must read `<k2>` / the body markup, never `<k1>`** (three
corrections in the series: MW §555, Grassmann §556, Macdonell §558).

## 2. Master table (rings / degree / deva-sign / seams)

Counts of U+02DA `˚` · U+00B0 `°` · U+0970 `॰` · seams in `<k2>`, per
`v02/<dict>/<dict>.txt`; zero-practice dicts omitted (abch, acph, acsj, armh,
lan, nmmb, pe, pgn, pui, skd, snp; bur/vcp/wil carry only stray degrees).

| dict | ring ˚ | lead | trail | mid-word | ° | ॰ | k2 seams | entries |
|---|---|---|---|---|---|---|---|---|
| pwg | 83 398 | 19 491 | 51 170 | — | 11 | 0 | 0 | 123 366 |
| mw | 53 307 | 12 100 | 9 088 | 6 935 | 0 | 0 | **73 772** (—) | 286 525 |
| stc | 24 754 | | | | 3 | 0 | 0 | 24 574 |
| pw | 23 706 | 18 135 | 3 893 | — | 14 | 0 | 0 | 170 556 |
| bhs | 22 103 | | | | 1 | 0 | 0 | 17 839 |
| mw72 | 21 099 | 75 | 846 | 1 | 14 | 0 | 0 | 55 390 |
| inm | 19 533 | | | | 0 | 0 | 0 | 12 647 |
| sch | 15 193 | | | | 9 254 | 0 | 0 | 29 125 |
| cae | 9 848 | 3 003 | 22 | — | 11 | 0 | 0 | 40 069 |
| ccs | 6 664 | 3 652 | 68 | — | 15 | 0 | 0 | 30 010 |
| ap | 5 150 | 2 353 | 1 290 | — | 3 | 7 | 61 | 90 843 |
| md | 4 827 | 137 | 13 | — | 0 | 0 | 0 (translit ~13 119) | 20 749 |
| ap90 | 4 051 | 2 116 | 871 | — | 3 | 0 | 1 414 | 34 882 |
| pwkvn | 2 203 | | | | 0 | 0 | 0 | 24 976 |
| lrv | 1 004 | | | | 2 | 0 | 0 | 53 441 |
| ben | 506 | 255 | 221 | — | 0 | 0 | 0 | 17 310 |
| gra | 0 | | | | 0 | 0 | **4 356** (-) | 12 785 |
| bop | 0 | | | | 0 | 82 | 0 | 8 961 |
| wil | 0 | | | | 5 | 0 | 0 (E. 39 713) | 44 577 |
| ae | 0 | | | | 245 | 0 | 0 | 11 359 |
| koch | 0 | | | | 136 | 0 | hyphen-led lemmas | 29 177 rows |

Minor ring users ≤200: acc 135 · fri 154 · gst 161 · ieg 45 · mci 67 · vei 5.
English→Sanskrit dicts (bor 1 229 / mwe 2 340 hyphenated `<k1>`) carry English
hyphens — a false positive for this census. Lead/trail for the blank rows was
not profiled (same method applies; markup per dict).

## 3. Per-dictionary summaries (with the FINDINGS section of record)

- **PWG** (§554): trailing-truncation majority + the only systematic
  parenthesized decomposition `({#agni#} + {#hotra#})`, 34 752×. Ring every
  ~1.5 entries.
- **PW** (§554): flipped the ring to leading member-elision; analysis dropped.
- **Cappeller CAE/CCS** (§553–554): PW convention at its endpoint —
  leading-only in practice; solid headwords; trailing single-digit noise.
- **Apte AP/AP90** (§555): leading dominates, tail alive; ring also
  abbreviates grammar labels (`[za˚ ta˚]` = ṣaṣṭhī-tatpuruṣa); compounds as
  `+`-joined hyphen sub-lemmas of the **—Comp.** block (36 248 in ap).
- **MW-1899** (§555): unique system — em-dash seam in 73 772 lemmas
  (`agni—hotra`, nested `agni—hotrI—vatsa`), ring three ways incl. 6 935
  mid-word sandhi-seam rings (`aM˚so-ccaya`); **read compound analysis from
  `<k2>` dashes, never reconstruct**.
- **MW-1872** (§555): pre-system; own symbol list: "˚ that the rest of a word
  is to be supplied, e. g. ˚ri- in˚ after karīndra is for kari-indra".
- **Grassmann** (§556): pure hyphenation pole — 4 356 hyphenated `<k2>`
  lemmas, zero rings; the precedent MW-1899 generalized.
- **Kochergina** (§556): `°` in three PW-shaped uses (leading elision in refs,
  hyphen-led bound second members, trailing prefix truncation); provenance =
  Böhtlingk's Imperial-Academy St. Petersburg typography, mediated by the
  Kalyanov school. Typography inherited; sense ORDER not (§18).
- **Benfey** (§557): prose analysis `i. e.` in 53 % of entries, sandhi
  resolved, `+` for suffixes; ring only in text-critical conjectures (506).
- **Wilson** (§558): pre-graphic era — 89 % of entries end in a prose `E.`
  etymology; leading hyphens abbreviate inflection, not compounds.
- **Macdonell** (§558): four devices — hyphenated translit lemmas (~13 119),
  underties `a-kravya‿ad` (2 852) for sandhi seams, **`˚—`/`—˚` as positional
  notation** ("as first / as final member", 409 / 4 258 — the closest
  historical precedent for the pwg_ru position marker), classic elision rings.
- **Whitney** (§561): no ring at all. Roots 1885: leading hyphen = bound stem
  (`-kartin`, `-karttṛ`; read from the
  [whit-023 scan](https://github.com/sanskrit-lexicon/csl-whitroot/blob/master/jpg/whit-023-kft2.jpg));
  Grammar: attested compounds quoted solid with accent, hyphens only in
  analysis. Böhtlingk abbreviates, Whitney classifies.
- **Mylius** (§557): **named gap** — no digitization in the org (only the
  H1153 unmarked rights-risk source); no source, no claim.

## 4. Practical residues for parsers and the RU cards

1. A ring is **three different signs**: elision (lead), truncation (trail),
   sandhi-seam (MW mid-word). PWG's majority sense is truncation — an
   "elision" reading is right ~¼ of the time there, almost always elsewhere.
2. MW↔md crosswalks must normalize `‿` vs mid-word `˚` vs nothing.
3. Apte rings need a label-vs-member disambiguation step (`<sab>` context).
4. koch.jsonl leading-hyphen lemmas are a lemma-class marker (bound second
   member) — strip for matching, keep the bit.
5. wg_text.txt line-wrap hyphens are indistinguishable from analytic hyphens —
   join wrapped lines before counting.
6. For the glyph vote: `˚` U+02DA is what 20+ CDSL digitizations use; `°` is a
   digitization variant of the same device (sch/ae/koch); `॰` only Bopp;
   Macdonell's `˚—`/`—˚` shows position can be encoded by sign ORDER, not a
   new glyph.

## 5. Candidate phenomena to measure next (same method, unmeasured)

Each is a §553-style pass: pick the marker, count it in each dictionary's own
markup, sample specimens, name the residue. Ordered by expected value for
pwg_ru / kosha work. **All ten are minted as handoffs (17-08-2026), one per
item in this order:**
[H2978](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2978-Sonnet_SanskritLexicography_typography-census-accent-digitization_17.08.26.md) (Sonnet, accent) ·
[H2979](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2979-Sonnet_SanskritLexicography_typography-census-homonym-splitting_17.08.26.md) (Sonnet, homonyms) ·
[H2980](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2980-Opus_SanskritLexicography_typography-census-sense-hierarchy-depth_17.08.26.md) (Opus, sense depth) ·
[H2981](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2981-Sonnet_SanskritLexicography_typography-census-citation-density_17.08.26.md) (Sonnet, citations) ·
[H2982](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2982-Sonnet_SanskritLexicography_typography-census-xref-conventions_17.08.26.md) (Sonnet, xrefs) ·
[H2983](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2983-Fable_SanskritLexicography_typography-census-kosha-devices_17.08.26.md) (Fable, kośa devices) ·
[H2984](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2984-Sonnet_SanskritLexicography_typography-census-root-notation_17.08.26.md) (Sonnet, root notation) ·
[H2985](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2985-Sonnet_SanskritLexicography_typography-census-inflection-abbreviation_17.08.26.md) (Sonnet, inflection) ·
[H2986](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2986-Haiku_SanskritLexicography_typography-census-prosody-marks_17.08.26.md) (Haiku, prosody) ·
[H2987](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2987-Sonnet_SanskritLexicography_typography-census-gloss-language-layering_17.08.26.md) (Sonnet, gloss languages).

1. **Accent digitization** — `/` (udātta) and `\` (svarita) in `<k2>` and
   bodies: which dicts carry Vedic accent, on what fraction of lemmas, and
   whether accent survives in compounds (PWG vs MW vs GRA vs MD disagree on
   where the accent sits in `agni/—hotra`-type lemmas).
2. **Homonym splitting** — `<h>` / `<hom>` density per dict: who splits
   agnihotra n. from agnihotra adj. as separate lemmas vs one article; drives
   any headword-join between dictionaries.
3. **Sense-hierarchy depth** — `<div n="…">` nesting profile (PWG's 1〉/a〉 vs
   Apte's numbered senses vs flat dicts); needed before importing any sense
   order into pwg_ru cards (extends §18's citation-density split).
4. **Citation apparatus density** — `<ls>` per entry, per dict: which
   dictionaries *prove* senses and which assert; the §18 measurement extended
   from 4 dictionaries to all 44.
5. **Cross-reference conventions** — `см. / s. / vide / Vgl. / q.v. / =` — the
   internal reference graph of each dict, and its ring interaction (`˚`-refs).
6. **Kośa devices** — skd/vcp (Śabdakalpadruma, Vācaspatya) showed ZERO
   Western markers: how the Sanskrit-Sanskrit kośas mark compounds instead
   (iti-quotation, devanāgarī daṇḍa segmentation) — **measured → FINDINGS
   [§564](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   (H2983): SKD spells vigraha + class term in parentheses; VCP compresses
   the same apparatus into ॰-abbreviations (`0` in the digitization) with a
   numeral for the vibhakti (`6 ta0` = ṣaṣṭhī-tatpuruṣa) — the native
   ancestor of Apte's `[za˚ ta˚]`.
7. **Verb-root notation** — `√`, class digits, present-stem citation forms:
   who lemmatizes roots vs 3sg forms (bears directly on WhitneyRoots
   crosswalks).
8. **Inflection abbreviation** — Wilson's `(-traM)`, MD's `-tas, -m` runs,
   Whitney's `-te etc.`: the leading-hyphen *inflectional* use that §558
   showed must be separated from the compound use before any expansion pass.
9. **Meter/quantity marks** — mw72's symbol list has `˘`/`—` for syllable
   quantity; who else marks prosody inline.
10. **Gloss-language layering** — German/English/Latin/Russian mixing per
    dict (`{%…%}` vs plain), for router/translation passes.

## 6. Reproduce

Census scripts (session scratchpad, throwaway — the counts are recorded
above and in the FINDINGS sections; re-derive with):
`python - <<'PY'` over `csl-orig/v02/*/<dict>.txt` counting U+02DA / U+00B0 /
U+0970 / `-` inside `<k2>`, with per-dict markup for positions (`{#˚`/`˚#}`,
`<s>˚`/`˚</s>`, `{%˚`/`˚%}`) — full recipes quoted in FINDINGS §553–§558, §561.

_Dr. Mārcis Gasūns_
