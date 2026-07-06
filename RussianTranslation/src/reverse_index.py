#!/usr/bin/env python
"""Reverse paradigm index for PWG — the Zaliznyak reverse-dictionary principle.

Streams csl-orig/v02/pwg/pwg.txt (read-only), computes the compact Zaliznyak-style
inflection index (`zaliznyak_index`, see ZALIZNYAK_INDEX.md) for every headword that
carries a <lex> gender/POS tag, and inverts it: index token → all headwords in that
paradigm. This is the foundation for declension display, a "show me every m·8n* noun"
view, and FAIR grammar export.

  python src/reverse_index.py --build              materialize the index + stats
  python src/reverse_index.py --query m·8n*         list headwords with that index
  python src/reverse_index.py --show m·8n*          render the paradigm template (vidyut)
  python src/reverse_index.py --stats [N]           top-N paradigm tokens by frequency

Inputs per entry: <k1> (SLP1 headword), <k2> (accented form → stress slot), first
<lex> in the body (gender/POS). Entries without a <lex> tag (cross-refs, bare verb
forms) are skipped and counted.

Outputs (src/):
  reverse_paradigm_index.json   {token: [headword#hom, ...]}  (sorted)
  paradigm_stats.tsv            token<TAB>count                (desc)
  headword_index.tsv            the per-word structured-grammar dataset (FAIR TSV):
                                k1·hom·lex·accented·index_token·stem_class·compound_members·irregularities

This grammar data is recorded PER WORD as a standalone structured-data asset. It is
DELIBERATELY NOT injected into translation: the nominal-grammar A/B (NOMINAL_GRAMMAR_AB.md)
showed grammar-ON does not improve DE→RU and sometimes mildly hurts it, so the portraits
(which the translation harness inlines) are left untouched and nominal windows run grammar OFF.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nominal_grammar import (zaliznyak_index, nominal_grammar_for, _GENDER_POMETA,
                             paradigm_for, render_paradigm)

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
        # full grammar block once per word (the structured-data record; NOT injected
        # into translation — the A/B rejected that. Portraits are deliberately left alone).
        # §§/paradigm_section are omitted from the row (fully derivable from stem_class via
        # nominal_grammar._STEM_SECTIONS) to keep the per-word table compact.
        g = nominal_grammar_for(k1, lex, accented=k2)
        token = g['zaliznyak_index']
        key = '%s#%s' % (k1, hom) if hom else k1
        index.setdefault(token, []).append(key)
        rows.append((k1, hom, lex, k2 or '', token, g['stem_class'],
                     '+'.join(g['compound_members']) if g['compound_members'] else '',
                     ';'.join(g['irregularities'])))
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

    # The per-word structured-grammar dataset (compact FAIR TSV; §§ derivable from stem_class).
    with open(HW_TSV, 'w', encoding='utf-8') as f:
        f.write('k1\thom\tlex\taccented\tindex_token\tstem_class\tcompound_members\tirregularities\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')

    print('PWG entries scanned: %d' % n_total)
    print('  indexed (have <lex>): %d' % n_indexed)
    print('  skipped no <lex>: %d ; unknown gender tag: %d' % (n_nolex, n_unknown_gender))
    print('  distinct paradigm tokens: %d' % len(index))
    print('wrote %s, %s, %s' % (os.path.basename(IDX_JSON), os.path.basename(STATS_TSV),
                                os.path.basename(HW_TSV)))
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


def _representative(token):
    """First (k1, lex) headword carrying `token`, from headword_index.tsv (built on demand)."""
    if not os.path.exists(HW_TSV):
        build()
    for i, line in enumerate(open(HW_TSV, encoding='utf-8')):
        parts = line.rstrip('\n').split('\t')
        if i == 0:
            continue
        if len(parts) >= 5 and parts[4] == token:
            return parts[0], parts[2]            # k1, lex
    return None, None


def show(token):
    """Render the shared declension TEMPLATE for a paradigm token (Zaliznyak's
    «Грамматические сведения»): a representative member's vidyut paradigm + the
    member count and a few example headwords."""
    members = _load().get(token, [])
    if not members:
        print('no headwords with index %s' % token)
        return
    k1, lex = _representative(token)
    print('=== paradigm %s — %d headwords ===' % (token, len(members)))
    print('representative: %s [%s]\n' % (k1, lex))
    print(render_paradigm(paradigm_for(k1, lex)))
    print('\nexamples:', ', '.join(members[:12]) + (' …' if len(members) > 12 else ''))


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
    elif '--show' in args:
        i = args.index('--show')
        if i + 1 < len(args):
            show(args[i + 1])
        else:
            print('Usage: --show <index_token>   (renders the paradigm template)')
    elif '--stats' in args:
        i = args.index('--stats')
        n = int(args[i + 1]) if i + 1 < len(args) and args[i + 1].isdigit() else 30
        stats(n)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
