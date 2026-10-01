#!/usr/bin/env python
"""build_h5262_nkrya_flag_sheet.py — NKRYa-flagged PWG-RU gloss words as ≤10-card vote sheets.

H5262 audits every content word of the PWG-RU store's Russian glosses against NKRYa
frequency (h5262_ipm_audit.py). A flagged lemma is ABSENT from the corpus, RARE (ipm < 1)
or ARCHAIC (the 1800–1899 slice holds at least half its usages). Ruling (grill
22-09-2026): flags become corrections-style rows with NKRYa evidence, voted on sheets of
at most 10 cards; nothing is auto-applied.

One card = one flagged lemma. Approve = the word is a gloss defect: open a correction row
for the cards shown (an agent drafts the replacement, a human approves it separately).
Reject = keep the word; the reject select names why, because each reason trains the
next pass differently (a legitimate Indological term, an intended archaism, an NKRYa
tokenizer miss).

  python src/build_h5262_nkrya_flag_sheet.py --batch 1
      [--flags reports/H5262_flags.json] [--context reports/H5262_flag_context.json]
  python src/build_h5262_nkrya_flag_sheet.py --all      # every batch not yet built

H5262 · Opus 5.5 (claude-opus-5-5) · 24-09-2026
H5468 · Opus 4.8 (claude-opus-4-8) · 25-09-2026 — append-only batch assignment
"""
import argparse
import datetime
import html
import io
import json
import os
import re
import sys

from csl_pyutil import render_review_sheet
from csl_pyutil.evidence import EvidenceManifest
from sheet_screening import screening_block
from review_binding import stamp, write_lock
from review_sheet_standard import slp1_iast, standard_config

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FLAGS = os.path.join(REPO, 'reports', 'H5262_flags.json')
CONTEXT = os.path.join(REPO, 'reports', 'H5262_flag_context.json')
ASSIGNMENTS = os.path.join(REPO, 'reports', 'H5262_sheet_assignments.json')
PER_SHEET = 10
# Sheet 1 was built on 24-09; every later sheet carries the day it was built, because the
# NKRYa drain keeps adding flags and a sheet_id must stay unique per batch (H5468).
GENERATED = '2026-09-24'

CLASS_RU = {
    'ABSENT': 'нет в НКРЯ',
    'RARE': 'очень редкое (ipm < 1)',
    'ARCHAIC': 'архаизм (≥ половины употреблений в 1800–1899)',
}
BASIS_RU = {
    'portrait': 'частотный портрет НКРЯ',
    'hits': 'число вхождений леммы в основном корпусе',
    'form': 'число вхождений словоформы (лемма НКРЯ не распознаёт)',
    'none': '—',
}
REJECT_LABELS = [
    ('term', 'Оставить: законный индологический термин / реалия'),
    ('archaism', 'Оставить: намеренная архаизация, стиль словаря'),
    ('artifact', 'Ложный флаг: ошибка лемматизации или токенизации'),
]


BRACED_SLP1 = re.compile(r'\{#(.*?)#\}', re.S)
TAG = re.compile(r'<[^>]*>')


def esc(s):
    return html.escape('' if s is None else str(s))


def human(s):
    """Card text for a reader: {#SLP1#} -> IAST, apparatus tags dropped."""
    s = BRACED_SLP1.sub(lambda m: slp1_iast(m.group(1)), s or '')
    return ' '.join(TAG.sub(' ', s).split())


def _num(v, nd=3):
    if v is None:
        return '—'
    if isinstance(v, float):
        return ('%.' + str(nd) + 'f') % v
    return '{:,}'.format(v).replace(',', ' ')


def evidence_panel(r):
    rows = [
        ('Класс', ' + '.join(CLASS_RU.get(c, c) for c in r['classes'])),
        ('ipm (на миллион словоупотреблений)', _num(r.get('ipm'))),
        ('Основание ipm', BASIS_RU.get(r.get('ipm_basis') or 'none', r.get('ipm_basis'))),
        ('Категория частотности НКРЯ (1–6)', _num(r.get('category'))),
        ('Вхождений леммы, основной корпус (426 млн слов)', _num(r.get('hits_main'))),
        ('Вхождений, срез 1800–1899 (82 млн слов)', _num(r.get('hits_19c'))),
    ]
    if r.get('form'):
        rows.append(('Проверена словоформа «%s», вхождений' % r['form'],
                     _num(r.get('form_hits_main'))))
    rows.append(('Употреблений в сторе / карточек', '%d / %d'
                 % (r['occurrences'], len(r.get('cards') or []))))
    return ('<table style="border-collapse:collapse">%s</table>'
            % ''.join('<tr><td class="muted" style="padding:2px 10px 2px 0">%s</td>'
                      '<td><b>%s</b></td></tr>' % (esc(k), esc(v)) for k, v in rows))


