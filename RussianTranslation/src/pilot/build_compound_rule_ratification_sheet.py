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
        # MG 29-07-2026: «MW оставляет с суффиксом, PWG приводит основу».
        'ru': 'MW оставляет с суффиксом, PWG приводит основу',
        'claim': ('Хвостовой член у MW несёт словообразовательный суффикс, PWG '
                  'приводит основу без него. Членение то же; верен PWG.'),
    },
    'mw_cut_leaves_nonword': {
        'ru': 'Разрез MW оставляет не-слово',
        'claim': ('Разрез MW порождает отрезок, который не является '
                  'самостоятельным словом. Членение PWG даёт словарные члены — '
                  'верен PWG.'),
    },
    'mw_anusvara_right_of_boundary': {
        # MG 29-07-2026: «Анусвара справа от первой части», и — важнее — никто не
        # утверждает, что ṃtapa отдельное слово: читается janaṃ + tapa. Поэтому
        # членение MW на карточке теперь показывается с анусварой, приклеенной
        # ВЛЕВО (см. mw_display_split), а не как index_members из TSV.
        'ru': 'Анусвара справа от первой части',
        'claim': ('MW печатает границу как <code>jana—ṃ-tapa</code>: анусвара '
                  'вынесена за дефис вправо. Это деталь записи, а не утверждение, '
                  'что <i>ṃtapa</i> — отдельное слово; читается '
                  '<b>janaṃ + tapa</b>. PWG пишет тот же член как <i>janam</i> '
                  '(винительный падеж). Это одно и то же членение — верен PWG.'),
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
    'mw_recursive_decomposition': {
        # MG's ruling, 30-07-2026 (H1918): любая самаса состоит ровно из двух
        # частей (кроме двандвы); n-членный список MW — это не конкурирующее
        # членение заголовка, а рекурсивный разбор ПЕРВОГО члена.
        'ru': 'Список MW — рекурсивный разбор первого члена, не другое членение',
        'claim': ('Самаса всегда двучленна (кроме двандвы). Список MW длиннее '
                  'списка PWG, и его члены складываются в тот же заголовок, но '
                  'это не конкурирующая виграха: MW заодно разбирает и первый '
                  'член PWG на его собственные составляющие — самаса внутри '
                  'самасы. Виграха заголовка — двучленная, верен PWG.'),
    },
}

# MG's structural ruling, 29-07-2026: любая самаса состоит РОВНО из двух частей
# (кроме двандвы, где частей может быть сколько угодно). Поэтому трёхчленный
# список MW — это не конкурирующий анализ, а самаса внутри самасы: для
# `gozWIpati` виграха — `gozWI + pati`, а `go + zWI` это уже разбор первого члена.
# Измерено: PWG даёт ровно 2 члена в 4 342 из 4 353 строк (99,7 %); MW даёт 3
# члена в 66 строках, и во ВСЕХ 66 у PWG ровно два.
BINARY_NOTE = (
    'Самаса состоит ровно из двух частей (исключение — двандва, где частей может '
    'быть сколько угодно). Трёхчленный список MW — это не другое членение, а '
    '<b>самаса внутри самасы</b>: MW заодно разбирает и первый член. Виграха для '
    'этого заголовка — двучленная, то есть PWG.')

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


def _ev_val(v):
    """Transliterate an evidence VALUE only when it is Sanskrit.

    `mw_is_finer=True` is a boolean flag, not a word: running it through
    slp1_iast turned it into "thrue" (T->th) on the goṣṭhīpati card. Flags carry
    no information beyond the key, so they render as nothing.
    """
    if v in ('True', 'true', '1'):
        return ''
    if v in ('False', 'false', '0'):
        return 'нет'
    if re.fullmatch(r'[\d.,]+', v):
        return v
    return slp1_iast(v)


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
            vals = ' | '.join(_ev_val(p.strip()) for p in v.split('|') if p.strip())
            out.append(('%s: %s' % (k, vals)) if vals else k)
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


# --------------------------------------------------------- MW display split
# MG 29-07-2026, point 3: «Никто, конечно, не имеет ввиду, что jana + ṃtapa, что
# существует отдельное слово ṃtapa … Имеется ввиду janaṃ + tapa.» The TSV's
# `index_members` splits MW's `jana—ṃ-tapa` at the em-dash, which strands the
# anusvāra on the second member and makes MW look like it is claiming a word
# that does not exist. MW's own notation says otherwise: `ṃ-` is hyphen-attached
# leftward material, not the head of the second member.
#
# Point 5: `tejo—'hvā` — the apostrophe is an avagraha, i.e. an elided initial
# `a` produced by sandhi. Printing it bare invites the same misreading.
_ANUSVARA_TAIL = re.compile(r'^M(.+)$')


