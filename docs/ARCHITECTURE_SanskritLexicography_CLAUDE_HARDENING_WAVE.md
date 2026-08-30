# Architecture — Claude Code hardening wave (pwg_ru pipeline)

_Created: 30-08-2026 · Last updated: 30-08-2026_

Component boundaries, contracts, and build-vs-reuse verdicts for the eight wave units. Index: [PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md).

## 1. The gate-evidence contract (W0/W1) — the load-bearing structure

The wave's central architectural change is one new module, not nine patches:

- **`RussianTranslation/src/pilot/gate_evidence.py`** (new, small): a `GateEvidence` record — `gate_id`, `inputs_examined` (count + content hash per input), `predicates_evaluated` (name + hit count each), `verdict`, ISO timestamp. One constructor, one `emit()` writing a JSON sidecar next to the gate's existing report, one `assert_nonvacuous()` that turns `inputs_examined == 0` (or all-predicates-zero-evaluations) into a hard FAIL.
- **The nine gates named in [#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803)** are retrofitted to build their verdict THROUGH this record. No gate's predicate logic changes in W1 — only its accounting. Behavior change is limited to: a PASS that examined nothing becomes a FAIL.
- **Consumers** (`audit_store_gates.py`, `window_selftest.py`, CI's RussianTranslation-gates job) read the sidecar; a missing sidecar after W1 means the gate did not run the contract — itself a FAIL.
- [#1800](https://github.com/gasyoun/SanskritLexicography/issues/1800) (promote claim guards the write, not the read-modify-write) is architecturally the same disease — the claim must wrap the whole read-modify-write span, and the evidence record is where the wrapped span's before/after hashes land.
- [#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798): G9's validity predicate gains a duplicate-entry-id check (12,374 known duplicates must flip it RED on the frozen fixture).

W0 precedes all of this: the repo-level epistemic integrity gate ([#1864](https://github.com/gasyoun/SanskritLexicography/issues/1864)) must be green on master so "merge only on green CI" is meaningful for every later unit.

## 2. Store-mutation pattern (W4/W5) — reuse, don't invent

Both logic revisions follow the **H3591 restore pattern** verbatim (build-vs-reuse: REUSE — [`restore_store_rows_from_mirror.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/restore_store_rows_from_mirror.py) is the shipped precedent):

1. **Census first** — a read-only script measures the affected population and writes a dated report under `RussianTranslation/reports/`. If the measured population differs ≥2× from the issue's claim, the rewrite half HALTS and the unit delivers census-only (ruling 14).
2. **Ledgered rewrite** — every changed row gets a JSONL ledger row (old value, new value, rule, timestamp) committed alongside; the ledger lands in the same PR as the rewrite.
3. **Mirror refresh** — `pwg-ru-data/tm/` refreshed in the same pass; `audit_store_gates.py` proves the delta equals the ledger (`changed_ru` exactly the ledger's row count, hard flags unchanged).
4. **Gates prove it** — after W1, the gates that pass are evidence-carrying, so the proof is a count, not a stamp.

W4's mapping fix itself lives where the `h<N>` index is assigned (fragmentize/assembly path), with the census keyed on the printed homograph column; W5's relation labels are re-derived from actual layer attachment, not layer identity.

## 3. Mechanical batch (W2) — no new structure

- H3/H4/H5/H7/H10 from the [H1811 fixlog](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1811/H1811_PIPELINE_REVIEW_FIXLOG_2026-07-29.md) each follow the fix shape already recorded there (e.g. H3 routes checkpoint writes through the fsynced `window_common.atomic_write_text`; H7 mirrors staged C4's consecutive-no-progress backstop).
- The 41-module `sibling_root.py` migration is a pure call-site sweep to the canonical resolver ([#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804)); REUSE — the resolver already exists (H2889), no path logic is authored.

## 4. Provenance measurement (W3) — census before design

A read-only pass over `pwg_ru_translated.jsonl` + the promotion/campaign ledgers classifies every row's provenance stamp as measured / asserted / absent, then designs (does NOT execute) the stamp backfill: what evidence exists per era, what is honestly unrecoverable. Output is a report + FINDINGS row + a backfill spec — execution is a later, separately-authorized act because it rewrites provenance fields at scale.

## 5. Fragmentizer (W6) and perf (W7)

- W6 changes [`pwg_tm_fragmentize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_fragmentize.py) only at the span-join step: `{%…%}` spans separated solely by an `<is>`…`</is>` run merge into ONE fragment before emission. Existing store rows keep their fragment identity (non-goal 5).
- W7 is measurement-led: profile the real hot paths first (coordinator claim/audit, residual ledger, TM), fix only the top ~10 confirmed by timings, each with before/after numbers. The 939 static I/O-in-loop findings are the map. `coordinator.py` is at 1.0/10 health and untested — W7 runs LAST among the parallel units and adds a characterization test before touching any hot function.

## Build-vs-reuse summary

| Piece | Verdict | Prior art |
|---|---|---|
| Gate evidence record | **Build** (small, nothing exists — the absence IS #1803) | — |
| Store rewrite machinery | **Reuse** | H3591 ledger + mirror-refresh pattern, `audit_store_gates.py` |
| Path resolution | **Reuse** | `sibling_root.py` (H2889) |
| Checkpoint atomic writes | **Reuse** | `window_common.atomic_write_text` |
| Census/report tooling | **Reuse** | `RussianTranslation/reports/` dated-report convention |
| Profiling harness | **Build** (thin) | `/drain` bytes/4 method for the timing discipline |

_Dr. Mārcis Gasūns_
