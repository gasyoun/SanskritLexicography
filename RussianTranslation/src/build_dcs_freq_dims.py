#!/usr/bin/env python
r"""Build the per-dimension DCS frequency table (genre + part-of-speech).

Companion to build_dcs_freq.py (which owns the single GENERAL 1-5 band). This adds the
two extra dimensions MG asked for (2026-06-30):

  - POS frequency  : FULL distribution per lemma from the DCS token upos column
                     (counts + shares + a recalibrated 1-5 band per POS tag).
  - GENRE frequency: RAW per-genre counts from the Renou register layer
                     (dcs_lemma_renou.json register_support[genre].n = document
                     frequency, i.e. how many texts of that genre attest the lemma).
                     Kept at BOTH granularities: the 16 fine DCS genres AND a 5-era
                     Renou rollup. Plus a recalibrated 1-5 band per genre and per era.

Banding is RECALIBRATED PER DIMENSION (per MG): a category's 1-5 band uses quintile
edges computed over that category's own positive-count distribution, so band 5 always
means "top ~20% of words within THIS genre / THIS POS", not a global cutoff. (The
general band in build_dcs_freq.py keeps its fixed log10 edges.)

Keyed by the same normalized IAST lemma as build_dcs_freq.py, so annotate_dcs_freq.py
can look both tables up with one key (compound form, root fallback).

  python src/build_dcs_freq_dims.py                 # -> src/dcs_freq_dims.json
  python src/build_dcs_freq_dims.py --selftest
"""
import argparse
import collections
import json
import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from build_dcs_freq import norm_lemma, DCS_SQLITE       # shared normalizer + sqlite path

HERE = os.path.dirname(os.path.abspath(__file__))
RENOU = os.path.join(HERE, 'dcs_lemma_renou.json')
OUT = os.path.join(HERE, 'dcs_freq_dims.json')

# Renou register codes (renou_register.REGISTERS) -> 5 Renou eras (chronological rollup).
ERA_MAP = {
    'rgveda': 'Vedic', 'atharva': 'Vedic', 'yajus': 'Vedic',
    'brahmana': 'Brahmana-Upanisad', 'upanisad': 'Brahmana-Upanisad',
    'sutra': 'Sutra-Sastra', 'vyakarana': 'Sutra-Sastra', 'karika': 'Sutra-Sastra',
    'bhasya': 'Sutra-Sastra',
    'epic': 'Epic-Purana', 'epig': 'Epic-Purana', 'purana': 'Epic-Purana', 'smrti': 'Epic-Purana',
    'kavya': 'Classical', 'katha': 'Classical', 'natya': 'Classical', 'tantra': 'Classical',
    'bauddha': 'Classical', 'jaina': 'Classical', 'hors_inde': 'Classical',
}
ERAS = ['Vedic', 'Brahmana-Upanisad', 'Sutra-Sastra', 'Epic-Purana', 'Classical']


def quintile_edges(values):
    """Ascending count thresholds for bands 2..5 at the 20/40/60/80 percentiles of the
    POSITIVE counts in one category. band(count) = 1 + number of edges it clears.
    Returns a 4-list. Degenerate (few distinct values) collapses gracefully."""
    vals = sorted(v for v in values if v > 0)
    if not vals:
        return [1, 1, 1, 1]
    return [vals[min(len(vals) - 1, int(len(vals) * p))] for p in (0.2, 0.4, 0.6, 0.8)]


def _band(count, edges):
    """1-5 by how many quintile edges the count meets/exceeds; 0 if absent."""
    if count <= 0:
        return 0
    b = 1
    for e in edges:
        if count >= e:
            b += 1
    return min(b, 5)


def build_pos(sqlite_path):
    """norm_lemma -> Counter(upos -> tokens). Aggregates homonyms (lemma string)."""
    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()
    pos = collections.defaultdict(collections.Counter)
    q = ('select l.lemma, t.upos, count(*) n from token t '
         'join lemma l on t.lemma_id = l.lemma_id group by l.lemma_id, t.upos')
    for lemma, upos, n in cur.execute(q):
        key = norm_lemma(lemma)
        if key and upos:
            pos[key][upos] += n
    con.close()
    return pos


def text_registers(sqlite_path):
    """text_id -> set(register codes), resolved with build_dcs_renou's genre+name logic
    (genre route from dcs_texts_clean.json when the title matches; name-substring route
    always). Returns (id->registers, coverage stats)."""
    import build_dcs_renou as b
    exact, norm = b.load_clean()
    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()
    id2regs, resolved = {}, 0
    for tid, name in cur.execute('select text_id, name from text'):
        rec = exact.get(name) or norm.get(b._norm(name))
        genre = rec.get('genre') if rec else None
        date = rec.get('date') if rec else None
        regs = set(b.registers_for_text(genre, date, name.lower(), b._CONF_RANK['high']))
        id2regs[tid] = regs
        resolved += 1 if regs else 0
    con.close()
    return id2regs, resolved


