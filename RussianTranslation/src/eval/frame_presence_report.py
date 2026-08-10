#!/usr/bin/env python
"""frame_presence_report.py — per-stratum corpus_lexicon presence for a gold frame.

The protocol must state, BEFORE annotation is paid for, how much P@1 signal each
stratum can yield: a lemma absent from `corpus_lexicon.jsonl` contributes to
coverage but to no retrieval metric, so a cell with near-zero presence buys nothing
for P@1 no matter how carefully it is annotated. This streams the 290 MB lexicon
once (never loads it whole, per the bli_eval.py contract) and reports presence per
(band x POS) cell of the frame.

Usage:
  python frame_presence_report.py --frame <frame.tsv> --lexicon <corpus_lexicon.jsonl>
  python frame_presence_report.py selftest
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_gold_strata import lexicon_presence  # noqa: E402


def load_frame(path):
    rows, columns = [], None
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#'):
                continue
            if columns is None:
                columns = line.split('\t')
                continue
            if line.strip():
                rows.append(dict(zip(columns, line.split('\t'))))
    return rows


def report(frame_rows, lexicon_path):
    wanted = {r['slp1'] for r in frame_rows}
    present = lexicon_presence(lexicon_path, wanted)

    total = collections.Counter()
    hit = collections.Counter()
    for r in frame_rows:
        cell = (int(r['band']), r['pos'])
        total[cell] += 1
        if r['slp1'] in present:
            hit[cell] += 1

    lines = []
    overall = len(present) / len(wanted) if wanted else 0
    lines.append(f'frame lemmas: {len(wanted)}; present in lexicon: {len(present)} '
                 f'({overall:.1%})')
    lines.append(f'{"band":>4} {"pos":<6} {"n":>4} {"present":>8} {"rate":>7}')
    for cell in sorted(total, key=lambda c: (-c[0], c[1])):
        rate = hit[cell] / total[cell]
        lines.append(f'{cell[0]:>4} {cell[1]:<6} {total[cell]:>4} '
                     f'{hit[cell]:>8} {rate:>7.2f}')

    thin = [c for c in total if hit[c] / total[c] < 0.25]
    if thin:
        lines.append('cells under 25% presence (annotation buys coverage, not P@1 — '
                     'report separately): ' +
                     ', '.join(f'band{c[0]} {c[1]}' for c in sorted(thin)))
    return lines, {'present': len(present), 'total': len(wanted)}


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp()
    fp = os.path.join(tmp, 'frame.tsv')
    lp = os.path.join(tmp, 'lex.jsonl')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write('# header\nslp1\tband\tpos\tpolysemy\tn_senses\tkoch_gloss\n')
        f.write('gaja\t5\tNOUN\t1\t1\tслон\n')
        f.write('nara\t5\tNOUN\t1\t1\tчеловек\n')
        f.write('rare\t1\tVERB\t1\t1\tредкий\n')
    with open(lp, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'slp1': 'gaja', 'ru': 'слон'}, ensure_ascii=False) + '\n')

    lines, stats = report(load_frame(fp), lp)
    ok = stats == {'present': 1, 'total': 3} and any('band1 VERB' in l for l in lines)
    print('\n'.join(lines))
    print('\nSELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('--frame', required=True)
    ap.add_argument('--lexicon', required=True)
    args = ap.parse_args()
    lines, _ = report(load_frame(args.frame), args.lexicon)
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
