# Budget hygiene — per-knob verdicts (PWG→RU, H2173 G10)

_Created: 03-08-2026 · Last updated: 03-08-2026_

Closes gap **G10** of the [H2025 pipeline audit](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_AUDIT_PWG_RU_H2025_01-08-2026.md)
(findings **F-B4 / F-B5 / F-B7 / F-B8**). The audit's charge was that nine manifest budgets
are *declared-only* — "each is a limit an operator can set and watch do nothing". This is
the per-knob adjudication it asked for: **every knob gets an explicit verdict, and no knob
is left serialized-but-unread without one.**

Executed by **Opus 5** (`claude-opus-5`), 03-08-2026. Verdicts are derived from the code as
of commit `7785bfa9` (`chore(release): 1.140.0`), not from the audit's prose — where the two
disagree, the code won and the difference is stated.

---

## 1. Verdict scheme

| Verdict | Meaning |
|---|---|
| **ENFORCED** | A live-lane call site reads it and behaviour changes. |
| **READ (offline)** | Read by a real consumer, but not by the paid executor — requeue/preflight planning. Not dead, not a runtime bound. |
| **ADVISORY** | Deliberately not enforceable on the live lane; carried for forensic/JS replay. Documented as such at the emit site. |
| **RETIRE** | No reader anywhere. Kept only as provenance, and now labelled so nobody reads it as a limit. |

The distinction that matters operationally: **ENFORCED knobs change what a paid window
does; nothing else does.** An operator tuning an ADVISORY or RETIRE knob is changing a
record, not a run.

## 2. The nine declared budgets

Sites are [gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)
`meta` (~:1381-1420) and the execution-manifest `budgets` block (~:1509).

| # | Knob | Verdict | Evidence |
|---|---|---|---|
| 1 | `kill_gate.ceil_ms` | **ENFORCED** | Reaches the executor as `budgets.timeout_ceil_ms`; [headless_worker.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py):671-673 clamps every subprocess to `min(operator, timeout_ceil_ms, HARD_TIMEOUT_MS)` (R4/C-15). The one knob H1110 already repaired. |
| 2 | `kill_gate.{factor,base_ms,slope_ms,floor_ms}` | **RETIRE** | Zero readers outside the emitter — including `budgets.timeout_floor_ms`, which is serialized and never read. They describe the **JS** kill-gate curve; the headless lane has no per-card curve, only the ceiling above. Now labelled at the emit site. |
| 3 | `max_wide` | **ADVISORY** | In `budgets`, read by nothing: the serial headless executor dispatches one call at a time. Already documented at :1400-1408 as an intra-process JS hint that *cannot* bound cross-process concurrency — the real cross-process guarantee is `execution_contract.ActiveCallClaim` (R9). |
| 4 | `stagger_ms` | **ADVISORY** | Same call site, same reasoning. |
| 5 | `sense_presplit_budget` | **RETIRE** | Zero readers anywhere in `src/`. |
| 6 | `selfheal_group_budget` | **READ (offline)** | [autosplit_requeue.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py):273, [perf_preflight.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py):369. |
| 7 | `output_budget` | **READ (offline)** | `perf_preflight.py`:368. |
| 8 | `presplit_group_cite_budget` | **READ (offline)** | `autosplit_requeue.py`:270. |
| 9 | `presplit_group_sense_cap` | **READ (offline)** | `autosplit_requeue.py`:271. |
| 10 | `kill_switch` + `max_agents_factor` / `max_agents_headroom` | **ENFORCED, indirectly** | Not read by name. They are *inputs* to `derive_agent_budget(enabled=KILL_SWITCH, …)`, whose output (`max_translate_agents` / `max_heal_agents`) **is** enforced at [headless_worker.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py):728-742 (R3). `kill_switch=false` ⇒ every ceiling `None` ⇒ unbounded. So the switch is real; only its *name* is absent downstream. |

**Correction to the audit.** F-B7 lists all nine as "read by nothing on the live headless
route". Four of them (#6-#9) **are** read — by the requeue and preflight consumers, not by
the executor. That makes them mis-placed rather than dead: they are planning inputs
serialized into a runtime artifact. The audit's *count* of genuinely dead knobs is
**three** (`kill_gate` minus ceil, `timeout_floor_ms`, `sense_presplit_budget`), not nine.

## 3. The inverse defect — read but never written

Auditing the nine surfaced the mirror-image bug, which the audit did not have:

