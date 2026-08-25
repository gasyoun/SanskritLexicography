#!/usr/bin/env python
"""check_wsd_frame.py — verify a sampled C1 WSD frame is well-formed.

Run this on any frame before it goes to annotation, exactly as check_gold_frame.py
gates the BLI frame. It asserts the properties the protocol claims, so a
regenerated frame cannot silently drift from its design:

  1. no label column leaked in (the H070 rule-based-arm trap);
  2. no duplicate token (occ_id), and no two rows sharing a sentence — rows sharing
     a context are not independent judgments and inflate apparent agreement;
  3. the per-lemma cap held, so no single frequent lemma became the band;
  4. every row is actually answerable: a non-empty sentence, and a sense menu with
     >= 2 options whose count matches n_senses;
  5. every menu offers >= 2 options that can actually be TOLD APART. Two senses
     whose glosses are textually identical ("[1] раздувание, вздутие" vs
     "[PW] раздувание, вздутие") are not a choice — annotators pick between them at
     random, and the kappa that results measures coin-flips. The live store really
     does contain these, via cross-layer duplicate subcards; this gate is what
     stops them reaching a reviewer.
  6. reports the band and UPOS spread, which are OBSERVED byproducts of the draw,
     not controlled axes — the protocol must not claim balance it does not have.

Usage: python check_wsd_frame.py <frame.tsv> [--max-per-lemma 6]
       python check_wsd_frame.py selftest
"""
import argparse
import collections
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BANNED_COLUMNS = ('gold', 'label', 'sense_gold', 'gold_tag', 'verdict', 'ruling')
SENSE_SEP = ' ‖ '
_TAGGED_RE = re.compile(r'^\[([^\]]*)\]\s*(.*)$')
_APPARATUS_RE = re.compile(r'^(?:\s*\[[^\]]*\])+')
_PUNCT_RE = re.compile(r'[^\w\s]+', re.UNICODE)


def _norm_gloss(text):
    return ' '.join(_PUNCT_RE.sub(' ', _APPARATUS_RE.sub('', text).lower()).split())


def load(path):
    header, rows, columns = [], [], None
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#'):
                header.append(line)
                continue
            if columns is None:
                columns = line.split('\t')
                continue
            if line.strip():
                rows.append(dict(zip(columns, line.split('\t'))))
    return header, columns or [], rows


def verify(header, columns, rows, max_per_lemma):
    failures, notes = [], []

    for banned in BANNED_COLUMNS:
        if banned in columns:
            failures.append(f'frame carries a label column "{banned}" — labels must '
                            'come from the two annotation passes, not the sampler')

    ragged = [r for r in rows if len(r) != len(columns)]
    if ragged:
        failures.append(f'{len(ragged)} row(s) do not have {len(columns)} columns '
                        '(a stray tab shifts every later column)')

    dupe_occ = [k for k, v in collections.Counter(r['occ_id'] for r in rows).items()
                if v > 1]
    if dupe_occ:
        failures.append(f'duplicate occ_id: {dupe_occ[:5]} ({len(dupe_occ)} total)')

    dupe_sent = [k for k, v in collections.Counter(r['sent_id'] for r in rows).items()
                 if v > 1]
    if dupe_sent:
        failures.append(f'{len(dupe_sent)} sentence(s) carry more than one row '
                        f'{dupe_sent[:5]} — rows sharing a context are not '
                        'independent judgments')

    per_lemma = collections.Counter(r['lemma_key1'] for r in rows)
    over = {k: v for k, v in per_lemma.items() if v > max_per_lemma}
    if over:
        failures.append(f'per-lemma cap {max_per_lemma} exceeded: {dict(list(over.items())[:5])}')

    empty_sent = [r['row_id'] for r in rows if not r.get('sentence', '').strip()]
    if empty_sent:
        failures.append(f'rows with no sentence: {empty_sent[:5]} '
                        f'({len(empty_sent)} total)')

    if 'sense_menu' not in columns:
        failures.append('frame has no sense_menu column')
    else:
        thin, mismatched, degenerate = [], [], []
        for r in rows:
            options = [p for p in r.get('sense_menu', '').split(SENSE_SEP) if p.strip()]
            n = len(options)
            if n < 2:
                thin.append(r['row_id'])
            if r.get('n_senses') and str(n) != r['n_senses']:
                mismatched.append((r['row_id'], n, r['n_senses']))
            glosses = set()
            for o in options:
                m = _TAGGED_RE.match(o)
                g = _norm_gloss(m.group(2) if m else o)
                if g:
                    glosses.add(g)
            if n >= 2 and len(glosses) < 2:
                degenerate.append(r['row_id'])
        if thin:
            failures.append(f'rows whose menu offers < 2 senses (nothing to '
                            f'disambiguate): {thin[:5]} ({len(thin)} total)')
        if mismatched:
            failures.append(f'menu size != n_senses: {mismatched[:5]} '
                            f'({len(mismatched)} total)')
        if degenerate:
            failures.append(f'rows whose menu options are textually identical, i.e. '
                            f'unanswerable: {degenerate[:5]} ({len(degenerate)} total)')

    total = len(rows) or 1
    notes.append(f'rows: {len(rows)} across {len(per_lemma)} lemmas '
                 f'(max {max(per_lemma.values()) if per_lemma else 0} per lemma)')
    bands = collections.Counter(r['band'] for r in rows)
    notes.append('bands: ' + ', '.join(f'{k}={v}' for k, v in sorted(bands.items())))
    upos = collections.Counter(r.get('upos', '?') for r in rows)
    notes.append('UPOS (OBSERVED, not a controlled stratum): ' + ', '.join(
        f'{k}={v} ({v / total:.0%})' for k, v in upos.most_common(6)))

    thin_bands = [k for k, v in bands.items() if v < 20]
    if thin_bands:
        notes.append('bands under 20 rows (report pooled, never quote a per-band '
                     f'rate): {sorted(thin_bands)}')
    dominant = [k for k, v in upos.items() if v / total > 0.8]
    if dominant:
        notes.append(f'WARNING: {dominant} is over 80% of rows — this frame describes '
                     'that POS, and any headline number must say so')
    return failures, notes


