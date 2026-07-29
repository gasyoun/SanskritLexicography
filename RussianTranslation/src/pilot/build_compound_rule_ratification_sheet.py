#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H1887 — ratify the RULES that auto-resolve the PWG-vs-index compound queue.

## What changed, and why this sheet is 30 cards and not 200

The 4,246-row `differs` queue already carries a machine verdict per row, with a
NAMED RULE and cited evidence, from `adjudicate_compound_differs.py` (H1681):
3,975 rows resolve for PWG, 24 for the index, 247 stay unresolved. The two blind
sheets (H1628 n=200, H1703 n=232) were built to PRICE that adjudicator.

On 29-07-2026 MG opened the H1628 sheet and asked why he was voting at all. The
measurement behind his complaint: **191 of its 200 cards already had a verdict, a
rule and a reason** — computed from the same two input files the sheet itself
reads — and the sheet rendered none of it. Worse, 69 of the 200 cards (34.5 %) were
not split disagreements in the first place (same cut, different spelling
convention), and 18 of the 44 cards showing a «Пāṇini» line showed a reference that
cannot exist (adhyāya > 8 — Ṛgveda citations swept into the upstream column).

MG's ruling (29-07-2026): auto-resolve the non-decisions by rule, and prove the
RULE on ~30 cards rather than re-voting the rows. So this sheet asks, per card,
one question: **does this rule hold here?** Approving a card ratifies the rule for
its whole class; rejecting it says the rule breaks on this card and names how.

Ratifying all seven rules retires **3,975 rows** from the human queue.

## The evidence contract (MG's V9 ruling, 29-07-2026)

Every card carries, or explicitly states why it cannot:

* both sides' split **in IAST**, never SLP1 (SLP1 lives in the copyable id chip);
* **what each side actually is** — PWG names the compound's members as LEXEMES in
  its etymology parenthesis; the "index" is Jim Funderburk's em-dash segmentation
  of MW's `<k2>`, which by construction concatenates back to the headword. Two
  conventions, not two claims;
* the **raw source text of both** — PWG's parenthesis and MW's `<k2>` — so the
  reviewer checks the dictionaries, not our transcription of them;
* DCS corpus frequency where the lemma has one;
* clickable: PWG entry (kosha co-location), PWG scan column, Cologne MW entry,
  and any Pāṇini sūtra that structurally CAN exist, deep-linked to ashtadhyayi.com;
* structurally impossible "sūtra" references are suppressed and counted, never
  shown as authority.

`review_evidence_preflight.preflight()` BLOCKS the write if any of that slips.

    python src/pilot/build_compound_rule_ratification_sheet.py --report
    python src/pilot/build_compound_rule_ratification_sheet.py --write
    python src/pilot/build_compound_rule_ratification_sheet.py --selftest
