# pwg_ru — running-text term mining (the `mined` TM tier)

_Created: 06-07-2026 · Last updated: 06-07-2026_

Design + pilot record for **H186 Track B**: mining Sanskrit→Russian term glosses out of
Russian **running prose** (monographs, term-encyclopedias, lecture transcripts) that
carries *no* verse-level alignment, into a **separate, lower-confidence `mined` TM
layer** — kept strictly apart from the clean 1.09M verse-aligned
[`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py).

Handoff:
[H186](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H186-Opus_RussianTranslation_pwg_ru_tm_corpus_mining_expansion_05.07.26.md)
· map context:
[REUSE_MAP.md §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md).
Model: orchestration + this design = Opus 4.8 (`claude-opus-4-8`); extraction =
**DeepSeek** `deepseek-chat` (`--backend` = direct `api.deepseek.com`), temperature 0,
JSON mode.

## Why a separate tier (not the 1.09M corpus)

Verse-aligned texts give a *word-for-word* Sa↔Ru pairing that
[`build_corpus_lexicon.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)
can align deterministically. Running prose does not: it *mentions* Sanskrit terms and
glosses *some* of them in passing ("Дити (др.-инд. *Diti*, букв. «связанность»)"). That
is genuine lexical evidence, but noisier — proper-name transliterations, contextual
(not lexical) glosses, and list-scoping mistakes all creep in. So mined pairs land in
[`src/corpus_lexicon.mined.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py)
tagged `tier: "mined"` and are **never** written into `corpus_lexicon.jsonl`. Harvest/QA
weight the `mined` tier **below** the dictionaries and the verse-aligned corpus.

## The 166k-hallucination guard applies here too

The prior corpus build let DeepSeek fabricate fluent Russian for translations that did
not exist (81% invention). Mining has the same risk in a new shape — the model
supplying a gloss from *world knowledge* instead of *the passage*. Guards (all in
[`mine_running_text.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py),
reusing `build_corpus_lexicon`'s `has_cyr` / `to_slp1` / `REJECT_RU`):

1. **Never-invent system prompt** — the gloss MUST be stated in *this* passage; a term
   named but not glossed is omitted.
2. **`ru` verbatim-in-passage check** — a deterministic backstop: if the extracted
   Russian gloss does not occur as a substring of the source passage, the row is
   dropped. This alone kills world-knowledge fabrications the prompt lets slip.
3. **`has_cyr(ru)`** — a "gloss" with no Cyrillic is a placeholder/echo → dropped.
4. **`ru != sa`, not in `REJECT_RU`** — no echoing the Sanskrit, no refusal strings.
5. **`to_slp1(sa)` non-empty** — `sa` must transliterate to a real SLP1 key; a
   Cyrillic-only "term" with no IAST is dropped.
6. **Per-passage dedup** on `(slp1, ru)`.

## Pipeline

```
python mine_running_text.py test  <textfile> [N]           # extract + print, no write
python mine_running_text.py mine  <textfile> [N] [workers]  # → corpus_lexicon.mined.jsonl
python mine_running_text.py mineall [--min-tb 15] [--include a,b] [--exclude c] [--plan] [--workers 8]
python mine_running_text.py status                          # rows + distinct keys + per-source
```

## Batch scan (`mineall`) — the deterministic selection rule (H224)

[`mineall`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py)
scans **every** `*.jsonl` in SamudraManthanam's `web/corpus_builder/jsonl/`, applies the
rule below, and mines each selected source resumably (cheap sources first,
`kommentarii-k-makhabkharate` LAST). `--plan` prints the selection with term-bearing
counts and makes no API calls. **Every skip is logged with its reason — no silent caps.**

