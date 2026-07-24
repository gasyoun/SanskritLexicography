# RussianTranslation — results log

_Created: 09-07-2026 · Last updated: 24-07-2026_

Append-only, reverse-chronological. Each entry: date, context, model tier, table.

## 24-07-2026 — c2 medium50 w1 forensics: only-b0 / all-nulls = `--max-agents 1` starvation

Executor: Grok 4.5 (session) · gen model: Sonnet 5 (`claude-sonnet-5`) · profile: **c2 Pro**
(not Max) · keys: `nakzatra` / `sarvatra` / `sakft` · artifacts under
`src/pilot/output/c2_m50_w1*` (gitignored). Ledger:
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) id `C2_M50_W1_MAX_AGENTS1_2026-07-24`.

| run | config | `--max-agents` | ok/null | attempts seen | translate/heal spent | budget_stops | cost USD | terminal |
|---|---|---:|---|---|---|---:|---:|---|
| full w1 | c2 full profile | **1** | 0/3 | **b0 only** (success 161.8s) | 1 / 0 | **24** | 0.599 | all errors `selfheal-nothing-resolved` |
| stripped w1 | c2-stripped (H1517) | **1** | 0/3 | **b0 only** (timeout 180.3s) | 1 / 0 | **23** | 0.000 | same error stamp |
| fix w1 | c2 full profile | **omit** (manifest 19/41) | aborted | b0 timeout + **many** `heal:nakzatra#g*` + b1 | multi-spawn | n/a (HardFailure) | partial (~0.50+ on last call) | **`rate_limit`** session limit; resets 15:30 Europe/Moscow |

**Root cause (operator/process, not Pro-host):** `--max-agents N` caps **total** model
spawns (translate+heal) for the whole run. `N=1` spends the budget on the first batch;
remaining work refuses as `budget_exceeded` without spawning; `self_heal` overwrites notes
with `selfheal-nothing-resolved`. Smoking gun triad: `budget_stops ≫ 0` +
`translate_agents_spent=1` + single `b0` in `headless_attempts`.

**Guardrail:** do not copy `--max-agents 1` from single-key canaries onto multi-key windows.
**Separate residual:** c2 Pro session limit blocked the fix-run before a clean 3/3; re-run
after reset without the flag.

## 20-07-2026 — Sa→Ru gloss layer, wave 4: read-only TM lookup wired (H1349 W4 — H1349 COMPLETE)

Downstream wave: [`src/saru_gloss_tm.py`](src/saru_gloss_tm.py) `GlossTM` exposes the lemma +
root gloss layers as a **read-only** lookup for the pwg_ru/mw_ru card path — given a Sanskrit
lemma/root (SLP1) it returns ranked candidate Russian renderings. Additive consumer only; it
does not touch `pilot/translation_memory.py`, the store, or anything the safety-plan PRs
#547/#550 touch (the wave-4 risk fence). Smoke test on the published `SanskritRussian` data:

| query | layer | top candidates |
|---|---|---|
| `gam` (prefer root) | root | пришел (196) · отправился (177) · ушел (141) · пришли (100) |
| `karman` | lemma | действия (240) · деяния (186) · действие … |

Fixture-backed regression test (`tests/test_saru_gloss_tm.py`, 6 cases) wired into CI;
PROJECT_INTERLINKS glossary downstream row flipped planned→wired. **This closes H1349** —
waves 1 (defect fixes) + 2 (measured 85% precision) shipped; wave 3 (coverage) a measured
NO-GO (DEAD_ENDS §11); wave 4 (this) wires the read-only consumer.

## 20-07-2026 — Sa→Ru gloss layer, wave-3 coverage spike: vidyut-cheda NO-GO (H1349 W3)

Tried recovering the 78,842 unresolved forms via `vidyut.cheda` compound segmentation
(D7 reuse). **Measured NO-GO.** A strict gate (≥2 tokens + every member glossable,
[`src/build_compound_split.py`](src/build_compound_split.py)) recovers 28,673 forms (36.4% of
unresolved / 55,008 tokens) — but a 2-judge panel (Opus 4.8 `claude-opus-4-8` + Sonnet 5
`claude-sonnet-5`) on 40 gated recoveries scored segmentation **28% both-correct / 72%
either-wrong**, gloss **18% both-correct / 60% either-wrong / 40% acceptable**. Against the
wave-2 baseline (85.3% gloss) that is a catastrophic regression — ~half the recoveries are
outright wrong. Root cause: vidyut-cheda is a *running-text* segmenter; on isolated OOV forms
it shatters inflected/dual/plural words into stem + spurious glossable particle (`sahadevaśca`
→ `sahadeva`+`ca`, head "и"). **Decision: not wired in** — the 85% layer stays unregressed;
the 78,842 stay an honest coverage gap. Recommended path (backlog): the DharmaMitra **neural**
segmenter over the aligned *verse text*, which kosha's `compare_sandhi_methods.py` already
benchmarked as near-perfect and far above vidyut-cheda. Full write-up:
[`gold/saru_gloss_wave3_cheda_coverage.md`](gold/saru_gloss_wave3_cheda_coverage.md).

