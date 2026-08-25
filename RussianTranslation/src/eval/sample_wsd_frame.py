#!/usr/bin/env python
"""sample_wsd_frame.py — draw the C1 token-in-context WSD annotation frame.

This emits the ANNOTATION FRAME for the WSD gold set: sampled DCS token
occurrences, each in its sentence, each with the PWG sense menu the annotator
chooses from. It deliberately does NOT emit gold labels — those are what MG
(pass 1) and the frozen model (pass 2) produce, and a script inventing them is the
H070 "rule-based arm" trap that invalidates a dual-annotation design
(/gold-adjudicate Phase 0). The BLI frame (sample_gold_frame.py) holds the same line.

Design (measured — see probe_wsd_strata.py and
docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md):

  * Unit = one token occurrence, not one lemma. WSD is a per-token judgment; a
    per-lemma frame would be measuring MFS, not disambiguation.
  * A SENSE is a pure-numeric sense_tag inside ONE dictionary layer (`pwg`).
    probe_wsd_strata.py's module docstring carries the measurement that forces
    this: counted naively across the store's five layers, `han` looks like it has
    430 senses and the inventory looks bimodal, which would demand a separate
    free-gloss tier for verb roots. Counted correctly the largest inventory in the
    entire store is 16, and ONE uniform pick-one frame covers every lemma.
  * Equal allocation per band, not proportional. The research question is
    "does disambiguation get harder as the inventory grows?", so band I10+ needs
    enough rows to report; a proportional draw would spend the budget on I6-9
    (174k tokens) and leave I10+ too thin to say anything about.
  * Per-lemma cap, so one frequent lemma cannot become the band. Without it a
    single high-frequency lemma would swallow a band and the "band" number would
    be one word's behaviour.
  * One token per sentence, so no two rows share a context.

Sampling is seeded and the seed is written into the output header: same inputs +
same seed = byte-identical frame.

Usage:
  python sample_wsd_frame.py --store <pwg_ru_translated.jsonl> --db <dcs_full.sqlite>
      --out <frame.tsv> [--total 200] [--max-per-lemma 6] [--layer pwg]
      [--seed 20260825] [--counts-cache <counts.json>]
  python sample_wsd_frame.py selftest
"""
import argparse
import collections
import json
import os
import random
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_wsd_strata import (  # noqa: E402  (local module, path set above)
    BANDS, DEFAULT_LAYER, MIN_TOKENS_PER_LEMMA,
    dcs_token_counts, fetch_tokens, lemma_pool, load_store,
)

SENSE_SEP = ' ‖ '
FRAME_COLUMNS = ('row_id', 'occ_id', 'sent_id', 'citation', 'lemma_key1', 'lemma_iast',
                 'band', 'n_senses', 'form', 'upos', 'sentence', 'sense_menu')


def render_menu(inv):
    """The sense menu one annotator reads, as a single tab-free, newline-free cell."""
    return SENSE_SEP.join(f'[{tag}] {gloss}' for tag, gloss in inv.items())


def _clean_cell(value):
    """TSV safety: a literal tab or newline inside a cell would shift every column."""
    return ' '.join(str(value).replace('\t', ' ').split())


def allocate(total, n_bands):
    """Split `total` across bands as evenly as possible, remainder to the first ones.

    Keeps the frame size exactly what was asked for instead of `per_band * n_bands`,
    so "200 tokens" in the roadmap means 200 rows on disk.
    """
    base, rem = divmod(total, n_bands)
    return [base + (1 if i < rem else 0) for i in range(n_bands)]


