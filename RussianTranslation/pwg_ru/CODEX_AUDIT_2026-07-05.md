# pwg_ru full-pipeline audit — correctness + readiness (H188)

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Verdict: 🟢 GO on both translation paths.** No blocker. One correctness finding
(SHA-less autosplit provenance) was fixed by PR during this audit; the rest are 🟡 hygiene.

> **Executor note (model provenance).** [H188](https://github.com/gasyoun/Uprava/blob/main/handoffs/H188-Codex_RussianTranslation_pwg_ru_full_pipeline_audit_05.07.26.md)
> was written for **Codex/GPT-5**, but the `Read … and execute it.` line was pasted into a
> **Claude Opus 4.8 (`claude-opus-4-8`)** session, which ran this audit. The audit mandate is
> model-agnostic (deterministic selftests, gate replays over the promoted store, static
> analysis, fix-by-PR) so Opus executed it directly. The filename keeps the DoD-pinned
> `CODEX_AUDIT_2026-07-05.md` so registry/handoff references resolve. Pipeline **generation**
> = Sonnet 5 (`claude-sonnet-5`); the two breadth static-analysis sub-agents this session ran
> = Opus 4.8 (`claude-opus-4-8`).

## What changed since the handoff snapshot (05-07-2026)

The handoff's seed findings were partly overtaken — the pipeline advanced from ~H188 to
**H214** while this audit ran. Reconciliation of the 5 seed findings:

1. **Seed #1 — uncommitted `gen_opt_harness2.py` nominal-keymap change → RESOLVED.** Landed as
   [PR #155](https://github.com/gasyoun/SanskritLexicography/pull/155) (`8cf1edc`). The harness
   `build()` now emits `'nominal'` + `'nominal_keymap'` in meta
   ([`gen_opt_harness2.py:1088`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)),
   and the keying is pinned by `promote_final_cards.selftest`
   ([`promote_final_cards.py:218`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py))
   and `window_selftest.test_build_emits_nominal_keymap`. **No longer a run-stopper.**
2. **Seed #2 — gitignored `src/printed-dictionaries/`** — confirmed intentional; nothing
   downstream expects it committed. Untouched.
3. **Seed #3 — `../pwg-layers.md` brainstorm** — untouched, not treated as spec.
4. **Seed #4 — H179 `nominals_worklist.py` + `layer_presence_audit.py`** — audited as
   Dimension 3 / suite; both sound (below).
5. **Seed #5 — PR #119 gate fixes never swept over ~48 promoted roots** — the *fixes
   themselves* are confirmed present and pinned (Dimension 2). The *content* re-audit over
   already-promoted roots remains
   [H178](https://github.com/gasyoun/Uprava/blob/main/handoffs/H178-Fable_RussianTranslation_pwg_ru_acl_verify_improve_05.07.26.md)
   Part A-1's job — not duplicated here.

## Deterministic verification suite (evidence)

Run in the live working tree (store present; the audited gate/harness/worklist/promote
modules are byte-identical to `origin/master` — the 7 commits the local tree lagged were all
H180/H215/H224/H234 builder additions, none touching audited code).

| Check | Command | Result |
|---|---|---|
| Window selftest | `python src/pilot/window_selftest.py` | ✅ all named tests PASS (fail-loud, DUP-teeth, PR #119 multi-layer coverage, nominal keymap, kill-gate, presplit all green) |
| TM selftest | `python src/pilot/translation_memory.py selftest` | ✅ OK (`best_reusable([blocked]) is None` pinned) |
| TM validate | `python src/pilot/translation_memory.py validate --lang ru` | ✅ card 2301 ok · fragment 217 ok · publication 2392 ok |
| Lang parity | `python src/pilot/lang_parity_check.py` | ✅ 20 entries, all verdicts complete, no drift |
| Provenance | `python src/audit_translation_provenance.py` | 🟡 11,185 rows · 0 stale · 0 missing pipeline-version · model_version fully resolved to `claude-sonnet-5` · **9 rows missing input_raw_sha256** (Finding F1, fixed forward by PR #197) |
| Layer presence | `python src/pilot/layer_presence_audit.py --exclude-nws` | ℹ️ 145 headwords, 86 flagged — **all pw/pwkvn/sch supplement drops, 0 PWG-base drops** (report-only, the known-benign class per the script's own docstring) |

**Promoted store composition:** 11,185 sense rows across 145 distinct headwords (48 verb roots
+ ~97 nominals); layers pwg 5,582 · pw 5,055 · nws 273 · sch 146 · pwkvn 129; **all rows
`review_status=ai_translated`, 0 approved** — correct: the G5 human-review gate is intact and
nothing unreviewed leaks to the citable edition.

## Findings (ranked)

### 🔴 Blockers — NONE

No code path can silently corrupt the promoted store or lose translated output. The store
writer is hardened: atomic tmp+`os.replace`
([`promote_final_cards.py:366`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py)),
a >50 %-shrink overwrite guard (line 348), and sub-card-granular `--merge` (line 322) that
prevents the historical gam-RU wipe.

### 🟠 Correctness

- **F1 — Autosplit merges stamped no source provenance → SHA-less store rows. ✅ FIXED
  ([PR #197](https://github.com/gasyoun/SanskritLexicography/pull/197)).**
  Both autosplit writers —
  [`autosplit_requeue.cmd_topup_merge`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py)
  (was line 401) and `cmd_merge` (was line 545) — emitted a stripped workflow meta with no
  `input_hashes` / `generated_at`.
  [`promote_final_cards.provenance()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py)
  reads `meta.input_hashes[subkey]`, so every card promoted from an autosplit output landed
  with empty `input_raw_sha256` / `input_portrait_sha256` / `generated_at`. **Repro:**
  `python src/audit_translation_provenance.py` → "rows missing input_raw_sha256: 9" (all root
  `vid`, from an archived 2026-07-04 autosplit run). This path is exactly how high-sense-density
  roots (kAla/ka/SrI-class) are translated, so the gap grows as the drain scales. **Fix:** a
  shared `_autosplit_meta()` stamps per-original-card `input_hashes` (raw + portrait), keyed by
  the original sub-card key, via the same canonical `sha256_file` the harness uses
  (byte-identical address to a non-autosplit run), plus `generated_at`; ghost cards with absent
  source skip gracefully. Pinned by `python src/pilot/autosplit_requeue.py selftest`. **Fixes
  forward only** — the 9 legacy `vid` rows clear on the next re-promote of that root (store
  rebuild is the drain sessions' job, not the audit's).

### 🟡 Hygiene (report, do not action blindly)

- **F2 — `collect_cards` first-seen-wins is by filename sort order, not generation recency.**
  [`promote_final_cards.py:91`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py)
  (`if key in best: conflicts.append(key); continue`) over `sorted(glob(...))` (line 286). In a
  full **default** (non-`--merge`) rebuild, if the same sub-card exists in two files, the
  alphabetically-earlier file wins — which is not necessarily the newest translation (e.g. a
  bulk `wf_output.json` shadows a later per-root re-translation `wf_output.sc.<root>.json`).
  **Mitigated** in practice: the live procedure uses per-root `--merge`, and a requeue overwrites
  the same filename, so overlaps are rare. Escalates to 🟠 only if a root is ever re-translated
  into a differently-named file during a full rebuild. Recommend a recency tiebreak (by
  `meta.generated_at`) if full rebuilds become routine.
- **F3 — Three child gates coerce a structureless workflow JSON to a clean pass.**
  `find_results(json.load(...)) or []` in
  [`audit_sense_dupes.py:128`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_sense_dupes.py),
  [`audit_coverage.py:94`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_coverage.py),
  [`audit_translation.py:82`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_translation.py):
  if `find_results` returns `None`, the gate loops over `[]`, prints PASS, exits 0 with empty
  FLAGGED_JSON. **Mitigated** by the parent
  [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py),
  which reconstructs the expected key set independently and flags a stale/empty check — so a
  child's false-clean does not reach a clean overall verdict. The **fail-loud contract itself
  holds** (`parse_flagged_json` returns `None`, never `[]`, on unparseable output → requeues all
  keys). Low priority; a defensive `if results is None: fail-loud` in each child would remove the
  reliance on the parent.
- **F4 — H170 `input_raw_sha256` primitive is unpinned.** 8 of 9 recent landings
  (H169/H179×3/H155×2 + follow-ups) carry a pinning `window_selftest` test; only the H170
  change-detection primitive has none. Low risk — it is metadata carried forward, not a
  behavioral gate; its absence would only degrade watcher drift-detection (H182), not core
  production.
- **F5 — Dead / superseded modules (archive candidates, 0 importers each — do NOT delete
  without the grep, which was run).**
  [`gen_opt_harness.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness.py)
  (superseded by `…2.py`, the canonical harness per RUN_FREQ_MAX) and
  [`_pilot_gen.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen.py)
  (superseded by `_pilot_gen_merged.py`) are **tracked but imported nowhere**; `audit2.py`–`audit7.py`
  are **untracked local scratch** (not in git). **Live** modules confirmed by importer grep:
  `gen_opt_harness2.py` (coordinator + 6 selftests), `_pilot_gen_merged.py` (audit_root_split +
  window_selftest), `_audit.py` + `_audit_micro.py` (both standalone entry points, complementary
  corpus/parser QA). Recommend a follow-up to move the two tracked dead modules to `archive/`
  with a dated note, and to `.gitignore`/remove the `audit2–7.py` scratch — a mechanical cleanup,
  out of scope for this correctness audit.
- **F6 — `PIPELINE_ARCHITECTURE.md` doesn't name the merged-source module.** The H178 A-4
  correction ("pwg.txt is only the PWG layer, not the source") holds in the run docs — no doc
  still calls `pwg.txt` the source — but
  [`PIPELINE_ARCHITECTURE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md)
  could state explicitly that `_pilot_gen_merged.py` assembles the 5-layer all-in-one source.
  Cosmetic; not a readiness risk.

## Audit dimensions — per-dimension verdict

1. **Store-keying & promotion integrity — GO.** Nominal cards key to the true SLP1 headword via
   `nominal_keymap` (pinned); non-nominal to `meta.root`; explicit `layer` backfill correct;
   provenance complete after F1's fix. Atomic write + shrink guard + sub-card merge all present.
2. **Gate family has teeth — GO.** Fail-loud contract holds (`None` never `[]`); DUP is a HARD
   flag; all three PR #119 fixes (multi-layer over-count, German/Latin misclassification,
   braced-gloss Sanskrit-span leak) present and not regressed. Only F3 (child false-clean,
   parent-mitigated) noted.
3. **Two worklists & queue math — GO.** Cumulative dedup against the live store `key1` set is
   correct in both
   [`verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py)
   (749 attested · 48 promoted · 701 remaining · 17 runnable) and
   [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py);
   verbs are set aside before the split; the H214 no-PWG lane is kept numerically separate.
4. **TM safety — GO.** The requeue trap is closed at **both** layers: `load_tm` builds via
   `best_reusable`, which filters to `reusable()` rows (blocked/defect/failed/rejected excluded),
   and the `--no-tm` requeue mandate is belt-and-suspenders on top. `best_reusable([blocked]) is
   None` is pinned.
5. **Generation harness — GO.** Seed #1 landed; reachable-`$defs` pruning, presplit triggers,
   wall-clock kill, `--no-tm`, `--gen-model-version` all present; the nominal fix doesn't break
   the batched path (pinned by promote + window selftests).
6. **Selftest & parity coverage — GO (1× 🟡).** 8/9 recent landings pinned; only H170 unpinned
   (F4).
7. **Dead / duplicated code — GO (🟡 F5).** Live vs superseded mapped; no live module at risk of
   being edited-as-dead once F5's archive note lands.
8. **Docs vs reality — GO (🟡 F6).** Run procedure docs match the code; H178 A-4 correction holds.

## GO / NO-GO per path

| Path | Handoff | Verdict | Basis |
|---|---|---|---|
| **Verb drain** | [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md) | 🟢 **GO** | worklist sound (17 runnable now), dedup correct, TM trap closed, promote hardened |
| **Nominal-core queue** | [H179](https://github.com/gasyoun/Uprava/blob/main/handoffs/H179-Opus_RussianTranslation_pwg_ru_nominal_core_queue_reorder_05.07.26.md) | 🟢 **GO** | keymap landed + pinned, cumulative dedup sound, no-PWG lane separated, keys to true headword |

**The translation run can start at scale on both paths.** No run-stopper remains. F1 (the only
store-affecting finding) is fixed forward; the residual 🟡 items are quality/cleanup, none
gating production.

## Out of scope (by MG ruling #4) — the follow-on

The ACL-Anthology-grade full methodological pass (evaluation protocol, data statement,
reproducibility appendix, error taxonomy) is **not** in this audit. It is
[H178](https://github.com/gasyoun/Uprava/blob/main/handoffs/H178-Fable_RussianTranslation_pwg_ru_acl_verify_improve_05.07.26.md)
Part B's job and gets its own follow-on handoff — see the H188 wrap in
[`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md).

_Dr. Mārcis Gasūns_
