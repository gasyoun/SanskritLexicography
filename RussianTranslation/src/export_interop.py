#!/usr/bin/env python
"""Export minimal interoperable release artifacts from assembled cards.

  python export_interop.py tei
  python export_interop.py ontolex
  python export_interop.py reverse-index
  python export_interop.py all --limit 100 --out-dir release/fixture
"""
import argparse
import json
import os
import re
import sys
from xml.sax.saxutils import escape

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_CARDS = os.path.join(HERE, 'assembled_cards.jsonl')
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_RELEASE = os.path.join(ROOT, 'release')
CYR = re.compile(r'[А-Яа-яЁё][А-Яа-яЁё-]{1,}')


def q(s):
    return escape(str(s or ''), {'"': '&quot;'})


def ttl(s):
    return str(s or '').replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')


def safe_id(s):
    return re.sub(r'[^A-Za-z0-9_]+', '_', str(s or 'x')).strip('_') or 'x'


def iter_cards(path, limit=None):
    n = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)
            n += 1
            if limit and n >= limit:
                break


APPROVED_STATUSES = {'approved', 'human_reviewed'}


def approved_store(path, statuses=APPROVED_STATUSES):
    """key1 -> [rows] from the translated store, keeping only rows whose review_status is in
    `statuses` (default the G5-approved set, so unreviewed ai_translated rows stay OUT of the
    citable edition). Pass a wider set (e.g. via --review-status ai_translated) only to preview
    the bridge — never for a published release."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get('review_status') in statuses and r.get('ru'):
                out.setdefault(r.get('key1'), []).append(r)
    return out


def statuses(args):
    raw = getattr(args, 'review_status', None)
    if not raw:
        return APPROVED_STATUSES
    return {s.strip() for s in raw.split(',') if s.strip()}


def card_glosses(card, translations):
    rows = []
    for d in card.get('attested_senses', {}).get('dict') or []:
        if d.get('gloss'):
            rows.append(('dict', d.get('code') or d.get('source') or 'dict', d.get('gloss')))
    for i, s in enumerate(card.get('kow_reference') or [], 1):
        rows.append(('kow', 'kow-%d' % i, s))
    for st in (card.get('corpus_lexicon') or {}).get('strata') or []:
        for r in st.get('renderings') or []:
            if r.get('lemma'):
                rows.append(('corpus_lexicon', st.get('period') or 'corpus', r.get('lemma')))
    for i, r in enumerate(translations.get(card.get('key1'), []), 1):
        rows.append(('approved_translation', 'review-%d' % i, r.get('ru')))
    return rows


def export_tei(args):
    os.makedirs(args.out_dir, exist_ok=True)
    translations = approved_store(args.store, statuses(args))
    out = os.path.join(args.out_dir, 'tei_lex0.xml')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n')
        f.write('  <teiHeader><fileDesc><titleStmt><title>PWG Russian assembled export</title></titleStmt>')
        f.write('<publicationStmt><p>Project release artifact.</p></publicationStmt>')
        f.write('<sourceDesc><p>Generated from assembled_cards.jsonl.</p></sourceDesc></fileDesc></teiHeader>\n')
        f.write('  <text><body>\n')
        for card in iter_cards(args.cards, args.limit):
            cid = 'pwg-%s' % safe_id(card.get('key1'))
            f.write('    <entry xml:id="%s">\n' % q(cid))
            f.write('      <form><orth>%s</orth><pron notation="iast">%s</pron></form>\n'
                    % (q(card.get('key1')), q(card.get('iast'))))
            for source, ref, text in card_glosses(card, translations):
                f.write('      <sense source="%s" n="%s"><def>%s</def></sense>\n'
                        % (q(source), q(ref), q(text)))
            f.write('    </entry>\n')
        f.write('  </body></text>\n</TEI>\n')
    print('TEI Lex-0 export -> %s' % out)


def export_ontolex(args):
    os.makedirs(args.out_dir, exist_ok=True)
    translations = approved_store(args.store, statuses(args))
    out = os.path.join(args.out_dir, 'ontolex.ttl')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write('@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .\n')
        f.write('@prefix lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#> .\n')
        f.write('@prefix pwg: <https://example.org/pwg/ru/> .\n\n')
        for card in iter_cards(args.cards, args.limit):
            sid = safe_id(card.get('key1'))
            f.write('pwg:%s a ontolex:LexicalEntry ;\n' % sid)
            f.write('  ontolex:canonicalForm [ ontolex:writtenRep "%s"@sa-Latn ] ;\n' % ttl(card.get('key1')))
            senses = card_glosses(card, translations)
            if senses:
                refs = ', '.join('pwg:%s_sense_%d' % (sid, i + 1) for i in range(len(senses)))
                f.write('  ontolex:sense %s .\n' % refs)
                for i, (source, ref, text) in enumerate(senses, 1):
                    f.write('pwg:%s_sense_%d a ontolex:LexicalSense ;\n' % (sid, i))
                    f.write('  lexinfo:termElement "%s" ;\n' % ttl(source))
                    f.write('  pwg:sourceRef "%s" ;\n' % ttl(ref))
                    f.write('  ontolex:usage "%s"@ru .\n' % ttl(text))
            else:
                f.write('  ontolex:sense pwg:%s_sense_0 .\n' % sid)
                f.write('pwg:%s_sense_0 a ontolex:LexicalSense .\n' % sid)
            f.write('\n')
    print('OntoLex export -> %s' % out)


def export_reverse_index(args):
    os.makedirs(args.out_dir, exist_ok=True)
    translations = approved_store(args.store, statuses(args))
    out = os.path.join(args.out_dir, 'reverse_index.jsonl')
    count = 0
    with open(out, 'w', encoding='utf-8', newline='') as f:
        for card in iter_cards(args.cards, args.limit):
            seen = set()
            for source, ref, text in card_glosses(card, translations):
                for m in CYR.findall(text or ''):
                    lemma = m.lower().strip('-')
                    if len(lemma) < 2:
                        continue
                    key = (lemma, card.get('key1'), source, ref)
                    if key in seen:
                        continue
                    seen.add(key)
                    f.write(json.dumps({'ru': lemma, 'key1': card.get('key1'),
                                        'iast': card.get('iast'), 'source': source,
                                        'ref': ref}, ensure_ascii=False) + '\n')
                    count += 1
    print('reverse index: %d row(s) -> %s' % (count, out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['tei', 'ontolex', 'reverse-index', 'all'])
    ap.add_argument('--cards', default=DEFAULT_CARDS)
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--out-dir', default=DEFAULT_RELEASE)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--review-status', default=None,
                    help='comma list of review_status values to include; default = approved,human_reviewed (G5 gate). Use ai_translated only to PREVIEW the bridge.')
    args = ap.parse_args()
    if args.mode in ('tei', 'all'):
        export_tei(args)
    if args.mode in ('ontolex', 'all'):
        export_ontolex(args)
    if args.mode in ('reverse-index', 'all'):
        export_reverse_index(args)


if __name__ == '__main__':
    main()
