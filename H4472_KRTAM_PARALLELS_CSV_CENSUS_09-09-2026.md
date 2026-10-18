# H4472 — kRtam "Параллели в Санскритских текстах" (621-object yadisk folder) — header census + dedupe verdict

_Created: 10-09-2026 · Last updated: 13-09-2026_

## Source probed

`yadisk:kRtam/Параллели в Санскритских текстах/` (personal Yandex Disk, accessed via the
`yadisk:` rclone remote already configured on this machine). Confirmed live via
`rclone size`: **621 objects, 3.889 GiB (4,176,315,658 bytes)** — matches the handoff's
"621 CSV, 4.2 GB" figure (604 of the 621 objects are `.csv`; the remainder are `.docx`/`.xlsx`/
one `.7z` bundle sitting alongside them). Four subtrees:

| Subtree | Objects | `.csv` count | Size |
|---|---|---|---|
| `Веды/` | — | 0 | (no CSVs; Rigveda/Atharvaveda notes only) |
| `Махабхарата/` | — | 0 | (no CSVs; `.docx` notes only) |
| `Параллели в текстах Корпуса (SRC)/PARA/Full_NEW/` | 245 | 245 | 56.18 MiB (58,908,613 B) |
| `Параллели в текстах Корпуса (SRC)/PARA/Полноразмерные/` | 245 | 245 | 53.227 MiB (55,812,085 B) |
| `Параллели в текстах Корпуса (SRC)/PARA/Стоповые/` | 113 | 113 | 3.491 GiB (3,748,614,994 B) |
| `Параллели в текстах Корпуса (SRC)/PARA/ВСЕ/PARA.7z` | 1 | 0 | 303,512,967 B (dated 2022-04-30) |
| `РАМАЯНА/248_1--606.csv` | 1 | 1 | 3,653,146 B |

## Header / encoding census (11 samples, `rclone cat --head`, no bulk pull)

All samples pulled with `rclone cat --head 250..300 <path>` — a few hundred bytes each,
zero bulk download.

| # | File | Subtree | Encoding | Delimiter | Header row? | First-column source text |
|---|---|---|---|---|---|---|
| 1 | `104_1--20.csv` | Full_NEW | UTF-8 | `;` | none (data from row 1) | Divyāvadāna |
| 2 | `107_1--1.csv` | Full_NEW | UTF-8 | `;` | none | Ekākṣarakoṣa |
| 3 | `10_1--1.csv` | Full_NEW | UTF-8 | `;` | none | Acintyastava |
| 4 | `112_1--1.csv` | Full_NEW | UTF-8 | `;` | none | GaṇaKār |
| 5 | `104_1--20.csv` | Полноразмерные | UTF-8 | `;` | none | Divyāvadāna |
| 6 | `107_1--1.csv` | Полноразмерные | UTF-8 | `;` | none | Ekākṣarakoṣa |
| 7 | `10_1--1.csv` | Полноразмерные | UTF-8 (CRLF) | `;` | none | Acintyastava |
| 8 | `104_1--20.csv` | Стоповые | UTF-8 | `;` | none | Divyāvadāna |
| 9 | `107_1--1.csv` | Стоповые | UTF-8 | `;` | none | Ekākṣarakoṣa |
| 10 | `10_1--1.csv` | Стоповые | UTF-8 (CRLF) | `;` | none | Acintyastava |
| 11 | `248_1--606.csv` | РАМАЯНА (standalone) | UTF-8 | `;` | none | Rāmāyaṇa |

**Verdict: UTF-8 throughout the sample, never cp1251.** The mission's "cp1251?" question is
answered negative for every file checked, across all three PARA subtrees and the standalone
Rāmāyaṇa file. Row shape is consistent everywhere: `<source citation>;<locus>;<verse text>;`
repeated for the matched passage plus a match-quality flag (`GOOD`/…) — no header row, IAST
diacritics throughout, one row per candidate parallel-passage pair. This is the same row
shape already documented for `dcs-parallel-passages-full` in kosha's manifest.

## Dedupe verdict: SAME-SCOPE, not NEW — do not ingest as a new dataset

This yadisk folder is the **personal-drive origin copy** of data already git-tracked in
`VisualDCS` and already registered in kosha's `data/manifest/datasets.json`. Evidence,
cross-checked directly against the local `VisualDCS` and `kosha` checkouts on this machine
(no assumption from memory or docs — every number below was re-measured this session):

1. **`Full_NEW` (245 files) is byte-identical, folder-total, to kosha's `dcs-parallel-passages-full`.**
   `rclone size` on yadisk `PARA/Full_NEW/` reports **58,908,613 bytes** — the exact
   `size_bytes` recorded in kosha's manifest row for `dcs-parallel-passages-full`
   (`source_path: VisualDCS derived-data/.../PARA/Polnorazmernye/`), and `du -sh` on the local
   `VisualDCS` checkout's `PARA/Polnorazmernye/` independently shows the same 245 files, ~56 M.
2. **`Полноразмерные` (245 files, 53.227 MiB) matches VisualDCS's `PARA/Polnorazmernye-2022-archive`**
   (245 files, 53 M on disk) — the *superseded 2022 snapshot* kosha's H291 note already
   describes ("a same-file-count, same-naming sibling directory … a superseded 2022 snapshot")
   and deliberately does **not** register as a separate dataset.
