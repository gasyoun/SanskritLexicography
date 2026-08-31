#!/usr/bin/env python
r"""H3751 fold -- probe the store for issue #1767's NAMED degraded keys.

`h3751_key1_census.py` finds zero sub-card/`key1` disagreements on the current store, which
is a claim strong enough to deserve a second, independent check: this looks up issue
[#1767](https://github.com/gasyoun/SanskritLexicography/issues/1767)'s own worked examples
by name -- the flattened lemmas, the three conflating keys, the junk-in-`key1` row and the
degraded `iast` values -- and reports, per example, whether it is still in the store.

    python src/h3751_key1_probe.py [--store PATH] [--json OUT]
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store   # noqa: E402

DEFAULT_STORE = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))

# issue #1767, verbatim: flattened key1 forms, conflating keys, the junk key1, degraded iast
FLATTENED = ['apta', 'gawa', 'asru']
CONFLATING = ['vasa', 'bara', 'vasin']
JUNK_KEY1 = ['durg_a~~h0_zz_sch']
DEGRADED_IAST = ['gaṭa', 'manorata']


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    by_key1 = collections.Counter()
    by_iast = collections.Counter()
    with io.open(args.store, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            by_key1[row.get('key1')] += 1
            by_iast[row.get('iast')] += 1

    out = {'store': args.store, 'flattened_key1': {}, 'conflating_key1': {},
           'junk_key1': {}, 'degraded_iast': {}}
    for label, names, table in (('flattened_key1', FLATTENED, by_key1),
                                ('conflating_key1', CONFLATING, by_key1),
                                ('junk_key1', JUNK_KEY1, by_key1),
                                ('degraded_iast', DEGRADED_IAST, by_iast)):
        print('--- %s ---' % label)
        for name in names:
            n = table.get(name, 0)
            out[label][name] = n
            print('  %-22s %s' % (name, ('%d row(s) STILL PRESENT' % n) if n else 'absent'))

    total = sum(sum(v.values()) for v in out.values() if isinstance(v, dict))
    print('issue #1767 named examples still present: %d' % total)
    if args.json:
        with io.open(args.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print('wrote %s' % args.json)
    return 0


if __name__ == '__main__':
    sys.exit(main())
