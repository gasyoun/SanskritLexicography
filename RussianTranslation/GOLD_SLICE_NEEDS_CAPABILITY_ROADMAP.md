# Gold-slice needs — PWG→RU research-capability roadmap

_Created: 12-07-2026 · Last updated: 12-07-2026_

Which cards of the [30-capability roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md)
are blocked on a **frozen, adjudicated human gold slice** that does not exist yet,
what each one needs, and why the deterministic work cannot close them alone. This
is the durable record of the "document need of gold for later" decision (H775,
12-07-2026): the deterministic, local-only halves of the evaluation spine and of
cards 5/23 are now built; their *acceptance metrics* all terminate at a gold slice
a human must stand up and adjudicate.

Standing up a gold slice is a **human action** — a human decides the sample frame,
labels a first pass, and a second annotator (or blind-LLM annotator, per the
deferred-second-annotator policy) adjudicates. The machinery already exists:
[`/gold-adjudicate`](https://github.com/gasyoun/claude-config/blob/main/commands/gold-adjudicate.md)
sets up multi-annotator review and
[`/review-sheet`](https://github.com/gasyoun/claude-config/blob/main/commands/review-sheet.md)
emits the interactive voting sheet (markdown checkboxes are banned). Card 25 (the
inter-annotator-agreement dashboard) is itself the gate that blocks "gold" status
until κ/α is computed.

## What each blocked card needs

| Card | Gold artifact needed | Size / frame | Labels | Unblocks |
|---:|---|---|---|---|
| 1 — COMET-QE calibration | Frozen adjudicated A/B/C translation-quality slice | ~200–300 rows, stratified by current `tm_grade.py` grade | A / B / C per row | reweighting the proxy QE; feeds 8, 13 |
| 3 — BLI evaluation | Sa→Ru bilingual-lexicon gold set | 300 items, dictionary-backed | correct Ru equivalent(s) per Sa lemma | P@1/MRR vs baseline on `corpus_lexicon` |
| 25 — IAA dashboard | Adjudication records for every active gold slice | all slices below | per-annotator labels + adjudicated truth | κ/α gate; blocks "gold" status when agreement missing |
| 4 — token-in-context WSD | Sense-labelled DCS token contexts | high-frequency polysemous lemmas | gold PWG sense per token | WSD accuracy vs the card-5 MFS baseline |
| 5 — MFS baseline (accuracy) | Same sense-labelled sample as card 4 | subset of the 169 MFS-candidate lemmas | gold primary sense per lemma | measures MFS baseline accuracy (emitter already built, H775) |
| 23 — government mismatch (precision) | RU-rendering mismatch review sample | ~50 high-severity flags | real issue / not | ">= 85% high-severity real" (extraction already built, H775) |
| 7 — variant-reading extractor | Reviewed translator-divergence clusters | >= 50 clusters | genuine sense-variation / style, κ ≥ 0.60 | mapping divergence to PWG senses |
| 8 — per-sense confidence | Frozen validation slice of review/audit failures | held-out | human/audit fail per sense | AUC of composite vs single feature |
| 9 — contradiction lane | Spot-check of `contradicts` markers | 50 items | correct / not | ">= 90% precision" on the contradiction lane |
| 11 — semantic-change detector | Review of top-shifted lemmas | top 100 | substantively meaningful / not | ">= 70% meaningful"; also needs card 10 dated bands |
| 13 — dual-model mined-pair | Precision/recall labels for mined pairs | policy-calibration sample | accept / reject | publication-grade promotion policy |
| 14 — bitext filter | Labelled accepted/rejected mined pairs | train + eval | accept / reject | ROC-AUC over the threshold gate |
| 16 — BLI drift detector | Reviewed flag sample | disagreement flags | actionable / not | ">= 50% actionable" (also needs external BLI tooling) |
| 22 — compound segmentation | Reviewed segmentation sample | compounds | correct / false-segmentation | recall gain under a false-seg ceiling |
| 24 — proper-name classifier | Labelled name/transliteration vs lexical sample | balanced | name / lexical | ">= 90% recall" on the name failure class |

## The immediate blocker (evaluation spine)

The [Evaluation spine](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CAPABILITY_OBSERVATORY.md)
is the strategic first family, but three of its five cards (1, 3, 25) are gold-gated.
The single unblocking human action is to **stand up and adjudicate the A/B/C
translation-quality gold slice** (card 1), which — together with card 25's
agreement computation — is the prerequisite the rest of the spine and card 30 (the
paper matrix) depend on. Cards 2 (aligner-agreement gate) and 5 (MFS emitter) are
the local-only spine work that does NOT wait on gold; card 5's *emitter* shipped in
H775, only its accuracy number waits.

## Related

- Roadmap: [`RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RESEARCH_CAPABILITY_ROADMAP_2026-07-09.md)
- Status board: [`CAPABILITY_OBSERVATORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CAPABILITY_OBSERVATORY.md)
- H775 deliverables (cards 5 + 23): [`src/mfs_baseline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mfs_baseline.py), [`src/government_sidecar.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_sidecar.py)
- An existing frozen gold set to reuse as a frame: [`gold/gold_set.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/gold_set.jsonl) (320 rows, TM-grade calibration)

_Dr. Mārcis Gasūns_
