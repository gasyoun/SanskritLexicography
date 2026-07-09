# Gate-truthfulness + requeue cache-bypass + launch-ledger re-audit (H424)

_Created: 09-07-2026 · Last updated: 09-07-2026_

Adversarial re-verification of [FIX_PLAN_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FIX_PLAN_2026-07-09.md)
P0 items #1 (requeue/TM cache-bypass) and #2 (gate truthfulness), per handoff
[H424](https://github.com/gasyoun/Uprava/blob/main/handoffs/H424-Opus_RussianTranslation_gate_truth_requeue_ledger_reaudit_09.07.26.md).
The premise attacked: `window_selftest.py` + `lang_parity_check.py` + `check_launch_ledger.py`
passing proves the *fixtures* pass — not that a live child-gate crash can be swallowed as
CLEAN, nor that a gate-rejected card/fragment can be re-served from cache. Method was
read-only + the three deterministic checkers; stance was "a gate is truthful only if you
cannot make a crash look green."

**Verdict: RE-VERIFIED CLEAN on `master` `9ac9ed1`.** No proven false-clean, no proven
cache-reuse of rejected content. No code change; no new `LAUNCH_FUCKUPS.md` row (nothing
manifested in a real run). One pre-existing 🟡 residual re-confirmed as still
parent-mitigated (below), not a new defect.

Model: audited by **Opus 4.8** (`claude-opus-4-8`).

## Deterministic checkers (read-only, re-run)

| Checker | Result |
|---|---|
| [`check_launch_ledger.py --since 2026-07-05`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/check_launch_ledger.py) | `10 entries complete` (exit 0) |
| [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) | `window selftest OK` (incl. `test_denylist_torn_line_fails_loud`, `test_audit_window_tag_routing`) |
| [`lang_parity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py) | `37 entries, all verdicts complete, no drift` |

## 1 — Requeue re-runs; no cache re-serve of rejected content — ✅ CLOSED

The past failure (gate-failed cards regenerated from TM/cache and getting the same defective
output back — the "gam requeue trap") is blocked by **two independent layers**:

| Claim | Evidence (`master 9ac9ed1`) | Verdict |
|---|---|---|
| Defect/all requeue forces `--no-tm` | [`requeue_from_audit.py:177-178`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) appends `--no-tm` for `which != 'transient'` | ✅ |
| `--no-tm` actually propagates into generation | [`gen_opt_harness2.py:322-324`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) sets `tm=None`; `:387` resolves only the `__default__`/`__auto__` sentinels, so `tm_path` stays `None`; both card TM (`:891`) and fragment TM (`:951`) are gated on truthy `tm_path` → **neither lane loads** | ✅ not just CLI-accepted |
| Failed **card** hashes denylisted | `append_tm_denylist` appends `kind:'card'`, `address='<lang>:<sha256(raw)>'` (`:88-96`) | ✅ |
| Failed **fragment** hashes (`fsha`) denylisted | same fn appends `kind:'frag'` rows from `requeue.defect.fshas.txt` (`:99-107`), which [`audit_window.py:522-525`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) emits from each defect card's `frag_prov` | ✅ |
| Denylist consulted on the **next** serve | [`translation_memory.load_tm:394`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py) skips denied card addresses; `load_frag_tm:510` skips denied `fsha` | ✅ |
| **Silent-drop hole** (§W1: `JSONDecodeError` skip re-enables reuse) | `load_denylist:234-240` now **raises `DenylistError`** on a torn line; propagated (uncaught) by both `load_tm:389` and `load_frag_tm:496` → any TM lookup **fails loud** before serving | ✅ CLOSED (landed `ddd53e6`, #273) |

**Cache-bypass proof.** Gate fails card `C` / fragment `F` → `requeue_from_audit --defect`
(a) denylists `C`'s card address and `F`'s `fsha`, and (b) runs generation with `--no-tm`,
so neither TM lane is even loaded in the requeue run. A *future* `--tm=auto` window sharing
`C`'s masked source or `F`'s fragment text is still denied at `load_tm`/`load_frag_tm`. `C`/`F`
cannot come back byte-identical from card TM or fragment TM. A torn denylist row no longer
silently re-enables reuse — it aborts the lookup.

## 2 — Gate truthfulness: no crash reads as clean — ✅ TRUTHFUL

[`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) runs six gates (`nws`, `translation`, `stage2_mechanical`, `coverage`, `sense_dupes`, `prompt_semantic`).

| Failure injected into a child gate | Parent behavior | Verdict |
|---|---|---|
| Missing/malformed `FLAGGED_JSON` line (wording drift, empty stdout) | `parse_flagged_json` returns **`None`, never `[]`** (`:71-88`); parent sets `requeue = sorted(keys)` (ALL) + `unparseable_verdict=True` (`:399-405`) → added to `crashed` (`:470-471`) | ✅ fails loud, requeues whole window |
| Non-zero child exit (exception / exit ≥2) | `if gate['returncode'] not in (0,1): crashed.append(name)` (`:468-469`) | ✅ FAIL, not skipped |
| Subprocess exceeds 1800 s | `run_py` `subprocess.run(timeout=1800)` raises `TimeoutExpired`, uncaught → whole audit aborts with traceback, no report, no promotion | ✅ loud (not false-clean) |
| Final disposition | `sys.exit(1 if report['requeue'] or crashed else 0)` (`:592`); `crash_state`/`audit_end` events emit at `level='error'` | ✅ crash ⇒ non-zero exit |
| Partial cards / fidelity drift | recorded per-key (`:484-497`), surfaced in report + summary (`:573-580`); at promotion, [`promote_final_cards.py:144-150`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) stamps `provenance.partial_card=True` + `missing_fragments/groups/senses` on **every row**, pinned by selftest (`:230-238`); TM `reconstruct_cards` then **skips** any partial row (`translation_memory.py:283-287`) | ✅ survives into store provenance, never TM-cached as complete |

**RU/EN parity.** [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py)
imports `stage2_pregate` (`:71`) and folds the **same** `stage2_pregate.pregate(g,e)['flags']`
in-process (`:187`) — the shared mechanical invariants, matching `stage2_pregate_en_wiring_h405`
SHARED in [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md).
EN carries the same crash-is-not-clean discipline: a sense-dupe subgate that cannot run is
tracked in `crashed_files` and fails `--strict` (`:324, :355, :381-392`); the module docstring
states it explicitly (`:42`). No RU-only gate lacks an EN twin that should be SHARED.

### Re-confirmed pre-existing residual (🟡, not new, parent-mitigated)

The three subprocess auditors use `results = find_results(...) or []`
([`audit_translation.py:82`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_translation.py), and the coverage/sense-dupe siblings) — a *silent-empty*, not a crash, so a child that finds
zero results emits `FLAGGED_JSON: []` (reads clean). This was rated 🟡 parent-mitigated in the
H188 audit (PR #198) and **remains** so: the child's `find_results` (`:65-78`) is the identical
recursive `results` descent as the parent's `workflow_payload.find_results_container`, so an
empty child result implies the parent independently derives `keys=[]` too — there is no window
where cards exist but are silently dropped past the gates. A pathological wf that the parent
parses but the child does not would additionally trip `stale_check` (selected-key mismatch →
`stale_artifact` refusal before gates). Not a crash, not a new false-clean; left as-is.

## 3 — Launch-ledger compliance — ✅ COMPLETE

`check_launch_ledger.py --since 2026-07-05` reports `10 entries complete`. Every RUN_LOG
launch heading since 2026-07-05 carrying an `H###` has a matching ledger `handoff`, and no
`window_ledger.jsonl` exists (the only other machine source). Full ledger:

| id | date | classification | residual_status |
|---|---|---|---|
| `SLICE_D_2026-06-30` | 06-30 | concurrency/api | structurally-guarded |
| `PRIL10_W1_2026-07-05` | 07-05 | complexity-estimate-drift | structurally-guarded |
| `NOMINAL_W1_100SMALL_2026-07-06` | 07-06 | concurrency/api | accepted-as-proven-residual |
| `DAH_TAIL_2026-07-06` | 07-06 | structured-output-limit | accepted-as-proven-residual |
| `NO_PWG_W1_FIRST_RUN_2026-07-06` | 07-06 | kill-gate-calibration | fixed |
| `NO_PWG_DIAG_2026-07-06` | 07-06 | kill-gate-calibration | fixed |
| `ARMB_SYNTH_FANOUT_2026-07-06` | 07-06 | operator/process | structurally-guarded |
| `H317_MEDIUM50_3WIDE_KILL_CASCADE_2026-07-08` | 07-08 | concurrency/api | accepted-as-proven-residual |
| `H389_MEDIUM50_SCHEMA_CLASSIFIER_BLOCK_2026-07-09` | 07-09 | structured-output-limit | fixed |
| `H428_OPT2_SCHEMA_SLIM_FIX_2026-07-09` | 07-09 | structured-output-limit | fixed |

- The `2026-07-05 pril10_w1 ⛔ ABORTED` cost blow-up (RUN_LOG heading carries no `H###`
  token, so the checker's heading scan skips it) is nonetheless substantively classified as
  its own `PRIL10_W1_2026-07-05` entry. No gap.
- **`H317_MEDIUM50` is no longer `open-paused`** (the state the handoff flagged for
  confirmation). It was correctly reclassified to `accepted-as-proven-residual`: the later
  H389 diagnosis (09-07) proved the true block is the deterministic agent()-schema-size
  classifier, not the 08-07 transient kill-cascade hypothesis, and the real root cause is
  now `fixed` via `H389_…` + `H428_OPT2_SCHEMA_SLIM_FIX`. Resolved and superseded, not
  silently forgotten.

## Conclusion

P0 #1 and P0 #2 are truthfully "done", not merely fixture-green. The requeue/TM path denies
gate-failed cards **and** fragments and cannot re-serve them (two layers, torn-denylist hole
closed); the gates cannot be made to read a crash, non-zero exit, timeout, or unparseable
child verdict as CLEAN; partials survive into store provenance and are never TM-cached; RU/EN
parity holds on the language-neutral mechanical gate; the launch ledger is complete with every
post-2026-07-05 failure classified. No fix PR is owed.

_Dr. Mārcis Gasūns_
