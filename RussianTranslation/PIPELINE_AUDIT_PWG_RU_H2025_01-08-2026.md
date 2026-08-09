# PWG→RU money-lane pipeline audit — H2025 (Fable dual-run lane)

_Created: 01-08-2026 · Last updated: 01-08-2026_

**Audited revision:** `b4db4259` (release 1.117.0, post-H2118).
**Handoff:** [H2025](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2025-Fable_SanskritLexicography_hygiene-pipeline-audit-pwg-lane_31.07.26.md) — `/pipeline-audit` with mandatory Phase 2b money checks.
**Executor:** Fable 5 (`claude-fable-5`), four parallel read-only Explore agents (call graph · silent-failure census · route-parity/budgets · data-at-rest/cost-gates). Static reading only — **no paid call, no probe, no selftest run, no store/TM mutation** occurred in this audit.
**Series position:** extends [PIPELINE_HARDENING_AUDIT_2026-07-25.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HARDENING_AUDIT_2026-07-25.md) (Codex, rev `f96361ca`) and [PIPELINE_AUDIT_2026-07_H818.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_AUDIT_2026-07_H818.md); dual-run counterpart of the same-day Grok 4.5 (`grok-4.5`) memo [PIPELINE_AUDIT_PWG_RU_01-08-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/PIPELINE_AUDIT_PWG_RU_01-08-2026.md) (§8 below adjudicates the two lanes).

---

## 1. Verdict in one paragraph

The headless lane's *paid boundary* is genuinely hardened: route pin, sealed manifests/preflights, mandatory call-reservation ledger, kill-tree containment, atomic+backed-up store replace, journaled batch promote. The residual money risk has moved **off** the call path and now sits in (a) the **promote/merge semantics** — the FINDINGS §9 overlay-wipe class is still live in two paths and 13 non-promote store mutators bypass the promote lock entirely; (b) **defaults** — cost and call ceilings default to `None` and the evaluability gate explicitly passes when unset; (c) **prose-only gates** — the live-gate GO/NO-GO is never consumed by code, the canary half of the gate exists only in skill text, and the skill states a latency policy 2.2× stricter than the one the code enforces; and (d) a **scheduler swallow** that can dispatch the same headwords into a second paid window. Promotion remains **NO-GO by default posture**; `--stop-before-promote` discipline stands.

## 2. Real call graph (verified at call sites)

Entry points a human/skill actually invokes:

| # | Entry | Command | Anchor |
|---|---|---|---|
| E1 | `/pwg-live-gate` health | `python src\pilot\h963_c4_gate0_probe.py [--account c4]` | [h963_c4_gate0_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py):7-11 |
| E2 | `/pwg-live-gate` canary | `python src\pilot\headless_worker.py <canary_manifest> --output … --only-profile c4 --max-agents 1 --timeout 180` | [headless_worker.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py):1157-1177 |
| E3 | `/pwg-bounded-run` (paid window) | `python src\pilot\bounded_staged_run.py --plan … --coord-dir … --only-profile c4 --max-windows 1 --max-calls <n> --stop-before-promote --execute` | [bounded_staged_run.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py):942-989 |
| E6 | `/pwg-window-close` | `audit_window.py` → `classify_run.py` → `requeue_from_audit.py` → `promote_final_cards.py` → `translation_memory.py build`/`build-frags` → coverage/parity/ledger checks | skill + [coordinator.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py):2524-2605 |

The money path (E3):

```text
bounded_staged_run.run()                                    bounded_staged_run.py:809
  ├─ refuse --cohort-width>1 on --execute                   :814-821
  ├─ coordinator validate-preflight (subprocess)            :851
  ├─ cost_ceiling_evaluable(...)  — FAIL-CLOSED iff SET     :147-167, :856
  ├─ CallReservationLedger(run_id, max_calls)               :887   ← pre-spawn call authority
  ├─ mao.probe_fleet(...)                                   :889
  └─ BoundedSupervisor.run()                                bounded_supervisor.py:286
       └─ run_window → mao.cmd_run_once                     bounded_staged_run.py:621-631
            └─ SPAWN: headless_worker.py <manifest>
                 --preflight-sha256 --manifest-sha256       max_account_orchestrator.py:486-492
                 env: CLAUDE_CONFIG_DIR, PWG_CALL_RESERVATION_*    :499-504
                 pre-spawn: sha drift check :469, validate_profile
                 + validate_preflight_artifact :478-480
                 post: result-hash match :549-555
       └─ mao.cmd_record_done → coordinator record-output
            └─ audit_window.py (killable subprocess)        coordinator.py:1639-1648
       └─ --stop-before-promote ⇒ STOP (store+TM untouched) bounded_staged_run.py:635-640
```

