# Evolution of approaches — PWG → Russian

_Created: 02-08-2026 · Last updated: 02-08-2026_

This is the **methodological** history of how the PWG→RU programme learned to
translate: which approach was tried, what forced the next pivot, and how the
codebase accreted as those pivots hardened into modules. It is complementary
to three siblings that already exist and should **not** be re-derived:

| Document | Role |
|---|---|
| [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) | Engineering phases 0–15 + reverse-chronological incident ledger (the “what broke and when”) |
| [`src/pilot/EVOLUTION_TIMELINE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/EVOLUTION_TIMELINE.md) | Early failure ledger F-series (mid-June only; stops ~29-06) |
| [`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md) | Versioned releases (newest first) |

Read this for the **shape of the thinking**. Read `PIPELINE_HISTORY` for PR
links, measured numbers, and gate-by-gate forensics. Operator path today:
[`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md).

**Provenance of this draft:** Grok 4.5 (`grok-4.5`), 02-08-2026. Synthesised
from the documents above, [`STRATEGY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/STRATEGY.md),
[`IMPLEMENTATION_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/IMPLEMENTATION_PLAN.md),
[`REVIEW_AND_ROADMAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md),
[`README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/README.md)
milestones, [`pwg_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md),
and the 02-08 nonstop plan
([`docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md)).
Counts that move (store rows, selftest N) are dated; re-measure before citing.

---

## 1. The problem that never changed

PWG (Böhtlingk–Roth, 1855–1875) is still the largest Sanskrit dictionary ever
compiled. The source is dense 19th-century lexicographic German, carrying
Sanskrit spans, grammar labels, and hundreds of thousands of source citations
that must survive translation **byte-for-byte**. At ~100k headwords the only
economically viable translator is an LLM — so the research object is not “can a
model translate a dictionary entry” (it can; gold-sample judging measured
96–98.5% faithfulness) but **how to make an LLM pipeline reliable, cheap, and
mechanically verifiable at scale**.

One standing mandate, never relaxed: this becomes a **printed dictionary** —
quality before throughput. Every approach below is a different answer to that
mandate under different constraints (quota, host health, human review time).

---

## 2. Prehistory — `mw_ru` as the engine seed

Before `pwg_ru` existed as a programme, the house had already finished a full
Monier-Williams **English → Russian** run (`mw_ru`: 287,358 cards). That work
established:

- **Mask untranslatable spans**, translate only the source-language “wrapper.”
- **Multi-pass multi-model** production (Sonnet bulk translate; dual QA judges;
  Opus rewrites rejects) — see [`mw_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/mw_ru.md).
- A **shared engine** parameterized by source language (`mw_ru` vs `pwg_ru`),
  not two unrelated scripts
  ([`PIPELINE_ARCHITECTURE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_ARCHITECTURE.md)).

`mw_ru` is complete and is **not** being redone. Its Russian cards seed
`pwg_ru` as a **terminological anchor** (not a copy source) for shared
headwords. Everything below is the PWG-specific story.

---

## 3. Evolution of approaches (seven eras)

Each era is named by the **ruling idea** that ordered work, not by a calendar
week. Calendar anchors are approximate; exact dates live in `PIPELINE_HISTORY`
and the changelog.

### Era A — Translate every gloss (inherited mental model, pre–mid-June 2026)

**Approach.** Treat PWG like `mw_ru`: send every German gloss to an LLM, judge
every card, re-translate rejects.

**Why it failed as a print strategy.** It invents Russian from model weights
instead of from attested human Russian (dictionaries + parallel corpus). For a
printed scholarly dictionary that is the wrong order of operations.

**Codebase at this stage.** Prompt packs
([`pwg_ru_prompts/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru_prompts)),
early masker sketch, `mw_ru` as reference — little PWG-specific machinery yet.

### Era B — Harvest-first assembly (strategic pivot, ~15–23 June 2026)

**Approach.** For each headword, **assemble** Russian from material that already
exists; use the LLM only for genuine German gaps and scholarly connective
prose. Harvested senses become **additional attested senses** in the card, not
mere “hints for the model.” Sources, in priority:

1. Five extracted Sa→Ru dictionaries (`koch` / `kow` / `kna` / `fri` / `smirnov`,
   ~57k keyed entries) via [`src/build_src.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_src.py)
   + [`src/corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
2. SamudraManthanam parallel corpus (verse-aligned Sa↔Ru)
3. `mw_ru` cards for shared headwords (anchor, not copy)

**Theory load.** Apresjan / Moscow Semantic School as the native standard for a
Russian-target dictionary
([`APRESJAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/APRESJAN.md),
[`HARVEST.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HARVEST.md)).

**Codebase rise.** `assemble.py`, harvest readers, stratified corpus lexicon
build, early a-section pilot harness, first hard rules (anti-fabrication,
coverage, sigla, Nachträge) — the F-series in
[`EVOLUTION_TIMELINE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/EVOLUTION_TIMELINE.md).

**Output of the era.** ~216 provisional `a–` cards at ~95% first-pass — a
**proof of process**, later treated as gold/reference rather than the bulk
queue order.

### Era C — Corpus-first reorder + frequency-first bulk (15–23 June pivot chain)

Two nested pivots on top of harvest-first:

1. **Corpus-first (15-06).** Build the durable Sa→Ru word-alignment lexicon
   **before** bulk-translating more alphabet sections, so every card harvests
   maximum attested Russian. Outcome: **1.09M alignments / ~190k keys**
   (gitignored regenerable asset).
2. **Frequency-first (23-06).** Stop walking the alphabet. Rank PWG headwords by
   a hybrid of DCS token frequency × text breadth × entry richness; translate
   the top ~2–5k core first. The a-section remains the validated gold slice;
   only the **queue order** for scale-up changes
   ([`REVIEW_AND_ROADMAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REVIEW_AND_ROADMAP.md)
   §5).

**Codebase rise.** `freq_route.py` / scale manifests, DCS joins, Renou genre
stratification, `add_corpus_text.py`.

### Era D — Production root windows + deterministic gate stack (26 June – early July)

**Approach.** The unit of production becomes a **root (or nominal) window**:
build a harness, run it through Claude Max / Workflow, audit with free Python
gates, requeue residuals, promote. Translation quality was already fine
(37/38 publishable on the first judge gate); the open problem was entirely
**process**.

Critical sub-pivots inside this era:

| Sub-pivot | Forced by | Standing rule |
|---|---|---|
| **Mask + batch** (`gen_opt_harness2`) | Fixed per-call system-prompt overhead (~27–46k cache_create tokens) made "$16/root" nonviable | Pack cards per agent; restore `{Tn}` markup in JS; measured **−72% to −90%** cost |
| **Translate-only + free gates** | ~10M tokens for one root with per-card LLM judge | Sonnet translates; `audit_window.py` is free; LLM judge only on a sample / rejects |
| **Concurrency cliff** | 18-wide fan-out → 117 transient nulls | Standing **≤3-wide**, roots one at a time |
| **5-layer merge card** | PWG alone is not the local-layer universe (~36% of the union has no PWG record) | All-in-one card: PWG + PW + SCH + PWKVN + NWS; later a dedicated **no-PWG** lane |
| **Grammar as data, not prompt** | A/B: grammar-in-prompt did not help DE→RU | Nominal/verb grammar ships as structured indices; never injected into translate prompts |

**Codebase rise (the production spine).**

```
src/pwg_mask.py                 # lossless masker
src/_pilot_gen_merged.py        # 5-layer card assembly
src/pilot/gen_opt_harness2.py   # batched+masked harness emitter
src/pilot/audit_window.py       # canonical free gate stack
src/pilot/window_selftest.py    # regression pins for every real gate bug
save_and_audit.py / promote_*   # land + promote with provenance
```

This is the era documented as Phases 0–8 in `PIPELINE_HISTORY` and the README
milestones table.

### Era E — Memory, fragments, and “residuals are often gate bugs” (early–mid July)

**Approach.** Stop treating every residual as a content defect:

- **Content-addressed TM** at card **and fragment** level — shared fragments
  and partial giants become free on rerun (standing cost lever).
- **Self-heal / head-splitter / sense-density presplit** — giant and dense
  cards route to fragment groups instead of burning StructuredOutput retries.
- **Wall-clock kill gate** — abandon any call that overruns a size-scaled
  budget (MG: “don’t wait for miracles”).
- **Gate-bug hunts as first-class work** — `gam`’s “documented residuals” were
  three false gates; re-audit of the same `wf_output` went 127/127 clean
  without re-translation (Phase 6). Lesson: **re-audit before re-translating.**

**Codebase rise.** Fragment TM, `autosplit_requeue`, kill-gate wiring in the
harness, `LANG_PARITY.md` (RU/EN gate drift ledger), `FAILURE_MODES_AND_KILL_GATE_*`,
launch ledger + `LAUNCH_FUCKUPS.md` / `LAUNCH_STATS.md`.

**Scope ruling (Phase 7).** Drain all remaining DCS-attested verb roots one at a
time (H151 standing drain) once readiness audit green.

### Era F — Factory hardening + execution-route change (mid–late July)

**Approach.** The bottleneck shifts from “can we translate a root” to “can we
run unattended without losing money or data.”

| Pivot | Meaning |
|---|---|
| **Headless CLI, not Workflow-from-session** (H1110, 18-07) | Production route = `headless_worker.py` + manifest v2; Workflow retained for forensics only |
| **Live-gate GO/NO-GO** (`/pwg-live-gate`) | One ≥5 KB health call + synthetic `dq_canary_puregloss`; mechanical `gate_reason`; stale GO never authorizes spend |
| **Bounded paid run** (`/pwg-bounded-run`) | One profile, `max-wide=1`, `--stop-before-promote`, no silent retry/widen |
| **Call reservation + promotion journal** | Paid call is a durable spend decision; promote is a multi-phase journal under one store claim |
| **Human review as a hard pre-filter** (H1655) | “No German before a human” — residue gates + machine flags before G5 sheets |
| **RU style as mechanical sweep** (H1305, H1303/H1306 → style guide of record) | Editorial metalanguage, abbreviation render maps, no-ё |

**Codebase rise (the factory layer).**

```
src/pilot/headless_worker.py
src/pilot/bounded_staged_run.py / coordinator.py
src/pilot/call_reservation.py / economy_ledger.py
src/pilot/canary_gate.py          # canary half becomes code (H2159)
src/pilot/cohort_engine.py        # multi-profile offline control plane
src/review_residue_gate.py
src/store_write.py                # locked rewrite for all mutators
src/german_anchor.py              # source-anchored {#…#} repair
src/pilot/d4_boundary_wrap.py     # mechanical RU defect repair class
```

**Measured reality of late July–early August.** Throughput often blocked on
**host/route economics**, not model quality: 180 s (later 300 s) kill ceilings,
CLI cache re-creation every call (~70% of cost), bare-cwd free win (−33% cost /
−30% wall). Call **shape is not the lever** (H2152); Messages-API port is the
open structural fix (H2158), human-gated because Max subscription vs metered
API is a spend trade.

Store snapshot cited in late-July docs: **~11,603** RU sense-rows; residual
unique population **~5,580** (H1339) — re-measure before quoting.

### Era G — Nonstop multilane (plan locked 02-08-2026; execution open)

**Approach.** The constraint is no longer weekly quota (“we never reach it”) but
**idle time waiting for a human to launch, review, and promote.** The 02-08
`/ask` plan (16 MG rulings, H2175) turns the bounded window into a **nonstop
multi-surface system**:

- Three runtime lanes: local PC · samskrte.ru prod box · Anthropic cloud routines
- Private `pwg-ru-data` LFS repo for the local-only working set
- Auto-promote on mechanical gates for a 1-week trial with daily 10% spot-check halt
- Pre-registered A/B (DeepSeek draft · Grok judge · routine vs CLI) before any
  cheap lane earns a production role
- **Claude API permanently out of scope** (subscription Max only)

This era is **planned, not yet executed** as of this document’s date. Layer docs:
[`docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md)
and siblings.

---

## 4. Compact timeline (approach-level)

| When (2026) | Approach era | One-line change |
|---|---|---|
| pre-June | A — full-gloss LLM (mw_ru heritage) | Engine exists; PWG not yet the bulk target |
| ~15-06 | B — harvest-first | Assemble attested Russian; LLM only fills German gaps |
| 15-06 → 23-06 | C — corpus-first + frequency-first | 1.09M lexicon; DCS-ranked core queue |
| 17-06 → 26-06 | B/C pilot hardening | F-series guards; owner-map kills NWS misattribution by construction |
| 26-06 → 03-07 | D — root windows + free gates | Mask+batch; audit_window; ≤3-wide; 5-layer cards |
| 01-07 → 07-07 | E — TM + fragment + gate-bug truth | Card/fragment TM; kill gate; re-audit before retranslate |
| 07-07 → 18-07 | E/F transition | Drain + no-PWG lane + coordinator hardening |
| 18-07 → 01-08 | F — headless factory | Live-gate; reservation; human residue gate; style sweeps |
| 25-07 → 02-08 | F cost forensics | Cache rewrite finding; bare cwd; ceiling variance; presplit floor fix |
| 02-08 → | G — nonstop multilane (planned) | Auto-promote trial; multi-surface; scientific cheap-lane A/B |

For phase-grain engineering detail (Phases 0–15), use
[`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md)
§ Timeline. For release-grain code, use
[`CHANGELOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md).

---

## 5. How the codebase rose (layer cake)

Layers appear in roughly the order a new reader should learn them. Later layers
depend on earlier ones; none of the early layers was deleted — they were
**constrained** by later gates.

```
┌─────────────────────────────────────────────────────────────┐
│  G  Nonstop multilane (planned): data repo, auto-promote,   │
│     multi-surface scheduler, cheap-lane experiments         │
├─────────────────────────────────────────────────────────────┤
│  F  Factory: headless_worker, coordinator, call reservation,│
│     promotion journal, live/canary gates, store_write lock, │
│     review residue gates, style/abbrev repair modules       │
├─────────────────────────────────────────────────────────────┤
│  E  Memory & recovery: card+fragment TM, autosplit/requeue, │
│     kill gate, denylist, save_and_audit merge discipline    │
├─────────────────────────────────────────────────────────────┤
│  D  Production spine: pwg_mask, gen_opt_harness2,           │
│     audit_window + window_selftest, promote_*, LANG_PARITY  │
├─────────────────────────────────────────────────────────────┤
│  C  Queue & corpus: freq ranking, DCS joins, corpus lexicon,│
│     Renou strata, add_corpus_text                           │
├─────────────────────────────────────────────────────────────┤
│  B  Harvest assembly: build_src, corpus_gate, assemble,     │
│     5 dicts + mw_ru seed + Apresjan candidate sets          │
├─────────────────────────────────────────────────────────────┤
│  A  Shared engine seed: mw_ru prompts/format, mask idea,    │
│     multi-pass multi-model discipline                       │
└─────────────────────────────────────────────────────────────┘
         │
         ▼ parallel research/export tracks (not on the critical path)
    grammar indices · re-glue / addenda typology · OntoLex/TEI DE export
    learner apparatus · paper spines A49/A51/A52 · RV multi-translation
```

**Invariant across all layers:** Sanskrit, citations, and non-German markup are
**never** the model’s responsibility to “get right” — they are masked,
restored, and checked deterministically. Every real gate is a tombstone for a
failure that taught that lesson
([`EVOLUTION_TIMELINE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/EVOLUTION_TIMELINE.md)
§ Standing lessons).

