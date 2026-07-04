"""verb_worklist.py — enumerate runnable DCS-attested PWG verb roots for the RU batch drain.

Universe = verbs01 `pwg_preverb1.txt` case headers (k1), the vetted PWG verb-root
list. A root is in scope when it appears in `scale_manifest.freq.json`
(DCS-attested) and is NOT yet promoted into the RU store
(`src/pwg_ru_translated.jsonl`). Operator output is further filtered to roots
with an existing rootmap, so the drain queue only names runnable windows. The
full backlog is still written to JSON for audit/debug use.

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
SRC = os.path.join(RT, 'src')
PREVERB = os.path.normpath(os.path.join(RT, '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt'))
MANIFEST = os.path.join(HERE, 'output', 'scale_manifest.freq.json')
STORE = os.path.join(RT, 'src', 'pwg_ru_translated.jsonl')
OUT = os.path.join(HERE, 'output', 'verb_batch_worklist.json')
ROOTMAP_DIR = os.path.join(HERE, 'input')

CASE = re.compile(r';; Case \d+: L=\d+, k1=(\S+), k2=\S+, code=\S+,')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

from safe_filename import candidate_names  # noqa: E402


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


def has_rootmap(root, rootmap_dir=ROOTMAP_DIR):
    for stem in candidate_names(root):
        if os.path.exists(os.path.join(rootmap_dir, stem + '.rootmap.json')):
            return True
    return False


def build_worklist(preverb=PREVERB, manifest=MANIFEST, store=STORE, rootmap_dir=ROOTMAP_DIR):
    verbs = verb_universe(preverb)
    freq = {it['key1']: it for it in json.load(open(manifest, encoding='utf-8'))}
    done = store_roots(store)
    attested = [k for k in verbs if k in freq]
    remain = sorted((k for k in attested if k not in done), key=lambda k: -freq[k]['score'])
    runnable = [k for k in remain if has_rootmap(k, rootmap_dir)]
    runnable_set = set(runnable)
    blocked = [k for k in remain if k not in runnable_set]

    return {
        'universe_verbs01': len(verbs),
        'dcs_attested': len(attested),
        'done_promoted': sorted(done & verbs),
        'remaining': remain,
        'remaining_count': len(remain),
        'remaining_bytes': sum(freq[k]['bytes'] for k in remain),
        'runnable_remaining': runnable,
        'runnable_count': len(runnable),
        'runnable_bytes': sum(freq[k]['bytes'] for k in runnable),
        'blocked_missing_rootmap': blocked,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--top', type=int, default=0, help='print the next N roots')
    ap.add_argument('--json', action='store_true', help='print the full worklist JSON to stdout')
    ap.add_argument('--include-unrunnable', action='store_true',
                    help='print raw remaining roots for audit/debug; default --top shows runnable roots only')
    args = ap.parse_args()

    payload = build_worklist()
    freq = {it['key1']: it for it in json.load(open(MANIFEST, encoding='utf-8'))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print(f"verbs01 universe: {payload['universe_verbs01']}  DCS-attested: {payload['dcs_attested']}  "
          f"promoted: {len(payload['done_promoted'])}  REMAINING: {payload['remaining_count']} "
          f"({payload['remaining_bytes']:,} source bytes)")
    print(f"runnable: {payload['runnable_count']} ({payload['runnable_bytes']:,} source bytes)  "
          f"missing rootmap: {len(payload['blocked_missing_rootmap'])}")
    print(f"worklist written: {OUT}")
    if args.top:
        roots = payload['remaining'] if args.include_unrunnable else payload['runnable_remaining']
        label = 'raw remaining' if args.include_unrunnable else 'runnable'
        print(f"top {min(args.top, len(roots))} {label} roots:")
        for k in roots[:args.top]:
            it = freq[k]
            print(f"  {k:12s} score={it['score']:.1f} band={it['band']} bytes={it['bytes']}")
        blocked = payload['blocked_missing_rootmap']
        if blocked:
            print('WARNING: %d remaining root(s) missing rootmaps; first: %s' %
                  (len(blocked), ', '.join(blocked[:10])), file=sys.stderr)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