1. **Skip verse-aligned works** (the 116 in `corpus_lexicon.jsonl`) — Track A's domain,
   not running text. The skip-set is read from the live corpus if present, else from the
   committed
   [`pwg_ru/aligned_works.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/aligned_works.txt)
   (the corpus is gitignored, absent in fresh worktrees).
2. **Skip registered dictionaries / glossaries / non-Sanskrit** (`DENYLIST`, 18 works:
   `kochergina, knauer, frish, slovar-smirnova, kossovich, kewa, dic_mw, dic_apte, dsg,
   erman-temkin, fasmer-dr-ind, slovar-potapovoy, slovar-grintsera-iz-ramayany-1-2,
   slovar-grintsera-iz-bada-kadambari, ramayana-3-slovar, toporov, warnemyr,
   iliada_gnedich`).
3. **Skip the `ukazateli-makhabkharaty` index** by name (17,915-line MBh index, 29
   term-bearing, 0%).
4. **Skip low-yield** sources whose term-bearing passage count `< --min-tb` (default 15):
   `mify-drind` (12), `pandey` (9), `buddhacharita-balmont` (5), `vishnu-purana` (2),
   `13_mahabharata-anushasanaparva` (0 — all-`…` Russian).
5. Mine everything left, resumably.

Over the 148-file folder this selects **8 sources** (18 denylist + 116 aligned + 1 index
+ 5 low-yield = 140 skipped, all logged). One delta from the H224 handoff's illustrative
Step-2 table: `stepanyants` (472 term-bearing, a philosophy term-encyclopedia the doc had
listed as "queued") is selected by the rule and mined — the rule is authoritative, so it
is included, not dropped.

- **Candidate pre-filter** (`term_bearing`) — a passage is sent to DeepSeek only if it
  carries an IAST diacritic, Devanagari, or a Sanskrit-origin marker (`санскр`,
  `др.-инд.`, `от корня`, `букв.`). Keeps cost and false-positive rate down.
- **Resumable** by `(work, passage)` — re-running skips already-mined passages.
- **Row schema**: `{slp1, sa, ru, work, passage, group, kind:"mined", tier:"mined"}`.
- Output is gitignored (`RussianTranslation/src/*.jsonl`) — code + this doc + the
  row-count/precision deltas are the deliverable, not the bulk `.jsonl`.

## Sources

| Source (SamudraManthanam jsonl) | Shape | Yield |
|---|---|---|
| [`induizm-dzhaynizm-sikkhizm`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md) | philosophy term-encyclopedia (headword + inline gloss) | high, clean |
| `mify_759_ind` | mythological encyclopedia (`Term (др.-инд. X, «gloss»)`) | high, clean |
| `syrkin_tom_1_utf` | running scholarly prose, terms scattered | lower, noisier |
| `stepanyants`, `stati-makhabkharaty`, Eliade-Yoga, `biruni` | prose monographs / encyclopedias | **mined** (scale phase — see below) |
| `pandey` | prose monograph | skipped — 9 term-bearing < min-tb 15 |
| samskrtam.ru lecture transcripts (`/l/…`) | **Sanskrit verse + Russian exegesis** | route to **Track A** (parallel-ish), not mined here — see below |

## Pilot (06-07-2026)

Mined 3 sources → **421 pairs, 0 API failures**, 408 distinct `(slp1, ru)`:

| Source | Term-bearing passages | Mined pairs |
|---|---|---|
| `induizm-dzhaynizm-sikkhizm` | 120 | 226 |
| `mify_759_ind` | 120 | 160 |
| `syrkin_tom_1_utf` | 41 | 35 |

### Precision gate

Stratified deterministic 30-row sample (~10/source), each adjudicated against its source
passage (sample kept at
[`pwg_ru/running_text_mining_precision_sample.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample.jsonl)):

| Verdict | Count | Rate |
|---|---|---|
| Correct meaning-gloss (e.g. `itihāsa`→эпос, `Duryodhana`→«с кем трудно сражаться») | 24 | 80% |
| Correct but low-information transliteration / proper-name (`Kṛṣṇa`→Кришна, `kāma`→кама) | 5 | 17% |
| **Hard error** (`asteya`→«отказ от 5 видов недолжного поведения» — grabbed the list *category*, not the item's meaning) | 1 | 3.3% |

**Correct-equivalence precision = 29/30 (97%); useful meaning-gloss precision = 24/30
(80%); hard-error rate = 3.3%.** The single hard error is a list-scoping mistake (a term
that is one of an enumerated set gets the set's description). The verbatim-in-passage
guard held — zero fabricated (not-in-passage) glosses survived to the sample.

## Scale run (H224, 06-07-2026) — whole corpus folder via `mineall`

The pilot's "proceed" decision was executed at folder scale with `mineall`. Extraction =
DeepSeek `deepseek-chat`; orchestration + adjudication = Opus 4.8 (`claude-opus-4-8`).
The small/new sources were mined and precision re-gated **before** committing to the
6,291-passage commentary. Final per-source `mined` counts:

| Source | Term-bearing passages | Mined pairs | Notes |
|---|---|---|---|
| `yoga-…-eliade-…` (Yoga: Immortality & Freedom) | 23 | 72 | new |
| `biruni` (al-Bīrūnī, India) | 33 | 280 | new |
| `syrkin_tom_1_utf` | 41 | 36 | pilot (re-mined; `mined.jsonl` absent in fresh worktree) |
| `induizm-dzhaynizm-sikkhizm` | 181 | 323 | pilot source, finished |
| `mify_759_ind` | 223 | 333 | pilot source, finished |
| `stepanyants` (philosophy encyclopedia) | 472 | 1,248 | new |
| `stati-makhabkharaty` | 495 | 596 | new |
| `kommentarii-k-makhabkharate` | 6,291 | 7,244 | new — dominant cost, run LAST (incl. mop-up) |
| **Total** | **7,759** | **10,132** | 8 sources; distinct `(slp1, ru)` = 8,576 |

**API failures (logged, not silent):** the first `kommentarii` pass hit **227** DeepSeek
read-timeout failures (transient `_ssl` / `read timeout=10.0`) that exhausted all 6
retries; those passages wrote no rows. A single resumable mop-up re-run (the miner skips
already-mined `(work, passage)`) re-scanned the 1,733 not-yet-done passages and recovered
**all 227 → +385 pairs, 0 failures**. Final residual: **0**. All other sources: **0
failures** on the first pass.

### Precision gate on the NEW material (30-row stratified sample)

Fresh deterministic 30-row sample across the 5 new sources (biruni / stati-makhabkharaty /
Eliade / stepanyants / kommentarii), 6 rows each, each gloss adjudicated against its
source passage. Sample kept at
[`pwg_ru/running_text_mining_precision_sample_scale.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/running_text_mining_precision_sample_scale.jsonl):

| Verdict | Count | Rate |
|---|---|---|
| Correct meaning-gloss (`yaj`→«совершать жертвоприношение», `ghṛta`→«топленое масло», `Bhāvanākrama`→«Ступени созерцания») | 22 | 73% |
| Correct but low-information (proper-name / river / person / text ident.: `Durga`→дурга, `pulomā`→«супруга Бхригу…», `vipāṭa`→«третий младший брат Карны») | 7 | 23% |
| **Hard error** (`anāhata`→«звук» — grabbed from an adjacent Mūlādhāra-chakra clause: list/context mis-scoping) | 1 | 3.3% |

**Correct-equivalence precision = 29/30 (97%); useful meaning-gloss = 22/30 (73%);
hard-error rate = 3.3%.** Statistically identical to the pilot (97% / 80% / 3.3%). The
slightly lower meaning-gloss share reflects the new sources (al-Bīrūnī's rivers, MBh
commentary's persons) carrying more proper-name/identifying glosses — low-information but
not wrong. The single hard error is again the **list/context mis-scoping** mode H186
flagged; the verbatim-in-passage guard held (zero fabricated glosses in the sample).

### Decision

**Scale complete — tier stays quarantined and down-weighted.** Precision clears the bar
for a lower-confidence TM tier; the folder is fully scanned (every skip logged). Known
noise to weight down, not to "fix" in the miner: (a) proper-name transliterations carry
low lexical information; (b) list-category mis-scoping is the dominant hard-error mode.
Neither justifies polluting the clean corpus — that is exactly why the tier is separate.

## Track A status (parallel-text alignment) — BLOCKED on missing verse-aligned input

H186 Track A asked to align ~12 "not-yet-added parallel Sa-Ru texts" via the existing
`build_corpus_lexicon.py`. **Investigation (06-07-2026) shows none of the 12 exist in
verse-aligned form** the aligner can consume — so the specified reuse-path has no input:

- `corpus_lexicon.jsonl` already covers **every** verse-aligned Sa↔Ru text present in
  SamudraManthanam's `web/corpus_builder/jsonl/` (116 works) — confirming the H184
  scout's "~98% already wired". Every unaligned jsonl there yields **0** alignable
  groups.
- `vishnu-purana.jsonl` (MG's list) is **Russian prose only** (`seg=None`, no parallel
  Sanskrit) → a `mined`/context source, not alignable.
- `13_mahabharata-anushasanaparva.jsonl` has full Sanskrit but **every Russian segment
  is `…`** (untranslated) → correctly excluded by `has_cyr`.
- Hitopadeśa, Bāṇa's Kādambarī, Bhāsa, Garuḍa-purāṇa exist only as **raw GRETIL TEI
  Sanskrit** (`GRETIL-1_sanskr/tei/sa_*.xml`); the Russian sides exist separately as
  glossaries / HTML (`ramayana-potapovoy.html`, the Grintser glossaries already wired
  SPECIALIST in H184). They are **not** verse-aligned to each other.
- Panchatantra / Классическая поэзия / Древнеиндийская литература / Schlegel — not in
  the corpus at all.

**Prerequisite before any Track A alignment**: building parallel verse-aligned jsonl
(source the Sanskrit, segment it, align verses to the chosen Russian edition) — a
**SamudraManthanam `corpus_builder` ingestion job upstream of the aligner**, needing
per-text edition + alignment decisions (prose works like Kādambarī/Panchatantra have no
verse numbers to anchor on). This is a scoping + sourcing call for a human — routed to
[GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md). It is *not*
reusable work the aligner can do today, and must not be faked by aligning
non-parallel prose.

_Dr. Mārcis Gasūns_