**`budgets.max_agents`** — `headless_worker.py`:693 reads it to set the total cross-pool
ceiling, and the emitter never wrote the key. `max_total_agents` was therefore `None` on
every live window.

**Enforcement impact: none — and the honest reason is arithmetic.** `derive_agent_budget`
returns `max_agents == max_translate + max_heal`, so with both per-lane caps enforced the
sum can only reach the total when both lanes are already refusing. The total is an *implied*
bound, never an independent one. It is now written anyway, so the executor's read resolves
to the plan rather than to `None` (a `None` ceiling reads as "unbounded" to anyone auditing
engine state) and so manifest and `meta.max_agents` agree on one number. **This was not a
missing cap**; the live bound has been the per-lane pair since R3.

## 4. F-B4 · F-B5 · F-B8

| Finding | Verdict | What changed |
|---|---|---|
| **F-B4** — `verdict_for` default + CLI `--policy` default frozen at `production_v1` | **FIXED** | Both now default to `probe_log.CURRENT_POLICY`. The failure was quiet *in the safe direction* — v1's 30 000 ms wall ceiling is the **strictest** of the three, so nothing was wrongly admitted; but live readings were judged against a retired number and stamped `production_v1`, and v3's `api_ceil_ms` guard (v1 carries none) could never fire. `--api-ms` added: it was a `verdict_for` parameter with **no CLI path**, so the route guard was unreachable on the one path that writes receipts. |
| **F-B4** — no boundary test at the live ceiling | **FIXED** | `test_h2173_g10_probe_gate_defaults_and_live_boundary` pins GO at `ceil-1`, NO-GO at `ceil`, plus the independent api-ceiling fail — all **derived from `POLICIES[CURRENT_POLICY]`**, never a literal, so a future bump cannot leave the test asserting a dead number. |
| **F-B5** — `state['translation_limit']` decorative | **FIXED** | [coordinator.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py) `begin_run_leases` standard mode now reads state with the constant as default — the same shape `preparation_limit` already used two frames down, which is what made this an inconsistency rather than a convention. |
| **F-B8** — `--wall-clock-minutes` "a metric labeled Max" | **RENAMED** (H2089 spec #4: *enforce or rename*) | Rename, not enforcement: the value is an **observation**, and there is no defensible ceiling to compare a window's wall-clock against. The ambiguity was that "Max" named the **Max Workflow lane**, not a maximum. Help text now says OBSERVED / recorded-never-a-cap in both the RU and EN twins, and `build_production_metrics`' docstring states that every field there is observational. |

## 5. `classify_run` was inert on the live lane

F-B7's second half — "`classify_run.py`:69 reads `budget_kill_switch_tripped`, a key the
headless summary never writes" — understates the defect. **Three** of the classifier's
inputs are absent from `headless_worker`'s summary:

| Classifier expects | Headless emits |
|---|---|
| `heal_calls` | `heal_agents_spent` |
| `agents_spent` | `translate_agents_spent` + `heal_agents_spent`, separately |
| `budget_kill_switch_tripped` | `budget_stops` |

`heal_calls` is in `TELEMETRY_FIELDS`, so **every headless payload answered
`unclassifiable`** — i.e. the tool was not merely mis-reading one key on the live lane, it
never adjudicated a live window at all. Had that gate been passed, `agents_spent = 0` would
have collapsed the infra-kill threshold to its floor and `tripped` would have read `False`
on a window that really did exhaust its budget.

Fixed by normalising at read time (`normalize_summary`) rather than renaming the emitter's
keys — so every historical JS payload stays classifiable under its original vocabulary,
which is the whole point of the tool. **Explicit JS-lane values always win**; a derived
value never overwrites one that is present.

## 6. What a future session should not re-derive

- **A knob's presence in a manifest says nothing about enforcement.** The manifest is both a
  runtime contract *and* a provenance record, and those two roles are not marked apart in
  the JSON. This table is the mapping; re-check it against `headless_worker` before trusting
  any budget as a bound.
- **Two of the four "fixed" items changed no behaviour** (`max_agents`, F-B8) and that is
  the correct outcome, not a shortfall — an implied bound and an observational metric should
  not be turned into new enforcement just because they looked like limits.
- **The probe ceiling is derived, never restated.** It has been 30 000 → 65 000 → 80 000 in
  four days. Any prose naming a number goes stale; read
  `probe_log.POLICIES[probe_log.CURRENT_POLICY]`.

---

_Dr. Mārcis Gasūns_