def mw_display_split(index_members, rule, k2_raw=''):
    """MW's split as a reader should read it, plus a note when the raw notation
    needed interpreting. Returns (iast_split, note_html_or_None)."""
    parts = [p.strip() for p in (index_members or '').split('+') if p.strip()]
    note = None
    # Every quotation of the raw `<k2>` goes through iast_mw_k2 for the VISIBLE
    # text, keeping the exact SLP1 bytes in the tooltip — the same contract as
    # src_cell. Printing the raw string here is what the preflight caught.
    k2_shown = src_cell(k2_raw, iast_mw_k2(k2_raw)) if k2_raw else '—'
    if rule == 'mw_anusvara_right_of_boundary' and len(parts) == 2:
        m = _ANUSVARA_TAIL.match(parts[1])
        if m:
            parts = [parts[0] + 'M', m.group(1)]
            note = ('MW печатает %s: анусвара отделена дефисом и стоит справа от '
                    'границы. Это запись, а не утверждение, что <i>%s</i> — '
                    'самостоятельное слово; здесь она приклеена обратно к первой '
                    'части.' % (k2_shown, esc(slp1_iast(m.group(0)))))
    if "'" in (k2_raw or ''):
        note = ((note + ' ') if note else '') + (
            'В %s апостроф — <b>аваграха</b>: он стоит на месте начального '
            '<i>a</i>, выпавшего по сандхи, то есть восходит к <i>%s</i>.'
            % (k2_shown, esc(iast_mw_k2(k2_raw.replace("'", 'a')))))
    return ' + '.join(slp1_iast(p) for p in parts), note


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


def _thou(n):
    return '{:,}'.format(int(n)).replace(',', ' ')      # 3 975 -> 3 975


_GERMAN_GLUE = re.compile(r'^\s*von\s+|\s*\bvon\b\s*')


def _same_text(a, b):
    """Do these two renderings say the same thing? German editorial glue («von»
    = "from") is not content — MG point 8: drop it rather than print the split
    twice with a German preposition in front of the second copy."""
    def n(s):
        s = _GERMAN_GLUE.sub(' ', (s or ''))
        return re.sub(r'[\s()​]+', '', re.sub(r'<[^>]+>', '', s))
    return bool(n(a)) and n(a) == n(b)