def cards_panel(ctx_cards):
    if not ctx_cards:
        return '<div class="muted">Контекст карточек не извлечён.</div>'
    items = []
    for c in ctx_cards:
        spans = ' · '.join('<span class="ru">%s</span>' % esc(human(s)) for s in c['ru_spans'])
        items.append(
            '<li style="margin-bottom:8px"><b>%s</b> <span class="muted">(%s, %s)</span>'
            '<div>RU: %s</div><div class="muted">DE (PWG): %s</div></li>'
            # The store carries `iast` for almost every card; where it is missing the
            # fallback must still be transliterated, never raw SLP1 (H5468: «viS» on the
            # one context card without an `iast`, which the preflight reads as a leak).
            % (esc(c.get('iast') or slp1_iast(c.get('key1') or '')), esc(c['subcard']),
               esc(c.get('review_status') or '—'), spans,
               esc(' · '.join(human(g) for g in c.get('de_gloss') or []) or '—')))
    return '<ul style="margin:0;padding-left:18px">%s</ul>' % ''.join(items)


def build_item(r, ctx_cards):
    lid = 'L-' + r['lemma']
    question = (
        '<b>«%s»</b> (%s) — %s'
        '<div style="margin-top:8px">Одобрить = <b>слово — дефект глоссы: открыть строку '
        'исправления для карточек ниже</b> (агент предложит замену, её утверждают отдельно).'
        '</div><div class="muted" style="margin-top:6px;font-weight:normal">Отклонить = '
        'оставить слово; в списке причин укажите, почему.</div>'
        % (esc(r['lemma']), esc(r['pos']), esc(' + '.join(CLASS_RU.get(c, c)
                                                          for c in r['classes']))))
    return {
        'id': lid,
        'filt': r['classes'][0].lower(),
        'title': r['lemma'],
        'badges': r['classes'] + ['ipm %s' % _num(r.get('ipm'))],
        'question': question,
        'panels': [
            ('Данные НКРЯ (ruscorpora.ru API, 24-09-2026)', evidence_panel(r)),
            ('Карточки PWG-RU с этим словом', cards_panel(ctx_cards)),
        ],
    }


def german_tokens(ctx, rows):
    """Words of PWG's German {%...%} meaning spans that the SLP1 detector misreads.

    `z` is an SLP1 letter, so German «ganz», «setzen», «zwingen» trip it. Only tokens
    from the German spans shown on these cards are allowed — never from the Sanskrit,
    which is rendered to IAST before the check runs.
    """
    from csl_pyutil.evidence import find_slp1
    text = ' '.join(g for r in rows for c in ctx.get(r['lemma']) or []
                    for g in c.get('de_gloss') or [])
    return tuple(sorted(set(find_slp1(human(text)))))


ASSIGN_NOTE = (
    'Append-only lemma -> sheet batch. The NKRYa drain (h5262_ipm_audit.py query) keeps '
    'adding verdicts, and every new flag is inserted into H5262_flags.json in severity '
    'order — so slicing that list by position renumbers sheets that are ALREADY '
    'published. H5468 hit exactly that: at 64 verdicts batch 1 ended on «кусывать», at '
    '345 verdicts the same slice ends on «приформовывать», which would have silently '
    'dropped a card off the published sheet 1 and duplicated another onto it. This ledger '
    'freezes the mapping instead: a lemma already assigned NEVER moves, and new flags '
    'only ever open batches after the highest one that exists.')


def load_assignments(path=ASSIGNMENTS):
    if os.path.exists(path):
        with io.open(path, encoding='utf-8') as fh:
            return json.load(fh)
    return {'handoff': 'H5468', 'per_sheet': PER_SHEET, 'note': ASSIGN_NOTE,
            'assigned': {}}


