#!/usr/bin/env python
r"""H1210 A/B — freeze the 100-card "maximally diverse" worklist (DeepSeek arm vs Claude arm).

The H1210 ruling (MG, 17-07-2026) asks for a STRATIFIED, not random, selection: length
deciles, sense count, root/nominal/indeclinable class, citation density, pwg vs no_pwg
layer, and deliberate inclusion of the historical defect classes ({#..#} spans H858,
sense-loss H920, circular glosses). Modelled on `select_medium50.py` (H317) but widened
from one frequency band to the whole runnable universe.

Strata (100 = 60 + 15 + 10 + 10 + 5):

  S1 length-decile grid   60  10 byte-deciles of the runnable pool x 6 cards, each decile's
                              6 picked by greedy max-min diversity over the normalized
                              feature vector (senses, cite_density, sanskrit_spans, pos class)
  S2 defect-class culprits 15  5 highest {#..#} density (H858 markup/Sanskrit spans)
                              + 5 highest top-level sense count (H920 sense-loss)
                              + 5 highest citation density (circular-gloss / dense-citation risk)
  S3 no_pwg supplement    10  the PWG-miss lane (PW/SCH/PWKVN-only records) — the layer whose
                              residual ledger holds 20 known-defect keys; those are preferred
  S4 verb roots           10  the verbs01 universe (root-class entries, excluded by H317)
  S5 medium50 overlap      5  deliberate intersection with H317_medium50_worklist for a direct
                              cross-run comparison (the handoff asks for it, marked in output)

Cap (declared, not silent): the runnable pool is `bytes <= --max-bytes` (default 12000, the
harness per-agent packing budget). That drops the 248 monster heads (0.6% of 43,968) whose
nominal-mode cost blew up in H189 (~5.29M tok/card) — deciles are computed over the runnable
pool and the excluded count is written into the worklist JSON.

Usage:
  python src/pilot/h1210/select_ab100.py [--n 100] [--max-bytes 12000] [--date 28.07.26]
Writes: src/pilot/h1210/H1210_ab100_worklist.<date>.json (committed, auditable)
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))              # .../src/pilot/h1210
PILOT = os.path.dirname(HERE)                                  # .../src/pilot
SRC = os.path.dirname(PILOT)                                   # .../src
RT = os.path.dirname(SRC)                                      # .../RussianTranslation

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if PILOT not in sys.path:
    sys.path.insert(0, PILOT)

import microstructure as M      # noqa: E402
import dict_merge as dm         # noqa: E402
import corpus_gate as cg        # noqa: E402
from store_path import canonical_store   # noqa: E402
from safe_filename import decode_safe_name   # noqa: E402

# `output/` is a gitignored runtime dir that lives in the MAIN checkout; a linked worktree
# has none. Resolve the frequency manifest the same way the store is resolved.
STORE = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
MAIN_RT = os.path.dirname(os.path.dirname(STORE))              # <main>/RussianTranslation
MANIFEST = os.path.join(MAIN_RT, 'src', 'pilot', 'output', 'scale_manifest.freq.json')
MEDIUM50 = os.path.join(PILOT, 'H317_medium50_worklist.08.07.26.json')
BACKFILL = os.path.join(PILOT, 'lexical_cores', 'pwg_miss_backfill_queue.md')
RESIDUALS = os.path.join(PILOT, 'no_pwg_residuals.jsonl')
PREVERB = os.path.normpath(os.path.join(RT, '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt'))

CASE = re.compile(r';; Case \d+: L=\d+, k1=(\S+), k2=\S+, code=\S+,')
QUEUE_ROW = re.compile(r'^\|\s*(\S+)\s*\|\s*\S+\s*\|\s*([a-z/]+)\s*\|')

INDECLINABLE_POS = {'adv.', 'interj.', 'partikel', 'praep.', 'conj.', 'avy.', 'indecl.',
                    'praef.', 'part.'}


def verb_universe(path=PREVERB):
    roots = set()
    if not os.path.exists(path):
        return roots
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = CASE.match(line)
            if m:
                roots.add(m.group(1))
    return roots


def store_keys(path=STORE):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                done.add(json.loads(line).get('key1'))
    return done


def no_pwg_queue(path=BACKFILL):
    """The 232 PWG-miss lemmas (key1 -> layer string) from the H206 backfill queue."""
    rows = {}
    if not os.path.exists(path):
        return rows
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = QUEUE_ROW.match(line.strip())
            if m and m.group(1) != 'key1':
                rows[m.group(1)] = m.group(2)
    return rows


def residual_keys(path=RESIDUALS):
    """Known-defect no_pwg keys (the residual ledger) — preferred inside stratum S3.

    Ledger keys are SAFE-NAME encoded (`avy_ahata~~h0_zz_pw`), the reversible Windows-safe
    stem, not SLP1 key1 — decode before use or the harness reports `missing input`.
    """
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line).get('key'))
                except ValueError:
                    pass
    return [k for k in out if k]


def pos_class(portraits, key, verbs):
    if key in verbs:
        return 'root'
    tags = {str(t).strip().lower() for p in portraits for t in (p.get('pos') or [])}
    if tags & INDECLINABLE_POS:
        return 'indeclinable'
    return 'nominal'


def features(key, pwg_idx, verbs, row=None):
    """Cheap deterministic feature vector for one headword. None if it has no PWG record."""
    fk = cg.form_key(key)
    bufs = pwg_idx.get(fk, [])
    if not bufs:
        return None
    portraits = [M.portrait(b) for b in bufs]
    joined = '\n'.join(bufs) if isinstance(bufs[0], str) else '\n'.join(str(b) for b in bufs)
    senses = [s for p in portraits for s in p['senses']]
    n_senses = len(senses)
    n_cits = sum(len(s.get('citations', [])) for s in senses)
    return {
        'key1': key,
        'bytes': (row or {}).get('bytes', len(joined)),
        'score': (row or {}).get('score'),
        'band': (row or {}).get('band'),
        'recs': len(bufs),
        'n_senses': n_senses,
        'n_citations': n_cits,
        'cite_density': round(n_cits / max(n_senses, 1), 2),
        'sanskrit_spans': len(re.findall(r'\{#.*?#\}', joined)),
        'ls_spans': joined.count('<ls'),
        'ab_spans': joined.count('<ab'),
        'pos_class': pos_class(portraits, key, verbs),
        'layer': 'pwg',
    }


# ---------------------------------------------------------------- diversity picking
DIVERSITY_DIMS = ('bytes', 'n_senses', 'cite_density', 'sanskrit_spans', 'ls_spans')


def _normalize(cands):
    lo, hi = {}, {}
    for d in DIVERSITY_DIMS:
        vals = [c[d] for c in cands]
        lo[d], hi[d] = min(vals), max(vals)
    vecs = []
    for c in cands:
        vecs.append([0.0 if hi[d] == lo[d] else (c[d] - lo[d]) / (hi[d] - lo[d])
                     for d in DIVERSITY_DIMS])
    return vecs


def _dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def pick_diverse(cands, k):
    """Greedy max-min (farthest-point) pick over the normalized feature vector.

    Deterministic: seeds on the candidate with the largest feature sum, then repeatedly adds
    the candidate farthest from everything already chosen. Ties break on key1 (sorted input).
    """
    if len(cands) <= k:
        return list(cands)
    cands = sorted(cands, key=lambda c: c['key1'])
    vecs = _normalize(cands)
    chosen = [max(range(len(cands)), key=lambda i: (sum(vecs[i]), -i))]
    while len(chosen) < k:
        best, best_d = None, -1.0
        for i in range(len(cands)):
            if i in chosen:
                continue
            d = min(_dist(vecs[i], vecs[j]) for j in chosen)
            if d > best_d:
                best, best_d = i, d
        chosen.append(best)
    return [cands[i] for i in sorted(chosen)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--max-bytes', type=int, default=12000)
    ap.add_argument('--per-decile', type=int, default=6)
    ap.add_argument('--decile-sample', type=int, default=60,
                    help='candidates featurized per decile before the diversity pick')
    ap.add_argument('--date', default='28.07.26')
    a = ap.parse_args()

    man = json.load(open(MANIFEST, encoding='utf-8'))
    verbs = verb_universe()
    done = store_keys()
    pwg_idx = dm.index('pwg')
    queue = no_pwg_queue()
    residuals = residual_keys()
    medium50 = set(json.load(open(MEDIUM50, encoding='utf-8'))['keys'])

    pool = [r for r in man if r.get('bytes', 0) <= a.max_bytes]
    excluded_monsters = len(man) - len(pool)
    pool.sort(key=lambda r: r['bytes'])

    picked, seen, strata = [], set(), {}

    def take(rows, stratum):
        added = []
        for f in rows:
            if f['key1'] in seen:
                continue
            seen.add(f['key1'])
            f = dict(f, stratum=stratum,
                     in_medium50=f['key1'] in medium50,
                     in_store=f['key1'] in done)
            picked.append(f)
            added.append(f['key1'])
        strata.setdefault(stratum, []).extend(added)
        return added

    # ---- S1: length deciles ------------------------------------------------------
    dec_size = len(pool) // 10
    decile_bounds = []
    for d in range(10):
        lo = d * dec_size
        hi = (d + 1) * dec_size if d < 9 else len(pool)
        chunk = pool[lo:hi]
        decile_bounds.append([chunk[0]['bytes'], chunk[-1]['bytes'], len(chunk)])
        # deterministic evenly-spaced sample of the decile, then featurize
        step = max(1, len(chunk) // a.decile_sample)
        cands = []
        for r in chunk[::step]:
            if r['key1'] in seen:
                continue
            f = features(r['key1'], pwg_idx, verbs, r)
            if f:
                cands.append(f)
            if len(cands) >= a.decile_sample:
                break
        take(pick_diverse(cands, a.per_decile), 'S1_decile_%d' % (d + 1))
        print('decile %2d bytes %5d-%5d n=%5d  cands=%3d  picked=%d'
              % (d + 1, decile_bounds[-1][0], decile_bounds[-1][1], len(chunk),
                 len(cands), min(a.per_decile, len(cands))))

    # ---- S2: defect-class culprits ------------------------------------------------
    # Featurize the densest tail of the pool (top 1200 by bytes below the cap) — the region
    # where {#..#} spans, many senses, and dense citations actually live.
    tail = [r for r in pool[-1200:]]
    tail_feats = []
    for r in tail:
        if r['key1'] in seen:
            continue
        f = features(r['key1'], pwg_idx, verbs, r)
        if f:
            tail_feats.append(f)
    take(sorted(tail_feats, key=lambda f: -f['sanskrit_spans'])[:5], 'S2_h858_sanskrit_spans')
    take(sorted(tail_feats, key=lambda f: -f['n_senses'])[:5], 'S2_h920_sense_loss')
    take(sorted(tail_feats, key=lambda f: -f['cite_density'])[:5], 'S2_cite_density')

    # ---- S3: no_pwg supplement lane ----------------------------------------------
    no_pwg = []
    for k, encoded in ([(x, True) for x in residuals]
                       + [(x, False) for x in sorted(queue)]):
        base = k.split('~~')[0]
        if encoded:
            base = decode_safe_name(base)
        if base in seen or any(x['key1'] == base for x in no_pwg):
            continue
        no_pwg.append({'key1': base, 'bytes': None, 'score': None, 'band': None,
                       'recs': 0, 'n_senses': None, 'n_citations': None,
                       'cite_density': None, 'sanskrit_spans': None, 'ls_spans': None,
                       'ab_spans': None, 'pos_class': 'nominal', 'layer': 'no_pwg',
                       'no_pwg_layers': queue.get(base, 'residual'),
                       'sub_key': k if '~~' in k else None})
        if len(no_pwg) >= 10:
            break
    take(no_pwg, 'S3_no_pwg')

    # ---- S4: verb roots ------------------------------------------------------------
    verb_rows = [r for r in pool if r['key1'] in verbs and r['key1'] not in seen]
    verb_rows.sort(key=lambda r: -r['bytes'])
    step = max(1, len(verb_rows) // 40)
    vcands = []
    for r in verb_rows[::step]:
        f = features(r['key1'], pwg_idx, verbs, r)
        if f:
            vcands.append(f)
        if len(vcands) >= 40:
            break
    take(pick_diverse(vcands, 10), 'S4_verb_root')

    # ---- S5: medium50 overlap ------------------------------------------------------
    m50_rows = [r for r in man if r['key1'] in medium50 and r['key1'] not in seen]
    m50_feats = []
    for r in sorted(m50_rows, key=lambda r: r['key1']):
        f = features(r['key1'], pwg_idx, verbs, r)
        if f:
            m50_feats.append(f)
    take(pick_diverse(m50_feats, 5), 'S5_medium50_overlap')

    out = {
        'schema': 'pwg.h1210_ab100_selection.v1',
        'handoff': 'H1210',
        'source': 'src/pilot/output/scale_manifest.freq.json (main-checkout runtime dir)',
        'selection_rule': 'stratified (not random): 10 byte-deciles x 6 diversity-picked '
                          '+ 15 defect-class culprits + 10 no_pwg + 10 verb roots '
                          '+ 5 medium50 overlap',
        'declared_caps': {
            'max_bytes': a.max_bytes,
            'monster_heads_excluded': excluded_monsters,
            'why': 'nominal-mode cost blow-up on giant heads (H189: ~5.29M tok/card); '
                   'deciles are computed over the runnable pool, not the full universe',
        },
        'universe_rows': len(man),
        'runnable_pool': len(pool),
        'decile_bounds_bytes': decile_bounds,
        'n_selected': len(picked),
        'strata': {k: len(v) for k, v in strata.items()},
        'medium50_overlap': sorted(f['key1'] for f in picked if f.get('in_medium50')),
        'already_in_store': sorted(f['key1'] for f in picked if f.get('in_store')),
        'keys': [f['key1'] for f in picked],
        'detail': picked,
    }
    out_path = os.path.join(HERE, 'H1210_ab100_worklist.%s.json' % a.date)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('\nuniverse=%d runnable=%d (monsters excluded=%d) selected=%d'
          % (len(man), len(pool), excluded_monsters, len(picked)))
    for k in sorted(strata):
        print('  %-24s %d' % (k, len(strata[k])))
    print('medium50 overlap: %d  already-in-store: %d'
          % (len(out['medium50_overlap']), len(out['already_in_store'])))
    print('wrote', out_path)


if __name__ == '__main__':
    main()