"""
import csv
import io
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # src/pilot
SRC = os.path.dirname(HERE)                                 # src
REPO = os.path.dirname(SRC)                                 # RussianTranslation
SL = os.path.dirname(REPO)                                  # SanskritLexicography

ADJ_TSV = os.path.join(REPO, 'research', 'pwg_compound_differs_adjudication.tsv')
REVIEW_DIR = os.path.join(REPO, 'review')
SHEET_ID = 'sanskritlexicography-pwg-compound-rules_ratify30'
SHEET_HTML = os.path.join(REVIEW_DIR, '%s_review.html' % SHEET_ID)
MANIFEST_JSON = os.path.join(REVIEW_DIR, '%s_evidence_manifest.json' % SHEET_ID)
SEED = 1887
TARGET = 30
PER_RULE_FLOOR = 3
GENERATED = '29-07-2026'

sys.path.insert(0, SRC)
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config  # noqa: E402
from review_evidence_preflight import (EvidenceManifest, preflight,            # noqa: E402
                                       valid_sutras, sutra_href)

KOSHA_WHEEL = 'https://gasyoun.github.io/SamasaChakram/'
CDSL_MW = ('https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/'
           'webtc/indexcaller.php')


def pwg_scan_href(colnum):
    """PWG scan page for a printed column — same builder the article site uses
    (pilot/build_article_site.py::_pwg_scan)."""
    try:
        return ('https://sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/'
                'web/webtc/servepdf.php?page=%d' % int(colnum))
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------- the rule book
# Every rule below resolves FOR PWG. The Russian gloss is what MG ratifies; the
# `claim` is the sentence the card asks him to accept or break.
RULES = {
    'same_split_pwg_lemma_form': {
        'ru': 'Одно и то же членение, разная форма члена',
        'claim': ('Оба источника делят слово в одном и том же месте. Члены '
                  'различаются только формой: MW пишет отрезок так, как он стоит '
                  'внутри сложного слова, PWG называет лексему, которая за ним '
                  'стоит. Списку членов нужна лексема — значит, верен PWG.'),
    },
    'pwg_lexeme_vs_mw_suffixed_tail': {
        'ru': 'MW оставляет суффикс в хвосте, PWG называет лексему',
        'claim': ('Хвостовой член у MW несёт словообразовательный суффикс, PWG '
                  'называет лексему без него. Членение то же; верен PWG.'),
    },
    'mw_cut_leaves_nonword': {
        'ru': 'Разрез MW оставляет не-слово',
        'claim': ('Разрез MW порождает отрезок, который не является '
                  'самостоятельным словом. Членение PWG даёт словарные члены — '
                  'верен PWG.'),
    },
    'mw_anusvara_right_of_boundary': {
        'ru': 'Анусвара справа от границы',
        'claim': ('MW ставит границу так, что анусвара отходит вправо; это '
                  'орфографическая деталь записи, не другое членение. Верен PWG.'),
    },
    'mw_cut_absorbs_initial_vowel': {
        'ru': 'Разрез MW поглощает начальный гласный',
        'claim': ('Разрез MW относит начальный гласный второго члена к первому '
                  '(результат сандхи в записи). Членение то же; верен PWG.'),
    },
    'mw_splits_derivational_suffix': {
        'ru': 'MW отделяет словообразовательный суффикс как член',
        'claim': ('MW выделяет словообразовательный суффикс в отдельный член. '
                  'Суффикс не член сложного слова — верен PWG.'),
    },
    'mw_splits_bound_morph': {
        'ru': 'MW отделяет связанную морфему как член',
        'claim': ('MW выделяет связанную морфему в отдельный член. Она не '
                  'самостоятельный член сложного слова — верен PWG.'),
    },
}

REJECT_LABELS = [
    ('rule_wrong_here', 'Правило здесь не работает — членение PWG неверно'),
    ('rule_too_broad', 'Правило само по себе верно, но эту карточку не покрывает'),
    ('both_wrong', 'Оба членения неверны (правильное укажите в примечании)'),
    ('need_source', 'Не могу решить без сканa/источника'),
]


def load_adjudication(path=ADJ_TSV):
    rows = []
    with io.open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            rows.append(r)
    return rows


def stratified(rows, seed=SEED, target=TARGET, floor=PER_RULE_FLOOR):
    """Floor per rule so every rule is actually tested, then the remaining budget
    proportional to class size (largest remainder). Deterministic under `seed`."""
    rng = random.Random(seed)
    by = {}
    for r in rows:
        if r['verdict'] != 'pwg_members-right' or r['rule'] not in RULES:
            continue
        by.setdefault(r['rule'], []).append(r)
    picked, quota = [], {}
    for rule, rs in by.items():
        quota[rule] = min(floor, len(rs))
    left = target - sum(quota.values())
    if left > 0:
        tot = sum(len(v) for v in by.values())
        raw = {k: left * len(v) / float(tot) for k, v in by.items()}
        add = {k: int(v) for k, v in raw.items()}
        short = left - sum(add.values())
        for k, _ in sorted(raw.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True)[:short]:
            add[k] += 1
        for k in quota:
            quota[k] = min(quota[k] + add.get(k, 0), len(by[k]))
    for rule in sorted(by):
        rs = sorted(by[rule], key=lambda r: r['id'])
        picked.extend(rng.sample(rs, quota[rule]))
    picked.sort(key=lambda r: (r['rule'], r['id']))
    return picked, {k: quota[k] for k in sorted(quota)}, {k: len(v) for k, v in by.items()}


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def iast_split(members_slp1):
    """`a + b` in SLP1 -> `a + b` in IAST (human-facing; never SLP1)."""
    parts = [p.strip() for p in (members_slp1 or '').split('+') if p.strip()]
    return ' + '.join(slp1_iast(p) for p in parts)


# MG asked to see what the dictionaries actually print, not our transcription of
# it — but the committed source of BOTH is SLP1, which he does not read. So the
# source line is shown transliterated, with the exact SLP1 bytes one hover away
# (title=) for anyone machine-checking the extraction.
_HOM = re.compile(r'<hom>([^<]*)</hom>')
_CURLY = re.compile(r'\{#([^#]+)#\}')
_LATIN_RUN = re.compile(r"[A-Za-z/\\^']+")
_AB = re.compile(r'<ab\b[^>]*>(.*?)</ab>', re.S)

# PWG wraps every abbreviation in <ab>. Printing it raw ships `<ab>acc.</ab>` to
# the reviewer as literal markup (H1808's defect #5, on a different generator).
# `pwg_ab_ru.display()` already returns exactly (visible, tooltip) under MG's
# 10-07-2026 ruling — grammatical Latin sigla stay Latin, editorial German gets a
# Russian equivalent, both keep the authoritative DE/EN expansion on hover.
try:
    import pwg_ab_ru as _AB_RU
except Exception:                                    # pragma: no cover
    _AB_RU = None


def gloss_ab(s):
    def one(m):
        tok = (m.group(1) or '').strip()
        vis, title = (tok, None)
        if _AB_RU is not None:
            try:
                vis, title = _AB_RU.display(tok)
            except Exception:
                pass
        return ('<abbr title="%s">%s</abbr>' % (esc(title), esc(vis))) if title \
            else '<abbr>%s</abbr>' % esc(vis)
    return _AB.sub(one, s or '')


_SPAN = re.compile(r'\{#([^#]+)#\}|<ab\b[^>]*>(?:.*?)</ab>', re.S)


def iast_pwg_paren(s):
    """PWG's etymology parenthesis as SAFE HTML.

    `({#janam#}, <ab>acc.</ab> von {#jana#}, + {#tapa#})`
      -> `(janam, <abbr title="…">acc.</abbr> von jana, + tapa)`

    Sanskrit spans transliterate to IAST and are italicised; `<ab>` becomes a
    glossed `<abbr>`; every other run is escaped. Nothing reaches the reviewer as
    raw markup or raw SLP1.
    """
    s = _HOM.sub(r'\1 ', s or '')
    out, pos = [], 0
    for m in _SPAN.finditer(s):
        out.append(esc(s[pos:m.start()]))
        if m.group(1) is not None:
            out.append('<i>%s</i>' % esc(slp1_iast(m.group(1))))
        else:
            out.append(gloss_ab(m.group(0)))
        pos = m.end()
    out.append(esc(s[pos:]))
    return ''.join(out).strip()


def iast_mw_k2(s):
    """MW's `<k2>` as safe HTML: `bfhat—kAya` -> `bṛhat—kāya`, boundaries kept."""
    return esc(_LATIN_RUN.sub(lambda m: slp1_iast(m.group(0)), s or ''))


