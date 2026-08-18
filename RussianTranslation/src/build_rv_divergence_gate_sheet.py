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
from sheet_screening import screening_block  # noqa: E402
from review_binding import stamp, write_lock        # noqa: E402
from review_sheet_standard import standard_config   # noqa: E402
import rv_divergence_type as dv                     # noqa: E402

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
# v5 (H1910): five translators, and the Renou witness band. A NEW id on purpose -- v4 was
# voted against a locked HTML whose content_hash must stay valid, so this must not
# overwrite it.
GENERATED = '2026-07-30'
SHEET_ID = 'rv_divergence_gate_2026-07-30-v5'
EXPLAINED = os.path.join(PWG_RU_DIR, 'h1844', 'rv_divergence_explained.jsonl')
RENOU_WITNESS = os.path.join(PWG_RU_DIR, 'rv_renou_evp_witness.jsonl')
DEFAULT_N = 100
DEFAULT_SEED = 1844

# Chronology is a first-class dimension, not decoration (H1908, MG 29-07-2026:
# "хронология имеет большое значение и должна быть отмечена и использована").
#
# Our four run 1876 -> 1896 -> 1951 -> 1989, and each later translator could read the
# earlier ones: Griffith knew Grassmann and Wilson, Elizarenkova argues explicitly with
# Geldner and Renou. So a divergence between a LATER and an EARLIER rendering is not a
# symmetric disagreement between peers -- the later one is often departing KNOWINGLY, and
# a reviewer judging "who is right" without that ordering is judging blind.
TRANSLATOR_CHRONO = {
    'grassmann_de_1876': (1876, '1876–77', 'Грассман'),
    'griffith_en_1896': (1896, '1896', 'Гриффит'),
    'geldner_de_1951': (1951, '1951–57', 'Гельднер'),
    'elizarenkova_ru_1989': (1989, '1989–99', 'Елизаренкова'),
    'jamison_brereton_en_2014': (2014, '2014', 'Джеймисон–Бреретон'),
}

# Renou belongs in the CHRONOLOGY but not in TRANSLATORS (H1910). EVP is a selective
# commentary, so it is a locus-keyed witness; a `translations` column for it would be
# mostly `absent_from_source` and would corrupt `omitted_by_one`, whose meaning depends on
# absence being meaningful. Kept in a separate map on purpose: anything merged into
# TRANSLATOR_CHRONO becomes pair-eligible via dv.PAIRS, which is exactly what must not
# happen here. He sits between Geldner 1951-57 and Elizarenkova 1989-99, which is why he
# matters -- she argues with him constantly.
WITNESS_CHRONO = {
    'renou_fr_1955': (1955, '1955–69', 'Рену'),
}
CHRONO_ALL = dict(TRANSLATOR_CHRONO, **WITNESS_CHRONO)

# H1908's asymmetry note is RE-DERIVED here, not carried over (H1910). It used to read:
# "our only English witness is Griffith 1896, 118 years older than the current standard,
# because R4 excluded Jamison-Brereton as in-copyright". R4 is lifted and J-B is now a
# full column, so that sentence is simply false. What survives the change is the opposite,
# and sharper: Griffith is no longer "the English column" but the VICTORIAN English one,
# and a Griffith↔J-B divergence is a 118-year gap between two English renderings.
EN_TRANSLATORS = ('griffith_en_1896', 'jamison_brereton_en_2014')

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


def _chronology(a, b):
    """Deterministic chronology band: who came first, the gap, and what that implies.

    Computed from the years, never asked of a model -- publication dates are facts.
    """
    ya, la, na = TRANSLATOR_CHRONO[a]
    yb, lb, nb = TRANSLATOR_CHRONO[b]
    (ey, el, en), (ly, ll, ln) = ((ya, la, na), (yb, lb, nb)) if ya < yb else \
                                 ((yb, lb, nb), (ya, la, na))
    gap = ly - ey
    parts = ['<b>Хронология:</b> %s %s → %s %s (позже на %d лет).'
             % (esc(en), esc(el), esc(ln), esc(ll), gap)]
    parts.append('%s мог знать перевод %s — расхождение здесь скорее '
                 '<i>сознательный отход</i>, чем независимое чтение.'
                 % (esc(ln), esc(en)))
    if a in EN_TRANSLATORS and b in EN_TRANSLATORS:
        parts.append('<b>Оба свидетеля здесь английские</b>, и между ними 118 лет: '
                     'Гриффит 1896 — викторианский, Джеймисон–Бреретон 2014 — '
                     'современный научный стандарт. Расхождение здесь — это не разница '
                     'языков, а разница прочтений внутри одного языка.')
    elif 'griffith_en_1896' in (a, b):
        parts.append('<b>Гриффит 1896 — это <i>викторианский</i> английский столбец</b>, '
                     'а не «английский» как таковой: с 2014 года в слое есть и '
                     'Джеймисон–Бреретон. Английская сторона этого расхождения — '
                     'старая, и её стоит сверить с Дж.–Б. в блоке ниже.')
    return '<div class="rv-chrono">%s</div>' % ' '.join(parts)


