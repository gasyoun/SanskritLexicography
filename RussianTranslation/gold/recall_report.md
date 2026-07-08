# Harvest recall — gold-standard measurement

_Created: 07-07-2026 · Last updated: 08-07-2026_

Companion to [precision_report.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/precision_report.md): that report asks "are the harvested pairs right?"; this one asks "of the Sanskrit content words the harvest saw, how many made it into [corpus_lexicon.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py)?" (the 1.09M-row output itself is gitignored; link is to its builder).

> NOTE: like the precision report, this is an **LLM-adjudicated** estimate — a single frontier-model reading pass (Fable 5 `claude-fable-5`, H136 session, 07-07-2026), every token of every sampled group read against its source verse and published Russian translation. The frozen per-group labels ([recall_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/recall_set.jsonl)) are the scaffold for a human spot-check.

> **08-07-2026 update ([H309](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H309-Sonnet_RussianTranslation_corpus-lexicon-reharvest-gaps_07.07.26.md), Sonnet 5 `claude-sonnet-5`):** both failure classes below were root-caused and the commentary-tail class was fixed by a **targeted re-harvest**, re-measured against the SAME 8 frozen Medieval groups from `recall_set.jsonl` (not a fresh resample, so the before/after is apples-to-apples). Root cause: `sa` for a verse+commentary group already carries BOTH the mūla verse AND the fused prose commentary in one blob, and the main `ru` translation segment already renders most of it — the aligner's single-pass call, given a longer/denser `sa`+`ru` pair, was silently dropping content words; the separate `comm1` segment (which most groups don't even have) was a red herring. Fix in [build_corpus_lexicon.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py): `SYS`/`SYS_BATCH` now say **"noun, verb, adjective, ADVERB"** (adverb was simply missing from the category list — the entire adverb-skip failure class) plus an explicit **"be EXHAUSTIVE … do not stop after the first few salient ones"** instruction. The two genre-tagged commentary works (`corpus_strata.json` genre `Śāstra — Commentary (Yāmuna/Abhinavagupta)`: `gitartha-samgraha_yamunacharya` 32 groups + `gitarthasamgraha-abhinavagupta` 748 groups = **780 groups**) were **REPLACED** — old rows for those two works removed, all 780 groups re-harvested fresh under the new prompt (12,841 old rows → 14,704 new rows, +14.5%; 20 transient API failures, both retry passes cleared to 0). The widened prompt is now the default for **all future harvests**, but per the "targeted, not full rebuild" mandate the ~58k groups outside this population were **not** re-harvested — their adverb-class misses (e.g. `adya`/`satatam` in `05_ramayana-sundarakanda:32.12`, Epic/early-Classical stratum) remain a documented residual. See "Re-measurement" below.

## Group-level coverage (deterministic, not sampled)

Of the verse groups eligible for harvesting (a Sanskrit segment AND a Cyrillic-bearing Russian segment, works in `corpus_strata.json`), the share with ≥1 lexicon row — computed by `python src/gold_recall_sample.py coverage` over the full corpus:

| period | eligible groups | processed | coverage |
|---|---|---|---|
| Vedic | 16,472 | 16,463 | 99.9% |
| Epic / early-Classical | 37,681 | 37,401 | 99.3% |
| Classical | 3,323 | 2,996 | 90.2% |
| Medieval | 1,421 | 1,416 | 99.6% |
| **TOTAL** | **58,897** | **58,276** | **98.9%** |

