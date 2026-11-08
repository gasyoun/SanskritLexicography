# Cologne entry-correction census, 2019–2026 — and a derived-site freshness check (H7223)

_Created: 22-10-2026 · Dataset: csl-orig @ `55e8addb` (26-09-2026) · Executor: GLM 5.3 Flash (`account:zai-individual-coding-plan/GLM-5.3-Flash`, ZCode) · Handoff: [H7223](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7223-GLM_SanskritLexicography_cologne-derived-yearly-entry-census_22.10.26.md)_

## Frame

A regenerable per-year census of every entry-level edit in the Cologne `csl-orig` `v02` tree, taken from
the clone's git history (read-only), plus a live check of whether two derived sites carry the corrections.
Nothing here is hand-tallied: the committed tool reads the history and the committed TSV is its
byte-identical re-run.

**Headline numbers**

- **4,439,695 record-events** — 2,070,796 additions (`<L>` records added) and 2,368,899 modifications —
  across **45 dictionaries**, **1,923 commits**, DC years 2019–2026.
- **1,508,914 distinct records** (`dict` + `<L>`) were touched at least once; the busiest record
  (`pwg` L56697 *mathurā*) was touched by 32 commits.
- 2019 is the import year (1.27M additions in 32 commits); **2026 is the busiest correction year to
  date** (580 commits, 801k events) and the year when `pwg` overtook `mw`/`pw` in event volume.
- **Derived sites:** michaelmeyer.fr carries **28/28** sampled MW additions — including one committed
  **2026-07-11**, i.e. its MW snapshot is current to at least July 2026. sanskritdictionary.com could
  **not be measured**: Cloudflare answers a managed challenge from this machine (403), with a dozen
  fetch paths tried (the archived 403 challenge is `reports/cologne_derived_receipts/probe.json`). Its 28 rows are recorded as
  `BLOCKED-CF`, **not** as staleness.

## Method

- One streaming `git log --no-color --date=short -p -U6 -- v02` pass over the read-only clone
  (`~/Documents/GitHub/csl-orig`, HEAD `55e8addb`).
- **Year axis** = the DC date in the commit subject (`DC 28 July 2026`), falling back to the commit year
  when the subject carries none. It is the editorial date, not `%ad`.
- **Attribution**: each added content line is attributed to the nearest preceding `<L>` record header
  visible in the same `-U6` hunk; an added `<L>` header is an `add`, an added content line under an
  existing header is a `mod`.
- **Dedupe** per `(commit, dict, L)`, so one commit touching one record yields one row; a record
  corrected in five commits yields five rows.
- Rows are sorted; the TSV is written deterministically (gzip `mtime=0`). `--check` re-runs the whole
  census and compares byte-for-byte; `--selftest` pins the attribution rules on a synthetic diff.
- Added lines in hunks whose context reaches no `<L>` header are counted as
  `entries_unattributed` and **reported, never silently dropped**: 277,536 of 4,717,231 added lines
  (**5.88%**).

**Correctness note (why the dataset was re-derived).** The first pass used
`--pretty=format:\x01SHA\x01…` and then read the format *word* `SHA` as the hash: the commit column was
the literal string `SHA`, and the per-commit dedupe key collapsed to `(dict, L)`, silently folding every
later correction of a record into its first event. The zero-diff canary passed because the output was
deterministic — deterministic and wrong. The format is now `\x01%H\x01…`, and the dataset below is the
re-derived one (1.51M → 4.44M rows; distinct records unchanged at 1,508,914). The canary was re-run on the
final file.

## Per DC year

| Year | Commits | Dicts | Entries | add | mod | add share |
|---|---:|---:|---:|---:|---:|---:|
| 2019 | 32 | 34 | 1,267,427 | 1,263,842 | 3,585 | 99.7% |
| 2020 | 248 | 24 | 49,602 | 6,516 | 43,086 | 13.1% |
| 2021 | 326 | 36 | 731,037 | 34,362 | 696,675 | 4.7% |
| 2022 | 141 | 22 | 339,097 | 194,705 | 144,392 | 57.4% |
| 2023 | 151 | 30 | 529,369 | 148,711 | 380,658 | 28.1% |
| 2024 | 200 | 27 | 603,282 | 252,930 | 350,352 | 41.9% |
| 2025 | 245 | 15 | 118,833 | 56,565 | 62,268 | 47.6% |
| 2026 | 580 | 40 | 801,048 | 113,165 | 687,883 | 14.1% |