def _renou_band(witness):
    """The Renou witness band: what Elizarenkova was arguing with at this locus.

    Renou is not a rendering to judge, so he never appears as a votable panel. But an
    Elizarenkova↔Geldner divergence at a locus where she quotes Renou is very likely her
    following Renou AGAINST Geldner, and a reviewer should see that in one glance rather
    than reconstruct it.
    """
    if not witness:
        return ''
    year, label, name = WITNESS_CHRONO['renou_fr_1955']
    bits = ['<b>Свидетель Рену (EVP %s):</b> Елизаренкова ссылается на него в этом '
            'месте %d раз.' % (esc(label), witness['mention_count'])]
    for q in witness.get('quotes_fr') or []:
        bits.append('<span class="rv-renou-q">«%s»</span>' % esc(q))
    if not witness.get('quotes_fr'):
        bits.append('<span class="muted">Прямой французской цитаты здесь нет — только '
                    'упоминание.</span>')
    return '<div class="rv-renou">%s</div>' % ' '.join(bits)


def _question(cls, ex, a, b, witness=None):
    """The card's ask. v1 printed only the class name and made the reviewer hunt for
    the difference; this states WHAT the difference is, in Russian, above the fold."""
    why = (ex.get('why_ru') or '').strip()
    parts = [_chronology(a, b)]
    band = _renou_band(witness)
    if band:
        parts.append(band)
    parts.append('Модель присвоила класс <b>%s</b> — <i>%s</i>.'
                 % (esc(cls), esc(CLASS_HELP.get(cls, ''))))
    if why:
        parts.append('<div class="rv-why"><b>В чём разница:</b> %s</div>' % esc(why))
    else:
        parts.append('<div class="rv-why rv-nowhy"><b>Модель не объяснила разницу</b> — '
                     'это само по себе повод для Reject или Defer.</div>')
    if ex.get('asymmetry_note'):
        parts.append('<div class="rv-asym"><b>⚠ Асимметрия переводов:</b> %s</div>'
                     % esc(ex['asymmetry_note']))
    parts.append('<span class="muted">Подсвеченное ниже — то место, из-за которого '
                 'присвоен класс. Approve = класс верен · Reject = неверен, '
                 '<b>выберите правильный класс</b> · Defer = по двум переводам не '
                 'решить.</span>')
    return '<br>'.join(parts)