# Every key that actually occurs in the adjudication's `evidence` column, glossed.
# Censused from the file itself (10 distinct keys over 4,353 rows) rather than
# guessed — an unglossed key would print a machine identifier at the reviewer.
_EV_KEYS = {
    'form_diffs': 'формы членов различаются',
    'index_members_unattested': 'член указателя не является самостоятельным словом',
    'pwg_members_unattested': 'член PWG не является самостоятельным словом',
    'taddhita_suffix': 'вторичный суффикс (taddhita)',
    'mw_hyphen_members': 'дефисные члены MW',
    'absorbed_vowel': 'поглощённый начальный гласный',
    'mw_is_finer': 'MW членит мельче',
    'pwg_is_finer': 'PWG членит мельче',
    'mw_suffix_member': 'MW выделил суффикс в член',
    'pwg_typo_pairs': 'опечатка в источнике PWG',
}


def iast_evidence(s):
    """`form_diffs=bfhant|bfhat; mw_hyphen_members=A-DAra` ->
    `формы членов = bṛhant | bṛhat; дефисные члены MW = ā-dhāra`."""
    out = []
    for chunk in (s or '').split(';'):
        chunk = chunk.strip()
        if not chunk:
            continue
        if '=' in chunk:
            k, v = chunk.split('=', 1)
            k = _EV_KEYS.get(k.strip(), k.strip())
            vals = ' | '.join(slp1_iast(p.strip()) for p in v.split('|') if p.strip())
            out.append('%s = %s' % (k, vals))
        else:
            out.append(slp1_iast(chunk))
    return '; '.join(out)


