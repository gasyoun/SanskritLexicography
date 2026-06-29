# Print + DH + Speed Readiness Review

Date: 2026-06-28

This review answers one practical question: what must be fixed to translate PWG
faster and eventually publish a scholarly bilingual German -> Russian
dictionary, without manually judging all entries.

Next operational companions:

- [PRINT_DH_ACCELERATION_REVIEW.md](PRINT_DH_ACCELERATION_REVIEW.md) is the
  compact "what to review next" queue: fresh `sTA`, deterministic audit,
  sampled semantic review, human gates, then print/DH decisions.
- [HUMAN_REVIEW_MINIMIZATION.md](HUMAN_REVIEW_MINIMIZATION.md) turns the G5/G6/G7
  blockers into exact reviewer files, editable columns, and validation commands.
- [PRINT_ENTRY_SPEC.md](PRINT_ENTRY_SPEC.md) defines the target printed bilingual
  entry shape before any PDF/LaTeX/HTML renderer is built.
- [PRINT_ENTRY_EXAMPLES.md](PRINT_ENTRY_EXAMPLES.md) tests that target against
  real local `agni`, `akzara`, and `ap` merged-card prototypes without treating
  stale workflow output as publication evidence.
- [roadmap/print_review_minimum.json](roadmap/print_review_minimum.json) is the
  machine-readable minimum human-review queue.

## Executive Verdict

| readiness level | verdict | reason |
|---|---|---|
| ready to continue bulk translation | **yes, with one immediate action** | `sTA` is structurally ready: 123/123 raw and portrait files present, optimized harness scoped to 123 keys, and prompt-rule wiring passes. The current `wf_output.json` is stale and must be replaced by a fresh Max Workflow run before advancing. |
| ready for reviewed core tranche | **not yet** | The DCS-frequency path is ready, but `sTA` still needs fresh output, deterministic audit, targeted requeue if needed, and sampled semantic judging. |
| ready for immutable digital edition | **not yet** | Interop artifacts validate, but G5/G6/G7/G10 are blocked: review decisions 0/217, gold labels 0/320, no real double-review agreement report, and no edition cut. |
| ready for printed bilingual dictionary | **not yet** | Print/export machinery exists only as interoperable data artifacts. Human review, typographic/display policy, front matter, and an edition cut are still missing. |
| ready for full PWG tail | **not yet** | The near-term target is the DCS-frequency core tranche. Full PWG tail strategy should be decided after several audited root windows establish speed, requeue rate, and semantic error rate. |

Bottom line: the engine is ready to continue the bulk run window-by-window, not
to claim a finished 144k-entry printed dictionary.

## Speed Blockers

| priority | finding | evidence | recommended fix | owner |
|---|---|---|---|---|
| P0 blocks scale/print | Fresh `sTA` Max output is required before any next root. | `root_window_status.py sTA`: state `stale_artifact`; old workflow has 106 keys, current rootmap expects 123; next action says run generated optimized harness and save fresh `wf_output.json`. | Run the current `src/pilot/run_pilot_wf.opt.js` in Max, save output as `wf_output.json`, then run `python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue`. | max_workflow |
| P1 slows production | Human review should start from ranked queues, not ad hoc reading. | `prompt_rule_audit.py --cards wf_output.json --review-limit 25`: 491 risks across 47 old/stale keys; prompt rules pass; ranked queue exists. | After a fresh audit, read `prompt_rule_audit.md` and `judge_sample.keys.txt` first; do not browse whole windows manually. | human_editor |
| P1 slows production | Max quota remains the main throughput unknown. | `RUN_FREQ_MAX.md`: cost/quota table needs enough windows to estimate duration; one root does not answer run-to-cap. | Record wall-clock and token fields on every `audit_window.py` run. After `sTA`, `BU`, and `gam`, update `PILOT_COST.md` and decide Max-seat vs paid API. | codex |
| P2 improves scholarly polish | The runbook still mentions a separate pre-audit semantic command before `audit_window.py`, while `audit_window.py` now includes `prompt_semantic`. | `RUN_FREQ_MAX.md` documents both `prompt_rule_audit.py --cards` and the integrated audit path. | Keep the separate command as optional preview only; trust `audit_window.py` for canonical reports and requeue. | codex |

## Digital Humanities/FAIR Blockers

| priority | finding | evidence | recommended fix | owner |
|---|---|---|---|---|
| P0 blocks scale/print | No immutable edition cut can be made until human gates close. | `release_readiness.py`: blockers are G5, G6, G7, G10. `gate_status_snapshot.md`: review decisions 0/217, gold complete 0/320, double review 0/80, latest edition none. | Complete G5 review decisions, G6 gold labels, G7 double review, then run `python src\make_edition_cut.py edition_vN` and `python src\validate_release.py release\edition_vN`. | human_editor |
| P0 blocks scale/print | Accepted cards must remain traceable to fresh workflow provenance. | `audit_window.py` refuses stale artifacts; current `wf_output.json` has no workflow meta and mismatched keys. | Do not accept any Max output without embedded `meta`; always audit against current rootmap/input hashes. | max_workflow |
| P1 slows production | Citation metadata is present but still provisional. | `CITATION.cff`: repository URL is generic and version is `unreleased`; `DOI_PLAN.md` says DOI comes after `release/edition_vN`. | At edition cut, update `CITATION.cff` with final repository URL, version, DOI, and release date. | future_release |
| P1 slows production | License story is usable but should be copied into release front matter. | `DATA_LICENSE.md`: CC BY-SA 4.0 dataset/edition scope, PWG public-domain source, third-party approvals, corpus caveats. | Include a release-level license and rights summary in front matter and edition manifest. | future_release |
| P2 improves scholarly polish | Interop export validates, which is excellent, but it is not a print layout. | `release_readiness.py`: G9 ready; TEI entries 120173, OntoLex entries 120173, reverse rows 209319. | Keep TEI/OntoLex as DH deliverables; add a separate print/typesetting path. | future_release |

