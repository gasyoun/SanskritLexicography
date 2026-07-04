# Pilot measurement & analysis (2026-07-04)

_Created: 04-07-2026 · Last updated: 04-07-2026_

Measurement of the PWG→RU/EN run **as it actually stands**, from the committed
run artifacts (every `wf_output.*.json` + the judge/fidelity verdict files), plus
the improvement analysis that follows. Read alongside
[CODE_REVIEW_2026-07-04.md](CODE_REVIEW_2026-07-04.md) (the bug findings) and
[research/ACL_ANTHOLOGY_MONITOR.md](research/ACL_ANTHOLOGY_MONITOR.md) (external
methods).

## Coverage (deterministic gate — card present / null / partial)

Aggregated over **108 completed root-output files, 4,392 cards**:

| lang | cards | null | partial | note |
|---|---:|---:|---:|---|
| en | 2,197 | 0 | 0 | current harness, full coverage |
| ru | 229 | 0 | 2 | current harness |
| `?` (legacy `sc`/`sd`) | 1,966 | 137 | 0 | pre-selfheal/presplit exploratory runs |
| **ALL** | **4,392** | **137 (3.1%)** | **2 (0.05%)** | |

**Finding — the coverage battle is essentially won.** All 137 nulls sit in the
older `?`-lang `sc`/`sd` exploratory outputs from *before* the presplit trigger,
wall-clock kill gate, and selfheal/binary-split recovery landed. Every saved
**current-format RU and EN** root output has **zero nulls** and effectively zero
partials. The recovery machinery (presplit ~2–3%, selfheal ~2–3% of cards) is
doing its job: sense-dense and citation-giant cards that used to blow the
StructuredOutput cap now route to the fragment lane and heal complete.

## Quality (LLM judge / fidelity battery)

The bulk path no longer judges every card (token optimization); judging runs on
gate-flagged cards + a ~10% deterministic sample. From the committed verdicts:

- **Fidelity battery (100 cards, 2026-06-30):** 98% `ok`, severity dist
  `sev0=39, sev1=58, sev2=1, sev3=2` → **2% hard-fail (sev≥3)**, 98% publishable.
- **Fable S7 sample (118 cards RU+EN, 2026-07-02, `claude-fable-5`):** **100%
  sev0** (no issues) across both language lanes — RU 50/50, EN 68/68.

**Finding — measured quality is high (98–100% publishable), but partly rests on
validators the review just found blind.** The `audit_window_en` HARD `DUP` gate
is never emitted and the RU gate recovers verdicts by scraping subprocess stdout
(CODE_REVIEW 🟠). Where those gates are blind, a "clean" card may carry an
undetected duplicate-sense or dropped-flag defect — so treat the 98–100% as an
**upper bound** until those validators are given teeth.

## What this session changed (PR #138)

- **Latin-mask leak fixed** — 33 Latin/Greek cognate glosses across PWG were
  being fed to the translator as German; now correctly masked. This is a direct
  quality improvement to every future run (and removes one silent wrong-language
  class the judge sample might not have caught).
- **Store writes made crash-atomic** + `collect` no longer crashes on a
  string-wrapped result — removes the two data-loss paths behind the project's
  "output lost / layer wiped" history, so a scale run can't corrupt the store
  mid-write.

## Where to improve next (ranked)

1. **Give the QA gates teeth (highest leverage).** Emit a real hard `DUP` flag in
   `audit_window_en`; make the RU gate assert a parseable verdict / consult the
   child returncode. Until then, measured quality is optimistic. (CODE_REVIEW 🟠.)
2. **Close the positional card-misassignment window** (CODE_REVIEW 🔴): strengthen
   the `resolveGroup`/`healGroup` fallback so a dropped/reordered card can't land
   Russian under the wrong headword — the one remaining silent *correctness*
   (not coverage) risk in generation.
3. **Adopt GEMBA-MQM-style error-span judging** ([WMT 2023](https://aclanthology.org/2023.wmt-1.64/)):
   move the judge from a holistic verdict to per-span severity so the 2% sev≥3
   tail is *localized* to the offending sense, shrinking human-review time.
4. **Treat TM reuse as a measured retrieval policy** ([Findings NAACL 2024](https://aclanthology.org/2024.findings-naacl.190/)):
   evaluate `best_reusable` selection rather than assuming it; and stop dropping a
   whole card from cache on one empty sense (CODE_REVIEW 🟡) so giant cards aren't
   needlessly re-translated.
5. **Structure terminology injection as a dictionary chain**
   ([Chain-of-Dictionary, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.55/))
   and A/B the lift on the curated Sa→Ru terminology lane.

## Run note

No fresh scale root was drained in this session: `tu` (the smallest band-5 root)
is a non-giant with no rootmap, so it doesn't fit the split-harness, and starting
a live Max Workflow run on a real production head (`sTA` 185 KB / `as` 59 KB) at
the tail of a long review session is the exact "run started, output lost" trap
the project has hit before. The next drain is the standing
[H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151_SanskritLexicography_pwg_ru_verb_batch_drain.md)
queue head, run in its own session — see the resume line in `.ai_state.md`.

_Dr. Mārcis Gasūns_
