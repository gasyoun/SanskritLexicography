_Created: 10-09-2026 · Last updated: 10-09-2026_

# Yadisk `Sanskrityatina/09_Palsule` — workbook schema census + merge/supersede/NEW verdict (H4478)

H4478 (OxAlpha `zai-coding-plan/glm-5.3-flash`, 10-09-2026) mission: schema-inspect
every Excel workbook in MG's yadisk folder `Sanskrityatina/09_Palsule/` (the
«!Gasuns Concordance» programme: BUOM-TNPEIH, the `Dhatu_*_Palsule_12_11_2013`
family, 22_october, Experimental/, Shilu Bayarin Dhatus/), cross-check against the
landed [H1333](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/data/dhatup_palsule.json)
concordance + [PALSULE_AUDIT](https://github.com/gasyoun/SanskritGrammar/blob/master/GasunsDhatu_2014/revision-2026/PALSULE_AUDIT.md)
+ [SanskritLexicography FINDINGS §63/§90](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md),
and issue a **merge / supersede / NEW** verdict per family, landing derived data
where novel. Raw XLSX stays gitignored (`pwg_ru/eval/`, line 222 of
`RussianTranslation/.gitignore`) — the [H1333](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1333-Opus_RussianTranslation_pwg-ru-dhatup-palsule-wire-from-xls_19.07.26.md)
precedent and MG's 07-09-2026 yadisk ruling (derived-only landing).

**Method.** `rclone copy yadisk:Sanskrityatina/09_Palsule --include "*.xls*"` → 39
files, 219.3 MiB / 229 923 823 bytes (24-09 listing: 28 xlsx flagged unreviewed in
[YADISK_INVENTORY_07-09-2026](https://github.com/gasyoun/Uprava/blob/main/reports/YADISK_INVENTORY_07-09-2026.md)).
Each opened read-only (`openpyxl 3.1.5`, `read_only=True`, 3-row probe per sheet);
no values modified anywhere.

## Schema census (39 workbooks, 4 areas)

Compact table — full per-sheet detail in the session's schema dump; sheets listed
`name rows×cols` with the first header cells.

| # | Workbook (area) | Sheets | Shape | Header (first sheet) |
|---|---|---|---|---|
| 1 | `Palsule_Artha_24_01_2014.xlsx` (root) | 4 | 8 171×11 | # · Text · page · Описание · Корень с метками · Корень · Метки |
| 2 | `Palsule_Artha_plus_Withney(L)_Apte(N)_28_01_2014.xlsx` (root) | 5 | 8 171×14 | # · Text · page · Description · Dhatu_with_lable … + Apte_translate 6 325×2 |
| 3 | `DCS-6427-dhatus_kjc-fs-cluster.xlsx` (root) | 1 | 6 428×5 | ## · WORD · A.P.U. · Minning · URL |
| 4 | `dhatu-index(Panini).xlsx` (root) | 3 | 2 253×15 | धातुः · गणः · इट् · प॰/आ॰ · उपदेशः · रूपान्तरम् · अर्थः |
| 5 | `Dhatu-Gasuns-v13-25-12-13.xlsm` (root) | 17 | 3 693×16 master | # · root · Palsule страница · gana · typology … + Dhatu Concordance 3 684×23 (Palsule·Panini·Bucknell·Whitney·Huet·Werba) |
| 6-12 | `!Gasuns Concordance/Dhatu_{Bucknell,EWA,Lihushina,Oliver_PWK,Panini,Verba,Whitney}_Palsule_12_11_2013.xlsx` ×7 | 4-5 | ~1 305×(8-18) staging | √## in Palsule · √Palsule · ## · OUT Dhatu · Ablaut Roots · (+ per-source pages) |
| 13 | `!Gasuns Concordance/22_october.xlsx` | 2 | 7 394×21 | Palsule Dhātupāṭha · Whitney Roots · Mayrh. EWA · Verba VIA I (+PWG/PWK) |
| 14 | `!Gasuns Concordance/22_october_macros-granici-strochek.xlsx` | 4 | 9×10 | prototype for row-boundary macros |
| 15 | `!Gasuns Concordance/BUOM-TNPEIH_255k-14src_b3.xlsx` | 3 | **255 083×20** | # · Text_origin · acc · inm · pex · vie · pui · bhs … (14 source cols) |
| 16 | `!Gasuns Concordance/Gasuns-Dhātupāṭha-Concordance (Dhatu_Merge_table_160813…).xlsm` | 12 | 7 379×21 | Final + per-source sheets (PWK 2 555×100, PWG_original 3 302×6 …) |
| 17 | `!Gasuns Concordance/Gasuns-Dhātupāṭha-Concordance (Merge_table_Final).xlsm` | 5 | 7 385×13 | **Финальная таблица**: Palsule (корень·стр.·№№) \| PWG (том-кол.·№№) \| PWK (том-кол.·№№) \| Whitney Roots (корень·стр.·№№) \| EWA (том-кол.·№№) \| Verba (корень) |
| 18 | `!Gasuns Concordance/Udareniya_07_01_2013_b3.xlsx` | 1 | 20 248×25 | # · List with accent · Where accent · IAST/SPL1 · syllables |
| 19 | `!Gasuns Concordance/Udareniya_b5.xlsx` | 2 | 105 979×9 | # · Full · Есть Ударения · Dev · HK/IAST with accept |
| 20 | `!Gasuns Concordance/XML_ALL_START_27_01_2014_переделанный Апте.xlsx` | 16 | 213 59×6 hue… | 14 source wordlists (acc/inm/pex/vie/pui/bhs/bur/skd/stc/apt/pwg/wil/pwk/mwe) — BUOM's input side |
| 21 | `!Gasuns Concordance/concordance-PhD.xlsx` | 3 | 7 379×13 | october Final-family revision |
| 22 | `!Gasuns Concordance/dhatu-index.xlsx` | 3 | 2 253×15 | = #4 (copy) |
| 23 | `!Gasuns Concordance/dybo-whitney.xls` | — | legacy `.xls` | unreadable by openpyxl (needs LibreOffice/xlrd); 4 KB |
| 24-29 | `!Gasuns Concordance/tmp/` — `10-rootlists-concordance_v1`, `BUOM-TNPEIH_269k-13src_b15`, `BUOM-TNPEIH_b1`, `ConcorDance_New`, `Dhatu-Gasuns-Sorting4`, `Dhatu-Gasuns-v13-21-05-14`, `SQRTv19` | 1-18 | intermediates | incl. **b15: 269 055×18 — a NEWER BUOM build than the mission-named b3** |
| 30-37 | `Experimental/` — `Dhatu-v01`, `Netochnie_vhozhdeniya_300913 (Panini)`, `Netochnie_vxohdeniya5 (EWA)`, `PWG_PWK_verb-endings-color`, `STARLING_Dybo_Export/` ×4 | 1-16 | byproducts | imprecise-match worksheets, verb endings, STARLING export prep (Dybo lane) |
| 38-39 | `Shilu Bayarin Dhatus/Bayarins-dhatu-index.xlsx`, `Panini-dhatu-index1.xlsx` | 2-3 | 2 253×12-15 | धातुः · गणः … DEV + IAST sheets (arthaḥ in IAST) — Bayarin-edition Pāṇinian index |

## Verdict (cross-checked against the landed lineage)

The landed lineage = `src/data/dhatup_palsule.json` (coordinate → Palsule artha,
built from #1) + `pwg_ru/eval/` raws. This census adds the other half of MG's own
2013-14 Concordance programme.

| Corpus item | Verdict | Where it lands |
|---|---|---|
| #1 `Palsule_Artha_24_01_2014.xlsx` | **ALREADY LANDED** | md5 `f44bc9596cb252a6637c9aad33436465` **byte-identical** to the `pwg_ru/eval/` copy — it IS H1333's source of record; nothing to merge |
| #3 `DCS-6427…xlsx` | **ALREADY LANDED** (local eval/) | [survey §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/REUSE_SURVEY_DHATUPATHA_COORDINATE_SOURCES_07-09-2026.md); its URL column stays unverified-as-href |
| #17 `Merge_table_Final.xlsm` «Финальная таблица» | **NEW → LANDED** | [`src/data/dhatup_multisource_crosswalk.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/data/dhatup_multisource_crosswalk.json) via [`src/build_dhatup_multisource_crosswalk.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dhatup_multisource_crosswalk.py) — see below |
| #13/#16/#21 Final-family revisions (22_october, Dhatu_Merge_table_160813, concordance-PhD) | **SUPERSEDED** by #17 for landing | #17 is the only sheet with page and № as *separate* columns and the only one with a populated «Статистика» (18 457 cells audited by the author); siblings kept as the author's revision trail, named in the JSON provenance |
| #6-12 `Dhatu_*_Palsule_12_11_2013` ×7 | **MERGED** into #17 | staging books behind the Final merge; their «Dhatu» sheets are 1 048 576-row formula grids — the published content is the Final table, no residual novel columns |
| #5, #24-29 master/intermediate builds (v13, Sorting4, SQRTv19, Dhatu-v01, ConcorDance_New, 10-rootlists) | **REGISTERED, not landed** | earlier revisions of the same programme; #17 post-dates them |
| #15 `BUOM-TNPEIH_255k-14src_b3` + #20 `XML_ALL_START` | **NEW CLASS — not landed (skip, explicit)** | a **word-form concordance** (255 083 forms × 14 dictionary/corpus sources: acc/inm/pex/vie/pui/bhs/bur/skd/stc/apt/pwg/wil/pwk/mwe) — a different artifact class from the dhātupāṭha coordinate lane; 255k rows out of a 60-min unit's scope. Note: `tmp/BUOM-TNPEIH_269k-13src_b15.xlsx` is a **newer build than the mission-named b3** — any successor lane starts from b15 |
| #4/#22/#38/#39 `dhatu-index(Panini)` + Bayarin ×2 | **NEW — registered pointer** | Pāṇinian-numbered dhātu index (2 253 dhātus, Devanagari + IAST artha) — exactly the root-join artha-witness family survey §2/§3 said was absent from this machine. Landing = successor unit (root-keyed join like vidyut), not this pass |
| #18/#19 `Udareniya_*` | **OUT OF SCOPE** | accentuation lane, not dhātu concordance |
| #30-37 Experimental/ (Netochnie, verb-endings, STARLING_Dybo_Export) | **OUT OF SCOPE** | byproducts + the Dybo STARLING collaboration lane |
| #14, #23 macros prototype, `dybo-whitney.xls` | **skip** | 9-row prototype; legacy .xls unreadable without LibreOffice |

## The landed artifact — `dhatup_multisource_crosswalk.json`

One JSON record per non-blank spreadsheet row, **verbatim** (nothing normalized,
matched, or re-ordered), 13 fields: `palsule_root/page/no`, `pwg_volcol/no`,
`pwk_volcol/no`, `whitney_root/page/no`, `ewa_volcol/no`, `verba_root`.

| Quantity | Value |
|---|---|
| Rows (non-blank) | 5 183 |
| Palsule root entries | 3 690 (of Palsule's ~3 694-root list) |
| PWG том-кол. filled | 2 390 (№: 1 643) |
| PWK том-кол. filled | 1 983 (№: 1 528) |
| Whitney root / page / № | 1 692 / 930 / 1 673 |
| EWA том-кол. / № | 841 / 1 210 |
| Verba root | 617 |
| Rows with all six witnesses | 178 |

Spot-checks (re-read from the workbook, not from the JSON): row 100
`1an` Palsule 3/49 → PWG 1-0164/53, PWK 1-037/13, Whitney 12/I-72, EWA 5/273,
Verba 256; row 1420 `gam` Palsule 33/709 → PWK 2-152/332, Whitney 169/I-465;
row 1424 `gambh` Palsule 33/711 with all witness cells empty (MG's own merge
state, preserved as-is). Empty = the author's build had no entry there; this
artifact records his merge state, it does not complete it.

Relationship to the landed concordance: `dhatup_palsule.json` answers "what does
Palsule record for this root spelling" (artha, tooltip); the crosswalk answers
"where does each of the six traditions print this root" (PWG/PWK volume-column,
Whitney page-№, EWA volume-№, Werba №). Join key between them: the Palsule root
string — with the same homonym caveat as H1333 (spelling-keyed joins smear
homonyms; FINDINGS §90's abstain rule still applies to any consumer).

## Acceptance / evidence (H4478 contract)

- **Done looks like:** schema census of all 39 workbooks (this document) +
  per-family verdict + the novel derived merge committed.
- **Prove with:** `python3 RussianTranslation/src/build_dhatup_multisource_crosswalk.py`
  prints the counts table above from the gitignored raw; spot-check rows 100/1420/1424
  re-read from the workbook match.
- **On our data:** md5 of #1 equals the landed eval/ raw (supersede test = negative);
  counts cross-checked against the author's «Статистика» sheet (18 457 cells,
  12 898 empty — same order as the extracted 5 559 non-empty data cells).
- **Fail =:** a workbook opened but not recorded here, or a verdict without the
  artifact/pointer it names. Neither happened; #23 (`dybo-whitney.xls`) is the one
  workbook whose *sheet schema* is unreadable without LibreOffice — recorded as such,
  not silently dropped.

**Risks:** values copied verbatim include the author's own abbreviations
(`том-кол.` shapes like `1-0164`, Whitney `I-72`); consumers must not parse them
without this document. The JSON is a snapshot of MG's 2013-14 merge state, not an
authoritative edition of any dhātupāṭha.

_Dr. Mārcis Gasūns_
