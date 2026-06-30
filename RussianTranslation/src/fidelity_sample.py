#!/usr/bin/env python
r"""Draw a deterministic stratified sample of translated cards for the Opus fidelity judge.

The bulk pwg_ru cards all carry judge=null — there is no measured DE->RU fidelity number yet.
This samples cards (stratified by stratum) so an Opus judge can rate a representative slice and
we can publish precision + a 95% Wilson CI. Reuses promote_final_cards.collect_cards for the same
non-null/dedup logic as the bridge.

  python src/fidelity_sample.py [--n 100] [--seed 42] [--glob 'wf_output*.json']
  -> writes src/pilot/output/fidelity_sample.jsonl  (key, iast, stratum, slice, senses[de,ru,tag])

Stratum per card = the most common non-empty sense.stratum (else 'unspecified'). The sample is
proportional to stratum sizes with a floor of min(5, available) per stratum, deterministic for a
given (seed, glob).
"""
import argparse
import collections
import glob
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'pilot', 'output')


def load_wf(path):
    with open(path, encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    return result if result is not None else wrapper


def collect_cards(paths):
    """sub-card key -> {card, meta, wf_file}; non-null wins (mirrors promote_final_cards)."""
    best = {}
    for path in paths:
        try:
            res = load_wf(path)
        except (OSError, json.JSONDecodeError):
            continue
        meta = res.get('meta') or {}
        for r in res.get('results') or []:
            key, card = r.get('key'), r.get('card')
            if key and card and key not in best:
                best[key] = {'card': card, 'meta': meta, 'wf_file': os.path.basename(path)}
    return best


def card_stratum(card):
    strata = [s.get('stratum') for rec in card.get('records') or []
              for s in rec.get('senses') or [] if s.get('stratum')]
    if not strata:
        return 'unspecified'
    return collections.Counter(strata).most_common(1)[0][0]


def card_senses(card):
    out = []
    for rec in card.get('records') or []:
        for s in rec.get('senses') or []:
            if s.get('russian'):
                out.append({'tag': s.get('tag'), 'de': s.get('german'),
                            'ru': s.get('russian'), 'stratum': s.get('stratum')})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--glob', default='wf_output*.json')
    ap.add_argument('--out', default=os.path.join(OUT, 'fidelity_sample.jsonl'))
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    best = collect_cards(paths)
    cards = []
    for subkey, entry in best.items():
        card = entry['card']
        senses = card_senses(card)
        if not senses:
            continue
        cards.append({
            'key': subkey,
            'iast': card.get('iast'),
            'root': entry['meta'].get('root'),
            'slice': 'sc' if '.sc.' in entry['wf_file'] else ('sd' if '.sd.' in entry['wf_file'] else 'other'),
            'wf_file': entry['wf_file'],
            'stratum': card_stratum(card),
            'senses': senses,
        })

    by_stratum = collections.defaultdict(list)
    for c in cards:
        by_stratum[c['stratum']].append(c)
    rng = random.Random(args.seed)
    total = len(cards)
    picked = []
    for stratum, group in sorted(by_stratum.items()):
        group = sorted(group, key=lambda c: c['key'])
        rng.shuffle(group)
        want = max(min(5, len(group)), round(args.n * len(group) / total)) if total else 0
        picked.extend(group[:min(want, len(group))])
    rng.shuffle(picked)
    picked = picked[:args.n] if len(picked) > args.n else picked

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        for c in picked:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')

    dist = collections.Counter(c['stratum'] for c in picked)
    print('population cards: %d | sampled: %d (seed %d)' % (total, len(picked), args.seed))
    print('sample by stratum: %s' % dict(sorted(dist.items())))
    print('wrote %s' % args.out)


if __name__ == '__main__':
    main()
