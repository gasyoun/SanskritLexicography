# Fast Print/DH Acceleration Review

Date: 2026-06-29

Purpose: answer the recurring operational question: what should be reviewed
next to move faster, satisfy Digital Humanities practice, and eventually print
a scholarly German -> Russian PWG dictionary with minimum human interaction?

This is a review pack only. It does not change prompts, schemas, audit gates, or
renderer code.

Executable packet: [NEXT_REVIEW_PACKET.md](NEXT_REVIEW_PACKET.md) is the narrow
operator checklist for fresh `sTA` audit plus print-renderer feasibility from
real examples.

## Executive Answer

| readiness level | verdict | next action |
|---|---|---|
| ready to continue bulk translation | **yes, after fresh `sTA` output** | Run the current optimized Max harness for `sTA`, save fresh `wf_output.json`, then audit it. |
| ready for reviewed DCS-frequency core tranche | **not yet** | Clear fresh `sTA`, then continue audited DCS-frequency windows and start G5 review from queue files. |
| ready for immutable DH edition | **not yet** | G5/G6/G7/G10 remain blocked; no edition cut should be made. |
| ready for printed bilingual dictionary | **not yet** | Print examples/spec exist, but reviewed rows, front matter, and a print renderer do not. |
| ready for full PWG tail | **not yet** | Decide tail strategy only after several audited core windows give speed and error-rate data. |

Fast answer: review fresh `sTA` first, not the whole 144k-entry tail. The current
bottleneck is stale workflow recovery; after fresh runs, measure Max quota,
requeue churn, and sampled semantic-review load.

Max batch-size answer: do **not** translate 10 big dhātus in one broad push yet.
Use the staged plan in [NEXT_REVIEW_PACKET.md](NEXT_REVIEW_PACKET.md): `sTA`
first, then `BU`/`as`/`i`, then prune and recheck `gam`/`yuj`/`vid`/`han`.

## Fastest Next Reviews

| priority | review | evidence | exact next action | owner |
|---|---|---|---|---|
| P0 blocks scale/print | Fresh `sTA` workflow output | `root_window_status.py sTA` says `stale_artifact`; rootmap expects 123 keys. | Run `src/pilot/run_pilot_wf.opt.js` in Max, save `wf_output.json`, then run `python src\pilot\audit_window.py wf_output.json --root sTA --write-requeue`. | max_workflow |
| P0 blocks scale/print | Deterministic audit before any semantic reading | `audit_window.py` is the canonical gate for stale/provenance, NWS, markup, coverage, sense duplicates, and prompt drift. | Read `audit_window.report.md` and `requeue.keys.txt`; requeue only named failing keys. | codex |
| P1 slows production | Semantic review queue | `prompt_semantic` and `judge_sample.keys.txt` separate high-confidence risks from clean-card sampling. | Review Python-gate failures first, high-confidence `prompt_semantic` risks second, `judge_sample.keys.txt` third. | human_editor |
| P1 slows production | Throughput evidence | Current status has one stale/recovered root; not enough to price full PWG. | Record wall-clock/token fields for `sTA`, `BU`, and `gam`; update cost estimates after three clean windows. | codex |
| P1 slows production | Batch-size evidence | `BU`, `as`, and `i` are clean-ready; `gam`, `yuj`, `vid`, and `han` currently have stale generated inputs. | Run staged roots, not 10 at once: `sTA`, then `BU`/`as`/`i`, then prune/recheck stale roots. | max_workflow |

Review order is fixed:

1. Python-gate failures.
2. `prompt_semantic` high-confidence risks.
3. `judge_sample.keys.txt`.
4. G5/G6/G7 human evidence.
5. Print/DH renderer and front-matter decisions.

## Digital Humanities/FAIR Review

Current strengths:

- License, citation, DOI plan, TEI Lex-0, OntoLex, reverse index, release
  readiness, and gate snapshots exist.
- The production audit refuses stale workflow output and expects rootmap/input
  provenance.
- Interop artifacts validate independently of print-readiness.

Current DH blockers:

