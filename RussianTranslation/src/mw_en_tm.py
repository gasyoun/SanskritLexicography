#!/usr/bin/env python
r"""Build the Monier-Williams English translation-memory feed for the PWG->EN pilot.

MW is partly a descendant of PW/PWG (Böhtlingk-Roth), so its English glosses overlap
PWG's German senses heavily. This extractor reads the read-only csl-orig MW source
(NEVER modified) and emits, per SLP1 headword, MW's English gloss prose with the
Sanskrit / sigla / abbreviation markup stripped — the candidate vocabulary the EN
harness injects as translation memory (the LLM adjudicates each candidate against PWG's
German + corpus, per MG's hybrid choice).

  source : csl-orig/v02/mw/mw.txt  (Cologne digitisation; <k1> is already SLP1)
  output : src/mw_en_tm.json  { slp1_headword: "english gloss; english gloss; ..." }

  python src/mw_en_tm.py                 # build for all MW headwords
  python src/mw_en_tm.py --keys vad,pA   # preview a few
  python src/mw_en_tm.py --selftest
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MW = os.environ.get('MW_TXT', os.path.normpath(os.path.join(REPO, '..', '..', 'csl-orig', 'v02', 'mw', 'mw.txt')))
OUT = os.path.join(HERE, 'mw_en_tm.json')
CAP = 700                                   # max chars of MW gloss per headword (prompt budget)

_K1 = re.compile(r'<k1>(.*?)<')
_PAIRED = re.compile(r'<(s|ls|ab|lang|etym|lex)>.*?</\1>', re.S)   # drop Sanskrit/sigla/abbrev/lang/etym/grammar
_SELF = re.compile(r'<[^>]+/>')                                    # <div n=../>, <pb/>, <srs/>
_TAG = re.compile(r'</?[^>]+>')                                    # any residual tag
_ETYMBR = re.compile(r'\[[^\]]*\]')                               # [cf. Lit. ...] etymology brackets


def clean_body(body):
    """MW record body -> plain English gloss prose (Sanskrit/sigla/markup removed)."""
    t = _PAIRED.sub(' ', body)
    t = _SELF.sub(' ', t)
    t = _ETYMBR.sub(' ', t)
    t = _TAG.sub(' ', t)
    t = t.replace('¦', ' ')
    t = re.sub(r'[ \t]*\n[ \t]*', ' ', t)
    # the stripped Sanskrit paradigm leaves empty parens + orphan punctuation: clean it
    for _ in range(3):
        t = re.sub(r'\([\s;,.&c]*\)', ' ', t)          # empty/near-empty parentheticals
    t = re.sub(r'\s*([;,])(\s*[;,])+', r'\1 ', t)      # collapse punctuation runs
    t = re.sub(r'\s*&c\.(\s*&c\.)+', ' &c.', t)         # collapse '&c. &c. &c.'
    t = re.sub(r'^[\s\d.;,()]+', '', t)                 # leading numbering/paradigm junk
    t = re.sub(r'\s{2,}', ' ', t).strip(' ;,.|')
    return t


def records(path):
    """Yield (k1, body) for each <L>...<LEND> MW record."""
    with open(path, encoding='utf-8') as f:
        buf, k1 = [], None
        for line in f:
            if line.startswith('<L>'):
                m = _K1.search(line)
                k1 = m.group(1) if m else None
                buf = []
            elif line.startswith('<LEND>'):
                if k1:
                    yield k1, ''.join(buf)
                k1, buf = None, []
            elif k1 is not None:
                buf.append(line)


def build(path):
    by = {}
    for k1, body in records(path):
        gloss = clean_body(body)
        if not gloss:
            continue
        prev = by.get(k1)
        by[k1] = (prev + ' | ' + gloss) if prev else gloss
    # cap length per headword to keep the injected TM cheap
    for k in by:
        if len(by[k]) > CAP:
            by[k] = by[k][:CAP].rsplit(' ', 1)[0] + ' …'
    return by


def slp1_simplify(key: str) -> str:
    """Reduce a standard SLP1 string to a simplified no-diacritic ASCII form.

    Works for both MW headword keys and indic_transliteration output — both use
    standard SLP1 where R=ṇ (retroflex nasal). Self-contained copy of
    sanskrit_util.slp1_simplify so this module works standalone.

    ⚠️ R=ṇ trap: guṇa is 'guRa' in MW, NOT 'guNa'. Missing R→n maps guṇa to
    gūna ("voided as ordure"). This function handles it.
    """
    s = key or ''
    s = (s.replace('K', 'kh').replace('G', 'gh')
          .replace('C', 'ch').replace('J', 'jh')
          .replace('T', 'th').replace('D', 'dh')
          .replace('P', 'ph').replace('B', 'bh'))
    s = s.replace('S', 's').replace('z', 's')
    s = s.replace('Y', 'n').replace('N', 'n').replace('R', 'n')
    s = s.replace('A', 'a').replace('I', 'i').replace('U', 'u')
    s = s.replace('E', 'ai').replace('O', 'au')
    s = s.replace('f', 'r').replace('F', 'r').replace('x', 'l').replace('X', 'l')
    s = s.replace('M', 'm').replace('H', '')
    s = s.replace('W', 'th').replace('Q', 'dh')
    s = s.replace('w', 't').replace('q', 'd')
    s = s.replace('L', 'l')
    return s.lower()


def build_simplified_index(mw_data: dict) -> dict:
    """Build a {simplified_form: [slp1_keys]} index for fuzzy MW headword lookup.

    Use slp1_simplify() on query tokens to look up in this index — same
    simplification on both sides ensures consistent matching.

    Example::

        mw_data = json.loads(Path('mw_en_tm.json').read_text(encoding='utf-8'))
        idx = build_simplified_index(mw_data)
        hits = idx.get(slp1_simplify(query_token), [])
    """
    idx: dict = {}
    for k in mw_data:
        s = slp1_simplify(k)
        idx.setdefault(s, []).append(k)
    return idx


def selftest():
    body = ('<s>vad</s> ¦ <ab>cl.</ab> 1. <ab>P.</ab> (<ls>Dhātup.</ls> <s>va/dati</s>)\n'
            '<div n="to"/>to speak, say, utter, tell, <ls>RV.</ls>;\n'
            '<div n="to"/> (<ab>P.</ab>) to praise, recommend, <ls>MBh.</ls>;')
    g = clean_body(body)
    assert 'to speak, say, utter, tell' in g, g
    assert 'vad' not in g and 'Dhātup' not in g and '<' not in g, g
    assert 'cl.' not in g, g
    print('mw_en_tm selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mw', default=MW)
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--keys', default='')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not os.path.exists(args.mw):
        sys.exit('MW source not found: %s' % args.mw)
    by = build(args.mw)
    if args.keys:
        for k in args.keys.split(','):
            print('%s -> %s' % (k, by.get(k.strip(), '(no MW entry)')))
        return
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(by, f, ensure_ascii=False)
    print('wrote %s (%d MW headwords with English gloss)' % (args.out, len(by)))


if __name__ == '__main__':
    main()
