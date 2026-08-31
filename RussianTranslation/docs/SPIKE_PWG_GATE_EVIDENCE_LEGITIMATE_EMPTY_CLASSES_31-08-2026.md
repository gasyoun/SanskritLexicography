# Spike — legitimate-empty input classes per gate (W1 / H3748)

_Created: 31-08-2026 · Last updated: 31-08-2026_

The [VERIFICATION doc](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_CLAUDE_HARDENING_WAVE.md) named one risk before W1 was allowed to start: an evidence-carrying gate may FAIL on an input class that is *legitimately* empty, and the cure for that must never be silence. This is that spike, run **before** `assert_nonvacuous()` was switched on.

Machine-readable twin: `LEGITIMATE_EMPTY` in [`RussianTranslation/src/pilot/gate_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gate_evidence.py) (`python src/pilot/gate_evidence.py --registry`). The two must agree; the module refuses an unregistered `gate_id` and an unregistered empty-class name, so a call site cannot invent an excuse after the fact.

## The rule

1. Zero **hits** is a PASS — the gate looked and found nothing wrong.
2. Zero **evaluations**, or zero inputs carrying content, is a FAIL — the gate did not look.
3. Unless the gate *declares* the emptiness by a pre-registered name, in which case the PASS stands and the sidecar records `vacuity: "declared_empty"` with the reason. The declaration is a claim the author signs, not an inferred silence.

An empty tuple in the registry is itself a claim: **that gate has no legitimately-empty input class**, so any emptiness there is a defect and will be red.

## Per gate

| Gate id | #1803 row | Legitimate-empty classes | Why legitimate | What would make it stop being legitimate |
|---|---|---|---|---|
| `lane_spotcheck_freshness` | `C2-2` | `no_telemetry_dir`, `no_spotcheck_reports` | Both already fail **closed**: `fresh_spotcheck` returns `None`, and `nonstop_scheduler` then refuses auto-promote. An empty telemetry dir is a correct "surveillance is not running" answer, not a green light. | If a caller ever treated `None` as "fine, proceed" — then the emptiness would be laundering a refusal into a pass. |
| `gold_agreement` | `C6-01` | `no_double_reviewed_items` | A corpus reviewed once by one human has no pair to compute Cohen κ over. The precision half is still fully measured; only the agreement half is `n/a`. The existing release-mode guard already refuses that state for a release. | In release mode. There it is already a hard exit, and stays one. |
| `spot_check_daily` | `C6-05` | `no_promotions_for_date` | A day with zero auto-promotions has nothing to sample. Sampling 10 % of nothing is not a failure of the sampler. | If promotion records exist for the date and the sample is still empty — that is a broken sampler, and is red. |
| `prompt_rule_audit` | `C3-4` | *(none)* | The audited template is a **committed** file. Its absence is exactly the defect `--fail-on-missing` was built to catch and silently did not (issue row C3-4). | — |
| `corpus_gate_coverage` | `C2-5` | *(none)* | The PWG headword index is committed. "0 % coverage" printed because the sources were never built is the defect; a real measured zero would still have scanned keys. | — |
| `launch_ledger` | `C8-4` | `no_launch_failures_recorded`, `no_runlog_launch_headings` | An empty launch-failure ledger is a **good history**, not a dead gate — the ledger records incidents, and having none is the desired state. Likewise a `--since` window containing no launch-shaped RUN_LOG heading. | If the ledger is unparseable or the fenced block is missing — that is not emptiness, it is breakage, and `load_ledger` already exits. |
| `changelog_duplicate_bullets` | `C8-3` | `no_changelog_in_repo` | The script is repo-generic and already prints "nothing to check". A repo with no changelog has no entries to duplicate. | A repo that *has* a changelog whose parse yields zero entries — a real parser failure, and red. |
| `run_observability_census` | `C8-7` | `no_events_logged` | A fresh box before the first run has an empty append-only events log. Every counter is honestly zero. | Any non-empty log that yields zero census rows. |
| `prompt_compiler_golden` | `C3-1` | *(none)* | The goldens are written by the selftest itself immediately before they are read, so they are never legitimately absent. (The self-comparison weakness the row names is a separate, still-open defect — see scope below.) | — |
| `interop_validity` | G9, [#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798) | *(none)* | A release artifact with zero entries is never valid. `validate_tei` already fails on "TEI contains no entries"; the evidence record makes the count and the uniqueness predicate explicit. | — |

## Scope note — what W1 deliberately does NOT change

Per the [ARCHITECTURE doc](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_CLAUDE_HARDENING_WAVE.md) §1: **no gate's predicate logic changes in W1 — only its accounting.** The single behavioural change is that a PASS which examined nothing becomes a FAIL. So the underlying predicate defects that #1803 also names (C2-2's mtime-only freshness that accepts a 0-byte file; C6-01's `release_mode` path comparison; C8-4's 3-digit `H\d{3}` regex; C3-1's compiler-against-itself golden) stay live and stay filed. What changes is that each now leaves a hashed, counted record — a 0-byte input is stamped into `warnings`, an unparsed input shows `units: 0` — so those defects are visible in evidence instead of hidden behind a green line.

The one exception is G9 ([#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798)), where the handoff mission explicitly calls for a **new** duplicate-entry-id predicate, and the promote path ([#1800](https://github.com/gasyoun/SanskritLexicography/issues/1800)), where the claim is widened to cover the read-modify-write span.

_Dr. Mārcis Gasūns_