def assign(flags, doc, per_sheet=PER_SHEET):
    """Give every unassigned flag a batch, without touching an existing assignment.

    Batches are sealed on creation: a sheet prepared for the vote hub is a fixed set of
    cards, so a later drain pass may not backfill its free slots. New flags therefore
    start at `max(existing) + 1`, even when the last batch is short.
    """
    assigned = doc.setdefault('assigned', {})
    first_new = max(assigned.values()) + 1 if assigned else 1
    fresh = [r['lemma'] for r in flags['flagged'] if r['lemma'] not in assigned]
    for i, lemma in enumerate(fresh):
        assigned[lemma] = first_new + i // per_sheet
    doc['per_sheet'] = per_sheet
    doc['note'] = ASSIGN_NOTE
    doc['lemmas_assigned'] = len(assigned)
    doc['batches'] = max(assigned.values()) if assigned else 0
    # A lemma can LEAVE the flag list: H5468's precision filters retire measurement
    # artifacts the earlier pass flagged. Its sheet keeps the assignment (the card must
    # never reappear on a later sheet), but the retirement is recorded, because a sheet
    # already prepared for the hub is now carrying a card its own audit withdrew.
    live = {r['lemma'] for r in flags['flagged']}
    doc['retired'] = {lemma: batch for lemma, batch in sorted(assigned.items())
                      if lemma not in live}
    doc['retired_note'] = (
        'Assigned to a sheet by an earlier pass, no longer flagged after the H5468 '
        'precision filters. Still listed so it can never be re-assigned; a sheet already '
        'published needs a human decision on whether to re-cut it.')
    return doc, fresh


def save_assignments(doc, path=ASSIGNMENTS):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write('\n')


def select(flags, batch, assigned=None):
    """The flagged rows on one sheet — by frozen assignment when the ledger exists."""
    if assigned:
        return [r for r in flags['flagged'] if assigned.get(r['lemma']) == batch]
    rows = [r for r in flags['flagged']]
    lo = (batch - 1) * PER_SHEET
    return rows[lo:lo + PER_SHEET]


def subcard_tokens(ctx, rows):
    """SLP1 heads of the store ids shown on this sheet.

    A card is labelled with its IAST headword and, in parentheses, its store subcard id
    («rakṣ (rakz~~h0_03_sec_3)»). The id half is SLP1 by construction — it is the store's
    key — and the preflight's SLP1-in-human-text rule reads it as a transliteration leak
    (H5468: batch 3 died on «rakz»). Only the ids actually rendered on this sheet are
    allowed, so a real leak anywhere else still blocks.
    """
    from csl_pyutil.evidence import find_slp1
    ids = ' '.join((c.get('subcard') or '').split('~~')[0]
                   for r in rows for c in ctx.get(r['lemma']) or [])
    return tuple(sorted(set(find_slp1(ids))))


def sealed(batch, review_dir=None):
    """True when this batch already has a review-binding lock, whatever date it carries."""
    import glob
    pattern = os.path.join(review_dir or os.path.join(REPO, 'review', 'locks'),
                           'h5262-nkrya-flags-b%02d-*.lock.json' % batch)
    return bool(glob.glob(pattern))


