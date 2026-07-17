# ROADMAP — PWG_RU_UNFREEZE (SanskritLexicography, 2026 H2)

_Created: 17-07-2026 · Last updated: 17-07-2026_

Waves, sequencing, and freezes for the **PWG_RU_UNFREEZE** plan. Index + rulings: [PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md).

---

## 1. The sequencing thesis

The lane is frozen for two independent reasons, and they need opposite treatments:

1. **Throughput** is blocked by route latency (~40 s/call vs a 30 s bar, size-independent jitter per [FINDINGS §80](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). **No agent can fix this.** It waits on a human `@DO` ([GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)).
2. **Quality** is blocked by an unmeasured bar. The 80% clean-rate target was never evaluated per-cohort — the one cohort with a number ([H911 census](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json): `no_pwg` at 41–69%, median ~62%) is failing it. **This an agent can settle, offline, today.**

So Wave 1 spends its hours entirely on (2) and on the guards that make any future drain trustworthy, and makes exactly one bounded live call to prove the pipeline is *correct* while it waits on (1). Ordering quality-before-capacity is not a consolation prize: if W1-A finds no cohort clears 80%, then the foreign-route provisioning — real personal effort from a human — would have bought the right to drain a lane that produces work below its own bar. Measuring first protects that spend.

---

## 2. Wave 1 — measure, guard, tell the truth

All offline except W1-L. Ordered by dependency, not priority.

| ID | Deliverable | Tier | Live? | Gated on |
|---|---|---|---|---|
| **W1-A** | Per-cohort clean-rate report + `h_reconstructed` debt worklist and regression guard | Sonnet 4.6 (`claude-sonnet-4-6`) | no | — **this gates every drain** |
| **W1-B** | Offline false-flag rate for `SANLOSS_*` / `TNMASK_*`, with an arming recommendation | Sonnet 4.6 (`claude-sonnet-4-6`) | no | — |
| **W1-C** | H858 `grammar`-field `{Tn}` stranding fix (`restoreCard`) | Sonnet 4.6 (`claude-sonnet-4-6`) | no | — |
| **W1-D** | H1070's three EN guards, offline | Sonnet 4.6 (`claude-sonnet-4-6`) | no | — |
| **W1-E** | ReverseDictionary dataset recovery + rights ledger | Opus 4.8 (`claude-opus-4-8[1m]`) | no | — (publish stays human `@DECIDE`) |
| **W1-F** | Handoff backlog triage (30 live rows) | Sonnet 4.6 (`claude-sonnet-4-6`) | no | — |
| **W1-L** | Bounded c4 ladder as **CORRECTNESS_PROOF** | Opus 4.8 (`claude-opus-4-8[1m]`) | **yes, ≤3 calls** | owned by [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) — **not re-minted here** |

**W1-L is deliberately not a new handoff.** [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) was minted 17-07-2026 and already owns the post-H1080 audit + bounded c4 restart, with its own atomic claim step. Minting a second handoff for the same ladder is the duplicate-mint this org has a registry check for. This roadmap only **binds its reporting vocabulary** (§4) and its budget (≤3 paid calls, home route, threshold untouched, two-profile).

Wave 1 can run **W1-A … W1-F fully in parallel** — they touch disjoint files. W1-L is independent of all of them.

---

## 3. What stays frozen through Wave 1

| Frozen | Until | Why |
|---|---|---|
| **H255 no-PWG drain** | W1-A reports | Ruling 3, explicit. Its own measured clean rate (median ~62%) is the reason the bar needs re-deciding, not a reason to drain harder. |
| **Every other drain** (nominal, root/upasarga) | W1-A reports | Same gate. "No drain until it reports." |
| **`promote_en.py` / the first EN store merge** | a live judge-tier profile frees | Ruling 5 is scaffolding-only. The store carries **0 EN rows**; W1-D must not change that. |
| **Arming either hard-reject** | owner ruling on W1-B's rate | Owner-gated by construction ([`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) comments say so at both flags). |
| **The 468 re-translation** | a later *authorized live run* | Debt D-1. Offline waves cannot discharge it; pretending otherwise re-creates the C-05 hazard. |
| **Any ReverseDictionary publish** | human `@DECIDE` on W1-E's ledger | The PD-only subset cannot be *certified* on available data. |
| **The 30 s threshold, 180 s kill ceiling, profile count** | — | Ruling 2 fixes them. [FINDINGS §80](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) already ruled "lower the ceiling" empirically dead. |
| **The canonical store** | — | Wave 1 is read-only against it. No deliverable mutates it. |

---

## 4. Reporting vocabulary — binding

W1-L's output may use **only** these labels:

- ✅ `CORRECTNESS_PROOF: PASS` / `FAIL` — the pipeline produced a faithful card end-to-end under ≤3 paid calls.
- ✅ `two-profile` — c1/c4. c5/c6 were `loggedIn:false` as of 15-07; nothing since re-authenticated them.

**Banned, whatever the result:** `PRODUCTION_GO`, `production-ready`, `four-profile`, `scale GO`, or any phrasing implying throughput was earned. Measured latency ~40 s against a 30 s bar with warm-up ≈ measured is **steady-state**, not a warm-up artifact — a passing correctness proof does not move that number, and reporting it as a go would repeat the exact class of error [PR #510](https://github.com/gasyoun/SanskritLexicography/pull/510) is being remediated for: a true statement ("468 rows repaired", "the ladder passed") standing in for a claim it does not support.

---

## 5. Wave 2 — conditional, nothing pre-authorized

Each Wave-2 branch is named with its trigger. **None is authorized by this plan**; each needs its own handoff once its trigger fires.

| Trigger | Then | Blocked by |
|---|---|---|
| W1-A names a cohort **≥80% clean** | Bounded drain of *that cohort only*, at the smallest window that can refute the number | Live capacity — still D-3. A drainable cohort with no route is still not drainable. |
| W1-A finds **no cohort ≥80%** | **Re-decide the bar itself** with a `/decision-record`: is 80% right for a lane whose best cohort is ~62%? Options: lower the bar with a stated human-review budget, narrow further (sub-cohorts), or accept the lane as human-gated | Human `@DECIDE`. This is a legitimate, planned-for outcome — not a failure. |
| W1-B's false-flag rate is **low** | Owner arms `SANLOSS_HARD_REJECT`, then `TNMASK_HARD_REJECT`; every drain thereafter rejects+requeues SAN-LOSS | Human ruling. |
| W1-B's rate is **high** | Fix the counter (the H960 cross-reference hardening precedent), re-measure. Do **not** arm | — |
| **Human** completes [GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) foreign-route provisioning | [H909](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H909-Opus_SanskritLexicography_h818-foreign-route-paired-probe-analysis_14.07.26.md) resumes on the paired A-B-B-A JSONL; a route PASS then feeds the one-account canary→10→20 ladder | Human `@DO`. Note GTD:579's own re-scoping: packet finding **C-15** says the 180 s kill ceiling is **route-independent**, so a route fix alone may not unblock the drain. W1-A is one of the two free measurements GTD:579 asks to run *before* spending that effort — this plan delivers it. |
| **Human** authenticates c5/c6 | Ladder rungs 3–6 become discussable — **and only then** is "four-profile" a word this repo may write | Human `@DO`. Latency remains an independent gate; the logins alone do not pass the ladder. |
| A live judge-tier profile frees | FU1 Phase 2: `promote_en` → `annotate_dcs_freq` → judge → human gold, with W1-D's guards already in place | Live capacity. W1-D exists precisely so this is a run, not a re-adjudication. |
| Human `@DECIDE` on W1-E's ledger | Publish / restrict / seek per-source lists for the 5 unresolvable sources | Human `@DECIDE`. |

---

## 6. Explicitly out of scope

- **Anything that touches the latency number by any means other than measuring it.** Ruled empirically dead ([FINDINGS §80](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)): payload size does not drive it (R²=0.02; a 93 B call hit 52.8 s).
- **Re-deriving cohort definitions.** [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py), [`verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py), [`no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py) and the store's own `layer` field already define them. Consume them.
- **Re-writing the SAN-LOSS guard.** It exists ([`sense_count.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py) + `accept()`), it is cross-reference-hardened, it is selftested by [`accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js). Only the arming decision is open.
- **A new review sheet, dashboard, or registry.** None of the six deliverables needs one.
- **Re-opening [PR #510](https://github.com/gasyoun/SanskritLexicography/pull/510)'s gate.** Ruling 1 settled it: stamp, don't revert.

---

_Dr. Mārcis Gasūns_
