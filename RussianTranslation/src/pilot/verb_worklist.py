"""verb_worklist.py — enumerate the remaining DCS-attested PWG verb roots for the RU batch drain.

Universe = verbs01 `pwg_preverb1.txt` case headers (k1), the vetted PWG verb-root
list. A root is in scope when it appears in `scale_manifest.freq.json`
(DCS-attested) and is NOT yet promoted into the RU store
(`src/pwg_ru_translated.jsonl`). Output is score-ranked (freq order), the same
order the drain consumes it in.

Usage:
  python src/pilot/verb_worklist.py            # print summary + write worklist JSON
  python src/pilot/verb_worklist.py --top 20   # also print the next N roots

Writes: src/pilot/output/verb_batch_worklist.json (gitignored, regenerable).
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))  # RussianTranslation/
PREVERB = os.path.normpath(os.path.join(RT, '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt'))
MANIFEST = os.path.join(HERE, 'output', 'scale_manifest.freq.json')
STORE = os.path.join(RT, 'src', 'pwg_ru_translated.jsonl')
OUT = os.path.join(HERE, 'output', 'verb_batch_worklist.json')

CASE = re.compile(r';; Case \d+: L=\d+, k1=(\S+), k2=\S+, code=\S+,')


def verb_universe(path=PREVERB):
    roots = set()
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = CASE.match(line)
            if m:
                roots.add(m.group(1))
    return roots


def store_roots(path=STORE):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                done.add(json.loads(line).get('key1'))
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--top', type=int, default=0, help='print the next N roots')
    ap.add_argument('--json', action='store_true', help='print the full worklist JSON to stdout')
    args = ap.parse_args()

    verbs = verb_universe()
    freq = {it['key1']: it for it in json.load(open(MANIFEST, encoding='utf-8'))}
    done = store_roots()
    attested = [k for k in verbs if k in freq]
    remain = sorted((k for k in attested if k not in done), key=lambda k: -freq[k]['score'])

    payload = {
        'universe_verbs01': len(verbs),
        'dcs_attested': len(attested),
        'done_promoted': sorted(done & verbs),
        'remaining': remain,
        'remaining_count': len(remain),
        'remaining_bytes': sum(freq[k]['bytes'] for k in remain),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print(f"verbs01 universe: {len(verbs)}  DCS-attested: {len(attested)}  "
          f"promoted: {len(done & verbs)}  REMAINING: {len(remain)} "
          f"({payload['remaining_bytes']:,} source bytes)")
    print(f"worklist written: {OUT}")
    if args.top:
        for k in remain[:args.top]:
            it = freq[k]
            print(f"  {k:12s} score={it['score']:.1f} band={it['band']} bytes={it['bytes']}")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
