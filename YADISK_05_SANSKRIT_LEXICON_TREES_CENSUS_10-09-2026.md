# Yandex Disk `05_Sanskrit-Lexicon` — 19 CDSL legacy trees census (H4477)

_Created: 10-09-2026 · Last updated: 10-09-2026_

Executor: OxAlpha (opencode, z-ai/glm-5.3-flash) · Handoff: [H4477](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4477-OxAlpha_SanskritLexicography_cdsl-legacy-trees-census_09.09.26.md) · class: data (awaiting different-session Verifier) · **derived-only** (MG ruling 07-09-2026 — raw files stay on the disk).

## 1 · Method & scope

- Read-only `rclone lsf -R yadisk:Sanskrityatina/05_Sanskrit-Lexicon` — **261 files, 1.243 GiB** (`;`-separator gotcha from [YADISK_INVENTORY_07-09-2026.md](https://github.com/gasyoun/Uprava/blob/main/reports/YADISK_INVENTORY_07-09-2026.md) applied).
- Baselines probed: [csl-orig/v02](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02) (per-dict txt sizes + meta2 files), [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) v02 inventory (generator layer, no dict data), kosha `datasets.json` (124 datasets), [PWG repo](https://github.com/sanskrit-lexicon/PWG) (gh api — scans + pipeline manual), [csl-whitroot](https://github.com/sanskrit-lexicon/csl-whitroot) (284 jpg), SanskritLexicography landed assets.
- Content samples pulled and opened: `1974-SNP/snp.txt`, `1890-AP90/apte.txt` (head), `1832-WIL/Wilson_dictionary_11_12_2013_build_1.xlsx` (openpyxl), `upasarga-stat/DCS-upasarga-analysis.xlsx` (openpyxl), `upasarga-stat/nI-PWG-upasargas.txt` (head).
- **Delta vs the handoff's own count:** H4477 said «14 dict trees»; the 07-09 deep-probe listed 15; the full recurse finds **19 year-prefixed tree dirs** (1987-KAT and 1997-VIA were missed — both turn out to be 2-file duplicate stubs, see table).

## 2 · Edition-code mapping (pinned — prevents the classic PWG/PWK mix-up)

| MG's yadisk naming | Edition | Cologne code (csl-orig v02) | Evidence |
|---|---|---|---|
| `1855-PWG` | Großes Petersburger Wörterbuch, Böhtlingk-Roth, 7 vols 1855–1875 | [`pw`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pw) (pw.txt 31.5 MB) | yadisk RTF volume titles «PWG1 (A-Au) 1855 … PWG7 (Sa-Ha) 1875» |
| `1879-PWK` | Sanskrit-Wörterbuch in kürzerer Fassung, Böhtlingk 1879–1889 | [`pwg`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pwg) (pwg.txt 54.6 MB) | pwg-meta2; yadisk «Bohtlingk-PWK1-(A-Au)-1879» |
| — (inside PWK volumes) | «Nachträge und Verbesserungen» sections | [`pwkvn`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pwkvn) (3.07 MB) | pwkvn-meta2 |
| `SCH-Nachträge`, `BohtSchmidt-PWK-Nachtrage-1924` | Schmidt's Nachträge 1924–1928 | [`sch`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/sch) (4.77 MB) | sch-meta2 («N = German Nachtrag») |

## 3 · Census — 19 tree dirs

| # | Dir | Files/size | Key contents (format · date) | csl-orig counterpart | Verdict |
|--:|---|---|---|---|---|
| 1 | `1832-WIL` | 2 · 2.1 MB | Wilson build xlsx (`Лист1` 44 271×4, 12-2013) | [wil](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/wil) wil.txt 9.96 MB | **overlap** — text superseded by Cologne wil; xlsx = MG build-grid only |
| 2 | `1855-PWG` | 27 · ~300 MB | PWG master xlsx chain, `PWG_09_11_2013.htm` 99 MB, **`Boethlingk_PWGScan.csv` 31 MB + `_Devanagary.xlsx` 21 MB (devanagari!), dhatu lists 2312/1909/1257/9273-verbs, abbreviation-RegEx ×3 (~37 MB), EWA/verba side workbooks** | [pw](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pw) 31.5 MB | **overlap + UNIQUE-DELTA (star asset)** — base text superseded; devanagari scan pair, dhatu counts and abbreviation corpora exist nowhere in the estate |
| 3 | `1873-VCP` | 7 · ~28 MB | Vācaspatyam proof chain b1→b6 (16-01→01-06-2014), devanagari variants b3/b4 | [vcp](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/vcp) vcp.txt 25.1 MB | **overlap** — proof-chain = MG QA lineage; dev-variants = minor delta |
| 4 | `1879-PWK` | 4 · ~5.9 MB | `PWK mystic.xlsx`, **`PWK-1823-dhatus`** ×2, 1823-verbs | [pwg](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/pwg) 54.6 MB | **overlap + UNIQUE-DELTA** — PWK dhatu list |
| 5 | `1885-WHI` | 9 · ~1 MB | Whitney roots rows/cols (doc+txt), **`SQRT_Whitney_upasarga-stats14.xlsm`**, warnemyr URLs, Cologne-matched roots | none in csl-orig; [csl-whitroot](https://github.com/sanskrit-lexicon/csl-whitroot) = 284 jpg scans | **UNIQUE-DELTA** — Cologne-matched root tables + upasarga stats; partially landed already ([ReverseDictionary/Whitney Roots sorted by Upasarga.mdx](https://github.com/gasyoun/SanskritLexicography/blob/main/ReverseDictionary/) + «3347 приставочных корней») |
| 6 | `1890-AP90` | 6 · ~52 MB | **`apte.txt` 15.8 MB = devanagari-first keyed master («ID: अ_a», HOM numbering)**, `apte_for_split` 16.1 MB, translate xlsx 18.4 MB, fuzzy 0.26 MB | [ap90](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/ap90) ap90.txt 11.8 MB (HK/SLP1 form) | **overlap-in-source + UNIQUE-DELTA** — full devanagari keyed digitization is a parallel layer Cologne lacks; cross-check candidate |
| 7 | `1891-CAE` | 2 · 4.7 MB | Cappeller xlsx + `Capellar1.htm` | [cae](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/cae) 5.3 MB | **overlap** |
| 8 | `1893-MD` | 2 · 70.6 MB | `Macdonell.htm` 60.5 MB (display build) + b4 xlsx | [md](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/md) 6.2 MB | **overlap** — htm = old display build |
| 9 | `1928-SCH` | 2 · 8 MB | schmidt.xlsx + `schmidt_b1_test_Anton.xlsx` (MG+Anton QA) | [sch](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/sch) 4.8 MB | **overlap** — QA-lineage xlsx |
| 10 | `1955-PAL` | 1 · 0.26 MB | Palsule dhatu list | none (Palsule = H1333 lane) | **UNIQUE-DELTA** |
| 11 | `1974-SNP` | 5 · ~0.6 MB | **`snp.txt` = 453 `<H1>`-keyed entries (key1/key2/L/pc markup, 09-2014)** + dev/SLP1 headword files | [snp](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/snp) snp.txt 0.29 MB, **plain unkeyed** (0 `<H1>`, 0 key2) | ~~UNIQUE-DELTA / upgrade candidate~~ → **SUPERSEDED — no upgrade** (H4535 correction 11-09-2026: csl-orig keys every entry via `<L>/<pc>/<k1>/<k2>` meta lines since meta2 2018; 453/453 L+pc+headword parity, 451/453 folded-body identity; csl-orig copy is the newer stage — typo fix + end-matter properly unkeyed. Evidence: [YADISK_SNP_KEYED_VS_CSLORIG_PARITY_11-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/main/YADISK_SNP_KEYED_VS_CSLORIG_PARITY_11-09-2026.md). Original «plain unkeyed» verdict counted only old-format `<H1>`/`key2` tags) |
| 12 | `1985-SOAS` | 7 · ~48 MB | Turner CDIAL: `turner_soas.htm` 36 MB, 9334-wordlist xlsx, question-mark file | none (Turner not in csl-orig) | **UNIQUE-DELTA** |
| 13 | `1987-KAT` | 2 · 2.7 MB | = exact copies of `1855-PWG/Dobivaem_Panini*` | — | **junk/duplicate** |
| 14 | `1989-MYL` | 5 · ~20 MB | Mylius S-D master xlsx chain (b2/b5) + input txt | none (Mylius not in csl-orig) | **UNIQUE-DELTA** (root-level `mylius.txt` dupes also present) |
| 15 | `1997-VIA` | 2 · 1.2 MB | = copies of `Dobivaem_Verba*` | — | **junk/duplicate** |
| 16 | `2001-EWA` | 5 · ~12 MB | Palsule-EWA xlsx chain (9_1) + `ewa-dhatu-artha.txt` | none | **UNIQUE-DELTA** (dhatu lane, H4479-adjacent) |
| 17 | `2006-LIH` | 6 · ~7 MB | Lihushina masters: indl/docx/xlsx, 577-verbs, sqrt_Anton2 | none ([H4484](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4484-OxAlpha_SanskritGrammar_frish-chrestomathy-census_09.09.26.md) pilot-vol adjacency) | **UNIQUE-DELTA** |
| 18 | `2012-DCS` | 24 · ~277 MB | DCS-Moniers-roots (html/doc/zip), **`DCS_statistical_evaluation.htm` 75 MB**, praefixus xlsx ×3, **reference-statistics-MBh ×2**, Root_kjc-fs-cluster, Oliver html | [DCS](https://www.sanskrit-lexicon.uni-koeln.de/) external; 2 files already landed at this repo root | **overlap (2 files landed) + UNIQUE-DELTA** — praefixus + MBh reference stats not in estate |
| 19 | `2014-HUE` | 1 · 0.89 MB | `Huet_Dic_b6.xlsx` | [HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md](https://github.com/gasyoun/SanskritLexicography/blob/main/HeadwordLists/Huet-INRIA-Wordlist-vs-Cologne.md) (landed) | **overlap-adjacent** — b6 grid = MG working copy; Huet lane active ([HERITAGE_INRIA_ROADMAP](https://github.com/gasyoun/SanskritLexicography/blob/main/HERITAGE_INRIA_ROADMAP.md)) |

## 4 · Census — aux dirs

| Dir | Files/size | Contents | Verdict |
|---|---|---|---|
| `corrigenda` | 4 · ~21 MB | Fuzzy MW-vs-PWK correction workbooks (26-11-2013, 2014) | **UNIQUE-DELTA** — pair-level corrigenda candidate for [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections) |
| `mwsdd_v15beta` | 8 · ~21 MB | MW Windows-HLP dict; `mwtot2.txt` 16.5 MB plain | **overlap** — superseded by csl-orig [mw](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02/mw); no unique delta |
| `pwg-pwk-sch` | 17 · ~2.9 MB | PDF+RTF page pairs: PWG vols **1,2,3,4,5,7** (1855–75), PWK vol 1 (**PDF only, no RTF**), Schmidt-Nachträge 1924 (PDF+RTF) | **overlap (text side)** — full text already digitized in csl-orig pw/pwg/sch; RTF = OCR layer of these same scans, so no OCR work owed; gaps noted: **PWG vol 6 missing, PWK1 RTF missing** |
| `upasarga-stat` | 4 · ~1.8 MB | **`DCS-upasarga-analysis.xlsx` (praefixus 6 426×6 + dhatu 3 688×8)**, Whitney-stats variant, **`nI-PWG-upasargas.txt`** (ni- occurrences extracted from Cologne PWG display) | **UNIQUE-DELTA** — see §5 |
| `Jim-Peter-emailed` | 23 · ~7 MB | Scharf Mādhavīya-DhP XML, Westergaard-DhP XML ×2, whit-mw match htmls, roots.xml archive | **overlap partially** (`helpmorphids.html` already landed at repo root); **Westergaard/Scharf dhP XMLs = UNIQUE-DELTA machine-readable dhātu-pāṭhas** |
| `!Dhaval Apte` | 18 · ~110 MB | incl. **`gasuns-phd-rao/` = MG's PhD PDFs** | out of scope here — covered by [H4479](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4479-OxAlpha_SanskritGrammar_gasuns-dissertation-corpus_09.09.26.md) |
| `!macros` | 3 · ~5.3 MB | diacritics-replacement macro workshop | tool residue, no data delta |

## 5 · upasarga delta vs kosha `sanskrit-upasarga-semantics` (acceptance item)

| Side | Source | Size |
|---|---|--:|
| kosha [sanskrit-upasarga-semantics](https://github.com/gasyoun/kosha/blob/main/data/gita/upasarga_semantics.tsv) | Gita.xlsm verbs sheet | 214 rows (148 roots, 69 preverb senses) |
| yadisk `upasarga-stat/DCS-upasarga-analysis.xlsx` | DCS | **praefixus 6 426 rows ×6 + dhatu 3 688 ×8** |
| yadisk `upasarga-stat/nI-PWG-upasargas.txt` | Cologne PWG display (ni-) | 97 KB extract |
| yadisk `1885-WHI/SQRT_Whitney_upasarga-stats14*.xlsm` (×2 variants) | Whitney roots | root×upasarga stats |

**Verdict: non-overlapping sources — same theme, zero data overlap.** kosha's dataset is the Gita compositional dimension; the yadisk workbooks are the DCS/PWG/Whitney dictionary dimension. No supersession either way.

## 6 · Verdict summary

- **overlap (base text superseded by csl-orig):** WIL, VCP, PWK, CAE, MD, SCH, mwsdd, pwg-pwk-sch (RTF text side).
- **overlap + unique-delta (star):** PWG (devanagari scan pair + dhatu + abbreviation corpora), AP90 (devanagari keyed master), DCS (praefixus + MBh reference stats), WHI, HUE.
- **unique-delta (nothing in Cologne):** PAL, SOAS/Turner, MYL, EWA, LIH, corrigenda, upasarga-stat, Jim-Peter dhP XMLs, SNP (keyed markup).
- **junk:** KAT, VIA (duplicate stubs).
- **Already-landed overlap found:** `DCS_statistical_evaluation.htm`, `DCS-Moniers-roots-w-references.html`, `helpmorphids.html`, Whitney-upasarga mdx ×2 — do not re-land.

## 7 · Follow-up candidates (NOT executed — census only, MG picks)

1. Register `dcs-upasarga-praefixus` derived dataset in kosha (from §5 workbook) + join to the Gita dataset — the two-source upasarga layer.
2. ~~SNP keyed upgrade~~ — **RESOLVED no-action** (H4535, 11-09-2026): parity validation proved csl-orig v02/snp strictly supersedes the yadisk keyed file (453/453 keying parity; csl-orig has the typo fix, the properly-unkeyed end-matter and the full two-part work). Evidence: [YADISK_SNP_KEYED_VS_CSLORIG_PARITY_11-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/main/YADISK_SNP_KEYED_VS_CSLORIG_PARITY_11-09-2026.md).
3. PWG devanagari pair (`Boethlingk_PWGScan*`, 52 MB) → PWG-RU lane enrichment (root×devanagari forms).
4. `corrigenda` fuzzy MW-PWK pairs → csl-corrections enrichment.
5. Westergaard/Scharf dhP XMLs → dhatu-pāṭha machine-readable corpus (H4479 adjacency).

## 8 · Provenance & limits

- Census depth: all 261 files named+sized (full `rclone lsf -R`); content opened for 5 artifacts (snp, apte-head, Wilson xlsx, DCS-upasarga xlsx, nI extract). «overlap» verdicts rest on counterpart-size + format evidence, not byte-level diff.
- Reproduce: `rclone lsf -R "yadisk:Sanskrityatina/05_Sanskrit-Lexicon" --files-only --format sp --separator "|"` (auth: H2303 WebDAV creds); samples in `/var/folders/.../T/opencode/h4477/` (ephemeral).
- Raw files stay on yadisk — derived-only rule (MG 07-09-2026, [YADISK_INVENTORY §7](https://github.com/gasyoun/Uprava/blob/main/reports/YADISK_INVENTORY_07-09-2026.md)).
- §2 csl-orig sizes probed live 10-09-2026 against the local csl-orig clone.

_Dr. Mārcis Gasūns_