## 20-07-2026 — Sa→Ru gloss layer, measured precision (H1349 wave 2)

First **accuracy** measurement of the gloss layer (every prior number was coverage).
**Model-vs-model LLM panel, NOT human gold** (org gold-provenance rule): 3 judges
(Opus 4.8 `claude-opus-4-8`, Sonnet 5 `claude-sonnet-5`, Haiku 4.5 `claude-haiku-4-5`)
independently labelled a **tier × frequency stratified** sample of 110 resolutions on two
axes (lemmatization, gloss — D6); 9 split/correct-vs-wrong disagreements adversarially
adjudicated by a 4th model (Fable 5 `claude-fable-5`). Sampler + aggregator
[`src/saru_gloss_sample.py`](src/saru_gloss_sample.py) / [`src/saru_gloss_aggregate.py`](src/saru_gloss_aggregate.py);
full report [`gold/saru_gloss_precision_report.md`](gold/saru_gloss_precision_report.md).
Wilson 95% CI; "unsure" excluded from the denominator.

| axis | precision | 95% CI | note |
|---|--:|--:|---|
| lemmatization (overall) | **86.1%** | 78.3–91.4 | correct 93 · wrong 15 · unsure 2 |
| gloss (overall) | **85.3%** | 77.5–90.8 | ≈ the 84.4% upstream pair-precision ceiling; good+partial 97.2% |

| tier | lemma prec | gloss prec |
|---|--:|--:|
| dcs (n=40) | 94.9% | 87.5% |
| **vidyut (n=40)** | **71.8%** | 79.5% |
| marker (n=30) | 93.3% | 90.0% |

The **vidyut** tier is the lemmatization weak spot. Panel + verify converged on three
systematic, actionable defect classes (wave-3 targets): (1) ṛ/ṝ root-vowel length collapsed
to short (`kiranto`→√kṛ not √kṝ); (2) derived nominals lemmatized to a bare verbal root
(`janitṛ`→jan, `liṅgin`→liṅg); (3) compound tokens lemmatized to their final member only
(`anartha-trivarga`→trivarga). A human spot-check of the frozen sample is queued as a GTD @DO.

## 20-07-2026 — Sa→Ru gloss layer, wave-1 defect fixes (H1349 W1.1–W1.3)

Three pipeline-defect fixes in the Sa→Ru gloss layer, measured before/after over
one regenerated two-pass bootstrap (DCS `dcs_full.sqlite` 5.69M tokens + vidyut
kosha 0.4.0 + `surface_glossary.jsonl`). Fixes + measurement Opus 4.8
(`claude-opus-4-8`);
[`src/measure_wave1_delta.py`](src/measure_wave1_delta.py) replays the OLD and NEW
rule over identical inputs so each row isolates the code change alone. Regressions
pinned by [`tests/test_saru_gloss_pipeline.py`](tests/test_saru_gloss_pipeline.py)
(7 passing).

| Defect | Before | After | Note |
|---|--:|--:|---|
| W1.1 distinct root keys in lemma→root map | 3,570 | 3,147 | 434 self-mapped pseudo-root rows split out to `dcs_lemma2root_unresolved.tsv` (net −423 distinct keys); `root_glossary` layer now 1,853 roots |
| W1.2 homograph alternate rows | 9,521 | 11,289 | +1,768 rows; the old code inspected only `cands[1]`, so a genuine 3rd+ homograph was dropped — now the full trail over 9,733 forms |
| W1.3 vidyut ambiguity rows recorded | 0 | 5,952 | `stats['ambiguous']` was a bare counter (4,133 forms); now a `vidyut_ambiguity.tsv` competitor trail mirroring the DCS schema |

Two-pass bootstrap outcome (regen, fixed pipeline): 40,370 lemmas / 1,853 roots;
surface-form resolution 43.6 % (DCS) → 58.7 % (+vidyut +marker). The published
`SanskritRussian` data (still showing 2,021 roots) is **not** regenerated here —
D8 fences republish behind a human GO; a wave-2-gated republish will drop the root
count to ~1,853. Accuracy of these glosses is still unmeasured (coverage ≠
accuracy — wave 2 publishes a per-tier precision figure).

## 12-07-2026 — E2 sense-genre vs DCS attestation (H833 / H350 backlog #3)

Does per-sense citation-genre predict DCS corpus attestation better than the
lemma's aggregate genre? Analysis Opus 4.8 (`claude-opus-4-8`);
[`research/analyze_sense_genre_attestation.py`](research/analyze_sense_genre_attestation.py),
full write-up [`research/SENSE_GENRE_ATTESTATION_FINDINGS.md`](research/SENSE_GENRE_ATTESTATION_FINDINGS.md).
n = 1316 headword lemmas (grouped by normalised IAST, **not** `key1`=root),
49.8% DCS-attested. 5-fold stratified CV AUC (out-of-fold):

