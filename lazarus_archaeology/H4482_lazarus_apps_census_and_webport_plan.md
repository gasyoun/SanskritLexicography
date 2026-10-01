# H4482 — Lazarus apps («Электронный словарь» = Saudamani, Zaliznyak): code census + web-port plan

_Created: 13-09-2026 · Last updated: 13-09-2026_

Executor: OxAlpha (opencode, z-ai/glm-5.3-flash) · Handoff: [H4482](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4482-OxAlpha_SanskritLexicography_lazarus-archaeology_09.09.26.md) · class: money (awaiting different-session Verifier) · **derived-only** — raw sources gitignored local only (`raw/`, never committed).

## 1 · Method & scope

- Read-only `rclone lsf -R yadisk:kRtam/{Электронный словарь,Zaliznyak}` — full recursive listings (214 + 805 files).
- **Source-only download** per budget: `*.pas/*.lfm/*.lpi/*.lpr/*.inc` + 3 README.md — 40 MB total into gitignored `raw/`; **no exe/zip/pdf/binaries downloaded, nothing built, nothing run** (handoff: no build risk).
- Static archaeology: unit/LOC census, `LoadFromCSV`/DB-marker grep across both trees, project-file inventory, README parsing.

## 2 · Census — tree level

| Tree | Total files | On-disk | Lazarus source | Product binaries | Verdict |
|---|--:|--:|---|---|---|
| `kRtam/Электронный словарь` | 214 | ~1.3 GB | `SRC/22102025/`: **80 .pas (~39.8k LOC), 76 .lfm, 14 .lpi/.lpr, 12 projects** | `bin/`: Saudamani v6.1 win64, v4.0, v103 Students, 2_4TLK zips, SDM4+ 7z (152 MB), `dic64.exe` 100 MB; `00000.csv` 86 MB in SRC | **one active codebase** — flagship «Saudamani» |
| `kRtam/Zaliznyak` | 805 | ~1.9 GB | `GH/` (git-tracked copy): **74 .pas (~31.9k LOC), 68 .lfm, 19 .lpr/22 .lpi, 14 projects** + 4 research sub-apps under `Высказывания/` | 273 MB git object, 189 MB unnamed blob, RV0110.txt 1 MB, 52 MB txt corpus | **same code family + unique data layer** |

Duplicate-note: ~60% of the unit inventory is byte-identical stems across the two trees (`sdm32/sdm64`, `dic32`, `RunDic`, `apteutil`, `csn1`, `texts`, `testgif`, `project12345`) — one evolving product, the Zaliznyak tree is a research fork with its own data.

## 3 · Census — projects & units (the 12+14 projects)

| Project (.lpr) | Tree | Role (from units) |
|---|---|---|
| **sdm32 / sdm64** | both | **«Saudamani» — the flagship** multi-dictionary app (bin/ ships `Saudamani_v6_1_win64.zip`) |
| dic32 / dic50 / dic64 | ESD | dictionary-viewer builds (64-bit = 100 MB exe; embedded images in .lfm) |
| RunDic | both | dictionary runner/launcher |
| Didact (+didactm.pas) | ESD | didactic/teaching module |
| texts | both | texts reader (`sys/t/texts.csv`, chapters, `111H.csv`) |
| csn1 | both | corpus/search lane (×2 variants in ZAL) |
| apteutil | both | Apte-dictionary utilities |
| charts1 | ESD | chart surfaces |
| s_update | ESD | self-updater |
| testgif / project12345 | both | test/scratch projects |
| ZAL `Высказывания/Verses` (p1) | ZAL | **verse index** over RV (`RV.txt` 1 MB; beg/end/lns/Yb/ye split indexes) |
| ZAL `Высказывания/Ядра/Names` (e1, E2) | ZAL | lexical-cores/Names query app |
| ZAL `Высказывания/Корни` (DDD + guna.pas) | ZAL | roots app (guṇa morphology) |
| ZAL `Высказывания/adj` (adj1 + load1.pas) | ZAL | adjectives app |

ZAL `GH/` READMEs self-describe: **«Zaliznyak-Kochergina: данные исследований утверждений и выводов Конспекта ЗАА и учебника ВАК»** — the research layer queries Zaliznyak's *Sanskrit Konspekt* statements against Kochergina's textbook; `Astronomy` md = unrelated side-course shipped in the same repo; `L_Base-1` = source texts.

## 4 · DB formats consumed (the data contract)

**No SQL engine anywhere** (zero SQLite/MySQL/ODBC/TSQLQuery hits in 71.7k LOC). The entire persistence layer is **flat CSV/TXT under `sys/`, loaded into `TStringGrid` via `LoadFromCSVFile` with per-file ad-hoc separators** (`#9` tab, `;`, `#`, `_`):

