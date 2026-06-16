# Failure gallery — how it looked when it went wrong, and after the fix

A curated record of real defects this project hit, each with the **bad sample**,
the **root cause**, the **fix**, and the **good sample** after. Purpose: to
demonstrate the methodology's value — these are the things that *silently* go
wrong in AI-assisted lexicography, and the QA that catches them. Machine-readable
companion: [failures.jsonl](failures.jsonl).

Ongoing capture is automatic: the corpus side by `_audit.py` (each build
milestone), the translation side by `run_batch.py review` (the editor worklist).

---

## F1 · Placeholder fabrication (the headline) — `2026-06-16`

**Symptom.** 81% of the corpus lexicon (166,143 / 204,266 rows) was pure
invention — fluent Russian attributed to verses that *have no translation*.

**Bad sample.** Source `12_mahabharata-shantiparva:12.8.1` has `ru = "…"` (an
untranslated placeholder). The aligner nonetheless emitted:

```
sa=arjuna  ru=Арджуна        ← invented
sa=vāc     ru=сказал          ← invented
sa=vākya   ru=слово           ← invented
sa=akṣamī  ru=нетерпимый      ← invented
```

None of these Russian words exist in any translation — DeepSeek hallucinated an
alignment against `…`. Whole works affected: `shantiparva` (99.8% placeholder),
`anushasanaparva` (100%).

**Why.** `pairs_of()` only tested `ru` *truthiness*, and `"…"` is truthy → the
empty verse was sent for alignment. The output is fluent Cyrillic, so it passes
every surface check — **invisible to QA**.

**Fix.** A Cyrillic-presence guard: `has_cyr()` in `pairs_of()` (placeholder →
not aligned → 0 API calls), plus write-step guards and `build_strata` requiring a
Cyrillic translation. Recovered the on-disk lexicon to 26,277 genuine rows.

**Good sample.** Placeholder works now yield 0 fabricated rows; only the 22
genuinely-translated `shantiparva` prose groups survive:

```
12_mahabharata-shantiparva:12.2.12-18  (ru="Когда Карна так обратился к Дроне…")
sa=karṇa   ru=Карна           ← attested
sa=droṇa   ru=Дрона           ← attested
sa=ukta    ru=обратился       ← attested
```

**Lesson.** *Truthiness ≠ translated.* A real rendering must contain Cyrillic.
Always re-scan a generative corpus build for source-placeholder leakage before
trusting volume.

---

## F2 · Footnote overwrote the translation — `2026-06-16`

**Bad.** A verse group with a real translation (`seg=ru`) and commentary
footnotes (`seg=comm1…commN`) was keyed by `lang`, so the *last footnote*
overwrote the actual translation. The card's Russian came from an editor's note,
not the verse.

**Fix.** Key by `seg`; emit both, tagged `kind=translation` vs `kind=commentary`.

**Good.** The verse translation and each commentary note are aligned separately
and labelled; commentary carries `+comm` in the harvest.

---

## F3 · Dhātu notation leaked into the key — `2026-06-16`

**Bad.** DeepSeek sometimes emits root notation: `sa=√gam`. `form_key` passed the
`√` through, producing `slp1=√arT`, `slp1=√kruS` — keys that can never join the
SLP1-keyed lexicon (~0.07% of rows).

**Fix.** Strip `√` in `to_slp1()` before `form_key`.

**Good.** `slp1=arT`, joinable.

---

## F4 · Commentary cross-segment duplication — `2026-06-16`

**Bad.** A group with many commentary notes (up to 32) emitted each note's
alignment separately with no collapse: `01_mahabharata-adiparva:1.2.105-129`
produced `(yudDa→битва) ×44`, `(vaDa) ×34` — frequency inflated ~13–44×, which
would corrupt any salience/sense-ordering downstream.

**Fix.** Per-batch dedup of `(group, slp1, ru, kind)`.

**Good.** One row per distinct rendering; counts are real.

---

## F5 · "Harvestable" stratum with zero data — `2026-06-16`

**Bad.** `build_ls_map` marked Ṛgveda/kāvya `harvestable` from *membership*, but
mid-build the lexicon had **0 Ṛgvedic rows**. A Ṛgveda-cited sense would silently
fall back to *Epic* Russian — an era mismatch presented as fact.

**Fix.** `corpus_harvest.py coverage` reports per-stratum rows and flags
`EMPTY`/`thin`; do not assemble print cards whose `<ls>` resolves to a
below-floor stratum.

**Good.** `coverage` shows Ṛgvedic 0% → 9.1% as the build reaches Rigveda; the
gap is visible, not hidden.

---

## F6 · Cost mis-projection ($260 scare) — `2026-06-16`

**Bad.** The full-corpus cost was extrapolated from the *comment-dense*
Atharvaveda (~74 alignments/verse) → a frightening $260 projection.

**Fix.** Biggest-first ordering (epics dominate, fewer alignments/group) + a
live-window measurement in `_watch.py`.

**Good.** Honest projection ~$30–37, stable across milestones.

---

## F7 · Trusting elapsed time on a frozen build — `2026-06-16`

**Bad (twice).** (a) A stalled DeepSeek connection froze the whole ThreadPool;
elapsed-time on the frozen output gave a bogus ~25 h ETA. (b) Later, a dead build
(process gone ~4 h) went unnoticed because only the **row count** was checked,
not file freshness.

**Fix.** `timeout=(10,60)` so no worker hangs; `_watch.py` measures a live
window and self-detects stalls; **always verify file mtime, not just row count.**

**Good.** Liveness is `mtime ≈ 0 min ago`; the watcher emits `STALLED` within
~6 min of any freeze.

---

## F8 · No provenance / rights / human review — `2026-06-16` (methodology review)

**Bad.** The LLM-translated card recorded no model id / prompt hash / source
commit (not reproducible); modern copyrighted glosses (Кочергина, Смирнов, Фриш)
sat verbatim in the card body; an LLM verdict was the *final* word with no human
queue.

**Fix.** Provenance stamping + persisted senses; `corpus_gate.RIGHTS` +
per-sense `publishable` flag + CC BY-SA 4.0; `review_status` state machine +
`run_batch.py review` editor worklist.

**Good.** Every card is reproducible and rights-aware; 11 flagged cards sit in a
severity-sorted human queue instead of going silently to print.
