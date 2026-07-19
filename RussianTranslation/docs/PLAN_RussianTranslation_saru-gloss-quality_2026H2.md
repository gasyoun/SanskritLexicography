# PLAN — Sa→Ru gloss layer, quality uplift (2026 H2)

_Created: 19-07-2026 · Last updated: 19-07-2026_

**Index / cover doc.** This is the single entry point for the Sa→Ru gloss-layer uplift.
A fresh agent executes it unattended by reading this file top-to-bottom, then the four
layer docs it links. Every decision a builder would hit is ruled below — a dangling
`@DECIDE` in a wave-1 path is a defect here, not a feature.

Execution handoff: [H1349-Opus_RussianTranslation_saru-gloss-quality-uplift_19.07.26](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1349-Opus_RussianTranslation_saru-gloss-quality-uplift_19.07.26.md).

## Goal (one paragraph)

The Sa→Ru gloss layer (three glossaries — 190,838 surface forms / 40,370 lemmas /
2,021 verb roots — built from `corpus_lexicon.jsonl`, published at
[gasyoun.github.io/SanskritRussian](https://gasyoun.github.io/SanskritRussian/)) is
**documented for coverage but never measured for accuracy**. Every published number
(87.1 % token coverage) is a resolution rate; nothing measures whether a rolled-up gloss
is *correct*. The upstream alignment is measured at 84.4 % pair precision — that error
propagates into the rollup and is then compounded by an **unvalidated lemmatization join**
(≥2-char longest-suffix root rule, Vidyut "most-entries-then-shortest" tiebreak, marker
recovery), each with known code defects. This span makes the layer **honest, measured,
and consumable**: fix the defects, publish a per-tier precision figure, attack the largest
miss classes with *reused* tooling, and wire the glossary into the Tier-1 pwg_ru/mw_ru
translation-memory path.

## The four layer docs

| Layer | Doc |
|---|---|
| Waves, deliverables, non-goals | [ROADMAP_RussianTranslation_saru-gloss_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ROADMAP_RussianTranslation_saru-gloss_2026H2.md) |
| Component boundaries, data model, build-vs-reuse | [ARCHITECTURE_RussianTranslation_saru-gloss.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/ARCHITECTURE_RussianTranslation_saru-gloss.md) |
| File-level, step-ordered build sequence | [IMPLEMENTATION_RussianTranslation_saru-gloss.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_saru-gloss.md) |
| Acceptance criteria, proof commands, risk register | [VERIFICATION_RussianTranslation_saru-gloss.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/VERIFICATION_RussianTranslation_saru-gloss.md) |

## Decisions taken (Phase-2 interview, 19-07-2026)

| # | Decision | Ruling | Rationale |
|---|---|---|---|
| D1 | Scope of "improved" | All four goals, sequenced | Not just one axis — defects, measurement, coverage, downstream, in dependency order. |
| D2 | Wave order | **Defects → measure → coverage → downstream** | A gold set measured against a defective rollup measures the wrong artifact and must be re-run; fix first. |
| D3 | Public accuracy claim | **Add an honest "coverage ≠ accuracy" caveat now** | Ship to README + `index.html` in wave 1, citing 84.4 % upstream pair precision as a ceiling, before any measurement. |
| D4 | Gold annotator | **LLM panel now, human sample slot later** | Same shape as the existing `precision_report.md` (panel + adversarial verify). Explicitly **model-vs-model, NOT gold** per the org gold-provenance audit. |
| D5 | Gold scope | **Two-axis: tier × frequency stratified** | Per-tier precision (dcs/vidyut/marker) isolates which heuristic fails; frequency stratum gives user-experienced accuracy. |
| D6 | Annotation rubric | **Lemmatization + top-gloss judged separately** | Two independent verdicts per item, separating pipeline error from corpus/alignment error — you learn *which stage* to fix. |
| D7 | Compound splitter | **Reuse, do not build** | `vidyut.cheda` v0.4.0 is installed; `kosha/scripts/compare_sandhi_methods.py` already benchmarks segmentation. A homegrown splitter fails the prior-art gate. |
| D8 | Republish published data after code fixes | **Fix code now, regen+republish in a later GATED pass** | The unattended run lands script fixes + tests + a delta report; touching the published `.tsv`/`.jsonl` is out of scope and needs a human GO. |
| D9 | Acceptance bar | **Regression tests + a delta report per wave** | Each fix gets a known-bad fixture test; each wave commits a before/after counts table. Machine-checkable, no human mid-run. |
| D10 | Downstream consumer (wave 4) | **pwg_ru / mw_ru translation memory** | Feeds the Tier-1 RussianTranslation dictionary-card path directly — highest strategic payoff. |
| D11 | Canonical doc owner | **SanskritRussian owns method/coverage/typology/accuracy; pipeline repo keeps build-only + pointer** | Users land on the data repo; the pipeline README shrinks to a runbook. Canonical doc gets a `.meta.md`. |
| D12 | Gold execution depth | **Build scaffold + run the LLM panel this run** | Produce a measured per-tier precision this run, labelled model-vs-model; human spot-check left as a `@DO`. Fully unattended. |

## Autonomy contract (verbatim — the unattended-execution rules)

The execution agent runs 5–8 h with no human reachable. It MUST obey the following.

- **On unplanned ambiguity:** apply the plan's marked default, log the call in
  `RussianTranslation/.ai_state.md` Dev Notes, and continue. Park-and-skip an item ONLY
  when no default in this plan applies. Never halt the whole run for a single fork.
- **Commit authority:** waves 1–4 code + doc changes land via a **git worktree → PR →
  auto-merge**, no confirmation prompt (handoff-scoped autonomy rule; SanskritLexicography
  is a guarded main-tree repo — a worktree off `origin/master` is mandatory, never commit
  in the shared checkout).
- **Stop conditions — halt and leave a note rather than improvise when:** (a) a required
  input file is absent (`dcs_full.sqlite`, `vidyut` kosha data, `corpus_lexicon.jsonl`);
  (b) a regeneration would be needed to proceed (D8 fences that off); (c) a change would
  touch a fenced path (below); (d) a wave's regression tests cannot be made to pass after
  one genuine fix attempt.
- **The hard fence — the agent MUST NOT touch:**
  1. **The published `SanskritRussian` data files** — no writes to `.tsv`/`.jsonl`/`.gz`/`md/`
     data in `gasyoun/SanskritRussian`. Docs (README, caveat block, `index.html` copy) ARE allowed.
  2. **`corpus_lexicon.jsonl` and `build_corpus_lexicon.py`** — no re-running the 290 MB
     DeepSeek alignment, no touching `src/.env` / the API key. Upstream is out of scope and costs money.
  3. **The `gold/` human-protocol machinery** — reuse `gold_sample.py`, `gold_agreement.py`,
     `HUMAN_GOLD_PROTOCOL.md` as-is; the new gold set plugs into them, it does not rewrite them.
  4. **Any Tier-0 / revenue repo** (Systema-Sanscriticum et al.) — wave 4 wires pwg_ru TM
     inside RussianTranslation only.

## Wave summary (detail in the ROADMAP)

1. **Wave 1 — Defects + honesty.** Fix pseudo-roots (`build_dcs_maps.py:111`), 3rd-homograph
   blind spot (`build_rollup_glossaries.py:213`), unwritten Vidyut ambiguity
   (`build_vidyut_fallback.py:79`); consolidate the two README copies to one canonical doc +
   pointer; add the coverage≠accuracy caveat; each fix gets a regression test.
2. **Wave 2 — Measure.** Tier × frequency stratified sample; lemmatization + top-gloss rubric;
   run the LLM panel + adversarial verify; publish a per-tier precision report (model-vs-model),
   plug into `gold/`.
3. **Wave 3 — Coverage.** Attack the 48,646 unrecognized simplexes (sandhi-normalization
   retries) and the 20,823 long compounds via **`vidyut.cheda`** (reuse), measured against the
   wave-2 baseline.
4. **Wave 4 — Downstream.** Wire the glossary as a lookup layer into the pwg_ru/mw_ru
   translation-memory path.

## Autonomy-readiness gate verdict

**PASS.** Every wave-1 deliverable has an architecture spec, ordered implementation steps,
an acceptance criterion, and identified risks (see the four layer docs). Zero blocking forks
remain — all twelve decisions are ruled; the one genuinely deferred item (data republish, D8)
is fenced off with a chosen default (fix-code-only). Prior-art verdicts are recorded (D7):
nothing scheduled reinvents an existing asset. The autonomy contract covers the plausible
ambiguities the audit surfaced.

_Dr. Mārcis Gasūns_
