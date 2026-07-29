#!/usr/bin/env python
r"""rv_divergence_explain.py -- make the divergence gate readable for a human (H1906).

The v1 gate sheet asked a reviewer to re-derive by eye what the model had already
computed: it printed the assigned class and two full renderings, and nothing else.
It did not even print the `why` the typer already stored on every pair. MG's verdict
on that sheet, 29-07-2026: "нужна подсветка и мотивация, я не буду 100 раз читать
4 перевода, выискивая глазами то, что ты уже и так пометил".

This pass re-queries ONLY the items on the sheet, asking for three things v1 never
requested:

  span_a / span_b   the EXACT substring of each rendering carrying the difference,
                    verbatim so the sheet can highlight it in place. `null` where the
                    class makes it meaningless (the missing side of `omitted_by_one`).
  why_ru            a real explanation in Russian -- what the difference IS, not a
                    restatement of the class name. The reviewer reads Russian; the
                    renderings are German/Russian/English.
  asymmetry_note    optional, and specifically requested after MG's point that
                    "не понятно как сравнивать плохой ранний английский перевод
                    griffith и хороший немецкий поздний перевод grassmann" -- when a
                    pair spans a 70-year quality/era gap, say so, because the class
                    alone hides that a "divergence" may be Griffith's Victorian padding
                    rather than a scholarly disagreement.

Verbatim spans are VERIFIED, not trusted: a span the model returns that is not an exact
substring of its rendering is recorded as `span_a_verbatim: false` and the sheet falls
back to quoting it instead of highlighting. The unverified rate is reported, so a
silently-degraded sheet is impossible.

  python src/rv_divergence_explain.py --items <sheet_items.json> --out <explained.jsonl>
  python src/rv_divergence_explain.py selftest
"""
import argparse
import json
import os
import sys
import threading

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
RUN_DIR = os.path.join(PWG_RU_DIR, 'h1844')

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'pilot', 'h1210'))
import deepseek_arm as ds_arm          # noqa: E402
import rv_divergence_type as dv        # noqa: E402

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
DEFAULT_OUT = os.path.join(RUN_DIR, 'rv_divergence_explained.jsonl')

# Era/quality gap in years above which the pair gets an asymmetry prompt (MG's point:
# Griffith 1896 vs Geldner 1951 is not a symmetric comparison).
TRANSLATOR_YEAR = {
    'grassmann_de_1876': 1876, 'geldner_de_1951': 1951,
    'elizarenkova_ru_1989': 1989, 'griffith_en_1896': 1896,
}

SYSTEM = '''Ты — сравнительный филолог-ведист. Тебе дают ОДНУ строфу Ригведы в двух
переводах и УЖЕ ПРИСВОЕННЫЙ класс расхождения. Твоя задача — не переклассифицировать,
а ПОКАЗАТЬ человеку, где именно это расхождение находится и в чём оно состоит.

Верни РОВНО один JSON-объект и ничего больше.

Схема:
{"span_a": "<точная подстрока перевода A или null>",
 "span_b": "<точная подстрока перевода B или null>",
 "why_ru": "<по-русски, 1-2 предложения: в чём именно разница>",
 "asymmetry_note": "<по-русски или null>"}

Правила, которые важнее желания быть полезным:

- span_a и span_b — ДОСЛОВНЫЕ подстроки соответствующих переводов, скопированные
  посимвольно. Не перефразируй, не переводи, не нормализуй регистр и не дописывай
  многоточия. Если выделить нечего — null. Короткие: слово или словосочетание, не
  целое предложение.
- Для класса omitted_by_one: span_a — то, что ЕСТЬ у одного и ОТСУТСТВУЕТ у другого;
  span_b — null (у второго этого просто нет). Если пропуск у A, а не у B, поменяй
  местами: span_a=null, span_b=<то, что есть у B>.
- Для added_by_one: заполни тот span, где материал ДОБАВЛЕН, второй — null.
- Для lexical_variant и semantic_shift: оба span-а — сопоставимые места, которые
  переданы по-разному. Именно те слова, из-за которых присвоен класс.
- Для agreement: оба span-а могут быть null, а why_ru объясняет, почему совпадение
  считается содержательным, несмотря на разные языки и слова.
- why_ru называет РАЗНИЦУ конкретно ("Грассман читает X как «...», Гельднер — как
  «...»"), а не повторяет название класса.
- asymmetry_note заполняй ТОЛЬКО если разрыв между переводами по времени или по
  качеству реально мешает считать расхождение научным спором: например, Гриффит 1896
  свободно дополняет текст пояснениями, и «расхождение» с Гельднером 1951 может быть
  его викторианской вольностью, а не другим прочтением. Иначе — null.'''


