# Implementation plan — the `pwg_ru` / `mw_ru` translation pipeline

> Engineering plan (English) for the shared dictionary-digitization engine behind
> two Russian-translation projects in this directory:
>
> - **`mw_ru`** — Russian translation of Monier-Williams (**English** source). A
>   full run is **already complete**; see [mw_ru.md](mw_ru.md). We are **not**
>   redoing it — but the engine must keep supporting it, and `mw_ru` is the
>   **seed / reference** for `pwg_ru`.
> - **`pwg_ru`** — Russian translation of the **German** Petersburger Wörterbuch
>   (Böhtlingk–Roth, PWG); see [pwg_ru.md](pwg_ru.md). **Not yet run.**
>
> **Superseded on two points** (this is the original pre-Max-harness plan): the
> production vehicle is now the Claude **Max** workflow harness (not the
> DeepSeek-key-gated path below), and the bulk judge is **Sonnet with Opus
> re-judging rejects only** (not Opus-every-card) — see
> [research/JUDGE_POLICY.md](research/JUDGE_POLICY.md). The phase-level engineering
> below remains the build reference.
>
> Both are one engine parameterized by **source language** (En→Ru vs De→Ru).
> This document is the build-side companion to the editor-facing
> [pwg_ru.md](pwg_ru.md); the corpus-feed roadmap is
> [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md).
>
> **Honesty rule for this document.** Every phase is tagged **DONE / NEXT /
> LATER**. BUILT facts and measured numbers are cited from code on disk; nothing
> beyond the verified counts is invented. Sibling repositories
> (SamudraManthanam, the future `mw_ru` working repo) are referenced as **plain
> text**, because Markdown links to paths outside this repo would fail CI
> link-check. In-repo files are linked normally.
>
> **Doc-scope note (harvest-first is new here).** Harvest-first and the additive
> attested-senses model (below) are a **new design introduced in this
> engineering doc set** — this file and
> [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md). The editor-facing
> [pwg_ru.md](pwg_ru.md) still documents the **older per-gloss model**: its §3
> describes translating every gloss, and its §4 covers the `mw_ru` seed **only**
> as a terminological anchor (explicitly *not* a source, *not* to be copied) with
> **no** mention of harvest-first or additive senses. So do **not** read pwg_ru.md
> as the authority for the harvest model; it is the build-side docs (here) that
> define it, until pwg_ru.md is updated to match.

---

## 0. The strategic pivot — harvest first, translate only the gaps

The earlier mental model was "send every German gloss to an LLM and translate
it." The decision this session **replaces** that with a **harvest-first**
assembly:

> For each PWG headword, **assemble** the Russian from material that **already
> exists**, and use the LLM only for (a) genuine gaps and (b) the
> source-language connective / scholarly prose that nothing else covers.

Existing material, in priority order:

1. **The five extracted Sanskrit→Russian dictionaries** —
   [src/](src/)`*.jsonl` produced by [src/build_src.py](src/build_src.py)
   (`koch` / `kow` / `kna` / `fri` / `smirnov`, **≈57 640** keyed entries). The
   deterministic SLP1 join is [src/corpus_gate.py](src/corpus_gate.py).