| sys/ path | Content | Evidence |
|---|---|---|
| `sys/t/texts.csv`, `0.csv`, `capters.txt`, `111H.csv` | reading texts + chapters | tcf.pas, unt.pas |
| `sys/rus/RAD.txt`, `AV.txt`, `RV.txt`, `M.txt`, `brn.csv`, `bra.csv` | **Russian reverse-lookup indexes** | rusk.pas |
| `sys/syn/s1.csv`, `s2.csv`, `sm/*` (`soren`, `d`, `dfx`) | synonyms module | syn.pas, df.pas |
| `sys/xlsdata/omoforms/nv.csv` | word-form (inflection) tables | code ref |
| `sys/xlsdata/vpref/v10000.csv` | verb-prefix data | code ref |
| `sys/dcs/8v.csv`, `8n.csv` | **DCS-derived** slices | code ref |
| `sys/forms.txt`, `sys/frq_P.csv`, `sys/liga/2–5.csv` | forms, frequencies, ligatures | frs.pas |
| `sys/history.sdm` | search history | sh1.pas |

Script layer: **SLP1 is the working key (231 code refs)**, IAST (15) and devanagari (5) as display targets; `keybrd.pas` (793 lines) = on-screen transliteration keyboard. Dictionary sources wired in code: **MW (46), Apte (44), PWG (20), Monier (16), Kochergina (4)**.

## 5 · Feature map → web-port plan (ruling б: port logic, kosha-like search)

| App feature (desktop) | Portable logic | Web phase | Salvage source |
|---|---|---|---|
| Multi-dict lookup MW/Apte/PWG/Monier | search + entry display over SLP1 keys | **Phase 1 (minimal web search)** | dictionaries already in csl-orig; **do NOT salvage from the app** |
| Kochergina dictionary | entry display | Phase 1 (optional) | `kRtam/Kochergina/Kochergina_unicode.docx` (already on yadisk) |
| SLP1 keyboard + script conversion (SLP1↔IAST↔devanagari) | transcoding only | Phase 1 (UI: input accept + display) | estate transcoders — never re-derive (FINDINGS §60/§629) |
| RU reverse index (`rus/*`) | second search lane, RU key → SLP1 | Phase 2 | the `sys/rus/` CSVs themselves |
| Word forms (`omoforms`, `forms.txt`, vpref) | inflection-aware lookup (form → lemma) | Phase 2 | CSVs |
| Synonyms (`syn/*`) | synonym browse | Phase 3 | CSVs |
| Texts reader + DCS slices (`dcs/8v/8n`, `texts.csv`) | aligned reading view | Phase 3 | CSVs; prefer estate DCS layers |
| **Высказывания layer** (Verses/Names/Roots/adj over Zaliznyak Konspekt × Kochergina) | statement/verse query — **unique data, exists nowhere else in the estate** | Phase 3 (its own lane) | `Высказывания/` data files (RV verse indexes, Ядра, adj, Корни) |
| Charts, gif images, Didact, s_update, VCL forms (76+68 .lfm, 1.02M lines total) | **NOT portable — discard** | — | none; VCL/LCL UI code is dead weight at port time |

**Salvage split (ruling): dictionary DATA ≠ Lazarus code.** The asset is the `sys/` CSV layer + `Высказывания/` research data (~500 MB of the 3.2 GB); the .pas logic is a thin TStringGrid viewer whose *behaviour* (SLP1 keys, per-file separators, RU indexes) ports as a spec, not as code. Nothing to revive as a desktop product — Windows-only, 100 MB monolithic exes, self-updater, no installer story.

## 6 · @DECIDE — HOW-to-port scope (phase 1 minimal web search) — human decision, MG rules

Ruling 09-09-2026 fixed **(б) port to web**; the whether is closed. Open scope forks for the @DECIDE row:

1. **Host & pattern**: extend kosha-style simple search (estate precedent: CDSL unified `/simple/` search; kosha has data hub, no end-user UI) as a new small page vs adding a dictionary lane to an existing samskrtam surface. Recommend: kosha-pattern static-first page, Phase 1 read-only.
2. **Phase-1 dictionary set**: MW + Apte only (both keyed in csl-orig, zero ingestion risk) vs including PWG (bigger, RU-translation adjacency). Recommend: MW + Apte; PWG when the RU lane wants it.
3. **Data ingest route**: register the two-four `sys/` CSVs worth keeping (rus reverse index, omoforms) as kosha datasets BEFORE any UI work, derived-only, yadisk stays the raw home. Recommend: yes — one `/census-stat`-style registration pass (~1 session) so phase 2 has a legal source of truth.
4. **Высказывания layer**: port as phase 3 alongside, or split into its own handoff family (it is a different product: Zaliznyak-Kochergina statement queries). Recommend: separate handoff family; do not let it gate phase 1.

Cost estimate (OxAlpha units): phase 1 minimal = **~2–3 sessions (~4–6 h)**: (i) MW+Apte ingest to the search surface, (ii) SLP1 input + IAST/devanagari display via estate transcoders, (iii) verify page + kosha registration rows. Phase 2 RU lane ~1–2 sessions; phase 3 Высказывания ~2–4 sessions (data audit first).

**@DECIDE (MG)**: options 1–4 above — one-word each (1a/1b, 2a/2b, 3a, 4a/4b) is enough.

## 7 · Follow-ups (NOT executed)

- `Высказывания/` data audit (RV indexes 1.07 MB RV.txt + beg/end splits; Ядра/Names; adj; Корни) — own handoff when phase 3 is ruled.
- The 86 MB `00000.csv` (ESD SRC) and 189 MB `!` blob (ZAL) were never opened (binary-size budget) — likely full dictionary dumps; inspect when the ingest handoff runs.

_Dr. Mārcis Gasūns_