---

## 6. What other timelines, related to PWG translation, can be made?

The material for each of these already exists in the tree as scattered handoffs,
audits, and changelogs. None is a full narrative yet (except the two already
listed). Ranked by usefulness to a future session:

### Already written (do not rebuild)

1. **Engineering phase timeline** — `PIPELINE_HISTORY.md` Phases 0–15 + post-07-07 factory notes.
2. **Early failure-driven evolution** — `src/pilot/EVOLUTION_TIMELINE.md` (through ~29-06).
3. **Release timeline** — `CHANGELOG.md` (version chronology).
4. **This document** — methodological approach eras + codebase layer cake.

### High value, not yet a single timeline doc

5. **Execution-route timeline** — Max Workflow session → opt2 harness → headless CLI (H1110) → bare-cwd spawn → (planned) Messages API (H2158) → (planned) multilane CLI/routines. *Why useful:* every stale runbook still says “run the Workflow from this session.”
6. **Gate-stack genealogy** — for each gate in `audit_window` / promote / residue: date added, failure that forced it, selftest pin, LANG_PARITY status (SHARED vs GAP vs INTENTIONAL). *Why useful:* stops “this gate looks over-strict, let’s disable it.”
7. **Cost-model timeline** — $16/root estimate → mask+batch −72–90% → TM free reruns → perf_preflight formula bugs → 4.7–5.8× preflight under-estimate → cache re-creation ~70% of call cost → bare-cwd free win. *Why useful:* papers A51/A52 and any budget `@DECIDE`.
8. **Quality / evaluation timeline** — Opus-every-card → Sonnet bulk + Opus rejects → free Python gates dominate → gold-sample 96–98.5% → four-rubric bake-off (H178) → G5/G6 human sheets → “no German before a human” (H1655) → machine-flag auto-reject. *Why useful:* A51 methods packet + print-readiness claims.
9. **Human-gating / review-sheet timeline** — markdown checkboxes banned → interactive HTML sheets → decisions.json apply path → residue pre-filter → positional-id drift fix → auto-reject of machine flags. *Why useful:* any session about to mint a sheet.
10. **Editorial / register timeline** — abbreviation maps, no-ё, doublet research, style guide of record (H1859), LES1990 comparison, mechanical RU style sweeps. *Why useful:* print-facing copy is a different lane from throughput.
11. **Edition-merge / DE-layer timeline** — single `pwg.txt` → 5-layer merge → no-PWG lane → re-glue Arm-A/B (synthesize-first loses) → addenda typology (5,603 senses) → DE OntoLex/TEI export track. *Why useful:* A49 and any “what is a card” discussion.
12. **Store-integrity / data-danger timeline** — root-level promote wipe risk → sub-card merge → overlay-preserving promote → store_write lock → content-mass gate → reconstructed-headword markers (H1080) → german_anchor provenance stamps. *Why useful:* FINDINGS-class integrity; never re-discover wipe modes.
13. **Host-health / live-gate reading log** — probe log as a **time series** (GO vs NO-GO, warm-up vs measured, 30 s vs 65 s policy, rate-limit hangs §270). *Why useful:* stops freezing “host blocked since DATE” as permanent truth.
14. **EN parallel-lane timeline** — FU1 pilot → head-splitter → LANG_PARITY gaps → gold adjudication H1070 → scale-up GO/NO-GO. *Why useful:* EN is SHARED machinery with intentional divergences, not a second copy of RU history.
15. **Research / papers timeline** — A49 (Petersburg self-layering) · A51 (LLM dictionary translation + bake-off) · A52 (launch failure taxonomy) · methods drafts under `pwg_ru/`. *Why useful:* anti-salami and “what is already a paper spine.”
16. **Corpus & TM asset growth** — 5 dicts → 1.09M lexicon → mined tier (10,132 @ 97% precision) → A/B/C grading → TMX 1.4b → rights-gated FAIR release queue. *Why useful:* any “reuse before translate” decision.
17. **Orchestration / multi-account timeline** — single Max session → ≤3-wide → four-account outer dispatch (H818) → profile fingerprints → account-switch packets → (planned) PC/prod/routines map. *Why useful:* H2175 Wave 1 and any concurrency debate.
18. **Residual population / coverage monitor** — verb roots done vs remaining · nominal · no-PWG · WAVE2_COVERAGE_MONITOR · store row counts over time. *Why useful:* “are we nearly done?” without trusting ambient `.ai_state` snapshots.

