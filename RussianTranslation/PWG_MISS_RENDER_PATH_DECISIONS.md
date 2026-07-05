# PWG-Miss Render-Path Decisions

_Created: 05-07-2026 · Last updated: 05-07-2026_

This file records settled decisions for the PWG-less headword card-rendering gap
found during [H206](https://github.com/gasyoun/Uprava/blob/main/handoffs/H206-Sonnet_RussianTranslation_pwg_ru_nominal_worklist_pwg_miss_gap_05.07.26.md).
Do not re-ask these as open planning questions unless the topic is explicitly reopened.

## Context

[H206](https://github.com/gasyoun/Uprava/blob/main/handoffs/H206-Sonnet_RussianTranslation_pwg_ru_nominal_worklist_pwg_miss_gap_05.07.26.md)
(PR [#168](https://github.com/gasyoun/SanskritLexicography/pull/168), merged 05-07-2026, Sonnet 5
`claude-sonnet-5`) fixed [`src/pilot/nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py)
to stop silently dropping PWG-miss nominal candidates that DO have a real PW/SCH/PWKVN record —
232 deduplicated lemmas across the 3 already-run wordlists (pril5, pril10, sbornoe), tagged by
which layer(s) hit, parked in [`src/pilot/lexical_cores/pwg_miss_backfill_queue.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lexical_cores/pwg_miss_backfill_queue.md).

That fix stopped short of actually promoting these 232 lemmas into the live runnable queue,
because [`src/_pilot_gen_merged.py:gen_card()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_pilot_gen_merged.py#L99-L153)
hard-requires a non-empty PWG buf and bails (`return None`, logged as `MISSING in PWG`) before ever
reaching the generic `dm.merged()` loop that would otherwise pull in the PW/SCH/PWKVN layers. The
`.portrait.json` it would have produced is load-bearing well beyond `gen_card()` itself — consumed
by `window_selftest.py`, `coordinator.py`, `root_window_status.py`, `window_provenance.py`, and the
harness prompt-assembly scripts (`gen_opt_harness.py`/`gen_opt_harness2.py`), all of which assume a
PWG-shaped portrait exists per key. Per [FINDINGS.md §61](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#61-pw-only-headwords-outnumber-pwg-only-ones-6-to-1-pwg-is-not-the-sole-spine-of-the-local-layer-universe),
this is not an edge case: ~36% of the local headword union carries zero PWG record.

## Settled Decisions

1. **Build the no-PWG render path — yes, now (in principle), but sequenced behind Track A (see #3).**

   The gap is large enough (~26% of headwords measured concretely, 232 lemmas already queued
   from just 3 wordlists) that leaving PWG-less headwords permanently unrenderable would mean a
   real, non-trivial slice of translatable content never reaches the pipeline. Worth building, not
   permanently parking as a known limitation.

2. **Portrait depth: extend `microstructure.portrait()` to parse PW/SCH/PWKVN buf formats, not a cheap stub.**

   A minimal/empty stub portrait would satisfy the load-bearing consumers structurally but would
   deprive translators/judges of the sense-numbered scaffolding PWG cards get. The larger lift —
   teaching the shared microstructure layer to parse PW/SCH/PWKVN buf shapes into a real structured
   portrait — is worth the cost so PWG-less cards get comparable structural support during
   translation and QA.

3. **Priority: queue behind the active Track A H151/SLA-scaling effort — do not interrupt it.**

   Per `.ai_state.md`, Track A's 30-day SLA scaling on the PWG-rooted verb/nominal queue is the
   active priority. This render-path build is backlog: pick it up once the current drain/SLA push
   has headroom, not an interrupt to it.

4. **Quality label: flag PWG-less cards distinctly downstream — do not treat identically to PWG-based cards.**

   PW/SCH/PWKVN are of different vintage/provenance than PWG. Once the render path exists, cards
   built from them (no PWG base) must carry a distinguishing provenance marker through the
   translator prompt, judge pass, and any published/dashboard surface, so readers and the QA chain
   know the card rests on thinner/different-vintage source material than the PWG-rooted majority.

## Consequences / Next concrete action

- The 232-lemma [backfill queue](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lexical_cores/pwg_miss_backfill_queue.md)
  stays parked (not promoted) until this render path is built — per decision 3, that is scheduled
  after the current Track A SLA push, not immediately.
- When picked up, the implementing session must: (a) extend `microstructure.portrait()` (or add a
  parallel PW/SCH/PWKVN-aware portrait builder) per decision 2, (b) update `gen_card()` to fall
  through to the generic layer path instead of bailing on empty `pwg_bufs`, (c) add the no-PWG
  provenance marker required by decision 4 to the card, the translator prompt, and the judge
  pass, (d) re-run the promotion path over `pwg_miss_backfill_queue.md` once the render path is
  verified end-to-end.
- Decider: a human. Eliciting session: Sonnet 5 (`claude-sonnet-5`), 05-07-2026.

_Dr. Mārcis Gasūns_
