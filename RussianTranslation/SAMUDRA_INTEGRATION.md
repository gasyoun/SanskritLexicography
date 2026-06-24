# SamudraManthanam integration — roadmap

How the **SamudraManthanam** parallel-corpus tool feeds the Russian-translation
projects in this directory (`pwg_ru`, `mw_ru`) and, across the org, the
WhitneyRoots root crosswalk. This is a planning document: it separates clearly
what is **built** from what is **designed/planned**, and it never invents
numbers beyond the verified extraction counts below.

SamudraManthanam is a **separate sibling repository**
(`gasyoun/SamudraManthanam`), not part of this repo. Its paths are written here
as **plain text** on purpose — a Markdown link to a path that does not exist in
this repository would fail the CI link-check. In-repo files are linked normally.

---

## 1. What SamudraManthanam is and what it gives us

SamudraManthanam (the `samskrtam.ru` corpus tool, v1.8 — a Lazarus desktop app
plus a FastAPI web service) is a **verse-aligned parallel Sanskrit–Russian
corpus** with bundled digitized dictionaries and morphological search. Three
things it offers this directory:

### 1.1 Digitized Sanskrit→Russian dictionaries (already extracted)

Inside SamudraManthanam the source dictionaries ship as
`web/corpus_builder/jsonl/*.jsonl`, already digitized and (mostly) SLP1-keyed.
We extract five of them with [src/build_src.py](src/build_src.py); see
[src/README.md](src/README.md) for the contract and counts:

| File | Dictionary | Records |
|------|------------|---------|
| `koch.jsonl` | Кочергина, Санскритско-русский словарь (1987) | 29 177 |
| `kow.jsonl` | Коссович, Санскрито-русский словарь (1854) | 13 488 |
| `kna.jsonl` | Кнауэр, учебник санскрита (1908), словарь | 3 271 |
| `fri.jsonl` | Фриш, санскритская хрестоматия (1956), словарь | 8 156 |
| `smirnov.jsonl` | Смирнов, «Симфонический словарь» (1955–1989) | 3 548 |

**57 640 keyed entries** total. Each line is
`{"source","slp1","iast","gloss"}`. The extracted `slp1` field carries the
source's own SLP1 (for koch/kow/kna) or a straight IAST→SLP1 transliteration
(for fri/smirnov) — extraction does **not** normalize it further. The
length-preserving `form_key()` normalization (not a naïve NFD-strip-Mn, which
would collapse vowel length and retroflex dots) is applied at **join / gate
time** — in the as-yet-unbuilt gate, not during the BUILT extraction step here.

### 1.2 The verse-aligned parallel corpus

The corpus pairs Sanskrit and Russian at the **verse / passage** level: each
passage carries a `#sa` segment and a `#ru` segment sharing a `group` id —
Sanskrit in IAST/SLP1, Russian in Cyrillic. Roughly **154 texts**: the Rigveda
and Atharvaveda, all 18 Mahābhārata parvans, the Rāmāyaṇa kāṇḍas, 10+
Bhagavadgītā translations (including Sementsov and Smirnov), dozens of
Upaniṣads, plus kāvya and śāstra.

Crucially, the alignment is **verse-level, not word-level**. There is no
per-token mapping from a Sanskrit word to its Russian rendering. This is the
single most important property for everything below: the corpus is a **soft**
signal — it tells us how a word is rendered *somewhere in a verse that contains
it*, not a guaranteed gloss for that word.

### 1.3 FTS5 morphological search

SamudraManthanam builds SQLite at `web/corpus.db` and a packaged
`web/offline-packs/dict.db` (FTS5) and already exposes **stem / root
(morphological) search** over the corpus. We **reuse** that search rather than
rebuilding morphology or copying the corpus into this repository.

### 1.4 Bonus payloads (broader leverage)

The same `web/corpus_builder/jsonl/` directory also contains:

- `dic_mw.jsonl` — Monier-Williams (relevant to **mw_ru**, §3).
- `dic_apte.jsonl` — Apte.
- `warnemyr.jsonl` — Whitney roots (relevant to **WhitneyRoots**, §4).
- Grintser / Potapova glossaries.

These are not part of the `pwg_ru` gate but are real assets for the wider
ecosystem; see §3–§5.

---

## 2. PWG corpus gate (`pwg_ru` stage 4)

The `pwg_ru` gate is settled design (see [pwg_ru.md](pwg_ru.md) §7): a
**non-blocking annotator** at stage 4 that emits **two independent signals** and
never withholds a card —