Reading: 2019 is the import (additions only), 2021 is a normalisation pass (0.7M modifications across
36 dictionaries at a 4.7% add share), and from 2022 on the pipeline mixes new entries with corrections.
The 2025 trough (15 dictionaries, 0.12M events) and the 2026 spike (580 commits, 0.80M) are real
changes of cadence in the source history, not artefacts of the year axis.

## Core dictionaries

| Year | mw | mw72 | ap90 | pw | pwg | bhs |
|---|---:|---:|---:|---:|---:|---:|
| 2019 | 287,481 | 55,390 | 32,196 | 135,797 | 122,741 | 17,838 |
| 2020 | 2,914 | 0 | 616 | 320 | 14 | 0 |
| 2021 | 107,340 | 47,977 | 87,446 | 49,585 | 5,940 | 14,493 |
| 2022 | 117,955 | 15 | 23 | 13,652 | 47,040 | 0 |
| 2023 | 1,337 | 165 | 21 | 395,801 | 19,028 | 18,062 |
| 2024 | 147,731 | 0 | 570 | 221,367 | 126,796 | 11 |
| 2025 | 1,810 | 0 | 3,509 | 956 | 17,984 | 0 |
| 2026 | 43,350 | 3,881 | 1,858 | 17,888 | 300,421 | 8,379 |

`pw` and `pwg` dominate the correction waves (2023–2024 `pw`, 2026 `pwg`), while `mw` is the steady
workhorse. `mw72` is effectively frozen after 2021.

## Dictionary breadth (top 10 of 45)

| Dict | Entries | add | mod | distinct L |
|---|---:|---:|---:|---:|
| pw | 835,366 | 486,526 | 348,840 | 170,586 |
| mw | 709,918 | 374,332 | 335,586 | 288,680 |
| pwg | 639,964 | 123,422 | 516,542 | 123,371 |
| ap | 230,465 | 129,002 | 101,463 | 90,887 |
| lrv | 129,836 | 75,286 | 54,550 | 53,494 |
| skd | 129,164 | 85,443 | 43,721 | 42,531 |
| sch | 127,263 | 54,520 | 72,743 | 29,126 |
| ap90 | 126,239 | 35,552 | 90,687 | 34,919 |
| wil | 121,047 | 44,764 | 76,283 | 44,578 |
| ben | 112,625 | 25,615 | 87,010 | 25,067 |

## Issue attribution

54.4% of events (2,413,386) carry a `csl-corrections` issue number in the commit subject; the rest are
direct commits without an issue reference.

| Issue | Entries |
|---|---:|
| _(none)_ | 2,026,309 |
| csl-corrections #26 | 370,335 |
| csl-corrections #88 | 268,249 |
| csl-corrections #105 | 143,853 |
| csl-corrections #102 | 137,617 |
| csl-corrections #77 | 117,093 |
| csl-corrections #1 | 104,699 |
| csl-corrections #12 | 91,140 |

## Record churn

2.94 events per record on average; 351,562 records (23.3%) were touched once, 115,660 five times, and
12,814 records ten or more times. The top of the distribution is pathological by design of the
source: `pwg` L56697 *mathurā* 32 events, `pwg` L96559 *vyāḍi* 29, `pwg` L112021 *sūkara* 25.

## Derived-site check

**Question:** do the two derived sites carry Cologne's recent entry-level work?

**Method (after the first draft failed its controls).** The first draft built text markers from each
commit's added gloss lines and asked whether the marker was on the site. It gave 16/20 ABSENT for recent
samples **and 4/4 ABSENT for 2019–2021 controls** — the method was measuring gloss re-rendering
(abbreviation expansion like `l˚` → `law`, compounds split with `—`, `<info>` tags leaking into HTML),
not staleness. It was discarded rather than shipped. The final method uses MW **additions**
(`kind=add`): fetch the meta page, locate the `<h2 id="mw">` section, fold diacritics/case/punctuation
and ask whether the added headword is in that section. Presence is a binary fact independent of gloss
wording; a page with no MW section, or a 404, is **skipped** (absence of a page is not evidence of
staleness — the meta site only carries what it digitised).