def selftest():
    import os
    import tempfile

    failures_out = []

    def check(label, got, want):
        if got != want:
            failures_out.append(f'{label}: got {got!r}, want {want!r}')

    cols = ['row_id', 'occ_id', 'sent_id', 'lemma_key1', 'band', 'n_senses',
            'upos', 'sentence', 'sense_menu']

    def row(rid, occ, sent, lemma, menu='[1] a ‖ [2] b', n='2', sent_text='ctx here'):
        return dict(zip(cols, [rid, occ, sent, lemma, 'I2-3', n, 'NOUN',
                              sent_text, menu]))

    good = [row('r1', '1', 's1', 'aa'), row('r2', '2', 's2', 'bb')]
    f, n = verify([], cols, good, 4)
    check('clean frame passes', f, [])

    f, _ = verify([], cols + ['gold'], good, 4)
    check('label column caught', any('label column' in x for x in f), True)

    f, _ = verify([], cols, good + [row('r3', '1', 's3', 'cc')], 4)
    check('duplicate occ_id caught', any('duplicate occ_id' in x for x in f), True)

    f, _ = verify([], cols, good + [row('r3', '3', 's1', 'cc')], 4)
    check('shared sentence caught', any('more than one row' in x for x in f), True)

    f, _ = verify([], cols, [row(f'r{i}', str(i), f's{i}', 'aa') for i in range(6)],
                  4)
    check('per-lemma cap caught', any('cap 4 exceeded' in x for x in f), True)

    f, _ = verify([], cols, [row('r1', '1', 's1', 'aa', menu='[1] only', n='1')],
                  4)
    check('single-sense menu caught', any('< 2 senses' in x for x in f), True)

    f, _ = verify([], cols, [row('r1', '1', 's1', 'aa', menu='[1] a ‖ [2] b', n='7')],
                  4)
    check('menu/n_senses mismatch caught', any('!= n_senses' in x for x in f), True)

    f, _ = verify([], cols, [row('r1', '1', 's1', 'aa', sent_text='  ')], 4)
    check('empty sentence caught', any('no sentence' in x for x in f), True)

    # The live-store failure this gate exists for: same gloss under two tags.
    f, _ = verify([], cols, [row('r1', '1', 's1', 'dd',
                                 menu='[1] раздувание, вздутие ‖ '
                                      '[PW] раздувание, вздутие')], 4)
    check('identical menu options caught',
          any('textually identical' in x for x in f), True)

    # Apparatus differs, gloss does not -> still unanswerable.
    f, _ = verify([], cols, [row('r1', '1', 's1', 'dd',
                                 menu='[NWS 1] [Sen 1952] слеза ‖ '
                                      '[NWS 2] [Hoernle 1908] слеза')], 4)
    check('apparatus-only difference caught',
          any('textually identical' in x for x in f), True)

    _, n = verify([], cols, [row(f'r{i}', str(i), f's{i}', f'l{i}') for i in range(5)],
                  4)
    check('POS dominance surfaced', any('over 80% of rows' in x for x in n), True)

    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, 'f.tsv')
    with open(p, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# header\n')
        fh.write('\t'.join(cols) + '\n')
        fh.write('\t'.join(['r1', '1', 's1', 'aa', 'I2-3', '2', 'NOUN', 'ctx',
                            '[1] a ‖ [2] b']) + '\n')
    h, c, r = load(p)
    check('loader skips header', len(h), 1)
    check('loader reads columns', c, cols)
    check('loader reads rows', len(r), 1)

    if failures_out:
        print('SELFTEST FAIL')
        for x in failures_out:
            print('  -', x)
        return 1
    print('SELFTEST PASS (label column, duplicate occ/sentence, per-lemma cap, '
          'menu sanity, identical-option detection, POS dominance)')
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('frame')
    ap.add_argument('--max-per-lemma', type=int, default=6)
    args = ap.parse_args()

    header, columns, rows = load(args.frame)
    failures, notes = verify(header, columns, rows, args.max_per_lemma)
    for x in notes:
        print('note:', x)
    if failures:
        print('\nCHECK FAIL')
        for x in failures:
            print('  -', x)
        return 1
    print('\nCHECK PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