Close path (when a human authorizes promotion):

```text
coordinator promote-ready --gen-model-version X             coordinator.py:2353
  ├─ revalidate clean-output sha / count / state / requeue  :2381-2403
  ├─ PromoteClaim (O_EXCL TTL lock)                         promote_lock.py:137-155
  ├─ promote_final_cards.batch_promote(...)                 coordinator.py:2421-2432
  │    backup (_fsynced_backup :541) → merge → mkstemp+fsync
  │    +durable_replace (_atomic_write_rows :500-515)
  ├─ promotion_journal phases prepare→store_committed
  │    →derived_validated→complete                          promotion_journal.py
  └─ build_promotion_derived: TM build + build_frags
       + clear_denials_for_promotion                        coordinator.py:2119-2148
```

Store: `src/pwg_ru_translated.jsonl` via [store_path.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py):111-119 (env → main-worktree → local, fail-closed). Live: 11,603 rows / 24.9 MB. Cost accounting is **three separate systems**: `call_reservation.py` (pre-spawn authority), `economy_ledger.py` (read-only pricing reducer), `run_observability.py` (append-only telemetry). `_watch.py`/`_supervise.py` are a **different** paid lane (DeepSeek corpus alignment), not this one.

## 3. Silent-failure census (execution lane)

Full sweep of `src/pilot/*.py` production files + 13 root scripts; selftest negative-assertion blocks excluded by design. Ranked; file:line verified. **S1 = money loss, S2 = store/artifact loss, S3 = accounting/observability.**

