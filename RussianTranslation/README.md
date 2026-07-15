# RussianTranslation — Sanskrit dictionaries into Russian, at scale

_Created: 28-06-2026 · Last updated: 11-07-2026_

This directory holds two independent machine-translation efforts that bring the
great 19th-century Sanskrit dictionaries to Russian readers, plus the
structured-grammar and translation-memory assets built alongside them:

- **mw_ru (complete):** an AI Russian translation of the full Monier-Williams
  dictionary — 287,358 cards, multi-pass, multi-model, with two independent QA
  judges per card. How it was produced:
  [`mw_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md);
  per-stage system prompts:
  [`mw_ru_prompts/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/mw_ru_prompts).
- **pwg_ru (live production):** PWG (Böhtlingk–Roth, the "Petersburg
  Dictionary", 1855–1875 — still the largest Sanskrit dictionary ever
  compiled) → Russian (primary) and English (secondary), headword by
  headword, preserving Sanskrit and citation markup exactly. Everything below
  is about this pipeline.

## The problem, stated as research

PWG has ~106,000 headwords; the source is 19th-century lexicographic German
dense with Sanskrit spans, grammar labels, and hundreds of thousands of source
citations that must survive translation byte-for-byte. At this scale the only
economically viable translator is an LLM — so the actual research object is
not "can a model translate a dictionary entry" (it can; independent
gold-sample judging measured 96–98.5% faithfulness) but **how to make an LLM
pipeline reliable, cheap, and mechanically verifiable across a hundred
thousand entries**. The answers — masking, batching, deterministic audit
gates, content-addressed translation memory, cost gates, kill gates, and
multi-agent orchestration guards — are documented as they were found, failure
by failure, in
[`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md).

## Method in one paragraph

Each headword's entry is assembled from a **5-layer merged source** (PWG base
plus the PW / Schmidt / PWK-Nachträge / NWS supplement layers), split into
sub-cards, and every untranslatable span (Sanskrit, citations, grammar labels)
is **masked to `{Tn}` tokens** so the model translates only the German prose;
markup is restored mechanically afterwards, which makes markup fidelity a
*checkable invariant* rather than a hope. Several cards are packed per agent
call (the fixed per-call system-prompt overhead, not the content, dominated
cost — batching+masking cut it 72–90%). Output is accepted only by a stack of
**deterministic, zero-LLM audit gates** (coverage, sense duplicates, markup
fidelity, untranslated-residue detectors, ownership attribution), each gate
itself regression-pinned with selftests after three separate rounds of
gate-bug hunting. A **content-addressed translation memory** (whole-card and
fragment level) makes reruns and shared fragments free; oversized or
sense-dense cards are pre-split into bounded fragment groups; a wall-clock
kill gate abandons any call that overruns its size-scaled time budget; and
multi-agent fan-outs run only through a dispatch-and-monitor wrapper that
judges liveness by output-file growth. Human judgment enters at defined
gates — interactive HTML review sheets, gold-sample judge sessions — never as
silent post-editing.

## Datasets (committed, FAIR)

| Asset | What | Where |
|---|---|---|
| Headword index | 98,639 headwords: homonym no. · lexical category · accented form · inflection index · stem class · compound segmentation · irregularities | [`src/headword_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/headword_index.tsv) |
| Reverse paradigm index | Zaliznyak-style index token → every headword in that paradigm | [`src/reverse_paradigm_index.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reverse_paradigm_index.json) |
| Paradigm statistics | Distribution of stem classes / index tokens across the lexicon | [`src/paradigm_stats.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/paradigm_stats.tsv) |
| Frictionless descriptor | Data-package metadata for the grammar dataset (CC-BY-SA-4.0) | [`src/datapackage.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/datapackage.json) |
| Addenda-relationship rollup | 5,603 supplement-layer senses classified by relationship to the PWG base | [`pwg_ru/relationships_rollup.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/relationships_rollup.tsv) |
| Arm-A/B synthesis scores | Re-glue vs synthesize-first bake-off metrics (10 words) | [`pwg_ru/reglue/synth_outputs/ARMB_SCORES.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/reglue/synth_outputs/ARMB_SCORES.tsv) |

Large regenerable artifacts (the translation store itself, TM files, learner
scores, re-glue outputs, review sheets) are deliberately local-only /
gitignored — the repo is public, the unpublished Russian text is not. The
Sa→Ru translation memory (1.09M verse-aligned pairs + a 10,132-pair
precision-gated mined tier + a specialist glossary tier) is graded A/B/C by
[`src/tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py)
and exportable as standard TMX 1.4b via
[`src/build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py);
its FAIR public release is queued behind a rights clearance.

## Who uses this, and for what

- **A Russian-speaking Sanskrit student** gets the learner apparatus: a
  22,772-headword *learner-core* subset (the 21% of PWG that Russian student
  dictionaries actually retain), declension tables for any headword
  (`python src\nominal_grammar.py --table agni m.`), and a reverse dictionary —
  "show me every word that declines like this one"
  (`python src\reverse_index.py --show "m·8n*"`), with a compact
  Zaliznyak-style inflection index familiar from Russian lexicography
  ([`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)).
