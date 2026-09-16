# H4527 — the acceptance window cannot be prepared on a sense-bearing card: a census, not a guess

_Created: 17-09-2026 · Last updated: 17-09-2026_

**Session:** Opus 5 (`claude-opus-5`), unattended worker on the Mac over MSI ssh, ~40 min, **0 paid calls**.
**Handoff:** [H4527](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4527-Opus_RussianTranslation_pwg-ru-cohort-live-acceptance-width2_10.09.26.md) — work item 1 (live serial cohort acceptance).

## Why no window ran (live-probed)

`python src/pilot/max_account_orchestrator.py --db src/pilot/max_orchestrator.sqlite probe-ration --account c1`
→ **exit 3** at `2026-09-16T21:51:57Z`:

| field | value |
|---|---|
| `attempts_today` | `2026-09-16T02:46:48Z`, `2026-09-16T08:48:13Z` |
| `legal_now` | `false` |
| `next_legal_utc` | `2026-09-17T00:00:00Z` |
| ledger | `%TEMP%\pwg-probe-ration\9321e2c1….jsonl` |

The 16-09 (3) pass set the floor at 17-09 00:00:00Z and it had **not** passed when this pass ran.
No `ALLOW_*`, no `--skip-canary-gate`, no canary bought (a receipt is valid 6 h; one bought at
21:55Z expires before the gate opens). Zero paid calls.

## So this pass executed the 16-09 (3) ordered step 1 — offline — and it is UNSATISFIABLE as written

That step reads: *«Prepare a fresh window-size-1 acceptance lease on a card with `senses >= 1` via
`no_pwg_scale_plan.py` — zero paid calls».* Two probed facts kill it in its current form.

### 1. The whole `nws00` sub-card class is structurally zero-sense

`sense_count.count_source_senses()` over every portrait sidecar on disk
(`src/pilot/input/*~~h0_zz_*.raw.txt`, 34 distinct keys, `~000d` duplicates excluded), cross-checked
against each key's stamped `portrait.source_senses` — the two agree on every key that carries a
portrait:

| sub-card class | keys on disk | `source_senses >= 1` |
|---|---|---|
| `~~h0_zz_nws00` | 10 | **0 of 10** |
| `~~h0_zz_pw` (incl. `pw00/01/02`) | 17 | 15 of 17 |
| `~~h0_zz_pwkvn` | 3 | 1 of 3 |
| `~~h0_zz_sch` | 4 | 0 of 4 |

So the 16-09 (3) diagnosis — *«the acceptance subject `asa_mskfta~~h0_zz_nws00` is a zero-marker
`no_pwg_supplement_chain` stub, `senses: []`, so `heal_default == 0`»* — was **not a property of that
card**. It is a property of its class: **no `nws00` sub-card anywhere on this box declares a source
sense**, therefore none of them can ever get a repair lane (`agent_budget` derives the heal pool from
sense groups). Re-running the lane on the next `nws00` card reproduces the zero-heal topology exactly.

### 2. Every sense-bearing card the planner can currently reach is a BLOCKED residual

Eligibility = not in the promoted store **and** not `status: blocked` in
`src/pilot/no_pwg_residuals.jsonl`:

- 23 eligible sub-cards on disk; **9 of them carry `senses >= 1`** —
  `darv_i~~h0_zz_pw` (3), `gl_ana~~h0_zz_pw` (2), `hasita~~h0_zz_pw` (2), `jaw_ayus~~h0_zz_pw` (2),
  `kast_ur_i~~h0_zz_pw` (3), `apr_apta~~h0_zz_pwkvn` (1), `d_a~~h0_zz_pw00/01/02` (15 / 9 / 3);
- 14 eligible sub-cards declare **0** senses — every one of them an `nws00`, `sch` or zero-marker
  `pwkvn` stub;
- 10 sub-cards are blocked residuals, and they include **every `pw` sibling of the queue head**:
  `arvant~~h0_zz_pw`, `asa_mskfta~~h0_zz_pw`, `avy_ahata~~h0_zz_pw`, `avyagra~~h0_zz_pw`,
  `b_ahlika~~h0_zz_pw`.

### 3. The planner has no lever that reaches them

`no_pwg_scale_plan.main()` carves windows strictly in queue order and prepares the **first**
non-omitted one; a window is omitted only when *every* unpromoted sub-card of its head is a blocked
residual. The live plan order (`--plan-only`, 122 remaining headwords) is:

