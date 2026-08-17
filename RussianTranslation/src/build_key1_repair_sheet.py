#!/usr/bin/env python
r"""Build the key1 / wrong-entry-ingestion review sheet (issue #1767).

Renders the proposals from key1_repair_proposals.py into the shared
csl-pyutil review/voting sheet (render_review_sheet - the canonical org
generator, never a hand-rolled shell). One card per proposal; approve =
queue the proposed action (re-ingest + quarantine, or the mechanical key
fix), reject = keep the store as is.

  input  : ../pwg_ru/key1_repair_proposals.jsonl
  output : ../pwg_ru/key1_repair_vote_2026-08-17.html

  python src/build_key1_repair_sheet.py
"""
import html
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from csl_pyutil import render_review_sheet   # noqa: E402
from csl_pyutil.evidence import EvidenceManifest   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GITHUB = os.path.normpath(os.path.join(REPO, '..', '..'))
sys.path.insert(0, os.path.join(GITHUB, 'sanskrit-util', 'py'))
from sanskrit_util import from_slp1, source_text_to_iast   # noqa: E402  (canonical SLP1->IAST)

SRC = os.path.join(REPO, 'pwg_ru', 'key1_repair_proposals.jsonl')
OUT = os.path.join(REPO, 'pwg_ru', 'key1_repair_vote_2026-08-17.html')

CLASS_RU = {
    'wrong_entry_dup': ('дубликация — доказано',
                        'Одна и та же карточка-двойник лежит в сторе НЕСКОЛЬКО раз — под сабкартами разных целевых лемм. Настоящие статьи целевых лемм в сторе отсутствуют.'),
    'wrong_entry': ('чужая статья',
                    'Печатный заголовок карточки совпадает с key1-двойником, а не с целевой леммой сабкарты: инжест взял соседнюю статью по уплощённому ключу.'),
    'junk_key1': ('мусорный key1',
                  'key1 несёт машинерию сабкарты; механическая починка ключа, контент не тронут.'),
}


def _iast(code):
    return from_slp1(code) if re.fullmatch(r'[a-zA-Z]+', code) else code


def build_items(props):
    """Human-facing text is IAST throughout (preflight rule: SLP1 belongs in
    machine ids only; machine forms live in the proposals JSONL)."""
    items = []
    for p in props:
        label, expl = CLASS_RU[p['class']]
        intended = ', '.join(_iast(c) for c in p['intended_lemmas'])
        printed = ', '.join(_iast(c) for c in p['printed_head']) or '—'
        q = ('<b>key1</b> = <i>%s</i> · <b>целевые леммы (subcard)</b> = <i>%s</i> · '
             '<b>печатный заголовок</b> = <i>%s</i> · строк затронуто: %d (%s).<br>%s<br>'
             '<b>Approve</b> = %s. <b>Reject</b> = оставить как есть.') % (
                 html.escape(_iast(p['key1'])), html.escape(intended),
                 html.escape(printed),
                 p['rows_affected'], ', '.join(p['layers']),
                 expl, html.escape(p['action']))
        items.append({
            'id': p['id'],
            'filt': p['class'],
            'title': '%s → %s [%s]' % (_iast(p['key1']), intended, label),
            'badges': [label, '%d строк' % p['rows_affected']],
            'question': q,
            'panels': [('Первая строка карточки (de, IAST)',
                        '<code>%s</code>' % html.escape(
                            source_text_to_iast(p['sample_de'], 'pwg')))],
        })
    return items


def main():
    props = [json.loads(l) for l in open(SRC, encoding='utf-8') if l.strip()]
    items = build_items(props)
    # V13: the only machine ids a question could mention are the k1r-### row
    # ids; lemmas are rendered as IAST (their real-world identity) directly.
    identity_gate = {'patterns': [r'\bk1r-\d{3}\b'], 'labels': {}}
    config = {
        'sheet_id': 'key1-repair-2026-08-17',
        'title': 'pwg_ru: чужие статьи под целевыми леммами (issue #1767)',
        'subtitle': ('56 предложений по 161 строке стора: инжест по уплощённому ключу брал '
                     'статью-двойника вместо целевой леммы (FINDINGS §560/§561). '
                     'Approve = переингест целевой леммы + карантин строк-двойников.'),
        'footer': ('Источник: RussianTranslation/pwg_ru/key1_repair_proposals.jsonl · '
                   'генератор build_key1_repair_sheet.py · стор не тронут (read-only).'),
        'approve_label': 'Переингест',
        'reject_label': 'Оставить',
        'filters': [('wrong_entry_dup', 'дубликация'),
                    ('wrong_entry', 'чужая статья'),
                    ('junk_key1', 'мусорный key1')],
        'generated': '17-08-2026',
        'identity_gate': identity_gate,
        # German source-quote words the SLP1 detector false-positives on
        # (plain German, not transliteration): reviewed one by one.
        'preflight': {'allow_slp1_tokens': ('Opfer', 'Verz', 'anzuziehen', 'salziger')},
    }
    screening = {
        'deterministic': 205,   # card-groups auto-cleared: witnesses agree (188) or
                                # printed head covers the variant on one card (17)
        'lookup': 0,
        'agent': 0,
        'human': len(items),
        'evidence_path': 'RussianTranslation/pwg_ru/key1_repair_proposals.jsonl',
        'rules': [
            'key1 vs subcard-декод vs iast (sanskrit_util.to_slp1) vs печатный заголовок {#lemma#}¦',
            'дубликация доказывается побайтово одинаковым контентом под разными сабкартами',
            'группы, где все свидетели согласны, в лист не попадают',
        ],
    }
    manifest = EvidenceManifest('key1-repair-2026-08-17', [p['id'] for p in props],
                                repo_root=REPO)
    manifest.declare_joined('pwg_ru/key1_repair_proposals.jsonl',
                            ['key1', 'intended_lemmas', 'printed_head', 'rows_affected',
                             'sample_de', 'class', 'action'])
    manifest.declare_omitted(
        'src/pwg_ru_translated.jsonl (canonical store, not in git)',
        'read-only source; every witness these cards show was already extracted '
        'into key1_repair_proposals.jsonl by key1_repair_proposals.py')
    manifest.declare_omitted_path(
        'pwg_ru/mw_ap_sense_coverage.jsonl',
        'keyed on MW/AP sense units, not on k1r ids; wave-4 context only')
    for p in props:
        manifest.add_card(p['id'], ['key1', 'intended_lemmas', 'printed_head',
                                    'rows_affected', 'sample_de'])
    doc = render_review_sheet(items, config, screening=screening, manifest=manifest)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)
    print('cards:', len(items), '->', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
