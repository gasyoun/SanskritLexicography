# AGENTS.md — RussianTranslation repo-local instructions

This file extends the org-level Sanskrit Lexicon instructions for this repo only.
The current repo objective is the PWG (Petersburger Wörterbuch) → Russian edition
pipeline, with article-comparison Russian review work as the secondary track.

## Scope and Current Truth

- **Primary track:** scale PWG → Russian through the frequency-window Max
  workflow described in `src/pilot/RUN_FREQ_MAX.md`.
- **Secondary track:** finish the article-comparison flagship pair
  `agni` + `akṣara` in `../article-comparison/`, after human sign-off on the
  review proposals.
- Treat `.ai_state.md` as the live local journal. It is subordinate to
  `../.ai_state.md`; when work changes the project state, keep both in lockstep
  if the parent state is relevant.
- Trust current command output and `src/pilot/output/window_status.json` over
  stale prose in older handoff files.

## PWG → Russian Production Loop

Use the optimized Max Workflow route. Do not run the committed template
`src/pilot/run_pilot_wf.js` directly for production windows.

Immediate next operator action:

1. Run the fresh `sTA` Max Workflow using the regenerated optimized harness for
   the 123-card/citation-batch rootmap.
2. Save the Max result as `wf_output.json`.
3. Audit it:

```powershell
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

If `requeue.keys.txt` is non-empty, build and run the targeted rerun harness:

```powershell
python src\pilot\requeue_from_audit.py sTA
```

If mechanical gates pass and `judge_sample.keys.txt` is non-empty, send only
that key set to semantic judging. After `sTA` is mechanically clean and judged as
needed, advance to `BU`.

Canonical loop from the repo root:

```powershell
python src\pilot\root_window_status.py <root>
python src\pilot\gen_opt_harness.py <root>
# run src\pilot\run_pilot_wf.opt.js in Claude/Max Workflow and save wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Current queue: finish `sTA` re-batch cleanup, then `BU`, `gam`, `yuj`, `as`,
`i`, `vid`, `han`.

The generated optimized harness:

- inlines raw and portrait inputs;
- disables translate-agent tools with `tools: []`;
- carries provenance metadata for root, selected keys, rootmap hash, and input
  hashes;
- is the supported in-chat Workflow route.

Any Max run where translate agents use file reads is using an obsolete harness.

## Audit and Acceptance Rules

Bulk acceptance is deterministic-first:

- `audit_window.py` is the canonical audit command.
- It runs NWS owner-map, markup fidelity, sense coverage, and sense-duplicate
  gates over the same workflow key set.
- Stale workflow output must be refused unless doing forensic inspection with
  `--allow-stale`.
- If stale output is refused, do not overwrite an existing `requeue.keys.txt`.
- `requeue.keys.txt` is the mechanical rerun list.
- `judge_sample.keys.txt` is the semantic review spend queue, not the mechanical
  requeue list.

NWS owner mismatches, markup failures, coverage failures, duplicate-sense
failures, missing cards, and stale inputs are requeue/blocking conditions, not
acceptable outputs.

If Max reports token or timing numbers, record them on the audit command so
`window_status.json` and `window_ledger.jsonl` preserve production economics:

```powershell
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue `
  --wall-clock-minutes <minutes> `
  --max-cache-read-tokens <n> `
  --max-cache-create-tokens <n> `
  --max-output-tokens <n> `
  --max-total-tokens <n>
```

If the weekly Max cap fires, also pass:

```powershell
--weekly-cap-fired --weekly-cap-cumulative-tokens <n>
```

## Generated and Archived Files

Generated/local runtime files are ignored and should not be treated as
deliverables:

- `src/pilot/run_pilot_wf.opt.js`
- `src/pilot/run_pilot_wf.run.js`
- `src/pilot/run_pilot_wf.headtest.js`
- `wf_output.json`
- `src/pilot/output/*.json`
- `src/pilot/output/*.md`
- `src/pilot/output/*.jsonl`
- `src/pilot/output/*.keys.txt`
- `release/gate_status_snapshot.*`
- `src/corpus_lexicon.failures.jsonl`

Superseded a-section/manual Max files under
`src/pilot/archive/legacy_max_2026-06-27/` are audit history only. Do not revive
them for current production windows.

## Python and Encoding

- Run Python scripts from the repo root unless a runbook explicitly says
  otherwise.
- Keep all text files UTF-8 without BOM.
- When adding Python that writes Sanskrit/Russian/German text, use
  `encoding="utf-8"` explicitly.
- On Windows-facing scripts that print non-ASCII text, configure stdout/stderr
  for UTF-8.
- Prefer deterministic local scripts over ad hoc manual editing of generated
  artifacts.

## Translation and Markup Policy

- Preserve PWG printed sense order.
- Preserve `{#...#}`, `<ls>...</ls>`, source sigla, and German abbreviations such
  as `Bed.` and `Schol.` verbatim unless a runbook says otherwise.
- Render all Nachträge patches; dropping a patch is a coverage failure.
- Treat `<is>...</is>` as source siglum text, not as a Russian gloss wrapper.
- Preserve NWS owner attribution exactly, one row per source.
- Renou labels are badges/context only; never reorder senses because of Renou
  classification.

## Corpus and External API Work

Claude production translation is not a local Python Claude API loop. It runs
through the Claude/Max Workflow surface.

DeepSeek/OpenRouter corpus-lexicon builds are append-only and resumable. Failed
batches are logged locally in `src/corpus_lexicon.failures.jsonl` and can be
retried with:

```powershell
python src\build_corpus_lexicon.py build <textfile> [N] [workers] --retry-failed
```

Tune `DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`,
`DEEPSEEK_READ_TIMEOUT`, and `DEEPSEEK_BACKOFF_BASE` for poor network
conditions.

## Verification Expectations

For code changes, run the narrowest relevant checks. Common checks include:

```powershell
python -m py_compile <changed-python-files>
python src\pilot\root_window_status.py <root>
python src\pilot\gen_opt_harness.py <root>
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
python src\verify_root_glue.py
node --check src\pilot\run_pilot_wf.js
```

Do not claim a production window is accepted until the deterministic audit gates
pass and the requeue status is understood.

## Session State Protocol

Maintain `.ai_state.md` using the existing section structure:

```markdown
# Project Objective: [Global Goal]
## ➡️ Next Steps (Queue)
## 🚧 Current Work-In-Progress (WIP)
## 🧠 Dev Notes & Hypotheses (Bugs, ideas, context)
## ✅ Completed (Recent only)
```

During work, record logical milestones, persistent bugs, and changed hypotheses.
On handoff, make next steps concrete. Avoid letting `.ai_state.md` diverge from
the actual operational state.
