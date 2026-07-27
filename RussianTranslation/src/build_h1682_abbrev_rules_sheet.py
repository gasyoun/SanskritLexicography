#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""build_h1682_abbrev_rules_sheet.py — H1682: the rule-level replacement for
`review/h1303_abbrev_sheet.html` (sheet_id `h1303_abbrev`, 273 cards, unvoted).

H1664 (VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11) ruled h1303_abbrev
HYBRID: "a ~6-rule policy asked 273 times... collapse to rule cards +
ambiguous residue". h1303_abbrev is UNVOTED, so supersession by remake is
legal (batch1v2 precedent, H1655) -- this generator does not touch any
fenced file, does not re-rule the underlying policy, and reclassifies no
token: every token's bucket/cls/proposed-ru/note is read verbatim from
build_h1303_abbrev_sheet.py's O overlay via h1682_abbrev_collapse.py, only
RE-GROUPED into human-facing cards:

  * 12 RULE cards, one per O's own `# --- ...` section header (the original
    curator's own semantic grouping, 21-07-2026) -- each with a cited
    precedent and its bulk token/RU membership; approving a rule ratifies
    the RU mapping for every bulk token in that section at once.
  * N individually-flagged RESIDUE cards -- tokens whose O entry carries no
    fixed `ru` or a collision/caution/OCR/context-dependent note (see
    h1682_abbrev_collapse._AMBIG_RE) -- same one-token-per-card format as
    the old sheet, so nothing genuinely ambiguous gets silently bulk-approved.
  * 3 ls-border cards + 1 meta card, carried over verbatim from
    build_h1303_abbrev_sheet.py (unchanged decisions, unchanged wording).

Usage (from RussianTranslation/):
    python src/build_h1682_abbrev_rules_sheet.py
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import h1682_abbrev_collapse as coll                              # noqa: E402
import review_binding                                             # noqa: E402
from csl_pyutil.review_sheet import render_review_sheet, esc, mark_cyrillic  # noqa: E402

GENERATED = '2026-07-26'
SHEET_ID = 'h1682_abbrev_rules'


def _slug(label):
    return 'rule:' + ''.join(c if c.isalnum() else '-' for c in label).strip('-').lower()[:40]


def rule_card(label, bulk_toks, residue_toks, citation, by_token):
    n_bulk = len(bulk_toks)
    total_freq = sum(by_token[t]['freq'] for t in bulk_toks)
    if bulk_toks:
        members = ' · '.join(
            '%s→%s' % (esc(t), esc(by_token[t]['ru_proposed'] or by_token[t]['ru_map_current'] or t))
            for t in sorted(bulk_toks, key=lambda t: -by_token[t]['freq']))
        q = mark_cyrillic(
            '<b>Раздел:</b> %s&nbsp;&mdash;&nbsp;<b>%d</b> токенов, %d вхождений в store.<br>'
            '<b>Принять</b> = утвердить RU-соответствие для всех %d токенов раздела разом (состав ниже). '
            '<b>Отклонить</b> = вернуть раздел к статус-кво (латиница/оригинал + тултип, без перевода). '
            '<b>Отложить</b> = обсудить.'
            % (esc(label), n_bulk, total_freq, n_bulk))
        panels = [('состав раздела (token → RU)', '<pre>%s</pre>' % members),
                  ('прецедент', '<pre>%s</pre>' % esc(citation))]
    else:
        q = mark_cyrillic(
            '<b>Раздел:</b> %s&nbsp;&mdash;&nbsp;механизм, без фиксированного RU на уровне токена.<br>'
            '<b>Принять</b> = утвердить сам render-time механизм (перевод по значению атрибута '
            '<code>n=</code> в момент рендера, не по токену). Все %d токенов этого раздела не имеют '
            'фиксированного соответствия и вынесены как отдельные карточки ниже '
            '(секция «неоднозначные»). <b>Отклонить</b> = обсудить другой механизм. <b>Отложить</b> = обсудить.'
            % (esc(label), len(residue_toks)))
        panels = [('состав раздела (без фикс. RU → см. карточки ниже)',
                   '<pre>%s</pre>' % ' · '.join(esc(t) for t in sorted(residue_toks))),
                  ('прецедент', '<pre>%s</pre>' % esc(citation))]
    if residue_toks and bulk_toks:
        panels.append(('вынесено как неоднозначные (см. ниже)',
                        '<pre>%s</pre>' % ' · '.join(esc(t) for t in sorted(residue_toks))))
    return {'id': _slug(label), 'filt': 'rule', 'title': label,
            'badges': ['%d×' % n_bulk if bulk_toks else 'механизм',
                       '%d неоднозн.' % len(residue_toks) if residue_toks else 'без остатка'],
            'question': q, 'panels': panels,
            'note_placeholder': 'своя формулировка / комментарий'}


def residue_card(tok, row):
    exp = ' — '.join(x for x in (row['de'], row['en']) if x) or 'нет в pwgab'
    cur = ('уже в RU_MAP: «%s»' % row['ru_map_current']) if row['ru_map_current'] else 'сейчас: латиница/оригинал + тултип'
    prop = row['ru_proposed'] if row['ru_proposed'] else '(без фиксированного соответствия — см. примечание)'
    q = ('<b>%s</b>&nbsp;→&nbsp;' % esc(tok)
         + mark_cyrillic('<b>%s</b>' % esc(prop))
         + '&nbsp;&nbsp;<span class="muted">(раздел: %s)</span>' % esc(row['section']))
    panels = [('данные', '<pre>расшифровка: %s\nчастота в store: %d\n%s</pre>'
               % (esc(exp), row['freq'], esc(cur)))]
    if row['note']:
        panels.append(('примечание (почему это неоднозначно)', '<pre>%s</pre>' % esc(row['note'])))
    return {'id': 'ab:%s' % tok, 'filt': 'ambig', 'title': tok,
            'badges': ['%d×' % row['freq'], row['cls']],
            'question': q, 'panels': panels,
            'note_placeholder': 'своя формулировка / комментарий'}


