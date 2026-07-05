#!/usr/bin/env python
r"""layer_presence_audit.py — report-only layer-presence completeness gate (H179 Step 1.3).

For each promoted headword, compare the layers `dict_merge.merged(key1)` *could* return
(pwg / pw / sch / pwkvn / nws) against the layers that actually produced promoted store
rows (the explicit `layer` field, added by promote_final_cards.py). A layer that the merge
holds records for but that yielded NO promoted sub-card is flagged `LAYER-DROPPED` — a
silent-drop guard so a whole supplement can't vanish unnoticed between generation and the
store.

REPORT-ONLY by design (H179): this does NOT block promotion. It is a characterization
tool for the deferred addenda re-glue / typology work (H180). Two known-benign sources of
`LAYER-DROPPED` that are NOT generation bugs:
  * **NWS** is folded by `merged()` whenever a net-new fragment exists, but an NWS
    sub-card is often held/deferred separately (e.g. gate-defect holds), so NWS drops are
    expected noise — use `--exclude-nws` to focus on the pwg/pw/sch/pwkvn overlay set.
  * A layer whose records carried no translatable sense (all German-only, filtered at
    promote time) legitimately yields no row. This gate cannot distinguish that from a
    true generation drop; treat a flag as "worth a look", not "proven bug".

Usage:
  python src/pilot/layer_presence_audit.py                 # audit the whole store
  python src/pilot/layer_presence_audit.py --exclude-nws   # ignore NWS (lower noise)
  python src/pilot/layer_presence_audit.py --selftest
"""
import argparse
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(RT, 'src')
STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')

if SRC not in sys.path:
    sys.path.insert(0, SRC)

import dict_merge as dm                                        # noqa: E402


def store_layers(store=STORE):
    """key1 -> set(layer) actually present in promoted rows."""
    have = defaultdict(set)
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            have[r['key1']].add(r.get('layer') or dm.layer_of(r.get('subcard', '')))
    return have


def audit(have, merged_layers, exclude_nws=False):
    """have: key1 -> set(layer); merged_layers: key1 -> set(layer) the merge could produce.
    -> list of {key1, dropped, present} for headwords missing a mergeable layer."""
    findings = []
    for key1 in sorted(have):
        could = set(merged_layers.get(key1, ()))
        got = set(have[key1])
        dropped = could - got
        if exclude_nws:
            dropped.discard('nws')
        if dropped:
            findings.append({'key1': key1, 'dropped': sorted(dropped), 'present': sorted(got)})
    return findings


def selftest():
    have = {
        'gA': {'pwg', 'pw', 'sch', 'pwkvn', 'nws'},            # complete
        'mad': {'pwg', 'pw', 'sch', 'pwkvn'},                  # nws dropped
        'paS': {'pwg', 'pw'},                                  # nws dropped (2-layer word)
        'x':   {'pwg'},                                        # pw dropped (a real overlay gap)
    }
    merged = {
        'gA': {'pwg', 'pw', 'sch', 'pwkvn', 'nws'},
        'mad': {'pwg', 'pw', 'sch', 'pwkvn', 'nws'},
        'paS': {'pwg', 'pw', 'nws'},
        'x':   {'pwg', 'pw'},
    }
    all_f = {f['key1']: f['dropped'] for f in audit(have, merged)}
    assert 'gA' not in all_f, 'a complete headword must not be flagged'
    assert all_f['mad'] == ['nws'] and all_f['paS'] == ['nws'] and all_f['x'] == ['pw']
    no_nws = {f['key1']: f['dropped'] for f in audit(have, merged, exclude_nws=True)}
    assert 'mad' not in no_nws and 'paS' not in no_nws, '--exclude-nws must silence NWS-only drops'
    assert no_nws['x'] == ['pw'], 'a genuine overlay gap survives --exclude-nws'
    print('layer_presence_audit selftest OK')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--exclude-nws', action='store_true', help='ignore NWS drops (expected noise)')
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    have = store_layers(args.store)
    merged_layers = {k: {L['layer'] for L in dm.merged(k)} for k in have}
    findings = audit(have, merged_layers, exclude_nws=args.exclude_nws)
    print('layer-presence audit: %d promoted headword(s), %d flagged%s'
          % (len(have), len(findings), ' (NWS excluded)' if args.exclude_nws else ''))
    for f in findings:
        print('  LAYER-DROPPED %-12s dropped=%s present=%s'
              % (f['key1'], ','.join(f['dropped']), ','.join(f['present'])))


if __name__ == '__main__':
    main()