2. **The SamudraManthanam parallel corpus** — 150+ verse-aligned
   Sanskrit↔Russian translations (Rigveda, Mahābhārata, Rāmāyaṇa, 10+ Gītā,
   Upaniṣads, kāvya, Aṣṭāṅgahṛdaya, …; **154 texts** per
   [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §1.2). Queried in place,
   never duplicated here.
3. **The `mw_ru` Russian cards** — for headwords shared with Monier-Williams,
   used as a terminology anchor (seed, not source — the seed-is-anchor-not-source
   rule is [pwg_ru.md](pwg_ru.md) §4; the *additive-sense* use of that material
   is new here, see the refinement below).

**The crucial refinement.** Harvested Russian meanings are **not merely anchors
for the LLM to copy** — they become **additional attested senses** in the output
dictionary. So `pwg_ru` ends up **richer** than a plain German translation: each
card carries **the German gloss rendered into Russian** *plus*
**corpus/dictionary-attested Russian senses**, each tagged with its source
(`Кочергина` / `FRI` / `KNA` / `Смирнов` / `KOW` / `corpus` / `mw_ru`) and its
role (independent authority vs human reference vs soft corpus usage). This
additive-senses model is **net-new to these engineering docs** and is not yet
reflected in the editor-facing [pwg_ru.md](pwg_ru.md) (see the doc-scope note
above).

### The single biggest new asset — a corpus word-alignment lexicon, built once

The corpus is **verse-aligned, not word-aligned**: it does not say which Russian
word renders which Sanskrit word. So we build a durable layer **once**: a
one-time bulk pass (DeepSeek) over every aligned verse extracts
**Sanskrit-word → Russian-equivalent** pairs across all 150+ texts, producing a
reusable **corpus-derived Sanskrit→Russian lexicon** (gitignored data, exactly
like the five dictionaries). After that, every later use is a **lookup**, not a
re-derivation. This is Phase **P1** below.

---

## 1. Models & plumbing (decided this session)

| Engine | Transport | Used for |
|--------|-----------|----------|
| **Claude Sonnet 4.6** | **Max subscription, via Claude Code** (no API key) — agent/workflow batches, **not** a Python API client | P3 — translate the gaps (masked German skeletons → Russian) |
| **Claude Opus 4.8** | **Max subscription, via Claude Code** | P4 — judge, then re-translate the rejects |
| **DeepSeek** | API key, flat-rate, nonstop — **Python API script, via OpenRouter** | P1 — the one-time corpus word-alignment build; P4 — a cheap second-judge / double-check pass |
| **YandexGPT** | **not available for the pilot** (key comes later) | LATER — second QA judge; the pilot runs **without** it, DeepSeek substitutes if a second judge is wanted |

Consequences that shape the architecture:

- **No Claude API key.** The Sonnet (P3) and Opus (P4) stages **cannot** be a
  Python `anthropic` client. They run **through Claude Code** on the Max
  subscription: the **pilot** is one workflow over *N* cards; **scale-up** is
  scheduled / looped Claude-Code workflows ("run nonstop for a month, no
  limits"). The harness must therefore read a **batch file of masked
  skeletons** and write a **batch file of Russian skeletons** — no live API
  loop.
- **DeepSeek is chat-only (no embeddings).** That is fine: nothing in this
  pipeline needs embeddings. Alignment (P1) and validation (P4 double-check) are
  chat-completion tasks.
- **Launch: tomorrow. Pilot first.**

---

## 2. Pipeline at a glance (stage map)

```text
P0  extractor + masker        De: pwg_mask.py (DONE)   En: mw-side masker (TODO)
        │  masked German/English skeleton  +  {Tn} placeholder map
        ▼
P1  corpus word-alignment     DeepSeek one-time bulk pass over 150+ corpus jsonl
    lexicon (build once)      → gitignored Sanskrit→Russian lexicon (key = SLP1)
        │
        ▼
P2  harvest layer             corpus_gate extended: merge 5 dicts + P1 lexicon
    (assemble reuse senses)   + mw_ru cards → source-tagged ATTESTED SENSES
        │  per headword: assembled "reuse" senses (each source-tagged)
        ▼
P3  translation runner        Claude-Code workflow: Sonnet translates the masked
    (gaps only)               skeleton; append-only versions; per-card round-trip
        │
        ▼
P4  QA                        Opus judge + Opus fix (Claude-Code workflow);
                              DeepSeek cheap double-check; Yandex LATER
        │
        ▼
P5  corpus-gate verdict       stage-4 LLM verdict (4_korpus_proverka.txt) +
    + assembly                assemble OUTPUT card = De→Ru gloss + attested senses
```

The same P0/P3/P4 engine serves `mw_ru` (English skeletons) and `pwg_ru` (German
skeletons); only the masker variant and the prompt set change.

---

## P0 — Extractor + masker

**De side: DONE.** [src/pwg_mask.py](src/pwg_mask.py) walks
`csl-orig/v02/pwg/pwg.txt` into `<L>…<LEND>` records and masks each into `{Tn}`
placeholders so the translator sees **only** German. Untranslatable spans
(Sanskrit `{#…#}`, refs `<ls>`, abbreviations `<ab>`, italic Sanskrit `<is>`,
grammar `<lex>`, foreign `<lang>`, structural tags) become placeholders,
restorable left-to-right. The PWG-specific `{%…%}` rule is implemented: German
glosses are kept inline (translate), high-confidence Latin is masked (leave),
ambiguous is kept-but-flagged.

Verified on the **full** dictionary:

- **123 365 / 123 366** records round-trip losslessly (restore == original) =
  **100.00 %** to two decimals.
- `{%..%}` classified **99.9 % German** (translate, inline) / **25 Latin**
  (leave) / **230 ambiguous** (flagged for the LLM).
- **1 lossy record** remains. **Runner requirement (non-negotiable):** the P3
  harness must assert **per-card** round-trip (`restore(skeleton, map) ==
  original`) and route any failure to **manual review** rather than emitting a
  silently corrupted card.

**En side: TODO (NEXT for `mw_ru` support; not on the pilot path).** `mw_ru` was
produced with an MW-side masker that lives in the (separate) `mw_ru` working
repo and is **not in this repository** — there is **no** En masker on disk here
(only `pwg_mask.py`). `mw_ru` is already complete, so the En masker is **not**
needed to launch the `pwg_ru` pilot; it is required only if/when the engine is
re-pointed at MW in-repo (e.g. for the P4/P5 enrichment of `mw_ru` described in
[SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §3). When built, it mirrors
`pwg_mask.py` over MW's opaque-tag set (`<s>`, `<s1>`, `<ab>`, `<lex>`, `<ls>`,
`<hom>`, …) and has **no** `{%…%}` rule (that class is PWG-only).

**Deliverables**

- [x] `pwg_mask.py` — `stats` / `sample` / `card` modes, full-dictionary
      round-trip verified. **DONE.**
- [ ] `mw_mask.py` (or a `--lang en` switch on a shared masker) over the MW
      opaque-tag set. **TODO / LATER.**
- [ ] Per-card round-trip assertion exposed as a library call the P3 runner
      imports (today it only runs inside `cmd_stats`). **NEXT.**

---

## P1 — Corpus word-alignment lexicon (build once)

**Status: NEXT — the single biggest new asset; not yet built.**

**Problem.** The corpus is verse-aligned, so for a Sanskrit headword we can find
verses that contain a form of it and read the aligned Russian *passage* — but
not the specific Russian word that renders it. A one-time alignment pass turns
that passage-level signal into a word-level lexicon.

**Approach.** A **DeepSeek Python API script, via OpenRouter**, flat-rate and
nonstop, makes a single bulk pass over every aligned verse across all 150+ texts
and extracts **Sanskrit-word → Russian-equivalent** pairs.

**Inputs**

- The SamudraManthanam verse-aligned corpus jsonl (the `#sa` / `#ru` segment
  pairs sharing a `group` id), read in place from the sibling SamudraManthanam
  repository (`web/corpus_builder/jsonl/` and/or `web/corpus.db`). Plain-text
  path on purpose; the corpus is **queried/read, never copied** into this repo.

**Output**

- A gitignored `src/corpus_lex.jsonl` (same discipline and directory as the five
  dictionaries), one alignment per line:
  `{"source":"corpus","slp1":"<SLP1 key>","iast":"…","gloss":"<Russian
  equivalent>","support":{"work":"…","group":"…"}}`.
- **Key = SLP1**, normalized with the **length-preserving `form_key()`** already
  in [src/corpus_gate.py](src/corpus_gate.py) — never a naïve NFD-strip-Mn
  (which would collapse `ā→a` and `ṣ→s`). This makes the new lexicon
  join-compatible with the five dictionaries on day one.

**Contract & honesty**

- Like `build_src.py`, the **script is committed**, the **data is gitignored**
  (regenerable from the corpus). It is reproducible from the corpus + the prompt.
- Provenance is preserved (`support.work` / `support.group`) so a derived sense
  can be cited and audited, and so its **softness** is visible: it is a
  corpus-derived equivalent, weaker than a dictionary gloss — exactly the
  softness contract in [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §5.
- After this pass, every consumer (P2, P5, and the wider ecosystem) **reuses the
  lexicon by lookup** — no re-derivation, no per-run LLM cost for alignment.

**Deliverables**

- [ ] `src/build_corpus_lex.py` — DeepSeek/OpenRouter bulk aligner. **NEXT.**
- [ ] `src/corpus_lex.jsonl` — gitignored SLP1-keyed output. **NEXT.**
- [ ] A short README note in [src/README.md](src/README.md) documenting the new
      sixth source and its softer role. **NEXT.**

---

## P2 — Harvest layer (assemble the reuse senses)

**Status: PART-BUILT.** The deterministic join already exists —
[src/corpus_gate.py](src/corpus_gate.py) loads the five dictionaries, joins a
PWG headword on the SLP1 key (`key1`, `key2` fallback), pulls verse-aligned
corpus examples (reusing SamudraManthanam FTS, `#sa`→`#ru`), and emits the
stage-4 input JSON with each gloss **source-tagged** (`independent_glosses` with
`source`/`code`, `kow_reference`, `corpus_examples`). It also offers the cheap
heuristic pre-check.

**Measured PWG coverage** (over all **106 085** PWG `key1` headwords; random
sub-sample with a fixed seed for the slow corpus query — see
[SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §2.3):

| Signal | Source(s) | Coverage |
|--------|-----------|----------|
| correctness (independent) | any of Кочергина / Фриш / Кнауэр / Смирнов | **16.4 %** (Кочергина alone 14.4 %) |
| reference (human) | KOW | **8.0 %** |
| corpus (soft) | parallel corpus, ≥1 aligned verse | **≈14–15 %** (sampling-noisy) |

So the **dominant outcome is `no-check`** (~84 % of headwords have no
independent gloss) — which is exactly why the gate is a non-blocking annotator,
and exactly why P1 + the harvest model matter: they recover attested Russian for
headwords the five dictionaries miss.

**Tuning fact that constrains P2.** Inter-dictionary agreement is low: only
~5 % of dictionary pairs reach Jaccard ≥ 0.4 (synonyms/paraphrase dominate). So
token overlap is used **only** as a confident auto-`pass` (`THRESHOLD = 0.5`,
head-sense only); everything else is `review`, owned by the LLM. **The
heuristic never declares `divergence`.**

**What P2 adds (NEXT).** Extend `corpus_gate.py` from "emit gate input" to
"**emit the assembled reuse senses per headword**":

1. **Merge a third and fourth source** into the existing join: the **P1
   corpus-alignment lexicon** (`src/corpus_lex.jsonl`) and the **`mw_ru`
   cards** (for headwords shared with MW). Both keyed on the same `form_key()`
   SLP1.
2. **Emit assembled senses**, each as a tagged record:
   `{"ru":"<sense>","source":"Кочергина|FRI|KNA|Смирнов|KOW|corpus|mw_ru",
   "role":"independent|reference|corpus|seed","support": …}`. These are the
   **additional attested senses** that make `pwg_ru` richer than a plain
   translation — they are carried into the output card in P5, not just shown to
   the translator.
3. Keep the existing source/role discipline intact: independent dictionaries
   decide correctness; KOW is reference + secondary; corpus and the P1 lexicon
   are **soft** (corroborate, never decide); `mw_ru` is a **seed** (anchor, never
   copied). SKD/VCP remain Sanskrit-side only and must hard-fail if ever routed
   in as a Russian gloss.

**Deliverables**

- [x] SLP1 join over 5 dictionaries + corpus query + heuristic pre-check
      ([src/corpus_gate.py](src/corpus_gate.py)). **DONE.**
- [x] Measured per-signal coverage (16.4 / 8.0 / ≈14–15) and threshold tuning.
      **DONE.**
- [ ] Merge `src/corpus_lex.jsonl` (P1) + `mw_ru` cards into the index. **NEXT.**
- [ ] New `corpus_gate.py assemble <key1>` mode emitting source-tagged attested
      senses per headword. **NEXT.**

---

## P3 — Translation runner (gaps only)

**Status: NEXT — prompts exist, no runner harness exists.** The system prompt
[pwg_ru_prompts/1_perevod.txt](pwg_ru_prompts/1_perevod.txt) (with the German→
Russian glossaries) is ready; what is missing is the **harness** that drives it.

Because there is no Claude API key, P3 is a **Claude-Code workflow on the Max
subscription**, not an API loop. The harness:

1. Reads a **batch of masked skeletons** from P0 (German text + `{Tn}` map) plus,
   where P2 found them, the **assembled reuse senses** (so Sonnet translates only
   the genuine gaps and the connective German prose, anchored by what already
   exists).
2. Feeds each card's user-message under the `1_perevod.txt` system prompt to
   **Sonnet 4.6** via the workflow.
3. Writes results **append-only** (new versions sit beside old; the dictionary
   build later takes the **latest** version per card — the `mw_ru` chunking
   model in [mw_ru.md](mw_ru.md) §3).
4. **Asserts per-card round-trip** using P0's restore (every `{Tn}` present, on
   the same positions); failures (incl. the known 1 lossy PWG record) route to
   **manual review**, never to the output.

Pilot = **one workflow over *N* cards**; scale-up = **scheduled / looped**
workflows.

**Deliverables**

- [ ] `data/scripts/translate_pilot/` harness: batch-in → Claude-Code workflow →
      append-only batch-out, with per-card round-trip assertion. **NEXT.**
- [ ] `glossary_de.json` — machine form of the
      [pwg_ru_prompts/1_perevod.txt](pwg_ru_prompts/1_perevod.txt) glossaries.
      **NEXT.**

---

## P4 — QA (judge + fix; double-check)

**Status: PART-READY — both judge prompts and the re-translate prompt exist; no
QA harness exists.** Ready on disk:
[pwg_ru_prompts/2_qa_sudya_opus.txt](pwg_ru_prompts/2_qa_sudya_opus.txt) (judge),
[pwg_ru_prompts/2_qa_sudya_yandexgpt.txt](pwg_ru_prompts/2_qa_sudya_yandexgpt.txt)
(second judge), and
[pwg_ru_prompts/3_pereperevod_opus.txt](pwg_ru_prompts/3_pereperevod_opus.txt)
(re-translate). Categories mirror `mw_ru` (semantic, structure, anchors,
hallucination, truncation, anglicism/germanism, grammar) plus the PWG-specific
`{%…%}` class (Latin wrongly translated / German left untranslated), severity
1–5; cards at severity ≥ 3 go to re-translation.

**Pilot plumbing (no Yandex).**

- **Opus 4.8 judge** + **Opus 4.8 fix** run as a **Claude-Code workflow** on the
  Max subscription (same transport as P3 — no API client).
- A **heuristic pre-filter** (stages A/B/C — dropped `<s>`/`{#…#}` tag,
  unresolved Latin `{%…%}` wrongly translated, anglicism/germanism markers,
  anomalously long body) selects suspicious cards so the judge sees those first.
- **DeepSeek** (Python API, via OpenRouter, flat-rate) runs a **cheap
  double-check / second judge** if a second judge is wanted in the pilot — it
  **substitutes for YandexGPT**, which is unavailable until its key arrives.

**Deliverables**

- [ ] `qa_prefilter_de.py` — A/B/C heuristic pre-filter. **NEXT.**
- [ ] Opus judge + Opus fix Claude-Code workflow (append-only verdicts and
      fixes). **NEXT.**
- [ ] DeepSeek double-check Python script (via OpenRouter). **NEXT.**
- [ ] YandexGPT second judge. **LATER** (blocked on key).

---

## P5 — Stage-4 corpus-gate LLM verdict + assembly into output cards

**Status: PART-BUILT.** The deterministic gate
([src/corpus_gate.py](src/corpus_gate.py)) and the LLM verdict prompt
([pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt))
both exist; the LLM verdict has **not been run** (it runs when the `pwg_ru` run
launches).

P5 is the **terminal, non-blocking annotator**. For each card it:

1. Takes the P2 assembled input and asks the **LLM verdict** to emit the two
   signals — **correctness** (`pass` / `divergence` / `no-check` / `key-mismatch`
   against the independent dictionaries, with `matched_source`) and
   **reference-agreement** (`high` / `partial` / `none` / `no-ref` against KOW)
   — plus soft `corpus_support` and `corpus_citations`. Per
   [pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt),
   only **independent** dictionaries can yield `pass`; KOW, SKD/VCP and the
   corpus only **corroborate**.
2. **Assembles the output card**: the German→Russian gloss (from P3/P4) **plus**
   the **attested reuse senses** harvested in P2 (each source-tagged), with the
   gate verdict and citations attached. This is where `pwg_ru` becomes **richer
   than a translation**: it ships the translated German *and* the
   corpus/dictionary-attested Russian, each labelled by source and role. (This
   additive-senses output is the new design defined in these engineering docs;
   [pwg_ru.md](pwg_ru.md) does not yet describe it — see the doc-scope note in
   the header.)
3. Never withholds a card: `divergence` at low confidence and `key-mismatch` are
   routed to the editor / join-repair bucket; `no-check` passes with an
   "uncovered" tag.

**Deliverables**

- [x] Deterministic gate: SLP1 join, corpus query, gate-input JSON, heuristic
      pre-check ([src/corpus_gate.py](src/corpus_gate.py)). **DONE.**
- [x] Verdict prompt + calibration
      ([pwg_ru_prompts/4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt)).
      **DONE.**
- [ ] Wire the LLM verdict (DeepSeek for the cheap pass, or the Claude-Code
      workflow) over the gate input. **NEXT.**
- [ ] `assemble` step that fuses gloss + attested senses + verdict into the
      final card record. **NEXT.**

---

## PILOT — launch tomorrow (no Yandex)

A bounded, **high-coverage** slice that demonstrates the whole harvest-first
idea end to end without waiting on the Yandex key or a month-long run.

**Slice.** One alphabet section (e.g. the PWG `a-` zone, where dictionary and
KOW coverage are densest) **or** a few hundred headwords selected for **existing
dict/corpus coverage**. Note that `corpus_gate.py coverage` only prints
aggregate percentages — it is **not** a key-picker and emits no list of
qualifying `key1` values. A coverage-based key selector (e.g. a new
`corpus_gate.py select <N> --min-indep 1 --min-corpus 1` mode that prints
qualifying `key1` lines) is a **NEXT deliverable, not yet built**. Until it
exists, pick the slice by the **alphabet-zone fallback** (one section, e.g. the
`a-` zone). Keep it small enough for **one Claude-Code workflow**.

**Run.** P0 → P2 (harvest) on the slice, then a **small** P3 (Sonnet over the
masked skeletons of the slice) and a **small** P5 (gate input already builds;
run the LLM verdict via DeepSeek or one Claude-Code workflow), and **show a
handful of assembled `pwg_ru` cards**: each with the **German→Russian gloss**
plus the **attested reuse senses** (e.g. `плечо` [Фриш], `доля; часть`
[Кочергина], a KOW reference, a corpus citation), every sense source-tagged.
QA (P4) on the pilot is Opus judge + Opus fix via Claude-Code, with DeepSeek as
the optional cheap second judge; **YandexGPT is skipped**.

**Pilot success = a handful of real assembled cards** that visibly carry more
than a plain German translation, with honest per-signal coverage reported
(16.4 % correctness / 8.0 % KOW / ≈14–15 % corpus on the full dictionary; the
slice will be higher by construction, and that must be stated as a
selection effect, not headline coverage).

---

## Concrete blockers remaining

1. **DeepSeek / OpenRouter keys to wire.** Needed for P1 (the one-time corpus
   word-alignment build) and the P4/P5 cheap double-check. No Python API client
   exists yet for either.
2. **The En-side masker (`mw_mask.py`).** Not on disk — only
   [src/pwg_mask.py](src/pwg_mask.py) exists. Not needed for the `pwg_ru` pilot;
   needed for any in-repo `mw_ru` enrichment (P0 En, P4/P5 on MW).
3. **The runner harness.** No P3/P4 harness and no `data/scripts/` directory
   exist. The Claude-Code-workflow batch driver (batch-in → workflow →
   append-only batch-out, per-card round-trip assertion) is the critical new
   piece for launch.
4. **The 1 lossy PWG record** (123 365 / 123 366 round-trip). The runner must
   assert per-card round-trip and route the failure to manual review.
5. **YandexGPT key.** Blocks the second QA judge (P4); the pilot proceeds
   without it, DeepSeek substituting.
6. **The pilot key-selector.** `corpus_gate.py coverage` reports aggregates only;
   a `select` mode that lists coverage-dense `key1` values is a NEXT
   deliverable. Until it lands, the pilot picks its slice by alphabet zone.
7. **Corpus transport for P1/P5.** Pick the SamudraManthanam access path
   (read-only open of `corpus.db` / offline `dict.db`, or the FastAPI shim) —
   open item carried from [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) §7.