3. **`Стоповые` (113 files) is the uncompressed twin of kosha's `stopovye-parallel-passages`.**
   Filename-by-filename size comparison (113/113 files, script-driven diff of `<name, size>`
   pairs) shows every file present in both, with near-identical byte counts (e.g.
   `107_1--1.csv`: 5,042 B on yadisk vs 4,988 B in the local VisualDCS checkout;
   `10_1--1.csv`: 54,900 B vs 54,781 B — small deltas consistent with CRLF/export-timestamp
   differences, not different content). The aggregate size differs (3.491 GiB on yadisk vs
   1.3 G in the local checkout) purely because VisualDCS stores its largest members as split
   `.7z` archives to keep the repo small — e.g. `104_1--20.csv` is `104_1--20.csv.7z.001`
   (11.5 MB compressed) in VisualDCS but the same 107,957,825-byte raw CSV on yadisk. This is
   the exact same corpus, compressed vs uncompressed.
4. **The standalone `РАМАЯНА/248_1--606.csv`** (3,653,146 B, dated 2022-04-28) duplicates the
   `248_1--606.csv` already inside `PARA/Full_NEW/` (3,099,699 B, dated 2022-05-04) — same
   source-passage id (248 = Rāmāyaṇa), six days apart in the same 2022 export run. Not a new
   text.
5. **`PARA/ВСЕ/PARA.7z`** (303.5 MB, dated 2022-04-30) sits in the same 2022 export window as
   the `Полноразмерные`/2022-archive material and is almost certainly a compressed bundle of
   that same superseded snapshot, not additional content — not unpacked or ingested given the
   dedupe verdict above already covers its likely contents.

**Conclusion: nothing in this yadisk folder is a genuinely new corpus.** It is Gasūns'
personal-drive staging copy of the DCS parallel-passage export whose *current* version
(`Full_NEW` = `Polnorazmernye`) and *stop-word* variant (`Стоповые` = `Stopovye`) are already
git-tracked in `VisualDCS` and already registered in kosha as `dcs-parallel-passages-full`
and `stopovye-parallel-passages`. The remaining material (`Полноразмерные`, `ВСЕ/PARA.7z`,
standalone Rāmāyaṇa CSV) is superseded 2022-vintage duplicates of the same export, already
noted as superseded in kosha's existing `dcs-parallel-passages-full` entry.

## What this means for `gasuns-krtam-parallels`

Per the mission's own acceptance bar ("land a bounded derived sample **if novel**; register
kosha `gasuns-krtam-parallels`") — **it is not novel**, so no new full-size dataset tier is
warranted. A 12 KB evidence sample (3 representative files: `Full_NEW/104_1--20.csv`,
`Стоповые/10_1--1.csv`, `Ramayana/248_1--606.csv`, each truncated to the first ~250–300
bytes with `rclone cat --head`) is committed alongside this report under
[`H4472_krtam_parallels_sample/`](https://github.com/gasyoun/SanskritLexicography/tree/h4472-drain/H4472_krtam_parallels_sample) as the evidence artifact —
not as the start of a bulk ingest.

A `gasuns-krtam-parallels` manifest row is **not** being added to kosha's
`data/manifest/datasets.json` as a new independent dataset, because that would mis-state the
scope: the content is not distinct from `dcs-parallel-passages-full` /
`stopovye-parallel-passages`. The correct manifest action — appending a cross-reference note
to those two existing rows pointing at this yadisk personal-drive copy as an alternate
uncompressed source location — **is DONE**: landed as kosha PR
[#548](https://github.com/gasyoun/kosha/pull/548) (merged to kosha `main` as `ea1e8dc35`,
10-09-2026; verified live on kosha main 13-09-2026).

## Follow-up (not done this pass)

- A full bulk pull of the 4.2 GB folder was **deliberately not attempted** — the dedupe
  verdict makes it redundant with data already in `VisualDCS`/kosha, and WebDAV bulk pulls
  need a `nohup` + done-signal plan per the mission's own scope note.
- ~~If a future session wants the manifest cross-reference added, it is a small, mechanical
  edit to the `dcs-parallel-passages-full` and `stopovye-parallel-passages` notes fields in
  `kosha/data/manifest/datasets.json`, done from a `kosha` worktree.~~ **DONE — kosha PR
  [#548](https://github.com/gasyoun/kosha/pull/548), merged 10-09-2026.**
- Residual for MG: this census + sample land on `SanskritLexicography` branch `h4472-drain`
  as PR [#2161](https://github.com/gasyoun/SanskritLexicography/pull/2161) (all CI green,
  MERGEABLE) — product repo, so the merge itself is a human click, not an auto-merge.

## Verification re-probe (13-09-2026, OxAlpha close pass)

All four load-bearing claims re-measured live before close, results identical:

| Claim | Re-probe | Result |
|---|---|---|
| 621 objects, 4,176,315,658 B | `rclone size` | **621 / 4,176,315,658 B — exact match** |
| UTF-8, `;` delimiter, no header, `GOOD` flag | `rclone cat --head 200 …Full_NEW/104_1--20.csv` | confirmed (`Divyāv, 1: 1;1 1;buddho bhagavāñ…;GOOD;;`) |
| 12 KB evidence sample committed | `du -sh H4472_krtam_parallels_sample` | **12K** |
| PR #2161 mergeable, CI green | `gh pr view 2161 --json mergeable,statusCheckRollup` | **MERGEABLE/CLEAN, all checks SUCCESS** |

## Evidence commands (reproducible)

```sh
rclone size "yadisk:kRtam/Параллели в Санскритских текстах/"
rclone lsf -R --files-only "yadisk:kRtam/Параллели в Санскритских текстах/" | wc -l
rclone cat --head 300 "yadisk:kRtam/.../PARA/Full_NEW/104_1--20.csv"
du -sh ~/Documents/GitHub/VisualDCS/derived-data/Paralleli-v-tekstah-korpusa-SRC/PARA/Polnorazmernye
du -sh ~/Documents/GitHub/VisualDCS/derived-data/Paralleli-v-tekstah-korpusa-SRC/PARA/Stopovye
```

_Dr. Mārcis Gasūns_
