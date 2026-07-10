# SanskritLexicography workspace manual — for agents

_Created: 10-07-2026 · Last updated: 10-07-2026_

Human twin (Russian):
[MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md).
Authored under H479 (Fable 5 `claude-fable-5`). This manual is an **index +
hard-rules sheet**, not a replacement for the canonical docs it points at —
when this file and a canonical doc disagree, the canonical doc wins; fix this
file in the same pass.

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
  [H462](https://github.com/gasyoun/Uprava/blob/main/handoffs/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md).
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

## 4. Current state snapshot (10-07-2026; verify against .ai_state before trusting)

- Store `src/pwg_ru_translated.jsonl` (gitignored): **11,275 rows** vs
  ~120,173 headword cards total. Engine audited **GO** (H188). Verb drain
  (H151) unaffected and runnable; nominal medium lane **paused** on
  H442/H462.
- Human-gated: ACC×NCC P2 vote ([PR #264](https://github.com/gasyoun/SanskritLexicography/pull/264)),
  H178 bake-off sheets, H180 sheets, G5/G6/G7 publication gates.

## 5. Multi-account bulk protocol (3→4 accounts, H335 §W1 + H336)

Hardening is landed ([PR #254](https://github.com/gasyoun/SanskritLexicography/pull/254):
promotion claim files, per-window namespacing, append hygiene). Protocol:

1. **One worktree/clone per account** — state paths are repo-relative, so
   per-clone runs are disk-isolated for free.
2. **Shard by root via the worklist before starting** — 4 disjoint slices;
   root-sharding guarantees disjoint rootmaps, inputs, TM card keys, requeue
   sets. Fragment-TM cross-duplication is benign iff sidecars are rebuilt by
   the single promoter.
3. **Single-promoter rule** (see §3). Non-promoter accounts stop at "audited
   clean, `wf_output.<window>.json` saved + RUN_LOG pointer".
4. **Global ≤3 lanes** regardless of account count: 4 accounts × 1 root each,
   max 3 in flight.
5. **Cloud/web sessions (claude.ai/code) return outputs via git**, since
   locks never span machines: commit `wf_output.<window>.json` +
   `audit_window.report.json` onto the session branch under
   `RussianTranslation/incoming/<account>/<window>/` (a tracked landing
   directory; proposed convention of this manual — create on first use), PR
   it, and the promoter promotes from `incoming/` then deletes the landed
   files in the same PR. The store itself is gitignored and NEVER travels
   through git — only `wf_output` payloads do.

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