1. **Correctness** vs **independent** dictionaries (now koch / kna / fri /
   smirnov) — does the Russian headword agree with an independently compiled
   Sanskrit→Russian dictionary?
2. **Reference-agreement** vs **KOW** (kow) — a partial, WIL-seeded human
   PWG→RU reference; secondary, and never decides correctness on its own.

SKD/VCP stay Sanskrit-side only (Sanskrit→Sanskrit). The join is on the SLP1
key1, with key2 as a homograph fallback, using the length-preserving
`form_key()`.

A **third-language sense signal** was evaluated 2026-06-24 (indic-dict Indic-gloss
dicts — Hindi `apte-hi`/`vedic-rituals-hi`, Kannada/Tamil; see
[INDIC_DICT_EVALUATION.md](INDIC_DICT_EVALUATION.md)). These gloss in Hindi/Tamil/
Kannada, not Russian, so they are **not** a correctness vote on the Russian head-term;
they can only corroborate **which sense is primary** — softer even than the verse-level
corpus signal (§2.2), annotate-only, never overriding. `apte-hi` is the one with real
leverage (Apte-aligned → structured sense map). **Licensing cleared 2026-06-24** (free
use with attribution for all four, by email); `apte-hi` is being folded as the first
third-language sense signal.

### 2.1 Dictionary signal — BUILT

The five dictionaries are **extracted and on disk** via
[src/build_src.py](src/build_src.py) (see [src/README.md](src/README.md)). They
slot directly into the gate's roles:

- **koch / kna / fri / smirnov** → **independent correctness** authorities. Any
  one of them matching the PWG Russian headword can yield `pass` and records
  `matched_source`.
- **kow** → the **reference-agreement** signal *and* a secondary corroborator of
  correctness — it can support a `pass` but never resolves a `divergence` alone,
  and its glosses are always flagged as PWG/WIL-derived.

This replaces the earlier "maintainer will supply the files" assumption for
koch / kna / kow: those sources are now obtained by extraction from
SamudraManthanam, and fri/smirnov extend coverage further. The gate's verdict
schema (`correctness`, `matched_source`, `reference_agreement`, …) is unchanged
and lives in [pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt).

> The `pwg_ru` run itself has **not been executed yet**. Coverage per signal is
> a measured metric reported at ingest, not a number we guess here.

### 2.2 Parallel-corpus signal — DESIGNED

A second, softer input to the same non-blocking gate, **reusing SamudraManthanam
morphological search** rather than rebuilding anything:

1. For a PWG headword (SLP1 key), query SamudraManthanam's FTS/morph search for
   corpus verses whose Sanskrit contains a **morphological form** of the
   headword (stem/root match).
2. Read the **aligned Russian** (`#ru`) for each matched `group`.

That yields two products:

- **(i) A soft usage signal** — how the word is *actually rendered* in running
  translation, across many translators and texts. Because alignment is
  verse-level (no per-word mapping), the Russian rendering of *this* word is not
  isolated from the rest of the verse. The signal is therefore **softer than a
  dictionary gloss match** and must be reported as such: it can *corroborate*
  (raise confidence, add a `corroborated_by` style note) but it does **not**
  resolve correctness by itself, and never overrides the independent-dictionary
  verdict.
- **(ii) Real example citations** — concrete verse references (text + group id,
  Sanskrit + Russian) attachable to a card for the editor and, later, for
  reader-facing display.

Design constraints, to keep it honest:

- **Verse-level only.** Always label corpus evidence as passage-level usage, not
  a per-word gloss. A morphological hit means "this verse contains a form of the
  word", not "this Russian fragment translates this word".
- **Query, don't duplicate.** The corpus and its morphology live in
  SamudraManthanam; this repository issues queries against `web/corpus.db` /
  `web/offline-packs/dict.db` and stores only the citations it pulls back. No
  corpus copy enters SanskritLexicography.
- **Non-blocking.** Like the dictionary signal, the corpus signal annotates and
  routes doubtful cards to the editor; it never withholds a card.

### 2.3 Built: `corpus_gate.py`, measured coverage & threshold tuning (2026-06-15)