def src_cell(raw, body_html):
    """One source cell: readable form visible, exact source bytes in the tooltip.

    `body_html` is ALREADY escaped/marked-up by its builder — never re-escape it.
    """
    if not (raw or '').strip():
        return '—'
    return '<code title="источник (SLP1): %s">%s</code>' % (esc(raw), body_html)


def load_derivation():
    """(k1, hom) -> the derivation-layer row, for `panini_sutras` + `ganas`.

    The adjudication TSV does NOT carry these columns, so joining the derivation
    layer is what makes the manifest's `panini_sutras` declaration true. Left
    unjoined, the Panini panel would silently claim every headword has no sutra.
    """
    path = os.path.join(SRC, 'pwg_derivation_layer.tsv')
    m = {}
    if not os.path.exists(path):
        return m
    with io.open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            m.setdefault((r['k1'], r.get('hom', '')), r)
    return m


def load_columns():
    """root -> printed PWG column, for the scan link."""
    path = os.path.join(SRC, 'pwg_columns.tsv')
    m = {}
    if not os.path.exists(path):
        return m
    with io.open(path, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        ci, hi = head.index('column'), head.index('headwords')
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) <= hi:
                continue
            for hw in p[hi].split(','):
                hw = hw.strip()
                if hw and hw not in m:
                    m[hw] = p[ci]
    return m