- **A lexicographer / historian of dictionaries** gets a machine-read map of
  how the Petersburg dictionary family actually fits together: which of the 5
  layers defines each headword
  ([`PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md) —
  ~36% of the headword union has *no* PWG record), a typed classification of
  every supplement-layer sense (restatement vs. new sense vs. correction), and
  measured edition deltas (what AP90→AP and MW72→MW silently dropped).
- **An NLP / MT researcher** gets a large graded Sanskrit–Russian translation
  memory with TMX export, a reproducible masking-and-gating harness design for
  high-fidelity structured-text MT, and a documented failure taxonomy
  (concurrency cliffs, retry-cap drivers, orchestration failure modes) with
  the measured fixes.
- **A working translator with CAT tooling** can import the TMX 1.4b export
  directly once the TM release clears.

## Milestones

Condensed from the full narrative in
[`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
(each phase there carries the evidence, PR links, and the exact failure that
forced the change):

| Phase | Dates (2026) | What changed |
|---|---|---|
| 0 | → 06-26 | Groundwork: DCS frequency prioritization, grammar layer, first judge gate (37/38 publishable) — quality fine, process is the problem |
| 1 | 06-26→27 | First end-to-end production root through the Workflow tool; `audit_window.py` gate stack born |
| 2 | 06-27→29 | Cost crisis solved: masking + batching harness, −72–90% measured; 4 roots complete |
| 3 | 06-29→30 | 44 more roots; the concurrency cliff (18-wide → 117 transient nulls) → the standing ≤3-wide rule |
| 4 | 06-30→07-01 | EN pilot; head-splitter / self-heal fragment lane; nominal grammar ships as data (A/B: grammar-in-prompt rejected) |
| 5 | 07-01→02 | Translation memory (card + fragment level); gold-sample judge 96–98.5% faithful; 4 real gate bugs fixed |
| 6 | 07-02→03 | Gate-bug hunt: `gam`'s "residuals" were 3 gate bugs, not defects — re-audited to 127/127 clean; `OUTPUT_BUDGET=90` calibrated live |
| 7 | 07-03→04 | Readiness audit → scope ruling: drain all 703 remaining DCS-attested verb roots, one at a time |
| 8 | 07-04 | Drain begins; sense-density presplit trigger + wall-clock kill gate; fragment-tag collision fixed |
| 9 | 07-05→06 | The 36%-no-PWG gap closed: no-PWG supplement-chain cards render; 232-lemma backfill queue documented |
| 10 | 07-05→06 | Nominal-lane cost post-mortem, independently re-verified, then the first 100/100-card production window |
| 11 | 07-05→06 | TM industrialization: mined tier (97% precision gate, 10,132 pairs), A/B/C grading, TMX 1.4b export |
| 12 | 07-05→06 | Re-glue research track: addenda typology, learner scores, and the bake-off verdict — synthesize-first does not beat re-glue |
| 13 | 07-06 | Multi-agent orchestration post-mortem → `synth_dispatch.py` guards (output-file liveness, kill-guard, sealed outputs) |

## Operating the pipeline (quickstart)

The production route is the frequency-window Max workflow documented step by
step in
[`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md);
task-oriented flows for every operator situation are in
[`USE_CASES.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md).

```powershell
python src\pilot\perf_preflight.py <root> --json     # cost gate first, always
python src\pilot\root_window_status.py <root>        # pre-spend truth source
python src\pilot\gen_opt_harness2.py <root>          # emit the optimized harness
# run src\pilot\run_pilot_wf.opt2.js in the Claude/Max Workflow, save wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

The preflight report estimates agents/tokens/cost and partitions mixed windows
into `cost_partition.run_now` / `cost_partition.defer_monster`, so one
expensive `kAla`-class card can be quarantined without blocking the cheap
cards in the same window. Multi-agent synthesis fan-outs (re-glue / edition
work) run only through
[`src/synth_dispatch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py) —
never as bare async dispatches.

## Structured grammar layer (the 3rd axis)

Alongside translation, pwg_ru carries a **structured grammatical layer** per
headword — verb-root and nominal. It is **recorded as data, not injected into
translation** (the A/B test
[`NOMINAL_GRAMMAR_AB.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NOMINAL_GRAMMAR_AB.md)
showed grammar-in-the-prompt does not improve DE→RU and sometimes hurts it).
Hub: [`GRAMMAR_LAYER.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GRAMMAR_LAYER.md).

| Piece | What | File(s) |
|---|---|---|
| Root grammar | PWG root → Whitney class/PPP/§§/exceptions (crosswalk join) | [`src/whitney_grammar.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/whitney_grammar.py) |
| Nominal grammar | stem class · Whitney §§ · vidyut paradigm · MW compound segmentation | [`src/nominal_grammar.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/nominal_grammar.py), [`src/mw_compounds.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_compounds.py) |
| Inflection index | compact Zaliznyak-style token `G·T S F` (e.g. `m·8n*`) | [`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md), `zaliznyak_index()` |
| Reverse dictionary | index token → every headword in that paradigm; per-word FAIR dataset | [`src/reverse_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/reverse_index.py) |
| Declension display | render the vidyut paradigm table for a headword / token | `nominal_grammar.py --table`, `reverse_index.py --show` |
| A/B verdict | grammar-in-prompt rejected; evidence appendix | [`NOMINAL_GRAMMAR_AB.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NOMINAL_GRAMMAR_AB.md), [`NOMINAL_GRAMMAR_AB_DETAIL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NOMINAL_GRAMMAR_AB_DETAIL.md) |

```powershell
python src\reverse_index.py --build              # materialize index + per-word grammar TSV
python src\reverse_index.py --show "m·8n*"       # paradigm template + members
python src\nominal_grammar.py --table agni m.    # one headword's declension
```

The portraits are deliberately left untouched so the translation harness never
inlines this; nominal windows run grammar **OFF** by default. Open extension
(unblocked + probed): the full Vedic accent a–f axis, validated against
[VedaWeb 2.0](https://vedaweb.uni-koeln.de) — see
[`ZALIZNYAK_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)
§"Vedic accent mobility".

## Guardrails

- [`src/pilot/root_window_status.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/root_window_status.py)
  is the pre-spend truth source for each root: rootmap/input structure, and
  that the optimized harness matches the intended selected-key scope.
- [`src/pilot/perf_preflight.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py)
  is the cost gate: estimated agents/tokens/$, refusal of over-ceiling
  windows, `run_now` / `defer_monster` partitioning of mixed windows.
- [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
  emits only agent-reachable raw/portrait payloads; TM-resolved and degenerate
  pass-through cards stay accounted in their own self-contained constants.
- [`src/pilot/autosplit_requeue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py)
  sub-splits citation-dense fragments at complete `<ls>...</ls>` spans without
  ever tearing an open Sanskrit `{#...#}` span.
- [`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)
  refuses stale workflow artifacts before collect/gates/glue, preserves
  existing requeue files on stale refusal, and writes status/ledger artifacts
  for the dashboard.
- [`src/pilot/nws_split.py`](https://github.com/gasyoun/SanskritLexicography/blob/48ac903b4c5f1076fda86a22030e7cf65e5915e5/RussianTranslation/src/pilot/nws_split.py)
  (retired in [PR #67](https://github.com/gasyoun/SanskritLexicography/pull/67);
  link pinned to the last pre-retirement commit) audited NWS owner attribution
  with root-split sub-card filename handling; missing raw/card files requeued,
  while cards with no NWS layer stayed neutral.
- [`src/synth_dispatch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py)
  is the only sanctioned way to run a multi-agent fan-out: ≤4 concurrency,
  10-minute output-file kill-guard, single-owner sealed outputs, watcher-safe
  landing, programmatic assembly for >800-citation entries.

## Local dashboard

A read-only local dashboard serves live pipeline status **and an evolution
timelapse** at `http://127.0.0.1:8765/`:

```powershell
python src\pilot\dashboard_server.py --port 8765
```

Panels: **Run Status** (current window · gates · queues · production metrics),
**Evolution Timelapse**, **Print Gates**, **Recent Events**, **Window Ledger**,
**File Freshness**. The **Evolution Timelapse**
([`src/pilot/evolution_stats.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/evolution_stats.py))
derives the pipeline's maturation story from the append-only logs —
throughput, coverage, an academic-rigor index (share of cards carrying full
model+pipeline provenance), quality, cost, speed, and a failure typology over
time — with a play/scrub control replaying the history day by day.

**Failure auto-capture:**
[`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)
auto-appends error-level incidents (kill-gate / stale refusals) to
`failures/auto_failures.jsonl` (git-ignored, de-duped per root/day) via
[`src/pilot/failure_capture.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/failure_capture.py).
The curated post-mortems in
[`failures/FAILURE_GALLERY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/failures/FAILURE_GALLERY.md)
stay human-authored; the dashboard reads both streams.

## Flaky-network policy

Claude production translation is not a Python API loop — it runs through the
Claude/Max Workflow surface, and interruptions are handled by deterministic
state files: null/failed cards land in `src/pilot/output/requeue.keys.txt`;
[`src/pilot/requeue_from_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py)
builds a rerun harness for only those cards (TM lookup force-disabled); stale
`wf_output.json` artifacts are refused before they can mutate outputs.

DeepSeek/OpenRouter corpus-lexicon builds are append-only and resumable. Tune
`DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`, `DEEPSEEK_READ_TIMEOUT`, and
`DEEPSEEK_BACKOFF_BASE` when the connection is poor; failed batches are logged
to `src/corpus_lexicon.failures.jsonl` and retried with:

```powershell
python src\build_corpus_lexicon.py build <textfile> [N] [workers] --retry-failed
```

## Runtime artifacts

Generated workflow, dashboard, status, ledger, requeue, and corpus retry files
are ignored by git. Superseded Max/a-section artifacts live in
[`src/pilot/archive/legacy_max_2026-06-27/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src/pilot/archive/legacy_max_2026-06-27)
for audit history only.

_Dr. Mārcis Gasūns_