def load_stanzas():
    out = {}
    with open(STANZA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                out[rec['location']] = rec
    return out


def build_user(stanza, a, b, cls, why):
    ta = stanza['translations'][a]['text'] or ''
    tb = stanza['translations'][b]['text'] or ''
    gap = abs(TRANSLATOR_YEAR[a] - TRANSLATOR_YEAR[b])
    lines = [
        'Ригведа %s.' % stanza['location'], '',
        'Перевод A — %s:' % dv.TRANSLATOR_LABEL[a], ta.replace('\n', ' / '), '',
        'Перевод B — %s:' % dv.TRANSLATOR_LABEL[b], tb.replace('\n', ' / '), '',
        'Присвоенный класс: %s' % cls,
    ]
    if why:
        lines.append('Краткое обоснование модели (v1): %s' % why)
    lines.append('Разрыв между переводами: %d лет.' % gap)
    return '\n'.join(lines)


def verify_span(span, text):
    """Verbatim check. Returns (span_or_None, is_verbatim)."""
    if not span:
        return None, True          # a deliberate null is not a failure
    return span, span in (text or '')


def explain_one(client, stanza, a, b, cls, why):
    text, call = client.chat(SYSTEM, build_user(stanza, a, b, cls, why),
                             '%s|%s|%s' % (stanza['location'], a, b))
    if text is None:
        return {'error': 'transport: %s' % call.get('error')}
    try:
        obj, _ = ds_arm.extract_json(text)
    except ValueError as e:
        return {'error': 'unparseable: %s' % e}
    ta = stanza['translations'][a]['text'] or ''
    tb = stanza['translations'][b]['text'] or ''
    span_a, ok_a = verify_span(obj.get('span_a'), ta)
    span_b, ok_b = verify_span(obj.get('span_b'), tb)
    return {
        'span_a': span_a, 'span_a_verbatim': ok_a,
        'span_b': span_b, 'span_b_verbatim': ok_b,
        'why_ru': (obj.get('why_ru') or '').strip(),
        'asymmetry_note': (obj.get('asymmetry_note') or None),
    }


def run(items, out_path, env_file, workers, model, provider):
    stanzas = load_stanzas()
    spec = dv.PROVIDERS[provider]
    key = os.environ.get(spec['key_env']) or ds_arm.load_env_file(env_file).get(spec['key_env'])
    if not key:
        sys.exit('%s not found (env or --env-file)' % spec['key_env'])
    client = ds_arm.DeepSeek(spec['base'], key, model, 1400)

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    lock = threading.Lock()
    fh = open(out_path, 'w', encoding='utf-8', newline='\n')
    stats = {'n': 0, 'nonverbatim': 0, 'errors': 0, 'asym': 0}

    def work(item):
        loc, pair_key, cls, why = item
        a, b = pair_key.split('|')
        res = explain_one(client, stanzas[loc], a, b, cls, why)
        row = {'location': loc, 'pair': pair_key, 'class': cls, **res}
        with lock:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
            fh.flush()
            stats['n'] += 1
            if res.get('error'):
                stats['errors'] += 1
            else:
                if not res['span_a_verbatim'] or not res['span_b_verbatim']:
                    stats['nonverbatim'] += 1
                if res.get('asymmetry_note'):
                    stats['asym'] += 1
            if stats['n'] % 20 == 0 or stats['n'] == len(items):
                print('  explained %d/%d' % (stats['n'], len(items)))

    dv._pool(items, work, workers)
    fh.close()
    cost = client.cost()
    print('explain: %d items -> %s' % (stats['n'], out_path))
    print('  non-verbatim spans (quoted, not highlighted): %d' % stats['nonverbatim'])
    print('  asymmetry notes emitted: %d' % stats['asym'])
    print('  errors: %d' % stats['errors'])
    print('  cost: $%.4f' % cost['usd'])
    return 0


def load_items_from_pilot(pilot_path, ids):
    """ids: iterable of '<location>|<a>|<b>' as used by the sheet."""
    want = set(ids)
    out = []
    with open(pilot_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for pair_key, entry in rec['pairs'].items():
                key = '%s|%s' % (rec['location'], pair_key)
                if key in want and entry.get('class'):
                    out.append((rec['location'], pair_key, entry['class'],
                                entry.get('why') or ''))
    return out


def selftest():
    assert verify_span('Agni', 'Den Priester Agni preise ich') == ('Agni', True)
    assert verify_span('Feuer', 'Den Priester Agni preise ich') == ('Feuer', False)
    assert verify_span(None, 'x') == (None, True)
    assert verify_span('', 'x') == (None, True)

    stanza = {'location': '1.1.1', 'translations': {
        'grassmann_de_1876': {'status': 'present', 'text': 'Den Priester Agni preise ich'},
        'griffith_en_1896': {'status': 'present', 'text': 'I Laud Agni the chosen Priest'}}}
    msg = build_user(stanza, 'grassmann_de_1876', 'griffith_en_1896',
                     'lexical_variant', 'Priester vs Priest')
    assert 'Ригведа 1.1.1' in msg
    assert 'Разрыв между переводами: 20 лет.' in msg, msg
    assert 'Присвоенный класс: lexical_variant' in msg
    assert 'Priester vs Priest' in msg
    assert set(TRANSLATOR_YEAR) == set(dv.TRANSLATORS)
    print('rv_divergence_explain selftest OK -- verbatim span check, prompt assembly, '
          'era-gap computation')
    return 0


def main():
    ap = argparse.ArgumentParser(description='explain + localize divergence (H1906)')
    ap.add_argument('cmd', nargs='?', default='run', choices=['run', 'selftest'])
    ap.add_argument('--ids', help='file with one <location>|<a>|<b> id per line')
    ap.add_argument('--pilot', default=os.path.join(PWG_RU_DIR, 'rv_divergence_pilot.jsonl'))
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--env-file', default=os.path.join(HERE, '.env'))
    ap.add_argument('--provider', choices=sorted(dv.PROVIDERS), default='deepseek')
    ap.add_argument('--model', default='deepseek-chat')
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()
    if a.cmd == 'selftest':
        return selftest()
    if not a.ids:
        sys.exit('--ids is required for `run`')
    ids = [l.strip() for l in open(a.ids, encoding='utf-8') if l.strip()]
    items = load_items_from_pilot(a.pilot, ids)
    print('explain: %d of %d requested ids resolved in the pilot' % (len(items), len(ids)))
    return run(items, a.out, a.env_file, a.workers, a.model, a.provider)


if __name__ == '__main__':
    sys.exit(main())
