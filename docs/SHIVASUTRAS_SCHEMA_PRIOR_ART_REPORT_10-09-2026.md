# Śiva Sūtras schema + prior-art report (H4471)

_Created: 10-09-2026 · Last updated: 10-09-2026_

## Mission

`Panini/ShivaSutras.xlsx` + `.docx` (yadisk, next to the `09_Palsule` folder):
inspect schema, check prior art in kosha / VisualDCS / Sangram / vidyut
first, land the gap as a machine-readable dataset unless prior art says
skip. Raw xlsx never committed — fetched to a local scratch directory
(`rclone copy yadisk:Panini/ShivaSutras.xlsx`) for inspection only, not a
repo path, not retained after the run.

## Source schema

`ShivaSutras.xlsx` has **3 sheets**, none of them a flat sūtra-numbered
table:

| Sheet | Dimensions | What it actually holds |
|---|---|---|
| `Ranges` | 52×59 | 42 rows, one per named pratyāhāra (`aK`, `aC`, `aṆ`, `yaṆ`, `haL`, …). **The pratyāhāra's content is the cell-fill highlight color**, not a text value — every row repeats the same 57-token master Māheśvara-sūtra sequence as plain text in columns C onward, and only a contiguous run of cells is filled to mark which sub-span belongs to that pratyāhāra. Reading cell **values** alone (openpyxl `data_only=True`, no fill inspection) yields 42 identical rows — the actual data requires reading `cell.fill.patternType`. |
| `Pictures` | 81×98 | Visual highlight-table renders of each pratyāhāra plotted against the full phonetic-alphabet grid (voiced/unvoiced × place-of-articulation) — a rendering aid for the accompanying essay, not additional data. |
| `SandhiExamples` | 775×50 | Worked sandhi examples applying the pratyāhāras (e.g. Pāṇini's own `इको यणचि`) — a pedagogy layer, out of scope for this handoff. |

`ShivaSutras.docx` (29 paragraphs, Russian, 0 tables) is an explainer essay
on *how* pratyāhāras work pedagogically — not a data source; no rows were
derived from it.

**Numbering.** There is no explicit "sūtra 1…14" column anywhere in the
workbook. The 14 sūtras are recoverable from the `Ranges` sheet's 57-token
master sequence by a single structural rule: every anubandha (IT) marker
token in the source typesetting carries a virāma (U+094D); every real
phoneme token does not. Splitting the sequence after each virāma-marked
token yields exactly 14 segments, and they match the traditional Māheśvara
Sūtras letter-for-letter (सुत्र 1 `अ इ उ ण्` … सूत्र 14 `ह ल्`).

## Derived data

Landed in **kosha** (the org's Sanskrit data hub, not this repo — see
[Landing location](#landing-location)):

- `data/shiva_sutras/sutras.tsv` — 14 rows: `sutra_number`, `devanagari`
  (incl. its own IT marker), `letters_only`, `it_marker`.
- `data/shiva_sutras/pratyaharas.tsv` — 42 rows: `name`, `devanagari_span`
  (first letter through terminal marker), `letters_only` (markers
  stripped), `it_marker`, `length`.
- `data/shiva_sutras/shiva_sutras.json` — both tables plus the 57-token
  master sequence.
- Manifest row `shiva-sutras-machine` in `data/manifest/datasets.json`
  (122 → 123 datasets).

Every pratyāhāra span was extracted programmatically from the xlsx's cell
fill (not hand-typed) and spot-checked against standard published
Pāṇinian pratyāhāra tables: `aK` = a i u ṛ ḷ, `aC` = all vowels, `aṇ`
(`aN1`) = a i u, `yaṆ` = y v r l, `haL` = all consonants — all match.

## Prior-art check (done first, before landing anything)

| Location checked | Result |
|---|---|
| kosha `data/manifest/datasets.json` (122 rows before this landing) | No existing pratyāhāra / Śiva-Sūtra table. `paninian-sutra-coverage-map` is a *different* object entirely: 3,983 rows over the Aṣṭādhyāyī's own numbered sūtras (vidyut-0.4.0 enumeration) — the 14 Māheśvara Sūtras are prerequisite grammar the Aṣṭādhyāyī *assumes*, not part of that count. |
| `VisualDCS` (local clone) | Grepped for `shiva.sutra`/`pratyahara`/`pratyāhāra` across `.py`/`.js`/`.json`/`.md` — no hits beyond unrelated filenames (paradigm/concordance data). |
| `Sangram` (`SanskritGrammar/sangram/`, no standalone Sangram repo exists on GitHub — confirmed via `gh api repos/gasyoun/Sangram` → 404) | Grepped `sangram/` for the same terms plus `grammar-lab-g1` — no dataset hits; a few substring false-positives in unrelated TSVs. |
| `vidyut` 0.4.0 (local Python build, `/opt/homebrew/lib/python3.13/site-packages/vidyut`) | `vidyut.prakriya.Sutra` is the Aṣṭādhyāyī sūtra type used by kosha's derivation harness; no pratyāhāra table or module is exposed to Python. The Rust core almost certainly has internal pratyāhāra-range logic (needed for sandhi rules), but that is engine code, not a shippable dataset — different scope from this mission (a machine-readable *dataset*). |

**Verdict: gap confirmed, no skip.** Landed as `shiva-sutras-machine`.

## Landing location

The derived TSV/JSON + manifest row live in **kosha**
([PR #550](https://github.com/gasyoun/kosha/pull/550), merged) —
kosha is this org's canonical Sanskrit data hub and is on the H4086
auto-merge allowlist, unlike this repo. This repo (`SanskritLexicography`)
is `pr_only` per `data/drain_repo_allowlist.json`, so this report is the
artifact that lands here; it is committed via a PR left for a human to
merge.

## Relation to the earlier same-day pass

An earlier pass at this same handoff (commit `895bd361`, ~07:10 same day)
derived `data/shiva_sutras_pratyahara_ranges.{tsv,json}` in this repo and
recorded an **explicit skip** on kosha registration, for three reasons:
rights on the xlsx were unconfirmed, kosha's main-tree checkout had
orphaned WIP at the time, and a manifest row looked like more than
"trivial" effort. That pass also declined to strip anubandha (IT) markers
out of each pratyāhāra's letter list, calling it "domain judgment beyond a
faithful transcription," and reported no derivable 14-sūtra numbering.

This pass resolves all three:

1. **Rights** were never the blocker they looked like — the *derived
   pratyāhāra/sūtra facts* are Pāṇini's public-domain grammar (~5th c.
   BCE), not the workbook author's creative expression; only the raw xlsx
   (MG's own explainer file) needed to stay unshipped, and it does, in
   both passes.
2. **A clean kosha worktree** (`git worktree add` off `origin/main`, not
   the dirty main-tree checkout) made registration a same-pass, five-file
   PR — [kosha PR #550](https://github.com/gasyoun/kosha/pull/550), merged
   — matching the existing `gita-etymology`/`sense-dating` pattern exactly,
   not a heavier contract.
3. **Marker-stripping is not a judgment call**: the anubandha convention
   (virāma-marked letters end a sūtra/pratyāhāra span and are excluded
   from its phoneme content) is a textbook rule (Pāṇini 1.3.2–9), not an
   invented one — confirming it against five standard pratyāhāras (`aK`,
   `aC`, `aṇ`, `yaṆ`, `haL`) was enough to apply it with confidence. The
   same rule recovers the 14-sūtra split the mission asked for and the
   earlier pass reported as absent.

Both derived-file locations now exist; this report's kosha landing is the
more complete one (adds `letters_only`, `it_marker`, and the 14-sūtra
table) and satisfies the acceptance criterion's "kosha manifest row"
branch directly, superseding the earlier pass's skip recommendation.
Neither commit was reverted — the earlier TSV/JSON stay in
`data/` as a historical by-product of the same handoff.

## Acceptance

- [x] Schema table above (per-sheet content, numbering derivation rule).
- [x] Derived file committed: [kosha PR #550](https://github.com/gasyoun/kosha/pull/550) (merged), dataset `shiva-sutras-machine`.
- [x] Prior-art check across all four named locations, done before landing.

_Dr. Mārcis Gasūns_