def build_items(sample, columns, deriv):
    items, suppressed_total, card_ev = [], 0, {}
    for r in sample:
        k1 = r['k1']
        iid = r['id']
        rule = RULES[r['rule']]
        iast = slp1_iast(k1)
        pwg_i = iast_split(r['pwg_members'])
        idx_i = iast_split(r['index_members'])

        fields, omitted = [], []

        # ---- the claim being ratified
        q = ['<p class="claim"><b>Правило:</b> %s</p>' % esc(rule['ru']),
             '<p>%s</p>' % esc(rule['claim'])]

        # ---- both sides, IAST, with what each side IS
        q.append(
            '<table class="sides"><tr><th></th><th>членение</th><th>что напечатано в словаре</th></tr>'
            '<tr><td><b>PWG</b><br><span class="prov">члены как ЛЕКСЕМЫ, '
            'из этимологической скобки статьи</span></td>'
            '<td class="split">%s</td><td>%s</td></tr>'
            '<tr><td><b>Указатель</b><br><span class="prov">сегментация MW '
            '&lt;k2&gt; эм-дефисами (Дж. Фундербёрк); по построению склады&shy;вается '
            'обратно в заголовок</span></td>'
            '<td class="split">%s</td><td>%s</td></tr></table>'
            % (esc(pwg_i),
               src_cell(r.get('pwg_source_paren'), iast_pwg_paren(r.get('pwg_source_paren'))),
               esc(idx_i),
               src_cell(r.get('mw_k2_raw'), iast_mw_k2(r.get('mw_k2_raw')))))
        fields += ['pwg_members', 'index_members']
        if (r.get('pwg_source_paren') or '').strip():
            fields.append('pwg_source_paren')
        if (r.get('mw_k2_raw') or '').strip():
            fields.append('mw_k2_raw')

        if (r.get('evidence') or '').strip():
            q.append('<p class="ev"><b>Что именно различается:</b> %s</p>'
                     % src_cell(r['evidence'], esc(iast_evidence(r['evidence']))))
            fields.append('evidence')

        # ---- panels
        panels = []

        # sources, all clickable
        links = []
        href = pwg_entry_href(k1)
        if href:
            links.append('<a href="%s">статья PWG (со-локация kosha)</a>' % href)
            fields.append('pwg_entry_href')
        col = columns.get(k1)
        if col:
            sh = pwg_scan_href(re.sub(r'\D', '', col.split('-')[-1]) or 0)
            if sh:
                links.append('<a href="%s">скан PWG, столбец %s</a>' % (sh, esc(col)))
                fields.append('pwg_scan')
        else:
            omitted.append('скан PWG: столбец для этого заголовка отсутствует в pwg_columns.tsv')
        links.append('<a href="%s">MW в Cologne</a>' % CDSL_MW)
        if (r.get('L_id') or '').strip():
            links.append('PWG <code>L%s</code>' % esc(r['L_id']))
            fields.append('L_id')
        panels.append(('Источники', ' · '.join(links)))

        # frequency
        f = (r.get('dcs_freq') or '').strip()
        if f and f not in ('0', ''):
            panels.append(('Частотность',
                           'DCS: <b>%s</b> вхождений корпуса.' % esc(f)))
            fields.append('dcs_freq')
        else:
            panels.append(('Частотность',
                           '<span class="miss">Нет данных DCS для этой леммы — '
                           'слово в корпусе DCS не засвидетельствовано, '
                           'поэтому примера употребления показать нельзя.</span>'))
            omitted.append('частота/цитата DCS: лемма не засвидетельствована в DCS')

        # samasa layer — honest about what does and does not exist
        panels.append((
            'Самаса',
            'Тип сложного слова для этого заголовка <b>не назначен</b>: в '
            '<a href="%s">SamasaChakram</a> есть таксономия (4 класса / 10 семейств / '
            '58 подтипов) и 20 разобранных примеров, но пословного соответствия '
            '«заголовок → подтип» нет ни в одном репозитории. Колесо и метод '
            'чтения справа налево — по ссылке.' % KOSHA_WHEEL))
        omitted.append('тип самасы: пословного соответствия заголовок→подтип не существует')

        # Panini — only what can exist
        drow = deriv.get((k1, r.get('hom', '')), {})
        raw = drow.get('panini_sutras') or ''
        good, bad = valid_sutras(raw)
        suppressed_total += len(bad)
        if good:
            hl = ' · '.join('<a href="%s">P. %s</a>' % (sutra_href(g), esc(g)) for g in good)
            body = 'Сутры: %s' % hl
            fields.append('panini_sutras')
        else:
            body = '<span class="miss">Сутр Панини для этого заголовка нет.</span>'
        if bad:
            body += ('<br><span class="miss">Скрыто %d ссыл(ки) вида <code>%s</code>: '
                     'в «Аштадхьяи» 8 адхьяй по 4 пады, поэтому такие номера сутрами '
                     'быть не могут — это цитаты других текстов, попавшие в колонку '
                     'при извлечении (дефект источника, H1888).</span>'
                     % (len(bad), esc(', '.join(bad[:4]))))
        gana = (drow.get('ganas') or '').strip()
        if gana:
            body += ('<br>Гана: <b>%s</b>%s' % (
                esc(slp1_iast(gana)),
                ' (подтверждена сутрой %s)' % esc(drow.get('gana_sutras', ''))
                if (drow.get('gana_corroborated') or '').strip() in ('1', 'true', 'True')
                else ''))
            fields.append('ganas')
        panels.append(('Панини', body))

        items.append({
            'id': iid,
            'filt': r['rule'],
            # structured facet dimensions, NOT a badge string. The H1628 sheet
            # concatenated three raw enum keys into one unreadable run
            # ("same_count_diff_splitmedium(9-10)no_dcs_freq"); facets keep each
            # dimension separate, labelled and filterable.
            'facets': {'rule': [rule['ru']],
                       'dcs': ['есть' if (f and f != '0') else 'нет']},
            'badges': [rule['ru']],
            'title': '%s' % iast,
            'title_href': href,
            'question': ''.join(q),
            'panels': panels,
            'note_placeholder': ('Если правило здесь ломается — напишите, какое '
                                 'членение верно и почему'),
        })
        card_ev[iid] = (fields, omitted)
    return items, suppressed_total, card_ev


EXTRA_CSS = """
.claim{font-size:1.05em}
table.sides{border-collapse:collapse;width:100%;margin:.6em 0}
table.sides th{text-align:left;font-weight:600;opacity:.7;font-size:.85em;padding:.2em .5em}
table.sides td{vertical-align:top;padding:.35em .5em;border-top:1px solid rgba(128,128,128,.35)}
table.sides td.split{font-size:1.25em;white-space:nowrap}
.prov{opacity:.65;font-size:.8em;font-weight:400}
.miss{opacity:.75;font-style:italic}
.ev code{font-size:.95em}
"""


