# H4527 — offline diagnosis of the 16-09 null card: `budget_stops` is not truncation, and the subject card has no repair lane by construction

_Created: 16-09-2026 · Last updated: 16-09-2026_

**Pass:** Opus 5 (`claude-opus-5`), unattended worker on MSI, **0 paid calls**. Nothing was
launched; `c1`'s 16-09 UTC ration is spent and the probe that says so costs nothing.

## Why this pass did not run the window (live-probed, not assumed)

```text
python src/pilot/max_account_orchestrator.py --db src/pilot/max_orchestrator.sqlite probe-ration --account c1
→ exit 3 · attempts_today ["2026-09-16T02:46:48Z", "2026-09-16T08:48:13Z"]
         · legal_now false · next_legal_utc "2026-09-17T00:00:00Z"   (read at 20:00:36Z)
```

Two attempts, `max_per_utc_day: 2`. Work item 1 (the live acceptance window) and work item 3
(width 2, parked on the one-lane condition anyway) are both unrunnable until **17-09-2026
00:00:00Z**. No `ALLOW_*` was set, no `--skip-canary-gate` reached for.

So this pass spent its time on the one thing the previous pass's own step 5 asked for before a
third paid call: the offline diagnosis of the null, against the retained artifacts of run
`h4527acc160916`.

## What the earlier pass hypothesised, and why it is wrong

[LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
entry `H4527_COHORT_WINDOW_NULL_CARD_2026-09-16` named «an output-budget truncation the first
hypothesis to test offline», reading `budget_stops: 1` as a truncation signal. It is not one.

`budget_stops` is incremented in exactly two places in
[headless_worker.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py)
— `HeadlessEngine.call()` when `_budget_ok()` refuses a spawn, and when the call-reservation
ledger raises `CallLimitReached`. Both are **refusals to spawn another agent**; neither has
anything to do with the token budget of a call that already ran. The refused spawn was a
**heal** spawn: the window's own summary carries `heal_agents_spent: 0` against
`max_heal_agents: 0`, so `_budget_ok(heal=True)` was false on the first ask.

## Root cause: a zero-sense card gets a heal pool of exactly zero

The heal pool is planned up front, per card, from **sense groups** —
[agent_budget.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/agent_budget.py):

```python
groups = {k: v for k, v in raw_groups.items() if v > 0}
...
heal_default = sum(_per_card_heal_cap(n, per_card_heal_factor, per_card_heal_headroom)
                   for n in groups.values())
```

The acceptance window's only subject is `asa_mskfta~~h0_zz_nws00`, and its manifest input is a
zero-marker cross-reference stub:

| field (execution manifest) | value |
|---|---|
| `portrait_kind` / `source_profile` | `no_pwg_supplement_chain` |
| `key1` (portrait) | `asaMskfta` |
| `senses` / `source_senses` | `[]` / `0` |
| `ls` / `sk` / `nws` | `0` / `0` / `1` |

Zero sense groups ⇒ `groups == {}` ⇒ `heal_default == 0` ⇒ `max_heal_agents: 0`
(`heal_budget_groups: 0`, `heal_budget_cards: 0` in the run's own `meta`, confirming it).

**Consequence, stated as the falsifiable claim it is:** for this card the single translate call
is the only shot there will ever be. When its echoed key failed to bind, the engine wanted a
per-card self-heal, was refused by a pool that is structurally zero, stamped `budget_stops: 1`
and settled the key null. A re-run of the same lease reproduces the same topology exactly — the
retry lane is not missing because of transport, it is missing because the card has no senses to
budget a repair against.

## The key-echo recovery path was present and correct — so the mismatch is upstream of it

`normalize_batch` in `headless_worker.py` has the H220 nominal tolerance: it re-keys a card the
model echoed under the clean SLP1 headword, gated on the reverse map being unambiguous. Both
gates were satisfiable here:

- `manifest['meta']['nominal_keymap']` is `{"asa_mskfta~~h0_zz_nws00": "asaMskfta"}` — the right
  direction (stem → clean SLP1), one entry, so `reverse == {"asaMskfta": [stem]}`, length 1.
- Therefore a card echoed as `asaMskfta` **would** have been recovered and re-keyed.

The card was not recovered, so the model echoed neither `asa_mskfta~~h0_zz_nws00` nor
`asaMskfta`. *What* it echoed is not knowable from disk: the parsed structured response is
discarded once `normalize_batch` has run, and only the normalised rows survive into
`wf_output.h4527acc05.json`. The `~005f`-escaped form quoted in the ledger entry
(`asa~005fmskfta~007e~007eh0~005fzz~005fnws00`) is a red herring — it is the key-escaping of the
**output** `meta` block, not what the prompt or the matcher used.

**Retention gap, recorded as such:** a `missing-or-mismatched-key` null is the one failure class
whose evidence the pipeline throws away. Nothing in the retained artifacts (`wf_output`,
`submitted_result`, `workflow_result`, `.attempt1.runner.json`, `.attempt1.status.json`,
`window_status.json`, `audit_window.report.json`) contains the returned `cards[]`. Any future
diagnosis of this class needs the raw response retained on the null path.

## The audit already said it, in its own vocabulary

The window's audit report — **local-only**, the whole `src/pilot/output/` tree is gitignored:
`file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/src/pilot/output/coordinator/artifacts/h4527acc05/audit_window.report.md`
(retained, not re-run) — files exactly one semantic risk for the key, score 100:
**`missing_senses`**. Gates `nws`, `translation`, `stage2_mechanical` and `coverage` each exit 1.
The window did not fail on transport; it failed on a card that carries nothing to translate.

## The subject card was a poor acceptance subject before it was ever dispatched

The acceptance plan — **local-only**, same gitignored tree:
`file:///C:/Users/user/Documents/GitHub/SanskritLexicography/RussianTranslation/src/pilot/output/h4527acc/plan.v2.json`
— records, in the same window object that selects `asa_mskfta~~h0_zz_nws00`:

```json
"residual_skipped": [{"key": "asa_mskfta~~h0_zz_pw",
                      "reason": "second consecutive selfheal-nothing-resolved on presplit card",
                      "source_window": "no_pwg_w06_rq1"}]
```

The window's headword `asaMskfta` is one whose `pw` sub-card is **already a twice-failed
residual**; what remained selectable of it was the zero-sense `nws00` layer. The handoff's own
«On our data» line asks for *a real small verb root from `verb_worklist.py --top`* — this card is
neither a verb root nor a card with sense content.

## What this changes for the next paid attempt (17-09-2026 00:00Z onwards)

The previous pass's ordered step 2 — «resume lease `h4527acc05`: it settled `transient_only`, so
its key is in the requeue backlog — a cheap re-run, not a rework» — is the one instruction this
diagnosis contradicts. On the evidence above it is **not cheap**: it spends one of two daily
attempts on a card that cannot self-heal, to re-test a bind that failed once already, and a
second null buys nothing but a second null.

Recommended ordering for the next pass, cheapest-first, all steps offline until the last:

1. **Prepare a second acceptance window on a card with at least one sense** (window size 1,
   zero paid calls — preparation builds the harness and manifest, it does not call the model),
   using [no_pwg_scale_plan.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py).
   A card with `senses >= 1` gives `max_heal_agents > 0`, i.e. an actual repair lane, and gives
   the acceptance record something an accepted-set comparison can be made against.
2. Keep lease `h4527acc05` **parked**, not resumed. It is not a defect requeue
   (`requeue.defect.keys.txt` is empty) but it is not a productive transient either.
3. Only then the ration probe → canary GO → the corrected `--execute --cohort-path` command of the
   16-09 (2) packet, pointed at the new lease.
4. If the *new* card also comes back `missing-or-mismatched-key`, the class is harness-wide and the
   next step is retention (log the raw `cards[]` on the null path) before any further paid call —
   not another window.

**Unchanged and deliberately so:** `COHORT_LIVE_ACCEPTANCE.json` stays unwritten, the width>1 gate
stays fail-closed, no code was touched this pass, and no `LAUNCH_FUCKUPS.md` entry is owed for a
pass that launched nothing. The existing entry's `root_cause` / `guardrail` / `residual_risk`
fields are updated in place with this diagnosis, which is what that ledger is for.

_Гасунс_
