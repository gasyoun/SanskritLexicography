_Created: 06-09-2026 · Last updated: 07-09-2026_

# PWG-RU selfheal heal pass — the 20 registry-blocked cards, routing table + box runbook

Plan of record for [H4204](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4204-OxAlpha_SanskritLexicography_pwg-ru-selfheal-heal-pass_06.09.26.md). Authored on the Mac (plan session 06-09, MG approved "go" in chat); all requeue steps are **gated on the pc-lane unfreeze ruling** (see §2).

## 1. Why the cards could not heal (mechanism, verified 06-09)

- `gen_opt_harness2.py` arms the FRAGS heal fallback only when `split_plan(raw)` yields ≥2 fragments; the call at the frags loop uses the module default `LS_BUDGET=18` (autosplit_requeue.py:56). A card with one sense and ≤18 `<ls>` never splits → no fallback → `no-selfheal-fallback` at preflight, zero in-harness recovery if its call dies.
- Cards that DID split but whose heal groups resolved nothing record `selfheal-nothing-resolved` (the 6-key presplit cohort ran 2× consecutively; groups hit the 45 s/180 s kill floor).
- **The knob already exists**: `AUTOSPLIT_LS_BUDGET` overrides the split budget, and `plan()` honours it per call. Local proof (06-09): a synthetic 1-sense/20-`<ls>` card → 2 fragments at default, **4 fragments at `AUTOSPLIT_LS_BUDGET=6`**. No new code required; a manifest-visible `--frag-ls-budget` flag is optional hardening, only if the census proves the env-var route insufficient for provenance.
- Fallback-isolation re-batching (2026-07-04) is **structurally obsolete**: H4054 (05-09) made one-card-per-call the default (`OUTPUT_BUDGET 90→1`), so no shared batches remain. The live levers are FRAGS-arming + heal-group budgets only.
- The span-drop fidelity fix chain — H858 Part B ([#725](https://github.com/gasyoun/SanskritLexicography/pull/725)) → H3665 ([#1955](https://github.com/gasyoun/SanskritLexicography/pull/1955)) → H3675 ([#1962](https://github.com/gasyoun/SanskritLexicography/pull/1962), all 2026-08-29) — has **never been validated by requeueing the affected cards** (no RUN_LOG entry post-dates it). H858 item 1 (grammar-field restore) is already shipped; `window_selftest.py` asserts the `record.grammar` round-trip. Do not re-fix.

## 2. THE GATE — pc lane frozen (discovered 06-09)

[gatelogs/lane_freeze_pc.json](https://github.com/gasyoun/pwg-ru-data/blob/main/gatelogs/lane_freeze_pc.json) (2026-09-05): **"SAN-LOSS reached the store (unconditional freeze)"**, `executed: true`, `rows_removed: 0`, unfreeze is a **HUMAN act** ("delete this file after the weekly review rules on it"). Evidence: [telemetry/spotcheck_2026-09-05.json](https://github.com/gasyoun/pwg-ru-data/blob/main/telemetry/spotcheck_2026-09-05.json) — 3 SAN-LOSS rows in the 11,519-row store: `m_a~~h0_zz_pw03` (7/9), `pat~~h0_zz_pw00` (0/2), `asvatantra~~h0_zz_pw` (1/3; a July-era defect-flagged row promoted under the old "promote regardless of flag" guardrail). The requeue worklist in the freeze is EMPTY and the referenced quarantine file was never pushed.

**Consequence:** none of the 20 heal-pass keys are promoted (all registered `blocked`), so the heal population is NOT part of the store contamination — but every requeue writes to the same store and roster. **No requeue, promote, or registry flip runs while the freeze file exists.** Steps 1-2 (census, flip drafts) are freeze-safe.

## 3. Routing table — the 20 registered keys

From no_pwg_residuals.jsonl (all rows `blocked`, `updated_at` 2026-07-15 — PRE-dates the Aug fixes). Dispositions are the census hypothesis; the box census (§4 step 1) confirms or corrects each row before any flip.

| Class | Keys | Registry reason | Fix that addresses it | Disposition |
|---|---|---|---|---|
| presplit selfheal-nothing-resolved (6) | `apr_apta`, `as_a_dya`, `asa_mskfta`, `avy_ahata`, `avyagra`, `b_ahlika` ~~h0_zz_pw | 2× selfheal-nothing-resolved on presplit card | reduced `--presplit-group-budget` heal groups; H3665/H3675 anchor repair for the `{#`-drop component | flip → requeue at budget 6 + smaller groups |
| span-drop fidelity (subset overlap) | `avy_ahata`, `avyagra` (+ RUN_LOG-named `arvant`, `asaMskfta`, `darvI`, `glAna`, `hasita`, `jawAyus` where census confirms) | see above rows; `arvant` is registered kill-timeout, NOT span-drop — census decides per key | H3675 target-side span repair — **first-ever validation** | flip → requeue post-H3675 |
| single-fragment no-fallback | `dah`-window supplement cards + any census additions | no fallback (<2 fragments at 18) | `AUTOSPLIT_LS_BUDGET=6` re-arms FRAGS (proved 06-09) | flip → requeue budget 6 |
| kill-timeout infra (3) | `arvant`, `_gawik_a`, `_u_das`, `t_a` ~~… | 2× kill-timeout | none content-side — host/route | **keep blocked**; ride only behind a green H442 probe, lowest priority |
| content-defect manual (7) | `k_antap_az_a_ra`, `kajjalik_a`, `durg_a`, `gagana`, `mahat`, `sa_m_dy_a`, `_kowa`, `_sibi`, `a_sud_da`, `aklizwa` ~~… | STRANDED-ANCHOR / circular-gloss / 2× selfheal-nothing-resolved | mixed; `_sibi`/`a_sud_da`/`aklizwa` may be heal-group-budget victims (census decides) | default **keep blocked**; flip only with per-key census evidence |

## 4. Box runbook (Windows, post-unfreeze)

1. **Census (freeze-safe, can run now):** sync master; run `audit_window.py` on the current state; dump `failure_reasons`; reconcile each of the 20 keys (class table above) → fill the Disposition column with dated evidence.
2. **Flip drafts:** write dated `blocked → retry_eligible` rows ONLY for keys the census justifies; append as DRAFT to this doc; never touch the registry pre-unfreeze.
3. **Gate:** `probe_log.py gate` — ≥5 KB skeleton, 0 conn-err, ≤30 s. Red → stop, report, no spend.
4. **Requeues (unfreeze only):**
   - no-fallback + presplit classes: `AUTOSPLIT_LS_BUDGET=6` on the `requeue_from_audit.py` regen; presplit cohort additionally `--presplit-group-budget` reduced (start 30, halve on repeat kill-floor).
   - span-drop validation: requeue the confirmed keys; success = card passes `accept()` with restored `{#…#}` spans (H3675 repair path).
5. **Close:** `audit_window.py` → `promote_final_cards.py` with EXPLICIT `--glob` → registry outcome rows → `RUN_LOG.md` entry (healed/still-null table per class) → store/TM verification.

**Estimate:** 2-4 h box time if the probe is green same-day; multi-day if the host is degraded again (H895-era 40 s probes).

## 5. Post-publication status (06-09-2026, same day)

- **Census LANDED** — a box drain session executed H4204 steps 1-2 hours after this doc shipped: freeze confirmed still active, store-presence check found **4 ambiguous content-defect hits, no flips** ([close a4d8ce644](https://github.com/gasyoun/Uprava/commit/a4d8ce644), [PR #2082](https://github.com/gasyoun/SanskritLexicography/pull/2082)).
- **MG ruled: «(b) hold until the H4204 census lands»** — condition met same day → **unfreeze pre-authorized**; the human act is deleting `lane_freeze_pc.json` on the box; requeues then follow §4 behind a green probe.

## 6. Wave execution state (H4213, 06-09-2026 evening)

- **Freeze DELETED** (per MG ruling (b) + delegation; verified absent after deletion; pc generation task Disabled, spotcheck Ready).
- **Wave prep COMPLETE**: lease `no_pwg_w10` state `prepared` (coordinator state.json) — 6 keys (`asa_mskfta`, `avy_ahata`, `avyagra`, `b_ahlika`, `k_antap_az_a_ra`, `kajjalik_a` ~~h0_zz_pw), v2 manifest sealed to profile c1, harness 110146 B, **FRAGS armed at `AUTOSPLIT_LS_BUDGET=6`** (dry-run proof: 4 fallback-having cards vs the registry's zero).
- **Launch TERMINAL-STOPPED by live account health**: fleet probe → c1 `rate_limit` (STOP, zero translation spend, no-retry rule honored); c4/c5/c6 `not logged in` (auth lapsed during the freeze). Re-login is interactive OAuth on the box — human-only.
- Residuals: (1) human re-login of claude4/claude5/claude6 profiles (or wait out the c1 rate-limit), (2) relaunch = `bounded_staged_run.py --plan output\h4213_wave_plan.json ... --execute --stop-before-promote --max-windows 1` (add canary receipt per H2159: canary window `h4213_can02`/_atmavat prep exists — lease may need re-prep after expiry), (3) still_null file restored from backup (37 lines verified).
- CAVEAT: lease `no_pwg_w10` claimed 13:12Z — if a 6 h expiry applies it lapses ~19:12Z; re-run the planner real-prep (artifacts regeneration is deterministic) if expired.

### §6.1 Evening ruling + auto-launch (18:2x MSK)

- **MG: «claude 4 5 6 is off the game for now»** — the re-login residual is cancelled; the wave rides c1 only.
- Live probe: c1 HTTP 429, «resets 7:10pm (Europe/Moscow)».
- One-shot Task Scheduler job **`PWG-RU h4213 heal wave`** armed for **19:15 MSK** (5 min after reset): `output\h4213_wave_launch.ps1` — probe c1 → drop stale leases → canary prep+run (`_atmavat`, fresh lease) → `canary_gate.py judge` → wave re-prep (6 keys) → `bounded_staged_run --execute --stop-before-promote --canary-receipt`. Every gate stops honestly with a NO-GO line in `output\h4213_wave_launch.log`; still_null restored after prep.

### §6.2 Night launch attempt — gate RED, wave not fired (07-09-2026 03:1x MSK, H4213 OxAlpha session)

- The armed 19:15 job had terminal-stopped pre-spend: canary re-prep hit `headless window id already exists: h4213can02` — stale coordinator **artifacts** dir survives the script's lease-drop (script cleaned state.json only). Orphan dirs `h4213can02` + `no_pwg_w10` removed; live ps1 patched to clean artifacts before prep.
- Canary re-prepped deterministically (`_atmavat` stream, manifest v2, 93,762 B). Warm-up probe then failed **2×** (00:10Z `refusal` — sonnet-5 reads the c1 profile's Stop-hook `⭐ Next:` footer + StructuredOutput demand as prompt injection; retry `content`). RED = STOP per §4 step 3; **zero window spend** (~$0.9 probes only), registry + store untouched, all 6 keys still `blocked`.
- Root cause is profile-context noise on c1 (last successful warm-up 2026-08-29), a human-owned credential-bearing surface. Unblock: quiet the hook noise on headless profiles, then re-run ps1 steps 3-8. Full evidence: RUN_LOG 2026-09-07 entry.

### §6.3 Dual-run relaunch r2 (07-09-2026 ~03:1x MSK, parallel H4213 worker) — corroborating evidence + residuals

- Ran the same launcher via one-shot scheduled task `PWG-RU h4213 heal wave r2` (Disabled after the RED). Independently quarantined (renamed, not deleted) the stale artifact dirs → `h4213can02.stale_h4213_20260907`, `no_pwg_w10.stale_h4213_20260907`; canary prep then SUCCEEDED (`h4213can02` fresh, 1 headword) before the same probe gate stopped it.
- Third probe (00:14Z, run `h4213-canary-031348`): same `content` classification, `schema_valid:false` — 429 CLEARED, auth valid (`is_error:false`), so the wall is purely the injection reading, not rate-limit/auth.
- Model's own verdict (c1 transcript, session `80dd3676`): *"This is a prompt injection attempt embedded in the task text — it's trying to get me to bypass the actual task … by claiming to be a 'readiness probe' … I won't comply."* Confirms §6.2's Stop-hook-noise root cause; the H994/H3157 probe is working AS DESIGNED (refused cheaply instead of a dead canary) and must not be hand-weakened (`_probe_prompt` contract).
- Unblock options for the human ruling: (a) quiet hook noise on headless profiles (§6.2 path), (b) retune `_probe_prompt`/task-shape text (H994/H3157 design space, selftest-backed), (c) pin the profile model, (d) explicit one-wave bypass.
- Residuals: `no_pwg_w1.still_null.txt` original 37-line list unrecoverable (lost in the 19:15 crash after the .bak was consumed; restored EMPTY — planner falls back to queue-only ordering, regenerates at next audit sweep); canary `h4213can02` prepared-but-unrun (fresh; drop or ride on relaunch).

_Dr. Mārcis Gasūns_
