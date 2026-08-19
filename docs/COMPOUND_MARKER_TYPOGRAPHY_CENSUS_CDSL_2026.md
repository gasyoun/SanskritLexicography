# Compound-marker typography across the Sanskrit dictionaries — consolidated census

_Created: 17-08-2026 · Last updated: 19-08-2026_

Consolidates FINDINGS **§553–§558, §561, §564–§566, §571** ([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)),
measured over the [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
digitizations, the OCRed Cologne front matter (§4.5),
`RussianTranslation/src/koch.jsonl` (local-only, gitignored —
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
Каппеллера `○—` / `—○`, объявленная им в предисловии 1887 г. и повторённая
по-английски в 1891 г. (Макдонелл 1893 её наследует и даёт самый крупный
корпус вхождений, но не первенство): начало/конец различаются порядком
знаков, не новым глифом. Печатные свидетельства — §4.5 ниже; они
единственные в этом своде получены не подсчётом, а чтением автора.
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
- **Cappeller CAE/CCS** (§553–554, §571): PW convention at its endpoint —
  leading-only in practice; solid headwords; trailing single-digit noise. But
  the *declared* system is both positions: his prefaces define `○—` / `—○`
  ("das Stichwort am Anfang oder am Ende eines Compositums", 1887; "at the
  beginning / at the end of a compound", 1891) — see **§4.5**. Leading
  dominance is a usage statistic, not the convention.
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
  notation** ("as first / as final member", 409 / 4 258 — the *largest*
  attestation of the pwg_ru position marker; the *earliest* is Cappeller 1887,
  §4.5), classic elision rings.
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
   Cappeller's `○—`/`—○` (1887, printed definition — §4.5) and Macdonell's
   `˚—`/`—˚` (1893, 4 667 attestations) both show position can be encoded by
   sign ORDER, not a new glyph.

## 4.5. Printed-preface evidence — the lexicographers define the ring themselves

_Section of record: FINDINGS [§571](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
([H3143](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3143-Opus_SanskritLexicography_preface-ring-definition-cappeller-priority_19.08.26.md), 19-08-2026)._

Everything in §1–§4 is **distributional**: counted out of the CDSL markup. It
was collected without opening a single preface, and the census therefore
carried an avoidable weakness — it inferred what a sign *means* from where it
occurs. The Cologne front matter has been OCRed for **33 dictionary codes**
(see the coverage table below), and two of those prefaces state the compound
convention **in the author's own prose**, including the positional pair that
the pwg_ru vote is about.

### Cappeller, German side — CCS, Vorrede, Jena, 3 July 1887

[`CCS/prefaces/ccspref05.md`](https://github.com/sanskrit-lexicon/CCS/blob/master/prefaces/ccspref05.md)
([scan page](https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/ccspref/ccspref05.html)):

> Das Zeichen ○ geht immer auf das Stichwort oder einen sich von selbst
> verstehenden Teil desselben; ○— und —○ bedeuten also resp. das Stichwort am
> Anfang oder am Ende eines Compositums (wobei auch die Verbindung eines
> Verbums mit einer Präposition als solches gilt).

### Cappeller, English side — CAE, "Symbols", 1891

[`CAE/prefaces/caepref06.md`](https://github.com/sanskrit-lexicon/CAE/blob/master/prefaces/caepref06.md)
([scan page](https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/caepref/caepref06.html)):

> ◦— the principal word of an article to be supplied at the beginning of a compound.
> —◦ the same supplied at the end of a compound.

### What this changes in the census

| Claim as stated in §1–§4 | Correction from the prefaces |
|---|---|
| §3 · §4-6: Macdonell's `˚—`/`—˚` (409 / 4 258) is "the closest historical precedent" for a **positional** marker | Cappeller prints the identical device **six years earlier** — `○—` / `—○`, CCS 1887, restated as `◦—` / `—◦` in CAE 1891. Macdonell (1893) inherits it; he is the *largest* attestation, not the first. |
| §3 Cappeller row: "PW convention at its endpoint — leading-only in practice" | True of the counts, but incomplete as a description of the **system**: Cappeller declares both positions and both directions of the em-dash. Leading dominance is a usage statistic, not the convention. |
| The positional reading was **inferred** from where the ring sits | It is **printed**. `○` "geht immer auf das Stichwort" — the ring always stands for the headword; position of the dash, not a second glyph, encodes start vs end. |
| §4-6: "`˚` U+02DA is what 20+ CDSL digitizations use" | Unchanged for the digitizations, but the *printed* sort in the Cappeller line is a circle, and the two OCR passes disagree on how to code it — `○` U+25CB in ccspref05, `◦` U+25E6 in caepref06. Glyph variance is a digitization artefact all the way down to the front matter. |

**Consequence for `h2805_q3_deploy`** (sheet
[h2805_q3_deploy](https://gasyoun.github.io/vote/sheets/h2805_q3_deploy.html),
7 cards, groups D слой / G глиф / T тултип): the **G** group no longer needs a
purely aesthetic argument, and the **T** (tooltip) group has a citable
authority. The wording under vote — "headword at the beginning / at the end of
a compound" — is a translation of Cappeller's own sentence, in both his
languages. A tooltip may quote him rather than paraphrase the census.
This does **not** re-open the form vote (MG ruled the circle on 15-08-2026,
[H2804](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2804-Opus_SanskritLexicography_h1306-style-vote-apply_15.08.26.md));
it supplies the evidence line the deployment cards were missing.

### Preface OCR coverage — where else to look for a printed definition

Front-matter editions under `GitHub/` (source pages + `*pref_all.*`), census
19-08-2026. The Cologne front-matter
[index](https://sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/index.html)
lists 38 codes; **33 have OCRed pages, 2 are empty stubs (SKD, PUI), and the
rest are unstarted**. Pipeline: [`/cologne-preface-ocr`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-preface-ocr.md).

| State | Codes |
|---|---|
| In a dictionary repo, with consolidated edition | ACC · AP90 · BEN · BHS · BOP · BOR · BUR · CAE · CCS · GRA · INM · KRM · MCI · MD · MW · MWE · MW72 · PW · PWG · SCH · SHS · STC · VCP · VEI · WIL · YAT |
| Local staging only (`GitHub/prefaces_*`, **not on any remote**) | AE · GST · IEG · LAN · PE · PGN · SNP |
| Directory exists, no edition pages | SKD · PUI |
| Ring/circle glyph present in the OCRed front matter | **CCS** pref05 (definition) · **CAE** pref06 (symbol list) · PWG pref13–14 (errata *using* `॰`, no definition) · KRM pref02/24 (`॰` in Sanskrit abbreviations) · GST pref06 (errata) |

Only Cappeller defines it. PWG's own Vorrede does **not** — which is why the
PWG truncation sense had to be counted rather than read, and why §4-1 ("a ring
is three different signs") stands on distribution alone for PWG.

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
   any headword-join between dictionaries. **measured → FINDINGS
   [§572](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   (H2979): `<h>` density spans 0–419 per 1 000 entries across the 44 dicts —
   8 split with inline `<hom>N.` display (mw/pw/pwg/gra/md/bhs/pwkvn/ap, 0.1–53
   per 1 000), 14 split without inline display (cae/ccs/inm/pui/pe/lrv/bop/…,
   up to 419 per 1 000), 22 split nothing. The high-density class (pui/inm/pe/
   mci/lrv/bop) is genre, not policy: name-indices splitting distinct persons,
   not sense-dictionaries splitting polysemy. `agnihotra` itself splits mfn./n.
   in 6 dicts (file:line proof, §572) and stays one entry in ap/vcp/wil — a 1:2
   vs 1:1 join mismatch any headword matcher must carry.**
3. **Sense-hierarchy depth** — `<div n="…">` nesting profile (PWG's 1〉/a〉 vs
   Apte's numbered senses vs flat dicts); needed before importing any sense
   order into pwg_ru cards (extends §18's citation-density split).
   **measured → FINDINGS
   [§566](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   (H2980): `<div>` is not one device — 20 of 44 dicts carry it, but only
   pw/pwg/bor give `n` a numeric SENSE level (elsewhere `n` is a type tag:
   mw `to`/`vp`, gra `TS`); depth reaches 3 in PWG (1〉/a〉/α〉), 4 once in PW.
   The bite: 25.2 % of hierarchical PWG entries open their `<div>` run at
   `2〉` or higher, because sense 1 is printed in the head line outside any
   `<div>` (PW regularised this to 99.96 % opening at `1〉`). Ruling: only
   PWG's own sense order may enter a pwg_ru card, and only via a parser that
   recovers the head-line sense 1; Apte/Kochergina are barred structurally as
   well as by §18.**
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
   **measured → FINDINGS
   [§573](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   (H2985): Wilson is 100 % inflectional (49,487/49,487 leading-hyphen runs);
   Macdonell splits 82.9 % compound-member / 1.9 % inflectional / 15.2 % a
   third taddhita-derivational class the two-way split cannot hold; Whitney's
   Roots 1885 device is pure compound-member while his Grammar's is
   inflectional (`-arthe`/`-kṛte`, §1116) — a 4-rule disambiguation table by
   markup context, not by dictionary.**
9. **Meter/quantity marks** — mw72's symbol list has `˘`/`—` for syllable
   quantity; who else marks prosody inline. **measured → FINDINGS
   [§565](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   (H2986): 27 dicts carry breve marks, 25 carry macron; 11 show collision with
   seam notation (MW-family).**
10. **Gloss-language layering** — German/English/Latin/Russian mixing per
    dict (`{%…%}` vs plain), for router/translation passes.

## 6. Reproduce

Census scripts (session scratchpad, throwaway — the counts are recorded
above and in the FINDINGS sections; re-derive with):
`python - <<'PY'` over `csl-orig/v02/*/<dict>.txt` counting U+02DA / U+00B0 /
U+0970 / `-` inside `<k2>`, with per-dict markup for positions (`{#˚`/`˚#}`,
`<s>˚`/`˚</s>`, `{%˚`/`˚%}`) — full recipes quoted in FINDINGS §553–§558, §561.

_Dr. Mārcis Gasūns_
