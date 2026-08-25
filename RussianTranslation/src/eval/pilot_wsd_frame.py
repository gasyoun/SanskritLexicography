#!/usr/bin/env python
"""pilot_wsd_frame.py — cut the instrument-check slice out of a frozen WSD frame.

WHY THIS EXISTS. The full C1 frame is 200 rows, but 200 rows is not the unit of
work an annotator feels: the frame presents **1,537 sense-menu options** in total
(median 3 in band I2-5, 7 in I6-9, **12 in I10+**, max 16), on top of a Sanskrit
sentence per row. Asking for all of it in one sitting — while 500 BLI cards are
already unvoted — spends the whole annotation budget before anyone has checked
that the instrument works. Standard practice is to pilot an annotation scheme
first; the BLI protocol reaches for the same reflex with its ~10% spot-check.

THE SLICE. One row per lemma: **every sense menu is inspected exactly once**.
That is a principled unit rather than a round number — the pilot's first job is
to find menus that cannot be answered (glosses that do not tell apart, senses
that never fit real corpus usage, a NONE rate so high the inventory is the
problem), and a menu bug shows up on its first row, not its fourth. The full
frame draws ~4 rows per lemma, so the pilot costs roughly a quarter of the frame
while covering 100% of its menus.

ROW IDENTITY IS PRESERVED. The pilot is a strict SUBSET of the frozen frame and
keeps each row's original `row_id`/`occ_id`, so pilot labels merge straight into
the full gold if the remaining rows are ever annotated. This is not a re-draw and
does not need the 920 MB corpus database.

Like every frame emitter here it carries NO label column: the labels are the
annotation passes' output.

Usage:
  python pilot_wsd_frame.py --frame wsd_frame_c1_200.tsv --out wsd_frame_c1_pilot.tsv
                            [--per-lemma 1] [--seed 20260825]
  python pilot_wsd_frame.py selftest
"""
import argparse
import collections
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SENSE_SEP = ' ‖ '
BANNED_COLUMNS = ('gold', 'label', 'sense_gold', 'gold_tag', 'verdict', 'ruling')


def load_frame(path):
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
    if columns is None:
        raise ValueError(f'{path}: no column header found')
    for banned in BANNED_COLUMNS:
        if banned in columns:
            raise ValueError(
                f'{path} carries a label column "{banned}" — a pilot must be cut '
                'from an UNLABELLED frame, or it leaks pass-1 answers')
    return header, columns, rows


def pick(rows, per_lemma, seed):
    """One (or `per_lemma`) row per lemma, seeded, in original frame order.

    Selection is by lemma rather than by band: bands fall out of it anyway (each
    lemma belongs to exactly one), and lemma coverage is what an instrument check
    needs. Output keeps frame order so the pilot reads like the frame it came from.
    """
    by_lemma = collections.OrderedDict()
    for r in rows:
        by_lemma.setdefault(r['lemma_key1'], []).append(r)

    rng = random.Random(seed)
    chosen_ids = set()
    for lemma in sorted(by_lemma):
        pool = sorted(by_lemma[lemma], key=lambda r: r['row_id'])
        take = pool if len(pool) <= per_lemma else rng.sample(pool, per_lemma)
        chosen_ids.update(r['row_id'] for r in take)
    return [r for r in rows if r['row_id'] in chosen_ids]


def menu_options(row):
    return [p for p in row.get('sense_menu', '').split(SENSE_SEP) if p.strip()]


def write_pilot(rows, columns, out_path, source_frame, per_lemma, seed, source_n):
    bands = collections.Counter(r['band'] for r in rows)
    lemmas = len({r['lemma_key1'] for r in rows})
    options = sum(len(menu_options(r)) for r in rows)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# C1 WSD annotation PILOT — instrument check before the full frame\n')
        fh.write('# ANNOTATION FRAME — candidates, NOT labels. Protocol:\n')
        fh.write('# docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md\n')
        fh.write(f'# Strict SUBSET of {os.path.basename(source_frame)} '
                 f'({source_n} rows); row_id and occ_id are PRESERVED, so pilot\n')
        fh.write('# labels merge straight into the full gold later. Not a re-draw.\n')
        fh.write(f'# Selection: {per_lemma} row(s) per lemma, seed {seed} — every '
                 'sense menu in the\n')
        fh.write('# source frame is inspected exactly once.\n')
        fh.write(f'# Rows: {len(rows)} across {lemmas} lemmas; bands '
                 f'{dict(sorted(bands.items()))}\n')
        fh.write(f'# Menu options presented in total: {options} '
                 f'(the source frame presents more)\n')
        fh.write('# Task: pick ONE sense tag from sense_menu for `form` as used in\n')
        fh.write('# `sentence`, or NONE if no listed sense fits, or SKIP with a reason.\n')
        fh.write('\t'.join(columns) + '\n')
        for r in rows:
            fh.write('\t'.join(r.get(c, '') for c in columns) + '\n')
    return {'rows': len(rows), 'lemmas': lemmas, 'options': options,
            'bands': dict(sorted(bands.items()))}