| # | Site | Class | What is lost when it fires |
|---|---|---|---|
| S1-1 | [max_account_orchestrator.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py):686-689 | swallowed except | **Duplicate paid window.** The `occupied` set (keys owned by pending/in-progress jobs) is built under `except (OSError, KeyError, JSONDecodeError): pass` — an unreadable manifest contributes zero keys, the overlap check at :781-784 passes, the same headwords are dispatched and billed again (plus a double-promote race). |
| S1-2 | same file :776-779 | swallowed except | Identical construct on the requeue import path — where manifests are most likely mid-write. |
| S1-3 | [workflow_payload.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/workflow_payload.py):104-108 | silent drop | **Row-level residual of the H2089 class.** The envelope now hard-fails, but a results row that is not a dict or has a falsy `key` hits `continue` and is counted in neither `keys` nor `nulls` — a paid card vanishes from every accounting surface; the window reads clean-and-complete. |
| S1-4 | [audit_window.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py):210-218 | swallowed except | `load_protected()` under bare `except Exception: pass` — a truncated batch file collapses the protected set to 3 hardcoded pilot keys (:63) and `quarantine()` at :221 then moves protected merged cards aside silently. |
| S1-5 | [translation_memory.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py):770-771, :862-863, :883-884 | swallowed except | Torn fragment-TM/denylist lines dropped with no counter — TM rows silently unavailable ⇒ re-translation at full price; on the denylist side a torn row silently re-enables reuse of gate-rejected content. The in-file docstring names this exact loss. |
| S1-6 | max_account_orchestrator.py:181-184 | unbounded wait | `coordinator_command` — the single funnel for dispatch/record-done/promote-ready — has no `timeout=`; a blocked coordinator hangs the orchestrator indefinitely **while holding the paid lease**. The only spawn in the file without a timeout. |
| S1-7 | [run_observability.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_observability.py):62-63 | torn append | `append_event` uses buffered text-mode `open(a)` instead of the O_APPEND single-`os.write` primitive built for exactly this; one torn line makes `read_events` raise ⇒ the window's cost census is unrecoverable. |
| S2-8 | [stage2_pregate.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/stage2_pregate.py):59 | hardcoded path | Only store consumer in the set that resolves neither `canonical_store()` nor `$PWG_RU_STORE` — run from a worktree it pre-gates the wrong store (read-side H255 class). |
| S2-9 | [window_common.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_common.py):140 | §262 `newline=` | `atomic_write_text` emits CRLF on Windows; `headless_worker.py:153-161` documents and routes around it, but `coordinator.py` (:1236, :1638, :1699 — sha-recorded clean outputs, :2417, :2505), `promotion_journal.py` (:405/:437/:679/:950) and `mao:157` still use it ⇒ two writers emit different bytes for identical payloads; every cross-writer sha comparison is platform-bound. Known, measured in-repo, still open. |
| S2-10 | window_common.py:75 | §262 + tear | `defer_monster` appends the cap-and-defer ledger via plain `open(a)` — not the atomic append primitive defined 8 lines below; its own comment says losing it "silently drops the most expensive entries". |
| S2-11 | [autosplit_requeue.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py):501-721 (6 sites) | non-atomic write | Requeue/top-up manifests — the record of which fragments were already paid for — written in place with unclosed handles; truncation ⇒ re-translating whole cards. Same class: [scale_route.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/scale_route.py):59 (cost-tier routing manifest), translation_memory.py:1200-1202 (`build_suggestions`). |
| S2-12 | [economy_ledger.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/economy_ledger.py):309-312 + run_observability.py:166-169 | no fsync | tmp+replace without fsync — the two files every other atomic writer in the lane fsyncs. |
| S2-13 | [promotion_receipt.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/promotion_receipt.py):232 | fixed tmp name | Non-unique `.tmp` (contrast `call_reservation.py:257` pid+uuid). Low likelihood, high blast radius — but see D8: not wired into the live lane. |
| S3-14 | [run_batch.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/run_batch.py):63-68, :90-93 | swallowed except | `pwg_src_commit: 'unknown'` on git hiccup (rows become un-targetable for later re-translation); torn store line ⇒ card re-translated and re-appended (duplicate rows + spend). Same shape on the primary lane: coordinator.py:790-793. |
| S3-15 | [scale_preflight.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/scale_preflight.py):233 | unconditional success | `coverage : OK` is a literal — printed with no computation behind it, beside two properly-conditioned verdict lines. |
| S3-16 | [failure_capture.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/failure_capture.py):57-66 + audit_window.py:466-472 | nested swallow | Two stacked `except: pass` between an error-level audit event and the failure gallery — an incident can vanish entirely. |
| S3-17 | [promote_lock.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py):113-121, :159-162 | swallowed OSError | A failed contender-restore destroys a live claim yet returns `False`; a failed release leaves a stale lock blocking promotion until TTL/`--steal-lock`. |
| S3-18 | `_supervise.py`:38, :51 + `_watch.py`:16-32 | unchecked exit + false success | (Adjacent DeepSeek lane.) Child exit never checked — a crash-looping build reads as "FINISHED"; `_watch` prints a dollar figure from a silently under-counted denominator. |

Positive findings worth keeping: subprocess exit codes are otherwise universally checked; `encoding='utf-8'` discipline is clean; there are **zero** direct network calls in the lane (all model calls via CLI subprocess with timeout + kill-tree); `headless_worker.call` (:604-669) finalizes the reservation even on `BaseException` — a crashed spawn can never look like a $0 call.

## 4. Phase 2b-A — execution-route parity

The H1110 fix **is wired**: enforcement in [execution_contract.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py):104-112 is reached from all four paid call sites (`headless_worker.py:1096`, `:1231`; `max_account_orchestrator.py:478`, `:1653`) and pinned by two selftests, one of which asserts refusal happens *before any runner call*.

