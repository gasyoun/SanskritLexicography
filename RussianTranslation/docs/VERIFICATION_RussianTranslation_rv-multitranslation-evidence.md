# VERIFICATION — Rig-Veda multi-translation evidence layer, wave 1

_Created: 29-07-2026 · Last updated: 29-07-2026_

Acceptance criteria, the exact command that proves each one, and the risk register for
[PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md).
Build sequence: [IMPLEMENTATION](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/IMPLEMENTATION_RussianTranslation_rv-multitranslation-evidence.md).

---

## 1. Acceptance criteria per deliverable

| ID | Deliverable | Criterion | Proven by |
|---|---|---|---|
| W1.1 | Griffith English layer | `contents` length equals the number of `p.stamp` blocks in the source HTML; every `location` matches the VedaWeb dotted form; unmatched loci reported, not silently dropped | `pytest tests/test_rv_spine.py -k griffith` |
| W1.2 | Stanza table | Exactly 10,552 records; `absent_from_source` count is 4 for Geldner and 0 for Grassmann and Elizarenkova; 0 `empty` rows | `pytest tests/test_rv_spine.py -k stanza` |
| W1.3 | Lemma occurrences | Token count reconciles to **164,758**; every occurrence's `location` exists in the stanza table; `id_gra`/`id_pwg`/`id_mw` present wherever the source token carried them | `pytest tests/test_rv_spine.py -k lemma` |
| W1.4 | Flat mirror + schema | TSV row count equals total lemma × stanza × translator; both JSONL files validate against `schemas/rv_translation_spine.schema.json` | `python src/rv_spine_build.py --validate` |
| W1.5 | Renou citation index | **2,213** rows; **368** with `mention_kind == "quoted_fr"`; per-maṇḍala totals match §1.1 below | `pytest tests/test_rv_spine.py -k renou` |
| W1.6 | Divergence pilot | ~2,000 stanzas typed; every `absent_from_source` pair labelled `omitted_by_one` without a model call | `python src/rv_divergence_type.py --pilot --report` |
| W1.7 | Human gate | ≥ 80 % agreement between the model's class and the human vote on 100 stanzas | the sheet's own `decisions.json` + the agreement report |
| W1.8 | Full typing run | All 10,552 stanzas × 6 translator pairs carry a class; distribution table persisted to `RESULTS_LOG.md` | `python src/rv_divergence_type.py --report` |
| W1.9 | Word-level layer B | Precision ≥ 85 % **per language** on the 300-token gold sample | `gold/rv_wordlevel_precision_report.md` |
| W1.10 | Judge witness | A headword with an `id_pwg` in the spine receives a witness block; one without receives none | `pytest tests/test_rv_spine.py -k witness` |
| W1.11 | Contradiction gate | Fires only on unanimous contradiction; a synthetic contradicting card is queued, a synthetic agreeing card is not | `pytest tests/test_rv_spine.py -k gate` |
| W1.12 | TM tier | New `trust_level` validates against the TM schema; the tier is reachable on **both** `ru` and `en`; the change is classified in `LANG_PARITY.md` | `python src/pilot/window_selftest.py` (includes `test_lang_parity_ledger_complete`) |
| W1.13 | wisdomlib, four roles | Each role has a smoke test; the run makes **zero** network calls | `pytest tests/test_rv_spine.py -k wisdomlib` |

### 1.1 Renou per-maṇḍala reference counts

Measured 29-07-2026 against the committed commentary files. A parser that does not reproduce
these is wrong.

| Maṇḍala | I | II | III | IV | V | VI | VII | VIII | IX | X | total |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Renou mentions | 459 | 117 | 161 | 118 | 158 | 110 | 171 | 123 | 226 | 287 | **2,213** |

Of these, **368** carry a Latin-script quotation in guillemets.

## 2. Hard invariants — a failure here is a bug, not a finding

These are measured facts about the committed data as of 29-07-2026. If a run reports something
different, the code is wrong; do not record the discrepancy as a discovery.

1. Ṛgveda stanzas: **10,552**.
2. Ṛgveda tokens: **164,758**.
3. Grassmann coverage **10,552**, Elizarenkova coverage **10,552**, Geldner coverage **10,548**.
4. The four stanzas Geldner does not translate are exactly **RV 10.106.5, 10.106.6, 10.106.7,
   10.106.8**.