### Optional / lower priority

19. **Skill/runbook evolution** — when `/pwg-live-gate`, `/pwg-bounded-run`, `/pwg-drain`, `/pwg-window-close` appeared and which handoff forced each.
20. **Model-pin timeline** — which exact model IDs were hard-coded in harnesses when (bare-tier ban + provenance discipline).
21. **Windows/process-tree timeline** — Job Objects, kill-on-close, bare cwd, orphaned child classes (platform-specific ops history).

### Suggested writing order if a human wants more

1. **#5 Execution-route** (stops the most expensive stale-doc failures).
2. **#6 Gate genealogy** (pairs with this doc’s “every gate is a tombstone”).
3. **#7 Cost-model** (feeds A51/A52 and H2175 experiments).
4. **#12 Store-integrity** (danger facts that belong in the repo’s own memory too).
5. **#13 Live-gate readings** as a committed table regenerated from the probe log.

Each of these can be a short sibling under `RussianTranslation/docs/` named
`TIMELINE_<subject>_PWG_RU.md` (self-identifying filename) with a one-line
pointer from this file’s §6 and from `PIPELINE_HISTORY` “Where to go next.”

---

## 7. Standing lessons (approach-level, not gate-level)

1. **Quality was rarely the open problem.** From the first judge gate (37/38)
   through gold samples (96–98.5%), the models could translate. Process,
   cost, gates, and human idle time were the successive bottlenecks.