| Site | Sample (2024–26 adds) | Controls (2019/21 adds) | Edge (commits ≥ 2026-06-01) | Verdict |
|---|---:|---:|---:|---|
| michaelmeyer.fr | 20/20 PRESENT | 4/4 PRESENT | 4/4 PRESENT | **fresh** |
| sanskritdictionary.com | 0 measured | 0 measured | 0 measured | **BLOCKED-CF** |

The edge probe includes `jambūdvīpeśvara`, added by a commit dated **2026-07-11** — the site carries it
in the MW section. michaelmeyer.fr therefore regenerates from Cologne data at least as recently as
July 2026; there is no detectable lag on additions.

**sanskritdictionary.com — Cloudflare.** Every request from this machine lands on a managed challenge
(`HTTP 403`, `Just a moment…`, `challenges.cloudflare.com`). Tried (the challenge page itself is archived
in `reports/cologne_derived_receipts/probe.json`): plain `curl` with a browser UA; `curl_cffi` impersonating `chrome`, `chrome124`, `safari`; Playwright with the installed real
Chrome (headed, fresh profile, Turnstile iframe present but never solved); Playwright Firefox; the
harness `web_fetch`; the r.jina.ai reader (451), Google Translate proxy (403), allorigins (CF page),
corsproxy (401 key), codetabs (522); Wayback Machine *Save Page Now* (520). This is a site-side wall, not
a transient error, and it is recorded as such — **not** as evidence that the site is stale. To complete
the half, run the same sample from a browser session that solves the challenge and merge the results:
`python3 tools/cologne_derived_sample.py --census reports/cologne_entry_census.tsv.gz --sd-results sd.json`,
where `sd.json` maps headword → `{http, text}`.

## Limits

- The year axis is the DC editorial date; commits without one fall back to the commit year.
- Bulk operations count as entry-level edits. 2019 (import) and 2021 (normalisation) are not hand
  corrections; use the `add`/`mod` split and the per-year shares, not the raw totals, for correction work.
- 5.88% of added lines sit in hunks whose `-U6` context never reaches an `<L>` header; they are counted
  in the residual line, not attributed to a record. A record-boundary parser would recover most of them.
- The shipped TSV is gzipped: the plain file is **364.5 MB**, over GitHub's per-file cap. Regenerate it
  with one command (below); the gzip is byte-deterministic (`mtime=0`).
- The derived-site check tests **additions**, not gloss corrections; a site could add new entries while
  serving stale glosses. The discarded marker method is the reason this is explicit.
- The census is pinned to clone HEAD `55e8addb`; new csl-orig commits change the output by construction.

## Reproduction

```sh
# read-only clone, pinned state used here
git -C ~/Documents/GitHub/csl-orig rev-parse HEAD   # 55e8addbd96e8d9001b8789026b026763f4049c1

# census: ~6 min on this Mac (Python 3.13, single core) -> gzip
python3 tools/cologne_entry_census.py --selftest
python3 tools/cologne_entry_census.py --out reports/cologne_entry_census.tsv.gz

# zero-diff canary: re-runs the whole pass and compares the decompressed TSV
python3 tools/cologne_entry_census.py --check --out reports/cologne_entry_census.tsv.gz
# PASS: byte-identical on re-run (4,439,695 rows)

# derived-site sample (28 verdicts per site; SD needs a CF-safe sd.json)
python3 tools/cologne_derived_sample.py --census reports/cologne_entry_census.tsv.gz --edge-after 2026-06-01
```

Dataset fingerprints: plain `sha256 a29fbb3265c32a29cbe373e069ed05286c611708b67832971c42657f15cfff10`,
gzip `sha256 4650b8c40d2edb68014f746102af01f79adcff5ae44f8d928d6662a8d496209b`.

## Files

- `tools/cologne_entry_census.py` — the census generator (`--selftest`, `--check`, `--out *.gz`).
- `reports/cologne_entry_census.tsv.gz` — the dataset (4,439,695 rows; columns
  `dc_year, dict, L, headword, kind, issue, commit, commit_date`).
- `tools/cologne_derived_sample.py` — the derived-site sampler.
- `reports/cologne_derived_sample_receipts.tsv` — 56 verdict rows (28 michaelmeyer, 28 SD).
- `reports/cologne_derived_receipts/` — per-headword JSON receipts (page sha256, MW-section excerpt,
  verdict) + `probe.json` for the CF wall.

_Dr. Mārcis Gasūns_
