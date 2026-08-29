# H3663 Lane A — the 16 never-attempted keys, run on c1 in chunks after a killed window

_Created: 29-08-2026 · Last updated: 29-08-2026_

Executor: Opus 5 (`claude-opus-5`), generation model `claude-sonnet-5`. Handoff:
[H3663](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3663-Opus_SanskritLexicography_h3658-residual-lane-a-16key-c1-window_29.08.26.md),
the unrun Lane A of
[H3658](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3658-Opus_SanskritLexicography_h3654-residual-16keys-and-3-defects_28.08.26.md).

**Store 11 482 → 11 515.** 7 audited-clean cards promoted, 33 sense rows; 9 keys withheld.
All 16 keys were translated; the audit, not the run, is what held 9 of them back.

## 1. The unsolved step had a purpose-built tool

H3663's own mission said scoping a run to exactly these 16 keys was unsolved, because
`coordinator.py claim --keys` is restricted to `--kind defect-repair`. That framing was wrong.
The 16 are the **transient** (never-ran, null) bucket of the H3627/H3654 window, and there is a
dedicated tool for exactly that:

```
python src/pilot/requeue_from_audit.py h3627-reingest --transient --nominal \
    --window-tag=h3654 --requeue-file=src/pilot/output/h3654/requeue.transient.keys.txt ...
```

Its docstring calls `--transient` "only null cards (cheap re-run)" and deliberately keeps
`--tm=auto` **because nothing was ever cached for them** — precisely this lane's situation.
`coordinator.py prepare-requeue --transient` is the wrapper that shells out to it, but there were
**0 coordinator leases** (H3627 drove `headless_worker.py` off a hand-built manifest), so the
underlying script was called directly. `root` is `h3627-reingest`, `nominal: true`, both read off
the sealed manifest's `meta`.

Manifests were rebuilt with `--budget=1` (byte mode) so every card is its own batch — the shape
H3627 chose so one unevaluable call cannot destroy cost attribution for a whole batch.

## 2. A killed window lost 6 paid translations — and the salvage path does not cover it

The first attempt ran all 16 keys as one background window. It was **killed at 15 minutes**,
having spent **7 calls with 6 finalized**, and `out.h3663.json` was **never written**.

The timing is the diagnosis: the task started 11:17 and died 11:32, exactly when this session's
turn ended after a Stop-hook cycle. **Background tasks did not survive turn end.**

That exposes a real gap. 1.144.114's salvage — the fix H3654 proved live, which publishes
`window_aborted.cards_salvaged` with `partial_output: true` — covers the worker's **own** abort.
It cannot cover an **external kill**: the worker holds results in memory and writes `--output`
only on clean completion or on its own salvage path, and a SIGKILL gives it neither. So this
reproduced the H3627 all-or-nothing loss shape that the salvage was supposed to have closed,
by a route the salvage never claimed to cover.

Containment was clean: no orphaned worker processes, store untouched at 11 482, no partial write.

**Mitigation adopted:** run the scope in short chunks, each writing its own `out.<tag>.json`, and
keep the session turn alive by polling. A kill then costs at most one chunk. Five chunks were used,
with `_sr_avaka` — the key that killed H3627 — deliberately **isolated alone** so its known failure
mode could not take any other card down with it.

## 3. The run: 5 chunks, 16/16 keys returned, `null_keys: []` everywhere

| chunk | keys | calls | notes |
|---|---|---:|---|
| c1a | `ar_sas` `h_uti` `jar_ayu` `k_anana` | 6 | 2 retries |
| c1b | `kzu_d_a` `majj_a` `men_a` `r_ama_wa` | 5 | 1 retry |
| c1c | `satt_a` `_s_ulin` `ut_ta` `ut_t_apana` | 8 | `ut_t_apana`: retry + 2 fragment-heal rounds, hit `max_calls` exactly |
| c1d | `v_as_a` `v_iqu` `y_atu` | 7 | `v_iqu` needed heals |
| c1e | `_sr_avaka` | **1** | first attempt, no retry, no heal |

**`_sr_avaka` is no longer a killer.** It ended H3627 on `structured_output_retry_exhausted` and
H3654 never reached it (index 19, the window died at b6). Here it translated **cleanly on the first
attempt in 134.6 s** and audited clean. The schema-park half of 1.144.114 was never even exercised —
the call simply succeeded.

## 4. The audit verdict is NOT the unit gate — 7 clean, not 15

`audit_window.py` prints two different things and they disagreed here:

* the **markup-fidelity unit gate** (`PASS: 4/4 units clean`) — ls/san/ru columns only;
* the audit's own **`requeue.defect.keys.txt`** — the promotable verdict, which is what
  `promote_final_cards.py` guards on.

Reading the first as the verdict gave a false "15 of 16 clean". The authoritative split:

