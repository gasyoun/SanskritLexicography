# Publication-Grade Sa→Ru Translation Memory — Data Statement / Datasheet

_Created: 04-07-2026 · Last updated: 22-07-2026 (H1458 Track C3 — filled per Bender/Friedman + Gebru)_

Filled per [Bender & Friedman, "Data Statements for NLP" (Q18-1041)](https://aclanthology.org/Q18-1041/)
and [Gebru et al., "Datasheets for Datasets"](https://arxiv.org/abs/1803.09010), for the
Publication-Grade Sa→Ru Translation Memory ([H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md))
and its sibling curated terminology dataset (D13). Settled repository decisions this datasheet
follows without re-deriving: `TRANSLATION_MEMORY_DECISIONS.md` D1–D14 — exact TM may auto-reuse
only when gated; fuzzy/suggestion TM is advisory; MW-derived English may affect RU only through
curated Sanskrit-to-Russian terminology (D9).

This datasheet covers **two artifacts** with materially different rights postures — read the
per-source rights table (§Composition) before reusing either one.

## A. Motivation (Gebru §1)

- **For what purpose was the dataset created?** To make the pwg_ru production pipeline's local
  translation cache into a citable, audit-grade scholarly resource: exact-reuse provenance for
  reproducibility, and a graded translation memory that can (a) support NKRYA-compatible parallel
  corpus submission and (b) be measured as retrieval context for the drafting engine (Track A6).
- **Who created it / on whose behalf?** Dr. Mārcis Gasūns (samskrte.ru / Sanskrit Lexicon project);
  translations are machine-produced (Claude Sonnet models) over public-domain source dictionaries,
  gated by deterministic scripts, no crowd-sourced or paid annotators.
- **Who funded it?** No external funding; personal research infrastructure.

## B. Composition (Gebru §2) — two pools, two rights regimes

### B1. `translation_memory/` — PWG exact-card/fragment TM (public, tracked)

- **What do the instances represent?** One row per PWG (Böhtlingk–Roth, *Sanskrit-Wörterbuch in
  kürzerer Fassung*, 1879–1889) headword card or fragment: Sanskrit key (`key1`/`iast`), the
  original German entry, and its Russian translation, sense-by-sense, with citation/example text
  (`<ls>`, `<ab>`) preserved untouched.
- **How many instances?** 2,392 records (2,175 exact-card + 217 exact-fragment) —
  `release/translation_memory/manifest.ru.json`, `artifact_sha256` pinned.
- **Rights.** PWG itself is public domain (19th-century German dictionary, author deceased >100
  years). The Russian translation is our own machine translation of that public-domain text — no
  third party holds rights over it. **Cleared for public release as-is.**
- **Is any information missing / is the dataset a sample?** This is a growing subset of the full
  pwg_ru production store (~5,580 headwords remain untranslated as of H1339); this datasheet
  covers only the promoted, gated, publication-tracked slice.

### B2. `corpus_tm/derived_only` — SamudraManthanam parallel-corpus structure (public, tracked; RU text NOT included)

- **What do the instances represent?** One row per Sanskrit content-word ↔ Russian-rendering
  alignment mined from the SamudraManthanam verse-aligned Sa↔Ru parallel corpus (131 source
  works spanning Veda, epic, purāṇa, kāvya, śāstra genres), by DeepSeek word-alignment
  (`build_corpus_lexicon.py`). Fields kept: `group`, `work`, `passage`, `slp1`, `sa` (Sanskrit),
  `kind`, `genre`, `period`, `date`, plus `rights_status`/`rights_basis`. **The `ru` field is
  never emitted into this bundle.**
- **How many instances?** 1,093,391 rows total; `derived_only.jsonl` (full, ~350 MB) is
  gitignored/regenerable (same policy as `pwg_sense_loci.tsv`); `derived_only.sample.jsonl`
  (first 2,000 rows, deterministic) is the tracked reviewable slice.
- **Rights.** The Russian halves of the 131 source works are **named, modern, in-copyright
  published translations** (e.g. П. А. Гринцер's Рамаяна, Я. В. Васильков & С. Л. Невелева's
  Махабхарата III). Per the canonical ledger —
  [SamudraManthanam `nkrya-parallel/export/RIGHTS_TABLE.md`](https://github.com/gasyoun/SamudraManthanam/blob/main/nkrya-parallel/export/RIGHTS_TABLE.md)
  (H821) — **all 131 sources are `needs_review`; zero are cleared.** `build_release_bundles.py`
  therefore treats every work as grey **by default** (fail-closed: a work absent from the rights
  table is *also* treated as grey, never assumed clear) and strips the `ru` field entirely before
  this bundle is written. The full bilingual pairs (`corpus_lexicon.jsonl`, 1.09M rows with `ru`)
  stay local and gitignored — never bundled, never pushed.
- **Per-source rights table.** See the live upstream table (linked above) for the per-work
  title/translator/rights column; do not duplicate it here (single source of truth, avoids drift).
  Four illustrative rows as of 22-07-2026:

  | Work (slug) | Title | Translator | Rights | Needs review |
  |---|---|---|---|:---:|
  | `01_ramayana-balakanda` | Вальмики. Рамаяна. Книга I. Балаканда | П. А. Гринцер | in-copyright modern academic translation — grey, no redistribution | ⚠️ yes |
  | `03_mahabharata-aranyakaparva` | Махабхарата. Книга III. Лесная | Я. В. Васильков, С. Л. Невелева | in-copyright modern academic translation — grey, no redistribution | ⚠️ yes |
  | `01_atharvaveda` | — | — | undocumented (127/131 sources have no `meta.json` sidecar — H821 metadata-loss finding) | ⚠️ yes |
  | *(remaining 128 of 131)* | — | mostly undocumented | fail-closed → treated as grey until reviewed | ⚠️ yes |

### B3. `sa_ru_terminology/` — curated terminology (D13, public, tracked)

- **What do the instances represent?** One term per PWG headword: the concise `{%...%}` core
  gloss span(s) from that headword's first sense carrying one, extracted from the same own/PD
  PWG translation memory as B1 (`terminology_build.py`) — not from MW English (sidesteps the D9
  restriction by not touching MW at all this wave).
- **How many instances?** 2,175 terms (one per distinct PWG `key1` with a gloss span) —
  `release/sa_ru_terminology/manifest.ru.json`.
- **Rights.** Same as B1 — own translation of public-domain PWG. Cleared.
- **Known limitation.** Written/PWG-derived terms only; Track B (oral) term-level feeds are not
  folded in yet (H290 is still blocked on an MG-supplied calibration sample as of 22-07-2026) —
  rerun `terminology_build.py` once B4 lands graded oral units.

## C. Collection Process (Gebru §3)

- **How was the data associated with each instance acquired?** B1/B3: Claude Sonnet models
  translate PWG headword-by-headword against the printed German, gated by deterministic
  window/audit scripts (`window_selftest.py` et al.), promoted to the publication JSONL by
  `build_tmx.py`'s legacy promotion path (2392 records carry `gate_status: legacy_promoted`).
  B2: DeepSeek aligns each Sanskrit content word in a verse to its counterpart in the existing
  (human-translated) SamudraManthanam parallel corpus — no new translation is produced, only
  alignment over pre-existing text.
- **Timeframe.** PWG TM promoted 04-07-2026 (`built_at`); corpus_lexicon alignment ongoing since
  early July 2026 (`build_corpus_lexicon.py`, resumable/append-only).

## D. Preprocessing / Cleaning / Labeling (Gebru §4)

- B1: PWG markup (`{#...#}` Sanskrit inline, `{%...%}` gloss span, `<ls>`/`<ab>` citations) is
  preserved verbatim in the publication JSONL; `terminology_build.py` strips it down to the bare
  gloss text only for the terminology dataset, not for the TM itself.
- B2: `build_release_bundles.py`'s `derived_only` path drops every field not in a fixed structural
  allowlist (`group, work, passage, slp1, sa, kind, genre, period, date`) — this is a lossy,
  one-way transform by design (the point is to guarantee no RU surface string survives it), not a
  reversible preprocessing step.

## E. Uses (Gebru §5 / Bender-Friedman "Intended Use")

- **Intended:** zero-token exact reuse for pwg_ru draft windows (content-hash + gate match only);
  advisory fuzzy/terminology prompt context; scholarly audit of provenance; NKRYA-compatible
  parallel-corpus export (B2 structure only, pending per-source clearance for RU text); retrieval
  measurement (Track A6).
- **Should NOT be used for:** citing B2 rows as containing Russian translation text (they don't,
  by construction); treating `needs_review` rights_status as clearance; using raw MW English as RU
  evidence in prompts (D9); redistributing `corpus_lexicon.jsonl` itself (gitignored, local-only).

## F. Distribution (Gebru §6)

- **Will the dataset be distributed?** Not yet — this datasheet, the reserved DOI slot (D13,
  `doi_status: reserved`, not minted), and the rights-partitioned bundles are **preparation only**.
  Publication requires a human `/publish-safety-check` pass with per-source clearance evidence
  (the H215/H1458 fence — no auto-publish, no DOI mint, no visibility flip by an agent).
- **License (once cleared):** CC-BY-SA-4.0 for the own/PD-derived artifacts (B1, B3; see
  `release/sa_ru_terminology/datapackage.ru.json`); B2's public_full status is contingent on
  future per-translator clearance and may never apply to any of the 131 current sources.

## G. Maintenance (Gebru §7)

- **Who maintains it?** Dr. Mārcis Gasūns; regenerable end-to-end via
  `terminology_build.py build` and `build_release_bundles.py build` (deterministic, no manual
  state) from the tracked PWG TM plus the local `corpus_lexicon.jsonl`.
- **Versioning.** `manifest.json`/`manifest.ru.json` `artifact_sha256` pins each build; re-run and
  diff the manifest to detect drift.

## Validation

```powershell
python src\pilot\translation_memory.py validate --lang ru
python src\pilot\translation_memory.py selftest
python src\pilot\window_selftest.py
python src\terminology_build.py selftest
python src\build_release_bundles.py selftest
python src\build_release_bundles.py --audit-rights   # the hard gate: 0 grey RU surface strings
```