def build_items(sample, columns, deriv, rule_sizes, queue_total):
    items, suppressed_total, card_ev = [], 0, {}
    for r in sample:
        k1 = r['k1']
        iid = r['id']
        rule = RULES[r['rule']]
        iast = slp1_iast(k1)
        pwg_i = iast_split(r['pwg_members'])
        idx_i, mw_note = mw_display_split(r['index_members'], r['rule'],
                                          r.get('mw_k2_raw') or '')

        fields, omitted = [], []

        # ---- the claim being ratified, with how much of the queue rides on it
        n_rule = rule_sizes.get(r['rule'], 0)
        q = ['<p class="claim"><b>Правило:</b> %s '
             '<span class="stat">— покрывает %s строк очереди (%.1f %% из %s)</span></p>'
             % (esc(rule['ru']), _thou(n_rule), 100.0 * n_rule / max(1, queue_total),
                _thou(queue_total)),
             '<p>%s</p>' % rule['claim']]

        # ---- both sides, IAST, with what each side IS.
        # The source cell is dropped when it would only repeat the split (MG
        # point 8: `aṅghri + parṇa   (von aṅghri + parṇa)` says nothing twice).
        pwg_src = iast_pwg_paren(r.get('pwg_source_paren'))
        pwg_src_cell = ('<span class="same">= членение</span>'
                        if _same_text(pwg_src, pwg_i)
                        else src_cell(r.get('pwg_source_paren'), pwg_src))
        mw_src = iast_mw_k2(r.get('mw_k2_raw'))
        mw_src_cell = ('<span class="same">= членение</span>'
                       if _same_text(mw_src, idx_i)
                       else src_cell(r.get('mw_k2_raw'), mw_src))
        q.append(
            '<table class="sides"><tr><th></th><th>членение</th><th>что напечатано в словаре</th></tr>'
            '<tr><td><b>PWG</b><br><span class="prov">члены как ЛЕКСЕМЫ, '
            'из этимологической скобки статьи</span></td>'
            '<td class="split">%s</td><td>%s</td></tr>'
            '<tr><td><b>MW split</b><br><span class="prov">сегментация MW '
            '&lt;k2&gt; эм-дефисами (Дж. Фундербёрк); по построению склады&shy;вается '
            'обратно в заголовок</span></td>'
            '<td class="split">%s</td><td>%s</td></tr></table>'
            % (esc(pwg_i), pwg_src_cell, esc(idx_i), mw_src_cell))
        if mw_note:
            q.append('<p class="note">%s</p>' % mw_note)
        # MG's binary ruling — only where MW actually lists more than two.
        if len([p for p in (r['index_members'] or '').split('+') if p.strip()]) > 2:
            q.append('<p class="note">%s</p>' % BINARY_NOTE)
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

        # No per-card samasa panel. MG point 4: the type is unassigned for EVERY
        # headword, so repeating that on 30 cards is 30 copies of one sentence.
        # It is stated once in the footer, together with what is actually missing.
        omitted.append('тип самасы: пословного соответствия заголовок→подтип не существует '
                       '(сказано один раз в подвале, а не на каждой карточке)')

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
            # No `badges`. MG point 1: the rule name was printed twice — once as a
            # badge beside the title and again in the «Правило:» line. It stays in
            # «Правило:» (where it carries its claim and its row count) and in the
            # facet bar (where it filters); the badge said nothing the other two
            # did not already say.
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
.stat{opacity:.7;font-weight:400;font-size:.85em}
.same{opacity:.55;font-style:italic;font-size:.9em}
.note{opacity:.9;border-left:3px solid rgba(128,128,160,.5);padding-left:.7em;margin:.5em 0}
table.stats{border-collapse:collapse;margin:.8em 0;font-size:.85em}
table.stats th{text-align:left;opacity:.7;font-weight:600;padding:.2em .8em .2em 0}
table.stats td{padding:.15em .8em .15em 0;border-top:1px solid rgba(128,128,128,.25)}
table.stats td.num{text-align:right;font-variant-numeric:tabular-nums}
table.stats tr.tot td{font-weight:700;border-top:2px solid rgba(128,128,128,.5)}
"""


def stats_table(rule_sizes, quota, queue_total, resolved_total):
    """MG point 2 — «Добавь статистику по каждому в голосовании и вообще».
    One table, up front: what each rule covers and how many cards test it."""
    rows = ['<table class="stats"><tr><th>Правило</th><th>строк очереди</th>'
            '<th>доля</th><th>карточек здесь</th></tr>']
    for k in sorted(RULES, key=lambda x: -rule_sizes.get(x, 0)):
        n = rule_sizes.get(k, 0)
        rows.append('<tr><td>%s</td><td class="num">%s</td><td class="num">%.1f %%</td>'
                    '<td class="num">%d</td></tr>'
                    % (esc(RULES[k]['ru']), _thou(n),
                       100.0 * n / max(1, queue_total), quota.get(k, 0)))
    rows.append('<tr class="tot"><td>Итого</td><td class="num">%s</td>'
                '<td class="num">%.1f %%</td><td class="num">%d</td></tr>'
                % (_thou(resolved_total), 100.0 * resolved_total / max(1, queue_total),
                   sum(quota.values())))
    rows.append('</table>')
    return ''.join(rows)


def render(sample, columns, deriv, rule_sizes, quota, queue_total, generated=GENERATED):
    from csl_pyutil import render_review_sheet
    items, suppressed, card_ev = build_items(sample, columns, deriv,
                                             rule_sizes, queue_total)
    n_rules = len({i['filt'] for i in items})
    resolved = sum(rule_sizes.values())
    config = {
        'sheet_id': SHEET_ID,
        'title': 'Правила членения сложных слов PWG: ратификация',
        'subtitle': (
            '%d карточек, %d правил. Вы решаете НЕ отдельные слова, а <b>правила</b>: '
            'каждое правило уже разобрало целый класс строк очереди <code>differs</code> '
            '(всего %s). Приняв правило, вы снимаете весь его класс с '
            'голосования навсегда; отклонив — возвращаете класс в очередь. '
            'Ратификация всех %d правил снимает <b>%s строк</b> (%.1f %% очереди).%s'
            % (len(items), n_rules, _thou(queue_total), n_rules, _thou(resolved),
               100.0 * resolved / max(1, queue_total),
               stats_table(rule_sizes, quota, queue_total, resolved))),
        'footer': (
            '<b>Принять</b> = правило на этой карточке работает, членение PWG верно. '
            '<b>Отклонить</b> = правило здесь ломается — выберите, как именно, и '
            'по возможности укажите верное членение в примечании. '
            '<b>Отложить</b> = нужен скан или источник. '
            'Что показано на карточке: оба членения в IAST, исходный текст обоих '
            'словарей (этимологическая скобка PWG и &lt;k2&gt; MW — если он не '
            'повторяет членение слово в слово), частота DCS, ссылки на статью и скан. '
            '<b>Тип самасы не показан ни на одной карточке</b>, и это не пропуск '
            'конкретной карточки: в <a href="%s">SamasaChakram</a> есть таксономия '
            '(4 класса / 10 семейств / 58 подтипов) и 20 разобранных примеров, но '
            'соответствия «заголовок → подтип» нет ни в одном репозитории. Чтобы его '
            'назначить, нужен классификатор по двум членам и их падежному отношению '
            '(татпуруша / кармадхарая / бахуврихи / двандва / авьяибхава) — '
            'отдельная работа, не побочный продукт этого голосования.'
            % KOSHA_WHEEL),
        'approve_label': 'Правило верно',
        'reject_label': 'Правило ломается',
        'reject_labels': REJECT_LABELS,
        # MG point 1: the emitter's filter bar and the facet bar each printed the
        # same seven rule labels, one above the other. The facet bar wins — it is
        # the one labelled «Правило» and it composes with the DCS dimension; the
        # plain filter bar could only ever repeat it. `filters` is a required key
        # in csl-pyutil 0.7.0, so it is emptied rather than dropped (only the
        # automatic "all" / "unvoted only" buttons remain, which are not labels).
        'filters': [],
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
    html, items, suppressed, card_ev = render(sample, columns, deriv,
                                              sizes, quota, len(rows))
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
        html, items, suppressed, card_ev = render(sample, columns, deriv,
                                                  sizes, quota, len(rows))
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
