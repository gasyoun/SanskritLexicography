# IMPLEMENTATION — PWG_RU_UNFREEZE (SanskritLexicography)

_Created: 17-07-2026 · Last updated: 17-07-2026_

Ordered steps per Wave-1 deliverable, each with its acceptance criterion. Index + rulings: [PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md) · design: [ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_RU_UNFREEZE.md) · proof: [VERIFICATION_SanskritLexicography_PWG_RU_UNFREEZE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_RU_UNFREEZE.md).

---

## Step 0 — preconditions for every deliverable

The default branch is **`master`**, not `main`. The main tree is commit-blocked by a tracked `.githooks/pre-commit`.

```sh
git -C C:/Users/user/Documents/GitHub/SanskritLexicography fetch origin
git -C C:/Users/user/Documents/GitHub/SanskritLexicography worktree add -b <branch> ../SanskritLexicography-<slug> origin/master
```

Never `git pull` in a shared clone (it can autostash and swallow a concurrent session's uncommitted work). Read `.ai_state.md` **in the worktree off `origin/master`** — the main tree's copy sits on `codex/russiantranslation-pr482-review-fixes` at 15-07 and still points at H963, which [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) supersedes. Claim the handoff atomically before any change.

**Standing constraints (all six deliverables):** read-only against `src/pwg_ru_translated.jsonl` · zero paid calls (W1-L excepted, ≤3) · never flip `SANLOSS_HARD_REJECT` / `TNMASK_HARD_REJECT` · never run `promote_en.py` · `sys.stdout.reconfigure(encoding='utf-8')` in every printing script · no UTF-8 BOM · multi-step logic goes in a `.py` file, not inline shell.

---

## W1-A — cohort clean-rate report + D-1 debt worklist

**Tier:** Sonnet 4.6 (`claude-sonnet-4-6`) — deterministic joins over existing evidence with fixed cohort definitions. The judgment (what the bar means) is the human's; the measurement is mechanical.
**Blocked by:** none. **Gates:** every drain in the repo.

1. Worktree per Step 0, slug `cohort-rates`.
2. Write `RussianTranslation/src/pilot/cohort_clean_rates.py`, stdlib-only, pure read.
3. **Partition** (ARCHITECTURE §2.1) — bind to existing machinery, do not invent:
   - `no_pwg` ← store `layer ∈ {pw, sch, nws, pwkvn}` (expect 6,009)
   - within `layer == pwg` (expect 5,594): `root_upasarga` ← key resolves to a rootmap in the `verbs01` `pwg_preverb1.txt` universe that [`verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py) reads; `nominal` ← it does not (the flat-card case per [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py))
   - anything else → `unassigned`, **reported, never dropped**
4. **Exclude** the 468 `provenance.h_reconstructed == true` rows from rates; count them separately; state the exclusion in the report.
5. **Join clean rates from frozen evidence, with provenance per number** (ARCHITECTURE §2.2). `no_pwg` **consumes** the H911 census figure (41–69%, median ~62%) — do not recompute it. `pwg` cohorts join from [`RUN_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md) windows + the census's H818 acceptance-canary family.
6. Emit `verdict` per cohort: `CLEARS_BAR` (≥80%) · `BELOW_BAR` · `INSUFFICIENT_EVIDENCE` (n too small to separate ~62% from 80%). Set `economy: "NOT_MEASURABLE"` with the census's `not_recoverable_note` as the reason.
7. Write `pwg_ru/h1112/cohort_clean_rates.json` + a dated `pwg_ru/h1112/H1112_COHORT_CLEAN_RATES_2026-07-17.md` carrying the results table (org rule: substantive tables get persisted, never chat-only).
8. **D-1**: emit `pwg_ru/h1112/h_reconstructed_worklist.jsonl` — 468 keys, derived `h`, and the 14 heads they collapse onto. Header comment: *this is the standing re-translation worklist; discharge requires an authorized live run.*
9. **D-1 regression guard** in [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py): assert `h_reconstructed` count == 468 unless a re-translation manifest documents a decrease. A silent drop must fail a test — the `h is None` 468→0 disappearance is the precise failure being guarded.
10. `CHANGELOG.md` `[Unreleased]` entry; commit; PR.

> **Acceptance:** `cohort_clean_rates.json` reports a verdict for all three cohorts, each `clean_rate` carrying the artifact path it came from and `unassigned == 0` (or the residue enumerated); the 468-row worklist exists; and the new selftest **fails** on a store mutated to 467 markers and **passes** on the real store.

**A `BELOW_BAR` verdict on every cohort is a PASS of this deliverable.** Ruling 3 asks the measurement to be capable of killing the 80% bar with data. Do not widen the sample, re-run, or retry to reach a better number.

---

## W1-B — offline false-flag rate for the two soft guards

**Tier:** Sonnet 4.6 (`claude-sonnet-4-6`) — mechanical recomputation over frozen pairs against an existing, selftested guard.
**Blocked by:** none for the measurement. **The arming decision it feeds is a human `@DECIDE`** (owner-gated at both `const`s).

1. Worktree, slug `softguard-falseflag`.
2. Assemble the frozen (source, emitted) pairs from [`h963/campaign_cards.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/) (SHA-pinned via `artifact_manifest.sha256` — verify the manifest **first**; if a hash mismatches, stop and report) plus promoted-store rows.
3. Recompute using the **real** guard, not a copy: pull `accept()` verbatim out of a generated harness exactly as [`accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js) does. A hand-written re-implementation would validate the measurement against itself — the anti-pattern in [Uprava FINDINGS §82](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).
4. **Denominator discipline:** count only cards that survived the `<ls>`/`{#` fidelity gate. It fires *first* (ARCHITECTURE §3.1); a card rejected there never reaches the SAN-LOSS counter, and pooling it would measure the wrong thing.
5. Partition flags: **true drop** vs **false flag**. Keep `SANLOSS` and `TNMASK` classes **separate** — their false-flag mechanisms differ (SAN-LOSS: cross-reference miscount, the H960 class; TNMASK: model self-expansion writing literal `<ls>..</ls>`). Pooling them would produce a meaningless average.
6. Write `pwg_ru/h1112/softguard_falseflag_rate.json` + a dated memo with the results table and a **recommendation** (`ARM` / `DO_NOT_ARM` / `FIX_COUNTER_FIRST`).
7. State the limit in the memo: frozen evidence is one route under one payload regime; the rate **bounds** the false-flag class, it does not prove the live rate.
8. `CHANGELOG.md`; commit; PR.

> **Acceptance:** the report gives a separate false-flag rate for `SANLOSS` and `TNMASK` with explicit numerator/denominator and named example keys per class; the manifest hash check passed; `git diff` shows **both** `const SANLOSS_HARD_REJECT = false` and `const TNMASK_HARD_REJECT = false` **unchanged**; and [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)'s literal-needle pin still passes.

---

## W1-C — H858 `grammar`-field `{Tn}` stranding fix

**Tier:** Sonnet 4.6 (`claude-sonnet-4-6`) — a diagnosed, localized fix with a known reproduction and a fixture-only test.
**Blocked by:** none.

1. Worktree, slug `grammar-tn-restore`.
2. Reproduce as a **fixture**: a card echoing `{T2}` in `grammar`, per the live `gokzuraka` recurrence ([RUN_LOG.md:909](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md)). Confirm current `restoreCard` leaves it literal.
3. Extend `restoreCard` in [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)'s emitted JS to restore `grammar` with the same placeholder map already used for `german`/`russian`.
4. Add a behavioural test on the `accept_sensecount_test.js` pattern (extract the real `restoreCard` from a generated harness): a `{Tn}` in `grammar` restores; german/russian behaviour is unchanged.
5. **Blast-radius query** (read-only): count promoted rows whose `grammar` matches `/\{T\d+\}/`. Report the count and keys. **Do not repair them** — store mutation escalates.
6. Confirm the interaction is understood and recorded: the soft `TNMASK` multiset check runs *before* `restoreCard` and sees the echoed `{Tn}` as **present**, so it passes the card and `restoreCard` then strands it. The fix belongs in `restoreCard`, not in TNMASK.
7. State plainly in the changelog: **forward-only**; `gokzuraka` is not reclaimable (no placeholder map was saved).
8. `node --check` the generated harness; `CHANGELOG.md`; commit; PR.

> **Acceptance:** the new test fails on `origin/master` and passes with the fix; `window_selftest.py` stays green (135/135 baseline); the generated harness passes `node --check`; the blast-radius count is reported; and the store is byte-identical (`git status` clean of any `.jsonl`).

---

## W1-D — H1070's three EN guards, offline

**Tier:** Sonnet 4.6 (`claude-sonnet-4-6`) for guards 1 and 3; **guard 2's diagnosis** may warrant Opus 4.8 (`claude-opus-4-8[1m]`) if the masking path proves non-obvious — it is the only silent-loss class.
**Blocked by:** nothing to build them. **Cashing them is gated on a human `@DO`** (a live judge-tier profile). Build anyway — that is Ruling 5.

1. Worktree, slug `en-guards-h1070`.
2. **Guard 2 first — diagnose before patching.** `accept()` already does `countOf(c, /\{#/g)` over the whole restored card, so a footnote `{#uc#}` *should* count. r102 dropped one and the guard did not fire ⇒ the failure is **upstream of the count** (masking/restore of `<F>` content), not in the comparison. Find where `<F>` content leaves the masked span. **Patching the counter without this diagnosis is the wrong fix.**
3. Land guard 2 in the accept path. If the accept-path fix proves unsafe to land offline, fall back to the HARD flag in [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) that H1070 explicitly names as the deferral option — and say which route was taken and why.
4. **Guard 1**: German-polyseme checklist line under `term-mistranslation` in [`gen_fidelity_judge_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_fidelity_judge_en.py) (Vergleich, braut/Braut, gelten, Zug, anführen, …) + the prompt rule in [`tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt): *"for polysemous German glosses, pick the sense the Sanskrit lemma licenses, never the frequent sense."*
5. **Guard 3**: extend the DE-RESIDUE gate to flag pure-cross-ref rows and NWS `{#..#}`-wrapped German as a **soft** class, so coverage stats stop counting them as translated.
6. **Parity**: a [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) row per change, classified SHARED / INTENTIONAL-DIVERGENCE / GAP. Guard 2 touches shared `accept()` ⇒ almost certainly SHARED; verify RU regressions stay green. Refresh hashes **only** via `lang_parity_check.py --update-hash`.
7. Fixture tests per guard. **No live judge call. No `promote_en.py`.**
8. `CHANGELOG.md`; commit; PR.

> **Acceptance:** guard 2 has a fixture reproducing r102's dropped `{#uc#}` that fails before and passes after, **with a written root-cause line naming where `<F>` content escaped the mask**; guards 1 and 3 are present with fixtures; `lang_parity_check.py` reports 49/49 clean; `window_selftest.py` green; and the store still carries **0 EN rows**.

---

## W1-E — ReverseDictionary dataset recovery + rights ledger

**Tier:** Opus 4.8 (`claude-opus-4-8[1m]`) — rights reasoning over an incomplete evidence base, where the correct output is a *bounded* claim and the tempting output is an unbounded one.
**Blocked by:** the **publish** is a human `@DECIDE` (the existing [GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) row). Recovery + ledger are not blocked.

1. Worktree, slug `revdict-rights`.
2. **Recover the canonical list.** [`ACL_DH_COMPATIBILITY_ANALYSIS.md:124`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md) cites `.doc.pdf/266820-reverse-Gasuns.txt`; the directory holds four `.mdx` files and no such file. Search git history (`git log --all --diff-filter=A -- '*266820*'`), the 250,026 / 255,882 `.doc` drafts, and local disk. Verify by line count.
   **If it cannot be found, that is the finding** — escalate as data loss (the H736 class) and stop at step 3. Do not reconstruct it from drafts.
3. Write `ReverseDictionary/RIGHTS_LEDGER.md` with the three buckets (ARCHITECTURE §6.2). The third bucket is the deliverable's point:
   - **PD** — subtractable
   - **In-copyright, marked** — `H` Edgerton 12,552 · `P` Vettam Mani 1,919 = **14,471 (5.4%)**
   - **In-copyright, UNMARKED — cannot be isolated** — Stchoupak–Nitti–Renou, Turner, Mylius, Kochergina, Pujol. Carry H270's caveat verbatim: 14,471 is a **lower bound**.
4. If step 2 recovered the list: write `build_pd_subset.py` emitting the subset **plus a rights-residue statement**. The subset artifact must **not** be labelled "PD-only" — it is "PD-minus-a-lower-bound", and the ledger says why.
5. **Flag** [`Reverse-Kochergina.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/) (701 KB, in-copyright) on public `master` as an H734-class exposure. **Flag only** — removal is a human call.
6. Update the GTD `@DECIDE` row with the sharpened question: *not* "publish full vs PD-only vs restricted", but **"the PD-only subset cannot be certified on available data — fund per-source lists for the 5 silent sources, publish with a stated lower-bound caveat, or keep restricted?"**
7. Run `/publish-safety-check` and **report** its output. Do not act on it.
8. `CHANGELOG.md`; commit; PR. **No publish. No file deletion.**

> **Acceptance:** `RIGHTS_LEDGER.md` exists with every source in exactly one of the three buckets and the unmarked bucket explicitly named as the blocker to certification; the dataset is either recovered+backed-up or its absence is escalated as data loss; the GTD `@DECIDE` carries the sharpened question; nothing was published and no in-copyright file was moved or deleted.

---

## W1-F — handoff backlog triage

**Tier:** Sonnet 4.6 (`claude-sonnet-4-6`) — per-row supersession judgment against a moved `origin/master`, via an existing skill.
**Blocked by:** none.

1. Run `/handoff-registry-audit`, scoped to this repo's **30 live rows** (22 🟡 + 8 🔵 in [`handoffs/README.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md), measured 17-07-2026; oldest 02-07).
2. Re-validate each against post-#511 `origin/master` (now through #519). Classify: **superseded** → archive · **still live** → keep/re-mint · **executed but unmarked** → close.
3. Apply the two known supersessions: **H963 → H1110** (H1110's own text says it supersedes H963 as the engineering/live resume point) and **H994 → H963** (already archived as a stale-clone duplicate).
4. Pay special attention to handoffs written **before #510/#511/#517** whose premises those PRs changed — the same staleness this plan's own §1 had to correct.
5. `python tools/registry_check.py --strict` must exit 0. Bucket counts and the next-free-ID marker are **derived**, never hand-edited.
6. `python tools/handoff_kanban_sync.py` after bucket changes.
7. Commit + push Uprava (direct to `main`, from a worktree — Uprava's own tree is hook-guarded too).

> **Acceptance:** `registry_check.py --strict` exits 0; every one of the 30 rows has an explicit verdict (no row silently left); H963 is archived under H1110; and the archived count + live count reconcile to the pre-triage 30.

---

## W1-L — the bounded c4 ladder (**owned by H1110 — do not re-mint**)

**Tier:** Opus 4.8 (`claude-opus-4-8[1m]`), per H1110's own model lock.
**Blocked by:** nothing to *run* it (c1/c4 are logged in). Everything it might unblock is blocked by a human `@DO`.

Not a deliverable of this plan. [H1110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1110-Opus_SanskritLexicography_pwg-ru-post-h1080-audit-fix-skills-c4-restart_17.07.26.md) already owns the post-H1080 audit + bounded c4 restart and carries its own atomic claim step. This plan adds only the binding constraints from Ruling 2:

- **≤3 paid calls.** Home route. **Threshold UNTOUCHED** (30 s bar, 180 s kill ceiling, unchanged).
- Report **only** as `CORRECTNESS_PROOF: PASS|FAIL` and **`two-profile`** (c5/c6 were `loggedIn:false` at 15-07; nothing since re-authenticated them).
- **Banned regardless of result:** `PRODUCTION_GO`, `production-ready`, `four-profile`, `scale GO`. Measured ~40 s vs a 30 s bar with warm-up ≈ measured is **steady-state**; a passing proof does not move it.
- The real unblock stays [GTD:579](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) (foreign-route provisioning) + the c5/c6 logins — both human `@DO`, neither touched here. Note GTD:579's own C-15 caveat: the 180 s kill ceiling is **route-independent**, so even a route fix may not unblock the drain.

> **Acceptance (H1110's, restated):** ≤3 paid calls spent; a faithful card produced end-to-end or an honest FAIL; `git diff` shows no threshold constant changed; and the report contains none of the banned labels.

---

## Wave-1 exit condition

Wave 1 is done when W1-A has reported. Everything else is parallel work that improves the lane's trustworthiness; **W1-A is the one that decides whether there is a lane to drain at all.** If it names no cohort ≥80%, the correct next move is a `/decision-record` re-deciding the bar — not another wave of drain preparation.

---

_Dr. Mārcis Gasūns_