| Model | Features | AUC |
|---|---|---:|
| 0 | size only (n_senses, citation mass) | 0.700 |
| A | 0 + lemma union coarse-genre | 0.716 |
| B | 0 + sense-resolution genre | 0.710 |
| A+B | 0 + both | 0.714 |

ΔAUC(B−A) = **−0.006**, 95% bootstrap CI [−0.020, +0.009] → **thesis not
supported**: sense-resolution adds no separable signal over the lemma aggregate
at this scale. Attestation is driven by citation *volume* (genre adds ~+0.016);
per-genre, a *pure* sense in kāvya/purāṇa/kośa/śāstra raises attestation odds
(OR 2.2–3.5, CI>1) but Vedic-only senses do not (OR 1.06) — antiquarian signal.

## 09-07-2026 — pwg_ru medium50 relaunch (H437, post-classifier-unblock)

Windows `h317_w1b`/`w2a`/`w2b` relaunched solo (1-wide) after
[H428](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H428-Sonnet_RussianTranslation_opt2-schema-slim-classifier-unblock_09.07.26.md)
slimmed the opt2 schema. Orchestrator Opus 4.8 (`claude-opus-4-8`); generation
Sonnet 5 (`claude-sonnet-5`, harness-pinned). Full account +
n=50 tally: [`MEASUREMENT_2026-07-08_H317.md`](MEASUREMENT_2026-07-08_H317.md)
(H437 section). Finding: classifier unblocked (agents ran, 0 connection errors),
but every window tripped its `MAX_AGENTS` budget-kill-switch via the self-heal
cascade — the kill-gate miscalibration for dense band-4 nominal singletons is now
the isolated blocker.

| window | cards | agents (spent/max) | net clean (promoted) | defect | transient-null | subagent tokens |
|---|---:|---:|---:|---:|---:|---:|
| h317_w1b | 12 | 61/61 | 1 (`yuvan`) | 2 | 9 | 2,898,353 |
| h317_w2a | 13 | 49/49 | 1 (`ṛtvij`) | 2 | 10 | 1,628,556 |
| h317_w2b | 12 | 52/52 | 0 | 2 | 10 | 2,153,758 |
| **total** | **37** | **162** | **2** | **6** | **29** | **6,680,667** |

medium50 net over the whole H317→H389→H437 arc: **2 / 50 promoted (4%)**;
kill-gate recalibration routed to a bug-hunt handoff (see
[`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) `H437_MEDIUM50_KILLGATE_CASCADE_2026-07-09`).

## 09-07-2026 — pwg_ru card stats rollup (annotate_stats.py)

Script v1.0.0 · Sonnet 5 (claude-sonnet-5)

| metric | value |
|---|---|
| lemmas | 145 |
| records (homonym groups) | 563 |
| senses | 11261 |
| government markers | 0 |
| lemmas with case variation | 0 |
| evidence: provides | 1734 |
| evidence: supports | 1935 |

## 12-07-2026 — pwg_ru card stats rollup (annotate_stats.py)

Script v1.1.0 · Opus 4.8 (claude-opus-4-8)

| metric | value |
|---|---|
| lemmas | 205 |
| records (homonym groups) | 635 |
| senses | 11505 |
| government markers | 508 |
| lemmas with case variation | 2 |
| grammar-joined lemmas (single homonym) | 32 |
| … whitney irregularities counted | 46 |
| grammar ambiguous-homonym (alignment owed) | 17 |
| dcs-matched lemmas | 170 |
| <ls> citations (total) | 41031 |
| evidence: provides | 1699 |
| evidence: supports | 1893 |

Numbers are over the current 205-lemma pwg_ru_translated store (the gitignored working
copy); the fields (`government`, `stats`, `sense_stats`, `record_stats`) are materialised
locally by re-running the annotator chain — the store itself is not committed. Contrast the
09-07 v1.0.0 row above (0 government markers, no grammar counts) with this v1.1.0 row: H777
joined the grammar block (`n_irregularities` no longer stuck at 0) and added the layer /
markup / QA / frequency families.

## 12-07-2026 — PWG case-government census, frozen (H778, government_census.py freeze)

Script v1.1.0 · Opus 4.8 (`claude-opus-4-8`). Corpus-level marker census over the **whole
raw** [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
(sha `430c910f8b0c9229`), frozen to the committed [`src/census_stats.json`](src/census_stats.json)
sidecar so the scan is not re-run on every question. This is the corpus answer to "сколько
таких помет в PWG"; the per-205-lemma store rollup above is the pwg_ru subset.

| metric | value |
|---|---|
| PWG entries scanned | 123366 |
| sense units scanned | 288991 |
| government markers (total) | 3853 |
| … paren-single / variation / mit-phrase | 2309 / 40 / 1504 |
| entries with ≥1 marker | 1476 |
| sense units with ≥1 marker | 3222 |