def draw_band(con, lemmas, pool, target, max_per_lemma, rng):
    """Round-robin tokens across a band's lemmas until the target is met.

    Round-robin rather than lemma-by-lemma: it spreads the draw over as many lemmas
    as possible, so the band describes the band and not its most frequent member.
    """
    buckets = {}
    for key in sorted(lemmas):
        toks = fetch_tokens(con, pool[key]['iast'])
        # One token per sentence: two rows sharing a context are not independent
        # judgments, and an annotator who has read the sentence once is primed.
        by_sentence = {}
        for t in toks:
            by_sentence.setdefault(t['sentence_id'], []).append(t)
        picked = [sorted(v, key=lambda r: r['token_id'])[0]
                  for v in by_sentence.values()]
        picked.sort(key=lambda r: r['token_id'])
        if len(picked) > max_per_lemma:
            picked = rng.sample(picked, max_per_lemma)
            picked.sort(key=lambda r: r['token_id'])
        buckets[key] = picked

    order = sorted(buckets)
    rng.shuffle(order)
    rows, exhausted = [], False
    while len(rows) < target and not exhausted:
        exhausted = True
        for key in order:
            if not buckets[key]:
                continue
            exhausted = False
            rows.append((key, buckets[key].pop(0)))
            if len(rows) >= target:
                break
    return rows


def build_frame(store_path, db_path, total, max_per_lemma, seed,
                layer=DEFAULT_LAYER, counts_cache=None):
    by_lemma = load_store(store_path)
    pool, rejected = lemma_pool(by_lemma, layer)
    counts = dcs_token_counts(db_path, [v['iast'] for v in pool.values()], counts_cache)
    for key, meta in pool.items():
        meta['n_tokens'] = counts.get(meta['iast'], 0)

    attested = {k: v for k, v in pool.items()
                if v['n_tokens'] >= MIN_TOKENS_PER_LEMMA}
    by_band = collections.defaultdict(list)
    for key, meta in attested.items():
        by_band[meta['band']].append(key)

    con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    rng = random.Random(seed)
    rows, shortfalls = [], []
    for band, target in zip(BANDS, allocate(total, len(BANDS))):
        lemmas = by_band.get(band, [])
        if not lemmas:
            shortfalls.append((band, 0, target))
            continue
        drawn = draw_band(con, lemmas, attested, target, max_per_lemma, rng)
        if len(drawn) < target:
            shortfalls.append((band, len(drawn), target))
        rows.extend((band, k, t) for k, t in drawn)
    con.close()

    stats = {
        'layer': layer,
        'store_lemmas': len(by_lemma),
        'pool_lemmas': len(pool),
        'rejected': dict(rejected),
        'attested_lemmas': len(attested),
        'max_inventory': max((v['n_senses'] for v in attested.values()), default=0),
        'band_lemmas': {b: len(v) for b, v in sorted(by_band.items())},
        'lemmas_drawn': len({k for _, k, _ in rows}),
    }
    return rows, shortfalls, stats, attested


def write_frame(rows, out_path, seed, stats, shortfalls, inputs, pool, max_per_lemma):
    with open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# C1 token-in-context WSD annotation frame\n')
        fh.write('# ANNOTATION FRAME — candidates, NOT labels. The gold label for a row\n')
        fh.write('# is produced by MG (pass 1) and the frozen model annotator (pass 2);\n')
        fh.write('# this file deliberately carries no label column. Protocol:\n')
        fh.write('# docs/WSD_GOLD_SET_ANNOTATION_PROTOCOL_2026.md\n')
        fh.write('# Task: pick ONE sense tag from sense_menu for the token `form` as it\n')
        fh.write('# is used in `sentence`, or NONE if no listed sense fits (the NONE\n')
        fh.write('# rate is a reported number, not an annotator error).\n')
        fh.write(f'# Seed: {seed} (reproducible: same inputs + seed = same frame)\n')
        fh.write(f'# Rows: {len(rows)} across {stats["lemmas_drawn"]} lemmas; '
                 f'per-lemma cap {max_per_lemma}\n')
        fh.write(f'# A SENSE = pure-numeric sense_tag within layer {stats["layer"]!r}.\n')
        fh.write(f'# Store lemmas {stats["store_lemmas"]} -> usable pool '
                 f'{stats["pool_lemmas"]} -> DCS-attested (>= {MIN_TOKENS_PER_LEMMA} '
                 f'tokens) {stats["attested_lemmas"]}\n')
        fh.write(f'# Excluded: {stats["rejected"]}\n')
        fh.write(f'# Largest inventory in the frame: {stats["max_inventory"]} senses\n')
        fh.write(f'# Lemmas per band: {stats["band_lemmas"]}\n')
        for label, path in inputs:
            fh.write(f'# Input {label}: {path}\n')
        if shortfalls:
            fh.write('# Shortfall bands (pool < target, drawn exhaustively):\n')
            for band, have, want in shortfalls:
                fh.write(f'#   {band}: {have} available, {want} requested\n')
        fh.write('\t'.join(FRAME_COLUMNS) + '\n')
        for i, (band, key, tok) in enumerate(rows, 1):
            meta = pool[key]
            cells = {
                'row_id': f'wsd-{i:04d}', 'occ_id': tok['occ_id'],
                'sent_id': tok['sent_id'], 'citation': tok['citation'],
                'lemma_key1': key, 'lemma_iast': meta['iast'], 'band': band,
                'n_senses': meta['n_senses'], 'form': tok['form'],
                'upos': tok['upos'], 'sentence': tok['sentence'],
                'sense_menu': render_menu(meta['inv']),
            }
            fh.write('\t'.join(_clean_cell(cells[c]) for c in FRAME_COLUMNS) + '\n')
    return out_path