def load_explanations(path=EXPLAINED):
    """'<loc>|<a>|<b>' -> {span_a, span_b, why_ru, asymmetry_note, *_verbatim}."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                out['%s|%s' % (r['location'], r['pair'])] = r
    return out


def highlight(text, span, verbatim):
    """Escape the rendering, then wrap the FIRST occurrence of `span` in a mark.

    Escaping happens before matching so the mark tags are the only markup in the
    output. A non-verbatim span (the model paraphrased instead of copying) is never
    force-fitted -- the caller quotes it separately instead.
    """
    safe = esc(text or '')
    if not span or not verbatim:
        return safe.replace('\n', '<br>'), False
    needle = esc(span)
    idx = safe.find(needle)
    if idx < 0:
        return safe.replace('\n', '<br>'), False
    marked = (safe[:idx] + '<mark class="rv-hit">' + needle + '</mark>'
              + safe[idx + len(needle):])
    return marked.replace('\n', '<br>'), True


def load_renou_witness(path=RENOU_WITNESS):
    """location -> witness record. Absent file is not an error: the witness is an
    enrichment, and a sheet built without it must still be a valid sheet."""
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                out[r['location']] = r
    return out


def build_items(picked, stanzas, explained, witnesses=None):
    witnesses = witnesses or {}
    items = []
    for location, pair_key, entry in picked:
        a, b = pair_key.split('|')
        stanza = stanzas[location]
        ex = explained.get('%s|%s' % (location, pair_key)) or {}
        spans = {a: (ex.get('span_a'), ex.get('span_a_verbatim', False)),
                 b: (ex.get('span_b'), ex.get('span_b_verbatim', False))}
        panels = []
        for key in sorted((a, b), key=lambda k: TRANSLATOR_CHRONO[k][0]):
            t = stanza['translations'][key]
            span, verbatim = spans[key]
            body, marked = highlight(t['text'], span, verbatim)
            note = ''
            if span and not marked:
                note = ('<div class="rv-quote">Модель указала на: «%s» '
                        '(не удалось подсветить дословно)</div>' % esc(span))
            elif not span:
                note = '<div class="rv-quote">Здесь выделять нечего.</div>'
            panels.append((dv.TRANSLATOR_LABEL[key],
                           '<div class="rv-rend">%s</div>%s' % (body, note)))
        other = [k for k in dv.TRANSLATORS if k not in (a, b)]
        ctx = []
        for key in other:
            t = stanza['translations'][key]
            if t['status'] == 'present':
                ctx.append('<b>%s:</b> %s' % (esc(dv.TRANSLATOR_LABEL[key]),
                                              esc(t['text'] or '').replace('\n', ' / ')))
        if ctx:
            # Count it rather than hardcoding "два": with J-B the layer has five
            # translators, so a pair leaves three others, not two (H1910).
            panels.append(('Остальные переводы — %d (для контекста, не голосуются)'
                           % len(ctx),
                           '<div class="rv-ctx">%s</div>' % '<br><br>'.join(ctx)))
        witness = witnesses.get(location)
        badges = [entry['class'], 'маṇḍала %d' % stanza['mandala']]
        if witness:
            badges.append('Рену' + (' ⟨цитата⟩' if witness.get('has_quote') else ''))
        items.append({
            'id': '%s|%s' % (location, pair_key),
            'filt': entry['class'],
            'title': 'RV %s — %s ↔ %s' % (location, a.split('_')[0], b.split('_')[0]),
            'badges': badges,
            'question': _question(entry['class'], ex, a, b, witness),
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
    explained = load_explanations()
    if not explained:
        sys.exit('no %s — run `python src/rv_divergence_explain.py run --ids …` first. '
                 'A sheet without spans and explanations is the v1 defect (H1906).'
                 % EXPLAINED)
    missing = [p for p in picked if '%s|%s' % (p[0], p[1]) not in explained]
    if missing:
        print('WARN: %d of %d items have no explanation and will render bare'
              % (len(missing), len(picked)))
    witnesses = load_renou_witness()
    print('Renou witness loci loaded: %d' % len(witnesses))
    hits = sum(1 for p in picked if p[0] in witnesses)
    print('  of the %d sampled items, %d sit at a locus Elizarenkova cites Renou at'
          % (len(picked), hits))
    items = build_items(picked, stanzas, explained, witnesses)

    dist = collections.Counter(r[2]['class'] for r in rows)
    total = sum(dist.values())
    # cards where the model named a place but could not point at it verbatim, so the
    # card quotes instead of highlighting -- stated in the subtitle rather than hidden
    n_unmarked = 0
    for loc, pair_key, _ in picked:
        ex = explained.get('%s|%s' % (loc, pair_key)) or {}
        if ((ex.get('span_a') and not ex.get('span_a_verbatim'))
                or (ex.get('span_b') and not ex.get('span_b_verbatim'))):
            n_unmarked += 1
    config = {
        'sheet_id': SHEET_ID,
        'title': 'RV · типология расхождений — калибровочный гейт (H1844, шаг 8)',
        'subtitle': (
            '%d пар (строфа × пара переводчиков), по 25 на класс. Гейт открывает '
            'полный прогон при согласии ≥ 80 %% (R15). Методика — внизу страницы.'
            % len(items)),
        'footer': (
            'Approve = класс модели верен · Reject = неверен (<b>обязательно выберите '
            'класс</b>, который должен быть) · Defer = не решается по двум переводам.'
            '<div class="rv-method">'
            '<h3>Методика</h3>'
            '<b>Читать целиком четыре перевода не нужно.</b> На каждой карточке жёлтым '
            'подсвечено то самое место, из-за которого присвоен класс, а над переводами '
            'сказано по-русски, в чём именно разница. Подсветка дословная: там, где модель '
            'не смогла указать место в тексте буквально, карточка честно пишет об этом '
            'вместо подсветки — <b>%d карточек из %d</b>.<br><br>'
            '<b>Хронология.</b> Переводы идут Грассман 1876–77 → Гриффит 1896 → '
            'Гельднер 1951–57 → Елизаренкова 1989–99 → Джеймисон–Бреретон 2014, и каждый '
            'более поздний мог читать более ранних. Поэтому расхождение позднего с ранним — '
            'чаще <i>сознательный отход</i>, чем независимое чтение; на карточке пара '
            'показана в хронологическом порядке. Английских свидетелей теперь два, и между '
            'ними 118 лет: Гриффит 1896 — это <i>викторианский</i> английский, а не '
            '«английский» вообще; современный научный стандарт — Джеймисон–Бреретон 2014.'
            '<br><br>'
            '<b>Рену.</b> Рену (EVP 1955–69) стоит в хронологии между Гельднером и '
            'Елизаренковой, но он <i>не</i> шестой столбец: EVP — выборочный комментарий, '
            'а не полный перевод, и столбец для него был бы почти сплошь '
            '<code>absent_from_source</code>. Поэтому он показан отдельной полосой-'
            'свидетелем там, где Елизаренкова на него ссылается — расхождение '
            'Елизаренкова↔Гельднер в таком месте, скорее всего, значит, что она идёт за '
            'Рену против Гельднера.<br><br>'
            '<b>Выборка</b> стратифицирована по классу, а не равномерна: в пилоте классы '
            'распределены как %s, и равномерная выборка ушла бы почти целиком на '
            'подтверждение одного класса.<br><br>'
            'Экспорт валидируется против review/locks/%s.lock.json перед применением.'
            '</div>'
            % (n_unmarked, len(items),
               ', '.join('%s %.0f%%' % (c, 100.0 * dist[c] / total)
                         for c in dv.FIVE_CLASSES if dist[c]),
               SHEET_ID)),
        'approve_label': 'Класс верен',
        'reject_label': 'Класс неверен',
        'reject_labels': [(c, '%s — %s' % (c, CLASS_HELP[c])) for c in dv.FIVE_CLASSES],
        'filters': [(c, '%s (%d)' % (c, sum(1 for it in items if it['filt'] == c)))
                    for c in dv.FIVE_CLASSES if any(it['filt'] == c for it in items)],
        'generated': GENERATED,
        'strict_review': {'reviewer': '', 'require_all_votes': False,
                          'require_reject_note': False},
        'extra_css': (
            # Every block below sets BOTH background and color. v3 set only the
            # background and inherited the theme foreground, which rendered white
            # text on the yellow highlight and pale text on the pale-blue panel.
            '.rv-rend{font-size:1.2em;line-height:1.6}'
            '.rv-ctx{opacity:.75;font-size:.95em}'
            'mark.rv-hit{background:#ffd54a;color:#1a1a1a;padding:.06em .2em;'
            'border-radius:.2em;box-shadow:0 0 0 1px #c79100 inset;font-weight:700}'
            '.rv-why{margin:.5em 0;padding:.55em .75em;background:#e8f1fb;'
            'color:#12243a;border-left:4px solid #2f6fb0;border-radius:.2em;'
            'font-size:1.05em}'
            '.rv-why b{color:#0d1b2c}'
            '.rv-nowhy{background:#fdecea;color:#5c1a15;border-left-color:#c0392b}'
            '.rv-asym{margin:.4em 0;padding:.5em .75em;background:#fff6df;'
            'color:#4a3608;border-left:4px solid #c79100;border-radius:.2em}'
            '.rv-asym b{color:#3a2a05}'
            '.rv-chrono{margin:.4em 0;padding:.5em .75em;background:#f0ecf9;'
            'color:#2b2140;border-left:4px solid #6a4fa3;border-radius:.2em;'
            'font-size:.97em}'
            '.rv-chrono b{color:#1e1730}'
            '.rv-quote{margin-top:.35em;font-size:.93em;color:#444;font-style:italic}'
            '.rv-method{margin-top:2.5em;padding:1em 1.2em;background:#f6f6f8;'
            'color:#222;border-top:2px solid #bbb;border-radius:.2em;font-size:.95em}'
            '.rv-method h3{margin:0 0 .5em;font-size:1.05em;color:#111}'),
    }
    config.update(standard_config(
        save_as='RussianTranslation\\review\\%s_decisions.json' % SHEET_ID))

    doc = render_review_sheet(items, config, extras=True,
                                   screening=screening_block(
                                       deterministic=0, lookup=0, agent=0,
                                      human=len(items),
                                      evidence_path="RussianTranslation/pwg_ru/SCREENING_H1650.md",
                                       rules=[]))
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
