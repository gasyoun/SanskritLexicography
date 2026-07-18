# Data-Reuse Manual — SanskritLexicography

_Created: 10-07-2026 · Last updated: 18-07-2026_

For the **programmer / data engineer / NLP researcher** who wants to *consume*
the data here in scripts. This manual is about the committed, reusable datasets —
their formats, encodings, traps, and rights. For the research framing see the
[Researcher Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md);
to operate the pipelines see the
[Maintainer Manual](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md).

---

## 0. Read this first — rights and what is *not* in the repo

- The repo is **public**, but it **mixes rights tiers**. The 19th-century source
  dictionaries and Böhtlingk's German are public domain; the AI Russian
  translations are **unpublished** and mostly **gitignored** (the `mw_ru`/`pwg_ru`
  translation store, TM files, learner scores). If you clone this, you get the
  *tooling and the FAIR-committed datasets*, **not** the full Russian dictionary
  text. The TMX release is gated behind rights clearance.
- Before redistributing anything from here, check
  [REFERENCES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/REFERENCES.md)
  (asset provenance), the per-dataset data statements (e.g.
  [ReverseDictionary/DATA_STATEMENT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/DATA_STATEMENT.md)),
  and — for the reverse dictionary specifically — the **rights position of
  record**, [ReverseDictionary/RIGHTS_LEDGER.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/RIGHTS_LEDGER.md)
  (W1-E, 17-07-2026): the identifiable in-copyright contribution is 14,471 /
  266,820 = 5.4% **as a LOWER BOUND**, and a "PD-only" subset **cannot be
  certified** on available data — distribution stays gated.

## 1. Encoding rules — get these right or your joins are garbage

- **Default transliteration is SLP1** in the headword keys (`aMSa`, `a/MSa`).
  Exceptions are explicitly named: the Huet/INRIA file is **Velthuis**
  (`a.mza` = aṃśa); `SCH-accents-IAST-*` and the Catalan-Pujol spine are
  **accented IAST**; `mw-apte-mcdonell-hk.txt` is **Harvard-Kyoto**.
- **BOM is inconsistent.** Some `.txt` exports carry a UTF-8 BOM (`EF BB BF`),
  some don't — even two files of the same dictionary differ. **Check
  `head -c 3 file | xxd` before reading**, strip the BOM in-code, and preserve
  the file's existing BOM state if you write it back. The org "no BOM" rule does
  **not** hold here. All files are UTF-8.
- **Filename counts are true counts, not `wc -l`.** In
  `{DICT}-unique-{key}-{N}.txt`, `N` is the entry count. Era matters for `wc -l`
  (verified across every list 18-07-2026): all 30 `then-2014/` files end WITHOUT
  a trailing newline (`wc -l` = `N − 1`); all 23 `now-2026/` files are
  newline-terminated (`wc -l` = `N` exactly).
- **Accented-IAST spines need normalizing before matching** — strip `√`,
  accents, and editorial hyphens and transcode IAST→SLP1 first. Use the org's
  canonical transcoder [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util),
  not a hand-rolled one (there is a known `devanagari_to_slp1` `ळ→x` bug in one
  copy — see org [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)).

## 2. HeadwordLists — the core reusable data

Full detail in
[HeadwordLists/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/README.md).
Naming: `{DICT}-unique-{key1|key2}-{N}.txt`, one headword per line, sorted.

- **key1** = normalized computational key — may not match any printed form; use
  for **matching, dedup, joins**.
- **key2** = closer to the printed source (keeps `-`, `--`, `/` accent, `°`); use
  for **display, citation, checking against the scan**. Not every dict ships both.