| priority | finding | evidence | exact next action | owner |
|---|---|---|---|---|
| P0 blocks scale/print | Accepted cards must be traceable to fresh workflow provenance. | Current `wf_output.json` is stale; fresh Max output must carry metadata accepted by `audit_window.py`. | Do not accept stale output; rerun `sTA` and audit against current rootmap/input hashes. | max_workflow |
| P0 blocks scale/print | No immutable edition while human gates are blocked. | `release_readiness.py` reports G5/G6/G7/G10 blocking. | Complete G5/G6/G7, then run `python src\make_edition_cut.py edition_vN` and `python src\validate_release.py release\edition_vN`. | human_editor |
| P1 slows production | Outside-scholar reproduction is not yet a single recipe. | The pieces exist across runbooks, release files, audit reports, and schemas. | Later add a reproducibility recipe: source XML -> rootmap/input hash -> Max output -> audit -> review status -> edition manifest. | future_release |
| P2 improves scholarly polish | Citation/DOI metadata is provisional until edition cut. | `CITATION.cff` and `DOI_PLAN.md` remain pre-release artifacts. | At edition cut, update citation version, DOI, release date, manifest checksums, and rights statement. | future_release |

DH conclusion: continue bulk translation now, but do not claim an immutable
edition until every included card has review status and release-manifest
provenance.

## Print Dictionary Review

Use [PRINT_ENTRY_SPEC.md](PRINT_ENTRY_SPEC.md) as the target and
[PRINT_ENTRY_EXAMPLES.md](PRINT_ENTRY_EXAMPLES.md) as real layout evidence.
The `agni`, `akzara`, and `ap` examples are prototypes only, not print-ready
publication text.

| priority | print issue | exposed by | exact decision needed | owner |
|---|---|---|---|---|
| P0 blocks scale/print | Zero reviewed print-ready rows. | G5 reports 0 print-ready rows. | Complete G5 review rows for the release slice. | human_editor |
| P1 slows production | Long citation runs can swamp the page. | `agni` | Define citation compaction/apparatus rules before renderer implementation. | renderer |
| P1 slows production | Nested labels and homonym/gender blocks are mandatory. | `akzara`, `ap` | Renderer must support nested sense labels, homonym blocks, and gender headers. | renderer |
| P1 slows production | NWS rows need compact but one-to-one display. | `agni`, `ap` | Use compact owner badges while preserving one row per owner. | renderer |
| P1 slows production | `{%...%}`, `<ls>`, `<ab>`, and sigla need locked display policy. | `ap` and spec display table | Keep source tokens validated until rendering; abbreviations go to front matter, not silent expansion. | renderer |
| P2 improves scholarly polish | Front matter remains unassembled. | Current docs are separate. | Create editorial principles, abbreviation/sigla list, source table, QA method, limitations, license/DOI statement. | future_release |

Print conclusion: build no renderer yet. First lock review evidence and display
policy from the existing examples.

## Minimum Human Actions

| gate | file | allowed human edits | validation command | done when |
|---|---|---|---|---|
| G5 | `src/_review_queue.csv` | `reviewer_id`, `decision`, `edit`, `notes` only | `python src\run_batch.py validate_review` and `python src\preflight_remaining_gates.py` | Included release rows are reviewed or explicitly excluded. |
| G6 | `gold/_human_gold_review.csv` | `human_label`, `reviewer_id`, `confidence`, `needs_adjudication`, `human_note` only | `python src\gold_status.py gold\_human_gold_review.csv` and `python src\gold_validate.py gold\_human_gold_review.csv` | 320/320 gold rows complete and valid. |
| G7 | `gold/_double_review_queue.csv` | second-review columns only | `python src\gold_double_review_verify.py gold\_double_review_queue.csv --sample-size 80`, ingest, then `python src\gold_agreement.py` | 80-row double review validates and agreement report exists. |

No human should be asked to "review more" without a named file, allowed columns,
validation command, and done condition.

## Immediate Commands

Run from the `RussianTranslation` repo root:

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

If mechanical gates pass:

```powershell
# Review only prompt_semantic high-confidence risks and judge_sample.keys.txt.
python src\pilot\root_window_status.py BU
python src\pilot\gen_opt_harness.py BU
```

For print/DH gates:

```powershell
python src\run_batch.py validate_review
python src\gold_status.py gold\_human_gold_review.csv
python src\preflight_remaining_gates.py
python src\release_readiness.py
```

Do not cut an immutable edition or claim print readiness until G5/G6/G7/G10 pass.
