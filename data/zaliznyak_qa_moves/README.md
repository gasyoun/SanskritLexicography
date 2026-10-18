# Zaliznyak Q&A move annotation (H5171) — Socratic-tutor eval corpus

_Created: 20-09-2026 · Last updated: 20-09-2026_

Regex+contextual annotation of **Q&A-ходов** («вопрос → совывыведение → вердикт
ученику») over the ingested Zaliznyak lecture corpus. Turns the transcripts into
an eval corpus for the Socratic tutor (spec: Systema PR
[#2724](https://github.com/gasyoun/Systema-Sanscriticum/pull/2724) —
`docs/SOCRATIC_TUTOR_N02_PROMPT_SPEC.md` after merge; handoff
[H5170](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H5170-OxAlpha_Systema-Sanscriticum_socratic-n02-tutor-prompt-spec_20.09.26.md)).

## Files

| File | What |
|---|---|
| `annotate_qa_moves.py` | The tool (stdlib-only, deterministic). Source of truth — JSONL/stats are derived. |
| `zaliznyak_qa_moves.jsonl` | One row per detected move occurrence. |
| `stats.json` | Per-class totals, per-file counts, top markers, verification numbers. |

## Inputs (BookIndex repo, sibling checkout)

1. **27 timecoded transcripts**: `BookIndex/data/imports/lectures-v2/transcripts/*.json`
   (schema `lecture_transcript/1`; ~240k words, 3 697 timecoded segments).
2. **itkin school-dialog contexts**: `BookIndex/src/content/itkin-i.-b..md`,
   `itkin-a.-i..md` — ~120-char KWIC windows with «Из зала» replies.

Regenerate:

```
python3 data/zaliznyak_qa_moves/annotate_qa_moves.py --selftest
python3 data/zaliznyak_qa_moves/annotate_qa_moves.py \
  --bookindex ../BookIndex --out data/zaliznyak_qa_moves
```

## Schema (JSONL)

```json
{"replica_id": "LJlxadWkzPc.s022.m00", "move_class": "deferred",
 "quote": "…я пока оставляю этот вопрос нерешённым…", "marker": "оставляю … нерешённ",
 "t": 1275, "file": "LJlxadWkzPc", "source": "lectures-v2/transcripts",
 "speaker": "А. А. Зализняк"}
```

`replica_id` = `<video_id|itkin-stem>.s<segment>.m<match>` (transcripts) /
`.ctx<k>.m<n>` (itkin windows). `t` = seconds, null for itkin. `speaker` = null
on itkin windows (truncated KWIC — attribution unreliable by design).

## Move classes (per Uprava [§3](https://github.com/gasyoun/Uprava/blob/main/docs/ZALIZNYAK_HINTING_STYLE_ANALYSIS_19-09-2026.md))

| Class | § | Verbatim anchor found in corpus |
|---|---|---|
| `answer_hold` | §3.1 | «не выкрикивайте… дайте возможность подумать тем, кто первый раз столкнулся» |
| `coinference` | §3.3 | «Как вы думаете, почему он такой кривой? Ответ из зала: …» |
| `deferred` | §3.5 | «я пока оставляю этот вопрос нерешённым, мы с вами попробуем его решить дальше» |
| `trap` | §3.7 | «Это, на самом деле, немножко ловушка такая» |
| `refusal_generalize` | §3.4 | «Я не буду вам это говорить, надеюсь, что вы сами это поймете» |
| `uncertainty_sign` | §3.9 | «что именно значит суффикс -ята- довольно трудно судить» |

Totals (this run): coinference 215 · uncertainty_sign 11 · trap 4 ·
refusal_generalize 3 · deferred 3 · answer_hold 3 = **239 rows over 27 files**
(29 scanned; 26/27 transcripts + `itkin-i-b` contribute rows; `itkin-a-i` and
film `BZQgfGBtCho` are move-free).

## Verification (H5171 handoff)

1. **Stratified sample 21 rows** (final data, seed 99): 20/21 class confirmed by
   quote. The one miss is a film-interviewer question (`А. Мозжухин: Почему
   так?…`, `P0G948VmXtM`) — speaker-marker list does not cover film
   interviewers; attribution defaults to the lecture voice.
2. **§2 sweep order-of-magnitude**: per-file rates ours/27 vs sweep/265 —
   «почему?» 4.26 vs 4.83, «как вы думаете» 0.93 vs 0.71, «попробуйте» 0.81 vs
   0.69, «подумайте» 0.30 vs 0.37, «трудно сказать/не ясно» 0.22 vs 0.23,
   «угадаете» 0.07 vs 0.20, «спорно/осторожно» 0.07 vs 0.22 — same orders,
   no contradiction.

## Known limitations

- Regex pass over unattributed transcript segments: speaker attribution uses a
  nearest-preceding-marker heuristic (`Из зала`/`Студент` rows are excluded and
  counted, film interviewers are not covered).
- Rare classes (trap 4, refusal 3, deferred 3, answer_hold 3) are anchored on
  §3 verbatim evidence but are low-recall — treat as high-precision seeds, not
  census.
- Legal frame: quotes stay short (≤240 chars), corpus inputs live in BookIndex
  (derived-only landing, precedent H1333); no full in-copyright text is stored
  here.

## Links (bilateral per H5171)

- Spec → corpus: [H5170](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H5170-OxAlpha_Systema-Sanscriticum_socratic-n02-tutor-prompt-spec_20.09.26.md) «золотые диалоги: itkin» + eval baseline.
- Analysis → corpus: [ZALIZNYAK_HINTING_STYLE_ANALYSIS_19-09-2026.md](https://github.com/gasyoun/Uprava/blob/main/docs/ZALIZNYAK_HINTING_STYLE_ANALYSIS_19-09-2026.md) §6.3, §8.
- Corpus → spec: this file (+ Systema PR [#2724](https://github.com/gasyoun/Systema-Sanscriticum/pull/2724)).

_Гасунс_
