# pwg_ru — Russian reuse-source map

_Created: 05-07-2026 · Last updated: 05-07-2026_

Canonical inventory of every Russian Sa→Ru reuse asset available to the `pwg_ru`
(PWG→RU) pipeline, and how to consume each — written so no future session
re-investigates what a 05-07-2026 scout (Opus 4.8) already found: **~98% of the
Russian sources MG brainstormed already exist and are wired**; the small gap
(two specialist name-glossaries) was closed the same day by
[H184](https://github.com/gasyoun/Uprava/blob/main/handoffs/H184-Sonnet_RussianTranslation_pwg_ru_reuse_sources_wiring_05.07.26.md).
See also [`src/README.md`](src/README.md) for the per-source technical contract
(schema, key hygiene, regeneration commands) — this file is the map of *what
exists and where it plugs in*, not the extraction spec.

## 1. Sa→Ru correctness authorities → `src/corpus_gate.py`

Five digitized dictionaries, extracted from SamudraManthanam's
`web/corpus_builder/jsonl/` by [`src/build_src.py`](src/build_src.py). Consumed
via `corpus_gate.lookup()` / `INDEP` + `REF`:

| Code | Dictionary | Role | Records |
|---|---|---|---|
| `koch` | Кочергина (1987) | INDEP correctness authority | 29 177 |
| `kna` | Кнауэр (1908) | INDEP correctness authority | 3 271 |
| `fri` | Фриш (1956) | INDEP correctness authority | 8 151 |
| `smirnov` | Смирнов, Симфонический словарь | INDEP correctness authority | 3 547 |
| `kow` | Коссович (1854), WIL-seeded | REF (secondary reference) | 13 488 |

Rights: koch/smirnov/fri approved-modern (copyright approval on file);
kna/kow public-domain. Printed sources mirrored 1:1 at
[`src/printed-dictionaries/`](src/printed-dictionaries/) (`KCH`, `KNA`, `KOW`).

## 2. Specialist name-glossaries → `src/corpus_gate.py` (SPECIALIST tier)

**New in H184.** Two SamudraManthanam name-index files (from the *raw*
`Data/*.txt`, not the `corpus_builder/jsonl` pipeline `build_src.py` reads),
extracted by [`src/build_glossaries.py`](src/build_glossaries.py) and
registered as `SPECIALIST` in `corpus_gate.py` — kept separate from `INDEP` so
they never enter the correctness heuristic/coverage/tune stats; they surface
only as corroborating evidence in the `specialist_glosses` card field.

| Code | Source | Records |
|---|---|---|
| `grin12` | Гринцер, словарь к «Рамаяне» I-II (2006) | 457 |
| `grin3` | Гринцер, словарь к «Рамаяне» III (2006) | 206 |

Rights unconfirmed → evidence-only by default (`RIGHTS['grin12'/'grin3']
.publishable = False` in `corpus_gate.py`), per the standing rights-before-quote
guardrail.

**Four glossaries from MG's original 6-item list were investigated and
deliberately NOT wired** — see [`src/README.md`](src/README.md#специализированные-глоссарии-имён--build_glossariespy)
for the full reasoning:
- `Словарь Потаповой.txt`, `Эрман-Темкин.txt`, `Словарь Гринцера из Бада
  Кадамбари.txt` — Cyrillic-only headwords, no IAST at all. No deterministic
  Cyrillic→Sanskrit transliterator exists (dental/retroflex collapse in
  practical Russian transcription makes one ambiguous); building a heuristic
  one now would risk silently wrong join keys inside what is used as a
  **correctness** signal for the rest of the pipeline. Flagged, not built.
- `Топоров.txt` — a name→page index into a printed encyclopedia article, not a
  headword→gloss glossary at all (`Агнихотра\t22`). Not a Sa→Ru source.

## 3. Word-aligned parallel corpus → `corpus_gate.corpus_examples()`

`corpus_lexicon.jsonl` (1.09M word-aligned Sa→Ru pairs, built by
[`src/build_corpus_lexicon.py`](src/build_corpus_lexicon.py) via DeepSeek) plus
40+ parallel Vedic/epic texts queried against SamudraManthanam's `corpus.db`
(read-only, FTS). This is the corpus-example signal in every `build_card()`
output, not a dictionary lookup. See [`SAMUDRA_INTEGRATION.md`](SAMUDRA_INTEGRATION.md).

## 4. Running-text sources — context lookup only, NOT translation memory

SamudraManthanam's FTS index over monographs/encyclopedias (Сыркин, Статьи
Махабхараты, Индуизм/Джайнизм/Сикхизм, Йога — Элиаде, samskrtam.ru lecture
transcripts) stays a **read-only context lookup**, not a source of aligned
Sa→Ru training pairs, for this map. **MG overrode that "skip" framing
05-07-2026**: these prose sources ARE to be mined into a separate, lower-
confidence `mined` TM layer — see
[H186](https://github.com/gasyoun/Uprava/blob/main/handoffs/H186-Opus_RussianTranslation_pwg_ru_tm_corpus_mining_expansion_05.07.26.md)
Track B. H186 Track A additionally aligns ~12 not-yet-added parallel Sa-Ru
texts. This map's "context only" framing applies to what `corpus_gate.py`
currently does with these sources — H186 is the tracked plan to go further.

## 5. Etymology / future additions

- **KEWA** (`Data/KEWA.txt` in SamudraManthanam) — etymology layer. Dhātus
  appear as finite verb forms (e.g. `bhavati` for √bhū) — normalize to the root
  before joining. Not yet wired; a future addition, not scoped into H184.
- **EWA**, **PD (Deccan College)** — future additions; compare against KEWA
  when they land. Not yet available locally.

## 6. Explicitly parked (not reuse candidates)

- `Dic_MW.txt` / `Dic_Apte.txt` (English) — already covered by csl-orig
  MW/AP90; sense-grounding only, not Russian TM.
- `devi-gita` — already indexed in the corpus, has Sanskrit inline; modest,
  no action needed.
- **dsg** ([samskrtam.ru/sanskrit-lexicon/dsg/](https://samskrtam.ru/sanskrit-lexicon/dsg/))
  — weak tertiary machine Sa→Ru signal; spot-check quality before any use,
  never treat as authoritative.
- **chandas** — prosody data, not a gloss source.

## Registration

This map is registered in
[`Uprava/PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
and the org-root [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
reuse index, so the org knows Russian Sa→Ru reuse for `pwg_ru` is solved and
where the one real gap (KEWA wiring, EWA/PD future adds) sits.

_Dr. Mārcis Gasūns_