def build_genre(sqlite_path):
    """norm_lemma -> {register -> TOKEN count}. Tokens are counted per register of the
    text they occur in (a text in N registers contributes to each — union semantics, as
    in the Renou register layer). Texts with no Renou register (medical/śāstra prose,
    nighaṇṭu, …) contribute to nothing — that ~24% of tokens is genuinely register-less."""
    id2regs, _resolved = text_registers(sqlite_path)
    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()
    genre = collections.defaultdict(collections.Counter)
    q = ('select l.lemma, c.text_id, count(*) n from token t '
         'join lemma l on t.lemma_id = l.lemma_id '
         'join sentence s on t.sentence_id = s.id '
         'join chapter c on s.chapter_id = c.chapter_id '
         'group by l.lemma_id, c.text_id')
    for lemma, tid, n in cur.execute(q):
        regs = id2regs.get(tid)
        if not regs:
            continue
        key = norm_lemma(lemma)
        if not key:
            continue
        for r in regs:
            genre[key][r] += n
    con.close()
    return genre


def finalize(pos, genre):
    # --- recalibrated edges per POS tag and per genre / era ---
    pos_tags = sorted({t for c in pos.values() for t in c})
    pos_edges = {t: quintile_edges([c[t] for c in pos.values() if c.get(t)]) for t in pos_tags}

    genres = sorted({g for c in genre.values() for g in c})
    genre_edges = {g: quintile_edges([c[g] for c in genre.values() if c.get(g)]) for g in genres}

    era_counts_all = collections.defaultdict(list)
    for c in genre.values():
        eras = collections.Counter()
        for g, n in c.items():
            eras[ERA_MAP.get(g, 'Classical')] += n
        for e, n in eras.items():
            era_counts_all[e].append(n)
    era_edges = {e: quintile_edges(v) for e, v in era_counts_all.items()}

    by_lemma = {}
    keys = set(pos) | set(genre)
    for k in keys:
        rec = {}
        pc = pos.get(k)
        if pc:
            total = sum(pc.values())
            dom = pc.most_common(1)[0][0]
            rec['pos'] = {
                'counts': dict(pc),
                'shares': {t: round(n / total, 4) for t, n in pc.items()},
                'band': {t: _band(n, pos_edges[t]) for t, n in pc.items()},
                'dominant': dom,
                'dominant_share': round(pc[dom] / total, 4),
                'total': total,
            }
        gc = genre.get(k)
        if gc:
            eras = collections.Counter()
            for g, n in gc.items():
                eras[ERA_MAP.get(g, 'Classical')] += n
            rec['genre'] = {
                'counts': dict(gc),
                'band': {g: _band(n, genre_edges[g]) for g, n in gc.items()},
            }
            rec['era'] = {
                'counts': dict(eras),
                'band': {e: _band(n, era_edges[e]) for e, n in eras.items()},
            }
        by_lemma[k] = rec
    return {
        'meta': {
            'pos_tags': pos_tags,
            'genres': genres,
            'eras': ERAS,
            'era_map': ERA_MAP,
            'pos_quintile_edges': pos_edges,
            'genre_quintile_edges': genre_edges,
            'era_quintile_edges': era_edges,
            'genre_count_semantics': 'token frequency (tokens of the lemma occurring in texts of that register; texts with no Renou register contribute nothing, ~24% of corpus tokens)',
            'generator': 'build_dcs_freq_dims.py',
            'lemmas_with_pos': len(pos),
            'lemmas_with_genre': len(genre),
        },
        'by_lemma': by_lemma,
    }


def selftest():
    assert _band(0, [2, 5, 10, 50]) == 0
    assert _band(1, [2, 5, 10, 50]) == 1
    assert _band(2, [2, 5, 10, 50]) == 2 and _band(4, [2, 5, 10, 50]) == 2
    assert _band(60, [2, 5, 10, 50]) == 5
    e = quintile_edges([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert len(e) == 4 and e == sorted(e)
    # finalize on a tiny synthetic
    pos = {'vad': collections.Counter({'VERB': 3914, 'NOUN': 4})}
    genre = {'vad': collections.Counter({'sutra': 27, 'rgveda': 2, 'epic': 4})}
    t = finalize(pos, genre)
    r = t['by_lemma']['vad']
    assert r['pos']['dominant'] == 'VERB' and r['pos']['counts']['NOUN'] == 4
    assert abs(r['pos']['shares']['VERB'] - 0.999) < 0.01
    assert r['genre']['counts']['sutra'] == 27
    # era rollup: rgveda->Vedic(2), sutra->Sutra-Sastra(27), epic->Epic-Purana(4)
    assert r['era']['counts']['Vedic'] == 2 and r['era']['counts']['Sutra-Sastra'] == 27
    assert r['era']['counts']['Epic-Purana'] == 4
    print('build_dcs_freq_dims selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sqlite', default=DCS_SQLITE)
    ap.add_argument('--renou', default=RENOU)
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not os.path.exists(args.sqlite):
        sys.exit('missing DCS sqlite: %s' % args.sqlite)
    pos = build_pos(args.sqlite)
    genre = build_genre(args.sqlite)
    table = finalize(pos, genre)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(table, f, ensure_ascii=False)
    m = table['meta']
    print('wrote %s' % args.out)
    print('  lemmas with POS    : %d (%d tags: %s)' % (m['lemmas_with_pos'], len(m['pos_tags']), ', '.join(m['pos_tags'])))
    print('  lemmas with genre  : %d (%d genres -> %d eras)' % (m['lemmas_with_genre'], len(m['genres']), len(m['eras'])))


if __name__ == '__main__':
    main()
