#!/usr/bin/env python
r"""build_rv_divergence_gate_sheet.py -- the step-8 human gate (H1844, deliverable W1.7).

Draws 100 typed (stanza x translator-pair) items out of the divergence pilot and renders
them as an HTML voting sheet. Markdown checkbox sheets are banned org-wide; this goes
through the canonical `csl_pyutil.render_review_sheet` + the H1404 binding standard
(`review_binding.stamp` / `write_lock`), so the export carries a `content_hash` bound to
the exact HTML voted in and validates against `schemas/decisions.schema.json`.

Vote semantics, mapped onto the standard approve/reject/defer vocabulary:

  approve         the model's class is right for this pair at this stanza
  reject + label  the model's class is wrong; the picked `reject_label` is the class it
                  SHOULD have had (the five classes are the reject-label typology)
  defer           genuinely undecidable from the two renderings alone

Agreement (R15) = approve / (approve + reject), and the gate releases step 9 at >= 80 %.
Sampling is stratified over the MODEL's assigned classes rather than uniform, so the rare
classes are actually scrutinised -- a uniform draw from a run where one class took 62 % of
the labels would spend the whole human budget re-confirming that one class.

  python src/build_rv_divergence_gate_sheet.py --pilot pwg_ru/rv_divergence_pilot.jsonl
"""
import argparse
import collections
import io
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
REVIEW_DIR = os.path.join(RT_ROOT, 'review')

from csl_pyutil import render_review_sheet          # noqa: E402
from review_binding import stamp, write_lock        # noqa: E402
from review_sheet_standard import standard_config   # noqa: E402
import rv_divergence_type as dv                     # noqa: E402

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
GENERATED = '2026-07-29'
SHEET_ID = 'rv_divergence_gate_2026-07-29'
DEFAULT_N = 100
DEFAULT_SEED = 1844

CLASS_HELP = {
    'agreement': 'одно и то же содержание; разные слова и разные языки — норма',
    'lexical_variant': 'тот же референт и то же прочтение, другой выбор слова',
    'semantic_shift': 'настоящее расхождение прочтений — не взаимозаменяемы',
    'omitted_by_one': 'один переводчик не передал то, что передал другой',
    'added_by_one': 'один переводчик добавил то, чему нет соответствия у другого',
}


