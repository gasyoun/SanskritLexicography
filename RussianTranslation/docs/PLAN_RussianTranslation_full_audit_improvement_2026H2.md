# PLAN — RussianTranslation full audit → improvement portfolio (2026 H2)

_Created: 23-07-2026 · Last updated: 23-07-2026_

**Index / cover doc.** Entry point for the post-audit improvement programme of
[`RussianTranslation/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation).
A fresh agent executes a **wave-1 track** by reading this file, then the four
layer docs, then its handoff's scoped section. Every decision a builder would
hit is ruled below — a dangling `@DECIDE` on a wave-1 must-complete path is a
defect.

## Goal (one paragraph)

RussianTranslation is a mature hybrid: a production PWG→RU factory (headless
CLI, coordinator, ~11.6k promoted rows, heavy hardening through H1339/H1386)
plus research/TM/gloss tracks and a large human-gated editorial surface. A
full audit (23-07-2026) found that **the highest leverage is not new
mechanisms** — the H1403 speed audit already showed 0/8 greenfield speed
ideas surviving unmodified — but **closing operator/telemetry residues,
scaffolding the cohort ledger H1437 depends on, and giving operators one
umbrella sequence** over the two existing `/ask` plans (pubgrade TM, Sa→Ru
gloss) and the live drain. Wave-1 is an **offline ≥8 h portfolio**: production
path residues (A+F), cohort/promotion ledger scaffold (B), and this umbrella
doc set (C), with best-effort quality-apply dry-run machinery (D) and thin
pointers to existing TM/gloss plans (E). **No paid generation. No live store
mutation.** Wave-2 starts only after wave-1 + a fresh health GO.

## The four layer docs

| Layer | Doc |
|---|---|
| Waves, deliverables, non-goals | [ROADMAP_RussianTranslation_full_audit_improvement_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_full_audit_improvement_2026H2.md) |
| Component boundaries, data model, build-vs-reuse | [ARCHITECTURE_RussianTranslation_full_audit_improvement.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_full_audit_improvement.md) |
| File-level, step-ordered build sequence | [IMPLEMENTATION_RussianTranslation_full_audit_improvement.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_full_audit_improvement.md) |
| Acceptance criteria, proof commands, risk register | [VERIFICATION_RussianTranslation_full_audit_improvement.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_full_audit_improvement.md) |

## Existing plans this umbrella indexes (authoritative for their scope)

| Programme | PLAN (do not rewrite decisions) |
|---|---|
| Publication-grade Sa→Ru TM + oral (finish H215) | [PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pubgrade_tm_oral_2026H2.md) |
| Sa→Ru gloss quality uplift | [PLAN_RussianTranslation_saru-gloss-quality_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_saru-gloss-quality_2026H2.md) |
| Bounded multi-profile cohort (claimed, deeper than Track B) | [H1437](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1437-Fable_RussianTranslation_bounded-wave-barrier-promotion-ledger_21.07.26.md) |
| Live medium50 / serial-c4 drain prep | [H1447 packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1447/H1447_C4_LIVE_GATE_2026-07-22.md) |

## Decisions taken (Phase-2 interview, 23-07-2026)

| # | Fork | Ruling | Rationale |
|---|---|---|---|
| R1.1 | Wave-1 “done” | **Balanced portfolio (2–3 must tracks + best-effort)** | Full coverage without a single mega-handoff. |
| R1.2 | 1–2 month primary objective | **One handoff per programme/track** | Portfolio of scoped executables, not one omnibus task. |
| R1.3 | Out of wave-1 | **No paid live generation** | Max/API spend reserved for wave-2 after health GO. |
| R1.4 | Relation to existing `/ask` plans | **Umbrella: index + order only** | H215 and Sa→Ru gloss plans stay authoritative for their scope. |
| R1.5 | Store safety | **Never risk gitignored store** | Dry-run / fixtures only in wave-1; no real promote merge. |
| R1.6 | Portfolio size | **8 h wave-1 + clear wave-2/3** | Enough for unattended build; later waves sketched for minting. |
| R2.1 | Wave-1 tracks | **Must: A+F, B, C · Best-effort: D then E** | A includes instrumentation (F is not a separate code path). |
| R2.2 | Handoff minting | **One handoff per wave-1 track** | A, B, C, D, E → five handoffs; E is a thin pointer. |
| R2.3 | Live drain placement | **Wave-2 immediately after wave-1 + fresh health GO** | Production volume is next, not blocked on editorial votes. |
| R2.4 | Build style | **Surgical only — extend existing modules** | No greenfield frameworks. |
| R2.5 | Existing PLAN docs | **Keep authoritative; umbrella links** | No mega-rewrite of H215 / gloss plans. |
| R2.6 | Wave-1 success bar | **Green selftests + PR(s) merged + umbrella docs committed** | Machine-checkable. |
| R3.1 | Time ranking | **Must A+F/B/C; best-effort D then E** | Core 8 h protected. |
| R3.2 | Track A scope | **Full H1403 A2+A3 set** | Telemetry auto + promote defect-refusal + ready_partial helper. |
| R3.3 | Track B depth | **Scaffold + selftests only; no multi-profile live** | Does not replace H1437; feeds its Phase-0 prerequisites. |
| R3.4 | Track D without votes | **Apply machinery + dry-run; never write store** | Votes remain human `@DO`. |
| R3.5 | Track E body | **None — handoff points at existing PLANs only** | Avoid re-implementing H215/H1349. |
| R3.6 | LANG_PARITY | **Update ledger + hashes when SHARED surfaces change** | Standing MG rule: EN stays level with RU. |
| R4.1 | Track A proof | **Pinned `window_selftest` + module selftests green** | |
| R4.2 | Track B proof | **Schema + selftests; no live coordinator run** | |
| R4.3 | Track C proof | **Five-layer docs + metadoc + ROADMAP_INDEX row** | |
| R5.1 | On ambiguity | **Pick plan default, log in `.ai_state` Dev Notes, continue** | |
| R5.2 | Commit authority | **Worktree → PR → auto-merge on green CI** | Never commit in shared main checkout. |
| R5.3 | Explicit fence (R5 multi) | **No paid generation / Max Workflow / headless production translate** | Combined with R1.5 store fence. |

## Autonomy contract (verbatim — unattended execution rules)

**On unplanned ambiguity.** Apply the plan's marked default for that fork, record
the choice in [`RussianTranslation/.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/.ai_state.md)
Dev Notes (one line: `default-taken: <fork> → <choice>`), and continue. Park-and-skip
an item ONLY when no default in this plan applies. Never halt the whole portfolio for
one fork.

