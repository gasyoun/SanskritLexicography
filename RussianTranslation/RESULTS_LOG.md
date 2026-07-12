# RussianTranslation — results log

_Created: 09-07-2026 · Last updated: 12-07-2026_

Append-only, reverse-chronological. Each entry: date, context, model tier, table.

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