| verdict | count | keys |
|---|---:|---|
| **clean → promoted** | **7** | `ar_sas` `h_uti` `k_anana` `kzu_d_a` `majj_a` `men_a` `satt_a` |
| defect | 8 | `jar_ayu` `r_ama_wa` `_s_ulin` `ut_ta` `v_as_a` `v_iqu` `y_atu` `_sr_avaka` |
| transient | 1 | `ut_t_apana` |

No defect carried a **high-confidence** risk (`high-confidence risks: 0` in every chunk report).
The dominant risk classes are `markup_wrapper_dropped`, `gloss_wrapper_became_guillemet` and
`suspicious_lexicographic_with_text_signal` — **the same classes H3658 Lane B cleared
deterministically** on `_atura` with `fix_d3` + `apply_no_yo`. Those repairs are already ruled
(PR #789's exact count-match rule), operate on already-paid output, and cost nothing to apply. That
is the obvious next move and is left as the residual rather than done here unaudited.

## 5. Promotion

The defect guard is all-or-nothing and `--force` bypasses it for **every** key, so the input was
narrowed instead: whole clean chunks copied verbatim, the mixed chunk rewritten without its flagged
key, and a **union** block list built from all five chunks' defect + transient files. The guard then
reported `no intersection with incoming keys` on its own.

```
python src/promote_final_cards.py --merge \
    --glob 'src/pilot/output/h3663/promote/out.*.json' \
    --defect-keys src/pilot/output/h3663/requeue.blocked.keys.txt \
    --gen-model-version claude-sonnet-5 --promotion-id h3663-lane-a
```

`--override-reviewed` was deliberately **not** passed, so human-touched rows stay protected.

> **Trap worth pinning: `--merge` is not dry-run by default.** `--apply` gates only
> `--ready-partial-report`; a plain `--merge` invocation **writes the store**. H3654's recipe
> carried `--apply`, so the asymmetry never surfaced there. This run intended a dry run and got a
> real promotion — correct in content (the same 7 cards, guard clean, automatic backup taken) but
> one step earlier than intended. Read the flag's help, not its name.

## 6. Gates after the write

| gate | result |
|---|---|
| `refresh_tm_mirror.py` G1 human-touched | PASS |
| `refresh_tm_mirror.py` G2 content-loss | PASS |
| `refresh_tm_mirror.py` G3 shrink | PASS |
| mirror refreshed | sha `5ed8a96c0d62` → `ed8265065ddf` |
| `audit_store_gates.py` | rows **11 515**, `only_src=0 only_mirror=0 changed_ru=0`, exit 0 |
| `placement_axis_check.py` | **OK** (6 320 sidecar rows, 633 placed), exit 0 |

The mirror backup is stamped `h3663` — `refresh_tm_mirror.py --handoff` is now required rather
than defaulted to `H3627` (shipped in H3658), so this refresh is the first one to carry its own
provenance. The 3 `SAN-LOSS` rows (`mA`, `pat`, `asvatantra`) are pre-existing and none of them is
a promoted key.

## 7. Spend

**35 calls, cost NOT evaluable.** Every run reports `billing_mode: unknown_gateway` with
`observed_cash_usd: null`; per FINDINGS §597 that is never reported as `$0`.

| run | calls |
|---|---:|
| health probe (GATE-0) | 2 |
| canary `dq_canary_puregloss` | 1 |
| **killed 16-key window (lost)** | **7** |
| c1a / c1b / c1c / c1d / c1e | 6 / 5 / 8 / 7 / 1 |

Tokens across the ledgers: 403 331 output · 976 569 cache-creation · 2 658 928 cache-read ·
4 038 964 subagent. The preflight's estimate was $0.92 for the 16-key scope
(`cost_gate.over_ceiling: false`, $0.06/card); the 7 discarded calls are re-payment that estimate
did not include.

## 8. Gate provenance

Fresh c1 gate, both halves green, fired because no live receipt existed:

* **GATE-0 health PASS** — measured 22 318 ms against an 80 000 ms ceiling, warm-up 26 073 ms.
* **CANARY GO** — one paid call, 12.1 s, `null_keys: []`, judged by `canary_gate.py judge`.

The durable probe log held **0 entries for 29-08** and its last c1 GO was 17.9 h old. H3659 had
fired a gate earlier the same day, but its receipt was worktree-local and died with the worktree —
so an earlier reading of "1 of 2 attempts used" was wrong, and this probe is the day's first
*logged* one. A receipt that does not survive its worktree cannot serve as the ration record.

## 9. Residual

1. **8 defects + 1 transient are unpromoted.** The deterministic repairs from H3658 Lane B
   (`fix_d3`, `apply_no_yo`) target the dominant risk classes and cost nothing to apply to output
   already paid for — try those before re-translating anything.
2. `ut_t_apana` is *transient*, not a content defect: it needed a retry plus two fragment-heal
   rounds and still landed in the null bucket.
3. Promoted rows are `ai_translated`, so they stay out of the citable edition until G5 human review.

_Dr. Mārcis Gasūns_
