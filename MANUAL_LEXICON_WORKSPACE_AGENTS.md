# SanskritLexicography workspace manual — for agents

_Created: 10-07-2026 · Last updated: 18-07-2026_

Human twin (Russian):
[MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md).
Authored under H479 (Fable 5 `claude-fable-5`); consolidated under H604. This
manual is an **index + hard-rules sheet**, not a replacement for the canonical
docs it points at — when this file and a canonical doc disagree, the canonical
doc wins; fix this file in the same pass. The **canonical audience-manual set**
lives in [docs/manuals/](https://github.com/gasyoun/SanskritLexicography/tree/master/docs/manuals)
(router: [docs/manuals/README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.md)) —
depth belongs there, this sheet stays thin.

## 1. Session entry protocol

1. Read [CLAUDE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md)
   (repo-specific) — org rules load from `../CLAUDE.md` automatically.
2. Read **fresh** the `## 🚧 WIP` sections of
   [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md)
   and, for pwg_ru work,
   [RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
   (subsystem file takes priority). Check
   [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
   for a `🔒 CLAIMED` tag on your row.
3. **This tree is shared by concurrent sessions** (Claude, Codex, external
   actors). Deliver via an isolated `git worktree` off `origin/master` +
   branch + PR. Never `git add -A` in the shared tree; stage named files only.
4. For pwg_ru specifically, read
   [RussianTranslation/AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/AGENTS.md)
   (local operating rules) before touching anything under `src/`.

## 2. Canonical-doc index — who owns what

| Concern | Canonical doc |
|---|---|
| How pwg_ru got here / already-fixed bugs | [PIPELINE_HISTORY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| Live production procedure (worked example) | [RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) |
| Operator command flows | [USE_CASES.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/USE_CASES.md) |
| Pipeline component map | [PIPELINE_ARCHITECTURE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md) |
| RU/EN fix-parity policy (selftest-enforced) | [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) |
| Launch incident ledger (append after EVERY launch) | [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md) + `src/pilot/check_launch_ledger.py` |
| Launch statistics | [LAUNCH_STATS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md) |
| API warm-up probes (append-only) | [GENERATION_API_PROBE_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/GENERATION_API_PROBE_LOG.md) + `src/pilot/probe_log.py` |
| Multi-account concurrency safety | [PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md) §W1 + [CONCURRENCY_REAUDIT_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CONCURRENCY_REAUDIT_2026-07-09.md) |
| Falsifiable research backlog (30 capabilities) | [RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md) |
| Full-dictionary bulk plan | [FULL_PWG_RU_30_DAY_SLA_PLAN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FULL_PWG_RU_30_DAY_SLA_PLAN.md) |
| Headword print-readiness | [HeadwordLists/PRINT_READINESS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/PRINT_READINESS.md) |
| Measured gotchas (Sanskrit-data) | [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) + 7 epistemic sibling registries |

## 3. Hard rules (violations have bitten before — see the ledger)

- **Never relaunch the medium50 / dense band-4 nominal lane blind.** The
  kill-gate/self-heal cascade is reproduced 3× (~2M tokens/window for ~1
  card). Gated on H442 recalibration →
  [H462](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md).
- **≤3 concurrent translation lanes, GLOBAL across all accounts and
  sessions.** The Slice-D collapse (~18 concurrent root workflows) is a
  server-side cliff.
- **Any multi-agent fan-out goes through `src/synth_dispatch.py`** — never a
  bare 10-wide dispatch (H234 post-mortem).
- **`--no-tm` on every requeue rerun**; per-window `--out` and
  `wf_output.<window>.json` names always — never bare defaults.
- **Single promoter**: one owner runs `promote_final_cards.py --merge` + TM
  rebuilds per convergence cycle.
- **Warm-up probe before any generation launch**, logged via
  `src/pilot/probe_log.py`; a NO-GO reading means do not launch. A trivial
  probe is necessary but not sufficient (H442 finding) — prefer a
  load-representative (≥5 KB) payload.
- **After every launch, append an incident/outcome row to
  [LAUNCH_FUCKUPS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md)**
  and re-harvest stats. Infra-confounded runs are recorded as such, never as
  code failures.
- **Classify every pwg_ru fix SHARED / INTENTIONAL-DIVERGENCE / GAP** before
  session end ([LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md);
  selftest-gated).
- **Encoding:** files here have inconsistent BOM state — check before edit,
  preserve on write, never add/strip silently. Python scripts:
  `sys.stdout.reconfigure(encoding='utf-8')` + `encoding='utf-8'` on
  output-capturing subprocess calls.
- **Generated/derived bulk stays gitignored** (store, TM sidecars, review
  sheets, wf outputs); builders + small summaries + reports get committed.
- Huge files (`DCS_statistical_evaluation.htm` ~75 MB, error lists) — stream,
  never Read whole.

## 4. Current state — read it live, not from this sheet

This sheet deliberately carries **no state snapshot** (the 11-07 one it used to
carry aged wrong within a week — store rows, blocker chain and the P2 gate all
moved). Read fresh, in this order:
[RussianTranslation/.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
(subsystem, takes priority) →
[.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md)
(root) → [Uprava/GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
(human gates). One durable correction worth pinning: the ACC×NCC P2 gate is
**MG's vote on the local 49,019-row sheet + `apply_p2_decisions.py`** —
[PR #264](https://github.com/gasyoun/SanskritLexicography/pull/264) itself
merged 09-07-2026 and is not the gate.

## 5. Multi-account bulk protocol — moved

> Moved to [RUSSIANTRANSLATION_DEEP_MANUAL.md §13](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md)
> (18-07-2026, H1245) — kept here as a pointer so existing links resolve. The
> one hard rule that stays on this sheet: **global ≤3 concurrent translation
> lanes across ALL accounts and sessions** (see §3).

## 6. Where results go

- Measured caveat → [FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (Sanskrit-data) or [Uprava/FINDINGS.md](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (infra).
- Substantive tables → [RESULTS_LOG.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESULTS_LOG.md)
  or the owning topic doc, same pass.
- Human review of any list → interactive HTML sheet (`/review-sheet`),
  registered in [Uprava/REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md);
  markdown checkboxes are banned.
- Session end → tidy the right `.ai_state.md`, mirror human items to GTD,
  `/handoff` for future-session work.

_Dr. Mārcis Gasūns_