| Finding | Anchor | Verdict |
|---|---|---|
| **F-1** Promote lane accepts any route string | [promote_final_cards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py):448-451 checks `isinstance(str)` + `.strip()` only — never compares to `claude-cli-headless` | H1110 class surviving in the one lane the fix didn't touch. One-line fix: compare to `execution_contract.HEADLESS_ROUTE`. |
| **F-2** `execute()` library path skips validation for v1 | headless_worker.py:1093 — `validate_profile` gated on `schema == SCHEMA_V2`; CLI requires `--allow-historical-v1`, library call doesn't | Low (v1 declares no route) but skips `config_dir_fingerprint` binding. |
| **F-3** Workflow JS generator still emits a runnable lane | autosplit_requeue.py:514-525, :599-606 ("RUN via Workflow tool") | Fail-closed at promote (no `execution` block ⇒ refused at promote_final_cards.py:444-446) — **no silent bypass**, but the retirement declared in `RUN_FREQ_MAX.md:160` is not enforced at the generator. |

## 5. Phase 2b-B — declared-vs-enforced budgets

Enforced correctly (verified at both declaration and enforcement sites): per-call timeout min(operator, manifest ceiling, 180 s hard); `max_calls` via durable reservation ledger (double-checked in supervisor); `cost_ceiling` fail-closed **when set**; `max_windows`/`max_clean`/`empty_streak`/`max_drain_iterations`; translate/heal/total agent ceilings pre-spawn; starvation refusal; preflight+manifest sha seals; probe ceiling (H2118) single-sourced at both gates; synthetic-control preflights refused for manifest execution (`headless_worker.py:129-131` — **not** a bypass).

The gaps:

| Finding | Anchor | Verdict |
|---|---|---|
| **F-B1** Cost/call ceilings are opt-in | `--max-calls` default `None` ([bounded_staged_run.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_staged_run.py):973), `--cost-ceiling` default `None` (:977); `cost_ceiling_evaluable` returns `(True, 'no cost ceiling requested')` when unset (:159-160); supervisor skips both checks on `None` | The fail-closed machinery is excellent and **inert unless the operator remembers two flags**. A billed run has no mandatory ceiling. |
| **F-B2** GO/NO-GO never consumed by code | `LIVE_GO` appears only in comments; `--execute` runs its own `probe_fleet` with no link to gate verdict or its age | The #729 staleness fix lives *inside* the probe; nothing stops a stale/absent verdict being carried to spend by a human. |
| **F-B3** Canary half of the gate is prose | policy ("3/3 senses + zero SAN-LOSS/TNMASK") lives in the `/pwg-live-gate` skill text; no `canary_gate.py`; inputs (`ru_coverage.py`, `sense_count.py`, `lang_parity_check.py`) all exist as code | Wiring, not research. Health half **is** mechanical ([probe_log.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py) `derive_fails`, pure function). |
| **F-B4** H2118 residuals | `verdict_for` default + CLI `--policy` default still `production_v1` (30 000) while `CURRENT_POLICY='production_v2'` (65 000); only boundary tests ride the stale 30 s default; stale docstring `mao:1267` | Fail-closed (mismatched receipts rejected) but the default lane produces receipts the dispatcher won't accept, and the **live 65 s ceiling has no boundary test**. |
| **F-B5** `translation_limit` state field decorative | declared coordinator.py:265/:284, echoed :2492; enforcement :683 reads the module constant | `preparation_limit` two lines away honors state — inconsistency, not convention. |
| **F-B6** USD ceilings trusted as a boolean | `per_card_ceiling_usd` $2.00 / `window_ceiling_usd` $25.00 declared+serialized ([perf_preflight.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/perf_preflight.py):71-108); consumers read only precomputed `over_ceiling` (`headless_worker.py:123-127`, `coordinator.py:1038-1043`) | Preflight is sha-sealed and coordinator-authored, so a weakness not an open door — but a preflight asserting `false` beside a $500 estimate passes. |
| **F-B7** Nine manifest budgets declared-only | `kill_gate` (except ceil), `max_wide`, `stagger_ms`, `sense_presplit_budget`, `selfheal_group_budget`, `output_budget`, `presplit_group_cite_budget`, `presplit_group_sense_cap`, `kill_switch`/factors — serialized into every manifest ([gen_opt_harness2.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py):1337-1376), read by nothing on the live headless route. Worse: [classify_run.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/classify_run.py):69 reads `budget_kill_switch_tripped`, a key the headless summary never writes ⇒ every run classified "not tripped" | H1110 predicted three of these; the set is larger, and only `timeout_ceil_ms` was repaired. Each is a limit an operator can set and watch do nothing. |
| **F-B8** `--wall-clock-minutes` is a metric labeled "Max" | audit_window.py:582-583 declared; [window_reports.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_reports.py):162-165 records, never compares | Matches Grok lane finding; H2089 spec #4 ("enforce or rename") not yet implemented. |

