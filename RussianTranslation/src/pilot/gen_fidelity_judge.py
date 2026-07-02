#!/usr/bin/env python
r"""Emit a self-contained Opus fidelity-judge workflow from the stratified sample.

Mirrors gen_opt_harness2: a Python generator inlines the data into a Workflow JS so the script
is self-contained (workflow scripts have no filesystem access). Each agent judges a batch of
cards' DE->RU faithfulness against the adapted qa_judge_v4 rubric and returns the established
{key, ok, severity, issues, note} verdict schema (judge_ab_score: BAD = ok=false || severity>=3).

  python src/fidelity_sample.py --n 100              # writes the sample
  python src/pilot/gen_fidelity_judge.py [--batch 6] # writes src/pilot/run_fidelity_judge.js
  # run run_fidelity_judge.js via the Workflow tool; save result.verdicts; then:
  python src/pilot/fidelity_aggregate.py <verdicts.json>
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
SAMPLE = os.path.join(OUT, 'fidelity_sample.jsonl')
HARNESS = os.path.join(HERE, 'run_fidelity_judge.js')
CAP = 600  # cap de/ru per sense for judging (gloss meaning is up front; citations are markup)

RUBRIC = (
    "Ты — корректор перевода санскритско-немецкого словаря Бётлингка-Рота (PWG) на русский. "
    "Для каждой карточки даны: заголовок (iast) и значения (senses), у каждого немецкий глосс "
    "(de) и его русский перевод (ru). Оцени, является ли русский ВЕРНЫМ переводом немецкого.\n\n"
    "Критерии BAD (severity>=3 или ok=false):\n"
    "1. semantic — русский искажает/инвертирует/теряет смысл немецкого глосса.\n"
    "2. anchors — потеряны/изменены санскрит {#..#}, цитаты <ls>, аббревиатуры <ab>, глоссы {%..%}.\n"
    "3. hallucination — русский добавляет значение, которого нет в немецком.\n"
    "4. truncation — русский опускает значения/содержание (с поправкой: глоссы здесь обрезаны до "
    "CAPCHARS символов для оценки, не штрафуй за обрыв в самом конце).\n"
    "5. grammar/anglicism — германизм-калька, ошибки падежа/рода, плохая русская естественность.\n\n"
    "НЕ считать ошибкой (НЕ BAD):\n"
    "- сохранённые немецкие сокращения (Bed., Schol., vgl., ebend., u. s. w.) — это конвенция PWG;\n"
    "- сохранённые латинские эвфемизмы (inire feminam, legere, seminis profectui) дословно;\n"
    "- сохранённые французские/научные термины и {%German%}-эхо рядом с русским;\n"
    "- отсутствие связки (немецкий род. падеж не требует предлога).\n\n"
    "МЕТКИ issues (используй ТОЛЬКО эти слова, по одной метке на дефект; детали — в note, не в "
    "issues; это канонический словарь pwg_ru/DharmaMitra crosswalk из FU1_PLAN.md):\n"
    "  addition            — русский добавляет значение/атрибуцию, которых нет в немецком\n"
    "  term-mistranslation — конкретное слово/термин переведено неверно или многозначность "
    "обработана неверно (критерий 1 semantic)\n"
    "  grammar             — германизм-калька, ошибки падежа/рода, плохая русская естественность "
    "(критерий 5)\n"
    "  omission            — содержание значения пропущено (не путать с обрезкой по CAPCHARS)\n"
    "  register-drift      — сдвиг тона/регистра относительно источника\n"
    "  markup-loss         — потеряна обёртка {%..%}/<div>, а не сам смысл (критерий 2 anchors, "
    "когда смысл сохранён)\n\n"
    "severity: 0-1 чисто, 2 мелочь, 3 реальный дефект, 4-5 грубый. Верни по ОДНОМУ вердикту на "
    "карточку (по её ключу key): {key, ok(bool), severity(0-5), issues([str]), note(одна фраза)}."
).replace('CAPCHARS', str(CAP))

VERDICTS_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["verdicts"],
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["key", "ok", "severity", "issues", "note"],
        "properties": {
            "key": {"type": "string"},
            "ok": {"type": "boolean"},
            "severity": {"type": "integer", "minimum": 0, "maximum": 5},
            "issues": {"type": "array", "items": {"type": "string"}},
            "note": {"type": "string"},
        }}}},
}

TEMPLATE = """// AUTO-DERIVED fidelity-judge workflow (gen_fidelity_judge.py). Opus judges DE->RU faithfulness.
export const meta = {
  name: 'pwgru-fidelity-judge',
  description: 'Opus DE->RU fidelity judge over a stratified pwg_ru sample (interim number)',
  phases: [{ title: 'Judge' }],
}
const BATCHES = %(batches)s
const RUBRIC = %(rubric)s
const SCHEMA = %(schema)s
phase('Judge')
const results = await parallel(BATCHES.map((batch, i) => () =>
  agent(RUBRIC + '\\n\\nКАРТОЧКИ (JSON):\\n' + JSON.stringify(batch),
        { label: 'judge-' + i, phase: 'Judge', schema: SCHEMA })))
const verdicts = results.filter(Boolean).flatMap(r => (r && r.verdicts) || [])
return { verdicts, judged: verdicts.length, batch_count: BATCHES.length }
"""


def trim(card):
    senses = []
    for s in (card.get('senses') or [])[:8]:
        senses.append({'tag': s.get('tag'),
                       'de': (s.get('de') or '')[:CAP],
                       'ru': (s.get('ru') or '')[:CAP]})
    return {'key': card['key'], 'iast': card.get('iast'), 'stratum': card.get('stratum'),
            'senses': senses}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, default=6)
    ap.add_argument('--sample', default=SAMPLE)
    ap.add_argument('--out', default=HARNESS)
    args = ap.parse_args()
    cards = [trim(json.loads(l)) for l in open(args.sample, encoding='utf-8') if l.strip()]
    batches = [cards[i:i + args.batch] for i in range(0, len(cards), args.batch)]
    js = TEMPLATE % {
        'batches': json.dumps(batches, ensure_ascii=False),
        'rubric': json.dumps(RUBRIC, ensure_ascii=False),
        'schema': json.dumps(VERDICTS_SCHEMA),
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(js)
    print('wrote %s | %d cards in %d batches of <=%d' % (args.out, len(cards), len(batches), args.batch))


if __name__ == '__main__':
    main()
