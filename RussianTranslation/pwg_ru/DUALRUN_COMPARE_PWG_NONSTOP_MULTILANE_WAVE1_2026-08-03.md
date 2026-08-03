# Dual-run compare — PWG→RU nonstop multilane, Wave 1 (H2175 override vs H2246 intended lane)

_Created: 03-08-2026 · Last updated: 03-08-2026_

**What this is.** [H2175](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2175-Opus_RussianTranslation_pwg-nonstop-multilane-wave1_02.08.26.md)
was tier-locked **Opus 5** but executed on an explicit human "run anyway" override by
**Fable 5 (`claude-fable-5`)**. Per the standing
[dual-run-override contract](https://github.com/gasyoun/claude-config/blob/main/references/dual-run-override.md)
that override owes an independent re-run on the intended tier, a written comparison, and
keep-best-of-both. This memo is that comparison, produced by
**Opus 5 (`claude-opus-5[1m]`)** under
[H2246](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2246-Opus_RussianTranslation_h2175-fable-dual-run-compare_03.08.26.md).

**Method, stated honestly.** The override lane's code had already **merged** to `master`
([PR #1057](https://github.com/gasyoun/SanskritLexicography/pull/1057), merge commit
`15d3b211`, 03-08-2026 05:37 UTC) before this pass began, so a from-scratch re-implementation
on a pre-merge base would have been re-derivation theatre against an artifact already in
production. This pass therefore took the handoff's stated alternative: **derive the expected
wave-1 build from the four layer docs first, then line-review every step 1–15 and every one of
the 16 MG rulings against the shipped code**, with independent empirical probes (live store
scan, byte-parity verify, verdict-history trace, import-graph analysis) rather than
diff-reading. Where a claim in the override's own comments could be checked mechanically, it
was checked rather than trusted.

## Four-class verdict over every override artifact

| # | Artifact | Class | Finding |
|---|---|---|---|
| 1 | `nonstop_scheduler.py` tick state machine (step 9) | **conflicting** | Every branch records a tick — *except* a raised runner exception. Fixed here. See C1. |
| 2 | `--auto-promote-until` promote-after-audit ordering (step 5) | **equivalent** | The flagged concern is unfounded — the ordering is correct. See E1. |
| 3 | `data_root.py` env-seam shim (step 4) | **net-new** (gap) | `corpus/` bucket missing from layout. Fixed here. See C2. |
| 4 | `LANG_PARITY.md` bulk re-stamp, 37 entries | **identical** (grounds verified) | The SHARED re-stamp is honest — 0 language-keyed tokens. See E2. |
| 5 | `LANG_PARITY.md` h1209/h1210 entries | **conflicting** | Merge silently reverted SHARED→GAP, asserting a gap the code does not have. Fixed here. See C3. |
| 6 | `lane_guard.py` R4.1 halt + revert (step 7) | **equivalent** | Correct and well-fenced; human rows protected. See E3. |
| 7 | R4.1 automation (spot-check → lane_guard) | **conflicting** | The compensating control has **no trigger**. Not fixed here — needs a ruling. See C4. |
| 8 | `spot_check_daily.store_san_loss_scan` R4.1 trigger | **conflicting** (latent) | Unscoped full-store scan. Not fixed here — narrows a ruled safety gate. See C5. |
| 9 | `data_migrate.py` migration + `--verify` (step 3) | **identical** | Byte parity re-verified independently. See E4. |
| 10 | `coordinator.py` two-store-constant re-resolution | **identical** (claim verified) | Exactly two, confirmed by import-graph. See E5. |
| 11 | `gen_opt_harness2.py` park-and-skip (step 8) | **equivalent** | Iteration-safe, fail-loud default preserved. |
| 12 | `pwg-ru-data` gates.yml (step 13) | **net-new** (risk) | Gate code floats on another repo's `master`. See C6. |
| 13 | `pc_lane_tick.cmd` PC lane (step 10) | **equivalent** | Correctly registered **disabled** behind an honest go-live checklist. |
| 14 | 50 USD/week placeholder ceiling | **equivalent** | Honest placeholder, gated on an MG ruling — not a defect. |
| 15 | CRLF / `skip-worktree` residue | **identical** (resolved) | No residue in the merged state: 0 skip-worktree entries, all modules LF. |
| 16 | Prod lane systemd units, deploy key | **not verified this pass** | Requires live SSH; capped, disabled per fence R4.3c. |
| 17 | [kosha PR #237](https://github.com/gasyoun/kosha/pull/237) registry row | **not verified this pass** | GitHub API rate limit hit. |

## Adjudications — one line per conflict

**C1 — scheduler swallowed its own failures (FIXED, kept: this lane).**
`tick()` had no exception guard, but steps 3–7 spawn subprocesses with timeouts
(`gate_probe` 900 s, `canary_receipt` 1800 s, `bounded_run` 4 h). A `subprocess.TimeoutExpired`
— the *expected* outcome of the very §270 CLI-hang class this module exists to detect —
escaped `tick()` before any `append_tick()`, so the ledger recorded **nothing**. That breaks
the module's own stated invariant ("an unexplained idle tick is a bug by construction") and
silently *inflates* the VERIFICATION acceptance metric, which is computed from that ledger:
crashed ticks vanish from the denominator instead of counting as failures.
**Adjudication:** keep this lane. A timeout is now recorded as
`window_failed / runner_timeout` with the failing step and timeout, any other exception as
`runner_exception`. Pinned by two new selftest cases (8b, 8c).

**C2 — `corpus/` bucket absent from the layout (FIXED, kept: this lane).**
`data_inventory.py` migrates a 592 MB `corpus/` bucket and calls it a "wave-1 layout
addition", but it was never propagated to `data_root.py` (`SUBDIRS`/`REL`) or to the
ARCHITECTURE layout diagram that `data_root.py` cites as its source of truth. A fresh lane's
`--data-root … --ensure-dirs` therefore would not create it and no key resolves it.
**Adjudication:** keep this lane — add `corpus` to both tables and both diagrams. The
alternative (leave consumers hardcoding a path) contradicts the whole point of the shim.

**C3 — two LANG_PARITY verdicts silently reverted (FIXED, kept: pre-merge master).**
The merge reverted `h1209_controller_worker_rig` and `h1210_ab_arm_scaffold` from **SHARED**
back to the pre-H2226 **GAP** text, and deleted the header note recording the previous repair.
Traced mechanically:

| ref | h1209 | h1210 |
|---|---|---|
| `15d3b211^1` (master before the merge) | SHARED | SHARED |
| `15d3b211` (the merge commit) | **GAP** | **GAP** |
| `origin/master` (today) | **GAP** | **GAP** |

This is the **third** recurrence of one class — a stale branch clobbering a freshly-merged
ledger (`#1051`/H2228, then H2209's repair, now this).
**Adjudication:** restore SHARED — and restored on *evidence*, not reflex. The GAP prose
claims "`wf_template.js` still hardcodes the russian target field"; the shipped file's line 23
is `const TARGET_FIELD = PAYLOAD.field || 'russian'` — a default, not a hardcode — and both
h1210 templates are parameterized too. Master was asserting a gap the repository does not
have, so SHARED is the *factually correct* verdict independent of which branch won.
**Gate blind spot worth recording:** `lang_parity_check.py` verifies completeness and hash
drift, never verdict *correctness*. GAP is a valid value, so the ledger stayed green through
all three reverts. Only merge-time diff review catches this class.

**C4 — R4.1 has no trigger (NOT fixed; needs a wiring decision).**
`nonstop_scheduler` only *reads* the freeze file (`lane_guard.frozen`). Nothing anywhere
*runs* `spot_check_daily.py` or `lane_guard.py` — grep finds only `--selftest` in CI, and
`pc_lane_tick.cmd` does not call them. R4.1 mandates a **daily automated** spot-check, and
ARCHITECTURE §3 names the spot-checker plus the halt rule as *the* compensating control that
makes auto-promote safe. **Mitigating fact:** `pc_lane_tick.cmd` does not pass
`--auto-promote-until`, so auto-promote is currently **off** and the lane is registered
disabled — the gap is not live. **Adjudication:** do not paper over it here. This is a
go-live blocker, and the honest fix is a checklist item plus a scheduled daily job; both
belong to the human go-live pass, not to a compare PR. Recorded as the first item below.

**C5 — SAN-LOSS freeze trigger is unscoped (NOT fixed; would narrow a ruled gate).**
`store_san_loss_scan()` scans the **entire** store, so any single legacy SAN-LOSS row — from
any past window, any lane, even a human-approved one — sets `san_loss_in_store: true`
permanently, freezing **every** lane on its first spot-check, forever (unfreezing is a human
act). It also mis-attributes another lane's defect to whichever lane runs the check, while
R4.1 says freeze *that* lane. **Probed empirically rather than asserted:** the live store has
**11,603 rows and 0 SAN-LOSS/UNMAPPED hits**, so this is **latent, not currently firing**.
**Adjudication:** report, do not unilaterally fix. Narrowing a safety trigger that a human
ruling defined is a decision a human should make — scoping it to the day's promoted keys is
the obvious candidate, but it genuinely weakens "ANY SAN-LOSS reaching the store".

**C6 — CI gate code is not pinned (NOT fixed; flagged).**
`pwg-ru-data/.github/workflows/gates.yml` clones `SanskritLexicography` with `--depth 1` at
run time under a step named "pinned to master". Tracking a tip is not a pin: the gate that
decides whether cards may land can change verdict with no change to the PR under test.
**Adjudication:** flag for the Wave-2 pass that actually turns Lane C on; pinning to a commit
SHA is cheap but changes gate semantics, so it belongs with the go-live ruling, not here.

## Equivalences confirmed (no delta owed)

- **E1 — auto-promote ordering is correct.** The handoff flagged "promote-after-audit vs
  in-loop promote" as a suspect. It is sound: `--auto-promote-until` takes the *same*
  no-promote drain path as `--stop-before-promote`, and the promotion decision moves into the
  audit wrapper, so an audit-rejected window is never promoted. Both the in-loop promote and
  the unconditional rescue promote are correctly disabled under the flag; expiry leaves the
  window `AWAITING_REVIEW` and says so; the promotion record binds manifest + audit hashes;
  the two modes are mutually exclusive at the CLI and a past date refuses to start.
- **E2 — the 37-entry SHARED re-stamp is honest.** Verified as the handoff demanded rather
  than accepted: the added lines of `gen_opt_harness2.py` contain **0** language-keyed tokens
  (`lang`/`russian`/`english`/`--lang`/`FIELD[`/`CARD_FIELD`). Park-and-skip keys on missing
  input files and mask round-trip losslessness, neither of which can reach the RU/EN split.
  The verdicts stand.
- **E3 — `lane_guard` revert is well-fenced.** `human_touched()` rows are never removed,
  the store is backed up with the promoter's own fsynced primitive, removed rows are
  quarantined, reverted keys land in a requeue worklist, freezes are per-lane, and dry-run is
  the default. One cosmetic wrinkle: in dry-run the freeze record names a `requeue_worklist`
  path that is not written.
- **E4 — byte parity re-verified independently.** `data_migrate.py --verify` against the
  live clone returns `verify_ok: true`, `bad: []`. *Caveat, stated rather than glossed:* this
  ran against the working clone, not a newly-cloned LFS checkout, so it proves hash parity of
  the migrated set, not fresh-clone LFS materialization.
- **E5 — the "two import-time store constants" claim is exactly right.** Eight modules bind a
  store constant at import via `canonical_store()`; the import-graph shows `coordinator.py`
  reaches exactly `promote_final_cards` and `translation_memory`, which are the two it
  re-resolves. `bounded_staged_run.py` binds none, and drives the coordinator as a subprocess
  with the environment forwarded. No stale-store path exists.

## VERIFICATION acceptance table — provable now vs gated

| Deliverable | Status this pass |
|---|---|
| Data repo migration | **PROVABLE NOW — passes.** `--verify` clean; fresh-clone LFS materialization untested. |
| Auto-promote | **PROVABLE NOW — passes.** Covered by window selftest case (u): parse/CLI gates, clean-audit promote with bound record, expired + tampered refusals. |
| Spot-check + halt | **PARTIALLY PROVABLE.** `lane_guard --selftest` proves 2-sev-3 freeze, 1-sev-3 no-freeze, revert with human-row protection. The *automation* R4.1 requires is absent (C4). |
| Park-and-skip | **PROVABLE NOW — passes.** `parked_queue --selftest`; all-parked window still dies loudly. |
| Scheduler (72h soak, ≥95%) | **GATED on go-live.** Needs live lanes. C1 matters here: before this PR the metric's own denominator was corrupted by unrecorded crashes. |
| Prod-box fence (`systemd-cgtop`) | **GATED on go-live.** Units capped and disabled; not load-tested. |
| Digest/packet (7 daily + 1 weekly) | **GATED on go-live.** Selftests green; no real ledger history yet. |
| CI gates (stub) | **PARTIALLY PROVABLE.** `ci_gate_runner --selftest` green; end-to-end blocked-PR behaviour untested, and C6 stands. |

## Evidence

- All **12** wave-1 module selftests: green (re-run this pass, not inherited).
- `bounded_staged_run_selftest.py` (window selftest): **PASS**, including case (u).
- `lang_parity_check.py`: **91 entries, all verdicts complete, no drift** — before and after
  the C3 restore.
- `data_migrate.py --verify`: `verify_ok: true`, `bad: []`.
- Live store probe: 11,603 rows, 0 SAN-LOSS/UNMAPPED hits.

## What a human still owes (not agent-doable)

1. **Wire R4.1 before enabling auto-promote (C4)** — a daily `spot_check_daily.py` →
   `lane_guard.py` job per lane, and a matching line in the `pc_lane_tick.cmd` go-live
   checklist. Auto-promote must not be switched on before this exists.
2. **Rule on the SAN-LOSS trigger scope (C5)** — keep the literal store-wide reading, or
   scope it to the day's promoted keys.
3. **Rule the weekly cost ceiling** — 50 USD/week is a placeholder awaiting a decision.
4. **Decide whether to pin the CI gate code (C6)** before Lane C goes live.

_Dr. Mārcis Gasūns_
