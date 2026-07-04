# Full PWG->Russian 30-Day SLA Plan

_Created: 04-07-2026_

## Target

Deliver a full PWG->Russian machine-translated pass in **under 30 calendar days**.
This is a full-dictionary target, not only the H151 verb-root drain:

- Whole PWG scope: `src/assembled_cards.jsonl` = **120,173 headword cards**.
- Expected translation units: **120k-160k sub-cards** after root/preverb expansion.
- Operating assumption: **24/7 if caps allow**, with no more than **3 concurrent
  LLM/Workflow translation lanes**.

The existing H151 handoff remains valid, but H151 is only one workstream inside
this SLA: it drains the remaining DCS-attested verb roots. The full SLA also needs
rootmap unblocking, non-root/noun bulk coverage, and publication-facing validation.

## Non-Negotiable Safety Rules

- Do **not** exceed **3 concurrent LLM/Workflow translation lanes**. The Slice-D
  18-wide run is the documented failure case.
- Wide parallelism is allowed only for deterministic work: enumeration, rootmap
  generation, audits, markdown/docs, TM validation, and publication export checks.
- Workflow output must be driven from the coding session and written
  programmatically; do not depend on a manual Max-surface save.
- Defect requeues must use `--no-tm`, so the TM cannot re-serve content that has
  already failed gates.
- Promotion is only through `promote_final_cards.py --gen-model-version <exact>`,
  followed by TM rebuild and validation.
- Exact model provenance is required everywhere; use `claude-sonnet-5`, not a bare
  `sonnet` alias.

## Workstreams

### 1. Translation Lanes

Run up to three LLM/Workflow lanes continuously, each following the current
production loop:

```powershell
python src\pilot\root_window_status.py <root-or-window>
python src\pilot\perf_preflight.py <candidate roots>
python src\pilot\gen_opt_harness2.py <root-or-window>
# run the generated Workflow from the coding session and write wf_output.json
python src\pilot\audit_window.py wf_output.json --root <root> --write-requeue
python src\pilot\promote_final_cards.py --gen-model-version claude-sonnet-5
python src\pilot\translation_memory.py build --lang ru
python src\pilot\translation_memory.py validate --lang ru
```

For H151 verb roots, use the live `verb_worklist.py` and `perf_preflight.py` order,
low-agent roots first. Roots marked `defer-calibrate` get dedicated sessions, not
tail-end opportunistic runs.

### 2. Rootmap Unblock Lane

Keep rootmap generation ahead of the translation lanes. The current H151 snapshot
showed a material blocker: hundreds of remaining roots were visible in the backlog
but not runnable because rootmaps were missing.

Daily rule:

```powershell
python src\pilot\verb_worklist.py --top 20
python src\pilot\verb_worklist.py --include-unrunnable
```

The unblock lane produces and verifies rootmaps for the highest-frequency blocked
roots before the translation lanes drain the current runnable queue. Missing
rootmaps must be tracked as SLA blockers, not hidden inside throughput numbers.

### 3. Non-Root / Noun Bulk Lane

The full PWG target is larger than DCS-attested verb roots. Run a parallel
deterministic planning lane over the assembled-card universe so nouns, adjectives,
compounds, indeclinables, cross-reference stubs, and already-TM-covered cards are
fed into translation in priority order.

The non-root lane must:

- consume `src/assembled_cards.jsonl` as the full-PWG scope anchor;
- pre-resolve exact TM hits before spending Workflow tokens;
- route degenerate cross-reference stubs through the no-LLM path when available;
- use existing assembled-card and translation-memory machinery rather than inventing
  a separate store;
- keep H151 verb-root work and noun/non-root work visibly separate in reports.

### 4. Publication Validation Lane

Every production day closes with publication-facing validation:

```powershell
python src\pilot\translation_memory.py build --lang ru
python src\pilot\translation_memory.py validate --lang ru
python src\pilot\window_selftest.py
```

The publication lane also verifies that promoted rows carry complete provenance,
that publication exports validate, and that the TM/card/fragment counts are
recorded in the daily log. A day is not SLA-countable unless promotion, TM rebuild,
and validation have completed for that day's translated work.

## Daily Operating Loop

1. Enumerate runnable and blocked work:
   `verb_worklist.py --top 20`, `--include-unrunnable`, and the assembled-card
   backlog for non-root work.
2. Preflight the next roots/windows and sort by low expected agents first.
3. Keep the rootmap unblock lane at least one day ahead of the three translation
   lanes.
4. Run up to three translation lanes, never more.
5. Audit every output, then run transient and defect requeues. Defect requeues use
   `--no-tm`.
6. Promote only gate-passing work, rebuild TM, and validate publication assets.
7. Record daily numbers: cards/sub-cards promoted, clean/partial/error counts,
   agents, wall-clock, token/cost notes, blocked rootmaps, and next queue head.

## Throughput Gate

The midpoint full-PWG estimate is **140k sub-cards**. To finish in 30 calendar
days, the sustained rate must average about **4,700 sub-cards/day**. The existing
economics note measured **800-1,000 cards/hour at <=3-wide** under the clean
harness, so the SLA is plausible only if translation lanes can stay fed and caps
do not force long idle periods.

After the first **48 hours** of SLA operation:

- If sustained promoted throughput is **>= 9,400 sub-cards** with publication
  validation clean, continue the current plan.
- If throughput is below that threshold because of rootmap starvation, prioritize
  rootmap unblock work and pause public under-30-day claims until the runnable
  backlog covers at least 72 hours of translation.
- If throughput is below that threshold despite a healthy runnable backlog, pause
  the SLA and write a separate implementation plan for coordinator machinery:
  dispatcher/lease ownership, single store-owner promotion, per-lane artifact
  registry, rate/cap tracking, and daily dashboarding.

## Done Criteria

- Full PWG RU scope is translated or explicitly no-LLM-passed where appropriate.
- H151 reports no remaining DCS-attested verb roots.
- Non-root/noun full-PWG backlog is empty against `src/assembled_cards.jsonl`.
- All promoted rows have exact model/pipeline provenance.
- TM card, fragment, and publication exports validate.
- The final daily log records the full-scope counts, residuals, and publication
  validation result.

