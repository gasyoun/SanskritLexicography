# Pipeline architecture — `pwg_ru` / `mw_ru` (harvest-first)

> Engineering reference (English) for the shared two-pipeline dictionary
> translation engine. The editor-facing process notes are
> [pwg_ru.md](pwg_ru.md) (German→Russian, *planned*) and
> [mw_ru.md](mw_ru.md) (English→Russian, *completed*). This document describes
> the engine itself: its components, the harvest-first data flow, the model
> plumbing, and what is BUILT versus TODO. It is scoped to the code and data
> that actually exist in this repository — it invents no run statistics.
>
> **Judge-policy note:** where this doc shows "Opus judges each card," the bulk
> policy is now **Sonnet judges every card, Opus re-judges rejects only** —
> [research/JUDGE_POLICY.md](research/JUDGE_POLICY.md).

---

## Current production architecture (2026-06-28)

The historical component notes below describe the design path. The live
operator path is now the frequency-window Max workflow:

```powershell
python src\pilot\root_window_status.py <root>
python src\pilot\gen_opt_harness.py <root>
# run src\pilot\run_pilot_wf.opt.js in Claude/Max Workflow and save wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Current source of truth:

- `src/pilot/gen_opt_harness.py` derives the production harness from
  `src/pilot/run_pilot_wf.js`, inlines raw/portrait inputs, disables tools for
  translate agents, and embeds rootmap/input hashes.
- `src/pilot/audit_window.py` is the canonical local acceptance gate. It now
  delegates workflow parsing, staleness/provenance checks, report/queue writing,
  and window-status writing to small helper modules under `src/pilot/`.
- `src/pilot/window_selftest.py` smoke-tests the critical architecture
  guardrails: nested workflow payload parsing, optimized-harness scope/tool
  guards, prompt-rule coverage, stale-artifact refusal preserving
  `requeue.keys.txt`, and release manifest hash validation.
- `src/pilot/prompt_rule_audit.py` is the no-token semantic wiring audit. It
  checks the committed template and generated optimized harness for the
  manual-derived rules harvested from Apresjan, Hartmann, Gonda/Vogel, Tubb,
  Baalbaki, Apte/Gillon/Inglese-Geupel, and Mitrenina/Zaliznyak-Paducheva/
  Ruppel. With `--cards`, it also scans translated workflow/card JSON for
  cheap semantic-risk patterns before human review. Both modes write ignored
  `prompt_rule_audit.{json,md}` reports with separate prompt-rule and card-risk
  sections; the card-risk section includes a ranked `review_queue` so humans
  can read the riskiest semantic cases first.
- The committed `src/pilot/run_pilot_wf.js` is a template. Do not run it
  directly for production windows; run the generated `run_pilot_wf.opt.js`.
- Semantics is deterministic-first locally: cheap semantic-risk patterns are
  flagged before human review, while LLM semantic judging remains only the
  later `judge_sample.keys.txt` spend queue.
- The corpus word-alignment lexicon exists; bulk throughput is no longer
  blocked on that asset. Print readiness remains downstream of human/gold
  gates G5/G6/G7/G10.

---

## 1. One engine, two pipelines

There is a single translation engine, parameterized by **source language**. It
drives two production runs:

| Pipeline | Source → target | Source lang | Status | Role here |
|----------|-----------------|-------------|--------|-----------|
| `mw_ru` | Monier-Williams **English** → Russian | English | a full run already exists (see [mw_ru.md](mw_ru.md)) | seed / reference for `pwg_ru`; the engine must keep supporting it, but we are **not** redoing it |
| `pwg_ru` | Petersburger Wörterbuch **German** (PWG, Böhtlingk–Roth) → Russian | German | **not yet run** | the run we are building the engine for now |

The two pipelines share every component below. What changes between them is a
small **per-pipeline parameter set**:

- **source language** — English (`mw_ru`) vs German (`pwg_ru`);
- **stage-0 masker rules** — `mw_ru` masks tags only; `pwg_ru` adds the
  PWG-specific `{%…%}` German-vs-Latin classifier (German gloss translated
  inline, Latin masked and left verbatim). See
  [src/pwg_mask.py](src/pwg_mask.py) and §4 of [pwg_ru.md](pwg_ru.md);
- **glossary** — English→Russian term pairs (`mw_ru`) vs German→Russian
  (`pwg_ru`, two glossaries: semantic core + lexicographic abbreviations);
- **seed** — `pwg_ru` is seeded by the finished `mw_ru` Russian card for any
  headword shared with MW (a *terminological anchor*, never copied); `mw_ru`
  had no such seed.

Everything else — placeholder masking discipline, the Sonnet-translate /
Opus-judge / Opus-retranslate loop, append-only versioning, per-card
round-trip assertion — is identical across both pipelines.

---

## 2. The strategic pivot: harvest-first

The earlier model (`mw_ru`) translated every gloss from scratch with an LLM.
`pwg_ru` changes that. For each headword we **assemble** the Russian from
material that already exists, and we use the LLM only for (a) genuine gaps and
(b) the source-language connective/scholarly prose that nothing else covers.

The material that already exists:

1. **Five extracted Sanskrit→Russian dictionaries** — `src/*.jsonl` produced by
   [src/build_src.py](src/build_src.py): `koch` / `kow` / `kna` / `fri` /
   `smirnov`, ~57,640 keyed entries total. The deterministic join over them is
   [src/corpus_gate.py](src/corpus_gate.py). (Data is gitignored; see
   [src/README.md](src/README.md).)
2. **The SamudraManthanam parallel corpus** — 122+ verse-aligned
   Sanskrit↔Russian translations (Rigveda, Mahabharata, Ramayana, 10+ Gita,
   Upanishads, kavya, Ashtangahridaya, and more). Lives in the sibling repo
   SamudraManthanam (queried read-only, never duplicated here).
3. **The `mw_ru` Russian cards** — for headwords shared with Monier-Williams.

**Crucial refinement.** Harvested Russian meanings are **not** merely anchors
for the LLM to copy. They become **additional attested senses** in the output
card, each tagged with its source. So `pwg_ru` ends up **richer than a plain
German translation**: it carries the German gloss rendered into Russian **plus**
corpus- and dictionary-attested Russian meanings. See §5 (Assembly).

---

## 3. Model plumbing — two different access paths

This is the single most important operational constraint, so it is stated
before the component diagram. There is **no Claude API key**. Therefore the
engine runs two physically different kinds of stages.

### 3a. Claude via Claude Code on the Max subscription (NOT a Python API client)

The Claude stages — Sonnet translates, Opus judges, Opus re-translates rejects
— run **through Claude Code**, as agent/workflow batches on the Max
subscription. They are **not** a Python `anthropic` client and must never be
written as one (there is no key to give such a client).

- **Pilot** = one Claude Code workflow over `N` cards.
- **Scale-up** = scheduled / looped Claude Code workflows ("run nonstop for a
  month, no limits").

| Claude stage | Model | Runs as |
|--------------|-------|---------|
| Translate the masked gaps | **Sonnet 4.6** | Claude Code workflow on Max |
| Judge translations (OK/BAD, severity 1–5) | **Opus 4.8** | Claude Code workflow on Max |
| Re-translate rejects (severity ≥ 3) | **Opus 4.8** | Claude Code workflow on Max |

### 3b. DeepSeek + OpenRouter via Python API (the high-volume work)

DeepSeek (API key, flat-rate, nonstop) reached through the OpenRouter gateway
**is** a Python API script. It owns the high-volume jobs:

- the **one-time corpus word-alignment lexicon build** (§4.1, component 1);
- a cheap **double-check / validation** pass over translations.

DeepSeek is chat-only (no embeddings) — which is fine; nothing in this engine
needs embeddings.

### 3c. YandexGPT — not in the pilot

YandexGPT is the second judge in the `pwg_ru` design, but its key arrives
later. **The pilot runs without it.** If a second judge is wanted in the pilot,
**DeepSeek substitutes** as the cheap second judge.

| Provider | Access path | Jobs |
|----------|-------------|------|
| Claude (Sonnet 4.6, Opus 4.8) | Claude Code workflows on Max | translate gaps, judge, re-translate rejects |
| DeepSeek (via OpenRouter) | Python API script | corpus word-alignment lexicon build; cheap double-check; pilot 2nd judge if wanted |
| YandexGPT 5.1 | (key later) | 2nd judge — **not in the pilot** |

**Launch: tomorrow. Pilot first.**

---

## 4. Component diagram (numbered, in prose)

Data flows through seven numbered components. Each card carries a small record
forward; harvested senses accumulate; the LLM fills only what is missing.

```
            ┌─────────────────────────────────────────────────────────────┐
            │  (1) corpus word-alignment lexicon builder  [DeepSeek, ONCE] │
            │      122+ verse-aligned texts → Sanskrit-word→Russian pairs  │
            │      → reusable corpus-derived S→R lexicon (gitignored)      │
            └───────────────────────────────┬─────────────────────────────┘
                                             │ (built once, then a lookup)
                                             ▼
 PWG/MW   (0) extractor+masker ──▶ (2) harvest layer ──▶ (3) translation runner
 source       {key1,key2,            5 dicts + corpus-      Sonnet → Opus judge
 file         headword,              lexicon + mw_ru seed   → Opus re-translate
              masked-skeleton,       → source-tagged           (DeepSeek check)
              placeholder-map}       attested Russian senses        │
                                             │                      ▼
                                             │              (4) stage-4 corpus gate
                                             │              corpus_gate.py + LLM verdict
                                             │              (two signals, non-blocking)
                                             ▼                      │
                                     (5) ASSEMBLY ◀─────────────────┘
                                     output card =
                                     translated German gloss
                                     PLUS harvested attested senses,
                                     each source-tagged  (richer than
                                     a plain translation)
```

### (0) Source extractor + masker

Walks the source dictionary into records and masks each so the translator sees
**only** translatable source-language prose; everything untranslatable becomes
a `{Tn}` placeholder, restorable left-to-right.

- **Output record per card:** `{key1, key2, headword, masked-skeleton,
  placeholder-map}`.
- **De = `pwg_ru`: BUILT** — [src/pwg_mask.py](src/pwg_mask.py). Splits
  `csl-orig/v02/pwg/pwg.txt` into `<L>…<LEND>` records and masks each into
  `{Tn}` placeholders. Verified on the full dictionary: **123,365 / 123,366**
  records round-trip losslessly (100.00%) — regenerate with
  `python src/pwg_mask.py stats`, which prints this count from the code on disk.
  `{%…%}` content classified 99.9% German (translate, kept inline) / 25 Latin
  (leave) / 230 ambiguous (flagged for the LLM). **One record is lossy** — so
  the runner **must** assert per-card round-trip and route any failure to
  manual review (see §6).
- **En = `mw_ru`: TODO** — an analogous masker for the English source. The
  finished `mw_ru` run used an equivalent masking discipline, but a
  parameterized engine component (`mw_mask`, sharing the `{Tn}` contract and
  round-trip assertion) is **not yet committed here**. The `pwg_mask.py` design
  is the template: same placeholder scheme, minus the `{%…%}` classifier.

### (1) Corpus word-alignment lexicon builder — DeepSeek, one-time

The parallel corpus is **verse-aligned, not word-aligned**: a passage has a
`#sa` Sanskrit segment and a `#ru` Russian segment under a shared group id, but
it does not say *which* Russian word renders *which* Sanskrit word. So we build
a durable layer **once**:

- a single bulk DeepSeek pass over **every** aligned verse across all 122+ texts
  extracts **Sanskrit-word → Russian-equivalent** pairs;
- the result is a **reusable corpus-derived Sanskrit→Russian lexicon**,
  gitignored like the five dictionaries;
- after this one pass, every later use is a **lookup**, not a re-derivation.

This is the **single biggest new asset** of the harvest-first design, and the
reason component (1) sits at the top of the diagram feeding component (2).

- **Status: TODO** (the build pass itself is not yet run). Its access path is
  fixed: DeepSeek via OpenRouter, a Python API script (§3b). The corpus it reads
  is queried from SamudraManthanam; the verse-aligned query plumbing already
  exists and is reused — see [src/corpus_gate.py](src/corpus_gate.py)
  (`corpus_examples`) and [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md).

### (2) Harvest layer

For each PWG headword, the harvest layer assembles the Russian from existing
material **before** any gap goes to the LLM:

- the deterministic **join over the five extracted S→R dictionaries** (`koch`,
  `kna`, `fri`, `smirnov` independent; `kow` reference), keyed by SLP1
  (`key1`, `key2` fallback; length-preserving `form_key()`);
- a lookup into the **corpus-derived lexicon** from component (1);
- the **`mw_ru` seed** for headwords shared with MW (terminological anchor).

Every harvested gloss is **tagged with its source and role** (independent vs
reference vs corpus-derived vs `mw_ru`-seed). The output of this layer is a
**set of source-tagged attested Russian senses** for the headword.

- **Status: BUILT (join + corpus query + heuristic pre-check)** —
  [src/corpus_gate.py](src/corpus_gate.py). Measured PWG coverage on the join
  (a `corpus_gate.py coverage` random sample, **fixed seed 20260615** — the
  sub-percentages are sample-size-dependent and will not reproduce at a
  different N): independent correctness **16.4%** (Кочергина 14.4% etc.), KOW
  reference **8.0%**, corpus ≈**14–15%**. Regenerate with
  `python src/corpus_gate.py coverage` (omit N to scan the full key set; pass N
  for a seeded random sample). Tuning result: token overlap is treated as
  **confident-pass only**; the LLM owns the `divergence` call. The
  **corpus-lexicon lookup** (component 1's output) and the **`mw_ru` seed**
  feed are **TODO** as harvest *inputs* — the corpus today contributes via the
  verse-aligned query, and the lexicon will make that contribution a cheap
  lookup. **The `mw_ru` seed is additionally BLOCKED**, not merely TODO: unlike
  every other harvest input it has **no concrete access path in this repo** —
  only [mw_ru.md](mw_ru.md) and [mw_ru_prompts/](mw_ru_prompts/) are present;
  the `mw_ru` **card data** lives in the (not-yet-located) future `mw_ru`
  working repo. A future repo cannot feed the pilot, so the seed is **off the
  pilot's critical path** — the pilot harvests from the five dicts + corpus
  alone. See the blocker list in §6.

### (3) Translation runner — Claude Code on Max

Translates only what the harvest layer left as a gap: the masked
source-language prose / connective text. Then the judge/retranslate loop:

1. **Sonnet 4.6** translates the masked German (or English) gaps — placeholders
   untouched, on the same positions.
2. **Opus 4.8** judges each translation OK/BAD with category + severity 1–5.
3. **Opus 4.8** re-translates rejects (severity ≥ 3), shown the error category
   and the judge's comment.
4. **DeepSeek** double-checks (cheap validation pass; §3b).

- **Status: TODO (no runner yet).** The **prompts exist** — the 6-file kit
  (5 prompts + 1 README) [pwg_ru_prompts/](pwg_ru_prompts/):
  [1_perevod.txt](pwg_ru_prompts/1_perevod.txt),
  [2_qa_sudya_opus.txt](pwg_ru_prompts/2_qa_sudya_opus.txt),
  [2_qa_sudya_yandexgpt.txt](pwg_ru_prompts/2_qa_sudya_yandexgpt.txt),
  [3_pereperevod_opus.txt](pwg_ru_prompts/3_pereperevod_opus.txt),
  [4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt),
  [README.md](pwg_ru_prompts/README.md). But stages 1–3 are **prompts only** —
  the Claude-Code workflow that drives them over a batch of cards is not yet
  written. The runner runs on the Max subscription, not a Python API (§3a).

### (4) Stage-4 corpus gate

A **non-blocking annotator** that runs after the runner. It never withholds a
card; it marks each one with **two independent signals**:

- **Signal 1 — correctness** vs the **independent** S→R dictionaries
  (Кочергина ∪ FRI ∪ KNA ∪ Смирнов): `pass` / `divergence` / `no-check` /
  `key-mismatch`. `divergence` at low confidence → editor queue; `no-check`
  passes through flagged "not covered".
- **Signal 2 — reference agreement** vs the **human** PWG→RU translation KOW
  (which descends from PWG/WIL, so it can corroborate but never *decide*
  correctness): `high` / `partial` / `none` / `no-ref`.

Mechanically: the deterministic part is [src/corpus_gate.py](src/corpus_gate.py)
(index `source → key1 → [Russian glosses]`, each tagged source + role; optional
soft corroboration from the parallel corpus); the verdict is the LLM step keyed
to [4_korpus_proverka.txt](pwg_ru_prompts/4_korpus_proverka.txt). SKD/VCP (and
the corpus) corroborate the referent but **never** decide correctness.

- **Status: BUILT (deterministic gate)** — `corpus_gate.py`. The **LLM verdict
  step** (the `4_korpus_proverka.txt` prompt) is a prompt; wiring it into the
  runner is **TODO**.

### (5) Assembly — the richer output card

The final card is assembled, **not** merely translated:

```
output card =  translated source-language gloss (Russian)
            +  harvested attested senses, each source-tagged
               (Кочергина / FRI / KNA / Смирнов / KOW / corpus-lexicon / mw_ru)
            +  stage-4 annotations (correctness signal, reference-agreement signal)
```

This is what makes `pwg_ru` **richer than a plain German translation**: the
German gloss rendered to Russian **plus** every corpus/dictionary-attested
Russian meaning the harvest layer found, each carrying its provenance tag.

- **Status: TODO** — the assembly/export step (merge translated gloss +
  source-tagged harvested senses + stage-4 signals into one card record) is not
  yet written. Its inputs (components 0, 2, 4) are partly BUILT; the merge is
  new.

---

## 5. Versioning and integrity invariants

- **Append-only, latest-wins.** Like `mw_ru`, each pass is written as a new
  versioned chunk; nothing is overwritten in place. When the dictionary is
  rebuilt, each card takes its **latest** version. The final `pwg_ru` is
  therefore layered: Sonnet base, Opus correction rounds on top, mechanical
  regex fixes, stage-4 annotations, harvested senses.
- **Per-card round-trip assertion (mandatory).** Because the masker has exactly
  one known lossy record out of 123,366, the runner **must** assert, per card,
  that `restore(skeleton, placeholder-map) == original` *before* sending to the
  translator, and route any failure to manual review rather than translating a
  corrupted skeleton. The assertion primitive already exists in
  [src/pwg_mask.py](src/pwg_mask.py) (`restore()`), but it is **not yet exposed
  as a runner-importable call** — today `restore()` runs only inside the
  `cmd_stats` / `cmd_card` CLI commands. Wiring it into the P3 harness as a
  per-card library assertion is the **NEXT** item; the runner must then call it
  on every card.

---

## 6. BUILT vs TODO — component summary

| # | Component | `pwg_ru` (De) | `mw_ru` (En) |
|---|-----------|---------------|--------------|
| 0 | Source extractor + masker | **BUILT** — [src/pwg_mask.py](src/pwg_mask.py) (123,365/123,366 lossless) | **TODO** — analogous `mw_mask` (run exists; component not committed here) |
| 1 | Corpus word-alignment lexicon builder (DeepSeek, one-time) | **TODO** — Python/OpenRouter script; corpus query plumbing reused | shared asset (Sanskrit→Russian; language-independent) |
| 2 | Harvest layer (5 dicts + corpus-lexicon + `mw_ru` seed) | **BUILT** join + corpus query + heuristic ([src/corpus_gate.py](src/corpus_gate.py)); corpus-lexicon lookup & seed feed **TODO** | the `mw_ru` cards are an **input** to this layer for `pwg_ru` |
| 3 | Translation runner (Sonnet → Opus judge → Opus re-translate; DeepSeek check) | **TODO** runner — prompts exist ([pwg_ru_prompts/](pwg_ru_prompts/)), workflow not written | run completed (see [mw_ru.md](mw_ru.md)) |
| 4 | Stage-4 corpus gate (non-blocking, two signals) | **BUILT** deterministic gate ([src/corpus_gate.py](src/corpus_gate.py)); LLM verdict wiring **TODO** | not part of `mw_ru` (new in `pwg_ru`) |
| 5 | Assembly → source-tagged richer card | **TODO** | n/a (plain translation) |

**Plumbing fixed (all components):** Claude stages (translate / judge /
re-translate) run through **Claude Code workflows on the Max subscription** —
never a Python Claude API client (no key). DeepSeek (via OpenRouter) and the
one-time corpus-lexicon build are **Python API scripts**. YandexGPT is **not in
the pilot**; DeepSeek substitutes as the cheap second judge if one is wanted.
Launch tomorrow, pilot first.

**Concrete blockers remaining (not on the pilot's critical path):**

- **DeepSeek / OpenRouter key** — needed for component (1)'s one-time
  corpus-lexicon build and the cheap double-check pass (§3b). Absent → those
  Python stages cannot run.
- **Corpus transport** — the verse-aligned parallel corpus must be reachable at
  the SamudraManthanam path the query plumbing reads
  (see [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md)); it is queried
  read-only and never duplicated here.
- **`mw_ru` card data** — the terminological seed (component 2) needs the
  `mw_ru` Russian **cards**, which are **not in this repo**: only
  [mw_ru.md](mw_ru.md) and [mw_ru_prompts/](mw_ru_prompts/) are present, and the
  card data sits in the future `mw_ru` working repo, **not yet located**. Until
  that repo is available, the seed feed stays off the pilot's critical path —
  the pilot harvests from the five dicts + corpus alone.

---

## 7. Related documents

- [pwg_ru.md](pwg_ru.md) — editor-facing process notes for the German→Russian
  run (the cards, the `{%…%}` rule, the two-signal gate).
- [mw_ru.md](mw_ru.md) — editor-facing account of the completed English→Russian
  run; the seed/reference for `pwg_ru`.
- [pwg_ru_prompts/](pwg_ru_prompts/) — the 6-file prompt kit (stages 1–4, with
  stage 2 carrying two judges, + one README).
- [src/README.md](src/README.md) — the five extracted S→R dictionaries and how
  [src/build_src.py](src/build_src.py) regenerates them.
- [SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md) — how the parallel corpus is
  queried (the sibling repo SamudraManthanam is read-only, never duplicated).
- The future `mw_ru` working repo and SamudraManthanam are separate
  repositories; their technical artifacts are not duplicated into this one.
