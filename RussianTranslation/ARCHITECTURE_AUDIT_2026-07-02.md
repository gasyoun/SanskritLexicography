# Architecture audit — pwg translation pipeline (Fable window S10)

_Created: 02-07-2026 · Last updated: 02-07-2026_

**Mission:** M.G. reported the pwg pipeline "failed too often" over the last week — big/dense
cards not translated even after many retries. A same-day Sonnet 5 (`claude-sonnet-5`) session
fixed 4 layered bugs ([PR #35](https://github.com/gasyoun/SanskritLexicography/pull/35),
[#37](https://github.com/gasyoun/SanskritLexicography/pull/37),
[#38](https://github.com/gasyoun/SanskritLexicography/pull/38),
[#40](https://github.com/gasyoun/SanskritLexicography/pull/40)). This audit read the whole
pipeline with fresh eyes, mined the week's actual run artifacts, and answers: is the
retry/heal design structurally sound now, and is "a big card never silently disappears"
true by construction?

**Analysis model:** Fable 5 (`claude-fable-5`), including the three parallel audit
subagents (failure-history mining, peripheral-module map, dead-code sweep — all inherited
`claude-fable-5`). Live-validation generation: the harness-pinned `sonnet` alias (see
[FABLE_S10_RUN_NOTE](#live-validation) below for the resolved version of the run).

---

## 1. The verdict, up front

**"Fails too often" was at least FIVE different diseases wearing one symptom.** The week's
failures decompose into ten modes (§4); the 4 merged PRs cover exactly one of them (the
citation-dense retry-cap class, plus its batch-poison sub-mode). The systemic root defect
spanning most of the rest: **every failure path collapsed to an undifferentiated
`card: null` — or a silently absent key — with the cause discarded.** A rate-limit collapse,
a deterministic fidelity reject, a model omission, and a hard crash were indistinguishable
in the artifacts, so every one of them read as "translation failed, retry" — and some of
them are retry-resistant by construction.

**Status after this audit: PARTIALLY CLOSED.**

- **Closed by construction** (this session's PRs [#63](https://github.com/gasyoun/SanskritLexicography/pull/63),
  [#64](https://github.com/gasyoun/SanskritLexicography/pull/64),
  [#65](https://github.com/gasyoun/SanskritLexicography/pull/65),
  [#66](https://github.com/gasyoun/SanskritLexicography/pull/66),
  [#67](https://github.com/gasyoun/SanskritLexicography/pull/67)): silent key loss
  (total-accounting invariant), cause erasure (failure ledger end-to-end from harness to
  audit report), unchecked heal fragments, all-or-nothing heal groups, partial cards
  invisible downstream, EN files shadowing RU promotion, the autosplit manifest race,
  fully-failed autosplit cards leaving no requeue trail.
- **Open, needs its own session** (named in §6): the dense-residual re-run through the fixed
  stack; the `prompt_rule_audit.has_text_signal()` false-positive requeue churn (Mode 6,
  OPEN since 2026-06-29); the EN store layer re-run (`promote_en.py`, open since S7); the
  flagged-not-fixed peripheral sites in §5.

---

## 2. The real call graph — "root in → translated card or diagnosable failure out"

What the code actually does (docs cross-checked; [`PIPELINE_ARCHITECTURE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md)
described the ~06-15 state and now carries a staleness banner; `AGENTS.md` described the
loop correctly but hardcoded a weeks-stale queue — both fixed in
[#67](https://github.com/gasyoun/SanskritLexicography/pull/67)):

```
rootmap + per-subcard raw/portrait               src/pilot/input/ (gitignored, local-only)
        │
        ▼
gen_opt_harness2.py  ── imports ──  pwg_mask (mask/restore), autosplit_requeue.plan
        │                            (selfheal fragment precompute), whitney_grammar /
        │                            nominal_grammar (evidence blocks), safe_filename
        │  parses CONV/TR prompt out of run_pilot_wf.js (template is LOAD-BEARING)
        ▼
run_pilot_wf.<tag>.js  (self-contained Workflow script; inputs INLINED)
        │  run via the Workflow tool
        │  translateBatch ─ resolveGroup (2 attempts, key1-matched accept(),
        │        │           optional --binary-split bisection)
        │        └─ selfHeal per still-failing card ─ healGroup per fragment group
        │              (3 attempts + bisection, per-fragment {Tn} fidelity, partial credit)
        ▼
task output ──► save_and_audit.py <root> <file> <tag>   → wf_output.<tag>.<root>.json
        │            (overwrite guard, --merge; drops null thunk slots — now a no-op
        │             because the harness accounts every key itself)
        ▼
audit_window.py (RU) / audit_window_en.py (EN, report-only — see §5 flag F6)
        │  stale_check (window_provenance) · collect (_pilot_collect) · gates:
        │  nws_split, audit_translation, audit_coverage, audit_sense_dupes,
        │  prompt_rule_audit · window_reports writes report/status/requeue files
        │  → requeue.keys.txt (+ .transient/.defect) → requeue_from_audit.py → regen
        ▼
promote_final_cards.py --merge   → src/pwg_ru_translated.jsonl   (gitignored, SINGLE-COPY)
promote_en.py                    → attaches en + en_provenance onto the same store
        ▼
export_interop.py  (approved_store() gate: only G5-reviewed rows export — unchanged)
```

Standalone recovery lane: `autosplit_requeue.py gen/merge` (fragments as pseudo-cards,
`--budget=1`) — same plan() as the inline selfheal, different merge bookkeeping; the
duplication map is in §7.

---

## 3. Silent-failure sites — found, and what happened to each

The pattern hunted (per the mission): a failure that discards work or drops a key without a
recorded reason. **F# = fixed this session; FL# = flagged, deliberately not fixed here.**

| # | Site | Failure | Disposition |
|---|---|---|---|
| F1 | harness `resolveGroup`/`healGroup` (template in [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)) | positional-only response matching: an omitted/reordered card shifts every later card onto the wrong key; equal-citation-count pairs swap **silently** | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — key1-matched acceptance, positional fallback |
| F2 | harness `healGroup` | fragments accepted with NO fidelity check (main path's `accept()` had no heal-side sibling); misaligned fragment stitched into a partial card that no gate reads | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — per-fragment `{Tn}`-multiset gate |
| F3 | harness `healGroup` | all-or-nothing per group: one stubborn fragment discarded the group's resolved siblings (same shape PR #40 removed one level up) | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — partial credit + exact `missing_fragments` ids on the card |
| F4 | harness, both bisections | unguarded `Promise.all`: one half's hard throw rejects wholesale, discarding the other half's resolved cards | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — per-half catch |
| F5 | harness top level + [`save_and_audit.py:44-52`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/save_and_audit.py) | a batch thunk that throws → `parallel()` yields null → keys **vanish from results**; save-side "drop null slots" made it permanent. Observed live: 07-01 catch-up files with selected keys absent (sc.As 4/5 missing, sc.Ap 6/12, sc.viS 5/10…) | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — total-accounting invariant: every `meta.selected_keys` entry appears in results exactly once, synthesized with a reason if needed |
| F6 | harness, all 3 catch sites + `accept()` | error reason discarded everywhere; `summary` carried only `null_keys` | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — failure ledger: per-row `error` + `summary.failures` + `log()` |
| F7 | [`autosplit_requeue.py` `cmd_merge`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py) | fully-failed cards dropped from results (console print only); no machine-readable requeue trail (observed: gam autosplit — 11 fragments queued, 4 results, no trace) | [#64](https://github.com/gasyoun/SanskritLexicography/pull/64) — accounted null rows + fragment keys persisted to the missing-file |
| F8 | `autosplit_requeue.py` shared `autosplit_manifest.json` | cross-session race: concurrent `gen` runs overwrite each other; later `merge` silently uses the wrong fragment map | [#64](https://github.com/gasyoun/SanskritLexicography/pull/64) — per-root+lang manifests, root-checked legacy fallback |
| F9 | `autosplit_requeue.py` `cmd_merge` fidelity drift | complete card with drifted `<ls>` counts: warn-print, card kept unmarked (opposite disposition to the harness's silent-null — both wrong ways) | [#64](https://github.com/gasyoun/SanskritLexicography/pull/64) — `fidelity_drift: true` on the row; [#65](https://github.com/gasyoun/SanskritLexicography/pull/65) carries it into store provenance |
| F10 | [`promote_final_cards.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) `collect_cards` | `wf_output.en.*` matches the default glob, sorts BEFORE RU files, first-seen-wins → EN card shadows the RU card → `rows_for` yields 0 rows (no `russian` field) → **silent RU loss on full rebuild** | [#65](https://github.com/gasyoun/SanskritLexicography/pull/65) — EN files excluded from the RU bridge |
| F11 | promotion + gates | partial cards (`ka` 39/41 groups) indistinguishable from complete: `audit_coverage.py` flags only <80% of source senses; NOTHING read `partial:true`; the marker died at promotion | [#65](https://github.com/gasyoun/SanskritLexicography/pull/65) + [#66](https://github.com/gasyoun/SanskritLexicography/pull/66) — `partial_card` in store provenance; `partial_cards` + missing pieces in the audit report |
| F12 | [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) transient/defect split | fidelity-reject nulls classified "transient — cheap re-run" although retry-resistant by construction (the Sam/Buj/naS stubborn-null loop) | [#66](https://github.com/gasyoun/SanskritLexicography/pull/66) — reason-aware split; reason histogram in the summary |
| F13 | gen-time selfheal precompute | a card whose fallback was dropped (lossy fragment mask / unsplittable) got no fallback **silently** | [#63](https://github.com/gasyoun/SanskritLexicography/pull/63) — printed at generation |
| F14 | `root_window_status.py`, README, PIPELINE_ARCHITECTURE, AGENTS | live tooling advising the DEPRECATED `gen_opt_harness.py` in all 4 next-action strings; docs claiming the runner is "TODO" | [#67](https://github.com/gasyoun/SanskritLexicography/pull/67) |

**Flagged, deliberately NOT fixed in this session** (each is either quality-adjacent — the
mission forbids touching translation-quality logic — or its own scoped change):

| # | Site | Issue | Suggested owner/session |
|---|---|---|---|
| FL1 | [`whitney_grammar.py:154-160`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/whitney_grammar.py) | `grammar_for(slp1, homonym)` falls back `… or recs`: a nonexistent homonym silently returns ALL homonyms — wrong-root grammar attached; collides with the siD homonym-safety finding | small dedicated PR; touches evidence injection, so validate on a homonym root |
| FL2 | [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) | the EN gate has no teeth: nulls never fail `--strict`; `save_and_audit.py` invokes it non-strict with no `--report`; a crashing sense-dupe subgate counts as clean (`returncode None` is falsy) | EN-track session (pairs with the EN residual re-run) |
| FL3 | [`ru_coverage.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ru_coverage.py) | the anti-silent-partial gate is wired to NOTHING (hand-run only), and a corrupt/missing EN denominator silently exempts a root from the very check built after the gam-6/127 incident | wire into `save_and_audit.py` or CI |
| FL4 | `en_residual_keys.py:27-34` + `en_split_triage.py:66-68` | "done" = ≥1 English sense (a 1/40 card counts as done); a null card with a missing input vanishes from triage entirely | EN-track session |
| FL5 | [`prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py) `has_text_signal()` | Mode-6 false positive (`suspicious_attested_without_text_signal`, 66% of round-2 risks) — requeues that NO model output can clear; 2,152 key-requeues on 06-29 alone | own session; semantic-risk heuristic, needs care |
| FL6 | [`pwg_mask.py:43-58`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py) | a truncated final record (missing `<L END>`) is buffered and never yielded — last record silently disappears from every consumer | small PR, low urgency (source file is stable) |
| FL7 | `corpus_gate.py` evidence loaders | absent evidence jsonl → authority silently removed (degrades safely to LLM-verdict, but "sources not built" and "word uncovered" are indistinguishable); DB errors leave `corpus_examples: []` unmarked | note-only; safe direction |
| FL8 | singleton status files (`window_status.json`, `audit_window.report.json`) | ANY audit run — including test fixtures — clobbers them; "current status" cannot be trusted without the event log (observed: current status reports a temp-file fixture) | small PR: per-run-id reports or a fixture guard |

---

## 4. The week's failure modes (evidence-mined) vs. coverage

Full evidence in the S10 session log; summary (dates 2026-06-25 → 07-02):

| Mode | What | Scale | Covered by #35/#37/#38/#40? | By this session? |
|---|---|---|---|---|
| 1 | StructuredOutput retry-cap on citation-dense cards (stochastic, all-or-nothing heal, `plan()` header bug) | 77 EN residuals; brū/kāla/ka/śrī | **YES** (the target class) | #63 adds reasons + partial credit depth |
| 2 | Slice-D 18×-parallel collapse — 117 nulls in whole-batch blocks, **zero** rate-limit strings persisted anywhere | 18 roots, 06-29 | no (process doctrine: ≤3-wide) | #63 preserves the cause per key |
| 3 | Artifact overwrite / stage loss (requeue-save clobber ~630 cards; store wipe 10,122→472; EN layer superseded — STILL OPEN) | 3 incidents | no (separate guards landed earlier) | #65 removes the EN/RU shadow contributor; EN re-run named in §6 |
| 4 | Queued-but-never-run requeues; keys absent from results with no marker | 41-harness queue built 07-01, never drained; 8 vas/gam keys missing from the store TODAY | no | #63 (accounting) + #64 (fail-trail); backlog re-run named in §6 |
| 5 | Fidelity-guard rejection loop (model answers, guard rejects, stored as bare null, retried pointlessly) | Sam/Buj/naS + han/vah/diS EN | no | #63 labels + #66 reclassifies as defect |
| 6 | `has_text_signal()` audit false positive → unclearable requeue churn | 2,152 requeues 06-29, 1,166 on 07-01 | no | **OPEN** (FL5) |
| 7 | prompt_semantic gate crashes → root blocked | 3× (Ap, Śru, siD) | no | recorded; low volume |
| 8 | Windows traps: CRLF harness rejection, CRLF requeue-key truncation, dA/DA case-collision readings | recurring | no | LF write already on master; rest documented |
| 9 | Harness >512 KB scriptPath cap; chunk-merge hash loss | root `i`, 06-29 | resolved then | — |
| 10 | Singleton status files clobbered by any run incl. tests | ongoing | no | FL8 |

**Answer to the mission's "is there more than 4 bugs' worth of failure surface?" — yes,
decisively:** modes 2–6 are all real, none of them is the fixed class, and mode 1 itself was
only ever *validated* on 4 headwords while its backlog was never re-run.

---

## 5. What "the guarantee" now means, concretely

M.G.'s requirement: a big card must never again silently disappear. As of PRs #63–#67
merged, the construction is:

1. **No key can vanish.** The harness emits one results row per `meta.selected_keys` entry
   — enforced by a final invariant even under thunk-null/crash. Nominal runs (no rootmap,
   e.g. `kāla`/`ka`/`śrī`) get the same protection — previously they had NONE (the
   stale-check net only covers root mode).
2. **No failure without a reason.** Per-row `error` + `summary.failures` + narrator `log()`
   lines; the audit report carries `failure_reasons` and a reason histogram; the requeue
   split is reason-aware.
3. **Partial beats nothing, everywhere, and is visible.** healGroup → selfHeal →
   autosplit-merge all return partial credit with exact missing-piece ids
   (`missing_fragments` / persisted missing-file), and the marker survives into the audit
   report AND store provenance instead of dying at each layer boundary.

What the guarantee does **not** yet include: the audit-side false-positive churn (FL5), the
EN gate's teeth (FL2), and the store's single-copy risk (gitignored, one machine — carried
as a standing @DECIDE in the GTD hub; not code).

---

## 6. Honest verdict + the named follow-up sessions

**"Fails too often" is PARTIALLY closed.** The *silent* part — undiagnosable, work-discarding
loss — is closed by construction pending merge of #63–#66. The *often* part needs three
specific follow-ups (in priority order):

1. **Dense-residual re-run session (Sonnet-tier, mechanical).** Re-run through the fixed
   stack (`--selfheal --binary-split --output-budget=60`): the 8 store-missing RU keys
   (`vas~~h0_zz_pw00`, `vas~~h0_zz_pw01`, `vas~~h2_11_prati`, `vas~~h4_18_ni`,
   `gam~~h0_zz_pw00`, `gam~~h3_04_upa`, `gam~~h3_06_vini`, `gam~~h3_08_sam` — 4 vas keys
   live-run this session, see below), `en.DA`'s 7 nulls, the 77 EN residuals, and `ka`'s 2
   missing groups (now targetable via `missing_fragments`). ≤3-wide, per Mode 2.
2. **Audit-churn session (Opus/Fable-tier judgment).** Fix FL5 (`has_text_signal`) — it
   burned more requeues last week than every real failure combined — plus FL2/FL3 gate
   wiring.
3. **EN store layer**: re-run `promote_en.py` (S7 leftover; one command + verification).

<a name="live-validation"></a>**Live validation (this session) — PASSED, 4/4.** The 4
store-missing `vas` keys were re-run through the #63 harness (RU,
`--selfheal --binary-split --output-budget=60`) via the Workflow tool: summary
`{cards:4, ok:4, null:0, healed:1, partial_keys:[], failures:{}}` — 15 agent calls,
~988k tokens, ~16 min. The run exercised the new machinery under real fire: one retry
returned a literal junk `"test"` card, which **key1-matched acceptance rejected** (the
pre-fix positional path would have mis-assigned it); one bisection half hard-threw
`StructuredOutput retry cap (5) exceeded` (the exact Mode-1 throw), was caught, and fell
through to selfheal; `vas~~h0_zz_pw01` healed across 9 fragment groups to a COMPLETE card.
All 4 cards merge-saved into `wf_output.sc.vas.json` (7→11 non-null) and merge-promoted
into the store (10,614→10,771 rows; dated `.SAFE_s10_20260702.keep` backup taken first).
**Provenance finding:** the harness's `model:'sonnet'` alias resolved to **Sonnet 5
(`claude-sonnet-5`)** in this runtime — NOT Sonnet 4.6 as during the 2026-06-30 FU1 run;
promotion used `--gen-model-version claude-sonnet-5`. Any promotion of runs after
~2026-07-02 must not use the 4.6 default.

---

## 7. Cleanup performed (mission step 4)

- **Deleted** (in [#67](https://github.com/gasyoun/SanskritLexicography/pull/67)):
  `gen_batched_harness.py`, `gen_tlonly_harness.py`, `assemble_tlonly.py` (retired
  prototypes, zero code refs, wins folded into `gen_opt_harness2.py`), 17
  `run_pilot_wf.sd_rq_*.js` spent one-shot artifacts.
- **Kept deliberately:** `gen_opt_harness.py` (deprecated, doc-described),
  `src/pilot/archive/` (do-not-revive history), `run_pilot_wf.js` (live CONV/TR template —
  `gen_opt_harness2.py` regex-parses it at every generation; deleting it breaks the
  canonical generator).
- **Duplication mapped, consolidation deferred:** `gen_opt_harness2.py`'s inline selfheal
  and `autosplit_requeue.py`'s standalone gen/merge implement the same fragment-planning +
  partial-credit philosophy twice, with divergent granularity (heal-group vs sense),
  marker names (`missing_fragments`/`missing_groups` vs `missing_senses`), and stitching
  (flat senses vs per-sense part rejoin; the JS stitched card lacks `iast`/`h`). They also
  make the OPPOSITE grouping choice (grouped fragments vs `--budget=1` solo). This session
  aligned their *failure semantics* (both now do accounted partial credit with persisted
  missing pieces) but did NOT merge the implementations — that refactor touches proven
  translation control flow for zero behavioral gain and was judged not worth the risk
  mid-recovery. Revisit only if a third consumer of plan() appears.
- `resolveGroup`/`healGroup` remain near-clones by design (different attempt budgets,
  different acceptance); unifying them parametrically was prototyped and rejected — the
  shared abstraction was harder to read than the duplication.

## 8. Hub/report follow-through

- GTD: SanskritLexicography row updated for S10 (see
  [`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)).
- Findings routed per the append reflex: the "one symptom, five diseases" measurement and
  the store single-copy risk belong to
  [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (infra/process).
- Fable window plan: outcome recorded in
  [`FABLE_WINDOW_PLAN.md`](https://github.com/gasyoun/Uprava/blob/main/FABLE_WINDOW_PLAN.md).

_Dr. Mārcis Gasūns_