(Post-H309: Medieval processed 1,411→1,416 — the re-harvest's failure-retry pass recovered 5 groups that the original run never wrote a row for at all, on top of the word-level fix below.)

## Word-level recall (adjudicated sample)

Sample: 32 processed groups, 8 per period stratum, seed=42 (`python src/gold_recall_sample.py sample 32`), 476 raw tokens → **287 unique content lemmata** after excluding particles, pronouns, copulas, and tokenization junk. Rubric per lemma:

- **covered** — the lexicon has a pair for it in this group (lemma/sandhi normalization allowed; a compound counts as covered when aligned whole OR via its member pairs);
- **miss-translated** — rendered in the published Russian but absent from the lexicon (**true recall loss**);
- **miss-untranslated** — no distinct Russian counterpart in this translation (the harvest prompt says omit these; reported separately, not a loss).

| metric | value (07-07-2026, pre-H309) | value (08-07-2026, post-H309) |
|---|---|---|
| content lemmata | 287 | 287 |
| covered | 258 | 267 |
| miss-translated | 22 | 13 |
| miss-untranslated | 7 | 7 |
| **recall (covered / covered+miss-translated)** | 92.1% (Wilson 95% CI 88.4–94.7) | **95.4%** (Wilson 95% CI 92.2–97.3) |
| coverage of all content lemmata | 89.9% | 93.0% |

### By stratum (period)

| stratum | content | covered | miss-tr | miss-untr | recall (pre) | recall (post) |
|---|---|---|---|---|---|---|
| Vedic | 73 | 71 | 2 | 0 | 97.3% | 97.3% (unchanged — not in the re-harvest population) |
| Epic / early-Classical | 49 | 42 | 4 | 3 | 91.3% | 91.3% (unchanged — not in the re-harvest population) |
| Classical | 81 | 77 | 3 | 1 | 96.3% | 96.3% (unchanged — not in the re-harvest population) |
| Medieval | 84 | 77 | 4 | 3 | 84.0% | **95.1%** |

Vedic/Epic/Classical numbers are carried forward unchanged from the 07-07-2026 measurement — the H309 re-harvest was scoped to the two genre-tagged commentary works, both Medieval, so those three strata's underlying lexicon rows were not touched this pass (see the update note above).

### Medieval re-measurement detail (the same 8 frozen groups, re-checked against the post-re-harvest lexicon)

| group | content | covered (pre→post) | miss-tr (pre→post) | resolved | still missing |
|---|---|---|---|---|---|
| gitarthasamgraha-abhinavagupta:6.44 | 19 | 9→16 | 8→1 | tāratamya, apavarga, śrīmat, geha, vighna, saṃsiddhi, mokṣa(mokṣātmikā, lemma-normalized) | ah ("сказано") |
| hatha-yoga-pradipika:3.17 | 10 | 10→10 | 0→0 | — (not in re-harvest population) | — |
| gitarthasamgraha-abhinavagupta:16.7 | 10 | 7→8 | 3→2 | vid (now covered via both `vidu`→«не знают» and `vidyate`→«не ведомы») | utpanna, pralī — see residual note below |
| gitagovinda:1.21 | 6 | 6→6 | 0→0 | — (not in re-harvest population) | — |
| gitarthasamgraha-abhinavagupta:1.40 | 8 | 8→8 | 0→0 | — (already full) | — |
| gitarthasamgraha-abhinavagupta:5.22 | 13 | 10→11 | 2→1 | bhāvay (now `bhāvayati`→«воспринимает») | sarva ("все", rendered in `ru` but still uncaptured) |
| gitarthasamgraha-abhinavagupta:2.20 | 12 | 12→12 | 0→0 | — (already full) | — |
| gitarthasamgraha-abhinavagupta:1.33 | 6 | 6→6 | 0→0 | — (already full) | — |
| **TOTAL** | **84** | **68→77** | **13→4** | **9 of 13 resolved** | **4 residual** |

### Failure classes — status after H309

1. **Commentary-tail unaligned — FIXED for the targeted population (was 13/22, now 4 residual).** Root cause was NOT "the harvest skipped the `comm1` segment" as originally hypothesized — it was single-pass alignment silently dropping content words from a dense `sa`+`ru` pair that already fuses verse and commentary. The exhaustiveness-instruction fix recovered 9 of the 13 original misses across the 780-group targeted re-harvest. **4 residual misses, all in already-re-harvested groups** (so this is a genuine remaining aligner limitation, not scope): `ah` ("says", a minor citation-frame verb), `utpanna`/`pralī` (16.7 — both appear only in a `sa`-embedded gloss whose Russian rendering is itself parenthetical/bracketed: "[Асуры не знают], что такое правритти … и откуда оно исходит … в Ком все растворяется" — still missed even under the exhaustive prompt, likely because DeepSeek's 8-item batching still dilutes attention on this specific dense pair), `sarva` ("все" in 5.22 — same batching-dilution pattern). Not chased further this pass (bounded, small-n residual; a possible next step is per-group unbatched `align()` calls for the handful of groups that stay dense after the fix, not attempted here to keep this a targeted, not open-ended, re-harvest).
2. **Adverbs of time/manner dropped — PROMPT FIXED, NOT retroactively applied.** `SYS`/`SYS_BATCH` now explicitly list "adverb" as a content-word category (was entirely absent — a literal wording gap, not a subtle prompt-engineering problem). This fixes the class for all **future** harvests. The 22-lemma sample's specific instances (adya ×2, satatam ×2, parastāt) live in Epic/early-Classical groups outside the H309 targeted population (verse+commentary works only) — they remain unfixed in the committed lexicon until those groups are re-harvested, which this pass deliberately did not do (targeted, not full rebuild).
3. **Scattered single misses (4/22, pre-H309).** sarva ×2, eka, arh, vid, bhāvay, utpanna, pralī, gatasarvabhāvā. Of these, `vid` and `bhāvay` fell inside the re-harvested population and are now resolved (see table above); the rest were outside it and are unchanged.

### Affected-group census

Population definition: `corpus_strata.json` groups with `genre` starting `Śāstra — Commentary` — the only two works so tagged. REPLACE semantics were used (not append): pre-existing rows for these two works were removed from `corpus_lexicon.jsonl` before re-harvesting, so the committed lexicon carries exactly one generation's worth of rows per group, never a stale/fresh duplicate pair.

| work | groups | rows removed (old) | rows written (new) | Δ | failed→retried |
|---|---|---|---|---|---|
| gitartha-samgraha_yamunacharya | 32 | (included in total below) | 348 | — | 0 |
| gitarthasamgraha-abhinavagupta | 748 | (included in total below) | 14,356 | — | 20→0 (2 retry passes) |
| **TOTAL** | **780** | **12,841** | **14,704** | **+1,863 (+14.5%)** | **20→0** |

### Caveats

- The Wilson CI treats lemmata as independent; they are cluster-sampled (32 groups), so the true interval is somewhat wider. The Medieval-vs-rest gap narrowed sharply post-H309 but is not fully closed — see the 4 residual misses above.
- Recall is measured **within processed groups**; multiply by group-level coverage (98.9%) for end-to-end coverage of the eligible corpus: ≈ **94.3%** of translated content lemmata overall post-H309 (was 91.1%).
- Precision issues observed in passing (renderings swapped, wrong-sense pairs, src_ru span drift in range-merged sources) were noted in `recall_set.jsonl` but NOT counted here — they are the precision report's axis.
- This re-measurement reused the SAME 8 frozen Medieval groups from `recall_set.jsonl` rather than drawing a fresh `gold_recall_sample.py sample 32` — deliberately, so the before/after comparison isolates the re-harvest's effect from sampling variance. A fresh full-sample recall run (all 4 strata, new random groups) was not performed this pass, since Vedic/Epic/Classical are provably unaffected by a population-scoped re-harvest.

_Dr. Mārcis Gasūns_
