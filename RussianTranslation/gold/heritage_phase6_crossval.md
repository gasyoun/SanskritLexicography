# Heritage phase 6 — segmenter-as-service cross-validation vs DharmaMitra

_Created: 23-08-2026 · Last updated: 23-08-2026_

Phase 6 of [HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md),
executed as [H3171 (OxAlpha) — Heritage phase 6: segmenter-as-service cross-validation](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3171-OxAlpha_SanskritLexicography_heritage-phase6-segmenter-service_19.08.26.md).
Two independent morphology witnesses were run over the hand-adjudicated
RussianTranslation glossary sample; agreement is reported **against the
adjudication** and **engine-vs-engine** separately, with every disagreement
classified in the phase-4 taxonomy. **Diff-only discipline held:** no canonical
morphology store was touched by either witness.

## The two witnesses

| | Witness A: Heritage segmenter/lemmatizer | Witness B: DharmaMitra ByT5 morphology |
|---|---|---|
| Engine | Gérard Huet's Sanskrit Heritage Platform v3.77 [2026-03-15] | `chronbmm/sanskrit5-multitask` ByT5 multi-task analyzer, pinned revision `c0d2ada` (csl-atlas contract) |
| Access | **UoHyd mirror** `https://sanskrit.uohyd.ac.in/cgi-bin/SKT/sktreader`, Word mode, SLP1 input, MW lexicon — live service, not Anubis-walled (the Inria primary is; per [FINDINGS §41](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)/§47 it was never touched) | **Local pinned-revision inference**, SLM task (`unsandhied-lemma-morphosyntax`), CPU |
| Why this access path | The mirror hosts the real platform (same CGI family as sanskrit.inria.fr); live-service etiquette applied: every response cached, 2 s throttle, identifying User-Agent | The live `dharmamitra.org/api/tagging/` was probed same-day and returned **identity echoes for every input, including sandhi-bearing sentences** (`rāmasya putraḥ vanam agacchat → rāmasya_putraḥ_vanam_agacchat_`, identical under all three mode strings) — the [FINDINGS §95](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) short-input failure class is now chronic at the API. Local inference of the pinned model is the documented reproducible fallback |

## Evaluation set — the adjudication, precisely

[RussianTranslation/gold/saru_gloss_gold_set.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/saru_gloss_gold_set.jsonl):
the H1349 wave-2 precision-panel sample of **110 surface forms** from the SaRu
glossary layer (tier × frequency stratified). Each row carries the automatic
pipeline lemma and a 3-judge panel verdict on it (`panel_lemma`). Per its own
[precision report](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/saru_gloss_precision_report.md)
this is a **model-vs-model LLM panel, not a human gold set** — that caveat
travels with every number below. Scoring vs the adjudication uses only the
**93 rows where the panel judged the recorded lemma correct** (those are the
only rows carrying a trusted reference lemma); the 110-row set is used intact
for engine-vs-engine. Matching is strict normalized-set membership after
phase-4 nasal-normalisation (anusvāra/homorganic nasals folded, avagraha and
Heritage `_N` homonym indexes stripped).

## Headline numbers

| Metric | agree / n | % | Wilson 95% |
|---|--:|--:|--:|
| Heritage vs adjudication (strict) | 32 / 93 | **34.4%** | 25.5–44.5 |
| DharmaMitra vs adjudication (strict) | 49 / 93 | **52.7%** | 42.6–62.5 |
| Both witnesses vs adjudication | 28 / 93 | 30.1% | 21.7–40.1 |
| Heritage ↔ DharmaMitra (engine-vs-engine, all 110) | 60 / 110 | **54.5%** | 45.2–63.5 |

**After classification** (below): counting only genuine errors as contradictions,
Heritage contradicts the adjudication on **20/93 = 21.5%** of rows (78.5%
adjusted agreement) and DharmaMitra on **10/93 = 10.8%** (89.2% adjusted).
The gap between strict and adjusted is dominated by one finding:

> **The dominant disagreement class is compound-entry granularity, not error.**
> The glossary records lexicalized compounds as single entries
> (`mahAkapi`, `kAmarUpa`, `kurunandana`, …); both witnesses lemmatize to
> members (`mahat+kapi`, `kAma+rUpa`, `kuru+nandana`). Both behaviours are
> internally consistent — a policy difference, exactly the phase-4 lesson.

Phase-4's raw 78.3% figure keeps its caveat here: it counted form-string
overlap between two *generative* engines and was never a precision number; it
is not used as a baseline anywhere above.

## Classified disagreement table

Full per-cell table with witness output and rationale:
[h3171_disagreements_classified.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/h3171_disagreements_classified.tsv)
(105 cells = every (row × witness) miss, machine-checked to cover exactly the
missed cells — verifier
[h3171_verify_classes.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3171_verify_classes.py)).

