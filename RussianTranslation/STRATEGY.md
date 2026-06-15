# pwg_ru — strategy & operating notes (2026-06-15)

## 0. Mandate: this becomes a PRINTED dictionary — quality > quantity

Every published card must be correct, idiomatic, terminologically consistent,
and lossless in its non-German markup. Throughput is secondary. Concretely the
pipeline enforces quality by:

- **Lossless masker** — [src/pwg_mask.py](src/pwg_mask.py) round-trips 123,365 /
  123,366 records byte-exact; the runner asserts per-card round-trip and routes
  the one failure to manual review. No Sanskrit / ref / markup is ever altered.
- **Harvest-first reuse** — translations are anchored to *existing human*
  Russian (dictionaries + the parallel corpus), not invented from scratch.
- **Judge every card** — Opus 4.8 judges each card (severity 1–5); nothing is
  published unjudged.
- **Re-translate rejects** — severity ≥ 3 cards go to an Opus re-translate pass.

## 1. The corpus-first reorder (the key change, 2026-06-15)

The first scaled run translated the `a–` section using the **5 extracted
dictionaries** (koch/kow/kna/fri/smirnov) as the reuse layer — but **before** the
DeepSeek **corpus word-alignment lexicon** (P1) existed. For a printed
dictionary that is the wrong order: build the durable corpus reuse FIRST, so
every card harvests the maximum attested Russian *before* a word is translated.

**New phase order:**

1. **P1 — corpus word-alignment lexicon (DeepSeek/OpenRouter).** One bulk pass
   over the 122+ verse-aligned Sanskrit↔Russian translations in SamudraManthanam
   → a durable Sanskrit-lemma → Russian-equivalent lexicon (gitignored).
   *Blocked on the DeepSeek + OpenRouter keys.*
2. **Harvest** — per headword, assemble attested Russian from: 5 dictionaries +
   the new corpus lexicon + the mw_ru seed. These become **additional attested
   senses** in the card.
3. **Translate** — Sonnet 4.6 renders the German gaps, *anchored to the
   harvested senses* (so terminology matches existing usage).
4. **Judge** — Opus 4.8, every card.
5. **Re-translate** — Opus on severity ≥ 3.
6. **Stage-4 corpus gate** — [src/corpus_gate.py](src/corpus_gate.py) annotates
   correctness vs. independent dicts + agreement vs. KOW.

The ~216 `a–` cards already produced are a **proof of concept** (the pipeline
works end-to-end at 95% first-pass). For the printed edition they should be
**re-harvested + re-translated corpus-first** once P1 exists, for the extra
corpus senses and cross-card consistency — they are provisional, not final.

## 2. Concurrency, speed, throughput

- **Agents at once:** a workflow caps concurrency at **min(16, CPU cores − 2)** —
  so roughly **8–14 subagents run simultaneously**. A 40-card batch spawns 80
  agents (40 Sonnet translate + 40 Opus judge); the rest queue and drain as slots
  free. Wall-clock ≈ **6 min per 40-card batch** when not rate-limited.
- **The real throttle is the model session limit** (the Max-subscription quota),
  not the agent cap. It was hit at ~batch 5 (≈216 cards) and resets on a schedule
  (e.g. 19:00 Europe/Moscow). When hit, agents fail until reset — the loop pauses
  and resumes (the store is append-only and resumable, so no work is lost).

### How to maximise speed without losing quality

1. **Corpus-first** (P1) is itself a speed win: better reuse → fewer re-translate
   rounds → less rework. Quality and throughput both improve.
2. **Offload judging to DeepSeek** once keys land. Translate (Sonnet) + re-translate
   (Opus) stay on Max; the high-volume *judge* moves to the flat-rate DeepSeek API.
   This removes ~half the load from the Max quota → roughly doubles sustainable
   cards/day **without** dropping the judge-every-card guarantee.
3. **Keep batches ≈ the concurrency cap × a few waves** (40 is well-sized). Bigger
   batches do not run faster (same cap) — they just queue longer.
4. **Run continuously across quota windows.** The event-driven loop
   (build → translate+judge → collect) resumes automatically; let it grind.
5. **Do NOT cut QA** to go faster — the quality mandate forbids it. Speed comes
   from reuse + cheaper judging, never from skipping the judge.

## 3. State & next step

- Pipeline proven; ~216 provisional `a–` cards (95% first-pass publishable).
  Store is gitignored append-only (`src/pwg_ru_translated.jsonl`).
- Loop **paused** (session limit + corpus-first redirect).
- **Next:** provide `DEEPSEEK_API_KEY` + `OPENROUTER_API_KEY` in a gitignored
  `src/.env`; then P1 (corpus lexicon) → re-harvest → translate corpus-first.

See also [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md),
[PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md),
[SAMUDRA_INTEGRATION.md](SAMUDRA_INTEGRATION.md), [PILOT_RESULTS.md](PILOT_RESULTS.md).