def render(sample, columns, deriv, generated=GENERATED):
    from csl_pyutil import render_review_sheet
    items, suppressed, card_ev = build_items(sample, columns, deriv)
    n_rules = len({i['filt'] for i in items})
    config = {
        'sheet_id': SHEET_ID,
        'title': 'Правила членения сложных слов PWG: ратификация',
        'subtitle': (
            '%d карточек, %d правил. Вы решаете НЕ отдельные слова, а <b>правила</b>: '
            'каждое правило уже разобрало целый класс строк очереди <code>differs</code> '
            '(всего 4&nbsp;246). Приняв правило, вы снимаете весь его класс с '
            'голосования навсегда; отклонив — возвращаете класс в очередь. '
            'Ратификация всех семи правил снимает <b>3&nbsp;975 строк</b>.'
            % (len(items), n_rules)),
        'footer': (
            '<b>Принять</b> = правило на этой карточке работает, членение PWG верно. '
            '<b>Отклонить</b> = правило здесь ломается — выберите, как именно, и '
            'по возможности укажите верное членение в примечании. '
            '<b>Отложить</b> = нужен скан или источник. '
            'Что показано на карточке: оба членения в IAST, исходный текст обоих '
            'словарей (этимологическая скобка PWG и &lt;k2&gt; MW), частота DCS, '
            'ссылки на статью и скан. Чего нет — написано прямо на карточке, с причиной.'),
        'approve_label': 'Правило верно',
        'reject_label': 'Правило ломается',
        'reject_labels': REJECT_LABELS,
        'filters': [(k, RULES[k]['ru']) for k in sorted(RULES)],
        'facets': [
            {'key': 'rule', 'label': 'Правило',
             'values': [RULES[k]['ru'] for k in sorted(RULES)]},
            {'key': 'dcs', 'label': 'Частота DCS', 'values': ['есть', 'нет']},
        ],
        'generated': generated,
        'font_scale': 1.5,
        'extra_css': EXTRA_CSS,
        'save_as': r'RussianTranslation\review\%s_decisions.json' % SHEET_ID,
        'strict_review': {'require_reject_note': True},
        # The emitter's own chrome is English by default; this sheet is Russian.
        # NOTE: the per-card "Defer" button and the "Reason" select label are NOT
        # reachable through UI_STRINGS in csl-pyutil 0.7.0 — they stay English.
        # Adding those two keys is folded into H1889 rather than patched here with
        # brittle post-processing (the exact anti-pattern UI_STRINGS exists to kill).
        'ui_strings': {
            'download_button': 'Скачать decisions.json',
            'save_button': 'Сохранить в папку…',
            'footer_hint': (
                'Клавиши: a — принять, r — отклонить, d — отложить, ←/→ — соседняя '
                'карточка. Голоса сохраняются в браузере по мере работы; '
                'по кнопке «Скачать decisions.json» выгружается файл решений.'),
        },
    }
    config.update(standard_config(save_as=config['save_as']))
    html = render_review_sheet(items, config)
    return html, items, suppressed, card_ev


def gate(html, items, card_ev):
    """The H1887 preflight — nothing is written unless this passes."""
    man = EvidenceManifest(sheet_id=SHEET_ID, row_ids=[i['id'] for i in items],
                           repo_root=REPO, min_evidence_fields=4)
    man.declare_joined('research/pwg_compound_differs_adjudication.tsv',
                       ['verdict', 'rule', 'reason', 'evidence', 'pwg_members',
                        'index_members', 'pwg_source_paren', 'mw_k2_raw', 'dcs_freq',
                        'L_id'])
    man.declare_joined('src/pwg_columns.tsv', ['column'])
    man.declare_joined('src/headword_index.tsv', ['compound_members'])
    man.declare_joined('src/pwg_derivation_layer.tsv', ['panini_sutras'])
    man.declare_joined('src/pwg_freq_order.tsv', ['count_all'])
    man.declare_omitted_path(
        'src/mw_compounds.json',
        'the index side IS MW: headword_index.compound_members is Funderburk\'s '
        'em-dash segmentation of MW <k2>, already shown as one of the two sides — '
        'joining this again would double-count one source as two opinions')
    man.declare_omitted_path(
        'src/pwg_entry_locations.tsv',
        'pagination only; pwg_columns.tsv already supplies the printed column used '
        'for the scan link, and entry location bears on neither split nor rule')
    man.declare_omitted_path(
        'src/pwg_pages.tsv',
        'page-level index, superseded here by pwg_columns.tsv which is column-level '
        'and is what the PWG scan URL actually needs')
    man.declare_omitted_path(
        'src/reverse_paradigm_index.json',
        'inflectional paradigms keyed on the same headwords; the question under '
        'ratification is compound segmentation, on which paradigm data is silent')
    man.declare_omitted_path(
        'research/lex_noun_link_pwg.tsv',
        'noun-sense linking layer; covers 16 of these 30 headwords but carries sense '
        'links, not segmentation evidence, so it cannot bear on the rule')
    man.declare_omitted(
        'samasa subtype per headword',
        'SamasaChakram carries a 58-subtype taxonomy and 20 worked plates but no '
        'headword-to-subtype mapping exists in any repo; the wheel is linked instead')
    man.declare_omitted(
        'DCS attested sentence',
        'the DCS attestation tables in research/ are SENSE-level for PWG entries, '
        'not headword-level for compounds; no per-compound sentence map exists yet')
    for iid, (fields, omitted) in card_ev.items():
        man.add_card(iid, evidence_fields=fields, omitted=omitted)
    # V3 of the standard puts a copyable SLP1 id chip on every card ON PURPOSE —
    # MG cites ids back. Those exact strings are therefore DECLARED as allowed
    # rather than silently exempted, so a stray SLP1 token anywhere else on the
    # card still blocks.
    ids = [i['id'] for i in items]
    allow = set(ids) | {i.split('~~')[0] for i in ids}
    return man, preflight(man, html, overlap_threshold=0.5,
                          allow_slp1_tokens=sorted(allow))


