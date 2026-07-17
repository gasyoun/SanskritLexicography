# PLAN — PWG_RU_UNFREEZE (SanskritLexicography, 2026 H2)

_Created: 17-07-2026 · Last updated: 17-07-2026_

Index doc for the **PWG_RU_UNFREEZE** plan set: unfreezing the `pwg_ru` lane *honestly* — narrowing to a cohort that can clear the quality bar with measurement rather than fatigue, arming the guards that already exist, and refusing to relabel a correctness proof as a production go.

Authored by **Opus 4.8 (`claude-opus-4-8[1m]`)** against `origin/master` at [`64054959`](https://github.com/gasyoun/SanskritLexicography/commit/64054959) (17-07-2026), not against the stale local checkout.

Companion docs:

- [ROADMAP_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md) — waves, sequencing, what stays frozen
- [ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md) — the design against real files
- [IMPLEMENTATION_SanskritLexicography_PWG_RU_UNFREEZE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_RU_UNFREEZE.md) — ordered steps + acceptance
- [VERIFICATION_SanskritLexicography_PWG_RU_UNFREEZE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_RU_UNFREEZE.md) — exact proof commands

---

## 1. Three briefed premises that reality moved — read this first

This plan was commissioned against an audit picture that `origin/master` has since overtaken. Recording the deltas rather than planning against the stale picture:

| Briefed as… | Actually, on `origin/master` today | Consequence for the plan |
|---|---|---|
| Ruling 1: *stamp* `provenance.h_reconstructed` on the 468 synthesised `h` rows | **Already landed** — [PR #517](https://github.com/gasyoun/SanskritLexicography/pull/517) / [`b7b3ebf8`](https://github.com/gasyoun/SanskritLexicography/commit/b7b3ebf8), merged 17-07-2026 12:57, via [`mark_reconstructed_headwords.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mark_reconstructed_headwords.py). Verified in the local store: exactly **468** rows carry `provenance.h_reconstructed`, 462 `iast_reconstructed`, 468 `grammar_defaulted_empty` | The *stamping* deliverable is **done and is not re-planned**. What survives is the **named debt** (§3, D-1) and a **regression guard** so the marker cannot silently vanish the way `h is None` did |
| The SAN-LOSS residual: *"consume `INPUT[k].senses` in the harness `accept()`"* | **Already consumed**, SOFT, since H960 — [`gen_opt_harness2.py:1650-1712`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) calls `count_source_senses` and records `SANLOSS_SHORTFALLS`; `const SANLOSS_HARD_REJECT = false` is the owner-gated arming flag. A sibling `TNMASK_HARD_REJECT` guard exists on the same pattern | The residual is **not** "write the guard" — it is **arming** it, which needs a false-flag rate. Wave 1 measures that rate **offline against frozen evidence** instead of waiting on live traffic |
| Ruling 4: *publish the PD-only subset (18 safely-PD sources; H270 sized it)* | **Not executable as written.** (a) The canonical dataset [`266820-reverse-Gasuns.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/) is **absent from the repo** (the H736 loss-risk finding — `.doc.pdf/` holds 4 `.mdx` files, not the list). (b) H270's 14,471/266,820 (5.4%) is an explicit **lower bound**: 5 of the 7 clear-risk sources (Stchoupak–Nitti–Renou, Turner, Mylius, Kochergina, Pujol) **never appear as a marked source-code at all**, so their unique contribution cannot be subtracted with data on hand | You cannot certify "PD-only" by subtracting what you cannot identify. Wave 1 delivers **dataset recovery + a rights ledger that names the unresolvable residue**; the publish itself stays a human `@DECIDE`. See §3, D-5 |

None of these are re-litigations of the rulings — each ruling is followed. They are the rulings meeting a repo that moved.

---

## 2. Decisions taken

Every ruling verbatim, with its consequence and its cost.

| # | Ruling (human, 17-07-2026) | Consequence in this plan | Trade-off recorded |
|---|---|---|---|
| **R1** | **The 468 synthesised `h` rows: stamp `provenance.h_reconstructed: true` + the derivation method.** PR #510 DERIVED each headword `h` from the row's own key, collapsing homonyms (`vid~~h0` and `vid~~h2` both now read `vid`), while provenance still names the ORIGINAL generator — so they are indistinguishable from model-authored values, and `h is None` fell 468→0 so the defect is unfindable by the query that found it. Stamping restores auditability without discarding work or reopening PR #510's gate. **Carry as a NAMED DEBT in the plan:** 468 derived values remain in the canonical store until a targeted re-translation is folded into a later authorized live run. Do not drop that debt. | **Stamping is DONE** ([PR #517](https://github.com/gasyoun/SanskritLexicography/pull/517), §1). The plan carries the debt as **D-1**: `provenance.h_reconstructed == true` is the re-translation worklist, exported and regression-guarded in Wave 1; the re-translation itself is folded into the first authorized live run, not this wave. | The canonical store knowingly ships **468 derived (not model-authored) headwords collapsing onto 14 distinct heads** — `vid~~h0_*` and `vid~~h2_*` are different homonyms and both read `vid`. Marked ≠ correct. Every downstream consumer of `h` reads a homonym-collapsed value until the re-translation lands. This debt is **not** discharged by this plan. |
| **R2** | **pwg_ru live route: run H1110's bounded c4 ladder as a CORRECTNESS PROOF.** ≤3 paid calls, home route, threshold **UNTOUCHED**. It CANNOT and MUST NOT be reported as a PRODUCTION_GO — measured latency ~40s vs a 30s bar, warm-up ≈ measured, so it is steady-state. Label it **two-profile** (c5/c6 logged out 15-07), never four-profile. The foreign-route provisioning ([GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)) stays the real unblock and stays a human `@DO`. | The ladder is **owned by the already-minted [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md)** — this plan does **not** re-mint or duplicate it (prior-art rule). The roadmap sequences it as W1-L, sole live item, and binds its reporting vocabulary: `CORRECTNESS_PROOF` \| `two-profile` only. | A correctness proof buys **no throughput**. ~40 s/call against a 30 s bar is steady-state (warm-up ≈ measured), and [FINDINGS §80](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) already ruled the breach size-independent route jitter — so "smaller prompts" and "lower the ceiling" are both empirically dead. The lane stays throughput-blocked on a **human** foreign-route provisioning after this proof passes. |
| **R3** | **Quality bar: narrow-and-measure per-cohort clean rates FIRST** (nominal vs root/upasarga vs no_pwg). Executable OFFLINE against frozen evidence in [`pwg_ru/h911/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/), [`h963/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/), [`h1070/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/). It either finds a cohort genuinely clearing 80% (unfreezing scale honestly) or proves the 80% bar unreachable with data rather than fatigue. **No drain until it reports.** H255's no-PWG lane stays frozen meanwhile. | **W1-A, the gate for the whole wave.** Cohorts bind to existing machinery, not new definitions (§ARCHITECTURE): `no_pwg` = store `layer ∈ {pw, sch, nws, pwkvn}` + [`no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py); `root/upasarga` = [`verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py) rootmap expansion; `nominal` = [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py) flat cards. No drain — including H255 — until W1-A reports. | **One cohort is already all but decided against.** The [H911 census](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json) records `no_pwg` per-window audit-clean at **41–69%, median ~62%** — far under 80%. A "prove the bar unreachable" outcome is a live possibility for ≥1 cohort, and the plan must be able to *report* that as a success. Also: per-cohort **economy** stays unmeasurable (tokens/cost are `not_recoverable` from frozen evidence, per the census's own field) — this measures quality only. |
| **R4** | **ReverseDictionary: publish the PD-only subset** (18 safely-PD sources; H270 already sized it 07-07). The ~10 in-copyright sources (Kochergina, Turner, Edgerton, Renou, Mylius, Pujol, Vettam Mani) stay out. Consistent with H734/[PR #481](https://github.com/gasyoun/SanskritLexicography/pull/481) two days prior. | Followed in **intent**, blocked in **mechanism** (§1). **W1-E** delivers: (1) locate + back up the canonical 266,820 list (the H736 loss-risk finding); (2) a **rights ledger** partitioning every source into PD / in-copyright / **unresolvable-by-available-data**; (3) the subset *tooling*. The **publish** stays the existing human `@DECIDE`, now with a sharper question. | The ruling's premise — that the 18 PD sources can be isolated — **does not hold on available data**. 5 of 7 risky sources are unmarked in the source-code column, so a "PD-only" subset built today would be PD-only *by assertion*, not by evidence. Shipping it as certified would be exactly the C-05 hazard R1 exists to punish. The plan therefore **does not publish this wave**, and says so rather than shipping a subset it cannot defend. Related live exposure: [`Reverse-Kochergina.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/) (701 KB, in-copyright source) sits on public `master` — the H734 class. |
| **R5** | **EN lane: RU-first for live capacity, but do the EN lane's OFFLINE scaffolding this wave** — the three named guards from [H1070's `pwg_ru/h1070/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/PWG_EN_FU1_SCALEUP_GO_NO_GO_2026-07-17.md) — so the conditional GO (2.94% wrong-sense) is cashable the instant a profile frees rather than re-adjudicated later. The guards are largely shared already ([LANG_PARITY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md); H920's `sense_count.py` landed lang-neutral). | **W1-D**, offline, zero live calls. Lands all three H1070 guards: (1) German-polyseme checklist into [`gen_fidelity_judge_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_fidelity_judge_en.py) + a rule line in [`tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt); (2) **the hard one** — `{#..#}` count blind to `<F>` footnote content, into the accept path with an [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) HARD flag; (3) DE-RESIDUE gate extended to cross-ref/NWS rows as a soft class. Every fix classified SHARED / INTENTIONAL-DIVERGENCE / GAP in LANG_PARITY. | Scaffolding an EN lane that **has never merged a row** — `promote_en.py` has still never run; the store carries **0 EN rows** against 11,603 RU. Every store-level H971 check is vacuous for EN until Phase 2. This is deliberate pre-investment against a conditional GO, and it competes for the same offline-agent hours as the RU cohort work. If the profile never frees, this wave's EN spend earns nothing. |
| **R6** | **Stale handoff backlog: run a triage pass** (dominant default, not asked). Re-validate the 33 live handoffs against post-#511 `origin/master` via `/handoff-registry-audit`; archive the dead, re-mint the live. Justified by measured waste — two H255 sessions hand-filtered the same failing headwords (~$0.30 each). | **W1-F.** Measured backlog for this repo today: **30 live rows** (22 🟡 queued + 8 🔵 in-work) in [`handoffs/README.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md), the oldest from 02-07. Runs the existing `/handoff-registry-audit` skill — no bespoke tooling. | Triage is **Uprava-side work carried in a SanskritLexicography plan**, and it consumes wave-1 agent hours that produce no lexicographic artifact. Accepted: the measured waste is real and recurring (the H858 incident re-spent ~$0.30 re-failing 4 headwords whose failure was already documented one RUN_LOG entry away). |

---

## 3. Named debts — carried, not discharged

| ID | Debt | Owner of discharge | Do not let this drop |
|---|---|---|---|
| **D-1** | **468 derived headwords in the canonical store.** Marked auditable by [PR #517](https://github.com/gasyoun/SanskritLexicography/pull/517), collapsing onto 14 distinct heads. Marked ≠ correct. | A **targeted re-translation folded into a later authorized live run** — not this wave, not any offline wave. | W1-A exports `provenance.h_reconstructed == true` as the standing re-translation worklist and adds a regression guard asserting the count stays 468 until a re-translation *reduces* it. A silent drop to 0 must fail a test, not a query nobody runs. |
| **D-2** | **`SANLOSS_HARD_REJECT` / `TNMASK_HARD_REJECT` remain `false`.** Both guards are telemetry-only; a whole dropped sense (the `darvī` 2/3 shape) is *counted* and the card is *kept*. | Owner, after a false-flag rate exists. W1-B produces that rate offline. | Until armed, every drain promotes SAN-LOSS cards with a log line and no rejection. |
| **D-3** | **Throughput stays human-blocked.** ~40 s/call vs a 30 s bar, route jitter, size-independent. | [GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) foreign-route provisioning + the c5/c6 logins — both human `@DO`. | No agent-side deliverable in this plan unblocks scale. Saying otherwise would be the exact dishonesty R2 forbids. |
| **D-4** | **Per-cohort economy is unmeasurable** from frozen evidence (tokens/cost `not_recoverable`). | A future instrumented live run. | W1-A must report quality only and say so — never imply a cost verdict. |
| **D-5** | **ReverseDictionary rights residue is unresolvable on available data** (5/7 risky sources unmarked). | Human `@DECIDE`, informed by W1-E's ledger. | A "PD-only" claim built today is assertion, not evidence. |

---

## 4. Autonomy contract

### An executing agent MAY decide alone

- Cohort **partition mechanics** in W1-A — how to bin store rows onto the three cohorts using existing `layer`/worklist machinery, provided the binning is deterministic, committed as code, and its unassignable residue is reported rather than dropped.
- **Exclusion of `h_reconstructed` rows** from any cohort clean-rate read (they would pollute a headword-keyed join), provided the exclusion is stated in the report.
- All **offline code** in W1-B/C/D: guard implementation, selftests, fixtures, Ruff/CI wiring.
- **Refusing to run** any step whose preconditions fail — always the correct autonomous call. Report the refusal.
- **Reporting a cohort as failing the 80% bar.** This is a success outcome, not a reason to widen the sample, re-run, or retry until the number improves. Report the number that came out.
- Archiving/re-minting in W1-F per `/handoff-registry-audit`'s own rules.
- Worktree hygiene, commit granularity, PR authoring.

### An executing agent MUST escalate

- **Arming `SANLOSS_HARD_REJECT` or `TNMASK_HARD_REJECT`.** Owner-gated by construction. W1-B *recommends*; it never flips.
- **Any change to the 30 s latency threshold, the 180 s kill ceiling, or the profile count.** R2 fixes all three. A threshold is not a knob to reach a verdict.
- **Any paid call beyond H1110's ≤3.** The budget is the ruling.
- **Publishing any ReverseDictionary subset**, or removing an in-copyright file from public `master`. Rights + publish are human calls; run `/publish-safety-check`, do not act on its output.
- **Any store mutation** (promotion, re-translation, `promote_en.py`'s first run). This wave is read-only against [`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/) except where a named deliverable says otherwise — and none do.
- **Unfreezing any drain**, including H255's no-PWG lane, before W1-A reports.
- **Reporting H1110's ladder as anything but `CORRECTNESS_PROOF` / `two-profile`.** If the ladder passes and the temptation to write `PRODUCTION_GO` arises, that is the escalation.
- Any conclusion that contradicts a ruling in §2. Follow the ruling, record the contradiction, escalate.

---

## 5. Honest shape of Wave 1

**Wave 1 is offline-heavy and buys no throughput, because the repo is human-blocked on throughput.** Exactly one deliverable makes a paid call (W1-L, ≤3 calls, owned by H1110), and it is a correctness proof by ruling — it cannot unfreeze scale. The real unblock ([GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md), foreign-route provisioning + c5/c6 logins) is a human `@DO` that no step here touches.

What Wave 1 *does* buy is the right to make the next decision on evidence: a per-cohort quality number that either names a drainable cohort or kills the 80% bar with data (W1-A), an offline false-flag rate that lets the owner arm two guards that currently do nothing (W1-B), one real defect fixed (W1-C), an EN lane ready to cash a GO the hour a profile frees (W1-D), a rights position that stops pretending (W1-E), and a backlog that stops re-spending money on solved failures (W1-F).

That is a genuine wave. It is not a scale wave, and this plan does not dress it as one.

---

_Dr. Mārcis Gasūns_
