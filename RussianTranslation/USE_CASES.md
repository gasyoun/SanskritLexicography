# RussianTranslation Use Cases

Operational scenarios for the PWG -> Russian production pipeline. The canonical
runbook remains [src/pilot/RUN_FREQ_MAX.md](src/pilot/RUN_FREQ_MAX.md); this
page is a quick map from intent to command path.

## 1. Preflight the Next Root

Use when deciding whether a frequency-window root is ready for Max spend.

```powershell
python src\pilot\root_window_status.py <root>
```

Expected outcome: one `next action` and one `next command`. Trust this output
over older handoff prose. A matching optimized harness must have the same root,
rootmap hash, and selected key scope.

## 2. Run a Fresh Max Window

Use when a root is structurally ready and no fresh workflow output exists.

```powershell
python src\pilot\gen_opt_harness.py <root>
# run src\pilot\run_pilot_wf.opt.js in Claude/Max Workflow
# save the JSON as wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Mechanical acceptance requires the deterministic audit to pass. The audit checks
workflow provenance, NWS owner attribution, markup fidelity, sense coverage, and
cross-part duplicate senses before writing queue/status files.

## 3. Recover from Stale Output

Use when `wf_output.json` belongs to an older rootmap or harness.

```powershell
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

Expected outcome: state `stale_artifact`. The audit refuses collect/gates/glue
and preserves the existing `requeue.keys.txt`. Run
`python src\pilot\root_window_status.py <root>` next: if the optimized harness
matches the current rootmap, rerun that harness in Max and save a fresh
`wf_output.json`; regenerate only if the status command says the harness is
missing, invalid, or scoped to the wrong keys. Use `--allow-stale` only for
forensic inspection.

## 4. Rerun Only Mechanical Failures

Use when `src/pilot/output/requeue.keys.txt` is non-empty.

```powershell
python src\pilot\requeue_from_audit.py <root>
# run the regenerated optimized harness in Max Workflow
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
```

The rerun harness is built only from current rootmap keys. Stale or invalid
requeue keys are rejected before Max spend.

## 5. Send a Semantic Judge Sample

Use after all mechanical gates pass and `judge_sample.keys.txt` is non-empty.

```powershell
Get-Content src\pilot\output\judge_sample.keys.txt
```

This queue contains all Python-gate failures plus a deterministic clean-card
sample. It is for semantic mistranslation review only; it is not the mechanical
requeue list.

## 6. Monitor Local Operations

Use while running or auditing windows.

```powershell
python src\pilot\dashboard_server.py --port 8765
```

Open `http://127.0.0.1:8765/`. The dashboard reads local status, audit reports,
ledger rows, dashboard events, queue files, freshness data, and print-gate
snapshots. It does not create human review decisions.

## 7. Check Release and Print Readiness

Use when validating downstream artifacts without cutting an edition.

```powershell
python src\preflight_remaining_gates.py
python src\release_readiness.py --release-dir release
python src\validate_interop.py --dir release
```

The print-readiness scripts are report-only by default. Add `--fail-on-blocked`
when using them as a CI/go-no-go gate. Current G5/G6/G7/G10 blockers require
human review/gold work.

`release/` is the staging directory for generated interop artifacts. The
immutable-edition validator expects an edition subdirectory created by
`make_edition_cut.py`, for example:

```powershell
python src\validate_release.py release\edition_v1
```

## 8. Resume Corpus Lexicon API Work

Use when DeepSeek/OpenRouter calls fail during corpus-lexicon construction.

```powershell
python src\build_corpus_lexicon.py build <textfile> [N] [workers] --retry-failed
```

Tune `DEEPSEEK_RETRIES`, `DEEPSEEK_CONNECT_TIMEOUT`,
`DEEPSEEK_READ_TIMEOUT`, and `DEEPSEEK_BACKOFF_BASE` for unstable network
conditions. Failed batches are logged locally and retried append-only.

---

# Structured grammar layer

The grammar layer is **structured data, not part of translation** (the
[A/B test](NOMINAL_GRAMMAR_AB.md) showed grammar-in-the-prompt does not help DE→RU). Hub:
[GRAMMAR_LAYER.md](GRAMMAR_LAYER.md); design: [ZALIZNYAK_INDEX.md](ZALIZNYAK_INDEX.md).

## 9. Look Up a Headword's Grammar / Inflection Index

Use when you need a headword's stem class, Whitney §§, compound split, or its compact
Zaliznyak index token.

```powershell
python src\nominal_grammar.py --show agni m.            # full block (JSON)
python src\nominal_grammar.py --index agni m. agni/     # just the token, e.g. m·3b
python src\whitney_grammar.py --show gam                # verb-root grammar
```

`--index` takes an optional accented form (PWG `<k2>`, `/` marks the udātta) for the stress
slot. Token format `G·T S F` = gender · Whitney type 0–8 · stress a/b/— · flags `*°+N`.

## 10. See a Headword's Declension Table

Use to render the actual vidyut paradigm for a noun/adjective.

```powershell
python src\nominal_grammar.py --table agni m.
python src\nominal_grammar.py --paradigm senA f.        # JSON (feminine ā/ī/ū use nyap)
```

8 cases × 3 numbers, SLP1→IAST. Indeclinables/unsupported genders return no paradigm.

## 11. List Every Headword in a Paradigm (Reverse Dictionary)

Use to pull all PWG headwords sharing one inflection class, or to render that class's
shared paradigm template (Zaliznyak's «Грамматические сведения»).

```powershell
python src\reverse_index.py --query "m·8n*"      # list headwords (an-stems, gradation)
python src\reverse_index.py --show  "m·8n*"      # representative paradigm + members
python src\reverse_index.py --stats 30           # paradigm distribution
```

## 12. Rebuild the Grammar Dataset / FAIR Package

Use after `csl-orig` PWG/MW updates, or to regenerate the materialized data.

```powershell
python src\mw_compounds.py --build               # MW <k2> compound lookup
python src\whitney_grammar.py --build            # root layer (needs WhitneyRoots sibling)
python src\reverse_index.py --build              # index + per-word headword_index.tsv + stats
```

Outputs are the resources described by [src/datapackage.json](src/datapackage.json)
(Frictionless, CC-BY-SA-4.0). The **portraits are never touched** by these builds, so the
translation harness cannot inline grammar; nominal windows run grammar **OFF**.

## 13. Get Accented RV Forms for the Accent Axis (VedaWeb)

Use when building/validating the Vedic accent a–f axis (the one open extension).

```powershell
curl -s -X POST https://vedaweb.uni-koeln.de/api/search `
  -H "Content-Type: application/json" -d '{"type":"quick","q":"agni"}'
```

Hits carry per-resource highlights; the udātta word-split is in the Casaretto et al. (2025)
annotation resource `66695e4a14f6d337f7788740` (lemma `679b7da2…`, accented text `66695c4b…`).
Bulk: `GET /api/resources/{id}/export`. CC BY 4.0. See
[ZALIZNYAK_INDEX.md](ZALIZNYAK_INDEX.md) §"Vedic accent mobility".