def build_sheet(rows, ctx, batch, generated=GENERATED, out=None):
    sheet_id = 'h5262-nkrya-flags-b%02d-%s' % (batch, generated)
    out_path = out or os.path.join(
        REPO, 'review', 'sanskritlexicography-h5262-nkrya-flags-b%02d_%d.html'
        % (batch, len(rows)))
    items = [build_item(r, ctx.get(r['lemma']) or []) for r in rows]

    manifest = EvidenceManifest(sheet_id, [it['id'] for it in items],
                                repo_root=os.path.dirname(REPO))
    manifest.declare_joined(
        'RussianTranslation/reports/H5262_flags.json',
        ['classes', 'ipm', 'category', 'ipm_basis', 'hits_main', 'hits_19c',
         'form_hits_main', 'occurrences', 'cards', 'severity'])
    manifest.declare_joined(
        'RussianTranslation/reports/H5262_flag_context.json',
        ['subcard', 'key1', 'iast', 'review_status', 'ru_spans', 'de'])
    manifest.declare_omitted(
        'NKRYa concordance lines',
        'The counts are shown; example sentences from the corpus are left out of a public '
        'sheet (third-party copyrighted texts). They are one API call away in /nkrya.')
    manifest.declare_omitted(
        'a proposed replacement word',
        'This sheet decides only whether the word is a defect. A replacement is drafted '
        'afterwards for approved rows and voted separately — never auto-applied.')

    config = {
        'sheet_id': sheet_id,
        'title': 'НКРЯ-аудит глосс PWG-RU (H5262), лист %d: редкие и отсутствующие слова'
                 % batch,
        'subtitle': ('Каждое содержательное слово русских глосс PWG-RU сверено с частотой в '
                     'Национальном корпусе русского языка. Здесь — слова, которых в корпусе '
                     'нет, которые очень редки (меньше 1 на миллион) или живут в основном в '
                     'XIX веке. Решите по каждому: дефект глоссы или законное слово.'),
        'footer': ('Одобрить = открыть строку исправления (замену предложит агент, утвердите '
                   'отдельно). Отклонить = оставить слово, причина — в списке. Ничего не '
                   'применяется автоматически; стор не меняется этим листом.'),
        'approve_label': 'Дефект — исправлять',
        'reject_label': 'Оставить',
        'reject_labels': REJECT_LABELS,
        'filters': [('absent', 'нет в НКРЯ'), ('rare', 'очень редкие'),
                    ('archaic', 'архаизмы')],
        'generated': generated,
        # English words the SLP1 detector reads as transliteration (F/Y/R/z are SLP1).
        'preflight': {'allow_slp1_tokens': ('NKRYa', 'surface')
                      + german_tokens(ctx, rows) + subcard_tokens(ctx, rows)},
        # V13: the only id a question names is the «quoted» gloss word, which is its own
        # real-world identity — a Russian word, glossed with its class right beside it.
        'identity_gate': {
            'patterns': [r'(?<=«)[^»]+(?=»)'],
            'labels': {r['lemma']: r['lemma']
                       for r in rows},
        },
    }
    config.update(standard_config(
        save_as='RussianTranslation\\review\\%s_decisions.json' % sheet_id))

    doc = render_review_sheet(
        items, config, extras=True, manifest=manifest,
        screening=screening_block(
            deterministic=0, lookup=0, agent=0, human=len(items),
            evidence_path='RussianTranslation/docs/H5262_NKRYA_STORE_IPM_CENSUS_24-09-2026.md',
            rules=['Hyphenated compounds with zero hits are held back as unverifiable '
                   '(NKRYa splits them into separate tokens), never shown as absent.',
                   'A lemma NKRYa has no portrait for is judged by its concordance hits, '
                   'then by its surface form, before it may be called absent.']))
    doc, chash = stamp(doc)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(doc)
    write_lock(sheet_id, chash, [it['id'] for it in items], generated, source_html=out_path)
    print('wrote %d cards -> %s (sheet_id %s)' % (len(items), out_path, sheet_id))
    return sheet_id, out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--batch', type=int, default=1)
    ap.add_argument('--all', action='store_true',
                    help='build every assigned batch whose sheet is not on disk yet')
    ap.add_argument('--flags', default=FLAGS)
    ap.add_argument('--context', default=CONTEXT)
    ap.add_argument('--assignments', default=ASSIGNMENTS)
    ap.add_argument('--generated', default=None,
                    help='sheet date (default: today UTC; sheet 1 is %s)' % GENERATED)
    ap.add_argument('--out')
    a = ap.parse_args(argv)

    with io.open(a.flags, encoding='utf-8') as fh:
        flags = json.load(fh)
    ctx = {}
    if os.path.exists(a.context):
        with io.open(a.context, encoding='utf-8') as fh:
            ctx = json.load(fh)

    doc = load_assignments(a.assignments)
    doc, fresh = assign(flags, doc)
    save_assignments(doc, a.assignments)
    assigned = doc['assigned']
    if fresh:
        print('assigned %d new flag(s); %d lemmas over %d batch(es)'
              % (len(fresh), len(assigned), doc['batches']))

    generated = a.generated or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    batches = sorted(set(assigned.values())) if a.all else [a.batch]
    built = []
    for batch in batches:
        rows = select(flags, batch, assigned)
        if not rows:
            if a.all:
                continue
            raise SystemExit('batch %d is empty (%d flagged lemmas)'
                             % (batch, len(flags['flagged'])))
        # A built sheet leaves a review-binding lock. In --all mode that lock is the seal:
        # rebuilding it under today's date would mint a second sheet_id for cards a human
        # may already be voting on.
        if a.all and sealed(batch):
            print('batch %d already built (lock present) — left alone' % batch)
            continue
        built.append(build_sheet(rows, ctx, batch, generated, a.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