def load_stanzas():
    out = {}
    with io.open(STANZA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                out[rec['location']] = rec
    return out


def load_pilot(path):
    """-> [(location, pair_key, entry)] over MODEL-decided pairs only.

    Deterministic pairs are excluded on purpose: asking a human to confirm that Geldner
    did not translate a stanza he demonstrably did not translate spends the 100-vote
    budget on the one thing already known with certainty.
    """
    rows = []
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for pair_key, entry in rec['pairs'].items():
                if entry.get('method') == 'model' and entry.get('class'):
                    rows.append((rec['location'], pair_key, entry))
    return rows


def stratified_by_class(rows, n, seed):
    by_class = collections.defaultdict(list)
    for r in rows:
        by_class[r[2]['class']].append(r)
    present = [c for c in dv.FIVE_CLASSES if by_class[c]]
    rng = random.Random(seed)
    base, extra = divmod(n, len(present))
    picked = []
    for i, cls in enumerate(present):
        want = min(base + (1 if i < extra else 0), len(by_class[cls]))
        picked.extend(rng.sample(sorted(by_class[cls], key=lambda r: (r[0], r[1])), want))
    # top up from the largest classes if a rare class could not fill its quota
    if len(picked) < n:
        seen = {(r[0], r[1]) for r in picked}
        rest = [r for r in rows if (r[0], r[1]) not in seen]
        picked.extend(rng.sample(sorted(rest, key=lambda r: (r[0], r[1])),
                                 min(n - len(picked), len(rest))))
    picked.sort(key=lambda r: ([int(x) for x in r[0].split('.')], r[1]))
    return picked


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_items(picked, stanzas):
    items = []
    for location, pair_key, entry in picked:
        a, b = pair_key.split('|')
        stanza = stanzas[location]
        panels = []
        for key in (a, b):
            t = stanza['translations'][key]
            text = esc((t['text'] or '')).replace('\n', '<br>')
            panels.append((dv.TRANSLATOR_LABEL[key], '<div class="rv-rend">%s</div>' % text))
        other = [k for k in dv.TRANSLATORS if k not in (a, b)]
        ctx = []
        for key in other:
            t = stanza['translations'][key]
            if t['status'] == 'present':
                ctx.append('<b>%s:</b> %s' % (esc(dv.TRANSLATOR_LABEL[key]),
                                              esc(t['text'] or '').replace('\n', ' / ')))
        if ctx:
            panels.append(('Остальные два перевода (для контекста, не голосуются)',
                           '<div class="rv-ctx">%s</div>' % '<br><br>'.join(ctx)))
        items.append({
            'id': '%s|%s' % (location, pair_key),
            'filt': entry['class'],
            'title': 'RV %s — %s ↔ %s' % (location, a.split('_')[0], b.split('_')[0]),
            'badges': [entry['class'], 'маṇḍала %d' % stanza['mandala']],
            'question': (
                'Модель присвоила этой паре класс <b>%s</b> (%s).<br>'
                'Approve = класс верен · Reject = неверен, выберите правильный класс '
                'в списке · Defer = по двум переводам не решить.'
                % (esc(entry['class']), esc(CLASS_HELP.get(entry['class'], '')))),
            'note_placeholder': 'reject → почему именно этот класс неверен',
            'panels': panels,
        })
    return items


def main():
    ap = argparse.ArgumentParser(description='H1844 step-8 divergence human gate')
    ap.add_argument('--pilot', default=os.path.join(PWG_RU_DIR, 'rv_divergence_pilot.jsonl'))
    ap.add_argument('--n', type=int, default=DEFAULT_N)
    ap.add_argument('--seed', type=int, default=DEFAULT_SEED)
    ap.add_argument('--out', default=os.path.join(REVIEW_DIR, '%s.html' % SHEET_ID))
    ap.add_argument('--locks-dir', default=os.path.join(REVIEW_DIR, 'locks'))
    a = ap.parse_args()

    if not os.path.exists(a.pilot):
        sys.exit('pilot not found: %s -- run `rv_divergence_type.py pilot` first' % a.pilot)
    stanzas = load_stanzas()
    rows = load_pilot(a.pilot)
    if not rows:
        sys.exit('no model-decided pairs in %s' % a.pilot)
    picked = stratified_by_class(rows, a.n, a.seed)
    items = build_items(picked, stanzas)

    dist = collections.Counter(r[2]['class'] for r in rows)
    total = sum(dist.values())
    config = {
        'sheet_id': SHEET_ID,
        'title': 'RV · типология расхождений — калибровочный гейт (H1844, шаг 8)',
        'subtitle': (
            '%d пар (станза × пара переводчиков) из пилота на %d стансах. Выборка '
            'стратифицирована по классу, присвоенному моделью, а НЕ равномерна: в самом '
            'пилоте классы распределены как %s, поэтому равномерная выборка потратила бы '
            'весь человеческий бюджет на подтверждение одного класса. Гейт открывает '
            'полный прогон при согласии ≥ 80 %% (R15).'
            % (len(items), len({r[0] for r in rows}),
               ', '.join('%s %.0f%%' % (c, 100.0 * dist[c] / total)
                         for c in dv.FIVE_CLASSES if dist[c]))),
        'footer': (
            'Approve = класс модели верен · Reject = неверен (обязательно выберите класс, '
            'который должен быть) · Defer = не решается по двум переводам.<br>'
            'Согласие = approve / (approve + reject). Экспорт валидируется против '
            'review/locks/%s.lock.json перед применением.' % SHEET_ID),
        'approve_label': 'Класс верен',
        'reject_label': 'Класс неверен',
        'reject_labels': [(c, '%s — %s' % (c, CLASS_HELP[c])) for c in dv.FIVE_CLASSES],
        'filters': [(c, '%s (%d)' % (c, sum(1 for it in items if it['filt'] == c)))
                    for c in dv.FIVE_CLASSES if any(it['filt'] == c for it in items)],
        'generated': GENERATED,
        'strict_review': {'reviewer': '', 'require_all_votes': False,
                          'require_reject_note': False},
        'extra_css': ('.rv-rend{font-size:1.15em;line-height:1.5}'
                      '.rv-ctx{opacity:.75;font-size:.95em}'),
    }
    config.update(standard_config(
        save_as='RussianTranslation\\review\\%s_decisions.json' % SHEET_ID))

    doc = render_review_sheet(items, config, extras=True)
    doc, chash = stamp(doc)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with io.open(a.out, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(doc)
    lock_path = write_lock(SHEET_ID, chash, [it['id'] for it in items], GENERATED,
                           locks_dir=a.locks_dir, gate='RV-DIVERGENCE',
                           source_html=a.out)
    print('divergence gate sheet: %d items -> %s' % (len(items), a.out))
    print('  %s' % chash)
    print('  lock -> %s' % lock_path)
    print('  class mix in the sheet: %s'
          % dict(collections.Counter(it['filt'] for it in items)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
