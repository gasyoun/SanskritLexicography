#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""build_h1682_abbrev_rules_sheet.py — H1682 rule-collapse sheet + H2047 content v3.

H1664 ruled h1303_abbrev HYBRID; H1682 collapsed 273 cards → rule + residue.
H2047 (MG 31-07-2026) remakes the *content* of that sheet so it is honestly votable:

  * expansion + frequency (not bare token→ru)
  * case-folded Latin grammar families (act./Act. under one row)
  * cases stay Latin (locked) — no Acc.→акк. bulk
  * up to 5 clickable KWIC examples per family / residue token
  * emitter hygiene: note_min_height_px=88, show_ids, save_as; mark_cyrillic
    only on strings under judgment

Usage (from RussianTranslation/):
    python src/build_h1682_abbrev_rules_sheet.py
"""
import collections
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import h1682_abbrev_collapse as coll                              # noqa: E402
import review_binding                                             # noqa: E402
import store_path                                                 # noqa: E402
from review_sheet_standard import (                               # noqa: E402
    NOTE_MIN_HEIGHT_PX, pwg_entry_href, slp1_iast, standard_config,
)
from csl_pyutil.review_sheet import render_review_sheet, esc, mark_cyrillic  # noqa: E402
from sheet_screening import screening_block  # noqa: E402

GENERATED = '2026-07-31'
SHEET_ID = 'h1682_abbrev_rules'
MAX_EXAMPLES = 5
_AB = re.compile(r'<ab\b[^>]*>(.*?)</ab>', re.S)
_TAG = re.compile(r'<[^>]+>')
_BRACE = re.compile(r'\{%([^%]*)%\}')
_HASH = re.compile(r'\{#([^#]*)#\}')

# Section labels whose bulk display uses case-fold families + stay-Latin framing
_CASE_SECTION = 'grammatical: cases (uniform internationalism: 8 cases vs 6 русских)'
_LATIN_GRAM_SECTIONS = frozenset({
    _CASE_SECTION,
    'grammatical: number / gender / person',
    'grammatical: voice / secondary stems',
    'grammatical: tense / mood',
    'grammatical: non-finite / POS / syntax',
    'grammatical: valency / diathesis-adjacent',
    'grammatical: word formation / morphology / degree',
})


def _slug(label):
    return 'rule:' + ''.join(c if c.isalnum() else '-' for c in label).strip('-').lower()[:40]


def _family_key(tok):
    """Case-fold Latin grammatical families (act./Act. → one decision family)."""
    return (tok or '').casefold()


def _snip(text, width=120):
    t = _TAG.sub('', text or '')
    t = _BRACE.sub(r'\1', t)
    t = _HASH.sub(r'\1', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > width:
        t = t[: width - 1] + '…'
    return t


def _format_surface(tok, row):
    """Required display: surface (expansion) · proposal · (n=freq)."""
    de = row.get('de') or ''
    en = row.get('en') or ''
    exp = de or en or 'нет в pwgab'
    if de and en and en.casefold() != de.casefold():
        exp = '%s / %s' % (de, en)
    prop = row.get('ru_proposed')
    if prop is None:
        prop_s = 'без фикс. RU (оставить + тултип)'
    elif prop == tok or (prop and prop.casefold() == tok.casefold()):
        prop_s = 'оставить латиницей (stay Latin)'
    else:
        prop_s = prop
    return '%s (%s)  · %s · (n=%d)' % (tok, exp, prop_s, row.get('freq') or 0)


def _group_families(toks, by_token):
    """Group tokens by case-fold family; keep surfaces with separate freqs."""
    fam = collections.OrderedDict()
    for t in sorted(toks, key=lambda x: (-by_token[x]['freq'], x)):
        k = _family_key(t)
        fam.setdefault(k, []).append(t)
    return fam


def collect_kwic(tokens, limit=MAX_EXAMPLES):
    """One store pass: up to `limit` real contexts per token (headword + snippets + href)."""
    wanted = set(tokens)
    hits = {t: [] for t in wanted}
    if not wanted:
        return hits
    store = store_path.canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    if not os.path.exists(store):
        print('KWIC: store missing at %s' % store, file=sys.stderr)
        return hits
    need = set(wanted)
    with io.open(store, encoding='utf-8') as f:
        for line in f:
            if not need:
                break
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            ru = r.get('ru') or ''
            if '<ab' not in ru:
                continue
            found = set(x.strip() for x in _AB.findall(ru))
            overlap = found & need
            if not overlap:
                continue
            key1 = r.get('key1') or ''
            href = pwg_entry_href(key1) if key1 else None
            iast = r.get('iast') or (slp1_iast(key1) if key1 else key1)
            de_s = _snip(r.get('de') or '', 100)
            ru_s = _snip(ru, 100)
            for tok in overlap:
                bucket = hits[tok]
                if len(bucket) >= limit:
                    continue
                sig = (key1, tok)
                if any(x.get('_sig') == sig for x in bucket):
                    continue
                bucket.append({
                    '_sig': sig,
                    'key1': key1,
                    'iast': iast,
                    'de': de_s,
                    'ru': ru_s,
                    'href': href,
                })
                if len(bucket) >= limit:
                    need.discard(tok)
    for t in hits:
        for ex in hits[t]:
            ex.pop('_sig', None)
    filled = sum(1 for t, v in hits.items() if v)
    print('KWIC: %d/%d tokens with ≥1 example (cap %d)' % (filled, len(wanted), limit),
          file=sys.stderr)
    return hits


def _examples_html(examples):
    if not examples:
        return '<pre class="muted">примеры не найдены в store (проверьте canonical store)</pre>'
    lines = []
    for i, ex in enumerate(examples, 1):
        hw = esc(ex.get('iast') or ex.get('key1') or '?')
        href = ex.get('href')
        if href:
            head = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(href), hw)
        else:
            head = hw
        lines.append(
            '%d. <b>%s</b> <code>%s</code><br>'
            '&nbsp;&nbsp;DE: %s<br>'
            '&nbsp;&nbsp;RU: %s'
            % (i, head, esc(ex.get('key1') or ''), esc(ex.get('de') or ''), esc(ex.get('ru') or ''))
        )
    return '<div class="kwic">%s</div>' % '<br>'.join(lines)


def _family_examples(surfaces, kwic):
    """Merge up to MAX_EXAMPLES across surfaces of one family (prefer high-freq order)."""
    seen = set()
    out = []
    for t in surfaces:
        for ex in kwic.get(t) or []:
            sig = (ex.get('key1'), t)
            if sig in seen:
                continue
            seen.add(sig)
            out.append(ex)
            if len(out) >= MAX_EXAMPLES:
                return out
    return out


def rule_card(label, bulk_toks, residue_toks, citation, by_token, kwic):
    n_bulk = len(bulk_toks)
    total_freq = sum(by_token[t]['freq'] for t in bulk_toks)
    is_case = label == _CASE_SECTION
    is_latin_gram = label in _LATIN_GRAM_SECTIONS

    if bulk_toks:
        fam = _group_families(bulk_toks, by_token)
        member_lines = []
        for _k, surfaces in fam.items():
            if len(surfaces) == 1:
                member_lines.append(_format_surface(surfaces[0], by_token[surfaces[0]]))
            else:
                # family header: surfaces with separate freqs, shared proposal
                parts = []
                for t in surfaces:
                    de = by_token[t].get('de') or by_token[t].get('en') or ''
                    parts.append('%s (%s, n=%d)' % (t, de or '—', by_token[t]['freq']))
                prop = by_token[surfaces[0]].get('ru_proposed')
                if is_case or (prop and prop.casefold() == surfaces[0].casefold()):
                    prop_s = 'оставить латиницей (stay Latin)'
                elif prop is None:
                    prop_s = 'без фикс. RU'
                else:
                    prop_s = 'предложение: %s (см. H2048 / N8 notes)' % prop
                member_lines.append(' · '.join(parts) + '  →  %s' % prop_s)
        members = '\n'.join(member_lines)

        # examples: first family by total freq
        top_fam = max(fam.values(), key=lambda ss: sum(by_token[t]['freq'] for t in ss))
        ex_html = _examples_html(_family_examples(top_fam, kwic))

        if is_case:
            q = (
                '<b>Раздел:</b> %s&nbsp;&mdash;&nbsp;<b>%d</b> токенов, %d вхождений.<br>'
                '<b>Политика MG 31-07 (LOCKED):</b> падежи остаются <b>латиницей</b> '
                '(Acc., Loc., Instr., …) в видимой колонке; полные Latin + русские названия '
                'падежей — только в тултипе/легенде (модель Kochergina). '
                'N5 <em>не</em> означает «перевести Acc.». LES-формы (акк., вин. п.) — '
                'только метаязык, не замена токена.<br>'
                '<b>Принять</b> = ратифицировать stay-Latin + легенду тултипов для всех '
                'case-fold семей раздела. <b>Отклонить</b> = оспорить lock (нужно новое '
                'решение MG). <b>Отложить</b> = обсудить.'
                % (esc(label), n_bulk, total_freq)
            )
            # no mark_cyrillic on whole chrome — only the judgment strings
            q = q  # Latin policy: judgment is policy text, not a RU mapping
            approve_hint = 'принять stay-Latin'
        else:
            interim = ''
            if is_latin_gram:
                interim = (
                    ' Для voice/tense/прочей грамматики: interim-рекомендация — '
                    '<b>оставить латиницу + русское полное имя в тултипе</b>, пока H2048 '
                    'не даст crosswalk; не изобретать calques (фут., прекат.) без источника. '
                    'N8 (Caus.→кауз.) — <em>одна</em> prior-vote note, не blank cheque.'
                )
            q = (
                '<b>Раздел:</b> %s&nbsp;&mdash;&nbsp;<b>%d</b> токенов, %d вхождений в store.<br>'
                '<b>Принять</b> = утвердить отображаемые соответствия (ниже: expansion + n=) '
                'для всех bulk-семей раздела разом. '
                '<b>Отклонить</b> = вернуть раздел к статус-кво (латиница/оригинал + тултип). '
                '<b>Отложить</b> = обсудить.%s'
                % (esc(label), n_bulk, total_freq, interim)
            )
            approve_hint = 'принять RU / stay-Latin'

        panels = [
            ('состав (surface · expansion · proposal · n=; case-fold семьи вместе)',
             '<pre>%s</pre>' % esc(members)),
            ('примеры (до %d, семья с max freq: %s)' % (MAX_EXAMPLES, esc(' / '.join(top_fam))),
             ex_html),
            ('прецедент', '<pre>%s</pre>' % esc(citation)),
        ]
    else:
        q = (
            '<b>Раздел:</b> %s&nbsp;&mdash;&nbsp;механизм, без фиксированного RU на уровне токена.<br>'
            '<b>Принять</b> = утвердить render-time механизм (перевод по значению атрибута '
            '<code>n=</code> в момент рендера, не по токену). Все %d токенов вынесены как '
            'отдельные карточки ниже. <b>Отклонить</b> = обсудить другой механизм. '
            '<b>Отложить</b> = обсудить.'
            % (esc(label), len(residue_toks))
        )
        panels = [
            ('состав раздела (без фикс. RU → см. карточки ниже)',
             '<pre>%s</pre>' % ' · '.join(esc(t) for t in sorted(residue_toks))),
            ('прецедент', '<pre>%s</pre>' % esc(citation)),
        ]
        approve_hint = 'принять механизм'

    if residue_toks and bulk_toks:
        panels.append((
            'вынесено как неоднозначные (см. ниже)',
            '<pre>%s</pre>' % ' · '.join(esc(t) for t in sorted(residue_toks)),
        ))

    return {
        'id': _slug(label),
        'filt': 'rule',
        'title': label,
        'badges': [
            '%d×' % n_bulk if bulk_toks else 'механизм',
            '%d неоднозн.' % len(residue_toks) if residue_toks else 'без остатка',
            'stay-Latin' if is_case else 'gram' if is_latin_gram else 'rule',
        ],
        'question': q,
        'panels': panels,
        'note_placeholder': 'своя формулировка / комментарий (%s)' % approve_hint,
    }


def residue_card(tok, row, kwic):
    exp = ' — '.join(x for x in (row['de'], row['en']) if x) or 'нет в pwgab'
    cur = ('уже в RU_MAP: «%s»' % row['ru_map_current']) if row['ru_map_current'] else (
        'сейчас: латиница/оригинал + тултип')
    prop = row['ru_proposed']
    # Residue: OCR / German articles — usually no RU translation
    if prop is None:
        prop_display = 'оставить оригинал + тултип (не изобретать RU)'
        q = (
            '<b>%s</b>&nbsp;→&nbsp;<b>%s</b>'
            '&nbsp;&nbsp;<span class="muted">(раздел: %s)</span>'
            % (esc(tok), esc(prop_display), esc(row['section']))
        )
    else:
        prop_display = prop
        q = (
            '<b>%s</b>&nbsp;→&nbsp;%s'
            '&nbsp;&nbsp;<span class="muted">(раздел: %s)</span>'
            % (esc(tok), mark_cyrillic('<b>%s</b>' % esc(prop_display)), esc(row['section']))
        )
    panels = [
        ('данные',
         '<pre>%s\nчастота в store: %d\n%s</pre>'
         % (esc(_format_surface(tok, row)), row['freq'], esc(cur))),
        ('примеры (до %d, кликабельные)' % MAX_EXAMPLES,
         _examples_html(kwic.get(tok) or [])),
    ]
    if row['note']:
        panels.append(('примечание (почему это неоднозначно)',
                       '<pre>%s</pre>' % esc(row['note'])))
    return {
        'id': 'ab:%s' % tok,
        'filt': 'ambig',
        'title': tok,
        'badges': ['%d×' % row['freq'], row['cls']],
        'question': q,
        'panels': panels,
        'note_placeholder': 'своя формулировка / комментарий',
    }


# ls-border + meta cards carried over VERBATIM from build_h1303_abbrev_sheet.py
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
        items.append({
            'id': 'ls:%s' % sig,
            'filt': 'ls',
            'title': sig,
            'badges': [freqs, 'ls-сигла'],
            'question': '<b>%s</b>&nbsp;→&nbsp;%s' % (esc(sig), mark_cyrillic('<b>%s</b>' % esc(prop))),
            'panels': [
                ('данные', '<pre>расшифровка: %s</pre>' % esc(exp)),
                ('примечание', '<pre>%s</pre>' % esc(note)),
            ],
            'note_placeholder': 'своя формулировка / комментарий',
        })
    return items


def meta_card():
    return {
        'id': 'meta:architecture',
        'filt': 'meta',
        'title': 'МЕТА: где применяется утвержденный список?',
        'badges': ['архитектура'],
        'question': (
            '<b>Принять</b> = применять только на этапе рендеринга (архитектура 10-07-2026: '
            'store хранит исходные теги, переводит генератор сайта — покрывает все будущие корни). '
            '<b>Отклонить</b> = список должен также переписать сам store (отдельный шаг с '
            'translation_memory/промоушен-механикой). <b>Отложить</b> = обсудить.'
        ),
        'panels': [(
            'контекст',
            '<pre>ABBREVIATIONS_RU.md § "Architecture decision: fix at RENDER TIME"\n'
            'Решение 10-07 остается в силе, пока эта карточка не проголосована иначе. '
            'Перенесено из h1303_abbrev без изменений (H1682). H2047: content remake only.</pre>',
        )],
        'note_placeholder': 'комментарий',
    }


def build():
    r = coll.classify()
    all_toks = list(r['by_token'].keys())
    kwic = collect_kwic(all_toks, limit=MAX_EXAMPLES)

    items = []
    for label in r['order']:
        sec = r['sections'][label]
        items.append(rule_card(
            label, sec['bulk'], sec['residue'], r['citation'][label], r['by_token'], kwic,
        ))
    n_rule_cards = len(items)

    residue_toks = [t for label in r['order'] for t in r['sections'][label]['residue']]
    for tok in residue_toks:
        items.append(residue_card(tok, r['by_token'][tok], kwic))
    n_residue_cards = len(residue_toks)

    items.extend(ls_cards())
    items.append(meta_card())

    n_bulk = sum(1 for row in r['by_token'].values() if not row['residue'])
    config = {
        'sheet_id': SHEET_ID,
        'title': 'H1682 — сокращения pwg_ru: ратификация правил (content v3 / H2047)',
        'subtitle': (
            'H2047 content remake (MG 31-07): expansion+freq, case-fold семьи, '
            'падежи stay-Latin (не Acc.→акк.), до %d кликабельных KWIC на карточку. '
            '%d ab-токенов → %d правил + %d неоднозначных + 3 ls + 1 мета = %d карточек. '
            'Не голосуйте, пока case-секция и примеры не совпадают с lock.'
            % (MAX_EXAMPLES, n_bulk, n_rule_cards, n_residue_cards,
               n_rule_cards + n_residue_cards + len(_LS_BORDER) + 1)
        ),
        'footer': (
            'Экспорт: pwg_ru/eval/h1682_abbrev_rules.decisions.json. '
            'H2047 executor override: Grok 4.5 (grok-4.5) for Opus comparison. '
            'Cases locked Latin-stay MG 31-07; non-case grammar awaits H2048 crosswalk.'
        ),
        'approve_label': 'принять',
        'reject_label': 'оставить как есть',
        'filters': [
            ('rule', 'правила'),
            ('ambig', 'неоднозначные'),
            ('ls', 'ls-сиглы'),
            ('meta', 'мета'),
        ],
        'generated': GENERATED,
    }
    config.update(standard_config(save_as='pwg_ru/eval/h1682_abbrev_rules.decisions.json'))
    # standard_config already sets note_min_height_px=88 and show_ids
    assert config.get('note_min_height_px') == NOTE_MIN_HEIGHT_PX

    html_doc = render_review_sheet(items, config, extras=True,
                                   screening=screening_block(
                                       deterministic=0, lookup=0, agent=0,
                                      human=len(items),
                                      evidence_path="RussianTranslation/pwg_ru/SCREENING_H1650.md",
                                       rules=[]))

    out = os.path.join(RT, 'review', 'h1682_abbrev_rules_sheet.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    stamped, chash = review_binding.stamp(html_doc)
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(stamped)
    lock_path = review_binding.lock_from_html(out, gate=None)

    print('H1682 rules sheet v3 (H2047): %d cards (%d rule + %d ambiguous + %d ls + 1 meta) -> %s'
          % (len(items), n_rule_cards, n_residue_cards, len(_LS_BORDER), out))
    print('  %s' % chash)
    print('  lock -> %s' % lock_path)
    return out


if __name__ == '__main__':
    build()