2. **Harvest before invent.** Attested Russian (dicts + corpus) is additive
   content, not just a prompt hint — that is the print-dictionary distinction
   from a raw MT dump.
3. **Deterministic gates beat LLM judges for scale.** Free Python gates became
   the acceptance path; LLM judging shrank to samples, rejects, and human sheets.
4. **Re-audit before re-translate.** Many “residuals” were gate false
   positives or presentation bugs (raw markup looking like German).
5. **Every expensive lesson became a constant or a module.** Concurrency
   cliffs, kill ceilings, reservation ledgers, overlay-preserving promote —
   the codebase is a fossil record of those lessons.
6. **Route economics dominate late-stage throughput.** Cache rewrite, cwd
   injection, and kill-ceiling variance explain more recent zero-card windows
   than translation difficulty.
7. **Do not freeze ambient status.** Live-gate is per-run; store counts move;
   “host blocked” is a reading, not a season.

---

## 8. Where to go next (reading order)

| If you need… | Open |
|---|---|
| Today’s operator loop | [`src/pilot/RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) |
| Engineering what-broke-when | [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| Editor-facing card format | [`pwg_ru.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru.md) |
| Deep operator manual | [`docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md) |
| Nonstop multilane plan (forward) | [`docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_pwg_nonstop_multilane_2026.md) |
| Quantitative launch failures | [`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md) + [`LAUNCH_FUCKUPS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_FUCKUPS.md) |

_Dr. Mārcis Gasūns_
