# G5 reject/requeue audit — judge-flagged translation defects (legacy queue)

_Created: 25-07-2026 · Last updated: 25-07-2026_

Routing record required by [H1404](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1404-Fable_SanskritLexicography_deep-manual-review-gold-voting-wave1_20.07.26.md)
(scope fence, R5): the German-untranslated and quality-doubt reject notes in the
G5 lane are **pwg_ru translation defects**, and this wave's job is to ROUTE
them, not to retranslate — retranslation is a fenced downstream handoff.
Documented by Fable 5 (`claude-fable-5`), 25-07-2026.

## Where these rows come from — and why their ids are orphaned

The surviving copy of the Opus QA-judge annotations is the 2026-06 triage CSV
(`src/_review_queue.triage.csv`, gitignored personal worklist, 217 rows, built
by [`src/triage_review_queue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/triage_review_queue.py)
from that generation's `src/_review_queue.jsonl`). The queue has since been
regenerated over the full promoted store (11,163 `ai_translated` rows,
`row:`-shaped review_ids, zero judge annotations), and the store no longer
carries `ord` fields — so the legacy `ord:N` ids **do not resolve** against
`python src/run_batch.py validate_review` any more. These verdicts are audit
history and a requeue worklist, not an applicable decisions file. (The triage
tool itself was fixed in this same pass to carry `review_id` and tolerate
ord-less queue generations, so this orphaning class cannot recur.)

## Routing verdict

| Bucket | Rows | Route |
|---|---:|---|
| A-mechanical (untranslated German connectives/format) | 13 | requeue for retranslation/patch in the downstream pwg_ru fix handoff; the judge names the exact word per row |
| B-quality (rendering doubted, sev ≥ 2) | 10 | same downstream handoff, scholarly judgment per row |
| B-quality (sev 1 "publishable" nits) | 9 | no action owed — recorded here so the nit is not re-derived |
| C-source (broken German source) | 0 | (none in this generation) |
| FAST-pass (sev ≤ 1, no defect clause) | 185 | bulk lane — superseded by the live 11,163-row G5 queue |

None of these rows was edited in this pass; no retranslation was performed.

## The 32 judge-flagged rows (verbatim defect clauses, truncated at ~110 chars)

| Bucket | Sev | Legacy id | Headword (key2) | Judge's defect clause |
|---|---:|---|---|---|
| A-mechanical | 4 | ord:164 | `akz` | fail on check (c): the german connectives 'und' (4x) and 'oder' (2x) are left untranslated throughout — should… |
| A-mechanical | 3 | ord:19 | `aMSu/` | fail on check (c): german connective prose outside the gloss markers left untranslated in 6 spans — "im" x3… |
| A-mechanical | 3 | ord:52 | `aMhasaspati/` | defect: the german connective "von" inside the parenthetical ({t2} {t3} von {t4}) was left untranslated… |
| A-mechanical | 2 | ord:22 | `aMSupawwa` | defect: the german connective "also" (= "т. е."/"таким образом") in the line ({t5} = {t6} also {t7}) was left… |
| A-mechanical | 2 | ord:31 | `aMSuhasta` | defect: german "im" on the last line ({t6} im {t7}) left untranslated — should be russian "в". not publishable… |
| A-mechanical | 2 | ord:37 | `aMsaDrI/` | one defect: the german word "von" in ({t2} {t3} von {t4}) is left untranslated — should be «от»/«из»… |
| A-mechanical | 2 | ord:44 | `a/MseBArika` | minor: the etymological marker "(von {t2})" retains untranslated german "von" — but it is copied verbatim from… |
| A-mechanical | 2 | ord:46 | `aMh` | defect: german conjunction "und" in the final line ({t16} {t17} und {t18}) left untranslated — should be russi… |
| A-mechanical | 2 | ord:48 | `aMhati/` | minor: german language abbreviations "lat." and "goth." left untranslated (should be "лат."/"гот.")… |
| A-mechanical | 2 | ord:60 | `a/Mhri` | defect: german preposition "von" in "(von 1. {t2})" left untranslated (should be "от"/"из"), violating check (… |
| A-mechanical | 2 | ord:106 | `akArya` | one defect: line "{t5} im {t6}" leaves the bare german preposition "im" untranslated (should be russian "в")… |
| A-mechanical | 2 | ord:183 | `akza/n` | defect: the final german conjunction "und" in "{t53} 2. und {t54} ." was left untranslated — should be russian… |
| A-mechanical | 2 | ord:190 | `akzamA` | defect: german connective "im" on line 2 left untranslated (should be "в" or similar). one short function word… |
| B-quality | 3 | ord:17 | `aMSAvataraRa` | "of chapters") clashes with the ordinals "64-й — 67-й" (should be "глав 64—67" or "глав 64-й — 67-й книги")… |
| B-quality | 2 | ord:1 | `a` | one minor slip: "demselben stamme begegnen wir ferner" -> "тому же основанию мы встречаем далее" — "основанию"… |
| B-quality | 2 | ord:7 | `aMSa` | minor: "das gewicht der autoritäten" rendered loosely as "авторитетом источников" (drops "weight"…) |
| B-quality | 2 | ord:18 | `aMSin` | minor blemish: german has a discontinuous verb "alle mögen gleiche theile … empfangen"; the ru added "получи… |
| B-quality | 2 | ord:54 | `aMhu/` | only blemish: slightly inverted/awkward word order in "это значение слово имеет" (more natural would be…) |
| B-quality | 2 | ord:55 | `aMhuBe/da` | minor: "engspaltig" can mean "narrow-columned" (typesetting) vs. the chosen "узкощелистая" (narrow-slit)… |
| B-quality | 2 | ord:57 | `aMhUraRa/` | minor: german "als {t7}" (= "as [a] n.") rendered "в значении {t7}" (= "in the sense of"); "как" would be clos… |
| B-quality | 2 | ord:137 | `a/kfzIvala` | minor nuance: "abgeneigt" (averse/disinclined) rendered as "чуждый" (alien to) is a slight semantic softening… |
| B-quality | 2 | ord:196 | `akzayatftIyA` | minor gender slip: "один {t7}" (masc.) renders german "eine {t7}" where t7=smṛti (fem. in russian)… |
| B-quality | 2 | ord:297 | `ag` | blemish: "wegen" rendered as "ради" (purpose, "for the sake of") rather than из-за/ввиду (cause)… |
| B-quality | 1 | ord:62 | `aMhriskanDa` | minor: singular 'ноги' vs reference plural, but idiomatic and acceptable. publishable. |
| B-quality | 1 | ord:72 | `akarA` | minor: "одного растения" is slightly more literal than idiomatic german indefinite "einer pflanze", but standa… |
| B-quality | 1 | ord:87 | `akalpa/` | only nit: "с собой" is a minor expansion not literally in the german, but it does not distort sense. publishab… |
| B-quality | 1 | ord:107 | `akAryakArin` | minor nuance only: "unterlässt" (neglects/omits) is slightly stronger than "не исполняющий" (does not fulfil)… |
| B-quality | 1 | ord:131 | `akftakAram` | minor stylistic point only: "поступали" (acted) is a touch looser than "делали" (done) but idiomatic and meani… |
| B-quality | 1 | ord:189 | `akzama` | only nit: "nicht gewachsen"→"не соответствующий" is slightly loose (≈"not up to"), but defensible. publishable… |
| B-quality | 1 | ord:207 | `akzaracCandas` | minor nuance only: german "quantität" rendered as "долготе" (acceptable prosodic term). publishable. |
| B-quality | 1 | ord:243 | `a/kzita` | minor nuance: непреходящий for unvergänglich leans 'enduring' over 'imperishable' but is in range and mirrors… |
| B-quality | 1 | ord:292 | `aKewika` | minor nuance only: "gesichert" (guaranteed) rendered as softer "подтверждается" (confirmed) — idiomatic, accep… |

## Downstream

The requeue handoff (fenced out of Wave 1) re-locates each A/B row in the
CURRENT store by headword + subcard (the `ord:N` id is dead; `key2` above is
the printed-form key), patches or retranslates, and closes this log with the
PR link. Until then, treat this file as the canonical list of judge-confirmed
pwg_ru translation defects from the legacy G5 pass.

_Dr. Mārcis Gasūns_