`arvant` → `asaMskfta` → `asvatantra` → `avyAhata` → `avyagra` → `bAhlika` → **`darvI`** → `glAna` → …

- `arvant` is omitted (nws00 promoted, pw blocked).
- `asaMskfta` is **not** omitted — its `nws00` is eligible, so the planner prepares the very card the
  16-09 (3) pass parked.
- `asvatantra` has no sidecars yet; `_pilot_gen_merged.py` would mint them, sense count unknown.
- `avyAhata` offers only its zero-sense `nws00` (pw blocked).
- `avyagra`, `bAhlika` are omitted (single pw sub-card, blocked).
- `darvI` is the **first reachable head with a sense-bearing sub-card** — and its window would carry
  *two* sub-cards (`nws00` 0 senses + `pw` 3 senses), i.e. 2 paid card calls, not 1.

No flag targets a sense-bearing card: `--start-index` only labels the window, `--headwords N`
truncates from the front, `--include-residuals` unblocks *all* residuals at once, and the residual
registry is a durable data surface this handoff has deliberately not written to since 11-09.

## The corrected step 1 — three options, one recommendation

1. **Add `--require-senses N` to `no_pwg_scale_plan.py`** (recommended): skip a head whose eligible
   sub-cards all declare `source_senses < N`, selftest-backed, offline, no data-semantics change and
   no residual write. It is the only option that leaves the lane's backlog untouched and makes
   «prepare an acceptance window on a card with a repair lane» a repeatable operation rather than a
   one-off hand-pick. Cost: one small planner change + pins; zero paid calls to build and verify.
2. **Prepare `darvI` as a 2-sub-card window** and raise the bound to `--max-calls 4` (2 cards + the
   readiness probe's two legs). Cheapest in code, but it spends the acceptance attempt on a wider
   window than the acceptance contract describes («window-size 1»), and the zero-sense `nws00`
   sibling rides along with the same no-heal topology that produced the 16-09 null.
3. **Park `asa_mskfta~~h0_zz_nws00` (and the other zero-sense heads) as blocked residuals** so the
   planner walks to `darvI` on its own. This writes the durable residual registry — a lane-backlog
   decision, not an acceptance-window decision, and out of this handoff's scope.

## What is unchanged and untouched

- Lease `h4527acc05` stays **parked** (16-09 (3) withdrawal stands).
- The MSI shared checkout was **not** modified: `git status --porcelain` empty before and after every
  command in this pass. The fast-forward to `origin/master` `8cf834e11` was attempted, refused by a
  live `.git/index.lock` (0 B, written 21:41:10Z) and **not forced** — 8 concurrent `claude` sessions
  were running in that checkout, so the lock is live, not the stale 12-09 one. The delta is one
  FINDINGS commit, no pilot code, so the census reads the same code either way.
- `no_pwg_scale_plan.py` was run **`--plan-only` with `--manifest` pointed at `%TEMP%`**, which
  prepares nothing and never reaches `_pilot_gen_merged.py` — so the tracked
  `progress_dashboard/*.json` rewrite hazard of the 11-09 (3) pass was not triggered.
- No selftests owed and none run: **no code changed this pass**, evidence only.
- Nothing was launched ⇒ no [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)
  entry is owed. A ration refusal is the guard working.

## Ordered next step (earliest 17-09-2026 00:00:00Z, cheapest-first)

1. Land option 1 above (`--require-senses`), offline, zero paid calls.
2. Prepare the window-size-1 acceptance lease it selects; keep `h4527acc05` parked.
3. `probe-ration --account c1` → exit 0 → fresh `dq_canary_puregloss` GO receipt → the corrected
   `--execute --cohort-path` command of the 16-09 (2) packet (it carries `--coordinator`, `--cwd` as a
   bare scratch dir and `--events`), pointed at the new lease.
4. If a card **with** senses also returns `missing-or-mismatched-key`, the class is harness-wide and
   retention (logging the raw `cards[]` on the null path) comes before any further paid call.
5. Work item 2 (Codex sign-off) and the money-class `## Verifier` PASS each still need a different
   session. Work item 3 (width 2) stays parked on the 11-09 one-lane MG ruling.

_Гасунс_
