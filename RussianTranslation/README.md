# RussianTranslation

Russian-edition working area for Sanskrit lexicography projects, with the live
PWG → Russian production pipeline as the active track.

## Current PWG Path

The current production route is the frequency-window Max workflow documented in
[`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md):

```powershell
python src\pilot\root_window_status.py <root>
python src\pilot\gen_opt_harness2.py <root>
# run src\pilot\run_pilot_wf.opt.js in Claude/Max Workflow and save wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

The generated optimized harness inlines inputs, disables tools for translation
agents, carries provenance metadata, and is audited by deterministic Python gates
before any mechanical acceptance.

For task-oriented operator flows, see [USE_CASES.md](USE_CASES.md). It covers
preflight, fresh Max windows, stale-output recovery, targeted requeue, sampled
semantic judging, dashboard monitoring, release readiness checks, and corpus API
retry work.

## Structured grammar layer (the 3rd axis)

Alongside translation, pwg_ru carries a **structured grammatical layer** per headword —
verb-root and nominal. It is **recorded as data, not injected into translation** (the
[A/B test](NOMINAL_GRAMMAR_AB.md) showed grammar-in-the-prompt does not improve DE→RU and
sometimes hurts it). Hub: [`GRAMMAR_LAYER.md`](GRAMMAR_LAYER.md).

| Piece | What | File(s) |
|---|---|---|
| Root grammar | PWG root → Whitney class/PPP/§§/exceptions (crosswalk join) | [`src/whitney_grammar.py`](src/whitney_grammar.py) |
| Nominal grammar | stem class · Whitney §§ · vidyut paradigm · MW compound segmentation | [`src/nominal_grammar.py`](src/nominal_grammar.py), [`src/mw_compounds.py`](src/mw_compounds.py) |
| Inflection index | compact Zaliznyak-style token `G·T S F` (e.g. `m·8n*`) | [`ZALIZNYAK_INDEX.md`](ZALIZNYAK_INDEX.md), `zaliznyak_index()` |
| Reverse dictionary | index token → every headword in that paradigm; per-word FAIR dataset | [`src/reverse_index.py`](src/reverse_index.py) |
| Declension display | render the vidyut paradigm table for a headword / token | `nominal_grammar.py --table`, `reverse_index.py --show` |
| A/B verdict | grammar-in-prompt rejected; evidence appendix | [`NOMINAL_GRAMMAR_AB.md`](NOMINAL_GRAMMAR_AB.md), [`NOMINAL_GRAMMAR_AB_DETAIL.md`](NOMINAL_GRAMMAR_AB_DETAIL.md) |

```powershell
python src\reverse_index.py --build              # materialize index + per-word grammar TSV
python src\reverse_index.py --show "m·8n*"       # paradigm template + members
python src\nominal_grammar.py --table agni m.    # one headword's declension
```

FAIR outputs (committed): `src/headword_index.tsv` (98,639 headwords ·
`k1·hom·lex·accented·index·stem_class·compound·irregularities`),
`src/reverse_paradigm_index.json`, `src/paradigm_stats.tsv`, described by a Frictionless
[`src/datapackage.json`](src/datapackage.json) (CC-BY-SA-4.0, archivable on its own DOI track).
The **portraits are deliberately left untouched** so the translation harness never inlines
this; nominal windows run grammar **OFF** by default. Open extension (unblocked + probed): the
full Vedic accent a–f axis, validated against [VedaWeb 2.0](https://vedaweb.uni-koeln.de) — see
[`ZALIZNYAK_INDEX.md`](ZALIZNYAK_INDEX.md) §"Vedic accent mobility".

Task-oriented command flows for all of the above are in [USE_CASES.md](USE_CASES.md) §§9–13
(look up a headword's grammar/index · render a declension · list a paradigm's headwords ·
rebuild the dataset · pull accented RV forms from VedaWeb).

## Guardrails

- `root_window_status.py` is the pre-spend truth source for each root. It checks
  rootmap/input structure and verifies that the optimized harness matches the
  intended selected-key scope.
- `audit_window.py` refuses stale workflow artifacts before collect/gates/glue,
  preserves existing requeue files on stale refusal, and writes status/ledger
  artifacts for the dashboard.
- `nws_split.py` audits NWS owner attribution with root-split sub-card filename
  handling; missing raw/card files requeue, while cards with no NWS layer remain
  neutral.

## Local dashboard

A read-only local dashboard serves live pipeline status **and an evolution
timelapse** at `http://127.0.0.1:8765/`:

```powershell
python src\pilot\dashboard_server.py --port 8765
```

Panels: **Run Status** (current window · gates · queues · production metrics),
**Evolution Timelapse**, **Print Gates**, **Recent Events**, **Window Ledger**,
**File Freshness**. The page polls `/api/status` every few seconds
(`--refresh-ms`); the timelapse polls `/api/evolution` (cached on source mtimes)
on a slower cadence.

The **Evolution Timelapse**
([`src/pilot/evolution_stats.py`](src/pilot/evolution_stats.py)) derives the
pipeline's maturation story from the append-only logs — throughput, PWG/DCS
coverage, an **academic-rigor index** (share of cards carrying full
model+pipeline provenance), quality (requeue rate), cost (tokens/window), speed
(minutes/window), and a **failure typology** ("what was wrong" over time). Static
trend charts plus a **play/scrub** control replay the history day by day, and a
**Trends** panel surfaces the computed insights. Run it standalone to write
`output/evolution_stats.json`:

```powershell
python src\pilot\evolution_stats.py
```

**Failure auto-capture:** `audit_window.py` auto-appends error-level incidents
(kill-gate / stale refusals) to `failures/auto_failures.jsonl` (git-ignored,
de-duped per root/day) via
[`src/pilot/failure_capture.py`](src/pilot/failure_capture.py). The curated
post-mortems in [`failures/FAILURE_GALLERY.md`](failures/FAILURE_GALLERY.md) +
`failures/failures.jsonl` stay human-authored; the dashboard reads both streams.

## Flaky Network Policy

Claude production translation is not a Python Claude API loop. It runs through
the Claude/Max Workflow surface, and interruptions are handled by deterministic
state files:

- null or failed cards are written into `src/pilot/output/requeue.keys.txt`;
- `requeue_from_audit.py` builds a rerun harness for only those cards;
- stale `wf_output.json` artifacts are refused before they can mutate outputs.

DeepSeek/OpenRouter corpus-lexicon builds are append-only and resumable. Tune
`DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`, `DEEPSEEK_READ_TIMEOUT`, and
`DEEPSEEK_BACKOFF_BASE` when the connection is poor. Failed API batches are
logged locally to `src/corpus_lexicon.failures.jsonl` and can be retried later:

```powershell
python src\build_corpus_lexicon.py build <textfile> [N] [workers] --retry-failed
```

## Runtime Artifacts

Generated workflow, dashboard, status, ledger, requeue, and corpus retry files
are ignored by git. Superseded Max/a-section artifacts live in
[`src/pilot/archive/legacy_max_2026-06-27/`](src/pilot/archive/legacy_max_2026-06-27/)
for audit history only.