- **`then-2014/` vs `now-2026/`:** the original lists were extracted in 2014 and
  are frozen in
  [then-2014/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/then-2014);
  the current regeneration is in
  [now-2026/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026).
  They have **drifted** — e.g. AP key1 36,030 → 88,867 (+146.6%; the shipped
  file is `AP-unique-key1-88867.txt` — NOW_VS_THEN's table says 88,869 but its
  own Use-cases section and the file agree on 88,867); across the 18 comparable
  lists 1,055,081 → 1,206,381 (+14.3%, recomputed from the shipped files
  18-07-2026; the table's 1,206,384 inherits the AP drift). See
  [NOW_VS_THEN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/NOW_VS_THEN.md).
  Compare **by set**, not raw line-diff. On 6 of the 15 key2 lists (BHS, GRA,
  MW×2, SCH, VEI) the 2014 key2 is legacy numeric transliteration (`am2s4a` =
  aṃśa), so THEIR then-vs-now diff is a format migration — but the other 9
  (AP, BUR, CAE, CCS, MD, PWG, PWK, SKD, VCP) were already SLP1-style in 2014,
  and their diffs are genuine headword-change signal (per-row verdicts in
  NOW_VS_THEN.md; nuance: its MW verdict overstates — MW's 2014 key2 digits are
  homonym indexes, not legacy transliteration, per the HeadwordLists deep
  manual's 18-07-2026 re-measurement).
- **The union is the print target:**
  [union/UNION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/union/UNION.md)
  — 323,425 headwords across 15 dicts with per-dict provenance + gender.
- **Ready-made comparison:**
  [mw-apte-mcdonell-hk.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/mw-apte-mcdonell-hk.txt)
  (~202k lines, HK, MW ∪ Apte ∪ Macdonell).
- **Variant patterns:** `{DICT}-fehlerhaft-{N}.txt` hold **full XML records, not
  bare headwords**; `sanhw1.xlsx` is a 41 MB binary — load with a library, never
  open in an editor.

**Dictionary codes:** AP · BHS · BUR · CAE · CCS · GRA · INM · MD · MW · PD ·
PWG · PWK · SCH · SKD · VCP · VEI (full titles in the HeadwordLists README).

## 3. RussianTranslation — the FAIR-committed datasets

These are committed and reusable (the *translation text* is not). Details in
[RussianTranslation/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md)
§"Datasets".

| Asset | What | Path |
|---|---|---|
| Headword index | 98,639 headwords: homonym no. · lexical category · accented form · inflection index · stem class · compound segmentation · irregularities | [src/headword_index.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv) |
| Reverse paradigm index | Zaliznyak-style index token → every headword in that paradigm | [src/reverse_paradigm_index.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reverse_paradigm_index.json) |
| Paradigm statistics | stem-class / index-token distribution across the lexicon | [src/paradigm_stats.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/paradigm_stats.tsv) |
| Frictionless descriptor | data-package metadata for the grammar dataset (CC-BY-SA-4.0) | [src/datapackage.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/datapackage.json) |
| Addenda-relationship rollup | 5,603 supplement-layer senses classified vs the PWG base | [pwg_ru/relationships_rollup.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/relationships_rollup.tsv) |

The Sa→Ru **translation memory** (1.09M verse-aligned pairs + a 10,132-pair
precision-gated mined tier + a specialist glossary tier) is graded A/B/C and
exportable as standard **TMX 1.4b**
([src/build_tmx.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py))
— but the bulk TM files are gitignored pending the FAIR release; a CAT-tool user
imports the TMX once the release clears.

## 4. Other committed datasets

- **Indische Sprüche** —
  [IndischeSprueche/data/indische_sprueche.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/data/indische_sprueche.jsonl),
  7,537 records, one JSON per line: `num`, `saying_id`, `page`, `deva`, `iast`,
  `translation_de`, `source_attribution`, `notes`. **Use it as a bulk/derived
  source, never as the citable edition** — it is 76 verses short of the verified
  7,613 and comes from an unproofed Excel transcription. For anything
  citation-facing, route to
  [boesp2](https://github.com/sanskrit-lexicon-scans/boesp2) /
  [boesp1](https://github.com/sanskrit-lexicon-scans/boesp1); `Spr. N` citation
  resolution is **already shipped** in csl-orig, do not rebuild it. Only
  `translation_de` exists (no RU/EN).
- **Reverse dictionary master list** — the 266,820-line master word list
  (266,819 CRLF-terminated + 1 unterminated final line, per
  [SCHEMA.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md))
  (`ReverseDictionary/.doc.pdf/266820-reverse-Gasuns.txt`, tab-separated
  `SOURCE_ABBREV<TAB>word`, reverse-sorted) is **local-only / gitignored in the
  public repo** — never on GitHub, but present in the canonical local clone at
  that path (restored 18-07-2026 under
  [H736](https://github.com/gasyoun/Uprava/blob/main/handoffs/H736-Fable_SanskritLexicography_reverse-dictionary-dataset-recovery_11.07.26.md))
  plus two full-dump local backups (drives C and D, SHA-256
  `925e696f533d5a9607ea90fb71fae2d2e51d2cc3cb21f332c81cc43e150b9970`, 4,135,335
  bytes) — see the README's "Data location, integrity & backups" section for the
  authoritative pointers. What *is* committed and reusable: its column
  semantics + source-code→bibliography table in
  [ReverseDictionary/SCHEMA.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md),
  the canonical-version declaration in
  [ReverseDictionary/CHANGELOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/CHANGELOG.md)
  (three counts 250,026 / 255,882 / 266,820 exist as compilation stages; the
  266,820 file is canonical), and the full-folder inventory in
  [ReverseDictionary/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md).
- **Catalan-Pujol spine** —
  [HeadwordLists/Catalan-Pujol/](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/Catalan-Pujol),
  an external Sanskrit–Catalan lemma list (61,267 lines — filename count; the
  last line is unterminated, so `wc -l` undercounts by one — accented IAST
  **with BOM**, `√`-roots + udātta + compound hyphens) plus its CDSL/DCS coverage
  analysis. **Normalize heavily before matching.**

## 5. What NOT to reuse (or reuse with care)

- **The giant reference HTML/binary** —
  `DCS_statistical_evaluation.htm` (~75 MB), `DCS-Moniers-roots-w-references.html`
  (~16 MB) and
  [HeadwordLists/sanhw1.xlsx](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/sanhw1.xlsx)
  (41 MB): stream with CLI tools /
  a library; **never** open in an editor or the Read tool. (Root
  `helpmorphids.html`, ~0.75 MB, is fine to open — it was wrongly lumped in
  here before 18-07-2026.) Provenance is in
  [REFERENCES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/REFERENCES.md).
- **The gitignored translation store / TM / dashboards** — regenerable, local-only,
  and (for the translations) unpublished. Not in a clone.
- **`{DICT}-fehlerhaft-*.txt`** — these are flagged *problem* entries as XML, not
  a clean wordlist.

## 6. Findings that will bite a reuser

From [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
(cite by `§N`):

- **§7 — DCS lemma data is keyed in two transliterations** (SLP1 vs IAST across
  the two frequency files); pick the right one before joining.
- **§8 — unaccented DCS cannot distinguish present class I from VI** (117
  spurious corpus-derived class additions were reverted); don't infer verb class
  from unaccented corpus data.
- **§9 — DCS OccId and sent_id are not unique keys** (PK collisions silently
  dropped tokens/sentences before synthetic keys were added).
- **§67 — PWG article size confounds every per-entry statistic** — normalize for
  entry length before comparing counts across entries.

## 7. Reuse checklist

1. `git remote -v` — confirm you're on `gasyoun/SanskritLexicography` (personal,
   branch `master`), not an org mirror.
2. `head -c 3 file | xxd` — BOM check on every `.txt` you read.
3. Identify the transliteration (SLP1 default; IAST/Velthuis/HK exceptions are
   named) and normalize with
   [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util).
4. Use the filename `N` as the true count; compare lists **by set**.
5. Prefer `now-2026/` over `then-2014/` unless you specifically want the frozen
   2014 snapshot.
6. Check rights before redistributing; the Russian translation text is not
   yours to republish.

_Dr. Mārcis Gasūns_
