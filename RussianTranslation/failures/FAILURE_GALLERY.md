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

---

## F9 · The auditor cried wolf — verify before you purge — `2026-06-16`

**Bad (the alarm).** At 95% the auditor flagged `shukasaptati` (18) then
`01_atharvaveda` (10) as placeholder-leak — the same signature as the F1
fabrication. The tempting move: purge them.

**Why it was a FALSE POSITIVE.** All 28 were `kind=commentary` rows with *correct*
Russian (`brahmā→Брахма`, `śarman→защиту`). `_audit.py`'s leak check asked "does
the group's `seg=ru` carry Cyrillic?" — but a commentary row is legitimate when
the group has a Cyrillic commentary, or (AV 21.4) a real `seg=ru` translation
while the `comm1` is just a cross-reference (`"4c-d. = I» 20…"`). The data was
clean; the *check* was too strict.

**Fix.** Make the leak rule the true fabrication signal: a row leaks only if its
group has **no Cyrillic source segment at all** (neither `ru` nor `comm`).

**Good.** Audit CLEAN; no legitimate row purged.

**Lesson.** A QA signal is a hypothesis, not a verdict — reproduce the specific
rows and read the source before destroying data. (A minor legacy item remains: a
few pre-fix commentary rows were aligned against non-Cyrillic reference notes and
mis-tagged; the Russian is the verse's, harmless, queued for the post-build
re-stamp.)


---

## F10 · Windows ate the capital letters — case-insensitive filenames — `2026-06-17`

**Bad.** The NWS scrape wrote one `pilot/nws/<key>.json` per headword, named by the
raw SLP1 key. On Windows `aMSa.json` and `AMSa.json` are the **same file**, so the
second variant's existence-check returned True and it was skipped as "already done"
— **silently lost**. The a-section alone: **1,795 colliding groups, 2,311 headwords
dropped** (e.g. `ABIka`/`aBIka`/`aBika` = ābhīka/abhīka/abhika → one file). The retry
pass even reported *"24621 done, 0 to fetch"* while 2,311 files were missing — the bug
wearing the mask of completion. Concurrency made it worse: 8 workers could both pass
the existence check and overwrite via `os.replace` (last-writer-wins).

**Why.** SLP1 is **case-sensitive** — uppercase encodes distinct phonemes (`A`=ā,
`S`=ś, `B`=bh, `R`=ṇ). NTFS is **case-insensitive**. Using the key directly as a
filename collapses every case variant.

**Fix.** `safe_name()` encodes each uppercase letter as `_`+lowercase → an injective,
all-lowercase stem with no case-insensitive collisions (`aMSa`→`a_m_sa`, `AMSa`→
`_a_m_sa`). **Proven**: 24,621 keys → 24,621 distinct case-insensitive names. Existing
files migrated by their internal `key1`; the lost variants re-fetched.

**Good.** Full a-section with **zero collisions** — and the bug was caught on the
**15% a-section sample BEFORE scaling** to all 167,990 headwords, where it would have
quietly lost ~15k.

**Lesson.** Never use externally-supplied, case-sensitive identifiers as filenames on
a case-insensitive filesystem. And a clean-looking "completion" can hide silent data
loss — **audit the representative sample before you scale**, not after.

---

## F11 · The translator narrated editorial intent it could not know — `2026-06-17`

**Bad.** First merged-layer pilot (`anna`). The Sonnet translator, folding PW + NWS into
the PWG entry, wrote *"[PW] omits m. Sonne **as unreliable**"* and listed PW's own sense
2c (*Wolke* "cloud") as a brand-new *"[PW new]"* addition, duplicating it. The Opus
judge (severity 3, not publishable) confirmed: PW silently drops *Sonne* — it never
states a **reason**; and *Wolke* is ordinary PW structure, not a new addition.

**Why it's the dangerous kind.** No citation, date, or gloss was invented — every
*content* claim checked out (the judge even cleared the suspicious "1349 A.D.", Geldner
1907:10, and the King Ānāka sense as genuinely in NWS). What was fabricated was
**editorial meta-narration**: a confident *why* the source never gives, and a *"[new]"*
label applied without checking the earlier layer. This reads as scholarship but is
unsourced inference — exactly what a printed dictionary must not carry.

**Fix.** Two locked guards in
[`6_merged_translate.md`](pwg_ru_prompts/6_merged_translate.md): (1) attribute facts to
layers, never narrate *why* a layer changed something; (2) never mark a sense "[new]"
without confirming it is absent from the earlier layer, and never re-list it.

**Good.** With guards 1–2 the card states only what each layer *carries* (PWG: m.+n.;
PW: n. only; NWS: re-adds an m. proper-name) — no invented motive, no phantom "new".

**Lesson.** Fabrication isn't only invented citations. A model will also invent the
*editorial story* — why an editor dropped or added something — which sounds like
expertise and is just as false. Judge for unsourced intent, not only unsourced facts.