## Print-Readiness Blockers

| priority | finding | evidence | recommended fix | owner |
|---|---|---|---|---|
| P0 blocks scale/print | There are zero print-ready reviewed rows. | `preflight_remaining_gates.py`: G5 review decisions 0/217 and print-ready rows 0. | Fill reviewer CSV decisions, run `python src\run_batch.py validate_review`, then apply validated review decisions. | human_editor |
| P0 blocks scale/print | Human gold and double-review evidence are absent. | `release_readiness.py`: G6 human gold 0/320; G7 double-review report missing. | Complete `gold/_human_gold_review.csv`, validate/ingest it, generate double-review queue, ingest labels, and run agreement report. | human_editor |
| P1 slows production | A bilingual print layout policy is not yet a validated artifact. | Existing validated artifacts are TEI Lex-0, OntoLex, and reverse index; no PDF/LaTeX/typeset export is reported by readiness gates. | Define a print view from final-card fields: Sanskrit headword, German PWG source/sense, Russian rendering, citations, NWS rows, Nachträge, and notes. | future_release |
| P1 slows production | Front matter still needs to be assembled as an edition object. | Existing docs cover method, license, DOI plan, manuals, failures, and runbook, but no single print-front-matter file is validated. | Create front matter after core-tranche review: editorial principles, abbreviation/sigla table, source table, QA method, license, limitations. | future_release |
| P2 improves scholarly polish | Typography decisions are not yet locked. | Sanskrit transliteration, Cyrillic, German abbreviations, `{#...#}`, `<ls>`, `<ab>`, `<is>`, and Nachträge all have processing rules, but no print stylesheet decision. | Decide display conventions before PDF/typesetting: what remains verbatim, what becomes tooltip/endnote, and how source sigla are indexed. | human_editor |

Exact next human packet: use [HUMAN_REVIEW_MINIMIZATION.md](HUMAN_REVIEW_MINIMIZATION.md).
Exact print target: use [PRINT_ENTRY_SPEC.md](PRINT_ENTRY_SPEC.md). The print
spec is intentionally descriptive; renderer code comes later.
Example evidence layer: use [PRINT_ENTRY_EXAMPLES.md](PRINT_ENTRY_EXAMPLES.md)
to review renderer/editorial decisions before implementing the print renderer.

## Lexicographic Quality Risks

| priority | finding | evidence | recommended fix | owner |
|---|---|---|---|---|
| P0 blocks scale/print | Current semantic-risk report is based on stale `wf_output.json`; do not use it for final acceptance. | `root_window_status.py sTA` marks stale artifact; `prompt_rule_audit.py --cards wf_output.json` reports old/stale keys. | Rerun Max for fresh `sTA`, then trust the new `prompt_semantic` section inside `audit_window.report.md`. | max_workflow |
| P0 blocks scale/print | Deterministic gates must remain mandatory before sampled semantic judging. | `RUN_FREQ_MAX.md`: stale, missing-card, NWS, markup, coverage, duplicate, and prompt-rule drift checks are canonical. | Continue the fixed loop: Max -> `audit_window.py` -> requeue until clean -> `judge_sample.keys.txt`. | codex |
| P1 slows production | Manual-derived semantic rules are wired and should not be re-litigated every window. | `prompt_rule_audit.py`: 11 required rules pass in both template and optimized harness; live coverage includes Apresjan, Hartmann, Gonda/Vogel, Tubb, Baalbaki, Apte/Gillon/Inglese-Geupel, and Mitrenina/Zaliznyak-Paducheva/Ruppel. | Treat prompt-rule audit as a drift check; spend human time on `review_queue` items and judge samples. | human_editor |
| P1 slows production | Some semantic risks require editor judgment, not automatic rerun. | `prompt_rule_audit.py`: suspicious `source_type` evidence and possible compression are review hints; only high-confidence mechanical risks feed requeue. | Keep noisy heuristics non-blocking; read ranked queue before broad manual review. | human_editor |
| P2 improves scholarly polish | Riemer/Klosa are methodology/design inputs, not live hard rules. | `prompt_rule_audit.json`: Riemer and Klosa reported as methodology-only. | Promote only concrete, testable rules into prompt/audit gates later; do not block current scale-up on them. | future_release |

## Immediate Next Commands

Run these in order from the `RussianTranslation` repo root:

```powershell
python src\pilot\root_window_status.py sTA
# Run src\pilot\run_pilot_wf.opt.js in Max Workflow and save fresh wf_output.json.
python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue
```

If `requeue.keys.txt` is non-empty:

```powershell
python src\pilot\requeue_from_audit.py sTA
# Run the regenerated harness in Max, save wf_output.json, rerun audit_window.py.
```

If mechanical gates pass and `judge_sample.keys.txt` is non-empty, send only
those keys to sampled semantic judging. After `sTA` is clean and judged as
needed, advance to:

```powershell
python src\pilot\root_window_status.py BU
python src\pilot\gen_opt_harness.py BU
```

For print/DH release readiness, the next human commands are:

```powershell
python src\run_batch.py validate_review
python src\gold_status.py gold\_human_gold_review.csv
python src\preflight_remaining_gates.py
python src\release_readiness.py
```

Do not cut an immutable edition until G5/G6/G7 pass.
