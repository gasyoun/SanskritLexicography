# H2254 — the bounded 300-second ceiling, converged; and why the live proof did not fire

_Created: 07-08-2026 · Last updated: 07-08-2026_

Executed by **Opus 5** (`claude-opus-5`) in an isolated worktree off `origin/master`
`1c68e5068`. **Zero model calls. $0.00 spent.** The three-call / $3.00 reservation this
handoff authorized is **unspent and intact** — see [§4](#4-section-b--the-live-proof-did-not-fire-and-that-is-the-finding).

Handoff: [H2254 (Opus 5) — PWG-RU budget convergence, bounded 300-second policy, and
safe-mode live proof](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2254-Opus_RussianTranslation_budget-runbook-300s-live-proof_03.08.26.md),
final mission of the three-handoff integrity chain.

---

## 1. Predecessors — reused, not rebuilt

Both merged before this ran; verified on `origin/master`, not taken on the packet's word.

| Predecessor | Landed | What H2254 REUSED | What H2254 SUPPLEMENTED |
|---|---|---|---|
| [H2253](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2253-Opus_RussianTranslation_durable-evidence-integrity-controls_03.08.26.md) — durable evidence, marker integrity, benchmark controls | [PR #1175](https://github.com/gasyoun/SanskritLexicography/pull/1175), release 1.144.13 | the durable evidence-root contract and `marker_scan`'s single marker/`{Tn}` scope | nothing — its controls were not re-derived here |
| [H2173](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2173-Opus_SanskritLexicography_pwg-audit-tail-g5-g8-g9-g10_02.08.26.md) — H2025 audit tail G5/G8/G9/G10 | [PR #1083](https://github.com/gasyoun/SanskritLexicography/pull/1083) | the whole per-knob budget adjudication ([BUDGET_HYGIENE_VERDICTS](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/BUDGET_HYGIENE_VERDICTS_PWG_RU_H2173_03-08-2026.md)); F-B4/F-B5/F-B8 and `classify_run` are FIXED and were **not** re-opened | the two G9/G10 residues it did not reach: kill-switch state in the terminal receipt, and one live doc-truth defect (§3) |

**The handoff's audit snapshot was materially stale and reproducing it mattered.** It
described "competing 30/65/180-second values, duplicated policy defaults, decorative
coordinator limits" as open. Measured against the code at `1c68e5068`, most of that had
already been closed by H2173 and #983. Classifying before editing is what kept this from
being a duplicate of work already merged.

| Handoff item | Status at `1c68e5068` | Evidence |
|---|---|---|
| A1 — one authoritative 300 000 ms maximum, layers synchronized | **PARTIAL** | `HARD_TIMEOUT_MS` and `KILL_CEIL_MS` were both 300000 and pinned *equal* by a selftest — but as two copied literals, and the manifest-validation layer had no ceiling check at all |
| A2 — reject a request above the maximum before a subprocess starts | **OPEN** | every route did `min(operator, ceil, HARD)`; nothing refused |
| A3 — probe defaults derived from `probe_log.CURRENT_POLICY` | **FIXED** (H2173 F-B4) | `verdict_for`, the `--policy` CLI default, `coordinator.PROBE_POLICY` and `max_account_orchestrator.PROBE_POLICY` all read `CURRENT_POLICY` |
| A4 — coordinator `translation_limit`, dead budgets, kill-switch in the receipt, wall-clock naming | **PARTIAL** | F-B5 and F-B8 FIXED by H2173; kill-switch state absent from status/receipt; dead budgets *labelled* rather than removed (ruling in §5) |
| A5 — reconcile runbooks / architecture / `AGENTS.md` / skill twins | **PARTIAL** | one live stale instruction and one outright false statement found (§3) |
| A6 — keep `execution.cli_safe_mode` opt-in | **FIXED** (H2189/H2251) | untouched here, deliberately |

---

## 2. Section A — what actually changed

### 2.1 One number, imported rather than copied

`#983` established that the ceiling is enforced in **five** independent places and that
raising one of them is inert. The prior fix pinned two of them equal with a selftest, which
catches drift but leaves two literals free to drift in the first place.

`execution_contract.PRODUCTION_HARD_TIMEOUT_MS` is now the single source, imported by
`headless_worker.HARD_TIMEOUT_MS`, by `gen_opt_harness2.KILL_CEIL_MS` (and therefore by the
`KILL_CEIL_MS` baked into every generated `run_pilot_wf.*.js` and by every manifest's sealed
`budgets.timeout_ceil_ms`). `execution_contract` was chosen because both modules **already**
imported it — no new dependency, no cycle.

The `#983` parity selftest is **kept**, not deleted. Its assertion is now true by
construction; its remaining job is to fail if someone re-introduces a literal.

### 2.2 Above the maximum is REFUSED, not clamped

This is the substantive behavioural change. Before it, a manifest or an operator asking for
7 200 s got 300 s and **no signal at all**: the request was wrong, the run looked normal, and
the discrepancy was recoverable only by reading the effective timeout off a subprocess call
that had already been spawned and paid for. An absolute maximum that silently rounds requests
down is not distinguishable, from the outside, from having no maximum.

`assert_timeout_within_ceiling` now raises on both inputs to the effective bound, at three
layers:

| Layer | Binds on | Why it is not redundant |
|---|---|---|
| `validate_manifest` | `budgets.timeout_ceil_ms` | a manifest is validated by `coordinator` and `max_account_orchestrator` too, and neither constructs an engine — a ceiling enforced only in the engine lets the planning routes accept a manifest they cannot run |
| `HeadlessEngine.__init__` | operator `--timeout` **and** the sealed budget | defence in depth: the guard must not depend on which validation path ran first |
| CLI parser default | — | the default IS the maximum (see 2.3) |

Checked **ahead of** the schema branch on purpose: a v1 manifest is still executable through
`--allow-historical-v1`, and this is a money guard, not a schema nicety.

The `min()` that selects the strictest of the three is unchanged. **Lower ceilings still
bind exactly as before** — that is the point of a maximum rather than a fixed value.

### 2.3 The 7 200-second default is gone from all three routes

It survived only because everything clamped. With a refusal in place a two-hour default
would refuse every ordinary invocation, so the default is now the ceiling itself: asking for
nothing gets the maximum, and asking for more is an error rather than a rounding. Changed in
`headless_worker` (CLI + `execute()`), `max_account_orchestrator` (3 sub-parsers) and
`bounded_staged_run`.

### 2.4 A regression this change would otherwise have introduced

Both supervisor spawn sites passed the **same** number to `headless_worker.py --timeout` and
to their own `run_tree_kill(timeout=...)`. At 7 200 s that was harmless — the outer bound was
24× the inner. Making the default equal the ceiling would have made them **identical**, and
an outer bound equal to the inner one lands the tree-kill during teardown of a call that
legitimately reached its own ceiling: `--status-out` is never written, and a correctly-killed
call becomes a worker that vanished without a status file — the H1 "crash without a status
file" class, re-opened from the outside.

`wrapper_timeout_s()` gives the supervisor 120 s of headroom over the per-call ceiling,
covering worker startup, manifest/preflight validation, prompt assembly and the atomic status
writes — all work that happens **outside** the model call and is therefore not bounded by the
per-call ceiling at all. A selftest greps the orchestrator source to stop the two numbers
being re-unified later.

This is recorded rather than quietly fixed because it is the more interesting half of the
finding: the silent clamp was not only hiding operator error, it was also **supplying the
supervisor's headroom by accident**.

### 2.5 The canary receipt records the run, not just the verdict

`canary_gate judge` wrote a verdict, its reasons and the profile — nothing about the run that
produced it. "How many calls did this cost, what did it cost in dollars, was the kill switch
on, which commit was it" were answerable only by correlating four files by hand, and only
while the operator still remembered which four. That is precisely the disposable-evidence
shape the live-gate contract forbids.

The receipt now carries an additive `evidence` block: commit, manifest SHA-256, calls spent
vs reserved, observed cost **with its `cost_evaluable` flag**, worst wall and route latency,
kill-switch state, effective safe-mode spawn shape, the ceiling that judged it, and the
absolute path of every durable artifact. `verdict` / `reasons` / `facts` / `profile_slot` /
`cli_safe_mode` keep their v1 meaning and position, so `enforce()` and every receipt already
on disk stay valid and the schema token does not move.

Two design points, both load-bearing:

- **An absent input is recorded as `null`, never as `0`.** The 05-08 sitting logged
  `observed_cost_usd: 0` meaning *not evaluable* (a killed call bills; its usage never
  finalized) and the 06-08 sitting logged the same zero meaning *genuinely free*. A receipt
  that cannot tell those apart turns a cost **floor** into a reported total. Pinned by a test.
- **Latency is the worst finalized call, not a mean.** A mean hides exactly the bimodality
  every c4 NO-GO day has shown — a 15–57 s warm-up beside a 300 s measured leg.
- **Kill-switch state records the declaration *and* its observable consequence.**
  `budgets.kill_switch` is only an *input* to `derive_agent_budget`; what actually bounds a
  run is whether the derived per-lane ceilings came out as numbers or as `None`
  (BUDGET_HYGIENE_VERDICTS §2 row 10). Both are written, so a receipt claiming a bounded run
  can be checked rather than believed.

---

## 3. Doc truth — one stale instruction and one false statement

A5 asked for stale 30/65/180-second *live instructions* to go while historical facts stay as
dated history. Most of the surface was already correct (the `/pwg-live-gate` policy section
was refreshed by H2173 G9 and marks its retired numerals as history). Two genuine defects:

1. **`RUN_FREQ_MAX.md` §A1 named a retired ceiling as the live rule** — "strict: measured
   ≥ 30 000 ms ⇒ NO-GO". That is `production_v1`, superseded twice (v2 65 000, v3 80 000 wall
   + 45 000 route). Replaced with the derivation and an explicit note that the numbers in the
   H1447 table below it are dated history.
2. **`/pwg-bounded-run` stated the opposite of the truth about its own flag.** It said
   bounded's `--timeout` "is the whole-**job** timeout (default 7200 s), not the per-call
   ceiling". It is neither: the value is passed **straight down** to `headless_worker.py
   --timeout`, so it *is* the per-call ceiling, one level up. Nothing in the system bounds a
   whole job by wall clock — `--max-calls` and `--cost-ceiling` do that. Corrected in the
   skill, with the H2254 default and refusal stated.

The second one matters more than a typo: an operator reading it would reasonably have set
`--timeout` to some large "job budget" value, which before this change silently clamped and
after it is refused outright.

---

## 4. Section B — the live proof did not fire, and that is the finding

**No model call was made. The three-call / $3.00 reservation is unspent.**

The handoff was written **03-08-2026** and authorized a bounded live sequence against the
lane state as it stood that day: **one** NO-GO day. It also instructed this session to
"reproduce remaining gaps rather than trusting this packet's audit snapshot". Reproducing the
lane state is what stopped the spend.

| Date | Sitting | Measured leg | Classification | Cost |
|---|---|---|---|--:|
| 03-08 | run `#728` | 297 949 ms wall, `duration_api_ms` 276 183, 1 146 B | `process` — **route stall, the call came back** | $0.976 |
| 05-08 | run `#730` | 300 099 ms wall, no `duration_api_ms`, 0 B | `timeout` — **our own kill at the ceiling + 99 ms teardown** | ≥ $0.57 (floor; second call unevaluable) |
| 06-08 | run `#729` | never ran — warm-up refused at 18 574 ms | `rate_limit` — **refused up front, no API call happened** | $0.00 |

Three consecutive NO-GO days. The `/pwg-live-gate` retry policy (MG ruling 02-08-2026,
H2174) is explicit about what that means:

> after **3 consecutive NO-GO days** the lane stops and the *ceiling* goes back to
> [H2138](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2138-Opus_RussianTranslation_probe-ceiling-paired-readings-946_01.08.26.md)
> for re-derivation **rather than to another probe**.

So the lane is **already stopped by its own governing contract**, and a fourth sitting is the
one move that rule names as wrong. H2254's own prohibitions agree from the other direction:
health NO-GO is "an immediate stop; there is no retry or reroll", and the canary is barred
before it starts.

**Ruling: `BLOCKED_ON_LANE_STOP`.** The live authorization was granted against a lane state
that no longer holds. Executing it now would spend real money to re-measure a lane whose
three most recent readings are already on file, whose diagnosis is owned by an open handoff
([H2299](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2299/C4_MEASURED_LEG_KILL_CEILING_HANG_CLASSIFICATION_06-08-2026.md)),
and which the contract has told us to stop probing. A human, not this session, should decide
whether to re-authorize a live sequence — and the diagnosis should land first.

**What the ceiling re-derivation remedy must NOT be applied to, stated because it is easy to
get backwards.** The 3-NO-GO clause routes to H2138 ceiling re-derivation. That remedy was
written for a *distribution* problem — "the median sits just under the ceiling", where a
correctly fitted ceiling can reach a PASS. **None of these three days has that shape:** 05-08
produced **no number to fit** (0 bytes, no route timing; no ceiling value admits a call with
no content in it), and 06-08 returned in 18 574 ms, **4.3× under** the 80 000 ms ceiling, with
the route ceiling never exercised. Re-fitting the ceiling here would be raising a guard to
pass a gate, which stays banned.

**What this does and does not authorize.** Nothing. No bulk translation, no promotion, no
canonical store or TM mutation, no production-default flip, and specifically **no flip of
`execution.cli_safe_mode`** — it stays opt-in exactly as H2189 shipped it. The offline work
in §2 changes what the executor *refuses*; it authorizes no spend whatsoever.

---

## 5. Two things a future session should not re-derive

- **The three dead manifest budgets stay labelled, not removed.** A4 said "remove or
  enforce". H2173 labelled `kill_gate.{factor,base_ms,slope_ms,floor_ms}`,
  `timeout_floor_ms` and `sense_presplit_budget` as RETIRE at the emit site. Removing them
  would change the emitted manifest bytes, and manifests are **both** a runtime contract and
  a provenance record — a historical manifest that no longer round-trips through the current
  emitter loses replay value to buy nothing, since a labelled key with zero readers already
  bounds nothing. Labelling is the resolution; this is the ruling, not an omission.
- **CI was already red at `master` HEAD, for an unrelated ordering bug — fixed here because
  it blocks every merge.** The H2252 truth gate runs `pytest tests -q` over the whole suite;
  two of those tests transitively import `csl_pyutil`, whose install step sat four steps
  *below* it, so collection died with `ModuleNotFoundError` and the job exited 2 before ever
  reaching the install. Reproduced on unmodified `origin/master` (`02ae0fce9`, `e8809dc07`).
  The install moved above the gate — **which exposed a second red the first one was hiding**:
  the pin was `csl-pyutil@v0.7.0` while the suite had grown to need post-0.7 behaviour, so
  `test_nws_ls_markup.py` failed 7 assertions on 0.7.0 and passes 23/23 on 0.9.0 (verified
  locally before bumping). While collection died on `ImportError` those tests never *ran*, so
  the stale pin could not be seen. Pin bumped to `v0.9.0`, still a tag, never `@main`.
  This is out of H2254's stated scope and is flagged rather
  than folded in silently — but a merge cannot be gated on a red that the branch does not
  cause and cannot outlast. The general form is worth keeping: **a whole-suite step must be
  preceded by every dependency the named steps install piecemeal**, and nothing enforces that.
- **`headless_worker_selftest`'s depth-N spawn test is flaky on this box, and it is not
  H2254's.** It fails at "level 2 never started" on unmodified `origin/master` and at
  "level 3 never started" on this branch — a timing-dependent multi-level process spawn, not
  a behavioural difference. Verified by running the identical suite in a second throwaway
  worktree at `origin/master`. Filed separately; it is not a regression from this work.

---

## 6. Gates

| Gate | Result |
|---|---|
| `window_selftest.py` | **210/210** |
| `pytest tests -q` (H2252 full-suite truth gate) | **123 passed** |
| `lang_parity_check.py` | **93 entries, no drift, coverage complete** — 35 entries re-derived, SHARED stands on every one (see below) |
| `execution_contract_selftest.py` | PASS, incl. the new manifest ceiling boundary |
| `bounded_staged_run_selftest.py` | PASS, incl. the new receipt-evidence pins |
| `max_account_orchestrator_selftest.py` | PASS |
| `ci_gate_runner.py --base origin/master` | green |
| `headless_worker_selftest.py` | new H2254 tests PASS; one **pre-existing** flaky depth-N spawn failure, reproduced on unmodified `origin/master` (§5) |

**The parity re-derivation, stated exactly rather than roundly.** Grepping the diff for
`lang` / `russian` / `english` / `german` / `--lang` / `FIELD[` / `CARD_FIELD` / `'ru'` /
`'en'` returns **zero hits in every pipeline file**. It returns 11 hits in one place:
[h2254_parity_restamp.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2254_parity_restamp.py),
the re-stamp driver, whose docstring *names* those tokens and whose `LANG_TOKENS` tuple
lists them — i.e. it matches for documenting the test, the same self-match that already
exempts `lang_parity_check.py` (which carries the detection regexes as string literals).
That file translates nothing, gates nothing and touches no store. Saying "zero in the whole
diff" would have been the convenient phrasing and would have been false.

The substantive argument behind the grep, so it can be attacked rather than taken on trust:
a per-call subprocess ceiling is applied to the CLI child on a path with **no target-language
branch**, and a REFUSED request is refused before any lane is selected at all — so the
ceiling cannot move for one language and not the other. The receipt's new fields are read
from artifacts (call ledger, worker status, manifest budgets) that are themselves
language-neutral.

Boundary evidence, all values derived from the constant rather than written as literals
(FINDINGS §518):

```
H2254 boundary: 299999/300000 accepted, 300001 refused pre-spawn on BOTH inputs
H2254 tree kill: bound 300.0 s reaches the runner; real child killed in 1.0 s on os.name=nt
H2254 manifest ceiling: <=300000 accepted, 300001 refused (v1 and v2)
#983 ceiling parity: HARD_TIMEOUT_MS == KILL_CEIL_MS == 300000 ms
```

The process-tree half is deliberately split: the bound under test is the **production** one
(300 s, asserted as the value reaching `run_tree_kill`), while the real spawn-and-kill runs at
a 1 s scaled deadline. A 300-second selftest would be a five-minute CI leg proving nothing the
scaled one does not — `terminate_tree` branches on `os.name`, never on the magnitude of the
deadline.

---

_Dr. Mārcis Gasūns_
