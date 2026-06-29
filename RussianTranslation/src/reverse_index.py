#!/usr/bin/env python
"""Reverse paradigm index for PWG — the Zaliznyak reverse-dictionary principle.

Streams csl-orig/v02/pwg/pwg.txt (read-only), computes the compact Zaliznyak-style
inflection index (`zaliznyak_index`, see ZALIZNYAK_INDEX.md) for every headword that
carries a <lex> gender/POS tag, and inverts it: index token → all headwords in that
paradigm. This is the foundation for declension display, a "show me every m·8n* noun"
view, and FAIR grammar export.

  python src/reverse_index.py --build              materialize the index + stats
  python src/reverse_index.py --query m·8n*         list headwords with that index
  python src/reverse_index.py --stats [N]           top-N paradigm tokens by frequency

Inputs per entry: <k1> (SLP1 headword), <k2> (accented form → stress slot), first
<lex> in the body (gender/POS). Entries without a <lex> tag (cross-refs, bare verb
forms) are skipped and counted.

Outputs (src/):
  reverse_paradigm_index.json   {token: [headword#hom, ...]}  (sorted)
  paradigm_stats.tsv            token<TAB>count                (desc)
  headword_index.tsv            k1<TAB>hom<TAB>lex<TAB>token   (per headword, FAIR)
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nominal_grammar import zaliznyak_index, _GENDER_POMETA

PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))
IDX_JSON = os.path.join(HERE, 'reverse_paradigm_index.json')
STATS_TSV = os.path.join(HERE, 'paradigm_stats.tsv')
HW_TSV = os.path.join(HERE, 'headword_index.tsv')

_K1 = re.compile(r'<k1>(.*?)<')
_K2 = re.compile(r'<k2>(.*?)(?:<|$)')
_H = re.compile(r'<h>(\d+)')
_LEX = re.compile(r'<lex>(.*?)</lex>')


def entries(path):
    """Yield (k1, k2, hom, lex) per PWG entry. lex = first <lex> tag (or '')."""
    header, body = None, []
    for line in open(path, encoding='utf-8'):
        if line.startswith('<L>'):
            if header is not None:
                yield _emit(header, body)
            header, body = line, []
        else:
            body.append(line)
    if header is not None:
        yield _emit(header, body)


def _emit(header, body):
    m1 = _K1.search(header); k1 = m1.group(1) if m1 else ''
    m2 = _K2.search(header); k2 = m2.group(1) if m2 else ''
    mh = _H.search(header); hom = mh.group(1) if mh else ''
    text = ''.join(body)
    ml = _LEX.search(text); lex = ml.group(1).strip() if ml else ''
    return k1, k2, hom, lex


def build():
    if not os.path.exists(PWG):
        sys.exit('PWG source not found: %s' % PWG)
    index = {}
    rows = []
    n_total = n_indexed = n_nolex = n_unknown_gender = 0
    for k1, k2, hom, lex in entries(PWG):
        if not k1:
            continue
        n_total += 1
        if not lex:
            n_nolex += 1
            continue
        if lex not in _GENDER_POMETA:
            n_unknown_gender += 1
            continue
        token = zaliznyak_index(k1, lex, accented=k2)
        key = '%s#%s' % (k1, hom) if hom else k1
        index.setdefault(token, []).append(key)
        rows.append((k1, hom, lex, token))
        n_indexed += 1

    for t in index:
        index[t].sort()
    json.dump(index, open(IDX_JSON, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    stats = sorted(((len(v), t) for t, v in index.items()), reverse=True)
    with open(STATS_TSV, 'w', encoding='utf-8') as f:
        f.write('index_token\tcount\n')
        for c, t in stats:
            f.write('%s\t%d\n' % (t, c))

    with open(HW_TSV, 'w', encoding='utf-8') as f:
        f.write('k1\thom\tlex\tindex_token\n')
        for k1, hom, lex, t in rows:
            f.write('%s\t%s\t%s\t%s\n' % (k1, hom, lex, t))

    print('PWG entries scanned: %d' % n_total)
    print('  indexed (have <lex>): %d' % n_indexed)
    print('  skipped no <lex>: %d ; unknown gender tag: %d' % (n_nolex, n_unknown_gender))
    print('  distinct paradigm tokens: %d' % len(index))
    print('wrote %s, %s, %s' % (os.path.basename(IDX_JSON),
                                os.path.basename(STATS_TSV), os.path.basename(HW_TSV)))
    print('\nTop 15 paradigms:')
    for c, t in stats[:15]:
        print('  %-10s %6d' % (t, c))


def _load():
    if not os.path.exists(IDX_JSON):
        build()
    return json.load(open(IDX_JSON, encoding='utf-8'))


def query(token):
    hits = _load().get(token, [])
    print('%s — %d headwords' % (token, len(hits)))
    for h in hits[:200]:
        print('  ', h)
    if len(hits) > 200:
        print('  ... (%d more)' % (len(hits) - 200))


def stats(n=30):
    idx = _load()
    rows = sorted(((len(v), t) for t, v in idx.items()), reverse=True)
    total = sum(c for c, _ in rows)
    print('distinct paradigm tokens: %d ; total indexed headwords: %d' % (len(rows), total))
    for c, t in rows[:n]:
        print('  %-10s %6d  (%4.1f%%)' % (t, c, 100.0 * c / total))


def main():
    args = sys.argv[1:]
    if '--build' in args:
        build()
    elif '--query' in args:
        i = args.index('--query')
        if i + 1 < len(args):
            query(args[i + 1])
        else:
            print('Usage: --query <index_token>')
    elif '--stats' in args:
        i = args.index('--stats')
        n = int(args[i + 1]) if i + 1 < len(args) and args[i + 1].isdigit() else 30
        stats(n)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