**Stop conditions (halt that track + report; other tracks may continue).** Halt a
track if: (a) CI goes red and the fix is outside the track's file list; (b) a change
would require writing the live store or running paid generation; (c) H1437's claimed
worktree already owns a file and a clean merge is impossible without overwriting
in-flight H1437 work — park Track B with a note, do not force; (d) `window_selftest`
cannot be made green after one genuine fix attempt on the failing assertion.

**Commit authority.** Full commit → PR → auto-merge on green CI, **one PR per track
handoff**, in an isolated worktree off `origin/master`
(`SanskritLexicography-h<id>-<pid>`). Delete branch after merge; remove worktree same
pass. Prefer rebase onto latest master before open if H1437 or other PRs land mid-run.

**The fence — never do these unattended:**

1. **No paid generation** — no Max Workflow, no headless production translate, no
   health probes that burn model quota (offline fixtures and pure-Python probes only).
2. **No live store mutation** — never run `promote_final_cards.py` against
   `src/pwg_ru_translated.jsonl` without `--dry-run` (and even dry-run must not
   rewrite the store). Fixtures and temp dirs only.
3. **No publication** — no Pages, visibility, DOI, Zenodo.
4. **No direct commits to guarded main-tree checkout** — worktree only.
5. **No destruction of non-rebuildable assets** — `corpus_lexicon.jsonl`, live TM
   bulk, NWS dumps: read-only.
6. **Scope** — RussianTranslation + Uprava handoff registry only (no SamudraManthanam
   / SanskritRussian data rewrites in wave-1).

## Wave summary

| Wave | Tracks | Paid gen? | Store write? |
|---|---|---|---|
| **1 (8 h must)** | A+F production residues · B ledger scaffold · C umbrella docs | No | No |
| **1 best-effort** | D quality dry-run apply · E thin PLAN pointers | No | No |
| **2** | Fresh health GO → medium50 / serial-c4 drain (H1447 path) | Yes (gated) | Yes (audited promote only) |
| **3** | H215 pubgrade TM + Sa→Ru gloss continuation + editorial apply after votes | Mostly offline / rights-gated | Editorial apply only after votes |

## Autonomy-readiness gate verdict

**PASS.** Every must-complete wave-1 deliverable has architecture, ordered
implementation steps, acceptance criteria, and risks. Zero blocking forks remain
on the must path. Prior-art: surgical extension of existing pilot modules; H215
and gloss plans reused not rebuilt; H1437 remains the live multi-profile vehicle
— Track B only scaffolds binding/receipt/reconcile tests it needs. Defaults cover
ambiguity (R5.1). Best-effort D/E may finish partial without failing the gate.

## Audit snapshot (inputs to this plan)

| Axis | Finding (23-07-2026) |
|---|---|
| Store | ~11,603 rows / ~26 MB; ~8–10% of long-run target |
| Code | ~298 `src/**/*.py`, ~89 `src/pilot/*.py` |
| Production route | Headless CLI + coordinator (H1110); Workflow forensics only |
| Speed (H1403) | Needle = execute queued work + telemetry; not new orchestration |
| Live head | H1447 medium50 prepared; needs **fresh** health PASS |
| Human gates | H1303, H1306, h178 residual, Renou v2, H180×3 await votes |
| Doc surface | Many dated audits; umbrella reduces cold-start thrash |

_Dr. Mārcis Gasūns_