def selftest():
    import tempfile

    failures = []

    def check(label, got, want):
        if got != want:
            failures.append(f'{label}: got {got!r}, want {want!r}')

    cols = ['row_id', 'occ_id', 'sent_id', 'lemma_key1', 'band', 'n_senses',
            'form', 'upos', 'sentence', 'sense_menu']
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, 'frame.tsv')
    with open(src, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# source header\n')
        fh.write('\t'.join(cols) + '\n')
        n = 0
        # 3 lemmas x 4 rows, two bands
        for lemma, band, senses in (('aa', 'I2-5', 2), ('bb', 'I2-5', 3),
                                    ('cc', 'I6-9', 6)):
            menu = SENSE_SEP.join(f'[{i}] гл{i}' for i in range(1, senses + 1))
            for _ in range(4):
                n += 1
                fh.write('\t'.join([f'wsd-{n:04d}', str(1000 + n), f's{n}', lemma,
                                    band, str(senses), 'форма', 'VERB',
                                    'a b c d e', menu]) + '\n')

    header, columns, rows = load_frame(src)
    check('source rows', len(rows), 12)
    check('header captured', len(header), 1)

    picked = pick(rows, per_lemma=1, seed=7)
    check('one row per lemma', len(picked), 3)
    check('every lemma covered', {r['lemma_key1'] for r in picked},
          {'aa', 'bb', 'cc'})
    check('row_ids preserved from the source',
          all(r['row_id'].startswith('wsd-') for r in picked), True)
    check('pilot is a strict subset',
          {r['row_id'] for r in picked} <= {r['row_id'] for r in rows}, True)
    check('frame order preserved',
          [r['row_id'] for r in picked], sorted(r['row_id'] for r in picked))

    again = pick(rows, per_lemma=1, seed=7)
    check('seed reproducible', [r['row_id'] for r in picked],
          [r['row_id'] for r in again])

    two = pick(rows, per_lemma=2, seed=7)
    check('per_lemma=2 doubles', len(two), 6)

    # A lemma with fewer rows than per_lemma must not crash or duplicate.
    thin = pick(rows[:1], per_lemma=3, seed=7)
    check('thin lemma taken exhaustively', len(thin), 1)

    out = os.path.join(tmp, 'pilot.tsv')
    stats = write_pilot(picked, columns, out, src, 1, 7, len(rows))
    check('stats rows', stats['rows'], 3)
    check('stats lemmas', stats['lemmas'], 3)
    check('stats counts options', stats['options'], 2 + 3 + 6)
    with open(out, encoding='utf-8') as fh:
        text = fh.read()
    body_header = [ln for ln in text.split('\n') if not ln.startswith('#')][0]
    check('columns identical to source', body_header.split('\t'), columns)
    check('no label column', [c for c in BANNED_COLUMNS
                              if c in body_header.split('\t')], [])
    check('header states subset', 'Strict SUBSET' in text, True)
    check('header carries seed', 'seed 7' in text, True)
    body = [ln for ln in text.split('\n') if ln and not ln.startswith('#')][1:]
    check('row count on disk', len(body), 3)
    check('no ragged rows', {len(ln.split('\t')) for ln in body}, {len(columns)})

    # A frame that already carries labels must be refused, not silently piloted.
    bad = os.path.join(tmp, 'labelled.tsv')
    with open(bad, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\t'.join(cols + ['gold']) + '\n')
        fh.write('\t'.join(['wsd-0001', '1', 's1', 'aa', 'I2-5', '2', 'ф', 'VERB',
                            'a b c', '[1] x ‖ [2] y', '1']) + '\n')
    try:
        load_frame(bad)
        failures.append('labelled frame was accepted')
    except ValueError as exc:
        check('label column refused', 'label column' in str(exc), True)

    if failures:
        print('SELFTEST FAIL')
        for f_ in failures:
            print('  -', f_)
        return 1
    print('SELFTEST PASS (subset identity, row_id preservation, per-lemma coverage, '
          'seed determinism, label-column refusal)')
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--frame', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--per-lemma', type=int, default=1)
    ap.add_argument('--seed', type=int, default=20260825)
    args = ap.parse_args()

    header, columns, rows = load_frame(args.frame)
    picked = pick(rows, args.per_lemma, args.seed)
    stats = write_pilot(picked, columns, args.out, args.frame, args.per_lemma,
                        args.seed, len(rows))
    src_options = sum(len(menu_options(r)) for r in rows)
    print(f'pilot rows: {stats["rows"]} across {stats["lemmas"]} lemmas '
          f'-> {args.out}')
    print(f'bands: {stats["bands"]}')
    print(f'menu options: {stats["options"]} of the frame\'s {src_options} '
          f'({stats["options"] / src_options:.0%})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
