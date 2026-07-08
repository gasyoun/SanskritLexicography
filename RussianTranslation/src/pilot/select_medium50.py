#!/usr/bin/env python
"""select_medium50.py — H317: freeze a 50-key medium-band worklist for the pipeline test window.

Selection: DCS frequency band 4 (scale_manifest.freq.json), 3-30 senses per PWG entry
(excludes monster/root-class), not a verb (verbs01 universe), not already in the
promoted store or a live requeue. Prefer nominal entries; a small verb minority is
allowed by the handoff but this run selects pure nominal for a clean test.

Usage: python src/pilot/select_medium50.py [--n 50]
Writes: src/pilot/H317_medium50_worklist.<date>.json (committed, auditable)
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
SRC = os.path.dirname(HERE)                                 # .../src
RT = os.path.dirname(SRC)                                   # .../RussianTranslation
MANIFEST = os.path.join(HERE, 'output', 'scale_manifest.freq.json')
STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
PREVERB = os.path.normpath(os.path.join(RT, '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt'))

if SRC not in sys.path:
    sys.path.insert(0, SRC)

import microstructure as M   # noqa: E402
import dict_merge as dm      # noqa: E402
import corpus_gate as cg     # noqa: E402

CASE = re.compile(r';; Case \d+: L=\d+, k1=(\S+), k2=\S+, code=\S+,')


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


def requeued_keys():
    """Keys already sitting in a live requeue lane (not yet re-promoted) -- skip them
    for a clean test window rather than double-booking."""
    seen = set()
    for fn in ('requeue.keys.txt', 'requeue.defect.keys.txt', 'requeue.transient.keys.txt'):
        p = os.path.join(HERE, 'output', fn)
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        seen.add(line)
    return seen


def sense_count(key, pwg_idx):
    """Size proxy for 'senses per entry'. Most PWG nominal entries carry a single
    top-level numbered sense (portrait['senses'] has length 1) -- the real size
    signal is citation density within that sense, which is exactly what the H189
    presplit trigger (HEAD_CIT_BUDGET=18, see gen_opt_harness2.py/_pilot_gen_merged.py)
    already gates on. So 'senses' here = total <ls>-equivalent citation count across
    all top-level senses, keeping the handoff's own "below the presplit citation-density
    triggers" ceiling as the operative definition of non-monster medium size."""
    fk = cg.form_key(key)
    bufs = pwg_idx.get(fk, [])
    if not bufs:
        return None
    portraits = [M.portrait(buf) for buf in bufs]
    cits = sum(len(s.get('citations', [])) for p in portraits for s in p['senses'])
    return cits, len(bufs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=50)
    ap.add_argument('--min-senses', type=int, default=3)
    ap.add_argument('--max-senses', type=int, default=30)
    ap.add_argument('--date', default='08.07.26')
    args = ap.parse_args()

    manifest = json.load(open(MANIFEST, encoding='utf-8'))
    band4 = [it for it in manifest if it.get('band') == 4]
    verbs = verb_universe()
    done = store_keys()
    inflight = requeued_keys()
    pwg_idx = dm.index('pwg')

    candidates = []
    checked = 0
    for it in band4:
        k = it['key1']
        if k in verbs or k in done or k in inflight:
            continue
        checked += 1
        r = sense_count(k, pwg_idx)
        if r is None:
            continue
        ns, nrecs = r
        if args.min_senses <= ns <= args.max_senses and nrecs == 1:
            candidates.append({'key1': k, 'score': it['score'], 'band': it['band'],
                                'n_texts': it['n_texts'], 'bytes': it['bytes'],
                                'senses': ns, 'recs': nrecs})
        if len(candidates) >= args.n * 3:   # enough headroom to pick a clean top-N
            break

    # Deterministic pick: highest frequency score first within the medium band.
    candidates.sort(key=lambda x: -x['score'])
    selected = candidates[:args.n]

    out = {
        'schema': 'pwg.h317_medium50_selection.v1',
        'source': 'src/pilot/output/scale_manifest.freq.json',
        'band': 4,
        'sense_range': [args.min_senses, args.max_senses],
        'excludes': ['verbs01 universe', 'promoted store (pwg_ru_translated.jsonl)',
                     'live requeue lanes', 'multi-record (nrecs>1) headwords'],
        'band4_total': len(band4),
        'candidates_scanned': checked,
        'candidates_matched': len(candidates),
        'n_selected': len(selected),
        'keys': [c['key1'] for c in selected],
        'detail': selected,
    }
    out_path = os.path.join(RT, 'src', 'pilot', 'H317_medium50_worklist.%s.json' % args.date)
    json.dump(out, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('band4 total=%d checked=%d matched=%d selected=%d' % (
        len(band4), checked, len(candidates), len(selected)))
    print('wrote', out_path)


if __name__ == '__main__':
    main()
