# Review-queue triage — pwg_ru legacy `needs_review`

**Auto-generated — do not hand-edit.** Regenerate with
[`src/triage_review_queue.py`](src/triage_review_queue.py).
Ranked worklist (one row per card, all columns): `src/_review_queue.triage.csv`
(gitignored — it is your personal worklist, derived from the gitignored
`src/_review_queue.jsonl`).

This is **pre-processing, not adjudication.** Every row was already scored by the
Opus QA judge (rubric: [`pwg_ru_prompts/2_qa_sudya_opus.txt`](pwg_ru_prompts/2_qa_sudya_opus.txt));
this tool only *buckets* those existing verdicts by defect type and orders them
by the judge's own severity. **You** make the final call on every card — nothing
here was auto-edited, and no correction was applied to any source.

## At a glance — 217 cards

| bucket | what it is | count | how to work it |
|--------|-----------|------:|----------------|
| **C — source-data defect** | the 19th-c. German source itself is broken (OCR/garble/typo) so a clean RU is impossible | **0** | escalate to Cologne; do **not** "fix" in Russian |
| **A — mechanical / format** | German connective/preposition left untranslated, or anchors/structure damaged | **13** | fast, low-judgement edits; the judge names the exact word |
| **B — translation-quality** | German *was* translated but the rendering is doubted (semantic / terminology / nuance) | **19** | needs scholarly judgement; weigh against the attested gloss |
| **FAST — likely clean** | sev ≤ 1, no actionable defect ("Publishable" / minor non-issue) | **185** | bulk rubber-stamp / spot-check |

Severity is the judge's own 0–5 confidence (rubric: 1–2 = keep, 3 = arguable,
4–5 = must redo). **23 cards score sev ≥ 2** — those are the real work; the other
194 are minor.
**197/217** cards carry an independent attested-dictionary corroboration
(Kochergina / KOW / Knauer …) in the `attested` column — lean on it in bucket B.

## Suggested order of work

1. **C (source defects) — 0.** None survived triage: every "source
   quirk" the judge noted was *faithfully mirrored* in the RU, so there is
   nothing to escalate. If you spot a genuine source defect while reviewing,
   route it to csl-orig / Cologne — never silently "correct" it in the RU.
2. **A (mechanical) — 13.** Quickest wins. Each is one or two
   untranslated German function-words (`und`→и, `oder`→или, `im`→в, `von`→от)
   sitting in an otherwise-fine card. Confirm the judge's call and patch.
3. **B (quality) sev ≥ 2 — 10.** The cards that need you. Semantic choice,
   terminology calque, gender/agreement slips, awkward word order. Decide
   against the attested gloss where present.
4. **B (quality) sev 1 — 9** and **FAST — 185.** Minor nuances
   and clean cards. Skim / spot-check; bulk-approve.

## A — mechanical / format (13)

| sev | headword (key2) | attested? | defect (judge's words) |
|----:|-----------------|:---------:|------------------------|
| 4 | `akz` | yes | fail on check (c): the german connectives 'und' (4x) and 'oder' (2x) are left untranslated throughout — should be russian 'и'/'или'. the text is th… |
| 3 | `aMSu/` | yes | fail on check (c): german connective prose outside the gloss markers left untranslated in 6 spans — "im" x3 (lines {t15..t17}, {t21..t22}, {t23..t2… |
| 3 | `aMhasaspati/` | — | defect: the german connective "von" inside the parenthetical ({t2} {t3} von {t4}) was left untranslated — violates check (c). should be russian "от… |
| 2 | `aMSupawwa` | yes | defect: the german connective "also" (= "т. е."/"таким образом") in the line ({t5} = {t6} also {t7}) was left untranslated, so criterion (c) fails.… |
| 2 | `aMSuhasta` | yes | defect: german "im" on the last line ({t6} im {t7}) left untranslated — should be russian "в". not publishable until "im" is rendered in russian; o… |
| 2 | `aMsaDrI/` | — | one defect: the german word "von" in ({t2} {t3} von {t4}) is left untranslated — should be «от»/«из». latin abbr. and case agreement otherwise soun… |
| 2 | `a/MseBArika` | — | minor: the etymological marker "(von {t2})" retains untranslated german "von" — but it is copied verbatim from the source skeleton scaffold (struct… |
| 2 | `aMh` | yes | defect: german conjunction "und" in the final line ({t16} {t17} und {t18}) left untranslated — should be russian "и". rest of that clause correctly… |
| 2 | `aMhati/` | yes | minor: german language abbreviations "lat." and "goth." left untranslated (should be "лат."/"гот."); journal title "zeitschrift für ... sprachf." a… |
| 2 | `a/Mhri` | yes | defect: german preposition "von" in "(von 1. {t2})" left untranslated (should be "от"/"из"), violating check (c). minor function-word residue, sema… |
| 2 | `akArya` | yes | one defect: line "{t5} im {t6}" leaves the bare german preposition "im" untranslated (should be russian "в") — german leftover outside the {% %} wr… |
| 2 | `akza/n` | yes | defect: the final german conjunction "und" in "{t53} 2. und {t54} ." was left untranslated — should be russian "и". single-word miss but it violate… |
| 2 | `akzamA` | yes | defect: german connective "im" on line 2 left untranslated (should be "в" or similar). one short function word leak — minor but it is untranslated … |

## B — translation-quality, sev ≥ 2 (10)

| sev | headword (key2) | attested? | defect (judge's words) |
|----:|-----------------|:---------:|------------------------|
| 3 | `aMSAvataraRa` | yes | "of chapters") clashes with the ordinals "64-й — 67-й" (should be "глав 64—67" or "глав 64-й — 67-й книги"), and the trailing genitive "des" linkin… |
| 2 | `a` | yes | one minor slip: "demselben stamme begegnen wir ferner" -> "тому же основанию мы встречаем далее" — "основанию" (dative, also wrong lexeme: should b… |
| 2 | `aMSa` | yes | minor: "das gewicht der autoritäten" rendered loosely as "авторитетом источников" (drops "weight", adds "источников") — faithful in sense, idiomati… |
| 2 | `aMSin` | — | minor blemish: german has a discontinuous verb "alle mögen gleiche theile ... empfangen"; the ru added "получить" into segment 1 ("все могут получи… |
| 2 | `aMhu/` | yes | only blemish: slightly inverted/awkward word order in "это значение слово имеет" (more natural would be "это значение имеет слово/это слово имеет")… |
| 2 | `aMhuBe/da` | — | minor: "engspaltig" can mean "narrow-columned" (typesetting) vs. the chosen "узкощелистая" (narrow-slit/fissured) — defensible but a slight lexical… |
| 2 | `aMhUraRa/` | — | minor: german "als {t7}" (= "as [a] n.") rendered "в значении {t7}" (= "in the sense of"); "как" would be closer, but acceptable lexicographic phra… |
| 2 | `a/kfzIvala` | yes | minor nuance: "abgeneigt" (averse/disinclined) rendered as "чуждый" (alien to) is a slight semantic softening, but idiomatic and consistent with th… |
| 2 | `akzayatftIyA` | yes | minor gender slip: "один {t7}" (masc.) renders german "eine {t7}" where t7=smṛti (fem. in russian) -- should be "одна". also "начиналась {t5}" uses… |
| 2 | `ag` | yes | blemish: "wegen" rendered as "ради" (purpose, "for the sake of") rather than из-за/ввиду (cause, "on account of") — minor semantic shift, sense sti… |

---
*Buckets are heuristic groupings of the judge's prose, meant to order your pass — not a substitute for reading the card. The full `reason` text for every row is in `src/_review_queue.triage.csv`.*
