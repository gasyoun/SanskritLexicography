# H3677 — gate 3 is closed: the planner now stamps a production-eligible v2 manifest; the window awaits authorization

_Created: 29-08-2026 · Last updated: 29-08-2026_

Three gates stand in front of a paid `no_pwg` window on c1. This pass **closed the only one an
agent may close** and left the other two exactly where they belong. No calls were made, nothing
was promoted, the store was not written.

## Verdict

| # | Gate | Owner | State after this pass |
|---|---|---|---|
| 1 | Human billing authorization for **this** window | human | **OPEN** — the 29-08 authorization was given for the H3659 window and was consumed by it |
| 2 | Fail-closed cost guard ([§602](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)) | human | **OPEN** — `--allow-unbounded` is the disclosed escape and is a human's call, never the agent's (H2851) |
| 3 | Manifest schema v2 ([§604](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) gate 3) | **agent** | **CLOSED** — fixed in the planner, verified end-to-end |

## What was wrong, and why it stayed wrong

[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
computes `bound = bool(profile_slot or config_dir)` and emits `SCHEMA_V2 if bound else …v1`.
[`coordinator.prepare`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py)
appends five flags that make `bound` true;
[`no_pwg_scale_plan.prepare_window`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py)
appended none. **Every window the planner ever prepared was therefore born unrunnable**, and
H3659 had to rebuild its manifest by hand before it could spend.

The failure is silent in the worst place: preparation prints `… | execution manifest
pwg.headless_execution_manifest.v1` and **exits 0** — lease registered, cost gate passed, harness
written, artifact apparently complete. The refusal lands at `bounded_staged_run`, which is
*after* a human has already cleared billing and the cost guard. The cheapest gate was discovered
last, every time.

## The fix

- `binding_args()` builds the coordinator's exact five-flag list and `prepare_window` forwards it.
- `coordinator.register_prepared_lease` records `profile_slot` / `config_dir` / `executor_lane`,
  so a planner lease carries the same production-eligibility facts `prepare` already recorded.
- `--profile-slot` and `--config-dir` are refused unless supplied together — the coordinator's own
  rule, not a new one.

**Verified end-to-end rather than asserted.** The patched planner emits

```
execution manifest pwg.headless_execution_manifest.v2
  profile_slot            c1
  config_dir_fingerprint  9321e2c138f02c1d19ec9c249ad096841813c82414b76d6caf3e3f3b518acd6b
  execution_route         claude-cli-headless
  executor_lane           serial-whole-card
  validation_method       audit_window+final_schema
```

— **byte-identical to the binding H3659 hand-built** for `no_pwg_w09`, and it selects exactly the
five sub-cards this handoff names: `darv_i`, `gl_ana`, `hasita`, `jaw_ayus`, `kast_ur_i`
(all `~~h0_zz_pw`, field `russian`).

`windows100_selftest._test_planner_binding` pins the flag list against `coordinator.py`'s
**source** rather than a copied literal, so the two paths cannot drift apart again.

## The window is worth running — `target_anchor` is genuinely reachable

[§604](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)'s hard lesson is
that a repair whose counter reads `0` both when there was nothing to repair *and* when it never
ran is unfalsifiable. Before treating a paid window as worth authorizing, the repair's
reachability was checked on the code that will actually execute — **both lanes**, by reading the
guard, not by trusting H3675's offline replay:

- Python — [`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py):
  `target_anchor.reanchor(masked, field)` sits **inside** the `count_card_field` branch, which is
  the branch that produced `hasita`'s `translation-fidelity-reject`.
- JS — the generated harness: `TARGET_ANCHOR_INVOCATIONS++` fires **before** `taReanchor`, inside
  the same `lsT/skT` guard.

Because the counter increments before the attempt, `invocations 0` (never reached) is now
distinguishable from `invocations 1, repairs 0` (reached and refused). That is the third state
§604 demanded, and it is what makes the spend measurable rather than a coin flip.

## The exact recipe, once a human clears gates 1 and 2

Run from a checkout of `master`, with `PWG_EVIDENCE_DIR` pointing **outside every checkout**
(§603), and `--start-index` / `--db` explicit because both resolve gitignored or untracked
on-disk state a worktree cannot see:

```
set PWG_EVIDENCE_DIR=D:\ClaudeTools\profiles\claude1\.pwg_ru_evidence\c1\h3677
python src/pilot/no_pwg_scale_plan.py --window-size 12 --limit-windows 1 --start-index 10 ^
    --headless --profile-slot c1 --config-dir D:\ClaudeTools\profiles\claude1\.claude
```

`--start-index 10` is **not optional**: the main tree has used `1, 02–05, 08, 09`, and the auto
index globs the gitignored `output/`, so any tree lacking that history silently proposes an
already-completed window.

**Budget floor.** `--max-calls` must be **≥ ~2.5 × card count** — 5 cards ⇒ **≥ 13**. H3659 set
`8` for the same five and `jaw_ayus` / `kast_ur_i` were never attempted
(`translate_agents_spent 5 + heal_agents_spent 3 = 8`).

**Success criterion.** `target_anchor_repairs > 0` on a real window, with the repaired cards
audited before any store write.

## Two things a human should know before authorizing

1. **Run all five — `darv_i` and `gl_ana` are NOT recoverable work.** They carry paid,
   unpromoted cards from H3659 in `out.w09.json`, and a three-key window (`hasita`, `jaw_ayus`,
   `kast_ur_i`) looks like the cheaper buy. It is not:
   [§612](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) established
   the same day that those two cards are **permanently unpromotable** — the input sidecars
   `audit_window` hashes died with the H3659 worktree and exist in none of the three places they
   could have survived, and every workaround is closed on principle. Re-running them inside this
   window is the only way they ever reach the store, and it regenerates the sidecars that make
   them promotable. Budget the full `--max-calls 13`.
2. **The Plan-Mode refusal class fired on `gl_ana` in the last window.** The standing rule is that
   a second refusal-class event on the same profile is a STOP and a diagnosis task, never a third
   attempt — so the window may legitimately end early rather than complete.

## Evidence

- Code: `src/pilot/no_pwg_scale_plan.py`, `src/pilot/coordinator.py`,
  `src/pilot/windows100_selftest.py`.
- `window_selftest.py` **218/218**, `windows100_selftest` / `h809_selftest` /
  `bounded_staged_run_selftest` / `coordinator_hardening_selftest` /
  `execution_contract_selftest` / `headless_worker_selftest` all PASS.
- `lang_parity_check.py`: 104 entries, no drift. Four entries re-stamped after re-deriving
  SHARED; all 93 added lines grepped for a language-keyed token with **zero** hits.
- Dry-run manifest (gitignored, reproducible):
  `output/headless_dryrun/no_pwg_w10/execution_manifest.no_pwg_w10.json`.
- **Zero paid calls this pass. Nothing promoted. No store write.**

_Dr. Mārcis Gasūns_