def report():
    rows = load_adjudication()
    sample, quota, sizes = stratified(rows)
    print('adjudicated rows            : %d' % len(rows))
    print('rules that resolve for PWG  : %d' % len(sizes))
    print()
    print('%-38s %8s %7s' % ('rule', 'in queue', 'sampled'))
    print('-' * 56)
    tot = 0
    for k in sorted(sizes):
        print('%-38s %8d %7d' % (k, sizes[k], quota.get(k, 0)))
        tot += sizes[k]
    print('-' * 56)
    print('%-38s %8d %7d' % ('TOTAL', tot, len(sample)))
    print()
    print('ratifying all %d rules retires %d rows from the human queue.' % (len(sizes), tot))


def selftest():
    rows = load_adjudication()
    sample, quota, sizes = stratified(rows)
    assert len(sample) == TARGET, len(sample)
    s2, _, _ = stratified(rows)
    assert [r['id'] for r in s2] == [r['id'] for r in sample], 'sample must be deterministic'
    assert all(quota[k] >= min(PER_RULE_FLOOR, sizes[k]) for k in sizes), \
        'every rule must be represented'
    ids = [r['id'] for r in sample]
    assert len(set(ids)) == len(ids), 'duplicate card id'
    columns, deriv = load_columns(), load_derivation()
    html, items, suppressed, card_ev = render(sample, columns, deriv)
    assert len(items) == TARGET
    man, rep = gate(html, items, card_ev)          # raises if it would ship broken
    assert rep['mixed_script'] == [], rep['mixed_script']
    assert rep['slp1_leak'] == [], rep['slp1_leak']
    assert rep['impossible_citations'] == [], rep['impossible_citations']
    assert not rep['prior_art_undeclared'], rep['prior_art_undeclared']
    print('selftest OK — %d cards over %d rules, deterministic under seed=%d, '
          'preflight clean (no mixed script, no SLP1 leak, no impossible citation, '
          'no undeclared prior art), %d impossible sutra refs suppressed'
          % (len(items), len(sizes), SEED, suppressed))


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    if '--write' in args:
        rows = load_adjudication()
        sample, quota, sizes = stratified(rows)
        columns, deriv = load_columns(), load_derivation()
        html, items, suppressed, card_ev = render(sample, columns, deriv)
        man, rep = gate(html, items, card_ev)
        os.makedirs(REVIEW_DIR, exist_ok=True)
        with io.open(SHEET_HTML, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        man.write(MANIFEST_JSON)
        print('wrote sheet    -> %s' % SHEET_HTML)
        print('wrote manifest -> %s' % MANIFEST_JSON)
        print('cards: %d over %d rules; suppressed %d impossible sutra refs'
              % (len(items), len(sizes), suppressed))
        print('preflight: PASS (%d prior-art artifacts declared)' % len(man.joined))
        return
    report()


if __name__ == '__main__':
    main()