5. Zero empty-text rows in any of the three VedaWeb translation files.
6. `transformContext` is a **JSON string**, not a nested object. A parser that treats it as an
   object silently yields zero tokens.
7. Renou mentions **2,213**, of which **368** carry a French quotation.

Invariants 3 and 4 double as the semantic regression test for the whole `omitted_by_one` class:
they are the one piece of the divergence taxonomy whose ground truth is known before any model
runs.

## 3. Risks and spikes

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| K1 | **LaBSE is weak on transliterated Sanskrit.** Already an honest finding in [LABSE_ALIGN.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/LABSE_ALIGN.md) (any-to-any retrieval 0.025 on formulaic epic prose). Vedic is harder than epic prose | high | Layer B is advisory by design (R5). Its failure degrades the layer to spine A, which is unaffected. This is why the 85 % bar exists per language rather than pooled |
| K2 | **The 0.20 confidence gate was calibrated on a 30-row sample with ONE negative.** [ALIGN_GATE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ALIGN_GATE.md) says so plainly | high | Do not treat 0.20 as validated for Vedic. Record the observed distribution; re-calibrate only against the new 300-token gold, as a separate evidence-backed step |
| K3 | **Divergence typing may not be reliably separable.** "Lexical variant" vs "semantic shift" is a judgment call even for humans; the pair may not reach 80 % agreement | medium | That is exactly what the step-8 gate is for. A failed gate means collapsing to a coarser 3-class taxonomy (agreement / divergence / omission), not tuning until it passes |
| K4 | **Renou locus resolution from prose commentary.** The commentary's stanza numbering must be tracked across a plain-text file with no markup | medium | `locus_unresolved: true` rather than dropping the row, so the 2,213 total always reconciles and the unresolved share is visible |
| K5 | **Griffith's stanza division may differ from VedaWeb's.** A 19th-century translation need not segment identically | medium | Unmatched loci are logged, not force-fitted. If the unmatched share exceeds 2 %, treat it as a spike: report it and ship the other three layers rather than guessing a mapping |
| K6 | **Grey-rights material in a public repo** (R8 + R10). The plan commits the Renou index — quotation-shaped — into an open repository | certain, and ruled | The human ruling stands and is followed. The bounded-window design (PLAN §5) keeps the artifact quotation-shaped; whole-stanza commentary text is **not** part of this plan. Wave 2 budgets a subsetting step for the DOI release |
| K7 | **Concurrent sessions in this repo.** A Codex session is active on `codex/rt-pipeline-hardening-speed` touching the pipeline | medium | Work in a session-unique worktree off `origin/master`; the guarded main tree is never edited. Expect a rebase at PR time on shared files (`LANG_PARITY.md`, `changelog.md`) and resolve by keeping both entries |
| K8 | **TSV size.** The flat mirror could be large enough to be a poor git citizen | low | Marked default in IMPLEMENTATION step 4: gitignore it above 200 MB, commit a 500-row sample, keep the JSONL pair as the contract |

## 4. Spikes to run before committing to the architecture

Two, both cheap, both before the expensive steps:

**S1 — Griffith locus alignment (before step 2).** Extract the loci only, intersect with the
VedaWeb set, report the unmatched share. If it exceeds 2 %, K5 has fired and the English layer
needs a decision before the spine is built on it. Cost: minutes.

**S2 — Divergence separability (before step 7's full pilot).** Type 50 stanzas, eyeball whether
`lexical_variant` and `semantic_shift` are actually being distinguished or whether the model is
assigning them arbitrarily. If they are not separable at 50, they will not be at 2,000 — collapse
to the coarse taxonomy (K3) before spending the pilot. Cost: one small model run.

## 5. What "wave 1 is done" means

All thirteen rows in §1 pass, all seven invariants in §2 hold, the existing test suite and
`window_selftest.py` are green, every results table is persisted to `RESULTS_LOG.md` with date
and model tier + exact version, and the changelog entry has been cut into a release. Step 8's
human vote is the one item that may legitimately remain open at the end of an unattended run —
it is queued as a `@DO` in [`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md),
and W1.8 stays blocked behind it rather than being self-approved.

_Dr. Mārcis Gasūns_