# ls-border + meta cards carried over VERBATIM from build_h1303_abbrev_sheet.py
# (same decisions, same wording -- this pass only re-groups <ab> tokens).
_LS_BORDER = [
    ('ed. Bomb.', '221', 'Bombay edition', 'Бомбейская ред.',
     'зафиксировано MG 19-07-2026 (N4); ls-территория, применение с H1307'),
    ('Verz. d. Oxf. H.', 'в ls-ссылках', 'Verzeichniss der Oxforder Handschriften (Aufrecht 1864)',
     'Кат. оксф. рукоп.', 'N9: не оставлять по-немецки; ls-территория'),
    ('Spr. / Spr. (II)', 'десятки', 'Indische Sprüche (Böhtlingk)',
     'оставить сиглой + тултип «Индийские изречения»', 'заглавие источника, как ṚV.; ls-территория'),
]


def ls_cards():
    items = []
    for sig, freqs, exp, prop, note in _LS_BORDER:
        items.append({'id': 'ls:%s' % sig, 'filt': 'ls',
                      'title': sig,
                      'badges': [freqs, 'ls-сигла'],
                      'question': '<b>%s</b>&nbsp;→&nbsp;%s' % (esc(sig), mark_cyrillic('<b>%s</b>' % esc(prop))),
                      'panels': [('данные', '<pre>расшифровка: %s</pre>' % esc(exp)),
                                 ('примечание', '<pre>%s</pre>' % esc(note))],
                      'note_placeholder': 'своя формулировка / комментарий'})
    return items


def meta_card():
    return {'id': 'meta:architecture', 'filt': 'meta',
            'title': 'МЕТА: где применяется утвержденный список?',
            'badges': ['архитектура'],
            'question': mark_cyrillic(
                '<b>Принять</b> = применять только на этапе рендеринга (архитектура 10-07-2026: '
                'store хранит исходные теги, переводит генератор сайта — покрывает все будущие корни). '
                '<b>Отклонить</b> = список должен также переписать сам store (отдельный шаг с '
                'translation_memory/промоушен-механикой). <b>Отложить</b> = обсудить.'),
            'panels': [('контекст', '<pre>ABBREVIATIONS_RU.md § "Architecture decision: fix at RENDER TIME"\n'
                        'Решение 10-07 остается в силе, пока эта карточка не проголосована иначе. '
                        'Перенесено из h1303_abbrev без изменений (H1682).</pre>')],
            'note_placeholder': 'комментарий'}


def build():
    r = coll.classify()
    items = []
    for label in r['order']:
        sec = r['sections'][label]
        items.append(rule_card(label, sec['bulk'], sec['residue'], r['citation'][label], r['by_token']))
    n_rule_cards = len(items)

    residue_toks = [t for label in r['order'] for t in r['sections'][label]['residue']]
    for tok in residue_toks:
        items.append(residue_card(tok, r['by_token'][tok]))
    n_residue_cards = len(residue_toks)

    items.extend(ls_cards())
    items.append(meta_card())

    n_bulk = sum(1 for row in r['by_token'].values() if not row['residue'])
    config = {
        'sheet_id': SHEET_ID,
        'title': 'H1682 — сокращения pwg_ru: ратификация правил (rule-collapse)',
        'subtitle': ('Замена 273-карточного h1303_abbrev (H1664, §11: "a ~6-rule policy asked 273 times"). '
                     '%d ab-токенов сгруппированы в %d карточек-правил (состав виден в панели «состав раздела»), '
                     'плюс %d индивидуально неоднозначных + 3 ls-пограничные + 1 мета = %d карточек всего '
                     '(было 273). Принять правило = утвердить RU для всех его bulk-токенов разом; '
                     'неоднозначные токены голосуются по одному, как раньше. Эмиттер: csl-pyutil 0.4.0.'
                     % (n_bulk, n_rule_cards, n_residue_cards,
                        n_rule_cards + n_residue_cards + len(_LS_BORDER) + 1)),
        'footer': ('Экспорт сохранить как pwg_ru/eval/h1682_abbrev_rules.decisions.json — применение '
                   'обновит RU_MAP/pwg_ab_ru.py разом по правилу и/или точечно по неоднозначным токенам.'),
        'approve_label': 'принять RU', 'reject_label': 'оставить как есть',
        'filters': [('rule', 'правила'), ('ambig', 'неоднозначные'), ('ls', 'ls-сиглы'), ('meta', 'мета')],
        'generated': GENERATED,
        'show_ids': True,
        'save_as': 'pwg_ru/eval/h1682_abbrev_rules.decisions.json',
        'note_min_height_px': 56,
    }
    html_doc = render_review_sheet(items, config)

    out = os.path.join(RT, 'review', 'h1682_abbrev_rules_sheet.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    stamped, chash = review_binding.stamp(html_doc)
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(stamped)
    lock_path = review_binding.lock_from_html(out, gate=None)

    print('H1682 rules sheet: %d cards (%d rule + %d ambiguous + %d ls-border + 1 meta) -> %s'
          % (len(items), n_rule_cards, n_residue_cards, len(_LS_BORDER), out))
    print('  %s' % chash)
    print('  lock -> %s' % lock_path)
    return out


if __name__ == '__main__':
    build()
