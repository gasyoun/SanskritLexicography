_Created: 06-09-2026 · Last updated: 06-09-2026 (§5 box census)_

# PWG-RU selfheal heal pass — the 20 registry-blocked cards, routing table + box runbook

Plan of record for [H4204](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4204-OxAlpha_SanskritLexicography_pwg-ru-selfheal-heal-pass_06.09.26.md). Authored on the Mac (plan session 06-09, MG approved "go" in chat); all requeue steps are **gated on the pc-lane unfreeze ruling** (see §2).

## 1. Why the cards could not heal (mechanism, verified 06-09)

- `gen_opt_harness2.py` arms the FRAGS heal fallback only when `split_plan(raw)` yields ≥2 fragments; the call at the frags loop uses the module default `LS_BUDGET=18` ([autosplit_requeue.py:56](../../src/pilot/autosplit_requeue.py)). A card with one sense and ≤18 `<ls>` never splits → no fallback → `no-selfheal-fallback` at preflight, zero in-harness recovery if its call dies.
- Cards that DID split but whose heal groups resolved nothing record `selfheal-nothing-resolved` (the 6-key presplit cohort ran 2× consecutively; groups hit the 45 s/180 s kill floor).
- **The knob already exists**: `AUTOSPLIT_LS_BUDGET` overrides the split budget, and `plan()` honours it per call. Local proof (06-09): a synthetic 1-sense/20-`<ls>` card → 2 fragments at default, **4 fragments at `AUTOSPLIT_LS_BUDGET=6`**. No new code required; a manifest-visible `--frag-ls-budget` flag is optional hardening, only if the census proves the env-var route insufficient for provenance.
- Fallback-isolation re-batching (2026-07-04) is **structurally obsolete**: H4054 (05-09) made one-card-per-call the default (`OUTPUT_BUDGET 90→1`), so no shared batches remain. The live levers are FRAGS-arming + heal-group budgets only.
- The span-drop fidelity fix chain — H858 Part B ([#725](https://github.com/gasyoun/SanskritLexicography/pull/725)) → H3665 ([#1955](https://github.com/gasyoun/SanskritLexicography/pull/1955)) → H3675 ([#1962](https://github.com/gasyoun/SanskritLexicography/pull/1962), all 2026-08-29) — has **never been validated by requeueing the affected cards** (no RUN_LOG entry post-dates it). H858 item 1 (grammar-field restore) is already shipped; `window_selftest.py` asserts the `record.grammar` round-trip. Do not re-fix.

## 2. THE GATE — pc lane frozen (discovered 06-09)

[gatelogs/lane_freeze_pc.json](https://github.com/gasyoun/pwg-ru-data/blob/main/gatelogs/lane_freeze_pc.json) (2026-09-05): **"SAN-LOSS reached the store (unconditional freeze)"**, `executed: true`, `rows_removed: 0`, unfreeze is a **HUMAN act** ("delete this file after the weekly review rules on it"). Evidence: [telemetry/spotcheck_2026-09-05.json](https://github.com/gasyoun/pwg-ru-data/blob/main/telemetry/spotcheck_2026-09-05.json) — 3 SAN-LOSS rows in the 11,519-row store: `m_a~~h0_zz_pw03` (7/9), `pat~~h0_zz_pw00` (0/2), `asvatantra~~h0_zz_pw` (1/3; a July-era defect-flagged row promoted under the old "promote regardless of flag" guardrail). The requeue worklist in the freeze is EMPTY and the referenced quarantine file was never pushed.

**Consequence:** none of the 20 heal-pass keys are promoted (all registered `blocked`), so the heal population is NOT part of the store contamination — but every requeue writes to the same store and roster. **No requeue, promote, or registry flip runs while the freeze file exists.** Steps 1-2 (census, flip drafts) are freeze-safe.

## 3. Routing table — the 20 registered keys

From [no_pwg_residuals.jsonl](https://github.com/gasyoun/pwg-ru-data/blob/main/gatelogs/no_pwg_residuals.jsonl) (all rows `blocked`, `updated_at` 2026-07-15 — PRE-dates the Aug fixes). Dispositions are the census hypothesis; the box census (§4 step 1) confirms or corrects each row before any flip.

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

## 5. Box census (Windows, 06-09-2026) — steps 1-2 executed, freeze confirmed still active

**Freeze re-checked:** [gatelogs/lane_freeze_pc.json](https://github.com/gasyoun/pwg-ru-data/blob/main/gatelogs/lane_freeze_pc.json) still exists (`executed: true`); an unrelated automated recheck re-stamped it today (2026-09-06, same reasons) as an in-flight uncommitted change in the `pwg-ru-data` main checkout — not touched by this pass, out of scope for H4204 and not this session's WIP to commit. **No requeue, promote, or registry flip executed** (steps 3-4 stay gated).

**`audit_window.py` could not run as literally specced:** it audits one `wf_output` file against an `--execution-manifest` contract from a live Max-Workflow/headless run; this worktree's `RussianTranslation/src/pilot/output/` is empty (gitignored, local-only per [[pwg-ru-store-worktree-persistence]]) and the main checkout's `output/` holds only already-merged `.merged.md` cards, not a fresh unaudited `wf_output`. No window is currently in flight to audit. This is a genuine constraint, not a skipped step — recorded so a later session doesn't re-attempt the identical call.

**Substitute census run:** [`h4204_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h4204_census.py) (read-only, touches neither registry nor store) reconciles the 20 `no_pwg_residuals.jsonl` keys against `pwg-ru-data/tm/pwg_ru_translated.jsonl` by `(root, dict_code)` presence — a weaker signal than a `failure_reasons` audit (it does not confirm the specific flagged sense healed, only that *some* entry for that root+dictionary now exists in the store):

| Key | Registry reason | Root+dict present in store? |
|---|---|---|
| `durg_a~~h0_zz_sch` | likely_circular_gloss | **yes** |
| `gagana~~h0_zz_nws00` | STRANDED-ANCHOR/circular-gloss | **yes** |
| `mahat~~h0_zz_pw` | content defect (circular-gloss/STRANDED-ANCHOR) | **yes** |
| `sa_m_dy_a~~h0_zz_sch` | content defect (circular-gloss/STRANDED-ANCHOR) | **yes** |
| remaining 16 keys (presplit, span-drop, no-fallback, kill-timeout, `k_antap_az_a_ra`, `kajjalik_a`, `_kowa`, `_sibi`, `a_sud_da`, `aklizwa`) | see §3 | no |

**Disposition — no flip drafted from this signal alone.** The 4 "present" hits are all in the §3 "content-defect manual" class, whose registry reason is a **quality** flaw (circular gloss / stranded anchor), not a missing-fallback mechanism the Aug/Sep fixes address — store presence there is ambiguous (could be the flagged defective content itself, promoted under the pre-H3593 "promote regardless of flag" guardrail the freeze doc footnotes) and is exactly the SAN-LOSS shape the pc-lane freeze exists to catch. Flipping on ambiguous evidence is the explicit fail condition in Acceptance. **Recommendation:** the 4 hits get a manual content spot-check (not a mechanical flip) once the freeze lifts and `audit_window.py` can run against a real window; §3's per-class dispositions stand unchanged otherwise. The other 16 keys show no store presence at all, consistent with §3's blocked classes.

**Steps 3-4 remain fully gated** — `lane_freeze_pc.json` still exists; no human unfreeze ruling has landed. This closes H4204's ungated scope (steps 1-2); the requeue windows in §4 wait on that ruling.

_Dr. Mārcis Gasūns_