## 6. Phase 2b-C — data-at-rest invariants pre/post promote

Enforced and verified: promote lock genuinely acquired at every promote entry point (TOCTOU-safe reclaim); mandatory unique fsynced backup on the journaled path; mkstemp+fsync+durable_replace store writes; TNMASK/`{Tn}` residue refusal (field list from `card_fields.PROMOTED_PAIRS`); synthetic/canary-row refusal; manifest-v2 provenance schema; zero-row refusal; duplicate-sense refusal; partial-over-complete downgrade refusal; model-identity cross-check; batch hash lineage incl. backup fingerprint verify.

The gaps, ranked:

| Finding | Anchor | Verdict |
|---|---|---|
| **F-C1** Overlay wipe (FINDINGS §9) **still live**, two paths | (a) `merge_store_rows` ([promote_final_cards.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py):595-619) decides purely on `_attempt_quality`, never reads `review_status`/`reviewer`/`editorial_decision*`; :698-699 hardcodes `review_status`=arg, `reviewer: None`. (b) non-`--merge` supersede at :1916-1917 rebuilds the store from `wf_output` wholesale; the >50%-row guard is `--force`-bypassable (:1668-1671). | **The live store carries 3 `approved` + 2 `needs_review` rows — real human overlay, currently exposed.** A re-promote of those subcards returns them to `ai_translated`/`reviewer: None`. Latent for the editorial layer (0 `editorial_decision` rows so far), live for the 5. |
| **F-C2** 13 non-promote mutators bypass the lock | `annotate_*.py`, `fix_*.py`, `backfill_tn_residue.py`, `mark_reconstructed_headwords.py`, `ru_style_sweep.py`, `repair_h178_da_cards.py` — 0 acquire `PromoteClaim` | `PromoteClaim` guards a *path*, not the file: an annotate run concurrent with a promote is last-writer-wins. |
| **F-C3** Overlay writer itself unguarded | [apply_editorial_decisions.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/apply_editorial_decisions.py):240-245 — fixed tmp name, no lock, no backup, no fsync | The path that writes the human layer has none of the protections the machine layer gets. |
| **F-C4** Delta gate is row-count-only | :932-935, :1932-1941 count rows; **measured**: `h1809.bak` → live store are both 11,603 rows yet 26,198,939 → 24,904,391 bytes — **a 1.29 MB content change passed invisibly** | Rows + field-name sets identical; `ru`/`de` content moved only 149 bytes; points at JSON separator reformatting (store is mixed-format: 32 spaced / 11,566 compact rows) — but the writer that produced the compact rewrite was not identified, and byte-stability assumptions (`expected_after_sha256`) hold only within a single promote. **Needs its own investigation.** |
| **F-C5** Single-mode escapes | `--no-backup` allowed in single mode (:1667) and EN ([promote_en.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py):355); single mode lacks the exact-key-delta and hash-lineage checks of batch; batch lacks single's `refuse_defect_keys` (:1817-1827) | Each mode is missing one of the other's guards. |
| **F-C6** H2089 route-bypass refusal has 3 overrides | :1772-1786 — `--promotion-id` OR `--allow-raw-default-merge` OR `PWG_ALLOW_RAW_MERGE_DEFAULT_STORE=1` | Fix landed (PR #960); env-var override is invisible in command review. |

## 7. Phase 2b-D — side-effect + cost-gate census

Every side effect of a paid window: store write (gated, backed up, journaled — §6); card-TM rebuild (validate-then-atomic-replace, post-promote); fragment-TM extend (append-only, atomic); denylist unblock (membership re-checked on the coordinator path; deliberately fail-open in single mode); promotion journal (crash-recoverable phase machine); coordinator state/registry (DirLock + PromoteClaim, byte-stable replay); batch report, economy ledger, probe events, daily-close dashboard (all append-only or atomic); **git commits: none from code** (human/skill-driven — good). API billing: reservation ledger mandatory, but its cap is the same `None` as F-B1. TM destructive-rebuild from the 25-07 audit is **fixed** (`_atomic_replace_card_tm` validates then durable-replaces).

Money-risk ranking: **F-B1** (no mandatory ceiling) > **F-B2/F-B3** (gate not consumed by code / half-prose) > **S1-1** (duplicate window) > **F-B4** (untested live ceiling).

## 8. Dual-run comparison — Fable lane vs Grok 4.5 lane (per the override contract)

Grok lane: [PIPELINE_AUDIT_PWG_RU_01-08-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/PIPELINE_AUDIT_PWG_RU_01-08-2026.md) + gap handoff [H2089](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2089-Grok_SanskritLexicography_pwg-ru-silent-empty-route-bypass_01.08.26.md) (✅ executed, [PR #960](https://github.com/gasyoun/SanskritLexicography/pull/960) merged: workflow_payload envelope hard-fail, null failure-REASON, refuse-raw-default-merge).

| Grok claim | Class | Adjudication |
|---|---|---|
| Route parity headless enforced (`claude-cli-headless`) | **identical** | Confirmed at all 4 call sites + 2 selftest pins (§4). |
| Route parity Workflow JS — gap, no `validate_profile` | **conflicting** | Overstated as a live bypass: Workflow artifacts carry no `execution` block and are **refused at promote** (:444-446) — fail-closed, not silent. Residue kept: generator still emits the lane (F-3); H2089's refuse-raw-merge closed the real store-side door (F-C6). |
| Budgets max_calls/pools enforced on headless | **conflicting** | Enforced **when set** — both ceilings default `None` and the evaluability gate passes when unset (F-B1). The Grok row is true of the mechanism, wrong as an assurance. |
| Audit token/wall flags record-only | **identical** | Confirmed (F-B8). H2089 spec #4 not yet implemented — carried into gap list. |
| Promote journal enforced on coordinator path; direct `--merge` gap | **equivalent** | Confirmed; `--merge` gap since narrowed by PR #960 with 3 documented overrides (F-C6). |
| H2089 spec #5 "bind model id from CLI not hardcode" | **equivalent** | Open; `DEFAULT_GEN_MODEL_VERSION='claude-sonnet-5'` hardcoded (bounded_staged_run.py:94), exact-match enforced at promote — safe but still a constant. |
| — | **net-new (Fable)** | Overlay-wipe still live + 5 exposed rows (F-C1); 13 unlocked mutators (F-C2); unguarded overlay writer (F-C3); 1.29 MB silent store shrink (F-C4); duplicate-paid-window swallow (S1-1/2); workflow_payload row-level residual (S1-3); GO/NO-GO not consumed by code + canary prose-only (F-B2/3); skill-vs-code gate policy 30 s vs 65 s (D4); nine declared-only budgets + inert kill-switch read (F-B7); `translation_limit` decorative (F-B5); USD-boolean trust (F-B6); §262 residue in `atomic_write_text` (S2-9); 11 doc-vs-code drifts (§9). |

**Keep-best-of-both:** the Grok lane's five gap specs were correct and three are already shipped — nothing to re-do; its two open specs (#4, #5) are absorbed into the gap list below. Everything else above is Fable-lane net-new. No Grok finding is discarded.

## 9. Doc-vs-code drift (first-class findings)

| # | Doc says | Code says |
|---|---|---|
| D1 | [PIPELINE_ARCHITECTURE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md):28-37 — live path is the Max-Workflow route | Retired; production is headless CLI (E3). Doc predates H1110, the lease model, the supervisor, the journal, and `canonical_store` — essentially the whole current lane (header still 2026-06-28, D11). |
| D2 | same :307 — "Translation runner — TODO (no runner yet)" | The runner is the money path (`headless_worker.py`, 1255 lines). |
| D3 | same :300-306 — per-card Opus judge loop, Sonnet 4.6 | No per-card LLM judge; deterministic gates + sampled judge queue; pinned model `claude-sonnet-5`. |
| D4 | `/pwg-live-gate` skill :25 — "BOTH readings < 30 000 ms" | [h963_c4_gate0_probe.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h963_c4_gate0_probe.py):112-125 — 65 000 ms, **measured reading only**, warm-up advisory (MG ruling 31-07-2026). The skill states the reverted policy. |
| D5 | `/pwg-drain` :45 — "no `deferred_monsters.jsonl` on disk" | [window_common.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_common.py):45-80 defines and appends it as a deliberate ledger. |
| D6 | `/pwg-window-close` :70-72 — promote, then manually rebuild TM | Coordinator path rebuilds TM automatically under the held claim; the manual `--glob` CLI path does **not** — two promote routes with different TM side effects. |
| D7-D10 | `save_and_audit.py` capture; `promotion_receipt` as the durability layer; `gen_opt_harness.py` as canonical; operator-run preflight as the gate | All four superseded in code (worker `--output`; `promotion_journal`; `gen_opt_harness2.py`; coordinator-internal sealed preflight). |

## 10. Ranked gap specs (routed, not fixed here)

| # | Gap | Fix shape | Where |
|---|---|---|---|
| G1 | **Overlay-preserving merge** (F-C1) | `merge_store_rows` must read `review_status`/`reviewer`/`editorial_decision*` and either preserve-and-flag or refuse to replace a human-touched subcard without `--override-reviewed`; supersede mode must re-merge overlays or refuse when they exist | `promote_final_cards.py:595-619`, :1916-1917 |
| G2 | **Fail-closed occupied-guard** (S1-1/2) | An unreadable pending-job manifest must abort dispatch, not contribute zero keys | `max_account_orchestrator.py:686-689`, :776-779 |
| G3 | **Mandatory ceilings** (F-B1) | Require `--max-calls` and `--cost-ceiling` on `--execute` (or a manifest default), refuse `None` | `bounded_staged_run.py:973-977` |
| G4 | **Mechanical live-gate consumption** (F-B2/3) | `canary_gate.py` deriving the canary verdict from existing checkers + a GO receipt (with age) that `--execute` requires and validates | new file + `bounded_staged_run.py:840-889` |
| G5 | **Row-level payload accounting** (S1-3) | Non-dict/falsy-key rows counted as failures with synthetic REASON — completes H2089 at row granularity | `workflow_payload.py:104-108` |
| G6 | **Store-writer discipline** (F-C2/3) | All 13 mutators + `apply_editorial_decisions.py` acquire `PromoteClaim` and use the atomic backup writer (one shared helper) | 14 files |
| G7 | **Content-delta gate + shrink forensics** (F-C4) | Add byte/char-mass delta to the promote gate; separately, identify the writer that compacted the store (compare `h1809.bak` → live) | `promote_final_cards.py:932-935` + investigation |
| G8 | **Promote-lane route check** (F-1) | Compare `execution_route` to `HEADLESS_ROUTE` | `promote_final_cards.py:448-451` (one line) |
| G9 | **Skill/doc truth pass** (D1-D10) | Rewrite `PIPELINE_ARCHITECTURE.md` header block to point at the live lane; fix `/pwg-live-gate` policy text to 65 s measured-only; fix `/pwg-drain` D5; note dual TM semantics in `/pwg-window-close` | docs + 3 skills |
| G10 | Budget hygiene (F-B4/5/7/8) | Boundary test at 65 000; retire or enforce the nine dead manifest budgets; stop `classify_run` reading a never-written key; honor or drop `state['translation_limit']`; implement H2089 #4 (rename/enforce wall-clock) | several small |

## 11. Not audited

No runtime execution of any kind (no selftests, probes, dry-runs); paid model behavior, OAuth/billing identity, quota; `gen_opt_harness2.py` internals (2501 lines — largest unaudited surface) and the emitted JS template; `promotion_journal.py` internals (call sites only — `durable_replace`/`reconcile` assumed correct); `window_selftest.py` coverage mapping; `citation_tm.py`; cohort/live multi-profile scheduling; EN lane beyond promote parity reads; the DeepSeek corpus lane beyond classifying it as separate; whether the 3 `approved` store rows were ever actually re-promoted (backups on disk would answer it — part of G7).

---

_Dr. Mārcis Gasūns_