The deterministic half of the gate is built — [src/corpus_gate.py](src/corpus_gate.py)
does the SLP1 join over the five dictionaries, the corpus query (reusing
SamudraManthanam's FTS, `#sa`→`#ru` verse alignment), assembles the
`4_korpus_proverka.txt` input, and offers a cheap heuristic pre-check. The
dictionary index, the join and the corpus query all run; the LLM verdict is the
remaining, not-yet-run step.

**Measured coverage over all 106 085 PWG headwords** (key1; random sub-sample for
the slow corpus query, fixed seed for reproducibility):

| Signal | Source(s) | Coverage |
|--------|-----------|----------|
| (1) correctness | any of Кочергина / Фриш / Кнауэр / Смирнов | **16.4 %** (Кочергина alone 14.4 %, Фриш 4.0 %, Кнауэр 2.7 %, Смирнов 1.7 %) |
| (2) reference | KOW | **8.0 %** |
| corpus (soft) | parallel corpus, ≥1 aligned verse | **≈14–15 %** (random sample; the corpus query is sampling-noisy) |

So **the dominant outcome is `no-check`** (~84 % of headwords have no independent
gloss) — exactly why the gate is a non-blocking annotator, not a filter. Coverage
is a reported metric, never hidden as passes.

**Threshold tuning (`tune`).** Calibrating the heuristic against inter-dictionary
agreement: where two independent dictionaries both cover a headword, their Russian
head-terms overlap only at **low** token levels (only ~5 % of dictionary pairs
reach Jaccard ≥ 0.4 — synonyms and paraphrase dominate). The consequence is
decisive: **a token-overlap threshold cannot detect divergence without massive
false positives.** So `corpus_gate.py` uses the heuristic only to auto-**pass**
high-overlap cases (`THRESHOLD = 0.5`, head-sense only) and routes everything else
to the synonym-aware LLM verdict (`review`) — it never calls `divergence` itself.
Sense-granularity: `HEAD_SENSE_ONLY = True` (compare sense 1, the text before the
first `;`), matching the gate's head-sense rule.

---

## 3. `mw_ru` — validating and citing the completed Russian Monier-Williams

`mw_ru` (the AI Russian translation of Monier-Williams; see
[mw_ru.md](mw_ru.md)) is a **completed run** living in this same directory. Two
SamudraManthanam assets help **validate and cite** it after the fact:

- **`dic_mw.jsonl`** (Monier-Williams, from SamudraManthanam) — an
  independently digitized MW keyed the same SLP1 way. It provides a **structural
  cross-check** of the `mw_ru` card inventory (headword coverage, key
  alignment) and a comparison surface for spot auditing translated cards against
  the English source as digitized elsewhere.
- **The parallel corpus** — the **same verse-level usage + citation** mechanism
  as §2.2, pointed at `mw_ru` headwords: for an MW entry, surface corpus verses
  containing a morphological form and their aligned Russian, as a soft
  sanity-check on the Russian rendering and as attachable example citations.

This is a *post-hoc enrichment* layer for `mw_ru`, not a re-run: `mw_ru`'s
translation pipeline is done. The corpus signal here is, again, softer than a
gloss and is reported as usage evidence, not ground truth.

---

## 4. WhitneyRoots (separate repo) — warnemyr + corpus for the root crosswalk

WhitneyRoots is a **separate repository**, not part of this directory. Two
SamudraManthanam payloads feed its root crosswalk:

- **`warnemyr.jsonl`** (Whitney roots, from SamudraManthanam) — a digitized
  Whitney-roots dataset that can seed or cross-check the root spine the
  WhitneyRoots crosswalk already maintains (grammar ↔ corpus ↔ dictionary
  layers).
- **The parallel corpus** — for a given root, morphological search returns
  verses whose Sanskrit contains attested forms of that root; the aligned
  Russian and the verse references provide **usage attestation and citations**
  for the crosswalk's form→reference edges.

As elsewhere, this is **query-time reuse** of SamudraManthanam's morphology and
corpus, delivered to a sibling repo over the shared interface in §5 — not a copy
of the corpus into WhitneyRoots. (The extraction script here writes only the
`pwg_ru` gate's five dictionaries; `dic_mw` / `warnemyr` extraction for the mw_ru
and WhitneyRoots consumers is a planned, separate, equally gitignored step.)

---

## 5. Shared citation backbone — one query interface over `corpus.db`

The corpus signal recurs in §2.2, §3, and §4 with the same shape: *given an SLP1
key, find morphologically matching Sanskrit verses, return their aligned Russian
and references.* That argues for **one** small query interface over
SamudraManthanam's `web/corpus.db` / `web/offline-packs/dict.db`, shared across
projects, rather than three bespoke integrations:

```text
cite(slp1_key, options) -> [ { text, group, sa, ru, ref } , ... ]
```

- **Single source of truth.** SamudraManthanam owns the corpus, the morphology,
  and the FTS index; consumers (`pwg_ru`, `mw_ru`, WhitneyRoots) only ever
  *query* it and cache the citations they keep.
- **Uniform softness contract.** Every consumer receives verse-level evidence
  with the same caveat baked in: it is usage/citation, not a per-word gloss, and
  cannot decide correctness alone.
- **No duplication, no morphology rebuild.** Nothing re-implements stem/root
  search and nothing copies the corpus into SanskritLexicography.

The concrete transport (a small CLI/HTTP shim against the FastAPI service, or a
read-only open of the offline `dict.db` pack) is an implementation choice for
the build phase; the contract above is what the three projects depend on.

---

## 6. Rights & placement

- **Extracted dictionary data is local / gitignored.** The `*.jsonl` outputs in
  [src/](src/) are in `.gitignore` and are never committed. The committed,
  regenerable contract is [src/build_src.py](src/build_src.py) +
  [src/README.md](src/README.md); the data is rebuilt locally / on the server.
- **PD vs approved modern.** Коссович (1854, kow) and Кнауэр (1908, kna) are
  **public domain**. Кочергина (1987, koch), Фриш (1956, fri) and Смирнов
  (1955–1989, smirnov) are modern sources, but the project has copyright
  approvals for extensive use in the publishable `pwg_ru` edition. They are no
  longer evidence-only inputs; they may feed card body text with source
  attribution/provenance. The extracted data still stays local/gitignored as an
  operational discipline, not as a publication blocker.
- **Corpus stays in SamudraManthanam.** The parallel corpus and its databases
  are queried in place; only the specific citations a card needs are pulled into
  this repository, keeping the redistribution surface minimal.
- **`dic_mw` / `warnemyr` and the corpus citations** inherit the same local /
  gitignored discipline when their extraction lands.

---

## 7. Phased plan + open items

**Phase 0 — dictionary extraction. DONE.** Five SLP1-keyed dictionaries
extracted from SamudraManthanam into [src/](src/) via
[src/build_src.py](src/build_src.py) (57 640 entries). Data gitignored.

**Phase 1 — dictionary-signal join. BUILT (2026-06-15).**
[src/corpus_gate.py](src/corpus_gate.py) feeds koch / kna / fri / smirnov
(correctness) and kow (reference) into the stage-4 input
([pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt));
coverage measured (§2.3). The LLM verdict runs when the `pwg_ru` run launches.

**Phase 2 — shared corpus query interface (§5).** Build the `cite(slp1_key)`
shim over SamudraManthanam's `corpus.db` / `dict.db`, reusing its morphological
search. Single dependency for all three consumers.

**Phase 3 — corpus signal + citations for `pwg_ru` (§2.2).** Attach verse-level
usage corroboration and example citations to PWG cards via the Phase 2
interface; report it explicitly as softer-than-gloss.

**Phase 4 — `mw_ru` post-hoc enrichment (§3).** Cross-check the completed
`mw_ru` against `dic_mw.jsonl`; attach corpus citations to MW headwords.

**Phase 5 — WhitneyRoots crosswalk (§4).** Deliver `warnemyr.jsonl` +
corpus-attested usage/citations to the WhitneyRoots repo over the shared
interface.

### Open items

1. **Transport for §5.** CLI/HTTP shim against the FastAPI service vs read-only
   open of the offline `dict.db` pack — pick one for Phase 2.
2. **Morphology fidelity.** Confirm SamudraManthanam stem/root search recall is
   adequate for headword lookup (handling sandhi/compounds) before relying on it
   as a coverage signal.
3. **Citation scoring.** How strongly a verse-level match may corroborate a
   `pass` (it must stay strictly below the independent-dictionary verdict) and
   how many citations to keep per card.
4. **`dic_mw` / `warnemyr` extraction.** A separate, gitignored extraction step
   analogous to Phase 0, scoped to the mw_ru and WhitneyRoots consumers.
5. **Coverage reporting.** Measured 2026-06-15 (§2.3): correctness 16.4 %, KOW
   8.0 %, corpus ≈14–15 % (sampling-noisy). The LLM verdict distribution still
   awaits the `pwg_ru` run.
