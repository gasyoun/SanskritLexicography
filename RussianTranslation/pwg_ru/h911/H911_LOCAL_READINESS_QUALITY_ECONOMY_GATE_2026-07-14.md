# H911 — pwg_ru LOCAL-READINESS quality/economy gate (offline)

_Created: 14-07-2026 · Last updated: 14-07-2026_

**Verdict: `LOCAL-READINESS = FAIL`.** Foreign generation, four-account scale, and
[H841](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md)/H842/H843 remain **blocked**.

**Executor:** Opus 4.8 (`claude-opus-4-8[1m]`) in Ultracode mode, under an **owner-authorized
executor-override** of the minted Fable 5 (`claude-fable-5`). Every H911 gate, threshold, evidence
boundary, and the **offline-only** restriction were preserved. **No** translation generation, probe,
account login, Linux provisioning, or store/TM mutation was performed. Generation model of the
evidence under review: `claude-sonnet-5`.

Tracking issue: [SanskritLexicography#459](https://github.com/gasyoun/SanskritLexicography/issues/459).
Handoff: [H911](https://github.com/gasyoun/Uprava/blob/main/handoffs/H911-Fable_SanskritLexicography_h818-local-quality-economy-readiness-gate_14.07.26.md).
Machine-readable companions in this folder: [census](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json) ·
[blind-review results](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_blind_review_results.json) ·
[frozen sample manifest v2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_blind_sample_manifest_v2.json).

## 0. Evidence boundary + provenance discipline

Existing evidence only; no missing denominators manufactured. Populations kept **stratified**, never
pooled across incompatible schemas. Missing telemetry is reported `unknown`/`not_recoverable`, **never 0**.

Sources (all hash-addressed; raw private outputs NOT committed):

- **H818 acceptance-canary evidence** — durable private archive `D:\ClaudeTools\evidence\H895_h818_acceptance\`
  (147 files, byte-verified), inventoried in
  [H899](https://github.com/gasyoun/Uprava/blob/main/handoffs/H899-Opus_SanskritLexicography_h818-acceptance-evidence-inventory_14.07.26.md).
- **H255 no_pwg Workflow drains** — the local, gitignored `RussianTranslation/src/pilot/output/wf_output.no_pwg_*.json`
  snapshots (immutable per-run `summary` blocks) + the single surviving `audit_window.report.json`
  (root `no_pwg_w05_rq1`) + `no_pwg_w1.*.keys.txt`.
- **H895 run1** — latency NO-GO, **no generation**; raw telemetry lost (documented in
  [H895](https://github.com/gasyoun/Uprava/blob/main/handoffs/H895-Opus_SanskritLexicography_h818-acceptance-DE-DK-latency-blocked_13.07.26.md)).
- Committed reports: [H818 rerun log](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_RERUN_2026-07-13.md),
  [latency-policy investigation](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PWG_RU_LATENCY_POLICY_INVESTIGATION_2026-07-13.md),
  [RUN_LOG](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md).

**Scope note:** the route-latency problem (H895/H909) is **independent** of quality/economy and does
**not** enter this verdict. Current promoted store = **11,605 rows** (baseline lineage: H895 11,579 →
w10 11,590 → w02-rerun 11,605).

## A. Denominator-honest census

Full data: [h911_quality_economy_census.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json).

### Family 1 — H818 acceptance-canary (Max-orchestrator path)

**Not** a demonstrated four-account production batch — the orchestrator path existed but these are
single-subcard canaries. The non-promoting `taru` presplit canary (2 calls, 1 clean, 5 fragments
healed+stitched) is reported **separately** and **excluded** from the clean-rate denominator.

| Production canary | Audit outcome | Store-row delta | Calls (recoverable) |
|---|---|---|---|
| durgA (`durg_a~~h0_zz_sch`) | **clean** | **+2 rows** (senses) = **1 clean subcard** | 1 (model_call; `workflow_result_count=1`) |
| darvI (`darv_i~~h0_zz_pw`) | reject — **SAN-LOSS(2/3)** (dropped sense "Löffel/spoon") | 0 | 5 (`run_summary calls=5`) |
| gaRanA (`ga_ran_a~~h0_zz_sch`) | reject — **SAN-LOSS** / needs_requeue | 0 | **not_recoverable_exact** |

- **Audit-clean: 1/3 = 33%. Fidelity-reject: 2/3 = 67%** (both SAN-LOSS).
- **Store rows are senses, not subcards:** durgA = 1 clean *subcard* → **+2** store *rows*.
- **Calls per clean subcard: INCOMPLETE — not published.** durgA 1 call/1 clean is exact; darvI 5
  calls/0 clean; gaRanA's isolated calls are `not_recoverable` (`run_summary calls=7` conflates the
  durgA+gaRanA+s10 segment, and `run_events.jsonl` model_call events carry **no `call_id`**, so per-key
  events cannot be deduped to real calls).
- **Tokens & API-equivalent cost: `not_recoverable`** (run_events has no token field; H818 dashboard
  `cost:null`). Never reported as 0.

### Family 2 — H255 no_pwg supplement-chain (Workflow-tool drains)

The bulk population. `wf_output.no_pwg_*.json` files are per-run snapshots; requeues re-attempt the
**same keys** — not pooled naively.

- **Only `no_pwg_w05_rq1` has a recoverable audit report: audit-clean = 13/21 = 62%** (a *requeue*
  window; content-defect 4, infra transient/null 4). All other windows' audit reports were overwritten
  → per-window audit-clean is `not_recoverable` from artifacts; RUN_LOG-sourced promoted counts below.
- **RUN_LOG-sourced per-window clean rates** (cited): w1 5/58 (infra-crippled first run, 52 null),
  w02 11/27 (requeue) & 10/15 (rerun), w03 9/13, w04 33/48, w06 29/54, w10 11/18.
- **Population audit-clean rate: per-window ~41–69% (median ~62%)**, excluding the w1 first run. This is
  **independently corroborated** by the [H818 rerun report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/H818_WINDOWS_LIVE_ACCEPTANCE_RERUN_2026-07-13.md)
  standing finding: the no_pwg lane's audit-clean rate is **~60–65%, explicitly "above the lane's real
  clean rate"**, i.e. **below** the 80% acceptance bar.
- **Tokens / cost / calls-per-clean: `not_recoverable` observed** (Workflow journals transient; RUN_LOG
  cites only isolated totals, e.g. w1 ~3.4M tokens, H442 ~1.8M/window).

### Economy — projected vs observed (kept separate)

- **Projected (offline, reproduced):** the deterministic 100-headword dry-run =
  124 subcards → 124 initial calls → **167.4** realism-adjusted agents (`124 × 1.35`) →
  **30,801,600 tokens** → **$58.09** API-equivalent (`perf_preflight`: 184,000 tok/agent, $0.347/agent,
  realism 1.35). _(The H911 prose "167.6" is a rounding slip for 167.4; the token/cost figures confirm
  167.4.)_ **$58.09 ≤ $75/100hw → PASS on the projected-cost field only** — an optimistic
  one-call-per-batch **floor**, not observed economy.
- **Observed:** `INCONCLUSIVE`. Observed calls-per-clean-subcard and observed API-equivalent
  cost-per-clean-subcard are **`not_recoverable`** for both families (no persistent token telemetry). The
  projection is **not** substituted for observed performance. Subscription marginal cash ($0 inside
  allowance) is distinct from this API-equivalent resource accounting.

## B. Systemic defects (audit-confirmed) + failure gallery

Grouped by the run's **actual audit contract**, not reviewer aesthetics. The surviving
`no_pwg_w05_rq1` semantic-risk gate + RUN_LOG give the confirmed defect taxonomy:

| Defect class | Kind | Evidence (redacted; hash-addressed in census) | Recurrence |
|---|---|---|---|
| **`missing_senses`** (= SAN-LOSS, dropped senses) | content-fidelity | `_sibi~~h0_zz_pw`, `_u_das~~h0_zz_pw`, `a_sud_da~~h0_zz_pw`, `aklizwa~~h0_zz_pw` (w05_rq1); darvI, gaRanA (H818) | **systemic** — recurs across w05_rq1, H818, and RUN_LOG windows |
| **`untranslated_braced_german_gloss`** | markup/completeness | `ajagan_d_a~~h0_zz_pw` (w05_rq1, **high-confidence**, score 210) — German left untranslated inside `{%…%}` | present, high-confidence |
| **`likely_circular_gloss`** / **`possible_sense_compression`** | content | `aklizwa~~h0_zz_sch`, `ambaz_w_a~~h0_zz_sch`, `ahi_pena~~h0_zz_sch` | recurring low-confidence |
| **`kill-timeout`** / **`selfheal-nothing-resolved`** | infra/generation | `_u_das` "kill-timeout 84s @ skelBytes=485"; `_sibi`/`a_sud_da`/`aklizwa_pw` "selfheal-nothing-resolved" | **systemic** — also w06 (7 nulls), w10, and the H442 kill-gate cascade |

**A defect is systemic where the mechanism recurs across keys/windows.** `missing_senses` (SAN-LOSS)
and the `kill-timeout`/`selfheal-nothing-resolved` infra class both clear that bar.

**Downgraded — NOT contract defects (verified against the audit contract):**

- **`[NWS:]` verbose attribution** (7/40 in the blind sample): the audit's STRANDED-ANCHOR class is
  specifically `{Tn}` mask placeholders ([stage2_pregate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/stage2_pregate.py) `ANCHOR_RE`),
  **not** `[NWS:]` markers; the surviving audit passed `aj_a~~h0_zz_nws00` and `m_ay_a~~h0_zz_nws00`
  **clean** despite the `[NWS:]` prefixes. → **reviewer stylistic concern**, excluded from fidelity-reject rates.
- **`{%…%}`-delimiter dropping** (8/40): audit passed dropped-delimiter cards (`aklizwa~~h0_zz_pwkvn`,
  `aj_a~~h0_zz_pwkvn`) **clean**; the contract flags the *opposite* (`untranslated_braced_german_gloss` =
  German left *inside* the braces). → **reviewer stylistic concern**.
- **V40** (`_badr_a~~h0_zz_pw`): «бреет {#kar#}» for "mit kar rasiren" reads as an infinitive→finite +
  idiom mangle — retained as a **reviewer concern only**; its sealed verdict is `unknown` (root not
  recoverable), so it is **not asserted** as a confirmed defect.

## C. Blind quality review — three separate measurements

Full per-card data (redacted; no translations): [h911_blind_review_results.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_blind_review_results.json).

**Protocol integrity (sol.md two-phase).** Freeze **v1** ([commit `564669fb`](https://github.com/gasyoun/SanskritLexicography/commit/564669fb)) was
**preserved but invalidated** for blind scoring: it sampled the 3 Max canaries whose individual
verdicts had been read before freezing (`prior_outcome_exposure`). Freeze **v2** ([commit `2906bd23`](https://github.com/gasyoun/SanskritLexicography/commit/2906bd23))
excludes those 3 **plus 3 other per-subcard verdict-exposed keys present as pairs**, and backfills
deterministically from the 114-card unexposed Workflow pool (strata preserved). **40 unexposed
keys+hashes** were frozen **before** scoring; only v2 was scored. The full worksheet stays private.

- **M1 — blind reviewer quality (n=40):** **27 fully publishable** (`pub`=5), **9 light-touch**
  (`pub`=4), **4 needs-repair** (`pub`≤3: `aj_a~~h0_zz_nws00`, `m_ay_a~~h0_zz_nws00`,
  `_s_a_k_a~~h0_zz_nws00`, `_badr_a~~h0_zz_pw`). Meaning preservation was strong across the sample; the
  4 low scores are the reviewer concerns above (`[NWS:]` verbosity + the V40 idiom mangle), which are
  **not** counted as fidelity rejects.
- **M2 — sealed automated audit:** `judge`/`judge_sonnet` = **null/unavailable for 40/40**. A canonical
  audit verdict is recoverable for only **15/40** (roots `no_pwg_w05_rq1` + `no_pwg_w1`); the other
  **25 are `unknown` and excluded from the denominator** — the n=15 rate is **not** extrapolated to 40.
  Within the 15: 10 audit-clean. Disagreements are dominated by w1 first-run *transient* requeues (not
  quality rejects) and 2 reviewer `[NWS:]` over-calls the audit correctly passed; 1 audit `requeue_defect`
  (`a_suci~~h0_zz_pw`, semantic-risk gate — specific risk **not** individually recoverable beyond
  `requeue_defect` membership, **not** attributed to `{%…%}`).
- **M3 — current promotion status (separate):** 33/40 have **similar current-store content**
  (token-Jaccard ~1.0), 7 absent. This is **not** exact provenance and **not** the audit verdict — an
  exact key + sense/card + RU-hash + promotion-provenance join was **not** performed, so **no
  audit-to-promotion escape is alleged**.

## D. Locked readiness gates → verdict

| Gate | Threshold | Result | Basis |
|---|---|---|---|
| audit-clean subcards | ≥ 80% | **FAIL** | population ~41–69% (median ~62%); H818 canary 1/3; w05_rq1 13/21; H818 report "~60–65%, above the lane's real clean rate" |
| fidelity rejects | < 5% | **FAIL** | SAN-LOSS/`missing_senses` + content `requeue_defect` ≈ 15–25% of generated cards (w05_rq1 4/21; H818 canary 2/3) |
| auth/malformed/manifest/duplicate/lost | all 0 | not a clean pass | no *confirmed generation-path* occurrence in recoverable evidence, but not fully verifiable (probe-path malformed seen; historical w06 lost-result, fixed [H805]); does not independently force the verdict |
| no repeated systemic quality defect | required | **FAIL** | `missing_senses`/SAN-LOSS + `kill-timeout`/`selfheal-nothing-resolved` both recur across windows |
| blind review — no material semantic-loss pattern | required | **FAIL** | SAN-LOSS is an audit-confirmed material semantic-loss pattern |
| **economy** projected API-equiv | ≤ $75/100hw | PASS (projected only) | $58.09 (optimistic floor) |
| **economy** observed calls/clean | ≤ 1.75 | **INCONCLUSIVE** | `not_recoverable` (no token/call-per-clean telemetry) — projection NOT substituted |
| **economy** observed $/clean | ≤ $0.75 | **INCONCLUSIVE** | `not_recoverable` |

**`LOCAL-READINESS = FAIL`.** The verdict rests on the **independently documented population
clean-rate hard-gate failure (<80%)** and the **recurring SAN-LOSS/`missing_senses` systemic defect** —
**not** on the incomplete 15/40 sealed-audit subset (which manufactures neither PASS nor FAIL). Thresholds
were not weakened; economy fields that cannot be measured are `INCONCLUSIVE`, and a measured hard-gate
FAIL dominates.

## Branch (per the corrected H911 logic)

**LOCAL-READINESS FAIL →** foreign generation, four-account scale, and H841/H842/H843 stay **blocked**.
No broad live retry and no store mutation in H911. The smallest systemic fix, ranked by measured
recurrence, is minted as a **narrowly-scoped OFFLINE fix handoff**:

1. **SAN-LOSS / `missing_senses`** (dropped senses) — highest recurrence → **minted** (see the H911
   footer / registry). Offline root-cause + code/prompt guard + selftest; live validation stays gated.
2. `kill-timeout` / `selfheal-nothing-resolved` infra class — ties to the H442 kill-gate cascade and the
   Codex runtime refactor (independent translate/heal pools), still unvalidated under load. *(backlog)*
3. `untranslated_braced_german_gloss` (high-confidence) → *(backlog)*.
4. Observed-economy instrumentation (tokens/calls-per-clean) — the INCONCLUSIVE economy fields need
   persistent per-call telemetry before any future gate can measure them. *(backlog)*

H909's independent foreign-route gate remains **WAITING ON OWNER**; even a PASS there does not lift this
FAIL. A one-account foreign acceptance may be minted only after **both** H911 and H909 PASS.

## Limitations

- Sealed per-card audit verdicts recoverable for only 15/40 (judge fields null; most window audit reports
  overwritten). The 25 `unknown` cards are neither pass nor fail.
- The blind worksheet's SOURCE is the per-output-sense German (paired), so **whole-dropped-sense**
  (SAN-LOSS) is detectable by the reviewer only via visible sense-numbering gaps; the audit's portrait-vs-output
  comparison (`missing_senses`) is the authority for that class.
- Tokens/cost `not_recoverable` for both families → observed economy is INCONCLUSIVE by measurement, not by choice.
- Current-source drift of the run-time input hashes vs live csl-orig was **not** re-rendered; the blind
  review used each artifact's own frozen source+output, so drift does not affect the review.

_Auto-generated by Opus 4.8 (`claude-opus-4-8[1m]`) as the H911 executor (owner-authorized override of Fable 5)._

_Dr. Mārcis Gasūns_
