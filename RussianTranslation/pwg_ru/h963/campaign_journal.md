# H963 — c4 correction-evidence campaign journal (append-only)

_Created: 16-07-2026 · Last updated: 16-07-2026_

Append-only. Never rewrite a prior entry; correct by appending a later one.

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`), Ultracode, Claude Code.
**Start:** 09:42 UTC / 12:42 MSK, 16-07-2026 (machine is UTC+3).
**Brief:** `H963_C4_FIVE_HOUR_CORRECTION_EVIDENCE_CAMPAIGN.md` (untracked, GitHub root).
**Worktree:** [`SanskritLexicography-h963-c4-live`](https://github.com/gasyoun/SanskritLexicography/tree/h963-c4-live-rung3), branch `h963-c4-live-rung3`, clean at `662a690f`.

---

## 09:42 UTC — checkpoint 1: acceptance, and a scope refusal

**Phase:** intake + reconnaissance.
**Live calls spent / remaining:** 0 / 0 (see below — the live matrix is NOT executable from this session).
**Store hash:** `cc1d544e…c805`, 11,605 rows — untouched, verified against the pilot's optimistic-concurrency base.

**The campaign is executing its OFFLINE half only. Zero live generation calls will be fired.** Three
independent reasons, each sufficient:

1. **This session is not the c4 session, and cannot become it.** The brief mandates `c4 only` via
   `D:\ClaudeTools\profiles\claude4\.claude` and "No second c4 CLI may run concurrently". This session's
   `CLAUDE_CONFIG_DIR` is **unset** → it runs the default profile `C:\Users\user\.claude`. Workflow
   subagents inherit the orchestrating session's credentials, so every generation call fired from here
   would bill and authenticate as the **wrong account**. That is the brief's own hard stop
   ("manifest provenance fails"). ~38 `claude` processes were live at intake; starting c4 work here
   would also risk being the prohibited second c4 CLI.
2. **Two of the brief's own hard stop conditions were already tripped** by the pilot it instructed us to
   close first — that pilot is already closed (`662a690f`, tree clean). Its recorded outcome: the real
   call **exceeded the 180 s kill ceiling**, and the two calls **were launched concurrently by mistake**.
   The brief's instruction for either condition is: stop all further live calls, continue the offline
   audit to the five-hour minimum. That is what is being done.
3. **The owner's own quoted words ask for "all the data for final pipeline correction"** — not for live
   calls. The offline packet is that data.

**Protocol deviation:** none introduced this session. The pilot's concurrency deviation is **preserved as
recorded**, not reinterpreted.

**Verified, not assumed:** all four pilot artifact SHA-256s recomputed and matched exactly
(`manifest.canary.json` `7fbb7b74…`, `run_pilot_wf.canary.js` `0d6e6aab…`, `manifest.real.json`
`5a438e34…`, `run_pilot_wf.real.js` `b088afbd…`). The prior session's evidence chain is sound.

---

## 10:05 UTC — checkpoint 2: the campaign's headline finding (C-01)

**Phase:** offline audit — kill-gate envelope.
**Live calls spent / remaining:** 0 / 0.
**Store hash:** `cc1d544e…c805`, 11,605 rows — unchanged.

### The 180 s kill ceiling is route-independent, and it is the unexamined blocker

The kill budget, verified at its call site
([`run_pilot_wf.real.js:95`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py), generated):

```js
killBudgetMs = skelBytes => Math.min(180000, Math.max(45000, 2.0 * (20000 + 45 * skelBytes)))
killBudgetForCur = cur => (cur.length === 1) ? KILL_CEIL_MS : killBudgetMs(skelBytesOfKeys(cur))
```

**The design invariant is stated in the code itself**
([`gen_opt_harness2.py:164-166`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)):
the slope "is set ABOVE the observed ceiling and then KILL_FACTOR is applied on top, **so no legit call
(even a +50% variance one) is ever killed**".

**`KILL_CEIL_MS` silently destroys that invariant.** The ceiling was lowered **480 000 → 180 000**
(`gen_opt_harness2.py:183`: "Was 480000 (8 min); the worst pril10_w1 agent ran 390 s") to kill one
observed stall — **and the envelope was never re-derived**. The canonical design doc
[`FAILURE_MODES_AND_KILL_GATE_2026-07-04.md:150`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md)
**still documents `KILL_CEIL_MS` = 480 000** and still asserts "Every observed legit call (≤ 84 s) sits
**far** under its budget" — true at 480 s, false at 180 s. Doc/code drift on a load-bearing constant.

Consequences, from the benchmark's **own** measured rates (doc `:136`, centre ≈ 25 ms/skel-byte, observed
max ≈ 44):

| band | skel bytes | meaning |
|---|---|---|
| SAFE | ≤ 4 091 B | survives even at the worst observed rate |
| COIN-FLIP | 4 091 – 7 200 B | dies on ordinary rate variance alone |
| **DOOMED on any route** | **> 7 200 B** | **killed even at the centre rate, on a perfectly healthy route** |

Per-shape (raw→skel projected across the **measured** per-key ratio band [0.537, 0.750], n=2 keys —
`zaz` skel 2 046 B / raw 3 813 B = 0.537; `upama` 3 560 / 4 745 = 0.750; their sum 5 606 B reproduces the
harness's logged `skelBytes` exactly):

| shape | skel B | verdict |
|---|---|---|
| pilot b0 `zaz`+`upama` (MEASURED) | 5 606 | **COIN-FLIP** — dies on rate variance alone |
| brief tiny stratum (<6 KiB raw) | 3 222–4 500 | SAFE .. COIN-FLIP |
| brief typical-hi (12 KiB raw) | 6 444–9 000 | COIN-FLIP .. DOOMED |
| nominal-core **MEDIAN** (12 556 raw) | 6 743–9 417 | **COIN-FLIP .. DOOMED** |
| `Atman` (21 610 raw) | 11 605–16 208 | **DOOMED** |
| `rasa` (38 693 raw) | 20 778–29 020 | **DOOMED** |
| `yoga` (40 555 raw) | 21 778–30 416 | **DOOMED** |

**Why this matters more than the latency story.** The `kAla`/`brahman`/`Atman`/`rasa`/`yoga` class — the
band-5 ultra-core heads, i.e. the *highest scholarly priority* material — is **structurally undeliverable
at a 180 s ceiling on any route, healthy or not**. The median nominal card is coin-flip-to-doomed. The
currently-recommended open path is the **foreign-route latency investigation (H909)** — but a route fix
does not move a hard 180 s ceiling that a median card cannot meet at the benchmark's own healthy centre
rate. **H909 would not unblock the pipeline.** This is the single most important thing the correction
packet must tell Sol.

**A third confound on the pilot, previously unrecorded.** The pilot's real call (skel 5 606 B) sits inside
the COIN-FLIP band: it would survive at 25 ms/B and die at 44 ms/B. Its death is therefore consistent with
**both** a slow route **and** ordinary rate variance on a healthy one. The pilot cannot distinguish them —
on top of the already-recorded concurrency confound. The pilot report attributes the kill to latency +
self-contention; it did not identify the kill-gate/size interaction. **This is not a criticism of that
report** — the arithmetic simply wasn't run.

**Interacting defect:** `--max-agents=1` (which the brief *mandates* for all eight campaign calls)
mechanically forces `max_heal_agents: 0` (`wf_output.h963_c4_real.json`), so a single kill-timeout
destroys **every card in the batch** with no heal lane — observed: both cards → null,
`"budget-kill-switch[heal]: hit 0 agent() calls"`.

**Honesty bound:** n=2 keys for the skel/raw ratio, and both measured ratios straddle the median's
DOOMED threshold (0.573). The median card is *more likely than not* undeliverable — **not proven**
undeliverable. `Atman`/`rasa`/`yoga` are doomed at any plausible ratio; that part is robust.

**Evidence:** `src/pilot/output/h963_c4_campaign/killgate_envelope.py` (non-behavioural, read-only,
attempt-dir, uncommitted; hashed in the artifact manifest).

**Open hypotheses / evidence still needed:**
- What is the true skel/raw ratio distribution across the 114 prebuilt-input nominal heads? (offline,
  computable, would replace the n=2 band with a real distribution — queued.)
- Was the 480→180 lowering ever reviewed against the size distribution? (search H189 history.)

**Blocker:** none for the offline audit.

---

## 10:28 UTC — checkpoint 3: C-01 quantified over the real candidate universe

**Phase:** offline audit — deliverability census.
**Live calls spent / remaining:** 0 / 0.
**Store hash:** `cc1d544e…c805`, 11,605 rows — unchanged.

Applied the C-01 envelope to the **actual 114-head runnable nominal universe**
(`candidate_scan.json`, schema `pwg.h963_c4_pilot_candidates.v1`, real `raw_bytes` per head), in the
pipeline's **most generous possible configuration** — one card per agent call. This is an **upper
bound**: `killBudgetForCur` grants a single-card call `KILL_CEIL_MS` unconditionally, and
`skelBytesOfKeys` **sums** skeletons across a batch, so any batching can only make delivery worse.

Raw-byte distribution of the 114: min 2,418 · p25 8,445 · **median 12,568** · p75 17,817 · p90 26,656 ·
max 40,555 B.

**Deliverability at the 180 s ceiling, across the measured skel/raw ratio band:**

| skel/raw ratio | SAFE | COIN-FLIP | DOOMED on any route |
|---|---|---|---|
| 0.537 (best case) | 23 (20.2%) | 39 (34.2%) | **52 (45.6%)** |
| 0.655 (batch mean) | 11 (9.6%) | 37 (32.5%) | **66 (57.9%)** |
| 0.750 (worst case) | 8 (7.0%) | 31 (27.2%) | **75 (65.8%)** |

**Headline: only 7–20% of the runnable nominal-core universe is reliably deliverable. 46–66% is
undeliverable on ANY route, healthy or not.**

**The ceiling bites hardest exactly where the scholarly value is highest** (at the 0.655 mean ratio):

| band (5 = ultra-core) | n | median raw | SAFE | DOOMED |
|---|---|---|---|---|
| **5** | 82 | 15,144 B | **3 (4%)** | **57 (70%)** |
| 4 | 32 | 8,242 B | 8 (25%) | 9 (28%) |

Scholarly priority and deliverability are **anti-correlated**: the highest-priority heads are the
longest articles, and length is exactly what the ceiling kills. The pipeline is structurally worst at
precisely the material the project most wants to translate. **This is not a route problem and no route
fix touches it.**

**Consequence for the H963 decision.** The pilot report's recommended open path is the foreign-route
latency investigation ([H909](https://github.com/gasyoun/Uprava/blob/main/handoffs/H909-Opus_SanskritLexicography_h818-foreign-route-paired-probe-analysis_14.07.26.md)).
On this evidence, **H909 is necessary-but-nowhere-near-sufficient**: even a perfect, instant route leaves
70% of band-5 undeliverable, because the blocker is a hard ceiling the card cannot meet at the
benchmark's own healthy centre rate. Re-opening H909 before correcting the kill-gate envelope would
spend the owner's quota measuring the wrong variable.

**Honesty bounds (all five carried into the report, none of them small):**
1. skel/raw ratio band is **n=2 keys** — the weakest link. The DOOMED verdict is robust for the largest
   heads across the whole band; the median's verdict is **not**.
2. Rates come from **one** benchmark run (13 calls, 04-07-2026) whose largest skeleton was **2,929 B**.
   Every number extrapolates far outside its fitted range. This cuts both ways.
3. Upper bound only (one card per call); real batching is worse.
4. TM hits can remove a card from the agent lane entirely — not modelled (TM contributed 0 for the
   pilot's keys, but would help at scale).
5. Says nothing about c4 route latency, which is separate and **additive**.

**Evidence:** `src/pilot/output/h963_c4_campaign/nominal_deliverability.py` (read-only, attempt-dir,
uncommitted; hashed in the artifact manifest). Input: `candidate_scan.json`.

**Blocker:** none for the offline audit.

---

## 10:51 UTC — checkpoint 4: validation gates + finding C-02

**Phase:** offline audit — validation gates.
**Live calls spent / remaining:** 0 / 0.
**Store hash:** `cc1d544e…c805`, 11,605 rows — unchanged.

**Gates run:**

| gate | result |
|---|---|
| `node --check` on both generated harnesses | **PASS** (canary + real) |
| `headless_worker_selftest.py` | **PASS** (incl. D-A `claude_argv_prefix` + D-J tree-kill) |
| Ruff fatal (`E9,F63,F7,F82`) on campaign scripts | **PASS** |
| `git diff --check` | **clean** |
| every JSONL row parses | **PASS** (10 + 3 + 114 rows) |
| artifact SHA-256 re-verification | **PASS** — all 4 pilot hashes match the report exactly |
| `window_selftest.py` | **FAIL — 104/131, aborts on the pre-existing LANG_PARITY gate** |

**Language-parity baseline, reported separately as the brief requires.** 3 unresolved violations
(`max_account_orchestrator.py`, `max_account_orchestrator_selftest.py`, `accept_sensecount_test.js`).
**Pre-existing, not caused by this campaign** — those files were last touched 15-07-2026 by `6c8115d4`
(D-P fix) and `a0c529df` (D-Q canary), the day before. This session changed **zero tracked files**
(`git status`: 5 new untracked files under `pwg_ru/h963/` only). **The hashes were NOT updated** — that
is the owner's distinct human reaffirmation to make, per the brief and per H963.

### C-02 (high): the parity gate hard-aborts the suite, masking 27/131 tests indefinitely

`window_selftest.py:5192` `main()` runs its 131 tests as a bare sequential loop —
`for test in (...): test()` — with **no per-test exception isolation**. The parity gate
(`test_lang_parity_ledger_complete`, `window_selftest.py:1397`) sits at roughly position 105 and raises
`AssertionError`, so **the suite aborts and the remaining 27 tests never execute** — among them
`test_lang_parity_hash_crlf_independent` and `test_frag_groups_presplit_parity`, which are real
pipeline gates.

Observed: **131 test functions defined, 104 PASS emitted, then abort (exit 1).** That is **20.6% of the
suite silently not running**.

**Why this is a silent failure and not just a red test.** The parity decision is *deliberately* escalated
to a human and the brief *forbids* clearing it — so this gate is **red by design and indefinitely red**.
For as long as it stays red (since 15-07-2026), a fifth of the suite is dark, and a genuine regression in
those 27 tests would be indistinguishable from the known-red parity gate. `.ai_state.md` still records
the H971 re-audit's "window_selftest **131 PASS**" — a claim no longer reachable while parity is red.

**Correction boundary:** do **NOT** touch the parity hashes (human decision, unchanged). **DO** isolate
per-test failures in `main()` so one red gate cannot mask the rest, and make the summary report
`run/passed/failed/defined` counts. That is a pure test-harness change, behaviour-preserving for the
pipeline — it does not weaken the parity gate, it stops the gate from hiding its neighbours.

**Regression test:** assert `len(tests_run) == len(tests_defined)` and that an injected single failure
still lets every other test execute and be reported.

**Blocker:** none for the offline audit.

---

## 11:14 UTC — checkpoint 5: finding C-03 — rung 3 was measurable offline all along

**Phase:** offline audit — analysis Q9 (what guard telemetry was actually exercised).
**Live calls spent / remaining:** 0 / 0.
**Store hash:** `cc1d544e…c805`, 11,605 rows — unchanged.

Ran the existing offline guard fixture suite **against the pilot's own real generated harness**:

```
node src/pilot/accept_sensecount_test.js src/pilot/output/h963_c4_pilot/run_pilot_wf.real.js
```

**Result: `accept_sensecount_test: PASS` (exit 0).** Among the assertions that passed:

| assertion | what it proves |
|---|---|
| `D-Q canary: drop 1st sense -> KEPT, fidelity-clean, SANLOSS fires (dropped=1)` | **SAN-LOSS true-positive sensitivity** |
| `D-Q canary: drop middle sense -> … SANLOSS fires (dropped=1)` | ditto, positional |
| `D-Q canary: drop last sense -> … SANLOSS fires (dropped=1)` | ditto, positional |
| `D-Q canary: drop 2 senses -> KEPT, dropped=2` | multi-drop counting |
| `D-Q canary: faithful 3/3 is clean (no false SANLOSS)` | no FP on a faithful fixture |
| `hard: darvI 2/3 shortfall REJECTED when armed` | **armed hard-reject works** |
| `hard: dropped {Tn} REJECTED when armed` | **armed TNMASK hard-reject works** |
| `FP-regression: exp=0 cross-ref card is skipped (never flagged)` | FP regression guard |
| `reordered-but-complete {Tn} multiset is not flagged` | no FP on reordering |

### This corrects the pilot report's central rung-3 conclusion

The pilot report states: *"SAN-LOSS true-positive sensitivity was NOT exercised… the detector's ability
to catch a silent drop — the thing rung 3 exists to measure — was never tested"* and *"Rung 3 remains
unmeasured. Nothing here supports arming a hard reject."*

That is **true of the live canary** but **false of the system's actual knowledge state**. The detector's
sensitivity is a property of **deterministic code** (`accept()`), and it is already proven by fixtures
committed 15-07-2026 as the D-Q work — the very same session's own output.

**The live canary is the wrong instrument, and structurally so.** A canary can only exercise the
detector by *hoping the model misbehaves*. If the model behaves — as it did, emitting 3/3 senses — the
detector is **never invoked** and nothing is learned, having spent a paid call. Detector sensitivity was
never a live-call question.

**Rung 3 decomposes into two questions with different instruments:**

| rung-3 question | right instrument | status |
|---|---|---|
| Does the guard **catch** a real silent drop? (true-positive sensitivity) | offline fixture — deterministic, free | **ALREADY PROVEN** for the modelled drop shapes |
| Does the guard **misfire** on correct **real model output**? (false-positive rate) | needs clean **real** cards | **GENUINELY UNMEASURED** — n=1 synthetic, 0 real clean cards |

**Consequence:** arming the hard rejects is **not** blocked on true-positive sensitivity. It is blocked
only on the false-positive rate on real output — which requires clean real cards, which **C-01's 180 s
ceiling currently prevents from existing**. C-01 and rung 3 are therefore the same blocker wearing two
hats: fix the envelope → obtain clean real cards → measure the FP rate → arm.

**Honesty bound (important, do not drop this).** The fixtures prove sensitivity on **constructed** drop
shapes (1st / middle / last / multi-sense). They cannot enumerate the space of real model output: a real
failure could take a shape the fixture does not model (a sense *merged* rather than dropped, a partial
gloss, a paraphrase that preserves count but loses content). So the honest claim is **"true-positive
sensitivity is proven for the modelled drop shapes"**, not "the detector is validated". The residual
live question is real — it is just far narrower than "rung 3 is unmeasured".

**Blocker:** none for the offline audit.

---

## 11:32 UTC — checkpoint 6: C-01 refined — the gate lost its discriminative power

**Phase:** offline audit — C-01 provenance.
**Live calls spent / remaining:** 0 / 0.
**Store hash:** `cc1d544e…c805`, 11,605 rows — unchanged.

**All three kill constants drifted from the design doc, not just the ceiling:**

| const | doc `FAILURE_MODES_AND_KILL_GATE_2026-07-04.md` | code `gen_opt_harness2.py` |
|---|---|---|
| `KILL_BASE_MS` | 30 000 (`:147`) | **20 000** (`:172`) |
| `KILL_FLOOR_MS` | 120 000 (`:149`) | **45 000** (`:178`) |
| `KILL_CEIL_MS` | 480 000 (`:150`) | **180 000** (`:183`) |

**The doc's worked envelope table (`:152-154`) is entirely stale.** It reads: *"744 B → 127 s · 1182 B →
166 s · 1828 B → 225 s · 2929 B → 324 s · 3956 B → 416 s · ≥8 kB → 480 s (ceil). Every observed legit
call (≤ 84 s) sits **far** under its budget."* Recomputed under the **current** constants:

| skel | doc says | actually now |
|---|---|---|
| 744 B | 127 s | 107 s |
| 1 182 B | 166 s | 146 s |
| 1 828 B | 225 s | **180 s (clamped)** |
| 2 929 B | 324 s | **180 s (clamped)** |
| 3 956 B | 416 s | **180 s (clamped)** |
| ≥8 kB | 480 s | **180 s** |

Every size ≥ ~1,828 B now receives a **flat 180 s**. The doc's monotonically-rising budget curve no
longer exists.

### The deeper point: the gate is no longer a stall detector

The gate's entire purpose (doc `:96-97`, `:155-156`) was to **discriminate** a legit-slow call from a
doomed retry-cap stall: *"A legit call should finish well under 2× its expected time; a doomed stall
(≥5× on H155) blows past it."* That separation only works while the budget tracks complexity.

At a flat 180 s it does not. For any skeleton beyond ~4 KiB, a **legit** call at the observed-max rate
(44 ms/B → 176 s at 4 kB) and a **doomed** stall both exceed the budget. The gate fires on both
identically. **It has degraded from a stall detector into a blunt fixed timeout** — and a fixed timeout
below the work's own expected duration is not a backstop, it is a cap on card size.

That is the precise, mechanism-level statement of C-01: *the pipeline did not lose the ability to
translate large cards because a route got slow; it lost it when the ceiling stopped scaling with the
work.*

**Provenance is untraceable from git.** The generator has only 13 commits and the first
(`c89d0cf8`) is the import — the repo's history is squashed, so the 480→180 change predates the visible
history. **The only surviving record of the change is the code comment itself** (`:183`: "Was 480000
(8 min); the worst pril10_w1 agent ran 390 s"). There is no reviewable evidence that the envelope was
re-derived against the card-size distribution when the ceiling was lowered — and C-01 is the evidence
that it was not.

**Blocker:** none for the offline audit.

---

## 11:52 UTC — checkpoint 7 (FINAL): the campaign corrects itself twice

**Phase:** close-out.
**Live calls spent / remaining:** **0 / 0 — none fired, none owed.**
**Store hash:** `cc1d544e…c805`, 11,605 rows — **verified unchanged at close**, byte-identical to the
campaign base. TM sidecars unchanged.

The 108-agent workflow completed (0 errors, ~11.0M subagent tokens, 98 min): 7 call-graph segments,
12 census classes, ~79 adversarial verifiers, 12 analysis answers, 3 reports. **87 candidates → 59
CONFIRMED · 11 PLAUSIBLE · 9 REFUTED.**

### The real headline was not the kill gate

Checkpoints 2–6 above were written before the census landed and they **buried the lede**. The census
found — and this session **independently re-verified against the live store**, rather than taking the
report's word:

| Verified this session | Value |
|---|---|
| Rows carrying a raw `{Tn}` | **670 / 11,605 (5.77 %)** — `sense_tag` 376 · `h` 223 · `differentia` 72; example row `{"h": "{T104}"}` — a **headword literally reading `{T104}`** (**C-01**) |
| Rows with `h == null` | **468** — exact match to the packet (**C-02**) |
| Poisoned launch gate | probe JSONL lines 14–15: `verdict: GO` **+** `gate_reason: "latency 53956ms > 30000ms"` **+** `probe.latency_ms: 53956`, on the `no_pwg_w07`/H255 lane — **a real launch fired under it: 532,941 tokens, 5/36 clean, 32 kill-timeouts** (**C-07**) |

**C-04** explains why none of it surfaced: `validate_final_card_schema.py`, the *only* component
encoding `record.required`, runs **only in CI against a hand-made passing fixture, never on live
output**. The corruption is **already shipped**, and it outranks every forward-looking finding here.

### Two corrections against this campaign's own work

1. **C-25 — self-inflicted, and it lands.** `build_campaign_evidence.py` recorded the killed 180 s call
   as `subagent_tokens: 0`, defended in-file as *"0 is MEASURED, not missing"* — in the file whose own
   docstring mandates null-not-zero. Verified: **neither `wf_output` carries any token field**, so
   `59250` and `0` were **both hand-entered**. The call ran 180 s and certainly burned tokens nobody
   captured. **The campaign committed the exact silent-failure class it was sent to census.** Corrected
   in-place: `null` + reason; `59250` re-labelled second-hand; `skel_bytes` re-labelled
   derived-by-extraction.
2. **The kill-gate magnitude (checkpoints 2–3) was over-claimed.** The packet ranks it **C-15,
   medium · telemetry-only**, and rules *"do not treat 44/25 ms/B as solid — one benchmark, 13 calls,
   largest skeleton 2 929 B"*. **That is right.** The **mechanism** stands (clamp falsifies the
   invariant; flat 180 s above skel > 1 555.6 B; the gate stopped discriminating legit-slow from
   doomed-stall; the pilot's card was plausibly size-doomed — a third confound the pilot never named).
   The **magnitude** — "7–20 % deliverable / 46–66 % doomed / band-5 70 % DOOMED" — is a **projection**
   on that 13-call fit extrapolated ~3× beyond range **times** an n=2 skel/raw ratio band. **It is a
   hypothesis worth testing, not a measurement**, and this journal stated it too confidently. H1080,
   the GTD `@DECIDE` and the H909 re-scope were corrected to demand the two free offline measurements
   *before* any ruling.

### Protocol deviations introduced this session

- **None affecting evidence.** No live calls, no store/TM mutation, no parity-hash update, no reroll.
- **One near-miss worth recording.** The `Uprava-h1080` worktree was pruned by another actor
  mid-session. Because `GitHub/` is itself a git repo, `git reset --hard origin/main` in that directory
  then **silently retargeted from Uprava to github-spine**. No damage (github-spine was clean and
  0 ahead; the reset was a fast-forward; `reset --hard` does not touch untracked files, so the ~85
  sibling repos were untouched), and all pushed Uprava work was verified intact. But the failure mode is
  general and sharp: **a broken worktree link silently falls through to the parent repo, and a
  destructive command aimed at repo A executes against repo B.** Recovery: fresh worktree at an
  absolute path, `.git`-is-a-file verified, `origin/main` confirmed to resolve to a *Uprava* commit.

### Close-out state

- **H963:** 🟡 WAITING ON OWNER — unchanged. **NOT PASS.** H255 frozen.
- **Successor:** [H1080](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1080-Opus_SanskritLexicography_pwg-ru-killgate-envelope-correction-packet_16.07.26.md)
  — registered on Uprava `origin/main`; defers to the packet's canonical C-01…C-59.
- **Draft PR:** [#498](https://github.com/gasyoun/SanskritLexicography/pull/498) — converted to draft, **not merged**.
- **Generalised lesson:** [Uprava FINDINGS §93](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).
- **Owner decision outstanding:** the ceiling `@DECIDE` in [GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) — **measure first, it is free**.

_Dr. Mārcis Gasūns_

---

## 17-07-2026 — checkpoint 8: evidence reconciliation after independent review

This append-only correction supersedes the campaign-duration, finding-count, and deliverability
summaries above without rewriting the historical checkpoints.

- **Actual elapsed campaign:** 09:42–11:52 UTC = **2 h 10 min**, not five hours. The 108-agent
  subworkflow lasted **98 minutes**.
- **87 provisional candidates reconciled:** the final C-01…C-59 packet retains **49 confirmed,
  9 plausible, and 1 mixed confirmed-path/plausible-trigger finding**; **19 provisional candidates
  were merged** into retained findings; **9 were refuted and dropped**; **0 were dropped for another
  reason**. Total = 87. The earlier “59 confirmed / 11 plausible / 9 refuted” line conflated retained
  IDs with verdict classes and did not account for merged candidates.
- **Withdrawn projection:** `SAFE` / `COIN-FLIP` / `DOOMED`, “7–20% deliverable,” and “46–66%
  undeliverable on any route” are not supported by serial whole-card evidence. They combined an
  `n=2` skeleton/raw ratio with a benchmark extrapolated beyond its measured range. The derived
  JSONLs now carry `null` plus an explicit withdrawal reason. Raw pilot artifacts remain unchanged.
- **Retained mechanical finding:** the 180-second clamp saturates for 113/114 current candidate
  skeletons, so the current kill budget has little admission-policy discrimination above 1,556 bytes.
  This is telemetry and policy input, not proof that large cards cannot be translated.