| Class | Heritage | DharmaMitra | What it is |
|---|--:|--:|---|
| **policy** | 39 | 34 | Compound-entry granularity (dominant), root↔derived stem (`nivAray`↔`vR`, `ukTa`↔`vac`, `Bakta`↔`Baj`), pronominal-stem convention (`tvad`↔`tva`) |
| **convention** | 2 | 0 | Same lexeme, notation variant (`bAndhava`/`bAnDava`; visarga `-s` listed as stem) |
| **error** | 20 | 10 | Heritage: 14 Word-mode **no-analysis** gaps (indeclinables `evaM`/`vAc`, pronoun `tvad`, rare forms) + 6 wrong outputs; DM: §95-style shattering (`sTira-budDi → bud;di;ra;t`), spelling slips (`durdA` for `durDA`) |
| surplus (primary) | 0 | 0 | Fragment noise (`Bu;Bu;Uta;av`) co-occurs with correct member analyses, so those rows classify as policy-primary; "+ surplus" appears in 9 notes |

Representative rows (SLP1):

| Surface | Adjudicated | Heritage | DharmaMitra | Class |
|---|---|---|---|---|
| `nivAryate` | nivAray | ni+vṛ (root) | nivAray ✓ | H: policy (root vs caus-stem) |
| `mahAkapi` | mahAkapi | mahat+kapi | mahAkapi ✓ | H: policy (entry granularity) |
| `sTira-budDi` | sTirabudDi | sthira+buddhi | bud;di;ra;t | H: policy · D: error (shatter) |
| `evaM` | evam | *(no analysis)* | evam ✓ | H: error (coverage gap) |
| `nyAYc` | nyAYc | *(no analysis)* | nyAMc ≡ (nasal-norm) ✓ | H: error |
| `brahma-nirvARa` | brahmanirvARa | brahman+nirvARa | brahman+nirvARa | both: policy (entry granularity) |

## Live-service etiquette evidence (fence compliance)

- **Requests:** 109 live GETs to `sktreader` (110 eval forms − 1 duplicate
  surface `brahmanirvARa` served from cache) + ~12 discovery/degradation
  probes across both services before the run. Ledger:
  [_cache_h3171/requests_ledger.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/_cache_h3171/requests_ledger.jsonl)
  (one line per fetch, timestamped, `cached` flag).
- **Throttle:** ≥ 2.0 s between consecutive requests, enforced client-side.
- **Cache path + size:** `RussianTranslation/gold/_cache_h3171/` — 109 raw
  Heritage HTML responses (`her_*.txt`), the local DM output snapshot
  (`dm_local_slm.json`), pre-run probes (`probes/`); ~440 KB total, committed.
- **Client identification:** every request carried
  `User-Agent: Mozilla/5.0 (compatible; SanskritLexicography-H3171 heritage-phase6 cross-validation client; +https://github.com/gasyoun/SanskritLexicography)`.
- **Anubis fence respected:** zero programmatic requests to `sanskrit.inria.fr`
  or `gitlab.inria.fr`; the UoHyd mirror serves the same platform openly.
- **No canonical overwrite:** witnesses wrote nothing outside
  `RussianTranslation/gold/h3171_*`; the kosha/DCS forms layers are untouched.

## Outputs

| File | Contents |
|---|---|
| [heritage_phase6_crossval.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/heritage_phase6_crossval.md) | this report |
| [h3171_results.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/h3171_results.jsonl) | per-row witness outputs + verdicts (110 rows) |
| [h3171_stats.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/h3171_stats.json) | machine-readable summary |
| [h3171_disagreements_classified.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/h3171_disagreements_classified.tsv) | all classified misses (105 cells) |
| [_cache_h3171/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/gold/_cache_h3171) | response cache + request ledger + DM snapshot |
| [src/heritage_phase6_crossval.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/heritage_phase6_crossval.py) | reproducible pipeline (cached re-runs make zero live calls) |
| [src/h3171_classify.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3171_classify.py) | classification map → TSV generator |

**Reproduce:** `python RussianTranslation/src/heritage_phase6_crossval.py`
(idempotent off the committed cache; delete `_cache_h3171/her_*.txt` to force
polite live refetching). Classification:
`python RussianTranslation/src/h3171_classify.py`.

## Consumer note (csl-atlas / RussianTranslation)

As a second independent witness beside kosha's vidyut-built forms layer, the
measured profile is: **DharmaMitra (pinned local) is the stronger isolated-form
lemmatizer** (52.7% strict / 89.2% adjusted vs the adjudication; whole-compound
lemmas on lexicalized entries), **Heritage Word-mode is the weaker isolated
analyst but adds value on prefixed verbs and root identification**
(`ni+vṛ`, `pra+hṛ`) — its no-analysis tail is concentrated in indeclinables,
pronouns and rare inflections, which its sentence-mode Reader handles better.
Any consumer wiring should treat both as evidence streams, never silent build
inputs (both licences permit derived composition: LGPLLR × BY-SA ruled 03-07-2026;
DM predictions are review-evidence-only per csl-atlas). Registration row:
[PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md).

_Dr. Mārcis Gasūns_
