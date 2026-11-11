# pwg_ru — Russian reuse-source map

_Created: 05-07-2026 · Last updated: 11-11-2026_

Canonical inventory of every Russian Sa→Ru reuse asset available to the `pwg_ru`
(PWG→RU) pipeline, and how to consume each — written so no future session
re-investigates what a 05-07-2026 scout (Opus 4.8) already found: **~98% of the
Russian sources MG brainstormed already exist and are wired**; the small gap
(two specialist name-glossaries) was closed the same day by
[H184](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H184-Sonnet_RussianTranslation_pwg_ru_reuse_sources_wiring_05.07.26.md).
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
kna/kow public-domain. The digitized records for all five live in the sibling
SamudraManthanam repo as `web/corpus_builder/jsonl/` files (`kochergina`,
`kossovich`, `knauer`, `frish`, `slovar-smirnova` — verified 11-07-2026),
consumed here via [`src/build_src.py`](src/build_src.py). An earlier claim that
the printed sources were "mirrored 1:1 at `src/printed-dictionaries/` (KCH,
KNA, KOW)" was wrong for this repo: no such directory exists (not tracked, not
on disk, not gitignored), and no printed-page (scan) mirror was located in
SamudraManthanam either — the printed-page mirror location is currently
unverified/local-only.

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
deliberately NOT wired** — see [`src/README.md`](src/README.md#специализированные-глоссарии-имен--build_glossariespy)
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

**Since H8040 (11-11-2026):** the lexicon is consume-only and **NOT
rebuildable** — the DeepSeek alignment API config was env-only, so no
reproducible regeneration exists. If `src/corpus_lexicon.jsonl` is absent
(normal for a fresh checkout), restore the verified mirror bytes per
[§7](#7-availability--verified-restore-h8040-11-11-2026) — do not rebuild.

## 4. Running-text sources — context lookup only, NOT translation memory

SamudraManthanam's FTS index over monographs/encyclopedias (Сыркин, Статьи
Махабхараты, Индуизм/Джайнизм/Сикхизм, Йога — Элиаде, samskrtam.ru lecture
transcripts) stays a **read-only context lookup**, not a source of aligned
Sa→Ru training pairs, for this map. **MG overrode that "skip" framing
05-07-2026**: these prose sources ARE to be mined into a separate, lower-
confidence `mined` TM layer — see
[H186](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H186-Opus_RussianTranslation_pwg_ru_tm_corpus_mining_expansion_05.07.26.md)
Track B. H186 Track A additionally aligns ~12 not-yet-added parallel Sa-Ru
texts. This map's "context only" framing applies to what `corpus_gate.py`
currently does with these sources — H186 is the tracked plan to go further.

**H186 outcome (06-07-2026, Opus 4.8 `claude-opus-4-8` + DeepSeek `deepseek-chat`):**
- **Track B DONE (pilot).** A `mined` TM tier now exists —
  [`src/mine_running_text.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py)
  → `src/corpus_lexicon.mined.jsonl` (gitignored), `tier: "mined"`, quarantined from the
  1.09M. Pilot mined 421 pairs from `induizm-dzhaynizm-sikkhizm` + `mify_759_ind` +
  `syrkin_tom_1_utf`; 30-row precision gate = **97% correct-equivalence, 80% useful
  meaning-gloss, 3.3% hard error** → scale approved. Design + guards + precision:
  [`pwg_ru/RUNNING_TEXT_MINING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RUNNING_TEXT_MINING.md).
- **Track A BLOCKED.** None of MG's ~12 parallel texts exist in verse-aligned jsonl the
  aligner can consume (raw GRETIL Sanskrit + separate Russian glossaries/prose only) —
  building parallel corpora is an upstream SamudraManthanam `corpus_builder` job needing
  human edition/alignment decisions. See `RUNNING_TEXT_MINING.md` § Track A status.

## 5. Etymology / future additions

- **KEWA** (`Data/KEWA.txt` in SamudraManthanam) — etymology layer. Dhātus
  appear as finite verb forms (e.g. `bhavati` for √bhū) — normalize to the root
  before joining. Not yet wired; a future addition, not scoped into H184.
- **EWA**, **PD (Deccan College)** — future additions; compare against KEWA
  when they land. Not yet available locally.
- **Leonchenko Sinonimy** — [`research/sinonimy/sinonimy.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/sinonimy/sinonimy.jsonl)
  (H1491, 26-07-2026): 47,273 rows digitized from
  [VisualDCS/derived-data/Sinonimy](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Sinonimy/README.md)
  — sense inventories + gloss-anchored Sanskrit synonym rings (verb/noun),
  evidence-only (rights unconfirmed, same posture as `grin12`/`grin3`). Digitized
  but **not yet wired** into `corpus_gate.py` — that step (SPECIALIST-tier
  registration, or a standalone PWG-sense crosswalk per the roadmap's "Sinonimy
  as its own published crosswalk" bullet) is future work.

## 6. Explicitly parked (not reuse candidates)

- `Dic_MW.txt` / `Dic_Apte.txt` (English) — already covered by csl-orig
  MW/AP90; sense-grounding only, not Russian TM.
- `devi-gita` — already indexed in the corpus, has Sanskrit inline; modest,
  no action needed.
- **dsg** ([samskrtam.ru/sanskrit-lexicon/dsg/](https://samskrtam.ru/sanskrit-lexicon/dsg/))
  — weak tertiary machine Sa→Ru signal; spot-check quality before any use,
  never treat as authoritative.
- **chandas** — prosody data, not a gloss source.

## 7. Availability & verified restore (H8040, 11-11-2026)

The consumer-path copies (`RussianTranslation/src/*.jsonl`) are gitignored and
routinely absent in a fresh checkout. An 11-11-2026 audit found
`src/corpus_lexicon.jsonl` and the seven authority/specialist sources
(`koch`, `kna`, `fri`, `smirnov`, `kow`, `grin12`, `grin3`) absent on the
COMPUTER host — **absence at the consumer path is not loss**: every one of
these files is mirrored as a Git-LFS object in the private
[`gasyoun/pwg-ru-data`](https://github.com/gasyoun/pwg-ru-data) repo under
`corpus/`.

**Restore recipe** (each file, verified on the COMPUTER host 11-11-2026):

```sh
# from any clone/worktree of gasyoun/pwg-ru-data (git-lfs >= 3.x required)
git lfs pull --include=corpus/corpus_lexicon.jsonl          # 290 MB corpus
git lfs pull --include=corpus/koch.jsonl,corpus/kna.jsonl,corpus/fri.jsonl,\
corpus/smirnov.jsonl,corpus/kow.jsonl,corpus/grin12.jsonl,corpus/grin3.jsonl
# consumer default path (build_tmx --in default, corpus_gate src/*.jsonl):
#   copy (or symlink) the restored files into RussianTranslation/src/
```

**Verification receipts (11-11-2026):**

| File | Bytes | SHA-256 | Verdict |
|---|---|---|---|
| `corpus_lexicon.jsonl` | 290,543,363 | `9f3d852f1f1424c275af2cc1823dab1b561e649320e597d3cab013068ccc4072` | byte-identical to Uprava `shadow_assets.jsonl` row `corpus_lexicon` (size + digest both match) |
| `koch/kna/fri/smirnov/kow/grin12/grin3.jsonl` | see `git lfs ls-files -l` | per-LFS pointer oid | restored; `corpus_gate.evidence_status()` → `ok`, all 5 INDEP+REF + 2 SPECIALIST present |

Consumer demonstration (same date): `python src/build_tmx.py build --in
<pwg-ru-data>/corpus/corpus_lexicon.jsonl --sample 500` →
`validate: OK — 500 <tu>, langs=ru+sa-slp1, well-formed TMX 1.4b` (exit 0), one
provenance-bearing record `tuid=cl-1229f39bdd15ee05` (`work=01_atharvaveda`,
`passage=1.4`) round-tripped with full props; restricted Russian bytes stayed
in the gitignored TMX only. `python src/corpus_gate.py lookup rAma` → 4
independent + 2 specialist glosses, `evidence_status=ok`.

**Do not rebuild the corpus.** It is consume-only / NOT rebuildable (shadow
registry status; see §3). `build_tmx.py`'s former missing-input advice
("build it first with build_corpus_lexicon.py") conflicted with that status and
was replaced by the restore recipe above; `build_tmx.py selftest` now asserts
the withdrawn phrasing can never reappear (H8040 regression check).

**Host availability, honestly** (recorded 11-11-2026, COMPUTER host):

- Registry `path_by_host.windows` names `C:\Users\user\...` (the `user` estate
  root) — that root does not exist on this host.
- H1998 `D:\Backups` mirror — the `D:` drive DOES exist on this host, but has
  no `Backups` directory (probe 11-11-2026: `D:\` lists entries,
  `D:\Backups*` empty); the mirror is therefore absent here and unverified.
- Off-machine `samskrtam.ru/guhya/corpus_lexicon.jsonl` — unreachable since
  25-10-2026 (FTPS `530 Login incorrect`, password rotated), not re-verified.
- Working verified copy on this host after the recipe above:
  `GitHub-worktrees/pwg-ru-data-h5937/corpus/corpus_lexicon.jsonl`.
- The five `build_src.py` dictionaries remain *additionally* rebuildable where
  their upstream inputs exist (SamudraManthanam
  `web/corpus_builder/jsonl/{kochergina,kossovich,knauer,frish,slovar-smirnova}.jsonl`
  — present on this host). For `grin12`/`grin3`, `build_glossaries.py` needs the
  raw `Data/*.txt` name-glossaries — **absent on this host** (no
  `SamudraManthanam/Data/` directory at all), so here the LFS mirror is the only
  route for those two. Restoring the hash-checkable mirror bytes is the cheaper
  route anyway.

## Registration

This map is registered in
[`Uprava/PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
and the org-root [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
reuse index, so the org knows Russian Sa→Ru reuse for `pwg_ru` is solved and
where the one real gap (KEWA wiring, EWA/PD future adds) sits.

_Dr. Mārcis Gasūns_