def selftest():
    import tempfile

    failures = []

    def check(label, got, want):
        if got != want:
            failures.append(f'{label}: got {got!r}, want {want!r}')

    check('menu render', render_menu(collections.OrderedDict([('1', 'первый'),
                                                              ('2', 'второй')])),
          '[1] первый ‖ [2] второй')
    check('tab scrubbed from a cell', _clean_cell('a\tb\nc'), 'a b c')
    check('allocation is exact', sum(allocate(200, 3)), 200)
    check('allocation spreads the remainder', allocate(200, 3), [67, 67, 66])
    check('allocation with no remainder', allocate(9, 3), [3, 3, 3])

    tmp = tempfile.mkdtemp()
    store = os.path.join(tmp, 'store.jsonl')
    # aa/bb land in I2-5, cc in I6-9 — proves per-band allocation and banding.
    with open(store, 'w', encoding='utf-8') as f:
        for key, n in (('aa', 3), ('bb', 3), ('cc', 7)):
            for s in range(1, n + 1):
                f.write(json.dumps({'key1': key, 'iast': key, 'layer': 'pwg',
                                    'sense_tag': str(s),
                                    'ru': f'{s}) {{%значение{key}{s}%}}'},
                                   ensure_ascii=False) + '\n')

    db = os.path.join(tmp, 'dcs.sqlite')
    con = sqlite3.connect(db)
    con.executescript(
        'CREATE TABLE text (text_id INTEGER PRIMARY KEY, name TEXT);'
        'CREATE TABLE chapter (chapter_id INTEGER PRIMARY KEY, text_id INTEGER, ref TEXT);'
        'CREATE TABLE sentence (id INTEGER PRIMARY KEY, sent_id TEXT, chapter_id INTEGER,'
        '                       sent_counter TEXT, text_sandhied TEXT);'
        'CREATE TABLE token (id INTEGER PRIMARY KEY, sentence_id INTEGER, occ_id INTEGER,'
        '                    sent_id TEXT, idx INTEGER, form TEXT, lemma TEXT, upos TEXT);')
    con.execute("INSERT INTO text VALUES (1, 'Test')")
    con.execute("INSERT INTO chapter VALUES (1, 1, 'T, 1')")
    tid = 0
    for lemma in ('aa', 'bb', 'cc'):
        for s in range(40):                       # clears MIN_TOKENS_PER_LEMMA
            sid = abs(hash((lemma, s))) % 10 ** 7
            con.execute('INSERT OR IGNORE INTO sentence VALUES (?,?,?,?,?)',
                        (sid, f's{sid}', 1, str(s), 'alpha beta gamma delta epsilon'))
            tid += 1
            con.execute('INSERT INTO token VALUES (?,?,?,?,?,?,?,?)',
                        (tid, sid, 1000 + tid, f's{sid}', 1, lemma + str(s), lemma, 'NOUN'))
    # Two tokens sharing ONE sentence: only one may reach the frame.
    con.execute('INSERT INTO sentence VALUES (9999999, "s9999999", 1, "9", '
                '"alpha beta gamma delta epsilon")')
    con.execute('INSERT INTO token VALUES (90001, 9999999, 5001, "s9999999", 1, "aa9", "aa", "NOUN")')
    con.execute('INSERT INTO token VALUES (90002, 9999999, 5002, "s9999999", 2, "aa9b", "aa", "NOUN")')
    con.commit()
    con.close()

    rows, shortfalls, stats, pool = build_frame(store, db, total=12,
                                                max_per_lemma=4, seed=11)
    per_band = collections.Counter(b for b, _, _ in rows)
    check('I2-5 got its allocation', per_band['I2-5'], 4)
    check('I6-9 got its allocation', per_band['I6-9'], 4)
    check('I10+ empty pool is a declared shortfall',
          any(b == 'I10+' and have == 0 for b, have, _ in shortfalls), True)
    check('per-lemma cap is an upper bound',
          max(collections.Counter(k for _, k, _ in rows).values()) <= 4, True)
    check('one token per sentence',
          len({t['sentence_id'] for _, _, t in rows}), len(rows))
    check('banding put cc in I6-9',
          {k for b, k, _ in rows if b == 'I6-9'}, {'cc'})

    capped, cap_short, _, _ = build_frame(store, db, total=300, max_per_lemma=4, seed=11)
    check('cap binds under pressure',
          set(collections.Counter(k for _, k, _ in capped).values()), {4})
    check('capped draw is 3 lemmas x 4', len(capped), 12)
    check('shortfall declared when the cap binds', len(cap_short) >= 1, True)

    again, _, _, _ = build_frame(store, db, total=12, max_per_lemma=4, seed=11)
    check('seed reproducible', [t['occ_id'] for _, _, t in rows],
          [t['occ_id'] for _, _, t in again])

    out = os.path.join(tmp, 'frame.tsv')
    write_frame(rows, out, 11, stats, shortfalls, [('store', store)], pool, 4)
    with open(out, encoding='utf-8') as f:
        text = f.read()
    header = [ln for ln in text.split('\n') if not ln.startswith('#')][0]
    check('no label column', [c for c in ('gold', 'label', 'sense_gold', 'verdict')
                              if c in header.split('\t')], [])
    check('sense_menu shipped', 'sense_menu' in header, True)
    check('header carries seed', '# Seed: 11' in text, True)
    check('header states the sense definition', "within layer 'pwg'" in text, True)
    body = [ln for ln in text.split('\n') if ln and not ln.startswith('#')][1:]
    check('every row has the full column count',
          {len(ln.split('\t')) for ln in body}, {len(FRAME_COLUMNS)})

    if failures:
        print('SELFTEST FAIL')
        for f_ in failures:
            print('  -', f_)
        return 1
    print('SELFTEST PASS (exact allocation, banding, per-lemma cap, '
          'one-token-per-sentence, seed determinism, no label column)')
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--store', required=True)
    ap.add_argument('--db', required=True, help='dcs_full.sqlite')
    ap.add_argument('--out', required=True)
    ap.add_argument('--total', type=int, default=200)
    ap.add_argument('--max-per-lemma', type=int, default=6)
    ap.add_argument('--layer', default=DEFAULT_LAYER)
    ap.add_argument('--seed', type=int, default=20260825)
    ap.add_argument('--counts-cache', default=None)
    args = ap.parse_args()

    rows, shortfalls, stats, pool = build_frame(
        args.store, args.db, args.total, args.max_per_lemma, args.seed,
        args.layer, args.counts_cache)
    write_frame(rows, args.out, args.seed, stats, shortfalls,
                [('store', args.store), ('dcs', args.db)], pool, args.max_per_lemma)
    print(f'rows: {len(rows)} across {stats["lemmas_drawn"]} lemmas -> {args.out}')
    print(f'largest inventory in the frame: {stats["max_inventory"]} senses')
    print(f'excluded from the pool: {stats["rejected"]}')
    if shortfalls:
        print(f'shortfall bands: {len(shortfalls)}')
        for band, have, want in shortfalls:
            print(f'  {band}: {have}/{want}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
